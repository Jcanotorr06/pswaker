"""Synthetic compiled game inputs for the public staging/inspection commands."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

from synthetic_program import png_bytes


def prepare(root, reference, locations):
    platform = root / 'platform'
    (root / 'evidence').mkdir(parents=True)
    sources = {}
    for name in ['switchwaker', 'recompcore', 'decomp', 'ps5-reference']:
        tree = root / 'src' / name
        tree.mkdir(parents=True)
        sources[name] = {}
    for name in ['aurora', 'platform']:
        (root / 'src' / name).mkdir()
    (root / 'assets/GZLE01').mkdir(parents=True)
    (root / 'evidence/game-inputs.json').write_text(json.dumps({
        'prepared_sources': sources, 'stub_headers': {}, 'aurora': {}, 'platform': {},
        'sources': [], 'patches': {}, 'platform_patches': {}, 'platform_evidence': {}}))
    for name in ['build/dawn/src/dawn/native/libwebgpu_dawn.a', 'build/sdl3/libSDL3.a',
                 'evidence/license-audit.json']:
        path = platform / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'synthetic platform input')
    # Execute the real packager with synthetic program/module bytes only.
    for name in ['refs/DolphinPS4/scripts/make-pkg.sh',
                 'sdk/opt/pacbrew/ps4/openorbis/bin/linux/create-gp4']:
        path = platform / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(reference) / name, path)
    shutil.copytree(Path(reference) / 'build/pkgtool', platform / 'build/pkgtool')
    for name in ['sce_sys/about/right.sprx', 'sce_module/libc.prx', 'sce_module/libSceFios2.prx']:
        path = platform / 'sdk/opt/pacbrew/ps4/openorbis/samples/piglet' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'Synthetic nonplayable module: ' + name.encode())
    cli = [sys.executable, str(locations.command('game-build.py'))]
    configured = subprocess.run(cli + ['identity', str(root), str(platform)],
                                check=True, capture_output=True, text=True)
    build_id = configured.stdout.strip()
    (root / 'build/switchwaker_eboot').mkdir(parents=True)
    source = root / 'synthetic.cpp'
    source.write_text(f'const char identity[] = "{build_id}"; int main() {{ return identity[0]; }}\n')
    subprocess.run(['clang++-21', '-g', '-march=btver2', str(source), '-o', str(root / 'build/switchwaker')],
                   check=True, capture_output=True)
    (root / 'build/switchwaker_eboot/eboot.bin').write_bytes(b'Synthetic nonplayable SELF ' + build_id.encode())
    (root / 'build/compile_commands.json').write_text(json.dumps([
        {'file': 'synthetic.cpp', 'command': 'clang++-21 -g -march=btver2 synthetic.cpp'}]))
    icon, splash = root / 'owner icon.png', root / 'owner splash.png'
    icon.write_bytes(png_bytes(512, 512))
    splash.write_bytes(png_bytes(1920, 1080))
    return platform, icon, splash, build_id
