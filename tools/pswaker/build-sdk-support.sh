#!/usr/bin/env bash
# Rebuild linked target support rather than inheriting SDK CPU/compiler settings.
set -euo pipefail
ROOT=$(realpath "${1:?Pass the Linux build root}")
export PSB=$ROOT
export OPENORBIS="$ROOT/sdk/opt/pacbrew/ps4/openorbis"
source "$ROOT/refs/DolphinPS4/toolchain/env.sh"
FLAGS="--target=$PS4_TARGET -march=btver2 -ftls-model=initial-exec -fPIC -DPS4 -D__PS4__ -D_LIBUNWIND_IS_BAREMETAL=1 -DPS4_FLEXIBLE_MEMORY=1"
MUSL="$ROOT/src/sdk-source/musl/ps4-openorbis-musl-140a653299ffcb1457bc63a5ab1f507d7bb37c54"
mkdir -p "$ROOT/build/musl"
cd "$ROOT/build/musl"
sh "$MUSL/configure" --target=x86_64-scei-ps4 --prefix="$OPENORBIS" --disable-shared \
  CC=clang-21 AR=llvm-ar-21 RANLIB=llvm-ranlib-21 CFLAGS="$FLAGS"
make -j"$JOBS"
# Preserve the SDK's header ordering; rebuild only its linked libc/CRT objects.
cp lib/libc.a lib/crt1.o lib/crti.o lib/crtn.o "$OPENORBIS/lib/"
LLVM="$ROOT/src/llvm-project-12.0.1.src"
COMMON=(-G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_NAME=FreeBSD
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
  -DCMAKE_C_COMPILER=clang-21 -DCMAKE_CXX_COMPILER=clang++-21
  -DCMAKE_C_COMPILER_TARGET="$PS4_TARGET" -DCMAKE_CXX_COMPILER_TARGET="$PS4_TARGET"
  -DCMAKE_AR=/usr/bin/llvm-ar-21 -DCMAKE_RANLIB=/usr/bin/llvm-ranlib-21
  -DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY -DCMAKE_INSTALL_PREFIX="$OPENORBIS"
  "-DCMAKE_C_FLAGS=$FLAGS --sysroot=$OPENORBIS -isystem $OPENORBIS/include"
  "-DCMAKE_CXX_FLAGS=$FLAGS --sysroot=$OPENORBIS -isystem $OPENORBIS/include")
cmake -S "$LLVM/compiler-rt" -B "$ROOT/build/builtins" "${COMMON[@]}" \
  -DLLVM_CMAKE_DIR="$LLVM/llvm/cmake/modules" -UCOMPILER_RT_DEFAULT_TARGET_TRIPLE \
  -DCOMPILER_RT_DEFAULT_TARGET_ONLY=ON -DCOMPILER_RT_BAREMETAL_BUILD=ON \
  -DCOMPILER_RT_BUILD_BUILTINS=ON -DCOMPILER_RT_BUILD_CRT=OFF -DCOMPILER_RT_BUILD_SANITIZERS=OFF \
  -DCOMPILER_RT_BUILD_XRAY=OFF -DCOMPILER_RT_BUILD_LIBFUZZER=OFF -DCOMPILER_RT_BUILD_PROFILE=OFF
cmake --build "$ROOT/build/builtins" --target builtins --parallel "$JOBS"
cp "$ROOT/build/builtins/lib/freebsd/libclang_rt.builtins-x86_64.a" "$OPENORBIS/lib/"
cmake -S "$LLVM/libunwind" -B "$ROOT/build/libunwind" "${COMMON[@]}" \
  "-DCMAKE_CXX_FLAGS=$FLAGS --sysroot=$OPENORBIS -isystem $OPENORBIS/include -include alloca.h" \
  -DLLVM_PATH="$LLVM/llvm" -DLIBUNWIND_USE_COMPILER_RT=YES -DLIBUNWIND_BUILD_32_BITS=NO \
  -DLIBUNWIND_ENABLE_STATIC=ON -DLIBUNWIND_ENABLE_SHARED=OFF -DLIBUNWIND_INCLUDE_TESTS=OFF
cmake --build "$ROOT/build/libunwind" --parallel "$JOBS"
cp "$ROOT/build/libunwind/lib/libunwind.a" "$OPENORBIS/lib/"
ZLIB="$ROOT/src/zlib-1.3.1"
cmake -S "$ZLIB" -B "$ROOT/build/zlib" "${COMMON[@]}" -DZLIB_BUILD_EXAMPLES=OFF
cmake --build "$ROOT/build/zlib" --target zlibstatic --parallel "$JOBS"
cp "$ROOT/build/zlib/libz.a" "$OPENORBIS/usr/lib/"
cmake -S "$ROOT/src/libpng-1.6.37" -B "$ROOT/build/libpng" "${COMMON[@]}" \
  -DPNG_SHARED=OFF -DPNG_STATIC=ON -DPNG_TESTS=OFF \
  -DZLIB_LIBRARY="$OPENORBIS/usr/lib/libz.a" -DZLIB_INCLUDE_DIR="$OPENORBIS/usr/include"
cmake --build "$ROOT/build/libpng" --target png_static --parallel "$JOBS"
cp "$ROOT/build/libpng/libpng16.a" "$OPENORBIS/usr/lib/"
cp "$ROOT/build/libpng/libpng16.a" "$OPENORBIS/usr/lib/libpng.a"
cp "$ROOT/build/libpng/pnglibconf.h" "$OPENORBIS/usr/include/libpng16/"
cp "$ROOT/build/libpng/pnglibconf.h" "$OPENORBIS/usr/include/pnglibconf.h"
make -C "$ROOT/src/bzip2-1.0.6" -j"$JOBS" libbz2.a CC=clang-21 AR=llvm-ar-21 RANLIB=llvm-ranlib-21 \
  "CFLAGS=$FLAGS --sysroot=$OPENORBIS -isystem $OPENORBIS/include -D_FILE_OFFSET_BITS=64"
cp "$ROOT/src/bzip2-1.0.6/libbz2.a" "$OPENORBIS/usr/lib/"
find "$ROOT/build/musl/lib" "$ROOT/build/builtins" "$ROOT/build/libunwind" "$ROOT/build/zlib" \
  "$ROOT/build/libpng" "$ROOT/src/bzip2-1.0.6" \
  -name '*.a' -exec sha256sum {} \; > "$ROOT/evidence/sdk-rebuilt-archives.sha256"
