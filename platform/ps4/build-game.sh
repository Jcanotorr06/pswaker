#!/usr/bin/env bash
# Build against an explicit maintained platform; never modify its diagnostic inputs.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
OWNERSHIP="$HERE/../../tools/pswaker/build_inputs.py"
ROOT=$(realpath -m "${1:?Pass an absolute Linux game build-root path}")
PLATFORM=$(realpath "${2:?Pass the verified maintained PS4 platform root}")
VERSION=${3:-01.00}
[[ "$ROOT" != "$PLATFORM" && "$ROOT" != *' '* ]] || { echo 'Use a separate game root without spaces' >&2; exit 1; }
source "$PLATFORM/tools/env.sh"
unset CC CXX CFLAGS CXXFLAGS CPPFLAGS LDFLAGS
python3 "$(python3 "$OWNERSHIP" command inputs.py)" host "$PLATFORM"
python3 "$HERE/prepare-game.py" "$ROOT" --platform-root "$PLATFORM"
BUILD_ID=$(python3 "$HERE/game-build.py" identity "$ROOT" "$PLATFORM")
cmake -S "$HERE/game" -B "$ROOT/build" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$PLATFORM/toolchain/ps4.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DPS4_MESA_BUILD="$PLATFORM/build/mesa" \
  -DPS4_PAID=0x3800000000000035 -DPSWAKER_BUILD_ID="$BUILD_ID" \
  -DPSWAKER_GAME_ROOT="$ROOT" > "$ROOT/evidence/game-configure.log" 2>&1
cmake --build "$ROOT/build" --target switchwaker_eboot --parallel "${JOBS:-8}" \
  > "$ROOT/evidence/game-compile.log" 2>&1
python3 "$HERE/game-build.py" stage "$ROOT" "$PLATFORM" --app-version "$VERSION"
