# Owner persistence checkpoint (#20)

## Saved controls follow-up (#94, after first playable)

Use a separately identified new build and private settings backup for these
checks; they do not change the original #20 acceptance. See the
[applied controls format](APPLIED-CONTROLS.md).

- [ ] Launch a complete custom layout, close and relaunch, then compare applied
  gameplay and both legends. Confirm the shared profile location remains the
  same after a versioned package update and cache-only clearing.
- [ ] With a temporary settings profile, check an absent controls section:
  complete defaults, no warning, no file rewrite. Check malformed/incomplete,
  duplicate, reserved and unsupported layouts: complete defaults, visible reason,
  byte-identical settings. Restore the private backup after the trials.
- [ ] Change port text size with a valid saved layout. Relaunch and verify both
  settings survive, including unrelated lines and `[dev]` placement.
- [ ] Record read/unavailable-storage failures separately from controls fallback;
  the existing Retry/Exit storage screen must still gate gameplay. Use only a
  temporary profile for failure trials and preserve real progress.
- [ ] Return the exact build/package association and missing observations. No
  hardware result for #94 is implied by the host harnesses.

## Button Apply follow-up (#95, after first playable)

Use a new identified build and a private profile backup; preserve real saves.

- [ ] Apply a custom layout from the editor. Fully close and relaunch; verify
  all six bindings, both preserved inversion switches, applied legends and
  gameplay. Confirm text size, unrelated lines and `[dev]` placement survive.
- [ ] With a temporary profile, verify Discard performs no settings write.
  Exercise failed Apply and successful Retry after repair. Retain observed
  file bytes and menu/gameplay behavior; uncertain completion may have changed
  disk despite the old in-memory layout. Never infer disk rollback from Discard.
- [ ] Check a versioned package update and cache-only clearing separately,
  preserving the shared applied layout. Restore the private profile backup
  after any failure trials. Return missing observations as pending.

## Restore defaults follow-up (#96, after first playable)

Use a new identified build and a private profile backup with custom bindings,
both saved inversion switches On, Standard text size and unrelated settings.
Preserve real saves; use a temporary profile for failure trials.

- [ ] Compare settings bytes before and after cancelling restore confirmation,
  then after confirming reset and choosing Discard. Both flows leave the file
  byte-identical and the previous applied snapshot/generation unchanged.
- [ ] Reset and successfully Apply. Compare settings: the complete controls
  section now contains six default bindings and both switches Off. Text size,
  unrelated lines and `[dev]` placement remain intact. Fully close/relaunch;
  verify the default gameplay layout and both applied legends.
- [ ] Exercise failed and uncertain reset Apply in a temporary profile. Retain
  file comparisons and observations of the old applied layout, pending defaults
  and Retry/Discard. A successful Retry saves all defaults; Discard never
  rewrites the disk, including after uncertain completion.
- [ ] Compare private save/cache inventories before and after these reset
  actions, accounting separately for normal game saves or cache activity.
  Resetting controls must not clear or rewrite owner saves or caches. Return
  missing observations as pending and restore the private profile backup.

## Camera and aiming preference follow-up (#97, acceptance in #98)

Use an identified new build and private profile backup. In each of neither,
X-only, Y-only and both configurations:

- [ ] Apply a custom binding and the chosen switches together, fully close and
  relaunch, then compare the applied editor/legend and actual camera/aiming
  directions against the [controls checklist](Controls-checklist.md).
- [ ] Confirm the same complete configuration after a versioned package update
  and cache-only clearing. Record identities and private profile comparisons;
  preserve text size, unrelated settings and real saves throughout.
- [ ] With a temporary profile, exercise failed and uncertain Apply: previous
  directions/bindings stay active and pending edits remain. Retry must save the
  whole configuration; Discard never promises rollback of uncertain disk state.
  Missing/invalid controls initialize complete defaults and camera switches Off
  with the existing feedback rules. Storage read failure still gates startup.

Return build-associated observations and failures to #98. Host checks and
historical persistence evidence do not establish behavior for this binary.

## Original #20 procedure

