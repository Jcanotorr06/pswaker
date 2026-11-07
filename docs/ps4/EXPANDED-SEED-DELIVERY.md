# Expanded default seed delivery (#156)

This workflow consolidates the six independent #150–#155 expansions and their
final reruns with the compatible corrected #149 baseline. It delivers a private
seed through required assembly assets and the Windows desktop bundle. The
[frozen evidence record](../../evidence/ps4/seed-delivery-156/README.md) identifies
the actual candidate, output changes, coverage and unresolved gaps. The
[rendering matrix](../../evidence/ps4/seed-delivery-156/rendering-matrix.json)
and full archive audit bound the claim. Generated evidence is separate from
physical observations. Neither default delivery nor host preparation establishes
full-game or physical acceptance. No release is published by this workflow.

## Consolidation and reproducibility

Use the supported USA GZLE01 revision-0 image, stock textures, synchronous
rendering, 1280×720, one sample and the selected PS4 renderer. Freeze the native
collector/build, actual PS4 representation witness, source and input identities.
Run each fixed plan using `freeze-inventory` and `batch` as documented in
[asset inventory](ASSET-INVENTORY.md), [particles](PARTICLE-COLLECTOR.md),
[equipment](EQUIPMENT-COLLECTOR.md), [actors](ENEMY-COLLECTOR.md),
[scenes](SCENE-COLLECTOR.md) and [presentation](PRESENTATION-COLLECTOR.md).
Retain earlier manifests and collection directories unchanged. Rerunning with a
later collector can change descriptions; an old expansion is not discarded
merely because a new run fails to reproduce it.

Write a private UTF-8 JSON plan with schema 1, `baseline_sha256` (the validated
baseline database), `baseline_manifest_sha256` (its provenance manifest),
`image_sha256`, `contract_sha256`, and a nonempty `sources`
array. Each source has a unique lowercase kebab-case `id`, a `manifest` path,
its exact `manifest_sha256`, and a `collections` directory. Paths resolve relative
to the plan; absolute private paths also work. Include retained and fresh runs as
separate sources. Different collector builds may coexist only under the same
image and renderer contract, with every manifest/collection independently valid.
The reserved source ID `baseline` cannot be used for a generated source.

```bash
python3 tools/pswaker/collect-model-seed.py consolidate \
  --plan "$PRIVATE_ROOT/consolidation-plan.json" \
  --baseline "$CORRECTED_BASELINE" --output "$PRIVATE_ROOT/frozen"
python3 tools/pswaker/collect-model-seed.py consolidate \
  --plan "$PRIVATE_ROOT/consolidation-plan.json" \
  --baseline "$CORRECTED_BASELINE" --output "$PRIVATE_ROOT/repeat"
```

Each source is revalidated through `prepare-batch`, including actual draws,
finite scripts, full description/state mappings, collector/build/input identities,
shared-configuration justifications and exclusions. The final union compares
type/hash, version, size and complete description bytes. Same-identity conflicts,
changed manifests, wrong targets and invalid seeds fail without publishing an
output. Existing/nested outputs are refused. Source inventories are checked
before and after validation, and the baseline's original records and frame
metadata survive. Identical records are deduplicated. Source-specific first-use
frames remain evidence metadata and do not create different configurations.

`assets/` contains only the standalone database and `pipeline-seed.json`.
`consolidation-report.json` preserves each complete source report and manifest,
all source mappings, method/state attribution and explicit gaps. `validated/`
retains the individual validation reports. A duplicate-only source still appears
in both provenance and mappings; no-addition consolidation preserves the exact
database but can change the provenance manifest. The baseline is retained as
baseline evidence, not relabeled as generated or physically observed content.
`inventory_complete` describes only the supplied manifest rows; consult source
exclusions and the full rendering/archive audits before making any broader claim.

