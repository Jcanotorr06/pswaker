"""Game preparation and installed-application boundaries; no game fixtures."""
import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tarfile
import io
import unittest

HERE = Path(__file__).resolve().parents[1]


class GamePreparationTests(unittest.TestCase):
    def test_prepared_source_edits_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cli = root / 'tools/prepare-game.py'
            cli.parent.mkdir()
            shutil.copyfile(HERE / 'prepare-game.py', cli)
            (root / 'downloads').mkdir()
            archive = root / 'downloads/switchwaker.tar.gz'
            with tarfile.open(archive, 'w:gz') as bundle:
                row = tarfile.TarInfo('source/README')
                row.size = 8
                bundle.addfile(row, io.BytesIO(b'original'))
            (cli.parent / 'game.lock.json').write_text(json.dumps({'sources': [{
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
            result = subprocess.run([sys.executable, str(HERE / 'prepare-game.py'), str(root)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('switchwaker: source archive SHA-256 mismatch', result.stderr)
            self.assertFalse((root / 'src/switchwaker').exists())


@unittest.skipUnless(shutil.which('clang++-21'), 'Linux host compiler required')
class InstalledApplicationTests(unittest.TestCase):
    def test_installed_content_failures_stop_and_preserve_user_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = b'GZLE01\0\0' + bytes(range(256)) * 4096
            (root / 'image-contract.hpp').write_text(
                '#pragma once\n#include <cstdint>\n'
                f'constexpr uint64_t image_size = {len(data)};\n'
                f'constexpr const char* image_sha1[] = {{"{hashlib.sha1(data).hexdigest()}"}};\n')
            binary = root / 'content-check'
            build = subprocess.run(['clang++-21', '-std=c++20', '-DPSWAKER_HOST_CONTENT_CHECK',
                                    '-I', str(root), str(HERE / 'game/installed-content.cpp'),
                                    '-o', str(binary)], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
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


if __name__ == '__main__':
    unittest.main()
