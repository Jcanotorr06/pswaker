#!/usr/bin/env bash
# Adapted from diagnosing-bugs/scripts/hitl-loop.template.sh.
# The human performs the console actions; this script records and classifies them.
set -euo pipefail
MODE=${1:?Use full or startup}
OUTPUT=${2:?Pass a local results directory}
RECORD=${3:-live}
[[ "$MODE" == full || "$MODE" == startup ]] || exit 2
mkdir -p "$OUTPUT"
step() { printf '\n>>> %s\n' "$1"; read -r -p '    [Enter when done] ' _; }
capture() {
  local answer
  printf '\n>>> %s\n' "$2"
  read -r -p '    > ' answer
  printf -v "$1" '%s' "$answer"
}
if [[ "$RECORD" == --record-existing ]]; then
  printf 'Recording a previously observed run. This does not execute or reproduce it.\n'
else
  step 'Fully close the installed app. Confirm the package/build from its local artifacts.json.'
  if [[ "$MODE" == startup ]]; then
    step 'Launch PSWaker Startup Probe. Wait up to 60 seconds. Black/silent for about 30 seconds is expected. Record any crash code and whether the app returns normally.'
  else
    step 'Launch the original PSWaker Platform Diagnostic. Observe for up to 60 seconds or until it crashes. Do not repeat the ten-minute acceptance run yet.'
  fi
fi
capture BUILD 'Build ID associated with the installed package:'
capture BASELINE 'Console / firmware / GoldHEN version (no network details):'
capture OUTCOME 'Outcome: crash, running, normal-exit, or unknown:'
capture ERROR 'PS4 error code, or none:'
capture SECONDS_OBSERVED 'Approximate seconds until that outcome:'
capture SCREEN 'Visible result: black, diagnostic-ui, or describe:'
capture AUDIO 'Audible result: silent, tone, or describe:'
if [[ "$RECORD" != --record-existing ]]; then
  step 'Retrieve probe files through existing FTP access before another launch. See README for paths. Preserve missing-file information too.'
fi
capture FILES 'Retrieved file names, or none (omit private addresses/credentials):'
capture LAST_STAGE 'Last entry.log stage if present, or none:'
export MODE RECORD BUILD BASELINE OUTCOME ERROR SECONDS_OBSERVED SCREEN AUDIO FILES LAST_STAGE
python3 - "$OUTPUT/observation.json" <<'PY'
import json, os, pathlib, sys
keys = ('MODE','RECORD','BUILD','BASELINE','OUTCOME','ERROR','SECONDS_OBSERVED','SCREEN','AUDIO','FILES','LAST_STAGE')
record = {key.lower():os.environ[key] for key in keys}
exact = (record['outcome']=='crash' and record['error'].lower()=='ce-34878-0'
         and record['screen']=='black' and record['audio']=='silent' and record['files']=='none')
record['original_symptom_reported'] = exact
record['execution'] = 'prior owner report only' if record['record']=='--record-existing' else 'owner-operated console run'
record['verdict'] = ('RED_REPORTED' if record['record']=='--record-existing' else 'RED_OBSERVED') if exact else 'REVIEW_REQUIRED'
pathlib.Path(sys.argv[1]).write_text(json.dumps(record,indent=2)+'\n')
print(record['verdict'] + ': ' + sys.argv[1])
print('This records observations; it is not an unattended console test or a proof of a fix.')
sys.exit(20 if exact else 2)
PY
