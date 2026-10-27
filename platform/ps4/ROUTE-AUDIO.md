# Outset/forest route and audio checkpoint (#19)

The owner-tested startup baseline already reached Dragon Roost after Outset,
the forest, Forsaken Fortress and Windfall without reported graphics/audio
glitches. Preserve its [returned observations](evidence/startup-17/console-2026-10-25/REPORT.md)
and the [01.05 controls return](evidence/controls-18/console-return-01.05/REPORT.md).
Neither return contains orderly shutdown evidence or the full focused route
review. No route-blocking defect has been identified from that return; this
checkpoint adds observability and a precise follow-up instead of speculative
renderer changes. The [candidate report](evidence/route-19/REPORT.md) distinguishes
prepared artifacts from installed-console observations. The
[owner follow-up to the 01.06 handoff](evidence/route-19/owner-return-01.06/REPORT.md)
confirms the requested title-through-Outset scenes/actions without visual or
audible anomalies in both empty-cache and retained-cache runs, completed-save
relaunch and clean normal port Quit without hanging or lingering audio. No logs
were available; candidate/cache corroboration and internal shutdown-stage evidence
remain outstanding.

## Retained renderer behavior

The actual game uses the reconciled Aurora reviewed in [RENDERER.md](RENDERER.md).
This checkpoint retains those source/patch inputs, synchronous FIFO/frame end,
stock textures, original 30 Hz logic and allocated 1280×720 internal rendering.
It does not adopt asynchronous end-frame, FIFO fast paths, HD textures or 60 Hz.

| Risk to examine in actual scenes | Retained implementation and evidence boundary |
| --- | --- |
| TEV/alpha | Patch 0001 latches colour inputs for alpha-channel compares. The diagnostic tests six compare operations; real foliage/particles/fades still need scene observations. |
| Toon lighting | Patches 0002/0004 use lit SRTG colour and finite zero-brightness attenuation. Synthetic lit-colour/attenuation tests do not cover all Outset/forest materials. |
| Quads | Patch 0003 emits a trailing three-vertex triangle and omits incomplete one/two vertices. Diagnostic coverage is bounded; inspect UI, text and effects in game. |
| EFB copies/scaling | Patches 0009/0017 retain viewport/copy scaling and synchronized copy-texture lookup. Actual telescope/transition images need the owner check; picto readback keeps explicit synchronization. |
| Texture/pipeline caches | Patches 0007/0012/0016 retain bounded database recovery and texture-object identity checks. Each binary has its own cache ID and logs pre-init contents. Cold/warm game runs remain separate evidence. |
| FIFO/frame order | Excluded 0018/0020/0021 remain excluded. Frame-end completion and capture reads drain the worker; inspect cuts/transitions for stale content. Source ordering and diagnostic pixels do not prove every game transition. |

No uncertain visual/audio mismatch was reported in the baseline, so there is no
specific original-game discrepancy to patch. Any uncertainty in the new return
requires a same-scene USA revision-0 original-game comparison, with captures,
action and cache/build association, before declaring it resolved.

## Clocked game audio and diagnostics

Ordered game patch 0005 builds on the unchanged SwitchWaker DMA/DSP engine:
the monotonic clock drives eight-frame/32-byte steps, interrupts occur at DMA
block ends, big-endian right/left samples convert to host left/right signed
16-bit PCM, and SDL converts the 32/48 kHz source to the selected PS4 backend's
48 kHz float-stereo 256-frame output. No pull callback drives game interrupts.
The existing 200 ms software queue bound and >100 ms clock catch-up policy stay.

Repeated queue drops and skipped source frames now have cumulative counters.
SDL init/open/resume, queue-query/put and format-change failures are reported;
a failed format change retains the previous rate and retries next tick. Every
five-second game heartbeat and normal shutdown record the counters alongside
game scene/frame/resource state. The queue byte count is a sampled input queue,
not a presentation timestamp or device latency measurement.

The executable's link wrapper observes `sceAudioOutOutput` return codes from
the unchanged, verified SDL archive, including its final null-buffer drain.
It returns the original result and does not change buffering/pacing. The pinned
backend/header contract supplies no documented hardware underrun counter:
logs explicitly say `hardware-underruns=unsupported`. API errors and software
drops/skips are evidence to investigate; their absence cannot establish hardware
underrun absence, DSP correctness or synchronization. Real music/effects and
visible/audible action alignment require the owner return.

## Normal shutdown

Quit occurs at the stopped game-frame boundary. Before requesting SDK shutdown,
it checks the actual card manager under its SDK mutex. A queued command counts
as busy even before the worker takes it. It waits for requested work, reports
a failed completed store without consuming SaveSync state, and after 30 seconds
offers Retry or explicit Exit with no save-success claim. It never requests a
gameplay save. Before the card thread is initialized, there is no work to wait for.

After that boundary the existing SDK shutdown request stops audio production;
the DMA producer joins before SDL conversion is flushed/drained (bounded to two
seconds) and its stream is destroyed. GPU work then synchronizes before Aurora
teardown. Logs preserve card outcome, join, drain, backend errors and final stage.
Fatal paths retain process-owned audio/GPU objects to avoid teardown under
unknown SDK locks. Owner-chosen Exit after a timeout can abandon unfinished
work and is explicitly an error exit. This does not implement #21's full storage
failure/recovery guarantees, settings writes, backups or durable-save acceptance.

## Build and return

Use the locked WSL2/Linux host, a fresh game root, and the verified #15 platform:

    bash tools/pswaker/build-game.sh "$HOME/.cache/pswaker/game-19" \
      "$HOME/.cache/pswaker/maintained-15-a" 01.06

Assemble and independently inspect through [COMPLETE-PACKAGES.md](COMPLETE-PACKAGES.md)
with this root's explicit program-stage/ELF, the owner's supported image and
version 01.06. Keep the stable application identity. Retain the unstripped ELF,
SELF, complete package, full input inventories, notices, build logs and hashes
privately; no game data or binaries are committed. Use the documented locked
host recovery if needed and restore the host package afterward.

Host audio checks compile the actual DMA engine, SDK OS threads and Aurora
address conversion with SDL services simulated. They check known right/left
PCM conversion, format-change retry, repeated queue drops, queue-query errors
and producer join before stream drain/destruction. Card checks compile the
actual game manager with real SDK locks/threads, requesting saves through its
public API and observing queued/active/completed/failed work without consuming
SaveSync. Storage calls and imported JKR registration/heap services are
simulated; these tests neither run game DSP nor write GCI data. Existing controls
checks cover the menu's deliberate Quit confirmation. The entire Quit/GPU/
Aurora process order remains source-reviewed and requires console evidence.

    export PSWAKER_GAME_ROOT="$HOME/.cache/pswaker/game-19"
    export PSWAKER_REFERENCE_BUILD="$HOME/.cache/pswaker/maintained-15-a"
    python3 -m unittest discover -s platform/ps4/tests -p 'test_route_*.py' -v

The [owner checklist](Route-audio-checklist.md) defines cold/warm route, focused
rendering/audio and normal Quit observations and FTP collection. The six-sample
performance contract remains #22; package construction and extended play alone
do not complete #19.
