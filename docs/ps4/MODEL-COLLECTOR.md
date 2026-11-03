# Bounded model/material collector (#147)

This maintainer-only Linux/WSL2 workflow exercises one stock material without
booting a stage, acquiring equipment, loading a save, or changing player settings.
Actual images, descriptions, builds, logs and complete packages remain private.
The public fixtures contain synthetic bytes only.

## Fixed scenario

`always-small-pot-stock-v1` mounts `/res/Object/Always.arc` with `JKRArchive`,
loads `bdl/obm_kotubo1.bdl` through
`J3DModelLoaderDataBase::loadBinaryDisplayList(..., 0x2020)`, and creates it with
`mDoExt_J3DModel__create(..., 0, 0x11000084)`. It exercises the single material's
display list and shape through `J3DModel::update`, `viewCalc`, and the opaque and
translucent `J3DDrawBuffer::draw` paths. It records three fixed model frames.
Merely mounting or loading the file cannot produce a successful collection.

The view is identity translated -200 on Z; projection is 45 degrees, 4:3,
near 1 and far 10000, over the game's 640x480 GX viewport/scissor.
`J3DSys::drawInit` establishes the ordinary J3D draw state; the model supplies
its own material state after `GXInit`, RGB8/Z24 setup and NTSC VI configuration.
No actor environment-lighting, fog, destruction,
carrying, animation or particles are claimed. Numeric camera/light uniforms
do not by themselves enumerate distinct pipeline configurations.

The supported image is USA `GZLE01`, revision 0, checked by the existing full
image validator. Use the selected prepared PS4 game source, its source-built
host Dawn/SDL dependencies, Vulkan, one sample, stock texture adapter, synchronous
pipelines, and the 1280x720 internal target (`VISetFrameBufferScale(1.5)`).
The collector bypasses the game logic loop; the program's original 30 Hz logic
and production startup are unchanged. Optional desktop 60 Hz/FIFO extensions
compile through their existing PS4-disabled branches.

Source references in the pinned SwitchWaker/decomp tree:

- `game/src/d/d_resorce.cpp`: archive/resource loading flags.
- `game/src/m_Do/m_Do_ext.cpp`: model creation and differed display lists.
- `game/src/m_Do/m_Do_machine.cpp`: heap/transform-table initialization.
- `game/src/JSystem/J3DGraphAnimator/J3DModel.cpp`: calculation and draw entry.
- `game/src/JSystem/J3DGraphBase/J3DPacket.cpp`: material and shape draws.
- Selected Aurora `lib/gx` and `lib/dolphin/gx`: actual GX description construction.
- Selected Aurora `lib/gfx/pipeline_cache.cpp`: identity, synchronous creation,
  recording, and target-layout preparation.

## Build and collect privately

Use new output directories. `GAME_ROOT` is an already prepared and target-built
game root with `evidence/game-inputs.json` and `build/compile_commands.json`.
`PLATFORM_ROOT` and `HOST_ROOT` are the matching source-built platform and
host-renderer dependency roots described in the retained build records.
All build/dependency roots must be on the Linux filesystem without spaces.

```bash
python3 tools/pswaker/collect-model-seed.py build \
  --game-root "$GAME_ROOT" --platform-root "$PLATFORM_ROOT" \
  --host-root "$HOST_ROOT" --build-directory "$BUILD_ROOT/model-collector" \
  --output "$PRIVATE_ROOT/model-collector-build"
python3 tools/pswaker/collect-model-seed.py collect \
  --collector "$PRIVATE_ROOT/model-collector-build" --image "$IMAGE" \
  --baseline "$BASELINE_ASSETS" --output "$PRIVATE_ROOT/model-collection-a"
python3 tools/pswaker/collect-model-seed.py collect \
  --collector "$PRIVATE_ROOT/model-collector-build" --image "$IMAGE" \
  --baseline "$BASELINE_ASSETS" --output "$PRIVATE_ROOT/model-collection-b"
python3 tools/pswaker/collect-model-seed.py prepare \
  --collection "$PRIVATE_ROOT/model-collection-a" --baseline "$BASELINE_ASSETS" \
  --output "$PRIVATE_ROOT/model-seed-a"
python3 tools/pswaker/collect-model-seed.py prepare \
  --collection "$PRIVATE_ROOT/model-collection-b" --baseline "$BASELINE_ASSETS" \
  --output "$PRIVATE_ROOT/model-seed-b"
cmp "$PRIVATE_ROOT/model-seed-a/assets/initial_pipeline_cache.db" \
    "$PRIVATE_ROOT/model-seed-b/assets/initial_pipeline_cache.db"
```

