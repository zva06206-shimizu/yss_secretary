#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lark Base（国際版 open.larksuite.com）Bitable 読み取り専用点検スクリプト。

同じフォルダの .env から接続情報を読み、指定した App Token（Base）内の
全テーブル・各テーブルのフィールド一覧・レコードの先頭数件を「のぞく」だけ。
作成・更新・削除は一切行わない（認証POSTと各GETのみ）。

--- .env の書式（このスクリプトと同じフォルダに置く） ---
    LARK_APP_ID=cli_xxxxxxxxxxxxx
    LARK_APP_SECRET=xxxxxxxxxxxxxxxx
    LARK_APP_TOKEN=basxxxxxxxxxxxxxxx
    # 任意。既定は open.larksuite.com（国際版）。中国版は open.feishu.cn
    LARK_DOMAIN=open.larksuite.com

--- PowerShell での実行例（Windows） ---
    # このスクリプトのあるフォルダへ移動
    cd C:\\git\\yss_secretary

    # そのまま実行（.env を自動で読む）
    python .\\inspect_lark.py

    # 文字化けする場合はコンソールを UTF-8 にしてから実行
    chcp 65001
    python .\\inspect_lark.py

    # 一時的に環境変数で上書きしたい場合（.env より環境変数が優先）
    $env:LARK_APP_TOKEN = "basxxxxxxxxxxxxxxx"
    python .\\inspect_lark.py

python-dotenv 等の外部依存は不要。標準ライブラリのみで動作する。
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

# ---------------------------------------------------------------------------
# 定数
# ---------------------------------------------------------------------------
DEFAULT_DOMAIN = "open.larksuite.com"
RECORD_PAGE_SIZE = 5          # レコードは先頭少数だけのぞく
SAMPLE_RECORD_LIMIT = 3       # サンプル表示するレコード件数
VALUE_TRUNCATE = 60           # 値表示の切り詰め文字数
HTTP_TIMEOUT = 30             # 秒

# code!=0 のとき、典型的な原因に案内文を添えるための対応表
KNOWN_ERROR_HINTS = {
    99991663: "tenant_access_token が無効/期限切れの可能性。app_id/app_secret を確認。",
    99991661: "アクセストークンが不正の可能性。app_id/app_secret を確認。",
    1254302: "権限（スコープ）不足の可能性。アプリに bitable:app:readonly 等を付与し、公開/バージョンを反映。",
    1254005: "app_token（Base）が見つからない/不正。LARK_APP_TOKEN を確認。",
    91402: "リソースが見つからない（NOTEXIST）。App Token やテーブル指定を確認。",
    91403: "アクセス拒否（FORBIDDEN）。アプリをこの Base に『追加』しているか確認（Base右上→…→アプリ追加）。",
}


# ---------------------------------------------------------------------------
# ユーティリティ
# ---------------------------------------------------------------------------
def eprint(*args):
    """標準エラーへ出力。"""
    print(*args, file=sys.stderr)


