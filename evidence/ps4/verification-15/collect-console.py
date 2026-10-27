#!/usr/bin/env python3
"""Recheck the already reviewed 01.04 owner records and export selected raw blocks.

This validates supplied records, not visible rendering, audible output or a new run.
Owner package confirmation and observations remain in the linked original review.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
REVIEW = HERE.parent / 'renderer-14/console-01.04'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def collect(originals, candidate, output):
    summary = json.loads((REVIEW / 'summary.json').read_text())
    inventory = json.loads((REVIEW / 'original-files.json').read_text())
    found = {p.relative_to(originals).as_posix() for p in originals.rglob('*') if p.is_file()}
    require(found == {item['path'] for item in inventory}, 'Original evidence file set changed')
    for item in inventory:
        data = (originals / item['path']).read_bytes()
        require(len(data) == item['bytes'] and digest(data) == item['sha256'],
                'Original evidence changed: ' + item['path'])
    manifest_data = (candidate / 'evidence/build-info.json').read_text()
    # The diagnostic logs fgets(..., 1024) chunks, including an additional newline
    # after each chunk. A long JSON string can span multiple MANIFEST records.
    expected_manifest_log = ''.join('MANIFEST ' + line[offset:offset + 1023] + '\n'
        for line in manifest_data.splitlines(keepends=True) for offset in range(0, len(line), 1023))
    artifacts = json.loads((candidate / 'evidence/artifacts.json').read_text())
    require(artifacts['package']['sha256'] == summary['installed_pkg_sha256_owner_confirmed'],
            'Candidate differs from owner-confirmed installed package')
    require(digest((candidate / 'out' / artifacts['package']['filename']).read_bytes()) ==
            summary['installed_pkg_sha256_owner_confirmed'], 'Installed candidate package hash changed')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'owner-report-original.md').write_bytes((originals / 'report.md').read_bytes())
    result = {'scope': 'Recheck of original returned evidence; no new console runs or owner claims',
              'original_files_verified': len(inventory),
              'original_inventory_sha256': digest((REVIEW / 'original-files.json').read_bytes()),
              'installed_pkg_sha256': summary['installed_pkg_sha256_owner_confirmed'],
              'build_id': summary['build_id'], 'runs': []}
    previous = originals / 'before-01.04'
    for run in summary['runs']:
        folder = originals / run['folder']
        selected = output / run['folder']
        selected.mkdir(exist_ok=True)
        exports = []
        blocks = {}
        for name, marker in [('diagnostic.log', b'BEGIN build='),
                             ('runtime-preflight.log', b'BEGIN runtime build preflight;')]:
            data = (folder / name).read_bytes()
            require(data.startswith((previous / name).read_bytes()), 'Append history changed: ' + name)
            start = data.rfind(marker)
            require(start >= 0, 'Missing BEGIN block: ' + name)
            block = data[start:]
            (selected / name).write_bytes(block)
            exports.append({'file': name, 'original_byte_range': [start, len(data)],
                            'sha256': digest(block), 'bytes': len(block)})
            blocks[name] = block.decode()
        log = blocks['diagnostic.log']
        observed_manifest_log = log.split('\n', 1)[1].split('PASS manifest-close\n', 1)[0]
        require(observed_manifest_log == expected_manifest_log,
                'Console embedded manifest differs from installed candidate')
        require(log.startswith('BEGIN build=' + summary['build_id'] + ';'), 'Run build ID differs')
        require(('RUN launch=' + str(run['launch']) + ' cache-entries-before-Aurora=' +
                 str(run['cache_entries_at_start']) + ';') in log, 'Run/cache association differs')
        require(not re.search(r'^FAIL ', log, re.M), 'Failed diagnostic check')
        require(re.search(r'END frames=\d+ checks=120 failures=0;', log), 'Missing successful END')
        for check in ['ten-minute-loop', 'controller-disconnect-reconnect-resume',
                      'synthetic-audio-API-errors', 'GPU-queue-drained', 'runtime-preflight',
                      'Wind-Waker-renderer-checks']:
            require('PASS ' + check + '\n' in log, 'Missing diagnostic result: ' + check)
        require('STAGE Aurora-shutdown-complete\n' in log, 'Missing ordered shutdown completion')
        pixels = Counter(re.findall(r'^PIXEL (\S+).* mismatches=0/1024$', log, re.M))
        require(dict(pixels) == run['pixel_sample_counts'], 'Known-result sample counts differ')
        require(Counter(re.findall(r'^TARGET .*$', log, re.M)) == run['efb_target_counts'],
                'Allocated target dimensions/counts differ')
        resources = [{key: float(value) if key == 'seconds' else int(value)
                      for key, value in re.findall(r'([\w-]+)=([\d.]+)', line)}
                     for line in log.splitlines() if line.startswith('RESOURCE ')]
        require(resources == run['resources'], 'Resource samples differ from reviewed evidence')
        runtime = blocks['runtime-preflight.log']
        require(runtime.splitlines() == run['runtime'], 'Runtime results differ')
        require(not re.search(r'^FAIL ', runtime, re.M), 'Failed runtime check')
        state = (folder / 'preflight-state.txt').read_bytes()
        require(int(state.strip()) == run['launch'], 'Persistence counter differs')
        (selected / 'preflight-state.txt').write_bytes(state)
        platform = (folder / 'platform.log').read_bytes()
        require(b'exit status 0: asking the shell to close the title' in platform,
                'Missing platform exit status')
        tail = b''.join(platform.splitlines(keepends=True)[-20:])
        (selected / 'platform-tail.log').write_bytes(tail)
        exports.extend([{'file': 'preflight-state.txt', 'sha256': digest(state), 'bytes': len(state)},
                        {'file': 'platform-tail.log', 'sha256': digest(tail), 'bytes': len(tail),
                         'original_byte_range': [len(platform) - len(tail), len(platform)]}])
        result['runs'].append({'folder': run['folder'], 'launch': run['launch'],
                               'embedded_manifest_matches_candidate': True,
                               'append_history_preserved': True, 'exports': exports})
        previous = folder
    result['limits'] = ('Original failures/history, backups and cache databases remain in the '
                        '47-file private inventory. Shared blocks select only the reviewed final '
                        'launch from each append log. Resource trends and visible/audible/controller '
                        'observations require the original human review; parsing does not supply them.')
    (output / 'console-recheck.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Verified original hashes, candidate manifest and all three selected run records.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('originals', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    collect(args.originals.resolve(), args.candidate.resolve(), args.output.resolve())
