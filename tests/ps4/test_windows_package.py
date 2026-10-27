"""Real native Windows package round trips through the application boundary."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from synthetic_disc import generate

REPOSITORY = Path(__file__).resolve().parents[2]
TOOLS = os.environ.get('PSWAKER_WINDOWS_TOOLS')


@unittest.skipUnless(sys.platform == 'win32' and TOOLS, 'Native Windows tool closure required')
class WindowsPackageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='pswaker-windows-test-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        _, self.image = generate(self.root, REPOSITORY)

    def run_scenario(self, scenario):
        script = '''
import hashlib
import json
from pathlib import Path
import sys
from synthetic_program import make_bundle
from windows_package import create_package
root, tools = map(Path, sys.argv[1:])
bundle = make_bundle(root / 'bundle', tools)
image, output = root / 'synthetic.iso', root / 'private-complete'
original = image.read_bytes()
events = []
''' + scenario + '''
assert image.read_bytes() == original
'''
        env = dict(os.environ, PYTHONPATH=os.pathsep.join([
            str(self.root / 'repo/tools/pswaker'), str(REPOSITORY / 'tests/ps4')]))
        result = subprocess.run([sys.executable, '-c', script, str(self.root), str(TOOLS)],
                                env=env, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_native_roundtrip_publishes_freshly_verified_game_package(self):
        self.run_scenario('''
result = create_package(image, output, bundle, observe=events.append)
report = json.loads((output / 'inspection.json').read_text())
assert result['package'] == report['package']
assert report['sfo']['TITLE_ID'] == 'PSWK00001'
assert report['sfo']['CONTENT_ID'] == 'IV0000-PSWK00001_00-PSWAKERGAME00000'
assert report['sfo']['APP_VER'] == '01.23'
assert report['installed_image'] == '/app0/game.iso'
assert report['image']['sha256'] == hashlib.sha256(original).hexdigest()
assert report['program']['build_id'] == 'synthetic-program'
assert report['payload_sha256']['eboot.bin'] == hashlib.sha256(
    (bundle / 'program/stage/eboot.bin').read_bytes()).hexdigest()
assert [e['stage'] for e in events if e['event'] == 'passed'] == [
    'validate', 'verify-program', 'assemble', 'inspect', 'publish']
assert not (output / 'stage').exists()
assert not list(root.glob('.complete-*'))
assert (output / 'out' / report['package']['filename']).is_file()
''')

    def test_reinspection_rejects_changed_package_even_with_rehashed_assembly(self):
        self.run_scenario('''
from windows_package import inspect_output
result = create_package(image, output, bundle)
package = output / 'out' / result['package']['filename']
with package.open('r+b') as stream:
    stream.seek(0x40)
    stream.write(b'IV0000-FAIL00000')
assembly = json.loads((output / 'assembly.json').read_text())
assembly['package']['sha256'] = hashlib.sha256(package.read_bytes()).hexdigest()
(output / 'assembly.json').write_text(json.dumps(assembly))
try:
    inspect_output(output, bundle)
except ValueError as error:
    assert 'header content ID mismatch' in str(error), str(error)
else:
    raise AssertionError('Altered package passed fresh inspection')
assert not (output / 'inspection.json').exists()
''')

    def test_changed_image_during_copy_never_becomes_a_completed_package(self):
        self.run_scenario('''
def change_source(event):
    if event == {'stage': 'assemble', 'event': 'started'}:
        changed = bytearray(original)
        changed[0x7000:0x7003] = b'BAD'
        image.write_bytes(changed)
try:
    create_package(image, output, bundle, observe=change_source)
except ValueError as error:
    assert 'Full image SHA-1 mismatch' in str(error), str(error)
else:
    raise AssertionError('Changed image was accepted')
finally:
    image.write_bytes(original)
assert not output.exists()
assert not list(root.glob('.complete-*'))
''')

    def test_fresh_extraction_rejects_extra_packaged_files(self):
        self.run_scenario('''
import subprocess
import xml.etree.ElementTree as ET
from windows_package import inspect_output
result = create_package(image, output, bundle)
package = output / 'out' / result['package']['filename']
tool = bundle / 'packaging/PkgTool.Core.exe'
rebuilt = root / 'altered-output'
rebuilt.mkdir()
project_root = root / 'altered-project'
subprocess.run([str(tool), 'pkg_makegp4', str(package), str(project_root)], check=True, capture_output=True)
(project_root / 'unexpected.txt').write_text('unexpected private payload')
project = ET.parse(project_root / 'Project.gp4')
ET.SubElement(project.getroot().find('files'), 'file', targ_path='unexpected.txt', orig_path='unexpected.txt')
project.write(project_root / 'Project.gp4')
subprocess.run([str(tool), 'pkg_build', str(project_root / 'Project.gp4'), str(rebuilt)],
               check=True, capture_output=True)
package.write_bytes((rebuilt / package.name).read_bytes())
assembly = json.loads((output / 'assembly.json').read_text())
assembly['package']['sha256'] = hashlib.sha256(package.read_bytes()).hexdigest()
(output / 'assembly.json').write_text(json.dumps(assembly))
try:
    inspect_output(output, bundle)
except ValueError as error:
    assert 'Unexpected complete-package payload files' in str(error), str(error)
else:
    raise AssertionError('Unexpected packaged file passed fresh extraction')
assert not (output / 'inspection.json').exists()
''')

    def test_existing_and_racing_destinations_remain_unchanged(self):
        self.run_scenario('''
output.mkdir()
sentinel = output / 'previous.pkg'
sentinel.write_bytes(b'previous successful package')
try:
    create_package(image, output, bundle)
except ValueError as error:
    assert 'Output already exists' in str(error), str(error)
else:
    raise AssertionError('Existing destination was replaced')
assert sentinel.read_bytes() == b'previous successful package'
sentinel.unlink()
output.rmdir()
def racing_output(event):
    if event == {'stage': 'publish', 'event': 'started'}:
        output.mkdir()
        sentinel.write_bytes(b'newer successful package')
try:
    create_package(image, output, bundle, observe=racing_output)
except ValueError as error:
    assert 'Output appeared' in str(error), str(error)
else:
    raise AssertionError('Racing destination was replaced')
assert sentinel.read_bytes() == b'newer successful package'
assert not list(root.glob('.complete-*'))
''')

    def test_changed_program_or_tool_closure_cannot_create_a_package(self):
        self.run_scenario('''
for path in ['program/stage/eboot.bin', 'program/elf/game', 'packaging/LibOrbisPkg.Core.dll',
             'packaging/coreclr.dll', 'platform/ps4/content-contract.json']:
    target = bundle / path
    saved = target.read_bytes()
    target.write_bytes(saved + b'changed')
    try:
        create_package(image, output, bundle)
    except ValueError as error:
        assert 'Bundled release inputs changed' in str(error), str(error)
    else:
        raise AssertionError('Changed release was accepted: ' + path)
    finally:
        target.write_bytes(saved)
    assert not output.exists()
    assert not list(root.glob('.complete-*'))
''')


if __name__ == '__main__':
    unittest.main()
