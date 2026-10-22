#!/usr/bin/env bash
# Exit status tests actual Aurora known-white output and the 1280x720 request.
set -euo pipefail
OUT=${1:?Pass the separate Linux host build directory}
shift
mkdir -p "$OUT/runs"
PSWAKER_REPRO_DATA=$(mktemp -d "$OUT/runs/run-XXXXXX")
export PSWAKER_REPRO_DATA
mkdir "$PSWAKER_REPRO_DATA/cache"
printf 'Fresh host evidence/cache directory: %s\n' "$PSWAKER_REPRO_DATA"
export SDL_VIDEODRIVER=x11
export VK_DRIVER_FILES=/usr/share/vulkan/icd.d/lvp_icd.json
exec timeout 30s xvfb-run -a -s '-screen 0 1920x1080x24' "$OUT/repro/aurora-repro" "$@"
