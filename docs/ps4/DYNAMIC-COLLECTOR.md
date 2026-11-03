# Bounded dynamic-effect collector (#148)

This maintainer-only extension to the [model collector](MODEL-COLLECTOR.md)
exercises one real particle lifetime without stage loading, equipment acquisition,
story progression, or access to owner saves/settings. The collector is a separate
host executable. The installed player program, original 30 Hz logic, stock
rendering quality, 1280x720 target, synchronous pipeline creation/recording and
storage behavior remain unchanged. Actual images, resource bytes, descriptions,
captures and complete packages stay private.

## Fixed scenario and source path

`common-pot-debris-lifecycle-v1` loads `/res/Particle/common.jpc` through
`JKRDvdToMainRam`, constructs `JPAResourceManager` and the ordinary
`JPAEmitterManager` pools (3000 particles, 150 emitters, 200 fields), and requests
`dPa_name::ID_AK_JN_TUBOKONAGONA` (`0x0018`) using
`JPAEmitterManager::createSimpleEmitterID`. This is the sprite-debris component
requested by `daTsubo::Act_c::eff_break_tsubo` through `dPa_control_c::set`.
The harness mirrors that setter's selected inputs; it does not invoke the actor's
whole break routine or claim to collect the companion model-shard effect.

The initial manager has no live emitters/particles. Each of two sequential
variations resets `JPABaseEmitter::emtrInfo.mRandom` to zero, creates one emitter
at `(0,0,0)`, sets unit scale, opaque white primary/environment colors and alpha,
and installs the game's `dPa_selectTexEcallBack` for texture index 0 or 1.
`JPAEmitterManager::calc(0)` advances one original particle tick per frame;
`draw` runs the real emitter/draw-manager/particle GX path, including the callback's
texture selection. No 60 Hz interpolation, owner preferences or game loop runs.
The script runs as fast as the host permits; tick count is simulation time,
not a measured console duration.

Each tick uses the static collector's fixed view (identity, Z=-200), projection
(45 degrees, 4:3, near 1, far 10000) and 640x480 GX viewport/scissor, scaled to
1280x720. `J3DSys::drawInit` and `reinitGX` establish state before particle draw;
the effect supplies its actual particle render state. Stage environment lighting
and the controller's `dKy_setLight_again` are deliberately outside this isolated
unlit particle exercise. The selected effect's complete description is compared
to a compatible actual PS4 capture below; this does not generalize to lit effects.

Completion requires actual particles and draws, followed by natural retirement
to zero particles and emitters. Each variation fails after 180 ticks if unfinished;
the process also has the existing 180-second command timeout. The terminal empty
tick is retained. The ordinary recorder is closed before exporting. Observation
starts after baseline preparation, so imported seed entries are never counted as
dynamic draws.

Source references in the build-identified prepared game tree:

- `game/src/d/actor/d_a_tsubo.cpp`, `Act_c::eff_break_tsubo`: caller and effect ID.
- `game/src/d/d_particle.cpp`, `dPa_control_c::set` and
  `dPa_selectTexEcallBack::draw`: selected setup and texture callback.
- `game/src/JSystem/JKernel/JKRDvdRipper.cpp`: real disc-resource loader.
- `game/src/JSystem/JParticle/JPAResourceManager.cpp` and
  `JPAEmitterManager.cpp`: resource loading, creation, calculation and retirement.
- `game/src/JSystem/JParticle/JPAEmitter.cpp`, `JPADraw.cpp` and `JPADrawVisitor.cpp`:
  particle lifetime and dynamic draw state.
- Selected Aurora `lib/gx` and `lib/gfx/pipeline_cache.cpp`: full description
  construction, identity, synchronous creation, recording and layout handling.

`collection.json` fixes the script, source resource, per-tick particle/emitter
counts, draws, lookups and configuration identities, plus explicit unhandled
states. `collection-report.json` maps each full-description identity/SHA-256 to
its texture variations and ticks. The exact complete bytes are in the standalone
observation database, never in public evidence. The two texture selections can
share one pipeline; neither changing uniforms/textures nor advancing a lifetime
implies a new configuration.

Unhandled states are the model-shard component `0x0017`, actor lighting and
collision, other pot textures, overlapping effects and other cameras. Stage
particles, water, shadows, other effects and full-game coverage are also outside
this bounded pilot. A real pot break on console includes additional paths.

## Reproduce and package privately

