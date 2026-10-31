"""Game preparation and installed-application boundaries; no game fixtures."""
import json
import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tarfile
import io
import unittest

from synthetic_program import png_bytes
from synthetic_game import prepare

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/pswaker'))
from build_inputs import Locations, maintained_inputs

LOCATIONS = Locations()
PLATFORM = LOCATIONS.platform
ARTWORK_HOST = sys.platform == 'linux' and importlib.util.find_spec('png') is not None


class GameStagingTests(unittest.TestCase):
    def test_artwork_paths_are_required_before_any_program_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for options, missing in [([], '--icon'), (['--icon', 'owner.png'], '--splash'),
                                     (['--splash', 'owner.png'], '--icon')]:
                with self.subTest(options=options):
                    result = subprocess.run([sys.executable, str(LOCATIONS.command('game-build.py')),
                                             'stage', str(root), str(root / 'platform'), *options],
                                            capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(missing, result.stderr)
                    self.assertFalse((root / 'build/program-stage').exists())
                    self.assertFalse((root / 'out/program').exists())

    @unittest.skipUnless(ARTWORK_HOST, 'Artwork decode requires the Linux python3-png host dependency')
    def test_invalid_artwork_rejects_restaging_and_preserves_previous_output_as_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            icon, splash = root / 'icon.png', root / 'splash.png'
            icon.write_bytes(png_bytes(512, 512))
            splash.write_bytes(png_bytes(1920, 1080))
            for path, resource in [(icon, 'ICON0_PNG'), (splash, 'PIC1_PNG')]:
                original = path.read_bytes()
                for invalid in [None, b'broken PNG', png_bytes(10, 10)]:
                    with self.subTest(resource=resource, invalid=invalid is None):
                        old = root / 'out/program/previous.pkg'
                        old.parent.mkdir(parents=True)
                        old.write_bytes(b'previous completed package')
                        previous_stage = root / 'build/program-stage'
                        previous_stage.mkdir(parents=True)
                        (previous_stage / 'eboot.bin').write_bytes(b'previous program')
                        if invalid is None:
                            path.unlink()
                        else:
                            path.write_bytes(invalid)
                        result = subprocess.run([sys.executable, str(LOCATIONS.command('game-build.py')),
                                                 'stage', str(root), str(root / 'platform'),
                                                 '--icon', str(icon), '--splash', str(splash)],
                                                capture_output=True, text=True)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn(resource, result.stderr)
                        self.assertFalse(previous_stage.exists())
                        self.assertFalse(old.parent.exists())
                        self.assertEqual(json.loads((root / 'evidence/game-staging-attempt.json').read_text())['status'],
                                         'failed')
                        self.assertTrue(any(p.read_bytes() == b'previous completed package' for p in
                                            (root / 'evidence/game-staging-history').rglob('previous.pkg')))
                        path.write_bytes(original)


@unittest.skipUnless(ARTWORK_HOST and os.environ.get('PSWAKER_REFERENCE_BUILD') and shutil.which('clang++-21'),
                     'Set PSWAKER_REFERENCE_BUILD on Linux for real program packaging')
class GameProgramPackageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='game-staging-test-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.platform, self.icon, self.splash, self.build_id = prepare(
            self.root, os.environ['PSWAKER_REFERENCE_BUILD'], LOCATIONS)

    def stage(self):
        return subprocess.run([sys.executable, str(LOCATIONS.command('game-build.py')), 'stage',
                               str(self.root), str(self.platform), '--app-version', '01.23',
                               '--icon', str(self.icon), '--splash', str(self.splash)], capture_output=True, text=True)

    def inspect(self):
        return subprocess.run([sys.executable, str(LOCATIONS.command('inspect-game-program.py')),
                               str(self.root), str(self.platform)], capture_output=True, text=True)

    def test_supplied_bytes_are_inspected_and_artwork_replacement_keeps_compiled_identity(self):
        configured = (self.root / 'evidence/game-build-inputs.json').read_bytes()
        for pixel in [42, 84]:
            with self.subTest(pixel=pixel):
                self.splash.write_bytes(png_bytes(1920, 1080, pixel=pixel))
                staged = self.stage()
                self.assertEqual(staged.returncode, 0, staged.stderr)
                inspected = self.inspect()
                self.assertEqual(inspected.returncode, 0, inspected.stderr)
                report = json.loads(inspected.stdout)
                evidence = json.loads((self.root / 'evidence/game-program-artifacts.json').read_text())
                manifest_text = (self.root / 'build/program-stage/build-info.json').read_text()
                self.assertNotIn(str(self.root), manifest_text)
                self.assertNotIn('source_path', manifest_text)
                self.assertEqual(report['compiled_build_id'], self.build_id)
                self.assertEqual(report['cache'], '/data/pswaker/cache/' + self.build_id)
                self.assertEqual((self.root / 'evidence/game-build-inputs.json').read_bytes(), configured)
                for resource, path, name in [('ICON0_PNG', self.icon, 'icon0.png'),
                                              ('PIC1_PNG', self.splash, 'pic1.png')]:
                    self.assertEqual(report['artwork'][resource]['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
                    self.assertEqual(evidence['artwork'][resource]['source_path'], str(path.resolve()))
                    self.assertEqual(report['package_files']['sce_sys/' + name],
                                     evidence['program_stage_sha256']['sce_sys/' + name])
        self.splash.write_bytes(b'replaced with invalid artwork')
        rejected = self.stage()
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn('PIC1_PNG', rejected.stderr)
        self.assertFalse((self.root / 'out/program').exists())
        self.assertFalse((self.root / 'evidence/game-program-inspection.json').exists())

    def test_failed_packager_publishes_no_partial_stage_or_package(self):
        script = self.platform / 'refs/DolphinPS4/scripts/make-pkg.sh'
        script.write_text('#!/bin/bash\nprintf partial > "$6/partial.pkg"\nexit 9\n')
        rejected = self.stage()
        self.assertNotEqual(rejected.returncode, 0)
        self.assertFalse((self.root / 'build/program-stage').exists())
        self.assertFalse((self.root / 'out/program').exists())
        self.assertFalse((self.root / 'evidence/game-program-artifacts.json').exists())
        attempt = json.loads((self.root / 'evidence/game-staging-attempt.json').read_text())
        self.assertEqual(attempt['status'], 'failed')


class GamePreparationTests(unittest.TestCase):
    def test_prepared_source_edits_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, path in maintained_inputs().items():
                target = root / 'repo' / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
            locations = Locations(root / 'repo')
            cli = locations.command('prepare-game.py')
            shutil.rmtree(locations.platform / 'patches/game')
            (root / 'downloads').mkdir()
            archive = root / 'downloads/switchwaker.tar.gz'
            with tarfile.open(archive, 'w:gz') as bundle:
                row = tarfile.TarInfo('source/README')
                row.size = 8
                bundle.addfile(row, io.BytesIO(b'original'))
            (locations.platform / 'game.lock.json').write_text(json.dumps({'sources': [{
                'name': 'switchwaker', 'repository': 'example/fixture', 'revision': 'a'*40,
                'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}]}))
            prepared = root / 'src/switchwaker'
            prepared.mkdir(parents=True)
            (prepared / 'README').write_text('unrecorded source edit')
            result = subprocess.run([sys.executable, str(cli), str(root)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('prepared source differs from pinned archive and patches', result.stderr)
            self.assertEqual((prepared / 'README').read_text(), 'unrecorded source edit')

    def test_changed_cached_source_is_rejected_before_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'downloads').mkdir()
            (root / 'downloads/switchwaker.tar.gz').write_bytes(b'changed archive')
            result = subprocess.run([sys.executable, str(LOCATIONS.command('prepare-game.py')), str(root)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('switchwaker: source archive SHA-256 mismatch', result.stderr)
            self.assertFalse((root / 'src/switchwaker').exists())


@unittest.skipUnless(shutil.which('clang++-21'), 'Linux host compiler required')
class InstalledApplicationTests(unittest.TestCase):
    @unittest.skipUnless(ARTWORK_HOST, 'Artwork decode requires the Linux python3-png host dependency')
    def test_build_staging_rejects_changed_dsp_reader_and_platform_headers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'game'
            platform = Path(directory) / 'platform'
            (root / 'evidence').mkdir(parents=True)
            source_files = {}
            for name in ['switchwaker', 'recompcore', 'ps5-reference']:
                path = root / 'src' / name / 'input.cpp'
                path.parent.mkdir(parents=True)
                path.write_bytes(b'original')
                source_files[name] = {'input.cpp': hashlib.sha256(b'original').hexdigest()}
            for name in ['aurora', 'platform']:
                (root / 'src' / name).mkdir()
            (root / 'assets/GZLE01').mkdir(parents=True)
            (root / 'evidence/game-inputs.json').write_text(json.dumps({
                'prepared_game': source_files['switchwaker'], 'prepared_sources': source_files,
                'stub_headers': {}, 'aurora': {}, 'platform': {}}))
            for archive in ['build/dawn/src/dawn/native/libwebgpu_dawn.a', 'build/sdl3/libSDL3.a']:
                path = platform / archive
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'fixture archive')
            header = platform / 'build/dawn/gen/include/webgpu/webgpu_cpp.h'
            header.parent.mkdir(parents=True)
            header.write_bytes(b'original header')
            cli = [sys.executable, str(LOCATIONS.command('game-build.py'))]
            icon, splash = root / 'icon.png', root / 'splash.png'
            icon.write_bytes(png_bytes(512, 512))
            splash.write_bytes(png_bytes(1920, 1080))
            configured = subprocess.run(cli + ['identity', str(root), str(platform)],
                                        capture_output=True, text=True)
            self.assertEqual(configured.returncode, 0, configured.stderr)
            for path in [root / 'src/recompcore/input.cpp',
                         root / 'src/ps5-reference/input.cpp', header]:
                with self.subTest(path=path):
                    before = path.read_bytes()
                    path.write_bytes(b'unrecorded change')
                    staged = subprocess.run(cli + ['stage', str(root), str(platform),
                                                   '--icon', str(icon), '--splash', str(splash)],
                                            capture_output=True, text=True)
                    self.assertNotEqual(staged.returncode, 0)
                    self.assertTrue('Prepared input changed' in staged.stderr or
                                    'Build inputs changed since configuration' in staged.stderr,
                                    staged.stderr)
                    path.write_bytes(before)

    def content_checker(self, root, data):
        """Compile the exact installed-content checker against a contract accepting `data`."""
        (root / 'image-contract.hpp').write_text(
            '#pragma once\n#include <cstdint>\n'
            f'constexpr uint64_t image_size = {len(data)};\n'
            f'constexpr const char* image_sha1[] = {{"{hashlib.sha1(data).hexdigest()}"}};\n')
        binary = root / 'content-check'
        build = subprocess.run(['clang++-21', '-std=c++20', '-DPSWAKER_HOST_CONTENT_CHECK',
                                '-I', str(root), str(PLATFORM / 'game/installed-content.cpp'),
                                '-o', str(binary)], capture_output=True, text=True)
        self.assertEqual(build.returncode, 0, build.stderr)
        return binary

    def test_installed_content_failures_stop_and_preserve_user_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = b'GZLE01\0\0' + bytes(range(256)) * 4096
            binary = self.content_checker(root, data)
            image = root / 'game.iso'
            saves = root / 'user/seed.gci'
            saves.parent.mkdir()
            saves.write_bytes(b'previous completed save')
            settings = root / 'user/settings.ini'
            settings.write_bytes(b'previous settings')
            for variant, payload in [('missing', None), ('truncated', data[:20]),
                                     ('invalid', data[:-1] + b'!'), ('valid', data)]:
                with self.subTest(variant=variant):
                    if payload is not None:
                        image.write_bytes(payload)
                    result = subprocess.run([str(binary), str(image)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0 if variant == 'valid' else 14)
                    if variant != 'valid':
                        self.assertIn('Rebuild', result.stderr)
                        self.assertIn('reinstall', result.stderr)
                    self.assertEqual(saves.read_bytes(), b'previous completed save')
                    self.assertEqual(settings.read_bytes(), b'previous settings')

    def test_full_image_check_runs_once_per_build_and_installed_image(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = b'GZLE01\0\0' + bytes(range(256)) * 4096
            binary = self.content_checker(root, data)
            image, manifest, record = root / 'game.iso', root / 'complete-package.json', root / 'image-check.txt'
            image.write_bytes(data)
            manifest.write_text('{"image": "owner image A"}\n')

            def check(build='build-1', record=record):
                result = subprocess.run([str(binary), str(image), str(manifest), str(record), build],
                                        capture_output=True, text=True)
                return result.returncode, result.stdout.strip(), result.stderr

            self.assertEqual(check(), (0, 'Installed image verified; full check recorded', ''))
            self.assertIn('build=build-1', record.read_text())
            self.assertEqual(check(), (0, 'Installed image verified by recorded full check', ''))

            # Size and file type are still checked on every launch.
            image.write_bytes(data[:-1])
            code, _, error = check()
            self.assertEqual(code, 14)
            self.assertIn('invalid size', error)

            # The same installed file under a new build or package manifest is hashed again.
            image.write_bytes(data)
            stat = image.stat()
            image.write_bytes(data[:-1] + b'!')
            os.utime(image, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            for build, contents in [('build-2', '{"image": "owner image A"}\n'),
                                    ('build-1', '{"image": "owner image B"}\n')]:
                with self.subTest(build=build, manifest=contents):
                    manifest.write_text(contents)
                    code, _, error = check(build)
                    self.assertEqual(code, 14)
                    self.assertIn('checksum is invalid', error)
                    self.assertIn('build=build-1', record.read_text())

            image.write_bytes(data)
            self.assertEqual(check('build-2'), (0, 'Installed image verified; full check recorded', ''))
            self.assertIn('build=build-2', record.read_text())

            # Without a readable manifest or a writable record, every launch hashes the image.
            manifest.unlink()
            self.assertEqual(check('build-2'), (0, 'Installed image verified; full check not recorded', ''))
            manifest.write_text('{"image": "owner image B"}\n')
            unwritable = root / 'missing-directory/image-check.txt'
            for _ in range(2):
                self.assertEqual(check('build-3', unwritable),
                                 (0, 'Installed image verified; full check not recorded', ''))


if __name__ == '__main__':
    unittest.main()
