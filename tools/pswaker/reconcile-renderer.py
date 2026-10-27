#!/usr/bin/env python3
"""Reconcile the reviewed Wind Waker series after the selected Aurora PS4 patch."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import build_inputs

PLATFORM = build_inputs.Locations().platform


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconcile(root):
    lock = json.loads((PLATFORM / 'renderer.lock.json').read_text())
    tree = root / 'src/aurora'
    # Check the whole input boundary before mutating any source file.
    for relative, expected in lock['initial_files'].items():
        path = tree / relative
        if not path.is_file() or digest(path) != expected:
            raise ValueError('Renderer source context mismatch: ' + relative)
    for relative in lock['created_files']:
        if (tree / relative).exists():
            raise ValueError('Renderer source already exists: ' + relative)
    for item in lock['patches'] + lock['platform_reference_patches']:
        for path_key, sha_key in [('original', 'original_sha256'), ('patch', 'sha256')]:
            if path_key in item and digest(PLATFORM / item[path_key]) != item[sha_key]:
                raise ValueError('Renderer patch SHA-256 mismatch: ' + item[path_key])
    applied = []
    for item in lock['patches']:
        if 'patch' not in item:
            continue
        patch = PLATFORM / item['patch']
        subprocess.run(['git', 'apply', '--check', str(patch)], cwd=tree, check=True)
        subprocess.run(['git', 'apply', str(patch)], cwd=tree, check=True)
        applied.append(item['name'])
    actual = {name: digest(tree / name) for name in lock['final_files']}
    if actual != lock['final_files']:
        raise ValueError('Reconciled renderer differs from reviewed source')
    report = dict(lock, applied=applied, prepared_files=actual, hardware_status='untested')
    (root / 'evidence/renderer-reconciliation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'Reconciled {len(applied)} renderer patches; all {len(lock["patches"])} dispositions recorded')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    try:
        reconcile(parser.parse_args().root.resolve())
    except (ValueError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
