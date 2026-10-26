# Frame-pacing candidate (#22)

The [01.10 owner return](console-return-01.10/REPORT.md) now records independent
cold/warm measurements with numerical shortfalls, an early cold Outset pause,
and timing verification still pending. The original preparation report below
describes the candidate's status at handoff; its untested wording is historical.

This branch adds completed-console-flip instrumentation and the
[owner sampling workflow](../../Frame-pacing-checklist.md) to the existing
playable baseline. **Installed-console measurements and acceptance remain
pending for this binary.** No numerical performance target or hardware row is
marked passed. Issue #22 remains open for the owner return and any measured
bottleneck correction; final integrated acceptance remains #23.

The [measurement contract](../../FRAME-PACING.md) documents FIFO game-frame
tagging, VideoOut completion timestamps, reliability checks, sample boundaries,
shader hitch/correlation definitions, separate startup/loading phases, fixed
quality and evidence renewal. No resolution, texture, logic-rate, selected
driver archive or speculative performance fix is changed.

## Checks and review

[All 70 host tests passed with zero skips](host-checks.log), including 12 tests
at the owner-confirmed exported-recorder and summary-CLI seams. The first
regression exposed acceptance of missing resume markers; the analyzer now
rejects those samples. Recorder exports verify repeated-refresh exclusion,
the first-presentation baseline, the whole closing interval, paused attempts,
missing completions, UI exclusion and first-game-frame shader accounting.
Summary tests verify 30 Hz worked examples, nearest-rank limits, independent
forest failure despite a good Outset sample, raw preservation, installed-build
mismatch, wrong stage labels, incomplete samples and unverified timing.
Synthetic traces and mocked console services are never console evidence.

The [check record](host-checks.json) also records Python compilation, eight
shell syntax checks and the linked hooks. PowerShell wrapped the native test
runner's stderr as `NativeCommandError` and returned 1; the retained complete
runner output ends `Ran 70 tests` / `OK`, with no failed or skipped tests.
This capture behavior is retained explicitly rather than represented as a
successful shell-wrapper exit. The public UTF-8 view normalizes trailing
whitespace; the original capture bytes remain private as well.

Target compilation/linking checked the combined C/C++ interfaces, retained a
matching unstripped ELF with source lines, checked Jaguar/btver2 compilation
commands and absence of unresolved TLS initializers, then generated SELF and
passed the OELF segment check. The [ABI audit](game-abi-audit.json) associates
these checks with the final binary. The emitted
[VideoOut link audit](videoout-link.txt) confirms that the selected Mesa flip
thread calls `__wrap_sceVideoOutSubmitFlip`; capture/present/shader hooks are
defined in the linked ELF. This checks hook reachability, not console timestamp
semantics or physical display behavior.

The [provenance record](provenance.json) retains pins, ordered patch hashes,
platform anchors, port-input hashes and the private full-input inventory hash.
The current input closure was checked against the configured/compiled closure
after final source changes. Earlier successful compilation was rejected by the
staging guard after intervening validation changes; no rejected artifact was
handed off. The new game root is `~/.cache/pswaker/game-22/`; it consumes the
unchanged selected `maintained-15-a` platform archives and game-local Aurora
hooks. The [host recovery record](host-recovery.json) records temporary use of
the retained hash-checked locked zlib package and restoration of the pre-task
installed version. No dependency guard was bypassed.

Independent [Standards and Spec reviews](REVIEW.md) found no confirmed
implementation defects or scope creep. The Spec review explicitly retains the
missing hardware requirement: actual scene samples, verified timing and any
measured bottleneck corrections. It does not label issue #22 complete.

## Exact candidate

Application **PSWaker**, version **01.10**, retains title ID `PSWK00001` and
content ID `IV0000-PSWK00001_00-PSWAKERGAME00000`. Compiled build:
**`8c892c5b54b28d9f41da`**.

| Artifact | Identity |
| --- | --- |
| Private Windows package | `local-research/performance-22-artifacts/PSWaker-performance-01.10.pkg` |
| Package size | 1,516,634,112 bytes |
| Package SHA-256 | `b6b47e7031c83eee06583e78eac456cec625b5477aff1765476fdb7f1d1a47f8` |
| Matching unstripped ELF SHA-256 | `e2eca045bcef3d90757661f3400ca982253d7206ec9d548585d49bf8d19e9c48` |
| SELF SHA-256 | `57548190e0948df2b59c30aaffaf410ab353b343698a9e51f6c57b7e6900476f` |
| Owner USA GZLE01 revision-0 image SHA-1 | `6b5f06c10d50ebb4099cded88217eb71e5bfbb4a` |
| Image SHA-256 | `ec2d4ee790f48bee3d4c10feed166370df895f474e8db3f9af3b16ee001436df` |

Assembly extraction/inspection and a second fresh extraction/inspection passed.
The Windows package and ELF copies match their inspected originals.
[inspection-01.10.json](inspection-01.10.json) and [artifacts.json](artifacts.json)
retain these associations. The inherited inspection status mentions issue #16's
tooling origin; this report's **untested #22 candidate** status controls the
handoff. The package contains no saves/settings, test markers or owner evidence.

Installed content remains `/app0/game.iso`; shared profile data remains
`/data/pswaker/`. The new disposable build cache is
`/data/pswaker/cache/8c892c5b54b28d9f41da/`. Rename only that cache for a cold
run, preserving saves, settings, recovery files and all earlier logs. Each launch
creates a unique `/data/pswaker/logs/performance-XXXXXX/` directory.
Use the [owner checklist](../../Frame-pacing-checklist.md) and return every
launch/sample, including failures. No console sample has been returned yet.

Private complete assembly, notices and tool logs remain in
`~/.local/share/pswaker-private/performance-22-01.10/`. The Windows
`local-research/performance-22-artifacts/` directory contains the package,
matching ELF, assembly record, full input inventory and build evidence. No
private disc/save bytes, complete packages or executables are committed.

The existing owner edit to root `GLOSSARY.md` is outside this task and is not
included in its commits.
