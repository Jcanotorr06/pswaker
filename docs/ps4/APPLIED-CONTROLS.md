# Applied controls and editor (#94, #95, #96, #97)

This is the saved-layout foundation for #78, after first playable. It does not
extend the accepted #18/#20 checkpoints. #95 adds button editing and Apply
persistence; #96 adds confirmed restore defaults. #97 adds independent camera
and aiming inversion, with a retained [source-path inventory](CAMERA-INVERSION.md).
Original in-game GameCube prompts remain until #79.

The [01.15 console return](../../evidence/ps4/controls-94/console-return-01.15/REPORT.md)
records owner-confirmed custom/default mappings, relaunch persistence, matching
legends, fallback warnings and fixed-input/recovery checks on build
`6d2368a5373b00387dc9`. Five extracted invalid profiles match their supplied
fixtures byte for byte. Broader update/cache/storage trials remain separately
unreported; these observations apply only to that candidate.

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
descriptions from the same snapshot. Camera integration and #79 should
consume this interface, with the generation identifying when to refresh.
The saved inversion switches initialize/update the pinned camera APIs at
publication. Scoped camera/aiming hooks consume them; raw stick axes stay fixed.

Generation 0 is the initial default snapshot. Startup publishes only after a
successful profile check. Every successful `pswaker_publish_controls(config)`
increments the generation once, even for identical values. Validation failure
or generation overflow rejects publication and leaves the old snapshot intact.
A mutex covers whole-snapshot reads and replacement: retained copies remain
stable, and concurrent consumers cannot observe bindings from one publication
with switches or a generation from another.

Apply must validate, successfully persist the complete configuration,
then publish. Discard, write failure and uncertain completion must not publish.
Pending controls never drive gameplay, the legend, camera integration or prompts.

Touchpad, port Cross/Circle/D-pad, movement/C-stick, analog triggers with the 90%
full press, analog A/B derivation, input-loss neutralization and the release gate
keep their existing behavior. Stick clicks are digital targets only.

## Button editor (#95)

Touchpad opens settings; choose **Controls...** with D-pad Up/Down and Cross.
The editor starts with the whole applied snapshot, including both saved camera
inversion switches. Each action row shows its pending and applied button.
Cross opens a picker containing all nine allowed targets. D-pad Up/Down selects,
Cross assigns, and Circle cancels the picker. An occupied target swaps the two
actions; an unused target frees the old button; choosing the current target is
a no-op. Button assignments preserve the saved inversion switches; restore
defaults resets both pending switches as described below.

Choose **Apply** to enter the apply-in-progress state. `PortSettings::setControls`
validates and serializes all six bindings and both inversion fields, preserving
text size, unrelated profile bytes and developer-section placement. One checked
settings-file replacement must succeed before the controls module publishes the
whole snapshot and advances its generation. The applied legend and gameplay
never read pending controls. A successful Apply returns to the editor, where
pending and applied values now agree.

Circle or **Back to settings** leaves a clean editor. Unsaved edits first offer
Cross **Discard** or Circle **Keep editing**. Discard copies the applied values
back into pending controls and returns to settings without publication or a
generation change. Apply failure retains both pending edits and the previous
applied generation. Its screen offers Cross **Retry** or Circle **Discard**,
with storage-repair guidance. Failure includes uncertain completion after file
replacement: disk rollback is never claimed, and Retry writes the entire pending
configuration again. Discard after uncertainty does not rewrite the disk.

Gameplay stays paused and neutral throughout all editor states. Port navigation
always uses physical D-pad/Cross/Circle, even with A, B and Start moved elsewhere.
Input loss preserves the current editor state and pending values; reconnection
alone cannot continue. Returning to settings and resuming gameplay retain the
existing explicit-confirmation and neutral-release gate.

## Restore defaults (#96)

Choose **Restore defaults...** in the Controls editor. Cross opens a separate
confirmation screen; Circle cancels it and keeps every existing pending edit.
A fresh Cross confirmation replaces only pending controls with A = Cross,
B = Circle, X = Square, Y = Triangle, Z = R1, Start = Options and both camera
inversion switches Off. The editor shows pending and applied inversion values
separately, alongside the pending/applied bindings.

Confirmation does not write settings, publish controls, advance the applied
generation or update the applied legend. **Apply** uses the same checked save
and whole-snapshot publication as any other edit. Leaving and confirming
**Discard** restores the previous applied values. Failed or uncertain Apply
keeps the pending defaults and previous applied snapshot, with the existing
**Retry**/**Discard** choices. Discard after uncertain completion makes no claim
to roll back a file that may already have been replaced.

Resetting controls preserves text size, unrelated settings, owner saves and
caches. Fixed port navigation, gameplay pause/neutralization, controller-loss
recovery and the explicit-resume release gate stay in effect during reset.

## Camera and aiming switches (#97)

Below the six action rows, Cross independently toggles **Invert camera X**
or **Invert camera Y** in pending controls. Each row shows its pending and
applied value; both default Off. A held Cross never repeatedly toggles. The
existing complete Apply/Discard/Retry and restore-defaults flows include both
switches. Successful publication updates camera and aiming together, before
gameplay resumes. See [the inventory](CAMERA-INVERSION.md) for ordinary camera,
first-person/item aiming and cannon bypass hooks and their observation limits.

## Verification

Run the installed-controls harness against a prepared game and the real-file
storage harness:

```bash
export PSWAKER_GAME_ROOT=/absolute/path/to/prepared-game
python3 -m unittest discover -s tests/ps4 -p test_controls.py -v
python3 -m unittest discover -s tests/ps4 -p test_camera_inversion.py -v
python3 -m unittest discover -s tests/ps4 -p test_persistence.py -v
```

The console harness simulates pad/system services and observes `PADStatus`,
`PortView`, the public applied lookup/legend and real temporary profiles. It
covers every action on every target, swap/free/no-op assignments, generation
publication, fixed controls and recovery under a custom layout, complete
fallback with feedback and byte-identical files, and settings read failure.
The #95 scenarios additionally drive every action/target through the editor,
observe no file/legend/publication effects before Apply, exercise leave/keep/
discard, failed sync/close/rename, uncertain completion, complete Retry and
controller loss in every editor state. The #96 scenarios start with custom
bindings and both saved inversion switches On, then exercise confirmation and
cancellation, reset/discard, reset/Apply, failed and uncertain Apply with Retry
or Discard, and input loss during reset confirmation. They compare saved profile
bytes, the complete applied snapshot/legend/generation, resumed gameplay and
synthetic save/cache preservation. The storage harness checks Apply across
a new process, controls preservation when text size changes, profile repair and
preservation, and failed/uncertain commits. These checks do not establish PS4
hardware acceptance.

Use the #94/#95/#96/#97 sections of the [controls](Controls-checklist.md) and
[persistence](Persistence-checklist.md) checklists on an identified new build.
Do not attribute historical checkpoint results to this changed binary.
