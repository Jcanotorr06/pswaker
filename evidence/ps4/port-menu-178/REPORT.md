# Port-menu host checks (#178)

Implementation worktree: `C:/Users/Joseph Cano/.t3/worktrees/pswaker/t3-962b26b1`.
Task branch: `feature/178-port-menu-design`, created from the verified clean
integration branch `feature/176-port-menu` at `6b2aecb` (also then `develop`).
Commands below run from this worktree's repository root on WSL Ubuntu.

## Red / green record

The approved seam is the existing native controls integration harness. It runs
the real native reader, port-controls logic, storage/publication, prompt
resolution and game-facing input, simulating console services and the clock.
Diagnostic requests are observed at the harness's existing performance action
boundary. No private timer/helper tests or new production testing seam were added.

These focused commands established red. Each slice then passed a focused run
or the full controls suite after its implementation:

```powershell
wsl -d Ubuntu -- bash -lc 'PSWAKER_GAME_ROOT=~/.cache/pswaker/prompts-105-console-01.27 python3 -m unittest discover -s tests/ps4 -p test_controls.py -k main_menu -v'
wsl -d Ubuntu -- bash -lc 'PSWAKER_GAME_ROOT=~/.cache/pswaker/prompts-105-console-01.27 python3 -m unittest discover -s tests/ps4 -p test_controls.py -k diagnostics_entry -v'
wsl -d Ubuntu -- bash -lc 'PSWAKER_GAME_ROOT=~/.cache/pswaker/prompts-105-console-01.27 python3 -m unittest discover -s tests/ps4 -p test_controls.py -k diagnostic_measurement -v'
wsl -d Ubuntu -- bash -lc 'PSWAKER_GAME_ROOT=~/.cache/pswaker/prompts-105-console-01.27 python3 -m unittest discover -s tests/ps4 -p test_controls.py -k button_guide -v'
```

- Main menu: red on `labels == expected` (the old ten-row list); green for the
  six expected labels, wraparound, fresh navigation and complete neutral resume.
- Diagnostics entry: red because Cross stayed in Settings; intermediate red
  exposed the missing Circle return; green for entry/back, no action request,
  controller loss and restoration of the selected submenu row.
- Diagnostic actions: red on the absent measurement/phase requests; green for
  Outset, forest, transition and gameplay requests with neutral resume. The
  adapted existing failed-read scenario checks the fifth action's five-second
  delay and native input-loss path under default and custom controls.
- Guide: red compilation because `PortView` did not yet expose guide-page
  state; green for all three pages, fresh navigation, reopening on page one,
  launch confirmation and menu return.

The full native controls suite passed **34 tests** before integration with
#177. This includes existing Apply/Discard/Restore, custom mapping, publication,
prompt refresh, save failures and loss/recovery regressions. Existing Text size
checks cover persistence and held-confirmation gating; the renderer retains
its existing save-error path and adds pinned feedback.

## Final checks

```powershell
wsl -d Ubuntu -- bash -lc 'PSWAKER_GAME_ROOT=~/.cache/pswaker/prompts-105-console-01.27 python3 -m unittest discover -s tests/ps4 -p test_controls.py -v'
wsl -d Ubuntu -- python3 evidence/ps4/port-menu-178/compile-target.py /home/joseph_cano/.cache/pswaker/prompts-105-console-01.27
wsl -d Ubuntu -- bash -lc 'PSWAKER_GAME_ROOT=~/.cache/pswaker/prompts-105-console-01.27 python3 -m unittest discover -s tests/ps4 -p test_prompts.py -v'
wsl -d Ubuntu -- bash -lc 'python3 -m unittest discover -s tests/ps4 -p test_persistence.py -v'
wsl -d Ubuntu -- bash -lc 'python3 -m unittest discover -s tests/ps4 -p test_frame_pacing.py -v'
wsl -d Ubuntu -- bash -lc 'PSWAKER_GAME_ROOT=~/.cache/pswaker/prompts-105-console-01.27 python3 -m unittest discover -s tests/ps4 -p test_frame_pacing.py -k periodic_diagnostics -v'
git diff --check
git diff --cached --check
```

The target check replays the prepared build's actual compiler flags against
this worktree's `main.cpp` (including the scoped Dear ImGui helpers) and
`controls.cpp`, emitting temporary objects. It uses the pinned FreeBSD/PS4
target, Jaguar flags, SDK/libc++, Dear ImGui and Aurora headers. It does not
reconfigure, overwrite or package the prepared game.

Merged `feature/176-port-menu` at `9385e1a` (including #177). Resolved overlapping
guide, documentation and test additions while retaining both implementations
and their tests. The shortcut implementation and published wording come from
#177; #178 consumes them unchanged.

| Check | Result after integration |
| --- | --- |
| Native controls integration | 39 tests passed, no skips (16.796 s). Includes both opening paths and all existing controls journeys. |
| PS4 target objects | `main.cpp` and `controls.cpp` compiled successfully. |
| Persistence | 9 tests passed, no skips. Includes text-size failures and unrelated profile preservation. |
| Prompt contracts | 7 passed; 1 optional hosted Aurora registry/cache check skipped because `PSWAKER_REPLACEMENT_CHECK` is not configured. |
| Frame pacing | 21 passed in the full 22-test run; the native periodic-diagnostics test initially skipped without the game-root environment. Rerunning that test with the prepared game root passed, covering all 22 scenarios across the two commands. |
| Whitespace/conflict review | Working tree and staged diff checks passed; no unresolved merge markers. |

The integration run confirms that #177's hold shortcut and existing published
guide/prompt descriptions coexist with the reorganized menu and guide paging.
The recorder implementation was not changed; its existing two-minute timing and
pause/phase-change behavior remain covered by the frame-pacing regressions.

## Physical PS4 acceptance

**Pending; no physical observations claimed.** No package was produced or
installed by this task. Run the [owner checklist](../../../docs/ps4/Port-menu-checklist.md)
at both text sizes on an identified integrated candidate. This must establish
actual appearance, contrast, controller hints, long-content reachability,
neutral-release behavior, Diagnostics recovery/return and Quit. Inspect retained
Controls/input-loss presentation and unaffected startup, storage recovery,
shader preparation and shutdown/progress screens. Host behavior and compilation
do not establish physical controller or console rendering correctness.

The coordinating agent owns issue publication and labels. This task does not
push, create PRs, or close/edit issues.
