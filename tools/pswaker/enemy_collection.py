"""Finite enemy/boss recipes; shared resources never imply unexercised actors."""
from typing import NamedTuple

from disc_image import require
import particle_collection as particle
import scripted_collection as scripted


class ActorRecipe(NamedTuple):
    resource: str
    states: list
    members: list


PROVENANCE = 'enemy-actor-batch'
# Every actor recipe enters the same game resource setup, so each binds the
# freeze material and toon images it consumes along with its own members.
SHARED_INPUTS = ['/res/Object/Always.arc:bmtm/ice.bmt', '/res/Object/Always.arc:btk/ice.btk',
                 '/res/Object/System.arc:dat/toon.bti', '/res/Object/System.arc:dat/toonex.bti']
ACTORS = {
    'enemy-bokoblin-materials-v1': ActorRecipe(
        '/res/Object/Bk.arc:bdlm/bk.bdl',
        ['body-stock', 'green-with-shield', 'pink-with-telescope', 'body-frozen', 'body-restored',
         'blur-club-first', 'blur-club-second', 'blur-sword-first', 'blur-sword-second'],
        ['bmt/green.bmt', 'bmt/pink.bmt', 'bmt/bk_boko.bmt', 'bmt/bk_ken.bmt', 'bmd/bk_kb.bmd', 'bmd/bk_tate.bmd',
         'bdlm/bouen.bdl']),
    'enemy-chuchu-states-v1': ActorRecipe(
        '/res/Object/Cc.arc:bmdm/cc.bmd',
        ['body', 'stone-first', 'stone-second', 'puddle', 'breakup', 'frozen'],
        ['bdlm/cc_iwa.bdl', 'bdlm/cc_beta.bdl', 'bdlm/cc_ptcl.bdl', 'brk/cc.brk', 'brk/cc_beta.brk',
         'brk/cc_iwa01.brk', 'brk/cc_iwa02.brk', 'btk/cc_iwa01.btk', 'btk/cc_iwa02.btk']),
    'enemy-peahat-freeze-v1': ActorRecipe(
        '/res/Object/Ph.arc:bdlm/phb.bdl',
        ['stock', 'frozen', 'restored'],
        ['bdlm/php.bdl']),
    'boss-jalhalla-visibility-v1': ActorRecipe(
        '/res/Object/Bpw.arc:bdlm/bpw.bdl',
        ['default', 'light-stun', 'curse-start', 'curse-end', 'light-freeze', 'possession', 'lantern'],
        ['bdlm/bpw_kan1.bdl', 'brk/default.brk', 'brk/hit.brk', 'brk/noroi_s1.brk', 'brk/noroi_e1.brk',
         'brk/hiraru1.brk', 'brk/bpw_kan1.brk']),
    'boss-gohma-defeat-v1': ActorRecipe(
        '/res/Object/Btd.arc:bmdm/sotai.bmd',
        ['phase-one', 'phase-two', 'defeat'],
        ['bmdm/btd.bmd', 'btk/btd.btk', 'brk/btd.brk', 'btk/sotai.btk', 'brk/sotai.brk', 'bmt/deada.bmt',
         'brk/deada.brk', 'btk/deada.btk']),
    'boss-puppet-ganon-water-v1': ActorRecipe(
        '/res/Object/Bgn.arc:bdlm/r0e_a.bdl',
        ['water-surface', 'water-mask', 'water-combined'],
        []),
}
EFFECTS = {'enemy-death-large-v1': '/res/Particle/common.jpc:0x0014+0x0013+0x0015+0x0016',
           'enemy-death-small-v1': '/res/Particle/common.jpc:0x043c+0x043d+0x043e'}
DEATH_EFFECTS = {0x0013, 0x0014, 0x0015, 0x0016, 0x043c, 0x043d, 0x043e}
SCENARIOS = [*ACTORS, *EFFECTS]
ACTOR_GAPS = ['actor-process-and-ai', 'skeletal-animation', 'stage-lighting-and-fog', 'shadows', 'other-cameras']


def recipe(scenario):
    require(scenario in SCENARIOS, 'Unsupported enemy recipe')
    if scenario in EFFECTS:
        resource = EFFECTS[scenario]
        return {'resource': resource, 'script': {**particle.script(resource, DEATH_EFFECTS), 'setup': scenario}}
    actor = ACTORS[scenario]
    return {'resource': actor.resource, 'script': {'states': actor.states, 'frames_per_state': 1}}


def companions(scenario):
    actor = ACTORS[scenario]
    archive = actor.resource.split(':')[0]
    return [f'{archive}:{member}' for member in actor.members] + SHARED_INPUTS


def check_report(metadata):
    expected = recipe(metadata.get('scenario'))
    require(metadata.get('schema') == 1 and all(metadata.get(k) == v for k, v in expected.items()),
            'Enemy resource/script differs from fixed recipe')
    if metadata['scenario'] in EFFECTS:
        require(metadata.get('method') == 'dynamic-effect-draw' and metadata.get('unhandled_states') == particle.UNHANDLED,
                'Invalid enemy effect method or exclusions')
        particle.check_lifetimes(metadata, max_ticks=240, emitter_limit=len(expected['script']['effect_ids']))
        return
    require(metadata.get('method') == 'scripted-actor-draw' and metadata.get('unhandled_states') == ACTOR_GAPS,
            'Invalid enemy actor method or exclusions')
    scripted.check_state_steps(metadata, expected['script']['states'])


def valid_identity(scenario, identity):
    if scenario in EFFECTS:
        return scripted.sized_hashes(identity, ['particle_sha256'], 'particle_bytes')
    if not isinstance(identity, dict):
        return False
    inputs = identity.get('companions')
    model = {key: value for key, value in identity.items() if key != 'companions'}
    return (scripted.sized_hashes(model, ['archive_sha256', 'model_sha256'], 'model_bytes')
            and isinstance(inputs, dict) and set(inputs) == set(companions(scenario))
            and all(scripted.sized_hashes(value, ['sha256'], 'bytes') for value in inputs.values()))


def read_manifest(document):
    return scripted.read_manifest(document, kind='enemy-actors', row_limit=32,
                                  recipe=recipe, valid_identity=valid_identity)
