# Integrated PS4 prompt validation (#106)

Use **PS4 Slim / firmware 9.00 / GoldHEN v2.4b18**, **USA GZLE01 revision 0**,
stock textures first. This is post-first-playable #79 work; #12/#18 acceptance
and historical results retain their original scope. Every physical check below
is pending until the owner returns observations for the installed binary.

The [candidate record](../../evidence/ps4/prompts-106/candidate.json) identifies
the prepared complete package, version 01.27, build `a21e4fc7a440bcaa3359`.
It reuses the #105 candidate unchanged, including its matching ELF. Its
[coverage review](../../evidence/ps4/prompts-106/coverage-review.json) records
known gaps. Do not credit earlier console results to this build.

## Before installation and each run

- [ ] Privately back up `/data/pswaker/settings.ini` and `/data/pswaker/saves/`.
  Preserve actual progress. Use a spare save slot for destructive native-menu
  checks; do not erase ordinary progress or the whole profile to test recovery.
- [ ] Hash the private `.pkg` and matching ELF against `candidate.json` and
  `SHA256SUMS.txt`. Install the complete package through the PS4 package installer;
  confirm version 01.27 / title ID `PSWK00001`. Record the actual startup build ID
  from the matching log block. A mismatch requires a new candidate record.
- [ ] Copy the [observation template](../../evidence/ps4/prompts-106/observations.json)
  to a new private run file. Fill `runs` with run ID, UTC time, installed identity,
  console/content identity, texture mode, applied bindings and generation (or
  explicitly state that generation was not observable), scene/menu/message ID,
  text/aspect settings and owner confirmation. `expected_candidate` is a reference,
  not an assertion that installation occurred. Give each observation its run ID.
- [ ] Record actual input, applied legend, icon instruction, written name and
  resulting action separately. A pass needs an observation and owner confirmation;
  expectations alone are not evidence. Use PASS, FAIL, BLOCKED or UNTESTED. If a
  context is unavailable, retain the reason and leave it pending. Append new runs
  and failed attempts; never overwrite archived evidence with a later success.

## 1. Stock defaults and representative surfaces

Apply complete defaults successfully. A/B/X/Y/Z/Start should use
Cross/Circle/Square/Triangle/R1/Options. Verify actual actions, the applied legend
and all instructions agree. Sticks, D-pad, L2/R2 and port controls stay fixed.

| Surface | Focused contexts | Observe |
| --- | --- | --- |
| HUD/context | Outset talk, pickup/lift, climb, drop/throw; weapon/defend/parry when reachable; X/Y/Z item slots | Upright round symbols, readable contrast, context words and both shadows; no overlap, squash or clipped labels |
| Dialog/tutorial | Outset telescope tutorial (message 3008); written/paper paths 816, 817, 1108 when reachable; directional/stick picture tags | Text/icon agreement, press/hold, accepted alternatives, page progression, direction and animation; preserve instruction meaning |
| Native menus | Inventory, bags, collection, options, save confirmations, dungeon/sea charts | Applied A/B/X/Y/Z/Start where accepted; L2/R2 chart controls and shadows; no Start-confirm instruction where Start is not accepted |
| File selection | Select/back, list alternative, copy/erase confirmation, name entry and error instructions | Applied A or Start selects only where both are accepted; nested confirmations retain their actual controls; preserve saves |
| Title/start | First visible instruction, introduction skip, ready-to-start transition, repeated title entry | All three accepted A/B/Start alternatives work; retained pulse and surrounding logo/model/material art remain intact |
| Port menus | Settings, keep/discard, Apply feedback, reconnect/resume | Fixed Cross/Circle/Touchpad click and D-pad, including with gameplay A/B/Start remapped |

- [ ] Complete each surface above with normal text, then check long labels at
  normal viewing distance with alternate text size/aspect settings. Follow the
  slice checklists for exact contexts: [HUD](HUD-prompts-checklist.md),
  [native menus](Native-menu-prompts-checklist.md), [title](Title-prompts-checklist.md),
  [embedded artwork](Embedded-prompts-checklist.md) and
  [written instructions](Written-instructions-checklist.md).
- [ ] Distinguish left/right stick movement from L3/R3 clicks, all available
  directional/rotating/oscillating instructions, D-pad directions, plain L2/R2
  presses and partial/full trigger travel. Check the unchanged 90% terminal click.
  L2/R2 are fixed analog controls, not remap targets. If no representative
  partial/full-travel instruction is found, report that coverage gap explicitly;
  a plain trigger icon or host resolver pass does not close it.

## 2. Six actions on all nine targets

Apply each full layout below in the controls editor. Assigning an occupied target
swaps bindings: verify the **entire applied legend** after editing and Apply.
Keep both inversion switches at defaults for this matrix. Each action traverses
all nine targets once; the 54 cells in the observation template remain UNTESTED
until an actual action and corresponding in-game instruction are observed.

| Layout | A | B | X | Y | Z | Start |
| --- | --- | --- | --- | --- | --- | --- |
| M0 | Cross | Circle | Square | Triangle | L1 | R1 |
| M1 | Circle | Square | Triangle | L1 | R1 | L3 |
| M2 | Square | Triangle | L1 | R1 | L3 | R3 |
| M3 | Triangle | L1 | R1 | L3 | R3 | Options |
| M4 | L1 | R1 | L3 | R3 | Options | Cross |
| M5 | R1 | L3 | R3 | Options | Cross | Circle |
| M6 | L3 | R3 | Options | Cross | Circle | Square |
| M7 | R3 | Options | Cross | Circle | Square | Triangle |
| M8 | Options | Cross | Circle | Square | Triangle | L1 |

