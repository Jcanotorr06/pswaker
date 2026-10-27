#!/usr/bin/env python3
"""Validate raw game images; assemble and inspect private complete PS4 packages."""
import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import struct
import subprocess
import sys
import tempfile

from disc_image import require, validate


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
INSTALLED_IMAGE = '/app0/game.iso'
IDENTITIES = {
    'diagnostic': {'title_id': 'PSWK00010', 'label': 'PSWAKERPROBE',
                   'title': 'PSWaker Diagnostic NONPLAYABLE',
                   'acceptance': 'NONPLAYABLE diagnostic; no game startup or hardware acceptance'},
    'game': {'title_id': 'PSWK00001', 'label': 'PSWAKERGAME', 'title': 'PSWaker',
             'acceptance': 'Unverified game program; package assembly does not establish playable acceptance'},
}
PROGRAM_FILES = {'eboot.bin', 'build-info.json', 'sce_sys/icon0.png', 'sce_sys/param.sfo',
                 'sce_sys/about/right.sprx', 'sce_module/libSceFios2.prx', 'sce_module/libc.prx'}
PIPELINE_SEED = 'initial_pipeline_cache.db'
# Selected game.lock.json Aurora ABI: clear.hpp v5 (8 bytes), gx/pipeline.hpp
# v13 (2772 bytes), little-endian x86-64. Renew this contract on renderer changes.
PIPELINE_CONFIGS = {0: (5, 8), 1: (13, 2772)}


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def inventory(root):
    files = {}
    for path in sorted(root.rglob('*')):
        require(not path.is_symlink(), f'Symbolic links are not allowed in payload: {path.name}')
        if path.is_file():
            files[path.relative_to(root).as_posix()] = digest(path)
    return files


def validate_pipeline_seed(db):
    require(db.execute('PRAGMA integrity_check').fetchall() == [('ok',)], 'Pipeline database integrity check failed')
    objects = db.execute("SELECT name FROM sqlite_master WHERE type != 'index'").fetchall()
    require(set(objects) == {('aurora_schema',), ('pipeline_cache',)}, 'Pipeline database has unexpected schema objects')
    require(db.execute('SELECT value FROM aurora_schema').fetchall() == [(1,)], 'Pipeline database schema must be 1')
    rows = db.execute('SELECT type, hash, config_version, config_size, config, first_frame_used '
                      'FROM pipeline_cache ORDER BY type, hash').fetchall()
    require(rows, 'Pipeline database contains no pipeline descriptions')
    seen, groups = set(), {}
    for kind, key, version, size, config, first_frame in rows:
        require(isinstance(kind, int) and kind in PIPELINE_CONFIGS and isinstance(key, int)
                and isinstance(first_frame, int) and 0 <= first_frame <= 0xffffffff,
                'Pipeline record has invalid type/hash/frame')
        require((version, size) == PIPELINE_CONFIGS[kind] and isinstance(config, bytes)
                and len(config) == size and int.from_bytes(config[:4], 'little') == version,
                'Pipeline configuration version/size differs from the selected renderer')
        require((kind, key) not in seen, 'Pipeline database contains duplicate pipeline descriptions')
        seen.add((kind, key))
        groups[kind] = groups.get(kind, 0) + 1
    return {'rows': len(rows), 'configurations': [
        {'type': kind, 'version': PIPELINE_CONFIGS[kind][0], 'bytes': PIPELINE_CONFIGS[kind][1], 'rows': count}
        for kind, count in sorted(groups.items())]}


