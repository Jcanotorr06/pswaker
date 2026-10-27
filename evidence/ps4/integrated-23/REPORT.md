# Integrated first-playable review (#23)

**PENDING owner validation of the final candidate.** The owner confirms that
**01.12** is currently installed. Its original logs, cache, analyses and saves
are retained privately under
`local-research/performance-22-artifacts/candidate-01.12/evidence/`.
They remain baseline evidence, not 01.13 observations.

This work starts from `develop` at
`91909bfadf14ac6d69ab7fccd61d32103208d907`, on
`feature/23-integrated-first-playable`. The
[integrated owner checklist](../../../docs/ps4/Integrated-checklist.md) and
[return form](owner-return.md) cover the combined route, controls, audio,
save/update/recovery, lifecycle and evidence responsibilities.

## Applicable performance decision

The [owner-approved exception](../performance-22/OWNER-DECISION.md) and
[issue #22 resolution](https://github.com/Jcanotorr06/pswaker/issues/22) allow the
initial release candidate to proceed with current performance. Further optimization
is deferred to [#51](https://github.com/Jcanotorr06/pswaker/issues/51). The original
per-sample limits remain reference goals: average >=29.5 FPS, p95 <=35 ms,
p99 <=50 ms, maximum <=100 ms. The exception does not relabel failures, verify
physical presentation timing, establish seed benefit or accept a new binary.

The [01.12 return](../performance-22/console-return-01.12/REPORT.md) retains four
separate completed samples. Cold Outset measured 28.753154 FPS, p99 66.765600 ms,
maximum 1234.577616 ms; cold forest maximum was 150.151814 ms. Both warm samples
met the numerical limits. Physical timing remains unverified. Visible clean Quit
was owner-confirmed, while internal shutdown completion is missing from those
logs. These are preserved limits, not reasons to require more optimization before
the initial release candidate.

## Fixed candidate for owner validation

Reuse the already prepared **PSWaker 01.13**, compiled build
**`f236a035ac406940e76a`**. No new game binary is selected by this task.
The [original preparation report](../performance-22/candidate-01.13/REPORT.md),
[inspection](../performance-22/candidate-01.13/inspection-01.13.json) and
[artifact record](../performance-22/candidate-01.13/artifacts.json) remain intact.

| Item | Identity |
| --- | --- |
| Private Windows package | `local-research/performance-22-artifacts/candidate-01.13/PSWaker-performance-01.13.pkg` |
| Package bytes / SHA-256 | 1,517,879,296 / `b3a3f46b8d4b7704b90881b74c7b980543184488cd7e7729f8823706d61a405c` |
| Matching unstripped ELF SHA-256 | `a99bcca89c4c0a54d808400ddffbfdca6d8df620d601b814386bf2fcd38e9ebb` |
| SELF SHA-256 | `ce00c04b039bf7a54bd4f547f77e4b06fd59c11de162c277045ec67caca195d8` |
| Installed seed SHA-256 / descriptions | `7e3f8527203dc488b5ae646904c986ac596d7d4017db45a0fcb18ae29de51dc1` / 287 |
| Title ID / content ID | `PSWK00001` / `IV0000-PSWK00001_00-PSWAKERGAME00000` |
| Installed game / writable profile | `/app0/game.iso` / `/data/pswaker/` |
| Disposable runtime/driver cache | `/data/pswaker/cache/f236a035ac406940e76a/` |

Support remains PS4 Slim / 9.00 / GoldHEN v2.4b18, USA GZLE01 revision 0,
stock textures, original 30 Hz logic, allocated 1280x720 internal rendering and
Linux/WSL2 preparation. The description seed is distinct from driver shader
binaries; cold means the disposable runtime/driver cache is empty with that
installed seed retained. No 01.13 console results are present yet.

## Coverage and remaining evidence

| Contract | Existing evidence | Final candidate status |
| --- | --- | --- |
| Title, name entry, prologue, Outset and forest; audio | Earlier startup/route returns, exploratory play through Dragon Roost; 01.12 scene correctness observations | Pending C/W1/W2 route and audible/visible observations |
| Fixed controls, menus, partial/full triggers, input recovery | Implemented controls and host checks; earlier candidate evidence | Pending action/context rows on 01.13 |
| Completed saves/settings after full relaunch and separately after update | [#20 return](../persistence-20/console-return-2026-10-26/REPORT.md) | Pending 01.12-to-01.13 update and 01.13 relaunch evidence |
| Unavailable storage, failed writes, corruption, explicit restore, pending-write Quit | Implemented cases and host regressions; original failures retained | Pending isolated controlled cases on 01.13 |
| Cold and two retained-cache route runs | Prior launches remain tied to their own binaries | Pending 01.13 launch/cache associations |
| Six independent frame samples and shader hitches | Four 01.12 samples retained; recorder/analyzer available | No 01.13 samples; preserve missing rows and measured shortfalls under performance exception |
| Startup/preparation/loading/transition and resource observations | Existing instrumentation and documented measurement limits | Pending final route observations and trend review |
| Crashes/hangs/audio defects/shutdown | Prior GBA panic fixed and host-regressed; 01.12 visible clean Quit, missing internal completion | Pending affected 01.13 observations and logs; investigate failures |
| Two fresh builds and ELF/SELF/package inspection | Unchanged platform has [two clean builds](../verification-15/REPORT.md) | Both final changed game-input builds, assembly and fresh inspections passed; difference review below |
| Source/input closure and actual installed identity | 01.13 compiled inventory and package inspection retained | Full current and both repeated closures match; installed association awaits owner return |
| Combined license/notices/module review | Inherited audit and exact module provenance retained | Private use only; unresolved redistribution rights remain |

Earlier issue closures and the performance exception do not create hardware
observations for this package. The owner's current 01.12 installation establishes
an update baseline, not the outcome of an update to 01.13. Each new materially
changed binary requires its affected hardware evidence. No first-playable
declaration or public release is made.

## Build/provenance review

The [repeat-build procedure](repeat-builds.py) archives the fixed source commit,
checks the current full input closure against the original compiled inventory,
and reinspects a private copy of the existing candidate without overwriting its
original evidence. It then extracts two independent source trees, copies only
verified downloads into fresh game roots, and builds game/game-local Aurora
objects anew with compiler caching disabled. Each receives an assembly-time
ELF-to-SELF round trip, OELF inspection and a second fresh package extraction.

The selected `maintained-15-a` SDK/runtime/driver/SDL/Dawn archives are unchanged
inputs; they are **not rebuilt by this repetition**. Their earlier two independent
clean platform builds remain the platform evidence. This task repeats the final
changed game inputs, rather than claiming two new entire-stack clean builds or
two independently provisioned machines. Rebuilt artifacts are provenance checks;
they never replace the candidate's package/ELF/SELF hashes or add console runs.

[candidate-closure.json](candidate-closure.json) records equality with all **10,989
platform** and **142 port** input entries, the prepared-source inventory hash and
compiled build identity. Both repeated builds have that same input closure.
The archived starting source commit is retained with SHA-256
`5466bc3386525f93658f54156f15d1490270311dd8ad1d5f3faab63bd5da7016`.
[candidate-reinspection.json](candidate-reinspection.json) records a fresh extraction
of the unchanged 01.13 package; both Windows package and matching ELF copies were
also hashed again and match it.

[repeat-builds.json](repeat-builds.json) retains each build's dates, hashes and ABI
audit. On 2026-10-27 UTC, A ran 02:35:03-02:46:58 and B 02:35:03-02:46:59.
Both checked 1,393 C/C++ compilation commands for Jaguar/btver2 flags, retained
unstripped ELFs and debug lines, rejected unresolved TLS initializers, and passed
SELF/OELF checks, complete assembly and a second fresh package inspection.
Image, seed and stable update identity remain unchanged. New ELF/SELF/PKG hashes
describe only these host rebuilds, not the installed 01.12 or selected 01.13.

### Explained differences and comparison limits

[build-differences.json](build-differences.json) checks all **996** ELF sections:
every section's layout matches and **989** sections are byte-identical. The
seven differing sections are `.text`, `.rela.dyn`, `.rodata`, `.debug_info`,
`.debug_str`, `.debug_line` and `.symtab`. Package payload differences are limited
to `eboot.bin` and its two hash-bearing manifests; image, seed, SFO, artwork,
modules and keystone match.

[text-differences.json](text-differences.json), produced by
[explain-text.py](explain-text.py), classifies the 158,258 changed `.text` bytes:
76,648 changed instructions keep the same instruction form and address a matching
path-normalized ASCII string, 1,621 keep the form and match only a NUL-terminated
prefix of a binary/empty target, and one references a different compilation-time
string. The latter is `CARDInit`, selected Aurora `lib/dolphin/card.cpp:299`, whose
source uses `__DATE__`/`__TIME__`: A contains `21:43:44`, B `21:43:56` (host local
compile times). All 65,235 dynamic relocation rows retain their location/type:
49,292 are identical, 15,485 address matching normalized ASCII strings and 458
match only a NUL prefix. No changed instruction form or otherwise unclassified
relocation remains within this bounded analysis.

[data-differences.json](data-differences.json), produced by
[explain-data.py](explain-data.py), confirms the normalized `.debug_str` string
multisets match despite order changes. Exactly four symbol values move within
`.rodata`; all four retain identical bytes over their declared sizes. Among
normalized printable `.rodata` NUL segments, only the two compilation-time
strings differ. **116/117 nonprintable excess segments remain**, so printable
string equality is not a comparison of every binary table. Full binary target
extents for the prefix-only instruction/relocation matches, and individual
`.debug_info`/`.debug_line` records, are not proved equivalent. Path/time strings,
pool placement and corresponding address references explain the observed
nondeterminism; these bounded checks and their residual limits do not establish
formal semantic equivalence or an extra console run. Raw artifacts and reports
remain available for further inspection. The first broad section comparison and
instruction classification are retained privately alongside the refined results.

Complete build roots, source archive, manifests, matching ELFs, packages and logs
stay private at
`/home/joseph_cano/.local/share/pswaker-private/integrated-23-builds-final/`
and the recorded cache roots. [host-recovery.json](host-recovery.json) confirms
the hash-checked locked zlib package was used for the build and the pre-task
version was restored afterward. No host guard or dependency lock was bypassed.
The first collector attempt stopped before compilation because it read the wrong
manifest field; that attempt is retained, the field is corrected, and the temporary
host recovery restored the pre-task zlib version on exit. No candidate was changed.

## Host checks and review

[host-checks.json](host-checks.json) records Python byte compilation, eight shell
syntax checks and focused game/package tests. The [full discovery log](host-checks.log)
retains **73 passed and 11 skipped**, exit 0: the launch omitted the existing
`PSWAKER_HOST_ROOT` variable needed by real-SDL GCI tests. The
[targeted follow-up](gci-checks.log) supplied the retained host SDL build and
passed all **11** skipped GCI cases with zero skips, exit 0. Thus all **84**
test cases passed across the full and targeted runs. The original skipped run
is preserved; it is not represented as a zero-skip full-suite run. Host fixtures
and services do not establish console acceptance.

[baseline-review.json](baseline-review.json) records a read-only inventory of the
owner-supplied 01.12 evidence: 37 files, including the retained save. The complete
relative-path/size/SHA-256 inventory stays private and its hash is recorded.
This corroborates retained inputs; it does not add a save/load or console observation.

Independent Standards and Spec reviews are retained in [REVIEW.md](REVIEW.md).
They found no actionable defects in the preparation/checklist implementation,
and explicitly retained missing hardware results as evidence gates.

## Licensing and private artifacts

[LICENSING.md](../../../docs/ps4/LICENSING.md) and the retained source/notice inventories cover
the game/DSP, reader, renderer, runtime, SDK and host packager. Original per-file
notices, ordered local patch hashes and corresponding-source/build recipes must
remain with any permitted combination. Review applies to the **actual packaged**
`libSceFios2.prx`, `libc.prx` and `right.sprx`, not a top-level license label.
The inspection binds their hashes to this complete package.
[license-review.json](license-review.json) rechecks **103 platform notices**,
**23 game notices**, and all three actual packaged module hashes against the
retained pinned-archive audit. These provenance checks do not resolve distribution
grants or replace review of the combined terms.

Inherited sample-module/import-stub rights and combined redistribution terms
remain unresolved; the later desktop-release work tracks those separately in
[#47](https://github.com/Jcanotorr06/pswaker/issues/47). Private complete-package
assembly is not redistribution clearance. No game image, seed bytes, saves,
executable, package, keys, credentials or private network details are committed.
Public release remains outside #23.

## Handoff

Use [Integrated-checklist.md](../../../docs/ps4/Integrated-checklist.md) with the currently
installed 01.12 as the before-update baseline and the fixed 01.13 package above.
The agent can review returned evidence and investigate defects; the owner must
perform and observe the console actions. Preserve every failure and missing row.
Any substitute timing claim requires its own agreement; the recorded performance
exception remains an exception with disclosed limits. If the selected stack is
invalidated, reopen [#6: Choose the PS4 platform stack and upstream integration
strategy](https://github.com/Jcanotorr06/pswaker/issues/6) before replacing it.