Use the supported USA `GZLE01` revision-0 image and the same prepared PS4 game,
platform and source-built host dependencies as the static pilot. The `build`
command compiles the complete contract witness under both actual host and PS4
flags; mismatched bytes fail. It records source inventories, compiler/dependencies
and executable identities. See [MODEL-COLLECTOR.md](MODEL-COLLECTOR.md) for setup.
Every output path below must be new and outside the repository.

```bash
python3 tools/pswaker/collect-model-seed.py build \
  --game-root "$GAME_ROOT" --platform-root "$PLATFORM_ROOT" \
  --host-root "$HOST_ROOT" --build-directory "$BUILD_ROOT/dynamic-collector" \
  --output "$PRIVATE_ROOT/dynamic-build"
for run in a b; do
  python3 tools/pswaker/collect-model-seed.py collect \
    --collector "$PRIVATE_ROOT/dynamic-build" --image "$IMAGE" \
    --scenario common-pot-debris-lifecycle-v1 \
    --baseline "$STATIC_SEED/assets" --output "$PRIVATE_ROOT/dynamic-$run"
  python3 tools/pswaker/collect-model-seed.py prepare \
    --collection "$PRIVATE_ROOT/dynamic-$run" --baseline "$STATIC_SEED/assets" \
    --output "$PRIVATE_ROOT/combined-$run"
done
cmp "$PRIVATE_ROOT/combined-a/assets/initial_pipeline_cache.db" \
    "$PRIVATE_ROOT/combined-b/assets/initial_pipeline_cache.db"
cmp "$PRIVATE_ROOT/combined-a/assets/pipeline-seed.json" \
    "$PRIVATE_ROOT/combined-b/assets/pipeline-seed.json"
python3 evidence/ps4/outset-coverage-111/verify-coverage.py \
  "$PRIVATE_ROOT/combined-a/assets" "$STATIC_COLLECTION/assets" \
  "$PRIVATE_ROOT/dynamic-a/assets" "$PRIVATE_ROOT/dynamic-b/assets" \
  --output "$PRIVATE_ROOT/combined-coverage.json"
python3 tools/pswaker/complete-package.py assemble --kind game \
  --platform-root "$PLATFORM_ROOT" --program-stage "$PROGRAM_STAGE" \
  --elf "$PROGRAM_ELF" --app-version "$PROGRAM_VERSION" --image "$IMAGE" \
  --assembly-assets "$PRIVATE_ROOT/combined-a/assets" \
  --output "$PRIVATE_ROOT/dynamic-complete"
python3 tools/pswaker/complete-package.py inspect \
  "$PRIVATE_ROOT/dynamic-complete" --platform-root "$PLATFORM_ROOT"
```

`STATIC_SEED` is the retained prepared static pilot; `STATIC_COLLECTION` is its
actual observation export. Repeat the static scenario with this new executable
as a regression control (omit `--scenario` or select `always-small-pot-stock-v1`).
Compare report mappings/lifetimes as well as seed bytes. Preserve the original
runtime baseline, captures and sidecars, static inputs and all failed attempts.
Source inventories are checked before/after preparation; collection additionally
checks the image, baseline and collector inputs. Existing output paths are refused.

Preparation rejects incompatible records and same-identity/different-byte
conflicts, validates complete state mappings and merges compatible additions.
It preserves baseline bytes exactly when there are no additions. Generated
evidence is labeled `dynamic-effect-draw`; that report is retained beside the
seed even when the seed's existing source manifest remains byte-identical.
No fabricated gameplay provenance or host driver binaries enter the package.

Host/target representation and hash checks do not establish portable driver
objects. This pilot uses the same schema 1, clear v5/8-byte and GX v13/2772-byte
descriptions and seeded XXH3 identity as the selected PS4 renderer. Configuration
identity is separate from layout-specific compiled identity. The host's Vulkan
BGRA surface differs from PS4 RGBA; PS4 prepares its own scene/offscreen layouts
and required destination-alpha variants. Existing compatible runtime descriptions
must survive the host recorder round trip byte-for-byte. The
[executed pilot record](../../evidence/ps4/dynamic-collector-148/README.md) states
the exact runtime comparison and remaining physical limits.

## Bounded static/dynamic console handoff

Use only the candidate identified in
[pilot.json](../../evidence/ps4/dynamic-collector-148/pilot.json), the matching ELF,
assembly, fresh inspection and private generation reports. This is the ordinary
01.23 player program with the combined seed; the host collector is never installed.
The private artifact directory is `dynamic-148-complete-01.23`; preserve the
adjacent `dynamic-148-pilot` records. Check package/build/seed hashes before use.
Changing seed bytes or the program requires a newly identified handoff.

