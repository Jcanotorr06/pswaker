"""Shared profile storage/settings through real files; no owner data."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/pswaker'))
from build_inputs import Locations

LOCATIONS = Locations()
PLATFORM = LOCATIONS.platform


@unittest.skipUnless(shutil.which('clang++-21'), 'Linux compiler required')
class PersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix='pswaker-storage-')
        cls.addClassCleanup(cls.directory.cleanup)
        cls.binary = Path(cls.directory.name) / 'storage'
        result = subprocess.run([
            'clang++-21', '-std=c++23', '-Wall', '-Wextra', '-Werror',
            '-I', str(PLATFORM / 'game'), str(PLATFORM / 'game/storage.cpp'),
            str(PLATFORM / 'game/controls-config.cpp'),
            str(LOCATIONS.tests / 'storage.cpp'), '-Wl,--wrap=fsync',
            '-Wl,--wrap=rename', '-Wl,--wrap=close', '-o', str(cls.binary)],
            capture_output=True, text=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)

    def scenario(self, name):
        with tempfile.TemporaryDirectory(prefix='pswaker-profile-') as directory:
            result = subprocess.run([str(self.binary), name, directory],
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_setting_survives_new_process_and_preserves_other_settings(self):
        self.scenario('roundtrip')

    def test_controls_survive_new_process_and_text_size_changes_preserve_the_section(self):
        self.scenario('controls-roundtrip')

    def test_failed_sync_close_or_replacement_preserves_previous_setting(self):
        self.scenario('failed-replacement')

    def test_unavailable_card_directory_requires_repair_before_retry(self):
        self.scenario('unavailable')

    def test_unreadable_or_invalid_settings_are_not_replaced_with_defaults(self):
        self.scenario('invalid')

    def test_uncertain_directory_sync_completion_is_reported_as_failure(self):
        self.scenario('uncertain-completion')
