#!/usr/bin/env python3
"""Freshly inspect a staged game's data-free program package and its artwork."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from disc_image import require
from package_artifact import (FAILURES, IDENTITIES, content_id, digest, expected_sfo_fields,
                              inventory, sfo_fields, write_json)
from program_payload import checked_artwork, inventory_changes, package_metadata, program_files


def inspect(root, platform):
    evidence = root / 'evidence'
    report_path = evidence / 'game-program-inspection.json'
    report_path.unlink(missing_ok=True)
    record = json.loads((evidence / 'game-program-artifacts.json').read_text())
    identity = IDENTITIES['game']
    filename = content_id(identity) + '.pkg'
    require(record['package']['filename'] == filename, 'Unexpected game program package identity')
    package = root / 'out/program' / filename
    # Reject a changed package before invoking any extraction tool.
    require(digest(package) == record['package']['sha256'], 'Package SHA-256 mismatch')
    attempt = json.loads((evidence / 'game-staging-attempt.json').read_text())
    require(attempt['status'] == 'succeeded', 'No successful current game staging attempt; rerun stage')
    require(record['title_id'] == identity['title_id'] and record['content_id'] == content_id(identity),
            'Game staging application identity mismatch')
    with package.open('rb') as stream:
        header = stream.read(0x70)
    require(header[:4] == b'\x7fCNT' and header[0x40:0x70].split(b'\0', 1)[0].decode() == content_id(identity),
            'Game package header content ID mismatch')
    expected = record['program_stage_sha256']
    require(set(expected) == program_files('game'), 'Unexpected recorded game program-stage inventory')
    require(inventory(root / 'build/program-stage') == expected, 'Current game program stage changed')
    elf = root / 'build/switchwaker'
    require(digest(elf) == record['elf_sha256'], 'Matching game ELF SHA-256 mismatch')
    require(record['compiled_build_id'].encode() in elf.read_bytes(), 'Compiled game build identity missing')
    tool = str(platform / 'build/pkgtool/PkgTool.Core')
    env = dict(os.environ, DOTNET_SYSTEM_GLOBALIZATION_INVARIANT='1')
    with tempfile.TemporaryDirectory(prefix='game-inspection-', dir=evidence) as directory:
        extracted = Path(directory)
        with (evidence / 'game-program-extract.log').open('w') as log:
            subprocess.run([tool, 'pkg_extract', str(package), str(extracted)], check=True,
                           env=env, stdout=log, stderr=subprocess.STDOUT)
        payload = extracted / 'uroot'
        actual = inventory(payload)
        resources = package_metadata('game')
        expected_payload = {name: sha for name, sha in expected.items()
                            if name not in {'sce_sys/' + name for _, name in resources}}
        require(set(actual) == set(expected_payload) | {'sce_sys/keystone'},
                'Unexpected game package payload (including ICON0_PNG/PIC1_PNG resources)')
        changes = inventory_changes(expected_payload, {name: sha for name, sha in actual.items()
                                                       if name != 'sce_sys/keystone'})
        require(not changes, 'Game package payload SHA-256 mismatch: ' + changes)
        entries = subprocess.check_output([tool, 'pkg_listentries', str(package)], text=True, env=env)
        (evidence / 'game-program-entries.txt').write_text(entries)
        metadata = extracted / 'metadata'
        metadata.mkdir()
        for resource, name in resources:
            rows = [line.split() for line in entries.splitlines() if line.split() and line.split()[-1] == resource]
            require(len(rows) == 1, f'Missing/duplicate game package metadata {resource}')
            target = metadata / name
            subprocess.run([tool, 'pkg_extractentry', str(package), rows[0][3], str(target)],
                           check=True, env=env, stdout=subprocess.DEVNULL)
            if resource != 'PARAM_SFO':
                require(digest(target) == expected['sce_sys/' + name], f'{resource}: packaged SHA-256 mismatch')
            actual['sce_sys/' + name] = digest(target)
        manifest = json.loads((payload / 'build-info.json').read_text())
        require(manifest == json.loads((evidence / 'game-program.json').read_text()), 'Packaged game manifest mismatch')
        require('diagnostic_build_id' not in manifest and manifest['program_build_id'] == record['compiled_build_id']
                and manifest['eboot_sha256'] == actual['eboot.bin'] == record['eboot_sha256']
                and manifest['elf_sha256'] == record['elf_sha256']
                and manifest['build_inputs_sha256'] == record['build_inputs_sha256']
                and manifest['app_version'] == record['app_version'] and manifest['cache'] == record['cache'],
                'Packaged game build identity mismatch')
        artwork = checked_artwork(metadata, manifest, decode=True)
        for resource, properties in artwork.items():
            require({key: value for key, value in record['artwork'][resource].items() if key != 'source_path'}
                    == properties, f'{resource}: local artwork identity mismatch')
        fields = sfo_fields((metadata / 'param.sfo').read_bytes())
        # The pinned packager adds image sizes, creation time and its tool version.
        require({key: value for key, value in fields.items() if key not in {'PUBTOOLINFO', 'PUBTOOLVER'}}
                == sfo_fields((root / 'build/program-stage/sce_sys/param.sfo').read_bytes()),
                'Packager changed game application SFO metadata')
        for key, value in expected_sfo_fields(identity, record['app_version']).items():
            require(fields.get(key) == value, f'Game package SFO mismatch: {key}')
        require(digest(package) == record['package']['sha256'], 'Game package changed during inspection')
        report = {'package': record['package'], 'compiled_build_id': record['compiled_build_id'],
                  'cache': record['cache'], 'artwork': artwork, 'sfo': fields, 'package_files': actual,
                  'hardware_status': 'Untested; host inspection does not establish console visibility or timing'}
        write_json(report_path, report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('platform_root', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(args.root.resolve(), args.platform_root.resolve()), indent=2))
    except FAILURES as error:
        print(f'Game program inspection failed: {error}', file=sys.stderr)
        sys.exit(1)
