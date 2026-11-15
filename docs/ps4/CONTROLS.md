# DualShock 4 controls checkpoint (#18)

The [owner checklist](Controls-checklist.md) covers every agreed action and safe
input loss on the updated private complete package. The
[candidate report](../../evidence/ps4/controls-18/REPORT.md) identifies that exact binary.
The [returned controls review](../../evidence/ps4/controls-18/console-return-01.05/REPORT.md)
records owner-confirmed passes for mapped buttons and the three focused
trigger/menu/input-loss checks on 01.05. Its original-capture and shutdown
evidence limits remain explicit. Previous #17 progression is separate evidence.

## Controls and menus

The table below is the default layout. Saved controls loading (#94), after the
first-playable checkpoint, replaces the six action bindings through the shared
profile. See [applied controls](APPLIED-CONTROLS.md) for the versioned section,
public lookup and focused validation. The first-launch/settings legend uses
that same applied snapshot. Port-menu controls remain fixed.

| DualShock 4 | Original GameCube action |
| --- | --- |
| Cross / Circle / Square / Triangle | A / B / X / Y |
| R1 | Z |
| L2 / R2 | Analog L / R, with digital terminal click at 90% |
| Options | Start |
| Left stick / right stick / D-pad | Control Stick / C Stick / D-pad |
| Touchpad click, or hold L3 + R3 together for 500 ms | Port settings; gameplay pauses |

Supported in-game prompts use the applied PS4 controls; unconverted artwork may
still show GameCube controls. See [PS4 prompts](PS4-PROMPTS.md) for coverage.
The port Button guide appears before the
first game frame on each launch and is available in port settings. Recording
that it has been seen across launches belongs to the later persistent-settings
work. Port UI draws PlayStation symbols as lines/shapes, avoiding missing font
glyphs. Cross confirms; Circle returns/cancels. Quit has a separate confirmation;
Circle does not quit. The main menu contains Resume, Controls, Button guide,
Text size, Diagnostics and Quit. Diagnostics groups the five existing technical
actions. See the [port-menu presentation](PORT-MENU.md) and its
[owner checklist](Port-menu-checklist.md). Completing any menu action consumes
the confirmation and waits for neutral controls before handing input back to gameplay.

Both port-menu shortcuts work in gameplay and native game menus wherever the
existing Touchpad shortcut works. Touchpad opens immediately. The stick-click
shortcut starts timing when both L3 and R3 are observed held, and opens once
after 500 ms of continuous monotonic elapsed time, with Resume selected. A lone
click or shorter hold does not open it. Releasing either click, opening another
port screen, disconnecting or a failed controller read clears partial progress.
The shortcuts only open the menu; they do not close it or bypass confirmations.

Applied actions on L3 and R3 remain immediate before the menu opens, so those
gameplay actions can occur during the hold. The port does not reserve or buffer
the clicks. Opening the menu pauses gameplay and neutralizes all game-facing
input. Circle or Resume still requires every button, both sticks and both
triggers to release before gameplay resumes. The launch guide and controller
recovery still require their existing deliberate confirmation and release.
See the [#177 host evidence and owner checks](MENU-HOLD.md).

The native reader's existing 12% stick dead zone is retained, with clamped
GameCube axes and inverted Y (up positive). L2/R2 retain their full 0–255 analog
travel independently of the terminal-click bits: 229/255 is below 90%, 230/255
is the first representable sample at/above it. The initial provisional threshold
has now passed the owner's partial/full action checks on candidate 01.05.

## Input loss and installed failure check

Aurora's input hook polls the native reader. The same sampled controller state
drives the port menu and PS4 game-facing PADRead. Fixed mappings bypass desktop
remapping files and stale SDL events; SDL virtual gamepads still supply Aurora
events, controller identity and rumble. Game input is neutral outside gameplay,
including while waiting for a confirmation release. Unused controller ports
report no controller. Existing PADBlockInput remains honored.

A failed/disconnected/intercepted native read clears the sample. Input loss
pauses at the next game-frame boundary, clears every game-facing button, stick
and trigger, and stops rumble. Every new loss invalidates any earlier release.
Fresh reconnected input must become neutral, then Cross must be pressed and all
controls released again before resuming. A loss inside a port menu returns to
that menu after explicit confirmation. A loss during a pending resume still
requires explicit confirmation. Startup preparation cannot dismiss the legend.

Select **Diagnostics → Check failed read in 5 seconds** in the port menu. After the
confirmation is released, gameplay resumes and a monotonic five-second deadline
starts. One scePadReadState call then returns failure through the installed
application's link wrapper. The ordinary native reader clears held input, the
same pause gate stops gameplay, and normal reads recover without auto-resume.
This exercises active gameplay with held controls on the installed binary. It
does not emulate a faulty wireless link or establish the console driver's
behavior under every real hardware fault. Physical disconnection is a separate
required owner check. The check never alters installed content or save files.

## Build and evidence

Use the locked WSL2/Linux host and verified #15 platform. A fresh game root
preserves the earlier owner-tested build:

    bash tools/pswaker/build-game.sh "$HOME/.cache/pswaker/game-18" \
      "$HOME/.cache/pswaker/maintained-15-a" 01.05 \
      /absolute/path/to/icon0.png /absolute/path/to/splash.png

Assemble and freshly inspect using the normal
[complete-package workflow](COMPLETE-PACKAGES.md), with that root's explicit
program-stage/ELF and app version 01.05. The application identity stays
PSWK00001 / IV0000-PSWK00001_00-PSWAKERGAME00000. No game data is committed.
If the host has drifted, use the documented
[locked-host recovery](../../evidence/ps4/verification-15/REPORT.md#host-drift-and-recovery)
and restore the current package afterward; the build guard is not bypassed.

The build identity covers controls source, ordered platform patches, native
reader, linked platform inputs and toolchain. Retain the matching ELF/SELF,
package, manifests, inspection, full build-input inventories and license notices.
Native-loss results, menu transitions, explicit confirms, injected-failure
markers and one-second raw/game-facing samples go to platform.log. Existing
build/cache identity, game heartbeat and orderly audio/GPU shutdown remain.
The controls work does not complete save durability or settings persistence.

Host checks compile the actual controls translation unit with the prepared
native reader and pinned Dolphin headers. Only console services and the clock
are simulated. Tests feed raw wire samples and observe public port state and
game-facing PADStatus, including failed reads that still contain stale bytes.
They do not render the port UI, run game logic, or establish physical actions:

    export PSWAKER_GAME_ROOT="$HOME/.cache/pswaker/game-18"
    python3 -m unittest discover -s tests/ps4 -p test_controls.py -v

Use PSWAKER_REFERENCE_BUILD pointing to maintained-15-a for the full suite's
real packaging checks. Run the owner checklist on the actual installed package
before marking #18's hardware criteria complete.
