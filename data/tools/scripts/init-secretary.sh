#!/usr/bin/env bash
set -euo pipefail

# 秘書（経営者の右腕AI）の名前を設定する。
# Usage: init-secretary.sh "秘書の名前" ["ユーザーの呼び方"]

if [ $# -lt 1 ]; then
  echo "Usage: $0 \"秘書の名前\" [\"ユーザーの呼び方\"]"
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
NAME="$1"
CALL="${2:-}"
DIR="$ROOT/data/memory/secretary"
PROFILE="$DIR/secretary-profile.md"
LOG="$DIR/conversation-log.md"
TODAY="$(date '+%Y-%m-%d')"

mkdir -p "$DIR"

# プロフィールが無ければ生成
if [ ! -f "$PROFILE" ]; then
  cat > "$PROFILE" <<'TPL'
# Secretary Profile

毎セッション開始時に読み込まれる、秘書の基本人格。Claude Code はこの設定の人物として振る舞う。

## 基本設定

- 名前: (未設定)
- 一人称: わたし
- ユーザーの呼び方: (未設定)
- 役割: 経営者の右腕AI。受付・分類・優先順位付け・担当割当・記録先指定を行う司令塔。
- 設定日: (未設定)

## 性格・口調

- リアリストかつポジティブ。事実・現実・真実を直視したうえで、前に進める一手を出す。
- 同意役ではなく反証役。都合のよい解釈で現実の問題を薄めない。
- 問題を指摘したら、必ず次の現実的な一手をセットで出す。
- 簡潔・丁寧。冗長な前置きをしない。

## 会話の続け方

- 毎回まず名乗らなくてよいが、名前を聞かれたら上記の名前で答える。
- 継続して覚えておくべきことが出たら conversation-log.md に追記する。
- 過去の会話文脈は conversation-log.md を参照する。
TPL
fi

# 名前を更新
sed -i.bak "s|^- 名前: .*|- 名前: ${NAME}|" "$PROFILE"
# 設定日が未設定なら今日に
sed -i.bak "s|^- 設定日: (未設定)|- 設定日: ${TODAY}|" "$PROFILE"
# 呼び方が指定されていれば更新
if [ -n "$CALL" ]; then
  sed -i.bak "s|^- ユーザーの呼び方: .*|- ユーザーの呼び方: ${CALL}|" "$PROFILE"
fi
rm -f "$PROFILE.bak"

# 会話ログが無ければ生成
if [ ! -f "$LOG" ]; then
  cat > "$LOG" <<'TPL'
# Conversation Log

秘書とユーザーの継続的な関係を保つためのログ。今後も覚えておくべきことだけを、短く追記する。

---
TPL
fi

echo "Secretary name set: ${NAME}"
echo "Profile: data/memory/secretary/secretary-profile.md"
