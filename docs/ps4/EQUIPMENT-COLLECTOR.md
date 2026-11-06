# Bounded equipment/action collection (#152)

This maintainer workflow extends the [model collector](MODEL-COLLECTOR.md) and
[particle collector](PARTICLE-COLLECTOR.md). The fixed
[manifest plan](../../evidence/ps4/equipment-collector-152/manifest-plan.json)
contains three exercised recipes and nine unsupported families/states. It is
an independent slice of #136, starting from the corrected 301-description pilot
baseline in #149. It does not accumulate the separate #150/#151 expansions.
Game resources, complete descriptions, seeds, packages and captures stay private.

The native collector bypasses the game loop and owner storage. The production
program retains stock rendering quality, 1280x720, original 30 Hz logic,
synchronous missing-pipeline creation/recording and ordinary startup behavior.
No equipment acquisition, story progression or hidden gameplay warmup is needed.

## Fixed recipes and evidence boundary

`equipment-arrow-tips-v1` loads `Link.arc:bdlm/arrow.bdl` through the actual game
archive/J3D loaders. It uses the arrow actor's model flags `0x00080000` and
`0x11000022`, hides all three tip shapes and the ice tip's second material, then
selects **normal, fire, ice, normal**, one rendered frame per state. As in
`daArrow_c::createInit/setDrawShapeMaterial/_draw`, the selected tip material and
its optional next material are shown for the draw and hidden afterward. Each
state must perform real GX draws and configuration lookups. Opaque/translucent
J3D buffers and the selected renderer construct the descriptions normally.

This is a scripted selection cycle using real model draw state. It does not
execute the complete arrow actor, player controller or a live ammunition-type
transition. Player-owned BTK, randomized animation frames, elemental light/ice
actors, trails, flight, collision and the separate light-arrow model remain gaps.
The fixed view/lighting does not establish stage or attachment equivalence.

`equipment-bomb-normal-v1` independently reruns the four simultaneous resource
requests in `daBomb_c::eff_explode_normal`: flash, two smoke families and
fragments. `equipment-bomb-cheap-v1` follows `eff_explode_cheap`: flash, light
smoke, smoke02 and fragments. Before the first actual simulation tick, it sets
flash lifetime 12 and particle scale 0.5/0.67; smoke02 and fragments lifetime 70;
fragment away-from-axis speed 25 and directional speed 35. Both use the real
bomb-smoke callback and `setBombSmoke` user-work values through real emitter APIs.
They reproduce those setup branches, without executing the full bomb actor.

The bomb recipes retain the particle collector's two deterministic variations
(seed 0/1, scale 1/2, alpha 255/128), normal-P1 then toon-P1 group draws and
30-tick cap for continuous emitters. Every variation must emit, draw and retire
naturally by tick 240. The terminal empty tick and every observed configuration
are mapped. The process timeout is 180 seconds, with the existing 120-second
baseline-preparation bound. Overlap attribution belongs to the collective
four-effect recipe, not an individual emitter or a full scene.

The manifest names the excluded sword/shield, boomerang, hookshot/grapple,
leaf/hammer, bottle/bait/camera, arrow effects/animation, model-shard and
environment/cross-equipment families, with source references, reasons and
follow-up ownership. Reusing their resources does not exercise their controllers.
The three recipes are deliberately finite; this is not all-equipment coverage.

## Reproduce privately

Use the prepared Linux/WSL2 game/platform/host dependencies and `build` command
in [MODEL-COLLECTOR.md](MODEL-COLLECTOR.md). Build the current collector into a
new private directory. `PILOT_ASSETS` is the corrected 301-description #149
asset directory. All outputs below must be new and outside the repository.

```bash
for run in a b; do
  python3 tools/pswaker/collect-model-seed.py freeze-inventory \
    --plan evidence/ps4/equipment-collector-152/manifest-plan.json \
    --collector "$COLLECTOR" --image "$IMAGE" \
    --output "$PRIVATE_ROOT/equipment-manifest-$run.json"
  python3 tools/pswaker/collect-model-seed.py batch \
    --manifest "$PRIVATE_ROOT/equipment-manifest-$run.json" \
    --collector "$COLLECTOR" --image "$IMAGE" --baseline "$PILOT_ASSETS" \
    --output "$PRIVATE_ROOT/equipment-$run"
done
cmp "$PRIVATE_ROOT/equipment-manifest-a.json" "$PRIVATE_ROOT/equipment-manifest-b.json"
cmp "$PRIVATE_ROOT/equipment-a/prepared/assets/initial_pipeline_cache.db" \
    "$PRIVATE_ROOT/equipment-b/prepared/assets/initial_pipeline_cache.db"
cmp "$PRIVATE_ROOT/equipment-a/prepared/assets/pipeline-seed.json" \
    "$PRIVATE_ROOT/equipment-b/prepared/assets/pipeline-seed.json"
python3 tools/pswaker/complete-package.py assemble --kind game \
  --platform-root "$PLATFORM_ROOT" --program-stage "$PROGRAM_STAGE" \
  --elf "$PROGRAM_ELF" --app-version "$PROGRAM_VERSION" --image "$IMAGE" \
  --assembly-assets "$PRIVATE_ROOT/equipment-a/prepared/assets" \
  --output "$PRIVATE_ROOT/equipment-complete"
python3 tools/pswaker/complete-package.py inspect \
  "$PRIVATE_ROOT/equipment-complete" --platform-root "$PLATFORM_ROOT"
```

