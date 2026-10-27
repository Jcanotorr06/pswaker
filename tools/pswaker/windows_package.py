"""Offline Windows adapter: bundled inputs to a freshly inspected private package."""
from datetime import datetime, timezone
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import traceback
import xml.etree.ElementTree as ET

from disc_image import CONTRACT, require, validate
from package_artifact import (IDENTITIES, INSTALLED_IMAGE, StageFailure, Stages, content_id, digest,
                              expected_sfo_fields, inspect_package, inventory, sfo_fields, write_json)
from package_validation import validate_selection
from program_payload import PROGRAM_FILES, bundled_program

TOOL_REVISION = '594021fdc435409f755a6ae0781b65ec6cec846c'
TOOL_ARCHIVE = 'c4b918b404e486784717a415cc5a50d866bc56099ed027b4d6bd443cf7f90ee6'
TOOL_SDK = '8.0.427'

INSTALL_INSTRUCTIONS = (
    'Manual installation — PS4 Slim / firmware 9.00 / GoldHEN v2.4b18\n'
    '1. Copy the verified .pkg to the root of an exFAT or FAT32 USB drive '
    '(use exFAT for files over 4 GB). Safely eject it and connect it to the PS4.\n'
    '2. With your established GoldHEN v2.4b18 environment active, open Settings → '
    'GoldHEN → Debug Settings → Package Installer and install the package from USB.\n'
    '3. Launch PSWaker from the home screen. The image is installed inside the app; '
    'remove the USB drive after installation. Gameplay needs no USB or external image.\n'
    'Keep your image and complete package private. Package verification does not establish console acceptance.'
)


def checked_tools(root):
    release = json.loads((root / 'tool-release.json').read_text())
    require(release['schema'] == 1 and release['platform'] == 'win-x64'
            and release['source_revision'] == TOOL_REVISION
            and release['source_archive_sha256'] == TOOL_ARCHIVE and release['sdk'] == TOOL_SDK,
            'Unsupported bundled Windows packaging tools; reinstall the complete application')
    files = inventory(root)
    del files['tool-release.json']
    require(files == release['files'] and {'PkgTool.Core.exe', 'PkgTool.Core.dll', 'LibOrbisPkg.Core.dll',
            'coreclr.dll', 'hostfxr.dll', 'hostpolicy.dll'}.issubset(files),
            'Bundled packaging closure is incomplete or changed; reinstall the application')
    return release


def checked_program(bundle):
    version, build_id = bundled_program(bundle)
    root = bundle / 'program'
    release = json.loads((root / 'program-release.json').read_text())
    name = release['elf_filename']
    require(isinstance(name, str) and Path(name).name == name and name not in {'.', '..'},
            'Invalid bundled matching ELF name')
    require(set(release['payload_sha256']) == PROGRAM_FILES, 'Unexpected bundled program inventory')
    expected = {'stage/' + path: sha for path, sha in release['payload_sha256'].items()}
    expected['elf/' + name] = release['elf_sha256']
    actual = inventory(root)
    del actual['program-release.json']
    require(actual == expected, 'Bundled program files differ from the verified release')
    info = json.loads((root / 'stage/build-info.json').read_text())
    require(info['eboot_sha256'] == release['eboot_sha256'] == expected['stage/eboot.bin'],
            'Bundled program SELF identity mismatch')
    binary = (root / 'elf' / name).read_bytes()
    require(len(binary) >= 64 and binary[:6] == b'\x7fELF\x02\x01'
            and struct.unpack_from('<H', binary, 18)[0] == 62 and build_id.encode() in binary,
            'Bundled game ELF/build identity mismatch')
    fields = sfo_fields((root / 'stage/sce_sys/param.sfo').read_bytes())
    identity = IDENTITIES['game']
    require(all(fields.get(key) == value for key, value in expected_sfo_fields(identity, version).items()),
            'Bundled game SFO identity mismatch')
    return version, release


