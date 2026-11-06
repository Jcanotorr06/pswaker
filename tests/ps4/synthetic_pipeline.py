"""Synthetic renderer descriptions; never console or driver shader data."""
import hashlib
import json
import sqlite3
import struct
from contextlib import closing


def make_seed(directory, *, keys=(42, 84)):
    directory.mkdir(parents=True)
    path = directory / 'initial_pipeline_cache.db'
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('CREATE TABLE aurora_schema(value INTEGER)')
        db.execute('INSERT INTO aurora_schema VALUES (1)')
        db.execute('CREATE TABLE pipeline_cache(type INTEGER, hash INTEGER, config_version INTEGER, '
                   'config_size INTEGER, config BLOB, first_frame_used INTEGER, PRIMARY KEY(type,hash))')
        for key in keys:
            db.execute('INSERT INTO pipeline_cache VALUES (0,?,5,8,?,10)',
                       (key, struct.pack('<I4B', 5, key % 256, 1, 1, 0)))
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    report = {'schema': 1, 'installed_path': '/app0/initial_pipeline_cache.db',
              'source_files': {'synthetic.db': {'bytes': path.stat().st_size, 'sha256': sha}},
              'rows': len(keys), 'configurations': [{'type': 0, 'version': 5, 'bytes': 8, 'rows': len(keys)}],
              'sha256': sha}
    (directory / 'pipeline-seed.json').write_text(json.dumps(report))
    return report


def make_model_collection(directory, *, keys=(84, 126)):
    asset = make_seed(directory / 'assets', keys=keys)
    report = {'schema': 1, 'scenario': 'always-small-pot-stock-v1',
              'method': 'asset-material-draw', 'draw_calls': 1,
              'resource': '/res/Object/Always.arc:bdl/obm_kotubo1.bdl', 'materials': 1,
              'collector': {'sha256': 'a' * 64, 'build_sha256': 'b' * 64},
              'image_sha256': 'c' * 64, 'seed_sha256': asset['sha256']}
    (directory / 'collection.json').write_text(json.dumps(report))
    return report


def make_dynamic_collection(directory, *, keys=(84, 126)):
    report = make_model_collection(directory, keys=keys)
    report.update(scenario='common-pot-debris-lifecycle-v1', method='dynamic-effect-draw',
                  resource='/res/Particle/common.jpc:0x0018', frames=6,
                  draw_calls=4, pipeline_lookups=4,
                  script={'effect_id': 24, 'random_seed': 0, 'max_ticks': 180,
                          'position': [0, 0, 0], 'scale': [1, 1, 1],
                          'color': [255, 255, 255, 255], 'texture_indices': [0, 1]},
                  unhandled_states=['model-shards-0x0017', 'actor-lighting-and-collision',
                                    'other-pot-textures', 'overlapping-effects', 'other-cameras'])
    report.pop('materials')
    report['variations'] = [
        {'texture_index': texture, 'steps': [
            {'tick': tick, 'particles': 1 if tick < 3 else 0,
             'emitters': 1 if tick < 3 else 0,
             'draw_calls': 1 if tick < 3 else 0, 'pipeline_lookups': 1 if tick < 3 else 0,
             'configurations': [{'type': 0, 'hash': keys[texture % len(keys)]}] if tick < 3 else []}
            for tick in range(1, 4)]}
        for texture in [0, 1]]
    (directory / 'collection.json').write_text(json.dumps(report))
    return report


def make_particle_collection(directory, resource='/res/Particle/common.jpc:0x000b', keys=(84, 126)):
    metadata = make_dynamic_collection(directory, keys=keys)
    metadata.update(scenario='particle-effect-lifecycle-v1', resource=resource,
                    script={'effect_ids': [int(x, 16) for x in resource.split(':')[1].split('+')],
                            'max_ticks': 240, 'continuous_emission_ticks': 30,
                            'variations': [{'random_seed': 0, 'scale': 1, 'alpha': 255, 'texture_index': 0},
                                           {'random_seed': 1, 'scale': 2, 'alpha': 128, 'texture_index': 1}]},
                    unhandled_states=['stage-lighting-and-wind', 'projection-framebuffer',
                                      'model-particles', 'actor-collision', 'other-cameras'])
    (directory / 'collection.json').write_text(json.dumps(metadata))
    return metadata
