#!/usr/bin/env python3
"""Repeat the final game build twice; keep complete packages and records private.

Uses the unchanged, verified maintained-15-a platform. This does not rebuild
that platform or create console evidence. Run on the recovered locked WSL host.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile


REPO = Path(__file__).resolve().parents[4]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def run(command, log, **kwargs):
    with log.open('w') as stream:
        subprocess.run([str(arg) for arg in command], check=True,
                       stdout=stream, stderr=subprocess.STDOUT, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--cache-root', required=True, type=Path)
    parser.add_argument('--platform', required=True, type=Path)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--candidate-build', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or output.is_relative_to(REPO):
        raise ValueError('Choose a new private output directory outside the repository')
    output.mkdir(mode=0o700)
    assembly = json.loads((args.candidate / 'assembly.json').read_text())
    source_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
    source_archive = output / 'source.tar'
    subprocess.run(['git', 'archive', '--format=tar', '--output', str(source_archive), source_commit],
                   cwd=REPO, check=True)
    spec = importlib.util.spec_from_file_location('game_build', REPO / 'platform/ps4/game-build.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    compiled_inputs = json.loads((args.candidate_build / 'evidence/game-build-inputs.json').read_text())
    current = module.inputs(args.candidate_build, args.platform)
    if current != compiled_inputs or module.identity(current) != assembly['program']['build_id']:
        raise ValueError('Current inputs differ from the candidate; retain mismatch and investigate')
    write(output / 'candidate-closure.json', {
        'source_commit': source_commit, 'source_archive_sha256': digest(source_archive),
        'compiled_build_id': module.identity(current), 'current_matches_compiled': True,
        'compiled_inputs_sha256': digest(args.candidate_build / 'evidence/game-build-inputs.json'),
        'platform_input_count': len(current['platform_inputs']),
        'port_input_count': len(current['port_inputs']), 'console_runs_created': 0})
    # Reinspect a private copy so original candidate evidence is never overwritten.
    candidate_copy = output / 'candidate-reinspection'
    shutil.copytree(args.candidate, candidate_copy)
    cli = REPO / 'platform/ps4/complete-package.py'
    run(['python3', cli, 'inspect', candidate_copy, '--platform-root', args.platform],
        output / 'candidate-inspect.log')

    def build(label):
        source = args.cache_root / ('source-23-' + label)
        root = args.cache_root / ('game-23-' + label)
        if source.exists() or root.exists():
            raise ValueError('Retain earlier attempts; use absent source and build destinations')
        source.mkdir()
        with tarfile.open(source_archive) as archive:
            archive.extractall(source, filter='data')
        # Downloads only: no target objects, headers or generated sources reused.
        root.mkdir()
        shutil.copytree(args.candidate_build / 'downloads', root / 'downloads')
        start = datetime.now(timezone.utc).isoformat()
        run(['bash', source / 'platform/ps4/build-game.sh', root, args.platform, '01.13'],
            output / ('build-' + label + '.log'),
            env=dict(os.environ, JOBS='6', CCACHE_DISABLE='1'))
        actual = json.loads((root / 'evidence/game-build-inputs.json').read_text())
        if actual != compiled_inputs:
            raise ValueError('Repeated build input closure differs from candidate')
        command = ['python3', cli, 'assemble', '--image', assembly['inputs']['image'],
                   '--program-stage', root / 'build/program-stage', '--elf', root / 'build/switchwaker',
                   '--platform-root', args.platform, '--kind', 'game', '--app-version', '01.13',
                   '--output', output / ('package-' + label)]
        original_argv = assembly['assembly_argv']
        if '--pipeline-cache' in original_argv:
            command.extend(['--pipeline-cache', original_argv[original_argv.index('--pipeline-cache') + 1]])
        run(command, output / ('assemble-' + label + '.log'))
        run(['python3', cli, 'inspect', output / ('package-' + label), '--platform-root', args.platform],
            output / ('inspect-' + label + '.log'))
        inspection = json.loads((output / ('package-' + label) / 'inspection.json').read_text())
        record = {'label': label, 'start_utc': start, 'end_utc': datetime.now(timezone.utc).isoformat(),
                  'source_root': str(source), 'build_root': str(root),
                  'compiled_build_id': module.identity(actual), 'inputs_match_candidate': True,
                  'elf_sha256': digest(root / 'build/switchwaker'),
                  'self_sha256': inspection['payload_sha256']['eboot.bin'],
                  'package_sha256': inspection['package']['sha256'],
                  'pipeline_seed_sha256': inspection['payload_sha256']['initial_pipeline_cache.db'],
                  'abi_audit': json.loads((root / 'evidence/game-abi-audit.json').read_text()),
                  'hardware_status': 'No console runs; provenance evidence only'}
        write(output / ('build-' + label + '.json'), record)
        return record

    with ThreadPoolExecutor(max_workers=2) as executor:
        records = list(executor.map(build, ['a', 'b']))
    write(output / 'repeat-builds.json', {'candidate_identity_preserved': assembly['package'],
          'scope': 'Two fresh game/source/Aurora builds using unchanged verified platform archives',
          'platform_rebuilt': False, 'builds': records, 'console_runs_created': 0})


if __name__ == '__main__':
    main()