Candidate identities and private artifact locations are in the
[candidate report](../../evidence/ps4/persistence-20/REPORT.md). These checks are for PS4
Slim / firmware 9.00 / GoldHEN v2.4b18, USA GZLE01 revision 0. Record any change
to that environment. Keep a separate record for each numbered step below.

1. **Protect real progress first.** Fully close PSWaker. Using the existing FTP
   workflow, copy all of `/data/pswaker/saves/` and `/data/pswaker/settings.ini`
   to a private PC backup. If settings.ini is absent, record that. Retain relative
   paths, sizes and SHA-256 values (`Get-FileHash -Algorithm SHA256` on Windows).
   Confirm the backup is readable. Do not upload it to GitHub. Do not replace,
   delete, format or seed the owner's real card to manufacture validation data.
2. Install **01.07** through the normal USB package installer. Record the full
   package filename, SHA-256, installed application version and the startup
   `BEGIN build=...` / `PACKAGE_MANIFEST` log block. The title must stay
   PSWK00001. Disconnecting USB afterward must not affect play.
3. Open existing progress without erasing a slot. Record the recognizable player
   name, slot, location and a concrete progress landmark. Make a normal in-game
   save only with progress the owner wants to retain. Wait for the game's save
   completion indication and record it. Do not treat unsaved gameplay as saved.
4. Touchpad → **Change port text size** → Cross. Confirm both the visible text
   size and the displayed Large/Standard value change and that “Port text size
   saved” appears. Record the value. Resume gameplay with Circle.
5. **Full relaunch check:** fully close the application from the PS4 system menu,
   then launch again. Load the same named slot and verify the recorded completed
   progress. Open port settings and confirm the same text size/value. Return the
   observations and the matching per-launch logs. This is the restart test.
6. Close the application and privately back up/hash the resulting GCI files and
   settings.ini again. **Separately install 01.08 over PSWaker**. Record installer
   completion, new installed version, package hash and matching launch manifest.
   Load the same completed progress and verify the same port text size. Retrieve
   saves/settings again and compare bytes/hashes before any new gameplay save or
   settings change. Record exact matches or explain each difference. This must
   be an actual complete-package install; another relaunch does not satisfy it.
7. **Cache separation:** close the application, retain the latest backup, and
   remove only files under `/data/pswaker/cache/`. Do not delete `/data/pswaker`,
   `saves`, `settings.ini` or logs. Relaunch, load matching completed progress,
   check the setting and compare retained user-data hashes. Keep cold preparation
   timing separate from gameplay. The prior #17 repaired-package evidence stays
   historical; it does not prove these steps for this new binary.
8. **Normal Quit:** play without making another in-game save, note an unsaved
   action, then Touchpad → Quit game → Cross. Relaunch and verify the last
   completed save and setting remain, without treating the unsaved action as
   automatically saved. Record any save activity observed before quitting;
   controlled pending-write overlap and failure/corruption trials belong to #21.

For each launch collect `/data/pswaker/logs/platform.log`, `platform.prev.log`
and `last-stage.txt` promptly before later launches rotate/overwrite them.
Identify `STORAGE checked`, `SETTINGS saved`, `BEGIN`, `PACKAGE_MANIFEST` and
shutdown stages when available. Keep owner observations when logs are missing,
but record the resulting binary/storage corroboration limit explicitly. Include
screenshots or a short video of recognizable progress and the observable setting
when practical. Never claim an old binary's results for a newly built one.

If startup says storage is unavailable, record the exact path/message. Repair
space/permissions or the obstructing path while preserving user data; Cross
retries and Circle exits. Gameplay must not begin until the check succeeds.
Do not deliberately corrupt or make the real owner profile unwritable for this
checkpoint; #21 provides the controlled failure/recovery procedure separately.

Return the package/version/build association, before/after private hash comparison
results, named progress/setting observations for **both relaunch and update**,
cache-only clearing and normal Quit results, and any errors or missing evidence.
Keep saves, game images, private network details and credentials out of public
reports. #20 remains hardware-pending until that return is reviewed.
