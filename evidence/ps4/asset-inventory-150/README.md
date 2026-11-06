# Bounded asset inventory and batch generation (#150)

Recorded 2026-11-06 for [#150](https://github.com/Jcanotorr06/pswaker/issues/150).
The owner explicitly instructed **“Proceed with asset expansion now”** after
being told that #149 still gates downstream expansion. This authorizes this
generation slice; it neither completes #149's remaining evidence nor changes #136.

## Fixed inventory and scope

[inventory-plan.json](inventory-plan.json) fixes the resource/family IDs, pinned
loader/use-site references, content/mode/state dimensions, assumptions and
separate dynamic-path ownership. [inventory.json](inventory.json) binds it to
the supported image, collector/build, complete target contract and exact archive
and expanded-model identities. Freezing the same plan twice reproduced the
complete manifest bytes. Use [the runnable workflow](../../../docs/ps4/ASSET-INVENTORY.md)
to reproduce the freeze, batch, preparation, assembly and fresh inspection.

The boundary is all **134 BDL/BMD resource members in 18 explicit archives**, plus
one justified alternate-mode stock-resource sharing row. It includes Outset,
Windfall and Forest Haven exteriors; Dragon Roost, Forbidden Woods, Tower of
the Gods, Earth/Wind Temples, Forsaken Fortress and Ganon's Tower rooms; Link's
house, the pirate ship and an optional cave; shared props, player equipment,
Rito/Bokoblin actor resources and title models. These are stock asset states,
not complete scenes, all dungeon rooms, enemy phases or alternate-mode gameplay.

The supported image has 1,282 object/stage archives. **1,264 archives are outside
this bounded inventory** and remain an explicit follow-up boundary. Merely
listing a resource establishes no pipeline coverage. Every in-boundary row has
a classification in [coverage.json](coverage.json):

| Classification | Rows | Meaning |
| --- | ---: | --- |
| Generated/exercised | 19 | Real isolated stock BDL draws, with recorder and baseline controls |
| Shared | 1 | Same Always pot archive/member bytes and fixed stock state, with explicit justification |
| Unsupported | 67 | BMD or nonstandard BDL loading/material setup lacks a validated recipe |
| Missing | 48 | Inventoried resource, not exercised within this bounded slice |

All generated/shared rows explicitly have `physical_verification: false`.
The alternate-mode row maps only the identical stock pot resource recipe:
the pot heap selects the resource by pot type, and the recipe is independent of
quest mode. It makes no alternate-mode runtime or reachability claim.
The complete row assumptions, source references, reasons and private evidence
references remain in the fixed manifest/report. `inventory_complete` is false.

## Generation and compatibility

The 18 new resource probes and retained small-pot control were consolidated
through `prepare-batch`. A separate `batch` invocation reruns every exercised
resource against the same immutable baseline and frozen manifest. Each model
uses the game archive/J3D loader, model update/view calculation, opaque and
translucent draw buffers, normal GX description construction, synchronous
pipeline creation and the normal recorder. Loading alone cannot pass.

The stock recipe is the proven `0x2020` BDL load, model flags `0`, differed
display-list flags `0x11000084`, three frames, fixed pilot view/projection,
1280x720, one sample and stock textures. It does not boot a stage or change
the production program, original 30 Hz logic, fallback policy or saves/settings.
Source references expose where actual actor/scene model flags, material setup,
animation, lighting and fog can differ from this stock recipe.

The first consolidated result contains **33 distinct collected configurations**:
one already in the baseline and **32 additions**, yielding **333 total**.
All 301 baseline/pilot/runtime-correction descriptions retain their complete
bytes and prior source provenance. Deduplication compares type/hash, version,
size and full description bytes; first-use frame metadata is excluded from
configuration identity. Every independently observed source survives in the
configuration mapping; no model/material/draw count is added to a pipeline count.

The collector recomputes every baseline identity with the selected XXH3 and
checks all observed and imported descriptions against the normal recorder.
The selected complete host/PS4 witness remains 2,872 bytes, SHA-256
`8c3392d2bf28dae71adecc908ed8056d987a6b2db36bb27ddcf07cc138825700`.
It establishes the version/representation/default-object contract; it does not
prove every generated state equivalent on PS4. The host BGRA surface differs
from PS4 RGBA; PS4 recreates descriptions with its own required target layouts.
No host compiled driver objects are packaged as portable descriptions.

## Candidate and private artifacts

The candidate uses the unchanged, verified **01.24** production program and
matching ELF, build `35a453336a0e4b0d432c`. The expanded standalone seed has
333 descriptions, 1,396,736 bytes, SHA-256
`e3559efe1e2920ef3880e73f9ae387ae856256dc71ba1c4aabe9e3004c46428a`.
The seed's complete source-manifest identity is
`4783c97a24747b93381d14ce54b2562d315806e5384daa746b13bac77f73c985`.
Normal complete-package assembly and a separate fresh inspection bind the
exact packaged seed; the final package/build/ELF/inspection identities are
retained in `candidate.json` alongside the generation records.

The complete package is **1,521,287,168 bytes**, SHA-256
`9c4bf9271bccc43396ba2d0e2e567daf3dfdc5e985c2690f0accbd41ec78adea`.
Separate fresh inspection reproduces the assembly inspection, SHA-256
`8ecacba4ff050990ce767e544984db3877e0e0a2cfaad8c2b2bfd97c1d12f922`.
The matching ELF remains
`c2d48776ed9f79d90ec71d61cc0732a3b2b673da361ca57d7c4a10596a2392fc`.

The private artifact group is `asset-inventory-150`: `collector-a`, all probe
collections/logs, both frozen manifests, `first-collections`, `first-prepared`,
the independent `batch-repeat`, final full-description comparison,
`complete-01.24`, input-preservation inventories and validation logs. Earlier
controls and plans remain retained. Actual resources, description databases,
packages, saves, logs and captures are private. The previous default assembly
asset and earlier candidates were not replaced; default delivery remains #156.

## Residual gaps and next observations

The largest inventoried families are player equipment (54 resources), common
props (31) and Rito actors (17). Their remaining stock resources and distinct
loading/material recipes need separate bounded follow-up. Bokoblin and title
families remain entirely unsupported here. Other rooms, assets, unused/debug
variants and the 1,264 unlisted archives have no coverage claim from this slice.
No actor callback, animation or scene-controller rewrite was introduced.

Particles belong to #151, equipment/action mutations to #152, enemy/boss phases
to #153, environment/scene variations to #154, and menus/cutscenes/alternate-mode
runtime state to #155. Material tables/animations and simultaneous effects are
not covered by enumerating or drawing these stock models.

The [bounded console selection](../../../docs/ps4/Asset-inventory-checklist.md)
uses accessible Outset/house/pot regression controls and optional already-owned
equipment/save contexts. It requires no story progression or newly acquired
save. New PS4 preparation/layout evidence, appearance, raw missing-pipeline
creation/waits, full-description membership, startup/resource viability and
save/settings preservation remain unobserved for this expanded seed. #149's
existing layout/profile/timing gaps remain visible; earlier 301-description
physical results do not transfer to the changed 333-description candidate.
Physical validation/acceptance remains with #157; this record does not close #150
or treat missing/unsupported inventory rows as accepted coverage.

## Public verification

Tests use synthetic disc/archive resources and descriptions. Public CLI tests
cover repeatable manifest freezing, actual requested resource attribution,
external-process batch execution, source sharing and full-description
deduplication. Preparation tests cover deterministic complete seed/report bytes,
all four classifications, invalid manifests/sharing, unsupported loader/state
requests, malformed/no-draw/missing exports, incompatible records, cross-resource
conflicts, target/resource attribution, immutable inputs and existing outputs.
The real-tool synthetic batch-to-package test assembles a complete package and
independently extracts/inspects its exact seed and provenance.

The first batch and freeze tests failed because the public commands did not
exist, then passed with implementation. The selected native collector builds
against the prepared sources and both actual compiler contracts. Pyright reports
zero errors/warnings; Python compilation and shell syntax checks pass. The full
reference-enabled WSL suite ran **264 tests, 60 platform/environment skips, no
failures**, in 635.643 seconds, including all ten initialized-renderer startup
checks and the real-tool batch package inspection. Subsequent focused checks
cover the final malformed-resource/state cases. These checks do not supply new
PS4 physical evidence.
