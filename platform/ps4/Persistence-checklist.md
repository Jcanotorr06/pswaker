# Owner persistence checkpoint (#20)

Candidate identities and private artifact locations are in the
[candidate report](evidence/persistence-20/REPORT.md). These checks are for PS4
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
