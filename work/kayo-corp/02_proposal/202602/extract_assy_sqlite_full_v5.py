#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_assy_sqlite_full_v5.py

機能:
- 入力フォルダ内の *.xls を解析
- extract_assy_xls_integrated.py と完全に同等のロジックで抽出
  (特に「管理費」と「工程コード2行」の対応を強化)
- 結果を SQLite データベース (.db) に保存
"""

import argparse
import datetime as dt
import logging
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import xlrd
import pandas as pd

# -------------------------
# Utility (共通関数)
# -------------------------
def norm_text(x: Any) -> str:
    if x is None: return ""
    if isinstance(x, float):
        if x.is_integer(): return str(int(x))
        return str(x)
    return str(x).replace("\u3000", " ").strip()

def compact(s: str) -> str:
    s = s.replace("\u3000", " ")
    s = re.sub(r"[\s\-‐-–—_・/\\]", "", s)
    return s.lower()

def is_blank_row(row: List[Any]) -> bool:
    return all(norm_text(c) == "" for c in row)

def joined_row(row: List[Any]) -> str:
    return "｜".join(norm_text(c) for c in row if norm_text(c) != "")

def safe_get(row: List[Any], idx: Optional[int]) -> str:
    if idx is None or idx < 0 or idx >= len(row):
        return ""
    return norm_text(row[idx])

def safe_get_num(row: List[Any], idx: Optional[int]) -> Optional[float]:
    if idx is None or idx < 0 or idx >= len(row):
        return None
    v = row[idx]
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    s = norm_text(v)
    if s == "": return None
    try:
        return float(s.replace(",", ""))
    except:
        return None

def find_cell_pos(rows: List[List[Any]], target: str, row_limit: Optional[int]=None) -> Optional[Tuple[int,int]]:
    t = target.strip()
    limit = row_limit if row_limit is not None else len(rows)
    for r in range(min(limit, len(rows))):
        row = rows[r]
        for c, cell in enumerate(row):
            if t in norm_text(cell):
                return (r, c)
    return None

def read_sheet_as_rows(sheet: xlrd.sheet.Sheet) -> List[List[Any]]:
    return [sheet.row_values(r) for r in range(sheet.nrows)]

# -------------------------
# Sheet Exclusion
# -------------------------
EXCLUDE_SHEET_NAME_CONTAINS = [
    "再検討依頼書", "プレス（組立品）", "プレス（単品）", "成形（組立品）", "成形（単品）",
]
def should_exclude_sheet(sheet_name: str) -> bool:
    return any(k in sheet_name for k in EXCLUDE_SHEET_NAME_CONTAINS)

# -------------------------
# ASSY Code Extraction
# -------------------------
ASSY_LABELS = ["部品コード", "製品コード", "品目コード", "品目ｺｰﾄﾞ"]
def looks_like_assy_code(s: str) -> bool:
    if not s: return False
    if s in ("部品名", "品名", "名称"): return False
    has_alnum = any(ch.isalnum() for ch in s)
    return has_alnum and len(s) >= 6

def extract_assy_code(rows: List[List[Any]]) -> str:
    for lab in ASSY_LABELS:
        pos = find_cell_pos(rows, lab, row_limit=40)
        if not pos: continue
        r, c = pos
        for dc in (1, 2, 3):
            if c + dc < len(rows[r]):
                v = norm_text(rows[r][c + dc])
                if looks_like_assy_code(v): return v
        for dr in (1, 2, 3):
            if r + dr < len(rows):
                v = norm_text(rows[r + dr][c])
                if looks_like_assy_code(v): return v
    return ""

# -------------------------
# Material Extraction
# -------------------------
PROCESS_BLOCK_HINTS = [
    "工程費明細", "加工費明細", "工程明細",
    "工程ｺｰﾄﾞ", "工程コード", "工程名・手順", "工程名", "使用設備",
    "標準時間", "準備時間", "レート", "金額"
]
NOTICE_KEYWORD_1 = "これより下は"
NOTICE_KEYWORD_2 = "行の追加"
def has_notice(row_text: str) -> bool:
    return (NOTICE_KEYWORD_1 in row_text) and (NOTICE_KEYWORD_2 in row_text)

def find_material_header(rows: List[List[Any]]) -> Optional[int]:
    for r, row in enumerate(rows):
        s = compact(joined_row(row))
        if "行番" in s and ("部品コード" in s or "品目コード" in s or "品目ｺｰﾄﾞ" in s):
            return r
    return None

def build_col_index_map(header_row: List[Any]) -> Dict[str, int]:
    m: Dict[str,int] = {}
    for i, cell in enumerate(header_row):
        name = norm_text(cell)
        if name and name not in m:
            m[name] = i
    return m

def pick_col(colmap: Dict[str,int], candidates: List[str]) -> Optional[int]:
    for c in candidates:
        if c in colmap: return colmap[c]
    for c in candidates:
        for colname, idx in colmap.items():
            if c in colname: return idx
    return None

def extract_material(rows: List[List[Any]], source_file: str, parent_assy: str, sheet_assy: str, sheet_name: str):
    header_r = find_material_header(rows)
    if header_r is None: return [], ""
    
    header = rows[header_r]
    colmap = build_col_index_map(header)
    pattern = "A" if any(k in colmap for k in ["材料・規格・グレード・色番", "展開寸法", "所要量"]) else "B"

    idx_line = pick_col(colmap, ["行番", "行", "No"])
    idx_partcode = pick_col(colmap, ["部品コード", "品目コード", "品目ｺｰﾄﾞ"])
    idx_partname = pick_col(colmap, ["部品名", "名称"])
    idx_unit = pick_col(colmap, ["単位"])
    idx_supplyno = pick_col(colmap, ["支給", "支給区分"])
    idx_qty = pick_col(colmap, ["使用数", "所要量", "数量", "取数"]) 
    
    idx_unitprice = pick_col(colmap, ["単価"])
    idx_self_cost = pick_col(colmap, ["自給材費", "自給材料費"])
    idx_supply_cost = pick_col(colmap, ["支給材費", "支給材料費", "支給材料", "支給費"])
    idx_raw_amount = pick_col(colmap, ["材料費計", "材料費合計"]) or pick_col(colmap, ["金額"])
    idx_assy_proc = pick_col(colmap, ["加工費", "加工賃"])

    out = []
    r = header_r + 1
    blank_streak = 0
    
    while r < len(rows):
        row = rows[r]
        row_text = joined_row(row)
        if has_notice(row_text): break
        if any(h in row_text for h in PROCESS_BLOCK_HINTS): break
        
        line_no = safe_get(row, idx_line)
        if not line_no:
            blank_streak += 1
        else:
            blank_streak = 0
        if blank_streak >= 2: break
        
        partcode = safe_get(row, idx_partcode)
        if not partcode and not safe_get(row, idx_partname):
            r += 1
            continue
            
        qty = safe_get_num(row, idx_qty)
        unit_price = safe_get_num(row, idx_unitprice)
        self_cost = safe_get_num(row, idx_self_cost)
        supply_cost = safe_get_num(row, idx_supply_cost)
        raw_amount = safe_get_num(row, idx_raw_amount)
        assy_proc = safe_get_num(row, idx_assy_proc)
        
        amount = raw_amount
        if amount is None:
            if self_cost or supply_cost:
                amount = (self_cost or 0) + (supply_cost or 0)
            elif unit_price and qty:
                amount = unit_price * qty
        if assy_proc and amount:
            amount += assy_proc
        elif assy_proc:
            amount = assy_proc

        out.append({
            "SourceFile": source_file, "ParentAssy": parent_assy, "SheetAssy": sheet_assy, "SheetName": sheet_name,
            "LineNo": line_no, "PartCode": partcode, "PartName": safe_get(row, idx_partname),
            "UnitNo": safe_get(row, idx_unit), "SupplyNo": safe_get(row, idx_supplyno),
            "Qty": qty, "UnitPrice": unit_price, "SelfSuppliedCost": self_cost, "SupplyCost": supply_cost,
            "RawAmount": raw_amount, "AssyRolledProcessCost": assy_proc, "Amount": amount,
            "Pattern": pattern, "ExtractedAt": dt.datetime.now().isoformat(timespec="seconds")
        })
        r += 1
    return out, pattern

# -------------------------
# Process Extraction
# -------------------------
PROCESS_SECTION_MARKERS = ["工程費明細", "加工費明細", "工程明細", "加工費"]

def find_process_section_start(rows: List[List[Any]]) -> Optional[int]:
    for mk in PROCESS_SECTION_MARKERS:
        pos = find_cell_pos(rows, mk)
        if pos: return pos[0]
    return None

def score_row_for_process_header(row: List[Any]) -> int:
    s = compact(joined_row(row))
    if not s: return 0
    score = 0
    if "工程" in s: score += 2
    if ("工程名" in s) or ("手順" in s): score += 2
    if ("使用設備" in s) or ("設備" in s): score += 1
    if ("レート" in s) or ("金額" in s): score += 1
    if ("標準時間" in s) or ("準備時間" in s): score += 1
    if ("工程コード" in s) or ("工程ｺｰﾄﾞ" in s): score += 2
    else:
        if ("工程" in s and "コード" in s): score += 1
    return score

def merge_vertical_header_rows(row1: List[Any], row2: List[Any]) -> List[str]:
    merged: List[str] = []
    n = max(len(row1), len(row2))
    for i in range(n):
        a = norm_text(row1[i]) if i < len(row1) else ""
        b = norm_text(row2[i]) if i < len(row2) else ""
        if a and b: merged.append(f"{a}{b}")
        else: merged.append(a or b)
    return merged

def build_col_index_map_fuzzy(header_row: List[Any]) -> Dict[str,int]:
    base: Dict[str,int] = {}
    for i, cell in enumerate(header_row):
        name = norm_text(cell)
        if name and name not in base: base[name] = i
    return base

def find_process_header(rows: List[List[Any]]) -> Tuple[Optional[int], bool]:
    start = find_process_section_start(rows)
    search_range = range(max(0, start-5), min(len(rows), start+160)) if start else range(0, min(len(rows), 320))

    best_score = -1
    best_r = None
    best_two = False

    for r in search_range:
        sc = score_row_for_process_header(rows[r])
        if r + 1 < len(rows):
            merged = merge_vertical_header_rows(rows[r], rows[r+1])
            sc2 = score_row_for_process_header(merged)
            if sc2 > best_score:
                best_score = sc2
                best_r = r
                best_two = True
        if sc > best_score:
            best_score = sc
            best_r = r
            best_two = False

    if best_score >= 3 and best_r is not None:
        return best_r, best_two
    return None, False

def extract_process(rows: List[List[Any]], source_file: str, parent_assy: str, sheet_assy: str, sheet_name: str):
    header_r, two_rows = find_process_header(rows)
    if header_r is None: return []

    if two_rows and header_r + 1 < len(rows):
        header = merge_vertical_header_rows(rows[header_r], rows[header_r + 1])
        data_start = header_r + 2
    else:
        header = rows[header_r]
        data_start = header_r + 1
    
    colmap = build_col_index_map_fuzzy(header)
    
    idx_pcode = pick_col(colmap, ["工程コード", "工程ｺｰﾄﾞ", "工程"])
    idx_pname = pick_col(colmap, ["工程名・手順", "工程名", "手順"])
    idx_equip = pick_col(colmap, ["使用設備", "設備"])
    idx_people = pick_col(colmap, ["人員", "人数"])
    idx_setup = pick_col(colmap, ["準備時間(H)", "準備時間"])
    idx_std = pick_col(colmap, ["標準時間(H)", "標準時間"])
    idx_qty = pick_col(colmap, ["取数", "数量"])
    idx_rate = pick_col(colmap, ["レート", "工賃レート"])
    idx_amount = pick_col(colmap, ["金額", "加工費"])

    out = []
    r = data_start
    blank_streak = 0
    while r < len(rows):
        row = rows[r]
        row_text = joined_row(row)
        if has_notice(row_text): break
        
        pcode = safe_get(row, idx_pcode)
        if not pcode:
            blank_streak += 1
        else:
            blank_streak = 0
        if blank_streak >= 2: break
        
        if pcode in ("ｺｰﾄﾞ", "コード"):
            r += 1
            continue

        out.append({
            "SourceFile": source_file, "ParentAssy": parent_assy, "SheetAssy": sheet_assy, "SheetName": sheet_name,
            "ProcessCode": pcode, "ProcessName": safe_get(row, idx_pname),
            "Equipment": safe_get(row, idx_equip), "People": safe_get_num(row, idx_people),
            "SetupH": safe_get_num(row, idx_setup), "StdH": safe_get_num(row, idx_std),
            "Qty": safe_get_num(row, idx_qty), "Rate": safe_get_num(row, idx_rate),
            "Amount": safe_get_num(row, idx_amount),
            "ExtractedAt": dt.datetime.now().isoformat(timespec="seconds")
        })
        r += 1
    return out

# -------------------------
# Management Cost Extraction (修正: 元スクリプトのロジックを完全再現)
# -------------------------
MGMT_NOTICE_TEXT = "これより下は、行の追加をしないで下さい"
def find_management_section_start(rows: List[List[Any]]) -> Optional[int]:
    """管理費セクションの開始行を探す"""
    # 優先: B列（index 1）をチェック
    for r, row in enumerate(rows):
        if len(row) > 1:
            cell_text = norm_text(row[1])
            if MGMT_NOTICE_TEXT in cell_text or "行の追加をしないで" in cell_text:
                return r
    # 次点: 全体をチェック
    for r, row in enumerate(rows):
        row_text = joined_row(row)
        if MGMT_NOTICE_TEXT in row_text or "行の追加をしないで" in row_text:
            return r
    return None

def extract_management_cost(rows: List[List[Any]], source_file: str, parent_assy: str, sheet_assy: str, sheet_name: str):
    section_start = find_management_section_start(rows)
    if section_start is None: return []

    # 固定列位置 (K=10, M=12, N=13)
    COL_ITEM = 10; COL_EST = 12; COL_ASS = 13
    
    out = []
    blank_streak = 0
    start_offset = 3
    max_rows = 25

    for offset in range(start_offset, max_rows):
        r = section_start + offset
        if r >= len(rows): break
        row = rows[r]
        
        item = safe_get(row, COL_ITEM)
        if not item:
            blank_streak += 1
            if blank_streak >= 3: break
            continue
        else:
            blank_streak = 0
        
        # 項目名のクリーンアップと番号抽出
        item_clean = item
        item_no = ""
        
        # Regex (元スクリプト準拠)
        m = re.match(r'^\s*(\d{1,2})\s*[\.,，,．。\s]+\s*(.*)$', item)
        if m:
            item_no = m.group(1)
            item_clean = (m.group(2) or "").strip() or item
        else:
            if len(item) > 1 and item[0].isdigit() and item[1] == '.':
                parts = item.split('.', 1)
                item_no = parts[0]
                item_clean = parts[1].strip() if len(parts) > 1 else item
            elif item[0].isdigit() and len(item) > 1 and (item[1] == ' ' or item[1] == '　'):
                item_no = item[0]
                item_clean = item[1:].strip()
        
        # 番号 5~9 のみ抽出
        if item_no:
            try:
                no_int = int(item_no)
                if not (5 <= no_int <= 9): continue
            except: continue
        else:
            continue

        est = safe_get_num(row, COL_EST)
        ass = safe_get_num(row, COL_ASS)
        
        out.append({
            "SourceFile": source_file, "ParentAssy": parent_assy, "SheetAssy": sheet_assy, "SheetName": sheet_name,
            "ItemNo": item_no, "ItemName": item_clean, "EstimatePrice": est, "AssessedPrice": ass,
            "ExtractedAt": dt.datetime.now().isoformat(timespec="seconds")
        })
    return out

# -------------------------
# Main Logic
# -------------------------
def process_file(xls_path: Path):
    mats_all, procs_all, boms_all, mgmts_all, summaries = [], [], [], [], []
    book = xlrd.open_workbook(str(xls_path), formatting_info=False)
    if book.nsheets == 0: return [],[],[],[],[]

    parent_assy = extract_assy_code(read_sheet_as_rows(book.sheet_by_index(0)))
    
    for sh in book.sheets():
        if should_exclude_sheet(sh.name): continue
        rows = read_sheet_as_rows(sh)
        sheet_assy = extract_assy_code(rows) or parent_assy
        
        mats, _ = extract_material(rows, xls_path.name, parent_assy, sheet_assy, sh.name)
        procs = extract_process(rows, xls_path.name, parent_assy, sheet_assy, sh.name)
        mgmts = extract_management_cost(rows, xls_path.name, parent_assy, sheet_assy, sh.name)
        
        mats_all.extend(mats)
        procs_all.extend(procs)
        mgmts_all.extend(mgmts)
        
        for m in mats:
            child = m.get("PartCode", "")
            if child:
                boms_all.append({
                    "SourceFile": xls_path.name, "ParentAssy": sheet_assy,
                    "ChildCode": child, "ChildName": m.get("PartName",""),
                    "LineNo": m.get("LineNo",""), "FromSheetName": sh.name,
                    "ExtractedAt": m.get("ExtractedAt",""), "ChildIsAssy": False,
                    "Qty": m.get("Qty", 0) # Qtyを追加
                })
        
        summaries.append({
            "SourceFile": xls_path.name, "SheetName": sh.name, "ParentAssy": parent_assy, "SheetAssy": sheet_assy,
            "MaterialRows": len(mats), "ProcessRows": len(procs), "Warnings": ""
        })
        
    return mats_all, procs_all, boms_all, mgmts_all, summaries

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input folder")
    parser.add_argument("--output", required=True, help="Output folder")
    parser.add_argument("--db_name", default="PartsStructure.db", help="DB Filename")
    args = parser.parse_args()

    in_dir = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    db_path = out_dir / args.db_name

    if db_path.exists():
        try:
            db_path.unlink()
        except:
            print("Error: DB file is locked.")
            return

    files = list(in_dir.glob("*.xls"))
    print(f"Processing {len(files)} files...")

    all_data = {"BOM": [], "MaterialDetail": [], "ProcessDetail": [], "ManagementCost": [], "SheetSummary": []}

    for f in files:
        try:
            m, p, b, mg, s = process_file(f)
            all_data["MaterialDetail"].extend(m)
            all_data["ProcessDetail"].extend(p)
            all_data["BOM"].extend(b)
            all_data["ManagementCost"].extend(mg)
            all_data["SheetSummary"].extend(s)
            print(".", end="", flush=True)
        except Exception as e:
            print(f"x ({f.name})", end="", flush=True)

    print("\nSaving to SQLite...")
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        for tbl, rows in all_data.items():
            if rows:
                df = pd.DataFrame(rows)
                # Key Columns String Conversion
                cols = df.columns
                for c in ["ParentAssy", "ChildCode", "PartCode", "ProcessCode"]:
                    if c in cols: df[c] = df[c].astype(str)
                
                df.to_sql(tbl, conn, if_exists='replace', index=False)
                print(f" - {tbl}: {len(df)} rows")
                
                if tbl == "BOM": cursor.execute("CREATE INDEX idx_bom_p ON BOM(ParentAssy)")
                elif tbl == "MaterialDetail": cursor.execute("CREATE INDEX idx_mat_p ON MaterialDetail(PartCode)")
                elif tbl == "ProcessDetail": cursor.execute("CREATE INDEX idx_proc_p ON ProcessDetail(ParentAssy)")
            else:
                print(f" - {tbl}: 0 rows (Skipped)")
        conn.commit()
        print(f"Done! DB saved to: {db_path}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()