"""Read-only, bounded checks for the pinned game's raw GameCube image contract."""
import hashlib
import json
from pathlib import Path
import struct
import sys

if getattr(sys, 'frozen', False):
    PLATFORM = Path(getattr(sys, '_MEIPASS')) / 'platform/ps4'
else:
    import build_inputs
    PLATFORM = build_inputs.Locations().platform
CONTRACT = PLATFORM / 'content-contract.json'
MAX_CONTAINER = 64 << 20


def require(condition, message):
    if not condition:
        raise ValueError(message)


def word(data, offset):
    require(0 <= offset <= len(data) - 4, 'Truncated content structure; re-dump your original disc')
    return struct.unpack_from('>I', data, offset)[0]


def region(data, offset, size, label):
    require(0 <= offset <= len(data) and 0 <= size <= len(data) - offset,
            f'{label}: invalid or truncated range; re-dump your original disc')
    return data[offset:offset + size]


def text(data, offset):
    require(0 <= offset < len(data), 'Invalid filename offset in disc/archive table')
    end = data.find(b'\0', offset)
    require(end != -1, 'Unterminated filename in disc/archive table')
    name = data[offset:end].decode('ascii')
    require(name not in {'', '.', '..'} and '/' not in name and '\\' not in name,
            'Invalid filename in disc/archive table')
    return name


def expand(data):
    if data[:4] != b'Yaz0':
        return data
    require(len(data) >= 16, 'Truncated Yaz0 header in required game content')
    size = word(data, 4)
    require(size <= MAX_CONTAINER, 'Required Yaz0 content exceeds the supported safety limit')
    out = bytearray()
    pos = 16
    while len(out) < size:
        require(pos < len(data), 'Truncated Yaz0 control byte in required game content')
        code = data[pos]
        pos += 1
        for bit in range(7, -1, -1):
            if len(out) == size:
                break
            if code & (1 << bit):
                require(pos < len(data), 'Truncated Yaz0 literal in required game content')
                out.append(data[pos])
                pos += 1
            else:
                pair = region(data, pos, 2, 'Yaz0 back reference')
                pos += 2
                distance = ((pair[0] & 15) << 8 | pair[1]) + 1
                length = pair[0] >> 4
                if length == 0:
                    length = region(data, pos, 1, 'Yaz0 length')[0] + 18
                    pos += 1
                else:
                    length += 2
                require(distance <= len(out) and len(out) + length <= size,
                        'Invalid Yaz0 back reference in required game content')
                for _ in range(length):
                    out.append(out[-distance])
    return bytes(out)


def archive_member(data, path):
    require(data[:4] == b'RARC', 'Required RELS.arc is not a RARC archive')
    require(word(data, 4) == len(data), 'RELS.arc has an invalid archive length')
    base = word(data, 8)
    count, nodes = word(data, base), base + word(data, base + 4)
    entries_count, entries = word(data, base + 8), base + word(data, base + 12)
    strings_size, strings_off = word(data, base + 16), base + word(data, base + 20)
    strings = region(data, strings_off, strings_size, 'RARC names')
    region(data, nodes, count * 16, 'RARC nodes')
    region(data, entries, entries_count * 20, 'RARC entries')
    payload = base + word(data, 12)
    require(count > 0, 'RELS.arc has no root node')
    parts = path.split('/')
    if parts[0] == text(strings, word(data, nodes + 4)):
        parts = parts[1:]
    node = 0
    for index, part in enumerate(parts):
        require(node < count, 'Invalid RARC directory reference')
        n = nodes + node * 16
        length = struct.unpack_from('>H', data, n + 10)[0]
        first = word(data, n + 12)
        require(first + length <= entries_count, 'Invalid RARC directory extent')
        found = []
        for k in range(first, first + length):
            entry = entries + k * 20
            flags_name = word(data, entry + 4)
            name_off = flags_name & 0xFFFFFF
            require(name_off < len(strings), 'Invalid RARC entry name offset')
            # Dot entries are legal in RARC directories, but never traversed.
            if strings[name_off:name_off + 2] == b'.\0' or strings[name_off:name_off + 3] == b'..\0':
                continue
            if text(strings, name_off) == part:
                found.append((flags_name >> 24, word(data, entry + 8), word(data, entry + 12)))
        require(len(found) == 1, f'RELS.arc: required member {path} is missing or duplicated')
        flags, offset, size = found[0]
        if index == len(parts) - 1:
            require(not flags & 2, f'RELS.arc: required member {path} is a directory')
            return expand(region(data, payload + offset, size, path))
        require(flags & 2, f'RELS.arc: invalid directory for {path}')
        node = offset
    raise ValueError(f'RELS.arc: missing required member {path}')


