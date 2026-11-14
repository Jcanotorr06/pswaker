# Embedded instruction console validation (#103)

Use stock textures, USA GZLE01 revision 0, PS4 Slim / firmware 9.00 /
GoldHEN v2.4b18. Record exact build ID, ELF/program/package hashes, applied
bindings, scene/substate, observations and pass/fail. All items are pending
hardware. Keep asset-bearing captures private; commit only metadata and findings.

- [ ] Title default layout: the embedded instruction names Cross, Circle and
  Options. Each really starts the title transition. Surrounding logo, gradient,
  layout, alpha/pulse and animations remain intact.
- [ ] Title with A=R3, B=L3, Start=L1: names read R3, L3 and L1; each works.
  Check Triangle, Options and the longest three-name combination for fit,
  contrast, correct aspect, no clipping or overlap, and readability at normal
  viewing distance. Port menus still use Cross/Circle/Touchpad click.
- [ ] Leave the title visible, open port settings, Apply a remap and resume.
  The first resumed frame uses only the new applied generation. Repeat with
  pending edits, discard, failed Apply, restore defaults discarded and applied.
- [ ] Relaunch with saved custom controls and with invalid-profile default
  recovery. The first visible title instruction matches the applied layout.
- [ ] Hold buttons/sticks/triggers over pause, Apply and disconnect/reconnect.
  Fixed fresh Cross confirmation and neutral release still protect resume.
- [ ] Leave/re-enter the title repeatedly, including after remaps: no stale
  replacement, reused archive pointer, corrupted logo, hang or crash.
- [ ] Record every `PROMPT unresolved surface=embedded-title` identifier/reason.
  Review further embedded menu/tutorial images and shared-atlas regions locally;
  add exact identifiers/status to the inventory. Preserve non-controller regions,
  alternatives, direction/animation and trigger travel before converting them.
  Leave untranslatable cases unresolved and report usable-play observations.

Samples do not establish full-game coverage or stock/HD transition behavior.
