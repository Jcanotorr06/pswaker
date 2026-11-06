# Bounded environment/scene collection (#154)

This maintainer workflow extends the [model collector](MODEL-COLLECTOR.md).
The [fixed plan](../../evidence/ps4/scene-collector-154/manifest-plan.json)
contains three recipes, fifteen frames in total, and nine unsupported families.
It starts independently from the corrected 301-description #149 pilot. It does
not accumulate the #150–#153 expansions or alter the #136 parent specification.
Game resources, full descriptions, seeds, packages and captures stay private.

## Real paths and finite boundary

`scene-ocean-world-v1` calls the real `daSea_packet_c::create/draw`. The game
initializes its 65×65 height table, ocean and distortion textures, indirect TEV
state, scrolling and perspective-linear sea fog. This recipe fixes a flat Y=1
grid spanning ±25600 with 800-unit cells. It does not call `execute`, which needs
stage/player/wave controllers. Its six single-frame states are day, night, dense
fog, range adjustment, raised camera, and day repeated.

`scene-simple-shadows-v1` calls `dDlst_shadowControl_c::setSimple/draw`, including
the game's front/back volume, optional texture seal, ground seal and clear display
lists. Its four frames exercise an untextured shadow, the stock `ball128b` texture,
a sloped receiver with raised camera/caster and elongated shadow, and the stock
texture repeated. The plane and caster are supplied directly, without collision.
Real model-caster capture and polygon receivers remain a separate gap.

`scene-alpha-overlap-v1` calls `dDlst_alphaModelPacket::draw` for a sphere, cube,
faded sphere, ocean+textured-shadow+faded-sphere sequence, and sphere repeated.
This is a selected packet sequence in one real renderer frame, not a reached
gameplay scene or a claim of full painter/controller ordering equivalence.

All recipes use the game's resource mount/setup and draw-list initialization.
They also run `pc::loadAssets` after opening the validated disc, before game
initialization, as the production native entry point does. That loader checks
the DOL/REL identities and fills the constant display lists and vertices; zero
stub arrays cannot establish scene coverage. Whole `Always` and `System` archive
hashes/lengths bind resource input, and the validated full-image identity binds
the DOL/REL-backed arrays. No extracted arrays enter the repository.

The [manifest](../../evidence/ps4/scene-collector-154/manifest.json) fixes exact
numeric world/camera/plane parameters, source references, assumptions and input
identities. Day/night colors, fog distances and transform/scroll values are
uniform/shared-state candidates; only matching complete observed descriptions
justify configuration equivalence. Texture presence, fog state and inherited
GX state may change descriptions. Every state must produce draws and lookups,
and every observed description must map to a state. Neither resource enumeration
nor a host setting alone counts as an exercised path.

## Layout and compatibility

The collector records both contracts used by the selected renderer's
`rebuild_pipeline_cache`: scene, and single-color/single-sample offscreen.
For stock rendering they have the same host key, `16288162637680331091`, with
one BGRA8 color attachment, Depth24Plus, one sample and 1280×720 dimensions.
That is justified contract equivalence; these recipes do not claim an offscreen
capture occurred. Additional capture/receiver paths are explicit unsupported rows.
State-to-description mappings retain the observed layout key, and validation
rejects missing, altered or incompatible contracts.

Portable configuration identity hashes complete description bytes and shader
type; compiled driver identity additionally includes the target layout. The PS4
uses RGBA8 and prepares its own driver objects, including applicable destination
alpha behavior. Matching host/PS4 representation witnesses, known-runtime hash
checks, ordinary-recorder byte controls and complete-description seed membership
support compatibility. They do not establish physical PS4 preparation or appearance.
No optional normals, MSAA, replacement textures or new target modes are enabled.

## Replay and inspect privately

Build with the [model collector instructions](MODEL-COLLECTOR.md) into a new
private directory using the selected prepared sources. `PILOT_ASSETS` is the
corrected #149 asset directory. Choose new output paths and retain failed runs.

