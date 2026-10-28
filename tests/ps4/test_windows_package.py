"""Real native Windows package round trips through the application boundary."""
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
        env = dict(os.environ, LOCALAPPDATA=str(self.root / 'local-state'), PYTHONPATH=os.pathsep.join([
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
    'validate', 'prepare', 'verify-program', 'assemble', 'inspect', 'publish']
assert not (output / 'stage').exists()
assert not list(root.glob('.complete-*'))
assert (output / 'out' / report['package']['filename']).is_file()
''')

    def test_cancellation_at_each_stage_preserves_packages_and_allows_fresh_retry(self):
        self.run_scenario('''
from build_operation import BuildCancelled, BuildOperation
prior = root / 'prior-complete'
prior_result = create_package(image, prior, bundle)
prior_package = prior / 'out' / prior_result['package']['filename']
prior_hash = hashlib.sha256(prior_package.read_bytes()).hexdigest()
for stage in ['validate', 'verify-program', 'assemble', 'inspect', 'publish']:
    events = []
    def cancel_at_stage(event):
        events.append(event)
        if event['stage'] == stage and event['event'] == ('started' if stage == 'publish' else 'progress'):
            operation.cancel()
    operation = BuildOperation(cancel_at_stage)
    try:
        create_package(image, output, bundle, operation=operation)
    except BuildCancelled:
        pass
    else:
        raise AssertionError('Cancellation published a result: ' + stage)
    assert not output.exists()
    assert not list(root.glob('.complete-*'))
    assert image.read_bytes() == original
    assert hashlib.sha256(prior_package.read_bytes()).hexdigest() == prior_hash
def cancel_after_publication(event):
    if event['stage'] == 'publish' and event['event'] == 'passed':
        assert not operation.cancel(), 'Late cancellation changed a completed publication'
operation = BuildOperation(cancel_after_publication)
result = create_package(image, output, bundle, operation=operation)
assert (output / 'inspection.json').is_file()
assert (output / 'out' / result['package']['filename']).is_file()
''')

    def test_cancel_preserves_a_replaced_workspace_and_can_recover_the_original(self):
        self.run_scenario('''
import shutil
from build_operation import BuildCancelled, BuildOperation
from owned_work import recover_abandoned
held = root / 'held-workspace'
def replace_and_cancel(event):
    if event['stage'] == 'assemble' and event['event'] == 'started':
        work, = root.glob('.complete-*')
        marker = (work / '.pswaker-owner').read_text()
        work.rename(held)
        work.mkdir()
        (work / '.pswaker-owner').write_text(marker)
        (work / 'owner.txt').write_text('replacement owner files')
        operation.cancel()
operation = BuildOperation(replace_and_cancel)
try:
    create_package(image, output, bundle, operation=operation)
except BuildCancelled as error:
    assert 'ownership changed' in str(error), str(error)
else:
    raise AssertionError('Cancellation completed a package')
work, = root.glob('.complete-*')
assert (work / 'owner.txt').read_text() == 'replacement owner files'
assert held.exists()
assert not output.exists()
shutil.rmtree(work)
held.rename(work)
assert all(item['event'] == 'passed' for item in recover_abandoned())
assert not work.exists()
create_package(image, output, bundle)
assert (output / 'inspection.json').is_file()
''')

    def test_initialization_failure_preserves_a_replaced_workspace(self):
        self.run_scenario('''
import errno
import shutil
from unittest.mock import patch
from package_artifact import StageFailure
from owned_work import recover_abandoned
held = root / 'held-initialization'
write_text = Path.write_text
def replace_marker_directory(path, *args, **kwargs):
    if path.name == '.pswaker-owner':
        path.parent.rename(held)
        path.parent.mkdir()
        (path.parent / 'owner.txt').write_bytes(b'owner files')
        raise OSError(errno.ENOSPC, 'Controlled initialization failure', str(path))
    return write_text(path, *args, **kwargs)
with patch('pathlib.Path.write_text', new=replace_marker_directory):
    try:
        create_package(image, output, bundle)
    except StageFailure as error:
        assert error.stage == 'prepare'
        assert 'Controlled initialization failure' in str(error), str(error)
        assert 'ownership changed' in str(error), str(error)
    else:
        raise AssertionError('Initialization failure was ignored')
work, = root.glob('.complete-*')
assert (work / 'owner.txt').read_bytes() == b'owner files'
assert held.exists()
shutil.rmtree(work)
held.rename(work)
assert all(item['event'] == 'passed' for item in recover_abandoned())
assert not work.exists()
create_package(image, output, bundle)
assert (output / 'inspection.json').is_file()
''')

    def test_interrupted_build_is_recovered_without_touching_live_or_unowned_work(self):
        self.run_scenario('''
import subprocess
import time
from owned_work import recover_abandoned
prior = root / 'prior-complete'
prior_result = create_package(image, prior, bundle)
prior_package = prior / 'out' / prior_result['package']['filename']
prior_hash = hashlib.sha256(prior_package.read_bytes()).hexdigest()
unowned = root / '.complete-owner-files'
unowned.mkdir()
(unowned / 'keep.txt').write_text('owner files')
script = """
from pathlib import Path
import sys
import time
from windows_package import create_package
root = Path(sys.argv[1])
def observe(event):
    if event['stage'] == 'assemble' and event['event'] == 'progress':
        (root / 'paused').touch()
        time.sleep(90)
create_package(root / 'synthetic.iso', root / 'private-complete', root / 'bundle', observe=observe)
"""
with subprocess.Popen([sys.executable, '-c', script, str(root)]) as worker:
    try:
        deadline = time.monotonic() + 20
        while not (root / 'paused').exists():
            assert worker.poll() is None
            assert time.monotonic() < deadline
            time.sleep(0.01)
        assert recover_abandoned() == []  # Another app still owns this lease.
        assert list(root.glob('.complete-*'))
        worker.kill()
        worker.wait(timeout=10)
    finally:
        if worker.poll() is None:
            worker.kill()
            worker.wait()
results = recover_abandoned()
assert len(results) == 1 and results[0]['event'] == 'passed', results
assert (unowned / 'keep.txt').read_text() == 'owner files'
assert list(root.glob('.complete-*')) == [unowned]
assert not output.exists()
assert image.read_bytes() == original
assert hashlib.sha256(prior_package.read_bytes()).hexdigest() == prior_hash
result = create_package(image, output, bundle)
assert (output / 'inspection.json').is_file()
assert hashlib.sha256(prior_package.read_bytes()).hexdigest() == prior_hash
''')

    def test_cancellation_and_app_interruption_stop_owned_tool_descendants(self):
        self.run_scenario('''
import subprocess
import time
import ctypes
from ctypes import wintypes
from owned_work import recover_abandoned
kernel = ctypes.WinDLL('kernel32', use_last_error=True)
kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel.OpenProcess.restype = wintypes.HANDLE
kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
kernel.CloseHandle.argtypes = [wintypes.HANDLE]
script = """
from pathlib import Path
import sys
import time
import threading
from build_operation import BuildOperation, BuildCancelled
from owned_work import workspace
from windows_package import WindowsTools
import subprocess
root, mode = Path(sys.argv[1]), sys.argv[2]
operation = BuildOperation()
def cancel_on_request():
    while not (root / 'cancel').exists():
        time.sleep(0.01)
    operation.cancel()
if mode == 'cancel':
    threading.Thread(target=cancel_on_request, daemon=True).start()
if mode == 'interrupt-before-assignment':
    class PausedSpawn(subprocess.Popen):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            (root / 'child').write_text(str(self.pid))
            time.sleep(90)
    subprocess.Popen = PausedSpawn
with workspace(root) as owned:
    work = owned.path
    scratch = work / 'scratch'
    scratch.mkdir()
    child = 'import os,sys,time; from pathlib import Path; Path(sys.argv[1]).write_text(str(os.getpid())); time.sleep(90)'
    source = ('import os,subprocess,sys,time; from pathlib import Path; '
              'subprocess.Popen([sys.executable, "-c", ' + repr(child) + ', ' + repr(str(root / 'grandchild')) + ']); '
              'Path(' + repr(str(root / 'child')) + ').write_text(str(os.getpid())); time.sleep(90)')
    try:
        with operation.bind():
            WindowsTools(root, work, scratch).capture([sys.executable, '-c', source])
    except BuildCancelled:
        (root / 'cancelled').touch()
"""
for mode in ['cancel', 'interrupt', 'interrupt-before-assignment']:
    handles = []
    with subprocess.Popen([sys.executable, '-c', script, str(root), mode]) as worker:
        try:
            deadline = time.monotonic() + 15
            names = ['child'] if mode == 'interrupt-before-assignment' else ['child', 'grandchild']
            while not all((root / name).exists() for name in names):
                assert worker.poll() is None
                assert time.monotonic() < deadline
                time.sleep(0.01)
            for name in names:
                pid = int((root / name).read_text())
                handle = kernel.OpenProcess(0x100000, False, pid)
                assert handle
                handles.append(handle)
            if mode == 'cancel':
                (root / 'cancel').touch()
            else:
                worker.kill()
            worker.wait(timeout=15)
            if mode == 'cancel':
                assert worker.returncode == 0
                assert (root / 'cancelled').exists()
            for handle in handles:
                assert kernel.WaitForSingleObject(handle, 10000) == 0, 'Owned descendant survived'
        finally:
            if worker.poll() is None:
                worker.kill()
                worker.wait()
            for handle in handles:
                kernel.CloseHandle(handle)
    assert all(item['event'] == 'passed' for item in recover_abandoned())
    assert not list(root.glob('.complete-*'))
    for name in ['child', 'grandchild', 'cancel', 'cancelled']:
        (root / name).unlink(missing_ok=True)
create_package(image, output, bundle)
assert (output / 'inspection.json').is_file()
''')

    def test_preflight_budgets_tool_snapshot_and_retry_preserves_prior_package(self):
        self.run_scenario('''
from unittest.mock import patch
from collections import namedtuple
from package_artifact import StageFailure
prior = root / 'previous.pkg'
prior.write_bytes(b'previous verified package')
prior_hash = hashlib.sha256(prior.read_bytes()).hexdigest()
usage = namedtuple('usage', 'total used free')
# Enough for the tiny image and package, but not the real tool snapshot plus reserve.
with patch('shutil.disk_usage', return_value=usage(1024**3, 504 * 1024**2, 520 * 1024**2)):
    try:
        create_package(image, output, bundle, observe=events.append)
    except StageFailure as error:
        assert error.stage == 'validate'
        assert 'Insufficient free space' in str(error), str(error)
        assert str(root.resolve()) in str(error), str(error)
        assert 'retry' in str(error).lower()
    else:
        raise AssertionError('Tool snapshot capacity was not budgeted')
assert not output.exists()
assert not list(root.glob('.complete-*'))
assert hashlib.sha256(prior.read_bytes()).hexdigest() == prior_hash
result = create_package(image, output, bundle)
assert (output / 'inspection.json').is_file()
assert (output / 'out' / result['package']['filename']).is_file()
assert hashlib.sha256(prior.read_bytes()).hexdigest() == prior_hash
''')

    def test_workspace_creation_failure_reports_stage_and_allows_retry(self):
        self.run_scenario('''
import errno
from unittest.mock import patch
from package_artifact import StageFailure
mkdir = Path.mkdir
def fail_workspace(path, *args, **kwargs):
    if path.name.startswith('.complete-'):
        raise OSError(errno.ENOSPC, 'Controlled disk exhaustion', str(path))
    return mkdir(path, *args, **kwargs)
with patch('pathlib.Path.mkdir', new=fail_workspace):
    try:
        create_package(image, output, bundle)
    except StageFailure as error:
        assert error.stage == 'prepare', error.stage
        assert 'Controlled disk exhaustion' in str(error)
        assert 'retry' in str(error).lower(), str(error)
    else:
        raise AssertionError('Workspace creation unexpectedly succeeded')
assert not output.exists()
assert not list(root.glob('.complete-*'))
create_package(image, output, bundle)
assert (output / 'inspection.json').is_file()
''')

    def test_packager_scratch_is_isolated_on_the_destination_drive(self):
        self.run_scenario('''
import os
import subprocess
from unittest.mock import patch
run = subprocess.Popen
def check_scratch(command, **kwargs):
    environment = kwargs['env']
    scratch = Path(environment['TEMP'])
    assert scratch == Path(environment['TMP'])
    assert scratch.is_dir() and scratch.is_relative_to(Path(kwargs['cwd'])), scratch
    return run(command, **kwargs)
with patch('subprocess.Popen', side_effect=check_scratch):
    create_package(image, output, bundle)
assert (output / 'inspection.json').is_file()
assert not list(root.glob('.complete-*'))
assert not (output / 'scratch').exists()
''')

    def test_real_packager_error_keeps_local_details_and_can_retry(self):
        self.run_scenario('''
import subprocess
from unittest.mock import patch
from package_artifact import StageFailure
run = subprocess.Popen
def malformed_project(command, **kwargs):
    if command[1] == 'pkg_build':
        Path(command[2]).write_text('<deliberately-invalid-project>')
    return run(command, **kwargs)
with patch('subprocess.Popen', side_effect=malformed_project):
    try:
        create_package(image, output, bundle)
    except StageFailure as error:
        assert error.stage == 'assemble'
        assert 'pkg_build' in str(error), str(error)
        assert 'exit code' in str(error), str(error)
        assert len(str(error)) < 1500, 'Tool failure overwhelms the desktop guidance'
        log = Path(str(error).split('Local diagnostic log: ')[-1])
        assert log.is_file()
        assert 'pkg_build' in log.read_text()
        assert 'Tool output:' in log.read_text()
    else:
        raise AssertionError('Malformed project was accepted')
assert not output.exists()
assert not list(root.glob('.complete-*'))
create_package(image, output, bundle)
assert (output / 'inspection.json').is_file()
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
