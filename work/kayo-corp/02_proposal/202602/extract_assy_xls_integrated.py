#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_assy_xls_integrated.py

統合版: Excel抽出 + 再帰的BOM展開を1つのスクリプトで実行

機能:
- v8の全機能を維持（MaterialDetail, ProcessDetail, BOM, SheetSummary出力）
- 再帰的BOM展開機能を統合（Recursive_BOM_Matrix.csv出力）
- MaterialDetailの全項目を保持
- Excelピボットテーブルで階層的に集計可能

実行例:
  python extract_assy_xls_integrated.py --input "C:\\Temp\\BOM_XLS" --output "C:\\Temp\\BOM_OUT"
"""

from __future__ import annotations

import argparse
import datetime as dt
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set

import xlrd
import pandas as pd


# -------------------------
# Utility
# -------------------------

def norm_text(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, float):
        if x.is_integer():
            return str(int(x))
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
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = norm_text(v)
    if s == "":
        return None
    try:
        return float(s.replace(",", ""))
    except Exception:
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
# Sheet exclusion
# -------------------------

EXCLUDE_SHEET_NAME_CONTAINS = [
    "再検討依頼書",
    "プレス（組立品）",
    "プレス（単品）",
    "成形（組立品）",
    "成形（単品）",
]

def should_exclude_sheet(sheet_name: str) -> bool:
    return any(k in sheet_name for k in EXCLUDE_SHEET_NAME_CONTAINS)


# -------------------------
# ASSY code extraction
# -------------------------

ASSY_LABELS = ["部品コード", "製品コード", "品目コード", "品目ｺｰﾄﾞ"]

def looks_like_assy_code(s: str) -> bool:
    if not s:
        return False
    if s in ("部品名", "品名", "名称"):
        return False
    has_alnum = any(ch.isalnum() for ch in s)
    return has_alnum and len(s) >= 6

def extract_assy_code(rows: List[List[Any]]) -> str:
    for lab in ASSY_LABELS:
        pos = find_cell_pos(rows, lab, row_limit=40)
        if not pos:
            continue
        r, c = pos
        for dc in (1, 2, 3):
            if c + dc < len(rows[r]):
                v = norm_text(rows[r][c + dc])
                if looks_like_assy_code(v):
                    return v
        for dr in (1, 2, 3):
            if r + dr < len(rows):
                v = norm_text(rows[r + dr][c])
                if looks_like_assy_code(v):
                    return v
    return ""


# -------------------------
# Common terminators
# -------------------------

NOTICE_KEYWORD_1 = "これより下は"
NOTICE_KEYWORD_2 = "行の追加"

def has_notice(row_text: str) -> bool:
    return (NOTICE_KEYWORD_1 in row_text) and (NOTICE_KEYWORD_2 in row_text)


# -------------------------
# Material extraction
# -------------------------

PROCESS_BLOCK_HINTS = [
    "工程費明細", "加工費明細", "工程明細",
    "工程ｺｰﾄﾞ", "工程コード", "工程名・手順", "工程名", "使用設備",
    "標準時間", "準備時間", "レート", "金額"
]

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
    # 完全一致を優先
    for c in candidates:
        if c in colmap:
            return colmap[c]
    
    # 部分一致（候補が列名に含まれる）
    for c in candidates:
        for colname, idx in colmap.items():
            if c in colname:
                return idx
    
    # 逆方向の部分一致（列名が候補に含まれる）
    for colname, idx in colmap.items():
        for c in candidates:
            if colname in c and len(colname) >= 3:  # 短すぎる列名は除外
                return idx
    
    return None

def pick_col_fuzzy(colmap: Dict[str,int], keywords: List[str]) -> Optional[int]:
    """
    キーワードベースのファジーマッチング
    例: ["使用数", "所要量"] → "使用数・所要量"にマッチ
    """
    for colname, idx in colmap.items():
        if all(kw in colname for kw in keywords):
            return idx
    return None

def extract_material(rows: List[List[Any]], source_file: str, parent_assy: str, sheet_assy: str, sheet_name: str, debug: bool = False):
    header_r = find_material_header(rows)
    if header_r is None:
        return [], ""

    header = rows[header_r]
    colmap = build_col_index_map(header)

    pattern = "A" if any(k in colmap for k in ["材料・規格・グレード・色番", "展開寸法", "所要量"]) else "B"

    # デバッグ出力
    if debug and pattern == "B":
        import sys
        print(f"\n[DEBUG] {source_file}:{sheet_name} Pattern=B", file=sys.stderr)
        print(f"[DEBUG] Available columns: {list(colmap.keys())}", file=sys.stderr)

    idx_line = pick_col(colmap, ["行番", "行", "No"])
    idx_partcode = pick_col(colmap, ["部品コード", "品目コード", "品目ｺｰﾄﾞ"])
    idx_partname = pick_col(colmap, ["部品名", "名称"])
    idx_unit = pick_col(colmap, ["単位"])
    idx_supplyno = pick_col(colmap, ["支給", "支給区分"])
    
    # Qty候補を広く取得
    idx_req = pick_col(colmap, ["所要量", "必要量", "所与量"])
    idx_qty = pick_col(colmap, ["取数", "数量", "使用数", "使用数量"])

    # idx_unitprice is defined above (before Qty sampling)
    # idx_unitprice = pick_col(colmap, ["単価"])  # moved

    
    # 「使用数・所要量」のようなハイブリッド列名にファジーマッチング
    idx_qty_alt = pick_col(colmap, [
        "使用数・所要量", 
        "使用数・所与量",
        "使用数･所要量",
    ])
    if idx_qty_alt is None:
        # ファジーマッチング: "使用数" AND "所要量" を両方含む列
        idx_qty_alt = pick_col_fuzzy(colmap, ["使用数", "所要量"])
    
    # Pattern=Bで、idx_reqもidx_qtyもidx_qty_altも見つからない場合、
    # データ行をサンプリングして数値が入っている列を探す
    if pattern == "B" and idx_req is None and idx_qty is None and idx_qty_alt is None:
        # ヘッダーの後の数行をサンプリング
        for sample_r in range(header_r + 1, min(header_r + 10, len(rows))):
            sample_row = rows[sample_r]
            partcode = safe_get(sample_row, idx_partcode)
            if partcode == "":
                continue
            # 単価列の左側3列を探索（通常、Qtyは単価の前にある）
            if idx_unitprice is not None:
                for offset in range(1, 4):
                    test_idx = idx_unitprice - offset
                    if test_idx >= 0:
                        test_val = safe_get_num(sample_row, test_idx)
                        if test_val is not None and test_val > 0:
                            idx_qty_alt = test_idx
                            if debug:
                                print(f"[DEBUG] Found Qty column by sampling: idx={test_idx}, val={test_val}", file=sys.stderr)
                            break
            if idx_qty_alt is not None:
                break
    
    # デバッグ出力
    if debug and pattern == "B":
        print(f"[DEBUG] idx_req={idx_req}, idx_qty={idx_qty}, idx_qty_alt={idx_qty_alt}", file=sys.stderr)
        if idx_qty_alt is None:
            print(f"[DEBUG] Header columns: {list(colmap.keys())}", file=sys.stderr)
    
    idx_unitprice = pick_col(colmap, ["単価"])
    idx_self_cost = pick_col(colmap, ["自給材費", "自給材料費"])
    idx_supply_cost = pick_col(colmap, ["支給材費", "支給材料費", "支給材料", "支給費"])
    
    # 材料費関連
    idx_raw_amount_a = pick_col(colmap, ["材料費計", "材料費合計", "材料費計 "])
    idx_raw_amount_b = pick_col(colmap, ["金額", "金額(円)", "金額（円）"])
    
    # 加工費（ASSY展開時の加工費）
    idx_assy_proc = pick_col(colmap, ["加工費", "加工賃", "加工費計", "加工費(円)", "加工費（円）"])

    out: List[Dict[str,Any]] = []
    blank_line_no_streak = 0

    r = header_r + 1
    while r < len(rows):
        row = rows[r]
        row_text = joined_row(row)

        if has_notice(row_text):
            break
        if any(h in row_text for h in PROCESS_BLOCK_HINTS):
            break

        line_no = safe_get(row, idx_line)
        if line_no == "":
            blank_line_no_streak += 1
        else:
            blank_line_no_streak = 0
        if blank_line_no_streak >= 2:
            break

        partcode = safe_get(row, idx_partcode)
        partname = safe_get(row, idx_partname)

        if partcode == "" and partname == "":
            r += 1
            continue

        # Qtyの取得（優先順位: 所要量 > 使用数・所要量 > 取数/数量）
        req = safe_get_num(row, idx_req)
        q = safe_get_num(row, idx_qty)
        q_alt = safe_get_num(row, idx_qty_alt)
        qty_merged = req if req is not None else (q_alt if q_alt is not None else q)

        unit_price = safe_get_num(row, idx_unitprice)
        self_cost = safe_get_num(row, idx_self_cost)
        supply_cost = safe_get_num(row, idx_supply_cost)
        
        # RawAmount（材料費）の取得
        raw_amount = safe_get_num(row, idx_raw_amount_a)
        if raw_amount is None:
            raw_amount = safe_get_num(row, idx_raw_amount_b)
        
        # AssyRolledProcessCost（加工費）の取得
        assy_proc_cost = safe_get_num(row, idx_assy_proc)

        # Amount（金額合計）の計算
        amount = raw_amount
        if amount is None:
            if (self_cost is not None) or (supply_cost is not None):
                amount = (self_cost or 0.0) + (supply_cost or 0.0)
            elif (unit_price is not None) and (qty_merged is not None):
                amount = unit_price * qty_merged
        
        # 加工費を含む場合は合計に加算
        if assy_proc_cost is not None and amount is not None:
            amount = amount + assy_proc_cost
        elif assy_proc_cost is not None and amount is None:
            amount = assy_proc_cost

        out.append({
            "SourceFile": source_file,
            "ParentAssy": parent_assy,
            "SheetAssy": sheet_assy,
            "SheetName": sheet_name,
            "LineNo": line_no,
            "PartCode": partcode,
            "PartName": partname,
            "UnitNo": safe_get(row, idx_unit),
            "SupplyNo": safe_get(row, idx_supplyno),
            "Qty": qty_merged,
            "UnitPrice": unit_price,
            "SelfSuppliedCost": self_cost,
            "SupplyCost": supply_cost,
            "RawAmount": raw_amount,
            "AssyRolledProcessCost": assy_proc_cost,
            "Amount": amount,
            "Pattern": pattern,
            "ExtractedAt": dt.datetime.now().isoformat(timespec="seconds"),
        })
        r += 1

    return out, pattern


# -------------------------
# Process extraction
# -------------------------

PROCESS_SECTION_MARKERS = ["工程費明細", "加工費明細", "工程明細", "加工費"]

def find_process_section_start(rows: List[List[Any]]) -> Optional[int]:
    for mk in PROCESS_SECTION_MARKERS:
        pos = find_cell_pos(rows, mk)
        if pos:
            return pos[0]
    return None

def score_row_for_process_header(row: List[Any]) -> int:
    s = compact(joined_row(row))
    if not s:
        return 0
    score = 0
    if "工程" in s:
        score += 2
    if ("工程名" in s) or ("手順" in s):
        score += 2
    if ("使用設備" in s) or ("設備" in s):
        score += 1
    if ("レート" in s) or ("金額" in s):
        score += 1
    if ("標準時間" in s) or ("準備時間" in s):
        score += 1
    if ("工程コード" in s) or ("工程ｺｰﾄﾞ" in s):
        score += 2
    else:
        if ("工程" in s and "コード" in s):
            score += 1
    return score

def combine_horizontal_headers(header_row: List[Any]) -> List[str]:
    cells = [norm_text(c) for c in header_row]
    out = cells[:]
    for i in range(len(cells)-1):
        a = compact(cells[i])
        b = compact(cells[i+1])
        if a == "工程" and (b == "ｺｰﾄﾞ" or b == "コード"):
            out[i] = "工程ｺｰﾄﾞ"
        if a == "工程名" and b == "手順":
            out[i] = "工程名・手順"
    return out

def merge_vertical_header_rows(row1: List[Any], row2: List[Any]) -> List[str]:
    merged: List[str] = []
    n = max(len(row1), len(row2))
    for i in range(n):
        a = norm_text(row1[i]) if i < len(row1) else ""
        b = norm_text(row2[i]) if i < len(row2) else ""
        if a and b:
            merged.append(f"{a}{b}")
        else:
            merged.append(a or b)
    return merged

def build_col_index_map_fuzzy(header_row: List[Any]) -> Dict[str,int]:
    base: Dict[str,int] = {}
    for i, cell in enumerate(header_row):
        name = norm_text(cell)
        if name and name not in base:
            base[name] = i
    combined = combine_horizontal_headers(header_row)
    for i, name in enumerate(combined):
        if name and name not in base:
            base[name] = i
    return base

def find_process_header(rows: List[List[Any]], log: Optional[logging.Logger]=None, debug: bool=False, sheet_tag: str="") -> Tuple[Optional[int], bool]:
    start = find_process_section_start(rows)
    ranges = []
    if start is not None:
        ranges.append((max(0, start-5), min(len(rows), start+160)))
    ranges.append((0, min(len(rows), 320)))

    best_score = -1
    best_r: Optional[int] = None
    best_two = False
    candidates: List[Tuple[int,int,str]] = []

    for (a, b) in ranges:
        for r in range(a, b):
            sc = score_row_for_process_header(rows[r])
            if sc > 0:
                candidates.append((sc, r, joined_row(rows[r])))

            if r + 1 < len(rows):
                merged = merge_vertical_header_rows(rows[r], rows[r+1])
                sc2 = score_row_for_process_header(merged)
                if sc2 > 0:
                    candidates.append((sc2, r, joined_row(merged) + " (merged2rows)"))
                if sc2 > best_score:
                    best_score = sc2
                    best_r = r
                    best_two = True

            if sc > best_score:
                best_score = sc
                best_r = r
                best_two = False

    if debug and log:
        candidates.sort(key=lambda x: (-x[0], x[1]))
        for sc, r, s in candidates[:10]:
            log.info("[DBG] %s process_header_candidate score=%d row=%d: %s", sheet_tag, sc, r, s[:300])

    if best_score >= 3 and best_r is not None:
        return best_r, best_two
    return None, False

def extract_process(rows: List[List[Any]], source_file: str, parent_assy: str, sheet_assy: str, sheet_name: str,
                    log: Optional[logging.Logger]=None, debug: bool=False):
    header_r, two_rows = find_process_header(rows, log=log, debug=debug, sheet_tag=f"{source_file}:{sheet_name}")
    if header_r is None:
        return []

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
    idx_people = pick_col(colmap, ["人員", "人数", "人", "作業者数", "作業者"])
    idx_setup = pick_col(colmap, ["準備時間(H)", "準備時間", "準備(H)"])
    idx_std = pick_col(colmap, ["標準時間(H)", "標準時間", "標準(H)"])
    idx_qty = pick_col(colmap, ["取数", "数量"])
    idx_rate = pick_col(colmap, ["レート", "工賃レート", "単価"])
    idx_amount = pick_col(colmap, ["金額", "加工費", "加工費計"])

    out: List[Dict[str,Any]] = []
    blank_pcode_streak = 0

    r = data_start
    while r < len(rows):
        row = rows[r]
        row_text = joined_row(row)

        if has_notice(row_text):
            break

        pcode = safe_get(row, idx_pcode)
        pname = safe_get(row, idx_pname)

        if pcode == "":
            blank_pcode_streak += 1
        else:
            blank_pcode_streak = 0
        if blank_pcode_streak >= 2:
            break

        if (pcode in ("ｺｰﾄﾞ", "コード")) and (pname == ""):
            r += 1
            continue

        if pcode == "" and pname == "":
            r += 1
            continue

        out.append({
            "SourceFile": source_file,
            "ParentAssy": parent_assy,
            "SheetAssy": sheet_assy,
            "SheetName": sheet_name,
            "ProcessCode": pcode,
            "ProcessName": pname,
            "Equipment": safe_get(row, idx_equip),
            "People": safe_get_num(row, idx_people),
            "SetupH": safe_get_num(row, idx_setup),
            "StdH": safe_get_num(row, idx_std),
            "Qty": safe_get_num(row, idx_qty),
            "Rate": safe_get_num(row, idx_rate),
            "Amount": safe_get_num(row, idx_amount),
            "ExtractedAt": dt.datetime.now().isoformat(timespec="seconds"),
        })
        r += 1

    return out


# -------------------------
# Management Cost extraction
# -------------------------

MGMT_SECTION_MARKERS = ["管理費・運賃等", "管理費", "運賃等", "管理費・運賃", "管理費運賃"]
MGMT_NOTICE_TEXT = "これより下は、行の追加をしないで下さい"

def find_management_section_start(rows: List[List[Any]]) -> Optional[int]:
    """
    管理費セクションの開始行を探す
    「＊これより下は、行の追加をしないで下さい」というテキストを探す
    """
    for r, row in enumerate(rows):
        # B列（インデックス1）をチェック
        if len(row) > 1:
            cell_text = norm_text(row[1])
            if MGMT_NOTICE_TEXT in cell_text or "行の追加をしないで" in cell_text:
                return r
    
    # 見つからない場合、全体から探索
    for r, row in enumerate(rows):
        row_text = joined_row(row)
        if MGMT_NOTICE_TEXT in row_text or "行の追加をしないで" in row_text:
            return r
    
    return None

def extract_management_cost(rows: List[List[Any]], source_file: str, parent_assy: str, sheet_assy: str, sheet_name: str, debug: bool = False):
    """
    管理費・運賃等のセクションを抽出
    
    構造:
    - 「＊これより下は、行の追加をしないで下さい」という文字がB列にある
    - その行から数行下に項目がある
    - 項目はK列（インデックス10）
    - 見積価格はM列（インデックス12）
    """
    section_start = find_management_section_start(rows)
    if section_start is None:
        if debug:
            import sys
            print(f"[DEBUG] {source_file}:{sheet_name} - Management section marker not found", file=sys.stderr)
        return []
    
    if debug:
        import sys
        print(f"[DEBUG] {source_file}:{sheet_name} - Management section marker found at row {section_start}", file=sys.stderr)
    
    # 固定列位置
    COL_ITEM = 10      # K列（項目）
    COL_ESTIMATE = 12  # M列（見積価格）
    COL_ASSESSED = 13  # N列（査定価格、あれば）
    
    out: List[Dict[str, Any]] = []
    
    # セクション開始から3～25行後までをデータ行として読み込み
    # （通常、注意書きの直後1-2行は空白またはヘッダー）
    start_offset = 3
    max_rows = 25
    
    blank_streak = 0
    for offset in range(start_offset, max_rows):
        r = section_start + offset
        if r >= len(rows):
            break
        
        row = rows[r]
        
        # K列（項目）を取得
        item = safe_get(row, COL_ITEM)
        
        # 空白行のカウント
        if item == "":
            blank_streak += 1
            if blank_streak >= 3:  # 3行連続空白で終了
                break
            continue
        else:
            blank_streak = 0
        
        # 項目名のクリーンアップ（番号を抽出）
        item_clean = item
        item_no = ""

        if item:
            # 先頭の番号を抽出（例: "5,表面処理", "5. 表面処理", "5 表面処理", "10,小計" など）
            m = re.match(r'^\s*(\d{1,2})\s*[\.,，,．。\s]+\s*(.*)$', item)
            if m:
                item_no = m.group(1)
                item_clean = (m.group(2) or "").strip() or item
            else:
                # "1." のような形式
                if len(item) > 1 and item[0].isdigit() and item[1] == '.':
                    parts = item.split('.', 1)
                    item_no = parts[0]
                    item_clean = parts[1].strip() if len(parts) > 1 else item
                # "1 " / "1　" のような形式
                elif item[0].isdigit() and len(item) > 1 and (item[1] == ' ' or item[1] == '　'):
                    item_no = item[0]
                    item_clean = item[1:].strip()

        # 要望: 5.表面処理 ～ 9.その他（改善効果）のみ抽出
        if item_no:
            try:
                no_int = int(item_no)
                if not (5 <= no_int <= 9):
                    continue
            except ValueError:
                # 番号が数値化できない場合は除外
                continue
        else:
            # 番号が取れない行は除外（想定外の行を混ぜないため）
            continue
        
        # M列（見積価格）とN列（査定価格）を取得
        estimate_price = safe_get_num(row, COL_ESTIMATE)
        assessed_price = safe_get_num(row, COL_ASSESSED)
        
        if debug:
            import sys
            print(f"[DEBUG] Row {r}: Item=[{item}] -> No={item_no}, Name={item_clean}, Est={estimate_price}, Ass={assessed_price}", file=sys.stderr)
        
        out.append({
            "SourceFile": source_file,
            "ParentAssy": parent_assy,
            "SheetAssy": sheet_assy,
            "SheetName": sheet_name,
            "ItemNo": item_no,
            "ItemName": item_clean,
            "EstimatePrice": estimate_price,
            "AssessedPrice": assessed_price,
            "ExtractedAt": dt.datetime.now().isoformat(timespec="seconds"),
        })
    
    if debug:
        import sys
        print(f"[DEBUG] Extracted {len(out)} management cost items", file=sys.stderr)
    
    return out


# -------------------------
# File processing
# -------------------------

def process_file(xls_path: Path, log: logging.Logger, debug: bool):
    material_all: List[Dict[str,Any]] = []
    process_all: List[Dict[str,Any]] = []
    bom_all: List[Dict[str,Any]] = []
    mgmt_all: List[Dict[str,Any]] = []
    sheet_assy_codes: List[str] = []
    sheet_summaries: List[Dict[str,Any]] = []

    book = xlrd.open_workbook(str(xls_path), formatting_info=False)
    if book.nsheets == 0:
        return material_all, process_all, bom_all, mgmt_all, sheet_assy_codes, sheet_summaries

    parent_assy = extract_assy_code(read_sheet_as_rows(book.sheet_by_index(0)))

    for si in range(book.nsheets):
        sh = book.sheet_by_index(si)

        try:
            if getattr(sh, "visibility", 0) != 0:
                continue
        except Exception:
            pass

        if should_exclude_sheet(sh.name):
            continue

        rows = read_sheet_as_rows(sh)

        sheet_assy = extract_assy_code(rows) or parent_assy
        sheet_assy_codes.append(sheet_assy)

        mats, _ = extract_material(rows, xls_path.name, parent_assy, sheet_assy, sh.name, debug=debug)
        procs = extract_process(rows, xls_path.name, parent_assy, sheet_assy, sh.name, log=log, debug=debug)
        mgmts = extract_management_cost(rows, xls_path.name, parent_assy, sheet_assy, sh.name, debug=debug)

        material_all.extend(mats)
        process_all.extend(procs)
        mgmt_all.extend(mgmts)

        for m in mats:
            child = m.get("PartCode", "")
            if child:
                bom_all.append({
                    "SourceFile": xls_path.name,
                    "ParentAssy": sheet_assy,
                    "ChildCode": child,
                    "ChildName": m.get("PartName",""),
                    "LineNo": m.get("LineNo",""),
                    "FromSheetName": sh.name,
                    "ExtractedAt": m.get("ExtractedAt",""),
                    "ChildIsAssy": None,
                })

        last_line = ""
        for x in reversed(mats):
            v = (x.get("LineNo","") or "")
            if v != "":
                last_line = v
                break

        last_pcode = ""
        for x in reversed(procs):
            v = (x.get("ProcessCode","") or "")
            if v != "":
                last_pcode = v
                break

        warn = []
        for x in mats:
            pc = (x.get("PartCode","") or "")
            pn = (x.get("PartName","") or "")
            if ("工程" in pc) or ("工程" in pn) or ("工程名" in pc) or ("工程名" in pn) or ("レート" in pc) or ("標準時間" in pc):
                warn.append("MaterialContainsProcessText")
                break

        sheet_summaries.append({
            "SourceFile": xls_path.name,
            "SheetName": sh.name,
            "ParentAssy": parent_assy,
            "SheetAssy": sheet_assy,
            "MaterialRows": len(mats),
            "ProcessRows": len(procs),
            "MaterialLastLineNo": last_line,
            "ProcessLastCode": last_pcode,
            "Warnings": ";".join(warn),
        })

        if debug:
            log.info("[DBG] %s:%s parent_assy=%s sheet_assy=%s mats=%d procs=%d mgmts=%d",
                     xls_path.name, sh.name, parent_assy, sheet_assy, len(mats), len(procs), len(mgmts))

    return material_all, process_all, bom_all, mgmt_all, sheet_assy_codes, sheet_summaries


# -------------------------
# Recursive BOM Matrix Generation
# -------------------------

def safe_float(val) -> float:
    """安全にfloatに変換（NaN, Noneを0.0に）"""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

def safe_str(val) -> str:
    """安全に文字列に変換"""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val).strip()

def generate_recursive_bom_matrix(
    bom_df: pd.DataFrame,
    material_df: pd.DataFrame,
    process_df: pd.DataFrame,
    mgmt_df: Optional[pd.DataFrame],
    output_path: Path,
    log: logging.Logger
) -> int:
    """
    再帰的なBOM階層マトリックスを生成
    """
    
    if bom_df.empty:
        log.warning("BOM is empty. Skipping recursive matrix generation.")
        return 0
    
    # ASSY部品のセットを作成
    assy_set: Set[str] = set()
    for _, row in bom_df.iterrows():
        if row.get('ChildIsAssy', False):
            assy_set.add(safe_str(row['ChildCode']))
    
    log.info(f"Identified {len(assy_set)} ASSY components")
    
    # 材料データを親コード（SheetAssy）でグループ化
    mat_dict: Dict[str, List[Dict]] = {}
    for _, row in material_df.iterrows():
        parent = safe_str(row.get('SheetAssy', ''))
        if parent not in mat_dict:
            mat_dict[parent] = []
        mat_dict[parent].append(row.to_dict())
    
    # 工程データを親コード（SheetAssy）でグループ化
    proc_dict: Dict[str, List[Dict]] = {}
    for _, row in process_df.iterrows():
        parent = safe_str(row.get('SheetAssy', ''))
        if parent not in proc_dict:
            proc_dict[parent] = []
        proc_dict[parent].append(row.to_dict())

    # 管理費データを親コード（SheetAssy）でグループ化
    mgmt_dict: Dict[str, List[Dict]] = {}
    if mgmt_df is not None and (not mgmt_df.empty):
        for _, row in mgmt_df.iterrows():
            parent = safe_str(row.get('SheetAssy', ''))
            if parent not in mgmt_dict:
                mgmt_dict[parent] = []
            mgmt_dict[parent].append(row.to_dict())

    # BOM親子マップ
    bom_map: Dict[Tuple[str, str], bool] = {}
    for _, row in bom_df.iterrows():
        parent = safe_str(row['ParentAssy'])
        child = safe_str(row['ChildCode'])
        is_assy = row.get('ChildIsAssy', False)
        bom_map[(parent, child)] = is_assy
    
    def get_recursive_bom(
        parent_code: str,
        level: int = 1,
        parent_path: str = "",
        visited: Optional[Set[str]] = None
    ) -> List[Dict[str, Any]]:
        """再帰的にBOMを展開"""
        if visited is None:
            visited = set()
        
        if parent_code in visited:
            log.warning(f"Circular reference detected: {parent_code} already visited in path {parent_path}")
            return []
        
        new_visited = visited | {parent_code}
        results: List[Dict[str, Any]] = []
        
        path_str = f"{parent_path}/{parent_code}" if parent_path else parent_code
        
        # A. 材料（Parts/ASSY）の展開
        children = mat_dict.get(parent_code, [])
        for mat_row in children:
            child_code = safe_str(mat_row.get('PartCode', '')).strip()
            if not child_code:
                continue
            
            is_assy = bom_map.get((parent_code, child_code), False)
            
            # MaterialDetailの全項目を取得
            source_file = safe_str(mat_row.get('SourceFile', ''))
            parent_assy = safe_str(mat_row.get('ParentAssy', ''))
            sheet_assy = safe_str(mat_row.get('SheetAssy', ''))
            sheet_name = safe_str(mat_row.get('SheetName', ''))
            line_no = safe_str(mat_row.get('LineNo', ''))
            part_code = safe_str(mat_row.get('PartCode', child_code))
            part_name = safe_str(mat_row.get('PartName', child_code))
            unit_no = safe_str(mat_row.get('UnitNo', ''))
            supply_no = safe_str(mat_row.get('SupplyNo', ''))
            qty = safe_float(mat_row.get('Qty'))
            unit_price = safe_float(mat_row.get('UnitPrice'))
            self_cost = safe_float(mat_row.get('SelfSuppliedCost'))
            supply_cost = safe_float(mat_row.get('SupplyCost'))
            raw_amount = safe_float(mat_row.get('RawAmount'))
            assy_rolled_proc_cost = safe_float(mat_row.get('AssyRolledProcessCost'))
            amount = safe_float(mat_row.get('Amount'))
            pattern = safe_str(mat_row.get('Pattern', ''))
            extracted_at = safe_str(mat_row.get('ExtractedAt', ''))
            
            item_type = 'ASSY' if is_assy else 'Part'
            
            node = {
                'Level': level,
                'ParentCode': parent_code,
                'ItemCode': child_code,
                'ItemName': part_name,
                'ItemType': item_type,
                'Path': path_str,
                'SourceFile': source_file,
                'ParentAssy': parent_assy,
                'SheetAssy': sheet_assy,
                'SheetName': sheet_name,
                'LineNo': line_no,
                'PartCode': part_code,
                'PartName': part_name,
                'UnitNo': unit_no,
                'SupplyNo': supply_no,
                'Qty': qty,
                'UnitPrice': unit_price,
                'SelfSuppliedCost': self_cost,
                'SupplyCost': supply_cost,
                'RawAmount': raw_amount,
                'AssyRolledProcessCost': assy_rolled_proc_cost,
                'Amount': amount,
                'Pattern': pattern,
                'ExtractedAt': extracted_at,
                'ProcessCode': '',
                'ProcessName': '',
                'Equipment': '',
                'People': 0,
                'SetupH': 0,
                'StdH': 0,
                'Rate': 0,
                'MgmtItemNo': '',
                'MgmtEstimatePrice': 0,
                'MgmtAssessedPrice': 0,
            }
            
            results.append(node)
            
            if is_assy and child_code in mat_dict:
                child_results = get_recursive_bom(child_code, level + 1, path_str, new_visited)
                results.extend(child_results)
        
        # B. 工程の展開
        processes = proc_dict.get(parent_code, [])
        for proc_row in processes:
            proc_code = safe_str(proc_row.get('ProcessCode', ''))
            proc_name = safe_str(proc_row.get('ProcessName', ''))
            if not proc_code and not proc_name:
                continue
            
            source_file = safe_str(proc_row.get('SourceFile', ''))
            parent_assy = safe_str(proc_row.get('ParentAssy', ''))
            sheet_assy = safe_str(proc_row.get('SheetAssy', ''))
            sheet_name = safe_str(proc_row.get('SheetName', ''))
            equipment = safe_str(proc_row.get('Equipment', ''))
            people = safe_float(proc_row.get('People'))
            setup_h = safe_float(proc_row.get('SetupH'))
            std_h = safe_float(proc_row.get('StdH'))
            qty = safe_float(proc_row.get('Qty'))
            rate = safe_float(proc_row.get('Rate'))
            proc_amount = safe_float(proc_row.get('Amount'))
            extracted_at = safe_str(proc_row.get('ExtractedAt', ''))
            
            node = {
                'Level': level,
                'ParentCode': parent_code,
                'ItemCode': proc_code,
                'ItemName': proc_name,
                'ItemType': 'Process',
                'Path': path_str,
                'SourceFile': source_file,
                'ParentAssy': parent_assy,
                'SheetAssy': sheet_assy,
                'SheetName': sheet_name,
                'LineNo': '',
                'PartCode': proc_code,
                'PartName': proc_name,
                'UnitNo': '',
                'SupplyNo': '',
                'Qty': qty,
                'UnitPrice': 0,
                'SelfSuppliedCost': 0,
                'SupplyCost': 0,
                'RawAmount': 0,
                'AssyRolledProcessCost': proc_amount,
                'Amount': proc_amount,
                'Pattern': '',
                'ExtractedAt': extracted_at,
                'ProcessCode': proc_code,
                'ProcessName': proc_name,
                'Equipment': equipment,
                'People': people,
                'SetupH': setup_h,
                'StdH': std_h,
                'Rate': rate,
                'MgmtItemNo': '',
                'MgmtEstimatePrice': 0,
                'MgmtAssessedPrice': 0,
            }
            
            results.append(node)
        

        # C. 管理費・運賃等の展開
        mgmts = mgmt_dict.get(parent_code, [])
        for mg in mgmts:
            item_no = safe_str(mg.get('ItemNo', ''))
            item_name = safe_str(mg.get('ItemName', ''))
            if not item_no and not item_name:
                continue

            source_file = safe_str(mg.get('SourceFile', ''))
            parent_assy = safe_str(mg.get('ParentAssy', ''))
            sheet_assy = safe_str(mg.get('SheetAssy', ''))
            sheet_name = safe_str(mg.get('SheetName', ''))
            est = safe_float(mg.get('EstimatePrice'))
            ass = safe_float(mg.get('AssessedPrice'))
            extracted_at = safe_str(mg.get('ExtractedAt', ''))

            # ItemCode は「MGMT-<No>」を優先（Noが無い場合は項目名）
            item_code = f"MGMT-{item_no}" if item_no else (item_name or "MGMT")

            node = {
                'Level': level,
                'ParentCode': parent_code,
                'ItemCode': item_code,
                'ItemName': item_name or item_code,
                'ItemType': 'ManagementCost',
                'Path': path_str,
                'SourceFile': source_file,
                'ParentAssy': parent_assy,
                'SheetAssy': sheet_assy,
                'SheetName': sheet_name,
                'LineNo': '',
                'PartCode': item_code,
                'PartName': item_name or item_code,
                'UnitNo': '',
                'SupplyNo': '',
                'Qty': 0,
                'UnitPrice': 0,
                'SelfSuppliedCost': 0,
                'SupplyCost': 0,
                'RawAmount': 0,
                'AssyRolledProcessCost': 0,
                'Amount': est if est != 0 else ass,
                'Pattern': '',
                'ExtractedAt': extracted_at,
                'ProcessCode': '',
                'ProcessName': '',
                'Equipment': '',
                'People': 0,
                'SetupH': 0,
                'StdH': 0,
                'Rate': 0,
                'MgmtItemNo': item_no,
                'MgmtEstimatePrice': est,
                'MgmtAssessedPrice': ass,
            }

            results.append(node)

        return results
    
    # ルートノード（トップレベルの親）を特定
    all_parents = set(bom_df['ParentAssy'].unique())
    all_children = set(bom_df['ChildCode'].unique())
    roots = all_parents - all_children
    
    if not roots:
        roots = {bom_df['ParentAssy'].iloc[0]}
        log.warning("No clear root found. Using first ParentAssy as root.")
    
    log.info(f"Found {len(roots)} root assembly(ies): {roots}")
    
    # 階層全体を構築
    full_hierarchy: List[Dict[str, Any]] = []
    
    for root in sorted(roots):
        root_node = {
            'Level': 0,
            'ParentCode': '',
            'ItemCode': root,
            'ItemName': root,
            'ItemType': 'Root',
            'Path': '',
            'SourceFile': '',
            'ParentAssy': '',
            'SheetAssy': root,
            'SheetName': '',
            'LineNo': '',
            'PartCode': root,
            'PartName': root,
            'UnitNo': '',
            'SupplyNo': '',
            'Qty': 0,
            'UnitPrice': 0,
            'SelfSuppliedCost': 0,
            'SupplyCost': 0,
            'RawAmount': 0,
            'AssyRolledProcessCost': 0,
            'Amount': 0,
            'Pattern': '',
            'ExtractedAt': '',
            'ProcessCode': '',
            'ProcessName': '',
            'Equipment': '',
            'People': 0,
            'SetupH': 0,
            'StdH': 0,
            'Rate': 0,
            'MgmtItemNo': '',
            'MgmtEstimatePrice': 0,
            'MgmtAssessedPrice': 0,
        }
        full_hierarchy.append(root_node)
        
        child_results = get_recursive_bom(root)
        full_hierarchy.extend(child_results)
    
    if full_hierarchy:
        result_df = pd.DataFrame(full_hierarchy)
        
        # 列の順序を整理
        col_order = [
            'Level', 'ParentCode', 'ItemCode', 'ItemName', 'ItemType', 'Path',
            'SourceFile', 'ParentAssy', 'SheetAssy', 'SheetName',
            'LineNo', 'PartCode', 'PartName', 
            'UnitNo', 'SupplyNo', 'Qty', 'UnitPrice',
            'SelfSuppliedCost', 'SupplyCost', 'RawAmount', 'AssyRolledProcessCost',
            'Amount', 'Pattern', 'ExtractedAt',
            'ProcessCode', 'ProcessName', 'Equipment', 'People', 
            'SetupH', 'StdH', 'Rate',
            'MgmtItemNo', 'MgmtEstimatePrice', 'MgmtAssessedPrice'
        ]
        
        available_cols = [c for c in col_order if c in result_df.columns]
        result_df = result_df[available_cols]
        
        result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        log.info(f"Recursive BOM Matrix created: {output_path} ({len(result_df)} rows)")
        
        return len(result_df)
    else:
        log.warning("No hierarchy data generated.")
        return 0


# -------------------------
# Main
# -------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="folder containing .xls")
    ap.add_argument("--output", required=True, help="output folder")
    ap.add_argument("--recursive", action="store_true", help="scan subfolders")
    ap.add_argument("--log", default="", help="log file path")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    in_dir = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    handlers = [logging.StreamHandler()]
    if args.log:
        lp = Path(args.log)
        lp.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(str(lp), encoding="utf-8"))

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=handlers)
    log = logging.getLogger("extract")

    glob_pat = "**/*.xls" if args.recursive else "*.xls"
    files = sorted(in_dir.glob(glob_pat))
    if not files:
        raise SystemExit(f"No .xls found in: {in_dir}")

    all_material: List[Dict[str,Any]] = []
    all_process: List[Dict[str,Any]] = []
    all_bom: List[Dict[str,Any]] = []
    all_mgmt: List[Dict[str,Any]] = []
    all_sheet_summaries: List[Dict[str,Any]] = []
    all_assy_codes: set[str] = set()
    failed = []

    log.info("Found %d xls files", len(files))

    # ステップ1: Excelから基本データ抽出
    for p in files:
        try:
            mats, procs, bom, mgmts, sheet_assys, summaries = process_file(p, log=log, debug=args.debug)
            all_material.extend(mats)
            all_process.extend(procs)
            all_bom.extend(bom)
            all_mgmt.extend(mgmts)
            all_sheet_summaries.extend(summaries)
            for a in sheet_assys:
                if a:
                    all_assy_codes.add(a)
            log.info("OK: %s material=%d process=%d mgmt=%d sheets=%d", p.name, len(mats), len(procs), len(mgmts), len(summaries))
        except Exception as e:
            failed.append((p.name, str(e)))
            log.exception("FAIL: %s", p.name)

    # mark ChildIsAssy
    for b in all_bom:
        child = b.get("ChildCode","")
        b["ChildIsAssy"] = bool(child and child in all_assy_codes)

    # CSV出力（基本5ファイル）
    material_cols = [
        "SourceFile","ParentAssy","SheetAssy","SheetName","LineNo",
        "PartCode","PartName","UnitNo","SupplyNo","Qty","UnitPrice",
        "SelfSuppliedCost","SupplyCost","RawAmount","AssyRolledProcessCost","Amount","Pattern","ExtractedAt"
    ]
    process_cols = ["SourceFile","ParentAssy","SheetAssy","SheetName","ProcessCode","ProcessName","Equipment","People","SetupH","StdH","Qty","Rate","Amount","ExtractedAt"]
    bom_cols = ["SourceFile","ParentAssy","ChildCode","ChildName","LineNo","FromSheetName","ExtractedAt","ChildIsAssy"]
    mgmt_cols = ["SourceFile","ParentAssy","SheetAssy","SheetName","ItemNo","ItemName","EstimatePrice","AssessedPrice","ExtractedAt"]
    summary_cols = ["SourceFile","SheetName","ParentAssy","SheetAssy","MaterialRows","ProcessRows","MaterialLastLineNo","ProcessLastCode","Warnings"]

    df_material = pd.DataFrame.from_records(all_material, columns=material_cols)
    df_process = pd.DataFrame.from_records(all_process, columns=process_cols)
    df_bom = pd.DataFrame.from_records(all_bom, columns=bom_cols)
    df_mgmt = pd.DataFrame.from_records(all_mgmt, columns=mgmt_cols)
    df_summary = pd.DataFrame.from_records(all_sheet_summaries, columns=summary_cols)
    
    df_material.to_csv(out_dir / "MaterialDetail.csv", index=False, encoding="utf-8-sig")
    df_process.to_csv(out_dir / "ProcessDetail.csv", index=False, encoding="utf-8-sig")
    df_bom.to_csv(out_dir / "BOM.csv", index=False, encoding="utf-8-sig")
    df_mgmt.to_csv(out_dir / "ManagementCost.csv", index=False, encoding="utf-8-sig")
    df_summary.to_csv(out_dir / "SheetSummary.csv", index=False, encoding="utf-8-sig")

    if failed:
        pd.DataFrame(failed, columns=["File","Error"]).to_csv(out_dir / "FailedFiles.csv", index=False, encoding="utf-8-sig")
        log.warning("Some files failed. See FailedFiles.csv (%d files).", len(failed))

    warn_count = sum(1 for x in all_sheet_summaries if (x.get("Warnings","") or "") != "")
    if warn_count:
        log.warning("Warnings detected on %d sheet(s). Check SheetSummary.csv", warn_count)

    # ステップ2: 再帰的BOMマトリックスの生成
    log.info("Generating Recursive BOM Matrix...")
    matrix_rows = generate_recursive_bom_matrix(
        df_bom,
        df_material,
        df_process,
        df_mgmt,
        out_dir / "Recursive_BOM_Matrix.csv",
        log
    )
    
    log.info("DONE. Output: %s (Matrix rows: %d)", out_dir, matrix_rows)


if __name__ == "__main__":
    main()
