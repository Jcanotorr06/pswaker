# Clean Windows owner-workflow acceptance (#48)

Run this checklist independently on **clean Windows 10 x64 and Windows 11 x64**.
Use the actual installed production app, an ordinary standard account, and the
owner's privately supplied supported image. The result template is
[Clean-windows-results.example.md](Clean-windows-results.example.md); current
handoff status and reference candidate identities are in
[windows-48](../../evidence/ps4/windows-48/README.md).

Keep #48 open until both returned records pass review. A development-machine run,
synthetic round trip, missing observation or successful earlier candidate does
not pass a row. Record `pending`, `pass`, `fail`, or `blocked` with a reason and
evidence reference. Keep failed attempts when a later retry succeeds. Private
acceptance can start before redistribution clearance; do not publish installers,
owner images, extracted game files or complete packages.

## 1. Prepare the private handoff (agent/maintainer)

Supply these locally before the owner disconnects the test system:

- Candidate A and newer candidate B, each with its own `installer-release.json`.
  Confirm installer bytes match its SHA-256 and retain both exact installers.
  Record the source commit for each build when available; do not guess it from
  the current branch. These candidates must contain the production contract.
- This checklist and one blank result template per OS, in a private folder
  outside the installation and output directories. No checkout, Python, SDK,
  compiler, external .NET installation, WSL or Docker goes onto the test system.
  Built-in Windows PowerShell, File Explorer, Notepad and Task Manager suffice.
- The owner's supported raw USA `GZLE01`, disc 0, revision 0 `.iso`/`.gcm`,
  exactly **1,459,978,240 bytes**, obtained privately. Retain its SHA-256 and
  accepted SHA-1. Supported SHA-1 values are
  `0289e70f470dc758c73be9b8bcd8c865fb82d8ae` and
  `6b5f06c10d50ebb4099cded88217eb71e5bfbb4a`.
- Clearly labelled **disposable private copies** for negative cases: change
  header game ID to `GZLP01` (region); byte 7 to 1 (revision); invalidate the
  GameCube magic at offset `0x1c` (container); truncate a copy; change a byte
  within a required DOL section without changing file length. Record exact
  mutations and before/after hashes privately. These are manufactured rejection
  cases, not proof of compatibility with real alternate releases. A genuinely
  compressed image, if privately available, is a separate rejection case.
- An empty, disposable NTFS destination volume with sufficient initial free
  space and a slower spare drive if needed to observe short stages. Keep the
  original image and earlier completed packages on a different stable volume.
  Prepare a second low-space volume for the capacity case; never fill the
  Windows system volume. Volume provisioning may be done by an administrator
  beforehand; installation and every acceptance operation use the standard
  account. If this equipment is unavailable, record affected cases as blocked.

The source inventory of the runtime modules (`desktop_app`, `disc_image`,
`package_validation`, `windows_package`, `windows_process`, `owned_work`,
`build_operation`, `installed_release`, `program_payload`, `package_artifact`,
`diagnostics`) must also be reviewed against the exact candidate's build source
for networking, telemetry, uploads, bootstrap downloads and update checks. Record
the commit, conclusion and any uncertainty. Offline execution proves independence
from networking; it alone cannot prove the absence of attempted connections.

## 2. Establish each clean environment (owner)

Use a fresh Windows installation or documented clean OS snapshot with no prior
PSWaker or developer prerequisites. Record physical/VM status; a clean Windows
guest is the test OS, never a consumer dependency. Record OS edition, build and
x64 architecture from Settings > System > About, plus CPU, RAM, storage type,
filesystem and free bytes. Note snapshot provenance and any preinstalled software.

In Settings > Accounts, confirm the test account is **Standard User**. In a
normal PowerShell window, run `whoami /groups` and retain the result **privately**.
There must be no Administrators SID `S-1-5-32-544`, including a deny-only entry,
and no high-integrity token. Record these conclusions in the shareable record;
raw account names/SIDs and command output remain private. A filtered administrator
token is not a standard account. Do not use Run as administrator for the app,
installer, uninstaller or fault operations.

