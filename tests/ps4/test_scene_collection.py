"""Public fixed-scene collection/seed interface, using no game content."""
import json
import hashlib
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing

from synthetic_pipeline import make_seed
from synthetic_scene import make_scene_collection


CLI = Path(__file__).resolve().parents[2] / 'tools/pswaker/collect-model-seed.py'


class SceneBatchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.baseline = self.root / 'baseline'
        make_seed(self.baseline)
        self.collections = self.root / 'collections'
        self.output = self.root / 'prepared'
        self.manifest = self.root / 'manifest.json'
        rows = []
        for name, ocean, keys in [('ocean', True, (84, 126)), ('shadow', False, (126, 168))]:
            metadata = make_scene_collection(self.collections / name, ocean=ocean, keys=keys)
            rows.append({'id': name, 'family': name, 'action': 'exercise',
                         'scenario': metadata['scenario'], 'resource': metadata['resource'],
                         'script': metadata['script'], 'input_identity': metadata['resources'],
                         'source_references': ['synthetic/scene.cpp:draw'],
                         'assumptions': ['Isolated draw state; no physical observation.']})
        self.document = {'schema': 1, 'kind': 'environment-scenes', 'id': 'synthetic-scene-v1',
                         'image_sha256': 'c' * 64, 'contract_sha256': 'f' * 64,
                         'collector': metadata['collector'], 'exclusions': ['Other scene controllers.'],
                         'rows': rows}
        self.manifest.write_text(json.dumps(self.document))

    def prepare(self):
        return subprocess.run([sys.executable, str(CLI), 'prepare-batch', '--manifest', str(self.manifest),
                               '--collections', str(self.collections), '--baseline', str(self.baseline),
                               '--output', str(self.output)], capture_output=True, text=True)

    def test_scene_batch_maps_states_layouts_and_deduplicates_repeatably_without_changing_inputs(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'batch-report.json').read_text())
        self.assertEqual(report['provenance'], 'environment-scene-batch')
        self.assertEqual((report['baseline_rows'], report['collected_rows'], report['new_rows'], report['seed']['rows']),
                         (2, 3, 2, 4))
        self.assertEqual([(r['hash'], r['sources']) for r in report['mapping']],
                         [(84, ['ocean']), (126, ['ocean', 'shadow']), (168, ['shadow'])])
        ocean = json.loads((self.output / 'validated/ocean/collection-report.json').read_text())
        self.assertEqual(ocean['mapping'][0]['states'], [
            {'tick': 1, 'state': 'day', 'layout_keys': [16288162637680331091]},
            {'tick': 3, 'state': 'dense-fog', 'layout_keys': [16288162637680331091]},
            {'tick': 5, 'state': 'camera-raised', 'layout_keys': [16288162637680331091]}])
        self.assertFalse(report['physical_verification'])
        self.assertEqual({p: p.read_bytes() for p in before}, before)
        first = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}
        self.output = self.root / 'repeat'
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}, first)

    def test_bad_layout_mapping_rejects_the_whole_batch_without_publishing(self):
        path = self.collections / 'ocean/collection.json'
        metadata = json.loads(path.read_text())
        metadata['layout']['samples'] = True
        metadata['preparation_layouts'][0]['samples'] = True
        metadata['preparation_layouts'][1]['samples'] = True
        path.write_text(json.dumps(metadata))
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.prepare()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertFalse(self.output.exists())
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_unsupported_families_remain_gaps_without_generated_or_physical_claims(self):
        self.document['rows'].append({'id': 'real-shadows', 'family': 'shadows', 'action': 'unsupported',
                                      'reason': 'Needs collision receivers and caster capture.', 'owner': '#154 follow-up',
                                      'source_references': ['synthetic/shadow.cpp:imageDraw'],
                                      'assumptions': ['Simple shadow draws do not establish real shadow coverage.']})
        self.manifest.write_text(json.dumps(self.document))
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'batch-report.json').read_text())
        self.assertFalse(report['inventory_complete'])
        self.assertEqual(report['residual_gaps'], ['real-shadows'])
        self.assertEqual(report['rows'][1]['classification'], 'unsupported')
        self.assertFalse(report['rows'][1]['physical_verification'])

    def test_incomplete_or_incompatible_evidence_rejects_without_changing_inputs(self):
        original = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        for defect in ['oversized', 'duplicate', 'sharing', 'gap-without-owner', 'recipe', 'wrong-resource',
                       'wrong-input', 'missing-archive', 'extra-archive', 'wrong-contract', 'wrong-collector',
                       'missing-state', 'wrong-order', 'no-draw', 'unmapped', 'invented-key', 'boolean-key',
                       'wrong-method', 'unknown-scenario', 'missing-layout', 'wrong-layout', 'missing-offscreen',
                       'wrong-target', 'conflict', 'incompatible']:
            with self.subTest(defect=defect):
                for p, value in original.items():
                    p.write_bytes(value)
                document = json.loads(self.manifest.read_text())
                row = document['rows'][0]
                path = self.collections / 'ocean/collection.json'
                metadata = json.loads(path.read_text())
                if defect == 'oversized':
                    document['rows'] = [{**row, 'id': f'row-{i}'} for i in range(25)]
                elif defect == 'duplicate':
                    document['rows'][1]['id'] = 'ocean'
                elif defect == 'sharing':
                    row.update(action='shared', shared_with='shadow', justification='Same visual family')
                elif defect == 'gap-without-owner':
                    row.update(action='unsupported', reason=' ', owner=' ')
                elif defect == 'recipe':
                    row['script']['states'] = ['day']
                elif defect == 'wrong-resource':
                    metadata['resource'] = '/res/Object/System.arc'
                elif defect == 'wrong-input':
                    metadata['resources']['/res/Object/Always.arc']['sha256'] = '0' * 64
                elif defect == 'missing-archive':
                    row['input_identity'].pop('/res/Object/System.arc')
                elif defect == 'extra-archive':
                    row['input_identity']['/res/Object/Extra.arc'] = {'sha256': '0' * 64, 'bytes': 1}
                elif defect == 'wrong-contract':
                    metadata['contract_sha256'] = '0' * 64
                elif defect == 'wrong-collector':
                    metadata['collector']['sha256'] = '0' * 64
                elif defect == 'missing-state':
                    metadata['states'].pop()
                elif defect == 'wrong-order':
                    metadata['states'][1]['state'] = 'day'
                elif defect == 'no-draw':
                    metadata['states'][1]['draw_calls'] = 0
                elif defect == 'unmapped':
                    metadata['states'][0]['configurations'] = []
                elif defect == 'invented-key':
                    metadata['states'][0]['configurations'][0]['hash'] = 999
                elif defect == 'boolean-key':
                    metadata['states'][0]['configurations'][0]['type'] = False
                elif defect == 'wrong-method':
                    metadata['method'] = 'scripted-actor-draw'
                elif defect == 'unknown-scenario':
                    metadata['scenario'] = 'scene-unlisted-v1'
                elif defect == 'missing-layout':
                    metadata['states'][0].pop('layout_keys')
                elif defect == 'wrong-layout':
                    metadata['states'][0]['layout_keys'] = [999]
                elif defect == 'missing-offscreen':
                    metadata['preparation_layouts'].pop()
                elif defect == 'wrong-target':
                    metadata['layout']['width'] = 1920
                else:
                    seed = path.parent / 'assets/initial_pipeline_cache.db'
                    with closing(sqlite3.connect(seed)) as db, db:
                        db.execute("UPDATE pipeline_cache SET config=X'0500000000010100' WHERE hash=84"
                                   if defect == 'conflict' else 'UPDATE pipeline_cache SET type=2 WHERE hash=126')
                    asset = path.parent / 'assets/pipeline-seed.json'
                    value = json.loads(asset.read_text())
                    value['sha256'] = metadata['seed_sha256'] = hashlib.sha256(seed.read_bytes()).hexdigest()
                    asset.write_text(json.dumps(value))
                self.manifest.write_text(json.dumps(document))
                path.write_text(json.dumps(metadata))
                before = {p: p.read_bytes() for p in original}
                result = self.prepare()
                self.assertNotEqual(result.returncode, 0, defect)
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse(self.output.exists())
                self.assertEqual({p: p.read_bytes() for p in before}, before)


if __name__ == '__main__':
    unittest.main()
