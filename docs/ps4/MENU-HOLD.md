# Port-menu hold shortcut (#177, spec #176)

Touchpad click immediately opens the port menu. Holding L3 and R3 together
continuously for 500 ms opens the same menu with Resume selected. Timing starts
at the first sample where both clicks are held and uses the native monotonic
clock. Releasing either click cancels progress. Leaving the eligible game/native
game-menu context or losing valid controller input also cancels progress.

Individual applied L3/R3 actions remain responsive before activation; gameplay
actions may occur during the hold. Both shortcuts only open the menu. The
existing pause, neutral game-facing input, fresh navigation release, deliberate
confirmation and full release before resume remain in effect. Pending controls
and applied controls keep their existing publication and persistence rules.

The guide's shared shortcut description and port-settings prompt results name
both alternatives and the 500 ms interval. They use text rather than inventing
one icon for two stick clicks. Native game-menu prompts retain applied bindings.
The obsolete guide claim that all original GameCube prompts remain is corrected.
This slice changes no menu theme, row order, diagnostics or settings schema.

## Host evidence

Run from the prepared worktree in PowerShell, using Ubuntu WSL and the existing
prepared Linux game sources. These checks compile the real native reader,
controls, settings/publication and prompt adapters with Clang 21; only external
console services, clock and existing filesystem fault boundaries are simulated.
The native `now_seconds()` uses `clock_gettime(CLOCK_MONOTONIC, ...)`.

```powershell
wsl.exe -d Ubuntu -- env PSWAKER_GAME_ROOT=/home/joseph_cano/.cache/pswaker/game-97-controls python3 -m unittest discover -s tests/ps4 -p test_controls.py -k test_port_menu_opens_at_500_ms -v
```

Red: the new `menu-hold-threshold` scenario aborted at the assertion that the
visible screen is Settings at exactly 500 ms (1 test, 1 failure). Green: the
same command passed after adding elapsed-time recognition (1 test, OK).
The fixture uses an exact clock origin and exact half-second endpoint, checking
499 ms first and continued held input afterward without sleeping.

```powershell
wsl.exe -d Ubuntu -- env PSWAKER_GAME_ROOT=/home/joseph_cano/.cache/pswaker/game-97-controls python3 -m unittest discover -s tests/ps4 -p test_controls.py -k test_port_menu_guide -v
```

Red: default and custom layouts failed because `AppliedControls::fixedPort()`
still described Touchpad alone (1 test, 2 failing subtests). After updating the
shared prompt result and completing native-menu adapter setup in the fixture,
the guide scenarios passed as part of the focused run below.

```powershell
wsl.exe -d Ubuntu -- env PSWAKER_GAME_ROOT=/home/joseph_cano/.cache/pswaker/game-97-controls python3 -m unittest discover -s tests/ps4 -p test_controls.py -k test_port_menu -v
```

Green: 5 tests passed before adding the launch-shortcut regression. Covered the
500 ms threshold, sparse polling above threshold, either click arriving first,
single clicks, interruption by either release, immediate custom A=L3/B=R3 input,
failed reads with stale held bytes, disconnect/reconnect, Touchpad during a hold,
non-Resume selection reset, submenu/Quit protection, and complete neutral resume.
Guide checks inspect published descriptions and actual native-menu prompt
textures with default and custom bindings. They do not run native game logic.

Final checks on 2026-11-14:

```powershell
wsl.exe -d Ubuntu -- env PSWAKER_GAME_ROOT=/home/joseph_cano/.cache/pswaker/game-97-controls python3 -m unittest discover -s tests/ps4 -p test_controls.py -v
wsl.exe -d Ubuntu -- python3 -m unittest discover -s tests/ps4 -p test_prompts.py -v
git diff --check
git merge --no-edit feature/176-port-menu
git merge-base --is-ancestor feature/176-port-menu HEAD
```

The full controls suite passed all 35 tests, including the launch-shortcut
regression and existing custom mappings, pending edits, Apply/Discard/Restore,
save failures, prompt refresh and controller-loss recovery scenarios. The prompt
suite ran 8 tests: 7 passed and the existing optional Aurora registry/GX cache
check was skipped because `PSWAKER_REPLACEMENT_CHECK` was not supplied. The
whitespace check passed. Merging the current local integration branch reported
`Already up to date`; its tip remained
`6b2aecbc053556e42dbe195375cff9c0cb04afae`, verified as an ancestor of the task
branch. No target package was built or installed. Ticket #178's concurrent
presentation/ordering changes are left for the later integration merge.

## Owner PS4 validation still required

No physical PS4 observations were collected in this worktree. Host checks do
not establish controller timing, actual game pausing or television readability.
Use a safe scene and retain your private saves/settings backup. Record the
package hash, build ID, console/controller, scene, date/run, input and observed
result for every row. Keep this ticket open until console evidence is recorded.
The integration owner should move it to `ready-for-human` when these checks are
the only remaining work; this implementation task does not edit issues.

- [ ] During gameplay and a native game menu, Touchpad opens immediately and
  L3 + R3 opens after a continuous half-second hold, with Resume selected.
- [ ] Either click alone, short combined holds and interrupted holds do not
  open the menu; a restarted hold must last a new half second.
- [ ] Apply actions to both L3 and R3. Observe each action immediately before
  activation, including during the combined hold, and compare guide/applied
  native-menu prompts. Both actions may occur during the half-second hold.
- [ ] Keep opening controls held after activation: the menu stays open and
  gameplay remains paused. Check fixed D-pad/Cross/Circle navigation, submenu
  return and Quit cancel/confirm; shortcuts must not bypass a decision.
- [ ] Resume with Circle and with Resume/Cross. Hold a click, stick or trigger
  during the release gate: gameplay stays paused until everything is neutral,
  with no confirmation or held action leaking into gameplay.
- [ ] Disconnect during a partial hold, then reconnect while holding the chord.
  Recovery still needs neutral input, fresh Cross and complete release. A new
  hold after recovery must last a fresh half second. Repeat the installed
  failed-read diagnostic separately, retaining native-loss and resume logs.
- [ ] Hold both shortcuts through launch. The guide still requires fresh Cross
  and release. Inspect the guide and shortcut text at Standard and Large sizes:
  both alternatives, two separate stick clicks and 500 ms must be readable.

Return the observations and relevant platform log alongside the exact package
identity; do not infer a hardware pass from host tests.
