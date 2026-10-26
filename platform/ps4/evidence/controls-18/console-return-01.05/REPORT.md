# Returned controls evidence — version 01.05

The owner reports: "Controls work just as they did before, buttons remain mapped
and functional as expected." This confirms functional mapped buttons on the
returned candidate. **The focused #18 hardware checklist remains partially open.**
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
  player actions. The 90% threshold remains provisional.
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

## Remaining focused owner checks

Use the [controls checklist](../../../Controls-checklist.md) for:

- Actual partial versus full L2/R2 actions, before locking the provisional 90%.
- First-launch/settings legend, unchanged GameCube prompts, PlayStation symbols
  and Cross confirm/Circle cancel, including canceling Quit.
- Physical disconnect while holding movement, buttons and triggers; visible
  pause/neutralization; reconnect remaining paused until deliberate resume.
- The settings menu's delayed failed-read check during held gameplay input,
  followed by neutralization and deliberate resume.
- Normal Cross-confirmed Quit with audio-producer join/orderly shutdown evidence.

The owner has been asked which of these passed or remains untested. Until that
evidence is returned, mapped-button functionality is owner-confirmed and the
overall controls checkpoint remains partial. Save/settings durability and
performance acceptance are separate work.
