#!/usr/bin/env python3
"""Inspect the observed #15 unwind/layout shift, retaining decoded frame records."""
import argparse
from collections import Counter
import json
from pathlib import Path
import runpy
import struct
import subprocess


def inspect(roots):
    sections = runpy.run_path(str(Path(__file__).with_name('explain-differences.py')))['sections']
    maps = [sections(root) for root in roots]
    result = {'scope': 'Supplemental decoded unwind/header and relative exception-table inspection; '
                       'not semantic equivalence', 'roots': list(map(str, roots))}
    result['embedded_build_paths'] = [
        {'occurrences': mapping['.rodata']['data'].count(str(root).encode()),
         'rodata_size': len(mapping['.rodata']['data']),
         'root_normalized_size': len(mapping['.rodata']['data'].replace(str(root).encode(), b'<BUILD>'))}
        for root, mapping in zip(roots, maps)]
    texts = []
    for root in roots:
        path = root / 'evidence/decoded-eh-frame.txt'
        with path.open('w') as log:
            subprocess.run(['llvm-dwarfdump-21', '--eh-frame',
                            str(root / 'build/probe/platform_diagnostic')], stdout=log, check=True)
        texts.append(path.read_text().replace(str(root), '<BUILD>'))
    result['decoded_unwind_A_B_equal'] = texts[1] == texts[2]
    left, right = [text.splitlines() for text in texts[:2]]
    result['decoded_unwind_line_counts'] = [len(left), len(right)]
    lsda, augmentation, other = [], [], []
    for a, b in zip(left, right):
        if a == b:
            continue
        if a.startswith('  LSDA Address: ') and b.startswith('  LSDA Address: '):
            lsda.append(int(b.split()[-1], 16) - int(a.split()[-1], 16))
        elif a.startswith('  Augmentation data: ') and b.startswith('  Augmentation data: '):
            augmentation.append([a, b])
        else:
            other.append([a, b])
    result['decoded_unwind_differences'] = {'LSDA_address_deltas': dict(Counter(lsda)),
        'augmentation': augmentation, 'other': other,
        'unmatched_lines': abs(len(left) - len(right))}
    result['augmentation_personality_pointer'] = []
    for left, right in augmentation:
        a, b = [bytes.fromhex(line.split(':', 1)[1]) for line in (left, right)]
        if len(a) == len(b) == 7 and a[0] == b[0] == 0x9b and a[5:] == b[5:]:
            delta = struct.unpack_from('<i', b, 1)[0] - struct.unpack_from('<i', a, 1)[0]
            result['augmentation_personality_pointer'].append({
                'encoded_PC_relative_delta': delta,
                'unchanged_absolute_target_after_section_shift':
                    delta + maps[1]['.eh_frame']['address'] - maps[0]['.eh_frame']['address'] == 0})
    headers = []
    for mapping in maps:
        header = mapping['.eh_frame_hdr']
        data = header['data']
        if data[:4] != bytes([1, 0x1b, 3, 0x3b]):
            raise ValueError('Unexpected unwind header encoding')
        pointer = header['address'] + 4 + struct.unpack_from('<i', data, 4)[0]
        count = struct.unpack_from('<I', data, 8)[0]
        if len(data) != 12 + count * 8 or pointer != mapping['.eh_frame']['address']:
            raise ValueError('Unwind header count/pointer mismatch')
        headers.append([(header['address'] + pc,
                         header['address'] + fde - mapping['.eh_frame']['address'])
                        for pc, fde in struct.iter_unpack('<ii', data[12:])])
    result['unwind_header_FDE_counts'] = list(map(len, headers))
    result['unwind_header_same_code_PC_and_frame_offsets'] = headers[0] == headers[1] == headers[2]
    a, b = [mapping['.gcc_except_table'] for mapping in maps[:2]]
    deltas = Counter()
    destinations_equal = True
    for offset in range(0, min(len(a['data']), len(b['data'])) - 3, 4):
        x, y = [struct.unpack_from('<i', entry['data'], offset)[0] for entry in (a, b)]
        if x != y:
            deltas[y - x] += 1
            destinations_equal &= a['address'] + offset + x == b['address'] + offset + y
    result['exception_table_sizes'] = [len(entry['data']) for entry in (a, b)]
    result['exception_table_differing_32bit_word_deltas'] = dict(deltas)
    result['exception_table_changed_words_same_PC_relative_destination'] = destinations_equal
    symbols = [list(struct.iter_unpack('<IBBHQQ', mapping['.symtab']['data'])) for mapping in maps]
    result['symbol_counts'] = list(map(len, symbols))
    result['symbol_metadata_equal'] = all(
        x[:4] == y[:4] == z[:4] and x[5] == y[5] == z[5] for x, y, z in zip(*symbols))
    result['function_symbol_addresses_equal'] = all(
        x[4] == y[4] == z[4] for x, y, z in zip(*symbols) if (x[1] & 15) == 2)
    result['symbol_address_delta_counts_candidate_A'] = dict(Counter(
        y[4] - x[4] for x, y in zip(*symbols[:2]) if x[4] != y[4]))
    result['limits'] = ('Complete decoded frame records and observed 32-bit exception-table '
                        'differences support the layout explanation. No universal ABI, exception '
                        'or runtime equivalence claim; rodata contents need the separate comparison.')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('first', type=Path)
    parser.add_argument('second', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = inspect([root.resolve() for root in (args.candidate, args.first, args.second)])
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
