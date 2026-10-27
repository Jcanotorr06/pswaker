#!/usr/bin/env python3
"""Maintainer-only build of the pinned, self-contained Windows packaging closure."""
import argparse
import hashlib
import io
from pathlib import Path
import subprocess
import tarfile
import tempfile
import urllib.request

from disc_image import require
from package_artifact import inventory, write_json
from windows_package import TOOL_REVISION as REVISION, TOOL_ARCHIVE as ARCHIVE_SHA256, TOOL_SDK as SDK_VERSION



def prepare(dotnet, output):
    output = output.resolve()
    require(not output.exists(), 'Tool output must not already exist')
    version = subprocess.check_output([str(dotnet), '--version'], text=True).strip()
    require(version == SDK_VERSION, f'Use the pinned .NET SDK {SDK_VERSION} for this maintainer build')
    url = f'https://api.github.com/repos/OpenOrbis/LibOrbisPkg/tarball/{REVISION}'
    with urllib.request.urlopen(url) as response:
        archive = response.read()
    require(hashlib.sha256(archive).hexdigest() == ARCHIVE_SHA256, 'Packaging source archive integrity mismatch')
    with tempfile.TemporaryDirectory(prefix='pswaker-native-tools-', dir=output.parent) as folder:
        work = Path(folder)
        with tarfile.open(fileobj=io.BytesIO(archive)) as source:
            source.extractall(work, filter='data')
        source_root, = [p for p in work.iterdir() if p.is_dir()]
        write_json(source_root / 'global.json', {'sdk': {'version': SDK_VERSION, 'rollForward': 'disable'}})
        # The established host adaptation, now published with its Windows runtime.
        for project in ['LibOrbisPkg.Core', 'PkgTool.Core']:
            path = source_root / project / (project + '.csproj')
            path.write_text(path.read_text().replace('net6.0', 'net8.0'))
        publish = work / 'publish'
        subprocess.run([str(dotnet), 'publish', str(source_root / 'PkgTool.Core/PkgTool.Core.csproj'),
                        '-c', 'Release', '-r', 'win-x64', '--self-contained', 'true',
                        '-p:PublishTrimmed=false', '-p:DebugType=None', '-p:DebugSymbols=false',
                        '-o', str(publish)], check=True)
        write_json(publish / 'tool-release.json', {
            'schema': 1, 'platform': 'win-x64', 'source_revision': REVISION,
            'source_archive_sha256': ARCHIVE_SHA256, 'sdk': SDK_VERSION,
            'adaptation': 'Retarget net6.0 projects to net8.0; self-contained win-x64 publish',
            'files': inventory(publish)})
        publish.rename(output)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dotnet', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(prepare(args.dotnet.resolve(), args.output))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'prepare-windows-tools: {error}\n')
