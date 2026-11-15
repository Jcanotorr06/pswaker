# Port-menu integration validation (#176)

The integration branch is `feature/176-port-menu`, based on develop at
`6b2aecbc053556e42dbe195375cff9c0cb04afae`. Tickets #177, #178 and #179 and the
review fixes are merged through `d2919a8097037efe407662959fbd6171c5d062d2`.
This record accompanies the final documentation-only commit on that branch.

## Host validation

Run from the repository root in Ubuntu WSL with the existing prepared game:

```bash
export PSWAKER_GAME_ROOT="$HOME/.cache/pswaker/prompts-105-console-01.27"
python3 -m compileall -q platform/ps4 tools/pswaker tests/ps4
python3 -m unittest discover -s tests/ps4
```

At integration `6aac5c1`, the full suite ran 320 tests in 252.667 seconds:
OK, 108 skipped for unavailable optional/platform inputs. Python compilation
passed. Syntax checks (`bash -n`) passed for all eight top-level shell scripts
in `platform/ps4` and `tools/pswaker`.

After the review fixes, the complete native controls suite passed all 40 tests
without skips; see the [review-fix record](../port-menu-176-review/REPORT.md).
Earlier focused validation also passed persistence (9), prompt contracts
(7 passed, 1 optional skip), and all 22 frame-pacing scenarios; see the
[main-menu](../port-menu-178/REPORT.md) and
[editor/recovery](../port-menu-179/REPORT.md) records.

At final integration `d2919a8`, all three changed production translation units
(`main.cpp`, `controls.cpp`, `prompts.cpp`) compiled using the prepared build's
pinned PS4 compiler flags and headers. This used the compile-command replay
described in `../port-menu-178/compile-target.py`, extended for that run to
include `prompts.cpp`, with temporary output objects. No prepared build or
package was modified. This is target object compilation, not a full program
link, package build, installation or console pass. Whitespace checks passed.

## Review

The code-review skill reviewed `6b2aecb...6aac5c1` in two independent agents.

- Standards: one documented violation (personal paths in new documentation)
  and one possible repeated-screen-metadata smell. Both were addressed in
  `ebc401a`: portable paths and one shared screen-description/classification.
  The coordinator inspected that patch and corrected the accompanying theme
  documentation to name the consolidated metadata.
- Spec: no actionable findings against #176 and its three child tickets.
  A temporary probe using the pinned Dear ImGui library confirmed that all
  three guide pages fit at Standard/Large text sizes at 1920x1080 and 1280x720.
  This does not establish actual PS4 rendering or television readability.

## Owner acceptance remains pending

No physical observations, screenshots or package identity are claimed here.
Run the [integrated owner checklist](../../../docs/ps4/Port-menu-checklist.md)
on an identified candidate built from the final integration source. Include
both text sizes, every menu/editor/recovery screen, both shortcuts, custom
stick-click bindings, held-input release, Diagnostics, Quit, reconnect and
unaffected startup/storage/shader/shutdown presentation.

Keep #176, #177, #178 and #179 open with `ready-for-human` until the required
console evidence is recorded and reviewed. Passing host checks or merging
the implementation PR does not complete that acceptance.
