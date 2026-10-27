# Windows complete-package creation

Issues [#41](https://github.com/Jcanotorr06/pswaker/issues/41) and
[#42](https://github.com/Jcanotorr06/pswaker/issues/42) provide the local desktop
selection, validation, assembly and verified-result flow from
[#39](https://github.com/Jcanotorr06/pswaker/issues/39). This is a private
development bundle. Installer delivery, clean Windows acceptance, console
acceptance and redistribution clearance remain separate work.

## Desktop workflow

Open `PSWaker.exe` from its complete application folder. It displays its fixed
game-program version/build and **PS4 Slim / firmware 9.00 / GoldHEN v2.4b18**
baseline. No program, SDK, build root or package-identity selection is required.

1. Select your own full raw `.iso` or `.gcm` image. Uppercase extensions work.
2. Select a private parent folder outside the application/source checkout. The
   proposed new `PSWaker-NN.NN` directory must not exist.
3. Select **Validate image**. Success shows measured duration and image hashes.
   Changed selections or input/destination changes invalidate the result.
4. Select **Create package**. The worker validates again, checks the bundled
   release, copies and revalidates the image, assembles a native Windows package,
   then extracts and inspects the actual output. The screen reports each stage
   with an activity indicator. Selections are locked during creation.
5. **Package verified** shows the actual `.pkg` location, SHA-256 and measured
   elapsed time. **Open folder** opens its containing directory.
   **Installation instructions** and the retained `INSTALL.txt` explain manual
   USB installation: copy the package to the root of an exFAT/FAT32 USB drive
   (exFAT for files over 4 GB), connect it to the prepared PS4, and use
   Settings → GoldHEN → Debug Settings → Package Installer. Launch PSWaker from
   the home screen. Remove USB after installation; gameplay uses the installed
   image and needs no external image or USB drive.

An existing destination is preserved, including one that appears during
creation. Only a verified output is renamed into the requested final directory.
Failure removes the application-owned temporary workspace and enables validation
and retry. Tool failures retain a local log under `%LOCALAPPDATA%\PSWaker\logs`.
Images and completed packages remain private; there are no accounts, uploads,
telemetry, runtime downloads, WSL, Docker, shell scripts or source compilation
in this consumer workflow. The installer belongs to #46; broader storage,
cancellation, interruption recovery and diagnostics work belongs to #43–45.

## Content and release integrity

Desktop validation and creation share `package_validation.validate_selection`
and the existing `disc_image.validate` policy. The production contract remains
USA GZLE01, disc 0, revision 0, exactly **1,459,978,240 bytes**, raw GameCube
header, bounded FST/DOL structure, pinned required DOL/REL content and both
whole-image SHA-1 fingerprints:

- `0289e70f470dc758c73be9b8bcd8c865fb82d8ae`
- `6b5f06c10d50ebb4099cded88217eb71e5bfbb4a`

There is no alternate-contract or synthetic-mode switch. A changed source must
match both the accepted validation report and the newly validated staged copy.
The image is opened for reading only. Space checks budget for staging, package,
fresh extraction and tool overhead in the destination filesystem.

The maintainer supplies a verified, relocatable #40 **game program release**,
never a diagnostic. Its exact data-free file inventory, ELF/SELF hashes,
compiled build identity, game kind, SFO identity and version are checked and
bound into `desktop-release.json` with the tool closure and production contract.
Windows consumes that fixed preverified release; it does not rerun the Linux
SELF converter or require its SDK. The input #40 release must already have
passed ELF-to-SELF reproduction. The bundle manifest detects changed release
files; it is not a signature or a replacement for trusted release delivery.

The Windows adapter serializes GP4 directly and invokes a self-contained x64
build of the existing pinned LibOrbisPkg source. All packaged tool/runtime files
are inventoried and SHA-256 checked, copied into private work and checked again
for inspection. CPython 3.12, Tkinter/ttk and PyInstaller supply the desktop
runtime. Consumers need neither Python nor a separately installed .NET runtime.

`package_artifact.inspect_package` is shared with Linux CLI assembly. Fresh
extraction checks the exact payload inventory, every file hash, PKG header,
SFO fields, packaged program/build manifest and whole-image/required-content
integrity. It does not trust a packager exit code or staging hashes alone.
`inspection.json`, `assembly.json`, `commands.json`, `tools.log` and measured
`stages.json` remain beside the private package. Staged image/tool copies are
removed before publication. `windows_package.inspect_output` can independently
repeat inspection of a retained artifact using the same fixed tool bundle.

The fixed game identity remains `PSWK00001` /
`IV0000-PSWK00001_00-PSWAKERGAME00000`, with `/app0/game.iso` installed content.
Container verification establishes neither console acceptance nor distribution
clearance; see [complete packages](../ps4/COMPLETE-PACKAGES.md) and
[licensing](../ps4/LICENSING.md).

## Maintainer preparation

These commands are developer preparation, never consumer setup. On Windows x64,
use CPython 3.12 with Tcl/Tk and the explicitly pinned .NET SDK **8.0.427**.
The tool preparer fetches the existing pinned LibOrbisPkg archive, verifies its
SHA-256, applies the established net6.0 → net8.0 retargeting, and publishes with
the Windows runtime. Network restore is confined to maintainer preparation.
Review the actual closure's redistribution obligations before distribution.

```powershell
python -m pip install -r tools/pswaker/desktop-requirements.txt
python tools/pswaker/prepare-windows-tools.py --dotnet C:\maintainer\dotnet\dotnet.exe --output C:\private\windows-tools
python tools/pswaker/build-desktop.py --program C:\private\game-release --packaging C:\private\windows-tools --output C:\private\desktop-build
```

Tool and build outputs must be new directories. Keep the entire resulting
`PSWaker` folder, including `_internal`, together. The standalone per-user
installer and its offline delivery acceptance remain #46 and #48.

## Verification and remaining evidence

```powershell
$env:PSWAKER_WINDOWS_TOOLS = 'C:\private\windows-tools'
python -m pyright --pythonpath python
python -m compileall -q tools/pswaker tests/ps4
python -m unittest discover -s tests/ps4 -p test_desktop.py -v
python -m unittest discover -s tests/ps4 -p test_windows_package.py -v
```

Windows CI builds the real tool closure and exercises actual Tk controls/workers
and data-free synthetic package round trips. Only OS dialogs/folder-opening are
substituted in desktop tests; validation, assembly and fresh extraction are real.
Synthetic contracts/programs exist only in isolated temporary test copies. The
shipping validator rejects these images. Coverage includes changed images,
tampered release files, altered package headers, unexpected freshly extracted
files, existing/racing output directories and desktop failure/retry.

Private production-image observations are recorded in
[Windows #42 evidence](../../evidence/ps4/windows-42/README.md). They do not
establish clean Windows 10/11 offline acceptance (#48), installed-console and
update/save acceptance (#49), or public release readiness (#47/#50). Run those
checklists using the exact candidate bundle and package identities.
