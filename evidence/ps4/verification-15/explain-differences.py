#!/usr/bin/env python3
"""Bounded, retrospective ELF/input comparison for issue #15, not an equivalence proof.

Kept with evidence so this analysis does not change the diagnostic build identity.
Adapted from the historical diagnostic's evidence/explain-differences.py.
Run inspect-artifacts.py independently for each root before using this report.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sections(root):
    data = (root / 'build/probe/platform_diagnostic').read_bytes()
    if data[:6] != b'\x7fELF\x02\x01':
        raise ValueError('Expected little-endian ELF64')
    offset = struct.unpack_from('<Q', data, 40)[0]
    size, count, names_id = struct.unpack_from('<HHH', data, 58)
    headers = [struct.unpack_from('<IIQQQQIIQQ', data, offset + i * size) for i in range(count)]
    names = data[headers[names_id][4]:][:headers[names_id][5]]
    # SHT_NOBITS describes memory allocation, not bytes stored in the ELF.
    return {names[h[0]:].split(b'\0', 1)[0].decode(): {
        'address': h[3], 'size': h[5], 'type': h[1], 'flags': h[2],
        'data': b'' if h[1] == 8 else data[h[4]:][:h[5]]} for h in headers}


def compare(first, second, first_source, second_source):
    roots = [first.resolve(), second.resolve()]
    sources = [first_source.resolve(), second_source.resolve()]

    def normalize(data, index):
        return data.replace(str(sources[index]).encode(), b'<SOURCE>').replace(
            str(roots[index]).encode(), b'<BUILD>')

    manifests = [json.loads((root / 'evidence/build-info.json').read_text()) for root in roots]
    artifacts = [json.loads((root / 'evidence/artifacts.json').read_text()) for root in roots]
    result = {'scope': 'Recorded input and bounded binary comparison; no additional console runs',
              'roots': list(map(str, roots)), 'sources': list(map(str, sources)),
              'artifacts': artifacts, 'manifest_fields_equal': {}, 'closure_fields_equal': {}}
    for key in sorted(set(manifests[0]) | set(manifests[1])):
        if key not in {'input_closure', 'eboot_sha256'}:
            result['manifest_fields_equal'][key] = manifests[0].get(key) == manifests[1].get(key)
    closures = [manifest['input_closure'] for manifest in manifests]
    for key in sorted(set(closures[0]) | set(closures[1])):
        values = [normalize(json.dumps(closure.get(key), sort_keys=True).encode(), i)
                  for i, closure in enumerate(closures)]
        result['closure_fields_equal'][key] = values[0] == values[1]
    result['maintained_source_files_verified'] = []
    for source, closure in zip(sources, closures):
        checked = []
        for item in closure['maintained_inputs']:
            path = source / 'platform/ps4' / item['path']
            if digest(path.read_bytes()) != item['sha256']:
                raise ValueError('Source snapshot mismatch: ' + str(path))
            checked.append(item['path'])
        result['maintained_source_files_verified'].append(len(checked))
    result['artifact_hashes_verified'] = []
    for root, record in zip(roots, artifacts):
        paths = {record['package']['sha256']: root / 'out' / record['package']['filename'],
                 record['elf_sha256']: root / 'build/probe/platform_diagnostic',
                 record['eboot_sha256']: root / 'build/probe/platform_diagnostic_eboot/eboot.bin'}
        for expected, path in paths.items():
            if digest(path.read_bytes()) != expected:
                raise ValueError('Artifact hash mismatch: ' + str(path))
        result['artifact_hashes_verified'].append(True)

    maps = [sections(root) for root in roots]
    result['sections'] = {}
    for name in sorted(set(maps[0]) | set(maps[1])):
        entries = [mapping.get(name) for mapping in maps]
        if any(entry is None for entry in entries):
            result['sections'][name] = {'missing_from_one_elf': True}
            continue
        a, b = [entry['data'] for entry in entries]
        normalized = [normalize(entry['data'], i) for i, entry in enumerate(entries)]
        result['sections'][name] = {
            'addresses': [entry['address'] for entry in entries],
            'sizes': [entry['size'] for entry in entries],
            'types': [entry['type'] for entry in entries],
            'flags': [entry['flags'] for entry in entries],
            'sha256': [digest(data) for data in (a, b)],
            'bytes_equal': a == b, 'path_normalized_bytes_equal': normalized[0] == normalized[1],
            'differing_bytes_at_same_offset_including_unmatched_tail':
                sum(x != y for x, y in zip(a, b)) + abs(len(a) - len(b))}

    def target(index, address):
        entry = maps[index]['.rodata']
        offset = address - entry['address']
        if not 0 <= offset < len(entry['data']):
            return None
        end = entry['data'].find(b'\0', offset)
        if end < 0:
            return None
        return normalize(entry['data'][offset:end], index)

    def relative_table_prefix(addresses):
        entries = [mapping['.rodata'] for mapping in maps]
        if addresses[1] - addresses[0] != entries[1]['size'] - entries[0]['size']:
            return False
        data = []
        for address, entry in zip(addresses, entries):
            offset = address - entry['address']
            if not 0 <= offset <= len(entry['data']) - 32:
                return False
            data.append(entry['data'][offset:offset + 32])
        changed = 0
        for offset in range(0, 32, 4):
            values = [struct.unpack_from('<i', block, offset)[0] for block in data]
            if values[0] == values[1]:
                continue
            destinations = [address + value for address, value in zip(addresses, values)]
            if destinations[0] != destinations[1] or not all(
                mapping['.text']['address'] <= destination <
                mapping['.text']['address'] + mapping['.text']['size']
                for mapping, destination in zip(maps, destinations)):
                return False
            changed += 1
        return bool(changed)

    instructions = []
    for root in roots:
        output = subprocess.check_output(['llvm-objdump-21', '-d', '--no-show-raw-insn',
                                          str(root / 'build/probe/platform_diagnostic')], text=True)
        instructions.append(dict(re.findall(r'^\s*([0-9a-f]+):\s+(.*)$', output, re.M)))
    counts = Counter()
    other_examples = []
    unchecked_examples = []
    ordered_addresses = sorted(set(instructions[0]) | set(instructions[1]), key=lambda x: int(x, 16))
    for position, address in enumerate(ordered_addresses):
        lines = [listing.get(address) for listing in instructions]
        if lines[0] == lines[1]:
            counts['identical'] += 1
            continue
        if any(line is None for line in lines):
            counts['missing_from_one_disassembly'] += 1
        else:
            matches = [re.search(r'(-?(?:0x)?[0-9a-f]+)\(%rip\)', line) for line in lines]
            if all(matches):
                # LLVM annotates vector broadcasts with lane contents rather than
                # an address. RIP is the next instruction address for those too.
                comments = [re.search(r'#\s*(?:0x)?([0-9a-f]+)(?:\s|$)', line) for line in lines]
                if not all(comments) and position + 1 == len(ordered_addresses):
                    counts['other_differing_instructions'] += 1
                    other_examples.append({'address': address, 'first': lines[0], 'second': lines[1]})
                    continue
                addresses = [int(comment[1], 16) if comment else
                             int(ordered_addresses[position + 1], 16) + int(match[1], 16)
                             for comment, match in zip(comments, matches)]
                targets = [target(i, value) for i, value in enumerate(addresses)]
                forms = [re.sub(r'-?(?:0x)?[0-9a-f]+\(%rip\)', 'TARGET(%rip)',
                                line.split('#')[0]).strip() for line in lines]
                if forms[0] == forms[1] and forms[0].startswith('vbroadcasti128'):
                    blocks = []
                    for mapping, value in zip(maps, addresses):
                        entry = mapping['.rodata']
                        offset = value - entry['address']
                        blocks.append(entry['data'][offset:offset + 16]
                                      if 0 <= offset <= len(entry['data']) - 16 else None)
                    if blocks[0] is not None and blocks[0] == blocks[1]:
                        counts['same_instruction_equal_16_byte_broadcast_constant'] += 1
                        continue
                if targets[0] is not None and targets[0] == targets[1] and forms[0] == forms[1]:
                    ascii_string = bool(targets[0]) and all(
                        c in (9, 10, 13) or 32 <= c < 127 for c in targets[0])
                    counts['same_instruction_equal_ASCII_string_target' if ascii_string else
                           'same_instruction_equal_empty_or_binary_NUL_prefix'] += 1
                    continue
                if forms[0] == forms[1] and relative_table_prefix(addresses):
                    counts['same_instruction_equal_first_8_relative_table_words'] += 1
                    continue
                rodata = [mapping['.rodata'] for mapping in maps]
                if (forms[0] == forms[1] and
                    addresses[1] - addresses[0] == rodata[1]['size'] - rodata[0]['size'] and
                    all(entry['address'] <= address < entry['address'] + entry['size']
                        for address, entry in zip(addresses, rodata))):
                    counts['same_instruction_rodata_layout_shift_TARGET_DATA_UNCHECKED'] += 1
                    if len(unchecked_examples) < 20:
                        unchecked_examples.append({'address': address, 'first': lines[0],
                                                   'second': lines[1], 'target_data_unchecked': True})
                    continue
                if forms[0] == forms[1] and any(
                    all(value == mapping[name]['address'] for value, mapping in zip(addresses, maps))
                    for name in ('.eh_frame', '.eh_frame_hdr', '.gcc_except_table')):
                    counts['same_instruction_relocated_unwind_section_base'] += 1
                    continue
            counts['other_differing_instructions'] += 1
        if len(other_examples) < 20:
            other_examples.append({'address': address, 'first': lines[0], 'second': lines[1]})
    result['instructions'] = {'counts': dict(counts), 'other_examples': other_examples,
        'unchecked_examples': unchecked_examples,
        'limit': 'Address-aligned disassembly, complete NUL-terminated targets, and the first '
                 'eight 32-bit table words (unchanged values or equal code destinations after '
                 'the observed rodata-size shift). Not full table, arbitrary constant, '
                 'control-flow or semantic equivalence. TARGET_DATA_UNCHECKED records only '
                 'an equal instruction shape and corresponding rodata layout shift, not data equality.'}

    relocations = [list(struct.iter_unpack('<QQq', mapping['.rela.dyn']['data'])) for mapping in maps]
    relocation_counts = Counter()
    examples = []
    for left, right in zip(*relocations):
        if left == right:
            relocation_counts['identical'] += 1
        elif (left[:2] == right[:2] and (left[1] & 0xffffffff) == 8
              and target(0, left[2]) is not None and target(0, left[2]) == target(1, right[2])):
            relocation_counts['R_X86_64_RELATIVE_equal_NUL_terminated_rodata_target'] += 1
        elif (left[:2] == right[:2] and (left[1] & 0xffffffff) == 8
              and all(record[2] == mapping['.eh_frame']['address']
                      for record, mapping in zip((left, right), maps))
              and maps[0]['.eh_frame']['data'][:24] == maps[1]['.eh_frame']['data'][:24]):
            relocation_counts['R_X86_64_RELATIVE_relocated_eh_frame_base_equal_first_CIE'] += 1
        else:
            relocation_counts['other_differing_records'] += 1
            if len(examples) < 10:
                examples.append([left, right])
    result['relocations'] = {'counts': dict(relocation_counts),
        'unmatched_records': abs(len(relocations[0]) - len(relocations[1])), 'other_examples': examples}
    strings = [Counter(normalize(mapping['.rodata']['data'], i).split(b'\0'))
               for i, mapping in enumerate(maps)]
    result['rodata_NUL_split_multisets_equal'] = strings[0] == strings[1]
    result['rodata_NUL_split_difference_examples'] = [
        [repr(value)[:240] for value in (strings[i] - strings[1 - i])][:10] for i in (0, 1)]
    ascii_strings = [Counter({value: count for value, count in items.items()
                             if value and all(c in (9, 10, 13) or 32 <= c < 127 for c in value)})
                     for items in strings]
    result['rodata_ASCII_NUL_terminated_multisets_equal'] = ascii_strings[0] == ascii_strings[1]
    result['rodata_ASCII_difference_examples'] = [
        [repr(value)[:240] for value in (ascii_strings[i] - ascii_strings[1 - i])][:10]
        for i in (0, 1)]
    result['limits'] = ('All differing/missing instructions, section lengths and unmatched relocations '
                        'are reported. NUL splitting includes binary tables and does not explain '
                        'all rodata bytes. SELF/package payloads and timestamps need separate inspection. '
                        'Only the owner-confirmed installed candidate has hardware results.')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('first', type=Path)
    parser.add_argument('second', type=Path)
    parser.add_argument('--first-source', type=Path, required=True)
    parser.add_argument('--second-source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = compare(args.first, args.second, args.first_source, args.second_source)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ('manifest_fields_equal', 'closure_fields_equal',
                                                 'instructions', 'relocations')}, indent=2))
