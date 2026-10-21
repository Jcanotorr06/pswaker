#!/usr/bin/env bash
# Differential regression at the real pinned SDL backend-selection seam.
set -euo pipefail
ROOT=$(realpath "${1:?Pass the prepared persistent platform root}")
PROGRAM="$ROOT/build/host-sdl-repro/startup-repro"
set +e
"$PROGRAM" > "$ROOT/evidence/host-sdl-baseline.log" 2>&1
RESULT=$?
set -e
cat "$ROOT/evidence/host-sdl-baseline.log"
[[ "$RESULT" == 20 ]]
grep -Fxq 'FAIL SDL startup: No available video device' "$ROOT/evidence/host-sdl-baseline.log"
echo 'EXPECTED RED: original automatic selection reproduces the logged SDL failure.'
"$PROGRAM" --candidate > "$ROOT/evidence/host-sdl-candidate.log" 2>&1
cat "$ROOT/evidence/host-sdl-candidate.log"
grep -Fxq 'PASS SDL startup driver=dummy window=1920x1080 external-context=true' "$ROOT/evidence/host-sdl-candidate.log"
echo 'GREEN: shared diagnostic configuration passes SDL initialization and placeholder-window creation.'
echo 'LIMIT: no Aurora/Dawn/Mesa/PS4 rendering or console crash is executed here.'