Compare the complete output inventories from repeat consolidation. Independently
compare all retained and final observation assets with the exact extracted seed,
using the public comparator documented in
[generated-seed feasibility](GENERATED-SEED-FEASIBILITY.md). File hashes/counts
alone cannot establish membership. Record changes versus each earlier expansion,
including descriptions not reproduced, and keep those compatible descriptions.
Retain commands, tool/source hashes, native process logs, manifests and all failed
attempts privately. Public fixtures and reports must contain no description bytes,
game resources, captures, credentials or personal paths.

## Default assets and private desktop bundle

After verification, preserve the previous private platform `assembly-assets`
directory and replace it with the validated `frozen/assets` pair. Normal Linux
assembly then selects it without `--assembly-assets` or extra owner selection.
Derive a verified data-free program release from the matching program/ELF. Build
the private Windows bundle with `build-desktop.py --assembly-assets` pointing to
that exact pair, following [BUILDING.md](../../BUILDING.md). The seed remains
outside the data-free program release. Owners select only their disc image and
output location; the required bundled asset is automatic.

Run the frozen executable's `--check-installation`, validate the bundle and asset
inventories, create a package through its normal Windows assembly adapter and
freshly inspect it again. Independently extract that package and compare every
retained/final observation's full description against its seed. Retain separate
identities for any Linux control package; it is not the Windows candidate merely
because the program and seed agree. The candidate record binds program version,
build/cache ID, ELF/SELF, package, seed/asset manifest, program/desktop release and
fresh inspection. Invalid required assets stop assembly instead of producing an
unseeded game.

## Bounded final console selection

Use only the canonical private desktop-built package in the
[candidate record](../../evidence/ps4/seed-delivery-156/candidate.json), its
matching ELF, and PS4 Slim / firmware 9.00 / GoldHEN v2.4b18. The old 01.26
package/seed and earlier expansion packages are separate candidates even when
the program version and build ID agree. The current handoff changes seed bytes;
earlier preparation, appearance, waits or shutdown results do not transfer.

Allow about **25–40 minutes of active observation total across cold and warm
runs**, plus installation, preparation and transfers. Multi-minute cold
preparation is allowed; there is no arbitrary startup ceiling. Use existing
backed-up ordinary saves. Do not obtain completion/progression saves, replay the
story or wait for weather to reach an inaccessible selection. Record unavailable
selected observations by scenario, missing evidence and risk; they remain gaps.

| Selection | First use and repeat | Rationale / prerequisites |
| --- | --- | --- |
| Opening Outset controls, roll, sword, grass and pot breaks | Move/turn/roll, swing into grass, view and break two pots; retain identifiable timings | Static/dynamic regression and known missed runtime descriptions; an ordinary Outset save is sufficient |
| Shoreline, swim/ripples and simple shadows | Enter/exit water twice, turn and raise the camera while viewing the shore and shadow | Indirect water, alpha, camera and projected-shadow interactions; reachable from ordinary Outset |
| Native file selection/inventory and transition fade | Open/close twice, change selection, observe a normal reachable fade | Picture tint/alpha and transition setup regressions; no cinematic replay |
| Bomb explosion and bow shots | First and repeated explosion/shot, observing smoke, overlap, alpha and retirement | Equipment/particle overlap; only if already available in an ordinary save |
| Enemy hit/death, ice freeze/thaw and visible alpha overlap | First/repeated available enemy interaction; freeze/thaw only if ice arrows are already available, plus an already reachable overlapping light/alpha effect | Ice material replacement/depth packets and inherited GX-state risk; do not progress to obtain a boss, item or effect |
| Hero/casual clothes or alternate mode | Observe already available clothes and menus without editing save flags | Palette/texture regression; unavailable alternate states remain selected physical gaps |

The native collectors exercise scene and offscreen preparation contracts; their
host keys can be equal. PS4 RGBA versus host BGRA and destination-alpha variants
remain target-driver work. Retain preparation/layout evidence for every applicable
PS4 layout. An aggregate ready count cannot certify an unlogged layout or an
unreached offscreen gameplay path. Do not invent a rendering observation for an
inaccessible selected scenario.

