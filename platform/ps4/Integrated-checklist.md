# Integrated first-playable check (#23)

Use **PSWaker 01.13**, build **`f236a035ac406940e76a`**, on PS4 Slim /
firmware 9.00 / GoldHEN v2.4b18. The [review record](evidence/integrated-23/REPORT.md)
identifies the private package and its evidence. This is a request for owner
observations; no integrated console run has yet been recorded here.

The [owner's performance decision](evidence/performance-22/OWNER-DECISION.md)
allows the initial release candidate to proceed with current performance.
Further optimization and strict numerical passes are deferred to #51. Keep
individual measurements and their limitations; do not turn failed or unverified
measurements into passes. Functional, stability and provenance checks still apply.

## 1. Before installing

Record the console model, firmware, GoldHEN, date, currently installed version,
available storage and any changed deployment conditions. Use the existing USB
installer/FTP workflow. Keep private network details out of shared notes.

Fully close PSWaker. Download **all** `/data/pswaker/` to a new private computer
backup. Retain file paths, lengths and SHA-256 values and verify the downloads
are readable. Include saves, settings, backups, pending/recovery files, caches
and logs. Keep this copy until review and restoration are complete.

If an older candidate is installed, load its completed progress and record the
player name, slot, landmark and port text setting before updating. Close it,
retrieve logs and hash saves/settings. Install 01.13 **over the existing
PSWK00001 application**, then load that same progress and setting. Retrieve and
compare saves/settings before making a new save or changing settings. Record
installer completion and both versions. This is the separate package-update
test; a second launch alone does not establish update persistence. If 01.13 is
already installed and no before/after evidence exists, mark this row pending
and return that fact before choosing an update pair. Do not downgrade genuine
progress merely to manufacture a result.

The private file is
`local-research/performance-22-artifacts/candidate-01.13/PSWaker-performance-01.13.pkg`.
On Windows, verify it before transfer:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'local-research/performance-22-artifacts/candidate-01.13/PSWaker-performance-01.13.pkg'
```

Expected SHA-256:
`b3a3f46b8d4b7704b90881b74c7b980543184488cd7e7729f8823706d61a405c`.
Title ID remains `PSWK00001`, content ID
`IV0000-PSWK00001_00-PSWAKERGAME00000`. Remove USB for play. For every launch,
retain `BEGIN`, `PACKAGE_MANIFEST`, build/cache/seed and rendering records; these
associate observations with the package but do not independently hash the installed
executable. Report any mismatch before continuing.

## 2. Isolate disposable progress

With the app closed and the computer backup verified, rename only console
`/data/pswaker/saves` and `settings.ini` to new absent holding names such as
`saves-owner-hold-23` and `settings-owner-hold-23.ini`. Record an absent settings
file instead of inventing one. Never overwrite a holding name. Keep genuine
progress held throughout controlled tests. The game will create a disposable
profile; identify it with a distinctive player name.

Use a fresh disposable in-game slot for each repeated new-game route, or retain
the preceding disposable saves/settings under new holding names while closed.
Preserve each run's files. Resetting disposable progress must leave this binary's
cache and earlier evidence untouched.

## 3. Repeated route on the same installed candidate

| Run | Cache condition | Required visible route |
| --- | --- | --- |
| C | Empty build-specific runtime/driver cache; bundled seed stays installed | Title, name entry, prologue, Outset, forest, completed save, full close/relaunch/load |
| W1 | Retain C's cache, fully close before launch | Repeat the same route with comparable actions and save/load |
| W2 | Retain W1's cache, fully close before launch | Repeat the same route with comparable actions and save/load |

For C, while closed, rename only
`/data/pswaker/cache/f236a035ac406940e76a/` to a new retained sibling if it exists.
Do not rename `/data/pswaker`, saves, settings, recovery files or logs. Let the
app create an empty original cache path. Record the startup cache inventory,
the installed seed identity and 287 merged descriptions. Cold here means an
empty disposable runtime/driver cache **with** the bundled description seed.
Do not remove the seed or copy caches from a different binary. W1/W2 retain the
same path unchanged. The save-load relaunches are additional launches; label
them C-load/W1-load/W2-load and retain their logs separately.

For every run, record actual scene completion and music/effects, pace, audio
dropouts/repetition/desynchronization, graphics defects, hangs and crashes.
Exercise village/shore movement, camera pans, sword/grass/effects, dialogue,
doors/loading and forest traversal/combat. Record available equipment and any
unavailable action. Preserve the first encounter with each effect; no extra
warmup to hide hitches. Save at a recognizable available location, wait for
completed in-game save feedback, change the port text setting and record it.
Fully close/relaunch, load and verify the named progress and setting. Separately
make unsaved progress, use normal port Quit, and confirm only the last completed
save loads afterward. Record whether Quit returns visibly to the PS4 menu.

The recorder remains available for **separate** two-minute Outset and forest
samples on C, W1 and W2 (six distinct diagnostic rows). Use the actions and
measurement boundaries in [Frame-pacing-checklist.md](Frame-pacing-checklist.md),
steps 5-8: four 30-second periods of comparable movement, camera and sword/effects,
at least 125 seconds of visible play per sample, no menus or stage changes inside
the sample. Record first-resume delays and every incomplete/failed attempt.
Keep all six rows separate. Further optimization runs or achieving the original
limits are not prerequisites under the owner decision. Missing samples or timing
verification stay explicitly missing, rather than being inferred from that decision.

Use the [return form](evidence/integrated-23/owner-return.md). Record startup,
content validation, shader preparation, loading and transitions independently,
with a visible start/end definition and method (external timer/video/manual
marker). Renderer startup can overlap seed preparation; the final preparation
screen wait alone is not total compilation time. No loading-time limit is invented.

## 4. Controls and shutdown

Apply the action rows in [Controls-checklist.md](Controls-checklist.md) to **this
01.13 candidate**, using the identity above instead of that checklist's historical
01.05 handoff. Return each physical input, actual action and scene/context:

- Cross=A, Circle=B, Square=X, Triangle=Y, R1=Z, Options=Start; both sticks and
  available D-pad actions; original GameCube prompts plus the PS4 legend.
- Separate partial/full L2 and R2 travel in contexts that distinguish their
  actions. Mark unavailable contexts pending, not passed from an input log.
- Touchpad/settings, PlayStation symbols, Cross confirm/Circle cancel,
  release-before-confirm, Quit cancel and deliberate Quit confirmation.
- Actual controller disconnect while holding movement, an action, triggers and
  a combination: inputs clear, gameplay pauses, reconnect/held Cross cannot
  resume, neutral release and a new Cross deliberately resume.

Exercise these outside frame samples. Retrieve zeroed input records, audio
counters and ordered shutdown stages. The backend reports
`hardware-underruns=unsupported`; zero API/software errors do not prove zero
hardware underruns. Compare music/effects against what was actually heard.
Keep visible clean Quit and missing internal markers as separate observations.
Look for card completion/idle, SDK shutdown, audio producer join/drain, GPU sync
and `shutdown,complete` in recorder events. Missing markers require review.

## 5. Controlled storage cases

Use [Storage-recovery-checklist.md](Storage-recovery-checklist.md) with **01.13's
inspection and identity**, replacing the historical 01.09 references. The genuine
profile must remain held; use only a completed **disposable** GCI from this
candidate. Prepare cases on WSL2 with a new absent private output directory:

```bash
python3 platform/ps4/storage-cases.py \
  --seed /absolute/private/disposable-seed.gci \
  --inspection "$HOME/.local/share/pswaker-private/performance-22-01.13-final/inspection.json" \
  --output "$HOME/.local/share/pswaker-private/integrated-23-storage-cases"
```

Follow the existing exact transfer/retention steps for each **complete** isolated
case, never merge profiles: startup unavailable Exit and Retry; corruption
decline, explicit restore and no valid backup; failed in-game write and failed-write
relaunch; observed 20-second pending-write Quit and relaunch; unsaved gameplay
Quit. Return every requested case row, actual choices/feedback/loaded progress,
settings and original bytes. An idle Quit does not demonstrate pending-write
coordination. These cases test controlled failures, not every possible physical
storage fault or power-loss condition.

## 6. Retrieve after each launch and restore

Before another launch rotates ordinary logs, download to a new private per-run
directory:

- All `/data/pswaker/logs/`, including the whole unique `performance-XXXXXX`
  directory (`identity.json`, `frames.csv`, `events.csv`, `samples.csv`),
  `platform.log`, `platform.prev.log`, `last-stage.txt` and other runtime records.
- `/data/DolphinPS4/crash.log` and other available traces if present; record
  absence rather than fabricating logs. Include photos/video and exact error text.
- Relevant disposable primary, backup, pending, test and recovery evidence files,
  settings, startup cache inventory, and actual package/build/seed association.

Retain original failures and inventory all downloads by relative path, size and
SHA-256. Keep raw data unchanged. For diagnostic samples copy
[frame-pacing-owner.example.json](frame-pacing-owner.example.json), fill actual
sample numbers/actions and cache state, leave timing verification false unless
reviewed, and use the [existing analyzer](FRAME-PACING.md#preserved-evidence-and-analysis).
Its exit 2 can mean a retained shortfall or unverified timing; the performance
exception does not change analyzer thresholds or authorize editing raw results.

Resource observations come from the five-second game heartbeat: driver
garlic/onion/buffer allocations, main-mspace and available flexible memory.
Compare repeated comparable landmarks across runs, include method/units/limitations,
and investigate sustained growth alongside crashes, repeated audio defects and
failed checks. A sampled counter is not proof that no leak exists.

Finally close the app, hold all disposable saves/settings under new absent names,
restore the held genuine entries to their exact original paths, and compare
**all** genuine save/settings hashes with the independent computer backup.
Do not merge `.test`, `.pending` or recovery fixtures into genuine progress.
Launch once to confirm genuine progress/settings, retaining its own logs.

Return observations and the private evidence location for review. Keep game data,
saves, keys, credentials and private network details out of shared artifacts.
First-playable acceptance remains pending until the applicable evidence is reviewed;
the performance exception does not grant binary redistribution or public release.
