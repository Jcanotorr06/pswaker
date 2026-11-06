"""Literal data-free equipment reports for public CLI tests."""
import json

from synthetic_pipeline import make_particle_collection, make_model_collection


def make_equipment_collection(directory, *, arrow=True, keys=(84, 126)):
    if arrow:
        metadata = make_model_collection(directory, keys=keys)
        metadata.update(scenario='equipment-arrow-tips-v1', method='scripted-equipment-draw',
                        resource='/res/Object/Link.arc:bdlm/arrow.bdl',
                        script={'states': ['normal', 'fire', 'ice', 'normal'], 'frames_per_state': 1,
                                'loader_flags': 8224, 'model_flags': 524288, 'differed_display_list_flags': 285212706},
                        unhandled_states=['texture-animation', 'elemental-effects-and-trails',
                                          'actor-lighting-and-collision', 'player-attachment-and-flight',
                                          'light-arrow', 'other-cameras'],
                        frames=4, draw_calls=4, pipeline_lookups=4,
                        states=[{'tick': i + 1, 'state': state, 'draw_calls': 1, 'pipeline_lookups': 1,
                                 'configurations': [{'type': 0, 'hash': keys[i % len(keys)]}]}
                                for i, state in enumerate(['normal', 'fire', 'ice', 'normal'])])
    else:
        metadata = make_particle_collection(directory, '/res/Particle/common.jpc:0x000b+0x232a+0x200a+0x2008', keys)
        metadata.update(scenario='equipment-bomb-cheap-v1')
        metadata['script']['setup'] = 'cheap-bomb-v1'
    metadata.update(resources=({'archive_sha256': 'd' * 64, 'model_sha256': 'e' * 64, 'model_bytes': 100}
                               if arrow else {'particle_sha256': 'd' * 64, 'particle_bytes': 100}),
                    contract_sha256='f' * 64)
    (directory / 'collection.json').write_text(json.dumps(metadata))
    return metadata
