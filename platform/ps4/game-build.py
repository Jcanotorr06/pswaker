#!/usr/bin/env python3
"""Associate the game program with its actual PS4 inputs and stage a data-free payload."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('game_preparation', HERE / 'prepare-game.py')
preparation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preparation)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def inputs(root, platform):
    prepared = json.loads((root / 'evidence/game-inputs.json').read_text())
    for name, expected in prepared['prepared_sources'].items():
        directory = root / 'src' / name
        if expected != preparation.inventory(directory):
            raise ValueError(f'Prepared input changed: {directory}; rerun prepare-game.py')
    for key, directory in [('stub_headers', root / 'assets/GZLE01'),
                           ('aurora', root / 'src/aurora'), ('platform', root / 'src/platform')]:
        if prepared[key] != preparation.inventory(directory):
            raise ValueError(f'Prepared input changed: {directory}; rerun prepare-game.py')
    archives = [platform / 'build/dawn/src/dawn/native/libwebgpu_dawn.a',
                platform / 'build/sdl3/libSDL3.a']
    for directory in ['sysroot/lib', 'build/mesa', 'sdk/opt/pacbrew/ps4/openorbis/lib']:
        archives += sorted((platform / directory).rglob('*.a'))
    # Include exact runtime sources/toolchain; a platform change invalidates the game cache ID.
    records = {p.relative_to(platform).as_posix(): preparation.digest(p) for p in archives}
    for directory in ['toolchain', 'refs/DolphinPS4/toolchain', 'refs/DolphinPS4/port',
                      'src/native-platform/ps4', 'src/dawn/include', 'build/dawn/gen/include',
                      'src/sdl3/include', 'build/sdl3', 'src/abseil', 'src/fetch',
                      'sysroot', 'sdk/opt/pacbrew/ps4/openorbis']:
        records.update({directory + '/' + name: sha for name, sha in
                        preparation.inventory(platform / directory).items()})
    code = {p.relative_to(HERE).as_posix(): preparation.digest(p) for p in sorted(HERE.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and
            not any(part in {'evidence', 'tests'} for part in p.relative_to(HERE).parts) and
            p.suffix not in {'.pyc', '.md'}}
    return {'preparation_sha256': preparation.digest(root / 'evidence/game-inputs.json'),
            'platform_inputs': records, 'port_inputs': code,
            'compiler': subprocess.check_output(['clang++-21', '--version'], text=True),
            'cmake': subprocess.check_output(['cmake', '--version'], text=True),
            'ninja': subprocess.check_output(['ninja', '--version'], text=True)}


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()[:20]


def stage(root, platform, version):
    recorded = json.loads((root / 'evidence/game-build-inputs.json').read_text())
    current = inputs(root, platform)
    if current != recorded:
        raise ValueError('Build inputs changed since configuration; rebuild before staging')
    build_id = identity(current)
    elf = root / 'build/switchwaker'
    executable = root / 'build/switchwaker_eboot/eboot.bin'
    # ps4_add_eboot operates in the wrapper directory but uses native's target ELF.
    if build_id.encode() not in elf.read_bytes():
        raise ValueError('Compiled game build identity does not match the current source/input closure')
    sections = subprocess.check_output(['llvm-readelf-21', '--sections', str(elf)], text=True)
    if '.symtab' not in sections or '.debug_line' not in sections:
        raise ValueError('Retain a matching unstripped ELF with source-line information')
    dynamic = subprocess.check_output(['llvm-readelf-21', '--dyn-syms', '--wide', str(elf)], text=True)
    if '_ZTH' in dynamic:
        raise ValueError('Unresolved TLS initializer in game ELF; audit static TLS declarations')
    commands = json.loads((root / 'build/compile_commands.json').read_text())
    for row in commands:
        command = row.get('command') or ' '.join(row['arguments'])
        if '-march=btver2' not in command or any(flag in command for flag in ['-march=znver2', '-march=native', '-mavx2']):
            raise ValueError('Unexpected target CPU flags: ' + row['file'])
    elf_report = subprocess.check_output(['llvm-readelf-21', '--file-header', '--program-headers',
                                          '--dynamic', str(elf)], text=True)
    (root / 'evidence/game-elf.txt').write_text(elf_report)
    write_json(root / 'evidence/game-abi-audit.json', {
        'elf_sha256': preparation.digest(elf), 'compiled_build_id': build_id,
        'compile_commands_checked': len(commands), 'cpu': 'btver2/Jaguar',
        'unresolved_tls_initializers': [], 'unstripped': True, 'debug_lines': True,
        'signal_handling': 'Selected PS4 DolphinPS4 logger; no PS5 context, division table or recovery handler',
        'hardware_status': 'Untested for this game binary'})
    stage_dir = root / 'build/program-stage'
    (stage_dir / 'sce_sys').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(executable, stage_dir / 'eboot.bin')
    shutil.copyfile(platform / 'refs/DolphinPS4/sce_sys/icon0.png', stage_dir / 'sce_sys/icon0.png')
    prepared = json.loads((root / 'evidence/game-inputs.json').read_text())
    manifest = {'program_build_id': build_id, 'app_version': version,
                'eboot_sha256': preparation.digest(executable),
                'elf_sha256': preparation.digest(elf),
                'hardware_status': 'UNTESTED installed-game candidate; owner evidence required for this exact binary',
                'scope': 'Frame-pacing candidate; independent installed-console Outset/forest samples and timing-method validation required for this exact binary; final integrated acceptance remains separate',
                'installed_image': '/app0/game.iso', 'user_data': '/data/pswaker/',
                'cache': '/data/pswaker/cache/' + build_id,
                'sources': prepared['sources'], 'patches': prepared['patches'],
                'platform_patches': prepared['platform_patches'],
                'platform_evidence': prepared['platform_evidence'],
                'build_inputs_sha256': preparation.digest(root / 'evidence/game-build-inputs.json'),
                'distribution_cleared': False}
    write_json(stage_dir / 'build-info.json', manifest)
    sdk = platform / 'sdk/opt/pacbrew/ps4/openorbis'
    env = dict(os.environ, OPENORBIS=str(sdk), OO_PS4_TOOLCHAIN=str(sdk),
               PS4_PKGTOOL=str(platform / 'build/pkgtool/PkgTool.Core'), SFO_STYLE='plain',
               DOLPHIN_PS4_MODULES_DIR='/nonexistent')
    # The inherited packager resolves this path before creating its output tree.
    (root / 'out/program').mkdir(parents=True, exist_ok=True)
    with (root / 'evidence/game-program-package.log').open('w') as log:
        subprocess.run(['bash', str(platform / 'refs/DolphinPS4/scripts/make-pkg.sh'),
                        str(stage_dir), 'PSWK00001', 'PSWaker', version, 'PSWAKERGAME',
                        str(root / 'out/program')], check=True, env=env,
                       stdout=log, stderr=subprocess.STDOUT)
    write_json(root / 'evidence/game-program.json', manifest)
    notices = {}
    for tree in [root / 'src/switchwaker', root / 'src/recompcore', root / 'src/decomp', root / 'src/ps5-reference']:
        for path in tree.rglob('*'):
            if path.is_file() and path.name.upper().startswith(('LICENSE', 'COPYING', 'NOTICE', 'COPYRIGHT')):
                relative = path.relative_to(root).as_posix()
                notices[relative] = preparation.digest(path)
                saved = root / 'evidence/license-notices' / relative
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, saved)
    write_json(root / 'evidence/game-license-review.json', {
        'program': manifest, 'game_notice_sha256': notices,
        'platform_license_audit_sha256': preparation.digest(platform / 'evidence/license-audit.json'),
        'review': 'GPL game/DSP sources and MIT reader provenance retained; inherited component notices retained with the maintained platform; SDK module/stub rights and combined distribution terms remain unresolved',
        'complete_package': 'Associate this report with the actual complete-package inspection and image hash before handoff',
        'distribution_cleared': False})
    print(json.dumps({'program': str(stage_dir), 'elf': str(elf), 'build_id': build_id}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['identity', 'stage'])
    parser.add_argument('root', type=Path)
    parser.add_argument('platform_root', type=Path)
    parser.add_argument('--app-version', default='01.00')
    args = parser.parse_args()
    if not re.fullmatch(r'\d{2}\.\d{2}', args.app_version):
        parser.error('--app-version must be NN.NN')
    try:
        root, platform = args.root.resolve(), args.platform_root.resolve()
        if args.command == 'identity':
            value = inputs(root, platform)
            write_json(root / 'evidence/game-build-inputs.json', value)
            print(identity(value))
        else:
            stage(root, platform, args.app_version)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'Game build failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
