# Follow-up performance candidate 01.12

This follows the [01.11 return](../console-return-01.11/REPORT.md). A delayed
UI completion incorrectly disabled later warm forest sampling. Synchronous
recorder I/O also shared the frame/submission lock, and a cold flush took
160.558390 ms. This candidate records delayed observations without permanently
disabling sampling and moves CSV I/O to a bounded worker queue. It retains
missing-frame/clock/error rejection, records simultaneous kernel clock reads
and drains evidence on normal Quit. The [measurement contract](../../../FRAME-PACING.md)
describes the new fields and reliability checks.

**UNTESTED on PS4.** The host regressions verify the recording/analysis fixes;
they do not establish a performance pass. Cold shader compilation stalls and
other unexplained spikes remain unresolved. Quality, thresholds, stock textures,
original 30 Hz logic, 1280x720 internal allocation and selected platform stack
remain fixed. New affected platform evidence is required; no prior binary's
pass is inherited. Issue #22 remains open; final integrated acceptance is #23.

## Verification

All **80 host tests passed with zero skips** and process exit 0, including
22 frame-pacing tests. [host-checks.log](host-checks.log) preserves the full
runner output and [host-checks.json](host-checks.json) records the checks.
The exported-record regression initially lost the later forest sample after a
160 ms UI observation delay; it now exports both completed samples. A blocked
external file flush initially blocked recording/submission; recording now
continues and normal shutdown drains all rows. Storage failure and bounded-queue
exhaustion export invalid evidence. CLI tests cover calibrated delayed reads,
future timestamps, clock disagreement and a backward read inside the rate-check
tolerance. Existing sample boundaries, repeats, hitch accounting, independent
scene verdicts, legacy inputs and invalid/incomplete evidence remain covered.
These use the agreed exported-record and summary-CLI seams, not physical display
timing verification.

Target C/C++ compilation, linking, SELF generation, Jaguar flags, unresolved-TLS
audit and OELF segment checks passed. [game-abi-audit.json](game-abi-audit.json)
identifies the matching ELF. [videoout-link.txt](videoout-link.txt) confirms the
Mesa flip-submission path still calls the recorder wrapper.
[release-log-link.txt](release-log-link.txt) confirms native file logging remains
and release debugger duplication remains absent. Python compilation and all
eight shell syntax checks passed. The [provenance record](provenance.json)
confirms the current input closure equals the compiled closure at collection.

The [independent review](REVIEW.md) found one shutdown synchronization defect,
fixed before the final build, and no remaining Standards/Spec implementation
findings. Twenty retained original 01.11 raw/owner/log/inspection/analysis blobs
were verified byte-for-byte against committed Git bytes and their inventory.
Original timing flags are preserved; reviewed copies record the owner's
after-Quit/no-interruption/no-video clarification and missing terminal markers.

The final build uses `~/.cache/pswaker/game-22-logfile/`, consuming unchanged
verified archives from `maintained-15-a`. [host-recovery.json](host-recovery.json)
records hash-checked use of the locked retained zlib package and restoration of
the pre-task host package after successful assembly and fresh inspection.

## Exact candidate

PSWaker **01.12**, compiled build **`bc90c33b639295f36912`**, retains title ID
`PSWK00001`, content ID `IV0000-PSWK00001_00-PSWAKERGAME00000` and installed
content `/app0/game.iso`. Saves/settings remain under `/data/pswaker/`.

| Artifact | Identity |
| --- | --- |
| Private Windows package | `local-research/performance-22-artifacts/candidate-01.12/PSWaker-performance-01.12.pkg` |
| Package size | 1,516,634,112 bytes |
| Package SHA-256 | `d60c319ac16f3e17a5de9357a9f12a897f8209873f42fe6b25715190785af534` |
| Matching unstripped ELF SHA-256 | `57094078764f1e5d0d3ebbdff4b5650752794f248c6227b67a3f5abe0fc2ae01` |
| SELF SHA-256 | `39bc4a637cc3bb126c495ddda75acd15ca701018e8795aafc6400061fc234e8b` |

Private assembly and a second fresh extraction/inspection passed.
[inspection-01.12.json](inspection-01.12.json) and [artifacts.json](artifacts.json)
associate program, image and package. Exported Windows package/ELF copies match
the inspected originals. The inspection's inherited #16 wording describes its
tooling origin; this report's **untested follow-up candidate** status controls
the handoff. No game bytes, saves/settings or test markers are committed.
The private complete assembly is `/home/joseph_cano/.local/share/pswaker-private/performance-22-01.12-final`; full build records
and matching ELF accompany the Windows package.

Use only `/data/pswaker/cache/bc90c33b639295f36912/` for this build's cold disposable
cache preparation, preserving real profile/recovery data. Follow the updated
[owner checklist](../../../Frame-pacing-checklist.md): independent full Outset
and forest samples, comparable actions, visible timing corroboration and
retrieval after normal Quit. Retain every failed launch/sample. Leave
`timing_method_verified=false` until actual displayed timing has been checked.
If `shutdown,complete` is absent, return the original files and visible Quit
outcome without adding markers. Cold shader waits still count as gameplay
hitches; no relaxed quality/threshold or substitute evidence is approved.
