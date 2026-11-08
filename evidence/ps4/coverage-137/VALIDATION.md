# Preparation validation and review (#137)

Recorded 2026-11-02 for the [prepared Windfall candidate](REPORT.md).
This records host/package checks; PS4 capture and frozen route acceptance are
pending. Issue #137 remains open with `ready-for-human`.

## Host and artifact checks

| Check | Result |
| --- | --- |
| Full Linux/WSL2 suite, once after implementation | 230 tests in 322.256 seconds, 60 environment/platform skips, no failures |
| Public seed coverage CLI, `test_outset_coverage.py` | 4 tests, no failures |
| Complete package CLI, `test_complete_package.py` | 32 tests, 1 environment skip, no failures |
| Existing initialized-renderer/frame-API check, `test_shader_startup.py` | 10 tests, no failures |
| Pyright | 0 errors, 0 warnings |
| Python compilation and maintained shell syntax | Passed |
| Document/record consistency | 207 unique scenario IDs, all 49 sea sectors, valid relative links and matching candidate/template identities |
| Actual normal game assembly | Passed with required default seed, no seed opt-in |
| Separate fresh extraction/inspection | Passed, seed/payload/manifest agreement |
| Windows handoff copy | PKG/ELF hashes match; separate WSL inspection reproduces inspection byte for byte |
| Historical cumulative snapshot | C000 reproduces #112; all 287 descriptions match D1 seed, zero historical additions |
| Source preservation | Six original source-file hashes unchanged after snapshot/comparison/assembly/inspection |

The full suite used the retained `maintained-15-a` real packaging tools and
current prepared `prompts-101-aspect` game tree. The shader checks reused the
existing #110 host-renderer executable with software Vulkan. No target source
or behavior changed, so no new target build/test seam was introduced. Existing
tests exercise the already agreed package, artifact and initialized-renderer
interfaces. Documentation/metadata additions have no new runtime contract for
a red/green test. No synthetic test is represented as physical acceptance.

The full suite's skips include platform/tool-dependent cases. Native Windows
desktop/installer suites were not run for this documentation-only change; a
Windows-path package inspected through WSL is not a native desktop test.
Exact logs are retained privately under `coverage-137`: `full-tests.log`,
`test_outset_coverage.py.log`, `test_complete_package.py.log`,
`test_shader_startup.py.log`, `pyright.log`, `compileall.log`, `C000-snapshot.log`,
`C000-membership.log`, `D1-assembly.log`, `D1-fresh-inspection.log` and
`D1-export-inspection.log`.

## Standards

No Standards findings.

The diff follows the documented privacy, branching, vocabulary and evidence
rules. It adds sanitized identities and new evidence records without modifying
archived captures, and clearly separates host preparation from pending PS4
validation. Save backups, failures, missing observations and exact candidate
identities remain explicit.

No applicable baseline code smells found in this documentation-only change.

## Spec

No Spec findings.

The preparation covers #137's inventory, fixed cohorts/checkpoints, ordinary-save
Windfall route, identified candidate, cumulative capture/provenance workflow,
raw waits, full-description membership, cold acceptance, and explicit waiver
requirements.

Physical PS4 discovery, expanded-seed analysis, and frozen acceptance remain
clearly pending, consistent with the issue's phased handoff. No unsupported
coverage claim or scope creep found.

Independent review compared the task branch with its `develop` base
`eeea9238e9dcf46904889bbd0b7c6a48318687f9`; the subsequent clarification keeps
normally learned songs distinct from debug warps and requires a warm comparison
or explicit missing-observation decision. Those documentation clarifications
were checked locally. No extra rendering or packaging behavior was added.

Review totals: Standards 0 findings; Spec 0 findings.
