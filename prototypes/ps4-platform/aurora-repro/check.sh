#!/usr/bin/env bash
# Differential regression through real Aurora/Dawn/Vulkan, not an evidence parser.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
OUT=${1:?Pass the separate Linux host build directory}
python3 "$HERE/check-source.py"
for variant in baseline repeat drain scale initialize-repeat alpha corrected; do
  expected=1
  [[ "$variant" == corrected ]] && expected=0
  set +e
  bash "$HERE/capture.sh" "$OUT" "$variant"
  status=$?
  set -e
  [[ "$status" == "$expected" ]] || { echo "Unexpected result for $variant: $status"; exit 1; }
done
python3 - "$OUT" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
for name in ('baseline', 'repeat', 'drain'):
    value = (root / f'{name}.log').read_text()
    assert 'RESULT sizing=0 graphics=0' in value
    assert 'expected=255,255,255,255 mismatches=1024/1024' in value
assert 'RESULT sizing=1 graphics=0' in (root / 'scale.log').read_text()
assert 'first=255,255,255,0 expected=255,255,255,255' in (root / 'initialize-repeat.log').read_text()
assert 'RESULT sizing=0 graphics=1' in (root / 'alpha.log').read_text()
value = (root / 'corrected.log').read_text()
assert 'RESULT sizing=1 graphics=1' in value
assert value.count('mismatches=0/1024') == 60
assert value.count('PASS allocated-EFB-render-size') == 30
assert 'FAIL ' not in value and 'Buffer mapping Aborted' not in value
assert 'PASS GPU-queue-drained' in value
print('PASS differential: failed baseline retained; corrected shared path passes every comparison')
PY
