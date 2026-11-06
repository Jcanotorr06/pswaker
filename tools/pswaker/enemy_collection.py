"""Finite enemy/boss recipes; shared resources never imply unexercised actors."""
from asset_inventory import sha256
from disc_image import require
import particle_collection as particle
import scripted_collection as scripted


# Every actor recipe enters the same game resource setup, so each binds the
# freeze material and toon images it consumes along with its own members.
SHARED_INPUTS = ['/res/Object/Always.arc:bmtm/ice.bmt', '/res/Object/Always.arc:btk/ice.btk',
                 '/res/Object/System.arc:dat/toon.bti', '/res/Object/System.arc:dat/toonex.bti']
ACTORS = {
    'enemy-bokoblin-materials-v1': (
        '/res/Object/Bk.arc:bdlm/bk.bdl',
        ['body-stock', 'body-green', 'body-pink', 'body-frozen', 'body-restored', 'weapon-club', 'weapon-sword'],
        ['bmt/green.bmt', 'bmt/pink.bmt', 'bmt/bk_boko.bmt', 'bmt/bk_ken.bmt', 'bmd/bk_kb.bmd']),
    'enemy-chuchu-states-v1': (
        '/res/Object/Cc.arc:bmdm/cc.bmd',
        ['body', 'stone-first', 'stone-second', 'puddle', 'frozen'],
        ['bdlm/cc_iwa.bdl', 'bdlm/cc_beta.bdl', 'brk/cc.brk', 'brk/cc_beta.brk', 'brk/cc_iwa01.brk',
         'brk/cc_iwa02.brk', 'btk/cc_iwa01.btk', 'btk/cc_iwa02.btk']),
    'enemy-peahat-freeze-v1': (
        '/res/Object/Ph.arc:bdlm/phb.bdl',
        ['stock', 'frozen', 'restored'],
        ['bdlm/php.bdl']),
    'boss-jalhalla-visibility-v1': (
        '/res/Object/Bpw.arc:bdlm/bpw.bdl',
        ['default', 'light-stun', 'curse-start', 'curse-end', 'light-freeze', 'possession'],
        ['bdlm/bpw_kan1.bdl', 'brk/default.brk', 'brk/hit.brk', 'brk/noroi_s1.brk', 'brk/noroi_e1.brk',
         'brk/hiraru1.brk']),
    'boss-gohma-defeat-v1': (
        '/res/Object/Btd.arc:bmdm/sotai.bmd',
        ['phase-one', 'phase-two', 'defeat'],
        ['bmdm/btd.bmd', 'btk/btd.btk', 'brk/btd.brk', 'btk/sotai.btk', 'brk/sotai.brk', 'bmt/deada.bmt',
         'brk/deada.brk', 'btk/deada.btk']),
    'boss-puppet-ganon-water-v1': (
        '/res/Object/Bgn.arc:bdlm/r0e_a.bdl',
        ['water-surface', 'water-mask', 'water-combined'],
        []),
}
EFFECTS = {'enemy-death-large-v1': '/res/Particle/common.jpc:0x0014+0x0013+0x0015+0x0016',
           'enemy-death-small-v1': '/res/Particle/common.jpc:0x043c+0x043d+0x043e'}
SCENARIOS = [*ACTORS, *EFFECTS]
ACTOR_GAPS = ['actor-process-and-ai', 'skeletal-animation', 'stage-lighting-and-fog', 'shadows', 'other-cameras']


def recipe(scenario):
    require(scenario in SCENARIOS, 'Unsupported enemy recipe')
    if scenario in EFFECTS:
        resource = EFFECTS[scenario]
        return {'resource': resource, 'script': {**particle.script(resource), 'setup': scenario}}
    resource, states, _ = ACTORS[scenario]
    return {'resource': resource, 'script': {'states': states, 'frames_per_state': 1}}


def companions(scenario):
    resource, _, members = ACTORS[scenario]
    archive = resource.split(':')[0]
    return [f'{archive}:{member}' for member in members] + SHARED_INPUTS


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
        return (isinstance(identity, dict) and set(identity) == {'particle_sha256', 'particle_bytes'}
                and sha256(identity.get('particle_sha256'))
                and type(identity.get('particle_bytes')) is int and identity['particle_bytes'] > 0)
    if not (isinstance(identity, dict) and set(identity) == {'archive_sha256', 'model_sha256', 'model_bytes', 'companions'}
            and all(sha256(identity.get(k)) for k in ['archive_sha256', 'model_sha256'])
            and type(identity.get('model_bytes')) is int and identity['model_bytes'] > 0):
        return False
    inputs = identity.get('companions')
    return (isinstance(inputs, dict) and set(inputs) == set(companions(scenario))
            and all(isinstance(value, dict) and set(value) == {'sha256', 'bytes'} and sha256(value.get('sha256'))
                    and type(value.get('bytes')) is int and value['bytes'] > 0 for value in inputs.values()))


def read_manifest(document):
    return scripted.read_manifest(document, kind='enemy-actors', row_limit=32,
                                  recipe=recipe, valid_identity=valid_identity)
