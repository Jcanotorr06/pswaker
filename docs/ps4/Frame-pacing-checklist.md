# Owner sampling checklist (#22)

**Further optimization is deferred by owner decision.** Current performance is
accepted as sufficient to proceed with the initial release candidate. This
checklist is retained for future improvements and diagnostic/regression checks;
it is not a request for another performance run before moving forward.
See the [decision and evidence limits](../../evidence/ps4/performance-22/OWNER-DECISION.md).

The candidate status and strict-target procedure below describe the previous
performance-validation workflow. The owner decision controls the initial
release-candidate performance gate.

Status: **01.13 is untested on PS4.** The 01.12 warm samples met numerical limits;
cold samples failed. Physical timing and internal shutdown evidence remain
incomplete. Use the exact package/build/seed hashes in
[the 01.13 candidate report](../../evidence/ps4/performance-22/candidate-01.13/REPORT.md).
Retain previous failures and save/settings backups. No new test data or cache
operation should touch your genuine profile.

The [01.12 return](../../evidence/ps4/performance-22/console-return-01.12/REPORT.md)
identifies cold pipeline compilation as the next measured bottleneck. Its returned
database/WAL now supplies a bundled description seed for startup preparation.
The owner confirms clean normal Quit, while 01.12 logs stop after the SDK-stop
request. Retain that gap. For this changed package, record visible timing
corroboration, Quit normally and retrieve afterward.

1. Confirm PS4 Slim / firmware 9.00 / GoldHEN v2.4b18, USA GZLE01 revision 0,
   the installed candidate version/build and package SHA-256. Install through
   the existing USB workflow; play installed content with USB removed. Back up
   `/data/pswaker/saves/` and `settings.ini` separately before testing an update.
2. With the application fully closed, make a cold **disposable build cache** by
   renaming only `/data/pswaker/cache/<this-build-id>/` to a unique retained
   sibling, if it exists. Let the application create an empty original path.
   Do not rename/delete `/data/pswaker`, `saves`, settings, recovery data, or logs.
   Label the run cold. Warm runs keep this same binary's cache unchanged.
   Preserve the startup cache listing/hashes from the ordinary log for each run.
   For 01.13, this means an empty disposable runtime/driver cache with the bundled
   description seed installed. Confirm the log merges 287 seed records and
   prepares them before gameplay. Record any mismatch or pipeline/cache error;
   do not add an unmeasured gameplay warmup to hide missing coverage.
3. Keep the unique `performance-XXXXXX` directory for each full launch. Record
   elapsed startup, validation, shader preparation and loading independently.
   Confirm the logged **allocated** internal size is 1280x720 (the 1080p display
   output is separate). Record visible/audio correctness and any abnormal pause.
4. Verify the timing method before any pass claim. Check that raw flip counts
   and arguments advance for each newly presented game frame, game tags remain
   consecutive, unchanged refreshes produce no new frames, the raw clocks track
   elapsed time, and the presented motion matches the tagged sequence. A short
   video with a visible external timer, including a deliberate port-menu pause
   and resume outside the samples, can corroborate new-game versus UI/held-frame
   behavior. Return the video/notes and logs for review. If timestamps, mappings
   or physical output cannot be verified, leave `timing_method_verified=false`
   and return that limitation; agree substitute evidence before any pass.
5. Reach controllable Outset outdoors. After transitions and story sequences
   finish, choose **Mark visible gameplay ready and resume** in port settings.
   Start **Measure Outset**, release controls to resume, record any resume delay,
   then start an external timer at the first visible game frame and stay in
   active play for at least 125 seconds. Keep to the village
   and shore; do not enter interiors, menus or transitions during the sample.
6. Use the same action pattern in both scenes and all launches: first 30 seconds
   walk/run a small loop with a slow full camera pan; next 30 repeat it in the
   opposite direction; next 30 include repeated sword swings/available effects
   while moving; last 30 repeat movement and camera pans. Document the precise
   route/actions and equipment so later runs are comparable. Do not perform an
   extra warmup to hide first-effect hitches. Record any slow first resumed
   frame separately; it remains active-gameplay evidence.
7. After the external timer, open port settings and record the numbered Outset
   result. If it says paused/incomplete/invalid, preserve it and repeat as a
   **new** numbered sample after documenting the cause. Never erase the failure.
8. Choose **Mark loading / transition start and resume** before the forest
   transition. Note the visible loading start and first controllable forest
   frame. When it is visibly ready, mark gameplay ready. Repeat a separate
   **Measure forest** with the same four action periods, within the forest.
   Record scene/stage/room, correctness and individual result. Avoid story events
   during the measured period; note them and retain any interrupted attempt.
9. Use normal Quit, confirming any storage error. Retrieve the whole unique run
   directory and ordinary logs by FTP immediately. Retain video/notes and fill
   in the owner JSON with a row for **every** requested sample. Check logs for
   shader waits, resource trends, errors and ordered shutdown, not just FPS.
   Confirm `events.csv` contains `shutdown,complete`; if absent, retain and
   report that gap with the visible Quit outcome. Do not edit raw files to add it.
10. Fully close/relaunch for warm-cache comparisons with the same actions and
    repeat both scenes. Return the cold and warm launches separately, plus any
    failed launch or sample. The final integrated #23 checkpoint owns its full
    required run matrix; these measurements do not silently satisfy that gate.

Run the analysis command in [FRAME-PACING.md](FRAME-PACING.md). Return all raw
files and individual summaries, package/ELF/SELF identities, cache listing,
owner observations, correctness/audio notes and resource observations. If any
numerical target is missed, report its measured shortfall. Investigate before
altering the selected stack, 720p allocation, stock textures, 30 Hz logic or
acceptance criteria. Renew affected evidence after material changes.
