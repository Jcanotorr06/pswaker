"""Card lifecycle observer through real game requests and SDK threads."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
GAME = os.environ.get('PSWAKER_GAME_ROOT')


@unittest.skipUnless(GAME and shutil.which('clang++-21'),
                     'Prepared game and Linux compiler required')
class RouteCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix='pswaker-route-card-')
        cls.addClassCleanup(cls.directory.cleanup)
        cls.binary = Path(cls.directory.name) / 'card'
        root = Path(GAME)
        game = root / 'src/switchwaker'
        sdk = game / 'native/sdk'
        includes = [game / 'native/include', game / 'native/include/sdk',
                    root / 'src/aurora/include', game / 'game/include',
                    root / 'assets/GZLE01/include', root / 'assets/GZLE01',
                    game / 'game/src', game / 'native/include/pc/msl', sdk / 'include']
        flags = ['clang++-21', '-std=c++23', '-DTARGET_PC=1', '-D__ORBIS__',
                 '-DVERSION=2', '-DMTX_USE_PS=1', '-pthread', '-ffunction-sections',
                 '-fdata-sections', '-Wl,--gc-sections', '-Wno-register',
                 '-include', str(game / 'native/include/pc/cos_pc_config.h'),
                 '-include', str(game / 'native/include/sdk/cos_sdk_extras.h')]
        for path in includes:
            flags += ['-I', str(path)]
        sources = [game / 'game/src/m_Do/m_Do_MemCard.cpp',
                   sdk / 'src/os/OSThread.cpp', sdk / 'src/os/OSMutex.cpp',
                   sdk / 'src/os/OSInterrupt.cpp', sdk / 'src/os/OSAlarm.cpp',
                   sdk / 'src/os/OSContext.cpp',
                   HERE / 'tests/route-card.cpp']
        result = subprocess.run(flags + list(map(str, sources)) + ['-o', str(cls.binary)],
                                capture_output=True, text=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)

    def check_scenario(self, name):
        result = subprocess.run([str(self.binary), name], capture_output=True,
                                text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_quit_observer_waits_for_queued_and_active_store_without_consuming_completion(self):
        self.check_scenario('completed-store')

    def test_quit_observer_reports_failed_store_without_claiming_success(self):
        self.check_scenario('failed-store')
