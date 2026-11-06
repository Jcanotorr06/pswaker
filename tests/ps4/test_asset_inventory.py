"""Public batch-to-seed tests using synthetic resources and descriptions only."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import sqlite3
from contextlib import closing

from synthetic_pipeline import make_seed, make_model_collection


CLI = Path(__file__).resolve().parents[2] / 'tools/pswaker/collect-model-seed.py'


class AssetInventoryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.baseline = self.root / 'baseline'
        make_seed(self.baseline, keys=(42, 84))
        self.collections = self.root / 'collections'
        self.collections.mkdir()
        self.manifest = self.root / 'inventory.json'
        self.output = self.root / 'prepared'
        self.rows = []
        for identifier, keys in [('exterior', (84, 126)), ('interior', (126, 168))]:
            metadata = make_model_collection(self.collections / identifier, keys=keys)
            metadata.update(resources={'archive_sha256': 'd' * 64, 'model_sha256': 'e' * 64,
                                       'model_bytes': 100}, contract_sha256='f' * 64)
            (self.collections / identifier / 'collection.json').write_text(json.dumps(metadata))
            self.rows.append({'id': identifier, 'family': 'synthetic-stock',
                              'resource': metadata['resource'], 'source_references': ['synthetic/actor.cpp:draw'],
                              'dimensions': {'content': [identifier], 'mode': ['normal'], 'state': ['stock-bdl-v1']},
                              'input_identity': metadata['resources'], 'action': 'exercise',
                              'assumptions': ['Stock draw excludes actor-controlled state.']})
        self.document = {'schema': 1, 'id': 'synthetic-inventory-v1',
                         'image_sha256': 'c' * 64, 'contract_sha256': 'f' * 64,
                         'collector': metadata['collector'],
                         'dynamic_exclusions': [{'id': 'actor-lighting', 'owner': '#151',
                                                'reason': 'Requires a separate dynamic exercise.'}],
                         'rows': self.rows}
        self.save_manifest()

    def save_manifest(self):
        self.manifest.write_text(json.dumps(self.document))

    def prepare(self):
        return subprocess.run([sys.executable, str(CLI), 'prepare-batch',
                               '--manifest', str(self.manifest), '--collections', str(self.collections),
                               '--baseline', str(self.baseline), '--output', str(self.output)],
                              capture_output=True, text=True)

    def test_batch_preserves_all_sources_and_deduplicates_full_descriptions_repeatably(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'batch-report.json').read_text())
        self.assertEqual((report['baseline_rows'], report['collected_rows'], report['new_rows'],
                          report['seed']['rows']), (2, 3, 2, 4))
        self.assertEqual([(row['hash'], row['sources']) for row in report['mapping']],
                         [(84, ['exterior']), (126, ['exterior', 'interior']), (168, ['interior'])])
        self.assertEqual([row['classification'] for row in report['rows']], ['generated/exercised'] * 2)
        self.assertFalse(report['physical_verification'])
        self.assertEqual(report['manifest_sha256'], hashlib.sha256(self.manifest.read_bytes()).hexdigest())
        self.assertEqual({p: p.read_bytes() for p in before}, before)
        first = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}
        self.output = self.root / 'repeat'
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({p.relative_to(self.output): p.read_bytes()
                          for p in self.output.rglob('*') if p.is_file()}, first)

    def test_shared_unsupported_and_missing_rows_remain_explicit_gaps(self):
        self.rows.extend([
            {**self.rows[0], 'id': 'alternate', 'action': 'shared', 'shared_with': 'exterior',
             'justification': 'Same archive member and stock state in alternate mode.',
             'dimensions': {**self.rows[0]['dimensions'], 'mode': ['alternate']}},
            {**self.rows[0], 'id': 'skinned', 'action': 'unsupported',
             'reason': 'Actor animation prerequisites need follow-up.'},
            {**self.rows[0], 'id': 'unavailable', 'action': 'missing',
             'reason': 'No executable stock-state exercise is available.'}])
        self.save_manifest()
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'batch-report.json').read_text())
        self.assertEqual({row['id']: row['classification'] for row in report['rows']},
                         {'alternate': 'shared', 'exterior': 'generated/exercised',
                          'interior': 'generated/exercised', 'skinned': 'unsupported', 'unavailable': 'missing'})
        self.assertEqual(report['mapping'][0]['sources'], ['alternate', 'exterior'])
        self.assertFalse(report['inventory_complete'])
        self.assertEqual(report['residual_gaps'], ['skinned', 'unavailable'])

    def test_invalid_manifest_or_unjustified_sharing_never_publishes_a_seed(self):
        original = json.dumps(self.document)
        for defect in ['duplicate-id', 'path-escape', 'no-exclusions', 'no-dimensions',
                       'unknown-action', 'unsupported-loader', 'sharing-cycle', 'different-shared-input', 'different-shared-state']:
            with self.subTest(defect=defect):
                self.document = json.loads(original)
                rows = self.document['rows']
                if defect == 'duplicate-id':
                    rows[1]['id'] = rows[0]['id']
                elif defect == 'path-escape':
                    rows[0]['id'] = '../outside'
                elif defect == 'no-exclusions':
                    self.document['dynamic_exclusions'] = []
                elif defect == 'no-dimensions':
                    del rows[0]['dimensions']
                elif defect == 'unknown-action':
                    rows[0]['action'] = 'verified'
                elif defect == 'unsupported-loader':
                    rows[0]['resource'] = '/res/Object/Always.arc:bmd/model.bmd'
                else:
                    rows[1].update(action='shared', shared_with='exterior', justification='Synthetic alias')
                    if defect == 'sharing-cycle':
                        rows[0].update(action='shared', shared_with='interior', justification='Synthetic cycle')
                    elif defect == 'different-shared-input':
                        rows[1]['input_identity']['model_sha256'] = '0' * 64
                    else:
                        rows[1]['dimensions']['state'] = ['animated']
                self.save_manifest()
                result = self.prepare()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.output.exists())
                self.assertNotIn('Traceback', result.stderr)

    def test_batch_rejects_wrong_attribution_and_cross_resource_conflicts(self):
        path = self.collections / 'interior/collection.json'
        original = path.read_bytes()
        for defect in ['image_sha256', 'collector', 'contract_sha256', 'resources', 'resource', 'conflict']:
            with self.subTest(defect=defect):
                metadata = json.loads(original)
                if defect == 'conflict':
                    seed = path.parent / 'assets/initial_pipeline_cache.db'
                    with closing(sqlite3.connect(seed)) as db, db:
                        db.execute("UPDATE pipeline_cache SET config=X'0500000000010100' WHERE hash=126")
                    sha = hashlib.sha256(seed.read_bytes()).hexdigest()
                    asset = path.parent / 'assets/pipeline-seed.json'
                    document = json.loads(asset.read_text())
                    document['sha256'] = sha
                    asset.write_text(json.dumps(document))
                    metadata['seed_sha256'] = sha
                else:
                    metadata[defect] = {} if defect in ['collector', 'resources'] else '0' * 64
                path.write_text(json.dumps(metadata))
                before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
                result = self.prepare()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.output.exists())
                self.assertNotIn('Traceback', result.stderr)
                self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_malformed_incompatible_or_absent_collection_never_publishes_partial_output(self):
        collection = self.collections / 'interior'
        original = {p: p.read_bytes() for p in collection.rglob('*') if p.is_file()}
        for defect in ['malformed', 'no-draw', 'incompatible', 'absent']:
            with self.subTest(defect=defect):
                for path, data in original.items():
                    path.write_bytes(data)
                metadata = collection / 'collection.json'
                if defect == 'malformed':
                    metadata.write_text('[]')
                elif defect == 'no-draw':
                    document = json.loads(metadata.read_text())
                    document['draw_calls'] = 0
                    metadata.write_text(json.dumps(document))
                elif defect == 'absent':
                    metadata.unlink()
                else:
                    seed = collection / 'assets/initial_pipeline_cache.db'
                    with closing(sqlite3.connect(seed)) as db, db:
                        db.execute('UPDATE pipeline_cache SET type=2 WHERE hash=168')
                    asset = collection / 'assets/pipeline-seed.json'
                    document = json.loads(asset.read_text())
                    document['sha256'] = hashlib.sha256(seed.read_bytes()).hexdigest()
                    asset.write_text(json.dumps(document))
                result = self.prepare()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.output.exists())
                self.assertNotIn('Traceback', result.stderr)

    def test_existing_output_and_nested_output_are_preserved(self):
        self.output.mkdir()
        marker = self.output / 'previous-result'
        marker.write_text('retain')
        self.assertNotEqual(self.prepare().returncode, 0)
        self.assertEqual(marker.read_text(), 'retain')
        self.output = self.collections / 'nested'
        self.assertNotEqual(self.prepare().returncode, 0)
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
