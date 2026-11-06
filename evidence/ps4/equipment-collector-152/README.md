# Equipment/action collection (#152)

This record accompanies [#152](https://github.com/Jcanotorr06/pswaker/issues/152),
part of #136. The [workflow](../../../docs/ps4/EQUIPMENT-COLLECTOR.md) provides
replay commands, setup boundaries and the targeted physical handoff. Resources,
full descriptions, seeds, packages and captures remain private. These are
generated observations, not physical console results.

## Fixed generated boundary

[manifest-plan.json](manifest-plan.json) fixes three recipes and nine unsupported
families/states. [manifest.json](manifest.json) freezes actual image/resource,
collector/build and contract identities. The arrow recipe loads the real
`Link.arc:bdlm/arrow.bdl`, applies the actor's model flags and exercises the
normal/fire/ice/normal tip-shape selection through real J3D/GX draws. Normal and
cheap bomb recipes run the four-component effect overlaps through real JPA
simulation, bomb-smoke callbacks and GX draws. The cheap recipe applies the
source branch's lifetime, particle-scale and velocity mutations before ticking.
These isolated setups do not execute the complete player/arrow/bomb actors.

[coverage.json](coverage.json) records all source mappings and exclusions:
**three generated/exercised rows, nine unsupported rows**, none physically
verified. Every private per-scenario report retains complete descriptions and
the exact state/variation/tick mappings. No unsupported controller is inferred
from a shared model or effect bank.

The arrow cycle performs nine actual draws/lookups over four frames. Normal and
fire each observe the same complete description; ice observes that description
plus a second one. Returning to normal reproduces the first state. Both are new
relative to the corrected 301-description pilot baseline. BTK, elemental actors,
flight, trails and light-arrow rendering remain explicit gaps.

The normal bomb recipe performs 44,640 draws and 1,241 lookups over 308 ticks
across its two variations; each naturally retires at tick 154. It observes 107
configurations, one baseline-covered and 106 additions. All its description
bytes match the independently retained #151 normal-bomb overlap. That control
is rerun here against the pilot baseline, not imported as newly drawn evidence.

The cheap recipe performs 20,106 draws and 690 lookups over 194 ticks, retiring
at ticks 98/96. Its 35 complete descriptions are a subset of the normal recipe.
The changed real setup/lifetimes were exercised, but add no unique configuration
to that union. Equal descriptions justify pipeline sharing for these observed
states; they do not imply identical visuals or all-equipment coverage.

## Seed, repeat and package

The union contains 109 observed configurations: one baseline-covered and **108
additions**, producing **409 combined descriptions**. All 301 pilot descriptions
and their source provenance survive unchanged. This independent candidate is
not the separate #151 candidate, despite their equal row counts.

[repeat.json](repeat.json) records exact standalone seed/provenance and frozen
manifest equality across two fresh runs. Every scenario's observed seed/source
manifest, script, states/lifetimes, counts, resource/collector identities and
target agree. Each process recomputes all 301 known-runtime identities and
checks complete baseline and observed bytes against the ordinary recorder.
Imported controls are never counted as equipment draws. Every generated full
description is present unchanged in the combined seed.

[candidate.json](candidate.json) identifies the unchanged verified **01.24**
program, build `35a453336a0e4b0d432c`, matching ELF, collector, inputs, seed,
assembly and independently repeated package inspection:

- Seed SHA-256: `9c99d6c7cf9dd573fe75f88601390f06b8773e01a5cb63eb4fc27922a81cbf86`.
- Complete package SHA-256:
  `69a1873e3a9659e0331db80226386da5022d0b78f415c48175b7cd6d7e859c86`.
- Fresh inspection SHA-256:
  `b4af3d8f19648a1dc2ecc203ac2c938163c8a93a4abc84b932ca728771206ffd`.

Ordinary complete-package assembly inspected the output before publication.
The subsequent independent inspection freshly extracted it, reproduced the
assembly inspection and matched the full pinned payload, exact seed bytes and
source manifest. Image, baseline, frozen manifest/plan, collector/build, matching
ELF/program and prepared asset identities remain unchanged. Default assembly
assets are not replaced; this is an identified private test complete package.

Private artifact group `equipment-152` retains `collector-a`, both frozen
manifests, `batch-a`/`batch-b`, `complete-01.24`, package/input preservation
records, commands, collection/build logs and validation logs. `run152.py`,
`verify152.py` and `package152.py` retain the executed replay/comparison procedure.

## Compatibility, limitations and handoff

The complete host/PS4 contract witness remains 2,872 bytes, SHA-256
`8c3392d2bf28dae71adecc908ed8056d987a6b2db36bb27ddcf07cc138825700`:
schema 1, clear v5/8 bytes, GX v13/2772 bytes, hash width, representation,
field offsets and default objects agree. Actual baseline/recorder byte controls
supplement that witness. Host BGRA versus PS4 RGBA still requires target-specific
driver-object preparation; no host driver binary is used as a portable shader.

The collector changes no production startup, rendering quality, 1280x720 target,
30 Hz logic, synchronous runtime policy or owner storage. New PS4 preparation,
appearance, wait, startup/resource, Quit and preservation observations remain
pending. Prior physical acceptance does not transfer to a changed seed.

The manifest explicitly leaves arrow effects/BTK/light arrows, sword/shield,
boomerang trails, hookshot/grapple, leaf/hammer, bottle/bait/camera, model shards,
stage lighting/wind/water and cross-equipment combinations for follow-up. These
are unsupported automation states, not owner-accepted gaps. The workflow selects
high-risk first/repeated ice-tip and explosion/overlap observations using only
already available equipment, with the ordinary Outset route as a regression
control. No normal acquisition or full story playthrough is required.

Public synthetic fixtures cover mixed model/effect batches, exact state/source
mapping, deduplication, baseline and input preservation, repeatability, atomic
rejection of bad scripts/identities/mappings/lifetimes/conflicts/incompatibility,
the external collector-process boundary, and actual package-tool assembly/fresh
inspection. Actual rendering evidence above is separate from those fixtures.
Independent reviews are recorded in [REVIEW.md](REVIEW.md), with final automated
checks in [FINAL-VERIFICATION.md](FINAL-VERIFICATION.md).
