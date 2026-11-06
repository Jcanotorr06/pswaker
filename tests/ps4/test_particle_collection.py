"""Public particle collection boundaries, with synthetic descriptions only."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import sqlite3
from contextlib import closing

from synthetic_pipeline import make_particle_collection as particle_collection, make_seed


CLI = Path(__file__).resolve().parents[2] / 'tools/pswaker/collect-model-seed.py'


class ParticlePreparationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.baseline = self.root / 'baseline'
        make_seed(self.baseline)
        self.collection = self.root / 'collection'
        particle_collection(self.collection)
        self.output = self.root / 'prepared'

    def prepare(self):
        return subprocess.run([sys.executable, str(CLI), 'prepare', '--collection', str(self.collection),
                               '--baseline', str(self.baseline), '--output', str(self.output)],
                              capture_output=True, text=True)

    def test_particle_variations_map_to_complete_descriptions_and_preserve_inputs(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'collection-report.json').read_text())
        self.assertEqual((report['baseline_rows'], report['new_rows'], report['seed']['rows']), (2, 1, 3))
        self.assertEqual([(r['hash'], [{k: v for k, v in state.items() if k != 'variation'}
                                      for state in r['states']]) for r in report['mapping']],
                         [(84, [{'texture_index': 0, 'ticks': [1, 2]}]),
                          (126, [{'texture_index': 1, 'ticks': [1, 2]}])])
        self.assertEqual(report['mapping'][1]['states'][0]['variation'],
                         {'random_seed': 1, 'scale': 2, 'alpha': 128, 'texture_index': 1})
        self.assertFalse(report['physical_verification'])
        self.assertEqual({p: p.read_bytes() for p in before}, before)
        first = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}
        self.output = self.root / 'repeat'
        self.assertEqual(self.prepare().returncode, 0)
        self.assertEqual({p.relative_to(self.output): p.read_bytes()
                          for p in self.output.rglob('*') if p.is_file()}, first)


class ParticleBatchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.baseline = self.root / 'baseline'
        make_seed(self.baseline)
        self.collections = self.root / 'collections'
        self.manifest = self.root / 'manifest.json'
        self.output = self.root / 'prepared'
        rows = []
        for name, resource, keys in [('flash', '/res/Particle/common.jpc:0x000b', (84, 126)),
                                     ('overlap', '/res/Particle/common.jpc:0x000b+0x2009', (126, 168))]:
            directory = self.collections / name
            metadata = particle_collection(directory, resource, keys)
            metadata.update(contract_sha256='f' * 64,
                            resources={'particle_sha256': 'd' * 64, 'particle_bytes': 100})
            (directory / 'collection.json').write_text(json.dumps(metadata))
            rows.append({'id': name, 'family': 'bomb', 'resource': resource, 'action': 'exercise',
                         'script': metadata['script'], 'input_identity': metadata['resources'],
                         'source_references': ['synthetic/bomb.cpp:explode'],
                         'assumptions': ['Synthetic simultaneous emitter recipe.']})
        self.document = {'schema': 1, 'id': 'synthetic-particles-v1', 'kind': 'particle-effects',
                         'image_sha256': 'c' * 64, 'contract_sha256': 'f' * 64,
                         'collector': metadata['collector'], 'exclusions': ['Scene particles need follow-up.'],
                         'rows': rows}
        self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.document))

    def prepare(self):
        return subprocess.run([sys.executable, str(CLI), 'prepare-batch', '--manifest', str(self.manifest),
                               '--collections', str(self.collections), '--baseline', str(self.baseline),
                               '--output', str(self.output)], capture_output=True, text=True)

    def test_batch_maps_overlaps_and_shared_configurations_repeatably(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.output / 'batch-report.json').read_text())
        self.assertEqual(report['provenance'], 'particle-effect-batch')
        self.assertEqual((report['baseline_rows'], report['collected_rows'], report['new_rows'],
                          report['seed']['rows']), (2, 3, 2, 4))
        self.assertEqual([(r['hash'], r['sources']) for r in report['mapping']],
                         [(84, ['flash']), (126, ['flash', 'overlap']), (168, ['overlap'])])
        self.assertEqual({p: p.read_bytes() for p in before}, before)
        first = (self.output / 'assets/initial_pipeline_cache.db').read_bytes()
        manifest = (self.output / 'assets/pipeline-seed.json').read_bytes()
        self.output = self.root / 'repeat'
        self.assertEqual(self.prepare().returncode, 0)
        self.assertEqual((self.output / 'assets/initial_pipeline_cache.db').read_bytes(), first)
        self.assertEqual((self.output / 'assets/pipeline-seed.json').read_bytes(), manifest)

    def test_bad_scripts_attribution_lifetimes_and_conflicts_reject_atomically(self):
        original = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        for defect in ['unknown-effect', 'oversized', 'script', 'duplicate', 'wrong-bank',
                       'wrong-contract', 'not-retired', 'unmapped', 'no-draw', 'conflict', 'incompatible']:
            with self.subTest(defect=defect):
                for p, value in original.items():
                    p.write_bytes(value)
                self.document = json.loads(self.manifest.read_text())
                row = self.document['rows'][1]
                path = self.collections / 'overlap/collection.json'
                metadata = json.loads(path.read_text())
                if defect == 'unknown-effect':
                    row['resource'] = '/res/Particle/common.jpc:0x4004'
                elif defect == 'oversized':
                    row['resource'] += '+0x2005+0x2006+0x2007'
                elif defect == 'script':
                    row['script']['max_ticks'] = 999
                elif defect == 'duplicate':
                    row['id'] = 'flash'
                elif defect == 'wrong-bank':
                    metadata['resources']['particle_sha256'] = '0' * 64
                elif defect == 'wrong-contract':
                    metadata['contract_sha256'] = '0' * 64
                elif defect == 'not-retired':
                    metadata['variations'][0]['steps'][-1]['particles'] = 1
                elif defect == 'unmapped':
                    metadata['variations'][0]['steps'][0]['configurations'] = []
                elif defect == 'no-draw':
                    metadata['draw_calls'] = 0
                else:
                    seed = path.parent / 'assets/initial_pipeline_cache.db'
                    with closing(sqlite3.connect(seed)) as db, db:
                        if defect == 'conflict':
                            db.execute("UPDATE pipeline_cache SET config=X'0500000000010100' WHERE hash=126")
                        else:
                            db.execute('UPDATE pipeline_cache SET type=2 WHERE hash=168')
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
                self.assertEqual({p: p.read_bytes() for p in original}, before)


if __name__ == '__main__':
    unittest.main()
