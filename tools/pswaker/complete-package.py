#!/usr/bin/env python3
"""Validate raw game images; assemble and inspect private complete PS4 packages."""
import argparse
from contextlib import closing, contextmanager
from dataclasses import dataclass
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
import time

import build_inputs

from disc_image import require, validate


LOCATIONS = build_inputs.Locations()
REPOSITORY = LOCATIONS.repository
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
RELEASE_MANIFEST = 'program-release.json'
KIND_MISMATCH = 'Program kind mismatch: diagnostic payloads must be explicitly labelled diagnostic/NONPLAYABLE'
# Expected input/tool failures; reported as actionable errors rather than tracebacks.
FAILURES =(OSError, ValueError, KeyError, StopIteration, struct.error, sqlite3.Error, subprocess.CalledProcessError)


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


def validate_pipeline_seed(db, *, allow_merge_metadata=False):
    require(db.execute('PRAGMA integrity_check').fetchall() == [('ok',)], 'Pipeline database integrity check failed')
    objects = set(db.execute("SELECT name FROM sqlite_master WHERE type != 'index'").fetchall())
    if allow_merge_metadata and ('aurora_seed',) in objects:
        columns = [(row[1], row[2], row[5]) for row in db.execute('PRAGMA table_info(aurora_seed)')]
        identities = db.execute('SELECT identity FROM aurora_seed').fetchall()
        require(columns == [('identity', 'TEXT', 1)] and len(identities) <= 1
                and all(isinstance(value, str) and value for (value,) in identities),
                'Pipeline seed merge metadata differs from the selected renderer')
        objects.remove(('aurora_seed',))
    require(objects == {('aurora_schema',), ('pipeline_cache',)}, 'Pipeline database has unexpected schema objects')
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
            validate_pipeline_seed(db, allow_merge_metadata=True)
            db.backup(snapshot)
            snapshot.execute('DROP TABLE IF EXISTS aurora_seed')
            snapshot.commit()
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
        locks = json.loads((LOCATIONS.platform / 'sources.lock.json').read_text())
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
        require(report['manifest']['kind'] == report['kind'] and report['manifest']['program'] == report['program'],
                'Complete-package manifest program identity mismatch')
        # Bind the extracted executable and its own build manifest to the verified program identity.
        info = json.loads((payload / 'build-info.json').read_text())
        diagnostic = report['kind'] == 'diagnostic'
        require(actual['eboot.bin'] == info.get('eboot_sha256') == report['program']['eboot_sha256'],
                'Packaged program SELF identity mismatch')
        require(('diagnostic_build_id' in info) == diagnostic and info.get(
            'diagnostic_build_id' if diagnostic else 'program_build_id') == report['program']['build_id'],
                'Packaged program build identity/kind mismatch')
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


def convert_program(tools, source, output, cwd=None):
    """Run the selected converter on the exact `-in=` argument `source`, then the retained OELF check."""
    output.mkdir()
    toolchain = (tools.root / 'refs/DolphinPS4/toolchain/ps4-love-style.cmake').read_text()
    authority = re.search(r'set\(PS4_AUTH_INFO "([0-9A-Fa-f]+)"\)', toolchain)
    require(authority is not None, 'Selected toolchain has no PS4_AUTH_INFO contract')
    tools.run([tools.sdk / 'bin/create-fself', '-in=' + source,
               '-out=' + str(output / 'program.oelf'), '--eboot', output / 'eboot.bin',
               '--paid', '0x3800000000000035', '--authinfo', authority[1]], cwd=cwd)
    tools.run(['cmake', '-DOELF=' + str(output / 'program.oelf'), '-P',
               tools.root / 'refs/DolphinPS4/toolchain/check-oelf.cmake'])
    return output / 'eboot.bin'


def prepare_program(stage, elf, kind, work, tools, release=None):
    files = inventory(stage)
    require(set(files) == PROGRAM_FILES, 'Program payload must contain only the documented data-free files; '
            'unexpected/missing: ' + ', '.join(sorted(set(files) ^ PROGRAM_FILES)))
    manifest = json.loads((stage / 'build-info.json').read_text())
    require(isinstance(manifest, dict), 'Program build-info.json must contain a JSON object')
    diagnostic = 'diagnostic_build_id' in manifest
    require(diagnostic == (kind == 'diagnostic'), KIND_MISMATCH)
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
    if release is None:
        # This pinned converter embeds the entire input path in DT_SCE_FILENAME.
        # Reproduce the original invocation, and check its input still matches our snapshot.
        eboot = convert_program(tools, str(elf.resolve()), work / 'self')
        mismatch = ('Explicit ELF does not reproduce the program payload SELF; '
                    'use its original build path and selected converter')
    else:
        # Releases are converted from the bare ELF filename, so any copy reproduces them.
        require(digest(snapshot) == release['elf_sha256'], 'Program ELF differs from its release manifest')
        eboot = convert_program(tools, snapshot.name, work / 'self', cwd=snapshot.parent)
        mismatch = 'Release ELF does not reproduce its program SELF with the selected converter; rebuild the release'
    require(digest(elf) == digest(snapshot), 'Explicit ELF changed during SELF conversion; retry with stable inputs')
    require(digest(eboot) == files['eboot.bin'], mismatch)
    return {'build_id': build_id, 'elf_filename': elf.name, 'elf_sha256': digest(snapshot),
            'eboot_sha256': files['eboot.bin'], 'payload_sha256': files}


