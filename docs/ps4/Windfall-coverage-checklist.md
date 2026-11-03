# Windfall pilot P01: owner capture checklist (#137)

Use the private `PSWaker-137-Windfall-D1` handoff folder in Downloads.
Candidate **137-D1** is a newly assembled complete package, app **01.23**, build
**`6e885683f47a49a119ae`**, for PS4 Slim / 9.00 / GoldHEN v2.4b18.
Its [candidate record](../../evidence/ps4/coverage-137/candidate.json) and
[report](../../evidence/ps4/coverage-137/REPORT.md) contain the exact hashes.
Install `out/IV0000-PSWK00001_00-PSWAKERGAME00000.pkg` from that folder.
Keep `elf/switchwaker`, manifests and the frozen seed together privately.

This first pass is **discovery**. After the return, the maintainer will snapshot,
compare, update the seed if necessary, assemble/freshly inspect a frozen
validation candidate, then supply the clean-cache replay. Preserve the discovery
cache until then. A capture without its observations cannot pass this pilot.

## Protect and identify

1. Fully close PSWaker. Back up all of `/data/pswaker/` to a new private folder;
   verify readable copies and record sizes/SHA-256. Identify saves/settings and
   caches separately. Never delete the profile.
2. Verify the supplied PKG SHA-256 on the PC:
   `b410b25cd7dabc7ca1abe648e24254c214cb6faf4ca768b08fa2a39dca73f0b0`.
   Keep `assembly.json` and the fresh `inspection.json` beside it.
3. Install that exact package. Record actual model/firmware/GoldHEN, date/time
   zone, version, applied controls and prior installation identity. Return any
   difference from the supported configuration.
4. With the app closed, rename only
   `/data/pswaker/cache/6e885683f47a49a119ae/` to an unused sibling such as
   `6e885683f47a49a119ae-before-137-D1-<date-time>`. Record absence if none.
   Preserve that directory and its file inventory. Both runtime descriptions
   and driver caches live under this disposable build directory. Do not touch
   `/data/pswaker/saves/` or `/data/pswaker/settings.ini`.

## Ordinary entry save

Use a backed-up daytime Windfall save with the town square and school accessible,
before leaving on the next story leg. Name it **CP-P01-entry**, record its private
file/hash, actual reload point, story progress, sail ownership, equipment,
applied controls and approach to the boat-side dock. No bombs/upgrades are needed.
Keep the same equipment and world state for replay.

If only an early Outset save is available, progress **normally** through the
pirate ship and first fortress to Windfall, then ordinary-save/back up there.
That progression is setup. Quit and archive setup logs/cache separately; repeat
the cache rename before the pilot. Do not use stage selection, warps, save states
or edited saves to reach Windfall. If the school is closed or the checkpoint is
unavailable, return the actual state instead of silently substituting a room.

## Startup and bounded route

Film continuously from launch through normal Quit. Show a readable timer or
record video timecodes, correlated with the recorder clock using visible
launch/loading/menu transitions. No unrecorded walk or gameplay warmup. Record
the actual first-use time of every action below, then **two complete repeats**
of the same circuit. Allow roughly 10-15 minutes; this is a planning allowance,
not a performance threshold. Include delays/failures.

Observe startup, visible progress/input responsiveness and handoff to gameplay.
Confirm matching `BEGIN build=`, package/seed, empty `CACHE before-init`, successful
`SHADERS` completion and `known-shaders-prepared` before loading. Record full
preparation and final drain separately; startup phases overlap. Note visible
launch-to-control time and available memory/resource telemetry separately.

| Action | Route and observation | First / repeat 1 / repeat 2 |
| --- | --- | --- |
| P01-01 | Walk from actual reload point to the dock near the King of Red Lions; include the approach | Actual video/recorder times |
| P01-02 | Pan water/boat, town and sky; close/far and over-shoulder views | Times and appearance |
| P01-03 | Walk uphill to the central square/vendor area; pan NPCs/buildings | Route and landmarks |
| P01-04 | Talk to the sail vendor, show dialogue/choice, cancel without buying; record already-owned sail if applicable | Dialogue/state and times |
| P01-05 | Walk to bomb shop exterior, pan facade/coast; do not enter or trigger later pirate events | Times and view |
| P01-06 | Return to square, enter school, pan room, speak to teacher without gifts or starting a quest | Entry/room/dialogue times |
| P01-07 | Open/close native inventory and sea chart without changing equipment/settings | Times |
| P01-08 | Exit school, return by same streets to same dock, pan water/town, stand about 10 seconds | Times and endpoint |

