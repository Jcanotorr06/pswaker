"""Data-free program fixture, used only in isolated copies of the production app."""
import shutil
import struct
import subprocess
import hashlib
import zlib


def png_bytes(width, height, *, colour_type=2, bit_depth=8, interlace=0, transparent=False, pixel=42,
              scanlines=None, compressed=None):
    """Generate synthetic PNGs without an image dependency on the desktop host."""
    def chunk(name, data):
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', zlib.crc32(name + data))
    planes = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[colour_type]
    header = struct.pack('>IIBBBBB', width, height, bit_depth, colour_type, 0, 0, interlace)
    extra = chunk(b'PLTE', bytes([pixel, pixel, pixel])) if colour_type == 3 else b''
    if transparent:
        extra += chunk(b'tRNS', struct.pack('>HHH', pixel, pixel, pixel))
    raw = b''
    passes = [(0, 0, 1, 1)] if not interlace else [
        (0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4),
        (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2)]
    for x, y, dx, dy in passes:
        columns, rows = len(range(x, width, dx)), len(range(y, height, dy))
        if columns and rows:
            row = b'\0' + bytes([pixel]) * (columns * planes * (bit_depth // 8))
            raw += row * (rows if scanlines is None else scanlines)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + extra
            + chunk(b'IDAT', zlib.compress(raw) if compressed is None else compressed) + chunk(b'IEND', b''))


def stage_artwork(stage, *, pixel=42):
    artwork = {}
    for role, resource, name, width, height in [
            ('icon', 'ICON0_PNG', 'icon0.png', 512, 512),
            ('splash', 'PIC1_PNG', 'pic1.png', 1920, 1080)]:
        data = png_bytes(width, height, pixel=pixel)
        (stage / 'sce_sys' / name).write_bytes(data)
        artwork[resource] = {'role': role, 'resource': resource, 'width': width, 'height': height,
                             'colour_type': 2, 'bit_depth': 8, 'interlace': 0,
                             'sha256': hashlib.sha256(data).hexdigest()}
    return artwork


def make_bundle(bundle, tools):
    from synthetic_pipeline import make_seed
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
                 'sce_module/libc.prx']:
        (stage / name).write_bytes(b'Synthetic nonplayable fixture: ' + name.encode())
    write_json(stage / 'build-info.json', {'app_version': '01.23', 'program_build_id': 'synthetic-program',
               'eboot_sha256': digest(stage / 'eboot.bin'), 'artwork': stage_artwork(stage)})
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
    make_seed(bundle / 'assembly-assets')
    seal_bundle(bundle)
    return bundle
