#!/usr/bin/env python3
"""Reproduce the data-free content contract from checksum-locked upstream sources."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import urllib.request


SOURCES = {
    'upstream': {
        'url': 'https://raw.githubusercontent.com/centollOS/SwitchWaker/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/game/UPSTREAM',
        'sha256': '809b2f08edea049a2ec9f0dd9f47cad7c0ee433f533efd90e79ea90c7a4b1075'},
    'oracle': {
        'url': 'https://raw.githubusercontent.com/centollOS/SwitchWaker/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/tools/disc_manifest.py',
        'sha256': 'f017dc882a0ef447119aabca7a09c12ef70d61fa19f70f3599869bb8b467d845'},
    'generator': {
        'url': 'https://raw.githubusercontent.com/centollOS/SwitchWaker/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/tools/gen_asset_stubs.py',
        'sha256': 'b23a652fe72c184f69b093794f2463e2386f7ba087ec7676a2ebcb2e5cecf4ee'},
    'config': {
        'url': 'https://raw.githubusercontent.com/snrubrm/tww/b09eebc39852e18397031d9a563a8eae124f21f1/config/GZLE01/config.yml',
        'sha256': '0676fb874cec639ed426b23d12c18afbca7b1a92dc341bd2fd351b50722bb883'},
}


def generate():
    # PyYAML is needed only to reproduce this committed contract, never to validate an image.
    import yaml
    sources = {}
    for name, row in SOURCES.items():
        with urllib.request.urlopen(row['url'], timeout=60) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError(f'{name}: upstream source SHA-256 mismatch')
        sources[name] = data.decode()
    cfg = yaml.safe_load(sources['config'])
    # Same selection as gen_asset_stubs.py: main.dol and RELs with extracted arrays.
    modules = [cfg] + [module for module in cfg['modules'] if module.get('extract')]
    required = []
    for module in modules:
        obj = module['object']
        path, _, member = obj.removeprefix('files/').partition(':')
        required.append({'path': path, 'member': member, 'sha1': module['hash'],
                         'asset_count': len(module.get('extract') or [])})
    iso_sha1 = re.search(r'^EXPECTED_ISO_SHA1 = "([0-9a-f]{40})"', sources['oracle'], re.M)[1]
    return {'schema': 1, 'game_id': 'GZLE01', 'disc_number': 0, 'revision': 0,
            'image_size': 1459978240, 'image_sha1': iso_sha1,
            'switchwaker_revision': 'ba8d0a31446cd53ceaebd6b7269cca641e73bf4c',
            'decomp_revision': 'b09eebc39852e18397031d9a563a8eae124f21f1',
            'sources': SOURCES, 'required_content': required}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='Write outside the repo, then compare content-contract.json')
    args = parser.parse_args()
    with args.output.open('x') as stream:
        stream.write(json.dumps(generate(), indent=2) + '\n')
