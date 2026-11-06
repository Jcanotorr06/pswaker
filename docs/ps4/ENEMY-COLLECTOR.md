# Bounded enemy/boss collection (#153)

This maintainer workflow extends the [model collector](MODEL-COLLECTOR.md) and
[particle collector](PARTICLE-COLLECTOR.md). The fixed
[manifest plan](../../evidence/ps4/enemy-collector-153/manifest-plan.json)
contains eight exercised recipes and fifteen unsupported families. It is an
independent slice of #136, starting from the corrected 301-description pilot
baseline in #149. It does not accumulate the separate #150/#151/#152 expansions.
Game resources, complete descriptions, seeds, packages and captures stay private.

The native collector bypasses the game loop and owner storage. The production
program retains stock rendering quality, 1280x720, original 30 Hz logic,
synchronous missing-pipeline creation/recording and ordinary startup behavior.
No combat agent, encounter AI, story progression, completed save or hidden
gameplay warmup is needed.

## What runs, and what is reproduced

Actor recipes enter real game code rather than loading a model alone:

- **Resources.** `dRes_control_c::setRes` queues the normal mount command. The DVD
  thread never starts, so the collector services one `mainLoop` pass itself, then
  `syncRes` runs the unmodified `dRes_info_c::loadResource`. Per-type material
  handling, `J3DMaterialAnm` setup and `setToonTex` therefore come from the game,
  using the `System` toon images and `Always` freeze material it would use.
- **Models and animation.** `mDoExt_McaMorf`, `mDoExt_J3DModel__create` and the
  BRK/BTK wrappers run with each actor's flags on a solid heap, as under
  `fopAcM_entrySolidHeap`.
- **Material state.** Freezing is the shared `dMat_control_c::iceEntryDL/iceUpdateDL`
  material copy, backup and restore. `mDoExt_invisibleModel` supplies the real
  depth-only packets. Material tables use `setMaterialTable`/`entryDL(table)`.
- **Draw lists.** `dDlst_list_c` sorts and draws the entries in painter order.

Each state draws one frame after `dComIfGd_reset`. Every state must perform real
GX draws and configuration lookups, or the process fails.

The actor processes themselves do not run. Each recipe reproduces the narrow
state selection of the named draw function: which branch, material table,
animation binding or list. Those are documented equivalent setups, not encounter
states reached through AI. Skeletal animation, actor lighting (`setLightTevColorType`),
fog, shadows, screen blur and other cameras are excluded from every actor recipe,
and the fixed view does not establish stage or attachment equivalence.

## Fixed recipes and evidence boundary

| Recipe | States | Real path |
| --- | --- | --- |
| `enemy-bokoblin-materials-v1` | stock, green with shield, pink with telescope, frozen, restored, four swing blurs | `daBk_Draw`, `br_draw`, blur tables, shared freeze |
| `enemy-chuchu-states-v1` | body, two stone overlays, puddle, breakup, frozen | `daCC_Draw` BMD/BDL branches, BRK/BTK, `iceUpdateDL` with invisible packets |
| `enemy-peahat-freeze-v1` | stock, frozen, restored | `daPH_Draw` body/propeller freeze with invisible packets |
| `boss-jalhalla-visibility-v1` | default, stun, curse start/end, light-freeze, possession, lantern | `body_draw`, `torituki_draw`, `kantera_draw`, mask-off list |
| `boss-gohma-defeat-v1` | phase one, phase two, defeat | `daBtd_Draw`, DEADA table and rebinding |
| `boss-puppet-ganon-water-v1` | surface, mask, combined | `water0_disp`/`water1_disp` blend and depth mutation |
| `enemy-death-large-v1` | 0x14+0x13+0x15+0x16 lifecycle | `set_disappear` default branch, stripes callback |
| `enemy-death-small-v1` | 0x43c+0x43d+0x43e lifecycle | `set_disappear` 0x4 branch |

The two death recipes retain the particle collector's deterministic variations
(seed 0/1, scale 1/2, alpha 255/128), 30-tick cap for continuous emitters and
natural retirement by tick 240, drawn in the normal group `setNormal` uses.
Attribution belongs to the collective effect, not an individual emitter.

Each state mirrors its draw function's model, table and list choices. The swing
blur shows only the `BLURA` or `BLURB` shape, as `br_draw` does; it swaps tables on
one shared model between states, where a spawned actor keeps the table chosen at
creation. The Bokoblin passes no invisible packets when frozen, because `daBk_Draw`
passes none, while the Chuchu and Peahat pass theirs.

Some selected states may add nothing. A state's value is that it was exercised,
and an equal description set is reported rather than hidden. Equal descriptions
justify pipeline sharing for those observed states only. They do not imply
identical visuals or coverage of any other actor using the same model.

The manifest names excluded Bokoblin eye/blink passes, the Seahat variant,
Jalhalla's alpha spheres, Moblin/Darknut equipment, Poe/Floormaster/Wizzrobe, other
ordinary enemies, line materials, hit/fire/ice effects, Kalle Demos, Gohdan, Molgera,
Phantom Ganon/Ganondorf, Gohma debris, Puppet Ganon's other phases and environment
combinations, with source references, reasons and follow-up ownership. Sharing the
freeze path does not prove those actors. This is not all-enemy coverage.

## Reproduce privately

Use the prepared Linux/WSL2 game/platform/host dependencies and `build` command
in [MODEL-COLLECTOR.md](MODEL-COLLECTOR.md). Build the current collector into a
new private directory. `PILOT_ASSETS` is the corrected 301-description #149
asset directory. All outputs below must be new and outside the repository.

