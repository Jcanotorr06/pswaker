#!/usr/bin/env python3
"""Resolved repository ownership and deterministic maintained build inputs.

Host commands have one canonical tooling directory. Target recipes and runtime
inputs remain with the platform; consumers never search fallback paths.
"""
import hashlib
import json
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[2]
DECLARATION = 'tools/pswaker/ownership.json'
EXCLUDED_PARTS = {'__pycache__', 'tests', 'evidence'}


class Locations:
    def __init__(self, repository=None):
        self.repository = Path(repository or REPOSITORY).resolve()
        self.declaration = json.loads((self.repository / DECLARATION).read_text())
        self.platform = self.repository / self.declaration['platform']
        self.tools = self.repository / self.declaration['tools']
        self.tests = self.repository / self.declaration['tests']

    def command(self, name):
        groups = [group for group in self.declaration['command_groups'].values()
                  if name in group['files']]
        if len(groups) != 1:
            raise ValueError(f'Command must have exactly one owner: {name}')
        return self.tools / name

    def maintained_inputs(self):
        roots = {self.platform, self.tools}
        for name in ['diagnostic', 'game']:
            group = self.declaration['command_groups'].get(name)
            if not group or not group.get('files'):
                raise ValueError(f'Missing required command input group: {name}')
        for name, group in self.declaration['command_groups'].items():
            for filename in group['files']:
                if not (self.tools / filename).is_file():
                    raise ValueError(f'Missing required {name} input: {self.tools / filename}')
        for name in self.declaration['required_target_directories']:
            if (not (self.platform / name).is_dir() or not any(
                    path.is_file() and path.suffix not in {'.md', '.pyc'}
                    for path in (self.platform / name).rglob('*'))):
                raise ValueError(f'Missing required target input group: {name}')
        for name in self.declaration['required_target_files']:
            if not (self.platform / name).is_file():
                raise ValueError(f'Missing required target input: {name}')
        for name in ['build_inputs.py', 'ownership.json']:
            if not (self.tools / name).is_file():
                raise ValueError(f'Missing required ownership input: {name}')
        paths = {}
        for root in sorted(roots):
            if not root.is_dir():
                raise ValueError(f'Missing required maintained input group: {root}')
            for path in root.rglob('*'):
                relative = path.relative_to(self.repository)
                if (path.is_file() and not EXCLUDED_PARTS.intersection(relative.parts)
                        and path.suffix not in {'.md', '.pyc'}):
                    paths[relative.as_posix()] = path
        return dict(sorted(paths.items()))


def maintained_inputs(repository=None):
    """Map deterministic repository-relative names to their resolved input files."""
    return Locations(repository).maintained_inputs()


def maintained_inventory(repository=None):
    """Map the same maintained input names to SHA-256 content digests."""
    result = {}
    for name, path in maintained_inputs(repository).items():
        with path.open('rb') as stream:
            result[name] = hashlib.file_digest(stream, 'sha256').hexdigest()
    return result



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('location', choices=['platform', 'repository', 'command'])
    parser.add_argument('name', nargs='?')
    args = parser.parse_args()
    locations = Locations()
    if args.location == 'command':
        if not args.name:
            parser.error('command requires a command filename')
        try:
            print(locations.command(args.name))
        except ValueError as error:
            parser.error(str(error))
    else:
        if args.name:
            parser.error('only command accepts a filename')
        print(getattr(locations, args.location))
