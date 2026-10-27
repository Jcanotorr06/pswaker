# Follow-up performance candidate 01.11

The [01.11 owner return](../console-return-01.11/REPORT.md) now records its
independent cold/warm results and unavailable warm forest sample. The report
below describes the historical handoff. Use [01.12](../candidate-01.12/REPORT.md)
for the recorder follow-up; no performance pass is inherited.

This candidate follows the [failed/partial 01.10 return](../console-return-01.10/REPORT.md).
It removes synchronous debugger-output duplication from the release native
logger while retaining the FTP log, adds input/heartbeat/recorder-flush duration
records, and fixes analysis of late presentations after an explicit sample end.
The change retains 720p, stock textures, original 30 Hz logic, synchronous
pipelines and the selected platform stack.

**New console measurements are required for this changed binary.** The host
regression demonstrates the cost mechanism with an intentionally slow external
debug service. It does not prove the actual PS4 syscall's isolated latency or
that the new candidate meets the targets. Cold shader stalls and residual warm
spikes remain unresolved. No earlier binary's performance or platform verdict
is inherited. Final integrated acceptance remains #23.

## Verification

All [73 host tests passed](host-checks.log) with **zero skips** and process exit
0, including 15 frame-pacing tests. The real native logger regression failed
before the guard with a 103 ms interval instead of 33 ms under the deterministic
slow external debug service. It now exports the 33 ms interval while preserving
all seven log lines. The late-arrival CLI regression failed with 3601 rather
than 3600 intervals; it now honors the end marker and preserves all 3602 original
frame rows in the full launch. Diagnostic event exports are checked separately.

Python compilation and all eight shell syntax checks passed.
[host-checks.json](host-checks.json) records the checks and linked capture hooks.
Target C/C++ compilation, linking, SELF generation and OELF segment checks
passed. The [ABI audit](game-abi-audit.json) identifies the matching unstripped
ELF/source lines, Jaguar flags and unresolved-TLS check. The emitted
[release logger audit](release-log-link.txt) confirms `say()` retains `fputs`
and `fflush` but does not call `sceKernelDebugOutText`. The
[VideoOut audit](videoout-link.txt) confirms Mesa still reaches the recorder.
These checks establish neither an isolated console syscall cost nor a
performance pass.

The [provenance record](provenance.json) pins the current inputs and confirms
they match the configured/compiled closure. A first successful compilation was
correctly rejected by staging after the analyzer boundary fix changed the
input closure. The final reconfiguration/rebuild passed the same guard. No
rejected artifact was handed off. The game root is
`~/.cache/pswaker/game-22-logfile/`, consuming unchanged selected platform
archives from `maintained-15-a`. The [host recovery record](host-recovery.json)
records use of the locked retained zlib package and restoration of pre-task
`.2.3` after package inspection.

The [independent review](REVIEW.md) found no confirmed implementation defects
and retains the hardware-dependent gates. Sixteen retained original 01.10
raw/owner/log blobs were checked byte-for-byte against the Git index; scoped attributes preserve original
CRLF/trailing spaces as evidence rather than rewriting them.

## Exact candidate

PSWaker **01.11**, compiled build **`5f4977765953663bf3f3`**, retains title ID
`PSWK00001`, content ID `IV0000-PSWK00001_00-PSWAKERGAME00000` and installed
content `/app0/game.iso`. Saves/settings remain under `/data/pswaker/`.

| Artifact | Identity |
| --- | --- |
| Private Windows package | `local-research/performance-22-artifacts/candidate-01.11/PSWaker-performance-01.11.pkg` |
| Package size | 1,516,634,112 bytes |
| Package SHA-256 | `b50cbdaf3e996faba3529a399891e397d3d1ff568a777ec628260762e1f8205c` |
| Matching unstripped ELF SHA-256 | `3b4ba738bed2a9485c6710585d15d3326092876ff8d01ff2d2a9c56c0b4c2ad8` |
| SELF SHA-256 | `c8a6d4872866cf0d71429388622b13111d610816e2f087f51f75932df77f2740` |

Private assembly and a second fresh extraction/inspection passed.
[inspection-01.11.json](inspection-01.11.json) and [artifacts.json](artifacts.json)
associate program, image and package. Exported Windows package/ELF copies match
their inspected originals. The inherited inspection wording mentioning #16
describes its tooling origin; this **untested follow-up candidate** status
controls the hardware handoff. No saves, settings, test markers or game data
are committed. The private complete assembly is
`~/.local/share/pswaker-private/performance-22-01.11/`; full build records and
matching ELF accompany the Windows package.

The new disposable cache is
`/data/pswaker/cache/5f4977765953663bf3f3/`. Use only that directory for cold
cache preparation; preserve real profile and recovery data. Follow the updated
[owner checklist](../../../Frame-pacing-checklist.md): full independent Outset
and forest samples, comparable actions, visible timing corroboration and
retrieval **after normal Quit**, retaining all failures. The new diagnostic-cost
events help investigate residual stalls. Do not expect the debugger-sink change
alone to remove cold shader compilation. Return measured shortfalls before
considering any quality or acceptance change. Issue #22 remains open.
