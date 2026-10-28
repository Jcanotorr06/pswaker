#!/usr/bin/env python3
"""Build a private, deliberately broken installed-content package for the owner checkpoint."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import struct
import sys
import tempfile

import build_inputs
from program_payload import package_metadata
spec = importlib.util.spec_from_file_location('complete_package', build_inputs.Locations().command('complete-package.py'))
assert spec is not None and spec.loader is not None
complete = importlib.util.module_from_spec(spec)
spec.loader.exec_module(complete)


def build(args):
    source = args.complete.resolve()
    destination = args.output.resolve()
    complete.require(not destination.exists(), 'Output already exists; choose a new private directory')
    complete.require(not destination.is_relative_to(complete.REPOSITORY), 'Failure packages must stay outside the repository')
    complete.require(destination.parent.is_dir(), 'Output parent must already exist')
    parent = json.loads((source / 'assembly.json').read_text())
    complete.require(parent['kind'] == 'game', 'Use an actual game complete package, never a diagnostic')
    complete.require(args.app_version != parent['app_version'], 'Give the failure variant a separate NN.NN version')
    with tempfile.TemporaryDirectory(prefix='.content-failure-', dir=destination.parent) as directory:
        work = Path(directory)
        tools = complete.Tools(args.platform_root.resolve(), work)
        provenance = tools.provenance()
        # Validate the complete parent independently before deriving a fault.
        complete.inspect_package(source, complete.Tools(args.platform_root.resolve(), source))
        program_stage = Path(parent['inputs']['program_stage'])
        complete.require(complete.inventory(program_stage) == parent['program']['payload_sha256'],
                         'Parent program staging payload changed; rebuild/reinspect the parent')
        stage = work / 'stage'
        shutil.copytree(program_stage, stage)
        if args.variant == 'unreadable':
            (stage / 'game.iso').mkdir()
            (stage / 'game.iso/INTENTIONALLY-NOT-A-FILE.txt').write_text('Controlled installed-content test\n')
        elif args.variant == 'invalid':
            # Keep the correct header and full length, then change one non-header byte.
            image = Path(parent['inputs']['image'])
            complete.require(complete.validate(image) == parent['manifest']['image'], 'Parent image changed')
            shutil.copyfile(image, stage / 'game.iso')
            with (stage / 'game.iso').open('r+b') as stream:
                stream.seek(0x7000)
                byte = stream.read(1)
                stream.seek(0x7000)
                stream.write(bytes([byte[0] ^ 1]))
        manifest = {'schema': 1, 'kind': 'CONTROLLED CONTENT FAILURE', 'variant': args.variant,
                    'expected': 'Installation error, stopped before gameplay; rebuild/reinstall guidance; preserve saves/settings',
                    'parent_package': parent['package'], 'program': parent['program'],
                    'installed_image': '/app0/game.iso', 'app_version': args.app_version,
                    'distribution_cleared': False, 'hardware_status': 'UNTESTED'}
        complete.write_json(stage / 'complete-package.json', manifest)
        identity = complete.IDENTITIES['game']
        tools.run(['bash', tools.root / 'refs/DolphinPS4/scripts/make-pkg.sh', stage,
                   identity['title_id'], identity['title'], args.app_version, identity['label'], work / 'out'])
        package = work / 'out' / (complete.content_id(identity) + '.pkg')
        with package.open('rb') as stream:
            header = stream.read(0x438)
        complete.require(len(header) == 0x438 and header[:4] == b'\x7fCNT'
                         and header[0x40:0x70].split(b'\0', 1)[0].decode() == complete.content_id(identity)
                         and struct.unpack_from('>Q', header, 0x430)[0] == package.stat().st_size,
                         'Failure package outer header identity/size mismatch')
        tools.run([tools.pkgtool, 'pkg_extract', package, work / 'extracted'])
        payload = work / 'extracted/uroot'
        expected = complete.inventory(stage)
        actual = complete.inventory(payload)
        resources = package_metadata(parent['kind'])
        metadata_paths = {'sce_sys/' + name for _, name in resources}
        complete.require(set(actual) == set(expected) - metadata_paths | {'sce_sys/keystone'},
                         'Failure package extraction has unexpected files')
        complete.require(all(actual[name] == sha for name, sha in expected.items()
                             if name not in metadata_paths),
                         'Failure package extraction changed program/content bytes')
        complete.require(actual['eboot.bin'] == parent['program']['eboot_sha256'], 'Failure package executable differs')
        if args.variant == 'missing':
            complete.require(not (payload / 'game.iso').exists(), 'Missing-content fault did not survive packaging')
        elif args.variant == 'unreadable':
            complete.require((payload / 'game.iso').is_dir(), 'Unreadable-content fault did not survive packaging')
        else:
            try:
                complete.validate(payload / 'game.iso')
            except ValueError as error:
                complete.require('SHA-1 mismatch' in str(error), 'Invalid-content fault failed for an unexpected reason')
            else:
                raise ValueError('Invalid-content fault unexpectedly passed validation')
        entries = tools.capture([tools.pkgtool, 'pkg_listentries', package])
        metadata = work / 'metadata'
        metadata.mkdir()
        for resource, name in resources:
            rows = [line.split() for line in entries.splitlines() if line.split() and line.split()[-1] == resource]
            complete.require(len(rows) == 1, f'Missing/duplicate failure package metadata {resource}')
            target = metadata / name
            tools.run([tools.pkgtool, 'pkg_extractentry', package, rows[0][3], target])
            if resource != 'PARAM_SFO':
                complete.require(complete.digest(target) == parent['program']['payload_sha256']['sce_sys/' + name],
                                 f'Failure package {resource} artwork differs from the parent program')
        fields = complete.sfo_fields((metadata / 'param.sfo').read_bytes())
        complete.require(fields['TITLE_ID'] == 'PSWK00001' and fields['APP_VER'] == args.app_version
                         and fields['CONTENT_ID'] == complete.content_id(identity), 'Failure package identity mismatch')
        manifest.update(package={'filename': package.name, 'sha256': complete.digest(package), 'size': package.stat().st_size},
                        payload_sha256=actual, sfo=fields, tools=provenance)
        shutil.copytree(source / 'elf', work / 'elf')
        complete.write_json(work / 'failure-inspection.json', manifest)
        shutil.rmtree(stage)
        shutil.rmtree(work / 'extracted')
        work.rename(destination)
    return manifest


def main():
    import re
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('complete', type=Path, help='Previously inspected private GAME complete-package directory')
    parser.add_argument('--platform-root', type=Path, required=True)
    parser.add_argument('--variant', choices=['missing', 'unreadable', 'invalid'], required=True)
    parser.add_argument('--app-version', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'\d{2}\.\d{2}', args.app_version):
        parser.error('--app-version must be NN.NN')
    try:
        os.umask(0o077)
        print(json.dumps(build(args), indent=2))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'Controlled failure assembly failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
