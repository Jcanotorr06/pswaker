#!/usr/bin/env python3
"""Bounded analysis of repeated-build instructions and dynamic relocations."""
import argparse
from bisect import bisect_left
from collections import Counter
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('private_build_review', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('comparison', Path(__file__).with_name('compare-builds.py'))
    comparison = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(comparison)
    records = [json.loads((args.private_build_review / ('build-' + label + '.json')).read_text())
               for label in ['a', 'b']]
    paths = [Path(r['build_root']) / 'build/switchwaker' for r in records]
    maps = [comparison.sections(path) for path in paths]
    text = [m['.text'] for m in maps]
    if text[0]['address'] != text[1]['address'] or text[0]['bytes'] != text[1]['bytes']:
        raise ValueError('Text layouts differ; this bounded analysis does not apply')
    differences = [text[0]['address'] + i for i, (a, b) in enumerate(zip(text[0]['data'], text[1]['data'])) if a != b]

    def instructions(path):
        result = {}
        previous = None
        process = subprocess.Popen(['llvm-objdump-21', '-d', '--section=.text', '--no-show-raw-insn', str(path)],
                                   stdout=subprocess.PIPE, text=True)
        def retain(entry, end):
            address, line = entry
            index = bisect_left(differences, address)
            if index < len(differences) and differences[index] < end:
                result[address] = (line, end)
        for line in process.stdout:
            match = re.match(r'^\s*([0-9a-f]+):\s+(.*)$', line)
            if not match:
                continue
            current = (int(match[1], 16), match[2])
            if previous:
                retain(previous, current[0])
            previous = current
        if previous:
            retain(previous, text[0]['address'] + text[0]['bytes'])
        if process.wait():
            raise ValueError('Disassembly failed')
        return result

    listings = [instructions(path) for path in paths]

    def target(index, address):
        section = maps[index]['.rodata']
        offset = address - section['address']
        if not 0 <= offset < len(section['data']):
            return None
        end = section['data'].find(b'\0', offset)
        if end < 0:
            return None
        return comparison.normalize_paths(section['data'][offset:end], records[index])

    counts, unknown, timestamps = Counter(), [], []
    for address in sorted(listings[0].keys() | listings[1].keys()):
        entries = [listing.get(address) for listing in listings]
        if all(entries):
            forms = [re.sub(r'-?(?:0x)?[0-9a-f]+\(%rip\)', 'TARGET(%rip)', entry[0].split('#')[0]).strip()
                     for entry in entries]
            operands = [re.search(r'(-?(?:0x)?[0-9a-f]+)\(%rip\)', entry[0]) for entry in entries]
            if all(operands) and forms[0] == forms[1]:
                addresses = [entry[1] + int(operand[1], 16) for entry, operand in zip(entries, operands)]
                values = [target(i, value) for i, value in enumerate(addresses)]
                if values[0] is not None and values[0] == values[1]:
                    printable = bool(values[0]) and all(c in (9, 10, 13) or 32 <= c < 127 for c in values[0])
                    counts['same_instruction_equal_normalized_ASCII_target' if printable else
                           'same_instruction_equal_NUL_prefix_only_TARGET_EXTENT_UNCHECKED'] += 1
                    continue
                if all(value and re.fullmatch(rb'\d\d:\d\d:\d\d', value) for value in values):
                    locations = [subprocess.check_output(['llvm-addr2line-21', '-f', '-e', str(path), hex(address)],
                                                         text=True).splitlines() for path in paths]
                    sources = [Path(location[1].rsplit(':', 1)[0]) for location in locations]
                    if all(location[0] == 'CARDInit' and '__TIME__' in source.read_text()
                           for location, source in zip(locations, sources)):
                        counts['same_CARDInit_instruction_distinct_compile_time_log_string'] += 1
                        timestamps.append({'address': hex(address), 'values': [v.decode() for v in values],
                                           'source': 'src/aurora/lib/dolphin/card.cpp:299 (__DATE__/__TIME__)'})
                        continue
        counts['unexplained'] += 1
        if len(unknown) < 20:
            unknown.append({'address': hex(address), 'a': entries[0], 'b': entries[1]})

    relocations = [m['.rela.dyn']['data'] for m in maps]
    relocation_counts, relocation_unknown = Counter(), []
    if len(relocations[0]) != len(relocations[1]):
        raise ValueError('Relocation sizes differ')
    for offset in range(0, len(relocations[0]), 24):
        a, b = [struct.unpack_from('<QQq', data, offset) for data in relocations]
        if a == b:
            relocation_counts['identical'] += 1
            continue
        values = [target(i, row[2]) for i, row in enumerate([a, b])]
        if a[:2] == b[:2] and values[0] is not None and values[0] == values[1]:
            printable = bool(values[0]) and all(32 <= c < 127 for c in values[0])
            relocation_counts['same_location_and_type_equal_normalized_ASCII_addend_target' if printable else
                              'same_location_and_type_equal_NUL_prefix_only_TARGET_EXTENT_UNCHECKED'] += 1
        else:
            relocation_counts['unexplained'] += 1
            if len(relocation_unknown) < 20:
                relocation_unknown.append({'a': a, 'b': b})
    result = {'scope': 'Explains differing operands/relocations with normalized string targets; no formal semantic equivalence or console evidence',
              'text_differing_bytes': len(differences), 'text_instruction_counts': dict(counts),
              'compile_timestamp_references': timestamps,
              'unexplained_instruction_examples': unknown,
              'relocation_counts': dict(relocation_counts), 'unexplained_relocation_examples': relocation_unknown}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