def snapshot_pipeline_seed(source, target):
    require(source.is_file(), 'Pipeline database is missing')
    paths = [source]
    wal = source.with_name(source.name + '-wal')
    if wal.exists():
        paths.append(wal)
    originals = {p.name: {'bytes': p.stat().st_size, 'sha256': digest(p)} for p in paths}
    # SQLite may create/checkpoint sidecars even for reads. Work only on private
    # copies, replay their WAL, then emit one standalone DELETE-journal database.
    with tempfile.TemporaryDirectory(prefix='pipeline-snapshot-', dir=target.parent) as folder:
        copied = Path(folder) / source.name
        for path in paths:
            shutil.copyfile(path, copied.with_name(path.name))
            require(digest(path) == originals[path.name]['sha256'] == digest(copied.with_name(path.name)),
                    'Pipeline database/WAL changed while copying; close the application and retry')
        with closing(sqlite3.connect(copied.as_uri() + '?mode=ro', uri=True)) as db, \
                closing(sqlite3.connect(target)) as snapshot:
            db.execute('PRAGMA trusted_schema=OFF')
            validate_pipeline_seed(db)
            db.backup(snapshot)
            snapshot.execute('PRAGMA journal_mode=DELETE')
            details = validate_pipeline_seed(snapshot)
        require({p.name for p in [source, wal] if p.exists()} == set(originals)
                and all(digest(path) == originals[path.name]['sha256'] for path in paths),
                'Pipeline database/WAL changed during snapshot; close the application and retry')
    return {'schema': 1, 'installed_path': '/app0/' + PIPELINE_SEED,
            'source_files': originals, **details, 'sha256': digest(target)}


def prepare_pipeline_seed(source, output):
    destination = output.resolve()
    require(not destination.exists(), 'Output already exists; retain it and choose a new seed directory')
    require(not destination.is_relative_to(REPOSITORY), 'Pipeline seeds must remain outside the repository')
    with tempfile.TemporaryDirectory(prefix='.pipeline-seed-', dir=destination.parent) as folder:
        work = Path(folder)
        report = snapshot_pipeline_seed(source.resolve(), work / PIPELINE_SEED)
        write_json(work / 'pipeline-seed.json', report)
        work.rename(destination)
    return report


def content_id(identity):
    return f'IV0000-{identity["title_id"]}_00-{identity["label"].ljust(16, "0")}'


class Tools:
    def __init__(self, root, work):
        self.root, self.work = root, work
        self.sdk = root / 'sdk/opt/pacbrew/ps4/openorbis'
        self.pkgtool = root / 'build/pkgtool/PkgTool.Core'
        self.env = dict(os.environ, OPENORBIS=str(self.sdk), OO_PS4_TOOLCHAIN=str(self.sdk),
                        PS4_PKGTOOL=str(self.pkgtool), SFO_STYLE='plain', NO_RIGHT_SPRX='0',
                        DOLPHIN_PS4_MODULES_DIR='/nonexistent', DOTNET_SYSTEM_GLOBALIZATION_INVARIANT='1')
        history = work / 'commands.json'
        self.commands = json.loads(history.read_text()) if history.exists() else []
        require(isinstance(self.commands, list), 'Invalid retained tool command history')

    def run(self, command, cwd=None):
        self.commands.append({'argv': list(map(str, command)), 'cwd': str(cwd or self.work)})
        write_json(self.work / 'commands.json', self.commands)
        with (self.work / 'tools.log').open('a') as log:
            result = subprocess.run(list(map(str, command)), cwd=cwd or self.work,
                                    env=self.env, stdout=log, stderr=subprocess.STDOUT)
        require(result.returncode == 0,
                f'{Path(str(command[0])).name} failed (exit {result.returncode}); '
                'check the selected Linux/WSL2 platform build and program payload')

    def provenance(self):
        paths = [self.sdk / 'bin/create-fself', self.sdk / 'bin/linux/create-gp4',
                 self.pkgtool, self.pkgtool.with_name('PkgTool.Core.dll'),
                 self.pkgtool.with_name('LibOrbisPkg.Core.dll'),
                 self.root / 'refs/DolphinPS4/scripts/make-pkg.sh',
                 self.root / 'refs/DolphinPS4/toolchain/ps4-love-style.cmake',
                 self.root / 'refs/DolphinPS4/toolchain/check-oelf.cmake']
        sources = json.loads((self.root / 'evidence/source-archives.json').read_text())
        locks = json.loads((HERE / 'sources.lock.json').read_text())
        for name in ['src/liborbispkg', 'refs/DolphinPS4']:
            pinned = next(row for row in locks if row['path'] == name)
            require(pinned in sources, f'Platform source closure does not match selected {name}')
        return {'files': {str(path.relative_to(self.root)): digest(path) for path in paths},
                'source_closure_sha256': digest(self.root / 'evidence/input-closure.json'),
                'sources': [row for row in sources if row['path'] in {'src/liborbispkg', 'refs/DolphinPS4'}],
                'patches_sha256': digest(self.root / 'evidence/patches-packager.json')}