```bash
for run in a b; do
  python3 tools/pswaker/collect-model-seed.py freeze-inventory \
    --plan evidence/ps4/enemy-collector-153/manifest-plan.json \
    --collector "$COLLECTOR" --image "$IMAGE" \
    --output "$PRIVATE_ROOT/enemy-manifest-$run.json"
  python3 tools/pswaker/collect-model-seed.py batch \
    --manifest "$PRIVATE_ROOT/enemy-manifest-$run.json" \
    --collector "$COLLECTOR" --image "$IMAGE" --baseline "$PILOT_ASSETS" \
    --output "$PRIVATE_ROOT/enemy-$run"
done
cmp "$PRIVATE_ROOT/enemy-manifest-a.json" "$PRIVATE_ROOT/enemy-manifest-b.json"
cmp "$PRIVATE_ROOT/enemy-a/prepared/assets/initial_pipeline_cache.db" \
    "$PRIVATE_ROOT/enemy-b/prepared/assets/initial_pipeline_cache.db"
cmp "$PRIVATE_ROOT/enemy-a/prepared/assets/pipeline-seed.json" \
    "$PRIVATE_ROOT/enemy-b/prepared/assets/pipeline-seed.json"
python3 tools/pswaker/complete-package.py assemble --kind game \
  --platform-root "$PLATFORM_ROOT" --program-stage "$PROGRAM_STAGE" \
  --elf "$PROGRAM_ELF" --app-version "$PROGRAM_VERSION" --image "$IMAGE" \
  --assembly-assets "$PRIVATE_ROOT/enemy-a/prepared/assets" \
  --output "$PRIVATE_ROOT/enemy-complete"
python3 tools/pswaker/complete-package.py inspect \
  "$PRIVATE_ROOT/enemy-complete" --platform-root "$PLATFORM_ROOT"
```

For an individual recipe, use `collect --scenario <recipe> --resource <resource>`
with the exact pair from the manifest. `prepare-batch --manifest ... --collections
... --baseline ... --output ...` revalidates retained collections without drawing
them again. Failed native attempts remain at their requested private output paths;
no failed batch publishes an accepted prepared seed. Existing outputs are refused.

Freeze binds the supported USA `GZLE01` revision-0 image, collector/build and
host/PS4 contract to the fixed plan. Each actor row binds its archive, primary
model and every companion member it consumes, including the shared `Always` freeze
material and `System` toon images; effect rows bind the particle bank. Preparation
verifies the script, full state/lifetime mappings, source/resource identities and
target contract. It rejects incompatible records and same-identity/different-
description conflicts. Complete description bytes, type/version/size and identity
establish sharing; first-use frame metadata does not. Zero additions preserve the
exact baseline seed and provenance bytes.

Retain each process's `collection.json`, observed and ordinary recorder snapshots,
per-scenario validated report and batch report. Compare the two runs' complete
observed assets/provenance and metadata except path-dependent command arguments:
scripts, state/variation/tick mappings, draw/lookup counts, target and resource/
collector identities must agree. Every baseline and collected full description
must be present unchanged in the combined seed. Fresh package inspection must
identify that exact seed and its full source manifest. The executed comparison
procedure is retained privately as `verify153.py` in artifact group `enemy-153`,
which also reruns the #152 recipes as a control on the changed collector.

## Targeted physical handoff

Use only the identified [candidate](../../evidence/ps4/enemy-collector-153/candidate.json)
and matching ELF. This changed seed has no inherited physical acceptance.
The host BGRA layout differs from PS4 RGBA; the console prepares its own driver
objects. The equal contract witness and known-runtime byte controls do not prove
successful PS4 preparation or appearance of new states.

Follow the cache isolation, raw wait capture, database/WAL retrieval after closure,
and full-description comparison in [DYNAMIC-COLLECTOR.md](DYNAMIC-COLLECTOR.md).
Back up saves/settings first. Rename only the build-specific disposable runtime/
driver caches for the cold run; keep them for a separate warm run. Do not add
unrecorded gameplay warmup or alter saves/settings to reach an encounter.

Owner story progression and completed-encounter saves are not prerequisites.
Select from what an ordinary backed-up save already reaches:

- First and repeated Bokoblin kills in the Outset forest. `set_disappear` selects
  its branch from the drop type, so a kill cannot be assumed to reach a particular
  recipe; record what appears. Watch flash, smoke, spirit stripes, disappearance
  and stalls.
- First and repeated Chuchu kills where one is reachable, including a puddle
  transition; a Chuchu covered in stone only if the save reaches one.
- First ice-arrow freeze of any enemy, then a repeat and thaw, only where ice arrows
  are already available. This is the highest-risk shared state: it replaces every
  material and, on Chuchus, Peahats and similar actors, adds depth-only packets.
- The existing opening-Outset pot-break/dry-ground-roll route as a baseline
  regression control. It does not substitute for unavailable encounter evidence.

Boss recipes have no required console step. Jalhalla, Gohma and Puppet Ganon stay
explicit physical gaps unless a backed-up save is already at that encounter; do
not require a new progression save. A console observation claims a state only with
its actor, location and context identified.

Allow roughly 5–10 minutes for available enemy samples plus the existing 15–25
minute regression route, preparation and transfers. Record the exact selected
actions and locations. Retain visible preparation progress, successful preparation/
cleanup before gameplay, full cold versus final-drain timing, warm timing and
resource observations. Keep raw creation/wait events including sub-hitch waits,
runtime descriptions, normal Quit outcome, and before/after save/settings
inventories. Require zero observed missing-pipeline creation/waits and
full-description membership against the exact bundled seed. Failures remain
evidence and require correction/revalidation. #149 feasibility and #159 Quit
diagnosis remain separate; this slice does not modify #136.
