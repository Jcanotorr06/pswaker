"""Exercise artifact inspection through the real public SDK packaging tools."""
import hashlib
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
REFERENCE = os.environ.get('PSWAKER_REFERENCE_BUILD')


@unittest.skipUnless(REFERENCE, 'Set PSWAKER_REFERENCE_BUILD to an inspected build root')
class PackageRoundtripTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix='pswaker-package-test-')
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.reference = Path(REFERENCE)
        (self.root / 'evidence').mkdir()
        (self.root / 'build').mkdir()
        for directory in ['probe', 'pkgtool']:
            (self.root / 'build' / directory).symlink_to(self.reference / 'build' / directory)
        for filename in ['artifacts.json', 'build-info.json']:
            shutil.copyfile(self.reference / 'evidence' / filename, self.root / 'evidence' / filename)
        self.environment = dict(os.environ, DOTNET_SYSTEM_GLOBALIZATION_INVARIANT='1')

    def inspect(self):
        return subprocess.run([sys.executable, str(LOCATIONS.command('inspect-artifacts.py')), str(self.root)],
                              capture_output=True, text=True, env=self.environment)

    def test_real_package_is_accepted(self):
        (self.root / 'out').symlink_to(self.reference / 'out')
        result = self.inspect()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_extra_packaged_file_is_rejected(self):
        stage = self.root / 'stage'
        shutil.copytree(self.reference / 'build/probe-stage', stage)
        (stage / 'unexpected.txt').write_text('An unapproved payload file')
        output = self.root / 'out'
        output.mkdir()
        creator = self.reference / 'sdk/opt/pacbrew/ps4/openorbis/bin/linux/create-gp4'
        tool = self.reference / 'build/pkgtool/PkgTool.Core'
        artifacts = json.loads((self.root / 'evidence/artifacts.json').read_text())
        content_id = Path(artifacts['package']['filename']).stem
        subprocess.run([str(creator), '-out', 'pkg.gp4',
                        '--content-id=' + content_id, '--path', '.'],
                       cwd=stage, env=self.environment, check=True, stdout=subprocess.DEVNULL)
        built = subprocess.run([str(tool), 'pkg_build', str(stage / 'pkg.gp4'), str(output)],
                               cwd=stage, env=self.environment, capture_output=True, text=True)
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        package, = output.glob('*.pkg')
        with package.open('rb') as stream:
            artifacts['package'] = {'filename': package.name,
                                    'sha256': hashlib.file_digest(stream, 'sha256').hexdigest()}
        (self.root / 'evidence/artifacts.json').write_text(json.dumps(artifacts))
        result = self.inspect()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Unexpected package payload', result.stderr)


if __name__ == '__main__':
    unittest.main()
