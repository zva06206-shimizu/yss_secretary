#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)"

case "$FILE_PATH" in
  *.env|*/.env|*.pem|*.key|*.p12|*.pfx)
    echo "Blocked editing sensitive file directly: $FILE_PATH. Use .env.example or documented setup instructions instead." >&2
    exit 2
    ;;
esac

exit 0
