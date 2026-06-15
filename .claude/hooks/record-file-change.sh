#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat || true)"
ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
LOG_DIR="$ROOT/data/logs"
LOG_FILE="$LOG_DIR/file-change-log.md"
mkdir -p "$LOG_DIR"

NOW="$(date '+%Y-%m-%d %H:%M:%S')"
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null || true)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"

{
  echo ""
  echo "## $NOW"
  echo ""
  echo "- tool: ${TOOL_NAME:-unknown}"
  echo "- file: ${FILE_PATH:-unknown}"
} >> "$LOG_FILE"

exit 0
