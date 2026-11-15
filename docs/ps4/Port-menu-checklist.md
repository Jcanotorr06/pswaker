# Owner port-menu check (#178 / #179 / #176)

Physical PS4 validation is **pending**. Use an identified integrated candidate;
record package SHA-256, application version, build ID, console/firmware,
controller connection, display resolution, viewing distance, scene/save and
date. Preserve existing saves/settings. Return observations and matching logs;
do not infer visual/controller passes from host checks.

Repeat every journey at **Standard and Large** text sizes. Record actual
inputs, selected row/page, readable content and pass/fail; include photos for
clipping, contrast or spacing failures.

- [ ] Launch Button guide: centered dark panel, full dark-blue backdrop, readable
  title and fixed hints. Hold Cross during launch; release and press freshly.
  Reach all three pages with D-pad Up/Down. Held navigation changes once;
  Circle cannot skip launch confirmation. Cross and release continues without
  an in-game action.
- [ ] Open the port menu. Check the six rows in order: Resume, Controls, Button
  guide, Text size, Diagnostics, Quit. Resume starts selected; Quit has a visual
  separator. Selection uses a clear blue row highlight. Navigate both directions
  through wraparound and any scrolling; every row stays fully reachable.
- [ ] Text size changes immediately and stays in the menu. The displayed value
  and visible save feedback agree. Hold Cross: only one change occurs. Relaunch
  and verify persistence with saved custom controls unchanged. If a safe
  disposable settings-write failure is available, verify failure feedback stays
  readable and retry works; otherwise mark that physical check pending.
- [ ] Button guide opened from the menu: check all six applied bindings, camera
  switches, fixed gameplay controls and current published shortcut descriptions.
  Compare a custom applied layout with gameplay. Return with both Cross and
  Circle in separate trials; the menu keeps Button guide selected.
- [ ] Diagnostics opens without executing an action. Read the performance status
  and explanation that actions resume and measurements use the current scene.
  Circle returns with Diagnostics selected. Inspect the longest status/help at
  both text sizes; returning to the first row reveals the list introduction.
- [ ] Run each diagnostic entry in separate trials. Failed read occurs about
  five seconds after resume, neutralizes held input and enters input-loss
  recovery. Outset/forest observations use the existing two-minute sample in
  the current scene without teleportation. Check transition/gameplay markers
  and existing pause/phase-change termination using the matching logs.
- [ ] Lose controller input inside Diagnostics on a non-first selection.
  Reconnect while holding Cross, then release. Reconnection alone stays paused;
  a fresh Cross and release returns to the same Diagnostics row. Circle returns
  normally afterward.
- [ ] Quit warning is fully readable: only completed in-game saves are retained;
  quitting does not save current progress. Circle cancels and returns to Quit
  selected. At the end of testing, Cross and release exits normally.
- [ ] Resume with Cross or Circle while holding movement, triggers and buttons.
  All inputs must release before gameplay resumes; confirmation never leaks.
- [ ] In every themed screen, inspect titles, wrapped long labels, complete
  page content, active rows, fixed hints, save/release feedback, comfortable row
  spacing and contrast. Check for clipped text, overlap or inaccessible content
  at the actual console output resolution and normal television distance.
- [ ] Controls editor: same centered panel/backdrop and blue focus as the main
  menu. Reach all six actions, both camera switches, Restore, Apply and Back
  with D-pad Up/Down, including wraparound. Read each pending/applied value and
  unsaved-change status; the active row must scroll fully into view. Return to
  the first row and read the introduction. Hold D-pad: only one move occurs.
- [ ] Binding picker: read the action, pending/applied binding and occupied or
  unused pending targets. Reach all nine buttons and the longest row at each
  size. Assign an occupied button and verify the pending swap. Circle cancels
  without changing the pending binding. Gameplay/guide still use applied values.
- [ ] Toggle camera X/Y independently with fresh Cross presses; held Cross
  changes once. Restore: read every default and the explanation that only
  pending edits change. Scroll with fresh D-pad presses if needed. Circle keeps
  existing edits; Cross sets pending defaults without changing applied controls.
- [ ] Back with unsaved edits opens Discard. Read both action hints. Circle
  keeps editing; Cross discards and returns to the port menu. No held input
  bypasses either confirmation. Verify gameplay and guide retain applied values.
- [ ] Apply: observe saving/paused feedback where visible, then clean pending
  status and matching applied bindings/switches. Check gameplay, guide and
  supported PS4 prompts agree. Relaunch and verify the complete layout persisted.
- [ ] With a safe disposable settings-write failure, read the entire Apply
  error, prior-applied/pending-kept status, uncertainty explanation, retry and
  discard hints. Use fresh D-pad presses to reach the bottom, press Down again,
  then Up: it must scroll back immediately. Hints stay visible. Retry requires
  fresh Cross, saves the full pending layout and clears the failure. In a
  separate trial Circle discards edits. If unavailable, keep this check pending.
- [ ] Lose input in each of Controls, Binding (non-first target), Restore,
  Discard, Applying (if safely observable), Apply failure, main menu and
  Diagnostics. Test both disconnect and the existing failed-read diagnostic
  where feasible. Record exact destination, selection, pending edits and error.
  Unavailable timing/failure combinations remain pending, not passed.
- [ ] Recovery: absent input says reconnect/wait and offers no active Cross
  confirmation. Restored input says release all buttons/sticks/triggers, then
  fresh Cross and release. Hold Cross, movement and triggers while reconnecting:
  remain paused; Circle cannot leave. Repeat input loss during confirmation
  release. Fresh Cross and full release return to the expected screen/selection
  with pending edits/error intact; recovery Cross never assigns/restores/
  discards/retries/quits at the destination. Confirm separately afterward.
- [ ] During editing, saving, errors and recovery, game-facing actions stay
  neutral and gameplay stays paused. Resume waits for prompt refresh and full
  neutral input; reconnection alone cannot resume. Inspect long instructions
  and errors with controller scrolling at both text sizes.
- [ ] Inspect startup content checks, installation/storage recovery, shader
  preparation and shutdown/progress screens for unintended styling changes.
  Record safely unavailable recovery/failure screens as pending.

Run the integrated shortcut checks from the independent #177 slice as well.
Keep #178/#179/#176 open until required console evidence is recorded. Issue labels
and publication are handled by the coordinating agent; this implementation
does not modify the tracker.
