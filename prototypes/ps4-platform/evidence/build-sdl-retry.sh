#!/usr/bin/env bash
# Run after prepare-sdl-retry.sh and build-graphics.sh complete.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")/.." && pwd)
ROOT=/home/joseph_cano/.cache/pswaker/startup-20261021
exec > >(tee "$ROOT/evidence/sdl-retry-build.log") 2>&1
echo "STAGE diagnostic $(date --utc --iso-8601=seconds)"
bash "$HERE/build-probe.sh" "$ROOT"
echo "STAGE package $(date --utc --iso-8601=seconds)"
python3 "$HERE/package-probe.py" "$ROOT" --app-version 01.01
echo "COMPLETE host-build-only $(date --utc --iso-8601=seconds)"
