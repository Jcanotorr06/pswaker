"""Leased ownership records for safe cleanup after an interrupted app session."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid


def state_root():
    return Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local/share')) / 'PSWaker'


def save_evidence(events, outcome, error=None):
    """Keep stage/timing/error metadata, never source data or file contents."""
    try:
        logs = state_root() / 'logs'
        logs.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix='attempt-', suffix='.json', dir=logs, delete=False) as saved:
            saved.write(json.dumps({'schema': 1, 'outcome': outcome, 'events': events,
                                    'error': str(error) if error else None}, indent=2).encode('utf-8'))
    except OSError:
        pass


def lock(stream):
    stream.seek(0)
    if os.name == 'nt':
        import msvcrt
        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def directory_identity(path):
    stat = path.stat()
    return [stat.st_dev, stat.st_ino]


def append_record(lease, record):
    lease.write((json.dumps(record) + '\n').encode('utf-8'))
    lease.flush()
    os.fsync(lease.fileno())


def read_record(lease):
    lease.seek(1)
    record = None
    # A crash can truncate the newest update; preceding complete records
    # remain usable. No bulk data is written before the ready record is durable.
    for line in lease:
        if not line.endswith(b'\n'):
            break
        record = json.loads(line)
    if record is None:
        raise ValueError('Incomplete workspace initialization record; no build data was written')
    return record


def remove_owned(record):
    work = Path(record['workspace'])
    # Never follow a replaced parent, symlink, junction or renamed directory.
    if (work.parent != work.parent.resolve()
            or directory_identity(work.parent) != record['parent_identity']):
        raise ValueError(f'Workspace parent ownership changed; preserved record for {work}')
    if not work.exists():
        return
    if (work != work.resolve() or not work.is_dir()
            or work.name != '.complete-' + record['id']
            or directory_identity(work) != record['identity']):
        raise ValueError(f'Workspace ownership changed; preserved {work}')
    marker = work / '.pswaker-owner'
    if record['phase'] == 'allocated':
        # Initialization has not authorized any build data. Delete only its
        # partial marker and empty directory; never recursively remove files.
        if any(path != marker for path in work.iterdir()):
            raise ValueError(f'Unfinished workspace initialization contains owner files; preserved {work}')
        if marker.exists():
            if marker.is_symlink() or not record['id'].startswith(marker.read_text()):
                raise ValueError(f'Workspace ownership marker changed; preserved {work}')
            marker.unlink()
        work.rmdir()
        return
    if marker.read_text() != record['id']:
        raise ValueError(f'Workspace ownership marker changed; preserved {work}')
    shutil.rmtree(work)


class OwnedWorkspace:
    def __init__(self, record):
        self.path = Path(record['workspace'])
        self.record = record

    def cleanup(self):
        remove_owned(self.record)


@contextmanager
def workspace(parent):
    parent = parent.resolve()
    records = state_root() / 'work'
    records.mkdir(parents=True, exist_ok=True)
    identifier = uuid.uuid4().hex
    work = parent / ('.complete-' + identifier)
    journal = records / (identifier + '.jsonl')
    # Lock before creating work, and journal ownership before copying any data.
    pending = True
    created = False
    registered = False
    try:
        with journal.open('x+b') as lease:
            lease.write(b' ')
            lease.flush()
            lock(lease)
            record = None
            try:
                record = {'schema': 1, 'id': identifier, 'workspace': str(work), 'identity': None,
                          'parent_identity': directory_identity(parent), 'phase': 'planned'}
                lease.seek(1)
                append_record(lease, record)
                work.mkdir()
                created = True
                record = dict(record, identity=directory_identity(work), phase='allocated')
                append_record(lease, record)
                (work / '.pswaker-owner').write_text(identifier)
                record = dict(record, phase='ready')
                append_record(lease, record)
                registered = True
                yield OwnedWorkspace(record)
            except Exception as error:
                if created and not registered and record is not None:
                    try:
                        remove_owned(record)
                    except (OSError, ValueError) as cleanup:
                        raise ValueError(f'{error}\nCleanup also failed: {cleanup}\n'
                                         f'Private unfinished workspace remains at {work}. '
                                         'Restore ownership/access and reopen the app to retry recovery.') from error
                raise
            finally:
                # Caller cleans before this lease ends; retain failed cleanup
                # for next launch. Publication removes the original work path.
                pending = work.exists()
    finally:
        if not pending:
            try:
                journal.unlink(missing_ok=True)
            except OSError as error:
                # A bookkeeping failure must not turn a verified publication
                # into a reported build failure. Recovery can retire it later.
                save_evidence([], 'record-cleanup-failed', error)


def recover_abandoned():
    """Skip live attempts and preserve anything whose ownership cannot be proved."""
    results = []
    records = state_root() / 'work'
    for journal in records.glob('*.jsonl'):
        try:
            with journal.open('r+b') as lease:
                try:
                    lock(lease)
                except OSError:
                    continue
                record = read_record(lease)
                if record['schema'] != 1 or journal.stem != record['id']:
                    raise ValueError('Invalid workspace ownership record')
                remove_owned(record)
                results.append({'stage': 'recover', 'event': 'passed', 'workspace': record['workspace']})
            journal.unlink(missing_ok=True)
        except (OSError, ValueError, KeyError, TypeError) as error:
            results.append({'stage': 'recover', 'event': 'failed', 'error': str(error), 'record': str(journal)})
    if results:
        save_evidence(results, 'interrupted')
    return results
