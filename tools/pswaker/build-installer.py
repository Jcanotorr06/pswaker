#!/usr/bin/env python3
"""Maintainer-only private offline Windows installer and exact release audit."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile

from disc_image import require
from package_artifact import digest, inventory, write_json


def build(program, packaging, output, app_version, iscc, *, assembly_assets):
    require(re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', app_version)
            and all(int(part) <= 65535 for part in app_version.split('.')),
            'App version must be four numeric Windows version components (0..65535)')
    require(iscc.is_absolute() and iscc.is_file(), 'Supply the explicit Inno Setup 6.7.3 ISCC.exe path')
    output = output.resolve()
    require(not output.exists() and output.parent.is_dir(), 'Choose an absent output with an existing parent')
    spec = importlib.util.spec_from_file_location('build_desktop', Path(__file__).with_name('build-desktop.py'))
    assert spec and spec.loader
    desktop = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(desktop)
    with tempfile.TemporaryDirectory(prefix='pswaker-installer-', dir=output.parent) as folder:
        work = Path(folder)
        exe = desktop.build(program, packaging, work / 'desktop', app_version, assembly_assets=assembly_assets)
        app = exe.parent
        manifest = json.loads((app / 'application-release.json').read_text())
        release_directory = app_version + '-' + digest(app / 'application-release.json')[:16]
        candidate = work / 'candidate'
        candidate.mkdir()
        script = Path(__file__).with_name('desktop-installer.iss')
        subprocess.run([str(iscc), '/Q', '/DAppVersion=' + app_version,
                        '/DReleaseDirectory=' + release_directory, '/DAppSource=' + str(app),
                        '/O' + str(candidate), str(script)], check=True)
        installer, = candidate.glob('*.exe')
        fixed = app / '_internal'
        write_json(candidate / 'installer-release.json', {
            'schema': 1, 'private_candidate': True, 'app_version': app_version,
            'platform': 'win-x64', 'release_directory': release_directory,
            'installer': {'filename': installer.name, 'sha256': digest(installer)},
            'compiler': {'name': 'Inno Setup', 'version': '6.7.3',
                         'files': inventory(iscc.parent)},
            'recipe_sha256': digest(script), 'application_manifest_sha256': digest(app / 'application-release.json'),
            'application': manifest, 'desktop': json.loads((fixed / 'desktop-release.json').read_text()),
            'program': json.loads((fixed / 'program/program-release.json').read_text()),
            'tools': json.loads((fixed / 'packaging/tool-release.json').read_text())})
        candidate.rename(output)
    return output / installer.name


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--program', type=Path, required=True)
    parser.add_argument('--packaging', type=Path, required=True)
    parser.add_argument('--assembly-assets', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--app-version', required=True)
    parser.add_argument('--iscc', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(build(args.program, args.packaging, args.output, args.app_version, args.iscc,
                    assembly_assets=args.assembly_assets))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'build-installer: {error}\n')
