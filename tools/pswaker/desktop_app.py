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
from package_artifact import StageFailure
from windows_package import create_package, INSTALL_INSTRUCTIONS


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
        self.open_button = ttk.Button(actions, text='Open folder', command=self.open_folder, state='disabled')
        self.open_button.pack(side='left')
        self.install_button = ttk.Button(actions, text='Installation instructions', command=self.show_installation,
                                         state='disabled')
        self.install_button.pack(side='left', padx=12)
        self.progress = ttk.Progressbar(frame, mode='indeterminate')
        self.progress.grid(sticky='ew', pady=(16, 8))
        ttk.Label(frame, textvariable=self.status, wraplength=680, font=('Segoe UI', 10, 'bold')).grid(sticky='w')
        ttk.Label(frame, textvariable=self.details, wraplength=680, justify='left').grid(sticky='w', pady=(8, 16))
        ttk.Separator(frame).grid(sticky='ew')
        ttk.Label(frame, text='Validation runs locally. Your image is only read; nothing is uploaded.\n'
                  'Create a private complete package, then install it manually from USB. Play without USB after installation.',
                  wraplength=680).grid(sticky='w', pady=(12, 0))
        root.after(100, self.poll)

    def invalidate(self, message='Selection changed. Validate again before creating a package.'):
        self.generation += 1
        self.accepted = None
        self.accepted_image = None
        self.package = None
        self.instructions.set('')
        self.details.set('')
        self.status.set(message)
        self.refresh_actions()

    def refresh_actions(self):
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
        self.refresh_actions()
        self.status.set('Validating image… Reading and checking the entire image; please wait.')
        self.progress.start()
        threading.Thread(target=self.validate, args=(self.generation, self.image, self.output), daemon=True).start()

    def validate(self, generation, image, output):
        start = time.monotonic()
        report, identity, error = None, None, None
        try:
            identity = (file_identity(image), file_identity(CONTRACT))
            report = validate_selection(image, output)
            require(identity == (file_identity(image), file_identity(CONTRACT)),
                    'The image or validation contract changed during validation. Select a stable local file and retry.')
        except OSError as failure:
            error = f'Cannot access the image or destination: {failure.strerror or str(failure)}. '
            error += 'Choose readable local files and a writable private folder, then retry.'
        except (ValueError, KeyError, TypeError) as failure:
            error = str(failure) + '\nReview your selections and validate again.'
        except Exception:
            error = 'Validation could not finish. Reopen the application and retry with a stable local image.'
        self.results.put((generation, report, identity, error, time.monotonic() - start))

    def start_package(self):
        if self.busy or not self.accepted or self.image is None or self.output is None:
            return
        self.busy = self.packaging = True
        self.package = None
        self.details.set('')
        self.status.set('Preparing package…')
        self.progress.start()
        self.refresh_actions()
        threading.Thread(target=self.assemble, args=(self.image, self.output, self.accepted_image), daemon=True).start()

    def assemble(self, image, output, accepted_image):
        start = time.monotonic()
        try:
            result = create_package(image, output, self.bundle, accepted_image=accepted_image,
                                    observe=lambda event: self.package_results.put(('stage', event)))
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
        while True:
            try:
                event, result = self.package_results.get_nowait()
            except queue.Empty:
                break
            if event == 'stage':
                if result['event'] == 'started':
                    self.status.set({'validate': 'Validating image again…', 'verify-program': 'Checking bundled game and tools…',
                                     'assemble': 'Creating private package…', 'inspect': 'Verifying freshly extracted package…',
                                     'publish': 'Publishing verified package…'}[result['stage']])
                continue
            self.busy = self.packaging = False
            self.accepted = self.accepted_image = None
            self.progress.stop()
            if event == 'failure':
                self.status.set('Package creation failed')
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
        try:
            generation, report, identity, error, seconds = self.results.get_nowait()
        except queue.Empty:
            pass
        else:
            self.busy = False
            self.progress.stop()
            if generation == self.generation:
                if error:
                    self.status.set('Validation failed')
                    self.details.set(error)
                else:
                    self.accepted = identity
                    self.accepted_image = report
                    self.status.set('Supported image — validation passed')
                    self.details.set(f'Checked required game content and whole-image allowlist in {seconds:.2f} seconds.\n'
                                     f'SHA-1: {report["sha1"]}\nSHA-256: {report["sha256"]}')
            self.refresh_actions()
        self.poll_package()
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
