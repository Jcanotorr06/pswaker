#!/usr/bin/env bash
set -euo pipefail
ROOT=$(realpath "${1:?Pass the Linux build root}")
source "$ROOT/tools/env.sh"
export JOBS=${JOBS:-8}
[[ -f "$PS4_SYSROOT/lib/libc++.a" ]]
bash "$ROOT/tools/build-sdl3.sh" > "$ROOT/evidence/sdl3-build.log" 2>&1
bash "$ROOT/tools/build-dawn.sh" > "$ROOT/evidence/dawn-build.log" 2>&1
bash "$ROOT/tools/build-mesa.sh" > "$ROOT/evidence/mesa-build.log" 2>&1
echo 'SDL/Dawn/Mesa archives built; hardware behavior untested.'
