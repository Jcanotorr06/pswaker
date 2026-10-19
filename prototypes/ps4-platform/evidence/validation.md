# Host build evidence; console verdict pending

Question: [Test the candidate PS4 platform with a disc-free diagnostic prototype](https://github.com/Jcanotorr06/pswaker/issues/10).
This is a disposable diagnostic branch. No PS4 execution, install, owner observation,
game integration or game performance result is recorded here.

## What was built

The final diagnostic source and packaging scripts are commit
`ea5b420906a903255562fa7cc1036ac7074b42d5`. The diagnostic's compiled identity is
`97fc99208640c483fdc2`. Later Markdown and evidence files are deliberately excluded
from that identity. The identity covers prototype source/scripts/locks and recorded
Clang, CMake, Ninja and .NET versions; it is not a hash of the entire OS.

Two previously absent build directories on the same Ubuntu 24.04.3 / WSL2 host
were populated from verified downloads, then independently compiled the selected
LLVM runtimes, SDL3, Dawn, Mesa, Aurora, diagnostic and patched LibOrbisPkg.
No target build archives were copied between roots. The exact SDK/source locks,
local adaptations, host inventory and fetched dependency closure compare equal.

| Build | Fresh preparation started (UTC) | Final packaging completed (UTC) |
| --- | --- | --- |
| `/tmp/pswaker-clean-a` | 2026-10-19 03:43:28 | 2026-10-19 04:09:37 |
| `/tmp/pswaker-clean-b` | 2026-10-19 03:43:39 | 2026-10-19 04:09:44 |

These were not two uninterrupted successful invocations. The initial build logs
retain a packaging-metadata error: Dawn's dependency fetcher can populate a shallow
repository directly via `FETCH_HEAD` without creating `origin`. The provenance
collector was corrected to capture that fetched revision/URL and tracked diff.
The diagnostic's viewport sizing was also corrected before handoff. Both roots
then ran [finalize-build.sh](finalize-build.sh): clean and recompile the complete
probe target from the frozen final source, retain their already freshly compiled
external dependencies, and rebuild the packager and package. Initial probe logs
remain under `before-final-probe/`; final logs and the failure are preserved.

## Artifact to install

Use **clean-a**, title `PSWaker Platform Diagnostic`, title ID `PSWK00010`,
version `01.00`, build `97fc99208640c483fdc2`.

Local Windows artifact:
`C:\Users\Joseph Cano\Code\pswaker\local-research\diagnostic-artifacts\PSWaker-Platform-Diagnostic.pkg`.

SHA-256:

| Artifact | clean-a | clean-b |
| --- | --- | --- |
| PKG | `30fba07810fc67da324415330eb4f3df3e66c6188a22d2fee6726df9b9318cfb` | `2889424ad4c527b92bd60742e58667914910667359a464869cf958dfe75561e5` |
| SELF | `a8aeb9cb40dc050dc6be9efa8559958ab57f0eb9ffaca11661a57a96e393ed08` | `a09bf5ce7e5369e1579f0205c47c0acb70bd2b68ac8bf7096b59dfdc2d07319f` |
| ELF | `8201c9dbf32f17c5e67b17edddb4ae9740a529f730fd6b9d44249ad63e4459b1` | `ee8db70c19db8bcbafa9545ed04ac3472437a57b8624cc467ea317faffda1630` |

The Windows package hash was checked after copying. Its matching unstripped ELF,
artifact hashes, packaged input manifest and console checklist are retained beside
it. No binary is published on this branch.

## Inspection and differences

[compare-builds.py](compare-builds.py) completed successfully. It verifies artifact
hashes, ELF64/x86-64 and zero-based first load segment, compiled/packaged build ID,
extracted SELF identity, exact eight-file package inventory, SFO title/version,
and the recorded input closures. Outer PKG metadata and inner PFS contents are
inspected separately. No game/key payload is in that inventory. See
[comparison.json](comparison.json) for the complete records.

The packages and ELFs are **not byte-identical**. Only `eboot.bin` and
`build-info.json` differ within the logical package inventory; the latter includes
the differing SELF hash and build-root-specific dependency metadata. The allocated
ELF sections that differ are `.text`, `.rodata` and `.rela.dyn`, all with equal sizes.

[explain-differences.py](explain-differences.py) investigates the layout differences
using LLVM disassembly and NUL-terminated constant targets; its results are in
[difference-analysis.json](difference-analysis.json). Changed instruction operands
reference relocated constant data, including embedded build-root paths and strings.
This supports a constant-pool layout explanation, rather than a claim that the
binary is deterministic. The audit records its limits: NUL-terminated comparisons
do not prove arbitrary binary-data equivalence, and normalizing root paths does
not make the whole `.rodata` section equal. It is not a semantic-equivalence proof.
No bit-for-bit reproducibility claim is made.

Of the changed instructions, 57,842 reference equal nonempty ASCII strings after
root normalization, and 1,059 reference equal empty or non-ASCII NUL-terminated
bytes. No changed instruction remains outside those categories. All 11,877 changed
relocation records retain their location/type and reference equal normalized
NUL-terminated target bytes. These counts describe this bounded audit only.

## Remaining decision gate

Follow the [console checklist](../README.md): one cold-cache launch and two
warm-cache launches, ten minutes each, complete close between launches, controller
disconnect/reconnect and deliberate resume, continuous audible tone, expected
visuals, checked GPU/runtime results, persistence, resource review and successful
FTP evidence retrieval after every run. Confirm firmware and GoldHEN versions for
the actual runs; their current manifest values are owner-reported baseline data.

The diagnostic has not passed this gate. Keep its decision open until the owner
returns the actual visible/audible observations and logs. Synthetic audio and file
checks cannot establish game DSP, game-save correctness or 720p30 performance.
SDK binary source-revision gaps and sample-module notice questions remain explicit
in the source/SDK locks and README; this local handoff does not settle distribution.
