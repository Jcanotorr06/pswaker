"""Data-free program payload contract shared by packaging and desktop bundling."""
import json
import hashlib
from pathlib import Path
import re
import warnings
import zlib

from disc_image import require

PROGRAM_FILES = {'eboot.bin', 'build-info.json', 'sce_sys/icon0.png', 'sce_sys/param.sfo',
                 'sce_sys/about/right.sprx', 'sce_module/libSceFios2.prx', 'sce_module/libc.prx'}
ARTWORK = {'icon': ('ICON0_PNG', 'icon0.png', 512, 512),
           'splash': ('PIC1_PNG', 'pic1.png', 1920, 1080)}


def program_files(kind):
    return PROGRAM_FILES | ({'sce_sys/pic1.png'} if kind == 'game' else set())


def package_metadata(kind):
    return [('PARAM_SFO', 'param.sfo'), ('ICON0_PNG', 'icon0.png')] + (
        [('PIC1_PNG', 'pic1.png')] if kind == 'game' else [])


def inventory_changes(expected, actual):
    """Describe changed payload files using artwork resource names where applicable."""
    resources = {'sce_sys/' + row[1]: row[0] for row in ARTWORK.values()}
    changes = []
    for path in sorted(set(expected) | set(actual)):
        if expected.get(path) != actual.get(path):
            resource = next((value for suffix, value in resources.items()
                             if path == suffix or path.endswith('/' + suffix)), None)
            changes.append(f'{resource} ({path})' if resource else path)
    return ', '.join(changes)


def artwork_properties(role):
    resource, _, width, height = ARTWORK[role]
    return {'role': role, 'resource': resource, 'width': width, 'height': height,
            'colour_type': 2, 'bit_depth': 8, 'interlace': 0}


def validate_artwork(role, path):
    """Fully decode owner PNG bytes on the pinned Linux preparation host."""
    properties = artwork_properties(role)
    contract = (f"{properties['resource']}: expected {properties['width']} x {properties['height']} "
                'PNG, 8-bit RGB (colour type 2), non-interlaced, no alpha or tRNS')
    try:
        # Host-only apt dependency; desktop assembly checks the prepared release's hashes.
        import png  # pyright: ignore[reportMissingImports]
    except ImportError as error:
        raise ValueError(contract + '; install the pinned python3-png package using install-host.sh') from error
    try:
        data = path.read_bytes()
        with warnings.catch_warnings():
            warnings.simplefilter('error')  # PyPNG reports CRC failures as warnings.
            chunk_reader = png.Reader(bytes=data)
            chunks = list(chunk_reader.chunks())
            require(not chunk_reader.file.read(1), 'unexpected bytes after IEND')
            require(all(name[0] & 32 or name in {b'IHDR', b'PLTE', b'IDAT', b'IEND'}
                        for name, _ in chunks), 'unknown critical PNG chunk')
            names = [name for name, _ in chunks]
            require(names[0] == b'IHDR' and names.count(b'IHDR') == 1 and names.count(b'PLTE') <= 1
                    and b'IDAT' in names, 'invalid PNG chunk inventory')
            first, last = names.index(b'IDAT'), len(names) - 1 - names[::-1].index(b'IDAT')
            require(all(name == b'IDAT' for name in names[first:last + 1])
                    and (b'PLTE' not in names or names.index(b'PLTE') < first),
                    'invalid PNG chunk ordering')
            reader = png.Reader(bytes=data)
            width, height, rows, info = reader.read()
            observed = (f'{width} x {height}, colour type {reader.color_type}, '
                        f"{info['bitdepth']}-bit, interlace {info['interlace']}")
            require((width, height) == (properties['width'], properties['height'])
                    and reader.color_type == 2 and info['bitdepth'] == 8
                    and info['interlace'] == 0, 'observed ' + observed)
            require(not any(name == b'tRNS' for name, _ in chunks), 'observed tRNS transparency')
            require(chunks[-1] == (b'IEND', b''), 'missing or invalid IEND')
            count = 0
            for row in rows:
                require(len(row) == width * 3, 'invalid decoded scanline length')
                count += 1
            require(count == height, f'incomplete decode: {count} of {height} rows')
            # PyPNG's row iterator does not require the zlib end marker.
            decoder = zlib.decompressobj()
            for name, chunk in chunks:
                if name == b'IDAT':
                    decoder.decompress(chunk)
            require(decoder.eof and not decoder.unused_data, 'incomplete or extra compressed image data')
        return {**properties, 'sha256': hashlib.sha256(data).hexdigest()}
    except (png.Error, OSError, ValueError, RuntimeError, Warning, IndexError, zlib.error) as error:
        raise ValueError(f'{contract}; {path}: {error}') from error


def checked_artwork(directory, manifest, *, decode=False):
    """Check both resources against the path-free manifest, optionally decoding on Linux."""
    recorded = manifest.get('artwork')
    require(isinstance(recorded, dict) and set(recorded) == {row[0] for row in ARTWORK.values()},
            'ICON0_PNG/PIC1_PNG: program manifest must record both artwork resources')
    for role, (resource, name, _, _) in ARTWORK.items():
        path = directory / name
        try:
            actual = validate_artwork(role, path) if decode else {
                **artwork_properties(role), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        except OSError as error:
            raise ValueError(f'{resource}: cannot read required artwork {path}: {error}') from error
        require(recorded[resource] == actual, f'{resource}: artwork differs from the program manifest; '
                'revalidate the artwork and rebuild the program release')
    return recorded


def bundled_program(bundle: Path) -> tuple[str, str]:
    """Read the identity of the fixed, maintainer-bundled game release."""
    release = json.loads((bundle / 'program/program-release.json').read_text())
    info = json.loads((bundle / 'program/stage/build-info.json').read_text())
    require(release['schema'] == 1 and release['kind'] == 'game'
            and 'diagnostic_build_id' not in info
            and isinstance(release['build_id'], str) and bool(release['build_id'])
            and info['program_build_id'] == release['build_id'],
            'The bundled release must be a matching game program')
    version = info['app_version']
    require(isinstance(version, str) and re.fullmatch(r'[0-9]{2}\.[0-9]{2}', version),
            'The bundled game version must be NN.NN')
    return version, release['build_id']
