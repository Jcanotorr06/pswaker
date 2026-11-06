"""Bounded scene draw paths, with explicit world/camera and preparation contracts."""
import hashlib

from disc_image import require
import scripted_collection as scripted


PROVENANCE = 'environment-scene-batch'
RESOURCE = '/res/Object/Always.arc'
ARCHIVES = [RESOURCE, '/res/Object/System.arc']
SCENARIOS = {
    'scene-ocean-world-v1': ['day', 'night', 'dense-fog', 'range-adjusted', 'camera-raised', 'day-repeated'],
    'scene-simple-shadows-v1': ['untextured', 'textured', 'sloped-raised', 'textured-repeated'],
    'scene-alpha-overlap-v1': ['sphere', 'cube', 'sphere-faded', 'sea-shadow-sphere', 'sphere-repeated'],
}
UNHANDLED = ['stage-and-weather-controllers', 'wave-simulation', 'real-shadow-receivers',
             'mirrors-and-reflections', 'other-camera-and-effect-combinations']
LAYOUT = {'key': 16288162637680331091, 'attachments': 1, 'color_format': 27,
          'depth_format': 48, 'samples': 1, 'width': 1280, 'height': 720}


def recipe(scenario):
    require(scenario in SCENARIOS, 'Unsupported scene recipe')
    return {'resource': RESOURCE, 'script': {'states': SCENARIOS[scenario], 'frames_per_state': 1,
                                            'setup': 'fixed-scene-world-camera-v1'}}


def valid_identity(scenario, identity):
    return (isinstance(identity, dict) and set(identity) == set(ARCHIVES)
            and all(scripted.sized_hashes(value, ['sha256'], 'bytes') for value in identity.values()))


def input_identity(disc, files):
    result = {}
    for path in ARCHIVES:
        offset, size = files[path.lstrip('/')]
        data = disc.read(offset, size, path)
        result[path] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    return result


def check_report(metadata):
    expected = recipe(metadata.get('scenario'))
    require(metadata.get('schema') == 1 and metadata.get('method') == 'scripted-scene-draw'
            and all(metadata.get(k) == v for k, v in expected.items())
            and metadata.get('unhandled_states') == UNHANDLED, 'Scene report differs from fixed recipe')
    scripted.check_state_steps(metadata, expected['script']['states'])
    layout = metadata.get('layout')
    preparations = metadata.get('preparation_layouts')
    require(isinstance(layout, dict) and all(type(layout.get(k)) is int for k in LAYOUT)
            and isinstance(preparations, list) and all(isinstance(p, dict)
                and all(type(p.get(k)) is int for k in LAYOUT) for p in preparations)
            and layout == LAYOUT and preparations == [
        {'role': 'scene', **LAYOUT}, {'role': 'offscreen', **LAYOUT}],
        'Scene layout differs from selected stock preparation contract')
    for step in metadata['states']:
        require(step.get('layout_keys') == [LAYOUT['key']], 'Missing or incompatible scene state layout mapping')


def read_manifest(document):
    return scripted.read_manifest(document, kind='environment-scenes', row_limit=24,
                                  recipe=recipe, valid_identity=valid_identity)
