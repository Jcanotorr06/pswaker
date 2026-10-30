# PS4 Wind Waker Port

A native PlayStation 4 port of the GameCube version of The Wind Waker.

## Language

**First playable**:
The initial playable scope covering the title screen, name entry, prologue,
Outset and its forest, with working controls and audio and saves that can be
loaded after restarting the application.
_Avoid_: Full-game validation, release candidate

**Program package**:
An installation package containing the native game program without the owner's
game data.

**Program release**:
A relocatable, data-free copy of a verified native program, with its matching
ELF and verification manifest. It is used to assemble packages away from the
developer build that produced it.
_Avoid_: Program package, which is an installation package

**Complete package**:
An owner-built installation package combining the native game program with game
data from the owner's disc image, ready to install and play on the PS4.

**Game icon**:
The artwork representing the installed game on the PS4 home screen and in the
library.

**Launch splash**:
The PS4 shell artwork shown while the application starts, until the first
successful rendered frame.

**PS4 control prompt**:
An on-screen instruction identifying the DualShock 4 control used for an action
in the current context.

**Native game menu**:
A menu supplied by The Wind Waker, such as file selection or inventory.

**Applied controls**:
The complete saved controls configuration used by gameplay, the legend and PS4
control prompts. It contains six action bindings and two camera inversion switches.

**Pending controls**:
Edits in the controls editor, including a pending restore defaults. They have no
effect until Apply succeeds.

**Port menu**:
A menu supplied by the PS4 port for settings, confirmation or input recovery.

**Release candidate**:
A tagged, versioned build of the desktop app and installer, published as a
pre-release for testing before the final release of that version.
_Avoid_: First playable, which is a scope of the game rather than a build
