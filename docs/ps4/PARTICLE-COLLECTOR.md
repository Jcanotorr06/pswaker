# Bounded particle collection (#151)

This maintainer workflow extends the [dynamic pilot](DYNAMIC-COLLECTOR.md).
It loads actual JPA resources and runs emitter construction, original particle
ticks, dynamic callbacks, GX draws and natural retirement. It never starts the
game loop or accesses owner saves/settings. The installed program retains stock
quality, 1280x720, original 30 Hz logic and synchronous creation/recording.
Images, resources, description bytes, complete packages and captures stay private.

## Fixed boundary

The [manifest plan](../../evidence/ps4/particle-collector-151/manifest-plan.json)
fixes stable scenario/family IDs, exact effect combinations, source references,
assumptions and explicit gaps. `freeze-inventory` binds it to the supported USA
GZLE01 revision-0 image, common bank, collector/build and host/PS4 contract.
`batch` executes only `exercise` rows; unsupported and missing rows survive in
the final report. No filename inventory is counted as rendered coverage.

The native recipe is `particle-effect-lifecycle-v1`. Its resource argument is
`/res/Particle/common.jpc:0xNNNN`, with up to four unique supported IDs joined
by `+`. The registry deliberately excludes scene banks, projection and model
particles. Adding a new family requires a validated recipe and a new manifest.

Each process starts with empty 3000-particle/150-emitter/200-field pools and runs
two sequential variations: random seed 0/1, global scale 1/2, alpha 255/128,
and debris texture index 0/1. Every variation resets the emitter RNG. Position
is the origin; the pilot view/projection and single-sample target are retained.
Other resource colors remain stock. Uniform/texture changes need not change
the pipeline description.

The normal-P1 and toon-P1 groups are calculated and drawn in that order, with
`J3DSys::reinitGX` at each group boundary. Within a group, the real manager
determines emitter draw order. Bomb smoke uses the actual
`dPa_bombSmokeEcallBack` and `setBombSmoke` user-work values. Ground smoke uses
the actual smoke emitter/particle TEV and vertex callbacks, wind disabled,
max-frame 1, rate 3 and spread 0.05 from `setSimpleLand`. Lighting uses the
isolated process's fixed stage defaults; no outdoor/indoor lighting equivalence
is claimed. The full actor, collision query and scene controller are excluded.

Continuous emitters receive a 30-tick emission window at construction. Ordinary
finite emitters keep their stock lifetime. Every variation must emit particles,
draw, perform configuration lookups and retire to zero particles/emitters by
tick 240. The terminal empty tick is retained. Each process also has a 180-second
timeout, and baseline preparation has its existing 120-second bound. A failed
recipe retains its attempt and cannot contribute an accepted seed.

## Reproduce privately

Use the Linux/WSL2 prerequisites and `build` invocation from
[MODEL-COLLECTOR.md](MODEL-COLLECTOR.md). All output paths must be new and outside
the repository. Use the corrected 301-description pilot baseline identified by
the particle evidence record, independently of #150's material expansion.

```bash
python3 tools/pswaker/collect-model-seed.py freeze-inventory \
  --plan evidence/ps4/particle-collector-151/manifest-plan.json \
  --collector "$COLLECTOR" --image "$IMAGE" \
  --output "$PRIVATE_ROOT/particle-manifest.json"
for run in a b; do
  python3 tools/pswaker/collect-model-seed.py batch \
    --manifest "$PRIVATE_ROOT/particle-manifest.json" \
    --collector "$COLLECTOR" --image "$IMAGE" --baseline "$PILOT/assets" \
    --output "$PRIVATE_ROOT/particle-$run"
done
cmp "$PRIVATE_ROOT/particle-a/prepared/assets/initial_pipeline_cache.db" \
    "$PRIVATE_ROOT/particle-b/prepared/assets/initial_pipeline_cache.db"
cmp "$PRIVATE_ROOT/particle-a/prepared/assets/pipeline-seed.json" \
    "$PRIVATE_ROOT/particle-b/prepared/assets/pipeline-seed.json"
python3 tools/pswaker/complete-package.py assemble --kind game \
  --platform-root "$PLATFORM_ROOT" --program-stage "$PROGRAM_STAGE" \
  --elf "$PROGRAM_ELF" --app-version "$PROGRAM_VERSION" --image "$IMAGE" \
  --assembly-assets "$PRIVATE_ROOT/particle-a/prepared/assets" \
  --output "$PRIVATE_ROOT/particle-complete"
python3 tools/pswaker/complete-package.py inspect \
  "$PRIVATE_ROOT/particle-complete" --platform-root "$PLATFORM_ROOT"
```

For individual recipes use `collect --scenario particle-effect-lifecycle-v1
--resource /res/Particle/common.jpc:0x000b`, with the same collector/image/baseline
arguments. `prepare-batch --manifest ... --collections ... --baseline ...
--output ...` consolidates retained successful individual runs.

Collection recomputes every baseline identity and checks complete observed and
baseline description bytes against the ordinary recorder. Preparation rejects
incompatible records, identity/byte conflicts, incomplete lifetime mappings,
wrong scripts and mismatched bank/image/collector/target identities. It preserves
every compatible baseline row and source provenance; zero additions preserve
the exact baseline seed and manifest bytes. Inputs and earlier outputs remain
immutable. Repeat comparisons include full description bytes, script/lifetime
and per-variation mappings, not just counts.

Each batch configuration lists all observed scenario sources, including overlaps.
Per-source validated reports retain the exact variations and ticks that observed
it. Equal type/hash/version/size/full-description bytes justify shared pipeline
configurations; effects, particles, draws and shaders are separate counts.
Overlap observations are collective scenario mappings, not causal attribution
to an individual emitter. Compare each overlap's complete descriptions against
its singleton controls to identify combinations that actually change state.

## Physical handoff and remaining risks

Use only the exact package/ELF/seed identities in the
[particle evidence record](../../evidence/ps4/particle-collector-151/README.md).
This changed seed has no inherited physical acceptance. Host BGRA versus PS4
RGBA layouts remain distinct; the console prepares its own driver objects.
Contract matching and known-runtime byte controls do not prove new PS4 states.

The bounded first check is the existing opening-Outset pot route: back up
saves/settings, retain/rename the exact build cache for a cold run, then perform
the same first/repeated pot breaks and dry-ground rolls in a two-minute sample.
Repeat warm with caches retained. Follow the retrieval and raw shader-wait/full
description comparison instructions in [DYNAMIC-COLLECTOR.md](DYNAMIC-COLLECTOR.md).
Allow the existing 15–25 minute route plus actual preparation/transfer time.

High-risk additional checks are first/repeated normal bomb explosions, several
simultaneous explosions, explosions overlapping smoke/debris, and ground-smoke
variants. Use only already available equipment/save contexts; unavailable
scenarios remain gaps and require no story progression or completed-save
acquisition. Record their exact locations/actions separately. Observe opacity,
toon lighting, flash/fragments, disappearance, stalls and audio. Do not equate
the isolated setup with the full actor effect.

Retain visible startup/preparation progress, raw creation/wait events including
sub-hitch waits, full runtime database/WAL pairs after closure, timing/capture
records, normal Quit outcome and before/after save/settings inventories. Compare
every runtime description against the exact bundled seed and preserve failures.
Scene banks, cheap-bomb mutations, model shards, framebuffer projection, stage
lighting/wind and cross-slice interactions remain with the named owners in the
manifest and final tests. #149's outstanding feasibility evidence and #159's
Quit diagnosis remain separate; this slice does not change #136 or claim
full-game coverage.
