#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_assy_xls_v10_7_8.py

v10:
- MaterialDetail: Pattern A/B に応じて PartName 見出し（材料・規格・グレード・色番 / 部品名）を自動選択
- RawAmount の仕様を Pattern で分岐
  - Pattern A: 列「材料費計」
  - Pattern B: 列「金額」
- MaterialDetail に AssyRolledProcessCost（列「加工費」）を追加
- MaterialDetail から Amount 列を削除
- 管理費・運賃等（5〜9）を抽出して SheetSummary に列追加

v8:
- MaterialDetailの列を調整
  - Unit -> UnitNo
  - SupplyNo(支給) を追加
  - SelfSuppliedCost(自給材費) を追加
  - SupplyCost(支給材料費/支給材費) を追加
  - 所要量/取数/数量/使用数 を Qty に統合（所要量優先）
- v7までの機能を維持
  - 非表示シート除外
  - テンプレシート名除外
  - 工程ヘッダー縦2行結合
  - 終端判定（注意文 / 2行連続空白）
  - 材料への工程混入防止
  - SheetSummary.csv 出力

実行例:
  python extract_assy_xls_v10_7_1.py --input "C:\\Temp\\BOM_XLS" --output "C:\\Temp\\BOM_OUT" --log "C:\\Temp\\BOM_OUT\\run.log"
