# HUD and contextual action prompts (#101)

Host and PS4 target-build validation on 2026-10-31, against task base
`4f2635af02f144801a0681331fa3d302d328b497` (`develop`).

## Changes exercised

The meter layout adapter resolves the applied physical PS4 controls. Separate
action-description paths retain their context textures and resolve the control
that accompanies them. Live pictures record the applied generation and refresh
at the existing before-resume boundary. The new ordered patch follows 0001–0013;
the message and HUD adapters share an independent project-owned texture cache.

See the [source verification](../../../docs/ps4/HUD-PROMPTS.md), asset-free
[coverage inventory](../../../platform/ps4/prompt-coverage.json) and
[console checklist](../../../docs/ps4/HUD-prompts-checklist.md).

## Verification

- The added installed-controls regression first failed with unresolved HUD
  pictures when HUD refresh registration was absent from the harness. After
  registration, Apply/discard/failed/uncertain Apply scenarios passed. A retained
  HUD button changes Cross to R3 before the resume gate releases gameplay; its
  synthetic context-description texture stays intact. Pending edits, discard
  and failed Apply retain Cross. Existing delayed refresh/disconnect/neutral
  release checks still pass.
- `test_controls.py`: **30 tests passed**, using real controls/storage code and
  simulated console services against freshly prepared maintained sources.
- `test_prompts.py`: **4 tests passed**, covering the public resolver, original
  artwork, message adapter and asset-free inventory schema. The shared texture
  extraction retains the existing independent GX decoder checks.
- Full Linux host suite with the prepared game root: **230 tests, 131 passed,
  99 skipped**, no failures (138.554 seconds). Skips require unavailable
  platform, GUI, tool or explicitly selected reference-build inputs.
- Pyright: **0 errors, 0 warnings, 0 informational diagnostics**. Python
  compilation, maintained top-level shell syntax and staged whitespace checks
  passed.
- Fresh pinned-source preparation applied the complete ordered game and
  game-platform patch series successfully. The maintained PS4 CMake target
  `switchwaker_eboot` compiled all 1394 build steps through ELF link and eboot
  generation. A final incremental build incorporated the final source/header
  changes and diagnostic build ID; `check-oelf` reported **segments OK**.
- Parallel code-review skill axes: **Standards 0 findings; Spec 0 findings**.

The target uses diagnostic build ID `unverified-101-compile`. Final SHA-256:

| Output | SHA-256 |
| --- | --- |
| `switchwaker` ELF | `8194fcf7162959feab175e322ed8a750a5964c4bab6449087546a84929f8950b` |
| `eboot.bin` | `2ffb8b09284ae87dcca826373c08cbe87b20cfad90a9110383afc3ee1da5411a` |

## Limits

This is a compile validation, not a packaged or independently inspected program
candidate. No existing diagnostic, package or retained console evidence changed.
The build and hosted tests use no disc data. Separate read-only local layout
inspection verified resource identifiers and dimensions; no game or pack assets,
extracted text, captures or converted outputs are committed.

Synthetic retained pictures cannot establish actual J2DPicture/GX rendering,
Options/R3 readability or spacing, animation, scene-transition cleanup, or real
HUD refresh. Those observations remain on the console checklist, tied to the
next exact candidate. Unknown action statuses are explicitly unresolved and
suppressed/reported; native-menu layouts, title/file selection, literal names
and unreviewed embedded instructions retain their separate #79 coverage gaps.
No hardware pass, full-game coverage or expanded first-playable acceptance is
claimed, and #101 remains open for console validation.
