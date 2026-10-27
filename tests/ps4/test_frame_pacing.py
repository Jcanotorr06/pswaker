"""Public exported-record and summary-CLI seams; console services are the boundary."""
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/pswaker'))
from build_inputs import Locations

LOCATIONS = Locations()
PLATFORM = LOCATIONS.platform


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='pswaker-pacing-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.run = self.root / 'run'
        self.run.mkdir()
        self.identity = dict(schema=1, build='synthetic', tsc_frequency=30000,
                             method='VideoOut-completed-flip-tsc', internal=[1280, 720],
                             logic_hz=30, textures='stock')
        self.inspection = dict(program=dict(build_id='synthetic'), package=dict(sha256='synthetic'))
        self.owner = dict(build='synthetic', package_sha256='synthetic',
                          platform=dict(model='PS4 Slim', firmware='9.00', goldhen='v2.4b18'),
                          cache_state='cold', timing_method_verified=True, samples={})
        self.frames, self.events, self.samples = [], [], []
        self.tick = 0

    def sample(self, number, scene, hitch=False):
        stage, room = ('sea', 44) if scene == 'outset' else ('A_mori', 0)
        start = self.tick * 1000000000 // 30000
        self.events += [[start, 'sample-arm', scene, number], [start + 1, 'sample-resume', scene, number]]
        first = None
        for frame in range(3601):
            self.tick += 6000 if hitch and frame == 100 else 1000
            if first is None:
                first = self.tick
            count = len(self.frames) + 1
            ns = self.tick * 1000000000 // 30000
            self.frames.append([count, ns // 1000, self.tick, ns + 1000000, count,
                                frame + 1, number, stage, room, ns - 1000000, 0, 0])
        self.events.append([ns + 2000000, 'sample-end', 'complete', number])
        self.samples.append([number, scene, 'complete', f'{(self.tick - first) / 30000:.6f}', 3600])
        self.owner['samples'][str(number)] = dict(scene=scene, actions='synthetic comparable actions',
                                                active_gameplay=True, graphics_audio_correct=True)

    def analyze(self):
        for name, value in [('identity.json', self.identity), ('inspection.json', self.inspection),
                            ('owner.json', self.owner)]:
            (self.run / name).write_text(json.dumps(value))
        frame_header = 'flip_count,process_time,tsc,observed_ns,flip_argument,game_frame,sample,stage,room,submit_ns,shader_ns,shader_calls'
        if getattr(self, 'calibrated', False):
            frame_header += ',read_tsc'
        tables = [('frames.csv', frame_header, self.frames),
                  ('events.csv', 'monotonic_ns,kind,detail,sample', self.events + [[self.tick * 1000000000 // 30000 + 3000000, 'shutdown', 'complete', 0]]),
                  ('samples.csv', 'sample,scene,outcome,seconds,intervals', self.samples)]
        for name, header, rows in tables:
            with (self.run / name).open('w', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow(header.split(','))
                writer.writerows(rows)
        result = subprocess.run([sys.executable, str(LOCATIONS.command('frame-pacing.py')), str(self.run),
                                 '--inspection', str(self.run / 'inspection.json'),
                                 '--owner', str(self.run / 'owner.json'), '--output', str(self.root / 'analysis')],
                                capture_output=True, text=True)
        report = json.loads(result.stdout) if result.stdout else None
        return result, report

    def test_missing_resume_boundary_cannot_be_reported_as_a_pass(self):
        self.sample(1, 'outset')
        self.sample(2, 'forest')
        self.events = [row for row in self.events if row[1] != 'sample-resume']
        result, report = self.analyze()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertTrue(all(not sample['target_met'] for sample in report['samples']))

    def test_delayed_ui_observation_uses_read_clock_without_changing_frame_intervals(self):
        self.sample(1, 'outset')
        self.tick += 1000
        count = len(self.frames) + 1
        ns = self.tick * 1000000000 // 30000
        self.frames.append([count, ns // 1000, self.tick, ns + 161000000,
                            count, 0, 0, 'sea', 44, ns - 1000000, 0, 0])
        self.tick += 6000
        self.sample(2, 'forest')
        self.calibrated = True
        for frame in self.frames:
            frame.append(frame[3] * 30000 // 1000000000)
        result, report = self.analyze()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(all(sample['target_met'] for sample in report['samples']))
        self.assertEqual(report['samples'][0]['metrics']['maximum_ms'], 1000 / 30)

    def test_kernel_clock_disagreement_cannot_pass_with_calibrated_records(self):
        self.sample(1, 'outset')
        self.sample(2, 'forest')
        self.calibrated = True
        for frame in self.frames:
            frame.append(frame[2] + 30)
        self.frames[100][-1] += 6000
        result, report = self.analyze()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('flip timestamp rate differs from monotonic observation clock',
                      report['samples'][0]['invalid_reasons'])

    def test_future_flip_timestamp_cannot_pass_with_calibrated_records(self):
        self.sample(1, 'outset')
        self.calibrated = True
        for frame in self.frames:
            frame.append(frame[2] + 30)
        self.frames[100][-1] = self.frames[100][2] - 1
        result, report = self.analyze()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('flip timestamp is later than kernel clock read', report['samples'][0]['invalid_reasons'])

    def test_backward_kernel_clock_read_cannot_pass_with_calibrated_records(self):
        self.sample(1, 'outset')
        self.calibrated = True
        for frame in self.frames:
            frame.append(frame[2] + 30)
        # A late read followed by a backward read remains within the rate-check
        # tolerance and after both completions, but is not a monotonic clock.
        self.frames[100][-1] += 2000
        result, report = self.analyze()
        self.assertEqual(result.returncode, 2)
        self.assertIn('nonmonotonic kernel clock read', report['samples'][0]['invalid_reasons'])

    def test_a_presentation_arriving_after_pause_stays_in_launch_but_outside_sample(self):
        self.sample(1, 'outset')
        self.samples[0][2] = self.events[-1][2] = 'paused'
        late = self.frames[-1].copy()
        late[0] += 1
        late[2] += 1000
        late[3] += 33333333
        late[4] += 1
        late[5] += 1
        late[9] += 33333333
        self.frames.append(late)
        self.tick += 1000
        result, report = self.analyze()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report['samples'][0]['metrics']['intervals'], 3600)
        self.assertEqual(report['samples'][0]['outside_boundary_presentations'], 1)
        with (self.root / 'analysis/raw-launch/frames.csv').open() as stream:
            self.assertEqual(len(list(csv.DictReader(stream))), 3602)

    def test_two_independent_30_hz_samples_preserve_raw_evidence(self):
        self.sample(1, 'outset')
        self.sample(2, 'forest')
        result, report = self.analyze()
        self.assertEqual(result.returncode, 0, result.stderr)
        for sample in report['samples']:
            self.assertEqual(sample['metrics']['average_fps'], 30)
            self.assertAlmostEqual(sample['metrics']['p95_ms'], 33.3333333333)
            self.assertTrue(sample['target_met'])
        self.assertEqual((self.root / 'analysis/raw-launch/frames.csv').read_bytes(), (self.run / 'frames.csv').read_bytes())
        self.assertEqual(len(json.loads((self.root / 'analysis/sample-002-forest-raw.json').read_text())), 3601)

    def test_a_forest_freeze_is_not_hidden_by_good_outset_or_average_fps(self):
        self.sample(1, 'outset')
        self.sample(2, 'forest', hitch=True)
        result, report = self.analyze()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertTrue(report['samples'][0]['target_met'])
        forest = report['samples'][1]
        self.assertGreater(forest['metrics']['average_fps'], 29.5)
        self.assertEqual(forest['shortfalls'], [{'metric': 'maximum_ms', 'measured': 200, 'limit': 100}])

    def test_unverified_timing_retains_metrics_but_cannot_pass(self):
        self.sample(1, 'outset')
        self.sample(2, 'forest')
        self.owner['timing_method_verified'] = False
        result, report = self.analyze()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertTrue(all(not sample['target_met'] for sample in report['samples']))
        self.assertIn('unverified', report['samples'][0]['invalid_reasons'][0])

    def test_partial_sample_and_missing_scene_are_retained(self):
        self.sample(1, 'outset')
        self.samples[0][2] = 'paused'
        self.events[-1][2] = 'paused'
        result, report = self.analyze()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(report['missing_scenes'], ['forest'])
        self.assertFalse(report['samples'][0]['target_met'])
        self.assertIn('sample incomplete: paused', report['samples'][0]['invalid_reasons'])

    def test_missed_completion_and_wrong_scene_labels_cannot_pass(self):
        self.sample(1, 'outset')
        self.sample(2, 'forest')
        self.frames[100][0] += 1
        self.frames[-1][7:9] = ['sea', 44]
        result, report = self.analyze()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('missing or duplicated flip completion', report['samples'][0]['invalid_reasons'])
        self.assertIn('scene label does not match game stage/room', report['samples'][1]['invalid_reasons'])

    def test_installed_binary_identity_must_match(self):
        self.sample(1, 'outset')
        self.owner['build'] = 'another-binary'
        result, report = self.analyze()
        self.assertEqual(result.returncode, 1)
        self.assertIsNone(report)
        self.assertIn('identity must match', result.stderr)

    def test_nearest_rank_percentiles_accept_exact_interval_limits(self):
        self.sample(1, 'outset')
        tick = 1000
        durations = [1000] * 3419 + [1050] * 144 + [1500] * 36 + [3000]
        for row, duration in zip(self.frames[1:], durations):
            tick += duration
            row[2] = tick
            row[1] = tick * 1000000 // 30000
            row[3] = tick * 1000000000 // 30000 + 1000000
            row[9] = row[3] - 2000000
        self.tick = tick
        self.samples[0][3] = '120.906667'
        self.events[-1][0] = tick * 1000000000 // 30000 + 2000000
        result, report = self.analyze()
        self.assertEqual(result.returncode, 2)  # Forest is intentionally absent.
        metrics = report['samples'][0]['metrics']
        self.assertEqual((metrics['p95_ms'], metrics['p99_ms'], metrics['maximum_ms']), (35, 50, 100))
        self.assertTrue(report['samples'][0]['target_met'])


@unittest.skipUnless(shutil.which('clang++-21'), 'Linux host compiler required')
class RecorderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix='pswaker-pacing-native-')
        cls.addClassCleanup(cls.directory.cleanup)
        cls.binary = Path(cls.directory.name) / 'recorder'
        result = subprocess.run(['clang++-21', '-std=c++23', '-pthread', '-Wall', '-Wextra', '-Werror',
                                 '-I', str(PLATFORM / 'game'), str(PLATFORM / 'game/frame-pacing.cpp'),
                                 str(LOCATIONS.tests / 'frame-pacing.cpp'), '-Wl,--wrap=fflush', '-o', str(cls.binary)],
                                capture_output=True, text=True)
        if result.returncode:
            raise AssertionError(result.stderr)

    def test_repeated_refreshes_and_first_baseline_are_not_extra_game_frames(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([str(self.binary), directory, 'boundary'], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            run = next(Path(directory).glob('performance-*'))
            with (run / 'frames.csv').open() as stream:
                frames = list(csv.DictReader(stream))
            with (run / 'samples.csv').open() as stream:
                samples = list(csv.DictReader(stream))
            self.assertEqual([f['game_frame'] for f in frames], ['1', '2', '3', '0'])
            self.assertEqual(samples[0]['outcome'], 'complete')
            self.assertEqual(float(samples[0]['seconds']), 120)
            self.assertEqual(int(samples[0]['intervals']), 2)
            self.assertEqual(float(samples[0]['maximum_ms']), 119000)
            self.assertEqual(samples[0]['shader_correlated_hitches'], '1')
            self.assertEqual(samples[0]['target_met'], '0')

    def test_paused_sample_survives_a_separate_forest_attempt(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([str(self.binary), directory, 'pause'], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            run = next(Path(directory).glob('performance-*'))
            with (run / 'samples.csv').open() as stream:
                samples = list(csv.DictReader(stream))
            self.assertEqual([(s['scene'], s['outcome']) for s in samples], [('outset', 'paused'), ('forest', 'complete')])

    def test_missing_console_completion_is_exported_as_invalid(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([str(self.binary), directory, 'missing'], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            run = next(Path(directory).glob('performance-*'))
            with (run / 'samples.csv').open() as stream:
                samples = list(csv.DictReader(stream))
            self.assertEqual(samples[0]['outcome'], 'invalid')
            self.assertIn('missed-flip-completion', (run / 'events.csv').read_text())

    def test_late_ui_observation_does_not_disable_later_forest_sampling(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([str(self.binary), directory, 'late-observation'], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            run = next(Path(directory).glob('performance-*'))
            with (run / 'samples.csv').open() as stream:
                samples = list(csv.DictReader(stream))
            self.assertEqual([(s['scene'], s['outcome']) for s in samples], [('outset', 'complete'), ('forest', 'complete')])
            self.assertIn('observer-delay-ns', (run / 'events.csv').read_text())

    def test_slow_storage_does_not_block_recording_and_shutdown_drains_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([str(self.binary), directory, 'slow-storage'], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            run = next(Path(directory).glob('performance-*'))
            with (run / 'frames.csv').open() as stream:
                frames = list(csv.DictReader(stream))
            self.assertEqual([row['game_frame'] for row in frames], ['1', '2'])
            self.assertIn('shutdown,complete', (run / 'events.csv').read_text())

    def test_storage_failure_and_queue_exhaustion_export_invalid_evidence(self):
        for scenario in ('storage-error', 'queue-overflow'):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as directory:
                result = subprocess.run([str(self.binary), directory, scenario], capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                run = next(Path(directory).glob('performance-*'))
                self.assertIn('invalid,evidence-writer', (run / 'events.csv').read_text())

    def test_arming_excludes_ui_but_retains_first_game_frame_shader_wait(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([str(self.binary), directory, 'ui'], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            run = next(Path(directory).glob('performance-*'))
            with (run / 'frames.csv').open() as stream:
                frames = list(csv.DictReader(stream))
            with (run / 'events.csv').open() as stream:
                events = list(csv.DictReader(stream))
            self.assertEqual([(f['game_frame'], f['sample']) for f in frames], [('0', '0'), ('1', '1'), ('2', '1')])
            self.assertEqual([e['sample'] for e in events if e['kind'] == 'shader-wait-ns'], ['0', '1'])

    @unittest.skipUnless(os.environ.get('PSWAKER_GAME_ROOT'), 'Prepared native platform required')
    def test_periodic_diagnostics_preserve_file_evidence_without_stalling_presentations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            platform = Path(os.environ['PSWAKER_GAME_ROOT']) / 'src/platform'
            compiled = subprocess.run(['clang-21', '-std=c11', '-D_POSIX_C_SOURCE=200809L',
                '-DPS4_DEV_TOOLS=0', '-ffunction-sections', '-fdata-sections', '-I', str(platform),
                '-c', str(platform / 'native/platform.c'), '-o', str(root / 'platform.o')],
                capture_output=True, text=True)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            linked = subprocess.run(['clang++-21', '-std=c++23', '-pthread', '-Wall', '-Wextra', '-Werror',
                '-DPSWAKER_TEST_PLATFORM_LOGGER', '-Wl,--gc-sections', '-I', str(PLATFORM / 'game'),
                str(PLATFORM / 'game/frame-pacing.cpp'), str(LOCATIONS.tests / 'frame-pacing.cpp'),
                str(root / 'platform.o'), '-Wl,--wrap=fflush', '-o', str(root / 'recorder')], capture_output=True, text=True)
            self.assertEqual(linked.returncode, 0, linked.stderr)
            result = subprocess.run([str(root / 'recorder'), directory, 'diagnostics'],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            run = next(root.glob('performance-*'))
            with (run / 'frames.csv').open() as stream:
                frames = list(csv.DictReader(stream))
            self.assertEqual((int(frames[1]['tsc']) - int(frames[0]['tsc'])), 33,
                             'Periodic diagnostics delayed the next game presentation')
            self.assertEqual(result.stderr.splitlines(), [f'heartbeat-evidence-{i}' for i in range(7)])

    def test_diagnostic_costs_are_exported_with_the_active_sample(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([str(self.binary), directory, 'diagnostic-cost'], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            run = next(Path(directory).glob('performance-*'))
            with (run / 'events.csv').open() as stream:
                events = list(csv.DictReader(stream))
            costs = [e for e in events if e['kind'] in ('diagnostic-heartbeat-ns', 'diagnostic-input-ns')]
            self.assertEqual([(e['kind'], e['sample']) for e in costs],
                             [('diagnostic-heartbeat-ns', '1'), ('diagnostic-input-ns', '1')])
            self.assertGreaterEqual(int(costs[0]['detail']), 44000000)
            self.assertGreaterEqual(int(costs[1]['detail']), 10000000)
