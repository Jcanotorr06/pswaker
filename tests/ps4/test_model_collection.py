"""Public collection-to-seed boundary, with synthetic descriptions only."""
import json
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil
import unittest

from synthetic_pipeline import make_seed, make_model_collection, make_dynamic_collection, make_particle_collection
from synthetic_disc import generate
from synthetic_model_collector import add_model_resource, make_collector, MODEL_BYTES, PARTICLE_BYTES
from synthetic_equipment import make_equipment_collection
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
        self.scenario = []
        self.root.joinpath('settings.ini').write_text('owner settings sentinel')

    def collect(self):
        return subprocess.run([sys.executable, str(self.cli), 'collect', '--collector', str(self.collector),
                               '--image', str(self.image), '--baseline', str(self.baseline),
                               '--output', str(self.output), *self.scenario], capture_output=True, text=True)

    def test_dynamic_command_repeats_resource_attribution_and_lifetime_mapping(self):
        shutil.rmtree(self.collector)
        make_collector(self.collector, dynamic=True)
        self.scenario = ['--scenario', 'common-pot-debris-lifecycle-v1']
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        result = self.collect()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'collection.json').read_text())
        self.assertEqual(report['resources']['particle_sha256'], hashlib.sha256(PARTICLE_BYTES).hexdigest())
        self.assertEqual(report['method'], 'dynamic-effect-draw')
        self.assertEqual(report['commands'][0][-1], 'common-pot-debris-lifecycle-v1')
        self.output = self.root / 'dynamic-repeat'
        self.assertEqual(self.collect().returncode, 0)
        repeated = json.loads((self.output / 'collection.json').read_text())
        for name in ['seed_sha256', 'variations', 'collector', 'resources', 'script']:
            self.assertEqual(repeated[name], report[name])
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_particle_batch_freezes_inputs_and_runs_the_requested_overlap(self):
        fixture = self.root / 'particle-fixture'
        metadata = make_particle_collection(fixture, '/res/Particle/common.jpc:0x000b+0x2009', (84,))
        metadata['runtime_identity_verified_rows'] = 3
        (self.collector / 'native-report.json').write_text(json.dumps(metadata))
        row = {'id': 'overlap', 'family': 'bomb', 'resource': metadata['resource'],
               'script': metadata['script'], 'source_references': ['synthetic.cpp:explode'],
               'action': 'exercise', 'assumptions': ['Synthetic overlap.']}
        plan = self.root / 'plan.json'
        plan.write_text(json.dumps({'schema': 1, 'id': 'synthetic-particles-v1', 'kind': 'particle-effects',
                                    'exclusions': ['Scene effects excluded.'], 'rows': [row]}))
        manifest = self.root / 'manifest.json'
        command = [sys.executable, str(self.cli), 'freeze-inventory', '--plan', str(plan),
                   '--collector', str(self.collector), '--image', str(self.image)]
        result = subprocess.run(command + ['--output', str(manifest)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run(command + ['--output', str(self.root / 'repeat-manifest.json')],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(manifest.read_bytes(), (self.root / 'repeat-manifest.json').read_bytes())
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        result = subprocess.run([sys.executable, str(self.cli), 'batch', '--manifest', str(manifest),
                                 '--collector', str(self.collector), '--image', str(self.image),
                                 '--baseline', str(self.baseline), '--output', str(self.output)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'prepared/batch-report.json').read_text())
        self.assertEqual((report['collected_rows'], report['new_rows']), (1, 0))
        collected = report['rows'][0]
        self.assertEqual(collected['input_identity']['particle_sha256'], hashlib.sha256(PARTICLE_BYTES).hexdigest())
        self.assertEqual(collected['script']['effect_ids'], [11, 8201])
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_equipment_freeze_and_batch_dispatch_real_process_arguments_and_preserve_inputs(self):
        # The stand-in rejects wrong scenario/resource arguments. Native rendering
        # is separately exercised with private inputs, not simulated by this test.
        for arrow in [True, False]:
            with self.subTest(arrow=arrow):
                if arrow:
                    _, self.image = generate(self.root, CLI.parents[2])
                    add_model_resource(self.image, self.root / 'repo/platform/ps4/content-contract.json', arrow=True)
                metadata = make_equipment_collection(self.root / ('arrow-fixture' if arrow else 'bomb-fixture'),
                                                     arrow=arrow, keys=(84,))
                metadata['runtime_identity_verified_rows'] = 3
                (self.collector / 'native-report.json').write_text(json.dumps(metadata))
                name = 'arrow' if arrow else 'bomb'
                row = {'id': name, 'family': name, 'scenario': metadata['scenario'], 'resource': metadata['resource'],
                       'script': metadata['script'], 'source_references': ['synthetic.cpp:draw'],
                       'action': 'exercise', 'assumptions': ['Synthetic equipment process boundary.']}
                plan = self.root / (name + '-plan.json')
                plan.write_text(json.dumps({'schema': 1, 'id': 'synthetic-equipment-v1', 'kind': 'equipment-actions',
                                            'exclusions': ['Other equipment excluded.'], 'rows': [row]}))
                manifest = self.root / (name + '-manifest.json')
                command = [sys.executable, str(self.cli), 'freeze-inventory', '--plan', str(plan),
                           '--collector', str(self.collector), '--image', str(self.image)]
                result = subprocess.run(command + ['--output', str(manifest)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                repeat = self.root / (name + '-repeat.json')
                result = subprocess.run(command + ['--output', str(repeat)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(manifest.read_bytes(), repeat.read_bytes())
                before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
                output = self.root / (name + '-batch')
                result = subprocess.run([sys.executable, str(self.cli), 'batch', '--manifest', str(manifest),
                                         '--collector', str(self.collector), '--image', str(self.image),
                                         '--baseline', str(self.baseline), '--output', str(output)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads((output / 'prepared/batch-report.json').read_text())
                self.assertEqual((report['collected_rows'], report['new_rows']), (1, 0))
                for filename in ['initial_pipeline_cache.db', 'pipeline-seed.json']:
                    self.assertEqual((output / 'prepared/assets' / filename).read_bytes(), (self.baseline / filename).read_bytes())
                native = json.loads((output / f'collections/{name}/collection.json').read_text())
                self.assertEqual(native['commands'][0][-2:], [metadata['scenario'], metadata['resource']])
                identity = native['resources']
                self.assertEqual(identity['model_sha256' if arrow else 'particle_sha256'],
                                 hashlib.sha256(MODEL_BYTES if arrow else PARTICLE_BYTES).hexdigest())
                self.assertEqual({p: p.read_bytes() for p in before}, before)

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

    def test_inventory_resource_is_exercised_and_bound_to_its_requested_path(self):
        path = self.collector / 'native-report.json'
        report = json.loads(path.read_text())
        report.update(scenario='asset-model-stock-v1', frames=3, loader_flags=8224,
                      model_flags=0, differed_display_list_flags=285212804)
        path.write_text(json.dumps(report))
        self.scenario = ['--scenario', 'asset-model-stock-v1',
                         '--resource', '/res/Object/Always.arc:bdl/obm_kotubo1.bdl']
        result = self.collect()
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads((self.output / 'collection.json').read_text())
        self.assertEqual(metadata['resource'], '/res/Object/Always.arc:bdl/obm_kotubo1.bdl')
        self.assertEqual(metadata['commands'][0][-2:],
                         ['asset-model-stock-v1', '/res/Object/Always.arc:bdl/obm_kotubo1.bdl'])
        (self.collector / 'mode').write_text('wrong-resource')
        self.output = self.root / 'wrong-resource'
        result = self.collect()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('different resource', result.stderr)

    def test_batch_runs_exercises_and_retains_shared_source_mapping(self):
        metadata_path = self.collector / 'native-report.json'
        metadata = json.loads(metadata_path.read_text())
        metadata.update(scenario='asset-model-stock-v1', frames=3, loader_flags=8224,
                        model_flags=0, differed_display_list_flags=285212804)
        metadata_path.write_text(json.dumps(metadata))
        build = json.loads((self.collector / 'collector-build.json').read_text())
        identity = {'archive_sha256': hashlib.sha256(self.image.read_bytes()[
            0x5000:0x5000 + 0x100 + len(MODEL_BYTES)]).hexdigest(),
                    'model_sha256': hashlib.sha256(MODEL_BYTES).hexdigest(), 'model_bytes': len(MODEL_BYTES)}
        row = {'id': 'exterior', 'family': 'synthetic', 'resource': metadata['resource'],
               'input_identity': identity, 'source_references': ['synthetic.cpp:draw'],
               'dimensions': {'content': ['test-island'], 'mode': ['normal'], 'state': ['stock-bdl-v1']},
               'action': 'exercise', 'assumptions': ['No actor lighting or animation.']}
        manifest = self.root / 'inventory.json'
        manifest.write_text(json.dumps({'schema': 1, 'id': 'synthetic-v1',
            'image_sha256': hashlib.sha256(self.image.read_bytes()).hexdigest(),
            'contract_sha256': build['contract_sha256'],
            'collector': {'sha256': build['binary_sha256'],
                          'build_sha256': hashlib.sha256((self.collector / 'collector-build.json').read_bytes()).hexdigest()},
            'dynamic_exclusions': [{'id': 'lighting', 'owner': '#151', 'reason': 'Separate dynamic exercise'}],
            'rows': [row, {**row, 'id': 'alternate', 'action': 'shared', 'shared_with': 'exterior',
                           'justification': 'Same immutable source and stock state.'}]}))
        result = subprocess.run([sys.executable, str(self.cli), 'batch', '--manifest', str(manifest),
                                 '--collector', str(self.collector), '--image', str(self.image),
                                 '--baseline', str(self.baseline), '--output', str(self.output)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'prepared/batch-report.json').read_text())
        self.assertEqual((report['collected_rows'], report['new_rows'], report['seed']['rows']), (1, 0, 3))
        self.assertEqual(report['mapping'][0]['sources'], ['alternate', 'exterior'])
        self.assertFalse((self.output / 'collections/alternate').exists())
        for name in ['initial_pipeline_cache.db', 'pipeline-seed.json']:
            self.assertEqual((self.output / 'prepared/assets' / name).read_bytes(), (self.baseline / name).read_bytes())

    def test_inventory_freeze_binds_resources_image_and_collector_repeatably(self):
        plan = self.root / 'plan.json'
        plan.write_text(json.dumps({'schema': 1, 'id': 'synthetic-freeze-v1',
            'dynamic_exclusions': [{'id': 'lighting', 'owner': '#151', 'reason': 'Dynamic exercise'}],
            'rows': [{'id': 'synthetic-pot', 'family': 'synthetic',
                      'resource': '/res/Object/Always.arc:bdl/obm_kotubo1.bdl',
                      'source_references': ['synthetic.cpp:draw'], 'action': 'exercise',
                      'dimensions': {'content': ['synthetic'], 'mode': ['normal'], 'state': ['stock-bdl-v1']},
                      'assumptions': ['Stock draw only.']}]}))
        outputs = [self.root / 'frozen-a.json', self.root / 'frozen-b.json']
        for output in outputs:
            result = subprocess.run([sys.executable, str(self.cli), 'freeze-inventory', '--plan', str(plan),
                                     '--collector', str(self.collector), '--image', str(self.image),
                                     '--output', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(outputs[0].read_bytes(), outputs[1].read_bytes())
        manifest = json.loads(outputs[0].read_text())
        self.assertEqual(manifest['image_sha256'], hashlib.sha256(self.image.read_bytes()).hexdigest())
        self.assertEqual(manifest['rows'][0]['input_identity']['model_sha256'], hashlib.sha256(MODEL_BYTES).hexdigest())
        self.assertEqual(manifest['plan_sha256'], hashlib.sha256(plan.read_bytes()).hexdigest())

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

    def test_dynamic_lifetime_maps_each_variation_to_combined_description_bytes(self):
        shutil.rmtree(self.collection)
        make_dynamic_collection(self.collection)
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'collection-report.json').read_text())
        self.assertEqual(report['provenance'], 'dynamic-effect-draw')
        self.assertEqual((report['baseline_rows'], report['collected_rows'],
                          report['baseline_covered_rows'], report['new_rows'], report['seed']['rows']),
                         (2, 2, 1, 1, 3))
        self.assertEqual([(row['hash'], row['states']) for row in report['mapping']], [
            (84, [{'texture_index': 0, 'ticks': [1, 2]}]),
            (126, [{'texture_index': 1, 'ticks': [1, 2]}])])
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_dynamic_export_requires_completed_lifetimes_and_exact_state_mapping(self):
        shutil.rmtree(self.collection)
        original = make_dynamic_collection(self.collection)
        path = self.collection / 'collection.json'
        for defect in ['no-particles', 'not-retired', 'skipped-tick', 'wrong-variation',
                       'unmapped-description', 'invented-description', 'no-draw', 'wrong-total']:
            with self.subTest(defect=defect):
                self.output = self.root / defect
                metadata = json.loads(json.dumps(original))
                steps = metadata['variations'][0]['steps']
                if defect == 'no-particles':
                    for step in steps:
                        step['particles'] = 0
                elif defect == 'not-retired':
                    steps[-1]['emitters'] = 1
                elif defect == 'skipped-tick':
                    steps[1]['tick'] = 5
                elif defect == 'wrong-variation':
                    metadata['variations'][1]['texture_index'] = 0
                elif defect == 'unmapped-description':
                    for step in steps:
                        step['configurations'] = []
                elif defect == 'invented-description':
                    steps[0]['configurations'].append({'type': 0, 'hash': 999})
                elif defect == 'no-draw':
                    metadata['draw_calls'] = 0
                else:
                    metadata['pipeline_lookups'] = 99
                path.write_text(json.dumps(metadata))
                result = self.prepare()
                self.assertNotEqual(result.returncode, 0, defect)
                self.assertIn('dynamic', result.stderr)
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse(self.output.exists())

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


class RuntimeCorrectionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.baseline = self.root / 'baseline'
        self.cold = self.root / 'cold'
        self.warm = self.root / 'warm'
        self.output = self.root / 'corrected'
        make_seed(self.baseline, keys=(42, 84))
        make_seed(self.cold, keys=(84, 126, 168, 210))
        make_seed(self.warm, keys=(84, 126, 168, 210))

    def correct(self):
        return subprocess.run([sys.executable, str(CLI), 'correct', '--baseline', str(self.baseline),
                               '--runtime-snapshot', str(self.cold), '--runtime-snapshot', str(self.warm),
                               '--output', str(self.output)], capture_output=True, text=True)

    def test_correction_preserves_baseline_and_attributes_deduplicated_runtime_discoveries(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.correct()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'correction-report.json').read_text())
        self.assertEqual(report['provenance'], 'runtime-capture-correction')
        self.assertEqual((report['baseline_rows'], report['runtime_union_rows'],
                          report['added_rows'], report['seed']['rows']), (2, 4, 3, 5))
        self.assertEqual([(row['hash'], row['sources']) for row in report['additions']], [
            (126, ['runtime-1', 'runtime-2']), (168, ['runtime-1', 'runtime-2']),
            (210, ['runtime-1', 'runtime-2'])])
        self.assertEqual(report['source_path_attribution'], 'unresolved')
        self.assertFalse(report['corrected_candidate_physical_verification'])
        self.assertEqual(set(report['seed']['source_files']), {
            'baseline:synthetic.db', 'runtime-1:synthetic.db', 'runtime-2:synthetic.db'})
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def change_snapshot(self, directory, statement):
        path = directory / 'initial_pipeline_cache.db'
        with closing(sqlite3.connect(path)) as db, db:
            db.execute(statement)
        manifest = directory / 'pipeline-seed.json'
        value = json.loads(manifest.read_text())
        value['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(value))

    def test_identity_conflicts_in_baseline_or_between_captures_reject_the_entire_correction(self):
        original = {p: p.read_bytes() for p in self.warm.iterdir()}
        for key in [84, 126]:
            with self.subTest(key=key):
                for path, data in original.items():
                    path.write_bytes(data)
                self.output = self.root / f'conflict-{key}'
                self.change_snapshot(self.warm,
                                     f"UPDATE pipeline_cache SET config=X'0500000000010100' WHERE hash={key}")
                before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
                result = self.correct()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('conflicting description bytes', result.stderr)
                self.assertFalse(self.output.exists())
                self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_incompatible_and_unvalidated_snapshots_do_not_publish_a_partial_seed(self):
        cases = ['incompatible', 'corrupt', 'sidecar', 'bad-hash', 'bad-provenance']
        original = {p: p.read_bytes() for p in self.warm.iterdir()}
        for case in cases:
            with self.subTest(case=case):
                self.output = self.root / case
                if case == 'incompatible':
                    self.change_snapshot(self.warm, 'UPDATE pipeline_cache SET type=2 WHERE hash=210')
                elif case == 'corrupt':
                    self.warm.joinpath('initial_pipeline_cache.db').write_bytes(b'invalid database')
                elif case == 'sidecar':
                    self.warm.joinpath('initial_pipeline_cache.db-wal').write_bytes(b'uncheckpointed')
                else:
                    manifest = self.warm / 'pipeline-seed.json'
                    value = json.loads(manifest.read_text())
                    value['sha256' if case == 'bad-hash' else 'source_files'] = 'bad'
                    manifest.write_text(json.dumps(value))
                before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
                result = self.correct()
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse(self.output.exists())
                self.assertEqual({p: p.read_bytes() for p in before}, before)
                self.warm.joinpath('initial_pipeline_cache.db-wal').unlink(missing_ok=True)
                for path, data in original.items():
                    path.write_bytes(data)

    def test_repeats_exact_outputs_and_preserves_baseline_frame_metadata(self):
        self.change_snapshot(self.cold, 'UPDATE pipeline_cache SET first_frame_used=900')
        self.change_snapshot(self.warm, 'UPDATE pipeline_cache SET first_frame_used=901')
        result = self.correct()
        self.assertEqual(result.returncode, 0, result.stderr)
        with closing(sqlite3.connect(self.output / 'assets/initial_pipeline_cache.db')) as db:
            self.assertEqual(db.execute('SELECT hash,first_frame_used FROM pipeline_cache ORDER BY hash').fetchall(),
                             [(42, 10), (84, 10), (126, 900), (168, 900), (210, 900)])
        before = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}
        self.assertNotEqual(self.correct().returncode, 0)
        self.assertEqual({p.relative_to(self.output): p.read_bytes()
                          for p in self.output.rglob('*') if p.is_file()}, before)
        self.output = self.root / 'repeated'
        self.assertEqual(self.correct().returncode, 0)
        self.assertEqual({p.relative_to(self.output): p.read_bytes()
                          for p in self.output.rglob('*') if p.is_file()}, before)

    def test_no_additions_keep_exact_baseline_asset_and_preserve_earlier_provenance(self):
        for directory in [self.cold, self.warm]:
            shutil.rmtree(directory)
            make_seed(directory, keys=(42, 84))
        result = self.correct()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'correction-report.json').read_text())
        self.assertEqual(report['added_rows'], 0)
        for name in ['initial_pipeline_cache.db', 'pipeline-seed.json']:
            self.assertEqual((self.output / 'assets' / name).read_bytes(), (self.baseline / name).read_bytes())

    def test_output_cannot_be_created_inside_baseline_or_runtime_inputs(self):
        for directory in [self.baseline, self.cold, self.warm]:
            with self.subTest(directory=directory.name):
                self.output = directory / 'output'
                result = self.correct()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('outside source', result.stderr)
                self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