def load_dotenv(path):
    """.env を自前でパースして dict で返す。

    - `#` で始まる行（コメント）と空行は無視。
    - `KEY=VALUE` 形式。最初の `=` で分割。
    - 値の前後の空白と、両端のクォート（' または "）を除去。
    外部依存（python-dotenv 等）は使わない。
    """
    env = {}
    if not os.path.isfile(path):
        return env
    with open(path, "r", encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if not key:
                continue
            value = value.strip()
            # 両端が同じクォートで囲まれていれば除去
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            env[key] = value
    return env


def mask_secret(s):
    """シークレット/トークンをログ用にマスクする（絶対に生値を出さない）。"""
    if not s:
        return "(未設定)"
    if len(s) <= 6:
        return "*" * len(s)
    return s[:3] + "*" * (len(s) - 6) + s[-3:]


def truncate(text, limit=VALUE_TRUNCATE):
    """長い値を切り詰める。改行は空白へ置換。"""
    if text is None:
        return ""
    text = str(text).replace("\r", " ").replace("\n", " ")
    if len(text) > limit:
        return text[:limit] + "…"
    return text


def field_type_name(type_id):
    """field_type 数値を人間可読な名称に変換（仕様表準拠）。"""
    names = {
        1: "テキスト/バーコード",
        2: "数値/進捗/通貨/評価",
        3: "単一選択",
        4: "複数選択",
        5: "日付",
        7: "チェックボックス",
        11: "ユーザー(人員)",
        13: "電話番号",
        15: "URL",
        17: "添付ファイル",
        18: "Single Link",
        19: "Lookup",
        20: "数式",
        21: "Duplex Link",
        22: "位置(Location)",
        23: "グループチャット",
        1001: "作成日時",
        1002: "更新日時",
        1003: "作成者",
        1004: "更新者",
        1005: "自動採番",
    }
    return names.get(type_id, "不明")


def format_field_value(value):
    """fields の値（型により形が変わる）を表示用文字列にする。"""
    if value is None:
        return ""
    # 単純型（文字列・数値・真偽）
    if isinstance(value, (str, int, float, bool)):
        return truncate(value)
    # 複数選択など文字列配列 / ユーザー型などオブジェクト配列
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict):
                # ユーザー型: name、テキストセグメント型: text、その他は代表キー
                if "name" in item:
                    parts.append(str(item["name"]))
                elif "text" in item:
                    parts.append(str(item["text"]))
                elif "link" in item:
                    parts.append(str(item["link"]))
                else:
                    parts.append(json.dumps(item, ensure_ascii=False))
            else:
                parts.append(str(item))
        return truncate(", ".join(parts))
    # オブジェクト（リンクやlocation等）
    if isinstance(value, dict):
        if "text" in value:
            return truncate(value["text"])
        if "name" in value:
            return truncate(value["name"])
        return truncate(json.dumps(value, ensure_ascii=False))
    return truncate(str(value))


# ---------------------------------------------------------------------------
# HTTP（標準ライブラリのみ）
# ---------------------------------------------------------------------------
def http_request(method, url, headers=None, body=None):
    """HTTP リクエストを送り、(status_code, parsed_json) を返す。

    2xx でない場合も本文を JSON として読めれば返す（Lark はエラーでも
    {code, msg} を返すため）。JSON にできなければ例外を送出。
    """
    headers = dict(headers or {})
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers.setdefault("Content-Type", "application/json; charset=utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = resp.getcode()
    except urllib.error.HTTPError as e:
        # HTTP エラーでも本文（Larkのcode/msg）を読み取る
        raw = e.read().decode("utf-8", errors="replace")
        status = e.code
    except urllib.error.URLError as e:
        raise RuntimeError(f"ネットワークエラー: {getattr(e, 'reason', e)}")
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"通信中に予期しないエラー: {e}")

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"レスポンスをJSONとして解釈できません (HTTP {status}): "
            f"{truncate(raw, 200)}"
        )
    return status, parsed


def check_lark_ok(parsed, context):
    """Lark レスポンスの code を検査。code!=0 なら分かりやすく案内して終了。"""
    code = parsed.get("code")
    if code == 0:
        return
    msg = parsed.get("msg", "(msgなし)")
    eprint("")
    eprint(f"[Larkエラー] {context}")
    eprint(f"  code = {code}")
    eprint(f"  msg  = {msg}")
    hint = KNOWN_ERROR_HINTS.get(code)
    if hint:
        eprint(f"  ヒント: {hint}")
    else:
        eprint("  ヒント: アプリのスコープ付与、Baseへのアプリ追加、"
               "App Token の値を確認してください。")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Lark API 呼び出し
