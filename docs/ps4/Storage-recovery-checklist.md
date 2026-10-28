# Owner storage recovery checklist (#21)

Use only PS4 Slim / firmware 9.00 / GoldHEN v2.4b18, supported USA GZLE01 revision
0, stock textures, original 30 Hz logic and 1280x720 internal rendering. The
[candidate report](../../evidence/ps4/storage-21/REPORT.md) supplies the exact package,
compiled build, SELF/ELF hashes and private retrieval paths. Install the private
01.09 complete package through the existing USB workflow. Record its filename,
SHA-256 and displayed application version. Do not substitute the prior 01.08
binary or attribute its hardware results to this candidate.

## Protect genuine progress first

1. Fully close PSWaker. Through FTP, copy **all** of `/data/pswaker/` to a new
   private computer directory, including both card channels, settings, backups,
   pending files, evidence and logs. Keep the previous #20 return. Record file
   sizes/SHA-256 hashes and verify that downloaded files can be read. Do not
   upload a synthetic fixture over your genuine Dragon Roost save.
2. With the game still closed, rename console `saves` and `settings.ini` to
   distinct, absent `saves-owner-hold-21` and `settings-owner-hold-21.ini` names
   under `/data/pswaker`. Retain the independent computer copy. If those names
   already exist, choose new names. Never replace them. The package does not
   contain user data, and the game will create a separate disposable `saves`.
3. Launch 01.09, confirm normal writable storage, then create **disposable**
   progress with a distinctive player name. Complete an in-game save A at a
   recognizable location. Quit and fully relaunch; record that name, landmark
   and Standard/Large port text setting. This is the fresh candidate baseline.
   Retrieve all logs before another launch rotates them.
4. Fully close. Download that disposable completed
   `saves/USA/Card A/01-GZLE-gczelda.gci` as a private seed. Prepare controlled
   cases in WSL2 using the freshly inspected candidate:

   ```bash
   python3 tools/pswaker/storage-cases.py \
     --seed /private/disposable-seed.gci \
     --inspection "$HOME/.local/share/pswaker-private/storage-21-01.09/inspection.json" \
     --output "$HOME/.local/share/pswaker-private/storage-21-cases"
   ```

The tool does not transfer files. For each case below, close the game, rename
the previous disposable `saves`/`settings.ini` to new case-specific names, then
upload **that case's complete** `saves` and `settings.ini` into `/data/pswaker`.
Do not merge cases: a stale `.backup`, `.pending` or `.test` changes the trial.
Keep `cases.json` privately; its hashes identify exact input data and package.
Standard text (`PSWAKER_LARGE_TEXT=0`) is the controlled setting in these cases.

## Cases and expected feedback

| Case | Owner action | Expected result and evidence |
| --- | --- | --- |
| Startup unavailable / Exit | Upload `startup-unavailable`. Card B is a regular file rather than a directory. Launch, photograph error/path and choose Circle. | Storage unavailable screen, no gameplay, unchanged save A/settings; retrieve logs and compare input files. |
| Startup unavailable / Retry | Reload the same case. While stopped, through FTP rename only the blocking disposable `saves/USA/Card B` file to a retained case-evidence name; create the directory. Press Cross. | Retry probes storage, then normal startup loads save A and Standard text. No reset or false successful save. |
| Corrupt / decline | Upload `corrupt-with-backup`. Launch, photograph exact recovery screen and choose Circle. | Valid-backup restore is offered; decline exits. Download primary, backup and logs; compare byte hashes to `cases.json`. Both remain unchanged. |
| Corrupt / restore | Freshly upload `corrupt-with-backup`. Cross explicitly selects Restore. | Load save A's distinctive name/landmark, Standard text. Retrieve restored primary, `.backup`, every `.evidence-*`, and logs showing the recovery choice. The original corrupt hash must occur in evidence. |
| Corrupt / no backup | Upload `corrupt-no-backup`. Launch; exercise Retry once, then Circle. | No Restore option. Actionable recovery guidance, no gameplay/reset. Primary hash unchanged; no backup silently created. Retrieve error/choice logs and original bytes. |
| Write failure during play | Upload `write-failure`. Explicitly continue the controlled-test warning. Load A, make a recognizable unsaved change B and request an in-game save. | Injected ENOSPC follows the real staged CARD write. Save completion is not reported; port error screen requires Exit. Primary/backup still match A; `.pending` and failure logs remain. Retrieve all before repair/relaunch. |
| Failed-write relaunch | With game closed, remove only this disposable `.test` marker after retaining it. Relaunch. | Interrupted-save recovery screen. Explicit restore loads A, not B. Preserve original stage/evidence, record exact selection and observed loaded progress. |
| Pending-write Quit | Upload `pending-quit`. Continue the warning. Load A, make recognizable progress B, request an in-game save, then quickly Touchpad → Quit → confirm while the 20-second hold is active. | Quit shows pending card work and waits; it never creates another save. Logs must show `STORAGE TEST pending-publish`, busy card waiting, `save-completed=1`, idle card, audio join, GPU sync and final shutdown. If the window was missed, repeat from a fresh case; an idle-only Quit does not count. |
| Pending-write relaunch | Close completely, retain/remove the disposable `.test`, then relaunch. | Load B, the last completed in-game save. Record name/landmark/settings, not merely that a save file exists. |
| Unsaved gameplay Quit | From B, make a recognizable change C without requesting an in-game save. Quit normally and fully relaunch. | Load B rather than C. No save-on-quit. Capture final audio/GPU stages and absence of the earlier GBA command panic. |

For every row record actual visible feedback, choices, loaded player/landmark,
port setting, any freeze/panic, audio result and whether shutdown returned to
the PS4 UI. Never mark an unrun row passed. A failed or uncertain operation may
leave newer primary bytes visible; preserve logs/backup and report that fact,
rather than counting visibility as successful completion.

## Retrieve and restore

After **each** run, before another launch, copy `/data/pswaker/logs/` through FTP
to a new case/run directory on the computer, including `platform.log`, rotated
logs, `last-stage.txt`, runtime/state files and the complete-package manifest
lines. Include screenshots/video of errors and choices. Retain every affected
primary, `.backup`, `.pending`, `.test` and `.evidence-*` file plus unchanged
settings from the disposable case. Keep originals and SHA-256 inventory, not
only selected excerpts. These files are private and must not be committed.

The return must associate 01.09, its compiled build ID and image/SELF hashes
with actual installed `PACKAGE_MANIFEST`/`BEGIN` records. Include whether the
20-second pending hold was observed and all final card/audio/GPU stages.
Returned logs corroborate identity but do not independently hash the installed
executable. Save behavior needs the player's actual loaded-result observations.

Finally, close the game. Rename the entire disposable profile entries to new
retained names. Restore the held genuine `saves` and `settings.ini` to their
exact original paths; ensure no disposable `.test`/`.pending` is merged into
them. Compare **all genuine save/settings hashes** with the independent backup.
Only then launch and confirm the original genuine progress/settings. Retain the
computer backup and controlled-test evidence until review completes.

Hardware-dependent acceptance stays pending until this return is reviewed
against the exact candidate. Do not close #21 based only on package generation
or host tests.
