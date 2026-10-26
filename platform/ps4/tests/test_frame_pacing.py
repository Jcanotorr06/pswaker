"""Public exported-record and summary-CLI seams; console services are the boundary."""
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]


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
        tables = [('frames.csv', 'flip_count,process_time,tsc,observed_ns,flip_argument,game_frame,sample,stage,room,submit_ns,shader_ns,shader_calls', self.frames),
                  ('events.csv', 'monotonic_ns,kind,detail,sample', self.events + [[self.tick * 1000000000 // 30000 + 3000000, 'shutdown', 'complete', 0]]),
                  ('samples.csv', 'sample,scene,outcome,seconds,intervals', self.samples)]
        for name, header, rows in tables:
            with (self.run / name).open('w', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow(header.split(','))
                writer.writerows(rows)
        result = subprocess.run([sys.executable, str(HERE / 'frame-pacing.py'), str(self.run),
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
                                 '-I', str(HERE / 'game'), str(HERE / 'game/frame-pacing.cpp'),
                                 str(HERE / 'tests/frame-pacing.cpp'), '-o', str(cls.binary)],
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
