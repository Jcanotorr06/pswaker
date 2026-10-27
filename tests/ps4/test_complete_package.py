"""Observable preparation/package CLI behavior; fixtures contain synthetic bytes only."""
import json
import hashlib
import os
from pathlib import Path
import shutil
import sqlite3
import struct
import subprocess
import sys
import tempfile
import unittest

from synthetic_disc import generate

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/pswaker'))
from build_inputs import Locations

LOCATIONS = Locations()
REFERENCE = os.environ.get('PSWAKER_REFERENCE_BUILD')


class PreparationCliTestCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='pswaker-content-test-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.cli, self.image = generate(self.root, LOCATIONS.repository)

    def run_cli(self, *args, cli=None):
        return subprocess.run([sys.executable, str(cli or self.cli), *map(str, args)],
                              capture_output=True, text=True)

    def change(self, offset, data):
        with self.image.open('r+b') as stream:
            stream.seek(offset)
            stream.write(data)

    def pipeline_database(self, path, wal=False):
        db = sqlite3.connect(path)
        self.addCleanup(db.close)
        if wal:
            db.execute('PRAGMA journal_mode=WAL')
        db.execute('CREATE TABLE aurora_schema(value INTEGER)')
        db.execute('INSERT INTO aurora_schema VALUES (1)')
        db.execute('CREATE TABLE pipeline_cache(type INTEGER, hash INTEGER, config_version INTEGER, '
                   'config_size INTEGER, config BLOB, first_frame_used INTEGER, PRIMARY KEY(type,hash))')
        return db


