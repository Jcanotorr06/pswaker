# Shader preparation before gameplay (#110)

This extends the existing Aurora renderer and installed-game preparation screen
for [#110](https://github.com/Jcanotorr06/pswaker/issues/110), part of
[#107](https://github.com/Jcanotorr06/pswaker/issues/107). It establishes completion
of included compatible descriptions. Outset action coverage, physical
presentation timing and elimination of action hitches require console evidence.

## Existing behavior and completion

The renderer loads descriptions synchronously in `initialize_pipeline_cache()`,
remembers compatible configurations, and schedules scene/offscreen layout
variants through `rebuild_pipeline_cache()`. It rebuilds when the scene layout
key changes. The game allocates and checks its 1280x720 target before waiting.

`g_pendingPipelines` retains jobs after dequeue until the driver call returns and
the result is published. Likewise, `queuedPipelines` decrements after creation.
Thus the old counter already included in-flight creation; an empty work deque
alone was not the established bug. However, seed failures were optional,
invalid results could drain the queue, and progress compared native pipeline
objects (including prepasses) against queued configuration/layout jobs. GPU cache
pruning could also race scheduling or remain pending after the last creation.

The renderer now exposes one preparation snapshot to its startup caller:

- Loading and layout scheduling must finish before completion is possible.
- Each unique configuration/layout job contributes one unit to total. Ready
  means a successful published result; pending includes creation inside the
  driver. Multi-pass configurations count once.
- Missing, unreadable, empty, malformed or incompatible bundled descriptions,
  unrecovered cache-loading failures, null creation results and captured Dawn
  creation errors cannot become successful completion. Error scopes also catch
  reported creation failures accompanied by a non-null handle.
- Pruning runs after loading, scheduling and creation finish. Completion and
  its timestamp follow cleanup. The port synchronizes prior render work and
  rechecks the result after its final preparation screen frame.

The screen routes failures through `pswaker_installation_error`, preserving its
actionable message, stopped-before-gameplay stage and Exit control. Uncovered
configurations retain synchronous creation and per-frame shader-wait accounting.
After the successful handoff, driver errors retain the existing fatal flow;
a failed newly encountered pipeline cannot become a permanently skipped effect.
Rendering stack, target allocation, stock textures and 30 Hz logic are unchanged.

## Timing and cache lifecycle

`events.csv` records `renderer-initialize` before Aurora starts, then the existing
content-validation, storage-check, shader-preparation and loading phases. These
describe foreground activity; worker preparation overlaps them.

The ordinary `TIMING` line reports `shader-preparation_ms` from before seed
loading through completed creation/pruning, using `pswaker_perf_now()`. It also
records start/completion nanoseconds in that performance clock,
`shader-final-drain_ms` for the final preparation screen, and
`startup_to_preparation_complete_ms` from the existing launch clock. Do not add
overlapping durations or treat only the final drain as preparation cost. A
retained cache can finish compilation before the preparation screen. There is
no numerical startup-time budget.

The runtime description database, seed merge identity, configuration versions,
layout keys and Dawn cache rules remain in use. Compatible relaunches retain
their cache. They still load descriptions and create runtime objects, with Dawn
reusing compatible cached data. A changed compiled build ID selects a new
`/data/pswaker/cache/<build-id>/` directory and requires preparation again. Later
launches are not promised zero startup work.

Caches remain separate from `/data/pswaker/saves/` and
`/data/pswaker/settings.ini`. Keep actual seeds, images, packages and captures in
the private artifact workflow.

## Repeatable host check

Prepare current game sources through the normal build. With the existing
source-built host Dawn/SDL tree:

```bash
cmake -S platform/ps4/host-renderer -B "$CHECK_ROOT" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=clang-21 \
  -DCMAKE_CXX_COMPILER=clang++-21 -DPLATFORM_ROOT="$PLATFORM_ROOT" \
  -DHOST_ROOT="$HOST_ROOT" -DPSWAKER_GAME_ROOT="$GAME_ROOT"
cmake --build "$CHECK_ROOT" --target shader-startup-check --parallel 6
PSWAKER_SHADER_STARTUP_CHECK="$CHECK_ROOT/shader-startup-check" \
  VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json \
  python3 -m unittest discover -s tests/ps4 -p test_shader_startup.py -v
```

The tests initialize the actual renderer and pump its real frame API. Synthetic
SQLite seeds are real files; only the Dawn driver boundary is delayed/faulted.
They verify in-flight work, partial progress, completion, bad seeds, null/reported
driver errors, retained-cache and fresh-cache launches, preserved save/settings
sentinels, synchronous uncovered work with wait accounting, and surfaced failures
after the gameplay handoff. The retained-cache case observes real Dawn cache-hit
callbacks as well as the description merge identity. They add no
private queue seam or independent timing system. They do not observe the PS4
error screen or physical presentation.

## Console handoff

Keep the candidate complete package, matching ELF, build/program/assembly and
fresh inspection reports together. Use the retained candidate recorded in
[the evidence](../../evidence/ps4/shader-preparation-110/README.md). A new build ID
requires new evidence. Assemble through the existing explicit `--assembly-assets`
selection; the validated seed is separate from the program release.

For the final verification work under #107:

1. Back up saves/settings separately and record hashes. Confirm the installed
   package/build/seed identities and PS4 model, firmware and GoldHEN.
2. Fully close the application. Rename only this build's disposable cache to a
   retained sibling, if present. Launch with its installed seed and empty
   runtime cache. Record visible startup, checking, preparation progress and
   first gameplay. Retain errors and stalls without extra gameplay warmup.
3. Confirm final `SHADERS` progress has ready equal to total and pending zero,
   followed by `TIMING` and `known-shaders-prepared` before gameplay. The latter
   stage confirms the final synchronized check and cleanup; no seed/pipeline
   error may become success. Total counts layout variants, so it need not equal the seed count.
   Record full preparation and final drain separately, including overlap with
   validation/storage.
4. Quit normally and retrieve logs before rotation. Relaunch this exact binary
   with caches retained. Record startup again and confirm compatible reuse;
   necessary runtime object creation is expected.
5. For an incompatible update, retain the previous build cache, install the new
   identified candidate, and confirm its new cache directory and preparation.
   Compare backed-up saves/settings; never clear the profile.
6. Return any seed/read/creation failure with its actionable screen, last stage,
   platform logs and matching ELF. It must stop before gameplay. Controlled
   faulty packages need a separately identified private fixture; ordinary
   assembly rejects bad seeds.
7. Use the existing [action baseline checklist](Action-baseline-checklist.md)
   and [presentation/wait records](FRAME-PACING.md) for first and repeated rolls,
   swimming and sword swings. Keep baseline and changed packages, first-use and
   repeated actions, and retained-cache launches distinct. Host completion and
   the current seed count cannot establish action coverage or hitch removal.
