# Bounded menu, cutscene and mode collection (#155)

This maintainer workflow adds three finite narrow rendering setups to the
[model collector](MODEL-COLLECTOR.md). The fixed
[plan](../../evidence/ps4/presentation-collector-155/manifest-plan.json) records
stable IDs, source references, numeric setup inputs, bounds and shared-content
ownership. It starts independently from the corrected 301-description #149
baseline; it does not accumulate #150–#154 or modify #136. Resources, full
descriptions, seeds, complete packages and captures remain private.

## Exercised boundary

`menu-picture-colors-v1` mounts the native `clctres.arc` and loads
`heart_piece_base.bti` through the typed archive lookup. The isolated MEM mount
expands the individually compressed image with the game's `JKRDecomp` decoder;
the ordinary menu's ARAM archive performs that expansion during loading.
Real `J2DPicture` code
draws plain, black/white tinted, tinted with half alpha, then plain again. The
file selector's `menuColorChange` uses this black/white setup. The equivalent
manifest row covers only that setup with the selected native texture; it does
not establish equivalence for other textures, complete layouts or controllers.
Each frame uses a 640×480 orthographic port, a 64×64 picture at (100,100), and
the stock 1280×720 renderer target. The manifest fixes colors and alpha.

`cutscene-fade-v1` calls the actual `mDoGph_gInf_c::fadeOut/calcFade` overlay
path. Each frame resets the fade: half black, full black, half white, half black
again. This is the shared overlay used by transitions, not a cinematic player
or a claim to have reached any story event. Framebuffer blur, monochrome,
depth and spot effects remain separate gaps.

`mode-link-clothes-v1` loads the real `Link` model with the player's model/list
flags, locates the second `linktexS3TC` header as `playerInit` does, draws the
original hero texture, substitutes the paletted casual texture, then restores
the original header and refreshes its texture object. All three states draw.
This exercises the texture change associated with opening/alternate clothes,
without creating a player or changing clear-count/save data. Hat/buckle masking,
face/body ordering, skeletal animation, equipment and attachments remain gaps.

There are eleven frames total, one draw-state sample per frame. Every state
must produce real draws and pipeline lookups, and all observed complete
descriptions must map to states. Numeric uniform changes alone do not imply
new configurations. Identical descriptions justify deduplication; selecting a
mode or listing a cutscene never establishes coverage.

## Reproduce privately

Build into a fresh private collector directory using the prepared sources and
`build` command in [MODEL-COLLECTOR.md](MODEL-COLLECTOR.md). Use the currently
supported USA `GZLE01` revision-0 image and corrected #149 baseline assets.
All generated output directories must be new and outside the repository.

```bash
for run in a b; do
  python3 tools/pswaker/collect-model-seed.py freeze-inventory \
    --plan evidence/ps4/presentation-collector-155/manifest-plan.json \
    --collector "$COLLECTOR" --image "$IMAGE" \
    --output "$PRIVATE_ROOT/presentation-manifest-$run.json"
  python3 tools/pswaker/collect-model-seed.py batch \
    --manifest "$PRIVATE_ROOT/presentation-manifest-$run.json" \
    --collector "$COLLECTOR" --image "$IMAGE" --baseline "$PILOT_ASSETS" \
    --output "$PRIVATE_ROOT/presentation-$run"
done
cmp "$PRIVATE_ROOT/presentation-manifest-a.json" "$PRIVATE_ROOT/presentation-manifest-b.json"
cmp "$PRIVATE_ROOT/presentation-a/prepared/assets/initial_pipeline_cache.db" \
    "$PRIVATE_ROOT/presentation-b/prepared/assets/initial_pipeline_cache.db"
cmp "$PRIVATE_ROOT/presentation-a/prepared/assets/pipeline-seed.json" \
    "$PRIVATE_ROOT/presentation-b/prepared/assets/pipeline-seed.json"
python3 tools/pswaker/complete-package.py assemble --kind game \
  --platform-root "$PLATFORM_ROOT" --program-stage "$PROGRAM_STAGE" \
  --elf "$PROGRAM_ELF" --app-version "$PROGRAM_VERSION" --image "$IMAGE" \
  --assembly-assets "$PRIVATE_ROOT/presentation-a/prepared/assets" \
  --output "$PRIVATE_ROOT/presentation-complete"
python3 tools/pswaker/complete-package.py inspect \
  "$PRIVATE_ROOT/presentation-complete" --platform-root "$PLATFORM_ROOT"
```

`collect` accepts each exact scenario/resource pair in the manifest.
`prepare-batch` revalidates retained collections. Freeze binds the image,
whole source archives, collector/build and matching host/PS4 representation
contract. The menu and clothes setups additionally bind their menu/Link archives.
Preparation validates the fixed script, state order, full-description mappings,
scene/offscreen preparation layouts, resources and immutable input identities.
It rejects incompatible or conflicting descriptions before publishing a seed.
The combined seed preserves every baseline record and provenance source; a
zero-addition batch preserves the exact original seed/provenance bytes.

Retain collection metadata, observed and ordinary recorder snapshots, validated
reports, commands, package and fresh inspection. Compare repeat metadata except
path-dependent command arguments. Check every generated full description against
the combined seed and exact packaged bytes. Scene and offscreen layout witnesses
are recorded even when equal; recording a contract does not mean an offscreen
capture was exercised. Host BGRA and target RGBA require target driver preparation.

## Residual paths and bounded console handoff

The [evidence record](../../evidence/ps4/presentation-collector-155/README.md)
identifies the exact candidate and residual gaps. Shared actor/equipment content
belongs to #152/#153, and environment content to #154; no coverage transfers
merely because a resource is shared. Unsupported menu controllers, cloth/capture,
framebuffer effects, alternate visibility/dialogue and one-time ending/title
states remain visible follow-up work. No completion save or story replay is a
default prerequisite.

The player program is unchanged: stock quality, 1280×720, original 30 Hz logic,
synchronous runtime creation/recording, and normal saves/settings. The collector
never enters the game loop or owner storage. Generated evidence is distinct from
physical observations; this changed seed inherits no console pass.

Use only the identified package and matching ELF. Back up saves/settings, archive
the build-specific disposable caches, then follow
[generated-seed feasibility](GENERATED-SEED-FEASIBILITY.md) for cold/warm
preparation timing, final drain and resource observations. Select:

1. Native file selection and inventory open/close, selection tint and fading;
   observe first and repeated draws, text, colors, transparency and restoration.
   Other layouts remain outside automated coverage.
2. A normal reachable transition with a fade, retaining the existing opening
   Outset route as a regression control. Do not progress the story for a cutscene.
3. Hero/casual clothes only if already available in an ordinary backed-up save.
   Watch palette/appearance and restoration; unavailable alternate clothes and
   one-time states remain explicit physical gaps. Do not edit a completion save.

Allow roughly 15–25 minutes of active observation plus preparation/transfers.
Record exact build/package/seed identities, first/repeated behavior, full cold
versus warm progress/timing, raw missing-pipeline creation and wait events,
normal Quit, and before/after save/settings inventories. Retrieve the runtime
database and adjacent WAL after closure. Independently require full-description
membership in the exact packaged seed and zero observed missing creation/waits,
including sub-hitch waits. Retain failures; fix and revalidate a changed candidate.