Disconnect Ethernet and disable Wi-Fi and every other external network path
**before installation A**. Disable host-provided networking too for a guest.
Record adapter/disconnection observations and UTC start/end times; keep the
network unavailable through first launch, both package builds, faults, update
and uninstall. Airplane mode alone is insufficient if Ethernet remains active.
An unreachable proxy or stripped PATH is not network isolation. Do not reconnect
to fetch a missing runtime; record that as a failure.

## 3. Install A and complete the offline workflow

1. Hash the delivered installer with built-in PowerShell:
   `Get-FileHash -LiteralPath 'C:\private\candidate-A\PSWaker-0.46.0.0-win-x64-setup.exe' -Algorithm SHA256`.
   Substitute the actual private path/version and compare with that candidate's
   audit, not a filename alone. Hash `installer-release.json` as well.
2. Run Setup normally. Expect no administrator credential request, prerequisite
   installer, download or sign-in. Confirm a per-user Start shortcut and one
   Installed apps entry. Launch from Start. Record any OS security prompt
   separately; do not count a blocked launch as a pass.
3. Record the visible app version, game-program version/build, packaging-tool
   revision/SDK and **PS4 Slim / firmware 9.00 / GoldHEN v2.4b18** baseline.
   Confirm input and destination text is readable, including a private folder
   containing spaces and a Unicode character. No developer configuration is
   required. Match the installed `application-release.json` hash and identities
   to `installer-release.json`.
4. Optionally run the installed executable's read-only closure probe from
   PowerShell: `& '<installed-release>\PSWaker.exe' --check-installation 'C:\private\A-installation.json'`.
   Use a new report filename, wait for process exit and check the file exists.
   A report is created only for a valid complete closure. This probe is not a
   replacement for the following UI operation.
5. Hash the original image. Select it through the actual native file dialog and
   choose a private custom parent through the folder dialog. The proposed
   `PSWaker-NN.NN` child must not already exist. Click **Validate image**; expect
   supported-image success, image hashes and a measured duration. Record them.
6. Click **Create package**. Observe validation again, bundled-input checks,
   assembly, fresh extraction/verification and publication. Byte counts should
   advance during measurable reads/copies; tools may show an activity indicator.
   Confirm the window repaints/moves, selections stay locked during creation,
   and completion is not shown before verification finishes.
7. Expect **Package verified**, the actual `.pkg` location, SHA-256 and elapsed
   time. Test **Open folder** and **Installation instructions**. Confirm `INSTALL.txt`
   describes manual USB installation on the stated baseline, exFAT for files
   over 4 GB, Package Installer and play without USB after installation. Actual
   console execution/save compatibility is a separate #49 gate.
8. Export a troubleshooting report **before starting another operation**. In the
   private completed directory retain `assembly.json`, `inspection.json`,
   `stages.json`, `commands.json`, `tools.log`, `INSTALL.txt` and the matching ELF.
   Compare a new `Get-FileHash` of the actual `.pkg` with the screen,
   `assembly.json`, `inspection.json` and diagnostic export. Check inspection
   reports the accepted image hash, matching program identities and SFO
   `TITLE_ID=PSWK00001`, `CONTENT_ID=IV0000-PSWK00001_00-PSWAKERGAME00000`.
   The app's fresh inspection of the actual output is required; staging success
   or the packager exit code alone is insufficient.
9. Rehash the original image and mark this complete package as the protected
   earlier result for fault tests. Retain the full package privately. An optional
   subsequent maintainer reinspection can use `windows_package.inspect_output`
   with this exact bundle away from the clean system; record it separately from
   installed-app acceptance and never add developer tools to this environment.

Record UI validation time separately from the creation stages `validate`,
`prepare`, `verify-program`, `assemble`, `inspect`, `publish` in `stages.json` or
the exported report. Record UI end-to-end creation time too; do not add the
standalone validation to it or substitute Linux/test times. Record cache state,
storage and run number. Missing timings remain missing; there is no duration
guarantee. Failed/cancelled/interrupted attempts retain their actual outcome.

## 4. Failures, cancellation and interruption