- [ ] For every cell, record the tested action/context, physical input, resulting
  action, applied legend and in-game icon/name. Use HUD/item assignment for X/Y/Z,
  contextual gameplay/dialogs for A/B and native menus/title/written instructions
  for Start. Do not mark an absent written/icon surface as observed; state its
  absence and add another reachable context where needed.
- [ ] With M6 or another recognizable saved layout, check native-menu versus
  fixed port controls. Remapping gameplay A/B/Start must never relabel the port's
  Cross/Circle/Touchpad prompts. Recheck fixed sticks, D-pad and analog triggers.
- [ ] Add A=Triangle, B=Options, X=Cross, Y=Circle, Z=L3, Start=Square as the long
  title-label case. Check Options, Triangle, L3 and R3 in HUD, menus and written
  text too. A readable accurate text fallback counts as fallback, not icon coverage.

## 3. Apply and retained instructions

Repeat the following flows separately with (a) affected HUD pictures visible,
(b) an already-open, partly typed dialog with adjacent icons/written names,
(c) a native menu/file-selection instruction and (d) the title instruction.
Record one observation per surface and flow, including the first resumed frame.

| Flow | Required observation |
| --- | --- |
| Pending edit, then Back/keep editing | Previous applied input, legend and prompts remain; returning to edits preserves the pending choice |
| Back/discard | Previous layout remains everywhere; no pending binding becomes visible |
| Successful Apply | All visible pictures, names, alternatives and later instructions use the new layout before gameplay resumes; no mixed generations |
| Failed Apply, then Retry after repair | Previous applied layout remains; feedback and pending choice are retained; repaired successful Retry publishes the complete layout |
| Uncertain Apply, then Retry | Record persistence feedback and actual selected layout; do not infer publication from the button press; only confirmed successful publication changes prompts |
| Restore defaults, then discard | Previous custom layout remains everywhere |
| Restore defaults, then Apply | Complete defaults replace custom prompts together before resume |

- [ ] Follow the temporary-profile-only failure check in the
  [controls checklist](Controls-checklist.md). Keep any profile backup
  private. Do not damage saves or add production failure switches. If a real
  failed/uncertain Apply cannot be safely produced on this candidate, mark that
  flow BLOCKED with its reason; simulated host failures are supporting evidence.
- [ ] If refresh waits or retries, verify gameplay stays paused with neutral
  inputs. Record the feedback, duration, old/new instructions and outcome. Reopen
  dialogs/menus and change scenes afterward: later instructions agree, with no
  stale/reused picture, lost typing progress, hang or crash.

## 4. Relaunch and complete-default recovery

- [ ] Save M6 through successful Apply, fully close the application from the PS4
  shell, then relaunch. The first title, file-select, HUD and written instructions
  follow M6 and agree with actual inputs and the legend. Record a new run.
- [ ] With the application closed and the profile backed up, separately exercise
  a missing controls section and an invalid/incomplete controls section using the
  controls checklist. Preserve other settings and saves. Relaunch each time and
  record recovery feedback: all six bindings and both inversion switches must
  use complete defaults, with prompts matching from the first title instruction.
  No mixture of custom/default values and no separate prompt persistence.
- [ ] Restore the private profile backup with the application closed; relaunch
  and confirm real progress and the selected applied layout are preserved.

## 5. Disconnect, refresh and deliberate resume

- [ ] With M6 applied, independently hold a mapped action button, each stick and
  each trigger while disconnecting. Observe pause and neutralization. Reconnect:
  no automatic resume. Require a fresh **fixed Cross** confirmation followed by
  release of all controls to neutral; no stale action or menu input afterward.
- [ ] Repeat with a port edit pending, after Apply and during any observable
  refresh wait. Disconnect cancels resume; reconnect still requires fresh Cross
  and neutral release. Held inputs must not escape when refresh finishes.
  If refresh is too fast to interrupt, retain that limit rather than claiming it.

## 6. Coverage defects, evidence return and #80

- [ ] Record each accurate text fallback and every missing/misleading control by
  inventory/resource identifier, context and applied layout. Check the nine known
  unsupported message IDs 18, 23, 37, 49, 54, 60, 96, 134 and 612 when reachable:
  their neutral unavailable notice should be readable and dismissible. They remain
  unresolved even if suppression is usable. Record absent encounters as UNTESTED.
- [ ] Audit native menu/name-entry embedded images, literal instructions, shared
  atlases and unaudited title/model/material resources locally. Keep identifiers
  and converted/text-fallback/unresolved status only. Preserve non-controller
  atlas regions. New defects extend the inventory; existing unresolved entries
  cannot be promoted merely because representative samples passed.
- [ ] Before another launch rotates logs, retain privately the matching BEGIN/build
  block, `/data/pswaker/logs/platform.log`, `platform.prev.log`, `last-stage.txt`
  and `/data/DolphinPS4/crash.log` if present. Associate coverage reports and
  failures with run IDs. Retain raw logs/captures locally; commit only reviewed,
  asset-free observations without game text, paths or personal/network details.
- [ ] Owner confirms the installed identity, individual observations, unresolved
  gaps and limits in a new evidence record. Keep #106 open with `ready-for-human`
  until that evidence is reviewed and required checks are complete. Current known
  gaps prevent declaring affected surfaces complete; samples never prove full-game
  visual coverage.

Review hosted resolver, installed-controls and precedence-rule results in
[the evidence record](../../evidence/ps4/prompts-106/README.md) as supporting
evidence only. The exported [prompt-over-pack rule](EMBEDDED-PROMPTS.md#public-precedence-rule-for-80)
reserves prompt ownership across pointer, exact source, palette-wildcard and
texture-wildcard matches, including cache invalidation and selective removal.
Actual HD loading, conflicting-pack artwork, fallback and loading-transition
observations belong to #80. This stock-mode handoff establishes no HD acceptance.
