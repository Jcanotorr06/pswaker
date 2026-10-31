"""Synthetic renderer descriptions; never console or driver shader data."""
import hashlib
import json
import sqlite3
import struct
from contextlib import closing


def make_seed(directory, *, keys=(42, 84)):
    directory.mkdir(parents=True)
    path = directory / 'initial_pipeline_cache.db'
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('CREATE TABLE aurora_schema(value INTEGER)')
        db.execute('INSERT INTO aurora_schema VALUES (1)')
        db.execute('CREATE TABLE pipeline_cache(type INTEGER, hash INTEGER, config_version INTEGER, '
                   'config_size INTEGER, config BLOB, first_frame_used INTEGER, PRIMARY KEY(type,hash))')
        for key in keys:
            db.execute('INSERT INTO pipeline_cache VALUES (0,?,5,8,?,10)',
                       (key, struct.pack('<I4B', 5, key % 256, 1, 1, 0)))
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    report = {'schema': 1, 'installed_path': '/app0/initial_pipeline_cache.db',
              'source_files': {'synthetic.db': {'bytes': path.stat().st_size, 'sha256': sha}},
              'rows': len(keys), 'configurations': [{'type': 0, 'version': 5, 'bytes': 8, 'rows': len(keys)}],
              'sha256': sha}
    (directory / 'pipeline-seed.json').write_text(json.dumps(report))
    return report