def bundle_inventory(bundle):
    return {directory + '/' + name: sha for directory in ['program', 'packaging', 'platform']
            for name, sha in inventory(bundle / directory).items()}


def seal_bundle(bundle):
    """Maintainer operation; record the fixed release inputs shipped beside the app."""
    version, release = checked_program(bundle)
    checked_tools(bundle / 'packaging')
    write_json(bundle / 'desktop-release.json', {'schema': 1, 'app_version': version,
               'program_build_id': release['build_id'], 'files': bundle_inventory(bundle)})


def inspect_output(output, bundle):
    """Reinspect a retained artifact using the fixed Windows tool closure."""
    output = output.resolve()
    (output / 'inspection.json').unlink(missing_ok=True)
    fixed = json.loads((bundle / 'desktop-release.json').read_text())
    require(fixed['schema'] == 1 and fixed['files'] == bundle_inventory(bundle), 'Bundled release inputs changed')
    require(digest(CONTRACT) == fixed['files']['platform/ps4/content-contract.json'], 'Validation contract changed')
    with tempfile.TemporaryDirectory(prefix='scratch-', dir=output) as scratch:
        return inspect_package(output, WindowsTools(bundle / 'packaging', output, Path(scratch)))


class WindowsTools:
    def __init__(self, root, work, scratch):
        self.root, self.work = root, work
        self.pkgtool = root / 'PkgTool.Core.exe'
        self.env = dict(os.environ, DOTNET_SYSTEM_GLOBALIZATION_INVARIANT='1',
                        DOTNET_MULTILEVEL_LOOKUP='0', DOTNET_CLI_TELEMETRY_OPTOUT='1',
                        TEMP=str(scratch), TMP=str(scratch))
        self.commands = []

    def capture(self, command):
        self.commands.append({'argv': list(map(str, command))})
        write_json(self.work / 'commands.json', self.commands)
        result = subprocess.run(list(map(str, command)), cwd=self.work, env=self.env,
                                capture_output=True, text=True, encoding='utf-8', errors='replace',
                                creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:
            # Preserve tool details even when the workspace log cannot be written.
            failure = ValueError(f'Windows packaging tool {command[1]} failed (exit code {result.returncode}). '
                                 'If the problem persists, reinstall the complete application.')
            failure.add_note('Tool output:\n' + result.stdout + result.stderr)
            raise failure
        with (self.work / 'tools.log').open('a', encoding='utf-8') as log:
            log.write(result.stdout + result.stderr)
        return result.stdout

    def run(self, command):
        self.capture(command)

    def provenance(self):
        return checked_tools(self.root)


def write_project(stage, target):
    """Native GP4 serialization; all paths are application-owned, fixed-inventory files."""
    project = ET.Element('psproject', fmt='gp4', version='1000')
    volume = ET.SubElement(project, 'volume')
    ET.SubElement(volume, 'volume_type').text = 'pkg_ps4_app'
    ET.SubElement(volume, 'volume_id').text = 'PS4VOLUME'
    ET.SubElement(volume, 'volume_ts').text = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    ET.SubElement(volume, 'package', content_id=content_id(IDENTITIES['game']),
                  passcode='0' * 32, storage_type='digital50', app_type='full')
    chunks = ET.SubElement(volume, 'chunk_info', chunk_count='1', scenario_count='1')
    ET.SubElement(ET.SubElement(chunks, 'chunks'), 'chunk', id='0', layer_no='0', label='Chunk #0')
    scenarios = ET.SubElement(chunks, 'scenarios', default_id='0')
    ET.SubElement(scenarios, 'scenario', id='0', type='sp', initial_chunk_count='1', label='Scenario #0').text = '0'
    files = ET.SubElement(project, 'files', img_no='0')
    for name in inventory(stage):
        ET.SubElement(files, 'file', targ_path=name, orig_path=str(stage / name))
    directories = {'.': ET.SubElement(project, 'rootdir')}
    for path in sorted(p for p in stage.rglob('*') if p.is_dir()):
        relative = path.relative_to(stage)
        directories[relative.as_posix()] = ET.SubElement(
            directories[relative.parent.as_posix()], 'dir', targ_name=relative.name)
    ET.ElementTree(project).write(target, encoding='utf-8', xml_declaration=True)


@contextmanager
def private_workspace(destination, stages):
    with stages('prepare'):
        work = Path(tempfile.mkdtemp(prefix='.complete-', dir=destination.parent))
    try:
        yield work
    except Exception as error:
        try:
            shutil.rmtree(work)
        except OSError as cleanup:
            raise StageFailure(getattr(error, 'stage', 'cleanup'),
                               f'{error}\nCleanup also failed: {cleanup}\n'
                               f'Private unfinished workspace remains at {work}. '
                               'Restore folder access before removing this workspace and retrying.') from error
        raise
    else:
        if work.exists():
            with stages('cleanup'):
                shutil.rmtree(work)


def create_package(image, output, bundle, *, accepted_image=None, observe=None):
    """Report actionable local failures without exposing an unfinished package."""
    try:
        return _create_package(image, output, bundle, accepted_image=accepted_image, observe=observe)
    except StageFailure as error:
        message = (f'{error}\nCheck that the image is readable and the destination drive is connected, '
                   'writable and has enough free space. Correct the problem or choose another folder, '
                   'then validate again and retry.')
        try:
            logs = Path(os.environ['LOCALAPPDATA']) / 'PSWaker/logs'
            logs.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(prefix='package-', suffix='.log', dir=logs, delete=False) as saved:
                details = ''.join(traceback.format_exception(error))
                saved.write(f'Failed stage: {error.stage}\n{message}\n{details}'.encode('utf-8'))
                message += f'\nLocal diagnostic log: {saved.name}'
        except (OSError, KeyError):
            pass
        raise StageFailure(error.stage, message) from error


def _create_package(image, output, bundle, *, accepted_image=None, observe=None):
    """Create only with bundled game/tools; publish only after fresh artifact inspection."""
    stages = Stages(observe)
    with stages('validate'):
        destination = output.resolve()
        require(sys.platform == 'win32', 'Complete desktop packaging requires Windows x64')
        original = validate_selection(image, destination)
        require(accepted_image is None or original == accepted_image,
                'The image changed after validation. Validate the selected image again.')
        # Stage, PKG, fresh extraction and packager scratch can coexist. Also
        # retain the program/ELF and the complete self-contained tool snapshot.
        program_bytes = sum(p.stat().st_size for p in (bundle / 'program').rglob('*') if p.is_file())
        tool_bytes = sum(p.stat().st_size for p in (bundle / 'packaging').rglob('*') if p.is_file())
        required = 4 * (image.stat().st_size + program_bytes) + tool_bytes + 512 * 1024**2
        require(shutil.disk_usage(destination.parent).free >= required,
                f'Insufficient free space at {destination.parent}: at least {required / 1024**3:.2f} GiB '
                'is needed for staging, tools, package, scratch and fresh extraction. '
                'Free space or choose a destination on a drive with more space, then retry.')
    with private_workspace(destination, stages) as work:
        with stages('verify-program'):
            fixed = json.loads((bundle / 'desktop-release.json').read_text())
            require(fixed['schema'] == 1 and fixed['files'] == bundle_inventory(bundle),
                    'Bundled release inputs changed. Reinstall the complete application.')
            require(digest(CONTRACT) == fixed['files']['platform/ps4/content-contract.json'],
                    'Bundled validation contract changed. Reinstall the application.')
            version, release = checked_program(bundle)
            require(version == fixed['app_version'] and release['build_id'] == fixed['program_build_id'],
                    'Bundled program version/build differs from the application release')
            shutil.copytree(bundle / 'packaging', work / 'packaging')
            shutil.copytree(bundle / 'program', work / 'program')
            # Verify the snapshot used below, independent of later bundle changes.
            version, release = checked_program(work)
            for directory in ['program', 'packaging']:
                expected = {name[len(directory) + 1:]: sha for name, sha in fixed['files'].items()
                            if name.startswith(directory + '/')}
                require(inventory(work / directory) == expected, 'Bundled inputs changed while copying; retry')
            scratch = work / 'scratch'
            scratch.mkdir()
            tools = WindowsTools(work / 'packaging', work, scratch)
            provenance = tools.provenance()
            stage = work / 'stage'
            (work / 'program/stage').rename(stage)
            (work / 'program/elf').rename(work / 'elf')
            program = {key: release[key] for key in [
                'build_id', 'elf_filename', 'elf_sha256', 'eboot_sha256', 'payload_sha256']}
        with stages('assemble'):
            shutil.copyfile(image, stage / 'game.iso')
            copied = validate(stage / 'game.iso')
            require(copied == original, 'Image changed during assembly; validate a stable local image and retry')
            identity = IDENTITIES['game']
            manifest = {'schema': 1, 'kind': 'game', 'acceptance': identity['acceptance'],
                        'title_id': identity['title_id'], 'content_id': content_id(identity),
                        'app_version': version, 'installed_image': INSTALLED_IMAGE, 'image': copied,
                        'program': program, 'distribution_cleared': False}
            write_json(stage / 'complete-package.json', manifest)
            files = inventory(stage)
            write_project(stage, work / 'package.gp4')
            (work / 'out').mkdir()
            tools.run([tools.pkgtool, 'pkg_build', work / 'package.gp4', work / 'out'])
            package = work / 'out' / (content_id(identity) + '.pkg')
            require(package.is_file(), 'Windows packager produced no package. Review local tools.log and retry.')
            # Record only the two entries the pinned packager generates/updates.
            with tempfile.TemporaryDirectory(prefix='metadata-', dir=work) as extracted:
                extracted = Path(extracted)
                tools.run([tools.pkgtool, 'pkg_extract', package, extracted])
                files['sce_sys/keystone'] = digest(extracted / 'uroot/sce_sys/keystone')
                entries = tools.capture([tools.pkgtool, 'pkg_listentries', package])
                rows = [line.split() for line in entries.splitlines()
                        if line.split() and line.split()[-1] == 'PARAM_SFO']
                require(len(rows) == 1, 'Missing/duplicate packaged SFO')
                sfo = extracted / 'param.sfo'
                tools.run([tools.pkgtool, 'pkg_extractentry', package, rows[0][3], sfo])
                fields = sfo_fields(sfo.read_bytes())
                require({k: v for k, v in fields.items() if k not in {'PUBTOOLINFO', 'PUBTOOLVER'}}
                        == sfo_fields((stage / 'sce_sys/param.sfo').read_bytes()),
                        'Packager changed game metadata unexpectedly')
                files['sce_sys/param.sfo'] = digest(sfo)
            report = {'schema': 1, 'kind': 'game', 'app_version': version, 'manifest': manifest,
                      'program': program, 'tools': provenance, 'payload_sha256': files,
                      'desktop_release_sha256': digest(bundle / 'desktop-release.json'),
                      'package': {'filename': package.name, 'sha256': digest(package)}}
            write_json(work / 'assembly.json', report)
        with stages('inspect'):
            inspect_package(work, tools)
        with stages('publish'):
            require(digest(package) == report['package']['sha256'], 'Package changed after inspection; retry')
            write_json(work / 'stages.json', stages.timings)
            (work / 'INSTALL.txt').write_text(INSTALL_INSTRUCTIONS, encoding='utf-8')
            for directory in [stage, work / 'packaging', work / 'program', scratch]:
                shutil.rmtree(directory)
            require(not destination.exists(), 'Output appeared during assembly; choose a new destination')
            # Windows rename refuses an existing destination, including a racing empty folder.
            work.rename(destination)
    return {'output': str(destination), 'package': report['package'], 'acceptance': identity['acceptance']}
