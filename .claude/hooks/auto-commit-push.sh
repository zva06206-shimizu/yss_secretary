#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat || true)"
ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"

if [ ! -d "$ROOT/.git" ]; then
  exit 0
fi

cd "$ROOT"

if echo "$INPUT" | jq -e '.stop_hook_active == true' >/dev/null 2>&1; then
  exit 0
fi

if git diff --quiet && git diff --cached --quiet; then
  exit 0
fi

git add -A

if git diff --cached --name-only | grep -E '(^|/)\.env$|\.pem$|\.key$|\.p12$|\.pfx$' >/dev/null 2>&1; then
  echo "Sensitive file staged. Commit aborted." >&2
  exit 2
fi

SUMMARY="$(git diff --cached --name-only | head -20 | tr '\n' ' ')"
if [ -z "$SUMMARY" ]; then
  SUMMARY="project updates"
fi

git commit -m "chore: auto record Claude Code work" -m "Changed files: $SUMMARY" >/dev/null 2>&1 || exit 0

REMOTE="${GIT_REMOTE_NAME:-origin}"
if git remote get-url "$REMOTE" >/dev/null 2>&1; then
  BRANCH="$(git rev-parse --abbrev-ref HEAD)"
  git push "$REMOTE" "$BRANCH" >/dev/null 2>&1 || exit 0
fi

exit 0
