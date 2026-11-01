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
        includes = ['-I', str(PLATFORM / 'game'), '-I', str(PLATFORM / 'game/include'),
                    '-I', str(game / 'src/platform'),
                    '-I', str(game / 'src/aurora/include'),
                    '-I', str(game / 'src/switchwaker/native/include'),
                    '-I', str(game / 'src/switchwaker/native/src/pc'), '-DTARGET_PC']
        native = subprocess.run(['clang-21', '-std=c11', '-D_POSIX_C_SOURCE=200809L',
                                 *includes, '-c', str(game / 'src/platform/native/platform.c'),
                                 '-o', str(root / 'platform.o')], capture_output=True, text=True)
        if native.returncode:
            raise AssertionError(native.stderr)
        build = subprocess.run(['clang++-21', '-std=c++23', '-Wall', '-Wextra', '-Werror',
                                *includes, str(PLATFORM / 'game/controls.cpp'),
                                str(PLATFORM / 'game/controls-config.cpp'),
                                str(PLATFORM / 'game/prompts.cpp'),
                                str(PLATFORM / 'game/prompt-art.cpp'),
                                str(PLATFORM / 'game/message-prompts.cpp'),
                                str(PLATFORM / 'game/storage.cpp'),
                                str(game / 'src/switchwaker/native/src/pc/features/pc_controls.cpp'),
                                str(LOCATIONS.tests / 'controls-console.cpp'), str(root / 'platform.o'),
                                '-Wl,--wrap=scePadReadState', '-Wl,--wrap=fsync',
                                '-Wl,--wrap=close', '-Wl,--wrap=rename', '-o', str(cls.binary)],
                               capture_output=True, text=True)
        if build.returncode:
            raise AssertionError(build.stderr)

    def check_scenario(self, name, contents=None):
        with tempfile.TemporaryDirectory(prefix='pswaker-menu-profile-') as profile:
            ini = Path(profile) / 'settings.ini'
            untouched = {}
            if name.startswith('restore-'):
                for relative in ['saves/USA/Card A/synthetic-progress.txt', 'cache/synthetic-build/pipelines.bin']:
                    path = Path(profile) / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    untouched[path] = b'synthetic preservation sentinel\n'
                    path.write_bytes(untouched[path])
            if contents is not None:
                ini.write_bytes(contents)
            result = subprocess.run([str(self.binary), name, profile], capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for path, expected in untouched.items():
                self.assertEqual(path.read_bytes(), expected)
            if contents is not None:
                self.assertEqual(ini.read_bytes(), contents)
            elif name == 'profile-defaults':
                self.assertFalse(ini.exists())

    def test_legend_confirmation_does_not_leak_into_game(self):
        self.check_scenario('legend')

    def test_prompts_refresh_before_resume_and_preserve_previous_generation_after_discard_or_failed_apply(self):
        for scenario in ['apply', 'discard', 'failure', 'uncertain']:
            with self.subTest(scenario=scenario):
                self.check_scenario('prompt-' + scenario)

    def test_independent_inversion_switches_are_pending_and_require_fresh_confirmation(self):
        self.check_scenario('inversion-pending')

    def test_camera_apis_follow_complete_publication_and_reloaded_preferences(self):
        for axes in ['neither', 'x', 'y', 'both']:
            with self.subTest(axes=axes):
                self.check_scenario('inversion-apply-' + axes)

    def test_inversion_discard_failed_and_uncertain_apply_keep_camera_apis_on_previous_generation(self):
        for axes in ['neither', 'x', 'y', 'both']:
            for fault in ['discard', 'sync', 'close', 'rename', 'uncertain', 'failed-discard', 'uncertain-discard']:
                with self.subTest(axes=axes, fault=fault):
                    self.check_scenario('inversion-apply-' + axes + '-' + fault)

    def test_editor_pending_swap_apply_publication_and_neutral_resume(self):
        self.check_scenario('editor-apply')

    def test_restore_confirmation_cancel_preserves_existing_pending_edits(self):
        self.check_scenario('restore-cancel')

    def test_restore_then_discard_keeps_applied_controls_profile_and_neutral_resume(self):
        self.check_scenario('restore-discard')

    def test_restore_then_apply_saves_and_publishes_complete_defaults_together(self):
        self.check_scenario('restore-apply')

    def test_restore_failed_and_uncertain_apply_preserve_applied_controls_and_offer_retry_or_discard(self):
        for fault in ['sync', 'close', 'rename', 'uncertain', 'discard', 'uncertain-discard']:
            with self.subTest(fault=fault):
                self.check_scenario('restore-fail-' + fault)

    def test_controller_loss_during_restore_requires_fresh_confirmation_and_preserves_pending_controls(self):
        self.check_scenario('restore-loss')

    def test_editor_reaches_every_action_and_target_and_applies_gameplay_mapping(self):
        self.check_scenario('editor-all-targets')

    def test_controller_loss_preserves_pending_edits_and_requires_fixed_confirmation_in_each_editor_state(self):
        self.check_scenario('editor-loss')

    def test_editor_noop_unused_assignment_leave_keep_editing_and_discard(self):
        self.check_scenario('editor-discard')

    def test_editor_failed_and_uncertain_apply_keep_applied_controls_and_allow_retry_or_discard(self):
        for fault in ['sync', 'close', 'rename', 'uncertain', 'discard']:
            with self.subTest(fault=fault):
                self.check_scenario('editor-fail-' + fault)

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