def sfo_fields(data):
    require(data[:4] == b'\0PSF' and len(data) >= 20, 'Invalid packaged SFO')
    keys, values, count = struct.unpack_from('<III', data, 8)
    require(20 + count * 16 <= keys <= values <= len(data), 'Invalid SFO tables')
    fields = {}
    for i in range(count):
        key_offset, kind, length, maximum, offset = struct.unpack_from('<HHIII', data, 20 + i * 16)
        start = keys + key_offset
        end = data.find(b'\0', start, values)
        require(keys <= start < end < values and length <= maximum and values + offset + maximum <= len(data),
                'Invalid SFO field bounds')
        key = data[start:end].decode()
        require(key not in fields, 'Duplicate SFO field')
        value = data[values + offset:values + offset + length]
        fields[key] = int.from_bytes(value, 'little') if kind == 0x0404 else value.rstrip(b'\0').decode()
    return fields


def inspect_package(work, tools):
    (work / 'inspection.json').unlink(missing_ok=True)
    report = json.loads((work / 'assembly.json').read_text())
    identity = IDENTITIES[report['kind']]
    filename = content_id(identity) + '.pkg'
    require(report['package']['filename'] == filename, 'Unexpected package application identity')
    package = work / 'out' / filename
    require(digest(package) == report['package']['sha256'], 'Package SHA-256 mismatch')
    # Header offsets follow the pinned LibOrbisPkg PKG/PkgReader.cs contract.
    with package.open('rb') as stream:
        header = stream.read(0x438)
    require(len(header) == 0x438 and header[:4] == b'\x7fCNT', 'Invalid PS4 package header')
    require(header[0x40:0x70].split(b'\0', 1)[0].decode() == content_id(identity),
            'Package header content ID mismatch')
    require(struct.unpack_from('>Q', header, 0x430)[0] == package.stat().st_size,
            'Package header size mismatch')
    elf_filename = report['program']['elf_filename']
    require(Path(elf_filename).name == elf_filename, 'Invalid matching ELF filename')
    require(digest(work / 'elf' / elf_filename) == report['program']['elf_sha256'], 'Matching ELF SHA-256 mismatch')
    require(tools.provenance() == report['tools'], 'Selected packaging tools/source closure changed')
    # Never reuse an extraction; include every extracted file in the comparison.
    with tempfile.TemporaryDirectory(prefix='inspect-', dir=work) as folder:
        extracted = Path(folder)
        tools.run([tools.pkgtool, 'pkg_extract', package, extracted])
        payload = extracted / 'uroot'
        actual = inventory(payload)
        expected = report['payload_sha256']
        require(set(actual) == set(expected) - {'sce_sys/param.sfo', 'sce_sys/icon0.png'},
                'Unexpected complete-package payload files')
        for path, sha in actual.items():
            require(sha == expected[path], f'Packaged payload SHA-256 mismatch: {path}')
        # These files are package entries, outside the PFS payload.
        entries = subprocess.check_output([str(tools.pkgtool), 'pkg_listentries', str(package)],
                                          cwd=work, text=True, env=tools.env)
        (work / 'package-entries.txt').write_text(entries)
        metadata = extracted / 'metadata'
        metadata.mkdir()
        for entry, name in [('PARAM_SFO', 'param.sfo'), ('ICON0_PNG', 'icon0.png')]:
            rows = [line.split() for line in entries.splitlines() if line.split() and line.split()[-1] == entry]
            require(len(rows) == 1, f'Missing/duplicate package metadata {entry}')
            target = metadata / name
            tools.run([tools.pkgtool, 'pkg_extractentry', package, rows[0][3], target])
            require(digest(target) == expected['sce_sys/' + name], f'Packaged {name} SHA-256 mismatch')
        fields = sfo_fields((metadata / 'param.sfo').read_bytes())
        for key, value in {'TITLE_ID': identity['title_id'], 'CONTENT_ID': content_id(identity),
                           'TITLE': identity['title'], 'APP_VER': report['app_version'],
                           'VERSION': report['app_version'], 'CATEGORY': 'gd',
                           'APP_TYPE': 1, 'ATTRIBUTE': 0, 'SYSTEM_VER': 0}.items():
            require(fields.get(key) == value, f'Package SFO identity/metadata mismatch: {key}')
        require(json.loads((payload / 'complete-package.json').read_text()) == report['manifest'],
                'Packaged complete-package manifest mismatch')
        seed = report['manifest'].get('pipeline_seed')
        if seed is not None:
            require(seed['installed_path'] == '/app0/' + PIPELINE_SEED
                    and digest(payload / PIPELINE_SEED) == seed['sha256'], 'Packaged pipeline seed identity mismatch')
            with closing(sqlite3.connect((payload / PIPELINE_SEED).as_uri() + '?mode=ro', uri=True)) as db:
                details = validate_pipeline_seed(db)
                require(details['rows'] == seed['rows'] and details['configurations'] == seed['configurations'],
                        'Packaged pipeline seed records differ from manifest')
        image = validate(payload / 'game.iso')
        require(image == report['manifest']['image'], 'Packaged image validation/hash mismatch')
        result = {'scope': identity['acceptance'], 'installed_image': INSTALLED_IMAGE,
                  'package': report['package'], 'sfo': fields, 'payload_sha256': expected,
                  'package_header': {'magic': '7f434e54', 'content_id': content_id(identity),
                                     'size': package.stat().st_size},
                  'image': image, 'program': report['program'], 'distribution_cleared': False,
                  'hardware_status': 'Untested; no console checkpoint in issue #16'}
        if seed is not None:
            result['pipeline_seed'] = seed
        write_json(work / 'inspection.json', result)
    return result


