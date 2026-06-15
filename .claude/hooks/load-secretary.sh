#!/usr/bin/env bash
set -euo pipefail

# SessionStart: 秘書プロフィールと直近の会話ログを文脈へ読み込み、
# 毎回「同じ秘書」として会話を続けられるようにする。

ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
PROFILE="$ROOT/data/memory/secretary/secretary-profile.md"
LOG="$ROOT/data/memory/secretary/conversation-log.md"

# 本文を実際の改行で組み立てる
CTX="あなたはこのリポジトリの秘書（経営者の右腕AI）として振る舞う。"

if [ -f "$PROFILE" ]; then
  CTX="$CTX 以下が秘書プロフィール。この名前・人格で応答すること。

--- secretary-profile.md ---
$(cat "$PROFILE")"
else
  CTX="$CTX 秘書プロフィール未設定。名前を聞かれたら、初期セットアップ（./data/tools/scripts/init-secretary.sh \"名前\"）での設定を案内すること。"
fi

if [ -f "$LOG" ]; then
  CTX="$CTX

--- conversation-log.md (直近) ---
$(tail -n 40 "$LOG")"
fi

CTX="$CTX

継続して覚えるべきこと（呼び方・好み・進行中の判断・約束）が出たら conversation-log.md に短く追記すること。"

# JSON エスケープして additionalContext で返す
ESCAPED="$(printf '%s' "$CTX" | jq -Rs '.' 2>/dev/null || printf '"%s"' "$CTX")"
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}\n' "$ESCAPED"