```bash
for run in a b; do
  python3 tools/pswaker/collect-model-seed.py freeze-inventory \
    --plan evidence/ps4/scene-collector-154/manifest-plan.json \
    --collector "$COLLECTOR" --image "$IMAGE" \
    --output "$PRIVATE_ROOT/scene-manifest-$run.json"
  python3 tools/pswaker/collect-model-seed.py batch \
    --manifest "$PRIVATE_ROOT/scene-manifest-$run.json" \
    --collector "$COLLECTOR" --image "$IMAGE" --baseline "$PILOT_ASSETS" \
    --output "$PRIVATE_ROOT/scene-$run"
done
cmp "$PRIVATE_ROOT/scene-manifest-a.json" "$PRIVATE_ROOT/scene-manifest-b.json"
cmp "$PRIVATE_ROOT/scene-a/prepared/assets/initial_pipeline_cache.db" \
    "$PRIVATE_ROOT/scene-b/prepared/assets/initial_pipeline_cache.db"
cmp "$PRIVATE_ROOT/scene-a/prepared/assets/pipeline-seed.json" \
    "$PRIVATE_ROOT/scene-b/prepared/assets/pipeline-seed.json"
python3 tools/pswaker/complete-package.py assemble --kind game \
  --platform-root "$PLATFORM_ROOT" --program-stage "$PROGRAM_STAGE" \
  --elf "$PROGRAM_ELF" --app-version "$PROGRAM_VERSION" --image "$IMAGE" \
  --assembly-assets "$PRIVATE_ROOT/scene-a/prepared/assets" \
  --output "$PRIVATE_ROOT/scene-complete"
python3 tools/pswaker/complete-package.py inspect \
  "$PRIVATE_ROOT/scene-complete" --platform-root "$PLATFORM_ROOT"
```

For individual exercises, pass the exact scenario and resource pair from the
manifest to `collect`. `prepare-batch` revalidates retained collections. The seed
union preserves baseline records, frame metadata and source provenance, deduplicates
identical descriptions and rejects identity/description conflicts. Freeze, collect,
prepare and package inspection record exact identities; generated rows stay distinct
from physical evidence. The [evidence record](../../evidence/ps4/scene-collector-154/README.md)
identifies the actual candidate, repeat checks, controls and retained private inputs.

## Limits and selected physical handoff

Nine families remain follow-up automation gaps with source references and owners:
wave/storm controllers, real shadow capture/receivers, rectangular shadow textures,
mirrors/reflections, rain/snow/clouds, sky/underwater scenes, waterfall/dungeon water,
other alpha accumulators, and other world/camera/overlap combinations. They are
oversized for this slice; no owner waiver or coverage is inferred from shared assets.

The production program is unchanged: stock quality, 1280×720, original 30 Hz logic,
synchronous creation/recording, normal startup, and ordinary save/settings behavior.
The collector never boots the game loop or enters owner storage.

Physical work is a targeted #136 handoff, pending for this exact changed seed:

1. Use the identified private complete package and matching ELF. Back up ordinary
   saves/settings; select an existing save with the Outset shoreline and normal
   simple shadows available. No story progression or boss save is required.
2. With the application fully closed, archive then clear only build-specific
   disposable runtime/driver caches. Record empty-cache state and exact package,
   build and seed identities. Follow the [feasibility procedure](GENERATED-SEED-FEASIBILITY.md)
   for preparation progress/timing and memory observations, if available there.
3. Allow preparation and cleanup to finish before control. Record full preparation,
   final drain and visible launch-to-control separately. On the shoreline, observe
   water and simple shadows at first use and repeated use while moving/raising the
   camera. This selects indirect texturing, fog and projected shadow passes together.
4. Repeat the existing short Outset control/audio route and ordinary save/load
   checks. Observe normal Quit. Retrieve raw creation/wait events and runtime DB
   plus adjacent WAL only after Quit. Compare every returned complete description
   against the exact packaged seed, independently of the raw wait check.
5. Run a separate retained-compatible-cache launch. Record progress, preparation,
   memory, first/repeated rendering, Quit and preservation observations separately.

Allow roughly 15–20 minutes of active observation plus preparation and transfers;
no fixed startup ceiling is imposed. Night/dense-fog weather, alpha volumes, real
shadows, inaccessible stages and capture variants remain physical gaps unless an
ordinary save already reaches them. Do not wait for game time or progress the story
to fill this inventory. Select any available alpha-volume/light overlap as a high-risk
optional observation because its inherited GX state can differ from isolated draws.
Missing descriptions or observed missing-pipeline creation/waits require correction
and fresh candidate validation; a changed seed inherits no prior physical pass.
