"""Bounded common-bank particle recipes and evidence validation."""
import re

from disc_image import require
from asset_inventory import identifier, sha256, text_list


SCENARIO = 'particle-effect-lifecycle-v1'
SUPPORTED_EFFECTS = {0x2022, 0x2027, 0x2008, 0x2009, 0x200a, 0x000b,
                     0x0013, 0x0018, 0x0019, 0x232a}
UNHANDLED = ['stage-lighting-and-wind', 'projection-framebuffer',
             'model-particles', 'actor-collision', 'other-cameras']


def effect_ids(resource, supported=SUPPORTED_EFFECTS):
    require(isinstance(resource, str) and re.fullmatch(
        r'/res/Particle/common\.jpc:0x[0-9a-f]{4}(?:\+0x[0-9a-f]{4}){0,3}', resource),
        'Invalid particle resource or oversized combination')
    effects = [int(value, 16) for value in resource.split(':')[1].split('+')]
    require(len(set(effects)) == len(effects) and set(effects) <= supported,
            'Unsupported or duplicate particle effect')
    return effects


def script(resource, supported=SUPPORTED_EFFECTS):
    return {'effect_ids': effect_ids(resource, supported), 'max_ticks': 240, 'continuous_emission_ticks': 30,
            'variations': [{'random_seed': 0, 'scale': 1, 'alpha': 255, 'texture_index': 0},
                           {'random_seed': 1, 'scale': 2, 'alpha': 128, 'texture_index': 1}]}


def check_report(metadata):
    require(metadata.get('schema') == 1 and metadata.get('method') == 'dynamic-effect-draw'
            and metadata.get('script') == script(metadata.get('resource'))
            and metadata.get('unhandled_states') == UNHANDLED,
            'Invalid particle script or exclusions')
    check_lifetimes(metadata, max_ticks=240, emitter_limit=len(metadata['script']['effect_ids']))


def check_lifetimes(metadata, *, max_ticks, emitter_limit):
    variations = metadata.get('variations')
    require(isinstance(variations, list) and len(variations) == 2, 'Invalid dynamic particle variations')
    variations = metadata['variations']
    totals = dict(frames=0, draw_calls=0, pipeline_lookups=0)
    for index, variation in enumerate(variations):
        require(isinstance(variation, dict) and type(variation.get('texture_index')) is int
                and variation['texture_index'] == index, 'Invalid dynamic particle variation identity')
        steps = variation.get('steps')
        require(isinstance(steps, list) and 1 < len(steps) <= max_ticks, 'Invalid dynamic particle lifetime length')
        steps = variation['steps']
        peak = draws = lookups = 0
        for tick, step in enumerate(steps, 1):
            require(isinstance(step, dict) and type(step.get('tick')) is int and step['tick'] == tick
                    and all(type(step.get(name)) is int and step[name] >= 0
                            for name in ['particles', 'emitters', 'draw_calls', 'pipeline_lookups']),
                    'Invalid dynamic particle lifetime step')
            require(0 <= step['emitters'] <= emitter_limit
                    and (step['emitters'] > 0 or tick == len(steps)), 'Invalid dynamic particle emitter transition')
            keys = step.get('configurations')
            require(isinstance(keys, list) and all(isinstance(key, dict) and set(key) == {'type', 'hash'}
                    and type(key['type']) is int and key['type'] in [0, 1] and type(key['hash']) is int
                    and -(2**63) <= key['hash'] < 2**63 for key in keys), 'Invalid dynamic particle configuration mapping')
            keys = step['configurations']
            require(len({(k['type'], k['hash']) for k in keys}) == len(keys)
                    and bool(keys) == bool(step['pipeline_lookups'])
                    and len(keys) <= step['pipeline_lookups'], 'Incomplete dynamic particle configuration mapping')
            peak = max(peak, step['particles'])
            draws += step['draw_calls']
            lookups += step['pipeline_lookups']
        require(peak > 0 and draws > 0 and lookups > 0 and steps[-1]['particles'] == 0
                and steps[-1]['emitters'] == 0, 'Incomplete dynamic particle lifetime or no actual draws')
        totals['frames'] += len(steps)
        totals['draw_calls'] += draws
        totals['pipeline_lookups'] += lookups
    require(all(type(metadata.get(key)) is int and metadata[key] == value for key, value in totals.items()),
            'Invalid dynamic particle collection totals')


def read_manifest(document):
    require(isinstance(document, dict) and document.get('schema') == 1
            and document.get('kind') == 'particle-effects' and identifier(document.get('id')),
            'Invalid particle manifest identity')
    require(sha256(document.get('image_sha256')) and sha256(document.get('contract_sha256'))
            and isinstance(document.get('collector'), dict)
            and set(document['collector']) == {'sha256', 'build_sha256'}
            and all(sha256(x) for x in document['collector'].values()), 'Invalid particle input/target identities')
    require(text_list(document.get('exclusions')), 'Particle manifest requires explicit exclusions')
    rows = document.get('rows')
    require(isinstance(rows, list) and bool(rows) and len(rows) <= 32, 'Particle manifest requires a bounded row set')
    rows = document['rows']
    seen = set()
    for row in rows:
        require(isinstance(row, dict) and identifier(row.get('id')) and row['id'] not in seen,
                'Invalid or duplicate particle row identity')
        seen.add(row['id'])
        require(identifier(row.get('family')) and text_list(row.get('source_references'))
                and text_list(row.get('assumptions')), 'Particle row requires source references and assumptions')
        require(row.get('action') in ['exercise', 'unsupported', 'missing'], 'Unsupported particle row action')
        if row['action'] == 'exercise':
            require(row.get('script') == script(row.get('resource')), 'Particle row script differs from fixed recipe')
        else:
            require(isinstance(row.get('reason'), str) and row['reason'].strip(), 'Particle gap requires a reason')
        if row['action'] == 'exercise':
            identity = row.get('input_identity')
            require(isinstance(identity, dict) and set(identity) == {'particle_sha256', 'particle_bytes'}
                    and sha256(identity.get('particle_sha256'))
                    and type(identity.get('particle_bytes')) is int and identity['particle_bytes'] > 0,
                    'Invalid particle bank identity')
    return document