def read_release(root, kind, tools):
    require(root.is_dir() and {path.name for path in root.iterdir()} == {RELEASE_MANIFEST, 'stage', 'elf'},
            f'Program release must contain only {RELEASE_MANIFEST}, stage/ and elf/')
    release = json.loads((root / RELEASE_MANIFEST).read_text())
    require(isinstance(release, dict) and release.get('schema') == 1
            and all(isinstance(release.get(key), dict) for key in ['converter', 'payload_sha256', 'developer_build']),
            'Unsupported program release manifest')
    require(release['kind'] == kind, KIND_MISMATCH)
    name = release['elf_filename']
    require(isinstance(name, str) and release['converter']['input'] == name
            and [path.name for path in (root / 'elf').iterdir()] == [name],
            'Program release must contain exactly its matching ELF')
    require(digest(tools.sdk / 'bin/create-fself') == release['converter']['sha256'],
            'Selected converter differs from the program release converter')
    return release


def load_program(source, kind, work, tools):
    """Snapshot a data-free program into work/stage and verify that its ELF reproduces its SELF."""
    stage = work / 'stage'
    if source.release is None:
        shutil.copytree(source.stage, stage, symlinks=True)
        program = prepare_program(stage, source.elf, kind, work, tools)
        return program, {'elf': str(source.elf.resolve()), 'program_stage': str(source.stage.resolve())}
    root = source.release.resolve()
    release = read_release(root, kind, tools)
    shutil.copytree(root / 'stage', stage, symlinks=True)
    files = inventory(stage)
    changed = sorted(path for path in set(files) | set(release['payload_sha256'])
                     if files.get(path) != release['payload_sha256'].get(path))
    require(not changed, 'Program payload differs from its release manifest: ' + ', '.join(changed))
    elf = root / 'elf' / release['elf_filename']
    program = prepare_program(stage, elf, kind, work, tools, release)
    program['release'] = {'manifest_sha256': digest(root / RELEASE_MANIFEST), 'converter_input': release['elf_filename'],
                          'developer_eboot_sha256': release['developer_build']['eboot_sha256']}
    return program, {'program': str(root), 'elf': str(elf), 'program_stage': str(root / 'stage')}


def release_program(stage, elf, kind, platform_root, output):
    """Derive a relocatable program release from a verified developer build at its original path."""
    destination = output.resolve()
    require(not destination.exists(), 'Output already exists; choose a new program release directory')
    require(not destination.is_relative_to(REPOSITORY), 'Program releases must be prepared outside the repository')
    require(destination.parent.is_dir(), 'Output parent directory must already exist')
    root = platform_root.resolve()
    with tempfile.TemporaryDirectory(prefix='.program-release-', dir=destination.parent) as folder:
        work = Path(folder)
        (work / 'developer').mkdir()
        tools = Tools(root, work / 'developer')
        developer, _ = load_program(Program(stage=stage, elf=elf), kind, work / 'developer', tools)
        release = work / 'release'
        (release / 'elf').mkdir(parents=True)
        shutil.copytree(work / 'developer/stage', release / 'stage', symlinks=True)
        shutil.copyfile(work / 'developer/elf' / elf.name, release / 'elf' / elf.name)
        eboot = convert_program(tools, elf.name, work / 'developer/release-self', cwd=release / 'elf')
        shutil.copyfile(eboot, release / 'stage/eboot.bin')
        info = json.loads((release / 'stage/build-info.json').read_text())
        info['eboot_sha256'] = digest(eboot)
        info['program_release'] = {'converter_input': elf.name, 'developer_eboot_sha256': developer['eboot_sha256']}
        write_json(release / 'stage/build-info.json', info)
        manifest = {'schema': 1, 'kind': kind, 'acceptance': IDENTITIES[kind]['acceptance'],
                    'build_id': developer['build_id'], 'elf_filename': elf.name, 'elf_sha256': developer['elf_sha256'],
                    'eboot_sha256': info['eboot_sha256'], 'payload_sha256': inventory(release / 'stage'),
                    'converter': {'input': elf.name, 'sha256': digest(tools.sdk / 'bin/create-fself')},
                    'developer_build': {'eboot_sha256': developer['eboot_sha256'],
                                        'payload_sha256': developer['payload_sha256']},
                    'tools': tools.provenance(), 'distribution_cleared': False,
                    'licensing': 'Data-free program payload. Review actual licenses, notices and provenance '
                                 'before any distribution; preparation is not licensing clearance.'}
        write_json(release / RELEASE_MANIFEST, manifest)
        # Accept the release only once it verifies exactly as assembly will verify it.
        (work / 'verify').mkdir()
        load_program(Program(release=release), kind, work / 'verify', Tools(root, work / 'verify'))
        release.rename(destination)
    return manifest


