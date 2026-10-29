# Owner controls check — issue #18

Use the exact 01.05 package in the [candidate report](../../evidence/ps4/controls-18/REPORT.md).
Back up your completed saves/settings before updating; keep the same PSWK00001
application. Install through your usual USB workflow. Confirm PS4 Slim, firmware
9.00 and GoldHEN v2.4b18, then disconnect USB for play. This candidate needs its
own observations even though the earlier build reached Dragon Roost Island.

Record package hash/version, compiled build ID, date/run and loaded scene/save.
Keep a short result for every row below: the physical input, actual action,
expected GameCube prompt/action, scene and pass/fail. For log samples, hold each
input for at least two seconds where practical; taps can occur between samples.
Do not overwrite a real save just to test controls. Use your existing route and
items, or a separate disposable in-game slot for any otherwise unavailable action.
Mark unavailable actions pending rather than inferring them from a log.

## Mapping and port menus

- [ ] Before gameplay, see the legend and all four PlayStation symbols. Hold
  Cross during launch: it must require release and a fresh press. Continue;
  the confirmation must not also activate an in-game A action.
- [ ] Cross performs A: confirm a game menu and a contextual action.
- [ ] Circle performs B: cancel a game menu and use the available B action.
- [ ] Square performs X and Triangle performs Y: assign usable items and operate
  each; record the items and their original GameCube prompts.
- [ ] R1 performs Z: assign/use an available Z item and record the action.
- [ ] Options performs Start: open and close the original game menu.
- [ ] Left stick moves Link in each direction; right stick/C Stick behaves
  normally in the scenes that allow camera movement. Verify D-pad directions
  wherever the route uses them; record action/context, or mark unavailable.
- [ ] Lightly hold L2, then squeeze fully; repeat R2. Observe distinct partial
  analog and full-click actions in contexts where the original game distinguishes
  them (L targeting/camera behavior, and R crouch/shield where available).
  Record the action/context at partial and full travel for each trigger.
  Travel up/down around the final portion must not lose analog response.
  The initial 90% threshold remains provisional until you return these results.
- [ ] Original in-game A/B/X/Y/Z/L/R prompts remain unchanged.
- [ ] Touchpad opens port settings and freezes gameplay. D-pad Up/Down selects;
  Cross confirms. Open the legend, return with Circle, then cancel settings
  with Circle. Neither Circle action quits or performs a game B action.
- [ ] Open Quit, cancel with Circle, and continue playing. At the end of checks,
  confirm Quit with Cross; the normal application/audio shutdown must complete.
  Quitting does not create a save of unsaved progress.

## Held input loss

Use a safe position away from combat/hazards. Repeat separately while holding
movement, a face/action button, L2/R2, and a combination. Record each trial.

- [ ] Disconnect the controller (turn it off; removing a cable alone may leave
  wireless input connected). Observe the paused input-loss screen and frozen
  scene; return logs showing zero game buttons, sticks and triggers.
- [ ] Reconnect while holding Cross and the previous inputs. Gameplay stays
  paused. Release everything and wait: reconnection and release alone still
  cannot resume. Press Cross and release everything: gameplay resumes without
  carrying the held controls or confirmation into an action.
- [ ] Repeat a loss while the legend/settings or confirmation-release screen is
  open. Reconnection must not dismiss it; explicit confirmation returns to the
  appropriate menu or resumes the pending action.
- [ ] Open settings, select **Resume and check failed read in 5 seconds**, confirm
  with Cross and release everything. Once gameplay resumes, immediately hold
  movement plus a face button and both triggers. After about five seconds the
  game must pause and all game-facing input must become zero. Keep holding Cross:
  normal reads recovering must not resume. Release everything, press Cross, then
  release: resume deliberately. Repeat for individual controls if needed.
- [ ] In the returned log, preserve the scheduling and injected-failure markers,
  native-loss result, transition to input-lost, neutral samples, explicit confirm
  and transition back to game. Report a missing marker or unexpected action.
  This is a controlled failed API read; it does not reproduce every physical
  hardware read fault. Report physical disconnect observations separately.

## Return evidence

### Saved layout slice (#94, after first playable)

On a new identified build, retain the matching build ID, program/package hashes
and private profile backup. These checks do not reopen the original #18 results.

- [ ] Launch with a complete custom `[controls]` section as documented in
  [applied controls](APPLIED-CONTROLS.md). Compare all six first-launch legend
  entries with gameplay actions; reopen the legend from settings and compare.
  Across focused layouts, include all nine allowed targets and each action.
- [ ] Move A, B and Start off Cross, Circle and Options. Check movement, C-stick,
  D-pad, partial/full L2/R2, digital stick clicks, Touchpad, fixed Cross/Circle
  navigation and confirmation release. Check disconnect, reconnection and the
  delayed failed-read action; resuming must remain deliberate.
- [ ] Record the saved X/Y switch values shown in the legend. Camera/aiming
  inversion acceptance belongs to the later integration slice.
- [ ] Return observations and any failures for this exact candidate; host tests
  do not prove on-console rendering or physical game actions.

### Button editor slice (#95, after first playable)

Use a new identified build and privately back up the shared settings profile.
Record each physical input and actual game/menu behavior for this candidate.

- [ ] Open **Controls...**. Verify pending/applied labels, six action rows and
  the nine-button picker. Exercise an occupied swap, an unused target, the
  current-target no-op and picker cancellation. Pending edits must not change
  the applied legend or gameplay, and the game stays paused throughout.
- [ ] Choose Apply. Observe the progress state and matching pending/applied
  values afterward. Resume deliberately and verify all six actions against the
  applied legend. Across focused layouts, reach all nine allowed targets.
- [ ] Leave with unsaved edits: Keep editing retains them; Discard returns to
  the previous applied values. Resume with held buttons/sticks/triggers and
  verify nothing reaches gameplay until everything is released.
- [ ] Move A, B and Start off their defaults. Check fixed Touchpad, D-pad,
  Cross/Circle navigation, movement/C-stick and partial/full analog triggers.
- [ ] In a temporary profile only, exercise an Apply failure. Verify the
  previous layout stays active, pending edits remain, and Retry/Discard are
  usable. After storage repair, Retry must save the complete layout. Report
  uncertain completion honestly; no disk rollback is promised.
- [ ] Disconnect while holding mapped buttons, movement and triggers. Repeat
  in editing, the picker and confirmations, then run the delayed failed-read
  check under the applied custom layout. Reconnection alone never continues;
  fresh Cross confirmation and neutral release remain required. Pending edits
  survive loss while in the editor.
- [ ] Retain the exact build/package identity and observations. Host results
  do not establish hardware acceptance; camera integration/reset are later work.

### Logs and observations

Before another launch rotates the logs, retrieve via your existing FTP:

- /data/pswaker/logs/platform.log, platform.prev.log and last-stage.txt.
- /data/DolphinPS4/crash.log and available xmb-trace.log/boot-trace.log if there
  was an abnormal exit. Retain the report's matching ELF for fault analysis.
- Your mapping/menu/partial/full/loss observations, exact candidate/run/scene
  association, platform confirmation and any useful video of defects.

Preserve the candidate's build/cache identity in logs. Keep saves, game data,
credentials and network details private. A successful host test or a zero input
sample cannot substitute for observing the actual action, pause or menu.
