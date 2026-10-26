"""Actual GCI backend with real SDL file I/O; only OS failures are injected."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
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
        includes = [aurora / 'include', aurora / 'lib', HERE / 'game',
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
            str(HERE / 'game/storage.cpp'), str(HERE / 'tests/gci-persistence.cpp'),
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

    def test_sync_failure_returns_ioerror_and_preserves_previous_gci(self):
        self.scenario('sync-failure')

    def test_rename_failure_returns_ioerror_and_preserves_previous_gci(self):
        self.scenario('rename-failure')
