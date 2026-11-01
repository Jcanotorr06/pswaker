"""Semantic PS4 prompt contract: hosted C++, no game data or GPU."""
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
import zlib


ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / 'platform/ps4/game'
SIZE = 64


def write_png(raw, target):
    """Convert one straight-RGBA preview from the art check into a PNG."""
    rows = b''.join(b'\0' + raw[y * SIZE * 4:(y + 1) * SIZE * 4] for y in range(SIZE))

    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data +
                struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff))
    target.write_bytes(b'\x89PNG\r\n\x1a\n' +
                       chunk(b'IHDR', struct.pack('>IIBBBBB', SIZE, SIZE, 8, 6, 0, 0, 0)) +
                       chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b''))


class CoverageInventoryTests(unittest.TestCase):
    def test_inventory_records_only_identifiers_and_status(self):
        inventory = json.loads((ROOT / 'platform/ps4/prompt-coverage.json').read_text())
        self.assertEqual(inventory['schema'], 1)
        ids = [entry['id'] for entry in inventory['entries']]
        self.assertEqual(len(ids), len(set(ids)))
        for entry in inventory['entries']:
            self.assertEqual(set(entry), {'id', 'status'})
            self.assertIn(entry['status'], {'converted', 'text-fallback', 'unresolved'})


@unittest.skipUnless(shutil.which('clang++-21'), 'Linux Clang 21 required')
class PromptTests(unittest.TestCase):
    def run_check(self, test, *sources):
        with tempfile.TemporaryDirectory(prefix='pswaker-prompts-') as directory:
            binary = Path(directory) / 'check'
            build = subprocess.run([
                'clang++-21', '-std=c++23', '-Wall', '-Wextra', '-Werror',
                '-I', str(GAME), '-I', str(GAME / 'include'),
                str(ROOT / 'tests/ps4' / test), *(str(GAME / source) for source in sources),
                '-o', str(binary)], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=60)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_public_resolver_contract(self):
        self.run_check('prompts.cpp', 'prompts.cpp', 'controls-config.cpp')

    def test_message_picture_adapter(self):
        self.run_check('message-prompts.cpp', 'message-prompts.cpp', 'prompt-textures.cpp', 'prompt-art.cpp',
                       'prompts.cpp', 'controls-config.cpp')

    def test_project_owned_artwork(self):
        # Set PSWAKER_PROMPT_ART_PREVIEW to a directory to review the artwork as PNG files.
        preview = os.environ.get('PSWAKER_PROMPT_ART_PREVIEW')
        if preview:
            Path(preview).mkdir(parents=True, exist_ok=True)
        self.run_check('prompt-art.cpp', 'prompt-art.cpp')
        if preview:
            for raw in Path(preview).glob('*.rgba'):
                write_png(raw.read_bytes(), raw.with_suffix('.png'))
                raw.unlink()


if __name__ == '__main__':
    unittest.main()
