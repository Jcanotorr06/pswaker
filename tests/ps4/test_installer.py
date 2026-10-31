"""Install, launch, update and uninstall real data-free Windows candidates."""
import json
from contextlib import ExitStack
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from synthetic_disc import generate

REPOSITORY = Path(__file__).resolve().parents[2]
ISCC = os.environ.get('PSWAKER_ISCC')
TOOLS = os.environ.get('PSWAKER_WINDOWS_TOOLS')


@unittest.skipUnless(sys.platform == 'win32' and ISCC and TOOLS,
                     'Windows installer compiler and native tool closure required')
class InstalledApplicationTests(unittest.TestCase):
    def setUp(self):
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                    r'Software\Microsoft\Windows\CurrentVersion\Uninstall\{05802D72-13B7-4ABF-8FDE-7C917237D446}_is1'):
                self.skipTest('Preserve the existing per-user PSWaker installation')
        except FileNotFoundError:
            pass

    def test_offline_install_update_and_uninstall_preserve_owner_files(self):
        # CI may run elevated; standard-user evidence must record its actual token separately.
        with tempfile.TemporaryDirectory(prefix='pswaker-installed-test-') as folder, ExitStack() as cleanup:
            root = Path(folder)
            _, image = generate(root, REPOSITORY)
            env = dict(os.environ, PYTHONPATH=os.pathsep.join([
                str(root / 'repo/tools/pswaker'), str(REPOSITORY / 'tests/ps4')]))
            self.run_command([sys.executable, '-c',
                'from pathlib import Path; from synthetic_program import make_bundle; '
                'import sys; make_bundle(Path(sys.argv[1]), Path(sys.argv[2]))',
                str(root / 'bundle'), str(TOOLS)], env=env)
            install = root / 'installed'
            uninstalled = False
            def uninstall():
                nonlocal uninstalled
                uninstaller = install / 'unins000.exe'
                if not uninstalled and uninstaller.exists():
                    self.run_command([str(uninstaller), '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART'])
                    uninstalled = True
            cleanup.callback(uninstall)
            image_before = image.read_bytes()
            # This is the agreed packaging seam in an isolated, data-free app copy.
            # The production validator continues to reject this fixture.
            script = root / 'repo/tools/pswaker/build-installer.py'
            installed_versions = []
            packages = []
            for version in ['0.46.0.0', '0.46.1.0']:
                output = root / version
                self.run_command([sys.executable, str(script), '--program', str(root / 'bundle/program'),
                    '--packaging', str(TOOLS), '--assembly-assets', str(root / 'bundle/assembly-assets'),
                    '--app-version', version, '--iscc', str(ISCC),
                    '--output', str(output)])
                audit = json.loads((output / 'installer-release.json').read_text())
                installer = output / audit['installer']['filename']
                self.run_command([str(installer), '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART',
                                  '/SP-', '/DIR=' + str(install)])
                app = install / 'releases' / audit['release_directory'] / 'PSWaker.exe'
                installed_versions.append(app)
                # System-only PATH and absent external runtime: installed closure must suffice.
                offline = dict(os.environ, PATH=os.path.join(os.environ['SystemRoot'], 'System32'),
                               DOTNET_ROOT=str(root / 'absent-runtime'), PYTHONPATH='',
                               HTTP_PROXY='http://127.0.0.1:9', HTTPS_PROXY='http://127.0.0.1:9',
                               LOCALAPPDATA=str(root / 'local-state'))
                report_path = root / ('installed-' + version + '.json')
                self.run_command([str(app), '--check-installation', str(report_path)], env=offline, cwd=root)
                report = json.loads(report_path.read_text())
                self.assertEqual(report['app_version'], version)
                self.assertEqual(report['program_version'], '01.23')
                self.assertEqual(report['tool_revision'], '594021fdc435409f755a6ae0781b65ec6cec846c')
                self.assertEqual(report['title_id'], 'PSWK00001')
                runtime = app.parent / '_internal/packaging/coreclr.dll'
                backup = root / 'runtime-backup.dll'
                runtime.rename(backup)
                try:
                    rejected = root / ('rejected-' + version + '.json')
                    result = subprocess.run([str(app), '--check-installation', str(rejected)],
                                            env=offline, cwd=root, timeout=30)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(rejected.exists())
                finally:
                    backup.rename(runtime)
                # Exercise real installed UI controls, validation and fresh PKG inspection.
                from installed_ui import build_package
                package = build_package(app, image, root / ('owner-output-' + version), offline)
                self.assertTrue(package.is_file())
                packages.append((package, package.read_bytes()))
                inspection = json.loads((package.parent.parent / 'inspection.json').read_text())
                self.assertEqual(inspection['sfo']['CONTENT_ID'], 'IV0000-PSWK00001_00-PSWAKERGAME00000')
                self.assertEqual(inspection['sfo']['APP_VER'], '01.23')
                if version == '0.46.0.0':
                    # Unknown owner files inside the installation are never wildcard-deleted either.
                    (install / 'owner.txt').write_text('preserve this owner file')
            self.assertTrue(all(path.read_bytes() == content for path, content in packages))
            self.assertEqual(image.read_bytes(), image_before)
            uninstall()
            self.assertTrue(all(not app.exists() for app in installed_versions))
            self.assertFalse((install / 'releases').exists())
            self.assertEqual((install / 'owner.txt').read_text(), 'preserve this owner file')
            self.assertEqual(image.read_bytes(), image_before)
            self.assertTrue(all(path.read_bytes() == content for path, content in packages))
            self.assertTrue(package.is_file())

    def run_command(self, command, **kwargs):
        result = subprocess.run(command, capture_output=True, text=True, timeout=240, **kwargs)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
