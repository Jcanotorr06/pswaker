"""Public enemy/boss collection-to-seed boundary with data-free descriptions."""
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing

from synthetic_pipeline import make_seed
from synthetic_enemy import make_enemy_collection


CLI = Path(__file__).resolve().parents[2] / 'tools/pswaker/collect-model-seed.py'


class EnemyBatchTests(unittest.TestCase):
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
        for name, actor, keys in [('peahat', True, (84, 126)), ('death', False, (126, 168))]:
            metadata = make_enemy_collection(self.collections / name, actor=actor, keys=keys)
            rows.append({'id': name, 'family': name, 'action': 'exercise',
                         'scenario': metadata['scenario'], 'resource': metadata['resource'],
                         'script': metadata['script'], 'input_identity': metadata['resources'],
                         'source_references': ['synthetic/enemy.cpp:draw'],
                         'assumptions': ['Isolated scripted state, no gameplay observation.']})
        self.document = {'schema': 1, 'kind': 'enemy-actors', 'id': 'synthetic-enemy-v1',
                         'image_sha256': 'c' * 64, 'contract_sha256': 'f' * 64,
                         'collector': metadata['collector'], 'exclusions': ['Other enemy and boss actors.'],
                         'rows': rows}
        self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.document))

    def prepare(self):
        return subprocess.run([sys.executable, str(CLI), 'prepare-batch', '--manifest', str(self.manifest),
                               '--collections', str(self.collections), '--baseline', str(self.baseline),
                               '--output', str(self.output)], capture_output=True, text=True)

    def test_mixed_actor_and_effect_batch_preserves_maps_and_deduplicates_repeatably(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'batch-report.json').read_text())
        self.assertEqual(report['provenance'], 'enemy-actor-batch')
        self.assertEqual((report['baseline_rows'], report['collected_rows'], report['new_rows'], report['seed']['rows']),
                         (2, 3, 2, 4))
        self.assertEqual([(r['hash'], r['sources']) for r in report['mapping']],
                         [(84, ['peahat']), (126, ['death', 'peahat']), (168, ['death'])])
        peahat = json.loads((self.output / 'validated/peahat/collection-report.json').read_text())
        self.assertEqual(peahat['mapping'][0]['states'],
                         [{'tick': 1, 'state': 'stock'}, {'tick': 3, 'state': 'restored'}])
        self.assertFalse(report['physical_verification'])
        self.assertEqual({p: p.read_bytes() for p in before}, before)
        first = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}
        self.output = self.root / 'repeat'
        self.assertEqual(self.prepare().returncode, 0)
        self.assertEqual({p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}, first)

    def test_oversized_families_survive_without_implying_generated_or_physical_coverage(self):
        self.document['rows'].append({'id': 'phantom-ganon', 'family': 'boss', 'action': 'unsupported',
                                      'reason': 'Needs its own phase controller.', 'owner': '#153 follow-up',
                                      'source_references': ['synthetic/boss.cpp:phase'],
                                      'assumptions': ['No phase coverage inferred from shared effects.']})
        self.save()
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'batch-report.json').read_text())
        self.assertFalse(report['inventory_complete'])
        self.assertEqual(report['residual_gaps'], ['phantom-ganon'])
        self.assertEqual(report['rows'][-1]['classification'], 'unsupported')
        self.assertFalse(report['rows'][-1]['physical_verification'])

    def test_bad_setup_mapping_identity_and_seed_records_reject_without_publication(self):
        original = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        for defect in ['oversized', 'duplicate', 'sharing', 'unsupported-gap', 'recipe', 'wrong-resource', 'wrong-input',
                       'missing-companion', 'extra-companion', 'wrong-companion', 'wrong-contract', 'wrong-collector',
                       'missing-state', 'wrong-order', 'no-draw', 'unmapped', 'invented-key', 'boolean-key',
                       'wrong-method', 'unfinished-effect', 'unknown-scenario', 'conflict', 'incompatible']:
            with self.subTest(defect=defect):
                for p, value in original.items():
                    p.write_bytes(value)
                self.document = json.loads(self.manifest.read_text())
                row = self.document['rows'][0]
                path = self.collections / 'peahat/collection.json'
                metadata = json.loads(path.read_text())
                if defect == 'oversized':
                    self.document['rows'] = [{**row, 'id': f'row-{i}'} for i in range(33)]
                elif defect == 'duplicate':
                    self.document['rows'][1]['id'] = 'peahat'
                elif defect == 'sharing':
                    row.update(action='shared', shared_with='death', justification='Same visual family')
                elif defect == 'unsupported-gap':
                    row.update(action='unsupported', reason=' ', owner=' ')
                elif defect == 'recipe':
                    row['script']['states'] = ['stock']
                elif defect == 'wrong-resource':
                    metadata['resource'] = '/res/Object/Ph.arc:bdlm/php.bdl'
                elif defect == 'wrong-input':
                    metadata['resources']['model_sha256'] = '0' * 64
                elif defect == 'missing-companion':
                    metadata['resources']['companions'].pop('/res/Object/Ph.arc:bdlm/php.bdl')
                    row['input_identity'] = metadata['resources']
                elif defect == 'extra-companion':
                    metadata['resources']['companions']['/res/Object/Ph.arc:bdlm/other.bdl'] = {'sha256': 'b' * 64, 'bytes': 10}
                    row['input_identity'] = metadata['resources']
                elif defect == 'wrong-companion':
                    metadata['resources']['companions']['/res/Object/System.arc:dat/toon.bti']['sha256'] = '0' * 64
                elif defect == 'wrong-contract':
                    metadata['contract_sha256'] = '0' * 64
                elif defect == 'wrong-collector':
                    metadata['collector']['sha256'] = '0' * 64
                elif defect == 'missing-state':
                    metadata['states'].pop()
                elif defect == 'wrong-order':
                    metadata['states'][1]['state'] = 'restored'
                elif defect == 'no-draw':
                    metadata['states'][1]['draw_calls'] = 0
                elif defect == 'unmapped':
                    metadata['states'][0]['configurations'] = []
                elif defect == 'invented-key':
                    metadata['states'][0]['configurations'][0]['hash'] = 999
                elif defect == 'boolean-key':
                    metadata['states'][0]['configurations'][0]['type'] = False
                elif defect == 'wrong-method':
                    metadata['method'] = 'scripted-equipment-draw'
                elif defect == 'unfinished-effect':
                    path = self.collections / 'death/collection.json'
                    metadata = json.loads(path.read_text())
                    metadata['variations'][0]['steps'][-1]['emitters'] = 1
                elif defect == 'unknown-scenario':
                    metadata['scenario'] = 'enemy-unlisted-v1'
                else:
                    seed = path.parent / 'assets/initial_pipeline_cache.db'
                    with closing(sqlite3.connect(seed)) as db, db:
                        db.execute("UPDATE pipeline_cache SET config=X'0500000000010100' WHERE hash=84"
                                   if defect == 'conflict' else 'UPDATE pipeline_cache SET type=2 WHERE hash=126')
                    asset = path.parent / 'assets/pipeline-seed.json'
                    value = json.loads(asset.read_text())
                    value['sha256'] = metadata['seed_sha256'] = hashlib.sha256(seed.read_bytes()).hexdigest()
                    asset.write_text(json.dumps(value))
                self.save()
                path.write_text(json.dumps(metadata))
                before = {p: p.read_bytes() for p in original}
                result = self.prepare()
                self.assertNotEqual(result.returncode, 0, defect)
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse(self.output.exists())
                self.assertEqual({p: p.read_bytes() for p in before}, before)


if __name__ == '__main__':
    unittest.main()
