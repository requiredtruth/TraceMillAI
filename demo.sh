#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || { echo "Run ./install.sh first." >&2; exit 1; }
TEMP=$(mktemp -d "${TMPDIR:-/tmp}/tracemillai-demo.XXXXXX")
trap 'rm -rf "$TEMP"' EXIT HUP INT TERM
cd "$ROOT"
"$PY" -m tracemillai examples/failure.jsonl \
    --out "$TEMP/minimized.jsonl" \
    --failing-code 7 \
    -- "$PY" examples/reproduce_failure.py '{trace}'
