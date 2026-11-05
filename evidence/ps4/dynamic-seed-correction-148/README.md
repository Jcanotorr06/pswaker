# Seed-only correction for the #148 pilot

Recorded 2026-11-04 for [#148](https://github.com/Jcanotorr06/pswaker/issues/148),
following the [failed candidate assessment](../dynamic-validation-148/REPORT.md).
The corrected standalone seed contains **291 descriptions**: all 288 original
records, unchanged in every column, plus exactly the three compatible runtime
discoveries. Two correction runs reproduced identical seed, manifest and
correction-report bytes. Normal complete-package assembly and separate fresh
inspection verified the exact corrected seed extracted from a new private package.

This is a **seed-only** change. The program and matching ELF are unchanged;
Quit still has the reported failure tracked in
[#159](https://github.com/Jcanotorr06/pswaker/issues/159). No Quit diagnosis,
runtime policy change, fixed-shutdown claim or new physical-console result is
part of this correction. The failed package and all earlier evidence remain intact.

[candidate.json](candidate.json) binds exact inputs and results without game bytes
or personal paths. The [public correction workflow](../../../docs/ps4/SEED-CORRECTION.md)
documents reproducibility, provenance, validation and future console handling.
Actual descriptions, database/WAL pairs, image, package, ELF and logs stay private.

## What was corrected

The old 288-description seed missed three descriptions in both returned runtime
snapshots. Their matching identities and complete bytes are now present:

| Added type-1 identity | Complete 2772-byte description SHA-256 |
| ---: | --- |
| `-998174050250713549` | `8953b0009777ab7de30f1112e943f8d404a96ba8015729a8d8fcd11dee6b60fe` |
| `1288118228291800766` | `29b1cbf3caf484e4347b671e6eb781ae0c515b86de6ca120189a1f7ab91596de` |
| `3435039316153706867` | `7821518846c80640c4d340e8ba7acba4a59f19adad2b43179ac2b433589d5bdf` |

The new `collect-model-seed.py correct` command uses the ordinary validated
standalone snapshot/asset interfaces. It checks both source assets, rejects all
identity/description conflicts before publication, deduplicates matching rows
and inserts only the additions into a copy of the old baseline. Baseline rows
retain their complete bytes and first-use metadata. The original runtime and
generated-static source inventories remain in the seed manifest; both new
runtime source inventories are retained under distinct labels.

Both original database/WAL pairs were freshly snapshotted with the public
`complete-package.py pipeline-seed` command. They reproduced the assessed cold
and warm snapshots exactly. The ordered inputs are `runtime-1` = cold and
`runtime-2` = warm. Every added row is attributed to both snapshots, with their
database/WAL hashes and per-source first-use metadata. The correction report's
provenance is `runtime-capture-correction`. These records are not relabeled as
automatically generated particle configurations or as evidence of a new
corrected-candidate console run.

The exact originating actor/effect/material code paths for these three records
remain unresolved. The failed return contained loading waits and one wait near
the first pot break, without configuration identities in those wait events.
The correction traces each description to its immutable real PS4 capture and
retains that attribution limit. It does not fabricate a more precise source
mapping or extend the isolated particle collector's claimed coverage.

## Compatibility and repeated checks

The source program, renderer/configuration, supported USA `GZLE01` revision-0
image and stock 1280x720/30 Hz/synchronous-rendering contract are unchanged.
The retained host/PS4 2,872-byte contract witness remains
`8c3392d2bf28dae71adecc908ed8056d987a6b2db36bb27ddcf07cc138825700`.
All added descriptions came from this exact program's real PS4 recorder and
pass the selected schema 1 / GX v13 / 2772-byte record contract. No arbitrary
raw states or host driver shader binaries were generated.

The same native collector executable reran the fixed dynamic scenario twice
and the static scenario once with the corrected seed as baseline. Each run
recomputed **all 291** identities through the selected seeded XXH3 implementation
and verified all 291 complete descriptions survived the normal host recorder's
round trip unchanged. Each dynamic run again produced 40 actual draws/lookups,
the same per-tick lifetimes and the prior single particle description. The static
control again produced three draws and its prior single material description.
Imported baseline controls remain separate from actual observed draws.

The unchanged public full-description comparator now passes against eight
retained/regression sources: the old baseline, both new runtime snapshots,
retained dynamic and static observations, both fresh dynamic exports and the
fresh static export. Every captured identity and complete description is in the
corrected seed, with no missing or conflicting bytes. This corrects the
previous **membership failure**; it does not retroactively erase the old
candidate's raw waits or prove that the replacement has zero PS4 waits.

Two identical correction invocations reproduced every output file. The original
288 complete baseline rows were also compared directly against the corrected
database, including metadata. All **69** tracked retained private input files
kept identical hashes before collection and after packaging/reinspection. All
**127** original returned files and their private archived copies still match
the original inventory. No prior package, default assembly asset, capture,
save/settings file or archived evidence report was replaced.

## Frozen corrected package

| Item | Identity |
| --- | --- |
| Program version / build-cache ID | `01.23` / `6e885683f47a49a119ae` |
| Matching ELF SHA-256 | `400de6f1bb42fb4fc79f9399f290d2f0ee292e58ea03e4f8eea9c2e4dd7c32ab` |
| Corrected seed | 291 descriptions, 1,216,512 bytes |
| Corrected seed SHA-256 | `d55bc3934764d66543a2a5b56ba02223da403e345d88dffe26c77c0c4b15cbaa` |
| Seed manifest SHA-256 | `524a2a8d9bc0b46fe560aea0d65f33a75231a4d9a6de97dd1fefcf164811716e` |
| Complete package SHA-256 | `058bd19c4fc4be1782b631ad4e808dbddea4b31530f0e3a599c38d71b93090e0` |
| Fresh inspection SHA-256 | `ab0caea56632e249def6210b2cec86da239f8a887fbdbda123c211301c9325a4` |
| Correction report SHA-256 | `c82fd699515d1d0164c30081cc26360d132c45d379ab0233d3bdd0a207f71996` |

Ordinary `assemble --kind game --assembly-assets` and a separate fresh `inspect`
both verified the exact seed bytes from this package, its provenance manifest,
image and matching program/ELF. The private package directory is
`dynamic-148-seed-corrected-complete-01.23`. The private `dynamic-148-seed-correction`
directory retains both corrected assets/reports, fresh runtime snapshots,
collector exports, commands, logs, coverage comparison and immutability records.

The private Windows Downloads handoff
`PSWaker-01.23-dynamic-pilot-148-seed-correction` retains the installable package,
matching ELF, standalone corrected asset, correction/coverage/identity reports,
future bounded console instructions, unfilled owner templates and hash list.
Fresh inspection of this copy reproduced the same package/seed/inspection
identities. Its instructions state that the known Quit failure is unchanged.

The package's program/build-cache ID is deliberately unchanged. A retained cache
already containing the discoveries cannot establish inclusion in the corrected
seed; a selected future cold test must retain/rename only that build's disposable
cache and preserve saves/settings. A new package hash and seed hash require
new affected physical evidence. Normal runtime fallback/recording remains
synchronous. The new package has not been physically validated.

## Public regression verification

The correction test first failed because the `correct` command was absent,
then passed after implementation. Six public CLI tests now cover actual
correction output, complete baseline/input preservation, source attribution,
deduplication, deterministic repeat outputs, zero-addition byte preservation,
conflicts against the baseline and between captures, incompatible/corrupt/hash-
mismatched/provenance-invalid inputs, live sidecars, and output preservation.
Fixtures are synthetic and contain no actual game descriptions.

The real-tool synthetic integration check prepares static and dynamic assets,
corrects them with overlapping runtime snapshots, assembles the corrected game
package, then freshly inspects its exact seed bytes and manifest. All **21**
focused collector/preparation/correction tests and that packaging integration
check pass. Pyright reports zero errors/warnings; Python compilation, maintained
shell syntax and Git whitespace checks pass. The full reference-enabled WSL
suite completed **252 tests, 60 platform/environment skips, no failures** in
359.371 seconds, including all ten real initialized-renderer startup checks.
The prepared game source and actual packaging tools were enabled. Native Windows
tool/desktop checks were among the environment skips; this correction does not
change the player executable or desktop workflow.

## Remaining boundary

The original owner observed correct pot breaks, three cold waits and a Quit
crash in both runs. Those observations still belong to the failed package.
The corrected candidate's physical preparation, zero-wait behavior, timing,
startup/resource observations and save/settings preservation are unverified.
Do not close #148 or waive known waits based on this automated correction.
Quit diagnosis remains exclusively in #159; this seed task changed no shutdown
code and does not request a duplicate diagnostic capture or story progression.

## Standards

Independent review of all seven staged task files against pre-correction commit
`1132d12178603e06e7ae5edcd1f5e294f536ecde` found no documented-standard breaches
or actionable heuristic smells. Private seed/build bytes stay excluded and
synthetic tests exercise the public correction workflow. Final test and review
notes were completed after review without changing the implementation.

## Spec

Independent review found no substantive scoped requirements missing, no scope
creep and no incorrect seed-correction behavior. It confirmed preservation of
the baseline, the three actual runtime additions and both source mappings,
honest provenance, exact inspected package/seed identities, explicit absence of
physical acceptance and exclusion of Quit work.

It found one minor documentation count error: this report initially said nine
comparison sources, while `candidate.json` contains eight. The wording above
was corrected and checked directly against the recorded snapshot count; no
implementation change or additional review agent was needed.

Review totals: Standards 0 findings; Spec 1 minor documentation finding,
corrected. No known finding remains within either axis.
