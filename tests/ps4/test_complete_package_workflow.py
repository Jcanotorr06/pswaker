"""Workflow transitions through the desktop's interface, without Tk or native tools."""
from collections.abc import Callable
from dataclasses import FrozenInstanceError
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/pswaker'))
from build_operation import progress
from complete_package_workflow import CompletePackageWorkflow
from diagnostics import DiagnosticExportError
from package_artifact import StageFailure, Stages


class HeldWorkers:
    """Run the work the workflow actually launches; never fabricate its messages."""
    def __init__(self):
        self.jobs: list[Callable[[], None]] = []

    def start(self, work: Callable[[], None]) -> None:
        self.jobs.append(work)

    def finish(self) -> None:
        self.jobs.pop(0)()


class CompletePackageWorkflowTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='pswaker-workflow-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.image = self.root / 'owner.iso'
        self.image.write_bytes(b'data-free workflow fixture')
        self.contract = self.root / 'contract.json'
        self.contract.write_text('{}')
        self.bundle = self.root / 'bundle'
        (self.bundle / 'program/stage').mkdir(parents=True)
        (self.bundle / 'program/program-release.json').write_text(json.dumps(
            {'schema': 1, 'kind': 'game', 'build_id': 'synthetic-program'}))
        (self.bundle / 'program/stage/build-info.json').write_text(json.dumps(
            {'app_version': '01.23', 'program_build_id': 'synthetic-program'}))
        (self.bundle / 'desktop-release.json').write_text(json.dumps({'app_version': '0.1.0'}))
        self.workers = HeldWorkers()
        self.enterContext(patch.dict(os.environ, LOCALAPPDATA=str(self.root / 'local-state')))
        self.enterContext(patch('complete_package_workflow._start_worker', self.workers.start))
        self.enterContext(patch('complete_package_workflow.CONTRACT', self.contract))
        self.recovery = self.enterContext(patch('complete_package_workflow.recover_abandoned', return_value=[]))
        self.validation = self.enterContext(patch('complete_package_workflow.validate_selection',
                                                 side_effect=self.check_image))
        self.creation = self.enterContext(patch('complete_package_workflow.create_package',
                                               side_effect=self.make_package))
        self.workflow = CompletePackageWorkflow(self.bundle)

    def check_image(self, image, destination):
        data = image.read_bytes()
        return {'sha1': hashlib.sha1(data).hexdigest(), 'sha256': hashlib.sha256(data).hexdigest()}

    def make_package(self, image, destination, bundle, *, accepted_image, operation):
        package = {'filename': 'synthetic.pkg', 'sha256': hashlib.sha256(b'fixture package').hexdigest()}
        with operation.bind(), Stages(operation.emit)('assemble'):
            with tempfile.TemporaryDirectory(dir=destination.parent) as directory:
                work = Path(directory) / 'work'
                (work / 'out').mkdir(parents=True)
                (work / 'out' / package['filename']).write_bytes(b'fixture package')
                operation.publish(work, destination)
        operation.diagnostics.record_package(package)
        operation.diagnostics.finish('complete')
        return {'output': str(destination), 'package': package}

    def selected(self):
        if self.workflow.view.activity == 'recovering':
            self.workers.finish()
            self.workflow.poll()
        self.workflow.select_image(self.image)
        self.workflow.select_destination(self.root)
        return self.workflow

    def validated(self):
        workflow = self.selected()
        workflow.validate()
        self.workers.finish()
        self.assertEqual(workflow.poll().result, 'validated')
        return workflow

    def test_recovery_owns_work_until_its_completion_is_consumed(self):
        workflow = self.workflow
        workflow.select_image(self.image)
        workflow.select_destination(self.root)
        self.assertEqual(workflow.view.activity, 'recovering')
        self.assertFalse(workflow.view.can_validate)
        workflow.validate()
        self.assertEqual(len(self.workers.jobs), 1)
        self.workers.finish()
        self.assertTrue(workflow.view.busy)
        self.assertTrue(workflow.poll().can_validate)
        self.assertFalse(workflow.view.can_export)

    def test_recovery_failure_is_advisory_and_close_waits_for_recovery(self):
        self.recovery.side_effect = PermissionError('controlled unavailable record')
        self.workers.finish()
        view = self.workflow.poll()
        self.assertEqual(view.result, 'recovery-attention')
        self.assertIn('controlled unavailable record', view.details)
        self.workflow.select_image(self.image)
        self.workflow.select_destination(self.root)
        self.assertTrue(self.workflow.view.can_validate)

        waiting = CompletePackageWorkflow(self.bundle)
        waiting.request_close()
        waiting.select_image(self.image)
        self.assertIsNone(waiting.view.image)
        self.assertFalse(waiting.view.ready_to_close)
        self.workers.finish()
        self.assertTrue(waiting.poll().ready_to_close)

    def test_view_and_progress_are_immutable_and_retained_views_stay_unchanged(self):
        workflow = self.selected()
        before = workflow.view
        with self.assertRaises(FrozenInstanceError):
            setattr(before, 'status', 'changed')
        with self.assertRaises(FrozenInstanceError):
            setattr(before.progress, 'total', 10)
        workflow.validate()
        self.assertFalse(before.busy)
        self.assertEqual(workflow.view.activity, 'validating')

    def test_validation_enables_creation_and_diagnostics_only_after_completion(self):
        workflow = self.selected()
        self.assertEqual(workflow.view.destination, self.root / 'PSWaker-01.23')
        workflow.validate()
        workflow.validate()
        workflow.create_package()
        self.assertEqual(len(self.workers.jobs), 1)
        self.assertFalse(workflow.view.can_create)
        self.assertFalse(workflow.view.can_export)
        self.workers.finish()
        self.assertTrue(workflow.view.busy)
        view = workflow.poll()
        self.assertEqual(view.result, 'validated')
        self.assertTrue(view.can_create)
        self.assertTrue(view.can_export)
        self.assertEqual(view.progress.mode, 'stopped')

    def test_selection_change_rejects_queued_success_and_holds_the_active_slot(self):
        workflow = self.selected()
        workflow.validate()
        self.workers.finish()  # Success is queued, but has not been accepted.
        other = self.root / 'another.iso'
        other.write_bytes(b'new selection')
        workflow.select_image(other)
        changed = workflow.view
        workflow.validate()
        self.assertFalse(self.workers.jobs)
        self.assertTrue(changed.busy)
        self.assertFalse(changed.can_create)
        view = workflow.poll()
        self.assertEqual(view.image, other)
        self.assertEqual(view.status, changed.status)
        self.assertEqual(view.details, '')
        self.assertTrue(view.can_validate)
        self.assertFalse(view.can_create)
        workflow.validate()
        self.workers.finish()
        self.assertTrue(workflow.poll().can_create)

    def test_destination_change_during_validation_discards_old_result(self):
        workflow = self.selected()
        workflow.validate()
        other = self.root / 'other-output'
        other.mkdir()
        workflow.select_destination(other)
        self.workers.finish()
        view = workflow.poll()
        self.assertEqual(view.destination, other / 'PSWaker-01.23')
        self.assertEqual(view.result, 'stale')
        self.assertFalse(view.can_create)
        self.assertTrue(view.can_validate)

    def test_cancel_queued_validation_success_requires_fresh_validation(self):
        workflow = self.selected()
        workflow.validate()
        self.workers.finish()
        workflow.cancel()
        self.assertTrue(workflow.view.busy)
        self.assertFalse(workflow.view.can_cancel)
        self.assertEqual(workflow.poll().result, 'cancelled')
        self.assertFalse(workflow.view.can_create)
        workflow.validate()
        self.workers.finish()
        self.assertEqual(workflow.poll().result, 'validated')

    def test_close_waits_for_cancelled_validation_and_suppresses_new_work(self):
        workflow = self.selected()
        workflow.validate()
        workflow.request_close()
        workflow.validate()
        workflow.select_destination(self.root / 'ignored')
        self.assertFalse(workflow.view.ready_to_close)
        self.assertFalse(workflow.view.can_select)
        self.workers.finish()
        self.assertTrue(workflow.poll().ready_to_close)
        self.assertEqual(workflow.view.result, 'cancelled')
        self.assertFalse(workflow.view.can_validate)

    def test_validation_failure_and_retry_keep_failure_report_until_next_attempt(self):
        workflow = self.selected()
        self.validation.side_effect = ValueError('controlled invalid input')
        workflow.validate()
        self.workers.finish()
        self.assertEqual(workflow.poll().result, 'failed')
        failed = workflow.view
        self.assertTrue(failed.can_export)
        first = self.root / 'first.json'
        self.assertTrue(workflow.export_diagnostics(first))
        workflow.select_destination(self.root)
        second = self.root / 'second.json'
        workflow.export_diagnostics(second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.validation.side_effect = self.check_image
        workflow.validate()
        self.assertFalse(workflow.export_diagnostics(self.root / 'running.json'))
        self.workers.finish()
        self.assertEqual(workflow.poll().result, 'validated')
        third = self.root / 'third.json'
        workflow.export_diagnostics(third)
        old, new = json.loads(first.read_text()), json.loads(third.read_text())
        self.assertEqual(old['outcome'], 'failed')
        self.assertEqual(new['outcome'], 'complete')
        self.assertNotEqual(old['operation_id'], new['operation_id'])

    def test_export_failure_preserves_result_and_does_not_replace_owner_file(self):
        workflow = self.validated()
        before = workflow.view
        original = self.image.read_bytes()
        with self.assertRaises(DiagnosticExportError):
            workflow.export_diagnostics(self.image)
        self.assertEqual(self.image.read_bytes(), original)
        self.assertEqual(workflow.view, before)
        self.assertFalse(list(self.root.glob('.diagnostic-*')))

    def test_changed_image_contract_or_destination_invalidates_accepted_selection(self):
        for change in ['image', 'contract', 'destination', 'parent']:
            with self.subTest(change=change):
                workflow = self.validated()
                destination = workflow.view.destination
                assert destination is not None
                before_image, before_contract = self.image.read_bytes(), self.contract.read_bytes()
                if change == 'image':
                    self.image.write_bytes(before_image + b'changed')
                elif change == 'contract':
                    self.contract.write_bytes(before_contract + b'changed')
                elif change == 'destination':
                    destination.mkdir()
                else:
                    parent = self.root / 'removed-parent'
                    parent.mkdir()
                    workflow.select_destination(parent)
                    workflow.validate()
                    self.workers.finish()
                    workflow.poll()
                    parent.rmdir()
                # Creation rechecks freshness even if Tk has not polled yet.
                workflow.create_package()
                self.assertEqual(workflow.view.result, 'stale')
                self.assertFalse(workflow.view.can_create)
                self.assertFalse(self.workers.jobs)
                self.creation.assert_not_called()
                self.image.write_bytes(before_image)
                self.contract.write_bytes(before_contract)
                if change == 'destination':
                    destination.rmdir()

    def test_image_change_during_validation_cannot_be_accepted(self):
        workflow = self.selected()
        def changed(image, destination):
            report = self.check_image(image, destination)
            image.write_bytes(b'changed while reading')
            return report
        self.validation.side_effect = changed
        workflow.validate()
        self.workers.finish()
        self.assertEqual(workflow.poll().result, 'failed')
        self.assertFalse(workflow.view.can_create)
        self.assertIn('changed during validation', workflow.view.details)

    def test_poll_invalidates_a_disappeared_image_without_another_action(self):
        workflow = self.validated()
        self.image.unlink()
        view = workflow.poll()
        self.assertEqual(view.result, 'stale')
        self.assertEqual(view.details, '')
        self.assertFalse(view.can_create)
        self.assertTrue(view.can_validate)

    def test_missing_bundle_release_disables_creation_but_allows_image_validation(self):
        workflow = self.validated()
        (self.bundle / 'desktop-release.json').unlink()
        self.assertFalse(workflow.view.can_create)
        workflow.create_package()
        self.assertFalse(self.workers.jobs)
        self.assertTrue(workflow.view.can_validate)

    def test_creation_locks_selection_and_returns_verified_package_and_instructions(self):
        workflow = self.validated()
        workflow.create_package()
        before = workflow.view
        workflow.select_image(self.root / 'ignored.iso')
        workflow.select_destination(self.root / 'ignored')
        workflow.validate()
        workflow.create_package()
        self.assertEqual(workflow.view, before)
        self.assertFalse(before.can_select)
        self.assertFalse(before.can_export)
        self.assertEqual(len(self.workers.jobs), 1)
        self.workers.finish()
        view = workflow.poll()
        self.assertEqual(view.result, 'verified')
        assert view.package_path is not None
        self.assertEqual(view.package_path.read_bytes(), b'fixture package')
        self.assertIn('USB', view.installation_instructions)
        self.assertTrue(view.can_open)
        self.assertTrue(view.can_export)
        self.assertFalse(view.can_create)

    def test_cancelled_creation_waits_for_completion_and_requires_fresh_validation(self):
        workflow = self.validated()
        workflow.create_package()
        workflow.cancel()
        workflow.validate()
        self.assertTrue(workflow.view.busy)
        self.assertEqual(len(self.workers.jobs), 1)
        self.workers.finish()
        self.assertEqual(workflow.poll().result, 'cancelled')
        self.assertTrue(workflow.view.can_validate)
        self.assertFalse(workflow.view.can_create)
        self.assertFalse(workflow.view.can_open)
        self.assertEqual(workflow.view.installation_instructions, '')
        self.assertTrue(workflow.view.can_export)

    def test_committed_publication_remains_successful_after_cancel_and_close(self):
        workflow = self.validated()
        workflow.create_package()
        self.workers.finish()  # The real BuildOperation has committed its rename.
        workflow.cancel()
        workflow.request_close()
        self.assertFalse(workflow.view.ready_to_close)
        view = workflow.poll()
        self.assertTrue(view.ready_to_close)
        self.assertEqual(view.result, 'verified')
        assert view.package_path is not None
        self.assertTrue(view.package_path.is_file())

    def test_package_failure_requires_revalidation_and_preserves_previous_files(self):
        workflow = self.validated()
        previous = self.root / 'previous.pkg'
        previous.write_bytes(b'owner package')
        self.creation.side_effect = StageFailure('inspect', 'controlled inspection failure')
        workflow.create_package()
        self.workers.finish()
        view = workflow.poll()
        self.assertEqual(view.result, 'failed')
        self.assertIn('inspect:', view.details)
        self.assertTrue(view.can_validate)
        self.assertFalse(view.can_create)
        self.assertIsNone(view.package_path)
        self.assertTrue(view.can_export)
        self.assertEqual(previous.read_bytes(), b'owner package')
        self.creation.side_effect = self.make_package
        workflow.create_package()
        self.assertFalse(self.workers.jobs)
        workflow.validate()
        self.workers.finish()
        self.assertTrue(workflow.poll().can_create)
        workflow.create_package()
        self.workers.finish()
        self.assertEqual(workflow.poll().result, 'verified')
        self.assertEqual(previous.read_bytes(), b'owner package')

    def test_unexpected_package_failure_is_terminal_and_exports_safe_diagnostics(self):
        workflow = self.validated()
        self.creation.side_effect = RuntimeError('PRIVATE-UNEXPECTED-FAILURE')
        workflow.create_package()
        self.workers.finish()
        self.assertEqual(workflow.poll().result, 'failed')
        self.assertNotIn('PRIVATE-UNEXPECTED-FAILURE', workflow.view.details)
        target = self.root / 'unexpected.json'
        self.assertTrue(workflow.export_diagnostics(target))
        contents = target.read_text()
        report = json.loads(contents)
        self.assertEqual(report['outcome'], 'failed')
        self.assertEqual(report['failure']['category'], 'unexpected-error')
        self.assertNotIn('PRIVATE-UNEXPECTED-FAILURE', contents)

    def test_progress_and_cancellation_are_observable_without_tk_or_sleep(self):
        workflow = self.selected()
        entered, release = threading.Event(), threading.Event()
        def paused(image, destination):
            progress('Reading fixture', 4, 10)
            entered.set()
            if not release.wait(10):
                raise AssertionError('Test did not release validation')
            return self.check_image(image, destination)
        self.validation.side_effect = paused
        workflow.validate()
        worker = threading.Thread(target=self.workers.jobs.pop(0))
        worker.start()
        try:
            self.assertTrue(entered.wait(10))
            view = workflow.poll()
            self.assertEqual(view.progress.mode, 'determinate')
            self.assertEqual((view.progress.completed, view.progress.total), (4, 10))
            workflow.cancel()
            self.assertTrue(workflow.view.busy)
            self.assertFalse(workflow.view.can_validate)
        finally:
            release.set()
            worker.join(timeout=10)
        self.assertFalse(worker.is_alive())
        self.assertEqual(workflow.poll().result, 'cancelled')


if __name__ == '__main__':
    unittest.main()
