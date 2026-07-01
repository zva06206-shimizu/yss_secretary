#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_assy_xls_sqlite.py

SQLite版: Excel抽出データをSQLiteデータベースに出力
- MaterialDetail, ProcessDetail, BOM, ManagementCostを各テーブルに保存
- Recursive_BOM_Matrix.csvは作成せず、DBから再帰的に取得可能に
- ExcelのPower QueryからODBC接続して集計可能

実行例:
  python extract_assy_xls_sqlite.py --input "C:\\Temp\\BOM_XLS" --output "C:\\Temp\\BOM_OUT\\bom_data.db"
"""

from __future__ import annotations

import argparse
import datetime as dt
import logging
import re
import sqlite3
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
    "プレス(組立品)",
    "プレス(単品)",
    "成形(組立品)",
    "成形(単品)",
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
# Material extraction (simplified)
# -------------------------

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
        if c in colmap:
            return colmap[c]
    for c in candidates:
        for colname, idx in colmap.items():
            if c in colname:
                return idx
    for colname, idx in colmap.items():
        for c in candidates:
            if colname in c and len(colname) >= 3:
                return idx
    return None

def extract_material(rows: List[List[Any]], source_file: str, parent_assy: str, sheet_assy: str, sheet_name: str):
    """簡略版の材料費明細抽出"""
    header_r = find_material_header(rows)
    if header_r is None:
        return [], ""

    header = rows[header_r]
    colmap = build_col_index_map(header)

    idx_line = pick_col(colmap, ["行番", "行", "No"])
    idx_partcode = pick_col(colmap, ["部品コード", "品目コード", "品目ｺｰﾄﾞ"])
    idx_partname = pick_col(colmap, ["部品名", "名称"])
    idx_qty = pick_col(colmap, ["所要量", "取数", "数量", "使用数"])
    idx_unitprice = pick_col(colmap, ["単価"])
    idx_amount = pick_col(colmap, ["金額", "合計"])

    result = []
    last_line_no = ""
    
    for r in range(header_r + 1, len(rows)):
        row = rows[r]
        if is_blank_row(row):
            continue
        if has_notice(joined_row(row)):
            break

        line_no = safe_get(row, idx_line)
        part_code = safe_get(row, idx_partcode)
        part_name = safe_get(row, idx_partname)
        qty = safe_get_num(row, idx_qty) or 0
        unit_price = safe_get_num(row, idx_unitprice) or 0
        amount = safe_get_num(row, idx_amount) or 0

        if not part_code and not part_name:
            continue

        if line_no:
            last_line_no = line_no

        result.append({
            "SourceFile": source_file,
            "ParentAssy": parent_assy,
            "SheetAssy": sheet_assy,
            "SheetName": sheet_name,
            "LineNo": line_no,
            "PartCode": part_code,
            "PartName": part_name,
            "Qty": qty,
            "UnitPrice": unit_price,
            "Amount": amount,
            "ExtractedAt": dt.datetime.now().isoformat()
        })

    return result, last_line_no


# -------------------------
# Process extraction (simplified)
# -------------------------

def find_process_header(rows: List[List[Any]]) -> Optional[int]:
    for r, row in enumerate(rows):
        s = compact(joined_row(row))
        if ("工程コード" in s or "工程ｺｰﾄﾞ" in s) and ("金額" in s or "レート" in s):
            return r
    return None

def extract_process(rows: List[List[Any]], source_file: str, parent_assy: str, sheet_assy: str, sheet_name: str):
    """簡略版の加工費明細抽出"""
    header_r = find_process_header(rows)
    if header_r is None:
        return [], ""

    header = rows[header_r]
    colmap = build_col_index_map(header)

    idx_code = pick_col(colmap, ["工程コード", "工程ｺｰﾄﾞ"])
    idx_name = pick_col(colmap, ["工程名", "手順"])
    idx_equipment = pick_col(colmap, ["使用設備", "設備"])
    idx_rate = pick_col(colmap, ["レート"])
    idx_amount = pick_col(colmap, ["金額"])

    result = []
    last_code = ""

    for r in range(header_r + 1, len(rows)):
        row = rows[r]
        if is_blank_row(row):
            continue
        if has_notice(joined_row(row)):
            break

        code = safe_get(row, idx_code)
        name = safe_get(row, idx_name)
        equipment = safe_get(row, idx_equipment)
        rate = safe_get_num(row, idx_rate) or 0
        amount = safe_get_num(row, idx_amount) or 0

        if not code and not name:
            continue

        if code:
            last_code = code

        result.append({
            "SourceFile": source_file,
            "ParentAssy": parent_assy,
            "SheetAssy": sheet_assy,
            "SheetName": sheet_name,
            "ProcessCode": code,
            "ProcessName": name,
            "Equipment": equipment,
            "Rate": rate,
            "Amount": amount,
            "ExtractedAt": dt.datetime.now().isoformat()
        })

    return result, last_code


# -------------------------
# Management Cost extraction (simplified)
# -------------------------

def extract_management_cost(rows: List[List[Any]], source_file: str, parent_assy: str, sheet_assy: str, sheet_name: str):
    """管理費の抽出"""
    result = []
    
    # 「管理費」セクションを探す
    mgmt_start = None
    for r, row in enumerate(rows):
        if "管理費" in joined_row(row):
            mgmt_start = r
            break
    
    if mgmt_start is None:
        return result

    # 管理費項目を抽出
    for r in range(mgmt_start, min(mgmt_start + 20, len(rows))):
        row = rows[r]
        row_text = joined_row(row)
        
        if is_blank_row(row):
            continue
        
        # 項目名と金額を探す
        for i, cell in enumerate(row):
            text = norm_text(cell)
            if text and len(text) > 2 and "管理費" not in text:
                # 次のセルが数値か確認
                if i + 1 < len(row):
                    amount = safe_get_num(row, i + 1)
                    if amount and amount != 0:
                        result.append({
                            "SourceFile": source_file,
                            "ParentAssy": parent_assy,
                            "SheetAssy": sheet_assy,
                            "SheetName": sheet_name,
                            "ItemName": text,
                            "Amount": amount,
                            "ExtractedAt": dt.datetime.now().isoformat()
                        })
                        break

    return result


# -------------------------
# BOM extraction
# -------------------------

def extract_bom_from_material(material_records: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
    """材料費明細からBOM情報を抽出"""
    bom = []
    for mat in material_records:
        if mat.get("PartCode"):
            bom.append({
                "SourceFile": mat["SourceFile"],
                "ParentAssy": mat["ParentAssy"],
                "ChildCode": mat["PartCode"],
                "ChildName": mat["PartName"],
                "LineNo": mat["LineNo"],
                "FromSheetName": mat["SheetName"],
                "Qty": mat.get("Qty", 0),
                "ExtractedAt": mat["ExtractedAt"]
            })
    return bom


# -------------------------
# File processing
# -------------------------

def process_file(file_path: Path, log: logging.Logger):
    """1つのExcelファイルを処理"""
    source_file = file_path.name
    
    wb = xlrd.open_workbook(str(file_path), formatting_info=False, on_demand=True)
    
    all_material = []
    all_process = []
    all_mgmt = []
    all_sheet_assys = []
    
    for sheet in wb.sheets():
        sheet_name = sheet.name
        
        if should_exclude_sheet(sheet_name):
            continue
        
        rows = read_sheet_as_rows(sheet)
        sheet_assy = extract_assy_code(rows)
        all_sheet_assys.append(sheet_assy)
        
        parent_assy = file_path.stem.lstrip("_")
        
        # 材料費明細
        mats, _ = extract_material(rows, source_file, parent_assy, sheet_assy, sheet_name)
        all_material.extend(mats)
        
        # 加工費明細
        procs, _ = extract_process(rows, source_file, parent_assy, sheet_assy, sheet_name)
        all_process.extend(procs)
        
        # 管理費
        mgmts = extract_management_cost(rows, source_file, parent_assy, sheet_assy, sheet_name)
        all_mgmt.extend(mgmts)
    
    wb.release_resources()
    
    # BOM抽出
    all_bom = extract_bom_from_material(all_material)
    
    return all_material, all_process, all_bom, all_mgmt, all_sheet_assys


# -------------------------
# Database creation
# -------------------------

def create_database(db_path: Path, log: logging.Logger):
    """SQLiteデータベースを作成"""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # MaterialDetailテーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS MaterialDetail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            SourceFile TEXT,
            ParentAssy TEXT,
            SheetAssy TEXT,
            SheetName TEXT,
            LineNo TEXT,
            PartCode TEXT,
            PartName TEXT,
            Qty REAL,
            UnitPrice REAL,
            Amount REAL,
            ExtractedAt TEXT
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_material_parent ON MaterialDetail(ParentAssy)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_material_part ON MaterialDetail(PartCode)")
    
    # ProcessDetailテーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ProcessDetail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            SourceFile TEXT,
            ParentAssy TEXT,
            SheetAssy TEXT,
            SheetName TEXT,
            ProcessCode TEXT,
            ProcessName TEXT,
            Equipment TEXT,
            Rate REAL,
            Amount REAL,
            ExtractedAt TEXT
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_process_parent ON ProcessDetail(ParentAssy)")
    
    # BOMテーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BOM (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            SourceFile TEXT,
            ParentAssy TEXT,
            ChildCode TEXT,
            ChildName TEXT,
            LineNo TEXT,
            FromSheetName TEXT,
            Qty REAL,
            ExtractedAt TEXT,
            ChildIsAssy INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bom_parent ON BOM(ParentAssy)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bom_child ON BOM(ChildCode)")
    
    # ManagementCostテーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ManagementCost (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            SourceFile TEXT,
            ParentAssy TEXT,
            SheetAssy TEXT,
            SheetName TEXT,
            ItemName TEXT,
            Amount REAL,
            ExtractedAt TEXT
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mgmt_parent ON ManagementCost(ParentAssy)")
    
    # 再帰的BOM展開用のビュー（簡易版）
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS BOM_Hierarchy AS
        WITH RECURSIVE bom_tree AS (
            -- ルートレベル（親が他の子として現れない）
            SELECT DISTINCT
                0 as Level,
                '' as ParentCode,
                ParentAssy as ItemCode,
                ParentAssy as ItemName,
                ParentAssy,
                1.0 as CumulativeQty
            FROM BOM
            WHERE ParentAssy NOT IN (SELECT DISTINCT ChildCode FROM BOM WHERE ChildCode IS NOT NULL)
            
            UNION ALL
            
            -- 再帰部分
            SELECT
                bt.Level + 1,
                bt.ItemCode as ParentCode,
                b.ChildCode as ItemCode,
                b.ChildName as ItemName,
                b.ParentAssy,
                bt.CumulativeQty * COALESCE(b.Qty, 1.0) as CumulativeQty
            FROM bom_tree bt
            INNER JOIN BOM b ON bt.ItemCode = b.ParentAssy
            WHERE bt.Level < 20  -- 無限ループ防止
        )
        SELECT * FROM bom_tree
    """)
    
    conn.commit()
    log.info(f"Database created: {db_path}")
    
    return conn


