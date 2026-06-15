#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat || true)"
ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
mkdir -p "$ROOT/data/logs" "$ROOT/work/_inbox/99_logs"

PROMPT="$(echo "$INPUT" | jq -r '.prompt // empty' 2>/dev/null || true)"
NOW="$(date '+%Y-%m-%d %H:%M:%S')"

{
  echo ""
  echo "## $NOW"
  echo ""
  echo "$PROMPT"
} >> "$ROOT/work/_inbox/99_logs/instruction-log.md"

cat <<'MSG'
{"additionalContext":"今回のユーザー指示は work/_inbox/99_logs/instruction-log.md に記録済み。対象案件が明確なら該当 work/{project}/99_logs/instruction-log.md にも転記すること。"}
MSG