"""

from __future__ import annotations

import argparse
import datetime as dt
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import xlrd  # type: ignore
    _HAVE_XLRD = True
except Exception:
    xlrd = None  # type: ignore
    _HAVE_XLRD = False

try:
    import win32com.client  # type: ignore
    _HAVE_WIN32COM = True
except Exception:
    win32com = None  # type: ignore
    _HAVE_WIN32COM = False
import pandas as pd
import numpy as np


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

def read_sheet_as_rows_xlrd(sheet) -> List[List[Any]]:
    return [sheet.row_values(r) for r in range(sheet.nrows)]


def read_sheet_as_rows_win32com(ws) -> List[List[Any]]:
    """
    Excel (win32com) でワークシートを読み取り、2次元リスト（行×列）にする。
    UsedRange を使うため、シート全体ではなく実データ範囲が対象。
    """
    used = ws.UsedRange
    v = used.Value  # tuple of tuples or scalar
    if v is None:
        return []
    if not isinstance(v, tuple):
        return [[v]]
    rows = []
    for r in v:
        if isinstance(r, tuple):
            rows.append(list(r))
        else:
            rows.append([r])
    return rows


def read_sheet_as_rows(sheet_or_ws) -> List[List[Any]]:
    """Read worksheet rows into a 2D list.

    Accepts:
      - xlrd sheet
      - win32com Worksheet
      - already-materialized list-of-rows (List[List[Any]])
    """
    # Already rows
    if isinstance(sheet_or_ws, list):
        return sheet_or_ws
    # xlrd sheet has 'cell_value' attribute
    if hasattr(sheet_or_ws, 'cell_value'):
        return read_sheet_as_rows_xlrd(sheet_or_ws)
    # win32com worksheet typically has 'Cells' attribute / UsedRange
    return read_sheet_as_rows_win32com(sheet_or_ws)


def open_workbook_sheets(xls_path: Path, log: Optional[logging.Logger]=None):
    """
    .xls 読み取り：
    - xlrd があれば xlrd を使用
    - 無ければ Windows + Excel インストール環境を前提に win32com を使用
    戻り値：[(sheet_name, visibility(0=visible), rows), ...]
    """
    if _HAVE_XLRD:
        book = xlrd.open_workbook(str(xls_path), formatting_info=False)  # type: ignore
        sheets = []
        for i in range(book.nsheets):
            sh = book.sheet_by_index(i)
            vis = 0
            try:
                vis = getattr(sh, "visibility", 0)
            except Exception:
                vis = 0
            sheets.append((str(sh.name), vis, read_sheet_as_rows_xlrd(sh)))
        return sheets

    if _HAVE_WIN32COM:
        excel = win32com.client.Dispatch("Excel.Application")  # type: ignore
        excel.DisplayAlerts = False
        excel.Visible = False
        wb = None
        try:
            wb = excel.Workbooks.Open(str(xls_path), ReadOnly=True)
            sheets = []
            for ws in wb.Worksheets:
                try:
                    # Excel: -1 = visible, 0=hidden, 2=very hidden
                    vis = 0 if int(ws.Visible) == -1 else 1
                except Exception:
                    vis = 0
                rows = read_sheet_as_rows_win32com(ws)
                sheets.append((str(ws.Name), vis, rows))
            return sheets
        finally:
            try:
                if wb is not None:
                    wb.Close(SaveChanges=False)
            except Exception:
                pass
            try:
                excel.Quit()
            except Exception:
                pass

    raise RuntimeError("xlrd が見つかりません。Windowsの場合は Excel インストール + pywin32(win32com) を入れるか、xlrd をインストールしてください。")


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


# -------------------------
# 管理費・運賃等（工程明細の下の追加費用）抽出
# -------------------------
# 仕様:
# - 工程費明細の終端注意文（＊これより下は…）の行を見つける
# - その行から 8 行下が「5,表面処理」行
# - 金額は K 列（0-based index 10）にある
# - 5～9 を抽出して SheetSummary に載せる
# 管理費・運賃等（1〜11の表）のうち、5〜9 を SheetSummary に載せる
# - 項目名は K列（0-based index 10）に「5,表面処理」などの形式で出現
# - 値は M列（0-based index 12）
ADMIN_ITEMS = [
    ("SurfaceTreatmentCost", 5),
    ("AdminProfitCost", 6),
    ("FreightCost", 7),
    ("MiscExpenseCost", 8),
    ("OtherImprovementCost", 9),
]

ADMIN_VALUE_COL_INDEX = 12  # M列（0-based=12）

def extract_admin_costs_fuzzy(rows: List[List[Any]]) -> Dict[str, float]:
    """運賃・管理費等の金額をシート全体からざっくり拾う（列位置に依存しない）。

    仕様が揺れるため、ラベル文字列を探して同一行の右側の数値を採用する。
    見つからなければ 0 のまま。
    """
    out: Dict[str, float] = {k: 0.0 for k, _no in ADMIN_ITEMS}

    # ラベル候補（部分一致）
    label_map = {
        "SurfaceTreatmentCost": ["表面処理", "表面", "めっき", "メッキ"],
        "AdminProfitCost": ["管理費", "管理", "利益", "粗利"],
        "FreightCost": ["運賃", "送料", "配送"],
        "MiscExpenseCost": ["諸経費", "雑費", "経費"],
        "OtherImprovementCost": ["改善", "改良", "その他改善"],
    }

    # 走査
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            s = norm_text(cell)
            if not s:
                continue
            s_comp = compact(s)
            for key, labels in label_map.items():
                if out.get(key, 0.0) != 0.0:
                    continue
                hit = False
                for lb in labels:
                    if compact(lb) in s_comp:
                        hit = True
                        break
                if not hit:
                    continue
                # 右方向に数値を探す（同一行）
                val = None
                for cc in range(c + 1, min(len(row), c + 8)):
                    v = safe_get_num(row, cc)
                    if v is not None:
                        val = v
                        break

                # 同一行で見つからない場合は、近傍行（下/上）も見る（レイアウト差吸収）
                if val is None:
                    for rr in (r + 1, r + 2, r - 1):
                        if rr < 0 or rr >= len(rows):
                            continue
                        row2 = rows[rr]
                        for cc in range(c + 1, min(len(row2), c + 8)):
                            v = safe_get_num(row2, cc)
                            if v is not None:
                                val = v
                                break
                        if val is not None:
                            break

                if val is None:
                    continue
                try:
                    out[key] = float(val)
                except Exception:
                    pass

    return out


def find_process_notice_row(rows: List[List[Any]], log: Optional[logging.Logger]=None, debug: bool=False, sheet_tag: str="") -> Optional[int]:
    """
    工程費明細の注意文（終端）行を特定する。

    シートによっては注意文が2回出る（工程明細の直後 / 合計行の後）ため、
    工程ヘッダー以降に出現する notice 行の **最後** を返す。
    """
    header_r, two_rows = find_process_header(rows, log=log, debug=debug, sheet_tag=sheet_tag)
    if header_r is None:
        return None

    data_start = header_r + 2 if two_rows else header_r + 1

    last_notice: Optional[int] = None
    for r in range(data_start, len(rows)):
        if has_notice(joined_row(rows[r])):
            last_notice = r

    return last_notice



def extract_admin_costs(rows: List[List[Any]], notice_row: Optional[int], log: Optional[logging.Logger]=None) -> Dict[str, float]:
    """
    管理費・運賃等（項目 5〜9）の金額を抽出する。

    レイアウト揺れが大きく、項目列が K 列に固定されないケースがあるため、
    以下の順で抽出する：

    1) ラベル部分一致で「表面処理/管理費/運賃/諸経費/改善」を探し、同一行の右側数値を拾う（fuzzy）
    2) それでも見つからない場合、シート全体を走査し
       「^\s*(5|6|7|8|9)\s*[,，]」で始まるセル（例: '7,運賃'）を見つけ、
       その行の右側（広め）から最初の数値を拾う
    """
    out: Dict[str, float] = {k: 0.0 for k, _no in ADMIN_ITEMS}

    # 1) まずは列位置に依存しない方法で拾う（見つかればそれを採用）
    fuzzy = extract_admin_costs_fuzzy(rows)
    if any((v or 0.0) != 0.0 for v in fuzzy.values()):
        return fuzzy

    # 2) 項目番号（5〜9）のセルをシート全体から検出（列固定しない）
    no_to_key = {no: key for key, no in ADMIN_ITEMS}

    def parse_item_no_any(cell: Any) -> Optional[int]:
        s = norm_text(cell)
        if not s:
            return None
        s = s.replace("，", ",")
        m = re.match(r"^\s*(\d{1,2})\s*,", s)
        if not m:
            return None
        try:
            no = int(m.group(1))
        except Exception:
            return None
        return no if no in no_to_key else None

    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            no = parse_item_no_any(cell)
            if no is None:
                continue

            # 同一行の右側から数値を探す（見積価格/査定価格など列位置が変わるため広めに見る）
            val = None
            for cc in range(c + 1, min(len(row), c + 30)):
                v = safe_get_num(row, cc)
                if v is not None:
                    val = v
                    break

            # 右側で見つからなければ、行全体で最初の数値（小計/合計誤検出を避けるため左からではなく右から）
            if val is None:
                for cc in range(len(row) - 1, -1, -1):
                    v = safe_get_num(row, cc)
                    if v is not None:
                        val = v
                        break

            if val is None:
                continue

            key = no_to_key[no]
            if out.get(key, 0.0) == 0.0:
                out[key] = float(val)

    return out

def find_material_header(rows: List[List[Any]]) -> Optional[int]:
    for r, row in enumerate(rows):
        s = compact(joined_row(row))
        if "行番" in s and ("部品コード" in s or "品目コード" in s or "品目ｺｰﾄﾞ" in s):
            return r
    return None

def build_col_index_map(header_row: List[Any]) -> Dict[str, int]:
    """ヘッダー行の列名→列indexを作る。表記ゆれ/改行/空白にも強くするため compactキーも併用。"""
    m: Dict[str,int] = {}
    for i, cell in enumerate(header_row):
        name = norm_text(cell)
        if not name:
            continue
        # そのまま
        if name not in m:
            m[name] = i
        # 空白・記号等を落とした compact 版でも登録（候補検索のヒット率を上げる）
        ck = compact(name)
        if ck and ck not in m:
            m[ck] = i
    return m

def pick_col(colmap: Dict[str,int], candidates: List[str]) -> Optional[int]:
    """候補ヘッダーを colmap から探す。

    - 完全一致（そのまま/compact）
    - 表記ゆれ対策: "使用数・所要量" のように複数語が結合されたヘッダーも拾う（compactの部分一致）
    """
    for c in candidates:
        if c in colmap:
            return colmap[c]
        cc = compact(c)
        if cc in colmap:
            return colmap[cc]
        # 部分一致（例: colmapに"使用数所要量"があり、候補が"所要量"）
        for k, idx in colmap.items():
            if not k:
                continue
            if cc and cc in k:
                return idx
    return None

def extract_material(rows: List[List[Any]], source_file: str, parent_assy: str, sheet_assy: str, sheet_name: str):
    header_r = find_material_header(rows)
    if header_r is None:
        return [], ""

    header = rows[header_r]
    colmap = build_col_index_map(header)

    pattern = "A" if any(k in colmap for k in ["材料・規格・グレード・色番", "展開寸法", "所要量"]) else "B"

    idx_line = pick_col(colmap, ["行番", "行", "No"])
    idx_partcode = pick_col(colmap, ["部品コード", "品目コード", "品目ｺｰﾄﾞ"])
    # PartName列は Pattern により見出しが異なる（A=材料・規格・グレード・色番 / B=部品名）
    idx_partname = pick_col(colmap, (["材料・規格・グレード・色番", "部品名", "名称"] if pattern == "A" else ["部品名", "名称", "材料・規格・グレード・色番"]))
    idx_unit = pick_col(colmap, ["単位"])
    idx_supplyno = pick_col(colmap, ["支給", "支給区分"])
    # Qty候補（所要量優先で統合）
    idx_req = pick_col(colmap, ["所要量", "必要量", "所与量"])
    idx_qty = pick_col(colmap, ["取数", "数量", "使用数", "使用数量"])

    idx_unitprice = pick_col(colmap, ["単価"])

    # 重要: 自給材費/支給材費（支給材料費）を別列として保持
    idx_self_cost = pick_col(colmap, ["自給材費", "自給材料費"])
    idx_supply_cost = pick_col(colmap, ["支給材費", "支給材料費", "支給材料", "支給費"])
    # RawAmount: Patternで参照列が異なる
    #  - A: 材料費計
    #  - B: 金額
    idx_raw_a = pick_col(colmap, ["材料費計", "材料費合計", "材料費計 "])
    idx_raw_b = pick_col(colmap, ["金額", "金額(円)", "金額（円）"])

    # AssyRolledProcessCost: 材料明細側にある「加工費」（ASSY集計加工費など）
    idx_assy_proc = pick_col(colmap, ["加工費", "加工賃", "加工費計", "加工費(円)", "加工費（円）"])

    out: List[Dict[str,Any]] = []
    blank_line_no_streak = 0

    r = header_r + 1
    while r < len(rows):
        row = rows[r]
        row_text = joined_row(row)

        # 1) 注意文で終了
        if has_notice(row_text):
            break

        # 2) 工程ブロックに入ったら終了（材料への工程混入防止）
        if any(h in row_text for h in PROCESS_BLOCK_HINTS):
            break

        # 3) 行番号が2行連続空白で終了
        line_no = safe_get(row, idx_line)
        if line_no == "":
            blank_line_no_streak += 1
        else:
            blank_line_no_streak = 0
        if blank_line_no_streak >= 2:
            break

        partcode = safe_get(row, idx_partcode)
        partname = safe_get(row, idx_partname)

        # 成立しない行はスキップ（終端は上で管理）
        if partcode == "" and partname == "":
            r += 1
            continue

        # Qty統合（所要量優先）
        req = safe_get_num(row, idx_req)
        q = safe_get_num(row, idx_qty)
        qty_merged = req if req is not None else q

        unit_price = safe_get_num(row, idx_unitprice)
        self_cost = safe_get_num(row, idx_self_cost)
        supply_cost = safe_get_num(row, idx_supply_cost)
        # RawAmount は Pattern に応じて抽出
        raw_a = safe_get_num(row, idx_raw_a)
        raw_b = safe_get_num(row, idx_raw_b)
        raw_amount = raw_a if pattern == "A" else raw_b
        # フォールバック（列揺れや判定揺れ対策）
        if raw_amount is None:
            raw_amount = raw_b if pattern == "A" else raw_a

        assy_proc = safe_get_num(row, idx_assy_proc)

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
            "AssyRolledProcessCost": assy_proc,
            "Pattern": pattern,
            "ExtractedAt": dt.datetime.now().isoformat(timespec="seconds"),
        })
        r += 1

    return out, pattern


# -------------------------
# Process extraction (縦2行ヘッダー対応 + 終端ルール)
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

        # 注意文で終了
        if has_notice(row_text):
            break

        pcode = safe_get(row, idx_pcode)
        pname = safe_get(row, idx_pname)

        # 工程ｺｰﾄﾞが2行連続空白で終了
        if pcode == "":
            blank_pcode_streak += 1
        else:
            blank_pcode_streak = 0
        if blank_pcode_streak >= 2:
            break

        # 見出し残骸のゴミ行を除外
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
# File processing (with summary)
# -------------------------

def process_file(xls_path: Path, log: logging.Logger, debug: bool):
    material_all: List[Dict[str,Any]] = []
    process_all: List[Dict[str,Any]] = []
    bom_all: List[Dict[str,Any]] = []
    sheet_assy_codes: List[str] = []
    sheet_summaries: List[Dict[str,Any]] = []

    sheets = open_workbook_sheets(xls_path, log=log)
    if len(sheets) == 0:
        return material_all, process_all, bom_all, sheet_assy_codes, sheet_summaries

    # 親ASSY（左端シート名 → ファイル名 の順で推定）
    parent_assy = extract_assy_code(sheets[0][0]) or extract_assy_code(xls_path.stem) or ""

    for (sheet_name, visibility, sh) in sheets:

        # 非表示シート除外（0: visible, 1: hidden, 2: very hidden）
        try:
            if visibility is not None and int(visibility) != 0:
                continue
        except Exception:
            pass
        try:
            if getattr(sh, "visibility", 0) != 0:
                continue
        except Exception:
            pass

        # ひな形シート名除外
        if should_exclude_sheet(sheet_name):
            continue

        rows = read_sheet_as_rows(sh)
        sheet_assy = extract_assy_code(rows) or parent_assy
        sheet_assy_codes.append(sheet_assy)

        mats, _ = extract_material(rows, xls_path.name, parent_assy, sheet_assy, sheet_name)
        procs = extract_process(rows, xls_path.name, parent_assy, sheet_assy, sheet_name, log=log, debug=debug)

        # 管理費・運賃等（5〜9）抽出
        notice_r = find_process_notice_row(rows, log=log, debug=debug, sheet_tag=f"{xls_path.name}:{sheet_name}")
        admin_costs = extract_admin_costs(rows, notice_r, log=log)

        material_all.extend(mats)
        process_all.extend(procs)

        # BOM（材料明細のPartCodeから親子を作る）
        for m in mats:
            child = m.get("PartCode", "")
            if child:
                bom_all.append({
                    "SourceFile": xls_path.name,
                    "ParentAssy": sheet_assy,
                    "ChildCode": child,
                    "ChildName": m.get("PartName",""),
                    "ChildUnitNo": m.get("UnitNo",""),
                    "ChildSupplyNo": m.get("SupplyNo",""),
                    "ChildQty": m.get("Qty", None),
                    "LineNo": m.get("LineNo",""),
                    "FromSheetName": sheet_name,
                    "ExtractedAt": m.get("ExtractedAt",""),
                    "ChildIsAssy": None,
                })

        # summary
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
        # 材料に工程っぽい語が混ざっていないか（簡易）
        for x in mats:
            pc = (x.get("PartCode","") or "")
            pn = (x.get("PartName","") or "")
            if ("工程" in pc) or ("工程" in pn) or ("工程名" in pc) or ("工程名" in pn) or ("レート" in pc) or ("標準時間" in pc):
                warn.append("MaterialContainsProcessText")
                break

        sheet_summaries.append({
            "SourceFile": xls_path.name,
            "SheetName": sheet_name,
            "ParentAssy": parent_assy,
            "SheetAssy": sheet_assy,
            "MaterialRows": len(mats),
            "ProcessRows": len(procs),
            "MaterialLastLineNo": last_line,
            "ProcessLastCode": last_pcode,
            "Warnings": ";".join(warn),
            "SurfaceTreatmentCost": admin_costs.get("SurfaceTreatmentCost", 0.0),
            "AdminProfitCost": admin_costs.get("AdminProfitCost", 0.0),
            "FreightCost": admin_costs.get("FreightCost", 0.0),
            "MiscExpenseCost": admin_costs.get("MiscExpenseCost", 0.0),
            "OtherImprovementCost": admin_costs.get("OtherImprovementCost", 0.0),
        })

        if debug:
            log.info("[DBG] %s:%s parent_assy=%s sheet_assy=%s mats=%d procs=%d",
                     xls_path.name, sheet_name, parent_assy, sheet_assy, len(mats), len(procs))

    return material_all, process_all, bom_all, sheet_assy_codes, sheet_summaries


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
    all_sheet_summaries: List[Dict[str,Any]] = []
    all_assy_codes: set[str] = set()
    failed = []

    log.info("Found %d xls files", len(files))

    for p in files:
        try:
            mats, procs, bom, sheet_assys, summaries = process_file(p, log=log, debug=args.debug)
            all_material.extend(mats)
            all_process.extend(procs)
            all_bom.extend(bom)
            all_sheet_summaries.extend(summaries)
            for a in sheet_assys:
                if a:
                    all_assy_codes.add(a)
            log.info("OK: %s material=%d process=%d sheets=%d", p.name, len(mats), len(procs), len(summaries))
        except Exception as e:
            failed.append((p.name, str(e)))
            log.exception("FAIL: %s", p.name)

    # mark ChildIsAssy
    for b in all_bom:
        child = b.get("ChildCode","")
        b["ChildIsAssy"] = bool(child and child in all_assy_codes)

    # output (always with columns)
    material_cols = [
        "SourceFile","ParentAssy","SheetAssy","SheetName","LineNo",
        "PartCode","PartName","UnitNo","SupplyNo","Qty","UnitPrice",
        "SelfSuppliedCost","SupplyCost","RawAmount","AssyRolledProcessCost","Pattern","ExtractedAt"
    ]
    process_cols = ["SourceFile","ParentAssy","SheetAssy","SheetName","ProcessCode","ProcessName","Equipment","People","SetupH","StdH","Qty","Rate","Amount","ExtractedAt"]
    bom_cols = ["SourceFile","ParentAssy","ChildCode","ChildName","ChildUnitNo","ChildSupplyNo","ChildQty","LineNo","FromSheetName","ExtractedAt","ChildIsAssy"]
    summary_cols = ["SourceFile","SheetName","ParentAssy","SheetAssy","MaterialRows","ProcessRows","MaterialLastLineNo","ProcessLastCode","Warnings","SurfaceTreatmentCost","AdminProfitCost","FreightCost","MiscExpenseCost","OtherImprovementCost"]

    pd.DataFrame.from_records(all_material, columns=material_cols).to_csv(out_dir / "MaterialDetail.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame.from_records(all_process, columns=process_cols).to_csv(out_dir / "ProcessDetail.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame.from_records(all_bom, columns=bom_cols).to_csv(out_dir / "BOM.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame.from_records(all_sheet_summaries, columns=summary_cols).to_csv(out_dir / "SheetSummary.csv", index=False, encoding="utf-8-sig")

    # -------------------------
    # Build PartCostSummary / PartCostSummary_WithSource (Python版 Power Query)
    # -------------------------
    df_mat = pd.DataFrame.from_records(all_material, columns=material_cols)
    df_proc = pd.DataFrame.from_records(all_process, columns=process_cols)
    df_sheet = pd.DataFrame.from_records(all_sheet_summaries, columns=summary_cols)

    # 数値列は NaN->0 で集計しやすくする
    for c in ["SelfSuppliedCost","SupplyCost","RawAmount","AssyRolledProcessCost"]:
        if c in df_mat.columns:
            df_mat[c] = pd.to_numeric(df_mat[c], errors="coerce").fillna(0.0)
    if "Amount" in df_proc.columns:
        df_proc["Amount"] = pd.to_numeric(df_proc["Amount"], errors="coerce").fillna(0.0)

    # Pattern（表示用：SheetAssyごとに最頻値）
    pat = None
    if "Pattern" in df_mat.columns and "SheetAssy" in df_mat.columns:
        pat = (df_mat.dropna(subset=["SheetAssy"])
                    .groupby("SheetAssy")["Pattern"]
                    .agg(lambda x: x.value_counts().index[0] if len(x) else "")
                    .reset_index())

    # 材料費系（SheetAssy単位）
    mat_sum = (df_mat.groupby("SheetAssy", dropna=False)[["SelfSuppliedCost","SupplyCost","RawAmount","AssyRolledProcessCost"]]
                    .sum()
                    .reset_index())

    # 工程費（SheetAssy単位）
    proc_sum = (df_proc.groupby("SheetAssy", dropna=False)[["Amount"]]
                    .sum()
                    .reset_index()
                    .rename(columns={"Amount":"ProcessCost"}))

    # SheetSummary から SourceFile/ParentAssy と管理費等（同一SheetAssyのうち最初の行を使用）
    sheet_pick = (df_sheet.sort_values(["SourceFile","SheetName"])
                        .drop_duplicates(subset=["SheetAssy"], keep="first")
                        [["SheetAssy","SourceFile","ParentAssy",
                          "SurfaceTreatmentCost","AdminProfitCost","FreightCost","MiscExpenseCost","OtherImprovementCost"]])

    pcs = mat_sum.merge(proc_sum, on="SheetAssy", how="left").merge(sheet_pick, on="SheetAssy", how="left")
    if pat is not None:
        pcs = pcs.merge(pat, on="SheetAssy", how="left")
    else:
        pcs["Pattern"] = ""

    for c in ["ProcessCost","SurfaceTreatmentCost","AdminProfitCost","FreightCost","MiscExpenseCost","OtherImprovementCost"]:
        if c in pcs.columns:
            pcs[c] = pd.to_numeric(pcs[c], errors="coerce").fillna(0.0)

    # AdminEtcCost / TotalCost（列名は PartCostSummary_WithSource に合わせる）
    pcs["AdminEtcCost"] = 0.0
    pcs["TotalCost"] = (pcs["SelfSuppliedCost"] + pcs["SupplyCost"] + pcs["RawAmount"] +
                        pcs["AssyRolledProcessCost"] + pcs["ProcessCost"] +
                        pcs["SurfaceTreatmentCost"] + pcs["AdminProfitCost"] + pcs["FreightCost"] +
                        pcs["MiscExpenseCost"] + pcs["OtherImprovementCost"] + pcs["AdminEtcCost"])

    pcs_cols = ["ParentAssy","SheetAssy","Pattern","SelfSuppliedCost","SupplyCost","RawAmount",
                "AssyRolledProcessCost","ProcessCost","SurfaceTreatmentCost","AdminProfitCost",
                "FreightCost","MiscExpenseCost","OtherImprovementCost","AdminEtcCost","TotalCost","SourceFile"]
    pcs_out = pcs.reindex(columns=[c for c in pcs_cols if c in pcs.columns]).copy()
    pcs_out.to_csv(out_dir / "PartCostSummary.csv", index=False, encoding="utf-8-sig")

    # PartMaster（PartCode → PartName。材料明細から最頻値）
    if len(df_mat) > 0 and "PartCode" in df_mat.columns:
        part_master = (df_mat[df_mat["PartCode"].astype(str).str.strip() != ""]
                            .assign(PartName2=lambda d: d.get("PartName","").fillna("").astype(str))
                            .groupby("PartCode")["PartName2"]
                            .agg(lambda x: (x[x.str.strip()!=""].value_counts().index[0] if (x.str.strip()!="").any() else ""))
                            .reset_index()
                            .rename(columns={"PartName2":"PartName"}))
    else:
        part_master = pd.DataFrame(columns=["PartCode","PartName"])

    # ProcessSteps_ByPart（SheetAssy → 工程名一覧）
    if len(df_proc) > 0 and "SheetAssy" in df_proc.columns:
        df_proc2 = df_proc.copy()
        df_proc2["ProcessName"] = df_proc2.get("ProcessName","").fillna("").astype(str)
        df_proc2["_ord"] = range(len(df_proc2))
        steps = (df_proc2[df_proc2["ProcessName"].str.strip()!=""]
                      .sort_values(["SheetAssy","_ord"])
                      .groupby("SheetAssy")["ProcessName"]
                      .agg(lambda x: "→".join(dict.fromkeys([v.strip() for v in x if v.strip()!=""])))
                      .reset_index()
                      .rename(columns={"ProcessName":"ProcessSteps"}))
    else:
        steps = pd.DataFrame(columns=["SheetAssy","ProcessSteps"])

    # PartCostSummary_WithSource 相当：部品名、工程一覧、表示名を追加
    pcs_ws = pcs_out.merge(part_master, left_on="SheetAssy", right_on="PartCode", how="left")
    pcs_ws = pcs_ws.merge(steps, on="SheetAssy", how="left")
    pcs_ws["PartName"] = pcs_ws.get("PartName","").fillna("")
    pcs_ws["ProcessSteps"] = pcs_ws.get("ProcessSteps","").fillna("")
    pcs_ws["PartDisplayName"] = pcs_ws.apply(
        lambda r: (str(r.get("PartName","")).strip() if str(r.get("PartName","")).strip() else str(r.get("SheetAssy",""))) +
                  (f"（{r.get('ProcessSteps','')}）" if str(r.get("ProcessSteps","")).strip() else ""),
        axis=1
    )
    pcs_ws.to_csv(out_dir / "PartCostSummary_WithSource.csv", index=False, encoding="utf-8-sig")

    # -------------------------
    # Recursive BOM expansion（ASSYを子まで展開）
    # -------------------------
    df_bom = pd.DataFrame.from_records(all_bom, columns=bom_cols)
    if "ChildQty" in df_bom.columns:
        df_bom["ChildQty"] = pd.to_numeric(df_bom["ChildQty"], errors="coerce").fillna(1.0)

    assy_set = set([x for x in all_assy_codes if x])

    # adjacency: ParentAssy -> rows
    adj = {}
    for _, row in df_bom.iterrows():
        pa = str(row.get("ParentAssy","") or "")
        adj.setdefault(pa, []).append(row.to_dict())

    def expand(root: str, node: str, qty_mul: float, level: int, path: list[str], out_rows: list[dict]):
        for e in adj.get(node, []):
            child = str(e.get("ChildCode","") or "")
            if not child:
                continue
            q = float(e.get("ChildQty", 1.0) or 1.0)
            cum = qty_mul * q
            new_path = path + [child]
            out_rows.append({
                "RootAssy": root,
                "ParentAssy": node,
                "ChildCode": child,
                "SheetAssy": (child if (child in assy_set) else ""),
                "ChildName": e.get("ChildName",""),
                "ChildUnitNo": e.get("ChildUnitNo",""),
                "ChildSupplyNo": e.get("ChildSupplyNo",""),
                "ChildQty": q,
                "CumQty": cum,
                "Level": level + 1,
                "Path": " > ".join(new_path),
                "SourceFile": e.get("SourceFile",""),
                "FromSheetName": e.get("FromSheetName",""),
                "LineNo": e.get("LineNo",""),
                "ChildIsAssy": bool(child in assy_set),
            })
            # cycle guard
            if child in path:
                return
            if child in assy_set:
                expand(root, child, cum, level + 1, new_path, out_rows)

    expanded: list[dict] = []
    # ルートは「ファイルの親ASSY（左端シートのASSY）」を優先
    roots = []
    if len(df_sheet) > 0 and "ParentAssy" in df_sheet.columns:
        roots = sorted(set(df_sheet["ParentAssy"].dropna().astype(str).str.strip()))
        roots = [r for r in roots if r]
    if not roots and len(df_bom) > 0 and "ParentAssy" in df_bom.columns:
        roots = sorted(set(df_bom["ParentAssy"].dropna().astype(str).str.strip()))
        roots = [r for r in roots if r]

    for r0 in roots:
        expand(r0, r0, 1.0, 0, [r0], expanded)

    df_exp = pd.DataFrame(expanded)
    df_exp.to_csv(out_dir / "ExpandedBOM.csv", index=False, encoding="utf-8-sig")

    # ASSY子に対して PartCostSummary_WithSource を結合（コスト列を横持ち）
    cost_cols = ["SheetAssy","Pattern","SelfSuppliedCost","SupplyCost","RawAmount","AssyRolledProcessCost",
                 "ProcessCost","SurfaceTreatmentCost","AdminProfitCost","FreightCost","MiscExpenseCost",
                 "OtherImprovementCost","AdminEtcCost","TotalCost","PartName","ProcessSteps","PartDisplayName"]
    for c in cost_cols:
        if c not in pcs_ws.columns:
            pcs_ws[c] = ""

    if len(df_exp) > 0:
        df_exp2 = df_exp.merge(pcs_ws[cost_cols], left_on="ChildCode", right_on="SheetAssy", how="left")
        # 行明細(MaterialDetail)のコストを ParentAssy(=元シートASSY) + LineNo + ChildCode で結合し、
        # 非ASSY部品も含めて 自給材費/支給材費/材料費計/加工費 を埋める
        try:
            if 'df_mat' in locals() and isinstance(df_mat, pd.DataFrame) and len(df_mat) > 0:
                md = df_mat.copy()
                md_cols = ["SheetAssy","LineNo","PartCode","SelfSuppliedCost","SupplyCost","RawAmount","AssyRolledProcessCost"]
                for c in md_cols:
                    if c not in md.columns:
                        md[c] = np.nan
                md2 = md[md_cols].copy()

                md2["SheetAssy"] = md2["SheetAssy"].astype(str).str.strip()
                md2["PartCode"]  = md2["PartCode"].astype(str).str.strip()
                md2["LineNo"]    = md2["LineNo"].astype(str).str.strip()

                df_exp2["ParentAssy"] = df_exp2["ParentAssy"].astype(str).str.strip()
                df_exp2["ChildCode"]  = df_exp2["ChildCode"].astype(str).str.strip()
                df_exp2["LineNo"]     = df_exp2["LineNo"].astype(str).str.strip()

                df_exp2 = df_exp2.merge(
                    md2,
                    left_on=["ParentAssy","LineNo","ChildCode"],
                    right_on=["SheetAssy","LineNo","PartCode"],
                    how="left",
                    suffixes=("", "_line")
                )

                # Line明細があれば優先（ASSY/非ASSY共通で、親シート上の見積行の値が最も正しい）
                for col in ["SelfSuppliedCost","SupplyCost","RawAmount","AssyRolledProcessCost"]:
                    if col in df_exp2.columns and (col + "_line") in df_exp2.columns:
                        base = pd.to_numeric(df_exp2[col], errors="coerce")
                        line = pd.to_numeric(df_exp2[col + "_line"], errors="coerce")
                        df_exp2[col] = base.fillna(line)

                # 加工費(ProcessCost)は、親シート行の加工費（AssyRolledProcessCost_line）で埋める
                if "ProcessCost" in df_exp2.columns and "AssyRolledProcessCost_line" in df_exp2.columns:
                    base = pd.to_numeric(df_exp2["ProcessCost"], errors="coerce")
                    line = pd.to_numeric(df_exp2["AssyRolledProcessCost_line"], errors="coerce")
                    df_exp2["ProcessCost"] = base.fillna(line)
        except Exception as _e:
            pass

        # PartName が空の場合は ChildName をフォールバックに使う（BOM側に名称が入っているため）
        if "PartName" in df_exp2.columns and "ChildName" in df_exp2.columns:
            _pn = df_exp2["PartName"].astype(str)
            _blank = df_exp2["PartName"].isna() | (_pn.str.strip() == "") | (_pn.str.strip().str.lower() == "nan")
            df_exp2.loc[_blank, "PartName"] = df_exp2.loc[_blank, "ChildName"]

        df_exp2["RolledTotalCost"] = pd.to_numeric(df_exp2["TotalCost"], errors="coerce").fillna(0.0) * pd.to_numeric(df_exp2["CumQty"], errors="coerce").fillna(0.0)
    else:
        df_exp2 = df_exp.copy()

    df_exp2.to_csv(out_dir / "ExpandedBOM_WithAssyCost.csv", index=False, encoding="utf-8-sig")

    # 失敗ファイル一覧
    if failed:
        pd.DataFrame(failed, columns=["File","Error"]).to_csv(out_dir / "FailedFiles.csv", index=False, encoding="utf-8-sig")
        log.warning("Some files failed. See FailedFiles.csv (%d files).", len(failed))

    warn_count = sum(1 for x in all_sheet_summaries if (x.get("Warnings","") or "") != "")
    if warn_count:
        log.warning("Warnings detected on %d sheet(s). Check SheetSummary.csv", warn_count)

    log.info("DONE. Output: %s", out_dir)
if __name__ == "__main__":
    main()
