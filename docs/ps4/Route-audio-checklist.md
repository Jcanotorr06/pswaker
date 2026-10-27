# Owner route and audio check — issue #19

Use version **01.06** from the [candidate report](../../evidence/ps4/route-19/REPORT.md).
Back up completed saves/settings before updating the same PSWK00001 application.
Install through the usual USB workflow, confirm PS4 Slim / firmware 9.00 /
GoldHEN v2.4b18, and remove USB before play. Keep the earlier #17 and #18
observations as historical evidence; this binary needs its own return.

## Record each launch

- [ ] Compare the PC package SHA-256 with the candidate report. Record run name,
  date, version, build ID, loaded slot/name/progress, and cache state.
- [ ] For a cold run, with the application fully closed, remove **only** this
  candidate's `/data/pswaker/cache/<build-id>/` directory. Preserve saves,
  settings and other builds' caches. For a warm run, close normally and relaunch
  without clearing that directory. Repeat the route in both states.
- [ ] Use a spare in-game slot for a new-name route; retain real progress.
  Existing saves may supplement representative checks but cannot substitute for
  title → name entry → prologue → controllable Outset → forest transitions.
- [ ] Note time from launch to usable title and each requested scene to usable
  control separately from gameplay. Main-clock and game-clock log timestamps
  have different origins. Note visible transition completion yourself.

Keep a row per observation: `run / build / cold-or-warm / scene / action /
approximate time / visible result / audible result / pass-fail-pending`.
A phone video with game sound can help associate a defect with the scene and
time; still return the written result. Missing observations stay pending.

## Route and representative rendering/audio

| Scene/action | Visible checks | Audible checks |
| --- | --- | --- |
| Title, name entry, new-game selection | Logos, text, alpha edges, name characters and menu quads; readable and stable | Title music and confirmation/cancel effects; no clicks or gaps |
| Prologue through arrival on Outset | Story art/text, fades, cuts and return to controllable gameplay; no old-frame flashes | Music continues at expected pitch/tempo across cuts; effects align with visible events |
| Outset outdoors; move camera around Link, shoreline, houses and foliage | Toon lighting, shadows, texture boundaries, translucent foliage/water; no missing triangles, stale textures or flicker | Outdoor music/ambience, footsteps and contextual actions remain continuous |
| Enter/leave Grandma's house and Orca's room; complete route-required dialogue and sword actions | Interior/exterior lighting, UI/text, held items and transitions; no route block | Door, dialogue, item/sword sounds; music changes correctly without persistent overlap |
| Use the telescope where the story requires it | Magnified scene, overlay borders and fades; no displaced/scaled copies or stale image | Telescope/menu effects and story cues align with the action |
| Climb to the mountain path, cross the bridge and enter the forest | Geometry, sky/foliage alpha, scene ordering and loading completion | Music/ambience changes without reproducible dropout or tempo/pitch shift |
| Forest movement, camera, grass/sword hits and required combat/rescue | Lit characters/enemies, particles, alpha edges and UI; no missing effects or route block | Impacts, enemy effects, fanfares and music continuous during action |
| Leave the forest and return to Outset for the next story transition | Correct destination/characters, fades and first usable frame; no remnants of the forest | Transition/story music and effects stay aligned with visible events |

These are representative checks, not proof that every draw uses a particular
TEV/EFB path. For any uncertain result, record the exact scene, camera/action,
slot/progress and cold/warm state; compare the same USA revision-0 scene in the
original game before accepting it. Keep paired captures and the comparison
method/result. Do not change textures, logic rate or rendering quality to hide
a mismatch. The [source review](ROUTE-AUDIO.md) maps these risks to retained
renderer fixes and their existing bounded evidence.

For every row, listen for crackling, missing channels/effects, repeated sound,
dropouts, changed tempo/pitch or growing delay between an action and its sound.
In Outset and the forest, remain in active play for at least five minutes each,
performing several visible actions with distinct sounds near the start/end.
Record whether their alignment changes. Repeat any audible defect using the
same route/action and record its time; repeated defects fail this checkpoint.
Record transition/first-effect pauses separately for #22, including their
effect on sound. Do not dismiss audible defects as shader compilation without
measurement. No numerical audiovisual-drift bound is established by this check.

## Normal Quit and pending work

- [ ] After a completed in-game save, note recognizable saved progress. Make a
  harmless unsaved change, open Touchpad → Quit and cancel with Circle; continue.
- [ ] Open Quit again, confirm with Cross. The application closes without hanging
  or sustained sound. If a card operation was already requested, allow it to
  finish. Record any waiting/error screen verbatim. Do not deliberately corrupt
  real saves or simulate failures against them.
- [ ] If a save is in progress and the port menu can be opened safely in a spare
  slot, confirm Quit then. Record whether “Finishing pending card work” appears
  and the result. If that overlap cannot be exercised, mark it pending.
- [ ] On relaunch, the last completed in-game save remains available; unsaved
  gameplay was not automatically saved. This bounded observation does not
  replace #20/#21's full persistence/failure-recovery contracts.

## Return before another launch rotates logs

Retrieve by FTP into a **new PC directory per launch**:

- `/data/pswaker/logs/platform.log`, `platform.prev.log`, `last-stage.txt`.
- `/data/DolphinPS4/crash.log`, `xmb-trace.log`, `boot-trace.log` when present;
  note absent files rather than substituting another run.
- Your observation rows, package hash comparison, hardware confirmation and
  captures. Preserve originals, filenames, byte counts and SHA-256 hashes.

Associate each log's BEGIN/build, PACKAGE_MANIFEST version/ELF/SELF/image and
CACHE records with the retained candidate inspection. Treat platform.prev.log
as a separate launch, potentially another binary. Do not assign last-stage.txt
to a run just because it was downloaded beside that log.

Review AUDIO_OUTPUT counter deltas with the scene/time and cache state. Queue
drops, DMA skips, stream/backend errors and drain errors require investigation;
zero values do not prove clean game DSP or absence of hardware underruns.
`hardware-underruns=unsupported` is an evidence limit, not a passing counter.
Return final SHUTDOWN card-status, producer join, stream-drained, GPU completion
and shutdown stage records. Source-frame/energy counts and synthetic PCM tests
cannot replace your audible observations. This route checkpoint does not pass
the final six-sample frame-pacing contract.
