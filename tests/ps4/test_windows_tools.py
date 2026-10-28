"""Prepare the real Windows closure independently of the caller's SDK policy."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPOSITORY = Path(__file__).resolve().parents[2]
DOTNET = os.environ.get('PSWAKER_WINDOWS_DOTNET', '')


@unittest.skipUnless(sys.platform == 'win32' and DOTNET, 'Native Windows .NET SDK required')
class WindowsToolPreparationTests(unittest.TestCase):
    def test_preparation_uses_pinned_sdk_despite_callers_global_json(self):
        with tempfile.TemporaryDirectory(prefix='pswaker-tool-preparation-') as folder:
            root = Path(folder)
            caller = root / 'caller'
            caller.mkdir()
            policy = {'sdk': {'version': '99.0.100', 'rollForward': 'disable'}}
            (caller / 'global.json').write_text(json.dumps(policy))
            result = subprocess.run([
                sys.executable, str(REPOSITORY / 'tools/pswaker/prepare-windows-tools.py'),
                '--dotnet', str(Path(DOTNET).resolve()), '--output', str(root / 'tools')],
                cwd=caller, capture_output=True, text=True, timeout=180)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            release = json.loads((root / 'tools/tool-release.json').read_text())
            self.assertEqual(release['sdk'], '8.0.427')
            self.assertEqual(json.loads((caller / 'global.json').read_text()), policy)
            version = subprocess.run([str(root / 'tools/PkgTool.Core.exe'), 'version'],
                                     capture_output=True, text=True, timeout=30)
            self.assertEqual(version.returncode, 0, version.stdout + version.stderr)
            self.assertIn('LibOrbisPkg version', version.stdout)


if __name__ == '__main__':
    unittest.main()
