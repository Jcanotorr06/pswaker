#!/usr/bin/env python3
"""Collect stock draws and preserve compatible generated/runtime seed descriptions privately."""
import argparse
from contextlib import closing, contextmanager
import hashlib
import json
from pathlib import Path
import re
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tempfile

from disc_image import DiscImage, archive_member, expand, require, validate
from package_artifact import PIPELINE_SEED, digest, inventory, validate_pipeline_seed, write_json
from pipeline_assets import checked_pipeline_asset
from build_inputs import REPOSITORY


DYNAMIC_SCENARIO = 'common-pot-debris-lifecycle-v1'
DYNAMIC_SCRIPT = {'effect_id': 24, 'random_seed': 0, 'max_ticks': 180,
                  'position': [0, 0, 0], 'scale': [1, 1, 1],
                  'color': [255, 255, 255, 255], 'texture_indices': [0, 1]}
DYNAMIC_UNHANDLED = ['model-shards-0x0017', 'actor-lighting-and-collision',
                     'other-pot-textures', 'overlapping-effects', 'other-cameras']


def source_inventory(directory):
    return {p.relative_to(directory).as_posix(): digest(p)
            for p in sorted(directory.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


def check_draw_report(metadata):
    if isinstance(metadata, dict) and metadata.get('scenario') == DYNAMIC_SCENARIO:
        require(metadata.get('schema') == 1 and metadata.get('method') == 'dynamic-effect-draw'
                and metadata.get('resource') == '/res/Particle/common.jpc:0x0018'
                and metadata.get('script') == DYNAMIC_SCRIPT
                and metadata.get('unhandled_states') == DYNAMIC_UNHANDLED,
                'Invalid dynamic collection script or unhandled states')
        check_dynamic_lifetimes(metadata)
        return
    require(isinstance(metadata, dict) and metadata.get('schema') == 1
            and metadata.get('scenario') == 'always-small-pot-stock-v1'
            and metadata.get('method') == 'asset-material-draw'
            and metadata.get('resource') == '/res/Object/Always.arc:bdl/obm_kotubo1.bdl'
            and type(metadata.get('draw_calls')) is int and metadata['draw_calls'] > 0
            and type(metadata.get('materials')) is int and metadata['materials'] > 0,
            'Invalid model collection or no actual material draws')


def check_dynamic_lifetimes(metadata):
    variations = metadata.get('variations')
    require(isinstance(variations, list) and len(variations) == 2,
            'Invalid dynamic variations')
    variations = metadata['variations']
    totals = dict(frames=0, draw_calls=0, pipeline_lookups=0)
    for texture, variation in enumerate(variations):
        require(isinstance(variation, dict) and type(variation.get('texture_index')) is int
                and variation['texture_index'] == texture,
                'Invalid dynamic texture variation')
        steps = variation.get('steps')
        require(isinstance(steps, list) and 1 < len(steps) <= DYNAMIC_SCRIPT['max_ticks'],
                'Invalid dynamic lifetime length')
        steps = variation['steps']
        peak = draws = lookups = 0
        for tick, step in enumerate(steps, 1):
            require(isinstance(step, dict) and type(step.get('tick')) is int and step['tick'] == tick
                    and all(type(step.get(name)) is int and step[name] >= 0
                            for name in ['particles', 'emitters', 'draw_calls', 'pipeline_lookups']),
                    'Invalid dynamic lifetime step')
            require(step['emitters'] == (0 if tick == len(steps) else 1),
                    'Invalid dynamic emitter transition')
            configurations = step.get('configurations')
            require(isinstance(configurations, list) and all(
                isinstance(key, dict) and set(key) == {'type', 'hash'}
                and type(key['type']) is int and key['type'] in [0, 1]
                and type(key['hash']) is int and -(2**63) <= key['hash'] < 2**63
                for key in configurations), 'Invalid dynamic description mapping')
            configurations = step['configurations']
            require(len({(key['type'], key['hash']) for key in configurations}) == len(configurations)
                    and bool(configurations) == (step['pipeline_lookups'] > 0)
                    and len(configurations) <= step['pipeline_lookups'],
                    'Incomplete dynamic description mapping')
            peak = max(peak, step['particles'])
            draws += step['draw_calls']
            lookups += step['pipeline_lookups']
        require(peak > 0 and draws > 0 and lookups > 0
                and steps[-1]['particles'] == steps[-1]['emitters'] == 0,
                'Incomplete dynamic particle lifetime or no actual draws')
        totals['frames'] += len(steps)
        totals['draw_calls'] += draws
        totals['pipeline_lookups'] += lookups
    require(all(type(metadata.get(name)) is int and metadata[name] == value
                for name, value in totals.items()), 'Invalid dynamic collection totals')


def check_dynamic_mapping(metadata, generated):
    if metadata['method'] == 'dynamic-effect-draw':
        mapped = {(key['type'], key['hash']) for variation in metadata['variations']
                  for step in variation['steps'] for key in step['configurations']}
        require(mapped == set(generated), 'Incomplete dynamic description-to-state mapping')


def configuration_states(metadata, key):
    if metadata['method'] != 'dynamic-effect-draw':
        return {}
    return {'states': [{'texture_index': variation['texture_index'],
                        'ticks': [step['tick'] for step in variation['steps']
                                  if {'type': key[0], 'hash': key[1]} in step['configurations']]}
                       for variation in metadata['variations']
                       if any({'type': key[0], 'hash': key[1]} in step['configurations']
                              for step in variation['steps'])]}


def run_logged(command, directory, log, *, timeout=None):
    with log.open('w', encoding='utf-8') as stream:
        subprocess.run(command, cwd=directory, check=True, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)


@contextmanager
def collection_attempt(output):
    with tempfile.TemporaryDirectory(prefix='.model-collection-', dir=output.parent) as folder:
        work = Path(folder)
        try:
            yield work
        except BaseException:
            # Failed native runs are evidence too. Retain logs and partial files
            # at the requested private path; a retry must choose a new path.
            shutil.copytree(work, output)
            raise
        else:
            work.rename(output)


def build_collector(args):
    require(not args.output.exists(), 'Output already exists; retain the earlier build record')
    require(not args.output.resolve().is_relative_to(REPOSITORY), 'Collector builds must remain private')
    prepared_path = args.game_root / 'evidence/game-inputs.json'
    prepared = json.loads(prepared_path.read_text())
    trees = {**{name: args.game_root / 'src' / name for name in prepared['prepared_sources']},
             'aurora': args.game_root / 'src/aurora', 'platform': args.game_root / 'src/platform',
             'stub_headers': args.game_root / 'assets/GZLE01'}
    expected = {**prepared['prepared_sources'], **{k: prepared[k] for k in ['aurora', 'platform', 'stub_headers']}}
    require(all(source_inventory(tree) == expected[name] for name, tree in trees.items()),
            'Prepared game source changed; use a verified prepared game root')
    maintained = source_inventory(REPOSITORY / 'platform/ps4/host-renderer')
    adapters = {name: digest(REPOSITORY / 'platform/ps4/game' / name)
                for name in ['stock-textures.cpp', 'frame-pacing.hpp', 'game-platform.hpp']}
    args.output.mkdir(parents=True)
    command = ['cmake', '-S', str(REPOSITORY / 'platform/ps4/host-renderer'), '-B', str(args.build_directory),
               '-G', 'Ninja', '-DCMAKE_C_COMPILER=/usr/bin/clang-21', '-DCMAKE_CXX_COMPILER=/usr/bin/clang++-21',
               '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON',
               '-DPSWAKER_MODEL_COLLECTOR=ON', '-DPLATFORM_ROOT=' + str(args.platform_root),
               '-DHOST_ROOT=' + str(args.host_root), '-DPSWAKER_GAME_ROOT=' + str(args.game_root)]
    commands = [command, ['cmake', '--build', str(args.build_directory), '--target', 'switchwaker', '--parallel', '8']]
    for index, command in enumerate(commands):
        run_logged(command, REPOSITORY, args.output / f'build-{index}.log')
    # Same complete default objects, versions, field offsets and hash width,
    # compiled with each renderer's actual flags. Full draw descriptions are
    # separately compared against the compatible runtime baseline by prepare.
    contract_source = REPOSITORY / 'platform/ps4/host-renderer/model-contract.cpp'
    for label, database, suffix in [
        ('ps4', args.game_root / 'build/compile_commands.json', 'pipeline-seed-abi.cpp'),
        ('host', args.build_directory / 'compile_commands.json', 'model-contract.cpp'),
    ]:
        entry = next(row for row in json.loads(database.read_text()) if row['file'].endswith(suffix))
        command = shlex.split(entry['command'])
        command[command.index('-o') + 1] = str(args.output / f'{label}-contract.o')
        command[command.index('-c') + 1] = str(contract_source)
        run_logged(command, Path(entry['directory']), args.output / f'{label}-contract.log')
        extraction = ['llvm-objcopy-21', '--dump-section',
                      '.pswaker_pipeline_contract=' + str(args.output / f'{label}-contract.bin'),
                      str(args.output / f'{label}-contract.o'), str(args.output / f'{label}-extracted.o')]
        run_logged(extraction, REPOSITORY, args.output / f'{label}-extract.log')
        commands.extend([command, extraction])
    require((args.output / 'host-contract.bin').read_bytes() == (args.output / 'ps4-contract.bin').read_bytes(),
            'Collector and selected PS4 pipeline representations differ')
    require(all(source_inventory(tree) == expected[name] for name, tree in trees.items())
            and maintained == source_inventory(REPOSITORY / 'platform/ps4/host-renderer')
            and all(digest(REPOSITORY / 'platform/ps4/game' / name) == sha for name, sha in adapters.items()),
            'Collector sources changed while building; retain this attempt and rebuild')
    shutil.copyfile(args.build_directory / 'switchwaker', args.output / 'collector')
    (args.output / 'collector').chmod(0o700)
    libraries = re.findall(r'(?:=>\s*)?(/\S+)', subprocess.check_output(['ldd', str(args.output / 'collector')], text=True))
    report = {'schema': 1, 'binary_sha256': digest(args.output / 'collector'),
              'prepared_inputs_sha256': digest(prepared_path), 'sources': prepared['sources'],
              'renderer_sources_sha256': hashlib.sha256(json.dumps(expected['aurora'], sort_keys=True).encode()).hexdigest(),
              'collector_sources': maintained, 'adapter_sources': adapters, 'commands': commands,
              'build_tool_sha256': digest(Path(__file__)),
              'runtime_libraries': {name: digest(Path(name)) for name in libraries},
              'contract_sha256': digest(args.output / 'ps4-contract.bin'),
              'contract_bytes': (args.output / 'ps4-contract.bin').stat().st_size,
              'host_dependencies': {name: digest(args.host_root / name) for name in [
                  'dawn/src/dawn/native/libwebgpu_dawn.a', 'sdl/libSDL3.a']},
              'compiler': subprocess.check_output(['/usr/bin/clang++-21', '--version'], text=True)}
    write_json(args.output / 'collector-build.json', report)
    return report


def collect(args):
    require(not args.output.exists(), 'Output already exists; retain the earlier collection')
    require(not args.output.resolve().is_relative_to(REPOSITORY), 'Collections must remain private')
    require(not any(args.output.is_relative_to(source) for source in [args.baseline, args.collector]),
            'Collection output must remain outside source assets and collector builds')
    build = json.loads((args.collector / 'collector-build.json').read_text())
    binary = args.collector / 'collector'
    require(digest(binary) == build['binary_sha256'], 'Collector binary differs from its build record')
    require(all(digest(Path(name)) == sha for name, sha in build.get('runtime_libraries', {}).items()),
            'Collector runtime libraries changed; rebuild and retain a new build record')
    require(all(digest(args.collector / f'{label}-contract.bin') == build['contract_sha256']
                for label in ['host', 'ps4']), 'Collector/PS4 contract witness differs from its build record')
    checked_pipeline_asset(args.baseline)
    image = validate(args.image)
    image_sha = image['sha256']
    with args.image.open('rb') as stream:
        disc = DiscImage(stream)
        files = disc.files(disc.read(0, 0x440, 'header'))
        if args.scenario == DYNAMIC_SCENARIO:
            offset, size = files['res/Particle/common.jpc']
            particles = disc.read(offset, size, 'common particles')
            resources = {'particle_sha256': hashlib.sha256(particles).hexdigest(), 'particle_bytes': len(particles)}
        else:
            offset, size = files['res/Object/Always.arc']
            archive = disc.read(offset, size, 'Always archive')
            model = archive_member(expand(archive), 'bdl/obm_kotubo1.bdl')
            resources = {'archive_sha256': hashlib.sha256(archive).hexdigest(),
                         'model_sha256': hashlib.sha256(model).hexdigest(), 'model_bytes': len(model)}
    baseline_before = inventory(args.baseline)
    collector_before = inventory(args.collector)
    with collection_attempt(args.output) as work:
        command = ['xvfb-run', '-a', str(binary), str(args.image), str(args.baseline)]
        if args.scenario != 'always-small-pot-stock-v1':
            command.append(args.scenario)
        # The isolated collector has no game boot or card/settings paths.
        run_logged(command, work, work / 'collector.log', timeout=180)
        native = json.loads((work / 'collection.json').read_text())
        check_draw_report(native)
        require(native['scenario'] == args.scenario, 'Collector returned a different scenario')
        seed_command = [sys.executable, str(REPOSITORY / 'tools/pswaker/complete-package.py'), 'pipeline-seed',
                        str(work / 'observed.db'), '--output', str(work / 'assets')]
        run_logged(seed_command, REPOSITORY, work / 'snapshot.log')
        # Confirm every observation was also recorded by Aurora's unmodified
        # synchronous recorder. Never import the preloaded baseline as observed.
        runtime_command = seed_command[:3] + [str(work / 'cache/pipeline_cache.db'), '--output', str(work / 'recorded')]
        run_logged(runtime_command, REPOSITORY, work / 'recorder-snapshot.log')
        observed_rows, recorded_rows = records(work / 'assets'), records(work / 'recorded')
        check_dynamic_mapping(native, observed_rows)
        baseline_rows = records(args.baseline)
        require(all(key in recorded_rows and row[2:5] == recorded_rows[key][2:5]
                    for key, row in observed_rows.items()), 'Observed descriptions differ from the normal recorder')
        require(all(key in recorded_rows and row[2:5] == recorded_rows[key][2:5]
                    for key, row in baseline_rows.items()), 'Known runtime descriptions changed in the host round trip')
        require(native.get('runtime_identity_verified_rows') == len(baseline_rows),
                'Known runtime identity comparison is incomplete')
        native.update(collector={'sha256': build['binary_sha256'],
                                 'build_sha256': digest(args.collector / 'collector-build.json')},
                      image_sha256=image_sha, image_validation=image, resources=resources,
                      commands=[command, seed_command, runtime_command],
                      recorder_verified_rows=len(observed_rows), contract_sha256=build['contract_sha256'],
                      baseline_roundtrip_rows=len(baseline_rows),
                      seed_sha256=digest(work / 'assets' / PIPELINE_SEED))
        native['collection_tool_sha256'] = digest(Path(__file__))
        require(digest(args.image) == image_sha and inventory(args.baseline) == baseline_before
                and inventory(args.collector) == collector_before,
                'Private inputs changed during collection')
        write_json(work / 'collection.json', native)
    return native


def records(directory):
    with closing(sqlite3.connect((directory / PIPELINE_SEED).resolve().as_uri()
                                + '?mode=ro&immutable=1', uri=True)) as db:
        return {(row[0], row[1]): row for row in db.execute(
            'SELECT type, hash, config_version, config_size, config, first_frame_used '
            'FROM pipeline_cache ORDER BY type, hash')}


def additional_records(existing, sources):
    combined = dict(existing)
    for source in sources:
        for key, row in sorted(source.items()):
            if key in combined:
                require(combined[key][2:5] == row[2:5],
                        'Same pipeline identity has conflicting description bytes')
            else:
                combined[key] = row
    return {key: row for key, row in combined.items() if key not in existing}


def write_combined_seed(baseline, original, additions, manifests, assets):
    assets.mkdir()
    shutil.copyfile(baseline / PIPELINE_SEED, assets / PIPELINE_SEED)
    if additions:
        with closing(sqlite3.connect(assets / PIPELINE_SEED)) as db, db:
            db.executemany('INSERT INTO pipeline_cache VALUES(?,?,?,?,?,?)',
                           [additions[key] for key in sorted(additions)])
            details = validate_pipeline_seed(db)
        write_json(assets / 'pipeline-seed.json', {
            'schema': 1, 'installed_path': '/app0/' + PIPELINE_SEED,
            'source_files': {f'{label}:{name}': source
                             for label, manifest in [('baseline', original), *manifests]
                             for name, source in manifest['source_files'].items()},
            **details, 'bytes': (assets / PIPELINE_SEED).stat().st_size,
            'sha256': digest(assets / PIPELINE_SEED)})
    else:
        shutil.copyfile(baseline / 'pipeline-seed.json', assets / 'pipeline-seed.json')
    return checked_pipeline_asset(assets)


def correct_seed(baseline, snapshots, output):
    require(not output.exists(), 'Output already exists; retain it and choose a new directory')
    require(not output.is_relative_to(REPOSITORY), 'Corrected seeds must remain outside the repository')
    sources = [('baseline', baseline), *[(f'runtime-{index}', directory)
                                       for index, directory in enumerate(snapshots, 1)]]
    require(not any(output.is_relative_to(directory) for _, directory in sources),
            'Seed output must remain outside source assets')
    inputs = {label: inventory(directory) for label, directory in sources}
    manifests = {label: checked_pipeline_asset(directory) for label, directory in sources}
    descriptions = {label: records(directory) for label, directory in sources}
    existing = descriptions['baseline']
    runtime = {label: rows for label, rows in descriptions.items() if label != 'baseline'}
    additions = additional_records(existing, runtime.values())
    with tempfile.TemporaryDirectory(prefix='.runtime-seed-', dir=output.parent) as folder:
        work = Path(folder)
        seed = write_combined_seed(baseline, manifests['baseline'], additions,
                                   [(label, manifests[label]) for label in runtime], work / 'assets')
        report = {
            'schema': 1, 'provenance': 'runtime-capture-correction',
            'baseline': manifests['baseline'], 'snapshots': {label: manifests[label] for label in runtime},
            'baseline_rows': len(existing), 'runtime_union_rows': len(set().union(*runtime.values())),
            'added_rows': len(additions), 'seed': seed, 'input_files': inputs,
            'source_path_attribution': 'unresolved', 'corrected_candidate_physical_verification': False,
            'additions': [{'type': key[0], 'hash': key[1], 'version': row[2], 'bytes': row[3],
                           'description_sha256': hashlib.sha256(row[4]).hexdigest(),
                           'sources': [label for label, rows in runtime.items() if key in rows],
                           'first_frame_used_by_source': {label: rows[key][5] for label, rows in runtime.items()
                                                         if key in rows}}
                          for key, row in sorted(additions.items())]}
        require(all(inventory(directory) == inputs[label] for label, directory in sources),
                'Correction inputs changed during preparation')
        write_json(work / 'correction-report.json', report)
        work.rename(output)
    return report


def prepare(collection, baseline, output):
    require(not output.exists(), 'Output already exists; retain it and choose a new directory')
    require(not output.is_relative_to(REPOSITORY), 'Generated seeds must remain outside the repository')
    require(not any(output.is_relative_to(source) for source in [collection, baseline]),
            'Seed output must remain outside source assets')
    inputs = {'baseline': inventory(baseline), 'collection': inventory(collection)}
    metadata = json.loads((collection / 'collection.json').read_text(encoding='utf-8'))
    check_draw_report(metadata)
    collector = metadata.get('collector')
    require(isinstance(collector, dict) and all(
        isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value)
        for value in [collector.get('sha256'), collector.get('build_sha256'), metadata.get('image_sha256')]),
        'Missing or invalid collector identity and private input identity')
    original = checked_pipeline_asset(baseline)
    collected = checked_pipeline_asset(collection / 'assets')
    require(metadata.get('seed_sha256') == collected['sha256'],
            'Collected seed differs from its collection attribution')
    existing, generated = records(baseline), records(collection / 'assets')
    check_dynamic_mapping(metadata, generated)
    additions = additional_records(existing, [generated])
    with tempfile.TemporaryDirectory(prefix='.model-seed-', dir=output.parent) as folder:
        work = Path(folder)
        seed = write_combined_seed(baseline, original, additions, [('generated', collected)], work / 'assets')
        report = {'schema': 1, 'provenance': metadata['method'], 'collection': metadata,
                  'baseline': original, 'generated': collected, 'baseline_rows': len(existing),
                  'collected_rows': len(generated), 'baseline_covered_rows': len(generated) - len(additions),
                  'new_rows': len(additions), 'seed': seed,
                  'mapping': [{'type': key[0], 'hash': key[1],
                               'description_sha256': hashlib.sha256(row[4]).hexdigest(),
                               'scenario': metadata['scenario'], 'baseline_covered': key in existing,
                               **configuration_states(metadata, key)}
                              for key, row in sorted(generated.items())],
                  'input_files': inputs, 'physical_verification': False}
        require(inventory(baseline) == inputs['baseline'] and inventory(collection) == inputs['collection'],
                'Collection inputs changed during preparation')
        write_json(work / 'collection-report.json', report)
        work.rename(output)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    command = commands.add_parser('correct', help='Supplement a seed with validated runtime snapshot assets')
    command.add_argument('--baseline', type=lambda value: Path(value).resolve(), required=True)
    command.add_argument('--runtime-snapshot', type=lambda value: Path(value).resolve(),
                         action='append', required=True)
    command.add_argument('--output', type=lambda value: Path(value).resolve(), required=True)
    command = commands.add_parser('prepare')
    command.add_argument('--collection', type=Path, required=True)
    command.add_argument('--baseline', type=Path, required=True)
    command.add_argument('--output', type=Path, required=True)
    command = commands.add_parser('build')
    for name in ['game-root', 'platform-root', 'host-root', 'build-directory', 'output']:
        command.add_argument('--' + name, type=lambda value: Path(value).resolve(), required=True)
    command = commands.add_parser('collect')
    command.add_argument('--scenario', choices=['always-small-pot-stock-v1', DYNAMIC_SCENARIO],
                         default='always-small-pot-stock-v1')
    for name in ['collector', 'image', 'baseline', 'output']:
        command.add_argument('--' + name, type=lambda value: Path(value).resolve(), required=True)
    args = parser.parse_args()
    try:
        if args.command == 'build':
            build_collector(args)
        elif args.command == 'collect':
            collect(args)
        elif args.command == 'correct':
            report = correct_seed(args.baseline, args.runtime_snapshot, args.output)
            print(json.dumps({'rows': report['seed']['rows'], 'added_rows': report['added_rows']}))
        else:
            report = prepare(args.collection.resolve(), args.baseline.resolve(), args.output.resolve())
            print(json.dumps({'rows': report['seed']['rows'], 'new_rows': report['new_rows']}))
        return 0
    except (OSError, ValueError, KeyError, TypeError, StopIteration, sqlite3.Error,
            subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        print(f'model collection: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
