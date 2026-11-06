"""Literal data-free enemy/boss reports and disc resources for public CLI tests."""
import hashlib
import json
import struct

from synthetic_pipeline import make_model_collection, make_particle_collection
from synthetic_model_collector import PARTICLE_BYTES


PEAHAT_RESOURCE = '/res/Object/Ph.arc:bdlm/phb.bdl'
PEAHAT_COMPANIONS = ['/res/Object/Ph.arc:bdlm/php.bdl', '/res/Object/Always.arc:bmtm/ice.bmt',
                     '/res/Object/Always.arc:btk/ice.btk', '/res/Object/System.arc:dat/toon.bti',
                     '/res/Object/System.arc:dat/toonex.bti']
ACTOR_GAPS = ['actor-process-and-ai', 'skeletal-animation', 'stage-lighting-and-fog', 'shadows', 'other-cameras']


def make_enemy_collection(directory, *, actor=True, keys=(84, 126)):
    if actor:
        metadata = make_model_collection(directory, keys=keys)
        metadata.pop('materials')
        states = ['stock', 'frozen', 'restored']
        metadata.update(scenario='enemy-peahat-freeze-v1', method='scripted-actor-draw', resource=PEAHAT_RESOURCE,
                        script={'states': states, 'frames_per_state': 1}, unhandled_states=ACTOR_GAPS,
                        frames=3, draw_calls=3, pipeline_lookups=3,
                        states=[{'tick': i + 1, 'state': state, 'draw_calls': 1, 'pipeline_lookups': 1,
                                 'configurations': [{'type': 0, 'hash': keys[i % len(keys)]}]}
                                for i, state in enumerate(states)])
        identity = {'archive_sha256': 'd' * 64, 'model_sha256': 'e' * 64, 'model_bytes': 100,
                    'companions': {name: {'sha256': 'b' * 64, 'bytes': 10} for name in PEAHAT_COMPANIONS}}
    else:
        metadata = make_particle_collection(directory, '/res/Particle/common.jpc:0x043c+0x043d+0x043e', keys)
        metadata.update(scenario='enemy-death-small-v1')
        metadata['script']['setup'] = 'enemy-death-small-v1'
        identity = {'particle_sha256': 'd' * 64, 'particle_bytes': 100}
    metadata.update(resources=identity, contract_sha256='f' * 64)
    (directory / 'collection.json').write_text(json.dumps(metadata))
    return metadata


def member_bytes(resource):
    return b'Synthetic member; no game content: ' + resource.encode()


def rarc(archive, directories):
    names = bytearray(b'root\0')
    entries, payload, nodes = [], bytearray(), [(b'ROOT', 0, len(directories), 0)]
    first = len(directories)
    for index, (directory, members) in enumerate(directories.items(), 1):
        nodes.append((b'DIR ', len(names), len(members), first))
        entries.append((2, len(names), index, 0))
        names += directory.encode() + b'\0'
        first += len(members)
    for directory, members in directories.items():
        for member in members:
            data = member_bytes(f'{archive}:{directory}/{member}')
            entries.append((0x11, len(names), len(payload), len(data)))
            names += member.encode() + b'\0'
            payload += data
    strings = 0x20 + len(nodes) * 16 + len(entries) * 20
    data_offset = strings + len(names)
    result = bytearray(0x20 + data_offset)
    struct.pack_into('>4sIII', result, 0, b'RARC', len(result) + len(payload), 0x20, data_offset)
    struct.pack_into('>6I', result, 0x20, len(nodes), 0x20, len(entries), 0x20 + len(nodes) * 16, len(names), strings)
    for index, node in enumerate(nodes):
        struct.pack_into('>4sIHHI', result, 0x40 + index * 16, node[0], node[1], 0, node[2], node[3])
    for index, (flags, name, offset, size) in enumerate(entries):
        struct.pack_into('>HHIIII', result, 0x40 + len(nodes) * 16 + index * 20, index, 0, flags << 24 | name, offset, size, 0)
    result[0x20 + strings:0x20 + strings + len(names)] = names
    return bytes(result + payload)


def add_enemy_resources(image, contract_path):
    archives = [('Always.arc', {'bmtm': ['ice.bmt'], 'btk': ['ice.btk']}),
                ('Ph.arc', {'bdlm': ['phb.bdl', 'php.bdl']}),
                ('System.arc', {'dat': ['toon.bti', 'toonex.bti']})]
    data = bytearray(image.read_bytes())
    fst_offset, fst_size = struct.unpack_from('>II', data, 0x424)
    old = data[fst_offset:fst_offset + fst_size]
    count = struct.unpack_from('>I', old, 8)[0]
    entries, names = bytearray(old[:count * 12]), bytearray(old[count * 12:])
    end = count + len(archives) + 4
    struct.pack_into('>I', entries, 8, end)

    def name(text):
        offset = len(names)
        names.extend(text.encode() + b'\0')
        return offset
    entries += struct.pack('>III', 0x01000000 | name('res'), 0, end)
    entries += struct.pack('>III', 0x01000000 | name('Object'), count, count + 2 + len(archives))
    for index, (archive, directories) in enumerate(archives):
        content = rarc(f'/res/Object/{archive}', directories)
        offset = 0x5000 + index * 0x800
        assert len(content) <= 0x800
        data[offset:offset + len(content)] = content
        entries += struct.pack('>III', name(archive), offset, len(content))
    entries += struct.pack('>III', 0x01000000 | name('Particle'), count, end)
    entries += struct.pack('>III', name('common.jpc'), 0x7000, len(PARTICLE_BYTES))
    fst = entries + names
    data[fst_offset:fst_offset + len(fst)] = fst
    struct.pack_into('>II', data, 0x428, len(fst), len(fst))
    data[0x7000:0x7000 + len(PARTICLE_BYTES)] = PARTICLE_BYTES
    image.write_bytes(data)
    contract = json.loads(contract_path.read_text())
    contract['image_sha1'] = hashlib.sha1(data).hexdigest()
    contract_path.write_text(json.dumps(contract))
