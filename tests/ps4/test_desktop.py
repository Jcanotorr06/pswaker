"""Observable desktop workflow and shared validation, using data-free images."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from synthetic_disc import generate

REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / 'tools/pswaker'))
DESKTOP_AVAILABLE = sys.platform == 'win32' or (
    bool(os.environ.get('DISPLAY')) and importlib.util.find_spec('tkinter') is not None)
WINDOWS_TOOLS = os.environ.get('PSWAKER_WINDOWS_TOOLS')


class DesktopValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='pswaker-desktop-test-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        _, self.image = generate(self.root, REPOSITORY)

    def test_synthetic_image_cannot_pass_shipping_desktop_validation(self):
        from package_validation import validate_selection
        original = hashlib.sha256(self.image.read_bytes()).hexdigest()
        output = self.root / 'private-package'
        with self.assertRaisesRegex(ValueError, 'full raw dump'):
            validate_selection(self.image, output)
        self.assertFalse(output.exists())
        self.assertEqual(hashlib.sha256(self.image.read_bytes()).hexdigest(), original)

    @unittest.skipUnless(DESKTOP_AVAILABLE, 'Tk desktop display required')
    def test_cancel_validation_keeps_desktop_responsive_and_allows_fresh_retry(self):
        self.run_desktop('''
import threading
from build_operation import BuildOperation
entered, release = threading.Event(), threading.Event()
progress = BuildOperation.progress
def pause_read(operation, *args):
    progress(operation, *args)
    entered.set()
    assert release.wait(10)
with patch.object(BuildOperation, 'progress', new=pause_read):
    app.image_button.invoke()
    app.output_button.invoke()
    app.validate_button.invoke()
    wait_until(entered.is_set)
    assert app.busy
    assert not app.cancel_button.instate(['disabled'])
    app.cancel_button.invoke()
    assert app.busy  # Wait for owned work to stop before enabling retry.
    release.set()
    wait_for('Validation cancelled')
assert app.accepted is None
assert app.create_button.instate(['disabled'])
assert not app.validate_button.instate(['disabled'])
assert not output.exists()
app.validate_button.invoke()
wait_for('Supported image')
''')

    @unittest.skipUnless(sys.platform == 'win32' and WINDOWS_TOOLS, 'Native Windows tool closure required')
    def test_desktop_cancels_each_build_stage_and_retries_from_the_beginning(self):
        self.run_desktop('''
import threading
from build_operation import BuildOperation
progress = BuildOperation.progress
app.image_button.invoke()
app.output_button.invoke()
for target in ['validate', 'assemble', 'inspect']:
    app.validate_button.invoke()
    wait_for('Supported image')
    entered, release = threading.Event(), threading.Event()
    def pause_stage(operation, *args):
        progress(operation, *args)
        if operation.stage == target and not entered.is_set():
            entered.set()
            assert release.wait(10)
    with patch.object(BuildOperation, 'progress', new=pause_stage):
        app.create_button.invoke()
        wait_until(entered.is_set)
        wait_until(lambda: 'bytes' in app.details.get())
        assert app.busy
        assert not app.cancel_button.instate(['disabled'])
        assert app.image_button.instate(['disabled'])
        assert 'bytes' in app.details.get(), app.details.get()
        app.cancel_button.invoke()
        assert app.busy
        release.set()
        wait_for('Package creation cancelled')
    assert not output.exists()
    assert not list(folder.glob('.complete-*'))
    assert app.accepted is None
    assert app.package is None
    assert not app.instructions.get()
    assert app.create_button.instate(['disabled'])
    assert app.open_button.instate(['disabled'])
    assert not app.validate_button.instate(['disabled'])
app.validate_button.invoke()
wait_for('Supported image')
app.create_button.invoke()
wait_for('Package verified')
assert (output / 'inspection.json').is_file()
evidence = list((folder / 'local-state/PSWaker/logs').glob('attempt-*.json'))
attempts = [json.loads(path.read_text()) for path in evidence]
assert any(item['outcome'] == 'cancelled' for item in attempts)
completed = [item for item in attempts if item['outcome'] == 'complete']
assert any({'validate', 'assemble', 'inspect'}.issubset(
    {e['stage'] for e in item['events'] if e['event'] == 'passed'}) for item in completed)
''', packaging=True)

    @unittest.skipUnless(DESKTOP_AVAILABLE, 'Tk desktop display required')
    def test_closing_desktop_waits_for_cancellation_before_destroying_window(self):
        self.run_desktop('''
import threading
from build_operation import BuildOperation
entered, release = threading.Event(), threading.Event()
progress = BuildOperation.progress
def pause_read(operation, *args):
    progress(operation, *args)
    entered.set()
    assert release.wait(10)
with patch.object(BuildOperation, 'progress', new=pause_read), patch.object(root, 'destroy') as destroy:
    app.image_button.invoke()
    app.output_button.invoke()
    app.validate_button.invoke()
    wait_until(entered.is_set)
    app.close()
    assert app.busy
    destroy.assert_not_called()
    release.set()
    wait_until(lambda: destroy.called)
assert not app.busy
assert app.accepted is None
assert not output.exists()
''')

    @unittest.skipUnless(DESKTOP_AVAILABLE, 'Tk desktop display required')
    def test_startup_recovers_abandoned_work_and_preserves_replaced_owner_files(self):
        self.run_desktop('''
import shutil
import textwrap
unowned = folder / '.complete-owner-files'
unowned.mkdir()
(unowned / 'keep.txt').write_text('owner files')
script = """
from pathlib import Path
import sys
import time
from owned_work import workspace
root = Path(sys.argv[1])
with workspace(root) as owned:
    work = owned.path
    (work / 'scratch').mkdir()
    (work / 'scratch/partial').write_bytes(b'synthetic unfinished work')
    (root / 'paused').touch()
    time.sleep(90)
