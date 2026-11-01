# HUD/context prompts console validation (#101)

Use USA GZLE01 revision 0 with stock textures on PS4 Slim / firmware 9.00 /
GoldHEN v2.4b18. Record the candidate build ID, program/ELF hashes, package
identity, applied layout, scene, observation and pass/fail. Keep captures private;
commit only asset-free observations. A new candidate needs new evidence.

- [ ] Default A/B/X/Y/Z HUD pictures show Cross/Circle/Square/Triangle/R1.
  Check ordinary and alternate/parry A pictures, all three item slots, R2
  contextual actions, L2/R2 map/menu controls and all four D-pad pictures.
- [ ] Check talk, lift/pick up, climb, drop/throw, defend and weapon contexts.
  The context description stays accurate beside the named physical control.
  Check action-text transitions and both description/shadow copies. Preserve
  press/hold distinctions, accepted alternatives and directional arrows.
- [ ] Remap A→R3, B→L3 and an item action→Options. Inspect the same contexts:
  labels read upright, contrast is clear and Options/R3 fit without clipping
  or overlapping text, counters or nearby item pictures. Check HUD scaling and
  the alternate/parry A animation. Follow #79's six-actions/nine-targets matrix
  where each action is actually presented; Start's non-HUD layouts belong to
  the native-menu/title slice.
- [ ] Leave a contextual HUD visible, open port settings, remap and Apply.
  Before the first resumed game frame every retained HUD/control picture shows
  the new layout together with any open message. Repeat while a native menu
  keeps the meter present; check the meter's pictures separately from that
  menu's own still-unconverted layout. No mixture of generations is visible.
- [ ] Repeat with pending edits, discard, failed/uncertain Apply, pending restore
  defaults and discarded restore: the previous applied prompts remain. A
  successful applied restore changes prompts back together before resume.
- [ ] Relaunch with the saved custom layout, then exercise default recovery with
  an invalid saved profile: the first HUD follows the selected applied snapshot.
- [ ] Move between scenes and close/reopen menus so HUD pictures are destroyed
  and created again. Apply afterward: no stale pictures, crashes or reused
  number/item pictures painted over by a prompt.
- [ ] Hold remapped buttons, sticks and triggers during pause, Apply and
  disconnect/reconnect. Gameplay stays neutral. Fresh fixed Cross confirmation
  and deliberate neutral release remain required before resume.
- [ ] L2/R2 still distinguish partial analog input from the unchanged 90%
  terminal click. Plain HUD L2/R2 pictures impose no new travel requirement.
- [ ] Inspect logs for `PROMPT unresolved surface=hud-*`. Record exact identifiers
  and reasons, update inventory status for any encountered gap, and keep play
  usable. Report absent observations as untested. Samples do not prove full-game
  coverage or accept the unrelated #79 slices.
