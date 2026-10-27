#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
PLATFORM=$(python3 "$HERE/build_inputs.py" platform)
ROOT=$(realpath "${1:?Pass the Linux build root}")
source "$ROOT/tools/env.sh"
export JOBS=${JOBS:-8}
BUILD_ID=$(python3 "$HERE/package-probe.py" "$ROOT" --identity-only)
cmake -S "$PLATFORM/probe" -B "$ROOT/build/probe" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$ROOT/toolchain/ps4.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DPS4_MESA_BUILD="$ROOT/build/mesa" \
  -DPS4_PAID=0x3800000000000035 -DPSWAKER_BUILD_ID="$BUILD_ID" > "$ROOT/evidence/probe-configure.log" 2>&1
cmake --build "$ROOT/build/probe" --target platform_diagnostic_eboot --parallel "$JOBS" > "$ROOT/evidence/probe-build.log" 2>&1
