# Enemy/boss collection (#153)

This record accompanies [#153](https://github.com/Jcanotorr06/pswaker/issues/153),
part of #136. The [workflow](../../../docs/ps4/ENEMY-COLLECTOR.md) provides replay
commands, setup boundaries and the targeted physical handoff. Resources, full
descriptions, seeds, packages and captures remain private. These are generated
observations, not physical console results.

## Fixed generated boundary

[manifest-plan.json](manifest-plan.json) fixes eight recipes and thirteen
unsupported families. [manifest.json](manifest.json) freezes actual image/resource,
collector/build and contract identities, including every companion member each
actor consumes. Actor recipes run the game's resource loading, material, freeze,
invisible-packet and draw-list code; effect recipes run real JPA simulation and GX
draws. The actor processes, AI, skeletal animation, actor lighting, fog, shadows
and blur do not run. Each recipe reproduces the state selection of the named draw
function, so these are documented narrow setups, not reached encounter states.

[coverage.json](coverage.json) records all source mappings and exclusions:
**eight generated/exercised rows, thirteen unsupported rows**, none physically
verified. Every private per-scenario report retains complete descriptions and the
exact state/variation/tick mappings.

## Generated coverage

| Recipe | Frames | Draws | Lookups | Descriptions | New vs pilot |
| --- | ---: | ---: | ---: | ---: | ---: |
| `enemy-bokoblin-materials-v1` | 7 | 74 | 19 | 5 | 5 |
| `enemy-chuchu-states-v1` | 5 | 11 | 11 | 6 | 6 |
| `enemy-peahat-freeze-v1` | 3 | 16 | 12 | 7 | 7 |
| `boss-jalhalla-visibility-v1` | 6 | 224 | 19 | 8 | 8 |
| `boss-gohma-defeat-v1` | 3 | 60 | 17 | 9 | 9 |
| `boss-puppet-ganon-water-v1` | 3 | 4 | 4 | 2 | 2 |
| `enemy-death-large-v1` | 224 | 11,336 | 802 | 4 | 3 |
| `enemy-death-small-v1` | 104 | 1,044 | 333 | 4 | 3 |

The union contains 40 observed configurations: one baseline-covered and **39
additions**, producing **340 combined descriptions**. Five descriptions are shared
across recipes: four by the two death effects and one by Jalhalla and the Peahat.
All 301 pilot descriptions and their source provenance survive unchanged. This
independent candidate does not contain the separate #150, #151 or #152 expansions;
three of its additions also appear in the independent #152 seed.

Freezing changes descriptions. The Peahat's frozen state observes five descriptions
against two for stock, including the depth-only invisible packets, and restoration
returns to the stock set. The Bokoblin's frozen state also differs from stock.

Several exercised states add nothing, which is reported rather than hidden.
Green/pink Bokoblins swap textures only and keep the stock set; club and sword
share one description; Chuchu's second stone overlay shares the first's set;
Jalhalla's curse and light-freeze states share the default set. Register and
texture changes do not select a new description here, and list placement alone
does not either. Equal descriptions justify pipeline sharing for these observed
states only. They do not imply identical visuals or cover other actors.

## Seed, repeat and package

[repeat.json](repeat.json) records exact standalone seed/provenance and frozen
manifest equality across two fresh runs. Every scenario's observed seed/source
manifest, script, states/lifetimes, counts, resource/collector identities and
target agree. Each process recomputes all 301 known-runtime identities and checks
complete baseline and observed bytes against the ordinary recorder. Every generated
full description is present unchanged in the combined seed.

The changed collector reran `equipment-arrow-tips-v1`, `equipment-bomb-normal-v1`
and `equipment-bomb-cheap-v1` as a control. Their 2, 107 and 35 complete descriptions
equal the retained #152 collections, so the shared particle and state-reporting
changes did not alter those recipes.

[candidate.json](candidate.json) identifies the unchanged verified **01.24**
program, build `35a453336a0e4b0d432c`, matching ELF, collector, inputs, seed,
assembly and independently repeated package inspection:

- Seed SHA-256: `912b99b13dbb1a5a077968f3d9ba2df32cd35a436c3441b81bccf19f17915056`.
- Complete package SHA-256:
  `abed3433b58c87179bf3516151ecfd9adcdcdaefaee64716fc09d7a9ff69aab5`.
- Fresh inspection SHA-256:
  `f82d2dcd2415985c695b540c5ad28e2b6281863c455aff66bd3b40964fedb192`.

Ordinary complete-package assembly inspected the output before publication. The
subsequent independent inspection freshly extracted it, reproduced the assembly
inspection and matched the full pinned payload, exact seed bytes and source
manifest. Image, baseline, frozen manifest/plan, collector/build, matching ELF/program
and prepared asset identities remain unchanged. Default assembly assets are not
replaced; this is an identified private test complete package.

Private artifact group `enemy-153` retains `collector-a`, both frozen manifests,
`batch-a`/`batch-b`, `controls`, `complete-01.24`, package/input preservation records,
commands, collection/build logs and validation logs. `run153.py`, `verify153.py` and
`package153.py` retain the executed replay/comparison procedure.

## Compatibility, limitations and handoff

The complete host/PS4 contract witness remains 2,872 bytes, SHA-256
`8c3392d2bf28dae71adecc908ed8056d987a6b2db36bb27ddcf07cc138825700`. Actual
baseline/recorder byte controls supplement that witness. Host BGRA versus PS4 RGBA
still requires target-specific driver-object preparation; no host driver binary is
used as a portable shader.

The collector changes no production startup, rendering quality, 1280x720 target,
30 Hz logic, synchronous runtime policy or owner storage. New PS4 preparation,
appearance, wait, startup/resource, Quit and preservation observations remain
pending. Prior physical acceptance does not transfer to a changed seed.

The thirteen unsupported families are automation gaps, not owner-accepted gaps:
Bokoblin eye/blink passes, Moblin/Darknut equipment, Poe/Floormaster/Wizzrobe,
other ordinary enemies, line materials, hit/fire/ice effects, Kalle Demos, Gohdan,
Molgera, Phantom Ganon/Ganondorf, Gohma debris and head, Puppet Ganon's other phases,
and environment combinations. Actor lighting, skeletal animation and shadows also
remain outside every exercised recipe, so a real encounter may reach descriptions
this seed does not contain. The workflow selects first/repeated kill and freeze
observations reachable from an ordinary save, with the Outset route as a regression
control. No story progression, completed-encounter save or full playthrough is
required, and the boss recipes stay physical gaps unless a save is already there.

Public synthetic fixtures cover mixed actor/effect batches, exact state/source
mapping, deduplication, baseline and input preservation, repeatability, atomic
rejection of bad scripts/identities/companions/mappings/lifetimes/conflicts/
incompatibility, the external collector-process boundary, and actual package-tool
assembly/fresh inspection. Actual rendering evidence above is separate from those
fixtures.
