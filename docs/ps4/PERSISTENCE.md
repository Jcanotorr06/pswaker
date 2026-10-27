# Completed saves and port settings (#20)

The shared profile remains `/data/pswaker/`, independent of the PS4 login.
No migration, initialization save, slot reset or automatic save on Quit is
introduced. Preserve the owner's existing Dragon Roost progress and the
[startup preservation evidence](../../evidence/ps4/startup-17/content-checks-2026-10-25/REPORT.md).
The [candidate report](../../evidence/ps4/persistence-20/REPORT.md) distinguishes host
checks and prepared packages from returned console evidence.

## Storage consumers

| Consumer | Location and behavior |
| --- | --- |
| Installed disc/runtime assets | Read-only `/app0/game.iso`; fixed image and DOL/REL validation remain. |
| Both game card channels | Explicit `CARD_GCIFOLDER`, with `CARDSetBasePath` for each channel before `OSInit`/`CARDInit`: `/data/pswaker/saves/USA/Card A` and `Card B`. Existing GCI names and layout stay compatible. |
| Port settings UI | `/data/pswaker/settings.ini`, `PSWAKER_LARGE_TEXT=0` (Standard) or `1` (Large). Touchpad → Change port text size → Cross saves and immediately changes port-menu text. Default Large preserves the prior 1.7 scale; Standard uses 1.3. |
| Desktop settings | The PS4 harness continues to bypass `pc_settings_load_early` and desktop `menuInit`. Existing unrelated lines, including `[dev]`, are retained when changing the port setting, but never applied as PS4 environment overrides. |
| Aurora user path | Explicit `/data/pswaker`, not the executable path or working directory. |
| Disposable shader/pipeline/texture caches | Explicit `/data/pswaker/cache/<compiled-build-id>/`, including `COS_CACHE_DIR`. Clearing this directory cannot target saves or settings. |
| Logs | `/data/pswaker/logs/`, including `COS_RUN_DIR`, platform logs and last-stage evidence. |

Before the first game frame, create and check the root, saves/USA and both
card directories. Each directory receives a uniquely named scratch file,
checked close, synced file replacement and directory sync; remove the scratch
file afterward. Existing saves/settings are never probe targets. Load the port
setting only after these checks. An unavailable directory or unreadable/invalid
port setting stops at a visible error with its path, repair guidance, Retry and
Exit. Retry reruns creation/checks; gameplay stays gated. Logging/cache setup and
graphics initialization precede this gate so an error can be displayed.

## Completion and replacement

Settings use an exclusive temporary file in the destination directory. Check
writes and close, reopen and sync that file, check directory-sync capability,
rename over the destination, then sync and close the directory. No old-file
unlink occurs before replacement. On failure, retain the previous in-memory
setting and display a failed-write message with the path; Cross on the same row
retries after repair. Confirm success only after the entire operation succeeds.

The game-local Aurora patch uses the same checked commit for its existing
atomic GCI create/data/metadata writes. SDL write/flush/close failures still
propagate before commit. Sync or rename failure before replacement leaves the
old destination intact. A failure after rename is an **uncertain completion**:
the new file may already be visible, but the application reports failure rather
than inventing durable success. Never claim rollback or power-loss guarantees
from host tests.

Game patch 0006 explicitly selects GCI and corrects inherited false-success
paths: save readback checksum mismatch returns an I/O error, copied picture
readback compares the actual returned bytes, and metadata get/set errors reach
the card manager's existing save-failure state. The storage backend tests cover
real GCI data/metadata replacement; the game routine's additional propagation
changes are source-reviewed and target-compiled. The existing pending-card Quit
observer remains unchanged and never requests a gameplay save.

The #20 implementation was atomic per GCI file write, without a transaction
across a multi-block game save. The subsequent [#21 recovery candidate](STORAGE-RECOVERY.md)
adds whole-store staging, previous-valid-save backups and explicit recovery.
Controlled installed-console failure/pending-write acceptance still requires
that candidate's owner return. Retain the game's replicated data and existing
progress; the historical #20 evidence does not validate the newer binary.

## Reproduce and validate

Use the selected WSL2/Linux host and unchanged verified #15 platform archives:

```bash
bash tools/pswaker/build-game.sh "$HOME/.cache/pswaker/game-20-final" \
  "$HOME/.cache/pswaker/maintained-15-a" 01.07

export PSWAKER_GAME_ROOT="$HOME/.cache/pswaker/game-20-final"
export PSWAKER_REFERENCE_BUILD="$HOME/.cache/pswaker/maintained-15-a"
export PSWAKER_HOST_ROOT="$HOME/.cache/pswaker/aurora-host-20261022"
python3 -m unittest discover -s platform/ps4/tests -p 'test_persistence.py' -v
python3 -m unittest discover -s platform/ps4/tests -p 'test_gci_persistence.py' -v
python3 -m unittest discover -s platform/ps4/tests -p 'test_controls.py' -v
python3 -m unittest discover -s platform/ps4/tests -v
python3 -m compileall -q platform/ps4
```

`PSWAKER_HOST_ROOT` supplies a separately built native Linux SDL3 archive in
`sdl/libSDL3.a` for real filesystem tests, never a target dependency. GCI tests
compile the actual prepared Aurora `CardGciFolder`, `FileIO` and I/O sources;
only logging and OS failure injection are simulated. Synthetic progress text
is not an actual in-game save. Settings tests exec a fresh process to verify
reload and preserve other settings. Menu tests exercise real controller input
with console services simulated. The target build typechecks the combined game.

Assemble and freshly inspect private complete packages with the supported
owner image through [COMPLETE-PACKAGES.md](COMPLETE-PACKAGES.md). Initial version
01.07 and update 01.08 deliberately use the same compiled program and disc;
the distinct newer package version isolates installation/update preservation.
Keep title/content IDs fixed. A new build ID selects new disposable caches,
never a new save/settings profile. No package includes or restores user data.

Use the [owner checklist](Persistence-checklist.md). Full close/relaunch,
separate installation of the newer complete package, cache-only clearing and
owner progress/settings observations are required before #20 can be accepted.
The [returned console review](../../evidence/ps4/persistence-20/console-return-2026-10-26/REPORT.md)
now completes that bounded persistence checkpoint for build
`9ac6fb9b2da43e02d642`, with matching 01.07/01.08 manifests and settings
comparisons. A captured Quit panic after an idle card remains an unresolved
lifecycle finding; successful visible Quit/save preservation does not establish
completed internal audio/GPU teardown or #21 failure-recovery acceptance.
