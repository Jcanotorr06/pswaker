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
        assert REFERENCE is not None
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
        report = json.loads(result.stdout)
        self.assertEqual(set(report['package_files']), {
            'eboot.bin', 'build-info.json', 'sce_sys/icon0.png', 'sce_sys/param.sfo',
            'sce_sys/about/right.sprx', 'sce_module/libSceFios2.prx', 'sce_module/libc.prx', 'sce_sys/keystone'})
        entries = (self.root / 'evidence/package-entries.txt').read_text().splitlines()
        self.assertFalse(any(line.split() and line.split()[-1] == 'PIC1_PNG' for line in entries))

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


@unittest.skipUnless(REFERENCE and shutil.which('clang++-21') and shutil.which('dotnet'),
                     'Reference platform, Linux compiler and .NET SDK required')
class ProbePackagingTests(unittest.TestCase):
    def test_probe_builds_and_inspects_with_its_existing_diagnostic_resources(self):
        assert REFERENCE is not None
        with tempfile.TemporaryDirectory(prefix='pswaker-probe-package-') as folder:
            root, reference = Path(folder), Path(REFERENCE)
            (root / 'build/probe/platform_diagnostic_eboot').mkdir(parents=True)
            (root / 'src').mkdir()
            (root / 'evidence').mkdir()
            for name in ['sdk', 'refs']:
                (root / name).symlink_to(reference / name)
            for name in ['mesa', 'libdrm']:
                (root / 'src' / name).symlink_to(reference / 'src' / name)
            shutil.copytree(reference / 'src/liborbispkg', root / 'src/liborbispkg',
                            ignore=shutil.ignore_patterns('bin', 'obj', '.git'))
            packages = Path.home() / '.nuget/packages'
            if packages.is_dir():
                shutil.copytree(packages, root / 'nuget-packages')
            for name in ['source-archives.json', 'local-adaptations.json', 'renderer-reconciliation.json',
                         'sdk-rebuilt-archives.sha256']:
                shutil.copyfile(reference / 'evidence' / name, root / 'evidence' / name)
            cli = [sys.executable, str(LOCATIONS.command('package-probe.py')), str(root)]
            env = dict(os.environ, DOTNET_SYSTEM_GLOBALIZATION_INVARIANT='1')
            build_id = subprocess.check_output(cli + ['--identity-only'], text=True, env=env).strip()
            # Compile a disc-free fixture carrying the current packaging identity.
            source = root / 'synthetic.cpp'
            source.write_text(f'const char identity[] = "{build_id}"; int main() {{ return identity[0]; }}\n')
            subprocess.run(['clang++-21', '-g', str(source), '-o', str(root / 'build/probe/platform_diagnostic')],
                           check=True, capture_output=True)
            (root / 'build/probe/platform_diagnostic_eboot/eboot.bin').write_bytes(
                b'O\x15=\x1dSynthetic NONPLAYABLE diagnostic ' + build_id.encode())
            built = subprocess.run(cli, capture_output=True, text=True, env=env)
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            inspected = subprocess.run([sys.executable, str(LOCATIONS.command('inspect-artifacts.py')), str(root)],
                                       capture_output=True, text=True, env=env)
            self.assertEqual(inspected.returncode, 0, inspected.stderr)
            report = json.loads(inspected.stdout)
            self.assertEqual(set(report['package_files']), {
                'eboot.bin', 'build-info.json', 'sce_sys/icon0.png', 'sce_sys/param.sfo',
                'sce_sys/about/right.sprx', 'sce_module/libSceFios2.prx', 'sce_module/libc.prx', 'sce_sys/keystone'})
            icon = reference / 'refs/DolphinPS4/sce_sys/icon0.png'
            self.assertEqual(report['package_files']['sce_sys/icon0.png'], hashlib.sha256(icon.read_bytes()).hexdigest())
            self.assertEqual(report['sfo']['TITLE_ID'], 'PSWK00010')
            entries = (root / 'evidence/package-entries.txt').read_text().splitlines()
            self.assertFalse(any(line.split() and line.split()[-1] == 'PIC1_PNG' for line in entries))


if __name__ == '__main__':
    unittest.main()