def insert_data(conn: sqlite3.Connection, df_material: pd.DataFrame, df_process: pd.DataFrame, 
                df_bom: pd.DataFrame, df_mgmt: pd.DataFrame, log: logging.Logger):
    """DataFrameをSQLiteに挿入"""
    
    log.info("Inserting MaterialDetail...")
    df_material.to_sql('MaterialDetail', conn, if_exists='append', index=False)
    
    log.info("Inserting ProcessDetail...")
    df_process.to_sql('ProcessDetail', conn, if_exists='append', index=False)
    
    log.info("Inserting BOM...")
    df_bom.to_sql('BOM', conn, if_exists='append', index=False)
    
    log.info("Inserting ManagementCost...")
    df_mgmt.to_sql('ManagementCost', conn, if_exists='append', index=False)
    
    conn.commit()
    log.info("Data insertion completed")


# -------------------------
# Main
# -------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="folder containing .xls files")
    ap.add_argument("--output", required=True, help="output SQLite database file path")
    ap.add_argument("--recursive", action="store_true", help="scan subfolders")
    ap.add_argument("--log", default="", help="log file path")
    args = ap.parse_args()

    in_dir = Path(args.input)
    db_path = Path(args.output)
    db_path.parent.mkdir(parents=True, exist_ok=True)

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
    all_assy_codes: Set[str] = set()
    failed = []

    log.info("Found %d xls files", len(files))

    # Excelから基本データ抽出
    for p in files:
        try:
            mats, procs, bom, mgmts, sheet_assys = process_file(p, log=log)
            all_material.extend(mats)
            all_process.extend(procs)
            all_bom.extend(bom)
            all_mgmt.extend(mgmts)
            for a in sheet_assys:
                if a:
                    all_assy_codes.add(a)
            log.info("OK: %s material=%d process=%d bom=%d mgmt=%d", p.name, len(mats), len(procs), len(bom), len(mgmts))
        except Exception as e:
            failed.append((p.name, str(e)))
            log.exception("FAIL: %s", p.name)

    # ChildIsAssyフラグを設定
    for b in all_bom:
        child = b.get("ChildCode", "")
        b["ChildIsAssy"] = 1 if (child and child in all_assy_codes) else 0

    # DataFrameに変換
    df_material = pd.DataFrame(all_material)
    df_process = pd.DataFrame(all_process)
    df_bom = pd.DataFrame(all_bom)
    df_mgmt = pd.DataFrame(all_mgmt)

    # SQLiteデータベースを作成
    if db_path.exists():
        log.warning(f"Database already exists: {db_path}. It will be overwritten.")
        db_path.unlink()
    
    conn = create_database(db_path, log)
    
    # データを挿入
    insert_data(conn, df_material, df_process, df_bom, df_mgmt, log)
    
    conn.close()

    if failed:
        log.warning("Some files failed (%d files). See log for details.", len(failed))

    log.info("DONE. Database: %s", db_path)
    log.info("Total records: Material=%d, Process=%d, BOM=%d, ManagementCost=%d", 
             len(all_material), len(all_process), len(all_bom), len(all_mgmt))


if __name__ == "__main__":
    main()
