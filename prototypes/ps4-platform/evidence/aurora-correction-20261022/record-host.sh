#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
HOST=/home/joseph_cano/.cache/pswaker/aurora-host-20261022
ROOT=/home/joseph_cano/.cache/pswaker/startup-20261021
bash "$HERE/../../aurora-repro/check.sh" "$HOST" > "$HOST/differential-check.log" 2>&1
python3 "$HERE/collect-evidence.py" "$ROOT" "$HOST"
