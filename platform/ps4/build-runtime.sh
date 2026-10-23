#!/usr/bin/env bash
# First build stage only; not a substitute for the agreed platform diagnostic.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=${1:?Pass the absolute Linux build-root path}
export PSB=$(realpath "$ROOT")
export PS4_BUILD_ROOT=$PSB
export OPENORBIS="$PSB/sdk/opt/pacbrew/ps4/openorbis"
export OO_PS4_TOOLCHAIN=$OPENORBIS
export PS4_SYSROOT="$PSB/sysroot"
export JOBS=${JOBS:-8}
export LLVM_LOCAL_SRC=/nonexistent
DOLPHINPS4="$PSB/refs/DolphinPS4"
mkdir -p "$PSB/evidence"
{ clang-21 --version; cmake --version; ninja --version; uname -sr; cat /etc/os-release; dpkg-query -W; } > "$PSB/evidence/host-tools.txt"
# The source must have been downloaded/digest-checked and patched by prepare-sources.py.
test -f "$PSB/src/llvm-project-21.1.6.src/.pswaker-libcxx-ps4-atomic-wait.patch"
chmod +x "$DOLPHINPS4/toolchain/prepare-sysroot.sh"
bash "$DOLPHINPS4/toolchain/build-libcxx.sh" 2>&1 | tee "$PSB/evidence/libcxx-build.log"
cmake -S "$HERE/runtime-preflight" -B "$PSB/build/runtime-preflight" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$DOLPHINPS4/toolchain/ps4-love-modern.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DDOLPHINPS4="$DOLPHINPS4" \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DPS4_PAID=0x3800000000000035 2>&1 | tee "$PSB/evidence/runtime-configure.log"
cmake --build "$PSB/build/runtime-preflight" --parallel "$JOBS" 2>&1 | tee "$PSB/evidence/runtime-build.log"
find "$PSB/build/runtime-preflight" -name eboot.bin -exec sha256sum {} \; > "$PSB/evidence/runtime-artifact-hashes.txt"
echo 'Runtime build preflight finished. Graphics, audio, pad, packaging, two clean builds and Slim tests remain.'
