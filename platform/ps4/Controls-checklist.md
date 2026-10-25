# Owner controls check — issue #18

Use the exact 01.05 package in the [candidate report](evidence/controls-18/REPORT.md).
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

Before another launch rotates the logs, retrieve via your existing FTP:

- /data/pswaker/logs/platform.log, platform.prev.log and last-stage.txt.
- /data/DolphinPS4/crash.log and available xmb-trace.log/boot-trace.log if there
  was an abnormal exit. Retain the report's matching ELF for fault analysis.
- Your mapping/menu/partial/full/loss observations, exact candidate/run/scene
  association, platform confirmation and any useful video of defects.

Preserve the candidate's build/cache identity in logs. Keep saves, game data,
credentials and network details private. A successful host test or a zero input
sample cannot substitute for observing the actual action, pause or menu.