class DiscImage:
    def __init__(self, stream):
        self.stream = stream
        self.size = stream.seek(0, 2)

    def read(self, offset, size, label):
        require(0 <= offset <= self.size and 0 <= size <= self.size - offset,
                f'{label}: range exceeds image; image is truncated or invalid, re-dump your disc')
        self.stream.seek(offset)
        data = self.stream.read(size)
        require(len(data) == size, f'{label}: short read; image changed or could not be read')
        return data

    def files(self, header):
        offset, size, maximum = struct.unpack_from('>III', header, 0x424)
        require(12 <= size <= MAX_CONTAINER and maximum >= size, 'Invalid GameCube FST size')
        fst = self.read(offset, size, 'GameCube FST')
        count = word(fst, 8)
        require(word(fst, 0) == 0x01000000 and word(fst, 4) == 0 and 1 <= count <= size // 12,
                'Invalid GameCube FST root/table')
        strings = fst[count * 12:]
        directories = [(count, '', 0)]
        files, paths = {}, set()
        for i in range(1, count):
            while i >= directories[-1][0]:
                directories.pop()
            kind_name, position, length = struct.unpack_from('>III', fst, i * 12)
            kind = kind_name >> 24
            require(kind in (0, 1), 'Invalid GameCube FST entry type')
            name = text(strings, kind_name & 0xFFFFFF)
            parent_end, parent, parent_index = directories[-1]
            path = f'{parent}/{name}' if parent else name
            require(path not in paths, f'Duplicate GameCube FST path: {path}')
            paths.add(path)
            if kind:
                require(position == parent_index and i < length <= parent_end,
                        'Invalid GameCube FST directory hierarchy')
                directories.append((length, path, i))
            else:
                require(position <= self.size and length <= self.size - position,
                        f'{path}: invalid/truncated file range; re-dump your disc')
                files[path] = (position, length)
        return files

    def dol(self, offset):
        header = self.read(offset, 0x100, 'main.dol header')
        offsets = struct.unpack_from('>18I', header)
        sizes = struct.unpack_from('>18I', header, 0x90)
        require(any(sizes), 'main.dol has no sections')
        end = 0x100
        for start, size in zip(offsets, sizes):
            if size:
                require(start >= 0x100, 'main.dol has an invalid section offset')
                end = max(end, start + size)
        require(end <= MAX_CONTAINER, 'main.dol exceeds the supported size limit')
        return self.read(offset, end, 'main.dol')


def validate(path):
    contract = json.loads(CONTRACT.read_text())
    require(path.suffix.lower() in {'.iso', '.gcm'},
            'Unsupported image format: supply your raw, uncompressed USA GZLE01 revision-0 .iso or .gcm')
    require(path.is_file(), 'Image must be a readable regular .iso/.gcm file')
    with path.open('rb') as stream:
        disc = DiscImage(stream)
        header = disc.read(0, min(disc.size, 0x440), 'Disc header')
        require(len(header) >= 0x20, 'Disc header is truncated; supply a full raw ISO/GCM dump')
        require(header[0x1C:0x20] == b'\xc2\x33\x9f\x3d',
                'Unsupported/compressed image or invalid GameCube magic; export a raw ISO/GCM from your original disc')
        require(header[:6] == contract['game_id'].encode() and header[6] == contract['disc_number']
                and header[7] == contract['revision'],
                f'Wrong game/region/revision ({header[:6].decode("ascii", errors="replace")} revision {header[7]}); '
                'supply USA GZLE01 revision 0 (disc 0)')
        require(len(header) >= 0x440, 'Disc header is truncated; supply a full raw ISO/GCM dump')
        require(disc.size == contract['image_size'],
                f'Image is truncated, compacted or oversized ({disc.size} bytes); supply a full raw dump '
                f'of {contract["image_size"]} bytes')
        files = disc.files(header)
        containers, checked = {}, []
        for row in contract['required_content']:
            name, member = row['path'], row['member']
            label = name + (':' + member if member else '')
            if name == 'sys/main.dol':
                data = disc.dol(word(header, 0x420))
            else:
                require(name in files, f'Missing required content {name}; supply the unmodified supported dump')
                if name not in containers:
                    offset, size = files[name]
                    require(size <= MAX_CONTAINER, f'{name}: unsupported required-content size')
                    try:
                        containers[name] = expand(disc.read(offset, size, name))
                    except ValueError as error:
                        raise ValueError(f'{name}: {error}') from error
                try:
                    data = archive_member(containers[name], member) if member else containers[name]
                except ValueError as error:
                    raise ValueError(f'{label}: {error}') from error
            actual = hashlib.sha1(data).hexdigest()
            require(actual == row['sha1'],
                    f'{label}: content SHA-1 mismatch against pinned GZLE01 revision 0; re-dump the unmodified disc')
            checked.append({'path': name, 'member': member, 'sha1': actual, 'size': len(data)})
        stream.seek(0)
        sha1, sha256 = hashlib.sha1(), hashlib.sha256()
        while chunk := stream.read(8 << 20):
            sha1.update(chunk)
            sha256.update(chunk)
        accepted_images = [contract['image_sha1']] + [row['sha1'] for row in contract.get('additional_images', [])]
        require(sha1.hexdigest() in accepted_images,
                'Full image SHA-1 mismatch against pinned GZLE01 revision 0; use the unmodified full raw dump')
    return {'game_id': contract['game_id'], 'revision': contract['revision'],
            'size': disc.size, 'sha1': sha1.hexdigest(), 'sha256': sha256.hexdigest(),
            'contract_sha256': hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
            'required_content': checked}
