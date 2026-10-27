"""Owner-flow automation of the installed Windows app through native windows.

No app imports, injected callbacks or alternate validation switches are used.
Tk buttons have no native text, so their public layout identifies the controls.
"""
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import subprocess
import time


def build_package(executable, image, parent, env):
    user = ctypes.WinDLL('user32', use_last_error=True)
    user.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user.GetDlgItem.argtypes = [wintypes.HWND, ctypes.c_int]
    user.GetDlgItem.restype = wintypes.HWND
    user.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
    user.GetAncestor.restype = wintypes.HWND
    callback = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    parent.mkdir()
    process = subprocess.Popen([str(executable)], cwd=parent, env=env)

    def windows(container=None):
        found = []

        @callback
        def collect(handle, _):
            pid = wintypes.DWORD()
            user.GetWindowThreadProcessId(handle, ctypes.byref(pid))
            if pid.value == process.pid:
                title = ctypes.create_unicode_buffer(1024)
                user.GetWindowTextW(handle, title, len(title))
                rect = wintypes.RECT()
                user.GetWindowRect(handle, ctypes.byref(rect))
                found.append((handle, title.value, rect))
            return True

        if container is None:
            user.EnumWindows(collect, 0)
        else:
            user.EnumChildWindows(container, collect, 0)
        return found

    def wait(predicate, timeout=90):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            result = predicate()
            if result:
                return result
            if process.poll() is not None:
                raise AssertionError(f'Installed app exited: {process.returncode}')
            time.sleep(0.1)
        raise AssertionError('Installed app did not finish: ' + str([(h, t) for h, t, _ in windows()]))

    def click(handle):
        user.SetForegroundWindow(user.GetAncestor(handle, 2))
        rect = wintypes.RECT()
        user.GetWindowRect(handle, ctypes.byref(rect))
        # Pointer interaction exercises Tk's actual button state and callbacks.
        user.SetCursorPos((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
        time.sleep(0.2)
        user.mouse_event(2, 0, 0, 0, 0)
        user.mouse_event(4, 0, 0, 0, 0)

    def fill_dialog(title, value):
        print('Installed UI: ' + title, flush=True)
        dialog = wait(lambda: next((h for h, t, _ in windows() if t == title), None))
        time.sleep(0.5)  # The shell can publish its window before initializing the filename field.
        if title == 'Select a private parent folder':
            # Alt+D activates the address edit; the folder picker's other Edit
            # control is its search box and cannot select a destination.
            click(dialog)
            user.keybd_event(0x12, 0, 0, 0)
            user.keybd_event(0x44, 0, 0, 0)
            user.keybd_event(0x44, 0, 2, 0)
            user.keybd_event(0x12, 0, 2, 0)
            time.sleep(0.2)
            class Focus(ctypes.Structure):
                _fields_ = [('size', wintypes.DWORD), ('flags', wintypes.DWORD),
                            ('active', wintypes.HWND), ('focus', wintypes.HWND),
                            ('capture', wintypes.HWND), ('menu', wintypes.HWND),
                            ('move', wintypes.HWND), ('caret', wintypes.HWND), ('rect', wintypes.RECT)]
            focused = Focus()
            focused.size = ctypes.sizeof(focused)
            assert user.GetGUIThreadInfo(0, ctypes.byref(focused))
            address = ctypes.create_unicode_buffer(str(value))
            assert user.SendMessageW(focused.focus, 12, 0, ctypes.addressof(address))
            user.keybd_event(13, 0, 0, 0)
            user.keybd_event(13, 0, 2, 0)
            time.sleep(0.5)
            click(user.GetDlgItem(dialog, 1))
            wait(lambda: not user.IsWindow(dialog))
            return
        edits = []
        for handle, _, _ in windows(dialog):
            kind = ctypes.create_unicode_buffer(128)
            user.GetClassNameW(handle, kind, len(kind))
            if kind.value == 'Edit':
                edits.append(handle)
        assert edits, 'Native path dialog has no filename field'
        edit = next((h for h in edits if user.GetDlgCtrlID(h) == 1148), edits[-1])
        click(edit)
        for _ in range(5):
            if not user.IsWindow(dialog):
                break
            value_buffer = ctypes.create_unicode_buffer(str(value))
            assert user.SendMessageW(edit, 12, 0, ctypes.addressof(value_buffer)), 'Cannot enter the selected path'
            time.sleep(0.2)
            # A native click also commits the edit's pending change notification.
            click(user.GetDlgItem(dialog, 1))
            time.sleep(0.3)
        wait(lambda: not user.IsWindow(dialog))

    top = None
    try:
        top = wait(lambda: next((h for h, t, _ in windows() if t.startswith('PSWaker —')), None))

        def buttons():
            found = sorted((r.top, r.left, h) for h, _, r in windows(top)
                           if 60 <= r.right - r.left <= 240 and 25 <= r.bottom - r.top <= 28)
            return found if len(found) == 8 else None

        controls = wait(buttons)
        print('Installed UI: controls located', flush=True)
        image_button, output_button, validate_button, create_button = [h for _, _, h in controls[:4]]
        click(image_button)
        fill_dialog('Select your original raw disc image', image)
        click(output_button)
        fill_dialog('Select a private parent folder', parent)
        logs = Path(env['LOCALAPPDATA']) / 'PSWaker/logs'
        known_logs = set(logs.glob('attempt-*.json'))
        click(validate_button)
        # Wait for externally observable validation evidence before creating.
        def validated():
            for path in set(logs.glob('attempt-*.json')) - known_logs:
                report = json.loads(path.read_text())
                if any(e['stage'] == 'validate' and e['event'] == 'passed' for e in report['events']):
                    return True
            return False
        wait(validated)
        time.sleep(0.3)  # Let Tk consume its worker's completed result.
        click(create_button)
        result = wait(lambda: next(parent.glob('PSWaker-*/inspection.json'), None), timeout=240)
        output = result.parent
        report = json.loads(result.read_text())
        package = output / 'out' / report['package']['filename']
        assert package.is_file()
        return package
    finally:
        if top:
            user.PostMessageW(top, 0x10, 0, 0)
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise AssertionError('Installed app failed to close after its operation')
