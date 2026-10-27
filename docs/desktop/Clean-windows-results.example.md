# Windows acceptance result — blank template (#48)

Copy once for Windows 10 x64 and once for Windows 11 x64 into a private location.
Follow [the checklist](Clean-windows-checklist.md). Every observation below starts
**pending**, not passed. Use `pass`, `fail`, `blocked`, `pending`; explain any
missing evidence. Repeat attempt rows instead of replacing failures with retries.
Use aliases for personal locations. Raw records and artifacts remain private;
manually review this record before sharing even a summary.

## Environment

| Field | Observation |
| --- | --- |
| Run ID / operator alias / UTC dates | pending |
| Windows edition / version / build / x64 | pending |
| Fresh OS/snapshot origin; physical or Windows guest | pending |
| Standard account confirmed in Settings | pending |
| Administrators SID absent, including deny-only | pending |
| Non-elevated token; private whoami record reference | pending |
| No prior PSWaker, checkout, SDK, Python, external runtime/developer tools | pending |
| Preinstalled software / deviations | pending |
| CPU / RAM / storage model and type | pending |
| Image / output filesystem and volume aliases | pending |
| Initial output free bytes; fault-volume free bytes | pending |
| Every external network path disabled, method and private evidence reference | pending |
| Offline interval start/end UTC; any interruption | pending |
| Candidate source audit for network/telemetry/upload/update paths; commit and conclusion | pending |
| Attempted network connections monitored? method/result or unmeasured | pending |

## Exact candidates

Use the matching private audit manifests. Record hashes of the actual files, not
just declared values. An unavailable source identity stays unknown with a reason.

| Field | A | B |
| --- | --- | --- |
| Installer filename / app version | pending | pending |
| Installer SHA-256 observed / matches audit | pending | pending |
| installer-release.json SHA-256 / private reference | pending | pending |
| Build source commit / provenance or unknown reason | pending | pending |
| release_directory | pending | pending |
| Installed application-release.json SHA-256 / matches audit | pending | pending |
| Installed desktop-release.json SHA-256 | pending | pending |
| Optional installed closure report reference / result | pending | pending |
| Python / PyInstaller / installer compiler identities (audit) | pending | pending |
| Displayed desktop version | pending | pending |
| Program version / compiled build ID | pending | pending |
| Program release manifest / ELF / SELF SHA-256 | pending | pending |
| Tool revision / SDK / release manifest SHA-256 | pending | pending |
| Production content-contract SHA-256 | pending | pending |
| Displayed supported console baseline | pending | pending |

## Input and verified results

| Field | A first build | B post-update build |
| --- | --- | --- |
| Input alias / bytes / game ID / disc / revision | pending | pending |
| Input SHA-1 / accepted production fingerprint | pending | pending |
| Input SHA-256 before / after | pending | pending |
| Output alias / package bytes | pending | pending |
| Actual package SHA-256 / UI and report hashes agree | pending | pending |
| assembly.json / inspection.json SHA-256 and private references | pending | pending |
| stages.json / successful diagnostic export SHA-256 and references | pending | pending |
| Inspected image / ELF / SELF / build match selected candidate | pending | pending |
| SFO TITLE_ID | pending | pending |
| SFO CONTENT_ID | pending | pending |
| SFO APP_VER / VERSION | pending | pending |
| Actual fresh extraction/inspection passed before publication | pending | pending |
| Optional later independent reinspection method / result (separate) | pending | pending |
| A package unchanged after B and uninstall | pending | pending |

Expected stable IDs are `PSWK00001` and
`IV0000-PSWK00001_00-PSWAKERGAME00000`. Package hashes may differ; compare each
package with its own reports. Do not claim console compatibility from stable IDs.

## UI, lifecycle and privacy observations

