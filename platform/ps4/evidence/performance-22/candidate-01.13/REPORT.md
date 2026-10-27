# Seeded cold-preparation candidate 01.13

The owner subsequently [accepted current performance as sufficient for the
initial release candidate](../OWNER-DECISION.md) and deferred further optimization.
The requests for renewed performance sampling below are historical. This decision
does not supply a 01.13 console result or alter this package's recorded identity.

This follows the [01.12 return](../console-return-01.12/REPORT.md). Both warm
samples met every numerical limit with zero recorded shader waits. Cold Outset
had 6,607.918540 ms of waits, and cold forest's 150.151814 ms maximum included
a 122.379947 ms shader wait. The owner supplied the route's pipeline database
and matching WAL so the existing renderer can prepare those known configurations
before gameplay, including on an empty disposable runtime/driver cache.

**UNTESTED on PS4.** This is a justified preparation candidate, not a demonstrated
cold performance fix. New states/effects may remain uncovered and all gameplay
stalls still count. Physical timing verification and the 01.12 internal shutdown
evidence gap remain unresolved. No earlier package's performance or platform
verdict is inherited. Issue #22 remains open; final integrated acceptance is #23.

## Bounded change and seed provenance

Complete-package assembly optionally snapshots `pipeline_cache.db` and its
adjacent WAL on private copies, validates integrity/schema/record versions and
sizes, and bundles one standalone DELETE-journal database at
`/app0/initial_pipeline_cache.db`. It strips only the selected runtime's optional
merge-identity metadata. The manifest pins source hashes, configuration counts
and the seed SHA-256; fresh inspection validates the extracted asset. Seeds and
their input databases stay private. The strict data-free program staging
allowlist is retained; the seed is a separately identified complete-package asset.

The returned main database alone contains **200** records; the committed view
with its WAL has **287**. The bundled seed contains **1 clear configuration**
(version 5, 8 bytes) and **286 GX configurations** (version 13, 2772 bytes).
Both original input files remain byte-identical. [seed-source.json](seed-source.json)
associates them with source build `bc90c33b639295f36912` and its 01.12 package.
The returned file inventory and actual seed are retained privately.

| Asset | SHA-256 |
| --- | --- |
| Original database | `c9ab6f97ccef18fcd08c2e4915140c5990f98fcae7cb4771df90619407864c2e` |
| Original WAL | `6c865d0295536048b31411a1aec5d758642c26134d86d0519ada76641a643886` |
| Installed standalone seed | `7e3f8527203dc488b5ae646904c986ac596d7d4017db45a0fcb18ae29de51dc1` |

The selected renderer already merges this asset and queues known pipelines;
its compilation/preparation logic is unchanged. The program adds compile-time
version/size assertions in the renderer target, tying the tool's ABI contract
to the actual structures. Original 30 Hz logic, stock textures, 1280x720 internal
allocation, synchronous missing-pipeline behavior and selected driver/library
archives remain fixed. The seed contains descriptions, not driver shader binaries.

Preparation can run during renderer startup and overlap other startup work.
The existing preparation screen drains the remaining queue before gameplay;
its final wait is not the total compilation time. Preserve startup, seed-merge,
pipeline-count and preparation records without inventing a loading-time limit.
An empty disposable cache with a bundled description seed is explicitly identified
as this candidate's cold condition; it is not relabeled as the earlier unseeded run.

## Verification

All **84 host tests passed with zero skips**, process exit 0, including 17
complete-package CLI tests at the newly approved seam. [host-checks.log](host-checks.log)
preserves the full output; [host-checks.json](host-checks.json) records the checks.
Regressions first failed for the absent snapshot command, accepted incompatible
records, absent assembly option, and rejection of valid runtime merge metadata.
They now verify WAL-only rows, unchanged originals, standalone output, invalid
schema/type/version/size/embedded version/frame/empty/extra-table rejection,
metadata normalization and manifest-bound freshly extracted seed identity.
The remaining recorder, analysis, persistence, controls, audio and platform
checks still pass. Host tests do not verify physical console presentation.

PS4 target C/C++ compilation, renderer ABI assertions, linking, SELF conversion,
Jaguar flags, unresolved-TLS audit and OELF segment checks passed.
[game-abi-audit.json](game-abi-audit.json) identifies the matching ELF.
[videoout-link.txt](videoout-link.txt) confirms the Mesa flip-submission wrapper;
[release-log-link.txt](release-log-link.txt) confirms retained file logging and
absent release debugger duplication. Python compilation and eight shell syntax
checks passed. [provenance.json](provenance.json) confirms current inputs match
the compiled closure at collection. [REVIEW.md](REVIEW.md) records independent
Standards/Spec reviews and the corrected metadata compatibility finding.

The final build uses `~/.cache/pswaker/game-22-logfile/`, consuming unchanged
verified archives from `maintained-15-a`. Initial ABI-check builds exposed include
dependency issues; the check now compiles in its owning renderer target. Only
the final successful build is handed off. [host-recovery.json](host-recovery.json)
records locked retained zlib use and restoration of the pre-task host package
after successful final assembly and fresh inspection.

## Exact candidate and owner return

PSWaker **01.13**, compiled build **`f236a035ac406940e76a`**, retains title ID
`PSWK00001`, content ID `IV0000-PSWK00001_00-PSWAKERGAME00000`, installed image
`/app0/game.iso` and writable user data `/data/pswaker/`.

| Artifact | Identity |
| --- | --- |
| Private Windows package | `local-research/performance-22-artifacts/candidate-01.13/PSWaker-performance-01.13.pkg` |
| Package size | 1,517,879,296 bytes |
| Package SHA-256 | `b3a3f46b8d4b7704b90881b74c7b980543184488cd7e7729f8823706d61a405c` |
| Matching unstripped ELF SHA-256 | `a99bcca89c4c0a54d808400ddffbfdca6d8df620d601b814386bf2fcd38e9ebb` |
| SELF SHA-256 | `ce00c04b039bf7a54bd4f547f77e4b06fd59c11de162c277045ec67caca195d8` |

Assembly and a second fresh extraction/inspection passed.
[inspection-01.13.json](inspection-01.13.json) and [artifacts.json](artifacts.json)
associate program, image, seed and package. Windows package/ELF copies match the
inspected originals. The inspection's inherited #16 wording describes tooling
origin; this report's untested 01.13 status controls the handoff. The complete
assembly is `/home/joseph_cano/.local/share/pswaker-private/performance-22-01.13-final`. Full build records and matching ELF
accompany the Windows package. No game bytes, pipeline database bytes or genuine
profile/test data are committed; private assembly is not distribution clearance.

Use only `/data/pswaker/cache/f236a035ac406940e76a/` for this build's disposable cold
cache preparation. Follow the [owner checklist](../../../Frame-pacing-checklist.md):
confirm zero runtime cache files before cold initialization, 287 merged seed
records and known pipeline preparation; sample Outset and forest independently
with the same actions, then repeat both after full relaunch with the cache retained.
Keep the installed seed present during cold testing. Record mismatches, uncovered
hitches, graphics/audio correctness, startup/resource observations and every failure.
Leave timing verification false until displayed timing is actually corroborated.
Retrieve after normal Quit and retain the visible outcome plus all internal
shutdown stages, including any missing markers. Limits remain average >=29.5 FPS,
p95 <=35 ms, p99 <=50 ms, maximum <=100 ms for each sample independently.
