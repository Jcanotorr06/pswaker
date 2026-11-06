"""Finite equipment recipes; shared assets never imply unexercised transitions."""
from asset_inventory import sha256
from disc_image import require
import particle_collection as particle
import scripted_collection as scripted


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
    scripted.check_state_steps(metadata, expected['script']['states'])


def valid_identity(scenario, identity):
    model = scenario == ARROW
    hashes = ['archive_sha256', 'model_sha256'] if model else ['particle_sha256']
    size = 'model_bytes' if model else 'particle_bytes'
    return (isinstance(identity, dict) and set(identity) == {*hashes, size}
            and all(sha256(identity.get(k)) for k in hashes)
            and type(identity.get(size)) is int and identity[size] > 0)


def read_manifest(document):
    return scripted.read_manifest(document, kind='equipment-actions', row_limit=16,
                                  recipe=recipe, valid_identity=valid_identity)
