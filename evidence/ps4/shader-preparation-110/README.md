# Shader preparation candidate (#110)

Recorded 2026-10-31. Host implementation/build/package evidence only. No PS4
presentation-timing or Outset hitch-elimination result is claimed. The console
handoff is in [shader preparation](../../../docs/ps4/SHADER-PREPARATION.md).

## Retained private candidate

The selected locked host built and inspected game program 01.20 against the
unchanged maintained platform. Complete-package assembly explicitly selected
the existing validated 287-description asset through `--assembly-assets`.
Assembly freshly extracted the resulting package; a separate `inspect` call
then repeated the inspection successfully.

| Identity | Value |
| --- | --- |
| Program build ID | `9f79516d60da618241a1` |
| Program version | `01.20` |
| EBOOT SHA-256 | `ac4e2bb217608637b5dd9be430f1f307112286d4c0e112a547b961afcafe690c` |
| Matching ELF SHA-256 | `06417d1c34cdf58b70baee9e679f83e77899b12405ce47f8a9b12bf578790f90` |
| Package filename | `IV0000-PSWK00001_00-PSWAKERGAME00000.pkg` |
| Package SHA-256 | `dc204e8fec1ec11913ba3b3902855f45c0780d502296272555f6ac49521cfe07` |
| Seed SHA-256 | `7e3f8527203dc488b5ae646904c986ac596d7d4017db45a0fcb18ae29de51dc1` |
| Seed bytes | 1,200,128 |
| Seed descriptions | 287: one clear/version 5/8-byte configuration; 286 GX/version 13/2772-byte configurations |
| Asset manifest SHA-256 | `e8d4b523aa45f58e272ccde4c258d76388200e26f28a9060b804f9969b4493fb` |
| Assembly report SHA-256 | `db90a9246394fb322947dd4bb81d3729107ff6a0e366edcb79ced136d6956501` |
| Inspection report SHA-256 | `e63568d447d4a3ed3e77a3adde4d54e7a9321c0eb7cb753f5058f1952d9e5950` |

The complete package, matching ELF, assembly/inspection reports and command/tool
records are retained as `shader-preparation-110-01.20` under the existing private
artifact root. Its build and validation records are retained as `shader-110`
under the existing build-cache root. The unchanged seed asset remains
`performance-22-seed-01.13`; the maintained platform is `maintained-15-a`.
Actual images, seeds, packages and personal host paths are excluded from git.

Independent reinspection, with those private roots selected:

```bash
python3 tools/pswaker/complete-package.py inspect \
  "$PRIVATE_ROOT/shader-preparation-110-01.20" \
  --platform-root "$PLATFORM_ROOT"
```

## Checks and limits

- The focused real-Vulkan suite passed all ten tests. It exercises the actual
  initialized game renderer, real synthetic SQLite seeds and frame pumping.
  Only the driver boundary is delayed/faulted or observed for real cache hits.
- Coverage includes pending creation, partial progress in configuration units,
  completion, missing/empty/corrupt/incompatible seeds, null and reported driver
  creation errors, compatible retained-cache hits, fresh-cache preparation,
  save/settings sentinels, and synchronous uncovered work with wait accounting.
  Two tests complete the gameplay handoff and verify later creation failures
  surface through fatal handling rather than permanently suppressing draws.
- Final reference-enabled WSL suite passed 221 tests in 305.639 seconds, with
  60 environment/platform skips and no failures. It includes both new gameplay-
  failure regressions. The earlier run passed 219 tests with the same 60 skips.
- Pyright reported zero errors or warnings. Python compilation, syntax checks
  for all eight maintained shell scripts, native Git whitespace checks and
  the PS4 target build/ABI/program inspection passed.
- Standards review: zero findings. Spec review identified an overly broad error
  capture that could hide gameplay creation errors. The explicit handoff and
  two runtime regressions repaired it; re-review found no remaining findings.

The first TDD compile failed because the renderer had no preparation-status API.
An initial driver fault fixture removed a shader module and crashed with the
release renderer's validation disabled; it was replaced with Dawn error
injection at the same driver boundary. The initial target staging attempt
correctly rejected source changes made while its build was running. The final
build reran preparation/identity/compilation/staging and inspection successfully;
the earlier attempt's log remains private. Neither failed attempt is counted
as a passing console result.

The tests verify the renderer status consumed by startup; they do not observe
the installed PS4 preparation/error screen. Console verification must record
that screen, full startup/preparation cost including overlapping work, the final
drain separately, cache lifecycle and save/settings preservation. The current
287 descriptions remain a starting point for the final action-verification
work under #107; their count does not establish roll/swim/sword coverage.
