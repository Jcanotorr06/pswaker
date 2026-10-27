#!/usr/bin/env python3
"""Maintainer-only Windows x64 bundle build. The installed app needs no Python."""
import argparse
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

from disc_image import CONTRACT, require
from windows_package import seal_bundle


def build(program, packaging, output):
    require(sys.platform == 'win32' and struct.calcsize('P') == 8, 'Build on Windows with x64 CPython')
    output = output.resolve()
    require(not output.exists(), 'Build output already exists; choose a new private directory')
    require(not output.is_relative_to(CONTRACT.parents[2]), 'Build outside the repository')
    require(output.parent.is_dir(), 'Build output parent must exist')
    # A #40 release is prepared/verified once by the maintainer, never selected by the consumer.
    with tempfile.TemporaryDirectory(prefix='pswaker-desktop-build-') as folder:
        work = Path(folder)
        bundle = work / 'bundle'
        bundled = bundle / 'program'
        shutil.copytree(program, bundled, symlinks=True)
        shutil.copytree(packaging, bundle / 'packaging', symlinks=True)
        (bundle / 'platform/ps4').mkdir(parents=True)
        shutil.copyfile(CONTRACT, bundle / 'platform/ps4/content-contract.json')
        seal_bundle(bundle)
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--windowed', '--onedir', '--name', 'PSWaker',
                        '--distpath', str(output), '--workpath', str(work / 'work'), '--specpath', str(work),
                        '--add-data', str(bundle) + ':.',
                        str(Path(__file__).with_name('PSWaker.pyw'))], check=True)
    return output / 'PSWaker/PSWaker.exe'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--program', type=Path, required=True, help='Verified, private #40 game program release')
    parser.add_argument('--packaging', type=Path, required=True, help='Pinned self-contained Windows tool release')
    parser.add_argument('--output', type=Path, required=True, help='Absent private build directory outside the checkout')
    args = parser.parse_args()
    try:
        print(build(args.program, args.packaging, args.output))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'build-desktop: {error}\n')


if __name__ == '__main__':
    main()