For individual collection, use `collect --scenario equipment-arrow-tips-v1
--resource /res/Object/Link.arc:bdlm/arrow.bdl` or the exact bomb recipe/resource
from the manifest. `prepare-batch --manifest ... --collections ... --baseline
... --output ...` revalidates retained collections without drawing them again.
Failed native attempts remain at their requested private output paths; no failed
batch publishes an accepted prepared seed. Existing outputs are refused.

Freeze binds the supported USA `GZLE01` revision-0 image, actual archive/model
or particle-bank identities, collector/build and host/PS4 contract to the fixed
plan. Preparation verifies the script, full state cycle/lifetime mappings,
source/resource identities and target contract. It rejects incompatible records
and same-identity/different-description conflicts. Complete description bytes,
type/version/size and identity establish sharing; first-use frame metadata does
not. Zero additions preserve the exact baseline seed and provenance bytes.

Retain each process's `collection.json`, observed and ordinary recorder snapshots,
per-scenario validated report and batch report. Compare the two runs' complete
observed assets/provenance and metadata except path-dependent command arguments:
scripts, state/variation/tick mappings, draw/lookup counts, target and resource/
collector identities must agree. Every baseline and collected full description
must be present unchanged in the combined seed. Fresh package inspection must
identify that exact seed and its full source manifest. The executed comparison
procedure is retained privately as `verify152.py` in artifact group `equipment-152`.

## Targeted physical handoff

Use only the identified [candidate](../../evidence/ps4/equipment-collector-152/candidate.json)
and matching ELF. This changed seed has no inherited physical acceptance.
The host BGRA layout differs from PS4 RGBA; the console prepares its own driver
objects. The equal contract witness and known-runtime byte controls do not prove
successful PS4 preparation or appearance of new states.

Follow the cache isolation, raw wait capture, database/WAL retrieval after closure,
and full-description comparison in [DYNAMIC-COLLECTOR.md](DYNAMIC-COLLECTOR.md).
Back up saves/settings first. Rename only the build-specific disposable runtime/
driver caches for the cold run; keep them for a separate warm run. Do not add
unrecorded gameplay warmup or alter saves/settings to acquire equipment.

Select from equipment already available in an ordinary backed-up save:

- First and repeated normal/fire/ice arrow draws and shots, returning to normal.
  Ice's extra translucent material and restoration of the normal tip are the
  highest-risk model states. Observe correct tip visibility, transparency,
  disappearance and trails; the latter remain outside automated generation.
- First/repeated normal bomb explosions, then simultaneous explosions and
  explosions overlapping ground smoke/debris. Watch flash, smoke fade, fragments,
  opacity, disappearance, audio and stalls. The cheap branch is a scripted source
  setup; no ordinary player action is assumed to select it reliably. A console
  observation needs an identified actor/location/context to claim that branch.
- The existing opening-Outset pot-break/dry-ground-roll route as a baseline
  regression control. It does not substitute for unavailable equipment evidence.

Allow roughly 5–10 minutes for available equipment samples plus the existing
15–25 minute regression route, preparation and transfers. Unavailable equipment
remains an explicit physical gap; do not require a full playthrough or a new
progression save. Record the exact selected actions and locations. Retain visible
preparation progress, successful preparation/cleanup before gameplay, full cold
versus final-drain timing, warm timing and resource observations. Keep raw creation/
wait events including sub-hitch waits, runtime descriptions, normal Quit outcome,
and before/after save/settings inventories. Require zero observed missing-pipeline
creation/waits and full-description membership against the exact bundled seed.
Failures remain evidence and require correction/revalidation. #149 feasibility
and #159 Quit diagnosis remain separate; this slice does not modify #136.
