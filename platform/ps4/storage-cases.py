#!/usr/bin/env python3
"""Prepare private recovery cases from an explicitly supplied disposable save.

Never connect to the console or modify the seed. The owner installs each case
only after isolating and independently backing up genuine progress/settings.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
GCI = Path('saves/USA/Card A/01-GZLE-gczelda.gci')


def valid_save(data):
    if (len(data) != 0x18040 or data[:6] != b'GZLE01' or
            data[8:16] != b'gczelda\0' or data[0x38:0x3a] != b'\0\x0c' or
            data[7] & 7 != 1 or data[0x2c:0x30] != bytes(4) or
            data[0x30:0x34] != b'\0\x01\0\x03' or data[0x3c:0x40] != b'\0\0\x1c\0'):
        return False
    for offset in (0x2040, 0x4040):
        block = data[offset:offset+0x2000]
        words = [int.from_bytes(block[i:i+2], 'big') for i in range(0, 0x1ffc, 2)]
        checksum = ((sum(words) & 0xffff) << 16) | (sum(w ^ 0xffff for w in words) & 0xffff)
        if int.from_bytes(block[-4:], 'big') != checksum or block[4:8] != bytes(4):
            return False
        for slot in range(3):
            start = 8+slot*0x770
            payload = block[start:start+0x768]
            expected = (sum(payload) << 32) | ((-sum(payload)-len(payload)) & 0xffffffff)
            if int.from_bytes(block[start+0x768:start+0x770], 'big') != expected:
                return False
    return data[0x2040:0x4040] == data[0x4040:0x6040]


def prepare(seed, output, inspection):
    data = seed.read_bytes()
    if not valid_save(data):
        raise ValueError('Seed must be a completed, valid USA GCI from disposable in-game progress')
    output = output.resolve()
    if output.is_relative_to(HERE.parents[1]):
        raise ValueError('Private case output must be outside the Git repository')
    identity = json.loads(inspection.read_text())
    if (identity.get('sfo', {}).get('TITLE_ID') != 'PSWK00001' or
            not identity.get('program', {}).get('build_id') or
            not identity.get('package', {}).get('sha256')):
        raise ValueError('Supply a fresh game complete-package inspection with its package hash and build ID')
    # Retain the full inspected package identity without guessing schema fields.
    damaged = bytearray(data)
    damaged[0x2048] ^= 1
    cases = {
        'baseline': {},
        'corrupt-with-backup': {str(GCI): bytes(damaged)},
        'corrupt-no-backup': {str(GCI): bytes(damaged), str(GCI)+'.backup': None},
        'write-failure': {str(GCI)+'.test': b'fail-write\n'},
        'pending-quit': {str(GCI)+'.test': b'hold-publish\n'},
        'startup-unavailable': {'saves/USA/Card B': b'Controlled unavailable-storage case\n'},
    }
    output.mkdir(mode=0o700)  # Refuse existing outputs rather than replacing evidence.
    inventory = {}
    for name, overrides in cases.items():
        files = {str(GCI): data, str(GCI)+'.backup': data,
                 'settings.ini': b'PSWAKER_LARGE_TEXT=0\n'} | overrides
        root = output / name
        (root / 'saves/USA/Card A').mkdir(parents=True)
        if name != 'startup-unavailable':
            (root / 'saves/USA/Card B').mkdir()
        records = {}
        for relative, contents in files.items():
            if contents is None:
                continue
            path = root / relative
            path.write_bytes(contents)
            records[relative] = {'bytes': len(contents), 'sha256': hashlib.sha256(contents).hexdigest()}
        inventory[name] = records
    manifest = {'seed_sha256': hashlib.sha256(data).hexdigest(),
                'inspection_sha256': hashlib.sha256(inspection.read_bytes()).hexdigest(),
                'package_inspection': identity, 'cases': inventory,
                'status': 'Prepared only; installed-console outcomes require owner evidence'}
    (output / 'cases.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=Path, required=True, help='Disposable completed GCI, never genuine progress')
    parser.add_argument('--inspection', type=Path, required=True, help='Fresh complete-package inspection.json')
    parser.add_argument('--output', type=Path, required=True, help='Absent private directory outside this repository')
    args = parser.parse_args()
    try:
        prepare(args.seed, args.output, args.inspection)
        print('Prepared private cases; seed unchanged. Follow Storage-recovery-checklist.md before console use.')
    except (OSError, ValueError) as error:
        print(f'Case preparation failed: {error}', file=sys.stderr)
        sys.exit(1)
