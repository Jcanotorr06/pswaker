"""Verify the complete installed closure without consulting developer tools or networks."""
from contextlib import contextmanager
import ctypes
import json
from pathlib import Path
import sys

from disc_image import CONTRACT, require
from package_artifact import digest, inventory
from windows_package import bundle_inventory, checked_program, checked_tools
from pipeline_assets import ASSET_DIRECTORY, checked_pipeline_asset

APP_MUTEX = 'PSWaker.Desktop.Offline'


def check_installation(root):
    manifest = json.loads((root / 'application-release.json').read_text())
    files = inventory(root)
    del files['application-release.json']
    require(manifest['schema'] == 1 and manifest['platform'] == 'win-x64'
            and manifest['files'] == files,
            'Installed application files are missing or changed. Reinstall the complete application.')
    bundle = root / '_internal'
    fixed = json.loads((bundle / 'desktop-release.json').read_text())
    version, release = checked_program(bundle)
    tools = checked_tools(bundle / 'packaging')
    checked_pipeline_asset(bundle / ASSET_DIRECTORY)
    require(fixed['schema'] == 1 and fixed['files'] == bundle_inventory(bundle)
            and digest(CONTRACT) == fixed['files']['platform/ps4/content-contract.json']
            and fixed['app_version'] == manifest['app_version']
            and version == fixed['program_version'] and release['build_id'] == fixed['program_build_id'],
            'Installed components are incompatible. Reinstall the complete application.')
    return {'app_version': manifest['app_version'], 'program_version': version,
            'program_build_id': release['build_id'], 'tool_revision': tools['source_revision'],
            'tool_sdk': tools['sdk'], 'title_id': 'PSWK00001',
            'application_manifest_sha256': digest(root / 'application-release.json'),
            'desktop_manifest_sha256': digest(bundle / 'desktop-release.json'),
            'runtime': manifest['runtime']}


@contextmanager
def installation_in_use():
    """Prevent update/uninstall while any app instance still owns work."""
    if sys.platform != 'win32':
        yield
        return
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
    kernel.CreateMutexW.restype = ctypes.c_void_p
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.CreateMutexW(None, False, APP_MUTEX)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        yield
    finally:
        kernel.CloseHandle(handle)
