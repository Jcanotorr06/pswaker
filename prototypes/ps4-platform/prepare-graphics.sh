#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(realpath "${1:?Pass the Linux build root}")
mkdir -p "$ROOT/src" "$ROOT/evidence" "$ROOT/toolchain"
cp "$HERE/ps4.cmake" "$ROOT/toolchain/ps4.cmake"
if [[ ! -d "$ROOT/tools" ]]; then cp -a "$ROOT/refs/dusklight/tools" "$ROOT/tools"; fi
if [[ ! -d "$ROOT/src/mesa/.git" ]]; then
  git clone --depth 1 --branch mesa-26.0.8 --single-branch https://gitlab.freedesktop.org/mesa/mesa.git "$ROOT/src/mesa"
fi
test "$(git -C "$ROOT/src/mesa" rev-parse HEAD)" = 60e95b787857afbc9a00b693b91c0d9c8923a430
if [[ ! -f "$ROOT/src/mesa/.pswaker-patched" ]]; then
  git -C "$ROOT/src/mesa" apply "$ROOT/refs/dusklight/patches/mesa-26.0.8-ps4.patch"
  touch "$ROOT/src/mesa/.pswaker-patched"
fi
if [[ ! -d "$ROOT/src/libdrm/.git" ]]; then
  git clone --depth 1 --branch libdrm-2.4.125 --single-branch https://gitlab.freedesktop.org/mesa/drm.git "$ROOT/src/libdrm"
fi
git -C "$ROOT/src/libdrm" rev-parse HEAD > "$ROOT/evidence/libdrm-revision.txt"
test "$(cat "$ROOT/evidence/libdrm-revision.txt")" = 76a1e97a9a7c29fa3035bb370d654791bdc23d90
python3 -m venv "$ROOT/mesa-venv"
"$ROOT/mesa-venv/bin/pip" download --dest "$ROOT/downloads/python" meson==1.9.1 Mako==1.3.10 PyYAML==6.0.3 packaging==25.0 MarkupSafe==3.0.3
sha256sum "$ROOT/downloads/python/"* > "$ROOT/evidence/python-wheels.sha256"
"$ROOT/mesa-venv/bin/pip" install --no-index --find-links "$ROOT/downloads/python" meson==1.9.1 Mako==1.3.10 PyYAML==6.0.3 packaging==25.0 MarkupSafe==3.0.3
"$ROOT/mesa-venv/bin/pip" freeze > "$ROOT/evidence/python-tools.txt"
echo 'Mesa/header/host inputs prepared; no target behavior validated.'