The build verifies the prepared source inventories, records source/build/compiler
and dependency identities, and compiles `model-contract.cpp` with both actual
compiler command lines. The complete named section must match: schema/config
versions, hash width, field offsets, and complete default description objects.
This is an ABI witness, supplemented by actual full-description comparisons;
it does not prove all host/PS4 rendering states equivalent.

The collector wraps only GX `find_pipeline`, delegates to the normal renderer,
and records the actual complete description and its normal seeded XXH3 identity.
The observation database contains only the fixed model's draws. The preloaded
baseline never counts as collected. Export also checks every observation against
the normal renderer's closed recorder database, using public standalone seed
preparation. All known baseline identities are recomputed with the host's
selected XXH3 implementation and all baseline description bytes must survive
the normal recorder's round trip unchanged. These imported control records
are counted separately from actual model observations. The report binds the
collector/build, image/resource identities,
settings, commands, layout and observation asset to a stable scenario.

`prepare` validates both standalone assets using the package validator, compares
`(type, hash)` and all description bytes, and ignores only first-use frame
metadata for configuration identity. It rejects any incompatible record or
same-identity/different-description conflict. Baseline bytes survive unchanged
when no additions are needed; otherwise compatible additions retain baseline
records and both original provenance inventories. Its `collection-report.json`
records per-configuration attribution, full-description hashes and covered/new
counts. Generated provenance remains `asset-material-draw`, never gameplay.
Source inventories are compared before and after; existing outputs are refused.
Failed collector attempts are retained at their requested private output path.

## Assemble and independently inspect

Reuse the matching verified PS4 program and ELF; the collector is never packaged
as the player executable. Keep the report next to the private package handoff.

```bash
python3 tools/pswaker/complete-package.py assemble --kind game \
  --platform-root "$PLATFORM_ROOT" --program-stage "$PROGRAM_STAGE" \
  --elf "$PROGRAM_ELF" --app-version "$PROGRAM_VERSION" --image "$IMAGE" \
  --assembly-assets "$PRIVATE_ROOT/model-seed-a/assets" \
  --output "$PRIVATE_ROOT/model-pilot-complete"
python3 tools/pswaker/complete-package.py inspect \
  "$PRIVATE_ROOT/model-pilot-complete" --platform-root "$PLATFORM_ROOT"
```

Retain program/build/ELF, package, standalone seed, asset manifest, assembly and
fresh inspection hashes. Inspection must identify the exact collected/combined
seed bytes extracted from the complete package. Counts and packaging are not PS4
preparation or physical gameplay evidence.

## Runnable handoff to the dynamic pilot (#148)

Start with this verified collector build command and the validated prepared
asset directory as the next baseline. Preserve both source collections and the
original runtime baseline. Add a separate finite scenario in the collector for
one game/effect state transition; keep this fixed pot scenario reproducible.
Use the actual effect constructor/update/draw path and explain its initial state,
variation and completion condition. A second draw of this unchanged pot does
not qualify as dynamic evidence.

A concrete follow-up candidate is the pot-break effect in
`game/src/d/actor/d_a_tsubo.cpp`, `Act_c::eff_break_tsubo`, which requests
`dPa_name::ID_AK_JN_M_TUBOHAHEN` and `ID_AK_JN_TUBOKONAGONA` through
`dComIfGp_particle_set`. The #148 implementation must establish the effect's
real resource-manager prerequisites and exercise its update/draw lifetime;
these particles were not exercised by the static pilot.

Run the same `build`, `collect`, `prepare`, `assemble`, and `inspect` sequence
with new private directories, after extending the scenario/report validation
and the agreed tests. Compare every available common identity to compatible
runtime description bytes, and expose unmatched descriptions and unhandled
states. Recheck layout/schema/hash compatibility when rendering paths change.

The next pilot must supply its own bounded cold/warm PS4 instructions and exact
candidate identities. Preserve saves/settings; normal Quit precedes database/WAL
retrieval. No story completion or full-game save acquisition is a prerequisite.
Host compilation, ABI agreement, matching known descriptions and host rendering
leave PS4 driver creation, early scaling/resources, and physical effect appearance
for the targeted checks under #138/#148. No full-game coverage is established.