"""
with subprocess.Popen([sys.executable, '-c', textwrap.dedent(script), str(folder)]) as worker:
    try:
        wait_until(lambda: (folder / 'paused').exists())
    finally:
        worker.kill()
        worker.wait(timeout=10)
record_path, = (folder / 'local-state/PSWaker/work').glob('*.jsonl')
record = json.loads(record_path.read_text().splitlines()[-1])
work = Path(record['workspace'])
held = folder / 'held-original-work'
work.rename(held)
work.mkdir()
(work / '.pswaker-owner').write_text(record['id'])
(work / 'owner.txt').write_text('replacement must survive')
root.destroy()
root = tk.Tk()
app = DesktopApp(root, bundle)
wait_until(lambda: not app.busy)
assert 'Interrupted work needs attention' in app.status.get(), app.status.get()
assert 'ownership changed' in app.details.get(), app.details.get()
assert (work / 'owner.txt').read_text() == 'replacement must survive'
assert (held / 'scratch/partial').exists()
shutil.rmtree(work)
held.rename(work)
root.destroy()
root = tk.Tk()
app = DesktopApp(root, bundle)
wait_until(lambda: not app.busy)
assert 'removed' in app.details.get(), app.details.get()
assert not work.exists()
assert not record_path.exists()
assert (unowned / 'keep.txt').read_text() == 'owner files'
assert app.accepted is None
assert app.create_button.instate(['disabled'])
app.image_button.invoke()
app.output_button.invoke()
app.validate_button.invoke()
wait_for('Supported image')
''')

    @unittest.skipUnless(DESKTOP_AVAILABLE, 'Tk desktop display required')
    def test_startup_recovers_interruption_before_and_after_the_ownership_marker(self):
        self.run_desktop('''
import textwrap
script = """
from pathlib import Path
import sys
import time
from owned_work import workspace
root, mode = Path(sys.argv[1]), sys.argv[2]
write_text = Path.write_text
def paused_marker(path, *args, **kwargs):
    if path.name == '.pswaker-owner' and mode == 'before':
        (root / 'paused').touch()
        time.sleep(90)
    result = write_text(path, *args, **kwargs)
    if path.name == '.pswaker-owner' and mode == 'after':
        (root / 'paused').touch()
        time.sleep(90)
    return result
