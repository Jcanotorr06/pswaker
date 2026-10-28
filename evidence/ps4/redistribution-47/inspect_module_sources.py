#!/usr/bin/env python3
"""Reproduce read-only module inspection; publish metadata, never extracted bytes.

Run on Linux with objdump:
  python3 inspect_module_sources.py BUILD_ROOT OUTPUT_JSON
BUILD_ROOT is the maintained build containing sdk/ and src/sdk-source/openorbis/.
Format references are recorded in the JSON. Only unencrypted, uncompressed SELF
segments are accepted. Disassembly is bounded by exported ELF function symbols;
executable segments also contain metadata and are not entirely instructions.
"""
import base64
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def nid(name):
    digest = hashlib.sha1(name.encode() + bytes.fromhex(
        '518D64A635DED8C1E6B039B1C3E55230')).digest()[:8][::-1]
    return base64.b64encode(digest).decode().rstrip('=').replace('/', '-')


root = Path(sys.argv[1])
source = root / 'src/sdk-source/openorbis/OpenOrbis-PS4-Toolchain-cd480230b946239f758333ef0dff40d67c5f0c20'
sample = root / 'sdk/opt/pacbrew/ps4/openorbis/samples/piglet'
report = {
    'format_source': 'https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/cd480230b946239f758333ef0dff40d67c5f0c20/scripts/make_fself.py',
    'symbols_source': 'https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/cd480230b946239f758333ef0dff40d67c5f0c20/scripts/symbol_entries.py',
    'nid_source': 'https://github.com/OpenOrbis/create-fself/blob/30d2e10507f55124cf21e85e19825482e4f93c87/pkg/oelf/OELFGenDynlibData.go',
    'limits': ['Body/data/export correspondence is not a full reconstruction of the inherited build.',
               'Disassembly uses exported function st_value/st_size, not whole segments.',
               'No source/build/staged input is modified; scratch segment bytes are temporary.'],
    'objdump_version': subprocess.check_output(['objdump', '--version'], text=True).splitlines()[0],
    'candidate_nids': {name: nid(name) for name in [
        '_Z5dummyv', '_Z19testLibraryFunctionv', 'printf',
        '__dummy__sce_fios2_func', '_Z23__dummy__sce_fios2_funcv',
        'sceGameRightGetVersion', 'sceGameRightGetString',
        'sceGameRightGetStringSizeInBytes', 'sceGameRightGetLogoPngImage',
        'sceGameRightGetLogoPngImageSizeInBytes']},
    'source_candidates': [], 'modules': []}
for relative in ['src/modules/libc/libc/lib.c',
                 'src/modules/libSceFios2/libSceFios2/lib.c',
                 'src/templates/PS4 SPRX Project/PS4 SPRX Project/lib.cpp',
                 'src/modules/right/right/lib.c',
                 'src/modules/right/right/string_data.h',
                 'src/modules/right/right/logo_data.h']:
    data = (source / relative).read_bytes()
    report['source_candidates'].append({'path': relative, 'sha256': sha(data)})

for path in sorted(sample.rglob('*prx')):
    data = path.read_bytes()
    assert data[:4] == bytes.fromhex('4f153d1d')
    count = struct.unpack_from('<H', data, 24)[0]
    elf_offset = 32 + 32 * count
    assert data[elf_offset:elf_offset + 4] == b'\x7fELF'
    header = struct.unpack_from('<HHIQQQIHHHHHH', data, elf_offset + 16)
    headers = [struct.unpack_from('<IIQQQQQQ', data,
               elf_offset + header[4] + i * header[8]) for i in range(header[9])]
    segments = {}
    segment_records = []
    for i in range(count):
        props, offset, size, memory_size = struct.unpack_from('<QQQQ', data, 32 + 32 * i)
        if not props & 0x800:
            continue
        assert not props & 0xA, 'Encrypted or compressed segment unsupported'
        index = (props >> 20) & 0xFFFF
        assert offset + size <= len(data)
        segments[index] = data[offset:offset + size]
        segment_records.append({'program_header_index': index, 'self_offset': offset,
                                'elf_offset': headers[index][2],
                                'virtual_address': headers[index][3],
                                'bytes': size, 'sha256': sha(segments[index])})
    dynamic_index = next(i for i, ph in enumerate(headers) if ph[0] == 0x61000000)
    dynamic_header = next(ph for ph in headers if ph[0] == 2)
    dynamic_data = segments[dynamic_index]
    start = dynamic_header[2] - headers[dynamic_index][2]
    tags = dict(struct.unpack_from('<QQ', dynamic_data, start + i)
                for i in range(0, dynamic_header[5], 16))
    symbols = []
    for offset in range(tags[0x61000039], tags[0x61000039] + tags[0x6100003F], 24):
        name, info, other, index, value, size = struct.unpack_from('<IBBHQQ', dynamic_data, offset)
        name = dynamic_data[tags[0x61000035] + name:].split(b'\0')[0].decode()
        symbol = dict(name=name, value=value, size=size, info=info, section_index=index)
        if info & 15 == 2 and index and size:
            segment_index = next(i for i, ph in enumerate(headers)
                                 if ph[0] == 1 and ph[1] & 1 and ph[3] <= value
                                 and value + size <= ph[3] + ph[5])
            relative = value - headers[segment_index][3]
            with tempfile.TemporaryDirectory(prefix='pswaker-module-47-') as scratch:
                segment_file = Path(scratch) / 'segment'
                segment_file.write_bytes(segments[segment_index])
                disassembly = subprocess.check_output([
                    'objdump', '-D', '-b', 'binary', '-m', 'i386:x86-64',
                    '--no-show-raw-insn', '--start-address=' + str(relative),
                    '--stop-address=' + str(relative + size), str(segment_file)], text=True)
            symbol['function_sha256'] = sha(segments[segment_index][relative:relative + size])
            symbol['disassembly'] = disassembly.split('Disassembly of section .data:\n', 1)[1].strip()
        symbols.append(symbol)
    item = {'name': path.name, 'sha256': sha(data), 'elf_header_self_offset': elf_offset,
            'segments': segment_records, 'symbols': symbols}
    parameter_header = next(ph for ph in headers if ph[0] == 0x61000002)
    parameter_segment = next(i for i, ph in enumerate(headers)
                             if i in segments and ph[2] <= parameter_header[2]
                             and parameter_header[2] + 24 <= ph[2] + ph[5])
    parameter_offset = parameter_header[2] - headers[parameter_segment][2]
    parameters = struct.unpack_from('<QQQ', segments[parameter_segment], parameter_offset)
    item['module_parameter_comparison'] = {
        'source': 'src/crt/crtlib.S', 'values': list(parameters),
        'matches_assembly_size_magic_sdk_version': parameters == (0x18, 0x13C13F4BF, 0x1000051)}
    if path.name == 'right.sprx':
        logo = bytes(int(x, 16) for x in re.findall(r'0x([0-9a-fA-F]{2})',
                     (source / 'src/modules/right/right/logo_data.h').read_text()))
        text = b'Homebrew was built with the OpenOrbis PS4 Toolchain.\n\nhttps://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain'
        item['right_data_comparison'] = {
            'source_logo_bytes': len(logo), 'source_logo_sha256': sha(logo),
            'source_logo_found_self_offset': data.find(logo),
            'pinned_lf_string_found_self_offset': data.find(text),
            'historical_crlf_string_found_self_offset': data.find(text.replace(b'\n', b'\r\n'))}
    report['modules'].append(item)
Path(sys.argv[2]).write_text(json.dumps(report, indent=2) + '\n')
