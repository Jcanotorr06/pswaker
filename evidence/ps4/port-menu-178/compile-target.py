"""Compile changed target units with a prepared game's pinned compile commands.

Run from the repository root. No prepared inputs or build outputs are modified.
This is a target compilation check, not physical PS4 acceptance.
"""
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

game = Path(sys.argv[1]).expanduser().resolve()
source = Path.cwd() / 'platform/ps4/game'
rows = json.loads((game / 'build/compile_commands.json').read_text())
with tempfile.TemporaryDirectory(prefix='pswaker-port-menu-target-') as output:
    for name in ['main.cpp', 'controls.cpp']:
        row = next(row for row in rows if row['file'].endswith('/' + name)
                   and 'pswaker_entry' in row['command'])
        old = str(Path(row['file']).parent)
        args = shlex.split(row['command'].replace(old, str(source)))
        args[args.index('-o') + 1] = str(Path(output) / (name + '.o'))
        result = subprocess.run(args, cwd=row['directory'])
        print(f'{name}: target object compile exit {result.returncode}', flush=True)
        if result.returncode:
            sys.exit(result.returncode)
