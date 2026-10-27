#!/usr/bin/env python3
"""Obtain and verify the maintained diagnostic's locked download inputs."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import zipfile

import build_inputs

PLATFORM = build_inputs.Locations().platform


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def archive(root, item, fetch):
    path = root / 'downloads' / item['path']
    if not path.exists() and fetch:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + '.part')
        subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
                        '--retry', '2', '--connect-timeout', '20', '--max-time', '1800',
                        item['url'], '--output', str(temporary)], check=True)
        if digest(temporary) != item['sha256']:
            raise ValueError('SHA-256 mismatch: ' + item['path'])
        temporary.replace(path)
    if not path.is_file():
        raise ValueError('Missing locked input: ' + item['path'])
    if digest(path) != item['sha256']:
        raise ValueError('SHA-256 mismatch: ' + item['path'])


def check_host():
    lock = json.loads((PLATFORM / 'host.lock.json').read_text())
    if Path('/etc/os-release').read_text() != lock['os_release']:
        raise ValueError('Host OS differs from host.lock.json')
    if subprocess.check_output(['uname', '-m'], text=True).strip() != lock['architecture']:
        raise ValueError('Host architecture differs from host.lock.json')
    for name, item in lock['tools'].items():
        found = shutil.which(name)
        if not found or digest(Path(found)) != item['sha256']:
            raise ValueError('Host tool differs from host.lock.json: ' + name)
        version = subprocess.check_output([name, '--version'], text=True, stderr=subprocess.STDOUT).strip()
        if version != item['version']:
            raise ValueError('Host tool version differs from host.lock.json: ' + name)
    installed = dict(line.split('\t') for line in subprocess.check_output(['dpkg-query', '-W'], text=True).splitlines())
    for name, version in lock['required_packages'].items():
        if installed.get(name) != version:
            raise ValueError('Host build package differs from host.lock.json: ' + name)
    print('Verified locked host tools')


def prepare_deps(root, lock):
    for name in ('mesa', 'libdrm'):
        item = lock[name]
        tree = root / 'src' / name
        subprocess.run(['git', 'clone', '--depth', '1', '--branch', item['ref'],
                        '--single-branch', item['repository'], str(tree)], check=True)
        actual = subprocess.check_output(['git', '-C', str(tree), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != item['revision']:
            raise ValueError('Source revision mismatch: ' + name)
    for item in lock['dawn_deps']:
        tree = root / item['path']
        tree.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'init', '-q', str(tree)], check=True)
        subprocess.run(['git', '-C', str(tree), 'fetch', '--depth', '1',
                        item['repository'], item['revision']], check=True)
        subprocess.run(['git', '-C', str(tree), 'checkout', '--detach', 'FETCH_HEAD'], check=True)
    for item in lock['cmake_archives']:
        target = root / 'src/fetch' / item['name']
        target.mkdir(parents=True)
        source = root / 'downloads' / ('cmake/' + item['filename'])
        if source.suffix == '.zip':
            with zipfile.ZipFile(source) as package:
                package.extractall(target)
        else:
            with tarfile.open(source) as package:
                package.extractall(target, filter='data')
        children = list(target.iterdir())
        if len(children) != 1 or not children[0].is_dir():
            raise ValueError('Expected one archive root: ' + item['name'])
        item['source_dir'] = str(children[0])
    options = ['set(FETCHCONTENT_FULLY_DISCONNECTED ON CACHE BOOL "Locked inputs" FORCE)']
    for item in lock['cmake_archives']:
        options.append(f'set(FETCHCONTENT_SOURCE_DIR_{item["name"].upper()} "{item["source_dir"]}" CACHE PATH "Locked input" FORCE)')
    (root / 'toolchain').mkdir(exist_ok=True)
    (root / 'toolchain/fetch-inputs.cmake').write_text('\n'.join(options) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['fetch', 'verify', 'host', 'dependencies'])
    parser.add_argument('root', type=Path)
    parser.add_argument('--lock', type=Path, default=PLATFORM / 'dependencies.lock.json')
    args = parser.parse_args()
    if args.action == 'host':
        check_host()
        return
    lock = json.loads(args.lock.read_text())
    root = args.root.resolve()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda item: archive(root, item, args.action == 'fetch'), lock['archives']))
    print('Verified all locked downloads')
    if args.action == 'dependencies':
        prepare_deps(root, lock)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
