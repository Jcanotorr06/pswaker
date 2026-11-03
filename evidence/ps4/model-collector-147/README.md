# Model/material collector pilot (#147)

Recorded 2026-11-02 for [#147](https://github.com/Jcanotorr06/pswaker/issues/147),
part of #136. This is an automated asset/material collection and private package
result. PS4 preparation, physical pot appearance and full-game coverage remain
unverified. The [runnable workflow and dynamic-pilot handoff](../../../docs/ps4/MODEL-COLLECTOR.md)
are maintained separately; [pilot.json](pilot.json) binds the data-free identities.

## Executed scenario and result

`always-small-pot-stock-v1` mounted the owner's supported USA `GZLE01` revision-0
image through the game disc/archive loaders and loaded
`Always.arc:bdl/obm_kotubo1.bdl`. The fixed model has one joint, shape and material.
The collector initializes the normal GX state and game transform tables, uses
the game's J3D loader/model/material/display-list and draw-buffer paths, then
executes three stock-material frames with the fixed state documented in the
workflow. It does not boot a stage or consult an owner's save/settings.

Both fresh runs observed three GX pipeline lookups and three draws at 1280x720,
one sample. They generated the same single type-1/version-13/2772-byte description,
with signed SQLite identity `-7485608149410595803` and full-description SHA-256
`21d64659ba67a00c25c2c4fdec5dfd5bb827982a1abfd5c8c65d1c51d782cc95`.
Neither run collected the preloaded baseline as if it had been drawn.

The description is new relative to the 287-description retained runtime baseline:
**one collected, zero baseline-covered, one added, 288 combined**. All 287 prior
records retain identical complete bytes; deduplication uses identity and complete
description bytes, ignoring only first-use frame metadata. The standalone observed
assets, combined seed bytes and per-configuration mappings agree across both
fresh runs. This is generated `asset-material-draw` provenance, not observed PS4
gameplay. No zero-new case is disguised as expansion; synthetic checks also
exercise the zero-new branch, which preserves the exact baseline asset bytes.

## Compatibility contract and limits

The collector uses prepared SwitchWaker `ba8d0a31446cd53ceaebd6b7269cca641e73bf4c`,
decomp `b09eebc39852e18397031d9a563a8eae124f21f1` and the selected reconciled
PS4 Aurora source tree. The retained build manifest binds all prepared source
inventories, renderer inventory identity, collector/adapter sources, compiler,
source-built host Dawn/SDL archives and runtime library hashes. The production
program remains the matching verified 01.23 program; its startup, logic rate,
synchronous missing-pipeline policy, quality and storage behavior are unchanged.

The data-only contract witness was compiled with the actual PS4 renderer and
host collector compiler command lines. Its **2,872 complete bytes match**, SHA-256
`8c3392d2bf28dae71adecc908ed8056d987a6b2db36bb27ddcf07cc138825700`.
It includes schema 1, clear v5/8 bytes, GX v13/2772 bytes, 64-bit hash width,
little-endian representation, all top-level field offsets, and the complete
default clear/GX objects. Unique object representations are asserted. This goes
beyond matching struct sizes, but default objects alone do not prove all states.

For an independent known-runtime control, the collector recomputed all **287**
baseline identities with the selected seeded XXH3 implementation. After normal
renderer loading, preparation and shutdown, the public snapshot interface
exported all 287 with matching identities and full description bytes. The actual
model observation also matched its independently recorded normal GX recorder
entry, including all 2772 bytes. Imported controls and actual draws remain separate
counts. The new pot configuration has **no identical known PS4 runtime sample**;
its first physical preparation/rendering is an explicit remaining equivalence
limit, not an inferred match from the controls.

Host Vulkan selected BGRA8Unorm/Depth32Float, one color attachment and one sample,
with observed layout key `16288162637680331091`. The retained compatible #112
PS4 log identifies RGBA8Unorm and a 1280x720 internal target; the selected renderer
uses Depth32Float. This surface-format difference is deliberate evidence of a
host/target limit. Description identity is seeded XXH3 over the complete config,
independent of target layout. Compiled pipeline identity additionally hashes
`layout.key`. On PS4, `rebuild_pipeline_cache` passes the PS4 scene layout and the
single-sample/single-color offscreen layout into the normal creation path; it
does not reuse the host's compiled driver objects or BGRA layout key. The same
source applies destination-alpha/layout variants during creation. No normal
attachment, MSAA variation, actor lighting/fog, destruction/carrying or dynamic
effect state is exercised by this scenario. Those states remain explicit gaps.

Host rendering and an inspected package do not establish that the new entry
successfully prepares on PS4, or establish startup/resource scaling. Those
targeted observations remain with #138 and the static/dynamic pilot handoff in
#148. The existing baseline acceptance and all prior evidence remain unchanged.

## Private complete package

The ordinary `assemble --kind game --assembly-assets` interface combined the
prepared standalone asset with the verified 01.23 program and matching ELF.
Assembly extracted and checked the package; a separate `inspect` command then
freshly extracted it again and identified the exact seed bytes. Program/build,
ELF, seed, package and assembly/inspection identities are in [pilot.json](pilot.json).

| Identity | SHA-256 / value |
| --- | --- |
| Program build | `6e885683f47a49a119ae` / `01.23` |
| Matching ELF | `400de6f1bb42fb4fc79f9399f290d2f0ee292e58ea03e4f8eea9c2e4dd7c32ab` |
| Combined seed | `37779b102fff3c8bd71330c77a78efd49ac9881b89bd17c5743bacb4daa281b4` |
| Seed size | 1,204,224 bytes |
| Complete package | `873434a91a3ea5e899b1f959c0b58d3fb0729a7f31561e64f6a9e5e7aa9c8196` |
| Fresh inspection | `0fe1b880bbebbf6eb2a3d63cd3db7ce85ef2210905b520f034213e2f7599a5a8` |

The existing private artifact root retains final `model-147-build-j`, both
`model-147-collection-f`/`model-147-collection-g` exports, both
`model-147-seed-f`/`model-147-seed-g` prepared results, `model-147-complete-01.23`
with its matching ELF and package reports, and `model-147-pilot` with commands,
logs and the private summary. The immutable original baseline remains
`performance-22-seed-01.13`; original captures, packages and seeds were retained.
Six source files (image, matching ELF, baseline database/manifest, and the known
runtime database/WAL pair) had identical hashes before collection and after
packaging/reinspection. Both public preparation calls also verified their full
input inventories unchanged. The baseline assembly asset was not replaced.
Earlier build-i collection-d/e and seed-d/e records remain retained. Final
build-j runs reproduce their exact combined seed **and provenance manifest**;
another independent inspection of the retained complete package confirms the
same seed and inspection identity after the final collector cleanup.

## Verification record

Three synthetic external-process tests invoke the public `collect` command,
checking repeatable exports, exact collector/build/image/resource attribution,
normal-recorder agreement, failed-attempt retention and rejection of malformed
or zero-draw reports. The synthetic process models the executable boundary;
the private runs separately establish actual J3D/GX execution.

The public synthetic preparation tests cover deterministic output/mapping,
baseline preservation, deduplication, zero additions, no-draw/malformed/corrupt
exports, incompatible records, identity/description conflicts, missing collector
provenance, mismatched attribution hashes, existing output preservation and
source immutability. A real-tool synthetic complete-package test passes the
prepared asset through normal game assembly and a separate fresh inspection,
checking the extracted seed identity and provenance. Fixtures contain no actual
model bytes, descriptions or images.

The first preparation test failed because the command did not exist; it passed
after implementation. Missing attribution and attribution/hash mismatch checks
also failed before their corresponding guards were implemented. Final checks:

- Full reference-enabled WSL suite: **243 tests, 60 platform/environment skips,
  no failures**, 362.545 seconds. The prepared game source and real packaging
  tools were enabled, including all ten real-renderer startup tests.
- All **12 focused collection/preparation tests** pass; the real-tool synthetic
  collection-to-package test also passes a separate fresh inspection.
- Pyright: zero errors/warnings. Python compilation, all maintained top-level
  shell syntax checks and native Git whitespace checks pass.
- Final native collector build/PS4 contract compilation, both final actual
  collections, both standalone preparations and independent package inspection
  pass. They reproduce the exact previously frozen seed/manifest bytes.

The first broad suite also passed (240 tests, 101 skips); the final run includes
the added command tests and enables the prepared game for the previously skipped
integration checks. Both logs and static-check attempts remain private under
`model-147-pilot`. Independent review findings and their corrections follow.

Failed integration attempts remain visible: the host build first exposed a
missing system zlib assumption and upstream optional desktop APIs absent from
the selected renderer. The collector now uses the source-built dependency and
existing PS4-disabled branches. A private debug run caught the omitted normal
transform-table initialization, then another caught unused full-game global
destructors after successful asset draws. The final collector initializes the
game's tables, explicitly shuts down GPU/recorders/reports and exits without
running teardown for unbooted game systems. The initial crash's transient log
was not retained; the reproducing debugger runs and subsequent failed attempts
are retained privately. They are not passing collection evidence. No owner
progression, story replay or parent-issue modification was required.

## Standards

The independent review found no documented-standard violations and one optional
Data Clumps heuristic: the separate target-layout fields were populated,
validated and exported together. The collector now retains the renderer's
existing `RenderTargetLayout` value as one object. The final native build and
two fresh collections reproduce the same description/seed bytes after this
cleanup. No additional review agent was run for this small correction.

## Spec

The independent review found one P2 gap: synthetic tests invoked `prepare`
and packaging but omitted the explicitly approved collector-command/report
seam. The three command tests above address that gap. They also exposed an
array-shaped report traceback and accepted zero-draw report before the shared
draw-report validation was applied; both now fail with an actionable error.
The review found no scope creep or additional incorrectly implemented
requirements. Follow-up corrections were verified directly with focused tests
and actual repeated collection, without claiming an independent re-review.

Original review totals: Standards 1 optional heuristic, Spec 1 P2 gap.
Both findings were addressed; no known findings remain within either axis.