For **every row**, use a new parent, note the observed stage/error and corrective
guidance, and export before retry/close when the app is still running. Confirm
no new unverified final output, disabled result/install actions after failure,
responsive UI, and unchanged original-image and protected-package hashes.
Restore the fault, validate from the beginning and create a freshly verified
package. Record that retry separately. A visible final package after a failed
operation is a failure even if some earlier staging checks passed.

| ID | Action through the installed app / controlled environment | Expected observation |
| --- | --- | --- |
| F01 | Select each region, revision, container, truncated and required-content negative copy from section 1; validate each separately. | Readable rejection and corrective supported-image/re-dump guidance; creation stays unavailable. Record each variant separately. |
| F02 | Select a disposable readable image copy, then hold an exclusive read lock on it using the recipe below; validate. | Useful unreadable-input error; no source changes. Release lock and reselect the supported image. |
| F03 | Select the empty scratch parent, then remove its write permission for the test user through Properties > Security before validation. Keep read/traverse and ownership so permission can be restored. | Destination-access rejection; restore the exact previous permissions and retry. If the drive has no ACL support, mark blocked and use prepared NTFS. |
| F04 | Select the dedicated low-space destination and validate, then click Create if enabled. Record free bytes and the app's required space. | Insufficient-space error before bulk output; validation alone need not perform the full creation capacity check. Use the normal scratch volume for retry. |
| F05 | Select a parent containing an existing `PSWaker-NN.NN` child with a sentinel file; separately create that child after assembly begins in another run. | Existing-output/racing-publication rejection; sentinel and any prior package remain byte-identical. Use a new parent for retry. |
| F06 | During image copying in assembly, exclusively lock only this attempt's `packaging\PkgTool.Core.exe` in its owned temporary directory. | Packaging fails at `assemble` with useful tool/stage guidance. Record actual outcome; a missed tool startup is pending, not pass. |
| F07 | During image copying in assembly, exclusively lock only this attempt's matching `elf\<filename>` in its temporary directory. Do not lock the installed bundle or any completed output. | Packaging may finish, but fresh verification fails at `inspect` when reading its matching ELF; no final publication. This is a controlled inspection I/O failure, not an altered-PKG corruption test. |
| F08 | In separate runs click Cancel during validation, assembly and fresh inspection. Use a supported private image copy on a slower source drive for validation, and a slower spare destination for assembly/inspection if needed. | UI stays active until work stops/cleanup finishes; retry starts at validation. A stage missed by the operator stays pending. |
| F09 | Close the window during active creation; separately use Task Manager to End task on this test's PSWaker during assembly and again during inspection. | Normal close waits for cancellation; forced interruption leaves no complete result. Native tool descendants stop. Reopen from Start: only recorded abandoned work is cleaned, and a fresh validation/build succeeds. |
| F10 | With an unrelated `.complete-owner-sentinel` directory beside the target, repeat forced interruption. In a separate attempt unplug only the disposable destination drive during work, reopen while absent, then reconnect and reopen. | Unrelated sentinel stays intact. Unavailable cleanup is explained and retained for later recovery; restored access permits cleanup/retry. No wildcard/manual cleanup of `.complete-*`. |

The exclusive-lock recipe uses Windows' built-in PowerShell and never changes
file bytes. Enter the exact disposable file path; while PowerShell holds it,
trigger/observe the app action in its other window:

```powershell
$faultFile = 'D:\private-scratch\exact-file-from-this-attempt'
$faultLock = [System.IO.File]::Open($faultFile, 'Open', 'Read', 'None')
try { Read-Host 'After the app reports failure, press Enter to release this test lock' }
finally { $faultLock.Dispose() }
```

For F06/F07, enable Hidden items in File Explorer and identify this attempt's
`.complete-<id>` from its new ownership record under
`%LOCALAPPDATA%\PSWaker\work`. Confirm the exact scratch parent, marker and new
attempt; never guess a directory or change the ownership record. Arm the lock
while the UI is copying the image, before the relevant tool/ELF read. If locking
fails or the target stage has passed, record the miss and repeat with a slower
drive. Holding a lock can also prevent cleanup: record that secondary error,
release the lock, close/reopen the app and confirm recovery removes only the
owned workspace. These observations exercise the unchanged installed app. They
do not replace the automated malformed-GP4/altered-PKG checks, and must not be
reported as those cases. Never patch a shipping bundle or weaken its contract.

