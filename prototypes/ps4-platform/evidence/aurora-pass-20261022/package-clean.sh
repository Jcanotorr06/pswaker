#!/usr/bin/env bash
# clean-build.sh uses the historical default SFO version; finalize as 01.02.
# No source, compiled object or dependency is changed by this metadata step.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")/../.." && pwd)
ROOT=$(realpath "${1:?Pass a completed renewed clean build root}")
exec > >(tee "$ROOT/evidence/version-01.02-package.log") 2>&1
printf 'STAGE package-clean-01.02 %s\n' "$(date --utc --iso-8601=seconds)"
python3 "$HERE/package-probe.py" "$ROOT" --app-version 01.02
printf 'COMPLETE clean-01.02 %s\n' "$(date --utc --iso-8601=seconds)"
