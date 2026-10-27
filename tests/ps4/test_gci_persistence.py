"""Actual GCI backend with real SDL file I/O; only OS failures are injected."""
import os
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
GAME = os.environ.get('PSWAKER_GAME_ROOT')
REFERENCE = os.environ.get('PSWAKER_REFERENCE_BUILD')
HOST = os.environ.get('PSWAKER_HOST_ROOT')


@unittest.skipUnless(GAME and REFERENCE and HOST and shutil.which('clang++-21'),
                     'Prepared game, reference platform and host SDL build required')
class GciPersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix='pswaker-gci-')
        cls.addClassCleanup(cls.directory.cleanup)
        cls.binary = Path(cls.directory.name) / 'gci'
        aurora = Path(GAME) / 'src/aurora'
        platform = Path(REFERENCE)
        includes = [aurora / 'include', aurora / 'lib', PLATFORM / 'game',
                    platform / 'src/sdl3/include',
                    platform / 'src/fetch/fmt/fmt-12.1.0/include']
        flags = ['clang++-21', '-std=c++23', '-D__ORBIS__', '-DFMT_HEADER_ONLY',
                 '-ffunction-sections', '-fdata-sections', '-Wl,--gc-sections']
        for path in includes:
            flags += ['-I', str(path)]
        sources = [aurora / 'lib' / name for name in [
            'io.cpp', 'card/CardGciFolder.cpp', 'card/FileIO.cpp',
            'card/File.cpp', 'card/Util.cpp']]
        result = subprocess.run(flags + list(map(str, sources)) + [
            str(PLATFORM / 'game/storage.cpp'), str(LOCATIONS.tests / 'gci-persistence.cpp'),
            str(Path(HOST) / 'sdl/libSDL3.a'), '-pthread', '-ldl', '-lm',
            '-Wl,--wrap=fsync', '-Wl,--wrap=rename', '-o', str(cls.binary)],
            capture_output=True, text=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)

    def scenario(self, name):
        with tempfile.TemporaryDirectory(prefix='pswaker-card-') as directory:
            result = subprocess.run([str(self.binary), name, directory],
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_gci_data_and_metadata_survive_close_and_reopen(self):
        self.scenario('roundtrip')

    def test_interrupted_multiblock_save_preserves_completed_save_until_explicit_restore(self):
        self.scenario('transaction')

    def test_corrupt_progress_is_preserved_before_explicit_backup_restore(self):
        self.scenario('corrupt')

    def test_corrupt_progress_without_backup_cannot_be_reset_or_restored(self):
        self.scenario('corrupt-no-backup')

    def test_wrong_size_save_can_be_restored_without_losing_original_evidence(self):
        self.scenario('corrupt-size')

    def test_missing_primary_with_retained_backup_requires_explicit_recovery(self):
        self.scenario('missing-primary')

    def test_owner_controlled_write_failure_reaches_real_gci_ioerror(self):
        self.scenario('controlled-failure')

    def test_invalid_game_metadata_is_detected_before_loading_or_backup(self):
        self.scenario('corrupt-metadata')

    def test_bad_test_marker_cannot_offer_restore_or_roll_back_healthy_progress(self):
        self.scenario('corrupt-marker')

    def test_sync_failure_returns_ioerror_and_preserves_previous_gci(self):
        self.scenario('sync-failure')

    def test_rename_failure_returns_ioerror_and_preserves_previous_gci(self):
        self.scenario('rename-failure')
