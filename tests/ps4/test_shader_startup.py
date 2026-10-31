"""Real initialized renderer and driver boundary; no private queue access."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

BINARY = os.environ.get('PSWAKER_SHADER_STARTUP_CHECK')


@unittest.skipUnless(BINARY and shutil.which('xvfb-run'),
                     'Set PSWAKER_SHADER_STARTUP_CHECK to the host renderer check binary')
class ShaderStartupTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='pswaker-shader-startup-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.sentinels = {'settings.ini': b'owner settings\n',
                          'saves/synthetic-progress.txt': b'owner progress\n'}
        for name, contents in self.sentinels.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)

    def launch(self, mode, success=True):
        result = subprocess.run(['xvfb-run', '-a', BINARY, mode], cwd=self.root,
                                capture_output=True, text=True, timeout=45)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        for name, contents in self.sentinels.items():
            self.assertEqual((self.root / name).read_bytes(), contents)
        return result.stdout + result.stderr

    def test_seeded_cold_launch_waits_for_in_flight_creation_and_reports_real_completion(self):
        self.assertIn('PASS all-included-configurations-ready-before-gameplay', self.launch('cold'))

    def test_progress_counts_completed_configurations_while_driver_work_is_pending(self):
        self.assertIn('PASS progress-counts-ready-configurations-and-keeps-in-flight-work-pending',
                      self.launch('progress'))

    def test_compatible_relaunch_reuses_cache_and_invalidation_prepares_again(self):
        self.launch('cold')
        seed = (self.root / 'initial_pipeline_cache.db').read_bytes()
        output = self.launch('reuse')
        self.assertIn('already merged', output)
        self.assertRegex(output, r'DRIVER cache-hits=[1-9][0-9]*')
        # A different build ID selects a fresh cache directory. Keep the old
        # directory, exactly as the installed program does after an update.
        (self.root / 'cache').rename(self.root / 'cache-previous-build')
        output = self.launch('reuse')
        self.assertIn('2 rows merged', output)
        self.assertIn('PASS all-included-configurations-ready-before-gameplay', output)
        self.assertEqual((self.root / 'initial_pipeline_cache.db').read_bytes(), seed)

    def test_missing_and_empty_seed_fail_before_gameplay(self):
        for mode in ['missing', 'empty']:
            with self.subTest(mode=mode):
                self.assertIn('PASS bad-seed-stops-before-gameplay', self.launch(mode))

    def test_corrupt_and_incompatible_seed_fail_before_gameplay(self):
        for mode in ['corrupt', 'incompatible']:
            with self.subTest(mode=mode):
                seed = self.root / 'initial_pipeline_cache.db'
                if seed.exists():
                    seed.unlink()
                self.assertIn('PASS bad-seed-stops-before-gameplay', self.launch(mode))

    def test_driver_creation_failure_is_not_successful_preparation(self):
        self.assertIn('PASS failed-creation-is-not-success', self.launch('creation-failure'))

    def test_non_null_driver_error_object_is_not_successful_preparation(self):
        self.assertIn('PASS failed-creation-is-not-success', self.launch('validation-failure'))

    def test_uncovered_configuration_blocks_and_keeps_gameplay_wait_accounting(self):
        self.assertIn('PASS uncovered-configuration-blocks-and-retains-gameplay-wait-accounting',
                      self.launch('uncovered'))

    def test_null_pipeline_after_gameplay_handoff_surfaces_a_fatal_failure(self):
        output = self.launch('runtime-failure', success=False)
        self.assertIn('PASS preparation-handoff-to-gameplay', output)
        self.assertIn('Shader pipeline creation failed during gameplay', output)

    def test_reported_driver_failure_after_gameplay_handoff_keeps_existing_fatal_flow(self):
        output = self.launch('runtime-validation-failure', success=False)
        self.assertIn('PASS preparation-handoff-to-gameplay', output)
        self.assertIn('synthetic driver creation error', output)
