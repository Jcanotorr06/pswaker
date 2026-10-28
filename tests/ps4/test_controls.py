"""Installed input: real native reader and game-facing controls, fake console APIs only."""
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


@unittest.skipUnless(GAME and shutil.which('clang++-21'),
                     'Set PSWAKER_GAME_ROOT to the prepared game; Linux compiler required')
class InstalledControlsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix='pswaker-controls-')
        cls.addClassCleanup(cls.directory.cleanup)
        root = Path(cls.directory.name)
        cls.binary = root / 'controls'
        game = Path(GAME)
        includes = ['-I', str(PLATFORM / 'game'), '-I', str(game / 'src/platform'),
                    '-I', str(game / 'src/aurora/include'), '-DTARGET_PC']
        native = subprocess.run(['clang-21', '-std=c11', '-D_POSIX_C_SOURCE=200809L',
                                 *includes, '-c', str(game / 'src/platform/native/platform.c'),
                                 '-o', str(root / 'platform.o')], capture_output=True, text=True)
        if native.returncode:
            raise AssertionError(native.stderr)
        build = subprocess.run(['clang++-21', '-std=c++23', '-Wall', '-Wextra', '-Werror',
                                *includes, str(PLATFORM / 'game/controls.cpp'),
                                str(PLATFORM / 'game/storage.cpp'),
                                str(LOCATIONS.tests / 'controls-console.cpp'), str(root / 'platform.o'),
                                '-Wl,--wrap=scePadReadState', '-o', str(cls.binary)],
                               capture_output=True, text=True)
        if build.returncode:
            raise AssertionError(build.stderr)

    def check_scenario(self, name):
        with tempfile.TemporaryDirectory(prefix='pswaker-menu-profile-') as profile:
            result = subprocess.run([str(self.binary), name, profile], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_legend_confirmation_does_not_leak_into_game(self):
        self.check_scenario('legend')

    def test_port_text_setting_requires_separate_confirmations_and_pauses_game(self):
        self.check_scenario('text-setting')

    def test_gamecube_actions_sticks_and_analog_terminal_click(self):
        self.check_scenario('mapping')

    def test_lost_held_input_requires_fresh_release_and_deliberate_resume(self):
        self.check_scenario('disconnect')

    def test_failed_read_with_stale_payload_is_neutral_and_paused(self):
        self.check_scenario('failed-read')

    def test_port_menu_legend_cancel_and_explicit_quit(self):
        self.check_scenario('menus')

    def test_installed_menu_failed_read_check_enters_real_loss_path(self):
        self.check_scenario('fault-check')

    def test_loss_during_launch_or_confirmation_cannot_skip_the_legend(self):
        self.check_scenario('boot-loss')


if __name__ == '__main__':
    unittest.main()
