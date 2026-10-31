# Owner return: Outset action baseline (#108)

The owner returned one empty-cache launch and one retained-cache relaunch of an
**unseeded 01.19** package, following the
[action baseline checklist](../../../docs/ps4/Action-baseline-checklist.md).
Each launch completed one two-minute Outset sample of rolls, sword swings and
swimming. Validated snapshots of both launches' pipeline databases were returned.

**Every configuration recorded in either launch is already in the 287-record
01.13 seed, with identical description bytes.**

In the cold launch, the first rolls coincide with about 3.2 s of sustained
shader waits. The first sword swings and the water entry each coincide with
one or two shader-correlated spikes. Later repetitions show no shader waits,
only smaller spikes without them. The warm relaunch has no shader-correlated
spikes.

Per-action timings, video, backup records and normal-Quit shutdown evidence
were not returned (see [limits](#limits-and-gaps)). Issue #108 stays open until
this return is reviewed.

## Baseline identity

| Item | Value |
| --- | --- |
| Console | PS4 Slim / firmware 9.00 / GoldHEN v2.4b18 (owner-confirmed; `BEGIN` line agrees) |
| App version / build | `01.19` / `48d0196e605f00284b21` (logs, `identity.json`, inspection and owner JSON agree) |
| Package SHA-256 | `b7739a9c2fb6490dc2faceffe44e706a6f1ecc412805ffb76aaa13ec7fc1319e` |
| Matching ELF SHA-256 | `88fa0ebf2c1c697b79e2215cece47c7f117250fc76fee5be0ddc0a7109c6a70b` |
| SELF (`eboot.bin`) SHA-256 | `56c77cf927304c059fbe8aa346abf3bac1103be8b2820c5a5952262432eeed8a` |
| Pipeline seed | None: no `pipeline_seed` in the manifest; both logs report `No bundled initial pipeline cache found` |
| Cold cache | `files-before-init=0` for `/data/pswaker/cache/48d0196e605f00284b21/` |
| Warm cache | `files-before-init=4`; the cold launch's returned database and WAL SHA-1 values match the warm launch's `CACHE before-init` listing |

The package is the private CLI assembly `image-check-121-01.19` from the #121
image-check program. It is not a released candidate. A fresh extraction and
inspection (`complete-package.py inspect`, 2026-10-30 23:02 -05:00) passed and
reproduced the returned `inspection.json` byte for byte. Both logs retain the
allocated 1280x720 internal size and pipelines=sync. The quality contract is
unchanged.

## Measurements

The cold sample is [cold/summary.json](cold/summary.json); the warm sample is
[warm/summary.json](warm/summary.json). Replaying `frame-pacing.py` on the raw
launches reproduces both summaries exactly, with exit 2. The reference limits
remain average >=29.5 FPS, p95 <=35 ms, p99 <=50 ms and maximum <=100 ms.

| Launch | Seconds | FPS | p95 ms | p99 ms | Maximum ms | Shader waits (calls / ms) | Correlated hitches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Cold | 120.004938 | 29.348792 | 33.400989 | 66.733669 | 333.668729 | 82 / 3,531.310 | 47 |
| Warm | 120.021617 | 30.002928 | 33.394892 | 33.424658 | 50.138269 | 1 / 0.426 | 0 |

Cold misses the average, p99 and maximum limits. Warm meets every numerical
limit. Neither sample is a pass, for two reasons: timing verification is false,
and neither launch has a recorder `shutdown,complete` event. The analyzer also
lists `forest` as missing, which this route does not sample.

## Startup, preparation and loading

| Phase (`events.csv`) | Cold ms | Warm ms |
| --- | ---: | ---: |
| startup | 914.0 | 1,514.5 |
| content-validation | 1.6 | 1.6 |
| storage-check | 57.4 | 543.0 |
| shader-preparation | 1.8 | 1,392.1 |
| loading (title, name entry and file select, owner-paced, to gameplay ready) | 37,065.7 | 25,773.8 |
| gameplay ready to sample arm (walk to start) | 31,853.0 | 20,881.9 |

Cold had nothing to prepare. Its known-shaders stage completed 999.8 ms after
launch.

Warm prepared the 258 retained configurations. By 2,112 ms, while the renderer
was still starting, 39 were already created and 219 queued. Known-shaders
completed at 3,324.2 ms. The 1,392 ms preparation phase therefore understates
warm preparation, because compilation overlapped earlier startup.

The cold launch instead created all 258 pipelines on demand, with
**13,641.9 ms** of blocking waits:

- 7,683.8 ms before gameplay was ready
- 2,426.7 ms during the walk
- 3,531.3 ms in the sample

That is the work a seeded cold start would move into preparation. It is not a
measurement of seeded preparation time; overlap and an empty driver cache can
change it.

The cold launch logged 258 waits and its database holds 258 configurations.
The warm launch logged 1 wait and its database gained 1 configuration. This
one-to-one match supports reading each wait as creation of a missing pipeline.

## Action correlation

No per-action timings or video were returned; both owner JSON `actions` fields
restate the planned timeline. The windows below are therefore the planned
timeline, measured from the sample's first presentation.

- Each interval is placed at the presentation that closes it.
- An interval counts as shader-correlated when it exceeds 35 ms and contains at
  least 1 ms of recorded shader wait.
- [correlation.json](correlation.json) lists every in-sample interval over
  35 ms. Regenerate it with `python3 correlation.py cold/raw-launch warm/raw-launch`
  in this folder.

| Cold window | Waits (>35 ms) | Wait ms | Intervals >35 ms | Correlated | Max interval ms | Max uncorrelated ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0–10 s still | 4 (4) | 446.9 | 4 | 2 | 333.7 | 50.1 |
| 10–40 s rolls | 68 (42) | 2,558.4 | 44 | 41 | 250.3 | 83.4 |
| 40–70 s sword | 5 (5) | 399.5 | 8 | 2 | 283.6 | 50.1 |
| 70–110 s swim | 5 (2) | 126.5 | 6 | 2 | 116.8 | 83.5 |
| 110–121 s still | 0 | 0 | 0 | 0 | — | — |

### First occurrences and repetitions

- **Rolls.** From 11.96 s to 15.15 s, 41 nearly continuous spikes contain shader
  waits. This is a sustained drop to about 15 FPS: most intervals are 66.7 ms
  with about 54 ms of waits each, peaking at 200.2 ms (11.96 s) and 250.3 ms
  (14.35 s). Compilation is strongly supported for the first rolls. It reads as
  a 3.2 s slowdown, not one isolated freeze. After 15.15 s the remaining rolls
  have no waits; only 83.4 ms at 19.32 s and 50.0 ms at 35.13 s occur, both
  without waits.
- **Sword.** The first swings coincide with 283.6 ms at 43.21 s and 183.5 ms at
  44.04 s, containing 251.6 and 147.9 ms of waits. Later swings have six
  single-frame 50 ms intervals with no waits.
- **Swimming.** Entering the water coincides with 116.8 ms at 72.96 s and
  83.4 ms at 73.94 s, containing 75.5 and 50.2 ms of waits. Later swimming has
  83.5 ms at 83.27 s and two 50 ms intervals, all without waits. One more 50 ms
  interval without waits, at 70.25 s, precedes the water entry.
- **Before the rolls.** During the planned still period there are two spikes
  with waits: 166.8 ms at 6.59 s and 333.7 ms at 6.92 s, which contain 127.4 and
  319.5 ms of waits. Without timings they cannot be assigned to an action. They
  may be an early first roll, or ambient or camera content.
- **Walk.** The cold walk to the start point, before the sample, created 30
  configurations with 2,426.7 ms of waits. Of its 18 spikes over 35 ms, 13
  contain waits; the largest is 784.1 ms. The walk was recorded but not
  described. A covered action during the walk therefore cannot be ruled out.
- **Warm.** The only wait (0.43 ms at 77.23 s, swim window) created the 259th
  configuration. All 14 warm in-sample spikes are about 50 ms (one missed
  presentation) with no waits.

**Other causes remain possible.** Cold has 15 in-sample spikes without waits,
two of them about 83 ms; warm has 14. They occur with both an empty and a
retained cache, which points to non-compilation causes such as scheduling, GPU
work, I/O or first-use resource loading. They need separate investigation under
#107 and must not be attributed to shaders. Correlation also does not prove a
correlated spike was entirely compilation.

## Returned configurations

| Snapshot | Rows (clear v5 / GX v13) | Seed SHA-256 | Source database / WAL SHA-256 |
| --- | --- | --- | --- |
| After cold | 258 (1 / 257) | `bdf848be0d1c43948d2e72fd512160033ebe911f72ba022fed61a81c036114fd` | `6f263afb…29079` / `a05b5f93…81a9a` |
| After warm | 259 (1 / 258) | `cb6f1d4d55a873195c67c4edaacfac8f06d726f0eef4de131f1d3da5e3f1114c` | `6f263afb…29079` / `1d80859c…adad9` |

[seed-cold.json](seed-cold.json) and [seed-warm.json](seed-warm.json) are the
returned snapshot reports, with full hashes. The warm snapshot contains every
cold row plus one.

[seed-comparison.json](seed-comparison.json) compares it read-only with the
seed packaged in 01.13 (`7e3f8527…51dc1`, 287 rows, recorded from 01.12 build
`bc90c33b639295f36912`). All 259 rows are present there, and their
configuration bytes are identical. 28 rows of that seed did not occur on this
route.

Without timings, the configurations cannot be split between the actions, the
walk and the scenery. That split is not needed for coverage: every recorded
configuration is already in the seed. On this run, no description beyond the
287 was needed for these actions.

The open question for #107 is delivery: whether a package that includes and
prepares that seed removes these waits on hardware. The seeded 01.13 package
has never been run on the console. This is one route and one run per cache
state, and other play can reach unrecorded configurations. The earlier
268-configuration cache of this build (see limits) was not returned and is not
compared.

Private artifacts stay in the gitignored `local-research/action-baseline-108/`:

- the databases, WALs and both snapshot directories
- the ordinary logs, which contain build-machine paths
- the owner's report, copied here as
  [owner-report-original.md](owner-report-original.md)

No database, seed, package, save or log bytes are committed.
[original-file-inventory.json](original-file-inventory.json) records the size
and SHA-256 of all 31 returned files. Its paths are relative to that folder:
`launch-1` is cold, `launch-2` is warm, and `REPORT.md` is the owner's report.

## Limits and gaps

- **Physical timing unverified.** `timing_method_verified` is false and no
  video was returned.
- **No per-action timings or notes.** Action attribution uses only the planned
  windows, and the walk is undescribed.
- **One sample per launch.** The checklist asked for two. Each sample still
  holds five repetitions of each action.
- **No shutdown evidence.** Both `platform.log` files end on the port settings
  screen, so they were retrieved while PSWaker was running. Neither launch has
  `shutdown,complete`. The complete cold log, retained as the warm launch's
  `platform.prev.log`, ends with controller removal and input-lost; it has no
  Quit or `EXIT` line. The visible Quit outcome was not recorded.
- **Warm database probably copied while running.** The local copies of the warm
  database and WAL are timestamped before the warm log, which itself was saved
  while PSWaker was running. Copy timestamps are not conclusive. The snapshot
  passed integrity and schema validation; any later commits are unknown. The
  cold copy is corroborated as the closed state, but no normal close was
  recorded.
- **Backup and cache rename not recorded.** An earlier launch of the same build
  (the cold `platform.prev.log`) found 268 queued configurations. Where that
  cache was moved is not recorded; `files-before-init=0` confirms only the cold
  state. Save and settings preservation is not shown.
- **Snapshots stored inside the repository tree.** They are gitignored, but the
  usual private store is `~/.local/share/pswaker-private/`, outside the
  repository.
- **Owner observations minimal.** Visible startup and loading times and
  graphics/audio notes are limited to the owner JSON booleans.

## Acceptance criteria status

| #108 criterion | Status |
| --- | --- |
| Identify package, build, platform, seed and cache; fresh inspection | Met |
| Repeatable route, fixed equipment and start, observed before first occurrence, no unmeasured warmup | Partial: route documented and the whole launch recorded; actual action timings and the walk are undescribed |
| Empty-cache launch with repetitions and a comparable retained-cache relaunch | Met (one sample each) |
| Preserve saves, settings, original caches and evidence | Not shown: no backup or cache-rename record |
| Startup, preparation, loading, first and repeated actions, and warm behavior recorded separately | Met from records; owner notes and video missing |
| Correlate spikes with missing-pipeline waits without blaming every slowdown on shaders | Met, bounded by the planned windows |
| Database and WAL after full close → standalone seed, with hashes, counts, provenance and location | Partial: cold corroborated; warm probably copied while running; no recorded close |
| Full preparation and startup cost, including overlap | Met |
| Game-derived artifacts in the private workflow; only report and identities published | Partial: nothing private committed; snapshots kept under gitignored `local-research/` |
| Physical timing and shutdown limits preserved | Preserved as gaps |

Closing the remaining gaps would need another cold and warm pair on the same
package, with:

- a recorded backup and cache rename
- a timed action log and video, including the walk
- port **Quit game...** before each retrieval

Whether that is required, or this bounded return is enough for the #107
coverage update, is the owner's decision.
