# Owner checkpoint: installed game startup

This validates only the exact game package in the
[candidate report](../../evidence/ps4/startup-17/REPORT.md). The earlier diagnostic results
do not validate it. Keep #17 open until the returned evidence is reviewed.

## Confirm and install

1. Record PS4 model, firmware and GoldHEN version; expected baseline is Slim /
   9.00 / v2.4b18. Record TV/headphone audio output and approximate volume.
2. Compare the PC package SHA-256 with the report. Normal startup is version
   01.00, title PSWaker, title ID PSWK00001. Use the existing USB installation
   workflow. This is a separate identity from the diagnostic.
3. If /data/pswaker already exists, download a backup before any install or file
   change. Preserve saves/settings when updating. Never clear the entire folder
   to clear shaders.
4. Remove the USB device before playing. The installed application must use its
   own content without an external image.

## Reach the checkpoint

1. For a cold run, with the app fully closed, rename only the candidate's cache
   directory under /data/pswaker/cache/ if it already exists. Record the cache
   label. Other builds' cache directories and saves/settings stay separate.
2. Launch. Observe checking installed content and shader-preparation progress.
   A new cache can report zero known shaders; new shaders then compile when
   encountered. Record launch-to-title time if possible.
3. Release Cross and press it on the legend. Reach the title screen. Confirm
   title visuals and music. Check Cross=A, Circle=B, Square=X, Triangle=Y,
   Options=Start, left stick movement and right stick/C-stick where applicable.
   Touchpad opens the basic port menu.
4. Start a new game, enter a recognizable name, view the prologue and reach
   controllable Outset. Record which steps completed, any stuck scene, loading
   interval or error, and music/effects heard in each scene.
5. Report missing/corrupt graphics, wrong colors, flicker, clipped audio,
   missing music/effects or bad pacing with the scene/action and approximate
   timestamp. If uncertain, compare that scene/action against the original
   game and retain the comparison's platform and observations. Photos/video
   are helpful; say when unavailable.
6. Check a held-input disconnect and deliberate resume if safe. A reconnection
   alone must not resume. This is a basic checkpoint check, not acceptance of
   all controls or the initial trigger threshold.
7. Close normally through the touchpad menu (Circle exits). Retrieve evidence
   before another launch rotates the log. A repeated warm startup is useful,
   labelled separately; the final cold/two-warm full-route contract belongs to
   later acceptance.

Return the package SHA-256/version, shown or logged build ID, cache label and
your actual platform. The log must show allocated internal 1280×720 separately
from output dimensions. A visible title or nonzero audio counter alone is
insufficient evidence of this route or audible game audio.

## Controlled failures and repair

Do this after the valid startup attempt, with the app fully closed.

1. Back up and hash actual seeded GCI save files plus settings.ini on the PC.
   Use a completed in-game save with a recognizable name/progress, or a known
   valid owner save. Do not seed a fake GCI that a repaired game could mistake
   for real progress. If no settings file exists, seed a small identifiable
   settings.ini only after preserving the prior absence in your report.
2. Install the separately labelled missing/01.01 package. Launch and verify a
   visible installation error with computer-side rebuild/reinstall guidance.
   It must stop before gameplay and must not request or search for an image.
3. Download the seeded files and compare their hashes/bytes with the backup.
   Retrieve this launch's logs. Repeat with unreadable/01.02 (image path is a
   directory) and invalid/01.03 (correct-size image, bad checksum).
4. Install the valid repaired 01.04 complete package over the same application.
   Recheck seeded file hashes before launching, then check title/startup again
   without USB. Preserve the seed backup until evidence review.
5. Report any install refusal, changed/missing file, unexpected gameplay,
   external-image prompt or failure to recover after repair.

These checks establish preservation of the chosen files during controlled
installation failures and repair only. They do not establish full save
durability, backups, corruption recovery or package-update gameplay acceptance.

## Files to retrieve

- /data/pswaker/logs/platform.log
- /data/pswaker/logs/platform.prev.log, when present
- /data/pswaker/logs/last-stage.txt
- /data/DolphinPS4/crash.log and xmb-trace.log/boot-trace.log, when present
- Seeded saves/settings before and after failures/repair, retained privately
- A short written report with per-package observations and scene timings

Keep each launch in a separate PC evidence directory. The package manifest in
the log distinguishes versions and image identities even when failure packages
share one executable. Do not publish complete packages, images or saves.
