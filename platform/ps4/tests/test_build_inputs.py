"""Maintained input ownership through its public inventory and existing identity seams."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
import shutil
import tempfile
import unittest

REPOSITORY = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPOSITORY / 'tools/pswaker'))
import build_inputs


class BuildInputTests(unittest.TestCase):
    def test_inventory_preserves_maintained_coverage_and_excludes_records(self):
        spec = importlib.util.spec_from_file_location(
            'build_inputs', REPOSITORY / 'tools/pswaker/build_inputs.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        inputs = module.maintained_inputs()
        self.assertIn('platform/ps4/game/storage.cpp', inputs)
        self.assertIn('platform/ps4/provenance/sdk-recipes.json', inputs)
        self.assertIn('platform/ps4/frame-pacing-owner.example.json', inputs)
        self.assertIn('tools/pswaker/build_inputs.py', inputs)
        self.assertIn('tools/pswaker/ownership.json', inputs)
        self.assertFalse(any('/evidence/' in name or '/tests/' in name or
                             name.endswith(('.md', '.pyc')) or '__pycache__' in name
                             for name in inputs))
        self.assertEqual(list(inputs), sorted(inputs))

    def test_diagnostic_identity_tracks_shared_ownership(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(REPOSITORY / 'platform/ps4', root / 'platform/ps4',
                            ignore=shutil.ignore_patterns('tests', 'evidence', '__pycache__'))
            shutil.copytree(REPOSITORY / 'tools/pswaker', root / 'tools/pswaker',
                            ignore=shutil.ignore_patterns('__pycache__'))
            binary = root / 'bin'
            binary.mkdir()
            for name in ['clang-21', 'cmake', 'ninja', 'dotnet']:
                tool = binary / name
                tool.write_text('#!/bin/sh\nprintf "fixture tool 1\\n"\n')
                tool.chmod(0o755)
            env = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ['PATH'])
            cli = [sys.executable, str(build_inputs.Locations(root).command('package-probe.py')),
                   str(root / 'external-build'), '--identity-only']
            def identity():
                result = subprocess.run(cli, env=env, cwd='/', capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout.strip()
            before = identity()
            shared = root / 'tools/pswaker/build_inputs.py'
            shared.write_text(shared.read_text() + '\n# changed maintained implementation\n')
            after_shared = identity()
            self.assertNotEqual(before, after_shared)
            for name in ['platform/ps4/README.md', 'platform/ps4/tests/fixture.cpp',
                         'platform/ps4/evidence/log.json', 'tools/pswaker/__pycache__/fixture.pyc']:
                excluded = root / name
                excluded.parent.mkdir(parents=True, exist_ok=True)
                excluded.write_text('excluded change')
            self.assertEqual(after_shared, identity())
            added = root / 'platform/ps4/game/new-runtime.cpp'
            added.write_text('new maintained source')
            after_addition = identity()
            self.assertNotEqual(after_shared, after_addition)
            added.rename(added.with_name('renamed-runtime.cpp'))
            self.assertNotEqual(after_addition, identity())
            added.with_name('renamed-runtime.cpp').unlink()
            self.assertEqual(after_shared, identity())
            relocated = root.with_name(root.name + '-relocated')
            root.rename(relocated)
            try:
                cli[1] = str(build_inputs.Locations(relocated).command('package-probe.py'))
                env['PATH'] = str(relocated / 'bin') + os.pathsep + os.environ['PATH']
                self.assertEqual(after_shared, identity())
            finally:
                relocated.rename(root)

    def test_game_identity_records_shared_and_target_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            game, platform = root / 'prepared-game', root / 'prepared-platform'
            (game / 'evidence').mkdir(parents=True)
            for name in ['switchwaker', 'aurora', 'platform']:
                (game / 'src' / name).mkdir(parents=True)
            (game / 'assets/GZLE01').mkdir(parents=True)
            (game / 'evidence/game-inputs.json').write_text(json.dumps({
                'prepared_sources': {'switchwaker': {}}, 'stub_headers': {},
                'aurora': {}, 'platform': {}}))
            for name in ['build/dawn/src/dawn/native/libwebgpu_dawn.a', 'build/sdl3/libSDL3.a']:
                archive = platform / name
                archive.parent.mkdir(parents=True)
                archive.write_bytes(b'fixture archive')
            binary = root / 'bin'
            binary.mkdir()
            for name in ['clang++-21', 'cmake', 'ninja']:
                tool = binary / name
                tool.write_text('#!/bin/sh\nprintf "fixture tool 1\\n"\n')
                tool.chmod(0o755)
            result = subprocess.run([sys.executable, str(build_inputs.Locations().command('game-build.py')),
                                     'identity', str(game), str(platform)], cwd='/',
                                    env=dict(os.environ, PATH=str(binary) + os.pathsep + os.environ['PATH']),
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            recorded = json.loads((game / 'evidence/game-build-inputs.json').read_text())
            self.assertIn('tools/pswaker/build_inputs.py', recorded['port_inputs'])
            self.assertIn('tools/pswaker/ownership.json', recorded['port_inputs'])
            self.assertIn('platform/ps4/game/storage.cpp', recorded['port_inputs'])

    def test_missing_required_target_recipe_is_rejected(self):
        spec = importlib.util.spec_from_file_location(
            'build_inputs', REPOSITORY / 'tools/pswaker/build_inputs.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(REPOSITORY / 'platform/ps4', root / 'platform/ps4',
                            ignore=shutil.ignore_patterns('tests', 'evidence', '__pycache__'))
            shutil.copytree(REPOSITORY / 'tools/pswaker', root / 'tools/pswaker',
                            ignore=shutil.ignore_patterns('__pycache__'))
            (root / 'platform/ps4/sdk.lock.json').unlink()
            with self.assertRaisesRegex(ValueError, 'Missing required target input: sdk.lock.json'):
                module.maintained_inventory(root)

    def test_provenance_records_shared_inventory_without_losing_host_closure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'evidence').mkdir()
            (root / 'evidence/sdk-rebuilt-archives.sha256').write_text('fixture archive digest\n')
            binary = root / 'bin'
            binary.mkdir()
            for name in ['git', 'clang-21', 'cmake', 'ninja', 'dotnet', 'dpkg-query']:
                tool = binary / name
                tool.write_text('#!/bin/sh\nprintf "fixture tool 1\\n"\n')
                tool.chmod(0o755)
            result = subprocess.run([sys.executable,
                                     str(build_inputs.Locations().command('capture-inputs.py')), str(root)],
                                    cwd='/', capture_output=True, text=True,
                                    env=dict(os.environ, PATH=str(binary) + os.pathsep + os.environ['PATH']))
            self.assertEqual(result.returncode, 0, result.stderr)
            closure = json.loads((root / 'evidence/input-closure.json').read_text())
            inventory = {row['path']: row['sha256'] for row in closure['maintained_inputs']}
            self.assertIn('tools/pswaker/build_inputs.py', inventory)
            self.assertIn('tools/pswaker/ownership.json', inventory)
            self.assertIn('platform/ps4/provenance/sdk-recipes.json', inventory)
            self.assertEqual(closure['mesa_revision'], 'fixture tool 1')
            self.assertEqual(closure['host_packages'], 'fixture tool 1')
            self.assertEqual(closure['rebuilt_sdk_archives'], 'fixture archive digest\n')

    def test_command_groups_can_move_independently_without_fallback_locations(self):
        for group_name in ['diagnostic', 'game']:
            with self.subTest(group=group_name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                shutil.copytree(REPOSITORY / 'platform/ps4', root / 'platform/ps4',
                                ignore=shutil.ignore_patterns('tests', 'evidence', '__pycache__'))
                shutil.copytree(REPOSITORY / 'tools/pswaker', root / 'tools/pswaker',
                                ignore=shutil.ignore_patterns('__pycache__'))
                declaration_path = root / 'tools/pswaker/ownership.json'
                declaration = json.loads(declaration_path.read_text())
                group = declaration['command_groups'][group_name]
                old_directory = root / group['directory']
                group['directory'] = 'tools/pswaker'
                for name in group['files']:
                    if old_directory != root / 'tools/pswaker':
                        (old_directory / name).rename(root / 'tools/pswaker' / name)
                declaration_path.write_text(json.dumps(declaration))
                locations = build_inputs.Locations(root)
                inputs = locations.maintained_inputs()
                name = group['files'][0]
                self.assertEqual(locations.command(name), root / 'tools/pswaker' / name)
                self.assertIn('tools/pswaker/' + name, inputs)
                self.assertNotIn('platform/ps4/' + name, inputs)
                other = declaration['command_groups']['game' if group_name == 'diagnostic' else 'diagnostic']
                self.assertIn(other['directory'] + '/' + other['files'][0], inputs)


if __name__ == '__main__':
    unittest.main()
