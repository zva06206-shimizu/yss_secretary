#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_assy_xls.py

フォルダ内の「1部品=1ファイル、複数シート」の .xls から、
- MaterialDetail.csv（材料費明細）
- ProcessDetail.csv（工程費明細）
- BOM.csv（親子関係：材料明細に出てくる部品コード）
を正規化して出力します。

前提（ユーザー要件）:
- 1ファイルの左端（最初）のシートが「親ASSY」の見積（材料費明細/工程費明細を含む）
- 同一ファイル内の他シートは、親ASSYの材料費明細に出てくる ASSY 部品の見積
- 材料費明細は「ASSY部品が含まれるパターン / 含まれないパターン」で列名が異なることがある
- 行数は可変（材料: 21行以上、工程: 7行以上になる場合がある）

使い方例:
  python extract_assy_xls.py --input "C:\\BOM_XLS" --output "C:\\BOM_OUT"

必要:
  pip install xlrd==2.* pandas
  ※ .xls 読み取りのため xlrd を使用
"""

from __future__ import annotations

import argparse
import datetime as dt
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import xlrd  # for .xls
import pandas as pd


# -------------------------
# ユーティリティ
# -------------------------

def norm_text(x: Any) -> str:
    """セル値を文字列化して前後空白を除去。None/NaNは空文字。"""
    if x is None:
        return ""
    if isinstance(x, float):
        if x.is_integer():
            return str(int(x))
        return str(x)
    s = str(x)
    s = s.replace("\u3000", " ").strip()  # 全角スペース→半角
    return s

def is_blank_row(row: List[Any]) -> bool:
    return all(norm_text(c) == "" for c in row)

def find_cell_pos(rows: List[List[Any]], target: str) -> Optional[Tuple[int,int]]:
    """指定文字列を含むセルを探して最初の位置 (r,c) を返す（部分一致）。"""
    t = target.strip()
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            if t in norm_text(cell):
                return (r, c)
    return None

def find_header_row(rows: List[List[Any]], required_keywords: List[str]) -> Optional[int]:
    """required_keywords（複数）を同一行に含む行をヘッダー行として探す。"""
    req = [k.strip() for k in required_keywords]
    for r, row in enumerate(rows):
        joined = "｜".join(norm_text(c) for c in row)
        if all(k in joined for k in req):
            return r
    return None

def build_col_index_map(header_row: List[Any]) -> Dict[str, int]:
    """ヘッダー行の各セル文字列→列番号 のマップ。同名が複数あれば最初を採用。"""
    m: Dict[str,int] = {}
    for i, cell in enumerate(header_row):
        name = norm_text(cell)
        if name and name not in m:
            m[name] = i
    return m

def pick_col(colmap: Dict[str,int], candidates: List[str]) -> Optional[int]:
    """候補ヘッダー名のどれかが存在すればその列番号を返す。"""
    for c in candidates:
        if c in colmap:
            return colmap[c]
    return None

def safe_get(row: List[Any], idx: Optional[int]) -> str:
    if idx is None or idx < 0 or idx >= len(row):
        return ""
    return norm_text(row[idx])

def safe_get_num(row: List[Any], idx: Optional[int]) -> Optional[float]:
    """数値列の取得。取れなければ None。"""
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
    except:
        return None

def guess_amount(qty: Optional[float], unit_price: Optional[float]) -> Optional[float]:
    if qty is None or unit_price is None:
        return None
    return qty * unit_price


# -------------------------
# ASSYコード取得
# -------------------------

ASSY_LABEL_CANDIDATES = [
    "部品コード",
    "製品コード",
    "品目コード",
    "品目ｺｰﾄﾞ",
]

def extract_assy_code(rows: List[List[Any]]) -> str:
    """シート上部にある ASSY部品コードを推定取得（ラベルの右セル）。"""
    for lab in ASSY_LABEL_CANDIDATES:
        pos = find_cell_pos(rows, lab)
        if not pos:
            continue
        r, c = pos
        for dc in (1, 2, 3):
            if c + dc < len(rows[r]):
                v = norm_text(rows[r][c + dc])
                if v:
                    return v
        for dr in (1, 2, 3):
            if r + dr < len(rows):
                v = norm_text(rows[r + dr][c])
                if v:
                    return v
    return ""


# -------------------------
# 材料費明細抽出
# -------------------------

MATERIAL_HEADER_KEYWORDS = ["行番", "部品コード"]  # 同一行にこの2つがあれば材料のヘッダー候補

def extract_material(rows: List[List[Any]], source_file: str, parent_assy: str, sheet_assy: str, sheet_name: str):
    header_r = find_header_row(rows, MATERIAL_HEADER_KEYWORDS)
    if header_r is None:
        return [], ""

    header = rows[header_r]
    colmap = build_col_index_map(header)

    # パターン判定（ざっくり）
    pattern = "A" if any(k in colmap for k in ["材料・規格・グレード・色番", "展開寸法", "所要量"]) else "B"

    idx_line = pick_col(colmap, ["行番", "行", "No"])
    idx_partcode = pick_col(colmap, ["部品コード", "品目コード", "品目ｺｰﾄﾞ"])
    idx_partname = pick_col(colmap, ["部品名", "名称"])
    idx_matspec = pick_col(colmap, ["材料・規格・グレード・色番", "材料・規格", "材料/規格", "材質"])
    idx_matcode = pick_col(colmap, ["素材コード", "材料コード", "素材ｺｰﾄﾞ"])
    idx_unit = pick_col(colmap, ["単位", "Unit"])
    idx_supply = pick_col(colmap, ["支給", "自給/支給", "支給区分", "自給支給", "自給/支給区分"])
    idx_qty = pick_col(colmap, ["取数", "数量", "使用数", "使用数量"])
    idx_req = pick_col(colmap, ["所要量", "必要量"])
    idx_unitprice = pick_col(colmap, ["単価"])
    idx_amount = pick_col(colmap, ["金額", "支給材料費", "材料費計", "材料費", "自給材料費", "支給材費"])

    out: List[Dict[str,Any]] = []
    r = header_r + 1
    while r < len(rows):
        row = rows[r]
        partcode = safe_get(row, idx_partcode)
        partname = safe_get(row, idx_partname)

        if partcode == "" and partname == "" and is_blank_row(row):
            break

        if partcode == "" and safe_get(row, idx_line) == "":
            if is_blank_row(row):
                break
            r += 1
            continue

        qty = safe_get_num(row, idx_qty)
        req = safe_get_num(row, idx_req)
        unit_price = safe_get_num(row, idx_unitprice)
        raw_amount = safe_get_num(row, idx_amount)
        amount = raw_amount
        if amount is None:
            amount = guess_amount(req, unit_price)
            if amount is None:
                amount = guess_amount(qty, unit_price)

        out.append({
            "SourceFile": source_file,
            "ParentAssy": parent_assy,
            "SheetAssy": sheet_assy,
            "SheetName": sheet_name,
            "LineNo": safe_get(row, idx_line),
            "PartCode": partcode,
            "PartName": partname,
            "MaterialSpec": safe_get(row, idx_matspec),
            "MaterialCode": safe_get(row, idx_matcode),
            "Unit": safe_get(row, idx_unit),
            "SupplyType": safe_get(row, idx_supply),
            "Qty": qty,
            "RequiredQty": req,
            "UnitPrice": unit_price,
            "Amount": amount,
            "RawAmount": raw_amount,
            "Pattern": pattern,
            "ExtractedAt": dt.datetime.now().isoformat(timespec="seconds"),
        })
        r += 1

    return out, pattern


# -------------------------
# 工程費明細抽出
# -------------------------

def find_process_header(rows: List[List[Any]]) -> Optional[int]:
    for r, row in enumerate(rows):
        joined = "｜".join(norm_text(c) for c in row)
        if ("工程コード" in joined or "工程ｺｰﾄﾞ" in joined) and ("工程名" in joined or "手順" in joined):
            return r
    for r, row in enumerate(rows):
        joined = "｜".join(norm_text(c) for c in row)
        if "工程コード" in joined or "工程ｺｰﾄﾞ" in joined:
            return r
    return None

def extract_process(rows: List[List[Any]], source_file: str, parent_assy: str, sheet_assy: str, sheet_name: str):
    header_r = find_process_header(rows)
    if header_r is None:
        return []

    header = rows[header_r]
    colmap = build_col_index_map(header)

    idx_pcode = pick_col(colmap, ["工程コード", "工程ｺｰﾄﾞ"])
    idx_pname = pick_col(colmap, ["工程名・手順", "工程名", "工程名/手順", "手順"])
    idx_equip = pick_col(colmap, ["使用設備", "設備"])
    idx_cap = pick_col(colmap, ["設備能力", "設備能力量"])
    idx_people = pick_col(colmap, ["人員"])
    idx_setup = pick_col(colmap, ["準備時間(H)", "準備時間", "準備(H)"])
    idx_std = pick_col(colmap, ["標準時間(H)", "標準時間", "標準(H)"])
    idx_qty = pick_col(colmap, ["取数", "数量"])
    idx_rate = pick_col(colmap, ["レート", "工賃レート", "単価"])
    idx_amount = pick_col(colmap, ["金額", "加工費", "加工費計"])

    out: List[Dict[str,Any]] = []
    r = header_r + 1
    while r < len(rows):
        row = rows[r]
        pcode = safe_get(row, idx_pcode)
        pname = safe_get(row, idx_pname)

        if pcode == "" and pname == "" and is_blank_row(row):
            break

        if pcode == "" and pname == "":
            if is_blank_row(row):
                break
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
            "EquipmentCapacity": safe_get(row, idx_cap),
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
# ファイル処理
# -------------------------

def read_sheet_as_rows(sheet: xlrd.sheet.Sheet) -> List[List[Any]]:
    return [sheet.row_values(r) for r in range(sheet.nrows)]

def process_file(xls_path: Path):
    material_all: List[Dict[str,Any]] = []
    process_all: List[Dict[str,Any]] = []
    bom_all: List[Dict[str,Any]] = []
    sheet_assy_codes: List[str] = []

    book = xlrd.open_workbook(str(xls_path), formatting_info=False)
    if book.nsheets == 0:
        return material_all, process_all, bom_all, sheet_assy_codes

    first_sheet = book.sheet_by_index(0)
    parent_assy = extract_assy_code(read_sheet_as_rows(first_sheet))

    for si in range(book.nsheets):
        sh = book.sheet_by_index(si)
        rows = read_sheet_as_rows(sh)
        sheet_assy = extract_assy_code(rows) or parent_assy
        sheet_assy_codes.append(sheet_assy)

        mats, _pattern = extract_material(rows, xls_path.name, parent_assy, sheet_assy, sh.name)
        procs = extract_process(rows, xls_path.name, parent_assy, sheet_assy, sh.name)

        material_all.extend(mats)
        process_all.extend(procs)

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

    return material_all, process_all, bom_all, sheet_assy_codes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="xls ファイルが入っているフォルダ")
    ap.add_argument("--output", required=True, help="出力フォルダ（CSVを作成）")
    ap.add_argument("--recursive", action="store_true", help="サブフォルダも再帰的に探索")
    ap.add_argument("--log", default="", help="ログファイルパス（省略可）")
    args = ap.parse_args()

    in_dir = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    handlers = [logging.StreamHandler()]
    if args.log:
        log_path = Path(args.log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(str(log_path), encoding="utf-8"))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers
    )
    log = logging.getLogger("extract")

    if not in_dir.exists():
        raise SystemExit(f"Input folder not found: {in_dir}")

    glob_pat = "**/*.xls" if args.recursive else "*.xls"
    files = sorted(in_dir.glob(glob_pat))
    if not files:
        raise SystemExit(f"No .xls found in: {in_dir}")

    all_material: List[Dict[str,Any]] = []
    all_process: List[Dict[str,Any]] = []
    all_bom: List[Dict[str,Any]] = []
    all_assy_codes: set[str] = set()
    failed = []

    log.info("Found %d xls files", len(files))

    for p in files:
        try:
            mats, procs, bom, sheet_assys = process_file(p)
            all_material.extend(mats)
            all_process.extend(procs)
            all_bom.extend(bom)
            for a in sheet_assys:
                if a:
                    all_assy_codes.add(a)
            log.info("OK: %s  sheets=%d  material=%d  process=%d", p.name, len(sheet_assys), len(mats), len(procs))
        except Exception as e:
            failed.append((p.name, str(e)))
            log.exception("FAIL: %s", p.name)

    for b in all_bom:
        child = b.get("ChildCode","" )
        b["ChildIsAssy"] = bool(child and child in all_assy_codes)

    def to_csv(records: List[Dict[str,Any]], path: Path):
        if not records:
            path.write_text("", encoding="utf-8-sig")
            return
        df = pd.DataFrame.from_records(records)
        df.to_csv(path, index=False, encoding="utf-8-sig")

    to_csv(all_material, out_dir / "MaterialDetail.csv")
    to_csv(all_process, out_dir / "ProcessDetail.csv")
    to_csv(all_bom, out_dir / "BOM.csv")

    if failed:
        pd.DataFrame(failed, columns=["File","Error"]).to_csv(out_dir / "FailedFiles.csv", index=False, encoding="utf-8-sig")
        log.warning("Some files failed. See FailedFiles.csv (%d files).", len(failed))

    log.info("DONE. Output: %s", out_dir)


if __name__ == "__main__":
    main()