For interruption, note app/tool PIDs in Task Manager before termination and
their absence afterward. A forced exit may have no final diagnostic export;
retain local attempt/recovery records privately and state that limitation.
If cancellation loses to an already completed verified publication, record the
verified completion and repeat earlier; it is not a cancellation pass.

## 5. Review explicit diagnostic exports

Export at least F01 validation failure, F06 packaging failure and F07 inspection
failure. Also export one successful result and a cancellation. Use image/output
paths containing a unique harmless personal-path sentinel, such as
`PRIVATE-PATH-48-TEST`, and inspect every exported JSON in Notepad or with
`Select-String -SimpleMatch`. Check the sentinel, username, drive/UNC paths and
private filenames are absent. Use no real credential as a sentinel.

Expect operation ID/UTC, distinct desktop/program versions, manifest hashes,
available program ELF/SELF/build identities, tool revision/SDK, stage
outcomes/seconds, failure category/next action and tool operation/exit codes when
a tool actually ran. Validated image/package hashes appear only when available;
a failure before creation has no package hash, and an inspection failure must
not imply verification. Unverified bundle metadata must stay labelled as such.

Confirm the report has no raw image/game bytes, extracted assets, keys,
credentials, personal paths, raw errors/arguments/tool output or attachments.
Search alone is insufficient: inspect the structured fields too. Only sanitized
JSON is intended for sharing; raw logs, setup logs, commands and artifact reports
can contain paths. Attempt export to an existing filename and an inaccessible
folder: expect useful export guidance without overwriting the file or losing
the original failure; then export to a new writable filename. Confirm no account,
upload or download UI and record network isolation plus the source review from
section 1. Any unavailable network-attempt monitoring stays explicitly unmeasured.

## 6. Manual update B and uninstall

1. While A is open and doing work, start B's installer and attempt uninstall
   separately. Expect close-app guidance/refusal without force-terminating work.
   Dismiss Setup/uninstall, finish or cancel work and close A.
2. Hash and manually install newer B, still offline and unelevated. Expect one
   app registration and a Start shortcut opening B's coherent complete runtime.
   Record B's audit/manifest hashes and displayed identities. Old versioned
   runtimes may remain until uninstall; files must not be mixed.
3. Repeat section 3 with the supported image at a new custom parent. Verify fresh
   inspection, stage timings and package hash, and rehash A's earlier complete
   package and original image. Compare both SFO identities: title/content IDs
   stay stable. A desktop-only update may retain program 01.13; do not claim
   console save/settings or a native program update from that observation.
4. Put a harmless untracked sentinel in the installation root and retain a local
   diagnostic. Uninstall through Installed apps with all app windows closed.
   Wait for the uninstaller's own removal to finish before checking. Expect all
   recorded app/runtime files, shortcuts and registration removed; the unknown
   sentinel and local diagnostic/recovery records may remain by design. Check
   source image, A/B packages, custom destinations and unrelated sentinel hashes
   are unchanged. Directory existence alone is not an uninstall failure.

## 7. Return and review (owner, then agent)

Return one filled result record per OS and reviewed sanitized diagnostic exports
by the owner's chosen private route. Keep exact installers, original image,
packages, artifact reports, raw logs and personal screenshots locally. Share
only manually reviewed path-free observations/hashes on the ticket; no archive
of the installation, logs, output or evidence folder.

The agent checks candidate identity consistency, the clean account/network
conditions, every case and retry, fresh inspection, privacy findings and measured
timings against the returned reports. Request missing evidence precisely; retain
failures and blocked/missed observations. #48 remains `ready-for-human` and open
while required execution is missing. Close it only after both OS records pass.
#49 console acceptance and #47/#50 distribution/release decisions remain separate.