@dataclass(frozen=True)
class Program:
    """A relocatable program release, or a developer stage with its ELF at the original build path."""
    release: Path | None = None
    stage: Path | None = None
    elf: Path | None = None


@dataclass(frozen=True)
class PackageRequest:
    image: Path
    program: Program
    kind: str
    app_version: str
    platform_root: Path
    output: Path
    pipeline_cache: Path | None = None
    command: tuple = ()


class StageFailure(ValueError):
    """A packaging failure attributed to the stage that observed it."""
    def __init__(self, stage, error):
        super().__init__(str(error))
        self.stage = stage


class Stages:
    def __init__(self, observe):
        self.observe = observe or (lambda event: None)
        self.timings = []

    @contextmanager
    def __call__(self, stage):
        self.observe({'stage': stage, 'event': 'started'})
        start = time.monotonic()
        try:
            yield
        except FAILURES as error:
            self.observe({'stage': stage, 'event': 'failed', 'seconds': round(time.monotonic() - start, 3),
                          'error': str(error)})
            raise StageFailure(stage, error) from error
        seconds = round(time.monotonic() - start, 3)
        self.timings.append({'stage': stage, 'seconds': seconds})
        self.observe({'stage': stage, 'event': 'passed', 'seconds': seconds})


def create_package(request, observe=None):
    """Validate, assemble, freshly inspect and publish a private complete package.

    `observe` receives each stage's start, then its pass or failure, in this order:
    validate, verify-program, assemble, inspect, publish. Failures raise StageFailure.
    The output appears only once a fresh inspection has passed.
    """
    stages = Stages(observe)
    destination = request.output.resolve()
    with stages('validate'):
        require(not destination.exists(), 'Output already exists; choose a new private assembly directory')
        require(not destination.is_relative_to(REPOSITORY), 'Complete packages must be assembled outside the repository')
        require(re.fullmatch(r'[0-9]{2}\.[0-9]{2}', request.app_version), '--app-version must be NN.NN')
        # Fail unsupported images before invoking tools or creating an output package.
        original_image = validate(request.image)
        require(destination.parent.is_dir(), 'Output parent directory must already exist')
        workspace = tempfile.TemporaryDirectory(prefix='.complete-', dir=destination.parent)
    with workspace as folder:
        work = Path(folder)
        with stages('verify-program'):
            tools = Tools(request.platform_root.resolve(), work)
            provenance = tools.provenance()
            # Snapshot both inputs, so subsequent validation/packaging uses the same bytes.
            program, inputs = load_program(request.program, request.kind, work, tools)
        with stages('assemble'):
            stage = work / 'stage'
            shutil.copyfile(request.image, stage / 'game.iso')
            image = validate(stage / 'game.iso')
            require(image == original_image, 'Image changed during assembly; retry from a stable local file')
            identity = IDENTITIES[request.kind]
            manifest = {'schema': 1, 'kind': request.kind, 'acceptance': identity['acceptance'],
                        'title_id': identity['title_id'], 'content_id': content_id(identity),
                        'app_version': request.app_version, 'installed_image': INSTALLED_IMAGE,
                        'image': image, 'program': program, 'distribution_cleared': False,
                        'licensing': 'Private artifact. Review actual combined licenses, notices and provenance '
                                     'before any distribution; assembly is not licensing clearance.'}
            if request.pipeline_cache is not None:
                manifest['pipeline_seed'] = snapshot_pipeline_seed(request.pipeline_cache.resolve(),
                                                                   stage / PIPELINE_SEED)
            write_json(stage / 'complete-package.json', manifest)
            tools.run(['bash', tools.root / 'refs/DolphinPS4/scripts/make-pkg.sh', stage, identity['title_id'],
                       identity['title'], request.app_version, identity['label'], work / 'out'])
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
                row = next(line.split() for line in entries.splitlines()
                           if line.split() and line.split()[-1] == 'PARAM_SFO')
                packaged_sfo = Path(extracted) / 'param.sfo'
                tools.run([tools.pkgtool, 'pkg_extractentry', package, row[3], packaged_sfo])
                fields = sfo_fields(packaged_sfo.read_bytes())
                # The pinned packager adds its creation date/image sizes and tool version.
                generated = {'PUBTOOLINFO', 'PUBTOOLVER'}
                require({k: v for k, v in fields.items() if k not in generated}
                        == sfo_fields((stage / 'sce_sys/param.sfo').read_bytes()),
                        'Packager unexpectedly changed application SFO metadata')
                files['sce_sys/param.sfo'] = digest(packaged_sfo)
            report = {'schema': 1, 'kind': request.kind, 'app_version': request.app_version, 'manifest': manifest,
                      'program': program, 'tools': provenance, 'payload_sha256': files,
                      'preparation_inputs_sha256': build_inputs.maintained_inventory(),
                      'packager_sfo_fields': {key: fields[key] for key in generated},
                      'package': {'filename': package.name, 'sha256': digest(package)},
                      'inputs': {'image': str(request.image.resolve()), **inputs,
                                 'platform_root': str(request.platform_root.resolve())},
                      'assembly_argv': list(request.command)}
            write_json(work / 'assembly.json', report)
        with stages('inspect'):
            inspect_package(work, tools)
        with stages('publish'):
            write_json(work / 'stages.json', stages.timings)
            # Only the inspected package is retained; staging/extraction copies contain private data.
            shutil.rmtree(stage)
            require(not destination.exists(), 'Output appeared during assembly; it was retained unchanged')
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
    release = commands.add_parser('release-program',
                                  help='Derive a relocatable program release from a verified developer build')
    release.add_argument('--program-stage', type=Path, required=True)
    release.add_argument('--elf', type=Path, required=True, help='Matching unstripped ELF at its original build path')
    release.add_argument('--platform-root', type=Path, required=True)
    release.add_argument('--kind', choices=IDENTITIES, required=True)
    release.add_argument('--output', type=Path, required=True)
    assembly = commands.add_parser('assemble', help='Assemble privately outside this repository')
    assembly.add_argument('--image', type=Path, required=True)
    assembly.add_argument('--program', type=Path, help='Relocatable program release from release-program')
    assembly.add_argument('--program-stage', type=Path, help='Developer program stage; requires --elf')
    assembly.add_argument('--elf', type=Path, help='Matching unstripped ELF at its original build path')
    assembly.add_argument('--platform-root', type=Path, required=True)
    assembly.add_argument('--kind', choices=IDENTITIES, required=True)
    assembly.add_argument('--app-version', required=True)
    assembly.add_argument('--output', type=Path, required=True)
    assembly.add_argument('--pipeline-cache', type=Path,
                          help='Optional private pipeline database; snapshot with its adjacent WAL into the package')
    assembly.add_argument('--progress', action='store_true',
                          help='Write one JSON stage event per line to stderr')
    inspection = commands.add_parser('inspect', help='Freshly extract and inspect an assembled private package')
    inspection.add_argument('output', type=Path)
    inspection.add_argument('--platform-root', type=Path, required=True)
    args = parser.parse_args()
    developer = (args.program_stage, args.elf) if args.command == 'assemble' else ()
    if developer and not ((args.program is not None and developer == (None, None))
                          or (args.program is None and None not in developer)):
        parser.error('assemble requires either --program, or both --program-stage and --elf')
    try:
        if args.command == 'validate':
            result = validate(args.image)
        elif args.command == 'pipeline-seed':
            os.umask(0o077)
            result = prepare_pipeline_seed(args.database, args.output)
        elif args.command == 'release-program':
            require(sys.platform == 'linux', 'Program release requires the selected Linux/WSL2 toolchain')
            os.umask(0o077)
            result = release_program(args.program_stage, args.elf, args.kind, args.platform_root, args.output)
        elif args.command == 'assemble':
            require(sys.platform == 'linux', 'Assembly requires the selected Linux/WSL2 toolchain')
            os.umask(0o077)
            request = PackageRequest(
                image=args.image, program=Program(args.program, args.program_stage, args.elf), kind=args.kind,
                app_version=args.app_version, platform_root=args.platform_root, output=args.output,
                pipeline_cache=args.pipeline_cache,
                command=(sys.executable, str(LOCATIONS.command('complete-package.py')), *sys.argv[1:]))
            progress = lambda event: print(json.dumps(event), file=sys.stderr, flush=True)
            result = create_package(request, progress if args.progress else None)
        else:
            output = args.output.resolve()
            result = inspect_package(output, Tools(args.platform_root.resolve(), output))
        print(json.dumps(result, indent=2))
    except FAILURES as error:
        print(f'complete-package: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
