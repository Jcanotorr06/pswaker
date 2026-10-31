"""Shared complete-package formats, fresh artifact inspection and operation stages."""
from contextlib import closing, contextmanager
import hashlib
import json
from pathlib import Path
import sqlite3
import struct
import subprocess
import tempfile
import time

from disc_image import require, validate
from build_operation import BuildCancelled, checkpoint, progress
from program_payload import package_metadata, checked_artwork

INSTALLED_IMAGE = '/app0/game.iso'

IDENTITIES = {
    'diagnostic': {'title_id': 'PSWK00010', 'label': 'PSWAKERPROBE',
                   'title': 'PSWaker Diagnostic NONPLAYABLE',
                   'acceptance': 'NONPLAYABLE diagnostic; no game startup or hardware acceptance'},
    'game': {'title_id': 'PSWK00001', 'label': 'PSWAKERGAME', 'title': 'PSWaker',
             'acceptance': 'Unverified game program; package assembly does not establish playable acceptance'},
}

PIPELINE_SEED = 'initial_pipeline_cache.db'

# Selected game.lock.json Aurora ABI: clear.hpp v5 (8 bytes), gx/pipeline.hpp
# v13 (2772 bytes), little-endian x86-64. Renew this contract on renderer changes.
PIPELINE_CONFIGS = {0: (5, 8), 1: (13, 2772)}

FAILURES = (OSError, ValueError, KeyError, TypeError, StopIteration, struct.error, sqlite3.Error,
            subprocess.CalledProcessError)

def digest(path):
    with path.open('rb') as stream:
        sha = hashlib.sha256()
        total, completed = path.stat().st_size, 0
        progress('Checking ' + path.name, 0, total)
        while chunk := stream.read(8 << 20):
            checkpoint()
            sha.update(chunk)
            completed += len(chunk)
            progress('Checking ' + path.name, completed, total)
        return sha.hexdigest()

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

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

def content_id(identity):
    return f'IV0000-{identity["title_id"]}_00-{identity["label"].ljust(16, "0")}'


def expected_sfo_fields(identity, version):
    return {'TITLE_ID': identity['title_id'], 'CONTENT_ID': content_id(identity),
            'TITLE': identity['title'], 'APP_VER': version, 'VERSION': version,
            'CATEGORY': 'gd', 'APP_TYPE': 1, 'ATTRIBUTE': 0, 'SYSTEM_VER': 0}


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
        resources = package_metadata(report['kind'])
        require(set(actual) == set(expected) - {'sce_sys/' + name for _, name in resources},
                'Unexpected complete-package payload files (including ICON0_PNG/PIC1_PNG resources)')
        for path, sha in actual.items():
            require(sha == expected[path], f'Packaged payload SHA-256 mismatch: {path}')
        # These files are package entries, outside the PFS payload.
        entries = tools.capture([tools.pkgtool, 'pkg_listentries', package])
        (work / 'package-entries.txt').write_text(entries)
        metadata = extracted / 'metadata'
        metadata.mkdir()
        if report['kind'] == 'diagnostic':
            require(not any(line.split() and line.split()[-1] == 'PIC1_PNG' for line in entries.splitlines()),
                    'Unexpected package metadata PIC1_PNG for diagnostic')
        for entry, name in resources:
            rows = [line.split() for line in entries.splitlines() if line.split() and line.split()[-1] == entry]
            require(len(rows) == 1, f'Missing/duplicate package metadata {entry}')
            target = metadata / name
            tools.run([tools.pkgtool, 'pkg_extractentry', package, rows[0][3], target])
            require(digest(target) == expected['sce_sys/' + name], f'Packaged {entry} ({name}) SHA-256 mismatch')
        fields = sfo_fields((metadata / 'param.sfo').read_bytes())
        for key, value in expected_sfo_fields(identity, report['app_version']).items():
            require(fields.get(key) == value, f'Package SFO identity/metadata mismatch: {key}')
        require(json.loads((payload / 'complete-package.json').read_text()) == report['manifest'],
                'Packaged complete-package manifest mismatch')
        require(report['manifest']['kind'] == report['kind'] and report['manifest']['program'] == report['program'],
                'Complete-package manifest program identity mismatch')
        # Bind the extracted executable and its own build manifest to the verified program identity.
        info = json.loads((payload / 'build-info.json').read_text())
        diagnostic = report['kind'] == 'diagnostic'
        artwork = checked_artwork(metadata, info, decode=tools.decode_artwork) if not diagnostic else None
        require(actual['build-info.json'] == report['program']['payload_sha256']['build-info.json'],
                'Packaged program manifest SHA-256 mismatch')
        if artwork is not None:
            for resource, name in resources[1:]:
                require(expected['sce_sys/' + name] == artwork[resource]['sha256']
                        == report['program']['payload_sha256']['sce_sys/' + name],
                        f'{resource}: packaged artwork differs from the verified program')
        require(actual['eboot.bin'] == info.get('eboot_sha256') == report['program']['eboot_sha256'],
                'Packaged program SELF identity mismatch')
        require(('diagnostic_build_id' in info) == diagnostic and info.get(
            'diagnostic_build_id' if diagnostic else 'program_build_id') == report['program']['build_id'],
                'Packaged program build identity/kind mismatch')
        seed = report['manifest'].get('pipeline_seed')
        require(diagnostic or isinstance(seed, dict), 'Game complete package requires its validated shader seed manifest')
        require((seed is not None) == (PIPELINE_SEED in actual), 'Packaged pipeline seed/manifest presence mismatch')
        if seed is not None:
            require(seed['installed_path'] == '/app0/' + PIPELINE_SEED
                    and digest(payload / PIPELINE_SEED) == seed['sha256'], 'Packaged pipeline seed identity mismatch')
            require(seed.get('bytes') == (payload / PIPELINE_SEED).stat().st_size,
                    'Packaged pipeline seed size differs from manifest')
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
                  'hardware_status': 'Untested; package inspection is not console acceptance'}
        if seed is not None:
            result['pipeline_seed'] = seed
        if artwork is not None:
            result['artwork'] = artwork
        require(digest(package) == report['package']['sha256'], 'Package changed during fresh inspection')
        write_json(work / 'inspection.json', result)
    return result

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
            checkpoint()
            yield
            checkpoint()
        except BuildCancelled:
            self.observe({'stage': stage, 'event': 'cancelled', 'seconds': round(time.monotonic() - start, 3)})
            raise
        except Exception as error:
            self.observe({'stage': stage, 'event': 'failed', 'seconds': round(time.monotonic() - start, 3),
                          'error': str(error)})
            raise StageFailure(stage, error) from error
        seconds = round(time.monotonic() - start, 3)
        self.timings.append({'stage': stage, 'seconds': seconds})
        self.observe({'stage': stage, 'event': 'passed', 'seconds': seconds})
