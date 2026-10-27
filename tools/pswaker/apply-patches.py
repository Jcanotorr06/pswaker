#!/usr/bin/env python3
"""Apply one phase of the ordered component patch series with exact contexts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import build_inputs

PLATFORM = build_inputs.Locations().platform
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('root', type=Path)
parser.add_argument('phase', choices=['runtime', 'graphics', 'aurora', 'packager'])
args = parser.parse_args()
root = args.root.resolve()
records = []
for item in json.loads((PLATFORM / 'patch-series.json').read_text()):
    if item['phase'] != args.phase:
        continue
    patch = root / 'refs/dusklight/patches' / item['patch']
    if hashlib.sha256(patch.read_bytes()).hexdigest() != item['sha256']:
        raise ValueError('Patch SHA-256 mismatch: ' + item['patch'])
    cwd = root / item['target'] / item['context']
    subprocess.run(['git', 'apply', '--check', str(patch)], cwd=cwd, check=True)
    subprocess.run(['git', 'apply', str(patch)], cwd=cwd, check=True)
    records.append(item)
(root / 'evidence' / ('patches-' + args.phase + '.json')).write_text(json.dumps(records, indent=2) + '\n')
