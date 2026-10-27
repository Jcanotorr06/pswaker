#!/usr/bin/env python3
"""Review pooled ELF data/debug strings and symbols without asserting equivalence."""
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import struct


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('private_build_review', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('comparison', Path(__file__).with_name('compare-builds.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    records = [json.loads((args.private_build_review / ('build-' + label + '.json')).read_text())
               for label in ['a', 'b']]
    maps = [module.sections(Path(r['build_root']) / 'build/switchwaker') for r in records]

    result = {'scope': 'String multiset and symbol-target comparison; ordering/offsets and unexamined DWARF records are not semantic-equivalence proof',
              'string_multisets': {}}
    for name in ['.rodata', '.debug_str']:
        counters = [Counter(module.normalize_paths(m[name]['data'], records[i]).split(b'\0'))
                    for i, m in enumerate(maps)]
        excess = [counters[i] - counters[1-i] for i in [0, 1]]
        result['string_multisets'][name] = {
            'normalized_all_NUL_segment_multisets_equal': counters[0] == counters[1],
            'excess_segment_counts': [sum(c.values()) for c in excess],
            'excess_printable_strings': [[{'string': k.decode('ascii'), 'count': v} for k, v in c.items()
                                          if k and all(32 <= x < 127 for x in k)] for c in excess],
            'excess_nonprintable_segment_counts': [sum(v for k, v in c.items()
                                                      if not k or not all(32 <= x < 127 for x in k)) for c in excess]}
    symbols = []
    for m in maps:
        names = m['.strtab']['data']
        rows = []
        for name, info, other, section, value, size in struct.iter_unpack('<IBBHQQ', m['.symtab']['data']):
            end = names.find(b'\0', name)
            rows.append((names[name:end].decode(), info, other, section, value, size))
        symbols.append(rows)
    changed = []
    if len(symbols[0]) != len(symbols[1]):
        raise ValueError('Symbol counts differ')
    for a, b in zip(*symbols):
        if a == b:
            continue
        targets = []
        for m, row in zip(maps, [a, b]):
            offset = row[4] - m['.rodata']['address']
            targets.append(m['.rodata']['data'][offset:offset + row[5]]
                           if 0 <= offset <= m['.rodata']['bytes'] - row[5] else None)
        changed.append({'symbol': a[0], 'same_except_value': a[:4] == b[:4] and a[5] == b[5],
                        'value_a': a[4], 'value_b': b[4], 'declared_bytes': a[5],
                        'declared_extent_target_bytes_equal': targets[0] is not None and targets[0] == targets[1]})
    result['changed_symbols'] = changed
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
