"""Data-free observations of the public presentation collection boundary."""
import json
import hashlib
import struct

from synthetic_pipeline import make_model_collection


def make_presentation_collection(directory, *, menu=True, clothes=False, keys=(84, 126)):
    metadata = make_model_collection(directory, keys=keys)
    names = ['plain', 'tinted', 'faded', 'plain-repeated'] if menu else ['black-half', 'black-full', 'white-half', 'black-half-repeated']
    paths = ['/res/Object/Always.arc', '/res/Object/System.arc']
    if menu:
        paths.append('/res/Msg/clctres.arc')
    if clothes:
        names = ['hero', 'casual', 'hero-repeated']
        paths = ['/res/Object/Always.arc', '/res/Object/System.arc', '/res/Object/Link.arc']
    layout = {'key': 16288162637680331091, 'attachments': 1, 'color_format': 27,
              'depth_format': 48, 'samples': 1, 'width': 1280, 'height': 720}
    metadata.update(scenario='mode-link-clothes-v1' if clothes else 'menu-picture-colors-v1' if menu else 'cutscene-fade-v1',
                    method='scripted-presentation-draw', resource='/res/Object/Always.arc',
                    script={'states': names, 'frames_per_state': 1, 'setup': 'fixed-presentation-v1'},
                    frames=len(names), draw_calls=len(names), pipeline_lookups=len(names),
                    unhandled_states=['menu-controllers-and-layouts', 'story-and-camera-controllers',
                                      'framebuffer-effects', 'player-animation-and-attachments', 'unreachable-one-time-states'],
                    resources={path: {'sha256': 'd' * 64, 'bytes': 100} for path in paths},
                    contract_sha256='f' * 64, layout=layout,
                    preparation_layouts=[{'role': 'scene', **layout}, {'role': 'offscreen', **layout}],
                    states=[{'tick': i + 1, 'state': name, 'draw_calls': 1, 'pipeline_lookups': 1,
                             'layout_keys': [16288162637680331091],
                             'configurations': [{'type': 0, 'hash': keys[i % len(keys)]}]}
                            for i, name in enumerate(names)])
    (directory / 'collection.json').write_text(json.dumps(metadata))
    return metadata


def add_presentation_resources(image, contract_path):
    data = bytearray(image.read_bytes())
    fst_offset, fst_size = struct.unpack_from('>II', data, 0x424)
    old = data[fst_offset:fst_offset + fst_size]
    count = struct.unpack_from('>I', old, 8)[0]
    entries, names = bytearray(old[:count * 12]), bytearray(old[count * 12:])
    end = count + 7
    struct.pack_into('>I', entries, 8, end)

    def name(value):
        offset = len(names)
        names.extend(value.encode() + b'\0')
        return offset
    entries += struct.pack('>III', 0x01000000 | name('res'), 0, end)
    entries += struct.pack('>III', 0x01000000 | name('Object'), count, count + 5)
    for filename, offset in [('Always.arc', 0x5000), ('System.arc', 0x6000), ('Link.arc', 0x7000)]:
        payload = ('Synthetic ' + filename).encode()
        data[offset:offset + len(payload)] = payload
        entries += struct.pack('>III', name(filename), offset, len(payload))
    entries += struct.pack('>III', 0x01000000 | name('Msg'), count, end)
    payload = b'Synthetic native menu archive'
    data[0x7800:0x7800 + len(payload)] = payload
    entries += struct.pack('>III', name('clctres.arc'), 0x7800, len(payload))
    fst = entries + names
    data[fst_offset:fst_offset + len(fst)] = fst
    struct.pack_into('>II', data, 0x428, len(fst), len(fst))
    image.write_bytes(data)
    contract = json.loads(contract_path.read_text())
    contract['image_sha1'] = hashlib.sha1(data).hexdigest()
    contract_path.write_text(json.dumps(contract))
