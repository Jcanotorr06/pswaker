#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
PLATFORM=$(python3 "$HERE/build_inputs.py" platform)
ROOT=$(realpath "${1:?Pass the Linux build root}")
mkdir -p "$ROOT/src" "$ROOT/evidence" "$ROOT/toolchain"
cp "$PLATFORM/ps4.cmake" "$ROOT/toolchain/ps4.cmake"
if [[ ! -d "$ROOT/tools" ]]; then cp -a "$ROOT/refs/dusklight/tools" "$ROOT/tools"; fi
python3 "$HERE/inputs.py" verify "$ROOT"
python3 -m venv "$ROOT/mesa-venv"
sha256sum "$ROOT/downloads/python/"* > "$ROOT/evidence/python-wheels.sha256"
"$ROOT/mesa-venv/bin/pip" install --no-index --find-links "$ROOT/downloads/python" meson==1.9.1 Mako==1.3.10 PyYAML==6.0.3 packaging==25.0 MarkupSafe==3.0.3
"$ROOT/mesa-venv/bin/pip" freeze > "$ROOT/evidence/python-tools.txt"
echo 'Mesa/header/host inputs prepared; no target behavior validated.'
