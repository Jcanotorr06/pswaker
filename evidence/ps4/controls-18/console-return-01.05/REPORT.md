# Returned controls evidence — version 01.05

The owner reports: "Controls work just as they did before, buttons remain mapped
and functional as expected." This confirms functional mapped buttons on the
returned candidate. In a follow-up, the owner explicitly confirms **all three
requested focused checks were tested and passed**: partial/full L2/R2 actions,
touchpad settings/legend with Cross confirm/Circle cancel, and held-input
disconnect/reconnect plus the delayed failed-read check. This validates the
current 90% trigger threshold through owner-observed actions on candidate 01.05.
No new binary or control changes are indicated by this report.

## Candidate association and retained originals

platform.log contains one BEGIN record for build d532217ac6a319ff6ad3 and an
embedded complete-package manifest for version 01.05. Its entire program/image
objects and content ID match the [candidate inspection](../inspection-01.05.json),
including SELF 056683cd1020158aa02063500699f99d291b4bad9ef061e860883a9c033b0a9b
and ELF 7614549b1f2e5b0aa636f8858daef6d90c56e967fd86095aa6d941ba5d3743f8.
The expected package SHA-256 is
8e572e447d5da87d8026911602119cbdcb898c93f10485b5ee64a315f08d3c5c.
The logged manifest associates the run with the candidate; it is not a fresh
console hash of the running executable or entire package.

platform.prev.log contains one BEGIN record for the older build
6ebc07987fe3b6c6064a, version 01.04. It is retained as previous-launch context and
is not counted as a second run of the controls candidate. The BEGIN platform
string names the expected Slim/9.00/GoldHEN v2.4b18 target; it does not detect
or independently reconfirm the hardware/software version.

Original files remain unchanged in the supplied private logs directory.
[original-files.json](original-files.json) records byte sizes, SHA-256 values and
line counts for all three files. [summary.json](summary.json) records parsed
identities, stages, events and sampled-input coverage with original line numbers.
[selected-records.txt](selected-records.txt) retains the relevant original lines.
[owner-observations.json](owner-observations.json) keeps the owner's statement
separate from inferred log evidence and unreported checklist results.

## Observations from the candidate log

- Startup records no preexisting cache files for this build. Installed-image
  validation completes at 40,561.2 ms; runtime assets validate at 40,763.8 ms.
  Allocated internal rendering is 1280x720; output is 1920x1080.
- All 146 logged heartbeats report zero checked errors. The final heartbeat
  is at 780,460.7 ms, with 299 created shaders and no queued shaders. No
  level-3/4 Aurora errors, EXIT or SHUTDOWN records occur in this capture.
  These counters do not certify performance or an orderly close.
- Legend confirmation and transition into gameplay appear at original lines
  501–502. There are 749 sampled input records: 12 in the legend, 718 in
  gameplay and 19 in input-lost. Every one of the 31 paused samples has zero
  game-facing buttons, both sticks and both triggers.
- Gameplay snapshots include Cross/A (4 pressed samples), Circle/B (3),
  Triangle/Y (2) and R1/Z (1). Their raw/mapped bits agree in every sampled
  record. Square/X, Options/Start and D-pad presses do not occur in the
  one-second snapshots; short taps can fall between samples. Their absence
  does not contradict the owner's broader confirmation of functional buttons.
- Left-stick axes and right-stick X span -127 to 127. Right-stick Y spans
  0 to 127 in these snapshots. This establishes sampled activity, without
  demonstrating every visible direction or camera/menu action.
- L2 has 6 nonzero partial samples below the click threshold and 2 terminal
  samples; its maximum sampled analog value is 236. R2 has 12 nonzero partial
  samples and 11 terminal samples, reaching 255. All sampled digital click
  bits agree with the initial threshold (first representable sample 230/255).
  This shows separate analog and digital values reaching the game-facing
  boundary, but does not confirm the original game's distinct partial/full
  player actions by itself. The owner's follow-up separately confirms those
  actions passed at the current 90% threshold.
- At line 1985 the state changes from game to input-lost with connected=0,
  followed by a controller-removal record and 19 neutral input-lost samples.
  The last preceding gameplay sample is neutral except for an unmapped raw
  system-button bit. There is no held movement/button/trigger sample immediately
  before this loss, no captured reconnect or explicit resume, and no native-loss
  result explaining its cause. The capture cannot distinguish physical
  disconnection, system interception or another failed-read path here.
- There are no settings/quit transitions or delayed check scheduling/injection
  markers. Their absence establishes only that these captures do not document
  those paths. No visible pause, menu-symbol or orderly-exit verdict is inferred.

last-stage.txt identifies the same build and runtime-assets-validated at
40,772.4 ms with zero checked errors, consistent with the candidate's startup
stage record followed by its file write. It is a startup breadcrumb, not a
record of the furthest gameplay scene or final lifecycle state.

## Owner-confirmed focused checks and capture limits

The owner answered the bundled follow-up question with: "Yes to all three,
all three were tested and passed." Record these as owner-observed passes:

- Actual partial versus full L2/R2 actions at the current 90% threshold.
- Touchpad settings and legend with Cross confirm/Circle cancel.
- Physical disconnect while holding movement, buttons and triggers; visible
  pause/neutralization; reconnect remaining paused until deliberate resume.
- The settings menu's delayed failed-read check during held gameplay input,
  followed by neutralization and deliberate resume.

The supplied log still does not capture the settings/reconnect/check sequences;
the follow-up supplies their pass verdict, not additional trace records.
Per-action scene/item details and individual symbol appearance were not
separately described. Normal Cross-confirmed Quit and audio-producer join/orderly
shutdown were not included in the three-part question and remain unverified by
these returned observations/logs. No such pass is inferred. The original
[controls checklist](../../../../docs/ps4/Controls-checklist.md) remains the detailed reference.
Save/settings durability and performance acceptance are separate work.
