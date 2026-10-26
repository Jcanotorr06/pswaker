"""Private controlled-case CLI; all progress here is synthetic and disposable."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]


class StorageCaseTests(unittest.TestCase):
    def test_case_preparation_preserves_seed_and_encodes_recovery_choices(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed = root / 'seed.gci'
            data = bytearray(0x18040)
            data[:6] = b'GZLE01'
            data[8:16] = b'gczelda\0'
            data[0x38:0x3a] = b'\0\x0c'
            data[7] = 1
            data[0x30:0x34] = b'\0\x01\0\x03'
            data[0x3c:0x40] = b'\0\0\x1c\0'
            for block in (0x2040, 0x4040):
                for slot in range(3):
                    start = block+8+slot*0x770+0x768
                    # USA checksum of 0x768 zero bytes, from the format contract.
                    data[start:start+8] = bytes.fromhex('00000000fffff898')
                data[block+0x1ffc:block+0x2000] = bytes.fromhex('e9c5063d')
            seed.write_bytes(data)
            inspection = root / 'inspection.json'
            inspection.write_text(json.dumps({'sfo': {'TITLE_ID': 'PSWK00001'},
                                              'program': {'build_id': 'synthetic'},
                                              'package': {'sha256': 'a'*64}}))
            output = root / 'cases'
            command = [sys.executable, str(HERE / 'storage-cases.py'), '--seed', str(seed),
                       '--inspection', str(inspection), '--output', str(output)]
            result = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(seed.read_bytes(), data)
            manifest = json.loads((output / 'cases.json').read_text())
            gci = 'saves/USA/Card A/01-GZLE-gczelda.gci'
            self.assertEqual(manifest['cases']['baseline'][gci]['sha256'], hashlib.sha256(data).hexdigest())
            corrupt = (output / 'corrupt-with-backup' / gci).read_bytes()
            self.assertNotEqual(corrupt, data)
            self.assertEqual((output / 'corrupt-with-backup' / (gci+'.backup')).read_bytes(), data)
            self.assertFalse((output / 'corrupt-no-backup' / (gci+'.backup')).exists())
            self.assertTrue((output / 'startup-unavailable/saves/USA/Card B').is_file())
            repeated = subprocess.run(command, text=True, capture_output=True)
            self.assertNotEqual(repeated.returncode, 0)
            self.assertEqual((output / 'corrupt-with-backup' / gci).read_bytes(), corrupt)
            seed.write_bytes(corrupt)
            rejected = subprocess.run(command[:-1] + [str(root / 'invalid')], text=True, capture_output=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertFalse((root / 'invalid').exists())
