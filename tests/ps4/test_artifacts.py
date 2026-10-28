"""Artifact inspection rejects a package changed after the build."""
import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from synthetic_game import prepare
from synthetic_program import png_bytes

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/pswaker'))
from build_inputs import Locations

LOCATIONS = Locations()


class ArtifactTests(unittest.TestCase):
    def test_changed_game_package_is_rejected_before_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'evidence').mkdir()
            (root / 'out/program').mkdir(parents=True)
            filename = 'IV0000-PSWK00001_00-PSWAKERGAME00000.pkg'
            (root / 'out/program' / filename).write_bytes(b'changed splash package')
            (root / 'evidence/game-program-artifacts.json').write_text(json.dumps({'package': {
                'filename': filename,
                'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'}}))
            report = root / 'evidence/game-program-inspection.json'
            report.write_text('{"previous": "success"}')
            result = subprocess.run([sys.executable, str(LOCATIONS.tools / 'inspect-game-program.py'),
                                     str(root), str(root / 'unavailable-platform')], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Package SHA-256 mismatch', result.stderr)
            self.assertFalse(report.exists())

    def test_changed_package_is_rejected_before_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'evidence').mkdir()
            (root / 'out').mkdir()
            (root / 'out/diagnostic.pkg').write_bytes(b'changed')
            (root / 'evidence/artifacts.json').write_text(json.dumps({'package': {
                'filename': 'diagnostic.pkg',
                'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'}}))
            result = subprocess.run([sys.executable, str(LOCATIONS.command('inspect-artifacts.py')), str(root)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Package SHA-256 mismatch', result.stderr)


@unittest.skipUnless(os.environ.get('PSWAKER_REFERENCE_BUILD') and shutil.which('clang++-21'),
                     'Set PSWAKER_REFERENCE_BUILD on Linux for real package inspection')
class GameArtworkInspectionTests(unittest.TestCase):
    def test_fresh_extraction_rejects_changed_splash_even_with_updated_package_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            platform, icon, splash, _ = prepare(root, os.environ['PSWAKER_REFERENCE_BUILD'], LOCATIONS)
            staged = subprocess.run([sys.executable, str(LOCATIONS.command('game-build.py')), 'stage', str(root),
                                     str(platform), '--icon', str(icon), '--splash', str(splash)],
                                    capture_output=True, text=True)
            self.assertEqual(staged.returncode, 0, staged.stderr)
            cli = [sys.executable, str(LOCATIONS.command('inspect-game-program.py')), str(root), str(platform)]
            inspected = subprocess.run(cli, capture_output=True, text=True)
            self.assertEqual(inspected.returncode, 0, inspected.stderr)
            record_path = root / 'evidence/game-program-artifacts.json'
            record = json.loads(record_path.read_text())
            package = root / 'out/program' / record['package']['filename']
            tampered = root / 'tampered-stage'
            shutil.copytree(root / 'build/program-stage', tampered)
            changed = png_bytes(1920, 1080, pixel=84)
            (tampered / 'sce_sys/pic1.png').write_bytes(changed)
            sdk = platform / 'sdk/opt/pacbrew/ps4/openorbis'
            subprocess.run([str(sdk / 'bin/linux/create-gp4'), '-out', 'pkg.gp4',
                            '--content-id=' + record['content_id'], '--path', '.'], cwd=tampered,
                           check=True, capture_output=True)
            package.unlink()
            subprocess.run([str(platform / 'build/pkgtool/PkgTool.Core'), 'pkg_build', 'pkg.gp4',
                            str(package.parent)], cwd=tampered, check=True, capture_output=True,
                           env=dict(os.environ, DOTNET_SYSTEM_GLOBALIZATION_INVARIANT='1'))
            record['package']['sha256'] = hashlib.sha256(package.read_bytes()).hexdigest()
            record_path.write_text(json.dumps(record))
            rejected = subprocess.run(cli, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('PIC1_PNG', rejected.stderr)
            self.assertFalse((root / 'evidence/game-program-inspection.json').exists())
            # Updating the stage inventory as well cannot bypass the embedded manifest.
            (root / 'build/program-stage/sce_sys/pic1.png').write_bytes(changed)
            record['program_stage_sha256']['sce_sys/pic1.png'] = hashlib.sha256(changed).hexdigest()
            record_path.write_text(json.dumps(record))
            rejected = subprocess.run(cli, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('PIC1_PNG: artwork differs from the program manifest', rejected.stderr)


if __name__ == '__main__':
    unittest.main()
