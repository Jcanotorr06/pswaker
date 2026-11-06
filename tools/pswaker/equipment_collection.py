"""Finite equipment recipes; shared assets never imply unexercised transitions."""
from asset_inventory import identifier, sha256, text_list
from disc_image import require
import particle_collection as particle


ARROW = 'equipment-arrow-tips-v1'
NORMAL = 'equipment-bomb-normal-v1'
CHEAP = 'equipment-bomb-cheap-v1'
SCENARIOS = [ARROW, NORMAL, CHEAP]
ARROW_GAPS = ['texture-animation', 'elemental-effects-and-trails', 'actor-lighting-and-collision',
              'player-attachment-and-flight', 'light-arrow', 'other-cameras']


def recipe(scenario):
    require(scenario in SCENARIOS, 'Unsupported equipment recipe')
    if scenario == ARROW:
        return {'resource': '/res/Object/Link.arc:bdlm/arrow.bdl',
                'script': {'states': ['normal', 'fire', 'ice', 'normal'], 'frames_per_state': 1,
                           'loader_flags': 8224, 'model_flags': 524288, 'differed_display_list_flags': 285212706}}
    resource = '/res/Particle/common.jpc:' + ('0x000b+0x2009+0x200a+0x2008' if scenario == NORMAL
                                            else '0x000b+0x232a+0x200a+0x2008')
    return {'resource': resource, 'script': {**particle.script(resource),
                                           'setup': 'normal-bomb-v1' if scenario == NORMAL else 'cheap-bomb-v1'}}


def check_report(metadata):
    expected = recipe(metadata.get('scenario'))
    require(metadata.get('schema') == 1 and all(metadata.get(k) == v for k, v in expected.items()),
            'Equipment resource/script differs from fixed recipe')
    if metadata['scenario'] != ARROW:
        require(metadata.get('method') == 'dynamic-effect-draw' and metadata.get('unhandled_states') == particle.UNHANDLED,
                'Invalid equipment effect method or exclusions')
        particle.check_lifetimes(metadata, max_ticks=240, emitter_limit=4)
        return
    require(metadata.get('method') == 'scripted-equipment-draw' and metadata.get('unhandled_states') == ARROW_GAPS
            and type(metadata.get('materials')) is int and metadata['materials'] > 0,
            'Invalid equipment model method or exclusions')
    states = metadata.get('states')
    require(isinstance(states, list) and len(states) == 4, 'Incomplete equipment state cycle')
    states = metadata['states']
    for tick, (step, state) in enumerate(zip(states, expected['script']['states']), 1):
        require(isinstance(step, dict) and type(step.get('tick')) is int and step['tick'] == tick
                and step.get('state') == state and all(type(step.get(k)) is int and step[k] > 0
                    for k in ['draw_calls', 'pipeline_lookups']), 'Invalid equipment draw state')
        keys = step.get('configurations')
        require(isinstance(keys, list) and bool(keys) and all(isinstance(k, dict) and set(k) == {'type', 'hash'}
                and type(k['type']) is int and k['type'] in [0, 1] and type(k['hash']) is int
                and -(2**63) <= k['hash'] < 2**63 for k in keys), 'Invalid equipment state mapping')
        keys = step['configurations']
        require(len({(k['type'], k['hash']) for k in keys}) == len(keys) <= step['pipeline_lookups'],
                'Incomplete equipment state mapping')
    require(type(metadata.get('frames')) is int and metadata['frames'] == 4
            and all(type(metadata.get(k)) is int and metadata[k] == sum(s[k] for s in states)
                    for k in ['draw_calls', 'pipeline_lookups']), 'Invalid equipment draw totals')


def read_manifest(document):
    require(document.get('schema') == 1 and document.get('kind') == 'equipment-actions'
            and identifier(document.get('id')) and sha256(document.get('image_sha256'))
            and sha256(document.get('contract_sha256')), 'Invalid equipment manifest identity/target')
    collector = document.get('collector')
    require(isinstance(collector, dict) and set(collector) == {'sha256', 'build_sha256'}
            and all(sha256(v) for v in collector.values()) and text_list(document.get('exclusions')),
            'Equipment manifest requires collector identities and exclusions')
    rows = document.get('rows')
    require(isinstance(rows, list) and 0 < len(rows) <= 16, 'Equipment manifest exceeds bounded row set')
    rows = document['rows']
    seen = set()
    for row in rows:
        require(isinstance(row, dict) and identifier(row.get('id')) and row['id'] not in seen
                and identifier(row.get('family')) and text_list(row.get('source_references'))
                and text_list(row.get('assumptions')), 'Invalid equipment row or source attribution')
        seen.add(row['id'])
        require(row.get('action') in ['exercise', 'unsupported', 'missing'], 'Unsupported equipment row action')
        if row['action'] != 'exercise':
            require(all(isinstance(row.get(k), str) and row[k].strip() for k in ['reason', 'owner']),
                    'Equipment gap requires reason and owner')
            continue
        require(all(row.get(k) == v for k, v in recipe(row.get('scenario')).items()),
                'Equipment row differs from fixed recipe')
        identity = row.get('input_identity')
        model = row['scenario'] == ARROW
        hashes = ['archive_sha256', 'model_sha256'] if model else ['particle_sha256']
        size = 'model_bytes' if model else 'particle_bytes'
        require(isinstance(identity, dict) and set(identity) == {*hashes, size}
                and all(sha256(identity.get(k)) for k in hashes)
                and type(identity.get(size)) is int and identity[size] > 0, 'Invalid equipment input identity')
    return document
