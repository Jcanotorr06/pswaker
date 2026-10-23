#!/usr/bin/env python3
"""Inspect matching ELF, SELF and extracted diagnostic PKG; never run target code."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inspect(root):
    artifacts = json.loads((root / 'evidence/artifacts.json').read_text())
    package = root / 'out' / artifacts['package']['filename']
    require(digest(package) == artifacts['package']['sha256'], 'Package SHA-256 mismatch')
    elf = root / 'build/probe/platform_diagnostic'
    require(digest(elf) == artifacts['elf_sha256'], 'ELF SHA-256 mismatch')
    binary = elf.read_bytes()
    require(binary[:6] == b'\x7fELF\x02\x01', 'Expected little-endian ELF64')
    require(struct.unpack_from('<H', binary, 18)[0] == 62, 'Expected x86-64 ELF')
    phoff = struct.unpack_from('<Q', binary, 32)[0]
    phsize, phnum = struct.unpack_from('<HH', binary, 54)
    loads = [struct.unpack_from('<IIQQQQQQ', binary, phoff + i * phsize) for i in range(phnum)]
    loads = [header for header in loads if header[0] == 1]
    require(bool(loads) and loads[0][3] == 0, 'First ELF PT_LOAD must start at zero')
    sections = subprocess.check_output(['llvm-readelf-21', '--sections', str(elf)], text=True)
    require('.symtab' in sections, 'Matching unstripped ELF required')
    (root / 'evidence/elf-sections.txt').write_text(sections)
    require(artifacts['build_id'].encode() in binary, 'Compiled build identity missing')
    self_file = root / 'build/probe/platform_diagnostic_eboot/eboot.bin'
    require(digest(self_file) == artifacts['eboot_sha256'], 'SELF SHA-256 mismatch')
    require(self_file.read_bytes()[:4] == b'O\x15=\x1d', 'Expected SELF magic')
    tool = str(root / 'build/pkgtool/PkgTool.Core')
    env = dict(os.environ, DOTNET_SYSTEM_GLOBALIZATION_INVARIANT='1')
    entries = subprocess.check_output([tool, 'pkg_listentries', str(package)], text=True, env=env)
    (root / 'evidence/package-entries.txt').write_text(entries)
    # Always extract afresh so a previous successful inspection cannot mask changes.
    with tempfile.TemporaryDirectory(prefix='inspection-', dir=root / 'evidence') as folder:
        extracted = Path(folder)
        with (root / 'evidence/package-extract.log').open('w') as log:
            subprocess.run([tool, 'pkg_extract', str(package), str(extracted)], check=True,
                           stdout=log, stderr=subprocess.STDOUT, env=env)
        payload = extracted / 'uroot'
        files = {path.relative_to(payload).as_posix(): digest(path)
                 for path in sorted(payload.rglob('*')) if path.is_file()}
        metadata = extracted / 'metadata'
        metadata.mkdir()
        for entry, filename in [('PARAM_SFO', 'param.sfo'), ('ICON0_PNG', 'icon0.png')]:
            row = next(line for line in entries.splitlines() if line.split() and line.split()[-1] == entry)
            subprocess.run([tool, 'pkg_extractentry', str(package), row.split()[3], str(metadata / filename)],
                           check=True, stdout=subprocess.DEVNULL, env=env)
            files['sce_sys/' + filename] = digest(metadata / filename)
        expected = {'eboot.bin', 'build-info.json', 'sce_sys/icon0.png', 'sce_sys/param.sfo',
                    'sce_sys/about/right.sprx', 'sce_module/libSceFios2.prx', 'sce_module/libc.prx', 'sce_sys/keystone'}
        require(set(files) == expected, 'Unexpected package payload: ' + str(set(files) ^ expected))
        require(files['eboot.bin'] == artifacts['eboot_sha256'], 'Packaged SELF mismatch')
        manifest = json.loads((payload / 'build-info.json').read_text())
        require(manifest == json.loads((root / 'evidence/build-info.json').read_text()), 'Packaged manifest mismatch')
        require(manifest['diagnostic_build_id'] == artifacts['build_id'], 'Packaged build identity mismatch')
        require(manifest['eboot_sha256'] == artifacts['eboot_sha256'], 'Manifest SELF mismatch')
        sfo = (metadata / 'param.sfo').read_bytes()
        require(sfo[:4] == b'\0PSF', 'Expected SFO magic')
        keys, values, count = struct.unpack_from('<III', sfo, 8)
        fields = {}
        for i in range(count):
            key_offset, kind, length, _, offset = struct.unpack_from('<HHIII', sfo, 20 + i * 16)
            key = sfo[keys + key_offset:].split(b'\0', 1)[0].decode()
            value = sfo[values + offset:values + offset + length]
            fields[key] = int.from_bytes(value, 'little') if kind == 0x0404 else value.rstrip(b'\0').decode()
        require(fields['TITLE_ID'] == 'PSWK00010' and fields['TITLE'] == 'PSWaker Platform Diagnostic'
                and fields['CATEGORY'] == 'gd' and fields['APP_VER'] == artifacts['app_version'], 'SFO identity mismatch')
    symbols = subprocess.check_output(['llvm-nm-21', '--undefined-only', str(elf)], text=True)
    (root / 'evidence/undefined-symbols.txt').write_text(symbols)
    atomics = [line for line in symbols.splitlines() if '__atomic_' in line]
    require(not atomics, 'Unresolved wider atomic references: ' + str(atomics))
    archives = sorted((root / 'build').rglob('*.a'))
    archives.extend(sorted((root / 'src/bzip2-1.0.6').glob('*.a')))
    emitted = subprocess.check_output(['llvm-nm-21', '--undefined-only', *map(str, archives)], text=True) if archives else ''
    (root / 'evidence/archive-undefined-symbols.txt').write_text(emitted)
    atomic_references = sorted(set(line.strip() for line in emitted.splitlines() if '__atomic_' in line))
    report = {'scope': 'Host inspection only; no hardware result', 'artifacts': artifacts,
              'package_files': files, 'sfo': fields, 'unresolved_wider_atomics': atomics,
              'emitted_archive_atomic_references': atomic_references}
    (root / 'evidence/inspection.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    try:
        inspect(args.root.resolve())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
