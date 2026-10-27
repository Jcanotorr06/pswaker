"""Data-free program fixture, used only in isolated copies of the production app."""
import json
from pathlib import Path
import shutil
import struct
import subprocess


def make_bundle(bundle, tools):
    from disc_image import CONTRACT
    from package_artifact import digest, inventory, write_json
    from windows_package import seal_bundle
    shutil.copytree(tools, bundle / 'packaging')
    contract = bundle / 'platform/ps4/content-contract.json'
    contract.parent.mkdir(parents=True)
    shutil.copyfile(CONTRACT, contract)
    stage = bundle / 'program/stage'
    (stage / 'sce_sys/about').mkdir(parents=True)
    (stage / 'sce_module').mkdir()
    (bundle / 'program/elf').mkdir()
    elf = bytearray(128)
    elf[:6] = b'\x7fELF\x02\x01'
    struct.pack_into('<H', elf, 18, 62)
    elf[64:64 + len(b'synthetic-program')] = b'synthetic-program'
    (bundle / 'program/elf/game').write_bytes(elf)
    for name in ['eboot.bin', 'sce_sys/about/right.sprx', 'sce_module/libSceFios2.prx',
                 'sce_module/libc.prx', 'sce_sys/icon0.png']:
        (stage / name).write_bytes(b'Synthetic nonplayable fixture: ' + name.encode())
    write_json(stage / 'build-info.json', {'app_version': '01.23', 'program_build_id': 'synthetic-program',
               'eboot_sha256': digest(stage / 'eboot.bin')})
    tool = str(bundle / 'packaging/PkgTool.Core.exe')
    sfo = str(stage / 'sce_sys/param.sfo')
    subprocess.run([tool, 'sfo_new', sfo], check=True, capture_output=True)
    for key, value in {'TITLE_ID': 'PSWK00001', 'CONTENT_ID': 'IV0000-PSWK00001_00-PSWAKERGAME00000',
                       'TITLE': 'PSWaker', 'APP_VER': '01.23', 'VERSION': '01.23', 'CATEGORY': 'gd',
                       'APP_TYPE': 1, 'ATTRIBUTE': 0, 'SYSTEM_VER': 0}.items():
        subprocess.run([tool, 'sfo_setentry', '--type', 'int' if isinstance(value, int) else 'utf8',
                        '--maxsize', '128', '--value', str(value), sfo, key], check=True, capture_output=True)
    write_json(bundle / 'program/program-release.json', {
        'schema': 1, 'kind': 'game', 'build_id': 'synthetic-program', 'elf_filename': 'game',
        'elf_sha256': digest(bundle / 'program/elf/game'), 'eboot_sha256': digest(stage / 'eboot.bin'),
        'payload_sha256': inventory(stage)})
    seal_bundle(bundle)
    return bundle