def prepare_program(stage, elf, kind, work, tools):
    files = inventory(stage)
    require(set(files) == PROGRAM_FILES, 'Program payload must contain only the documented data-free files; '
            'unexpected/missing: ' + ', '.join(sorted(set(files) ^ PROGRAM_FILES)))
    manifest = json.loads((stage / 'build-info.json').read_text())
    require(isinstance(manifest, dict), 'Program build-info.json must contain a JSON object')
    diagnostic = 'diagnostic_build_id' in manifest
    require(diagnostic == (kind == 'diagnostic'),
            'Program kind mismatch: diagnostic payloads must be explicitly labelled diagnostic/NONPLAYABLE')
    require(manifest['eboot_sha256'] == files['eboot.bin'], 'Program manifest SELF SHA-256 mismatch')
    build_id = manifest.get('diagnostic_build_id' if diagnostic else 'program_build_id')
    require(isinstance(build_id, str) and bool(build_id), 'Program manifest requires its compiled build identity')
    # Keep the matching unstripped input independently of the original build root.
    (work / 'elf').mkdir()
    snapshot = work / 'elf' / elf.name
    shutil.copyfile(elf, snapshot)
    binary = snapshot.read_bytes()
    require(len(binary) >= 64 and binary[:6] == b'\x7fELF\x02\x01'
            and struct.unpack_from('<H', binary, 18)[0] == 62, 'Program must be a little-endian x86-64 ELF')
    require(build_id.encode() in binary, 'Program build identity is absent from the matching ELF')
    sections = subprocess.check_output(['llvm-readelf-21', '--sections', str(snapshot)], text=True)
    require('.symtab' in sections, 'Matching unstripped program ELF is required')
    (work / 'elf-sections.txt').write_text(sections)
    output = work / 'self'
    output.mkdir()
    toolchain = (tools.root / 'refs/DolphinPS4/toolchain/ps4-love-style.cmake').read_text()
    authority = re.search(r'set\(PS4_AUTH_INFO "([0-9A-Fa-f]+)"\)', toolchain)
    require(authority is not None, 'Selected toolchain has no PS4_AUTH_INFO contract')
    # This pinned converter embeds the entire input path in DT_SCE_FILENAME.
    # Reproduce the original invocation, and check its input still matches our snapshot.
    tools.run([tools.sdk / 'bin/create-fself', '-in=' + str(elf.resolve()),
               '-out=' + str(output / 'program.oelf'), '--eboot', output / 'eboot.bin',
               '--paid', '0x3800000000000035', '--authinfo', authority[1]])
    tools.run(['cmake', '-DOELF=' + str(output / 'program.oelf'), '-P',
               tools.root / 'refs/DolphinPS4/toolchain/check-oelf.cmake'])
    require(digest(elf) == digest(snapshot), 'Explicit ELF changed during SELF conversion; retry with stable inputs')
    require(digest(output / 'eboot.bin') == files['eboot.bin'],
            'Explicit ELF does not reproduce the program payload SELF; use its original build path and selected converter')
    return {'build_id': build_id, 'elf_filename': elf.name, 'elf_sha256': digest(snapshot),
            'eboot_sha256': files['eboot.bin'], 'payload_sha256': files}


