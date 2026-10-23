#!/usr/bin/env bash
# One command, fresh build tree. Cache contains verified downloads, never target build archives.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(realpath -m "${1:?Pass a NEW absolute Linux build-root path}")
[[ "$ROOT" != *' '* ]] || { echo 'Build root must not contain spaces' >&2; exit 1; }
python3 "$HERE/inputs.py" host "$ROOT"
[[ ! -e "$ROOT" ]] || { echo "Clean build requires a new directory: $ROOT" >&2; exit 1; }
mkdir -p "$(dirname "$ROOT")"
mkdir "$ROOT"
mkdir "$ROOT/evidence"
exec > >(tee "$ROOT/evidence/clean-build.log") 2>&1
export JOBS=${JOBS:-5}
export CLANG_VER=21
unset PGO PGO_PROFILE FLAVOR MESA_BUILD MESA_EXTRA_FLAGS MESA_EXTRA_LINK
unset CC CXX AR RANLIB CFLAGS CXXFLAGS CPPFLAGS LDFLAGS
echo "STAGE fresh-download-cache $(date --utc --iso-8601=seconds)"
if [[ -n "${2:-}" ]]; then
  CACHE=$(realpath "$2")
  cp -a "$CACHE/downloads" "$ROOT/downloads"
fi
python3 "$HERE/inputs.py" fetch "$ROOT"
python3 "$HERE/lock-sdk.py" fetch "$ROOT"
echo "STAGE pinned-sources $(date --utc --iso-8601=seconds)"
python3 "$HERE/prepare-sources.py" "$ROOT"
python3 "$HERE/adapt-platform.py" "$ROOT"
python3 "$HERE/prepare-sdk-sources.py" "$ROOT"
echo "STAGE sdk-target-support $(date --utc --iso-8601=seconds)"
bash "$HERE/build-sdk-support.sh" "$ROOT" > "$ROOT/evidence/sdk-support-build.log" 2>&1
echo "STAGE runtime $(date --utc --iso-8601=seconds)"
bash "$HERE/build-runtime.sh" "$ROOT" > "$ROOT/evidence/runtime-driver.log" 2>&1
echo "STAGE graphics-inputs $(date --utc --iso-8601=seconds)"
python3 "$HERE/inputs.py" dependencies "$ROOT" > "$ROOT/evidence/dependencies-prepare.log" 2>&1
python3 "$HERE/apply-patches.py" "$ROOT" graphics
git -C "$ROOT/src/libdrm" rev-parse HEAD > "$ROOT/evidence/libdrm-revision.txt"
bash "$HERE/prepare-graphics.sh" "$ROOT" > "$ROOT/evidence/graphics-prepare.log" 2>&1
echo "STAGE graphics-libraries $(date --utc --iso-8601=seconds)"
bash "$HERE/build-graphics.sh" "$ROOT"
echo "STAGE diagnostic $(date --utc --iso-8601=seconds)"
python3 "$HERE/apply-patches.py" "$ROOT" aurora
python3 "$HERE/reconcile-renderer.py" "$ROOT"
bash "$HERE/build-probe.sh" "$ROOT"
echo "STAGE package $(date --utc --iso-8601=seconds)"
python3 "$HERE/apply-patches.py" "$ROOT" packager
python3 "$HERE/package-probe.py" "$ROOT"
python3 "$HERE/inspect-artifacts.py" "$ROOT"
python3 "$HERE/audit-inputs.py" "$ROOT"
echo "COMPLETE host-build-only $(date --utc --iso-8601=seconds)"
