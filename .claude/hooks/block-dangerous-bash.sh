#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"

# jq があれば command を抽出。無ければ生JSONを対象に最低限スキャンする（素通り防止）。
if command -v jq >/dev/null 2>&1; then
  COMMAND="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null || true)"
  [ -z "$COMMAND" ] && COMMAND="$INPUT"
else
  COMMAND="$INPUT"
fi

# 空入力は対象外
[ -z "$COMMAND" ] && exit 0

# 危険コマンドの検出パターン（空白ゆらぎに耐えるよう [[:space:]]+ を使用）
DENY_PATTERNS=(
  'rm[[:space:]]+-[a-zA-Z]*[rf][a-zA-Z]*[[:space:]]+(/|~|\*|\$HOME)'
  'sudo[[:space:]]+rm[[:space:]]+-[a-zA-Z]*r'
  'drop[[:space:]]+database'
  'truncate[[:space:]]+table'
  'chmod[[:space:]]+-R[[:space:]]+777[[:space:]]+/'
  '(curl|wget)[[:space:]].*\|[[:space:]]*(ba|z)?sh'
  ':\(\)[[:space:]]*\{[[:space:]]*:[[:space:]]*\|[[:space:]]*:'
  'mkfs\.'
  'dd[[:space:]]+if=.*[[:space:]]*of=/dev/'
)

for pattern in "${DENY_PATTERNS[@]}"; do
  if printf '%s' "$COMMAND" | grep -Eiq "$pattern"; then
    echo "Blocked dangerous command by project policy: $COMMAND" >&2
    exit 2
  fi
done

exit 0
