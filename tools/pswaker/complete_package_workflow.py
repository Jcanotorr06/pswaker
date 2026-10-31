"""Complete package workflow, independent of the desktop presentation adapter.

Actions and poll run on the caller's thread. Workers only enqueue outcomes;
poll accepts them and checks selection freshness without waiting for work.
"""
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import json
import queue
import sys
import threading
import time
from typing import Literal

from build_operation import BuildCancelled, BuildOperation
from disc_image import CONTRACT, require
from owned_work import recover_abandoned, save_evidence
from package_artifact import StageFailure, Stages
from package_validation import validate_selection
from program_payload import bundled_program
from windows_package import create_package, INSTALL_INSTRUCTIONS


Activity = Literal['idle', 'recovering', 'validating', 'creating']
Result = Literal['none', 'validated', 'verified', 'failed', 'cancelled', 'stale', 'recovery-attention']
FileIdentity = tuple[int, int, int, int, int]
SelectionIdentity = tuple[FileIdentity, FileIdentity]


@dataclass(frozen=True)
class WorkflowProgress:
    mode: Literal['stopped', 'indeterminate', 'determinate'] = 'stopped'
    completed: int = 0
    total: int = 0


@dataclass(frozen=True)
class WorkflowView:
    image: Path | None
    destination: Path | None
    program_text: str
    activity: Activity
    result: Result
    status: str
    details: str
    progress: WorkflowProgress
    can_select: bool
    can_validate: bool
    can_create: bool
    can_cancel: bool
    can_export: bool
    package_path: Path | None
    installation_instructions: str
    ready_to_close: bool

    @property
    def busy(self) -> bool:
        return self.activity != 'idle'

    @property
    def can_open(self) -> bool:
        return self.package_path is not None and not self.busy


@dataclass(frozen=True)
class _RecoveryFinished:
    worker: object
    items: list[dict]


@dataclass(frozen=True)
class _Stage:
    worker: object
    generation: int
    event: dict


@dataclass(frozen=True)
class _ValidationFinished:
    worker: object
    generation: int
    report: dict | None
    identity: SelectionIdentity | None
    error: str | None
    seconds: float


@dataclass(frozen=True)
class _PackageFinished:
    worker: object
    result: dict | None
    error: str | None
    cancelled: bool
    seconds: float


def _start_worker(work: Callable[[], None]) -> None:
    """Internal execution seam: a thread in production, held work in tests."""
    threading.Thread(target=work, daemon=True).start()


def _file_identity(path: Path) -> FileIdentity:
    stat = path.stat()
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