Keep the table privately per circuit. Note pauses, occlusion, missing effects,
graphics/audio/control faults, stutters, weather and accidental quest changes.
Record unavailable actions as missing. The route adds Windfall geometry/NPCs/
interior/menu rendering beyond #107; it does not claim explosion coverage.

The recorder writes raw frames/events throughout the launch, including unsampled
gameplay. Its Outset/forest sample labels are not Windfall labels. Do not relabel
this route to obtain a green summary. Keep raw stage/room transitions. Physical
presentation timing remains unverified until corroborated with visible output.

## Finish and retrieve before another launch

1. Ordinary-save at the dock as **CP-P01-exit** in the backed-up test slot. Keep
   CP-P01-entry separately for replay. Record changed hashes and verify reload.
   Intentional saving changes save bytes; record the reason. Settings should
   remain unchanged unless an intentional change is recorded.
2. Use the port menu's **Quit game...**, observe completion and fully close the
   app. Record the outcome and `shutdown,complete`. A crash remains an incomplete
   return: keep failure evidence and matching ELF, never claim normal Quit.
3. Retrieve the whole unique `/data/pswaker/logs/performance-XXXXXX/` directory,
   `platform.log`, `platform.prev.log`, `last-stage.txt` and any crash log.
4. Retrieve the closed-app build cache into `P01-D1-cold/cache-after/`, including
   `pipeline_cache.db` and adjacent `pipeline_cache.db-wal`/`-shm` when present.
   Note absent sidecars. Do not checkpoint/modify originals. Retain a paths/
   sizes/SHA-256 inventory and backup/rename evidence.
5. Keep video, timecoded notes, ordinary entry/exit save references and the filled
   [scenario record](../../evidence/ps4/coverage-137/pilot-record.example.json)
   with this launch. Return its private location for analysis. No game-derived
   files belong on GitHub.

## Warm comparison and subsequent acceptance

After retrieving cold evidence, optionally repeat with the **same** package,
CP-P01-entry and equipment, retaining the discovery cache. Restore the entry save
only with the app closed, keeping CP-P01-exit backed up; record the restoration
and actual reload. Repeat startup/route/Quit/retrieval into `P01-D1-warm/` before
logs rotate. Mark `cache_state: warm`. Warm data cannot pass cold acceptance.

After the agent supplies frozen V1 (or confirms the exact D1 PKG/seed can serve
as V1), replay from CP-P01-entry after backing up/renaming only that build's
disposable cache. Any seed change requires a newly identified assembled/
inspected PKG and another cold run. A learned cache cannot prove shipped coverage.

## Agent analysis on return

Use existing `pipeline-seed` and full-byte `verify-coverage.py` commands in the
[campaign protocol](COVERAGE-CAMPAIGN.md). Hash sources before/after; preserve
database/WAL and provenance. Compare every configuration identity/description
byte, not row counts. Report zero additions truthfully if identical. Retain
missing/conflicting-description failures and expand the cumulative seed before
validation if necessary.

Inspect **all** `events.csv` for `shader-wait-ns` (sample 0 and sub-35 ms waits
included), `invalid`, phase/stage markers and `shutdown,complete`. Check
`frames.csv` shader counter deltas, including the first observed/resumed frame.
Match build/cache/package/quality to inspection and actual action timecodes to
monotonic records, retaining uncertainty. Include loading, approach and all
three circuits. Check preparation completion/cleanup before gameplay.

`frame-pacing.py` accepts only Outset/forest target scenes. Preserve any invalid
Windfall analyzer result; do not change raw labels or interpret its exit 2 as
a pilot pass/failure. Report explicit raw wait counts/totals/max, frame counter
deltas, startup/progress/memory, action observations and seed membership. If
returned evidence exposes a tooling gap, add only the needed public artifact
check/test. There is no new renderer seam.

Append results with frozen candidate identities, cold/warm separately, cumulative
milestone, provenance, next save and limitations. Observed missing-pipeline waits
require correction/replay. Eligible missing observations require named risk and
explicit owner acceptance. Keep #137 open until that review is complete.