1. With the application fully closed, back up `/data/pswaker/saves/` and
   `/data/pswaker/settings.ini`, including recovery files, and inventory them
   by private relative path, size and SHA-256. Record the ordinary card/slot,
   starting landmark and unavailable selections; retain absent-file observations.
   Archive and rename only `/data/pswaker/cache/be0a6ae04878271c6c1d/` outside the
   active path. This removes both build-specific runtime and driver caches from
   initialization. Installation or replacing the seed does not establish empty
   caches. Preserve image-check state, other build caches and ordinary storage.
   Record the candidate package/seed identity; the cold log must show
   `files-before-init=0`. Do not perform extra unrecorded warmup.
2. Film launch to first control with an external timer. Record responsive progress,
   surfaced errors, full preparation/cleanup and final drain separately. Require
   all compatible seed records and applicable layouts ready, pending zero,
   complete true, zero preparation errors and `known-shaders-prepared` before
   gameplay. A drained queue with failed creation is a failure. Do not add
   overlapping preparation/content-validation durations.
3. Mark visible gameplay ready in the existing port menu. Record each selected
   first/repeat action and visible rendering, controls and audio. Keep the normal
   two-minute Outset measurement and three additional minutes of movement as the
   regression control; identify later selection intervals separately. Collect
   startup and subsequent sampled resource observations, allocation failures or
   growth. Sampled counters are not total memory or guaranteed transient peaks.
4. Choose **Quit game...** normally and record actual closure and any CE error.
   An `EXIT code=0` message alone does not establish clean closure. After the
   application is fully closed, retrieve the entire performance directory
   (`identity.json`, events/frames/samples and extras), matching `platform.log`,
   `platform.prev.log`, `last-stage.txt`, crash artifacts if present, and the
   whole build-specific cache including database/WAL/SHM and driver files.
   Preserve their structure in a new private cold folder before another launch
   rotates logs. Do not copy a live SQLite database.
5. Relaunch the exact candidate with compatible caches retained. Repeat the same
   available selection and normal Quit, retrieving into a separate warm folder.
   Record preparation/progress, resources and launch-to-control independently;
   warm still creates runtime objects. Compare save/settings inventories with
   backups and explain all changes. Do not delete saves to invalidate caches.

Maintainers archive/hash originals first, freshly reinspect the candidate and
snapshot database/WAL pairs through `complete-package.py pipeline-seed`. Compare
**every** returned type/hash and complete description bytes against the extracted
frozen seed. Independently inspect whole-launch raw missing-pipeline creation and
`shader-wait-ns` events, including below-threshold waits and cumulative frame
counters. Require zero observed missing creation/waits. Neither average FPS nor
seed membership substitutes for that check. Unexpected runtime creation remains
synchronous, renderable and recorded; treat its discovery as a coverage defect.

Missing/conflicting descriptions or observed missing waits require a corrected
collector/seed/package, applicable automated reruns and affected physical checks
with documented regression selection. They cannot be waived. Important unresolved
generation or selected-observation gaps require resolution or explicit owner
acceptance recording scenario/path, missing evidence, risk and decision. The
current audit does not record such acceptance or certify complete inventory
coverage. Preserve #136 and keep final acceptance open.

## Later releases

Review shader/renderer/schema/hash, target/layout, compiler/ABI, asset revision,
recipe and seed changes before carrying claims forward. Rebuild and compare the
complete native host/PS4 witness with actual compiler flags, rerun relevant fixed
manifests, preserve prior compatible descriptions/provenance and compare full
bytes. Update archive/matrix gaps and source/output identities. Produce a new
private seed and default bundle, assemble and freshly extract/inspect the exact
candidate, and repeat affected targeted console checks. Document the basis for
any unchanged evidence carried forward; a new package or seed never silently
inherits another candidate's physical acceptance.