| Requirement | Status / observation / evidence reference |
| --- | --- |
| A install and first launch, no admin request or prerequisites | pending |
| Per-user Start shortcut / Installed apps registration | pending |
| Native dialogs / readable spaces and Unicode paths | pending |
| App/program/tool/baseline display matches candidate | pending |
| Responsive stage progress; byte counts/activity; locked selections | pending |
| Verified-result location / Open folder opens actual result | pending |
| Manual USB instructions / INSTALL.txt / no USB needed for installed play | pending |
| Update and uninstall refuse while A is open/working | pending |
| Offline manual B update / one registration / coherent runtime | pending |
| B package freshly inspected; stable console identity | pending |
| Uninstall removed recorded files, shortcuts and registration after exit | pending |
| Original image, A/B packages and custom output contents preserved | pending |
| Untracked install-root sentinel and local diagnostics preserved | pending |
| No accounts, runtime download, automatic update/upload or telemetry UI | pending |
| Validation failure export has useful identities/stage/recovery | pending |
| Packaging failure export has tool outcome when invoked | pending |
| Inspection failure export does not imply verified success | pending |
| Success / cancellation exports reviewed | pending |
| Sentinel, personal paths/filenames, raw messages/arguments/tool output absent | pending |
| No game bytes/assets, keys, credentials or attachments | pending |
| Existing export file preserved / inaccessible export explained / retry succeeds | pending |
| Source audit vs exact build and offline evidence reviewed together | pending |

## Attempts and fault recovery

For each attempt record **candidate**, operation ID/UTC when available, negative
fixture alias/mutation and hash, controlled action and actual stage reached,
visible result/next action, export reference/hash, cleanup or recovery record,
presence/absence of a final output, original-image and protected-package hashes
before/after, and fresh retry result/package hash. Record sentinel hashes where
used. A forced exit can lack an export: explain and reference recovery evidence.

| Case | Status | Attempt references / observed limitation |
| --- | --- | --- |
| F01 region header | pending | pending |
| F01 revision header | pending | pending |
| F01 invalid container magic | pending | pending |
| F01 truncated image | pending | pending |
| F01 modified required DOL content | pending | pending |
| F01 actual compressed container, if supplied (optional additional coverage) | pending | pending |
| F02 unreadable image | pending | pending |
| F03 destination access | pending | pending |
| F04 insufficient capacity | pending | pending |
| F05 existing child / racing child (record separately) | pending | pending |
| F06 packaging failure at assemble | pending | pending |
| F07 fresh inspection I/O failure at inspect | pending | pending |
| F08 Cancel validation / assembly / inspect (record separately) | pending | pending |
| F09 Close during creation / forced assembly exit / forced inspect exit | pending | pending |
| F10 unrelated workspace preserved / absent-drive recovery | pending | pending |

Attempt record to duplicate:

- Attempt ID / case / candidate / UTC / operation ID: pending
- Fixture mutation/hash or fault setup; exact stage observed: pending
- Actual UI result and next action (path-free paraphrase): pending
- Diagnostic export SHA-256 / private reference or why unavailable: pending
- Source-image SHA-256 before / after: pending
- Protected-package SHA-256 before / after: pending
- Sentinel before/after hashes; final output absent or verified completion race: pending
- Tool descendants stopped; cleanup/recovery result and evidence: pending
- Fault removed; fresh validation/retry result and verified package SHA-256: pending
- Failure, missed stage or limitation retained: pending

## Measured timings

Duplicate one row per attempt; label success, failure, cancellation or interrupted.
Use seconds from the actual UI/export/stages, never inferred Linux throughput.
Separate standalone UI validation from the creation operation's own revalidation.
Record missing values explicitly. Publication-stage timing may be absent from
`stages.json`; use the completed diagnostic stage event when available.

| Attempt/candidate/outcome | Cache state/run # | UI validation s | Create validate s | Prepare s | Verify-program s | Assemble s | Inspect s | Publish s | UI create total s | Source/reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |

## Return review

- Required rows still pending/blocked, failures and retained first attempts: pending
- Privacy review of the intended shared record/exports: pending
- Agent identity/fresh-inspection/account/offline/timing review: pending
- Windows 10 result: pending; Windows 11 result: pending
- #48 disposition: **open; awaiting actual clean-system evidence**
- No numerical duration guarantee, console acceptance or redistribution clearance
  is established by this record.