Path.write_text = paused_marker
with workspace(root):
    raise AssertionError('Initialization was not interrupted')
"""
for mode in ['before', 'after']:
    with subprocess.Popen([sys.executable, '-c', textwrap.dedent(script), str(folder), mode]) as worker:
        try:
            wait_until(lambda: (folder / 'paused').exists())
        finally:
            worker.kill()
            worker.wait(timeout=10)
    record, = (folder / 'local-state/PSWaker/work').glob('*.jsonl')
    # A partially appended newest update cannot hide the durable allocated record.
    with record.open('ab') as stream:
        stream.write(b'{"incomplete":')
    root.destroy()
    root = tk.Tk()
    app = DesktopApp(root, bundle)
    wait_until(lambda: not app.busy)
    assert 'removed' in app.details.get(), app.details.get()
    assert not list(folder.glob('.complete-*'))
    assert not record.exists()
    assert app.accepted is None
    (folder / 'paused').unlink()
''')

    @unittest.skipUnless(sys.platform == 'win32' and WINDOWS_TOOLS, 'Native Windows tool closure required')
    def test_desktop_creates_verified_package_and_offers_manual_installation(self):
        self.run_desktop('''
app.image_button.invoke()
app.output_button.invoke()
app.validate_button.invoke()
wait_for('Supported image')
assert not app.create_button.instate(['disabled'])
app.create_button.invoke()
assert app.image_button.instate(['disabled'])
assert app.output_button.instate(['disabled'])
wait_for('Package verified')
report = json.loads((output / 'inspection.json').read_text())
package = output / 'out' / report['package']['filename']
assert package.is_file()
assert str(package.resolve()) in app.details.get(), app.details.get()
assert 'USB' in app.instructions.get()
assert '9.00' in app.instructions.get()
assert 'GoldHEN v2.4b18' in app.instructions.get()
assert 'remove the USB' in app.instructions.get()
assert not app.open_button.instate(['disabled'])
with patch('os.startfile') as opened:
    app.open_button.invoke()
    opened.assert_called_once_with(str(package.parent.resolve()))
assert app.create_button.instate(['disabled'])
assert not list(folder.glob('.complete-*'))
''', packaging=True)

    @unittest.skipUnless(sys.platform == 'win32' and WINDOWS_TOOLS, 'Native Windows tool closure required')
    def test_desktop_reports_packaging_failure_and_can_retry_from_validation(self):
        self.run_desktop('''
program = bundle / 'program/stage/eboot.bin'
saved = program.read_bytes()
program.write_bytes(saved + b'changed')
app.image_button.invoke()
app.output_button.invoke()
app.validate_button.invoke()
wait_for('Supported image')
app.create_button.invoke()
wait_for('Package creation failed')
assert 'verify-program' in app.details.get(), app.details.get()
assert 'reinstall' in app.details.get().lower()
assert not output.exists()
assert app.open_button.instate(['disabled'])
assert not app.validate_button.instate(['disabled'])
assert app.create_button.instate(['disabled'])
assert not list(folder.glob('.complete-*'))
program.write_bytes(saved)
app.validate_button.invoke()
wait_for('Supported image')
app.create_button.invoke()
wait_for('Package verified')
assert (output / 'inspection.json').is_file()
''', packaging=True)

    @unittest.skipUnless(sys.platform == 'win32' and WINDOWS_TOOLS, 'Native Windows tool closure required')
    def test_desktop_rejects_insufficient_capacity_and_retries(self):
        self.run_storage_failure('capacity', 'validate', 'Insufficient free space')

    @unittest.skipUnless(sys.platform == 'win32' and WINDOWS_TOOLS, 'Native Windows tool closure required')
    def test_desktop_handles_partial_image_write_and_retries(self):
        self.run_storage_failure('disk-full', 'assemble', 'Controlled disk exhaustion')

    @unittest.skipUnless(sys.platform == 'win32' and WINDOWS_TOOLS, 'Native Windows tool closure required')
    def test_desktop_handles_lost_access_and_retries(self):
        self.run_storage_failure('lost-access', 'assemble', 'Controlled lost access')

    @unittest.skipUnless(sys.platform == 'win32' and WINDOWS_TOOLS, 'Native Windows tool closure required')
    def test_desktop_rejects_destination_access_failure_and_retries(self):
        self.run_storage_failure('destination-access', 'validate', 'Controlled destination access loss')

    @unittest.skipUnless(sys.platform == 'win32' and WINDOWS_TOOLS, 'Native Windows tool closure required')
    def test_desktop_reports_lost_publish_access_without_exposing_package(self):
        self.run_storage_failure('publish-access', 'publish', 'Controlled publish access loss')

    @unittest.skipUnless(sys.platform == 'win32' and WINDOWS_TOOLS, 'Native Windows tool closure required')
    def test_desktop_handles_real_packager_failure_and_retries(self):
        self.run_storage_failure('packager', 'assemble', 'exit code')

    @unittest.skipUnless(sys.platform == 'win32' and WINDOWS_TOOLS, 'Native Windows tool closure required')
    def test_desktop_rejects_corrupted_package_before_publication_and_retries(self):
        self.run_storage_failure('inspection', 'inspect', 'Package header content ID mismatch')

    @unittest.skipUnless(sys.platform == 'win32' and WINDOWS_TOOLS, 'Native Windows tool closure required')
    def test_desktop_preserves_racing_destination_and_retries_in_another_folder(self):
        self.run_storage_failure('collision', 'publish', 'Output appeared')

    @unittest.skipUnless(sys.platform == 'win32' and WINDOWS_TOOLS, 'Native Windows tool closure required')
    def test_desktop_retains_original_error_when_cleanup_loses_access(self):
        self.run_storage_failure('cleanup', 'assemble', 'Cleanup also failed')

    @unittest.skipUnless(sys.platform == 'win32' and WINDOWS_TOOLS, 'Native Windows tool closure required')
    def test_desktop_retains_disk_error_when_local_diagnostics_are_unwritable(self):
        self.run_storage_failure('no-log', 'assemble', 'Controlled disk exhaustion')

    def run_storage_failure(self, fault, stage, message):
        self.run_desktop('''
import errno
import shutil
from contextlib import ExitStack
from windows_package import create_package
fault, expected_stage, expected_message = ''' + repr((fault, stage, message)) + '''
prior = folder / 'prior-complete'
prior_result = create_package(image, prior, bundle)
prior_package = prior / 'out' / prior_result['package']['filename']
prior_hash = hashlib.sha256(prior_package.read_bytes()).hexdigest()
open_file, run, rmtree = Path.open, subprocess.Popen, shutil.rmtree
rename = Path.rename
class FailedWrite:
    def __init__(self, stream):
        self.stream = stream
    def __enter__(self):
        self.stream.__enter__()
        return self
    def __exit__(self, *args):
        return self.stream.__exit__(*args)
    def write(self, data):
        # A real partial artifact exists before the OS reports the failed write.
        self.stream.write(data[:1024])
        raise OSError(errno.ENOSPC, 'Controlled disk exhaustion', self.stream.name)

def fail_open(path, mode='r', *args, **kwargs):
    if path.name == 'game.iso' and mode == 'wb':
        if fault == 'lost-access':
            raise PermissionError(errno.EACCES, 'Controlled lost access', str(path))
        return FailedWrite(open_file(path, mode, *args, **kwargs))
    return open_file(path, mode, *args, **kwargs)

class FaultTool(run):
    def __init__(self, command, **kwargs):
        if fault == 'packager' and command[1] == 'pkg_build':
            Path(command[2]).write_text('<deliberately-invalid-project>')
        self.command, self.injected = command, False
        super().__init__(command, **kwargs)
    def communicate(self, *args, **kwargs):
        result = super().communicate(*args, **kwargs)
        if not self.injected:
            self.injected = True
            command = self.command
            if command[1] == 'pkg_build' and fault == 'collision':
                output.mkdir()
                shutil.copyfile(prior_package, output / 'previous.pkg')
            if command[1] == 'pkg_extract' and fault == 'inspection':
                with Path(command[2]).open('r+b') as stream:
                    stream.seek(0x40)
                    stream.write(b'IV0000-FAIL00000')
        return result

def fail_cleanup(path, *args, **kwargs):
    if Path(path).name.startswith('.complete-'):
        raise PermissionError(errno.EACCES, 'Controlled cleanup access loss', str(path))
    return rmtree(path, *args, **kwargs)
def fail_publish(path, target):
    if path.name.startswith('.complete-'):
        raise PermissionError(errno.EACCES, 'Controlled publish access loss', str(target))
    return rename(path, target)
app.image_button.invoke()
app.output_button.invoke()
app.validate_button.invoke()
wait_for('Supported image')
with ExitStack() as faults:
    if fault == 'capacity':
        from collections import namedtuple
        usage = namedtuple('usage', 'total used free')
        faults.enter_context(patch('shutil.disk_usage', return_value=usage(1024, 1024, 0)))
    if fault in {'disk-full', 'lost-access', 'cleanup', 'no-log'}:
        faults.enter_context(patch('pathlib.Path.open', new=fail_open))
    if fault == 'destination-access':
        faults.enter_context(patch('tempfile.TemporaryFile', side_effect=PermissionError(
            errno.EACCES, 'Controlled destination access loss', str(folder))))
    if fault == 'publish-access':
        faults.enter_context(patch('pathlib.Path.rename', new=fail_publish))
    if fault in {'packager', 'inspection', 'collision'}:
        faults.enter_context(patch('subprocess.Popen', new=FaultTool))
    if fault == 'cleanup':
        faults.enter_context(patch('shutil.rmtree', side_effect=fail_cleanup))
    if fault == 'no-log':
        faults.enter_context(patch('tempfile.NamedTemporaryFile', side_effect=PermissionError(
            errno.EACCES, 'Controlled diagnostic access loss')))
    app.create_button.invoke()
    wait_for('Package creation failed')
assert expected_stage + ':' in app.details.get(), app.details.get()
assert expected_message in app.details.get(), app.details.get()
assert 'retry' in app.details.get().lower()
assert app.package is None
assert not app.instructions.get()
assert app.open_button.instate(['disabled'])
assert app.install_button.instate(['disabled'])
assert app.create_button.instate(['disabled'])
assert not app.validate_button.instate(['disabled'])
assert not app.image_button.instate(['disabled'])
assert not app.output_button.instate(['disabled'])
assert hashlib.sha256(image.read_bytes()).hexdigest() == original
assert hashlib.sha256(prior_package.read_bytes()).hexdigest() == prior_hash
if fault == 'collision':
    assert hashlib.sha256((output / 'previous.pkg').read_bytes()).hexdigest() == prior_hash
    assert not (output / 'inspection.json').exists()
    retry_folder = folder / 'retry'
    retry_folder.mkdir()
    with patch('tkinter.filedialog.askdirectory', return_value=str(retry_folder)):
        app.output_button.invoke()
    output = retry_folder / 'PSWaker-01.23'
else:
    assert not output.exists()
if fault == 'cleanup':
    unfinished = list(folder.glob('.complete-*'))
    assert len(unfinished) == 1
    assert str(unfinished[0].resolve()) in app.details.get(), app.details.get()
    assert 'Controlled disk exhaustion' in app.details.get()
    shutil.rmtree(unfinished[0])
else:
    assert not list(folder.glob('.complete-*'))
app.validate_button.invoke()
wait_for('Supported image')
app.create_button.invoke()
wait_for('Package verified')
report = json.loads((output / 'inspection.json').read_text())
assert report['image']['sha256'] == original
assert hashlib.sha256(app.package.read_bytes()).hexdigest() == report['package']['sha256']
assert hashlib.sha256(prior_package.read_bytes()).hexdigest() == prior_hash
assert not list(folder.glob('.complete-*'))
''', packaging=True)

    @unittest.skipUnless(DESKTOP_AVAILABLE, 'Tk desktop display required')
    def test_desktop_selection_shows_supported_image_and_program_identity(self):
        self.run_desktop('''
app.image_button.invoke()
app.output_button.invoke()
app.validate_button.invoke()
wait_for('Supported image')
assert '01.23' in app.program_text.get(), app.program_text.get()
assert 'PS4 Slim / firmware 9.00 / GoldHEN v2.4b18' in app.baseline_text.get()
assert 'SHA-256' in app.details.get()
assert app.create_button.instate(['disabled'])
assert not output.exists()
''')

    @unittest.skipUnless(DESKTOP_AVAILABLE, 'Tk desktop display required')
    def test_desktop_rejects_synthetic_image_with_production_contract(self):
        self.run_desktop('''
app.image_button.invoke()
app.output_button.invoke()
app.validate_button.invoke()
wait_for('Validation failed')
assert 'full raw dump' in app.details.get(), app.details.get()
assert app.create_button.instate(['disabled'])
assert not output.exists()
''', production=True)

    @unittest.skipUnless(DESKTOP_AVAILABLE, 'Tk desktop display required')
    def test_changed_selection_and_late_validation_cannot_keep_success(self):
        self.run_desktop('''
app.image_button.invoke()
app.output_button.invoke()
app.validate_button.invoke()
app.image_button.invoke()
wait_until(lambda: not app.validate_button.instate(['disabled']))
assert 'Selection changed' in app.status.get(), app.status.get()
assert not app.details.get()
app.validate_button.invoke()
wait_for('Supported image')
saved = image.read_bytes()
image.write_bytes(saved + b'changed')
wait_for('Selection is stale')
assert not app.details.get()
image.write_bytes(saved)
app.validate_button.invoke()
wait_for('Supported image')
output.mkdir()
(output / 'previous.pkg').write_text('previous result')
wait_for('Selection is stale')
app.validate_button.invoke()
wait_for('Validation failed')
assert 'Output already exists' in app.details.get(), app.details.get()
assert (output / 'previous.pkg').read_text() == 'previous result'
assert app.create_button.instate(['disabled'])
''')

    @unittest.skipUnless(DESKTOP_AVAILABLE, 'Tk desktop display required')
    def test_desktop_reports_content_failures_and_can_retry(self):
        self.run_desktop('''
app.image_button.invoke()
app.output_button.invoke()
saved = image.read_bytes()
for offset, value, message in [
    (3, b'P', 'supply USA GZLE01 revision 0'),
    (6, b'\\x01', 'supply USA GZLE01 revision 0'),
    (7, b'\\x01', 'supply USA GZLE01 revision 0'),
    (0x1c, b'RVZ!', 'Unsupported/compressed'),
    (0x424, b'\\xff\\xff\\xff\\xff', 'GameCube FST'),
    (0x1100, b'BAD', 'sys/main.dol: content SHA-1 mismatch'),
    (0x3011, b'BAD', 'rels/direct.rel: content SHA-1 mismatch'),
    (0x4148, b'BAD', 'RELS.arc:rels/mmem/second.rel: content SHA-1 mismatch'),
    (0x7000, b'BAD', 'Full image SHA-1 mismatch')]:
    changed = bytearray(saved)
    changed[offset:offset + len(value)] = value
    image.write_bytes(changed)
    app.validate_button.invoke()
    wait_for('Validation failed')
    assert message in app.details.get(), app.details.get()
    assert 'Traceback' not in app.details.get()
    assert app.create_button.instate(['disabled'])
    assert image.read_bytes() == changed
    assert not output.exists()
    app.image_button.invoke()
image.write_bytes(saved)
app.validate_button.invoke()
wait_for('Supported image')
''')

    @unittest.skipUnless(sys.platform == 'win32', 'Windows file sharing contract')
    def test_desktop_reports_an_unreadable_image_without_traceback(self):
        self.run_desktop('''
import ctypes
from ctypes import wintypes
kernel = ctypes.WinDLL('kernel32', use_last_error=True)
kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
    ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
kernel.CreateFileW.restype = wintypes.HANDLE
kernel.CloseHandle.argtypes = [wintypes.HANDLE]
handle = kernel.CreateFileW(str(image), 0x80000000, 0, None, 3, 0x80, None)
assert handle != wintypes.HANDLE(-1).value
try:
    app.image_button.invoke()
    app.output_button.invoke()
    app.validate_button.invoke()
    wait_for('Validation failed')
    assert 'Cannot access' in app.details.get(), app.details.get()
    assert 'retry' in app.details.get()
    assert app.create_button.instate(['disabled'])
finally:
    kernel.CloseHandle(handle)
app.validate_button.invoke()
wait_for('Supported image')
''')

    def run_desktop(self, scenario, *, production=False, packaging=False):
        bundle = self.root / 'bundle/program'
        (bundle / 'stage').mkdir(parents=True)
        (bundle / 'program-release.json').write_text(json.dumps(
            {'schema': 1, 'kind': 'game', 'build_id': 'synthetic-program'}))
        (bundle / 'stage/build-info.json').write_text(json.dumps(
            {'app_version': '01.23', 'program_build_id': 'synthetic-program'}))
        tools = (REPOSITORY if production else self.root / 'repo') / 'tools/pswaker'
        script = '''
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import tkinter as tk
from unittest.mock import patch
from desktop_app import DesktopApp
image, folder, bundle = map(Path, sys.argv[1:])
if ''' + repr(packaging) + ''':
    from synthetic_program import make_bundle
    import shutil
    shutil.rmtree(bundle)
    make_bundle(bundle, Path(''' + repr(WINDOWS_TOOLS or '') + '''))
output = folder / 'PSWaker-01.23'
original = hashlib.sha256(image.read_bytes()).hexdigest()
root = tk.Tk()
app = DesktopApp(root, bundle)
def wait_for(text):
    wait_until(lambda: text in app.status.get())
def wait_until(predicate):
    deadline = time.monotonic() + 30
    while not predicate():
        root.update()
        if time.monotonic() > deadline:
            raise AssertionError(app.status.get())
        time.sleep(0.01)
wait_until(lambda: not app.busy)
with patch('tkinter.filedialog.askopenfilename', return_value=str(image)), \\
     patch('tkinter.filedialog.askdirectory', return_value=str(folder)):
''' + '\n'.join('    ' + line for line in scenario.strip().splitlines()) + '''
assert hashlib.sha256(image.read_bytes()).hexdigest() == original
root.destroy()
'''
        result = subprocess.run([sys.executable, '-c', script, str(self.image), str(self.root),
                                 str(bundle.parent)], cwd=tools, capture_output=True, text=True, timeout=90,
                                env=dict(os.environ, PYTHONPATH=str(REPOSITORY / 'tests/ps4'),
                                         LOCALAPPDATA=str(self.root / 'local-state')))
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)


if __name__ == '__main__':
    unittest.main()
