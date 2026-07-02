#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lark Base（国際版 open.larksuite.com）Bitable 読み取り専用点検スクリプト。

同じフォルダの .env から接続情報を読み、指定した App Token（Base）内の
全テーブル・各テーブルのフィールド一覧・レコードの先頭数件を「のぞく」だけ。
作成・更新・削除は一切行わない（認証POSTと records/search（読み取り）のみ）。

--- .env の書式（このスクリプトと同じフォルダに置く） ---
    LARK_APP_ID=cli_xxxxxxxxxxxxx
    LARK_APP_SECRET=xxxxxxxxxxxxxxxx
    LARK_APP_TOKEN=basxxxxxxxxxxxxxxx
    # 任意。既定は open.larksuite.com（国際版）。中国版は open.feishu.cn
    LARK_DOMAIN=open.larksuite.com

  書式の注意:
    - `#` で始まる行と空行は無視（行頭コメントのみ。行末インラインコメントは値に残る）。
    - `KEY=VALUE`。最初の `=` で分割するので値に `=` を含めてよい。
    - 値の両端が同じクォート（' か "）で囲まれていれば、その中身をそのまま採用
      （クォート内の前後空白は保持する）。クォートが無い場合のみ前後空白を除去。
    - 行頭 `export KEY=...` にも対応（`export ` は取り除く）。
    - BOM 付き UTF-8（utf-8-sig）に対応。

--- PowerShell での実行例（Windows） ---
    # このスクリプトのあるフォルダへ移動
    cd C:\\git\\yss_secretary

    # そのまま実行（.env を自動で読む）
    python .\\inspect_lark.py

    # コンソールが cp932 のままでも、本スクリプトは標準出力/標準エラーを
    # UTF-8 に再構成して出力するため、日本語や絵文字で異常終了しない。
    # それでも表示が化ける場合は、コンソール自体を UTF-8 にすると綺麗になる:
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
# 標準出力/標準エラーを UTF-8 へ再構成（Windows cp932 での UnicodeEncodeError 回避）
# ---------------------------------------------------------------------------
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # Python 3.7+
    except Exception:  # noqa: BLE001  reconfigure 非対応環境でも落とさない
        pass

