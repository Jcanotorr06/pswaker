#!/usr/bin/env python3
"""Compare repeated ELF sections and package payloads; no equivalence claim."""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def sections(path):
    data = path.read_bytes()
    if data[:6] != b'\x7fELF\x02\x01':
        raise ValueError('Expected little-endian ELF64')
    offset = struct.unpack_from('<Q', data, 40)[0]
    size, count, names_id = struct.unpack_from('<HHH', data, 58)
    headers = [struct.unpack_from('<IIQQQQIIQQ', data, offset + i * size) for i in range(count)]
    names = data[headers[names_id][4]:][:headers[names_id][5]]
    return {names[h[0]:].split(b'\0', 1)[0].decode(): {
        'address': h[3], 'bytes': h[5], 'type': h[1], 'flags': h[2],
        'data': b'' if h[1] == 8 else data[h[4]:][:h[5]]} for h in headers}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('private_build_review', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    folder = args.private_build_review
    records = [json.loads((folder / ('build-' + label + '.json')).read_text()) for label in ['a', 'b']]
    elves = [sections(Path(r['build_root']) / 'build/switchwaker') for r in records]
    if elves[0].keys() != elves[1].keys():
        raise ValueError('ELF section sets differ; inspect manually')

    def normalize(data, index):
        record = records[index]
        return data.replace(record['source_root'].encode(), b'<SOURCE>').replace(
            record['build_root'].encode(), b'<BUILD>')

    rows = []
    for name in elves[0]:
        first, second = elves[0][name], elves[1][name]
        row = {'section': name, 'bytes_a': first['bytes'], 'bytes_b': second['bytes'],
               'layout_equal': {k: v for k, v in first.items() if k != 'data'} ==
                               {k: v for k, v in second.items() if k != 'data'},
               'raw_equal': first['data'] == second['data'],
               'path_normalized_equal': normalize(first['data'], 0) == normalize(second['data'], 1),
               'sha256_a': hashlib.sha256(first['data']).hexdigest(),
               'sha256_b': hashlib.sha256(second['data']).hexdigest()}
        rows.append(row)
    inspections = [json.loads((folder / ('package-' + label) / 'inspection.json').read_text())
                   for label in ['a', 'b']]
    payloads = [r['payload_sha256'] for r in inspections]
    result = {'scope': 'Bounded A/B ELF section and payload comparison, not semantic equivalence or console evidence',
              'compiled_build_id': records[0]['compiled_build_id'], 'sections': rows,
              'all_section_layouts_equal': all(r['layout_equal'] for r in rows),
              'all_section_bytes_equal_after_path_normalization': all(r['path_normalized_equal'] for r in rows),
              'payload_differences': [name for name in sorted(set(payloads[0]) | set(payloads[1]))
                                      if payloads[0].get(name) != payloads[1].get(name)],
              'candidate_hashes_replaced': False, 'console_runs_created': 0}
    args.output.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
