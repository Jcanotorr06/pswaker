#!/usr/bin/env bash
# Throwaway Linux reproduction of the pinned Aurora call path, not a PS4 pass.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=${1:?Pass the existing locked platform input root}
OUT=${2:?Pass a separate Linux host build directory}
mkdir -p "$OUT"
cmake -S "$ROOT/src/sdl3" -B "$OUT/sdl" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DSDL_SHARED=OFF -DSDL_STATIC=ON \
  -DSDL_X11=ON -DSDL_WAYLAND=OFF -DSDL_TESTS=OFF > "$OUT/sdl-configure.log" 2>&1
cmake --build "$OUT/sdl" --parallel 8 > "$OUT/sdl-build.log" 2>&1
cmake -S "$ROOT/src/dawn" -B "$OUT/dawn" -G Ninja \
  -DCMAKE_C_COMPILER=clang-21 -DCMAKE_CXX_COMPILER=clang++-21 \
  -DCMAKE_BUILD_TYPE=Release '-DCMAKE_C_FLAGS_RELEASE=-O0 -DNDEBUG' \
  '-DCMAKE_CXX_FLAGS_RELEASE=-O0 -DNDEBUG' -DDAWN_FETCH_DEPENDENCIES=OFF \
  -DDAWN_BUILD_MONOLITHIC_LIBRARY=STATIC -DDAWN_BUILD_PROTOBUF=OFF \
  -DTINT_BUILD_IR_BINARY=OFF -DDAWN_SUPPORTS_CXX_MODULES=OFF \
  -DDAWN_BUILD_SAMPLES=OFF -DDAWN_BUILD_TESTS=OFF -DDAWN_BUILD_BENCHMARKS=OFF \
  -DDAWN_ENABLE_D3D11=OFF -DDAWN_ENABLE_D3D12=OFF -DDAWN_ENABLE_METAL=OFF \
  -DDAWN_ENABLE_DESKTOP_GL=OFF -DDAWN_ENABLE_OPENGLES=OFF -DDAWN_ENABLE_NULL=OFF \
  -DDAWN_ENABLE_VULKAN=ON -DDAWN_ENABLE_WEBGPU_ON_WEBGPU=OFF \
  -DDAWN_SUPPORTS_GLFW_FOR_WINDOWING=OFF -DDAWN_USE_X11=ON -DDAWN_USE_WAYLAND=OFF \
  -DTINT_BUILD_TESTS=OFF -DTINT_BUILD_CMD_TOOLS=OFF -DTINT_BUILD_SPV_WRITER=ON \
  -DTINT_BUILD_GLSL_WRITER=OFF -DTINT_BUILD_HLSL_WRITER=OFF -DTINT_BUILD_MSL_WRITER=OFF \
  > "$OUT/dawn-configure.log" 2>&1
cmake --build "$OUT/dawn" --target webgpu_dawn --parallel 8 > "$OUT/dawn-build.log" 2>&1
bash "$HERE/configure-repro.sh" "$ROOT" "$OUT" > "$OUT/repro-configure.log" 2>&1
cmake --build "$OUT/repro" --parallel 8 > "$OUT/repro-build.log" 2>&1
