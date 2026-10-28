"""Explicit local export of structured evidence; never copy logs or attachments.

Redaction is a closed schema, not a search for known secret/path spellings.
Exception messages, notes, tool output, arguments, filenames and arbitrary
manifest fields never enter an export, including through nested exceptions.
"""
from datetime import datetime, timezone
import errno
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import uuid


STAGES = {'validate', 'prepare', 'verify-program', 'assemble', 'inspect', 'publish', 'cleanup'}
NEXT_ACTION = {
    'validate': 'Check the supported raw image, folder access and free space; validate again.',
    'prepare': 'Restore access and free space in the destination, then validate again.',
    'verify-program': 'Reinstall the complete application, then validate again.',
    'assemble': 'Check destination access and free space; retry. If it persists, reinstall the application.',
    'inspect': 'Do not install the failed output. Validate again; if it persists, reinstall the application.',
    'publish': 'Choose a new writable destination that does not exist, then validate again.',
    'cleanup': 'Restore destination access and reopen the application to retry cleanup.',
}


def failure_details(stage, error):
    """Keep failure classes and OS codes, never arbitrary exception text."""
    stage = stage if stage in STAGES else 'validate'
    causes, seen = [], set()
    current = error
    while current is not None and id(current) not in seen and len(causes) < 8:
        seen.add(id(current))
        category = 'unexpected-error'
        if isinstance(current, OSError):
            category = {errno.ENOSPC: 'insufficient-space', errno.EACCES: 'access-denied',
                        errno.EPERM: 'access-denied', errno.ENOENT: 'file-unavailable',
                        errno.EEXIST: 'destination-exists'}.get(current.errno or 0, 'io-error')
        elif isinstance(current, (ValueError, KeyError, TypeError)):
            category = {'validate': 'invalid-input', 'verify-program': 'bundle-integrity',
                        'inspect': 'verification-failed'}.get(stage, 'operation-failed')
        item: dict[str, str | int] = {'category': category}
        if isinstance(current, OSError) and type(current.errno) is int:
            item['errno'] = current.errno
        causes.append(item)
        current = current.__cause__ or current.__context__
    category = next((item['category'] for item in causes if 'errno' in item),
                    causes[-1]['category'] if causes else 'unexpected-error')
    return {'stage': stage, 'category': category,
            'causes': causes, 'next_action': NEXT_ACTION[stage]}


def select_fields(source, patterns):
    return {key: value for key, pattern in patterns.items()
            if isinstance(value := source.get(key), str) and re.fullmatch(pattern, value)}


HASH = r'[0-9a-f]{64}'
VERSION = r'[0-9]{2}\.[0-9]{2}'
DESKTOP_VERSION = VERSION + r'|[0-9]{1,5}(?:\.[0-9]{1,5}){3}'


class DiagnosticExportError(ValueError):
    """Export failed; the original operation evidence remains available for retry."""


