# Port menu presentation (#178 / #179)

The main port menu contains **Resume → Controls → Button guide → Text size →
Diagnostics → Quit**. Quit is separated from everyday settings and still asks
for confirmation; it does not save unsaved gameplay. D-pad Up/Down chooses,
Cross confirms, and Circle returns or resumes. Opening selects Resume.
Every destination still waits for buttons, sticks and triggers to release.

The main menu, Diagnostics, Button guide (including launch) and Quit confirmation
use a centered dark panel over a full-screen dark-blue backdrop. A blue row
highlight identifies the selection. Rows wrap and scroll to keep the selection
visible; returning to the first row reveals the information above the list.
Controller hints and release feedback stay below the scrolling content. Text
size success/failure feedback also stays visible there. **Text size** changes
between Standard and Large without closing the menu; its existing default,
profile format and save behavior are retained.

The Button guide has three short pages: applied action buttons; sticks,
triggers and camera; fixed port-menu controls. D-pad Up/Down changes pages with
the same fresh neutral-release gating as menu navigation. The guide reads the
published applied controls and shortcut descriptions. Cross continues at launch
or returns when opened from the menu. Circle returns only when opened from the
menu. Supported in-game PS4 prompts use applied controls; unconverted artwork
can still show GameCube controls.

## Diagnostics

Open **Diagnostics**, then choose one of the five existing actions. Entering
the submenu does not run an action. Circle returns with Diagnostics selected.
Performance status and explanations appear here rather than in the main menu.

| Action | Behavior after confirmation and neutral release |
| --- | --- |
| Check failed read in 5 seconds | Resume; five seconds later, fail one native controller read and enter ordinary input-loss recovery. |
| Measure Outset for two minutes | Observe the current scene with the existing `outset` sample label. |
| Measure forest for two minutes | Observe the current scene with the existing `forest` sample label. |
| Mark loading / transition start | Record the existing transition phase and resume. |
| Mark visible gameplay ready | Record the existing gameplay phase and resume. |

Measurements do not load or teleport to a scene. Their two-minute duration,
pause/phase/stage-change termination and logging remain in the existing
[frame-pacing recorder](FRAME-PACING.md). Controller loss inside Diagnostics
requires reconnection, fresh neutral input, Cross and release; it returns to
the same submenu selection.

## Presentation scope and follow-up

### Controls editing and input recovery

Controls, the binding picker, Restore/Discard confirmations, Apply progress,
Apply failure and input-loss recovery now use the same scoped panel. Each
editor row wraps its pending and applied values inside the blue selection
highlight. D-pad Up/Down keeps the active row visible, including both inversion
switches, Restore, Apply and Back. Returning to the first row reveals the
introduction. The picker identifies occupied pending buttons; assigning one
still swaps the actions. Its introduction shows the edited action's pending
and applied bindings. Unsaved-change status stays in the footer.

Restore changes only pending controls; Discard retains the applied layout.
Applying shows a paused, saving state without offering an ineffective cancel.
Failure keeps pending edits and the previous applied layout, explains uncertain
disk completion, and offers **Cross: Retry Apply** or **Circle: Discard and
return to port menu**. These actions retain the existing complete-save and
publication contracts. Prompts still refresh before the gameplay gate opens.

On information screens (Restore, Discard, Apply failure, input loss and Quit),
fixed D-pad Up/Down scrolls details by three text lines per fresh press. This
reaches long wrapped errors and instructions without a mouse. Each step clamps
to the actual body bounds, so pressing Down again at the bottom never delays
the next Up press. Hints, status and release feedback remain in the reserved
footer. Scrolling uses the same complete neutral-release navigation gate as
selection and never confirms or cancels an action.

Input loss distinguishes absent/failed controller input from restored input
awaiting release and a fresh Cross press. No confirmation hint appears while
input is unavailable; Circle never leaves recovery. Cross and a complete release
return to the interrupted destination, preserving pending edits and decisions.
The hint says Continue rather than promising to resume gameplay from an editor
or confirmation. Reconnection alone keeps gameplay paused.

`platform/ps4/game/port-menu.hpp` provides scoped Dear ImGui `Panel` and `row`
helpers. `Panel` owns local colors/spacing, a centered window, a scrolling body
and a reserved footer; call `footer()` before drawing hints. Each screen title
has its own scroll position. The destructor restores the style stack. The
native controls state machine remains responsible for selection and gating.
No renderer, settings schema or extra production testing interface was added.

Only the explicit `themedPortScreen` list in `main.cpp` opts into this theme.
Startup content checks, installation/storage recovery, shader preparation and
shutdown progress continue through the existing shared `screen` path.

See the [main-menu host evidence](../../evidence/ps4/port-menu-178/REPORT.md),
[controls/recovery host evidence](../../evidence/ps4/port-menu-179/REPORT.md) and
[physical PS4 checklist](Port-menu-checklist.md). Host checks establish native
behavior and target compilation; appearance and physical controller acceptance
remain pending.
