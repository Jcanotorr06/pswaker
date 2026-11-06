"""Public equipment collection/seed boundary with data-free descriptions."""
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
from synthetic_equipment import make_equipment_collection


CLI = Path(__file__).resolve().parents[2] / 'tools/pswaker/collect-model-seed.py'


class EquipmentBatchTests(unittest.TestCase):
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
        for name, arrow, keys in [('arrow', True, (84, 126)), ('bomb', False, (126, 168))]:
            metadata = make_equipment_collection(self.collections / name, arrow=arrow, keys=keys)
            rows.append({'id': name, 'family': name, 'action': 'exercise',
                         'scenario': metadata['scenario'], 'resource': metadata['resource'],
                         'script': metadata['script'], 'input_identity': metadata['resources'],
                         'source_references': ['synthetic/equipment.cpp:draw'],
                         'assumptions': ['Isolated scripted state, no gameplay observation.']})
        self.document = {'schema': 1, 'kind': 'equipment-actions', 'id': 'synthetic-equipment-v1',
                         'image_sha256': 'c' * 64, 'contract_sha256': 'f' * 64,
                         'collector': metadata['collector'], 'exclusions': ['Other equipment controllers.'],
                         'rows': rows}
        self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.document))

    def prepare(self):
        return subprocess.run([sys.executable, str(CLI), 'prepare-batch', '--manifest', str(self.manifest),
                               '--collections', str(self.collections), '--baseline', str(self.baseline),
                               '--output', str(self.output)], capture_output=True, text=True)

    def test_mixed_state_and_effect_batch_preserves_maps_and_deduplicates_repeatably(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'batch-report.json').read_text())
        self.assertEqual(report['provenance'], 'equipment-action-batch')
        self.assertEqual((report['baseline_rows'], report['collected_rows'], report['new_rows'], report['seed']['rows']),
                         (2, 3, 2, 4))
        self.assertEqual([(r['hash'], r['sources']) for r in report['mapping']],
                         [(84, ['arrow']), (126, ['arrow', 'bomb']), (168, ['bomb'])])
        arrow = json.loads((self.output / 'validated/arrow/collection-report.json').read_text())
        self.assertEqual(arrow['mapping'][0]['states'], [{'tick': 1, 'state': 'normal'}, {'tick': 3, 'state': 'ice'}])
        self.assertFalse(report['physical_verification'])
        self.assertEqual({p: p.read_bytes() for p in before}, before)
        first = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}
        self.output = self.root / 'repeat'
        self.assertEqual(self.prepare().returncode, 0)
        self.assertEqual({p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}, first)

    def test_unsupported_families_survive_without_implying_generated_or_physical_coverage(self):
        self.document['rows'].append({'id': 'flight', 'family': 'arrow', 'action': 'unsupported',
                                      'reason': 'Needs player and collision controllers.', 'owner': '#152 follow-up',
                                      'source_references': ['synthetic/arrow.cpp:flight'],
                                      'assumptions': ['No flight coverage inferred from the tip model.']})
        self.save()
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'batch-report.json').read_text())
        self.assertFalse(report['inventory_complete'])
        self.assertEqual(report['residual_gaps'], ['flight'])
        self.assertEqual(report['rows'][-1]['classification'], 'unsupported')
        self.assertFalse(report['rows'][-1]['physical_verification'])

    def test_bad_setup_mapping_identity_and_seed_records_reject_without_publication(self):
        original = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        for defect in ['oversized', 'duplicate', 'sharing', 'recipe', 'wrong-resource', 'wrong-input',
                       'wrong-contract', 'wrong-collector', 'missing-state', 'wrong-order', 'no-draw',
                       'unmapped', 'invented-key', 'boolean-key', 'unfinished-effect', 'conflict', 'incompatible']:
            with self.subTest(defect=defect):
                for p, value in original.items():
                    p.write_bytes(value)
                self.document = json.loads(self.manifest.read_text())
                row = self.document['rows'][0]
                path = self.collections / 'arrow/collection.json'
                metadata = json.loads(path.read_text())
                if defect == 'oversized':
                    self.document['rows'] = [{**row, 'id': f'row-{i}'} for i in range(17)]
                elif defect == 'duplicate':
                    self.document['rows'][1]['id'] = 'arrow'
                elif defect == 'sharing':
                    row.update(action='shared', shared_with='bomb', justification='Same visual family')
                elif defect == 'recipe':
                    row['script']['states'] = ['normal']
                elif defect == 'wrong-resource':
                    metadata['resource'] = '/res/Object/Link.arc:bdlm/arrowglitter.bdl'
                elif defect == 'wrong-input':
                    metadata['resources']['model_sha256'] = '0' * 64
                elif defect == 'wrong-contract':
                    metadata['contract_sha256'] = '0' * 64
                elif defect == 'wrong-collector':
                    metadata['collector']['sha256'] = '0' * 64
                elif defect == 'missing-state':
                    metadata['states'].pop()
                elif defect == 'wrong-order':
                    metadata['states'][1]['state'] = 'ice'
                elif defect == 'no-draw':
                    metadata['states'][1]['draw_calls'] = 0
                elif defect == 'unmapped':
                    metadata['states'][0]['configurations'] = []
                elif defect == 'invented-key':
                    metadata['states'][0]['configurations'][0]['hash'] = 999
                elif defect == 'boolean-key':
                    metadata['states'][0]['configurations'][0]['type'] = False
                elif defect == 'unfinished-effect':
                    path = self.collections / 'bomb/collection.json'
                    metadata = json.loads(path.read_text())
                    metadata['variations'][0]['steps'][-1]['emitters'] = 1
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