class Diagnostics:
    def __init__(self):
        self.operation_id = uuid.uuid4().hex
        self.started = datetime.now(timezone.utc).isoformat()
        self.app = {}
        self.program = {}
        self.tools = {}
        self.image = {}
        self.package = {}
        self.tool_runs = []
        self.stages = []
        self.outcome = 'running'
        self.failure = None

    def capture_bundle(self, bundle):
        # Snapshot metadata at the start, never re-read a different bundle on export.
        for name, target, patterns in [
            ('desktop-release.json', self.app, {'app_version': DESKTOP_VERSION}),
            ('program/program-release.json', self.program,
             {'build_id': r'[0-9a-f]{20}|' + HASH, 'elf_sha256': HASH, 'eboot_sha256': HASH}),
            ('packaging/tool-release.json', self.tools,
             {'source_revision': r'[0-9a-f]{40}', 'source_archive_sha256': HASH,
              'sdk': r'[0-9]+\.[0-9]+\.[0-9]+'}),
        ]:
            try:
                raw = (bundle / name).read_bytes()
                source = json.loads(raw)
                target.update(select_fields(source, patterns))
                target['manifest_sha256'] = hashlib.sha256(raw).hexdigest()
                target['verification'] = 'reported; not yet verified for this operation'
                if target is self.program and isinstance(source.get('build_id'), str):
                    target['build_id_sha256'] = hashlib.sha256(source['build_id'].encode()).hexdigest()
            except (OSError, ValueError, TypeError, AttributeError):
                continue
        try:
            info = json.loads((bundle / 'program/stage/build-info.json').read_text())
            self.program.update(select_fields(info, {'app_version': VERSION}))
            if 'app_version' not in self.app and 'version' not in self.app:
                self.app.update(select_fields(info, {'app_version': VERSION}))
        except (OSError, ValueError, TypeError, AttributeError):
            pass
        if 'app_version' in self.app:
            self.app['version'] = self.app.pop('app_version')

    def record_image(self, image):
        self.image = select_fields(image, {'sha1': r'[0-9a-f]{40}', 'sha256': HASH})

    def verified_bundle(self, bundle):
        self.capture_bundle(bundle)
        self.program['verification'] = 'verified snapshot used by this operation'
        self.tools['verification'] = 'verified snapshot used by this operation'
        self.app['verification'] = 'verified release inventory'

    def record_package(self, package):
        self.package = select_fields(package, {'sha256': HASH})
        self.package.update(title_id='PSWK00001', content_id='IV0000-PSWK00001_00-PSWAKERGAME00000')

    def record_tool(self, command, returncode):
        if command in {'pkg_build', 'pkg_extract', 'pkg_listentries', 'pkg_extractentry'} and type(returncode) is int:
            self.tool_runs.append({'operation': command, 'exit_code': returncode})

    def stage_event(self, event):
        if event.get('stage') not in STAGES or event.get('event') not in {'started', 'passed', 'failed', 'cancelled'}:
            return
        item = {'stage': event['stage'], 'event': event['event']}
        seconds = event.get('seconds')
        if type(seconds) in {int, float} and math.isfinite(seconds) and seconds >= 0:
            item['seconds'] = seconds
        self.stages.append(item)

    def finish(self, outcome, stage=None, error=None):
        self.outcome = outcome
        if error is not None:
            self.failure = failure_details(stage, error)

    def export(self, destination):
        """Write only sanitized JSON, atomically, without replacing an owner file."""
        report = {'schema': 1, 'operation_id': self.operation_id, 'started_utc': self.started,
                  'outcome': self.outcome, 'app': self.app, 'program': self.program,
                  'tools': self.tools, 'tool_runs': self.tool_runs, 'image': self.image, 'package': self.package,
                  'runtime': {'python': '.'.join(map(str, sys.version_info[:3])),
                              'platform': 'Windows' if sys.platform == 'win32' else 'other'},
                  'stages': self.stages, 'failure': self.failure,
                  'console_acceptance': False, 'distribution_cleared': False,
                  'privacy': 'Paths, filenames, arguments, raw errors, tool output and attachments omitted. '
                             'No game data, keys or credentials. Local report; share only by choice.'}
        temporary = None
        try:
            destination = Path(destination)
            with tempfile.NamedTemporaryFile(prefix='.diagnostic-', suffix='.tmp', dir=destination.parent,
                                             delete=False) as saved:
                temporary = Path(saved.name)
                saved.write((json.dumps(report, indent=2) + '\n').encode('utf-8'))
                saved.flush()
                os.fsync(saved.fileno())
            if os.name == 'nt':
                os.rename(temporary, destination)  # Windows refuses any existing file.
            else:
                os.link(temporary, destination)  # POSIX rename would overwrite an owner file.
        except (OSError, ValueError, TypeError):
            raise DiagnosticExportError('Could not export the report. Choose another writable location and a new '
                                        'filename, check free space, then retry. The original operation is preserved.') from None
        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass  # This temporary contains only the sanitized report, never raw evidence.