# ---------------------------------------------------------------------------
# 定数
# ---------------------------------------------------------------------------
DEFAULT_DOMAIN = "open.larksuite.com"
RECORD_PAGE_SIZE = 5          # レコードは先頭少数だけのぞく（search 上限500に対し十分小さい）
SAMPLE_RECORD_LIMIT = 3       # サンプル表示するレコード件数
VALUE_TRUNCATE = 60           # 値表示の切り詰め文字数
HTTP_TIMEOUT = 30             # 秒
TABLES_PAGE_SIZE = 100        # tables 一覧の page_size（上限100）
FIELDS_PAGE_SIZE = 100        # fields 一覧の page_size（上限100）
MAX_PAGES = 1000              # ページネーション無限ループ防御の上限

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
    - 行頭 `export KEY=...` は `export ` を取り除いて扱う。
    - `KEY=VALUE` 形式。最初の `=` で分割（値に `=` を含めてよい）。
    - 値の両端が同じクォート（' か "）で囲まれていれば中身をリテラルに採用
      （クォート内の前後空白は保持）。クォートが無い場合のみ前後空白を除去。
    外部依存（python-dotenv 等）は使わない。
    """
    env = {}
    if not os.path.isfile(path):
        return env
    with open(path, "r", encoding="utf-8-sig") as f:
        for raw in f:
            # CRLF の \r を含め両端の空白を落として行を判定
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            # 行頭 export 対応（例: export LARK_APP_ID=...）
            if key.startswith("export ") or key.startswith("export\t"):
                key = key[len("export"):].strip()
            if not key:
                continue
            # クォート判定は「前後空白を落とした形」で行うが、
            # クォート内は strip せずリテラルに保持する。
            stripped = value.strip()
            if (
                len(stripped) >= 2
                and stripped[0] == stripped[-1]
                and stripped[0] in ("'", '"')
            ):
                value = stripped[1:-1]  # クォート内はそのまま
            else:
                value = stripped        # クォート無しは前後空白を除去
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


# 日付系（エポックミリ秒で来る）の型ID
DATE_LIKE_TYPES = frozenset({5, 1001, 1002})


def format_epoch_millis(value):
    """エポックミリ秒（数値）を人間可読な日時文字列に変換。失敗時は生値表示。"""
    try:
        import datetime
        seconds = float(value) / 1000.0
        dt = datetime.datetime.fromtimestamp(seconds)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:  # noqa: BLE001  変換不能なら生値のまま
        return str(value)


def format_field_value(value, field_type=None):
    """fields の値（型により形が変わる）を表示用文字列にする。

    field_type が日付系（5/1001/1002）で値が数値のとき、エポックミリ秒を
    人間可読な日時へ変換して見やすくする。
    """
    if value is None:
        return ""
    # 日付系はエポックミリ秒 → 可読日時に変換（bool は日付ではないので除外）
    if (
        field_type in DATE_LIKE_TYPES
        and isinstance(value, (int, float))
        and not isinstance(value, bool)
    ):
        return truncate(format_epoch_millis(value))
    # 単純型（真偽 → 数値 → 文字列の順で判定）
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (str, int, float)):
        return truncate(value)
    # 複数選択など文字列配列 / ユーザー型などオブジェクト配列
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict):
                # ユーザー型: name、テキストセグメント型: text、リンク型: link
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


def build_url(base_url, path, query=None):
    """パスパラメータを quote した安全な URL を組み立てる。

    path 内の各セグメントは呼び出し側で quote 済みを前提とし、query は
    urlencode で組む（将来 view_id 等を足しても事故りにくい）。
    """
    url = base_url + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    return url


# ---------------------------------------------------------------------------
# HTTP（標準ライブラリのみ）
# ---------------------------------------------------------------------------
def http_request(method, url, headers=None, body=None):
    """HTTP リクエストを送り、(status_code, parsed_json) を返す。

    2xx でない場合も本文を JSON として読めれば返す（Lark はエラーでも
    {code, msg} を返すため）。JSON にできなければ例外を送出。
    例外・本文には秘密値（app_secret / token）を載せない
    （secret は body のみ、token は URL に載せず Authorization ヘッダ）。
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
    elif code is None:
        eprint("  ヒント: 想定外のレスポンス構造です（code キーがありません）。"
               "ドメインやエンドポイントを確認してください。")
    else:
        eprint("  ヒント: アプリのスコープ付与、Baseへのアプリ追加、"
               "App Token の値を確認してください。")
    sys.exit(1)


# ---------------------------------------------------------------------------
# ページネーション共通ヘルパ（tables / fields）
# ---------------------------------------------------------------------------
def paginate_get(base_url, path, headers, page_size, context):
    """GET のページネーションを回して items を集約する。

    無限ループ防御:
      - MAX_PAGES を超えたら打ち切り。
      - page_token が前回と同じ値のまま返り続けたら打ち切り。
    """
    items = []
    page_token = None
    prev_token = None
    for _ in range(MAX_PAGES):
        query = {"page_size": page_size}
        if page_token:
            query["page_token"] = page_token
        _status, parsed = http_request(
            "GET", build_url(base_url, path, query), headers=headers
        )
        check_lark_ok(parsed, context)
        data = parsed.get("data", {}) or {}
        items.extend(data.get("items", []) or [])
        next_token = data.get("page_token")
        if not (data.get("has_more") and next_token):
            break
        # 同じ page_token を返し続けるサーバ不具合への防御
        if next_token == prev_token:
            eprint(f"  [警告] {context}: page_token が変化しないため打ち切ります。")
            break
        prev_token = page_token
        page_token = next_token
    else:
        eprint(f"  [警告] {context}: ページ数が上限({MAX_PAGES})に達したため打ち切ります。")
    return items


