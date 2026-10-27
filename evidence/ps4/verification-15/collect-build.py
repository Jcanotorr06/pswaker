#!/usr/bin/env python3
"""Retain command audits and an inventory of a completed #15 build's full evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess


def file_record(path, base):
    with path.open('rb') as stream:
        checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'path': path.relative_to(base).as_posix(), 'bytes': path.stat().st_size,
            'sha256': checksum}


def collect(root, output):
    evidence = root / 'evidence'
    if 'COMPLETE host-build-only ' not in (evidence / 'clean-build.log').read_text():
        raise ValueError('Build did not complete: ' + str(root))
    audit = []
    for component in ['builtins', 'libunwind', 'zlib', 'libpng', 'libcxx',
                      'runtime-preflight', 'mesa', 'sdl3', 'dawn', 'probe']:
        commands = subprocess.check_output(['ninja', '-C', str(root / 'build' / component),
                                            '-t', 'commands'], text=True)
        (evidence / (component + '-commands.txt')).write_text(commands)
        compiled = [line for line in commands.splitlines() if ' -c ' in line and
                    re.search(r'(?:^|\s)\S*clang(?:\+\+)?-21(?:\s|$)', line)]
        assembly = [line for line in compiled if re.search(r'\.(?:S|s|asm)(?:\s|$)', line)]
        target = [line for line in compiled if line not in assembly]
        row = {'component': component, 'target_compile_commands': len(target),
               'without_btver2': sum('-march=btver2' not in line for line in target),
               'ps5_flag_commands': sum(bool(re.search(r'znver|PLATFORM_PS5', line)) for line in compiled),
               'assembly_commands': len(assembly),
               'assembly_without_btver2': sum('-march=btver2' not in line for line in assembly),
               'assembly_command_lines': assembly}
        if not target or row['without_btver2'] or row['ps5_flag_commands']:
            raise ValueError('Target command audit failed: ' + json.dumps(row))
        audit.append(row)
    (evidence / 'target-command-audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    assembly_objects = sorted(path for component in ['builtins', 'libunwind', 'mesa']
                              for path in (root / 'build' / component).rglob('*.S.o'))
    with (evidence / 'handwritten-assembly.txt').open('w') as log:
        for path in assembly_objects:
            subprocess.run(['llvm-objdump-21', '-d', str(path)], stdout=log, check=True)
    dispatch = root / 'src/mesa/src/util/blake3/blake3_dispatch.c'
    assembly_review = {'objects': [file_record(path, root) for path in assembly_objects],
                      'blake3_dispatch_source': file_record(dispatch, root),
                      'method': 'Disassembled all nine assembly objects. Five LLVM routines use '
                                'fixed x86-64/x87/SSE instructions without a march flag. Four Mesa '
                                'BLAKE3 SIMD variants carry btver2 but include explicit SSE/AVX2/AVX512 '
                                'assembly; the pinned dispatcher checks CPUID and XGETBV before '
                                'selecting a variant. No claim that march restricts handwritten ISA.'}
    (evidence / 'assembly-review.json').write_text(json.dumps(assembly_review, indent=2) + '\n')
    elf = root / 'build/probe/platform_diagnostic'
    for name, command in [('elf-header-program-headers.txt', ['llvm-readelf-21', '-h', '-l', str(elf)]),
                          ('elf-dynamic.txt', ['llvm-readelf-21', '-d', str(elf)])]:
        (evidence / name).write_text(subprocess.check_output(command, text=True))
    binaries = [elf, *sorted((root / 'out').glob('*.pkg')),
                root / 'build/probe/platform_diagnostic_eboot/eboot.bin',
                root / 'build/probe/platform_diagnostic_eboot/platform_diagnostic.oelf']
    records = [file_record(path, root) for path in sorted(evidence.rglob('*'))
               if path.is_file() and path.name != 'evidence-inventory.json']
    inventory = {'build_root': str(root), 'files': records,
                 'artifacts': [file_record(path, root) for path in binaries],
                 'limits': 'Full logs, command listings, source/dependency archives, SDK and binaries '
                           'remain at this local build root; the shared report contains selected evidence.'}
    (evidence / 'evidence-inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    output.mkdir(parents=True, exist_ok=True)
    for name in ['artifacts.json', 'build-info.json', 'clean-build.log', 'host-tools.txt',
                 'input-closure.json', 'inspection.json', 'license-audit.json', 'local-adaptations.json',
                 'source-archives.json', 'renderer-reconciliation.json', 'target-command-audit.json',
                 'verification-build.json', 'sdk-rebuilt-archives.sha256', 'evidence-inventory.json',
                 'assembly-review.json',
                 'patches-runtime.json', 'patches-graphics.json', 'patches-aurora.json',
                 'patches-packager.json', 'elf-header-program-headers.txt', 'elf-dynamic.txt']:
        shutil.copyfile(evidence / name, output / name)
    print('Recorded complete build and', sum(row['target_compile_commands'] for row in audit),
          'target compilation commands:', root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    collect(args.root.resolve(), args.output.resolve())
