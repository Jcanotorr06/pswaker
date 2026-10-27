"""Renderer preparation CLI at the existing locked-source preparation boundary."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/pswaker'))
from build_inputs import Locations

LOCATIONS = Locations()
REFERENCE = os.environ.get('PSWAKER_REFERENCE_BUILD')


@unittest.skipUnless(REFERENCE, 'Set PSWAKER_REFERENCE_BUILD to exercise real pinned sources')
class RendererPreparationTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        tree = self.root / 'src/aurora'
        tree.mkdir(parents=True)
        (self.root / 'evidence').mkdir()
        reference = Path(REFERENCE)
        with tarfile.open(reference / 'downloads/src-aurora.tar.gz') as archive:
            prefix = archive.getmembers()[0].name.split('/')[0] + '/'
            for member in archive.getmembers():
                if member.name.startswith(prefix) and member.name != prefix:
                    member.name = member.name[len(prefix):]
                    archive.extract(member, tree, filter='data')
        subprocess.run(['git', 'apply', str(reference / 'refs/dusklight/patches/aurora-ps4.patch')],
                       cwd=tree, check=True)

    def test_matched_platform_accepts_ordered_renderer_reconciliation(self):
        result = subprocess.run([sys.executable, str(LOCATIONS.command('reconcile-renderer.py')), str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.root / 'evidence/renderer-reconciliation.json').read_text())
        self.assertEqual(len(report['patches']), 21)
        self.assertEqual(len(report['applied']), 15)
        self.assertEqual(report['hardware_status'], 'untested')

    def test_changed_source_is_rejected_before_any_renderer_patch_is_applied(self):
        path = self.root / 'src/aurora/lib/gx/shader.cpp'
        path.write_text(path.read_text() + '\n// changed source\n')
        result = subprocess.run([sys.executable, str(LOCATIONS.command('reconcile-renderer.py')), str(self.root)],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Renderer source context mismatch: lib/gx/shader.cpp', result.stderr)
        self.assertFalse((self.root / 'evidence/renderer-reconciliation.json').exists())
        # First patch would add this helper. A rejected input must not receive any patch.
        self.assertNotIn('bool tev_op_is_channel_compare', path.read_text())



if __name__ == '__main__':
    unittest.main()
