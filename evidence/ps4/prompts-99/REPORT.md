# Semantic prompt resolver and port legend (#99)

Host validation on 2026-10-31, against task base
`072b2e744ec3de9b3d88d46fc785946328deca96` (`develop`).

## Changes exercised

The public semantic resolver consumes a complete applied-controls snapshot.
The port legend, fixed instructions and port refresh adapter use it. The
existing explicit-confirmation/neutral-release boundary waits for registered
presentation adapters to finish rebuilding the applied generation.

The [coverage inventory](../../../platform/ps4/prompt-coverage.json) records port
text fallback/converted instructions and unresolved in-game surfaces. See the
[contract and source verification](../../../docs/ps4/PS4-PROMPTS.md) for interface
semantics and maintained patch-series integration.

## Verification

- Red/green resolver tracer: the new hosted test first failed because the
  resolver source did not exist, then passed for default A = Cross. The expanded
  action/context test exposed incorrect remapped port controls before fixed
  context resolution was implemented.
- Red/green installed refresh tracer: the public registration calls were
  initially unavailable. After implementing the coordinator and integrating
  the existing release gate, the multi-surface scenarios passed.
- `test_prompts.py`: passed, compiling public requests/results, resolver and
  shared configuration with Clang 21, C++23, `-Wall -Wextra -Werror`. No game
  headers, game data or GPU. Includes all 54 action/target combinations, both
  game contexts, fixed port controls, variants, press/hold, alternatives,
  missing-icon fallback and unresolved requests.
- `test_controls.py`: 30 tests passed against prepared maintained sources.
  The added scenarios observe successful Apply, unchanged generations after
  pending/discard/failed/uncertain Apply, delayed retained-presentation refresh,
  disconnect during refresh, fresh confirmation and no held-input leakage.
- Full Linux host suite with the prepared game root: **227 tests, 128 passed,
  99 skipped** for unavailable platform/GUI/tool requirements, no failures
  (94.992 seconds). This includes the installed-controls and resolver checks.
- Pyright: zero errors, warnings or informational diagnostics. Python
  compilation, maintained top-level shell syntax checks and `git diff --check`
  passed.
- Maintained PS4 CMake target `switchwaker_eboot`: passed through compilation,
  static libraries, ELF link and `eboot.bin` generation; `check-oelf` reported
  segments OK. This used an isolated copy of the cached target build with
  prepared maintained sources including shader-preparation integration.
  The initial attempt against older cached sources failed on their missing
  shader-preparation APIs; selecting the current sources resolved it.

The target compile uses the diagnostic ID `unverified-99-compile`; it is not a
packaged or independently inspected program candidate. Existing accepted
packages and retained console evidence were not updated. No disc data was used
by these checks and no game/texture assets or new raster artwork were added.

## Limits

The retained-presentation participants in the installed harness are synthetic.
Host tests cannot prove real game-picture refresh, console layout fit, icon
readability or PS4 controller behavior. Real HUD, dialogs, native menus, title,
file selection and written instructions still need later #79 adapters and
build-specific owner evidence. No new hardware pass or first-playable
acceptance is claimed.
