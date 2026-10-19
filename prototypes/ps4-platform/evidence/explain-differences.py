#!/usr/bin/env python3
"""Locate remaining clean-build byte differences for human review."""
import bisect
from collections import Counter
import json
from pathlib import Path
import re
import struct
import subprocess

roots = [Path('/tmp/pswaker-clean-a'), Path('/tmp/pswaker-clean-b')]

def sections(root):
    data = (root / 'build/probe/platform_diagnostic').read_bytes()
    shoff = struct.unpack_from('<Q', data, 40)[0]
    size, count, names_id = struct.unpack_from('<HHH', data, 58)
    headers = [struct.unpack_from('<IIQQQQIIQQ', data, shoff+i*size) for i in range(count)]
    names = data[headers[names_id][4]:][:headers[names_id][5]]
    return {names[h[0]:].split(b'\0', 1)[0].decode(): (h[3], data[h[4]:][:h[5]]) for h in headers}

a, b = [sections(root) for root in roots]
symbols = subprocess.check_output(['llvm-nm-21', '-n', '-C', str(roots[0] / 'build/probe/platform_diagnostic')], text=True, stderr=subprocess.DEVNULL)
symbols = [(int(row.split()[0], 16), ' '.join(row.split()[2:])) for row in symbols.splitlines() if len(row.split()) >= 3 and row.split()[1] in ('t', 'T')]
addresses = [item[0] for item in symbols]
result = {}
for name in ('.rodata', '.text', '.rela.dyn'):
    left = a[name][1].replace(str(roots[0]).encode(), b'/tmp/pswaker-clean-x')
    right = b[name][1].replace(str(roots[1]).encode(), b'/tmp/pswaker-clean-x')
    offsets = [i for i, (x, y) in enumerate(zip(left, right)) if x != y]
    groups = []
    for offset in offsets:
        if not groups or offset > groups[-1][-1] + 8:
            groups.append([offset])
        else:
            groups[-1].append(offset)
    records = []
    for group in groups[:8]:
        start, end = group[0], group[-1] + 1
        symbol = symbols[bisect.bisect_right(addresses, a[name][0]+start)-1] if name == '.text' else None
        records.append({'offset': hex(start), 'end': hex(end), 'symbol': symbol,
                        'first_context': repr(left[max(0,start-40):start+120]),
                        'second_context': repr(right[max(0,start-40):start+120])})
    result[name] = {'differing_bytes': len(offsets), 'groups': len(groups), 'examples': records}
def normalize_target(section_map, address, root):
    base, data = section_map['.rodata']
    offset = address - base
    if 0 <= offset < len(data):
        # Keep enough bytes to compare a whole ordinary string; cap binary constants.
        return data[offset:offset+8192].split(b'\0', 1)[0].replace(str(root).encode(), b'/tmp/pswaker-clean-x')
    return None

disassemblies = [subprocess.check_output(['llvm-objdump-21', '-d', '--no-show-raw-insn', str(root / 'build/probe/platform_diagnostic')], text=True, stderr=subprocess.DEVNULL).splitlines() for root in roots]
unexplained = []
equal_other_constant = 0
explained = 0
instructions = [dict(re.findall(r'^\s*([0-9a-f]+):\s+(.*)$', '\n'.join(lines), re.M)) for lines in disassemblies]
for address, left in instructions[0].items():
    right = instructions[1].get(address)
    if left == right:
        continue
    matches = [re.search(r'(?:0x)?([0-9a-f]+)\(%rip\)(.*)#\s*(?:0x)?([0-9a-f]+)', line or '') for line in (left,right)]
    if all(matches):
        targets = [normalize_target(s, int(m[3],16), root) for s,m,root in zip((a,b),matches,roots)]
        forms = [re.sub(r'(?:0x)?[0-9a-f]+\(%rip\)', 'CONSTANT(%rip)', line.split('#')[0]).strip() for line in (left,right)]
        if targets[0] and all(c in (9,10,13) or 32 <= c < 127 for c in targets[0]) and targets[0] == targets[1] and forms[0] == forms[1]:
            explained += 1
            continue
        if targets[0] is not None and targets[0] == targets[1] and forms[0] == forms[1]:
            equal_other_constant += 1
            continue
    unexplained.append({'address':address,'first':left,'second':right})
result['instruction_comparison'] = {'differing_instructions_referencing_equal_nonempty_ASCII_string':explained,'differing_instructions_referencing_equal_empty_or_non_ASCII_nul_terminated_bytes':equal_other_constant,'other_differing_instructions_count':len(unexplained),'examples':unexplained[:20],'limit':'NUL-terminated target comparisons are not a proof that arbitrary binary constants or all runtime behavior are equivalent.'}
relocations = [list(struct.iter_unpack('<QQq', s['.rela.dyn'][1])) for s in (a,b)]
relocation_differences = [(left,right) for left,right in zip(*relocations) if left != right]
relocation_unexplained = [(left,right) for left,right in relocation_differences if left[:2] != right[:2] or normalize_target(a,left[2],roots[0]) is None or normalize_target(a,left[2],roots[0]) != normalize_target(b,right[2],roots[1])]
result['relocation_comparison'] = {'differing_records':len(relocation_differences),'other_than_equal_nul_terminated_rodata_targets':len(relocation_unexplained),'examples':relocation_unexplained[:10]}
strings = [Counter(s['.rodata'][1].replace(str(root).encode(),b'/tmp/pswaker-clean-x').split(b'\0')) for s,root in zip((a,b),roots)]
result['rodata_nul_split_multisets_equal'] = strings[0] == strings[1]
result['rodata_nul_split_difference_examples'] = [[repr(value)[:300] for value in (strings[i]-strings[1-i]).keys()][:15] for i in (0,1)]
output = Path('/tmp/pswaker-difference-analysis.json')
output.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({key:value for key,value in result.items() if key in ('instruction_comparison','relocation_comparison','rodata_nul_split_multisets_equal')}, indent=2))
