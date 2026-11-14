# Stock-mode title/start console validation (#104)

Run on PS4 Slim / firmware 9.00 / GoldHEN v2.4b18, USA GZLE01 revision 0,
with stock textures. Record exact build ID, program/ELF/package hashes, applied
layout and generation, scene/substate, observations and pass/fail. The prepared
[observation record](../../evidence/ps4/title-prompts-104/observations.json)
contains expected instructions and pending observations, not console passes.
Keep captures and game-bearing logs private. Add a new evidence record for the
installed build; do not overwrite archived observations.

- [ ] Default startup: title says `PRESS CROSS / CIRCLE / OPTIONS` on its first
  visible instruction. Each alternative skips the introduction and starts the
  transition when the title is ready. Check fresh presses, not held input.
- [ ] Saved custom startup after full relaunch: A=L3, B=R3, Start=Circle gives
  `PRESS L3 / R3 / CIRCLE`; Circle performs Start. Options performs the custom
  action assigned to it, not an assumed Start. Verify the applied legend agrees.
- [ ] Invalid or incomplete saved controls: all controls recover together to
  defaults, feedback is present, and the first title instruction uses Cross,
  Circle and Options. No custom/default mixture or stale title appears.
- [ ] Longest-label layout: A=Triangle, B=Options, Start=Square. Check the full
  `PRESS TRIANGLE / OPTIONS / SQUARE` instruction at normal viewing distance,
  with no clipping, overlap or confusing character shapes. Compare default and
  short L3/R3 labels for contrast, fit and aspect ratio.
- [ ] Check title background, copyright, both logo layers, subtitle/glint model
  materials, ship, particles and introduction/pulse animation before and after
  entering the title. None of these surrounding surfaces should be replaced.
- [ ] Retain the visible title, open port settings and Apply A=R3, B=L3,
  Start=L1. The first resumed frame says `PRESS R3 / L3 / L1` consistently with
  the legend. Repeat pending edits, discard, failed Apply, defaults discarded
  and defaults applied. Only successful publication changes the instruction.
- [ ] Hold buttons/sticks/triggers over pause/Apply and disconnect/reconnect.
  Fixed fresh Cross confirmation, fixed port prompts and neutral release still
  protect resume; no held input starts the game. Repeat with Start remapped.
- [ ] Re-enter the title repeatedly before/after Apply. No stale generation,
  reused archive-pointer replacement, corrupted artwork, hang or crash appears.
- [ ] Record every `surface=title-layout`, `surface=embedded-title` and
  `surface=embedded-texture` coverage defect. With local fault injection, confirm
  missing/wrong `pres`, unexpected texture and registration/upload failures do
  not expose a misleading original instruction; record usability and retry.
  Report unreviewed title/model/material instructions by resource identifier,
  without guessing a binding. Unresolved paths prevent claiming that coverage.

All physical observations are pending. Samples do not prove full-game coverage,
other language/revision coverage, or HD pack behavior (#80).
