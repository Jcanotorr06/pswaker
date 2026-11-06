# Bounded common-bank particle collection (#151)

This record accompanies [#151](https://github.com/Jcanotorr06/pswaker/issues/151),
part of #136. The [workflow](../../../docs/ps4/PARTICLE-COLLECTOR.md) describes
the fixed scripts, prerequisites, reproducible commands and physical handoff.
Actual resources, full descriptions, seeds, builds, packages and captures remain
private. Generated evidence is distinct from physical console observations.

## Fixed manifest

[manifest-plan.json](manifest-plan.json) selects ten available common-bank
effects and three simultaneous combinations: ground-smoke variants, bomb
flash/fragments/two smoke families/light smoke, death and ascension clouds, and
pot debris. The selected normal bomb combination mirrors the four resource
requests in `daBomb_c::eff_explode_normal`; other recipes isolate selected
resource/callback paths without executing the complete actor or scene.

Each recipe has two deterministic seed/scale/alpha variations; debris also
selects two textures. Real smoke emitter/particle callbacks build the TEV and
vertex state. Bomb smoke uses the actual timed fade callback and its selected
user-work values. Simulation and draws use the real JPA/GX renderer, including
normal-P1 then toon-P1 group transitions, synchronous creation and recording.
Actual particle emission, draw calls, lookups and terminal retirement are
required. The 30-tick cap applies only to continuous emitters; each variation
must drain naturally by tick 240, within the existing process timeout.

The manifest also exposes three missing source-enum effects and four
unsupported families. Source IDs `0x2005`–`0x2007` are absent from the supported
revision's common bank; their real creation attempts failed and are retained.
They were not relabeled as generated. The available ground-smoke pair
`0x2022`/`0x2027` is exercised separately. The common bank has 193 resource IDs;
the ten selected available IDs leave 183 outside this fixed generated boundary.
Scene banks, projection/framebuffer paths, model shards and cheap-bomb mutations
remain explicit follow-up work, with owners and assumptions in the plan.

## Generated configurations

[manifest.json](manifest.json) freezes the actual image/bank, collector/build,
recipe and target identities. [coverage.json](coverage.json) classifies all
20 rows: **13 generated/exercised, four unsupported, three missing**. It records
draws, ticks, peak particles, per-scenario configuration counts, description
hashes, every configuration's source mapping and explicit residual gaps.
Generated rows all retain `physical_verification: false`.

The union contains **113 distinct observed configurations**, five already in
the pilot baseline and **108 additions**, yielding **409 combined**. Every one
of the 301 baseline descriptions and its source provenance is preserved.
Deduplication compares identity, version, size and complete bytes; it ignores
first-use frame metadata. Uniform/texture changes and thousands of particle
draws are not equated with new pipeline configurations.

The two ground-smoke singleton controls each observe three configurations.
Their simultaneous overlap observes five, including **two complete descriptions
absent from the singleton union**. The normal four-component bomb overlap and
flash/ground-smoke overlap produce no descriptions beyond their singleton
controls in this fixed setup. The mapping retains those observations too;
absence of additions is not reported as expansion or as proof of all overlaps.
Overlap mappings identify the collective scenario, not the individual emitter
responsible for an inherited state. Equal complete description bytes justify
sharing a pipeline across these sources, not identical visual appearance.

## Repeat and package identities

Both fresh runs exercised all 13 recipes independently, with 301 baseline
identity/recorder controls per process. [repeat.json](repeat.json) records the
complete-byte comparison: the standalone seed **and its source manifest** agree
exactly, and each scenario's script, per-tick mappings/lifetime, draw/lookup
counts, resource/collector/contract identities and target layout agree. All 301
baseline descriptions retain identical complete bytes. Both manifest freezes
also reproduce exact bytes. The public report contains hashes and counts;
the actual complete descriptions remain in the private exports.

[candidate.json](candidate.json) identifies the unchanged **01.24** program,
build `35a453336a0e4b0d432c`, matching ELF, collector, source inventories, seed,
package, assembly and fresh inspection. Normal complete-package assembly
inspected the package before publishing its private output. Separate subsequent
inspection commands freshly extracted it again, agreed with one another, and
matched the assembly's complete pinned payload and exact seed/provenance.

- Seed: 409 descriptions, 1,708,032 bytes, SHA-256
  `539c836848da045c471f3ee43d988f19c2716207566c3a615410ef223832bb43`.
- Seed source manifest: SHA-256
  `6189ff7287f9548ba8acdb4af9f5dd0f4e1c9b0ca55e5020d40e543b9b5fd3fa`.
- Complete package: 1,521,614,848 bytes, SHA-256
  `1ad540305f75cd63135921dc249a2ba20efb6adf3c19b6597a993d1a4da16427`.
- Fresh inspection: SHA-256
  `663a68d943098201de40d2f075517f0dddaeea163955e49eae2c529783c98115`.

The private artifact group is `particle-151`: final `collector-d`, both
`manifest-d-*` freezes, `collections-d-a`/`collections-d-b`, `prepared-d-first`
and both `prepared-d-*` consolidations, `repeat-verification.json`,
`complete-01.24`, candidate records, commands, immutable-input inventories and
validation logs. `run-d.py` and `verify-final.py` retain the actual replay and
comparison/inspection procedure. Earlier builds/probes, the smoke crash attempts,
cancelled run and earlier seeds/packages/captures are retained. Image, baseline,
collector, plan/manifest, matching ELF/program and prepared seed inputs retain
their identities. The existing default assembly asset is not replaced; this
is an independent test package, not default delivery or release publication.

## Controls and evidence boundaries

The retained corrected pilot has 301 descriptions. This slice starts directly
from that baseline, independently of #150's 333-description model expansion.
Every baseline identity is recomputed by the selected seeded XXH3, and complete
baseline/observed description bytes are checked against the ordinary recorder.
Imported baseline records are not counted as particle draws.

The full host/PS4 contract witness remains 2,872 bytes, SHA-256
`8c3392d2bf28dae71adecc908ed8056d987a6b2db36bb27ddcf07cc138825700`.
Schema 1, clear v5/8-byte and GX v13/2772-byte descriptions, hash width,
representation, field offsets and complete default objects agree. This does
not prove all new states on PS4. The host BGRA surface differs from PS4 RGBA;
the target prepares layout-specific driver objects from descriptions. No host
driver objects are treated as portable shaders.

The ordinary verified 01.24 program/build and ELF are reused. The collector is
maintainer-only. Production quality, 1280x720, original 30 Hz logic, synchronous
missing-pipeline policy, startup and storage behavior are unchanged. No owner
save/settings or story progression is required. New candidate PS4 preparation,
appearance, raw waits, startup/scaling, Quit and preservation observations are
pending. Prior physical results do not transfer to a changed seed. #149's
remaining feasibility gaps and #159's Quit diagnosis remain separate.

## Failed attempts and correction

The first native build rejected particle arguments in the model-resource guard
before rendering. The corrected build retained those failures. Actual resource
probes then exposed the three unavailable source-enum IDs above.

The first ground-smoke singleton/overlap attempts crashed in the real follow
callback path. The isolated setup supplied a null position even though
`dPa_followEcallBack::execute` dereferences its retained position pointer. The
collector now gives that callback a fixed `cXyz` whose lifetime covers every
simulation tick. Both ground-smoke variants and their overlap scenarios then
completed with real draws and natural retirement. The real-resource CLI replay
is the regression check at this seam; synthetic public descriptions cannot
execute the game's follow callback and are not claimed as that regression.
The superseded partially completed run was cancelled with its attempts retained.

## Public verification

Synthetic fixtures test public particle preparation and the external collector
process boundary: deterministic manifest freezing, requested overlap arguments,
variation/tick mappings, shared-configuration deduplication, exact baseline
preservation, script/resource/target attribution and immutable inputs. Rejection
checks cover unsupported/oversized/duplicate requests, wrong scripts/bank/target,
unfinished lifetimes, missing mappings, no draws, incompatible records and
identity/description conflicts. Failed preparation never publishes a partial seed.

The real-tool synthetic particle batch-to-package test assembles the prepared
seed, separately extracts/inspects the package and checks exact seed bytes and
source provenance. Actual game rendering and private package evidence are
separate from these synthetic fixtures.

Final checks: full reference-enabled WSL suite **269 tests run, 101 environment/
platform skips, no failures**, 602.362 seconds. This includes the ten real
renderer startup checks and real packaging tools. Windows/UI and unselected
prepared-game integrations remain skipped; no console coverage is inferred.
The 25 collection tests, three particle tests and focused real-tool particle
package round trip pass. Pyright reports zero errors/warnings; Python compilation,
all eight maintained top-level shell syntax checks and Git whitespace checks
pass. The initial particle preparation and external-process manifest tests were
observed failing before implementation, then passed after their respective
changes. Review results are recorded separately in `REVIEW.md`.
