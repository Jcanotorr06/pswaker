#!/usr/bin/env bash
# Build the pinned, patched SDL source for the host with the console's video options.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(realpath "${1:?Pass the prepared persistent platform root}")
BUILD="$ROOT/build/host-sdl-repro"
cmake -S "$ROOT/src/sdl3" -B "$BUILD" -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DSDL_SHARED=OFF -DSDL_STATIC=ON -DSDL_TEST_LIBRARY=OFF -DSDL_TESTS=OFF \
  -DSDL_UNIX_CONSOLE_BUILD=ON -DSDL_X11=OFF -DSDL_WAYLAND=OFF -DSDL_KMSDRM=OFF \
  -DSDL_VULKAN=OFF -DSDL_OPENGL=OFF -DSDL_OPENGLES=OFF -DSDL_OPENVR=OFF \
  -DSDL_AUDIO=OFF -DSDL_JOYSTICK=OFF -DSDL_HAPTIC=OFF -DSDL_SENSOR=OFF \
  -DSDL_CAMERA=OFF -DSDL_DIALOG=OFF -DSDL_TRAY=OFF -DSDL_HIDAPI=OFF \
  -DSDL_RENDER_GPU=OFF -DSDL_DUMMYVIDEO=ON -DSDL_OFFSCREEN=ON \
  > "$ROOT/evidence/host-sdl-configure.log" 2>&1
cmake --build "$BUILD" --target SDL3-static --parallel 5 > "$ROOT/evidence/host-sdl-build.log" 2>&1
c++ -std=c++17 "$HERE/main.cpp" -I"$ROOT/src/sdl3/include" "$BUILD/libSDL3.a" -pthread -ldl -lm -o "$BUILD/startup-repro"
echo "Built $BUILD/startup-repro; this does not test PS4 presentation."
