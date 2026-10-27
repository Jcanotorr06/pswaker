#!/usr/bin/env python3
"""Recheck the retained #23 program's inherited inputs without building or packaging.

Run on the recorded Linux host. Writes only audit metadata and verified notice
texts to a new evidence directory; never copies program or owner content bytes.
This checkpoint helper is outside the maintained build input inventory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tarfile
import zipfile


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository', type=Path)
    parser.add_argument('platform_root', type=Path)
    parser.add_argument('game_root', type=Path)
    parser.add_argument('output', type=Path, help='New output directory')
    parser.add_argument('--source-snapshot', type=Path, required=True,
                        help='Retained repository snapshot used for this game build')
    args = parser.parse_args()
    repo, platform, game = [p.resolve() for p in
                            (args.repository, args.platform_root, args.game_root)]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    sdk = platform / 'sdk/opt/pacbrew/ps4/openorbis'

    def normalized(text):
        for root, label in [(platform, '<platform>'), (game, '<game>'), (repo, '<repository>')]:
            text = text.replace(str(root), label)
        return text

    def record(path, root):
        return {'path': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size,
                'sha256': digest(path)}

    def read(path):
        return json.loads(path.read_text())

    def write(name, value):
        (output / name).write_text(json.dumps(value, indent=2) + '\n')

    info = read(game / 'build/program-stage/build-info.json')
    elf = game / 'build/switchwaker'
    stage = game / 'build/program-stage'
    require(digest(elf) == info['elf_sha256'], 'Game ELF differs from recorded candidate')
    require(digest(stage / 'eboot.bin') == info['eboot_sha256'], 'Staged SELF differs')
    expected_files = {'eboot.bin', 'build-info.json', 'sce_sys/icon0.png', 'sce_sys/param.sfo',
                      'sce_sys/about/right.sprx', 'sce_module/libSceFios2.prx', 'sce_module/libc.prx'}
    files = {p.relative_to(stage).as_posix() for p in stage.rglob('*') if p.is_file()}
    require(files == expected_files, 'Unexpected program-stage closure; review before collecting')
    write('program.json', {'build_id': info['program_build_id'], 'version': info['app_version'],
                          'elf': record(elf, game),
                          'stage': [record(stage / name, stage) for name in sorted(files)],
                          'distribution_cleared': False,
                          'scope': 'Retained #23 data-free stage; no complete package read or exported'})

    dynamic = subprocess.check_output(['llvm-readelf-21', '--dynamic', str(elf)], text=True)
    (output / 'elf-dynamic.txt').write_text(dynamic)
    needed = re.findall(r'Shared library: \[([^]]+)\]', dynamic)
    old_inputs = read(game / 'evidence/game-build-inputs.json')['platform_inputs']
    stub_package = next(p for p in read(repo / 'platform/ps4/sdk.lock.json')['packages']
                        if p['name'] == 'ps4-openorbis-orbis-lib-gen')
    package_path = platform / 'downloads/pacbrew' / stub_package['filename']
    require(digest(package_path) == stub_package['sha256'], 'Stub package differs from lock')
    stubs = []
    with tarfile.open(package_path) as package:
        members = {m.name.lstrip('./'): m for m in package.getmembers() if m.isfile()}
        for name in needed:
            path = sdk / 'lib' / name
            relative = path.relative_to(platform).as_posix()
            member = 'opt/pacbrew/ps4/openorbis/lib/' + name
            require(digest(path) == old_inputs[relative], 'Stub changed since game build: ' + name)
            with package.extractfile(members[member]) as stream:
                member_digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            require(member_digest == digest(path), 'Stub differs from package: ' + name)
            stubs.append(dict(record(path, platform), package_member=member,
                              matches_locked_package=True, matches_recorded_game_input=True))
    write('import-stubs.json', {'package': stub_package, 'needed': stubs,
                              'limits': 'DT_NEEDED identifies direct imports, not a removal proof or rights grant'})

    sdk_archive = platform / 'downloads/sdk-source/openorbis.zip'
    sdk_lock = next(row for row in read(repo / 'platform/ps4/dependencies.lock.json')['archives']
                    if row['path'] == 'sdk-source/openorbis.zip')
    require(digest(sdk_archive) == sdk_lock['sha256'], 'SDK source archive differs from lock')
    modules = []
    with zipfile.ZipFile(sdk_archive) as archive:
        prefix = archive.namelist()[0].split('/')[0] + '/'
        source_candidates = []
        for name in sorted(archive.namelist()):
            relative = name.removeprefix(prefix)
            if relative.startswith('src/modules/') and not name.endswith('/'):
                source_candidates.append({'path': relative, 'bytes': archive.getinfo(name).file_size,
                                          'sha256': hashlib.sha256(archive.read(name)).hexdigest()})
        for name in sorted(files):
            if not name.endswith(('.prx', '.sprx')):
                continue
            member = 'samples/piglet/' + name
            sha = hashlib.sha256(archive.read(prefix + member)).hexdigest()
            require(sha == digest(sdk / member) == digest(stage / name), 'Module provenance differs: ' + name)
            modules.append(dict(record(stage / name, stage), archive_member=prefix + member,
                                matches_sdk_and_pinned_archive=True))
    write('modules.json', {'source_archive': sdk_lock, 'packaged_modules': modules,
                           'source_candidates': source_candidates,
                           'limits': 'Candidate sources exist; matching archive membership alone does not prove binary correspondence or per-file rights'})

    ninja = (game / 'build/build.ninja').read_text()
    target = re.search(r'^build switchwaker:.*?(?=^build |^# ===|\Z)', ninja, re.M | re.S)
    require(target is not None, 'Missing native link rule')
    block = target.group()
    libraries = re.search(r'^  LINK_LIBRARIES = (.*)$', block, re.M)
    require(libraries is not None, 'Missing native link libraries')
    (output / 'link-rule.txt').write_text(normalized(block))
    archives = []
    search = [sdk / 'lib', sdk / 'usr/lib']
    for name in shlex.split(libraries.group(1)):
        if name.startswith('-l'):
            candidates = [directory / ('lib' + name[2:] + suffix)
                          for directory in search for suffix in ['.so', '.a']]
            path = next((p for p in candidates if p.is_file()), None)
            require(path is not None, 'Cannot resolve link input: ' + name)
        elif name.endswith(('.a', '.o')):
            path = Path(name) if Path(name).is_absolute() else game / 'build' / name
        else:
            continue
        root, label = (platform, 'platform') if path.is_relative_to(platform) else (game, 'game')
        archives.append(dict(record(path, root), root=label, link_argument=normalized(name)))
    write('link-inputs.json', {'libraries_in_link_order': archives,
                             'limits': 'Link arguments, not an archive-member extraction map; response-file objects remain in retained build tree'})

    retained = []
    for row in read(repo / 'platform/ps4/dependencies.lock.json')['archives']:
        path = platform / 'downloads' / row['path']
        require(digest(path) == row['sha256'], 'Locked platform download differs: ' + row['path'])
        retained.append(dict(record(path, platform), root='platform', url=row['url']))
    for row in read(platform / 'evidence/source-archives.json'):
        name = (Path(row['archive_url']).name if row['path'].startswith('src/llvm-project')
                else row['path'].replace('/', '-') + '.tar.gz')
        path = platform / 'downloads' / name
        require(digest(path) == row['archive_sha256'], 'Platform source archive differs: ' + name)
        retained.append(dict(record(path, platform), root='platform', url=row['archive_url']))
    for row in info['sources']:
        path = game / 'downloads' / (row['name'] + '.tar.gz')
        require(digest(path) == row['sha256'], 'Game source archive differs: ' + row['name'])
        retained.append(dict(record(path, game), root='game', url=row['archive_url']))
    write('retained-downloads.json', retained)

    snapshot = args.source_snapshot.resolve()
    source_inputs = read(game / 'evidence/game-build-inputs.json')['port_inputs']
    snapshot_records = []
    for name, sha in source_inputs.items():
        path = snapshot / 'platform/ps4' / name
        require(digest(path) == sha, 'Retained repository source differs: ' + name)
        snapshot_records.append(record(path, snapshot))
    write('retained-source-snapshot.json', snapshot_records)

    notices = []
    (output / 'notices').mkdir()
    audit = read(platform / 'evidence/license-audit.json')
    game_audit = read(game / 'evidence/game-license-review.json')
    for root, label, rows in [(platform, 'platform', audit['notice_files']),
                               (game, 'game', [{'path': p, 'sha256': sha}
                                              for p, sha in game_audit['game_notice_sha256'].items()])]:
        for row in rows:
            path = root / row['path']
            require(digest(path) == row['sha256'], 'Retained notice differs: ' + row['path'])
            saved = output / 'notices' / (row['sha256'] + '.txt')
            shutil.copyfile(path, saved)
            notices.append(dict(row, root=label, retained_notice=saved.relative_to(output).as_posix()))
    write('notice-index.json', notices)

    inputs = []
    for root, label, names in [
        (platform, 'platform', ['evidence/input-closure.json', 'evidence/license-audit.json',
                                'evidence/local-adaptations.json', 'evidence/renderer-reconciliation.json',
                                'evidence/patches-runtime.json', 'evidence/patches-graphics.json',
                                'evidence/patches-aurora.json', 'evidence/patches-packager.json']),
        (game, 'game', ['evidence/game-inputs.json', 'evidence/game-build-inputs.json',
                        'evidence/game-license-review.json', 'build/compile_commands.json',
                        'build/cos_exe/objects.rsp'])]:
        inputs.extend(dict(record(root / name, root), root=label) for name in names)
    write('retained-records.json', inputs)
    write('tools.json', {name: {'executable_sha256': digest(Path(shutil.which(name))),
                              'version': subprocess.check_output([name, '--version'], text=True).splitlines()[0]}
                         for name in ['python3', 'llvm-readelf-21', 'ninja']})
    print(f'Checked {len(modules)} modules, {len(stubs)} direct import stubs, '
          f'{len(retained)} downloads and {len(notices)} notices; distribution remains uncleared.')


if __name__ == '__main__':
    main()
