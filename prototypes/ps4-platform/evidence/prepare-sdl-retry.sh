#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")/.." && pwd)
ROOT=/home/joseph_cano/.cache/pswaker/startup-20261021
bash "$HERE/prepare-graphics.sh" "$ROOT" > "$ROOT/evidence/graphics-prepare.log" 2>&1
python3 "$ROOT/src/dawn/tools/fetch_dawn_dependencies.py" --directory "$ROOT/src/dawn" > "$ROOT/evidence/dawn-deps-fetch.log" 2>&1
echo 'Prepared graphics inputs for the SDL startup retry.'
