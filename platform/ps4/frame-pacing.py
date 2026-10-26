#!/usr/bin/env python3
"""Summarize one preserved PS4 launch without combining independent samples."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(newline='') as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
    require(all(None not in row and None not in row.values() for row in rows),
            f'Truncated or malformed CSV: {path}')
    return rows


def percentile(values, fraction):
    return sorted(values)[math.ceil(len(values) * fraction) - 1]


def analyze(run, inspection, owner):
    identity = json.loads((run / 'identity.json').read_text())
    require(identity['schema'] == 1 and identity['method'] == 'VideoOut-completed-flip-tsc',
            'Unsupported timing method/schema; obtain owner agreement before substituting evidence')
    require(identity['build'] == inspection['program']['build_id'] == owner['build'],
            'Installed build, inspection and run identity must match')
    require(owner['package_sha256'] == inspection['package']['sha256'], 'Installed package hash mismatch')
    require(identity['internal'] == [1280, 720] and identity['logic_hz'] == 30
            and identity['textures'] == 'stock', 'Quality contract changed; renew the platform evidence')
    require(owner['platform'] == {'model': 'PS4 Slim', 'firmware': '9.00', 'goldhen': 'v2.4b18'},
            'Owner must confirm the supported platform')
    require(owner['cache_state'] in ('cold', 'warm'), 'Owner must label cache state')
    frequency = int(identity['tsc_frequency'])
    require(frequency > 0, 'Invalid TSC frequency')
    frames = read_csv(run / 'frames.csv')
    events = read_csv(run / 'events.csv')
    samples = read_csv(run / 'samples.csv')
    require(frames, 'No completed console flips')
    # Raw completion continuity is mandatory. Never reconstruct missing timings.
    errors = [e['detail'] for e in events if e['kind'] == 'invalid']
    if owner['timing_method_verified'] is not True:
        errors.append('VideoOut timestamp semantics unverified; obtain agreement before substituting evidence')
    if not any(e['kind'] == 'shutdown' and e['detail'] == 'complete' for e in events):
        errors.append('launch has no completed recorder shutdown')
    previous = None
    for frame in frames:
        for field in set(frame) - {'stage'}:
            frame[field] = int(frame[field])
        if previous:
            if frame['flip_count'] != previous['flip_count'] + 1:
                errors.append('missing or duplicated flip completion')
            if frame['flip_argument'] != previous['flip_argument'] + 1:
                errors.append('missing or duplicated present argument')
            if frame['tsc'] <= previous['tsc'] or frame['observed_ns'] <= previous['observed_ns']:
                errors.append('nonmonotonic presentation/observation time')
        previous = frame
    if frames[0]['flip_count'] != 1:
        errors.append('missing initial flip evidence')
    # Across the launch, completed-flip time must track an independent monotonic
    # observation clock. Poll latency may vary, but cannot change the clock rate.
    elapsed = (frames[-1]['tsc'] - frames[0]['tsc']) / frequency
    observed = (frames[-1]['observed_ns'] - frames[0]['observed_ns']) / 1e9
    if abs(elapsed - observed) > .100 or any(abs(
            (f['tsc'] - frames[0]['tsc']) / frequency -
            (f['observed_ns'] - frames[0]['observed_ns']) / 1e9) > .100 for f in frames):
        errors.append('flip timestamp rate differs from monotonic observation clock')
    armed = {int(e['sample']): e['detail'] for e in events if e['kind'] == 'sample-arm'}
    require(len(armed) == len([e for e in events if e['kind'] == 'sample-arm']), 'Duplicate sample arm')
    finished = {int(row['sample']): row for row in samples}
    require(len(finished) == len(samples), 'Duplicate sample summary')
    results = []
    for number in sorted(set(armed) | set(finished) | {f['sample'] for f in frames if f['sample']}):
        raw = [f for f in frames if f['sample'] == number]
        reasons = list(dict.fromkeys(errors))
        scene = armed.get(number, 'unknown')
        recorded = finished.get(number, {})
        if scene not in ('outset', 'forest') or recorded.get('scene') != scene:
            reasons.append('missing or inconsistent scene identity')
        if recorded.get('outcome') != 'complete':
            reasons.append('sample incomplete: ' + recorded.get('outcome', 'missing end record'))
        ends = [e for e in events if e['kind'] == 'sample-end' and int(e['sample']) == number]
        if len(ends) != 1 or ends[0]['detail'] != 'complete':
            reasons.append('missing complete sample end marker')
        outside_boundary = []
        if len(ends) == 1:
            boundary = int(ends[0]['monotonic_ns'])
            # A frame already queued when the owner pauses can complete later.
            # Retain it in raw-launch, but honor the explicit sample end marker.
            outside_boundary = [f for f in raw if f['observed_ns'] > boundary]
            raw = [f for f in raw if f['observed_ns'] <= boundary]
        if len(raw) < 2:
            reasons.append('insufficient game presentations')
        seconds = (raw[-1]['tsc'] - raw[0]['tsc']) / frequency if len(raw) >= 2 else 0
        intervals = [(b['tsc'] - a['tsc']) * 1000 / frequency for a, b in zip(raw, raw[1:])]
        if seconds < 120:
            reasons.append('less than two minutes of presentation evidence')
        if any(not f['game_frame'] for f in raw) or any(
                b['game_frame'] != a['game_frame'] + 1 or b['flip_count'] != a['flip_count'] + 1
                for a, b in zip(raw, raw[1:])):
            reasons.append('UI/repeated/missing game frame in active sample')
        if len({(f['stage'], f['room']) for f in raw}) != 1 or any(f['stage'] == 'unknown' for f in raw):
            reasons.append('unknown or changing stage/room')
        expected_location = {'outset': ('sea', 44), 'forest': ('A_mori', 0)}.get(scene)
        if not expected_location or any((f['stage'], f['room']) != expected_location for f in raw):
            reasons.append('scene label does not match game stage/room')
        if recorded and (int(recorded['intervals']) != len(intervals) or
                         abs(float(recorded['seconds']) - seconds) > .00001):
            reasons.append('raw evidence disagrees with on-console sample summary')
        action = owner['samples'].get(str(number), {})
        resumed = [int(e['monotonic_ns']) for e in events if e['kind'] == 'sample-resume' and int(e['sample']) == number]
        if len(resumed) != 1 or (raw and resumed[0] > raw[0]['observed_ns']):
            reasons.append('missing or invalid resume boundary')
        if action.get('scene') != scene or not action.get('actions') or action.get('active_gameplay') is not True:
            reasons.append('owner action/boundary confirmation missing')
        if action.get('graphics_audio_correct') is not True:
            reasons.append('representative graphics/audio correctness not confirmed')
        metrics = None
        shortfalls = []
        if intervals and all(value > 0 for value in intervals):
            waits = [int(e['detail']) for e in events if e['kind'] == 'shader-wait-ns' and int(e['sample']) == number]
            metrics = {'seconds': seconds, 'intervals': len(intervals), 'average_fps': len(intervals) / seconds,
                       'p95_ms': percentile(intervals, .95), 'p99_ms': percentile(intervals, .99),
                       'maximum_ms': max(intervals),
                       'shader_wait_ms': (raw[-1]['shader_ns'] - raw[0]['shader_ns']) / 1e6,
                       'shader_wait_calls': raw[-1]['shader_calls'] - raw[0]['shader_calls'],
                       'active_shader_waits_over_35ms': sum(wait > 35000000 for wait in waits),
                       'active_shader_wait_total_ms': sum(waits) / 1e6,
                       'resume_to_first_observation_ms': (raw[0]['observed_ns'] - resumed[0]) / 1e6 if resumed else None,
                       'shader_correlated_hitches': sum(interval > 35 and b['shader_ns'] - a['shader_ns'] >= 1e6
                                                       for interval, a, b in zip(intervals, raw, raw[1:]))}
            for metric, limit, minimum in [('average_fps', 29.5, True), ('p95_ms', 35, False),
                                          ('p99_ms', 50, False), ('maximum_ms', 100, False)]:
                value = metrics[metric]
                if (value < limit if minimum else value > limit):
                    shortfalls.append({'metric': metric, 'measured': value, 'limit': limit})
        results.append({'sample': number, 'scene': scene, 'owner': action, 'metrics': metrics,
                        'outside_boundary_presentations': len(outside_boundary),
                        'invalid_reasons': reasons, 'shortfalls': shortfalls,
                        'target_met': bool(metrics and not reasons and not shortfalls), 'raw': raw})
    phases = []
    marks = [e for e in events if e['kind'] == 'phase']
    for begin, end in zip(marks, marks[1:]):
        phases.append({'phase': begin['detail'], 'start_ns': int(begin['monotonic_ns']),
                       'duration_ms': (int(end['monotonic_ns']) - int(begin['monotonic_ns'])) / 1e6})
    return {'schema': 1, 'identity': identity, 'installed_program': inspection['program'],
            'package': inspection['package'], 'owner': owner, 'samples': results, 'phases': phases,
            'missing_scenes': [scene for scene in ('outset', 'forest') if not any(r['scene'] == scene for r in results)],
            'acceptance': 'Individual measured candidates only; final integrated acceptance belongs to issue #23'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--inspection', type=Path, required=True)
    parser.add_argument('--owner', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        require(not args.output.exists(), 'Output exists; retain previous results and choose a new directory')
        inspection = json.loads(args.inspection.read_text())
        owner = json.loads(args.owner.read_text())
        report = analyze(args.run, inspection, owner)
        args.output.mkdir(parents=True)
        raw_dir = args.output / 'raw-launch'
        shutil.copytree(args.run, raw_dir)
        shutil.copyfile(args.inspection, args.output / 'inspection.json')
        shutil.copyfile(args.owner, args.output / 'owner.json')
        report['evidence_sha256'] = {p.relative_to(args.output).as_posix(): digest(p)
                                     for p in sorted(args.output.rglob('*')) if p.is_file()}
        for sample in report['samples']:
            raw = sample.pop('raw')
            (args.output / f"sample-{sample['sample']:03d}-{sample['scene']}-raw.json").write_text(json.dumps(raw, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
        return 0 if report['samples'] and not report['missing_scenes'] and all(s['target_met'] for s in report['samples']) else 2
    except (OSError, ValueError, KeyError, TypeError, csv.Error) as error:
        print(f'frame-pacing: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
