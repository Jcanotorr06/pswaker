"""Consolidation CLI contract; all resources and descriptions are synthetic."""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from synthetic_pipeline import make_seed, make_model_collection, make_particle_collection


CLI = Path(__file__).resolve().parents[2] / 'tools/pswaker/collect-model-seed.py'


class SeedConsolidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.baseline = self.root / 'baseline'
        make_seed(self.baseline, keys=(42, 84))
        self.plan = self.root / 'plan.json'
        self.output = self.root / 'consolidated'
        sources = []
        for name, particle, keys in [('models', False, (84, 126)), ('particles', True, (126, 168))]:
            collections = self.root / (name + '-collections')
            metadata = (make_particle_collection if particle else make_model_collection)(collections / 'draw', keys=keys)
            metadata.update(resources=({'particle_sha256': 'd' * 64, 'particle_bytes': 100} if particle else
                                      {'archive_sha256': 'd' * 64, 'model_sha256': 'e' * 64, 'model_bytes': 100}),
                            contract_sha256='f' * 64)
            (collections / 'draw/collection.json').write_text(json.dumps(metadata))
            row = {'id': 'draw', 'family': 'synthetic', 'resource': metadata['resource'],
                   'source_references': ['synthetic.cpp:draw'], 'input_identity': metadata['resources'],
                   'action': 'exercise', 'assumptions': ['Only the synthetic draw is exercised.']}
            manifest = {'schema': 1, 'id': name, 'collector': metadata['collector'],
                        'image_sha256': 'c' * 64, 'contract_sha256': 'f' * 64, 'rows': [row]}
            if particle:
                row['script'] = metadata['script']
                manifest.update(kind='particle-effects', exclusions=['Other effects remain gaps.'])
            else:
                row['dimensions'] = {'content': ['pot'], 'mode': ['normal'], 'state': ['stock-bdl-v1']}
                manifest['dynamic_exclusions'] = [{'id': 'dynamic', 'owner': '#151', 'reason': 'Separate effect draw.'}]
                manifest['rows'].append({**row, 'id': 'alias', 'action': 'shared', 'shared_with': 'draw',
                                         'justification': 'Identical synthetic resource and stock state.'})
            path = self.root / (name + '.json')
            path.write_text(json.dumps(manifest))
            sources.append({'id': name, 'manifest': path.name, 'manifest_sha256': self.sha(path),
                            'collections': collections.name})
        self.document = {'schema': 1, 'baseline_sha256': self.sha(self.baseline / 'initial_pipeline_cache.db'),
                         'baseline_manifest_sha256': self.sha(self.baseline / 'pipeline-seed.json'),
                         'image_sha256': 'c' * 64, 'contract_sha256': 'f' * 64, 'sources': sources}
        self.save_plan()

    @staticmethod
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def save_plan(self):
        self.plan.write_text(json.dumps(self.document))

    def consolidate(self):
        return subprocess.run([sys.executable, str(CLI), 'consolidate', '--plan', str(self.plan),
                               '--baseline', str(self.baseline), '--output', str(self.output)],
                              capture_output=True, text=True)

    def update_manifest(self, name, mutate):
        path = self.root / (name + '.json')
        document = json.loads(path.read_text())
        mutate(document)
        path.write_text(json.dumps(document))
        source = next(s for s in self.document['sources'] if s['id'] == name)
        source['manifest_sha256'] = self.sha(path)
        self.save_plan()

    def test_union_preserves_records_all_attribution_and_repeat_bytes(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.consolidate()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'consolidation-report.json').read_text())
        self.assertEqual((report['baseline_rows'], report['new_rows'], report['seed']['rows']), (2, 2, 4))
        by_hash = {row['hash']: row for row in report['mapping']}
        self.assertEqual([(s['source'], s['row']) for s in by_hash[126]['sources']],
                         [('models', 'alias'), ('models', 'draw'), ('particles', 'draw')])
        self.assertEqual(by_hash[126]['sources'][-1]['method'], 'dynamic-effect-draw')
        self.assertTrue(by_hash[84]['baseline_covered'])
        self.assertTrue(by_hash[42]['baseline_covered'])
        self.assertFalse(report['physical_verification'])
        self.assertEqual(report['sources']['models']['manifest']['collector'],
                         {'sha256': 'a' * 64, 'build_sha256': 'b' * 64})
        source_files = report['seed']['source_files']
        self.assertTrue(any(key.startswith('baseline:') for key in source_files))
        self.assertTrue(any(key.startswith('models:') for key in source_files))
        self.assertTrue(any(key.startswith('particles:') for key in source_files))
        with closing(sqlite3.connect(self.output / 'assets/initial_pipeline_cache.db')) as db:
            self.assertEqual(db.execute('SELECT hash,first_frame_used FROM pipeline_cache ORDER BY hash').fetchall(),
                             [(42, 10), (84, 10), (126, 10), (168, 10)])
        self.assertEqual({p: p.read_bytes() for p in before}, before)
        first = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}
        self.output = self.root / 'repeat'
        self.assertEqual(self.consolidate().returncode, 0)
        self.assertEqual({p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}, first)

    def test_duplicate_only_sources_keep_provenance_and_original_frame_metadata(self):
        shutil.rmtree(self.baseline)
        make_seed(self.baseline, keys=(42, 84, 126, 168))
        self.document['baseline_sha256'] = self.sha(self.baseline / 'initial_pipeline_cache.db')
        self.document['baseline_manifest_sha256'] = self.sha(self.baseline / 'pipeline-seed.json')
        self.save_plan()
        # A different first-use frame is evidence metadata, not a description conflict.
        path = self.root / 'particles-collections/draw/assets/initial_pipeline_cache.db'
        with closing(sqlite3.connect(path)) as db, db:
            db.execute('UPDATE pipeline_cache SET first_frame_used=123')
        manifest = path.parent / 'pipeline-seed.json'
        document = json.loads(manifest.read_text())
        document['sha256'] = self.sha(path)
        manifest.write_text(json.dumps(document))
        metadata_path = path.parents[1] / 'collection.json'
        metadata = json.loads(metadata_path.read_text())
        metadata['seed_sha256'] = self.sha(path)
        metadata_path.write_text(json.dumps(metadata))
        result = self.consolidate()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'consolidation-report.json').read_text())
        self.assertEqual(report['new_rows'], 0)
        self.assertEqual((self.output / 'assets/initial_pipeline_cache.db').read_bytes(),
                         (self.baseline / 'initial_pipeline_cache.db').read_bytes())
        self.assertTrue(any(k.startswith('particles:') for k in report['seed']['source_files']))
        row = next(row for row in report['mapping'] if row['hash'] == 126)
        self.assertEqual(row['first_frame_used'], 10)
        self.assertEqual(row['sources'][-1]['first_frame_used'], 123)

    def test_gaps_and_exclusions_are_retained_without_claiming_physical_coverage(self):
        self.update_manifest('particles', lambda document: document['rows'].append({
            'id': 'unreachable', 'family': 'unsupported', 'action': 'unsupported',
            'source_references': ['synthetic.cpp:unreachable'], 'assumptions': ['No controller exercise.'],
            'reason': 'Prerequisites unavailable.'}))
        result = self.consolidate()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'consolidation-report.json').read_text())
        self.assertFalse(report['inventory_complete'])
        self.assertEqual(report['residual_gaps'], ['particles/unreachable'])
        self.assertEqual(report['sources']['particles']['manifest']['exclusions'], ['Other effects remain gaps.'])
        self.assertTrue(all(row['physical_verification'] is False for row in report['rows']))

    def test_invalid_frozen_inputs_and_conflicts_never_publish_output(self):
        saved = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        for defect in ['plan', 'empty', 'duplicate-id', 'unsafe-id', 'baseline', 'baseline-manifest', 'manifest-hash',
                       'image', 'contract', 'missing', 'empty-seed', 'malformed', 'changed',
                       'incompatible', 'conflict', 'attribution']:
            with self.subTest(defect=defect):
                for relative, data in saved.items():
                    (self.root / relative).write_bytes(data)
                self.document = json.loads(self.plan.read_text())
                path = self.root / 'particles-collections/draw/assets/initial_pipeline_cache.db'
                metadata_path = path.parents[1] / 'collection.json'
                if defect == 'plan':
                    self.plan.write_text('[]')
                elif defect == 'empty':
                    self.document['sources'] = []
                    self.save_plan()
                elif defect in ['duplicate-id', 'unsafe-id']:
                    self.document['sources'][1]['id'] = 'models' if defect == 'duplicate-id' else '../escape'
                    self.save_plan()
                elif defect in ['baseline', 'baseline-manifest', 'manifest-hash']:
                    if defect == 'baseline':
                        self.document['baseline_sha256'] = '0' * 64
                    elif defect == 'baseline-manifest':
                        self.document['baseline_manifest_sha256'] = '0' * 64
                    else:
                        self.document['sources'][1]['manifest_sha256'] = '0' * 64
                    self.save_plan()
                elif defect in ['image', 'contract']:
                    self.update_manifest('particles', lambda document: document.update({defect + '_sha256': '0' * 64}))
                elif defect == 'missing':
                    metadata_path.unlink()
                elif defect == 'malformed':
                    metadata_path.write_text('[]')
                elif defect == 'attribution':
                    document = json.loads(metadata_path.read_text())
                    document['collector']['sha256'] = '0' * 64
                    metadata_path.write_text(json.dumps(document))
                else:
                    with closing(sqlite3.connect(path)) as db, db:
                        if defect == 'empty-seed':
                            db.execute('DELETE FROM pipeline_cache')
                        elif defect == 'incompatible':
                            db.execute('UPDATE pipeline_cache SET config_version=999')
                        else:
                            db.execute("UPDATE pipeline_cache SET config=X'0500000000010100' WHERE hash=126")
                    if defect != 'changed':
                        manifest = path.parent / 'pipeline-seed.json'
                        document = json.loads(manifest.read_text())
                        document['sha256'] = self.sha(path)
                        manifest.write_text(json.dumps(document))
                        metadata = json.loads(metadata_path.read_text())
                        metadata['seed_sha256'] = self.sha(path)
                        metadata_path.write_text(json.dumps(metadata))
                before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
                result = self.consolidate()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.output.exists())
                self.assertNotIn('Traceback', result.stderr)
                self.assertEqual({p: p.read_bytes() for p in before}, before)
                self.assertFalse(list(self.root.glob('.consolidated-seed-*')))

    def test_existing_and_nested_outputs_are_preserved(self):
        self.output.mkdir()
        marker = self.output / 'keep'
        marker.write_text('previous evidence')
        self.assertNotEqual(self.consolidate().returncode, 0)
        self.assertEqual(marker.read_text(), 'previous evidence')
        self.output = self.root / 'particles-collections/nested'
        self.assertNotEqual(self.consolidate().returncode, 0)
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
