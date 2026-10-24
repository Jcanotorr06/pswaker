#!/usr/bin/env python3
"""Prepare the pinned native game and data-free stub headers on Linux/WSL2."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

HERE = Path(__file__).resolve().parent


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory(tree):
    return {p.relative_to(tree).as_posix(): digest(p) for p in sorted(tree.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts}


def apply_patches(tree, directory):
    for patch in sorted(directory.glob('*.patch')):
        subprocess.run(['git', 'apply', '--check', str(patch)], cwd=tree, check=True)
        subprocess.run(['git', 'apply', '--whitespace=nowarn', str(patch)], cwd=tree, check=True)


def retain_verified_source(expected, target):
    if not target.exists():
        shutil.copytree(expected, target)
    elif inventory(expected) != inventory(target):
        raise ValueError(f'{target.name}: prepared source differs from pinned archive and patches; '
                         'use a fresh game root; existing files were preserved')


def prepare(root, platform_root=None):
    lock = json.loads((HERE / 'game.lock.json').read_text())
    (root / 'downloads').mkdir(parents=True, exist_ok=True)
    (root / 'evidence').mkdir(exist_ok=True)
    records = []
    for row in lock['sources']:
        name = row['name']
        archive = root / 'downloads' / (name + '.tar.gz')
        url = f"https://api.github.com/repos/{row['repository']}/tarball/{row['revision']}"
        if not archive.exists():
            part = archive.with_suffix('.part')
            urllib.request.urlretrieve(url, part)
            if digest(part) != row['sha256']:
                raise ValueError(f'{name}: source archive SHA-256 mismatch')
            part.replace(archive)
        if digest(archive) != row['sha256']:
            raise ValueError(f'{name}: source archive SHA-256 mismatch')
        with tempfile.TemporaryDirectory(prefix='.source-', dir=root) as directory:
            expected = Path(directory)
            with tarfile.open(archive) as source:
                for member in source.getmembers():
                    parts = Path(member.name).parts[1:]
                    if parts:
                        member.name = str(Path(*parts))
                        source.extract(member, expected, filter='data')
            if name == 'switchwaker':
                apply_patches(expected, HERE / 'patches/game')
            retain_verified_source(expected, root / 'src' / name)
        records.append(dict(row, archive_url=url))
    game = root / 'src/switchwaker'
    assets = root / 'assets/GZLE01'
    assets.mkdir(parents=True, exist_ok=True)
    if not (assets / 'res').exists():
        shutil.copytree(root / 'src/decomp/assets/GZLE01/res', assets / 'res')
    subprocess.run([sys.executable, str(game / 'native/tools/gen_asset_stubs.py'),
                    '--decomp', str(root / 'src/decomp'), '--out', str(assets)], check=True)
    contract = json.loads((HERE / 'content-contract.json').read_text())
    hashes = [contract['image_sha1']] + [row['sha1'] for row in contract['additional_images']]
    (assets / 'image-contract.hpp').write_text(
        '#pragma once\n#include <cstdint>\n'
        f"constexpr uint64_t image_size = {contract['image_size']};\n"
        'constexpr const char* image_sha1[] = {' + ','.join(json.dumps(h) for h in hashes) + '};\n')
    result = {'sources': records,
              'patches': inventory(HERE / 'patches/game'),
              'prepared_game': inventory(game), 'stub_headers': inventory(assets)}
    if platform_root:
        # Work on game-local copies. Never mutate the verified diagnostic's inputs.
        with tempfile.TemporaryDirectory(prefix='.platform-', dir=root) as directory:
            expected = Path(directory)
            shutil.copytree(platform_root / 'src/aurora', expected / 'aurora')
            shutil.copytree(platform_root / 'src/native-platform/ps4', expected / 'platform')
            apply_patches(expected, HERE / 'patches/game-platform')
            for name in ['aurora', 'platform']:
                retain_verified_source(expected / name, root / 'src' / name)
                result[name] = inventory(root / 'src' / name)
        result['platform_root'] = str(platform_root)
        result['platform_patches'] = inventory(HERE / 'patches/game-platform')
        result['platform_evidence'] = {
            name: digest(platform_root / 'evidence' / name) for name in [
                'artifacts.json', 'inspection.json', 'input-closure.json',
                'license-audit.json', 'renderer-reconciliation.json']}
    (root / 'evidence/game-inputs.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Prepared pinned game and stub headers; no disc data used.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--platform-root', type=Path, help='Previously verified maintained PS4 build')
    args = parser.parse_args()
    try:
        prepare(args.root.resolve(), args.platform_root.resolve() if args.platform_root else None)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'Game preparation failed: {error}', file=sys.stderr)
        sys.exit(1)
