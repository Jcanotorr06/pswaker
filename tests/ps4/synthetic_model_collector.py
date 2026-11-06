"""Synthetic disc resource and external collector process for command tests.

The process stands in for the native executable at its system boundary. It
does not claim to load J3D; actual J3D runs are retained privately.
"""
import hashlib
import json
import struct

from synthetic_pipeline import make_seed, make_model_collection, make_dynamic_collection


MODEL_BYTES = b'Synthetic model resource; no game content'
PARTICLE_BYTES = b'Synthetic particle resource; no game content'


def add_model_resource(image, contract_path):
    strings = b'root\0bdl\0obm_kotubo1.bdl\0'
    archive = bytearray(0x100)
    struct.pack_into('>4sIII', archive, 0, b'RARC', 0x100 + len(MODEL_BYTES), 0x20, 0xE0)
    struct.pack_into('>6I', archive, 0x20, 2, 0x20, 2, 0x40, len(strings), 0x80)
    struct.pack_into('>4sIHHI', archive, 0x40, b'ROOT', 0, 0, 1, 0)
    struct.pack_into('>4sIHHI', archive, 0x50, b'BDL ', 5, 0, 1, 1)
    for index, (flags, name, offset, size) in enumerate([
            (2, 5, 1, 0), (0x11, 9, 0, len(MODEL_BYTES))]):
        struct.pack_into('>HHIIII', archive, 0x60 + index * 20, index, 0,
                         flags << 24 | name, offset, size, 0)
    archive[0xA0:0xA0 + len(strings)] = strings
    archive += MODEL_BYTES
    data = bytearray(image.read_bytes())
    fst_offset, fst_size = struct.unpack_from('>II', data, 0x424)
    old = data[fst_offset:fst_offset + fst_size]
    count = struct.unpack_from('>I', old, 8)[0]
    entries, names = bytearray(old[:count * 12]), old[count * 12:]
    struct.pack_into('>I', entries, 8, count + 5)
    entries += struct.pack('>III', 0x01000000 | len(names), 0, count + 5)
    entries += struct.pack('>III', 0x01000000 | (len(names) + 4), count, count + 3)
    entries += struct.pack('>III', len(names) + 11, 0x5000, len(archive))
    entries += struct.pack('>III', 0x01000000 | (len(names) + 22), count, count + 5)
    entries += struct.pack('>III', len(names) + 31, 0x6000, len(PARTICLE_BYTES))
    fst = entries + names + b'res\0Object\0Always.arc\0Particle\0common.jpc\0'
    data[fst_offset:fst_offset + len(fst)] = fst
    struct.pack_into('>II', data, 0x428, len(fst), len(fst))
    data[0x5000:0x5000 + len(archive)] = archive
    data[0x6000:0x6000 + len(PARTICLE_BYTES)] = PARTICLE_BYTES
    image.write_bytes(data)
    contract = json.loads(contract_path.read_text())
    contract['image_sha1'] = hashlib.sha1(data).hexdigest()
    contract_path.write_text(json.dumps(contract))


def make_collector(directory, *, dynamic=False):
    directory.mkdir()
    make_seed(directory / 'baseline', keys=(42, 84, 126))
    factory = make_dynamic_collection if dynamic else make_model_collection
    metadata = factory(directory / 'observations', keys=(84,))
    metadata['runtime_identity_verified_rows'] = 3
    (directory / 'native-report.json').write_text(json.dumps(metadata))
    executable = directory / 'collector'
    executable.write_text('''#!/usr/bin/env python3
import json, shutil, sqlite3, sys
from pathlib import Path
root = Path(__file__).resolve().parent
mode = (root / 'mode').read_text() if (root / 'mode').exists() else 'valid'
if mode == 'fail':
    print('synthetic native failure', flush=True)
    sys.exit(7)
shutil.copyfile(root / 'observations/assets/initial_pipeline_cache.db', 'observed.db')
Path('cache').mkdir()
shutil.copyfile(root / 'baseline/initial_pipeline_cache.db', 'cache/pipeline_cache.db')
if mode == 'recorder-mismatch':
    with sqlite3.connect('cache/pipeline_cache.db') as db:
        db.execute('DELETE FROM pipeline_cache WHERE hash=84')
metadata = json.loads((root / 'native-report.json').read_text())
if len(sys.argv) >= 4 and sys.argv[3] != metadata['scenario']:
    sys.exit('wrong scenario input')
if len(sys.argv) == 5 and sys.argv[4] != metadata['resource']:
    sys.exit('wrong resource input')
if mode == 'wrong-resource':
    metadata['resource'] = '/res/Object/Other.arc:bdl/model.bdl'
if mode == 'no-draw':
    metadata['draw_calls'] = 0
if mode == 'malformed':
    metadata = []
Path('collection.json').write_text(json.dumps(metadata))
''')
    executable.chmod(0o700)
    for label in ['ps4', 'host']:
        (directory / f'{label}-contract.bin').write_bytes(b'Synthetic ABI witness')
    (directory / 'collector-build.json').write_text(json.dumps({
        'schema': 1, 'binary_sha256': hashlib.sha256(executable.read_bytes()).hexdigest(),
        'contract_sha256': hashlib.sha256(b'Synthetic ABI witness').hexdigest(), 'runtime_libraries': {}}))
    return directory / 'baseline'
