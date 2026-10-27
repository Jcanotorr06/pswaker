"""Preparation CLI contracts, using real files at the download boundary."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import stat
import tarfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/pswaker'))
from build_inputs import Locations

LOCATIONS = Locations()


class InputTests(unittest.TestCase):
    def test_sdk_preparation_preserves_ps4_setjmp_directory_link(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            downloads = root / 'downloads/sdk-source'
            downloads.mkdir(parents=True)
            prefix = 'ps4-openorbis-musl-140a653299ffcb1457bc63a5ab1f507d7bb37c54'
            with zipfile.ZipFile(downloads / 'musl.zip', 'w') as archive:
                archive.writestr(prefix + '/src/setjmp/x86_64/registers.S', 'jump routines')
                link = zipfile.ZipInfo(prefix + '/src/setjmp/ps4')
                link.create_system = 3
                link.external_attr = (stat.S_IFLNK | 0o777) << 16
                archive.writestr(link, 'x86_64')
            with zipfile.ZipFile(downloads / 'openorbis.zip', 'w'):
                pass
            for filename, mode in [('llvm12.tar.xz', 'w:xz'), ('zlib.tar.gz', 'w:gz'),
                                   ('libpng.tar.xz', 'w:xz'), ('bzip2.tar.bz2', 'w:bz2')]:
                with tarfile.open(downloads / filename, mode):
                    pass
            result = subprocess.run([sys.executable, str(LOCATIONS.command('prepare-sdk-sources.py')), str(root)],
                                     capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            prepared = root / 'src/sdk-source/musl' / prefix / 'src/setjmp/ps4'
            self.assertTrue(prepared.is_dir(), 'The prepared PS4 jump-routine directory must resolve')
            self.assertEqual((prepared / 'registers.S').read_text(), 'jump routines')

    def test_unchanged_locked_download_is_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'downloads').mkdir()
            (root / 'downloads/source.tar').write_bytes(b'abc')
            lock = root / 'lock.json'
            lock.write_text(json.dumps({'archives': [{
                'path': 'source.tar', 'url': 'https://example.invalid/source.tar',
                'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'}]}))
            result = subprocess.run([sys.executable, str(LOCATIONS.command('inputs.py')), 'verify', str(root),
                                     '--lock', str(lock)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_changed_download_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'downloads').mkdir()
            (root / 'downloads/source.tar').write_bytes(b'changed')
            lock = root / 'lock.json'
            lock.write_text(json.dumps({'archives': [{
                'path': 'source.tar', 'url': 'https://example.invalid/source.tar',
                'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'}]}))
            result = subprocess.run([sys.executable, str(LOCATIONS.command('inputs.py')), 'verify', str(root),
                                     '--lock', str(lock)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('SHA-256 mismatch: source.tar', result.stderr)


if __name__ == '__main__':
    unittest.main()
