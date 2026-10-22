#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
OUT=${1:?Pass the separate Linux host build directory}
VARIANT=${2:-baseline}
set +e
bash "$HERE/run.sh" "$OUT" "$VARIANT" > "$OUT/$VARIANT.log" 2>&1
status=$?
set -e
printf 'variant=%s exit=%s\n' "$VARIANT" "$status"
grep -E '^(FAIL internal|PASS internal|PIXEL|FRAME|RESULT)' "$OUT/$VARIANT.log" | tail -n 8
exit "$status"
