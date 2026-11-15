# Owner port-menu check (#178 / #176)

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
- [ ] In all four themed screens, inspect titles, wrapped long labels, complete
  page content, active rows, fixed hints, save/release feedback, comfortable row
  spacing and contrast. Check for clipped text, overlap or inaccessible content
  at the actual console output resolution and normal television distance.
- [ ] Existing Controls editor, picker, Restore/Discard confirmations, Apply
  progress/failure and input-loss screen keep their existing presentation and
  operation. Pending edits affect gameplay only after a successful Apply;
  loss/recovery preserves pending edits and confirmation destinations.
- [ ] Inspect startup content checks, installation/storage recovery, shader
  preparation and shutdown/progress screens for unintended styling changes.
  Record safely unavailable recovery/failure screens as pending.

Run the integrated shortcut checks from the independent #177 slice as well.
Keep #178/#176 open until required console evidence is recorded. Issue labels
and publication are handled by the coordinating agent; this implementation
does not modify the tracker.
