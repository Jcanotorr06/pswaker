"""Finite menu, transition and alternate-clothes rendering setups."""
import hashlib

from disc_image import require
import scene_collection as scene
import scripted_collection as scripted


PROVENANCE = 'presentation-variation-batch'
RESOURCE = '/res/Object/Always.arc'
SCENARIOS = {
    'menu-picture-colors-v1': ['plain', 'tinted', 'faded', 'plain-repeated'],
    'cutscene-fade-v1': ['black-half', 'black-full', 'white-half', 'black-half-repeated'],
    'mode-link-clothes-v1': ['hero', 'casual', 'hero-repeated'],
}
UNHANDLED = ['menu-controllers-and-layouts', 'story-and-camera-controllers',
             'framebuffer-effects', 'player-animation-and-attachments', 'unreachable-one-time-states']


def recipe(scenario):
    require(scenario in SCENARIOS, 'Unsupported presentation recipe')
    return {'resource': RESOURCE, 'script': {'states': SCENARIOS[scenario], 'frames_per_state': 1,
                                            'setup': 'fixed-presentation-v1'}}


def archives(scenario):
    recipe(scenario)
    return [*scene.ARCHIVES, *({'menu-picture-colors-v1': ['/res/Msg/clctres.arc'],
                              'mode-link-clothes-v1': ['/res/Object/Link.arc']}.get(scenario, []))]


def valid_identity(scenario, identity):
    return (isinstance(identity, dict) and set(identity) == set(archives(scenario))
            and all(scripted.sized_hashes(value, ['sha256'], 'bytes') for value in identity.values()))


def input_identity(scenario, disc, files):
    result = {}
    for path in archives(scenario):
        offset, size = files[path.lstrip('/')]
        data = disc.read(offset, size, path)
        result[path] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    return result


def check_report(metadata):
    expected = recipe(metadata.get('scenario'))
    require(metadata.get('schema') == 1 and metadata.get('method') == 'scripted-presentation-draw'
            and all(metadata.get(k) == v for k, v in expected.items())
            and metadata.get('unhandled_states') == UNHANDLED, 'Presentation report differs from fixed recipe')
    scripted.check_state_steps(metadata, expected['script']['states'])
    scene.check_layout(metadata)


def read_manifest(document):
    rows = document.get('rows')
    require(isinstance(rows, list) and all(isinstance(row, dict) for row in rows), 'Invalid presentation rows')
    checked = {**document, 'rows': [{**row, 'action': 'exercise'} if row.get('action') == 'shared' else row
                                  for row in rows]}
    scripted.read_manifest(checked, kind='menu-cutscene-modes', row_limit=24,
                           recipe=recipe, valid_identity=valid_identity)
    by_id = {row['id']: row for row in rows}
    for row in rows:
        if row['action'] != 'shared':
            continue
        target = by_id.get(row.get('shared_with'))
        require(isinstance(target, dict) and target['action'] == 'exercise'
                and all(row.get(k) == target[k] for k in ['scenario', 'resource', 'script', 'input_identity'])
                and all(isinstance(row.get(k), str) and row[k].strip() for k in ['justification', 'owner']),
                'Equivalent presentation path requires an identical exercised setup, justification and owner')
    return document
