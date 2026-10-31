"""Semantic PS4 prompt contract: hosted C++, no game data or GPU."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(shutil.which('clang++-21'), 'Linux Clang 21 required')
class PromptTests(unittest.TestCase):
    def test_public_resolver_contract(self):
        with tempfile.TemporaryDirectory(prefix='pswaker-prompts-') as directory:
            binary = Path(directory) / 'prompts'
            build = subprocess.run([
                'clang++-21', '-std=c++23', '-Wall', '-Wextra', '-Werror',
                '-I', str(ROOT / 'platform/ps4/game'),
                str(ROOT / 'tests/ps4/prompts.cpp'),
                str(ROOT / 'platform/ps4/game/prompts.cpp'),
                str(ROOT / 'platform/ps4/game/controls-config.cpp'),
                '-o', str(binary)], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=15)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == '__main__':
    unittest.main()
