"""Generate a tiny raw image and a synthetic contract; contains no Nintendo data.

Tests copy the CLI into an isolated directory and replace only that copy's contract.
The production CLI never accepts alternate contracts or test-mode flags.
"""
import hashlib
import json
from pathlib import Path
import shutil
import struct


def literal_yaz0(data):
    return b'Yaz0' + struct.pack('>I', len(data)) + bytes(8) + b''.join(
        b'\xff' + data[i:i + 8] for i in range(0, len(data), 8))


def generate(root, repository):
    import sys
    sys.path.insert(0, str(repository / 'tools/pswaker'))
    import build_inputs
    for name, path in build_inputs.maintained_inputs(repository).items():
        target = root / 'repo' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    locations = build_inputs.Locations(root / 'repo')

    # A small DOL with one synthetic section.
    dol = bytearray(0x120)
    struct.pack_into('>I', dol, 0, 0x100)
    struct.pack_into('>I', dol, 0x48, 0x80003100)
    struct.pack_into('>I', dol, 0x90, 0x20)
    dol[0x100:] = b'Synthetic DOL section'.ljust(0x20, b'!')

    first, second, direct = b'ABABAB', b'Synthetic second REL', b'Synthetic direct REL'
    # Two literals followed by a length-4, distance-2 overlapping back reference.
    first_compressed = b'Yaz0' + struct.pack('>I', 6) + bytes(8) + b'\xc0AB\x20\x01'
    strings = b'rels\0mmem\0first.rel\0second.rel\0'
    arc = bytearray(0x100)
    struct.pack_into('>4sIII', arc, 0, b'RARC', 0x100 + len(first_compressed) + len(second), 0x20, 0xE0)
    struct.pack_into('>6I', arc, 0x20, 2, 0x20, 3, 0x40, len(strings), 0x80)
    struct.pack_into('>4sIHHI', arc, 0x40, b'ROOT', 0, 0, 1, 0)
    struct.pack_into('>4sIHHI', arc, 0x50, b'MMEM', 5, 0, 2, 1)
    for index, (flags, name, offset, size) in enumerate([
            (2, 5, 1, 0), (0x11, 10, 0, len(first_compressed)),
            (0x11, 20, len(first_compressed), len(second))]):
        struct.pack_into('>HHIIII', arc, 0x60 + index * 20, index, 0,
                         flags << 24 | name, offset, size, 0)
    arc[0xA0:0xA0 + len(strings)] = strings
    arc += first_compressed + second
    archive = literal_yaz0(arc)
    rel = literal_yaz0(direct)

    fst = bytearray(4 * 12)
    struct.pack_into('>III', fst, 0, 0x01000000, 0, 4)
    struct.pack_into('>III', fst, 12, 0x01000000, 0, 3)
    struct.pack_into('>III', fst, 24, 5, 0x3000, len(rel))
    struct.pack_into('>III', fst, 36, 16, 0x4000, len(archive))
    fst += b'rels\0direct.rel\0RELS.arc\0'
    image = bytearray(0x8000)
    image[:8] = b'GZLE01\0\0'
    image[0x1C:0x20] = b'\xc2\x33\x9f\x3d'
    struct.pack_into('>IIII', image, 0x420, 0x1000, 0x2000, len(fst), len(fst))
    image[0x1000:0x1000 + len(dol)] = dol
    image[0x2000:0x2000 + len(fst)] = fst
    image[0x3000:0x3000 + len(rel)] = rel
    image[0x4000:0x4000 + len(archive)] = archive
    path = root / 'synthetic.iso'
    path.write_bytes(image)
    contract = {'schema': 1, 'game_id': 'GZLE01', 'disc_number': 0, 'revision': 0,
                'image_size': len(image), 'image_sha1': hashlib.sha1(image).hexdigest(),
                'required_content': [
                    {'path': 'sys/main.dol', 'member': '', 'sha1': hashlib.sha1(dol).hexdigest()},
                    {'path': 'RELS.arc', 'member': 'rels/mmem/first.rel', 'sha1': hashlib.sha1(first).hexdigest()},
                    {'path': 'RELS.arc', 'member': 'rels/mmem/second.rel', 'sha1': hashlib.sha1(second).hexdigest()},
                    {'path': 'rels/direct.rel', 'member': '', 'sha1': hashlib.sha1(direct).hexdigest()}]}
    (locations.platform / 'content-contract.json').write_text(json.dumps(contract))
    return locations.command('complete-package.py'), path