# ---------------------------------------------------------------------------
def get_tenant_access_token(base_url, app_id, app_secret):
    """自社開発アプリの tenant_access_token を取得。

    仕様: POST /open-apis/auth/v3/tenant_access_token/internal
    Authorization ヘッダは不要。トークンはレスポンス直下（data入れ子ではない）。
    """
    url = f"{base_url}/open-apis/auth/v3/tenant_access_token/internal"
    body = {"app_id": app_id, "app_secret": app_secret}
    status, parsed = http_request("POST", url, body=body)

    if parsed.get("code") != 0:
        # このエンドポイントは data に包まれないが、code/msg 構造は共通
        check_lark_ok(parsed, "tenant_access_token 取得")

    token = parsed.get("tenant_access_token")
    if not token:
        raise RuntimeError("tenant_access_token がレスポンスに含まれません。")
    expire = parsed.get("expire")
    print(f"[認証OK] tenant_access_token を取得（有効期限 {expire} 秒 / "
          f"token={mask_secret(token)}）")
    return token


def list_tables(base_url, token, app_token):
    """Base 内の全テーブルを一覧（ページネーション対応）。"""
    url_base = f"{base_url}/open-apis/bitable/v1/apps/{app_token}/tables"
    headers = {"Authorization": f"Bearer {token}"}
    items = []
    page_token = None
    while True:
        query = "?page_size=100"
        if page_token:
            query += f"&page_token={urllib.parse.quote(page_token)}"
        status, parsed = http_request("GET", url_base + query, headers=headers)
        check_lark_ok(parsed, "テーブル一覧取得")
        data = parsed.get("data", {})
        items.extend(data.get("items", []))
        if data.get("has_more") and data.get("page_token"):
            page_token = data["page_token"]
            continue
        break
    return items


def list_fields(base_url, token, app_token, table_id):
    """テーブルのフィールド（列）一覧を取得（ページネーション対応）。"""
    url_base = (
        f"{base_url}/open-apis/bitable/v1/apps/{app_token}"
        f"/tables/{table_id}/fields"
    )
    headers = {"Authorization": f"Bearer {token}"}
    items = []
    page_token = None
    while True:
        query = "?page_size=100"
        if page_token:
            query += f"&page_token={urllib.parse.quote(page_token)}"
        status, parsed = http_request("GET", url_base + query, headers=headers)
        check_lark_ok(parsed, f"フィールド一覧取得 (table_id={table_id})")
        data = parsed.get("data", {})
        items.extend(data.get("items", []))
        if data.get("has_more") and data.get("page_token"):
            page_token = data["page_token"]
            continue
        break
    return items


