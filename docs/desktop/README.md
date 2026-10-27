# Windows image validation

Issue [#41](https://github.com/Jcanotorr06/pswaker/issues/41) provides the first
desktop step of [#39](https://github.com/Jcanotorr06/pswaker/issues/39): select an
owner-supplied image and private output folder, then validate locally. Package
creation remains disabled in this build; Windows assembly and the per-user
installer are separate tickets. This is a private development build, not a
public release or console acceptance result.

## Desktop workflow

Open `PSWaker.exe` from the complete application folder. It displays the version
and compiled build identity of its bundled game program and the single supported
baseline: **PS4 Slim / firmware 9.00 / GoldHEN v2.4b18**. The consumer does not
select a program, SDK, build root, ELF, console identity or configuration.

1. Select your own full raw `.iso` or `.gcm` image. Uppercase extensions work.
2. Select a private parent folder outside the application/source checkout. The
   screen shows the proposed new `PSWaker-NN.NN` output directory. It must not
   already exist; previous completed packages are preserved.
3. Select **Validate image**. The interface stays responsive while a worker
   reads and checks the image. The progress bar indicates activity, with no
   invented percentage. Success shows measured validation duration and image
   SHA-1/SHA-256. Failure gives an explanation and a retry action.

Selecting another image/destination invalidates the previous result, including
a late result from work already running. Changes to the image, validation
contract or destination detected after success mark the selection stale. File
identity checks support this feedback; they are not a validation cache or an
authorization to package. The assembly operation always validates the image
again and validates the copied image before proceeding.

All validation uses `package_validation.validate_selection`, also used by
`complete-package.py` assembly. That boundary calls the existing
`disc_image.validate` production validator. The contract is unchanged: USA
GZLE01, disc 0, revision 0, exactly **1,459,978,240 bytes**, GameCube header,
FST/DOL structure and bounds, pinned required DOL/REL hashes and both existing
whole-image SHA-1 fingerprints:

- `0289e70f470dc758c73be9b8bcd8c865fb82d8ae`
- `6b5f06c10d50ebb4099cded88217eb71e5bfbb4a`

Renaming compressed content or changing labels cannot bypass these checks.
The source image is opened only for reading. The destination check writes and
removes only an application-owned temporary access probe, and creates no package
folder. No accounts, telemetry, uploads, automatic downloads or network service
are used. No contract override, synthetic mode or arbitrary program selector is
shipped. See [the content contract](../ps4/COMPLETE-PACKAGES.md).

## Implementation decision

Use **CPython 3.12 x64, Tkinter/ttk and a PyInstaller one-folder Windows build**.
Tkinter reuses the Python standard-library validator directly and provides native
file/folder dialogs without a browser server or a second content-policy
implementation. The worker communicates with the UI through a queue; only the
UI thread touches Tk widgets. Hashing runs locally in bounded chunks, with the
existing bounded required-content decompression.

PyInstaller bundles Python, Tcl/Tk and their required runtime files alongside the
windowed executable. Consumers do not need Python, pip, a checkout, WSL, an SDK
or a terminal. [PyInstaller documents Tkinter support and OS-specific
bundling](https://pyinstaller.org/en/stable/operating-mode.html); the
[windowed/one-folder options](https://pyinstaller.org/en/stable/usage.html) keep
the runtime closure together for inspection and later installer integration.
The [CPython Windows documentation](https://docs.python.org/3.12/using/windows.html)
describes the runtime and bundled Tcl/Tk components.

Windows 10 x64 and Windows 11 x64 are the targets. A subsequent installer can
place this folder under the ordinary user's local application directory and
create shortcuts without requiring administrator rights or downloading a
runtime. This issue supplies the folder build, not that installer. No PS4
runtime, renderer, installed-content path or application identity changes.
Program/module redistribution review and clean-machine Windows acceptance
remain required by #39.

## Maintainer preparation

These are developer build commands, never consumer instructions. Use x64
CPython with Tcl/Tk on Windows. Prepare a private, data-free, verified game
[program release](../ps4/COMPLETE-PACKAGES.md#relocatable-program-release) using
#40 first. Do not substitute a diagnostic or include owner game data.

```powershell
python -m pip install -r tools/pswaker/desktop-requirements.txt
python tools/pswaker/build-desktop.py --program C:\private\game-release --output C:\private\desktop-build
```

The output directory must be absent and outside the checkout. Open
`C:\private\desktop-build\PSWaker\PSWaker.exe`. Retain the entire adjacent
`_internal` directory: it contains the runtime, fixed production contract and
the fixed program release. The build checks the release's data-free payload
allowlist, file hashes, game kind and version/build metadata. It does not replace
#40's ELF-to-SELF verification or make an unsigned release trustworthy.

Do not distribute this private bundle before the actual bundled payload and
dependencies pass the existing licensing gate.

## Checks and remaining evidence

```powershell
python -m pyright --pythonpath python
python -m compileall -q tools/pswaker tests/ps4
python -m unittest discover -s tests/ps4 -p test_desktop.py -v
python -m unittest discover -s tests/ps4 -p test_complete_package.py -v
```

Desktop tests use actual Tk controls and workers, replacing only OS file-dialog
answers. Synthetic images/contracts live in isolated temporary copies; shipping
desktop validation explicitly rejects those fixtures. Windows file-sharing
tests lock a real synthetic image to exercise unreadable-file feedback. They
also cover observable content failures, retries, changed selections, late
results, stale success and preservation of existing output. No game data is
committed. On Linux without a display, GUI tests skip; Windows CI runs them.
The full existing suite remains the Linux host-check job.

Development-host checks do not establish clean Windows 10/11, offline installer,
owner-image acceptance or console results. Before accepting the desktop release,
record both supported Windows versions as an ordinary user, with networking
unavailable and no development tools: launch the supplied bundle, check the
displayed program identity, select a privately supplied supported image and
destination, validate, change selections, exercise actionable failures, and
confirm the image and previous results are preserved. Installer and actual
package-creation acceptance follow in their respective tickets.
