"""Fixed, data-free resource/state manifests for private material collection."""
import json
import re

from disc_image import require


def sha256(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def identifier(value):
    return isinstance(value, str) and re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', value) is not None


def text_list(value):
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def model_resource(value):
    return (isinstance(value, str)
            and re.fullmatch(r'/res/[A-Za-z0-9_./-]+\.arc:[A-Za-z0-9_./-]+\.(?:bdl|bmd)', value) is not None
            and all(part not in ['', '.', '..'] for part in value[1:].replace(':', '/').split('/')))


def read_manifest(path):
    manifest = json.loads(path.read_text(encoding='utf-8'))
    require(isinstance(manifest, dict) and manifest.get('schema') == 1
            and identifier(manifest.get('id')), 'Invalid inventory manifest identity')
    collector = manifest.get('collector')
    require(sha256(manifest.get('image_sha256')) and sha256(manifest.get('contract_sha256'))
            and isinstance(collector, dict) and set(collector) == {'sha256', 'build_sha256'}
            and all(sha256(value) for value in collector.values()), 'Invalid inventory input/collector identities')
    exclusions = manifest.get('dynamic_exclusions')
    require(isinstance(exclusions, list) and bool(exclusions) and all(
        isinstance(row, dict) and identifier(row.get('id'))
        and all(isinstance(row.get(key), str) and row[key].strip() for key in ['owner', 'reason'])
        for row in exclusions), 'Inventory requires explicit dynamic-path exclusions and owners')
    rows = manifest.get('rows')
    require(isinstance(rows, list) and bool(rows), 'Inventory requires resource/state rows')
    rows = manifest['rows']
    identities = set()
    for row in rows:
        require(isinstance(row, dict) and identifier(row.get('id')) and row['id'] not in identities,
                'Invalid or duplicate inventory row identity')
        identities.add(row['id'])
        require(identifier(row.get('family')) and text_list(row.get('source_references'))
                and text_list(row.get('assumptions')), 'Inventory row requires family, source references and assumptions')
        dimensions = row.get('dimensions')
        require(isinstance(dimensions, dict) and set(dimensions) == {'content', 'mode', 'state'}
                and all(text_list(value) for value in dimensions.values()), 'Invalid inventory content/mode/state dimensions')
        require(model_resource(row.get('resource')), 'Invalid inventory model resource')
        if row.get('action') in ['exercise', 'shared']:
            require(row['resource'].endswith('.bdl') and row['dimensions']['state'] == ['stock-bdl-v1'],
                    'Only the proven stock BDL state is supported for batch exercise')
        identity = row.get('input_identity')
        require(isinstance(identity, dict) and set(identity) == {'archive_sha256', 'model_sha256', 'model_bytes'}
                and all(sha256(identity.get(key)) for key in ['archive_sha256', 'model_sha256'])
                and type(identity.get('model_bytes')) is int and identity['model_bytes'] > 0,
                'Invalid inventory resource identity')
        action = row.get('action')
        require(action in ['exercise', 'shared', 'unsupported', 'missing'], 'Unsupported inventory action')
        if action in ['unsupported', 'missing']:
            require(isinstance(row.get('reason'), str) and row['reason'].strip(),
                    'Inventory gap requires an explicit reason')
        if action == 'shared':
            require(identifier(row.get('shared_with')) and isinstance(row.get('justification'), str)
                    and row['justification'].strip(), 'Shared inventory row requires mapping and justification')
    by_id = {row['id']: row for row in rows}
    for row in rows:
        if row['action'] == 'shared':
            target = by_id.get(row['shared_with'])
            require(target is not None and target['action'] == 'exercise',
                    'Shared mapping must point directly to an exercised row')
            target = by_id[row['shared_with']]
            require(row['resource'] == target['resource'] and row['input_identity'] == target['input_identity']
                    and row['dimensions']['state'] == target['dimensions']['state'],
                    'Shared mapping must retain identical source bytes and stock state')
    return manifest
