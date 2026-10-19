#!/usr/bin/env bash
# One command, fresh build tree. Cache contains verified downloads, never target build archives.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(realpath -m "${1:?Pass a NEW absolute Linux build-root path}")
CACHE=$(realpath "${2:?Pass the previous download cache root}")
[[ ! -e "$ROOT" ]] || { echo "Clean build requires a new directory: $ROOT" >&2; exit 1; }
mkdir "$ROOT"
mkdir "$ROOT/evidence"
exec > >(tee "$ROOT/evidence/clean-build.log") 2>&1
export JOBS=${JOBS:-5}
echo "STAGE fresh-download-cache $(date --utc --iso-8601=seconds)"
cp -a "$CACHE/downloads" "$ROOT/downloads"
python3 "$HERE/lock-sdk.py" fetch "$ROOT"
echo "STAGE pinned-sources $(date --utc --iso-8601=seconds)"
python3 "$HERE/prepare-sources.py" "$ROOT"
python3 "$HERE/adapt-platform.py" "$ROOT"
echo "STAGE runtime $(date --utc --iso-8601=seconds)"
bash "$HERE/build-runtime.sh" "$ROOT" > "$ROOT/evidence/runtime-driver.log" 2>&1
echo "STAGE graphics-inputs $(date --utc --iso-8601=seconds)"
bash "$HERE/prepare-graphics.sh" "$ROOT" > "$ROOT/evidence/graphics-prepare.log" 2>&1
python3 "$ROOT/src/dawn/tools/fetch_dawn_dependencies.py" --directory "$ROOT/src/dawn" > "$ROOT/evidence/dawn-deps-fetch.log" 2>&1
echo "STAGE graphics-libraries $(date --utc --iso-8601=seconds)"
bash "$HERE/build-graphics.sh" "$ROOT"
echo "STAGE diagnostic $(date --utc --iso-8601=seconds)"
bash "$HERE/build-probe.sh" "$ROOT"
echo "STAGE package $(date --utc --iso-8601=seconds)"
python3 "$HERE/package-probe.py" "$ROOT"
echo "COMPLETE host-build-only $(date --utc --iso-8601=seconds)"
