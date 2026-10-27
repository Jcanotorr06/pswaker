"""Game audio API with real clocked DMA/SDK threads; SDL is the external boundary."""
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


@unittest.skipUnless(GAME and REFERENCE and shutil.which('clang++-21'),
                     'Prepared game/platform and Linux compiler required')
class RouteAudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix='pswaker-audio-')
        cls.addClassCleanup(cls.directory.cleanup)
        cls.binary = Path(cls.directory.name) / 'audio'
        game = Path(GAME)
        sdk = game / 'src/switchwaker/native/sdk'
        platform = Path(REFERENCE)
        sources = [sdk / 'src/audio/AI.cpp', sdk / 'src/os/OSThread.cpp',
                   sdk / 'src/os/OSMutex.cpp', sdk / 'src/os/OSInterrupt.cpp',
                   sdk / 'src/os/OSAlarm.cpp',
                   game / 'src/aurora/lib/dolphin/os/OSAddress.cpp']
        result = subprocess.run([
            'clang++-21', '-std=c++23', '-D__ORBIS__', '-DTARGET_PC', '-pthread',
            '-ffunction-sections', '-fdata-sections', '-Wl,--gc-sections',
            '-I', str(sdk / 'include'), '-I', str(game / 'src/aurora/include'),
            '-I', str(platform / 'src/sdl3/include'), '-I', str(PLATFORM / 'game'),
            '-I', str(next((platform / 'src/fetch/fmt').glob('*/include'))),
            *map(str, sources), str(LOCATIONS.tests / 'route-audio.cpp'), '-o', str(cls.binary)
        ], capture_output=True, text=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)

    def run_scenario(self, scenario):
        result = subprocess.run([str(self.binary), scenario], capture_output=True,
                                text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_dma_converts_big_endian_right_left_pcm_and_joins_before_destroy(self):
        self.run_scenario('pcm')

    def test_format_failure_is_reported_and_retried_at_the_new_dsp_rate(self):
        self.run_scenario('format')

    def test_repeated_queue_drops_are_counted_without_stopping_dma_interrupts(self):
        self.run_scenario('drops')

    def test_queue_api_failure_is_reported(self):
        self.run_scenario('queue-error')

    def test_shutdown_reports_drain_failure_after_joining_the_producer(self):
        self.run_scenario('drain-error')
