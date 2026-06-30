#!/usr/bin/env python3
"""yfinance で株価を取得し、Lark Base にレコードを追加する。

GitHub Actions から定期実行する前提。認証情報はすべて環境変数で渡す
（リポジトリには絶対に書かない）。

必要な環境変数:
  LARK_APP_ID       Lark 開発者アプリの App ID
  LARK_APP_SECRET   Lark 開発者アプリの App Secret
  LARK_APP_TOKEN    Base の app_token（BaseのURL: .../base/<ここ>）
  LARK_TABLE_ID     対象テーブルの table_id（テーブルURL内 tbl... ）

Base 側に用意するフィールド（列名は下の FIELD_* と一致させる）:
  銘柄(テキスト) / 名称(テキスト) / 日付(テキスト) /
  終値(数値) / 始値(数値) / 高値(数値) / 安値(数値) / 出来高(数値) / 通貨(テキスト)
"""

import os
import sys
import time
import datetime as dt

import requests
import yfinance as yf

# Lark（グローバル版）。中国 Feishu の場合は open.feishu.cn に変える。
LARK_BASE_URL = "https://open.larksuite.com/open-apis"

# Base 側の列名（日本語可。Base の実際の列名に合わせる）
FIELD_TICKER = "銘柄"
FIELD_NAME = "名称"
FIELD_DATE = "日付"
FIELD_CLOSE = "終値"
FIELD_OPEN = "始値"
FIELD_HIGH = "高値"
FIELD_LOW = "安値"
FIELD_VOLUME = "出来高"
FIELD_CURRENCY = "通貨"


def load_tickers(path: str = "tickers.txt") -> list[str]:
    tickers = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            # 行内コメント（# 以降）を落とす
            code = line.split("#", 1)[0].strip()
            if code:
                tickers.append(code)
    return tickers


def fetch_one(ticker: str, retries: int = 3) -> dict | None:
    """直近の取引日のOHLCVを1件返す。失敗したら None。"""
    for attempt in range(1, retries + 1):
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")  # 直近営業日を確実に拾う
            if hist.empty:
                print(f"[warn] {ticker}: 履歴が空")
                return None
            row = hist.iloc[-1]
            day = hist.index[-1].date().isoformat()
            # 名称・通貨はメタ情報から（取れなければ空）
            info = getattr(t, "fast_info", {}) or {}
            currency = ""
            try:
                currency = info.get("currency") or ""
            except Exception:
                pass
            name = ""
            try:
                name = (t.info or {}).get("shortName", "") or ""
            except Exception:
                pass
            return {
                FIELD_TICKER: ticker,
                FIELD_NAME: name,
                FIELD_DATE: day,
                FIELD_CLOSE: round(float(row["Close"]), 2),
                FIELD_OPEN: round(float(row["Open"]), 2),
                FIELD_HIGH: round(float(row["High"]), 2),
                FIELD_LOW: round(float(row["Low"]), 2),
                FIELD_VOLUME: int(row["Volume"]),
                FIELD_CURRENCY: currency,
            }
        except Exception as e:  # noqa: BLE001
            wait = attempt * 5
            print(f"[warn] {ticker}: 取得失敗({attempt}/{retries}) {e} -> {wait}s 待機")
            time.sleep(wait)
    print(f"[error] {ticker}: リトライ上限。スキップ")
    return None


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    url = f"{LARK_BASE_URL}/auth/v3/tenant_access_token/internal"
    resp = requests.post(
        url, json={"app_id": app_id, "app_secret": app_secret}, timeout=30
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"token取得失敗: {data}")
    return data["tenant_access_token"]


def push_to_lark(token: str, app_token: str, table_id: str, records: list[dict]) -> None:
    url = (
        f"{LARK_BASE_URL}/bitable/v1/apps/{app_token}"
        f"/tables/{table_id}/records/batch_create"
    )
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"records": [{"fields": r} for r in records]}
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Lark書込失敗: {data}")
    n = len(data.get("data", {}).get("records", []))
    print(f"[ok] Lark に {n} 件書き込み")


def main() -> int:
    app_id = os.environ["LARK_APP_ID"]
    app_secret = os.environ["LARK_APP_SECRET"]
    app_token = os.environ["LARK_APP_TOKEN"]
    table_id = os.environ["LARK_TABLE_ID"]

    tickers = load_tickers()
    if not tickers:
        print("[error] tickers.txt に銘柄がない")
        return 1
    print(f"[info] {len(tickers)} 銘柄を取得: {', '.join(tickers)}")

    records = [r for tk in tickers if (r := fetch_one(tk)) is not None]
    if not records:
        print("[error] 取得できた銘柄が0件。Lark書込みはスキップ")
        return 1

    token = get_tenant_access_token(app_id, app_secret)
    push_to_lark(token, app_token, table_id, records)
    print(f"[done] {dt.datetime.now().isoformat()} 完了")
    return 0


if __name__ == "__main__":
    sys.exit(main())
