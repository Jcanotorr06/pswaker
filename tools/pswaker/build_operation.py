"""Cooperative cancellation and measured progress for one local build attempt."""
from contextlib import contextmanager
from contextvars import ContextVar
import threading
from pathlib import Path
import json
import uuid

from owned_work import state_root
from diagnostics import Diagnostics


class BuildCancelled(Exception):
    """Owned work has stopped; this attempt must not publish a result."""


CURRENT: ContextVar['BuildOperation | None'] = ContextVar('build_operation', default=None)


class BuildOperation:
    def __init__(self, observe=None):
        self.observe = observe or (lambda event: None)
        self.cancelled = threading.Event()
        self.lock = threading.Lock()
        self.committed = False
        self.stage = 'validate'
        self.events = []
        self.log = None
        self.diagnostics = Diagnostics()

    def cancel(self):
        # Publication and cancellation have one ordering. After the verified
        # rename wins, a late Cancel cannot misreport a completed package.
        if not self.lock.acquire(blocking=False):
            return False
        try:
            if self.committed:
                return False
            self.cancelled.set()
            return True
        finally:
            self.lock.release()

    def check(self):
        if self.cancelled.is_set():
            raise BuildCancelled('Cancelled. Validate again to retry from the beginning.')

    def emit(self, event):
        self.stage = event['stage']
        self.diagnostics.stage_event(event)
        if event['event'] != 'progress':
            self.events.append(event)
            try:
                if self.log is None:
                    logs = state_root() / 'logs'
                    logs.mkdir(parents=True, exist_ok=True)
                    self.log = logs / ('stages-' + uuid.uuid4().hex + '.jsonl')
                with self.log.open('a', encoding='utf-8') as saved:
                    saved.write(json.dumps(event) + '\n')
            except OSError:
                pass
        self.observe(event)

    def progress(self, activity, completed, total):
        self.check()
        self.emit({'stage': self.stage, 'event': 'progress', 'activity': activity,
                   'completed': completed, 'total': total})
        self.check()

    @contextmanager
    def bind(self):
        token = CURRENT.set(self)
        try:
            self.check()
            yield self
        finally:
            CURRENT.reset(token)

    def publish(self, work, destination):
        with self.lock:
            self.check()
            work.rename(destination)
            self.committed = True


def checkpoint():
    operation = CURRENT.get()
    if operation:
        operation.check()


def progress(activity, completed, total):
    operation = CURRENT.get()
    if operation:
        operation.progress(activity, completed, total)


def copy_file(source, target, *args, **kwargs):
    """shutil copy function with bounded reads and cancellation between chunks."""
    source, target = Path(source), Path(target)
    total, completed = source.stat().st_size, 0
    with source.open('rb') as incoming, target.open('wb') as outgoing:
        progress('Copying ' + target.name, 0, total)
        while chunk := incoming.read(8 << 20):
            checkpoint()
            outgoing.write(chunk)
            completed += len(chunk)
            progress('Copying ' + target.name, completed, total)
    return str(target)
