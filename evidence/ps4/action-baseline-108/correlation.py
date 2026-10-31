#!/usr/bin/env python3
"""Correlate #108 frame intervals and shader waits with the planned route windows."""
import csv
import json
import sys
from pathlib import Path

WINDOWS = [(0, 10, 'still'), (10, 40, 'rolls'), (40, 70, 'sword'), (70, 110, 'swim'), (110, 121, 'still')]


def launch(run):
    identity = json.loads((run / 'identity.json').read_text())
    freq = int(identity['tsc_frequency'])
    events = list(csv.DictReader((run / 'events.csv').open(newline='')))
    frames = [{k: (v if k == 'stage' else int(v)) for k, v in row.items()}
              for row in csv.DictReader((run / 'frames.csv').open(newline=''))]
    at = lambda kind, detail=None, sample=None: [int(e['monotonic_ns']) for e in events if e['kind'] == kind
                                                 and (detail is None or e['detail'] == detail)
                                                 and (sample is None or e['sample'] == sample)]
    loading = at('phase', 'loading')[0]
    ready = at('phase', 'gameplay', '0')[0]
    arm = at('sample-arm')[0]
    first = at('sample-first-presentation')[0]
    end = at('sample-end')[0]

    def window(ns):
        if ns < loading:
            return 'startup'
        if ns < ready:
            return 'loading-to-gameplay-ready'
        if ns < arm:
            return 'walk-to-start'
        if ns < first:
            return 'arm-to-first-presentation'
        if ns > end:
            return 'after-sample'
        seconds = (ns - first) / 1e9
        return next(f'sample {a}-{b} s {name}' for a, b, name in WINDOWS if a <= seconds < b)

    order = ['startup', 'loading-to-gameplay-ready', 'walk-to-start', 'arm-to-first-presentation',
             *[f'sample {a}-{b} s {name}' for a, b, name in WINDOWS], 'after-sample']
    table = {name: {'shader_waits': 0, 'shader_waits_over_35ms': 0, 'shader_wait_ms': 0.0, 'max_shader_wait_ms': 0.0,
                    'intervals_over_35ms': 0, 'shader_correlated': 0, 'max_interval_ms': 0.0,
                    'uncorrelated': 0, 'max_uncorrelated_ms': 0.0} for name in order}
    for e in events:
        if e['kind'] == 'shader-wait-ns':
            row, wait = table[window(int(e['monotonic_ns']))], int(e['detail']) / 1e6
            row['shader_waits'] += 1
            row['shader_waits_over_35ms'] += wait > 35
            row['shader_wait_ms'] += wait
            row['max_shader_wait_ms'] = max(row['max_shader_wait_ms'], wait)
    in_sample = []
    for a, b in zip(frames, frames[1:]):
        interval = (b['tsc'] - a['tsc']) * 1000 / freq
        shader = (b['shader_ns'] - a['shader_ns']) / 1e6
        if interval <= 35:
            continue
        name = window(b['observed_ns'])
        row = table[name]
        row['intervals_over_35ms'] += 1
        row['max_interval_ms'] = max(row['max_interval_ms'], interval)
        if shader >= 1:
            row['shader_correlated'] += 1
        else:
            row['uncorrelated'] += 1
            row['max_uncorrelated_ms'] = max(row['max_uncorrelated_ms'], interval)
        if name.startswith('sample'):
            in_sample.append({'seconds_after_first_presentation': round((b['observed_ns'] - first) / 1e9, 3),
                              'window': name, 'interval_ms': round(interval, 3), 'shader_ms': round(shader, 3),
                              'shader_calls': b['shader_calls'] - a['shader_calls'],
                              'stage_room': f"{b['stage']}/{b['room']}"})
    for row in table.values():
        for key, value in row.items():
            if isinstance(value, float):
                row[key] = round(value, 3)
    return {'windows': table,
            'launch_shader_waits': sum(e['kind'] == 'shader-wait-ns' for e in events),
            'walk_to_start_seconds': round((arm - ready) / 1e9, 3),
            'sample_intervals_over_35ms': in_sample}


def main():
    cold, warm = Path(sys.argv[1]), Path(sys.argv[2])
    report = {'schema': 1,
              'method': 'Route windows are the planned timeline measured from sample-first-presentation; '
                        'no per-action owner timings or video were returned. Intervals are placed by the '
                        'observation of their closing presentation. A shader-correlated interval exceeds '
                        '35 ms and contains >=1 ms of recorded shader wait. '
                        'Usage: correlation.py cold/raw-launch warm/raw-launch',
              'cold': launch(cold), 'warm': launch(warm)}
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
