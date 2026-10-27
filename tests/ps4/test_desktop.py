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

    def run_desktop(self, scenario, *, production=False):
        bundle = self.root / 'bundle/program'
        (bundle / 'stage').mkdir(parents=True)
        (bundle / 'program-release.json').write_text(json.dumps(
            {'schema': 1, 'kind': 'game', 'build_id': 'synthetic-program'}))
        (bundle / 'stage/build-info.json').write_text(json.dumps(
            {'app_version': '01.23', 'program_build_id': 'synthetic-program'}))
        tools = (REPOSITORY if production else self.root / 'repo') / 'tools/pswaker'
        script = '''
import hashlib
from pathlib import Path
import sys
import time
import tkinter as tk
from unittest.mock import patch
from desktop_app import DesktopApp
image, folder, bundle = map(Path, sys.argv[1:])
output = folder / 'PSWaker-01.23'
original = hashlib.sha256(image.read_bytes()).hexdigest()
root = tk.Tk()
app = DesktopApp(root, bundle)
def wait_for(text):
    wait_until(lambda: text in app.status.get())
def wait_until(predicate):
    deadline = time.monotonic() + 10
    while not predicate():
        root.update()
        if time.monotonic() > deadline:
            raise AssertionError(app.status.get())
        time.sleep(0.01)
with patch('tkinter.filedialog.askopenfilename', return_value=str(image)), \\
     patch('tkinter.filedialog.askdirectory', return_value=str(folder)):
''' + '\n'.join('    ' + line for line in scenario.strip().splitlines()) + '''
assert hashlib.sha256(image.read_bytes()).hexdigest() == original
root.destroy()
'''
        result = subprocess.run([sys.executable, '-c', script, str(self.image), str(self.root),
                                 str(bundle.parent)], cwd=tools, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)


if __name__ == '__main__':
    unittest.main()
