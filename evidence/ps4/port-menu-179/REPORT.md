# Controls-menu and input-recovery host checks (#179 / #176)

Implementation worktree: `<worktree-root>/t3-053be06e`.
Task branch: `feature/179-controls-menu-design`. The clean prepared worktree
matched integration `feature/176-port-menu` at
`f5c3db65a92d4b34498736ab933255926e8be4f8`, including #177 and #178, before edits.
The task branch was created there as explicitly requested.

## Change and approved seam

Reuses `port-menu.hpp`'s scoped panel, wrapping rows, focus and reserved footer
for the editor, picker, Restore/Discard, Apply/failure and controller recovery.
Pending/applied values, occupied picker targets, unsaved status, failure and
connection instructions are explicit. Information screens accept fixed,
fresh-release D-pad scrolling; the renderer clamps each step to actual content
bounds. This also makes Quit details scrollable. No profile schema, gameplay
binding, shortcut, persistence, renderer interface or prompt gate changed.
Out-of-scope screens still use the original shared screen path.

Tests extend the approved native controls integration harness: real native
reader, controls, settings/publication, prompt resolution and game-facing input;
external console services and filesystem failures are simulated at their
existing boundaries. No production testing seam or theme-helper tests added.
The existing public `PortView` now includes fresh information-scroll navigation
steps, alongside row/page state, so information screens can use fixed controls.

## Red / green

```powershell
wsl -d Ubuntu -- bash -lc 'PSWAKER_GAME_ROOT=~/.cache/pswaker/prompts-105-console-01.27 python3 -m unittest discover -s tests/ps4 -p test_controls.py -k failure_scroll -v'
```

Red: harness compilation reported missing `PortView::informationScroll` for
the new observable information navigation state. Green after implementing the
fresh-release scroll navigation: 1 test passed (10.019 s).

The scenario makes a pending L3 binding, forces Apply failure, checks held
navigation cannot scroll until neutral, checks one step per fresh D-pad press,
then fails a native controller read with stale held payload. Reconnected held
buttons/stick/trigger cannot confirm. A second read failure during recovery
confirmation release requires a new deliberate confirmation. Circle cannot
resume. Recovery returns to Apply failure with the same error, pending edits
and applied generation; its Cross input never retries. A separate fresh Retry
saves/publishes once, persists the complete pending layout, clears the error
and ultimately drives gameplay with L3. All existing tests retained.

## Focused checks

Run from this worktree's repository root, using the existing prepared game and
pinned WSL compiler. The target script emits temporary objects without changing
or packaging the prepared game.

```powershell
wsl -d Ubuntu -- bash -lc 'PSWAKER_GAME_ROOT=~/.cache/pswaker/prompts-105-console-01.27 python3 -m unittest discover -s tests/ps4 -p test_controls.py -v'
wsl -d Ubuntu -- bash -lc 'python3 -m unittest discover -s tests/ps4 -p test_persistence.py -v'
wsl -d Ubuntu -- bash -lc 'PSWAKER_GAME_ROOT=~/.cache/pswaker/prompts-105-console-01.27 python3 -m unittest discover -s tests/ps4 -p test_prompts.py -v'
wsl -d Ubuntu -- bash -lc 'python3 evidence/ps4/port-menu-178/compile-target.py "$HOME/.cache/pswaker/prompts-105-console-01.27"'
git diff --check
git diff --cached --check
```

| Check | Result |
| --- | --- |
| Native controls integration | 40 passed, no skips (16.449 s). Includes all existing swap, all-targets, inversion, restore, discard, Apply, failure, prompt refresh, shortcuts, Diagnostics and loss/recovery regressions. |
| Persistence | 9 passed, no skips (4.433 s). |
| Prompt contracts | 7 passed; 1 optional hosted Aurora registry/cache check skipped because `PSWAKER_REPLACEMENT_CHECK` is unset (14.217 s). |
| PS4 target objects | `main.cpp` and `controls.cpp` compiled successfully using existing pinned target flags/headers. |
| Whitespace | Working-tree and staged diff checks passed. |

Before committing, merged the latest local integration branch again:
`git merge feature/176-port-menu` reported already up to date at
`f5c3db65a92d4b34498736ab933255926e8be4f8`. Verified the current branch was
`feature/179-controls-menu-design`. The implementation commit contains this
report and the owner checklist; use that commit's SHA to identify the host
source candidate, not a console package or physical acceptance result.

## Owner acceptance and handoff

**Physical PS4 observations remain pending.** No package, installation, console
run, screenshot or physical controller result is claimed. Host tests establish
state/persistence/input-gate behavior and target compilation; they do not
establish Standard/Large appearance or actual console/controller correctness.

The updated [owner checklist](../../../docs/ps4/Port-menu-checklist.md) requires
both sizes, long wrapped content and errors, every row/target, held input,
connection-state wording, preserved edits/errors/destinations, repeated loss,
deliberate resume, prompt agreement and unaffected out-of-scope screens on an
identified integrated candidate. Safely unavailable failure/timing cases stay
pending. The coordinating agent owns tracker edits: implementation and host
checks are ready for owner validation; keep #179/#176 open and change
`ready-for-agent` to `ready-for-human` when that is the only remaining work.
This task does not push, publish a PR or modify issues.
