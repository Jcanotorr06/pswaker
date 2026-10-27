#!/usr/bin/env python3
"""Maintainer-only Windows x64 bundle build. The installed app needs no Python."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

from disc_image import CONTRACT, require
from program_payload import PROGRAM_FILES, bundled_program


def build(program, output):
    require(sys.platform == 'win32' and struct.calcsize('P') == 8, 'Build on Windows with x64 CPython')
    output = output.resolve()
    require(not output.exists(), 'Build output already exists; choose a new private directory')
    require(not output.is_relative_to(CONTRACT.parents[2]), 'Build outside the repository')
    require(output.parent.is_dir(), 'Build output parent must exist')
    # A #40 release is prepared/verified once by the maintainer, never selected by the consumer.
    with tempfile.TemporaryDirectory(prefix='pswaker-desktop-build-') as folder:
        work = Path(folder)
        bundled = work / 'program'
        shutil.copytree(program, bundled, symlinks=True)
        bundled_program(work)
        release = json.loads((bundled / 'program-release.json').read_text())
        require(set(release['payload_sha256']) == PROGRAM_FILES,
                'Program payload must contain only the documented data-free files')
        require({path.name for path in bundled.iterdir()} == {'program-release.json', 'stage', 'elf'},
                'Use a data-free program release with no extra entries')
        paths = [path for path in bundled.rglob('*')]
        require(not any(path.is_symlink() for path in paths), 'Program releases must not contain symbolic links')
        actual = {path.relative_to(bundled).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in paths if path.is_file() and path != bundled / 'program-release.json'}
        expected = {'stage/' + name: sha for name, sha in release['payload_sha256'].items()}
        expected['elf/' + release['elf_filename']] = release['elf_sha256']
        require(actual == expected, 'Program release files differ from the verified release manifest')
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--windowed', '--onedir', '--name', 'PSWaker',
                        '--distpath', str(output), '--workpath', str(work / 'work'), '--specpath', str(work),
                        '--add-data', str(bundled) + ':program',
                        '--add-data', str(CONTRACT) + ':platform/ps4',
                        str(Path(__file__).with_name('PSWaker.pyw'))], check=True)
    return output / 'PSWaker/PSWaker.exe'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--program', type=Path, required=True, help='Verified, private #40 game program release')
    parser.add_argument('--output', type=Path, required=True, help='Absent private build directory outside the checkout')
    args = parser.parse_args()
    try:
        print(build(args.program, args.output))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'build-desktop: {error}\n')


if __name__ == '__main__':
    main()
