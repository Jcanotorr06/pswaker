#!/usr/bin/env bash
# One incremental PS4 candidate, not a renewed two-clean-build claim.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")/../.." && pwd)
ROOT=/home/joseph_cano/.cache/pswaker/startup-20261021
ARCHIVE="$ROOT/aurora-baseline-01.01"
if [[ ! -e "$ARCHIVE" ]]; then
  mkdir -p "$ARCHIVE"
  cp -a "$ROOT/evidence" "$ROOT/out" "$ARCHIVE/"
  cp "$ROOT/build/probe/platform_diagnostic" "$ARCHIVE/"
  cp "$ROOT/build/probe/platform_diagnostic_eboot/eboot.bin" "$ARCHIVE/"
fi
exec > >(tee "$ROOT/evidence/aurora-candidate-build.log") 2>&1
printf 'STAGE incremental-diagnostic %s\n' "$(date --utc --iso-8601=seconds)"
bash "$HERE/build-probe.sh" "$ROOT"
printf 'STAGE package-01.02 %s\n' "$(date --utc --iso-8601=seconds)"
python3 "$HERE/package-probe.py" "$ROOT" --app-version 01.02
python3 "$HERE/evidence/aurora-correction-20261022/inspect-candidate.py" "$ROOT"
printf 'COMPLETE host-build-only %s\n' "$(date --utc --iso-8601=seconds)"
