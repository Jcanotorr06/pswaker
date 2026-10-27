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

REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / 'tools/pswaker'))
import build_inputs

REPRESENTATIVE_INPUTS = [
    'tools/pswaker/inputs.py', 'tools/pswaker/build-game.sh',
    'platform/ps4/game/storage.cpp', 'platform/ps4/probe/main.cpp',
    'platform/ps4/runtime-preflight/main.cpp',
    'platform/ps4/host-renderer/CMakeLists.txt', 'platform/ps4/ps4.cmake',
    'platform/ps4/sdk.lock.json', 'platform/ps4/provenance/sdk-recipes.json',
    'platform/ps4/LICENSE', 'platform/ps4/frame-pacing-owner.example.json',
    'tools/pswaker/build_inputs.py', 'tools/pswaker/ownership.json',
]
EXCLUDED_RECORDS = [
    'docs/ps4/fixture.json', 'docs/ps4/fixture.md', 'tests/ps4/fixture.cpp',
    'evidence/ps4/fixture.json', 'platform/ps4/fixture.md',
    'platform/ps4/game/__pycache__/fixture.pyc',
    'tools/pswaker/__pycache__/fixture.pyc',
]


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
        with tempfile.TemporaryDirectory(prefix='pswaker checkout ') as directory:
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
            patches = next((root / 'platform/ps4/patches').rglob('*.patch'))
            for name in REPRESENTATIVE_INPUTS + [patches.relative_to(root).as_posix()]:
                with self.subTest(input=name):
                    path = root / name
                    original = path.read_bytes()
                    path.write_bytes(original + b'\n')
                    self.assertNotEqual(before, identity())
                    path.write_bytes(original)
                    self.assertEqual(before, identity())
            shared = root / 'tools/pswaker/build_inputs.py'
            shared.write_text(shared.read_text() + '\n# changed maintained implementation\n')
            after_shared = identity()
            self.assertNotEqual(before, after_shared)
            for name in EXCLUDED_RECORDS:
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
            relocated = root.with_name(root.name + ' relocated checkout')
            root.rename(relocated)
            try:
                cli[1] = str(build_inputs.Locations(relocated).command('package-probe.py'))
                env['PATH'] = str(relocated / 'bin') + os.pathsep + os.environ['PATH']
                self.assertEqual(after_shared, identity())
            finally:
                relocated.rename(root)

    def test_game_identity_records_shared_and_target_inputs(self):
        with tempfile.TemporaryDirectory(prefix='pswaker game identity ') as directory:
            root = Path(directory)
            checkout = root / 'checkout with spaces'
            shutil.copytree(REPOSITORY / 'platform/ps4', checkout / 'platform/ps4')
            shutil.copytree(REPOSITORY / 'tools/pswaker', checkout / 'tools/pswaker',
                            ignore=shutil.ignore_patterns('__pycache__'))
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
            def identity():
                result = subprocess.run([
                    sys.executable, str(build_inputs.Locations(checkout).command('game-build.py')),
                    'identity', str(game), str(platform)], cwd='/',
                    env=dict(os.environ, PATH=str(binary) + os.pathsep + os.environ['PATH']),
                    capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout.strip()
            before = identity()
            recorded = json.loads((game / 'evidence/game-build-inputs.json').read_text())
            self.assertIn('tools/pswaker/build_inputs.py', recorded['port_inputs'])
            self.assertIn('tools/pswaker/ownership.json', recorded['port_inputs'])
            self.assertIn('platform/ps4/game/storage.cpp', recorded['port_inputs'])
            patches = next((checkout / 'platform/ps4/patches').rglob('*.patch'))
            for name in REPRESENTATIVE_INPUTS + [patches.relative_to(checkout).as_posix()]:
                with self.subTest(input=name):
                    path = checkout / name
                    original = path.read_bytes()
                    path.write_bytes(original + b'\n')
                    self.assertNotEqual(before, identity())
                    path.write_bytes(original)
                    self.assertEqual(before, identity())
            for name in EXCLUDED_RECORDS:
                excluded = checkout / name
                excluded.parent.mkdir(parents=True, exist_ok=True)
                excluded.write_text('excluded change')
            self.assertEqual(before, identity())
            self.assertEqual(recorded, json.loads((game / 'evidence/game-build-inputs.json').read_text()))
            relocated = root / 'relocated checkout with spaces'
            checkout.rename(relocated)
            checkout = relocated
            self.assertEqual(before, identity())
            self.assertEqual(recorded, json.loads((game / 'evidence/game-build-inputs.json').read_text()))

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

    def test_missing_required_input_groups_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(REPOSITORY / 'platform/ps4', root / 'platform/ps4')
            shutil.copytree(REPOSITORY / 'tools/pswaker', root / 'tools/pswaker')
            for name in ['game', 'probe', 'host-renderer', 'runtime-preflight',
                         'patches', 'provenance']:
                with self.subTest(group=name):
                    path = root / 'platform/ps4' / name
                    saved = root / 'saved'
                    path.rename(saved)
                    with self.assertRaisesRegex(ValueError, 'Missing required target input group'):
                        build_inputs.maintained_inventory(root)
                    saved.rename(path)
            for name in ['inputs.py', 'game-build.py', 'build_inputs.py', 'ownership.json']:
                with self.subTest(input=name):
                    path = root / 'tools/pswaker' / name
                    saved = root / 'saved'
                    path.rename(saved)
                    with self.assertRaises((ValueError, FileNotFoundError)):
                        build_inputs.maintained_inventory(root)
                    saved.rename(path)
            declaration_path = root / 'tools/pswaker/ownership.json'
            original = declaration_path.read_bytes()
            for name in ['diagnostic', 'game']:
                with self.subTest(command_group=name):
                    declaration = json.loads(original)
                    del declaration['command_groups'][name]
                    declaration_path.write_text(json.dumps(declaration))
                    with self.assertRaisesRegex(ValueError, 'Missing required command input group'):
                        build_inputs.maintained_inventory(root)
            declaration_path.write_bytes(original)

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

    def test_legacy_command_location_cannot_replace_required_tooling(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(REPOSITORY / 'platform/ps4', root / 'platform/ps4')
            shutil.copytree(REPOSITORY / 'tools/pswaker', root / 'tools/pswaker')
            declaration_path = root / 'tools/pswaker/ownership.json'
            declaration = json.loads(declaration_path.read_text())
            group = declaration['command_groups']['diagnostic']
            group['directory'] = 'platform/ps4'
            for name in group['files']:
                (root / 'tools/pswaker' / name).rename(root / 'platform/ps4' / name)
            declaration_path.write_text(json.dumps(declaration))
            with self.assertRaisesRegex(ValueError, 'Missing required diagnostic input'):
                build_inputs.maintained_inventory(root)


if __name__ == '__main__':
    unittest.main()
