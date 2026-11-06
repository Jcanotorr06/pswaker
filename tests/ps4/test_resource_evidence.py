"""Platform-log boundary with synthetic console memory services."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ResourceEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('clang++') or shutil.which('g++')
        if not compiler:
            raise unittest.SkipTest('C++ compiler required')
        cls.temporary = tempfile.TemporaryDirectory(prefix='pswaker-resource-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.executable = Path(cls.temporary.name) / 'resource-evidence'
        subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror',
                        '-I', str(ROOT / 'platform/ps4/game'),
                        str(ROOT / 'platform/ps4/game/resource-evidence.cpp'),
                        str(ROOT / 'tests/ps4/resource-evidence.cpp'),
                        '-o', str(cls.executable)], check=True, capture_output=True, text=True)

    def test_startup_log_retains_memory_units_phase_and_clock(self):
        result = subprocess.run([str(self.executable)], check=True, capture_output=True, text=True)
        self.assertEqual(result.stdout.strip(),
                         'RESOURCE ms=1250.0 garlic=1048576 onion=2097152 buffers=7 '
                         'main-mspace-allocated=3145728 flexible-available=4194304 '
                         'query-result=0 phase=before-renderer')

    def test_failed_query_is_unavailable_instead_of_a_memory_measurement(self):
        result = subprocess.run([str(self.executable), 'fail'], check=True, capture_output=True, text=True)
        self.assertIn('flexible-available=unavailable query-result=-5', result.stdout)
        self.assertNotIn('flexible-available=4194304', result.stdout)


if __name__ == '__main__':
    unittest.main()
