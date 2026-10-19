#!/usr/bin/env bash
# Refresh only the diagnostic component after its final source corrections.
# All external target dependencies in this root were compiled from the empty-root build.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")/.." && pwd)
ROOT=$(realpath "${1:?Pass the completed fresh build root}")
mkdir -p "$ROOT/evidence/before-final-probe"
for name in probe-build.log probe-configure.log; do
  cp "$ROOT/evidence/$name" "$ROOT/evidence/before-final-probe/$name"
done
exec > >(tee "$ROOT/evidence/finalize-build.log") 2>&1
echo "STAGE clean-final-probe $(date --utc --iso-8601=seconds)"
cmake --build "$ROOT/build/probe" --target clean > "$ROOT/evidence/probe-final-clean.log" 2>&1
export JOBS=${JOBS:-5}
bash "$HERE/build-probe.sh" "$ROOT"
python3 "$HERE/package-probe.py" "$ROOT"
echo "COMPLETE final-host-build-only $(date --utc --iso-8601=seconds)"
