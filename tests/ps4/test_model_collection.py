"""Public collection-to-seed boundary, with synthetic descriptions only."""
import json
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil
import unittest

from synthetic_pipeline import make_seed, make_model_collection
from synthetic_disc import generate
from synthetic_model_collector import add_model_resource, make_collector, MODEL_BYTES
from contextlib import closing
import sqlite3

CLI = Path(__file__).resolve().parents[2] / 'tools/pswaker/collect-model-seed.py'


@unittest.skipUnless(sys.platform == 'linux' and shutil.which('xvfb-run'), 'Linux collector process boundary required')
class CollectorCommandTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        _, self.image = generate(self.root, CLI.parents[2])
        self.cli = self.root / 'repo/tools/pswaker/collect-model-seed.py'
        add_model_resource(self.image, self.root / 'repo/platform/ps4/content-contract.json')
        self.collector = self.root / 'collector-build'
        self.baseline = make_collector(self.collector)
        self.output = self.root / 'collected'
        self.root.joinpath('settings.ini').write_text('owner settings sentinel')

    def collect(self):
        return subprocess.run([sys.executable, str(self.cli), 'collect', '--collector', str(self.collector),
                               '--image', str(self.image), '--baseline', str(self.baseline),
                               '--output', str(self.output)], capture_output=True, text=True)

    def test_command_repeats_export_and_attributes_exact_build_image_and_resource(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        result = self.collect()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'collection.json').read_text())
        self.assertEqual(report['collector']['sha256'], hashlib.sha256((self.collector / 'collector').read_bytes()).hexdigest())
        self.assertEqual(report['collector']['build_sha256'],
                         hashlib.sha256((self.collector / 'collector-build.json').read_bytes()).hexdigest())
        self.assertEqual(report['image_sha256'], hashlib.sha256(self.image.read_bytes()).hexdigest())
        self.assertEqual(report['resources']['model_sha256'], hashlib.sha256(MODEL_BYTES).hexdigest())
        self.assertEqual((report['recorder_verified_rows'], report['baseline_roundtrip_rows']), (1, 3))
        self.assertEqual(report['scenario'], 'always-small-pot-stock-v1')
        self.assertEqual(report['method'], 'asset-material-draw')
        self.output = self.root / 'repeat'
        self.assertEqual(self.collect().returncode, 0)
        repeated = json.loads((self.output / 'collection.json').read_text())
        self.assertEqual(repeated['seed_sha256'], report['seed_sha256'])
        self.assertEqual(repeated['collector'], report['collector'])
        self.assertEqual(repeated['resources'], report['resources'])
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_malformed_or_no_draw_report_is_rejected_at_the_collector_boundary(self):
        for mode in ['malformed', 'no-draw']:
            with self.subTest(mode=mode):
                self.collector.joinpath('mode').write_text(mode)
                self.output = self.root / mode
                result = self.collect()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Invalid model collection', result.stderr)
                self.assertNotIn('Traceback', result.stderr)

    def test_native_failures_and_recorder_disagreement_retain_failed_attempts(self):
        for mode, signal in [('fail', 'synthetic native failure'), ('recorder-mismatch', 'Observed descriptions differ')]:
            with self.subTest(mode=mode):
                self.collector.joinpath('mode').write_text(mode)
                self.output = self.root / mode
                result = self.collect()
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue((self.output / 'collector.log').is_file())
                self.assertIn(signal, result.stderr + (self.output / 'collector.log').read_text())
                self.assertNotEqual(self.collect().returncode, 0)


class ModelCollectionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.baseline = self.root / 'baseline'
        self.collection = self.root / 'collection'
        self.output = self.root / 'prepared'
        make_seed(self.baseline, keys=(42, 84))
        make_model_collection(self.collection)

    def prepare(self):
        return subprocess.run([sys.executable, str(CLI), 'prepare',
                               '--collection', str(self.collection),
                               '--baseline', str(self.baseline), '--output', str(self.output)],
                              capture_output=True, text=True)

    def test_preserves_baseline_and_attributes_deduplicated_generated_descriptions(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'collection-report.json').read_text())
        self.assertEqual(report['baseline_rows'], 2)
        self.assertEqual(report['collected_rows'], 2)
        self.assertEqual(report['baseline_covered_rows'], 1)
        self.assertEqual(report['new_rows'], 1)
        self.assertEqual(report['seed']['rows'], 3)
        self.assertEqual(report['provenance'], 'asset-material-draw')
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_unattributed_export_is_rejected_without_publishing_a_seed(self):
        path = self.collection / 'collection.json'
        metadata = json.loads(path.read_text())
        del metadata['collector']
        path.write_text(json.dumps(metadata))
        result = self.prepare()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('collector identity', result.stderr)
        self.assertFalse(self.output.exists())

    def test_attribution_must_identify_the_exact_collected_description_asset(self):
        path = self.collection / 'collection.json'
        metadata = json.loads(path.read_text())
        metadata['seed_sha256'] = 'd' * 64
        path.write_text(json.dumps(metadata))
        result = self.prepare()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('collection attribution', result.stderr)
        self.assertFalse(self.output.exists())

    def change_asset(self, statement):
        path = self.collection / 'assets/initial_pipeline_cache.db'
        with closing(sqlite3.connect(path)) as db, db:
            db.execute(statement)
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest = self.collection / 'assets/pipeline-seed.json'
        value = json.loads(manifest.read_text())
        value['sha256'] = sha
        manifest.write_text(json.dumps(value))
        metadata = self.collection / 'collection.json'
        value = json.loads(metadata.read_text())
        value['seed_sha256'] = sha
        metadata.write_text(json.dumps(value))

    def test_conflicting_description_rejects_the_whole_collection(self):
        self.change_asset("UPDATE pipeline_cache SET config=X'0500000000010100' WHERE hash=84")
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.prepare()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('conflicting description bytes', result.stderr)
        self.assertFalse(self.output.exists())
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_incompatible_record_is_rejected_even_alongside_compatible_records(self):
        self.change_asset('UPDATE pipeline_cache SET type=2 WHERE hash=126')
        result = self.prepare()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('renderer-incompatible', result.stderr)
        self.assertFalse(self.output.exists())

    def test_corrupt_or_malformed_exports_are_rejected(self):
        path = self.collection / 'collection.json'
        original = path.read_bytes()
        for bad in ['{', '[]', '{"schema":99}', json.dumps({**json.loads(original), 'draw_calls': 0})]:
            with self.subTest(metadata=bad):
                path.write_text(bad)
                self.assertNotEqual(self.prepare().returncode, 0)
                self.assertFalse(self.output.exists())
        path.write_bytes(original)
        self.collection.joinpath('assets/initial_pipeline_cache.db').write_bytes(b'not a database')
        self.assertNotEqual(self.prepare().returncode, 0)
        self.assertFalse(self.output.exists())

    def test_repeat_preparation_is_deterministic_and_keeps_prior_outputs(self):
        self.assertEqual(self.prepare().returncode, 0)
        before = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}
        self.assertNotEqual(self.prepare().returncode, 0)
        prior = self.output
        self.output = self.root / 'repeat'
        self.assertEqual(self.prepare().returncode, 0)
        self.assertEqual({p.relative_to(self.output): p.read_bytes()
                          for p in self.output.rglob('*') if p.is_file()}, before)
        self.assertEqual({p.relative_to(prior): p.read_bytes() for p in prior.rglob('*') if p.is_file()}, before)

    def test_covered_collection_retains_the_exact_baseline_asset(self):
        self.change_asset('DELETE FROM pipeline_cache WHERE hash=126')
        path = self.collection / 'assets/pipeline-seed.json'
        value = json.loads(path.read_text())
        value['rows'] = value['configurations'][0]['rows'] = 1
        path.write_text(json.dumps(value))
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'collection-report.json').read_text())
        self.assertEqual((report['baseline_covered_rows'], report['new_rows']), (1, 0))
        for name in ['initial_pipeline_cache.db', 'pipeline-seed.json']:
            self.assertEqual((self.output / 'assets' / name).read_bytes(), (self.baseline / name).read_bytes())

    def test_output_cannot_be_created_inside_an_immutable_input(self):
        self.output = self.collection / 'new-seed'
        result = self.prepare()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('outside source', result.stderr)
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