Prerequisites: the supported console/package-install and private retrieval setup,
a controller, video/timing notes, a backed-up ordinary opening-Outset save already
available to the owner, and a reachable small breakable ceramic pot with a second
pot of the same kind nearby. No acquired item is needed: lift and throw the pot.
Use an accessible opening house/village area; record the actual room/landmark,
pot appearance and route before first use. If the backed-up opening save or pots
are unavailable, return that gap for maintainer setup; do not acquire progression
or a completed save. Use the same starting save and route on both launches.

Allow about 15–25 minutes of owner work for backup/cache handling, two two-minute
samples, normal Quits and retrieval, plus actual startup/preparation and transfer
time. Cold preparation may take minutes; no fixed time ceiling is imposed. The
selection checks a static pot before use, its first and repeated dynamic break,
and ordinary movement/control/audio regression without playing the story.

1. Fully close PSWaker. Back up `/data/pswaker/` and retain a hash inventory,
   especially saves/settings. Install the exact package. Rename only
   `/data/pswaker/cache/6e885683f47a49a119ae/` to a new retained sibling if it
   exists. Empty both runtime-description and driver caches by selecting this
   fresh build directory; do not delete saves/settings or older caches. The same
   build ID was used by 01.23: installing a package alone is not a cold launch.
2. Film launch through preparation and first control. Record responsive progress,
   success or failure, visible launch-to-control time and resources visible in
   available logs (memory exhaustion/crashes included). Retain `SHADERS`
   configurations-ready=total, pending=0, complete=1, no preparation errors,
   `known-shaders-prepared` before gameplay, and `TIMING` total
   preparation versus final-drain durations. Layout-job count need not equal 288.
   Do not infer total preparation from the final screen or invent absent memory
   measurements; #138 retains the fuller scaling/resource obligation.
3. Load the backed-up opening save. At first visible control, use the port menu's
   **Mark visible gameplay ready and resume**. Film the entire approach with no
   extra unrecorded actions. At the selected pots, arm **Measure Outset (resume
   for two minutes)** and start an external timer on resume. For 0–10 seconds,
   view the intact pot; at about 10 seconds lift/throw the first pot. Record the
   actual break time, visible debris, its disappearance and any pause. Around
   40 seconds break a second same-kind pot and observe the repeat. For the rest
   of the sample, move/turn and perform a few ordinary dry-ground rolls as a
   bounded regression control. Note actual action times, sample ID, audio,
   controls and effect appearance. Do not save changed progression. If a second
   texture is already available nearby, its check is optional and must be labeled
   separately; automated texture coverage is not a physical observation.
4. Use the port menu's **Quit game...** and wait for full closure. Before another
   launch rotates logs, retrieve into a new private cold folder:
   `/data/pswaker/logs/performance-XXXXXX/` in full (`identity.json`, `events.csv`,
   `frames.csv`, `samples.csv`), `platform.log`, `platform.prev.log`,
   `last-stage.txt`, crash logs if present, and the build directory's
   `pipeline_cache.db` plus adjacent `-wal`/`-shm` files when present. Copy the
   database and sidecars together after closure. Retain video, notes, cache
   rename/backup evidence and save/settings inventories. Never retrieve a live
   database or overwrite a previous return.
5. Relaunch the exact package with compatible caches retained. Repeat the same
   starting save, route, timed actions and normal Quit. Retrieve to a separate
   warm folder. Record warm progress/timing and cache reuse independently.
   Compare saves/settings to the backup; document intentional settings writes
   separately. Preserve both returns and the previous cache directory.

Maintainers snapshot each returned database with `complete-package.py pipeline-seed`
(it handles the adjacent WAL without mutating originals), then compare every
identity and all description bytes against this exact frozen seed with
`verify-coverage.py`. Also compare the final static/dynamic observation assets.
Independently inspect raw `shader-wait-ns` events and frame shader counters across
the approach, first action and repeats; require zero missing-pipeline creation/
wait events, including waits below the hitch threshold. Counts, successful startup
and seeded membership alone do not establish zero waits. Use the existing
[frame-pacing analyzer](FRAME-PACING.md) and retain incomplete/failed samples.

Missing/conflicting descriptions or observed missing-pipeline waits require a
collector/seed fix and revalidation of an updated identified package. Return
unavailable scenarios and absent observations explicitly. A known-runtime byte
match, host draw or inspected package does not prove this candidate's physical
appearance, PS4 preparation, resource viability or full-game coverage. These
physical observations remain pending until the bounded return is reviewed.
