# Applied controls (#94)

This is the saved-layout foundation for #78, after first playable. It does not
extend the accepted #18/#20 checkpoints. The editor, Apply persistence and camera
integration are later slices; original in-game GameCube prompts remain until #79.

## Shared profile format

The existing startup check reads `/data/pswaker/settings.ini` after verifying
writable profile/card directories. Put the optional `[controls]` section before
`[dev]`, keeping `PSWAKER_LARGE_TEXT` outside the controls section:

```ini
PSWAKER_LARGE_TEXT=1
[controls]
version=1
A=Cross
B=Circle
X=Square
Y=Triangle
Z=R1
Start=Options
invert_camera_x=0
invert_camera_y=0
[dev]
```

All nine keys are required when the section exists. Action targets are
`Cross`, `Circle`, `Square`, `Triangle`, `L1`, `R1`, `L3`, `R3` or `Options`.
Each action has exactly one target; no two actions share a target. Key/target
spelling is case sensitive; surrounding whitespace, CRLF, blank lines and full
lines beginning with `#` or `;` are accepted. Unknown keys, duplicate keys or
sections, shared targets, reserved/unknown targets, incomplete values, malformed
entries and unsupported versions reject the entire section.

An absent section silently selects all defaults. An invalid section selects all
defaults with a visible reason in the first-launch/settings legend and settings
screen. Startup never rewrites the settings file, even on fallback. Read failures
and directory/write-probe failures still block at the existing storage recovery
screen; invalid text size still fails that check. Changing text size preserves
the controls section and unrelated profile bytes.

## Consumer interface

`controls-config.hpp` owns the complete `ControlsConfig` value, defaults,
validation, assignment with swap/free/no-op semantics, versioned parsing and
serialization. Serialization returns one complete section; it performs no I/O.

`pswaker_applied_controls()` in `controls.hpp` returns a copy of one complete
`AppliedControls` snapshot: six bindings, independent saved camera switches,
fixed gameplay/port-menu descriptions and a generation. Gameplay resolves
bindings from this lookup. The legend renders `snapshot.legend()` and the fixed
descriptions from the same snapshot. Later camera integration and #79 should
consume this interface, with the generation identifying when to refresh.
The saved inversion switches are published here; this slice does not change
camera or aiming paths, or negate raw stick axes.

Generation 0 is the initial default snapshot. Startup publishes only after a
successful profile check. Every successful `pswaker_publish_controls(config)`
increments the generation once, even for identical values. Validation failure
or generation overflow rejects publication and leaves the old snapshot intact.
A mutex covers whole-snapshot reads and replacement: retained copies remain
stable, and concurrent consumers cannot observe bindings from one publication
with switches or a generation from another.

Future Apply must validate, successfully persist the complete configuration,
then publish. Discard, write failure and uncertain completion must not publish.
Pending controls never drive gameplay, the legend, camera integration or prompts.

Touchpad, port Cross/Circle/D-pad, movement/C-stick, analog triggers with the 90%
full press, analog A/B derivation, input-loss neutralization and the release gate
keep their existing behavior. Stick clicks are digital targets only.

## Verification

Run the installed-controls harness against a prepared game and the real-file
storage harness:

```bash
export PSWAKER_GAME_ROOT=/absolute/path/to/prepared-game
python3 -m unittest discover -s tests/ps4 -p test_controls.py -v
python3 -m unittest discover -s tests/ps4 -p test_persistence.py -v
```

The console harness simulates pad/system services and observes `PADStatus`,
`PortView`, the public applied lookup/legend and real temporary profiles. It
covers every action on every target, swap/free/no-op assignments, generation
publication, fixed controls and recovery under a custom layout, complete
fallback with feedback and byte-identical files, and settings read failure.
The storage harness checks relaunch in a new process and controls preservation
when text size changes. These checks do not establish PS4 hardware acceptance.

Use the #94 sections of the [controls](Controls-checklist.md) and
[persistence](Persistence-checklist.md) checklists on an identified new build.
Do not attribute historical checkpoint results to this changed binary.
