"""Artifact inspection rejects a package changed after the build."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]


class ArtifactTests(unittest.TestCase):
    def test_changed_package_is_rejected_before_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'evidence').mkdir()
            (root / 'out').mkdir()
            (root / 'out/diagnostic.pkg').write_bytes(b'changed')
            (root / 'evidence/artifacts.json').write_text(json.dumps({'package': {
                'filename': 'diagnostic.pkg',
                'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'}}))
            result = subprocess.run([sys.executable, str(HERE / 'inspect-artifacts.py'), str(root)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Package SHA-256 mismatch', result.stderr)


if __name__ == '__main__':
    unittest.main()
