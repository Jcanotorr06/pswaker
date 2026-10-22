#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=${1:?Pass the existing locked platform input root}
OUT=${2:?Pass the separate Linux host build directory}
cmake -S "$HERE" -B "$OUT/repro" -G Ninja \
  -DCMAKE_C_COMPILER=clang-21 -DCMAKE_CXX_COMPILER=clang++-21 \
  -DCMAKE_BUILD_TYPE=Release -DPLATFORM_ROOT="$ROOT" -DHOST_ROOT="$OUT"
