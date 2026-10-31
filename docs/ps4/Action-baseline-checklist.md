# Outset action baseline checklist (#108)

This captures the PS4 baseline for [#108](https://github.com/Jcanotorr06/pswaker/issues/108),
part of [#107](https://github.com/Jcanotorr06/pswaker/issues/107): cold-install
hitches during rolling, swimming and sword swings around Outset, and the
pipeline configurations that route encounters. It is future-release work and
does not reopen the [accepted initial release-candidate performance gate](../../evidence/ps4/performance-22/OWNER-DECISION.md).

Use the existing [frame-pacing recorder and analyzer](FRAME-PACING.md) and the
[pipeline-seed snapshot](COMPLETE-PACKAGES.md#required-pipeline-description-seed).
Every game package carries the recorder; no new build is needed. Only the
owner's console return completes this ticket. A record count, host checks or a
returned seed without action evidence cannot.

No earlier return records when each action first occurred, so earlier private
evidence does not satisfy this route. Retain it unchanged; do not substitute it.
The [first 01.19 return](../../evidence/ps4/action-baseline-108/REPORT.md)
records the results and remaining gaps. The owner
[accepted it as the #108 baseline](../../evidence/ps4/action-baseline-108/OWNER-DECISION.md).

## 1. Identify the installed baseline

Use the complete package already installed when its private `.pkg` and
assembly/output folder are retained. If you must install one, record why and
which. Do not assume the installed package matches an earlier candidate.

Record:

- Console model, firmware and GoldHEN version, date and time zone.
- App version on the PS4, and the `.pkg` SHA-256 on the PC:

  ```powershell
  Get-FileHash -Algorithm SHA256 -LiteralPath '<private package path>'
  ```

- A **fresh** inspection of that package. For CLI-assembled packages, on Linux/WSL2:

  ```bash
  python3 tools/pswaker/complete-package.py inspect \
    "<private assembly directory>" --platform-root "$PLATFORM_ROOT"
  ```

  It rewrites that directory's `inspection.json`. For a desktop-created package,
  record the output folder's `inspection.json` and the matching PKG hash; the
  desktop app has no reinspection command. Return that limitation so a
  maintainer can repeat inspection with `windows_package.inspect_output`.
- Seed presence: `pipeline_seed` (rows, configurations, SHA-256) in the
  inspection, or its absence in an older baseline. New game complete packages
  require this field. Current inspection rejects unseeded packages; preserve
  older baseline evidence and report that limitation instead of treating it as
  evidence for a newly assembled seeded package.
- From the first launch's `platform.log`: the `BEGIN build=` and `PACKAGE_MANIFEST`
  lines, the `CACHE before-init` listing and `files-before-init` count, and
  the `Seeded pipeline cache from ... rows merged` line or
  `No bundled initial pipeline cache found`.

The build in `platform.log`, `identity.json`, the inspection and your owner
JSON must all agree. Stop and report any mismatch.

## 2. Back up and empty the disposable cache

1. Fully close PSWaker. Download **all** of `/data/pswaker/` by FTP into a new
   private backup folder. Record paths, sizes and SHA-256 values and check that
   the copies are readable.
2. Rename only `/data/pswaker/cache/<build-id>/` to a new, unused sibling such as
   `<build-id>-before-108-<date-time>`. If it does not exist, record its absence.
   Do not rename or delete `saves/`, `settings.ini`, recovery data or logs. The
   application creates an empty cache at the original path on launch.
3. Keep any installed seed in place; a seeded package's cold state is an empty
   runtime/driver cache **with** its bundled seed. Label which cold state you tested.
4. Use a save that loads on Outset with the Hero's Sword. Do not save during
   these launches. Record the applied controls layout; do not change it.

## 3. The route

Keep the save, equipment (Hero's Sword and shield, no items), start point and
action timing the same in every sample. Pick a start point on open ground,
near the shore, outdoors on Outset. Write it down with a landmark so later runs
match it.

As soon as the loaded save is visibly controllable, open the port menu
(Touchpad) and choose **Mark visible gameplay ready and resume**. This closes
the recorded `loading` phase. Then only walk to the start point: no rolls,
sword, or water. Note that walk. If it crosses a doorway, mark the transition
and visible gameplay as in the [frame-pacing checklist](Frame-pacing-checklist.md).
Do not add any other warmup. Then:

1. At the start point, open the port menu, choose
   **Measure Outset (resume for two minutes)**, and release the controls.
2. Start a visible external timer at the first resumed game frame. Film the
   screen and timer together for the whole sample.
3. Follow this timeline. The recorder closes the sample at 120 s; the final
   still period is only a margin. Stay outdoors near the shore and avoid menus, items,
   cutscenes and transitions:

   | Timer | Action |
   | --- | --- |
   | 0:00–0:10 | Stand still, camera untouched. |
   | 0:10–0:40 | Five rolls on dry ground, about 5 s apart. |
   | 0:40–1:10 | Five standing sword swings, about 5 s apart. |
   | 1:10–1:50 | Walk into the sea and swim near the shore for about 30 s, with a few turns. |
   | 1:50–2:05 | Return to the shallows or shore and stand still. |

4. After at least 125 s, open the port menu and write down the sample number and
   result. Never discard an incomplete or invalid sample. Note its cause, walk
   back to the start point and arm a **new** sample.

For each action, note the timer value of its first occurrence and any visible
hitch on later repetitions:

| Launch | Sample | Action | Occurrence | Timer (m:ss) | Visible hitch / notes |
| --- | --- | --- | --- | --- | --- |
| cold | 1 | roll | 1 | 0:11 | |

## 4. Launches

| Launch | Cache | Samples |
| --- | --- | --- |
| Cold | Empty disposable cache from step 2 | Sample 1: first occurrences. Walk back without the covered actions; sample 2: repetitions. |
| Warm | Retain the cold launch's cache unchanged; fully close before relaunching | Samples 1 and 2 as above. |

For each launch, separately record:

- The time from the home-screen tap to the preparation screen ending, and to
  controllable gameplay. The `phase` rows in `events.csv` (`startup`,
  `content-validation`, `storage-check`, `shader-preparation`, `loading`) also
  record these phases. Compilation can overlap earlier startup phases, so a
  short preparation screen does not prove there was little compilation work.
- Graphics and audio correctness of rolls, swimming and sword effects.
- Any other pause, its timer value and what was on screen.

End each launch with the port menu's **Quit game...**. Record the visible outcome.

## 5. Retrieve after each launch

Before the next launch rotates the logs, with PSWaker fully closed, download to
a new per-launch private folder, for example
`local-research/action-baseline-108/<date>/launch-1-cold/`:

- The whole unique `/data/pswaker/logs/performance-XXXXXX/` directory, plus
  `platform.log`, `platform.prev.log`, `last-stage.txt` and any crash log.
- `/data/pswaker/cache/<build-id>/` into `cache-after/`: `pipeline_cache.db`
  and, together with it, `pipeline_cache.db-wal` and `-shm` when present.
- The video, the action notes table and your written observations.

Keep failed or incomplete launches in their own folders. Never edit raw files.
Inventory each folder's paths, sizes and SHA-256 values.

## 6. Analyze and snapshot (Linux/WSL2)

Copy [frame-pacing-owner.example.json](../../platform/ps4/frame-pacing-owner.example.json)
once per launch. Fill in the build, installed PKG SHA-256 and `cache_state`.
Check `platform` against the console you used; the analyzer accepts only the
supported PS4 Slim / 9.00 / GoldHEN v2.4b18 and exits 1 otherwise. Report a
different console rather than editing the value. Replace its samples with only
the samples actually recorded, all `"scene": "outset"`. Describe the route and
actual action timings in `actions`. Set `active_gameplay` and
`graphics_audio_correct` to what you observed. Leave `timing_method_verified`
false unless the video has actually been reviewed against the recorded timing.
Then run:

```bash
python3 tools/pswaker/frame-pacing.py <launch>/performance-XXXXXX \
  --inspection <inspection.json> --owner <owner-launch.json> \
  --output <launch>/analysis
```

Expect **exit 2** for this route. The analyzer also lists `forest` as missing.
Unverified timing, or a missing `shutdown,complete` event, invalidates every
sample. These do not invalidate the capture. Exit 1 is an identity or input error; fix the inputs, never the raw files.

Snapshot both launches' databases, with the app closed and the originals
unchanged, into new directories **outside** the repository (the tool refuses
repository paths):

```bash
mkdir -p ~/.local/share/pswaker-private/action-baseline-108
python3 tools/pswaker/complete-package.py pipeline-seed \
  <launch-1-cold>/cache-after/pipeline_cache.db \
  --output ~/.local/share/pswaker-private/action-baseline-108/seed-after-cold
python3 tools/pswaker/complete-package.py pipeline-seed \
  <launch-2-warm>/cache-after/pipeline_cache.db \
  --output ~/.local/share/pswaker-private/action-baseline-108/seed-after-warm
```

Each run reads the adjacent WAL itself; see
[COMPLETE-PACKAGES.md](COMPLETE-PACKAGES.md#required-pipeline-description-seed)
for its output. A validation failure is a result; return it.

## 7. Report

Keep packages, saves, databases, seeds and other game-derived files private.
Never attach them to GitHub. Return the private folder locations for review. A
maintainer then writes `evidence/ps4/action-baseline-108/REPORT.md`, following
earlier console returns. It covers:

- The package, build, seed and cache identities from step 1.
- Each launch's phase durations and each sample's metrics and shader waits.
- Frame-time spikes near each noted first occurrence and repetition, compared
  with the `shader-wait-ns` events and `frames.csv` shader counters at that time.
  The report states where compilation is supported and where another cause
  remains possible.
- Seed hashes, configuration counts and source provenance for #107's coverage
  update. For a seeded baseline, the configurations the route added beyond the
  installed seed.
- A fresh reinspection of a desktop-created package, if step 1 could not do one.
- Limits: physical timing unverified, missing `shutdown,complete`, incomplete samples.

Post a short comment on #108 with the identities, the cold and warm results
per action, the seed hashes and counts, and a link to that report. Per
[CONTRIBUTING.md](../../CONTRIBUTING.md), #108 stays open until the returned
evidence and validated snapshot have been reviewed.