# ---------------------------------------------------------------------------
# Lark API 呼び出し
# ---------------------------------------------------------------------------
def get_tenant_access_token(base_url, app_id, app_secret):
    """自社開発アプリの tenant_access_token を取得。

    仕様: POST /open-apis/auth/v3/tenant_access_token/internal
    Authorization ヘッダは不要。トークンはレスポンス直下（data入れ子ではない）。
    app_secret は body でのみ送る（URL には載せない）。
    """
    url = build_url(base_url, "/open-apis/auth/v3/tenant_access_token/internal")
    body = {"app_id": app_id, "app_secret": app_secret}
    _status, parsed = http_request("POST", url, body=body)

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
    path = f"/open-apis/bitable/v1/apps/{urllib.parse.quote(app_token, safe='')}/tables"
    headers = {"Authorization": f"Bearer {token}"}
    return paginate_get(
        base_url, path, headers, TABLES_PAGE_SIZE, "テーブル一覧取得"
    )


def list_fields(base_url, token, app_token, table_id):
    """テーブルのフィールド（列）一覧を取得（ページネーション対応）。"""
    path = (
        f"/open-apis/bitable/v1/apps/{urllib.parse.quote(app_token, safe='')}"
        f"/tables/{urllib.parse.quote(table_id, safe='')}/fields"
    )
    headers = {"Authorization": f"Bearer {token}"}
    return paginate_get(
        base_url, path, headers, FIELDS_PAGE_SIZE,
        f"フィールド一覧取得 (table_id={table_id})",
    )


def search_records(base_url, token, app_token, table_id, page_size):
    """レコードを検索（POST records/search・推奨API）で先頭ページのみ取得。

    読み取り専用のため、fetch は1ページ（先頭 page_size 件）に限定する。
    戻り値: (items, total)
    """
    path = (
        f"/open-apis/bitable/v1/apps/{urllib.parse.quote(app_token, safe='')}"
        f"/tables/{urllib.parse.quote(table_id, safe='')}/records/search"
    )
    url = build_url(base_url, path, {"page_size": page_size})
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    # filter/sort を空にして view 全体の先頭から。automatic_fields は不要。
    body = {"automatic_fields": False}
    _status, parsed = http_request("POST", url, headers=headers, body=body)
    check_lark_ok(parsed, f"レコード検索 (table_id={table_id})")
    data = parsed.get("data", {}) or {}
    return data.get("items", []) or [], data.get("total")


# ---------------------------------------------------------------------------
# 各テーブルのフィールド → 型ID の対応を作る（値の可読化に使う）
# ---------------------------------------------------------------------------
def build_field_type_map(fields):
    """field_name -> type の辞書を作る。"""
    m = {}
    for f in fields:
        name = f.get("field_name")
        if name is not None:
            m[name] = f.get("type")
    return m


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

    # 点検結果本体は stdout、進捗/エラーは stderr に寄せる（パイプ時に扱いやすい）
    eprint("=" * 70)
    eprint("Lark Base 点検（読み取り専用）")
    eprint("=" * 70)
    eprint(f"ドメイン    : {base_url}")
    eprint(f"APP_ID      : {app_id}")            # app_id は識別子。秘密ではない
    eprint(f"APP_SECRET  : {mask_secret(app_secret)}")   # マスク
    eprint(f"APP_TOKEN   : {app_token}")         # Base識別子。秘密トークンではない
    eprint("-" * 70)

    # (1) 認証（token はマスク表示。secret は body のみで送出）
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

        field_type_map = build_field_type_map(fields)

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

        # total はこのビュー全体の件数（filter/sort 未指定）。
        total_str = f"{total} 件" if total is not None else "取得不可"
        print(f"  このビューのレコード総数: {total_str}"
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
                ftype = field_type_map.get(col_name)
                print(f"       {col_name}: {format_field_value(col_value, ftype)}")

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
