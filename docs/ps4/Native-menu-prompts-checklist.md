# Native menu prompts console validation (#102)

Use stock textures, USA GZLE01 revision 0, PS4 Slim / firmware 9.00 /
GoldHEN v2.4b18. Record the exact build ID, program/ELF and package identities,
applied bindings, menu/substate, observation and pass/fail. Keep captures private;
commit only asset-free observations. All checks below are pending hardware.

| Context | Default expectation | Representative remap expectation |
| --- | --- | --- |
| File selection Select/Back | Cross / Circle pictures | A=R3, B=L3: R3 / L3 pictures |
| File list Select alternative | Cross / Options: Select | A=R3, Start=L1: R3 / L1: Select |
| Main inventory/collection Close | Circle / Options: Close | B=L3, Start=L1: L3 / L1: Close |
| Inventory item slots | Square / Triangle / R1 | X=Options, Y=Cross, Z=R3: each assigned target |
| Chart comparison page controls and shadows | L2 / R2 | Still L2 / R2; arrows and shadows preserved |
| Port settings, confirmation and reconnect | Cross / Circle / Touchpad click | Still Cross / Circle / Touchpad click |

- [ ] Inspect inventory, bags, item explanations, collection, native options,
  save confirmations, dungeon map, sea-chart comparison, file list, copy/erase,
  name entry and memory-card errors. Verify context words, movement directions,
  stick animations, press/hold distinctions and native alternatives remain.
- [ ] Verify each remappable action on all nine targets where that action is
  actually presented. Include A/B/Start remapped independently, and an item action
  on Options. Fixed sticks, D-pad, analog triggers and the existing 90% terminal
  click retain their meanings.
- [ ] File list advertises both accepted Select actions. Start must not be
  advertised as confirm in copy/erase/native confirmations or name entry. The
  window Close alternative disappears in nested descriptions, bags, save/option
  dialogs and transitions; both actions really close the advertised main window.
- [ ] Check the 32x32 file-select controls through the bottom-button animations,
  the 24x24 chart controls/shadows, message icons, item slot prompts and the new
  footer. Include the two longest labels (Triangle / Options), alternate
  aspect/layout scales, neighbouring words and shadows. No clipping, overlap,
  lost text, distortion or unreadable contrast. Record actual observations,
  not just the expected values above.
- [ ] Leave each representative native menu open, enter port settings, remap
  A/B/Start and Apply. Before the first resumed native-menu frame all retained
  pictures, alternative text, messages and HUD use one applied generation.
- [ ] Repeat with pending edits, discard, failed/uncertain Apply, pending restore
  defaults and discarded restore: previous prompts remain. Successful applied
  restore changes them together before resume.
- [ ] Relaunch with saved custom controls; file-selection instructions use them
  from the first visible frame. Repeat with invalid-profile default recovery.
- [ ] Hold remapped actions, sticks and triggers across pause, Apply and
  disconnect/reconnect. Fixed fresh Cross confirmation and neutral release remain
  necessary. No held input reaches gameplay or a native menu after resume.
- [ ] Repeatedly close/reopen native menus and change scenes, then Apply: no
  stale pictures, reused item/number pictures overwritten, crashes or hangs.
- [ ] Record every `PROMPT unresolved surface=menu-*` identifier/reason and any
  still-visible literal GameCube name or embedded controller image. Identify
  exact resources locally and extend the coverage inventory. Hand baked art to
  the dedicated replacement slice. Keep play usable and report missing cases
  as untested; samples do not establish full-game coverage or #79 acceptance.
