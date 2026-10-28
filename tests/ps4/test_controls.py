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
                                str(PLATFORM / 'game/controls-config.cpp'),
                                str(PLATFORM / 'game/storage.cpp'),
                                str(LOCATIONS.tests / 'controls-console.cpp'), str(root / 'platform.o'),
                                '-Wl,--wrap=scePadReadState', '-o', str(cls.binary)],
                               capture_output=True, text=True)
        if build.returncode:
            raise AssertionError(build.stderr)

    def check_scenario(self, name, contents=None):
        with tempfile.TemporaryDirectory(prefix='pswaker-menu-profile-') as profile:
            ini = Path(profile) / 'settings.ini'
            if contents is not None:
                ini.write_bytes(contents)
            result = subprocess.run([str(self.binary), name, profile], capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            if contents is not None:
                self.assertEqual(ini.read_bytes(), contents)
            elif name == 'profile-defaults':
                self.assertFalse(ini.exists())

    def test_legend_confirmation_does_not_leak_into_game(self):
        self.check_scenario('legend')

    def test_saved_layout_drives_gameplay_and_applied_legend(self):
        self.check_scenario('saved-layout')

    def test_every_action_on_all_nine_targets_and_legend_agreement(self):
        self.check_scenario('all-targets')

    def test_assignment_swap_free_and_noop_and_publication_generation(self):
        self.check_scenario('assignments')

    def test_concurrent_readers_observe_a_complete_applied_generation(self):
        self.check_scenario('coherent-snapshot')

    def test_fixed_inputs_and_recovery_under_custom_layout(self):
        for scenario in ['mapping', 'menus', 'disconnect', 'failed-read', 'boot-loss', 'fault-check']:
            with self.subTest(scenario=scenario):
                self.check_scenario('custom-' + scenario)

    def test_missing_controls_silently_use_defaults_without_creating_or_rewriting_settings(self):
        self.check_scenario('profile-defaults')
        self.check_scenario('profile-defaults', b'# legacy profile\r\nPSWAKER_LARGE_TEXT=0\r\n[dev]\r\nCOS_FPS60=1\r\n')

    def test_invalid_controls_use_complete_defaults_with_feedback_without_rewriting(self):
        complete = (b'[controls]\nversion=1\nA=L3\nB=R3\nX=L1\nY=Options\nZ=Cross\nStart=Circle\n'
                    b'invert_camera_x=1\ninvert_camera_y=1\n')
        cases = {
            'malformed': complete.replace(b'A=L3', b'A L3'),
            'incomplete': complete.replace(b'Start=Circle\n', b''),
            'missing-version': complete.replace(b'version=1\n', b''),
            'missing-axis': complete.replace(b'invert_camera_y=1\n', b''),
            'duplicate-target': complete.replace(b'B=R3', b'B=L3'),
            'duplicate-key': complete + b'A=L3\n',
            'duplicate-section': complete + complete,
            'reserved': complete.replace(b'A=L3', b'A=Touchpad'),
            'unsupported-button': complete.replace(b'A=L3', b'A=Share'),
            'unsupported-version': complete.replace(b'version=1', b'version=2'),
            'invalid-axis': complete.replace(b'invert_camera_x=1', b'invert_camera_x=On'),
            'unknown-action': complete + b'L=L2\n',
            'malformed-header': complete.replace(b'[controls]', b'[controls'),
            'empty-section': b'[controls]\n',
        }
        for case, contents in cases.items():
            with self.subTest(case=case):
                self.check_scenario('profile-fallback', b'PSWAKER_LARGE_TEXT=0\n' + contents + b'[dev]\nCOS_FPS60=1\n')

    def test_settings_read_failure_stays_a_storage_error_and_keeps_applied_controls(self):
        self.check_scenario('profile-read-failure')

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
