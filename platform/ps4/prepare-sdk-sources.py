#!/usr/bin/env python3
"""Recover the SDK runtime sources named by the matching PacBrew recipes."""
import argparse
from pathlib import Path
import stat
import tarfile
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('root', type=Path)
root = parser.parse_args().root.resolve()
for name in ['musl', 'openorbis']:
    target = root / 'src/sdk-source' / name
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(root / 'downloads/sdk-source' / (name + '.zip')) as archive:
        archive.extractall(target)
        for member in archive.infolist():
            path = target / member.filename
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode):
                destination = archive.read(member).decode()
                if not (path.parent / destination).resolve().is_relative_to(target.resolve()):
                    raise ValueError('SDK source link escapes extraction root: ' + member.filename)
                path.unlink()
                path.symlink_to(destination)
            elif not member.is_dir():
                path.chmod(mode & 0o777 or 0o644)
with tarfile.open(root / 'downloads/sdk-source/llvm12.tar.xz') as archive:
    wanted = ['compiler-rt/', 'libunwind/', 'libcxx/', 'llvm/cmake/', 'cmake/']
    members = [item for item in archive if any(item.name.startswith('llvm-project-12.0.1.src/' + part) for part in wanted)]
    archive.extractall(root / 'src', members=members, filter='data')
with tarfile.open(root / 'downloads/sdk-source/zlib.tar.gz') as archive:
    archive.extractall(root / 'src', filter='data')
for name in ['libpng.tar.xz', 'bzip2.tar.bz2']:
    with tarfile.open(root / 'downloads/sdk-source' / name) as archive:
        archive.extractall(root / 'src', filter='data')
# The PacBrew LLVM-12 patch changes libc++ only. We rebuild its unmodified
# builtins/unwinder sources; libc++ and libc++abi come from the selected LLVM 21.
