"""Local Windows desktop adapter for the production packaging validation boundary."""
from pathlib import Path
import os
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from disc_image import CONTRACT, require
from package_validation import validate_selection
from program_payload import bundled_program
from package_artifact import StageFailure, Stages
from windows_package import create_package, INSTALL_INSTRUCTIONS
from build_operation import BuildCancelled, BuildOperation
from owned_work import recover_abandoned, save_evidence
from diagnostics import DiagnosticExportError


def file_identity(path):
    stat = path.stat()
    return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)


class DesktopApp:
    def __init__(self, root, bundle=None):
        self.root = root
        self.image = None
        self.output = None
        self.generation = 0
        self.busy = False
        self.operation = None
        self.closing = False
        self.accepted = None
        self.accepted_image = None
        self.packaging = False
        self.package = None
        self.package_results = queue.Queue()
        self.instructions = tk.StringVar()
        self.results = queue.Queue()
        self.status = tk.StringVar(value='Select your image and a private destination to begin.')
        self.details = tk.StringVar()
        self.image_text = tk.StringVar(value='No image selected')
        self.output_text = tk.StringVar(value='No destination selected')
        self.baseline_text = tk.StringVar(value='PS4 Slim / firmware 9.00 / GoldHEN v2.4b18')
        self.program_text = tk.StringVar()
        self.version = None
        self.bundle = bundle or Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent / 'desktop-bundle'))
        try:
            self.version, build_id = bundled_program(self.bundle)
            self.program_text.set(f'Bundled game program {self.version} · build {build_id}')
        except (OSError, ValueError, KeyError, TypeError):
            self.program_text.set('Bundled game program unavailable — use a complete application build.')

        root.title('PSWaker — Create your complete package')
        root.minsize(740, 600)
        frame = ttk.Frame(root, padding=28)
        frame.pack(fill='both', expand=True)
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text='PSWaker', font=('Segoe UI', 26, 'bold')).grid(sticky='w')
        ttk.Label(frame, text='Prepare your own game image', font=('Segoe UI', 14)).grid(sticky='w', pady=(0, 18))
        ttk.Label(frame, textvariable=self.program_text, wraplength=680).grid(sticky='w')
        ttk.Label(frame, textvariable=self.baseline_text).grid(sticky='w', pady=(4, 18))
        ttk.Separator(frame).grid(sticky='ew', pady=(0, 16))
        ttk.Label(frame, text='1. Owner-supplied image', font=('Segoe UI', 11, 'bold')).grid(sticky='w')
        ttk.Label(frame, text='Full raw ISO/GCM · USA GZLE01 · disc 0 · revision 0 · 1,459,978,240 bytes').grid(sticky='w')
        ttk.Entry(frame, textvariable=self.image_text, state='readonly').grid(sticky='ew', pady=(8, 6))
        self.image_button = ttk.Button(frame, text='Select image…', command=self.choose_image)
        self.image_button.grid(sticky='w', pady=(0, 16))
        ttk.Label(frame, text='2. Private output folder', font=('Segoe UI', 11, 'bold')).grid(sticky='w')
        ttk.Label(frame, text='Choose a parent folder. The new package folder shown below must not already exist.').grid(sticky='w')
        ttk.Entry(frame, textvariable=self.output_text, state='readonly').grid(sticky='ew', pady=(8, 6))
        self.output_button = ttk.Button(frame, text='Select destination…', command=self.choose_output)
        self.output_button.grid(sticky='w', pady=(0, 18))
        actions = ttk.Frame(frame)
        actions.grid(sticky='ew')
        self.validate_button = ttk.Button(actions, text='Validate image', command=self.start_validation, state='disabled')
        self.validate_button.pack(side='left')
        self.create_button = ttk.Button(actions, text='Create package', command=self.start_package, state='disabled')
        self.create_button.pack(side='left', padx=12)
        self.cancel_button = ttk.Button(actions, text='Cancel', command=self.cancel, state='disabled')
        self.cancel_button.pack(side='left', padx=(0, 12))
        self.open_button = ttk.Button(actions, text='Open folder', command=self.open_folder, state='disabled')
        self.open_button.pack(side='left')
        self.install_button = ttk.Button(actions, text='Installation instructions', command=self.show_installation,
                                         state='disabled')
        self.install_button.pack(side='left', padx=12)
        self.progress = ttk.Progressbar(frame, mode='indeterminate')
        self.progress.grid(sticky='ew', pady=(16, 8))
        ttk.Label(frame, textvariable=self.status, wraplength=680, font=('Segoe UI', 10, 'bold')).grid(sticky='w')
        ttk.Label(frame, textvariable=self.details, wraplength=680, justify='left').grid(sticky='w', pady=(8, 16))
        self.export_button = ttk.Button(frame, text='Export troubleshooting report…',
                                        command=self.export_diagnostics, state='disabled')
        self.export_button.grid(sticky='w', pady=(0, 12))
        ttk.Separator(frame).grid(sticky='ew')
        ttk.Label(frame, text='Validation runs locally. Your image is only read; nothing is uploaded.\n'
                  'Create a private complete package, then install it manually from USB. Play without USB after installation.',
                  wraplength=680).grid(sticky='w', pady=(12, 0))
        root.after(100, self.poll)
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.busy = True
        self.status.set('Checking interrupted work…')
        self.refresh_actions()
        threading.Thread(target=self.recover, daemon=True).start()

    def recover(self):
        try:
            result = recover_abandoned()
        except OSError as error:
            result = [{'event': 'failed', 'error': str(error)}]
        self.package_results.put(('recovered', result))

    def cancel(self):
        if self.operation and self.operation.cancel():
            self.status.set('Cancelling… Waiting for active work and cleanup to finish.')
            self.cancel_button.configure(state='disabled')

    def close(self):
        if self.busy:
            self.closing = True
            self.cancel()
        else:
            self.root.destroy()

    def invalidate(self, message='Selection changed. Validate again before creating a package.'):
        if self.busy and not self.packaging and self.operation:
            self.operation.cancel()
        self.generation += 1
        self.accepted = None
        self.accepted_image = None
        self.package = None
        self.instructions.set('')
        self.details.set('')
        self.status.set(message)
        self.refresh_actions()

    def refresh_actions(self):
        self.export_button.configure(state='normal' if self.operation and not self.busy
                                     and self.operation.diagnostics.outcome != 'running' else 'disabled')
        self.cancel_button.configure(state='normal' if self.busy and self.operation
                                     and not self.operation.cancelled.is_set() else 'disabled')
        self.validate_button.configure(state='normal' if self.image and self.output and not self.busy else 'disabled')
        self.create_button.configure(state='normal' if self.accepted and not self.busy and self.version
                                     and (self.bundle / 'desktop-release.json').is_file() else 'disabled')
        for button in [self.image_button, self.output_button]:
            button.configure(state='disabled' if self.packaging else 'normal')
        for button in [self.open_button, self.install_button]:
            button.configure(state='normal' if self.package and not self.busy else 'disabled')

    def choose_image(self):
        if self.packaging:
            return
        selected = filedialog.askopenfilename(parent=self.root, title='Select your original raw disc image',
            filetypes=[('Raw GameCube image', '*.iso *.gcm *.ISO *.GCM'), ('All files', '*.*')])
        if selected:
            self.image = Path(selected)
            self.image_text.set(str(self.image))
            self.invalidate()

    def choose_output(self):
        if self.packaging:
            return
        selected = filedialog.askdirectory(parent=self.root, title='Select a private parent folder', mustexist=True)
        if selected:
            self.output = Path(selected) / ('PSWaker-' + (self.version or 'package'))
            self.output_text.set(str(self.output))
            self.invalidate()

    def start_validation(self):
        if self.busy or self.image is None or self.output is None:
            return
        self.invalidate()
        self.busy = True
        generation = self.generation
        self.operation = BuildOperation(lambda event: self.package_results.put(('stage', dict(event, generation=generation))))
        self.refresh_actions()
        self.status.set('Validating image… Reading and checking the entire image; please wait.')
        self.progress.stop()
        self.progress.configure(mode='indeterminate')
        self.progress.start()
        threading.Thread(target=self.validate, args=(self.generation, self.image, self.output), daemon=True).start()

    def validate(self, generation, image, output):
        start = time.monotonic()
        report, identity, error = None, None, None
        operation = self.operation
        assert operation is not None
        try:
            operation.diagnostics.capture_bundle(self.bundle)
            with operation.bind(), Stages(operation.emit)('validate'):
                identity = (file_identity(image), file_identity(CONTRACT))
                report = validate_selection(image, output)
                require(identity == (file_identity(image), file_identity(CONTRACT)),
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
        self.results.put((generation, report, identity, error, time.monotonic() - start))

    def export_diagnostics(self):
        if self.busy or self.operation is None or self.operation.diagnostics.outcome == 'running':
            return
        selected = filedialog.asksaveasfilename(parent=self.root, title='Export private troubleshooting report',
            initialfile='PSWaker-troubleshooting.json', defaultextension='.json',
            filetypes=[('Troubleshooting report', '*.json')])
        if not selected:
            return
        try:
            self.operation.diagnostics.export(Path(selected))
        except DiagnosticExportError as error:
            messagebox.showerror('Could not export report', str(error), parent=self.root)
        else:
            messagebox.showinfo('Report saved locally',
                'The report omits personal paths, raw logs, game data, keys and credentials. '
                'It stays here until you choose to share it. It does not establish console acceptance '
                'or redistribution clearance.', parent=self.root)

    def start_package(self):
        if self.busy or not self.accepted or self.image is None or self.output is None:
            return
        self.busy = self.packaging = True
        self.generation += 1
        generation = self.generation
        self.operation = BuildOperation(lambda event: self.package_results.put(('stage', dict(event, generation=generation))))
        self.package = None
        self.instructions.set('')
        self.details.set('')
        self.status.set('Preparing package…')
        self.progress.start()
        self.refresh_actions()
        threading.Thread(target=self.assemble, args=(self.image, self.output, self.accepted_image), daemon=True).start()

    def assemble(self, image, output, accepted_image):
        start = time.monotonic()
        try:
            result = create_package(image, output, self.bundle, accepted_image=accepted_image,
                                    operation=self.operation)
        except BuildCancelled as failure:
            self.package_results.put(('cancelled', str(failure)))
        except StageFailure as failure:
            self.package_results.put(('failure', f'{failure.stage}: {failure}\nReview the error and validate again to retry.'))
        except Exception:
            self.package_results.put(('failure', 'Package creation could not finish. Check free space and folder access, '
                                      'then validate again. If it continues, reinstall the complete application.'))
        else:
            self.package_results.put(('complete', (result, time.monotonic() - start)))

    def open_folder(self):
        if self.package:
            try:
                os.startfile(str(self.package.parent))
            except OSError:
                messagebox.showerror('Could not open folder', 'Open the verified package location shown on screen.',
                                     parent=self.root)

    def show_installation(self):
        if self.package:
            messagebox.showinfo('Install your verified package', self.instructions.get(), parent=self.root)

    def poll_package(self):
        for _ in range(100):
            try:
                event, result = self.package_results.get_nowait()
            except queue.Empty:
                break
            if event == 'recovered':
                self.busy = False
                failed = [item['error'] for item in result if item['event'] == 'failed']
                self.status.set('Interrupted work needs attention' if failed else
                                'Select your image and a private destination to begin.')
                self.details.set('\n'.join(failed) if failed else
                                 'Interrupted temporary work removed. Validate again to start fresh.' if result else '')
                self.refresh_actions()
                continue
            if event == 'stage':
                if not self.busy or result.get('generation', self.generation) != self.generation:
                    continue
                if self.operation and self.operation.cancelled.is_set():
                    continue
                if result['event'] == 'progress':
                    self.progress.stop()
                    self.progress.configure(mode='determinate', maximum=max(result['total'], 1),
                                            value=result['completed'])
                    self.details.set(f'{result["activity"]}: {result["completed"]:,} / {result["total"]:,} bytes')
                if result['event'] == 'activity':
                    self.progress.stop()
                    self.progress.configure(mode='indeterminate')
                    self.progress.start()
                    self.details.set(result['activity'])
                if result['event'] == 'started':
                    self.progress.stop()
                    self.progress.configure(mode='indeterminate')
                    self.progress.start()
                    self.details.set('')
                    self.status.set({'validate': 'Validating image again…', 'verify-program': 'Checking bundled game and tools…',
                                     'prepare': 'Preparing private workspace…', 'cleanup': 'Removing unfinished workspace…',
                                     'assemble': 'Creating private package…', 'inspect': 'Verifying freshly extracted package…',
                                     'publish': 'Publishing verified package…'}[result['stage']])
                continue
            self.busy = self.packaging = False
            self.accepted = self.accepted_image = None
            self.progress.stop()
            if event in {'failure', 'cancelled'}:
                self.status.set('Package creation cancelled' if event == 'cancelled' else 'Package creation failed')
                self.details.set(result)
            else:
                report, seconds = result
                self.package = Path(report['output']) / 'out' / report['package']['filename']
                self.status.set('Package verified — ready for manual USB installation')
                self.details.set(f'{self.package}\nSHA-256: {report["package"]["sha256"]}\n'
                                 f'Validation, assembly and fresh inspection finished in {seconds:.2f} seconds.\n'
                                 'Open Installation instructions for the USB steps. Remove USB after installation for play.')
                self.instructions.set(INSTALL_INSTRUCTIONS)
            self.refresh_actions()

    def poll(self):
        self.poll_package()
        try:
            generation, report, identity, error, seconds = self.results.get_nowait()
        except queue.Empty:
            pass
        else:
            self.busy = False
            self.progress.stop()
            if generation == self.generation:
                if error == 'cancelled' or (self.operation and self.operation.cancelled.is_set()):
                    self.status.set('Validation cancelled')
                    self.details.set('Validate again to retry from the beginning.')
                elif error:
                    self.status.set('Validation failed')
                    self.details.set(error)
                else:
                    self.accepted = identity
                    self.accepted_image = report
                    self.status.set('Supported image — validation passed')
                    self.details.set(f'Checked required game content and whole-image allowlist in {seconds:.2f} seconds.\n'
                                     f'SHA-1: {report["sha1"]}\nSHA-256: {report["sha256"]}')
            self.refresh_actions()
        if self.closing and not self.busy:
            self.root.destroy()
            return
        if self.accepted and not self.packaging and self.image is not None and self.output is not None:
            try:
                require(self.accepted == (file_identity(self.image), file_identity(CONTRACT))
                        and not self.output.exists() and self.output.parent.is_dir(), 'Selection is stale')
            except (OSError, ValueError):
                self.invalidate('Selection is stale. The image, contract or destination changed. Validate again.')
        self.root.after(100, self.poll)


def main():
    root = tk.Tk()
    try:
        DesktopApp(root)
        root.mainloop()
    except Exception:
        messagebox.showerror('PSWaker could not start', 'Reopen a complete application build. '
                             'If the problem continues, reinstall the application.', parent=root)
        root.destroy()


if __name__ == '__main__':
    main()
