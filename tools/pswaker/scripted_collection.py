"""Validation shared by finite scripted recipes; shared inputs never imply coverage."""
from asset_inventory import identifier, sha256, text_list
from disc_image import require


STATE_METHODS = ['scripted-equipment-draw', 'scripted-actor-draw']


def sized_hashes(value, hashes, size):
    return (isinstance(value, dict) and set(value) == {*hashes, size}
            and all(sha256(value.get(k)) for k in hashes)
            and type(value.get(size)) is int and value[size] > 0)


def check_state_steps(metadata, expected):
    states = metadata.get('states')
    require(isinstance(states, list) and len(states) == len(expected), 'Incomplete scripted state cycle')
    states = metadata['states']
    for tick, (step, state) in enumerate(zip(states, expected), 1):
        require(isinstance(step, dict) and type(step.get('tick')) is int and step['tick'] == tick
                and step.get('state') == state and all(type(step.get(k)) is int and step[k] > 0
                    for k in ['draw_calls', 'pipeline_lookups']), 'Invalid scripted draw state')
        keys = step.get('configurations')
        require(isinstance(keys, list) and bool(keys) and all(isinstance(k, dict) and set(k) == {'type', 'hash'}
                and type(k['type']) is int and k['type'] in [0, 1] and type(k['hash']) is int
                and -(2**63) <= k['hash'] < 2**63 for k in keys), 'Invalid scripted state mapping')
        keys = step['configurations']
        require(len({(k['type'], k['hash']) for k in keys}) == len(keys) <= step['pipeline_lookups'],
                'Incomplete scripted state mapping')
    require(type(metadata.get('frames')) is int and metadata['frames'] == len(expected)
            and all(type(metadata.get(k)) is int and metadata[k] == sum(s[k] for s in states)
                    for k in ['draw_calls', 'pipeline_lookups']), 'Invalid scripted draw totals')


def read_manifest(document, *, kind, row_limit, recipe, valid_identity):
    require(document.get('schema') == 1 and document.get('kind') == kind
            and identifier(document.get('id')) and sha256(document.get('image_sha256'))
            and sha256(document.get('contract_sha256')), 'Invalid scripted manifest identity/target')
    collector = document.get('collector')
    require(isinstance(collector, dict) and set(collector) == {'sha256', 'build_sha256'}
            and all(sha256(v) for v in collector.values()) and text_list(document.get('exclusions')),
            'Scripted manifest requires collector identities and exclusions')
    rows = document.get('rows')
    require(isinstance(rows, list) and 0 < len(rows) <= row_limit, 'Scripted manifest exceeds bounded row set')
    rows = document['rows']
    seen = set()
    for row in rows:
        require(isinstance(row, dict) and identifier(row.get('id')) and row['id'] not in seen
                and identifier(row.get('family')) and text_list(row.get('source_references'))
                and text_list(row.get('assumptions')), 'Invalid scripted row or source attribution')
        seen.add(row['id'])
        require(row.get('action') in ['exercise', 'unsupported', 'missing'], 'Unsupported scripted row action')
        if row['action'] != 'exercise':
            require(all(isinstance(row.get(k), str) and row[k].strip() for k in ['reason', 'owner']),
                    'Scripted gap requires reason and owner')
            continue
        require(all(row.get(k) == v for k, v in recipe(row.get('scenario')).items()),
                'Scripted row differs from fixed recipe')
        require(valid_identity(row['scenario'], row.get('input_identity')), 'Invalid scripted input identity')
    return document