def assemble(args):
    destination = args.output.resolve()
    require(not destination.exists(), 'Output already exists; choose a new private assembly directory')
    require(not destination.is_relative_to(REPOSITORY), 'Complete packages must be assembled outside the repository')
    require(re.fullmatch(r'[0-9]{2}\.[0-9]{2}', args.app_version), '--app-version must be NN.NN')
    # Fail unsupported images before invoking tools or creating an output package.
    original_image = validate(args.image)
    require(destination.parent.is_dir(), 'Output parent directory must already exist')
    with tempfile.TemporaryDirectory(prefix='.complete-', dir=destination.parent) as folder:
        work = Path(folder)
        tools = Tools(args.platform_root.resolve(), work)
        provenance = tools.provenance()
        # Snapshot both inputs, so subsequent validation/packaging uses the same bytes.
        stage = work / 'stage'
        shutil.copytree(args.program_stage, stage, symlinks=True)
        program = prepare_program(stage, args.elf, args.kind, work, tools)
        shutil.copyfile(args.image, stage / 'game.iso')
        image = validate(stage / 'game.iso')
        require(image == original_image, 'Image changed during assembly; retry from a stable local file')
        identity = IDENTITIES[args.kind]
        manifest = {'schema': 1, 'kind': args.kind, 'acceptance': identity['acceptance'],
                    'title_id': identity['title_id'], 'content_id': content_id(identity),
                    'app_version': args.app_version, 'installed_image': INSTALLED_IMAGE,
                    'image': image, 'program': program, 'distribution_cleared': False,
                    'licensing': 'Private artifact. Review actual combined licenses, notices and provenance '
                                 'before any distribution; assembly is not licensing clearance.'}
        if args.pipeline_cache is not None:
            manifest['pipeline_seed'] = snapshot_pipeline_seed(args.pipeline_cache.resolve(), stage / PIPELINE_SEED)
        write_json(stage / 'complete-package.json', manifest)
        tools.run(['bash', tools.root / 'refs/DolphinPS4/scripts/make-pkg.sh', stage,
                   identity['title_id'], identity['title'], args.app_version, identity['label'], work / 'out'])
        package = work / 'out' / (content_id(identity) + '.pkg')
        require(package.is_file(), 'Selected packager did not produce the expected application package')
        files = inventory(stage)
        require(all(files[path] == sha for path, sha in program['payload_sha256'].items()
                    if path != 'sce_sys/param.sfo'), 'Packager changed an explicit program payload file')
        # LibOrbisPkg creates this PFS entry rather than writing it to the stage.
        # Extract it independently, then pin it for subsequent inspections.
        with tempfile.TemporaryDirectory(prefix='keystone-', dir=work) as extracted:
            tools.run([tools.pkgtool, 'pkg_extract', package, extracted])
            files['sce_sys/keystone'] = digest(Path(extracted) / 'uroot/sce_sys/keystone')
            entries = subprocess.check_output([str(tools.pkgtool), 'pkg_listentries', str(package)],
                                              text=True, env=tools.env)
            row = next(line.split() for line in entries.splitlines() if line.split() and line.split()[-1] == 'PARAM_SFO')
            packaged_sfo = Path(extracted) / 'param.sfo'
            tools.run([tools.pkgtool, 'pkg_extractentry', package, row[3], packaged_sfo])
            fields = sfo_fields(packaged_sfo.read_bytes())
            # The pinned packager adds its creation date/image sizes and tool version.
            generated = {'PUBTOOLINFO', 'PUBTOOLVER'}
            require({k: v for k, v in fields.items() if k not in generated}
                    == sfo_fields((stage / 'sce_sys/param.sfo').read_bytes()),
                    'Packager unexpectedly changed application SFO metadata')
            files['sce_sys/param.sfo'] = digest(packaged_sfo)
        report = {'schema': 1, 'kind': args.kind, 'app_version': args.app_version, 'manifest': manifest,
                  'program': program, 'tools': provenance, 'payload_sha256': files,
                  'preparation_inputs_sha256': {name: digest(HERE / name) for name in [
                      'complete-package.py', 'disc_image.py', 'content-contract.json', 'sources.lock.json']},
                  'packager_sfo_fields': {key: fields[key] for key in generated},
                  'package': {'filename': package.name, 'sha256': digest(package)},
                  'inputs': {'image': str(args.image.resolve()), 'elf': str(args.elf.resolve()),
                             'program_stage': str(args.program_stage.resolve()),
                             'platform_root': str(args.platform_root.resolve())},
                  'assembly_argv': [sys.executable, str(HERE / 'complete-package.py'), *sys.argv[1:]]}
        write_json(work / 'assembly.json', report)
        inspect_package(work, tools)
        # Only the inspected package is retained; staging/extraction copies contain private data.
        shutil.rmtree(stage)
        work.rename(destination)
    return {'output': str(destination), 'package': report['package'], 'acceptance': identity['acceptance']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    image = commands.add_parser('validate', help='Read-only supported-image validation; outputs hashes, never game bytes')
    image.add_argument('image', type=Path)
    seed = commands.add_parser('pipeline-seed', help='Snapshot a private pipeline database and its adjacent WAL')
    seed.add_argument('database', type=Path)
    seed.add_argument('--output', type=Path, required=True)
    assembly = commands.add_parser('assemble', help='Assemble privately outside this repository')
    assembly.add_argument('--image', type=Path, required=True)
    assembly.add_argument('--program-stage', type=Path, required=True)
    assembly.add_argument('--elf', type=Path, required=True)
    assembly.add_argument('--platform-root', type=Path, required=True)
    assembly.add_argument('--kind', choices=IDENTITIES, required=True)
    assembly.add_argument('--app-version', required=True)
    assembly.add_argument('--output', type=Path, required=True)
    assembly.add_argument('--pipeline-cache', type=Path,
                          help='Optional private pipeline database; snapshot with its adjacent WAL into the package')
    inspection = commands.add_parser('inspect', help='Freshly extract and inspect an assembled private package')
    inspection.add_argument('output', type=Path)
    inspection.add_argument('--platform-root', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'validate':
            result = validate(args.image)
        elif args.command == 'pipeline-seed':
            os.umask(0o077)
            result = prepare_pipeline_seed(args.database, args.output)
        elif args.command == 'assemble':
            require(sys.platform == 'linux', 'Assembly requires the selected Linux/WSL2 toolchain')
            os.umask(0o077)
            result = assemble(args)
        else:
            output = args.output.resolve()
            result = inspect_package(output, Tools(args.platform_root.resolve(), output))
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, KeyError, StopIteration, struct.error, sqlite3.Error, subprocess.CalledProcessError) as error:
        print(f'complete-package: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
