"""Public coverage evidence CLI; descriptions and provenance are synthetic."""
from contextlib import closing
import json
import hashlib
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from synthetic_pipeline import make_seed


CLI = Path(__file__).resolve().parents[2] / 'evidence/ps4/outset-coverage-111/verify-coverage.py'


class OutsetCoverageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='pswaker-coverage-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.candidate = self.root / 'candidate'
        self.cold = self.root / 'cold'
        self.warm = self.root / 'warm'
        make_seed(self.candidate, keys=(42, 84, 126))
        make_seed(self.cold, keys=(42,))
        make_seed(self.warm, keys=(42, 84))
        self.output = self.root / 'coverage.json'

    def run_cli(self):
        return subprocess.run([sys.executable, str(CLI), str(self.candidate),
                               str(self.cold), str(self.warm), '--output', str(self.output)],
                              capture_output=True, text=True)

    def change_snapshot(self, statement):
        database = self.warm / 'initial_pipeline_cache.db'
        with closing(sqlite3.connect(database)) as db, db:
            db.execute(statement)
        manifest = self.warm / 'pipeline-seed.json'
        report = json.loads(manifest.read_text())
        report['sha256'] = hashlib.sha256(database.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(report))

    def test_recorded_subset_retains_candidate_without_inventing_descriptions(self):
        self.change_snapshot('UPDATE pipeline_cache SET first_frame_used=999')
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(self.output.read_text())
        self.assertEqual(report['candidate']['rows'], 3)
        self.assertEqual(report['recorded_union_rows'], 2)
        self.assertEqual(report['already_represented_rows'], 2)
        self.assertEqual(report['added_rows'], 0)
        self.assertEqual(report['candidate_rows_not_recorded'], 1)
        self.assertEqual([r['identical_rows_in_candidate'] for r in report['snapshots']], [1, 2])
        self.assertEqual({p: p.read_bytes() for p in before}, before)
        self.assertEqual(set(self.root.rglob('*')), set(before) | {
            self.candidate, self.cold, self.warm, self.output})
        self.assertNotIn(str(self.root), self.output.read_text())

    def test_missing_or_conflicting_descriptions_cannot_be_claimed_as_covered(self):
        for statement, message in [
            ('UPDATE pipeline_cache SET hash=999 WHERE hash=84', 'missing from the candidate'),
            ("UPDATE pipeline_cache SET config=X'0500000000010100' WHERE hash=84", 'conflicting description bytes'),
        ]:
            with self.subTest(statement=statement):
                before = {p: p.read_bytes() for p in self.warm.iterdir()}
                self.change_snapshot(statement)
                result = self.run_cli()
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(message, result.stderr)
                self.assertFalse(self.output.exists())
                for path, data in before.items():
                    path.write_bytes(data)

    def test_one_unsupported_record_rejects_the_entire_snapshot(self):
        self.change_snapshot('UPDATE pipeline_cache SET type=2 WHERE hash=84')
        before = {p: p.read_bytes() for p in self.warm.iterdir()}
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('renderer-incompatible', result.stderr)
        self.assertFalse(self.output.exists())
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_existing_coverage_report_is_preserved(self):
        self.output.write_text('retained earlier evidence')
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('Output already exists', result.stderr)
        self.assertEqual(self.output.read_text(), 'retained earlier evidence')


if __name__ == '__main__':
    unittest.main()