class ImageValidationTests(PreparationCliTestCase):
    def test_catalogued_dump_acceptance_keeps_required_content_checks(self):
        contract_file = Locations(self.root / 'repo').platform / 'content-contract.json'
        contract = json.loads(contract_file.read_text())
        contract['additional_images'] = [{'sha1': contract['image_sha1'],
                                          'source': 'https://example.invalid/synthetic-catalogue'}]
        contract['image_sha1'] = '0' * 40
        contract_file.write_text(json.dumps(contract))
        result = self.run_cli('validate', self.image)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.change(0x1100, b'BAD')
        rejected = self.run_cli('validate', self.image)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn('sys/main.dol: content SHA-1 mismatch', rejected.stderr)

    def test_raw_image_and_compressed_required_members_are_accepted(self):
        result = self.run_cli('validate', self.image)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['game_id'], 'GZLE01')
        self.assertEqual(report['size'], 32768)
        self.assertEqual([row['size'] for row in report['required_content']], [288, 6, 20, 20])
        self.image.rename(self.image.with_suffix('.GCM'))
        result = self.run_cli('validate', self.image.with_suffix('.GCM'))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_synthetic_image_never_passes_the_production_contract(self):
        result = self.run_cli('validate', self.image, cli=LOCATIONS.command('complete-package.py'))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('full raw dump', result.stderr)

    def test_wrong_region_revision_and_disc_number_are_rejected(self):
        for offset, value in [(3, b'P'), (7, b'\x01'), (6, b'\x01')]:
            with self.subTest(offset=offset):
                original = self.image.read_bytes()
                self.change(offset, value)
                result = self.run_cli('validate', self.image)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('supply USA GZLE01 revision 0', result.stderr)
                self.image.write_bytes(original)

    def test_label_alone_does_not_allow_changed_executable_or_rel(self):
        for offset, label in [(0x1100, 'sys/main.dol'), (0x3011, 'rels/direct.rel'),
                              (0x4148, 'RELS.arc:rels/mmem/second.rel')]:
            with self.subTest(label=label):
                original = self.image.read_bytes()
                self.change(offset, b'BAD')
                result = self.run_cli('validate', self.image)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(label, result.stderr)
                self.assertIn('content SHA-1 mismatch', result.stderr)
                self.assertNotIn('Traceback', result.stderr)
                self.image.write_bytes(original)

    def test_changed_unchecked_asset_fails_the_full_image_contract(self):
        self.change(0x7000, b'changed padding/asset')
        result = self.run_cli('validate', self.image)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Full image SHA-1 mismatch', result.stderr)

    def test_truncated_image_and_bad_file_table_ranges_are_rejected(self):
        for offset, value in [(0x424, struct.pack('>I', 0xFFFFFF00)),
                              (0x2020, struct.pack('>I', 0xFFFFFFFF))]:
            with self.subTest(offset=offset):
                original = self.image.read_bytes()
                self.change(offset, value)
                result = self.run_cli('validate', self.image)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('invalid', result.stderr.lower())
                self.assertNotIn('Traceback', result.stderr)
                self.image.write_bytes(original)
        with self.image.open('r+b') as stream:
            stream.truncate(0x6000)
        result = self.run_cli('validate', self.image)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('truncated', result.stderr)

    def test_compressed_image_renamed_iso_has_actionable_format_error(self):
        with tempfile.TemporaryDirectory() as folder:
            image = Path(folder) / 'compressed.iso'
            image.write_bytes(b'RVZ\x01' + bytes(60))
            result = subprocess.run([sys.executable, str(LOCATIONS.command('complete-package.py')), 'validate', str(image)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Unsupported/compressed image', result.stderr)
            self.assertIn('raw ISO/GCM', result.stderr)
        self.assertNotIn('Traceback', result.stderr)


class PipelineSeedTests(PreparationCliTestCase):
    def test_runtime_seed_merge_metadata_is_not_bundled_again(self):
        source = self.root / 'merged.db'
        with self.pipeline_database(source) as db:
            db.execute('CREATE TABLE aurora_seed(identity TEXT PRIMARY KEY)')
            db.execute("INSERT INTO aurora_seed VALUES ('old-seed-identity')")
            db.execute('INSERT INTO pipeline_cache VALUES (0,42,5,8,?,10)', (struct.pack('<I4B', 5, 1, 1, 1, 0),))
        output = self.root / 'seed'
        result = self.run_cli('pipeline-seed', source, '--output', output)
        self.assertEqual(result.returncode, 0, result.stderr)
        with sqlite3.connect(output / 'initial_pipeline_cache.db') as seed:
            self.assertEqual(seed.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall(),
                             [('aurora_schema',), ('pipeline_cache',)])
        with sqlite3.connect(source) as original:
            self.assertEqual(original.execute('SELECT identity FROM aurora_seed').fetchall(), [('old-seed-identity',)])

    def test_wal_rows_are_snapshotted_without_modifying_original_files(self):
        source = self.root / 'pipeline_cache.db'
        with self.pipeline_database(source, wal=True) as db:
            db.commit()
            db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            db.execute('INSERT INTO pipeline_cache VALUES (0,42,5,8,?,10)',
                       (struct.pack('<I4B', 5, 1, 1, 1, 0),))
            db.commit()
            originals = {p: p.read_bytes() for p in [source, source.with_name(source.name + '-wal')]}
            output = self.root / 'seed'
            result = self.run_cli('pipeline-seed', source, '--output', output)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report['rows'], 1)
            seed = output / 'initial_pipeline_cache.db'
            self.assertEqual(report['sha256'], hashlib.sha256(seed.read_bytes()).hexdigest())
            with sqlite3.connect(seed) as snapshot:
                self.assertEqual(snapshot.execute('SELECT hash FROM pipeline_cache').fetchall(), [(42,)])
                self.assertEqual(snapshot.execute('PRAGMA journal_mode').fetchone(), ('delete',))
            self.assertEqual({p.name for p in output.iterdir()}, {'initial_pipeline_cache.db', 'pipeline-seed.json'})
            for path, original in originals.items():
                self.assertEqual(path.read_bytes(), original)

    def test_invalid_or_incompatible_seed_leaves_no_output(self):
        for case in ('schema', 'type', 'version', 'size', 'embedded-version', 'frame', 'empty', 'extra-table'):
            with self.subTest(case=case):
                source = self.root / (case + '.db')
                with self.pipeline_database(source) as db:
                    if case == 'schema':
                        db.execute('UPDATE aurora_schema SET value=2')
                    if case != 'empty':
                        db.execute('INSERT INTO pipeline_cache VALUES (?,?,?,?,?,?)',
                            (2 if case == 'type' else 0, 42, 4 if case == 'version' else 5,
                             7 if case == 'size' else 8,
                             struct.pack('<I4B', 4 if case == 'embedded-version' else 5, 1, 1, 1, 0),
                             -1 if case == 'frame' else 10))
                    if case == 'extra-table':
                        db.execute('CREATE TABLE unrelated(data BLOB)')
                output = self.root / (case + '-seed')
                result = self.run_cli('pipeline-seed', source, '--output', output)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Pipeline', result.stderr)
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse(output.exists())


@unittest.skipUnless(REFERENCE, 'Set PSWAKER_REFERENCE_BUILD to exercise real packaging tools')
class CompletePackageRoundtripTests(PreparationCliTestCase):
    def setUp(self):
        super().setUp()
        self.reference = Path(REFERENCE)
        self.output = self.root / 'private-complete'

    def assembly_args(self, stage=None, kind='diagnostic', output=None, version='01.05'):
        return ['assemble', '--image', self.image,
                '--program-stage', stage or self.reference / 'build/probe-stage',
                '--elf', self.reference / 'build/probe/platform_diagnostic',
                '--platform-root', self.reference, '--kind', kind,
                '--app-version', version, '--output', output or self.output]

    def test_explicit_diagnostic_roundtrip_and_changed_package_rejection(self):
        result = self.run_cli(*self.assembly_args())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        preparation = json.loads((self.output / 'assembly.json').read_text())['preparation_inputs_sha256']
        self.assertIn('tools/pswaker/build_inputs.py', preparation)
        self.assertIn('tools/pswaker/ownership.json', preparation)
        self.assertIn('platform/ps4/game/storage.cpp', preparation)
        original_commands = json.loads((self.output / 'commands.json').read_text())
        inspected = self.run_cli('inspect', self.output, '--platform-root', self.reference)
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        commands = json.loads((self.output / 'commands.json').read_text())
        self.assertEqual(commands[:len(original_commands)], original_commands)
        report = json.loads(inspected.stdout)
        self.assertEqual(report['installed_image'], '/app0/game.iso')
        self.assertEqual(report['sfo']['TITLE_ID'], 'PSWK00010')
        self.assertEqual(report['sfo']['CONTENT_ID'], 'IV0000-PSWK00010_00-PSWAKERPROBE0000')
        self.assertEqual(report['sfo']['APP_VER'], '01.05')
        self.assertIn('NONPLAYABLE', report['scope'])
        self.assertFalse(report['distribution_cleared'])
        self.assertEqual(report['image']['size'], 32768)
        package = self.output / 'out' / report['package']['filename']
        with package.open('r+b') as stream:
            stream.seek(0x40)
            stream.write(b'IV0000-FAIL00000')
        assembly = json.loads((self.output / 'assembly.json').read_text())
        with package.open('rb') as stream:
            assembly['package']['sha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
        (self.output / 'assembly.json').write_text(json.dumps(assembly))
        rejected = self.run_cli('inspect', self.output, '--platform-root', self.reference)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn('Package header content ID mismatch', rejected.stderr)
        self.assertFalse((self.output / 'inspection.json').exists())
        with package.open('r+b') as stream:
            stream.write(b'changed package')
        rejected = self.run_cli('inspect', self.output, '--platform-root', self.reference)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn('Package SHA-256 mismatch', rejected.stderr)

    def test_version_updates_keep_the_same_application_and_image_identity(self):
        reports = []
        for version in ['01.05', '01.06']:
            output = self.root / version
            result = self.run_cli(*self.assembly_args(output=output, version=version))
            self.assertEqual(result.returncode, 0, result.stderr)
            reports.append(json.loads((output / 'inspection.json').read_text()))
        self.assertEqual([r['sfo']['APP_VER'] for r in reports], ['01.05', '01.06'])
        self.assertEqual(reports[0]['sfo']['TITLE_ID'], reports[1]['sfo']['TITLE_ID'])
        self.assertEqual(reports[0]['sfo']['CONTENT_ID'], reports[1]['sfo']['CONTENT_ID'])
        self.assertEqual(reports[0]['image'], reports[1]['image'])

    def test_pipeline_seed_is_bound_to_manifest_and_freshly_inspected_payload(self):
        source = self.root / 'pipeline_cache.db'
        with self.pipeline_database(source) as db:
            db.execute('INSERT INTO pipeline_cache VALUES (0,42,5,8,?,10)', (struct.pack('<I4B', 5, 1, 1, 1, 0),))
        result = self.run_cli(*self.assembly_args(), '--pipeline-cache', source)
        self.assertEqual(result.returncode, 0, result.stderr)
        assembly = json.loads((self.output / 'assembly.json').read_text())
        seed = assembly['manifest']['pipeline_seed']
        self.assertEqual((seed['rows'], seed['installed_path']), (1, '/app0/initial_pipeline_cache.db'))
        inspected = self.run_cli('inspect', self.output, '--platform-root', self.reference)
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        report = json.loads(inspected.stdout)
        self.assertEqual(report['pipeline_seed'], seed)
        self.assertEqual(report['payload_sha256']['initial_pipeline_cache.db'], seed['sha256'])
        self.assertNotIn('initial_pipeline_cache.db-wal', report['payload_sha256'])

    def test_mismatched_elf_leaves_no_complete_package(self):
        other_elf = self.root / 'wrong.elf'
        other_elf.write_bytes(b'not an executable')
        args = self.assembly_args()
        args[args.index('--elf') + 1] = other_elf
        result = self.run_cli(*args)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('x86-64 ELF', result.stderr)
        self.assertFalse(self.output.exists())

    def test_diagnostic_cannot_be_relabelled_as_a_game(self):
        result = self.run_cli(*self.assembly_args(kind='game'))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('NONPLAYABLE', result.stderr)
        self.assertFalse(self.output.exists())

    def test_unapproved_program_file_leaves_no_complete_package(self):
        stage = self.root / 'program'
        shutil.copytree(self.reference / 'build/probe-stage', stage)
        (stage / 'unexpected.key').write_text('Synthetic forbidden payload')
        result = self.run_cli(*self.assembly_args(stage=stage))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unexpected.key', result.stderr)
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
