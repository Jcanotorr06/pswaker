#!/usr/bin/env python3
"""Inventory actual SDK provenance and retained notices before any distribution."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('root', type=Path)
root = parser.parse_args().root.resolve()
records = []
for item in json.loads((HERE / 'provenance/sdk-recipes.json').read_text()):
    recipe = HERE / item['recipe']
    package = next(record for record in json.loads((HERE / 'sdk.lock.json').read_text())['packages'] if record['name'] == item['package'])
    metadata = root / 'downloads/pacbrew' / (package['filename'] + '.BUILDINFO')
    expected = re.search(r'^pkgbuild_sha256sum = (.+)$', metadata.read_text(), re.M).group(1)
    if digest(recipe) != expected:
        raise ValueError('SDK build recipe provenance mismatch: ' + item['package'])
    records.append(dict(item, metadata_sha256=digest(metadata)))
notices = []
notice_root = root / 'evidence/notices'
notice_root.mkdir(exist_ok=True)
for tree in ['refs', 'src']:
    for path in sorted((root / tree).rglob('*')):
        if not path.is_file() or '.git' in path.parts:
            continue
        if path.name.upper().startswith(('LICENSE', 'COPYING', 'COPYRIGHT', 'NOTICE', 'THIRD_PARTY_LICENSE')):
            sha = digest(path)
            shutil.copyfile(path, notice_root / sha)
            notices.append({'path': path.relative_to(root).as_posix(), 'sha256': sha})
sdk = root / 'sdk/opt/pacbrew/ps4/openorbis'
original = root / 'src/sdk-source/openorbis/OpenOrbis-PS4-Toolchain-cd480230b946239f758333ef0dff40d67c5f0c20'
modules = []
for relative in ['samples/piglet/sce_module/libSceFios2.prx', 'samples/piglet/sce_module/libc.prx',
                 'samples/piglet/sce_sys/about/right.sprx']:
    path = sdk / relative
    source = original / relative
    if digest(path) != digest(source):
        raise ValueError('SDK sample module does not match recorded source archive: ' + relative)
    modules.append({'path': relative, 'sha256': digest(path), 'source_archive_member': relative,
                    'status': 'Inherited binary; per-file redistribution grant and corresponding source unresolved'})
report = {'sdk_recipes': records, 'notice_files': notices, 'inherited_modules': modules,
          'distribution_cleared': False,
          'limits': ['Sample-module binary provenance is verified; inclusion in an SDK archive does not establish distribution rights.',
                     'Preserve per-file notices in complete source archives, including musl math/regex and Mesa/DRM exceptions.',
                     'Provide exact source archives, patches, host locks and build instructions with any permitted combined distribution.',
                     'Resolve module rights and combined licensing obligations before public binary distribution.']}
(root / 'evidence/license-audit.json').write_text(json.dumps(report, indent=2) + '\n')
print(f'Verified {len(records)} SDK recipes; retained {len(notices)} notice files; inventoried {len(modules)} inherited modules')
