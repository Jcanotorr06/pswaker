# DualShock 4 controls checkpoint (#18)

The [owner checklist](Controls-checklist.md) covers every agreed action and safe
input loss on the updated private complete package. The
[candidate report](evidence/controls-18/REPORT.md) identifies that exact binary.
The [returned controls review](evidence/controls-18/console-return-01.05/REPORT.md)
records owner-confirmed passes for mapped buttons and the three focused
trigger/menu/input-loss checks on 01.05. Its original-capture and shutdown
evidence limits remain explicit. Previous #17 progression is separate evidence.

## Controls and menus

| DualShock 4 | Original GameCube action |
| --- | --- |
| Cross / Circle / Square / Triangle | A / B / X / Y |
| R1 | Z |
| L2 / R2 | Analog L / R, with digital terminal click at 90% |
| Options | Start |
| Left stick / right stick / D-pad | Control Stick / C Stick / D-pad |
| Touchpad click | Port settings; gameplay pauses |

Original in-game prompts remain unchanged. The port legend appears before the
first game frame on each launch and is available in port settings. Recording
that it has been seen across launches belongs to the later persistent-settings
work. Port UI draws PlayStation symbols as lines/shapes, avoiding missing font
glyphs. Cross confirms; Circle returns/cancels. Quit has a separate confirmation;
Circle does not quit. Settings includes Resume, the legend, a delayed failed-read
check and Quit. Completing any menu action consumes the confirmation and waits
for neutral controls before handing input back to gameplay.

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

Select **Resume and check failed read in 5 seconds** in settings. After the
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

    bash platform/ps4/build-game.sh "$HOME/.cache/pswaker/game-18" \
      "$HOME/.cache/pswaker/maintained-15-a" 01.05

Assemble and freshly inspect using the normal
[complete-package workflow](COMPLETE-PACKAGES.md), with that root's explicit
program-stage/ELF and app version 01.05. The application identity stays
PSWK00001 / IV0000-PSWK00001_00-PSWAKERGAME00000. No game data is committed.
If the host has drifted, use the documented
[locked-host recovery](evidence/verification-15/REPORT.md#host-drift-and-recovery)
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
