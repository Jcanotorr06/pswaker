#!/usr/bin/env python3
"""Check that a retained seed covers validated recorded snapshots, without changing any seed."""
import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools/pswaker'))
from disc_image import require
from package_artifact import PIPELINE_SEED
from pipeline_assets import checked_pipeline_asset


def descriptions(directory):
    with closing(sqlite3.connect((directory / PIPELINE_SEED).resolve().as_uri()
                                + '?mode=ro&immutable=1', uri=True)) as db:
        return {(kind, key): config for kind, key, config in
                db.execute('SELECT type, hash, config FROM pipeline_cache')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path, help='Verified standalone default assembly assets')
    parser.add_argument('snapshots', type=Path, nargs='+', help='Validated standalone capture assets')
    parser.add_argument('--output', type=Path, required=True, help='New path for a data-free coverage report')
    args = parser.parse_args()
    try:
        require(not args.output.exists(), 'Output already exists; retain it and choose a new report path')
        candidate = checked_pipeline_asset(args.candidate)
        expected = descriptions(args.candidate)
        recorded, snapshots = {}, []
        for index, directory in enumerate(args.snapshots, 1):
            snapshot = checked_pipeline_asset(directory)
            rows = descriptions(directory)
            require(all(key in expected for key in rows),
                    f'Snapshot {index} contains configurations missing from the candidate; extend coverage first')
            require(all(expected[key] == config for key, config in rows.items()),
                    f'Snapshot {index} has conflicting description bytes for a candidate type/hash')
            recorded.update(rows)
            snapshots.append({**snapshot, 'identical_rows_in_candidate': len(rows)})
        report = {'schema': 1, 'method': 'Validated read-only comparison of type/hash keys and config bytes; '
                  'first_frame_used is capture metadata, not configuration identity',
                  'candidate': candidate, 'snapshots': snapshots, 'recorded_union_rows': len(recorded),
                  'already_represented_rows': len(recorded), 'added_rows': 0,
                  'candidate_rows_not_recorded': len(expected.keys() - recorded.keys()),
                  'conclusion': 'Retain the existing candidate seed unchanged; all recorded descriptions are present. '
                  'This establishes recorded configuration coverage, not gameplay smoothness.'}
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(report, indent=2) + '\n')
        return 0
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f'coverage: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
