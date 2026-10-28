# Windows complete-package creation

Issues [#41](https://github.com/Jcanotorr06/pswaker/issues/41),
[#42](https://github.com/Jcanotorr06/pswaker/issues/42) and
[#43](https://github.com/Jcanotorr06/pswaker/issues/43),
[#44](https://github.com/Jcanotorr06/pswaker/issues/44) and
[#45](https://github.com/Jcanotorr06/pswaker/issues/45) provide the local desktop
selection, validation, assembly, failure handling, private reports and verified-result flow from
[#39](https://github.com/Jcanotorr06/pswaker/issues/39). This is a private
candidate. [#46](https://github.com/Jcanotorr06/pswaker/issues/46) adds the per-user
offline installer and manual updates. Clean Windows acceptance, console acceptance
and redistribution clearance remain separate gates.

## Install, update and remove

Use the private `PSWaker-N.N.N.N-win-x64-setup.exe` candidate on Windows 10 or
Windows 11 x64. It installs for the current account under
`%LOCALAPPDATA%\Programs\PSWaker` and creates a Start menu shortcut and an entry
in Windows Installed apps. Installation, launch and package creation require no
administrator access, Python, .NET installation, SDK, checkout or first-run
download. Everything needed is in the installer; it never downloads a bootstrapper
or asks for an account. ARM64 and 32-bit Windows are rejected by Setup.

Close all PSWaker windows before manually running a newer installer. Setup and
uninstall refuse to proceed while the app owns work; they never force-close an
active package operation. Each candidate contains its own complete, versioned
runtime directory. Updates reuse the per-user app registration and point the
Start menu shortcut at the new complete release. Earlier installed runtimes are
retained until uninstall, so no old/new runtime files are mixed and no wildcard
cleanup can consume owner files. Installers provide all updates; there is no
automatic updater or network update check.

The window displays the desktop version, bundled game-program version/build and
packaging-tool revision/SDK. Desktop versions are independent of console program
versions. Startup verifies the full executable/runtime inventory, program,
production content contract and tool closure before showing the workflow. Changed,
missing or incompatible bundled files require reinstalling the complete app;
the app never searches PATH or a developer installation for replacements. These
hash inventories detect changed files; they are not cryptographic signatures or
a substitute for trusted delivery.

Remove PSWaker through Windows Installed apps. Uninstall removes the files and
shortcuts recorded by all installers for this app. It has no recursive cleanup
rule for the installation directory, output folders or local state. Owner images,
completed packages, custom output locations, unknown files and local diagnostic/
recovery records are preserved. Finish or cancel active work before removal.
Console application/content identity and the native save/settings format remain
unchanged by desktop updates or uninstall. An installed PS4 package and its saves
are managed separately on the console.

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
   with measured byte counts during reads, hashing and copies, and an activity
   indicator during tools that do not provide measurable progress. Selections
   are locked during creation. These are per-operation counts, not estimated
   overall percentages or duration promises.
5. **Package verified** shows the actual `.pkg` location, SHA-256 and measured
   elapsed time. **Open folder** opens its containing directory.
   **Installation instructions** and the retained `INSTALL.txt` explain manual
   USB installation: copy the package to the root of an exFAT/FAT32 USB drive
   (exFAT for files over 4 GB), connect it to the prepared PS4, and use
   Settings → GoldHEN → Debug Settings → Package Installer. Launch PSWaker from
   the home screen. Remove USB after installation; gameplay uses the installed
   image and needs no external image or USB drive.

Select **Cancel** during validation or creation to stop the current attempt.
The screen stays active while owned work stops and temporary files are removed;
retry is enabled only after that finishes. Closing the window requests the same
cancellation and waits for cleanup. A cancelled attempt requires **Validate
image** again and starts from the beginning. Cancellation immediately before
publication prevents publication; if the verified final rename has already
won that race, the result is a completed verified package.

On launch, PSWaker checks its local ownership records for interrupted work.
It skips attempts still running in another app, and removes only the recorded
temporary directory with its matching directory identity and ownership marker.
It preserves unrelated `.complete-*` directories, replaced directories, the
source image and final packages. Changed ownership or unavailable storage is
reported on screen; restore access and reopen the app to retry recovery. No
unfinished validation or inspection is reused. Native tools run in a Windows
job that stops their descendants on cancellation and when the app process exits.

An existing destination is preserved, including one that appears during
creation. Only a verified output is renamed into the requested final directory.
Failure removes the application-owned temporary workspace and enables validation
and retry. Errors identify the failed stage, affected path or tool operation and
an action to take. Local logs under `%LOCALAPPDATA%\PSWaker\logs` retain failure
details and full failed-tool output when that location is writable. A log-write
failure does not hide the original error. If lost access prevents cleanup, the
error identifies the exact unfinished workspace; restore access before removing
that workspace and retrying. Existing owner files and completed packages are
preserved. Choose another parent folder when the proposed output already exists.
Images and completed packages remain private; there are no accounts, uploads,
telemetry, runtime downloads, WSL, Docker, shell scripts or source compilation
in this consumer workflow.

## Private troubleshooting reports

After validation or package creation finishes, fails or is cancelled, select
**Export troubleshooting report…** and choose a new `.json` filename. Export is
explicit, works offline and never replaces an existing file. If saving fails,
the app explains how to retry while preserving the original failure on screen
and retaining its report in memory. Selecting a different image or destination
does not change that report; starting another operation replaces it. Export the
report before retrying or closing the app if you want to keep that attempt.

The report contains a unique operation ID, UTC start time, app/program versions
and manifest fingerprints, supported program build identities, packaging-tool
revision/SDK and manifest fingerprint, measured stage outcomes/timings, tool
operation names/exit codes, and validated image/package hashes when available.
It distinguishes declared bundle metadata from the verified snapshots actually
used. Unavailable identities remain empty, including a package hash when failure
occurs before a package exists. A failed inspection never implies verification.

Reports use an allowlist of structured fields. Personal paths and filenames,
command arguments, raw exception messages (including nested errors/notes), tool
output and arbitrary manifest fields are omitted altogether. Failure categories,
OS error codes and stage-specific recovery guidance provide context without
copying that sensitive text. No log directories, file attachments, disc bytes,
extracted game files, keys or credentials are collected. Temporary export files
contain only this sanitized JSON and are removed after saving or a failed write.

Only the exported JSON is intended for sharing. Local developer logs and the
private package folder can contain personal paths and raw tool output; do not
bundle them with the report. Reports stay on your computer until you choose to
share them. There is no upload, telemetry, sign-in or automatic tool download.
Diagnostic evidence establishes neither console acceptance nor redistribution
clearance. This implements [#45](https://github.com/Jcanotorr06/pswaker/issues/45);
the public Windows/console acceptance gates below remain separate.

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
The image is opened for reading only. Before creation, the app checks image
readability and probes destination access using only an app-owned file. Space
checks budget for the image/program copies, matching ELF, self-contained tool
snapshot, final package, fresh extraction, packager scratch and a 512 MiB reserve.
All bulk writes, including the packager's `TEMP`/`TMP` scratch, stay under a new
app-owned workspace beside the final output, so the budget applies to their
actual destination filesystem even when the image, app and system temporary
folder are on other drives. The final rename needs no additional package copy.
Optional local failure logs use the local application-data location and may fail
independently. Free-space estimates cannot reserve capacity against other apps;
runtime write/access failures still fail safely and permit correction and retry.

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
Stage starts and measured elapsed times are also retained locally under
`%LOCALAPPDATA%\PSWaker\logs`, including completed, failed, cancelled and interrupted
attempts, for later Windows benchmarking. These records contain stage and error
metadata, not game bytes, and are never uploaded. Ownership leases live under
`%LOCALAPPDATA%\PSWaker\work`; successful cleanup removes the lease record. If
that storage is unavailable, creation fails before copying image data into a
workspace that could not be recovered safely. Optional log failures continue to
leave the original result/error visible.

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
python tools/pswaker/build-installer.py --program C:\private\game-release --packaging C:\private\windows-tools --app-version 0.46.0.0 --iscc 'C:\maintainer\Inno Setup 6\ISCC.exe' --output C:\private\installer-0.46.0.0
```

Tool and build outputs must be new directories. Keep the entire resulting
`PSWaker` folder, including `_internal` and `application-release.json`, together.
The application and setup executables embed the repository's
`tools/pswaker/waker.ico` icon.
The installer builder uses the same bundle builder with **CPython 3.12**,
**PyInstaller 6.22.3** and an explicit **Inno Setup 6.7.3** compiler. Its script
rejects any other compiler version. App versions have four numeric Windows version
components, each 0..65535; assign a new version to each manual desktop release.
Compiler preparation is a maintainer step only. Obtain the pinned compiler from
[Inno Setup's official downloads](https://jrsoftware.org/isdl.php), verify its
publisher/signature and record the archive identity. The CI recipe additionally
checks the exact pinned download SHA-256 before installing that compiler.

The new installer output contains the self-contained setup executable and
`installer-release.json`: installer SHA-256, app version, installed directory
identity, executable/runtime inventory, Python/PyInstaller versions, desktop
manifest, full program/tool manifests, installer recipe digest and compiler-file
inventory. Retain both files privately for audit and acceptance. No owner image
is read when building an installer. The builder seals only the strict data-free
program/tool/contract inventories; arbitrary program files are rejected. No
release artifacts are published by the build or CI.

For a read-only installed closure probe, run the installed `PSWaker.exe
--check-installation C:\private\new-installation-report.json`. It returns zero
and creates a new identity report only when the entire installed closure matches.
An invalid closure or an existing report path returns nonzero. This maintainer
acceptance probe cannot select a different program or alter image policy.

## Verification and remaining evidence

```powershell
$env:PSWAKER_WINDOWS_TOOLS = 'C:\private\windows-tools'
python -m pyright --pythonpath python
python -m compileall -q tools/pswaker tests/ps4
python -m unittest discover -s tests/ps4 -p test_desktop.py -v
python -m unittest discover -s tests/ps4 -p test_windows_package.py -v
$env:PSWAKER_ISCC = 'C:\maintainer\Inno Setup 6\ISCC.exe'
python -m unittest discover -s tests/ps4 -p test_installer.py -v
```

Windows CI builds the real tool closure and exercises actual Tk controls/workers
and data-free synthetic package round trips. OS dialogs/folder-opening are
substituted in desktop tests; storage fault tests also inject OS write/access,
capacity and subprocess-boundary conditions. Validation, assembly and fresh
extraction are real. Malformed GP4 input provokes a real packager failure, and an
altered PKG is rejected by production inspection before publication.
Synthetic contracts/programs exist only in isolated temporary test copies. The
shipping validator rejects these images. Coverage includes changed images,
tampered release files, altered package headers, unexpected freshly extracted
files, existing/racing output directories, partial image writes, lost destination
and publication access, failed workspace setup/cleanup, unavailable diagnostic
storage, and desktop failure/retry. Failure scenarios compare the source image
and a real prior verified package before/after, reject newly completed output,
and successfully create and inspect a package after correction.

Cancellation coverage includes desktop validation, assembly and inspection;
artifact publication races; owned tool descendants; forced worker termination;
live-session leases; cold-start cleanup; replaced-directory ownership; and a
freshly verified retry. All cancellation/interruption fixtures are data-free.

The installer lifecycle test compiles two real setup executables containing an
isolated data-free fixture, installs them in sequence, launches their actual
frozen application, selects paths through native dialogs and creates freshly
inspected packages. It checks the installed closure with system-only PATH and an
absent external .NET runtime, rejects a missing bundled runtime, preserves stable
console IDs and the prior package across a desktop-only update, and uninstalls
both versions while preserving input, outputs and an unknown file inside the app
directory. It skips when a real per-user PSWaker installation is already registered.
GUI automation needs an interactive Windows desktop. CI may use an elevated
runner, so its smoke test does not establish standard-account acceptance.
Unreachable proxy settings exercise offline-friendly operation but do not prove
network isolation; the #48 matrix must physically disable networking from before
installation on both clean Windows versions and record the actual account token.

Private production-image observations are recorded in
[Windows #42 evidence](../../evidence/ps4/windows-42/README.md) and
[installed-app #46 evidence](../../evidence/ps4/windows-46/README.md). Use the
[clean Windows checklist](Clean-windows-checklist.md) and
[result template](Clean-windows-results.example.md) for the complete #48 workflow,
failure/recovery, diagnostics, timing and lifecycle matrix. The
[handoff record](../../evidence/ps4/windows-48/README.md) retains pending status and
reference candidate identities; the [installer checklist](Installer-checklist.md)
also covers the narrower #46 lifecycle. These observations do not
establish clean Windows 10/11 offline acceptance (#48), installed-console and
update/save acceptance (#49), or public release readiness (#47/#50). Run those
checklists using the exact candidate bundle and package identities.

The [#47 inherited-program audit](../ps4/INHERITED-PROGRAM-AUDIT.md) records the
actual retained module/stub inputs, upstream source findings and concrete
remaining distribution blockers. It does not clear the eventual installer.
