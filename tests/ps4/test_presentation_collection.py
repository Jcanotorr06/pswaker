"""Public fixed-presentation collection/seed interface, using no game content."""
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
from synthetic_presentation import make_presentation_collection


CLI = Path(__file__).resolve().parents[2] / 'tools/pswaker/collect-model-seed.py'


class PresentationBatchTests(unittest.TestCase):
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
        for name, menu, keys in [('menu', True, (84, 126)), ('fade', False, (126, 168))]:
            metadata = make_presentation_collection(self.collections / name, menu=menu, keys=keys)
            rows.append({'id': name, 'family': name, 'action': 'exercise',
                         'scenario': metadata['scenario'], 'resource': metadata['resource'],
                         'script': metadata['script'], 'input_identity': metadata['resources'],
                         'source_references': ['synthetic/presentation.cpp:draw'],
                         'assumptions': ['Isolated draw state; no physical observation.']})
        self.document = {'schema': 1, 'kind': 'menu-cutscene-modes', 'id': 'synthetic-presentation-v1',
                         'image_sha256': 'c' * 64, 'contract_sha256': 'f' * 64,
                         'collector': metadata['collector'], 'exclusions': ['Other presentation controllers.'],
                         'rows': rows}
        self.manifest.write_text(json.dumps(self.document))

    def prepare(self):
        return subprocess.run([sys.executable, str(CLI), 'prepare-batch', '--manifest', str(self.manifest),
                               '--collections', str(self.collections), '--baseline', str(self.baseline),
                               '--output', str(self.output)], capture_output=True, text=True)

    def test_presentation_batch_maps_states_layouts_and_deduplicates_repeatably_without_changing_inputs(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'batch-report.json').read_text())
        self.assertEqual(report['provenance'], 'presentation-variation-batch')
        self.assertEqual((report['baseline_rows'], report['collected_rows'], report['new_rows'], report['seed']['rows']),
                         (2, 3, 2, 4))
        self.assertEqual([(r['hash'], r['sources']) for r in report['mapping']],
                         [(84, ['menu']), (126, ['fade', 'menu']), (168, ['fade'])])
        menu = json.loads((self.output / 'validated/menu/collection-report.json').read_text())
        self.assertEqual(menu['mapping'][0]['states'], [
            {'tick': 1, 'state': 'plain', 'layout_keys': [16288162637680331091]},
            {'tick': 3, 'state': 'faded', 'layout_keys': [16288162637680331091]}])
        self.assertFalse(report['physical_verification'])
        self.assertEqual({p: p.read_bytes() for p in before}, before)
        first = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}
        self.output = self.root / 'repeat'
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}, first)

    def test_bad_layout_mapping_rejects_the_whole_batch_without_publishing(self):
        path = self.collections / 'menu/collection.json'
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

    def test_equivalent_context_requires_the_same_exercised_setup_and_explicit_justification(self):
        equivalent = {**self.document['rows'][0], 'id': 'file-tint-equivalent', 'action': 'shared',
                      'shared_with': 'menu', 'owner': '#155',
                      'justification': 'Only the same J2DPicture tint setup; not the entire file menu.'}
        self.document['rows'].append(equivalent)
        self.manifest.write_text(json.dumps(self.document))
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'batch-report.json').read_text())
        row = next(row for row in report['rows'] if row['id'] == 'file-tint-equivalent')
        self.assertEqual(row['classification'], 'shared')
        self.assertEqual(row['evidence'], 'validated/menu/collection-report.json')
        self.assertFalse(row['physical_verification'])
        self.assertEqual(report['seed']['rows'], 4)

    def test_alternate_clothes_maps_the_restore_state_and_binds_its_extra_archive(self):
        metadata = make_presentation_collection(self.collections / 'clothes', clothes=True, keys=(84, 126))
        self.document['rows'] = [{**self.document['rows'][0], 'id': 'clothes', 'family': 'mode',
                                  'scenario': metadata['scenario'], 'script': metadata['script'],
                                  'input_identity': metadata['resources']}]
        self.manifest.write_text(json.dumps(self.document))
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'validated/clothes/collection-report.json').read_text())
        self.assertEqual(report['mapping'][0]['states'], [
            {'tick': 1, 'state': 'hero', 'layout_keys': [16288162637680331091]},
            {'tick': 3, 'state': 'hero-repeated', 'layout_keys': [16288162637680331091]}])
        self.assertIn('/res/Object/Link.arc', report['collection']['resources'])

    def test_equivalence_rejects_unjustified_or_different_setups_without_publication(self):
        for defect in ['target', 'target-type', 'chain', 'scenario', 'identity', 'justification', 'owner']:
            with self.subTest(defect=defect):
                shared = {**self.document['rows'][0], 'id': 'equivalent', 'action': 'shared',
                          'shared_with': 'menu', 'owner': '#155', 'justification': 'Only this exact tint setup.'}
                if defect == 'target':
                    shared['shared_with'] = 'unknown'
                elif defect == 'target-type':
                    shared['shared_with'] = []
                elif defect == 'chain':
                    shared['shared_with'] = 'equivalent'
                elif defect == 'scenario':
                    shared.update(scenario='cutscene-fade-v1', script=self.document['rows'][1]['script'])
                elif defect == 'identity':
                    shared['input_identity'] = {**shared['input_identity'], '/res/Msg/clctres.arc': {'sha256': 'a' * 64, 'bytes': 100}}
                else:
                    shared[defect] = ' '
                self.manifest.write_text(json.dumps({**self.document, 'rows': [*self.document['rows'], shared]}))
                result = self.prepare()
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse(self.output.exists())

    def test_unsupported_and_missing_paths_remain_gaps_without_generated_or_physical_claims(self):
        gap = {'id': 'menu-capture', 'family': 'menu', 'action': 'unsupported',
                                      'reason': 'Needs framebuffer capture and a menu controller.', 'owner': '#155 follow-up',
                                      'source_references': ['synthetic/menu.cpp:capture'],
                                      'assumptions': ['Picture draws do not establish menu capture coverage.']}
        self.document['rows'].extend([gap, {**gap, 'id': 'ending', 'family': 'cutscene', 'action': 'missing',
                                            'reason': 'No bounded one-time ending setup is available.'}])
        self.manifest.write_text(json.dumps(self.document))
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'batch-report.json').read_text())
        self.assertFalse(report['inventory_complete'])
        self.assertEqual(report['residual_gaps'], ['ending', 'menu-capture'])
        by_id = {row['id']: row for row in report['rows']}
        for identifier, classification in [('ending', 'missing'), ('menu-capture', 'unsupported')]:
            self.assertEqual(by_id[identifier]['classification'], classification)
            self.assertFalse(by_id[identifier]['physical_verification'])
            self.assertNotIn('evidence', by_id[identifier])

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
                path = self.collections / 'menu/collection.json'
                metadata = json.loads(path.read_text())
                if defect == 'oversized':
                    document['rows'] = [{**row, 'id': f'row-{i}'} for i in range(25)]
                elif defect == 'duplicate':
                    document['rows'][1]['id'] = 'menu'
                elif defect == 'sharing':
                    row.update(action='shared', shared_with='fade', justification='Same visual family')
                elif defect == 'gap-without-owner':
                    row.update(action='unsupported', reason=' ', owner=' ')
                elif defect == 'recipe':
                    row['script']['states'] = ['plain']
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
                    metadata['states'][1]['state'] = 'plain'
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
                    metadata['scenario'] = 'presentation-unlisted-v1'
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
