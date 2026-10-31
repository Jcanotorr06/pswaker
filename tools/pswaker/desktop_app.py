"""Tk presentation adapter for the Complete package workflow."""
from pathlib import Path
import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from complete_package_workflow import CompletePackageWorkflow, WorkflowView
from diagnostics import DiagnosticExportError
from installed_release import check_installation, installation_in_use


class DesktopApp:
    def __init__(self, root, bundle=None):
        self.root = root
        self.bundle = bundle or Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent / 'desktop-bundle'))
        self.workflow = CompletePackageWorkflow(self.bundle)
        self.instructions = tk.StringVar()
        self.status = tk.StringVar()
        self.details = tk.StringVar()
        self.image_text = tk.StringVar()
        self.output_text = tk.StringVar()
        self.baseline_text = tk.StringVar(value='PS4 Slim / firmware 9.00 / GoldHEN v2.4b18')
        self.program_text = tk.StringVar()
        self._progress_mode = None

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
        self.validate_button = ttk.Button(actions, text='Validate image', command=lambda: self._perform(self.workflow.validate), state='disabled')
        self.validate_button.pack(side='left')
        self.create_button = ttk.Button(actions, text='Create package', command=lambda: self._perform(self.workflow.create_package), state='disabled')
        self.create_button.pack(side='left', padx=12)
        self.cancel_button = ttk.Button(actions, text='Cancel', command=lambda: self._perform(self.workflow.cancel), state='disabled')
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
        self.render(self.workflow.view)
        root.after(100, self.poll)
        root.protocol('WM_DELETE_WINDOW', self.close)

    def _perform(self, action):
        action()
        self.render(self.workflow.view)

    def close(self):
        self.workflow.request_close()
        self.render(self.workflow.view)
        if self.workflow.view.ready_to_close:
            self.root.destroy()

    def choose_image(self):
        if not self.workflow.view.can_select:
            return
        selected = filedialog.askopenfilename(parent=self.root, title='Select your original raw disc image',
            filetypes=[('Raw GameCube image', '*.iso *.gcm *.ISO *.GCM'), ('All files', '*.*')])
        if selected:
            self.workflow.select_image(Path(selected))
            self.render(self.workflow.view)

    def choose_output(self):
        if not self.workflow.view.can_select:
            return
        selected = filedialog.askdirectory(parent=self.root, title='Select a private parent folder', mustexist=True)
        if selected:
            self.workflow.select_destination(Path(selected))
            self.render(self.workflow.view)

    def export_diagnostics(self):
        if not self.workflow.view.can_export:
            return
        selected = filedialog.asksaveasfilename(parent=self.root, title='Export private troubleshooting report',
            initialfile='PSWaker-troubleshooting.json', defaultextension='.json',
            filetypes=[('Troubleshooting report', '*.json')])
        if not selected:
            return
        try:
            exported = self.workflow.export_diagnostics(Path(selected))
        except DiagnosticExportError as error:
            messagebox.showerror('Could not export report', str(error), parent=self.root)
        else:
            if exported:
                messagebox.showinfo('Report saved locally',
                    'The report omits personal paths, raw logs, game data, keys and credentials. '
                    'It stays here until you choose to share it. It does not establish console acceptance '
                    'or redistribution clearance.', parent=self.root)

    def open_folder(self):
        view = self.workflow.view
        if view.can_open and view.package_path is not None:
            try:
                os.startfile(str(view.package_path.parent))
            except OSError:
                messagebox.showerror('Could not open folder', 'Open the verified package location shown on screen.',
                                     parent=self.root)

    def show_installation(self):
        view = self.workflow.view
        if view.can_open:
            messagebox.showinfo('Install your verified package', view.installation_instructions, parent=self.root)

    def render(self, view: WorkflowView):
        self.status.set(view.status)
        self.details.set(view.details)
        self.image_text.set(str(view.image) if view.image is not None else 'No image selected')
        self.output_text.set(str(view.destination) if view.destination is not None else 'No destination selected')
        self.program_text.set(view.program_text)
        self.instructions.set(view.installation_instructions)
        for button, enabled in [
                (self.image_button, view.can_select), (self.output_button, view.can_select),
                (self.validate_button, view.can_validate), (self.create_button, view.can_create),
                (self.cancel_button, view.can_cancel), (self.export_button, view.can_export),
                (self.open_button, view.can_open), (self.install_button, view.can_open)]:
            button.configure(state='normal' if enabled else 'disabled')
        progress = view.progress
        if progress.mode != self._progress_mode:
            self.progress.stop()
            if progress.mode != 'stopped':
                self.progress.configure(mode=progress.mode)
                if progress.mode == 'indeterminate':
                    self.progress.start()
            self._progress_mode = progress.mode
        if progress.mode == 'determinate':
            self.progress.configure(maximum=max(progress.total, 1), value=progress.completed)

    def poll(self):
        view = self.workflow.poll()
        self.render(view)
        if view.ready_to_close:
            self.root.destroy()
        else:
            self.root.after(100, self.poll)


def main():
    with installation_in_use():
        if len(sys.argv) == 3 and sys.argv[1] == '--check-installation':
            # Read-only installed acceptance probe; never changes validation policy.
            try:
                report = check_installation(Path(sys.executable).parent)
                with Path(sys.argv[2]).open('x', encoding='utf-8') as saved:
                    json.dump(report, saved, indent=2)
            except Exception:
                raise SystemExit(1) from None
            return
        root = tk.Tk()
        root.withdraw()
        try:
            if getattr(sys, 'frozen', False):
                check_installation(Path(sys.executable).parent)
            DesktopApp(root)
            root.deiconify()
            root.mainloop()
        except Exception:
            messagebox.showerror('PSWaker could not start', 'Reopen a complete application build. '
                                 'If the problem continues, reinstall the application.', parent=root)
            root.destroy()


if __name__ == '__main__':
    main()