class CompletePackageWorkflow:
    def __init__(self, bundle: Path):
        self._bundle = bundle
        self._image: Path | None = None
        self._destination: Path | None = None
        self._generation = 0
        self._worker: object | None = object()
        self._operation: BuildOperation | None = None
        self._closing = False
        self._accepted: SelectionIdentity | None = None
        self._accepted_image: dict | None = None
        self._activity: Activity = 'recovering'
        self._result: Result = 'none'
        self._status = 'Checking interrupted work…'
        self._details = ''
        self._progress = WorkflowProgress()
        self._package: Path | None = None
        self._messages: queue.Queue[_RecoveryFinished | _Stage | _ValidationFinished | _PackageFinished] = queue.Queue()
        self._version: str | None = None
        try:
            self._version, build_id = bundled_program(bundle)
            self._program_text = f'Bundled game program {self._version} · build {build_id}'
            if getattr(sys, 'frozen', False):
                fixed = json.loads((bundle / 'desktop-release.json').read_text())
                tools = json.loads((bundle / 'packaging/tool-release.json').read_text())
                self._program_text = (f"PSWaker {fixed['app_version']} · game program {self._version} · build {build_id}\n"
                                      f"Packaging tools {tools['source_revision'][:12]} · .NET {tools['sdk']}")
        except (OSError, ValueError, KeyError, TypeError):
            self._program_text = 'Bundled game program unavailable — use a complete application build.'
        worker = self._worker
        _start_worker(lambda: self._recover(worker))

    @property
    def view(self) -> WorkflowView:
        idle = self._worker is None
        available = idle and not self._closing
        operation = self._operation
        return WorkflowView(
            image=self._image, destination=self._destination, program_text=self._program_text,
            activity=self._activity, result=self._result, status=self._status, details=self._details,
            progress=self._progress, can_select=self._activity != 'creating' and not self._closing,
            can_validate=available and self._image is not None and self._destination is not None,
            can_create=available and self._accepted is not None and self._version is not None
                       and (self._bundle / 'desktop-release.json').is_file(),
            can_cancel=not idle and operation is not None and not operation.cancelled.is_set(),
            can_export=available and operation is not None and operation.diagnostics.outcome != 'running',
            package_path=self._package,
            installation_instructions=INSTALL_INSTRUCTIONS if self._package is not None else '',
            ready_to_close=self._closing and idle)

    def select_image(self, image: Path) -> None:
        if self.view.can_select:
            self._image = image
            self._invalidate()

    def select_destination(self, parent: Path) -> None:
        if self.view.can_select:
            self._destination = parent / ('PSWaker-' + (self._version or 'package'))
            self._invalidate()

    def _invalidate(self, message: str = 'Selection changed. Validate again before creating a package.') -> None:
        if self._activity == 'validating' and self._operation is not None:
            self._operation.cancel()
        self._generation += 1
        self._accepted = self._accepted_image = None
        self._package = None
        self._result = 'stale'
        self._details = ''
        self._status = message

    def validate(self) -> None:
        if not self.view.can_validate:
            return
        image, destination = self._image, self._destination
        assert image is not None and destination is not None
        self._invalidate()
        worker, operation = self._begin('validating')
        generation = self._generation
        self._status = 'Validating image… Reading and checking the entire image; please wait.'
        _start_worker(lambda: self._validate(worker, operation, generation, image, destination))

    def create_package(self) -> None:
        # A view is a rendering snapshot, not permission to use stale inputs.
        self._check_selection()
        if not self.view.can_create:
            return
        image, destination, accepted = self._image, self._destination, self._accepted_image
        assert image is not None and destination is not None and accepted is not None
        self._generation += 1
        worker, operation = self._begin('creating')
        self._package = None
        self._details = ''
        self._status = 'Preparing package…'
        _start_worker(lambda: self._assemble(worker, operation, image, destination, accepted))

    def _begin(self, activity: Activity) -> tuple[object, BuildOperation]:
        worker, generation = object(), self._generation
        operation = BuildOperation(lambda event: self._messages.put(_Stage(worker, generation, dict(event))))
        self._worker, self._operation = worker, operation
        self._activity, self._result = activity, 'none'
        self._progress = WorkflowProgress('indeterminate')
        return worker, operation

    def cancel(self) -> None:
        if self.view.can_cancel and self._operation is not None and self._operation.cancel():
            self._status = 'Cancelling… Waiting for active work and cleanup to finish.'

    def request_close(self) -> None:
        self._closing = True
        self.cancel()

    def export_diagnostics(self, destination: Path) -> bool:
        if not self.view.can_export or self._operation is None:
            return False
        # DiagnosticExportError reaches the presentation adapter's error dialog;
        # neither successful nor failed export changes the operation's view.
        self._operation.diagnostics.export(destination)
        return True

    def _recover(self, worker: object) -> None:
        try:
            items = recover_abandoned()
        except OSError as error:
            items = [{'event': 'failed', 'error': str(error)}]
        self._messages.put(_RecoveryFinished(worker, items))

    def _validate(self, worker: object, operation: BuildOperation, generation: int,
                  image: Path, destination: Path) -> None:
        start = time.monotonic()
        report, identity, error = None, None, None
        try:
            operation.diagnostics.capture_bundle(self._bundle)
            with operation.bind(), Stages(operation.emit)('validate'):
                identity = (_file_identity(image), _file_identity(CONTRACT))
                report = validate_selection(image, destination)
                require(identity == (_file_identity(image), _file_identity(CONTRACT)),
                        'The image or validation contract changed during validation. Select a stable local file and retry.')
        except BuildCancelled:
            error = 'cancelled'
            operation.diagnostics.finish('cancelled')
        except (OSError, ValueError, KeyError, TypeError) as failure:
            operation.diagnostics.finish('failed', 'validate', failure)
            cause = failure.__cause__ if isinstance(failure, StageFailure) else failure
            if isinstance(cause, OSError):
                error = f'Cannot access the image or destination: {cause.strerror or str(cause)}. '
                error += 'Choose readable local files and a writable private folder, then retry.'
            else:
                error = str(failure) + '\nReview your selections and validate again.'
        except Exception as failure:
            operation.diagnostics.finish('failed', 'validate', failure)
            error = 'Validation could not finish. Reopen the application and retry with a stable local image.'
        if not error:
            operation.diagnostics.record_image(report)
            operation.diagnostics.finish('complete')
        save_evidence(operation.events, 'cancelled' if error == 'cancelled' else
                      'failed' if error else 'complete', error)
        self._messages.put(_ValidationFinished(worker, generation, report, identity, error, time.monotonic() - start))

    def _assemble(self, worker: object, operation: BuildOperation, image: Path,
                  destination: Path, accepted_image: dict) -> None:
        start = time.monotonic()
        result, error, cancelled = None, None, False
        try:
            result = create_package(image, destination, self._bundle, accepted_image=accepted_image,
                                    operation=operation)
        except BuildCancelled as failure:
            error, cancelled = str(failure), True
            if operation.diagnostics.outcome == 'running':
                operation.diagnostics.finish('cancelled')
        except StageFailure as failure:
            error = f'{failure.stage}: {failure}\nReview the error and validate again to retry.'
            if operation.diagnostics.outcome == 'running':
                operation.diagnostics.finish('failed', failure.stage, failure)
        except Exception as failure:
            error = ('Package creation could not finish. Check free space and folder access, '
                     'then validate again. If it continues, reinstall the complete application.')
            if operation.diagnostics.outcome == 'running':
                operation.diagnostics.finish('failed', operation.stage, failure)
        self._messages.put(_PackageFinished(worker, result, error, cancelled, time.monotonic() - start))

    def poll(self) -> WorkflowView:
        for _ in range(100):
            try:
                message = self._messages.get_nowait()
            except queue.Empty:
                break
            if message.worker is not self._worker:
                continue
            if isinstance(message, _Stage):
                if message.generation == self._generation and self._operation is not None \
                        and not self._operation.cancelled.is_set():
                    self._stage(message.event)
                continue
            self._worker = None
            self._activity = 'idle'
            self._progress = WorkflowProgress()
            if isinstance(message, _RecoveryFinished):
                failed = [item['error'] for item in message.items if item['event'] == 'failed']
                self._result = 'recovery-attention' if failed else 'none'
                self._status = ('Interrupted work needs attention' if failed else
                                'Select your image and a private destination to begin.')
                self._details = ('\n'.join(failed) if failed else
                                 'Interrupted temporary work removed. Validate again to start fresh.' if message.items else '')
            elif isinstance(message, _ValidationFinished):
                if message.generation != self._generation:
                    continue
                if message.error == 'cancelled' or (self._operation and self._operation.cancelled.is_set()):
                    self._result, self._status = 'cancelled', 'Validation cancelled'
                    self._details = 'Validate again to retry from the beginning.'
                elif message.error:
                    self._result, self._status, self._details = 'failed', 'Validation failed', message.error
                else:
                    assert message.report is not None and message.identity is not None
                    self._accepted, self._accepted_image = message.identity, message.report
                    self._result, self._status = 'validated', 'Supported image — validation passed'
                    self._details = (f'Checked required game content and whole-image allowlist in {message.seconds:.2f} seconds.\n'
                                     f'SHA-1: {message.report["sha1"]}\nSHA-256: {message.report["sha256"]}')
            else:
                self._accepted = self._accepted_image = None
                if message.error:
                    self._result = 'cancelled' if message.cancelled else 'failed'
                    self._status = 'Package creation cancelled' if message.cancelled else 'Package creation failed'
                    self._details = message.error
                else:
                    assert message.result is not None
                    report = message.result
                    self._package = Path(report['output']) / 'out' / report['package']['filename']
                    self._result, self._status = 'verified', 'Package verified — ready for manual USB installation'
                    self._details = (f'{self._package}\nSHA-256: {report["package"]["sha256"]}\n'
                                     f'Validation, assembly and fresh inspection finished in {message.seconds:.2f} seconds.\n'
                                     'Open Installation instructions for the USB steps. Remove USB after installation for play.')
        self._check_selection()
        return self.view

    def _check_selection(self) -> None:
        if self._accepted is not None and self._activity != 'creating' \
                and self._image is not None and self._destination is not None:
            try:
                require(self._accepted == (_file_identity(self._image), _file_identity(CONTRACT))
                        and not self._destination.exists() and self._destination.parent.is_dir(), 'Selection is stale')
            except (OSError, ValueError):
                self._invalidate('Selection is stale. The image, contract or destination changed. Validate again.')

    def _stage(self, event: dict) -> None:
        if event['event'] == 'progress':
            self._progress = WorkflowProgress('determinate', event['completed'], event['total'])
            self._details = f'{event["activity"]}: {event["completed"]:,} / {event["total"]:,} bytes'
        elif event['event'] == 'activity':
            self._progress = WorkflowProgress('indeterminate')
            self._details = event['activity']
        elif event['event'] == 'started':
            self._progress = WorkflowProgress('indeterminate')
            self._details = ''
            self._status = {'validate': 'Validating image again…', 'verify-program': 'Checking bundled game and tools…',
                            'prepare': 'Preparing private workspace…', 'cleanup': 'Removing unfinished workspace…',
                            'assemble': 'Creating private package…', 'inspect': 'Verifying freshly extracted package…',
                            'publish': 'Publishing verified package…'}[event['stage']]