def search_records(base_url, token, app_token, table_id, page_size):
    """レコードを検索（POST records/search・推奨API）で先頭ページのみ取得。

    読み取り専用のため、fetch は1ページ（先頭 page_size 件）に限定する。
    戻り値: (items, total)
    """
    url = (
        f"{base_url}/open-apis/bitable/v1/apps/{app_token}"
        f"/tables/{table_id}/records/search?page_size={page_size}"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    # filter/sort を空にして view 全体の先頭から。automatic_fields は不要。
    body = {"automatic_fields": False}
    status, parsed = http_request("POST", url, headers=headers, body=body)
    check_lark_ok(parsed, f"レコード検索 (table_id={table_id})")
    data = parsed.get("data", {})
    return data.get("items", []), data.get("total")


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------
def main():
    # 実行フォルダではなくスクリプトと同じフォルダの .env を読む
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ".env")
    file_env = load_dotenv(env_path)

    def get_conf(key):
        # 環境変数を優先し、無ければ .env の値
        return os.environ.get(key) or file_env.get(key)

    app_id = get_conf("LARK_APP_ID")
    app_secret = get_conf("LARK_APP_SECRET")
    app_token = get_conf("LARK_APP_TOKEN")
    domain = get_conf("LARK_DOMAIN") or DEFAULT_DOMAIN
    domain = domain.strip().rstrip("/")
    # スキーム無しで書かれていても補完
    if domain.startswith("http://") or domain.startswith("https://"):
        base_url = domain
    else:
        base_url = f"https://{domain}"

    # 必須項目チェック
    missing = [
        name for name, val in (
            ("LARK_APP_ID", app_id),
            ("LARK_APP_SECRET", app_secret),
            ("LARK_APP_TOKEN", app_token),
        ) if not val
    ]
    if missing:
        eprint("[設定エラー] 次の必須項目が未設定です: " + ", ".join(missing))
        eprint(f"  .env を確認してください: {env_path}")
        eprint("  例:")
        eprint("    LARK_APP_ID=cli_xxxxxxxxxxxxx")
        eprint("    LARK_APP_SECRET=xxxxxxxxxxxxxxxx")
        eprint("    LARK_APP_TOKEN=basxxxxxxxxxxxxxxx")
        sys.exit(2)

    print("=" * 70)
    print("Lark Base 点検（読み取り専用）")
    print("=" * 70)
    print(f"ドメイン    : {base_url}")
    print(f"APP_ID      : {app_id}")            # app_id は識別子。秘密ではない
    print(f"APP_SECRET  : {mask_secret(app_secret)}")   # マスク
    print(f"APP_TOKEN   : {app_token}")         # Base識別子。秘密トークンではない
    print("-" * 70)

    # (1) 認証
    token = get_tenant_access_token(base_url, app_id, app_secret)

    # (2) テーブル一覧
    tables = list_tables(base_url, token, app_token)
    print("")
    print(f"[テーブル数] {len(tables)} 件")
    print("=" * 70)

    if not tables:
        print("テーブルが見つかりませんでした。App Token を確認してください。")
        return

    # (3) 各テーブルの詳細
    for idx, table in enumerate(tables, start=1):
        table_id = table.get("table_id", "(不明)")
        name = table.get("name", "(名称なし)")
        print("")
        print(f"■ テーブル {idx}/{len(tables)}: {name}")
        print(f"  table_id: {table_id}")

        # --- フィールド一覧 ---
        try:
            fields = list_fields(base_url, token, app_token, table_id)
        except RuntimeError as e:
            eprint(f"  [フィールド取得失敗] {e}")
            fields = []

        print(f"  フィールド（列）: {len(fields)} 列")
        for f in fields:
            fname = f.get("field_name", "(名称なし)")
            ftype = f.get("type")
            ui_type = f.get("ui_type", "")
            primary = "★主キー" if f.get("is_primary") else ""
            tname = field_type_name(ftype)
            ui_part = f" / ui:{ui_type}" if ui_type else ""
            print(f"    - {fname}  [type={ftype}:{tname}{ui_part}] {primary}".rstrip())

        # --- レコード（先頭数件）---
        try:
            records, total = search_records(
                base_url, token, app_token, table_id, RECORD_PAGE_SIZE
            )
        except RuntimeError as e:
            eprint(f"  [レコード取得失敗] {e}")
            records, total = [], None

        total_str = f"{total} 件" if total is not None else "取得不可"
        print(f"  レコード総数: {total_str}"
              f"（先頭 {len(records)} 件を取得）")

        # サンプル表示（最大 SAMPLE_RECORD_LIMIT 件）
        for r_idx, rec in enumerate(records[:SAMPLE_RECORD_LIMIT], start=1):
            rec_id = rec.get("record_id", "(id不明)")
            fields_map = rec.get("fields", {}) or {}
            print(f"    -- サンプル {r_idx} (record_id={rec_id}) --")
            if not fields_map:
                print("       （空のレコード）")
                continue
            for col_name, col_value in fields_map.items():
                print(f"       {col_name}: {format_field_value(col_value)}")

        print("-" * 70)

    print("")
    print("点検完了（読み取り専用。作成/更新/削除は行っていません）。")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        eprint(f"[エラー] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        eprint("\n中断されました。")
        sys.exit(130)
