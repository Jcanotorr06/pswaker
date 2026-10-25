# Returned startup evidence — 2026-10-25

The owner reports reaching controllable Outset and continuing through the
Forsaken Fortress and Windfall Island to Dragon Roost Island, with no observed
graphical or audio glitches. Continuing beyond Outset does not invalidate the
startup observations. The additional play is recorded as exploratory evidence,
without declaring full-route, persistence or performance acceptance.

Both supplied logs match the prepared startup candidate's build, version,
embedded image identity and program manifest. The owner confirmed PS4 Slim /
firmware 9.00 / GoldHEN v2.4b18, USB removed while playing, and a fresh first-launch
cache after first installation. The BEGIN platform string is an expected-target
label; the hardware confirmation comes from the owner. A separate PC comparison
of the installed package SHA-256 and per-launch route attribution were not
explicitly returned. Controlled content-failure and repair checks remain pending.

## Identity and original evidence

- Logged application/version: PSWaker / PSWK00001 / 01.00.
- Logged and manifest build ID: 6ebc07987fe3b6c6064a.
- Expected package SHA-256: 0b619d1b85d51f6c2bebae12369c170f88446c543747bf0d1c24c1fe97643ac1.
- Logged manifest SELF SHA-256: bf3bdd961ab9e652c72996b5038f8a95d371ad4b6b6d7923f8d8620988b51bd2.
- Logged manifest ELF SHA-256: a191be91af014df4ffa983cb672544621c7de489994b898bb478e0efabadbe95.
- Logged image: USA GZLE01 revision 0; SHA-256 ec2d4ee790f48bee3d4c10feed166370df895f474e8db3f9af3b16ee001436df.

The complete logged image/program objects match [candidate inspection](../inspection-01.00.json).
Logging an embedded manifest is not a fresh runtime hash of the executable or
whole PKG. The runtime did separately validate the complete installed image and
required DOL/REL objects before gameplay.

Original files remain unchanged in
local-research/game-17-artifacts/evidence/logs/.
[original-files.json](original-files.json) records all three files' byte sizes and
SHA-256 values. [summary.json](summary.json) records parsed evidence and original
line numbers; [selected-records.txt](selected-records.txt) retains relevant lines.
[owner-observations.json](owner-observations.json) records the owner's report and
subsequent hardware/cache/USB/save confirmations separately from parsed logs.
There is exactly one BEGIN block in each supplied log.

## Two supplied launches

| Logged observation | platform.prev.log | platform.log |
| --- | ---: | ---: |
| Cache files before initialization | 0 | 4 |
| Content progress span | 45.970 s | 44.758 s |
| Installed-image validation completed, main clock | 48.510 s | 48.711 s |
| Known-shader preparation loop | 3.9 ms | 4.1 ms |
| Preparation complete, main clock | 48.602 s | 48.773 s |
| Runtime assets validated, main clock | 48.758 s | 48.920 s |
| Allocated internal target | 1280x720 | 1280x720 |
| Output dimensions | 1920x1080 | 1920x1080 |
| Prepared pipelines reported at startup | 0 | 566 |
| Highest logged created-pipeline count | 566 | 1,138 |
| Last heartbeat, main clock | 3,813.643 s | 8,598.762 s |
| Highest checked-error count | 1 | 0 |
| Logged orderly exit/audio join | absent | absent |

The earlier launch has an empty-cache observation consistent with the owner's
fresh-first-launch confirmation; the later one has four
readable cache/database/WAL files whose names, sizes and SHA-1 values are
retained in the summary. This supports cold/warm cache distinction, but does
not establish the later acceptance protocol's prescribed three-run sequence.

The owner estimated roughly 30 seconds for installed-content checking and
shader preparation. The instrumented intervals above are retained separately
from that estimate. Most of the measured preparation interval is the full image
check, rather than the brief known-shader queue loop. Title-stage milestones
appear at game-clock 85.801 s and 63.116 s respectively. Game-clock milestones
and main-clock records have different origins; they are not interchangeable
launch-to-visible-title measurements.

Both logs contain opening/name/game scene records and sustained audio counters.
The earlier log includes a new-game milestone and Outset/forest archive names;
the later log includes fortress and later-area archive names. Resource/scene
records support progression but do not independently prove visible scene
completion. The owner's account supplies the visible/audible route observations.

Both logs record a controller disconnect/failed-read pause followed by deliberate
resume. The earlier log ends after another pause; the later ends around file
selection/controller removal. Neither contains an EXIT/audio-producer-joined
sequence, so normal shutdown correctness is not established by these captures.
The separate last-stage.txt says runtime-assets-validated at 48,928.3 ms with
zero checked errors, consistent with the later log's 48,919.7 ms stage record
followed by the file write. It has no separate launch identifier. It is a startup
breadcrumb, not evidence of the furthest game scene or an orderly exit.

## Errors and reported pauses

The earlier log records one level-3 Aurora card error at original line 528:

    AURORA level=3 aurora::card Failed to open file: gczelda

Its checked-error count subsequently remains one. Name-scene records include
memory-card creation/check/error-message procedures before the new-game
milestone. The later log records no level-3-or-higher Aurora error and its
checked-error count remains zero. The owner subsequently confirmed no visible
card/save-file error and no issues saving. This resolves the requested
visible-symptom context without explaining the underlying file-open record or
proving it harmless. The owner did not separately confirm load-after-restart.
Neither log establishes save durability or controlled-failure preservation.

The owner reports pauses lasting a couple of seconds on entry to large areas
and the first appearance of effects such as explosions and smoke. Created
pipeline counts increase during play, but the captures do not measure each
pipeline build or provide timestamped first-effect/frame-time events. All
sampled heartbeat shader queues are zero; that does not rule out synchronous
work between samples. No individual pause's cause or duration is established.

This is evidence review, not a completed performance diagnosis. There is no
agent-runnable replay of the exact slow-area/effect event in this console
capture. No root-cause verdict, optimization, or green regression result is
claimed. A later performance slice needs a repeatable named event, cold/warm
cache identities and event/frame-time measurements before attributing the pause.

## Remaining #17 evidence

- A separate PC package-hash comparison can strengthen the logged candidate
  association; hardware/software, USB removal and fresh first-launch cache are
  owner-confirmed.
- Complete missing/01.01, unreadable/01.02 and invalid/01.03 stopped launches,
  checking visible rebuild/reinstall guidance and seeded saves/settings bytes.
- Install repaired/01.04, compare seeds before launch and confirm startup recovery.
- Retain the earlier card-file-open record alongside the owner's no-error,
  saving-worked observation. Normal shutdown and save/load durability remain
  unverified; do not promote this run to broader persistence acceptance.

Use the [owner checklist](../../../Startup-checklist.md). #17 stays open while
the required controlled-failure/repair evidence is outstanding. No
uncertain visual/audio defect requiring an original-game comparison was
reported; the observed timing pauses remain a separate performance limitation.
