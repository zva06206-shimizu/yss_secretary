#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 company-slug"
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SLUG="$1"
SRC="$ROOT/data/_template"
DST="$ROOT/data/memory/company/$SLUG"

if [ ! -d "$SRC" ]; then
  echo "Template directory not found: $SRC"
  exit 1
fi

if [ -e "$DST" ]; then
  echo "Company data already exists: $DST"
  exit 1
fi

mkdir -p "$(dirname "$DST")"
cp -R "$SRC" "$DST"
find "$DST" -type f -name "*.md" -print0 | xargs -0 sed -i.bak "s/{{COMPANY_SLUG}}/$SLUG/g" || true
find "$DST" -type f -name "*.bak" -delete || true

echo "Created company memory: data/memory/company/$SLUG"
echo "Use work/ for active work."
