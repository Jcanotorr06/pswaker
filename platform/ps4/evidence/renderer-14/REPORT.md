# Renderer reconciliation evidence — issue #14

One absent-root Linux/WSL2 clean cross-build produced and inspected the disc-free
`PSWK00010` version `01.04` package. Build ID: `60975dcf4480aa914369`.
All 99 maintained input files match the frozen source and compiled package identity.
This original build record covers renderer preparation and host evidence; the
binary was untested on a console when it was written. Returned owner evidence
from 2026-10-24 is reviewed separately in the [01.04 console report](console-01.04/REPORT.md).

## Build and retained outputs

```bash
JOBS=12 bash /home/joseph_cano/.cache/pswaker/maintained-source-14/platform/ps4/clean-build.sh /home/joseph_cano/.cache/pswaker/maintained-14 /home/joseph_cano/.cache/pswaker/maintained-13-complete
```

The destination did not exist. The cache supplied checked downloads only; every
target implementation library was rebuilt, including the runtime, Mesa, SDL3,
Dawn and reconciled Aurora. Frozen source archive SHA-256:
`5adbf0b576d7ac4c84308618d79c61a3348cddbbdd6d8eab0b1003ea29304967`. The full source archive, binaries, matching
unstripped ELF, complete stage logs, command listings, generated headers and
notices remain local at `local-research/diagnostic-artifacts/renderer-14` and `/home/joseph_cano/.cache/pswaker/maintained-14`.

| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `PSWaker-Platform-Diagnostic-01.04.pkg` | `edeaebf3a68413c1f3a23a8224b0125240e6419710b9247b2132ccfccd5d6522` | 43909120 |
| `platform_diagnostic.elf` | `1cb796480f3961447158d6658c56e7bb309f3fc2a290ef2195b38d4b1c6e40e6` | 47494376 |
| `eboot.bin` | `5d3438436d381fef0facd0cd2397461e9d3f9741b52f996b88c8e7b89952c036` | 41763824 |
| `platform_diagnostic.oelf` | `48db76f35879cfcfe5430cd7af7e707f415bb452f5c23f73d58021dec569ea17` | 48595112 |

```text
STAGE fresh-download-cache 2026-10-23T20:51:02+00:00
STAGE pinned-sources 2026-10-23T20:51:38+00:00
STAGE sdk-target-support 2026-10-23T20:52:03+00:00
STAGE runtime 2026-10-23T20:52:35+00:00
STAGE graphics-inputs 2026-10-23T20:53:05+00:00
STAGE graphics-libraries 2026-10-23T20:53:55+00:00
STAGE diagnostic 2026-10-23T21:04:50+00:00
STAGE package 2026-10-23T21:06:15+00:00
COMPLETE host-build-only 2026-10-23T21:06:29+00:00
```

## Source, ABI and artifact checks

- All 21 SwitchWaker renderer patches have immutable originals, hashes, ordered
  dispositions and an original-hunk/context record. Fifteen selected patches
  produce the reviewed final hashes. Nineteen PS5 reference hunks are excluded
  explicitly in favor of the matched PS4 stack.
- [Platform contracts](platform-contracts.json) confirm unchanged selected surface,
  Vulkan loader/WSI, runtime source and generated C/C++ WebGPU headers relative to
  the maintained baseline. AuroraConfig's new opt-in field is compiled into the
  application and Aurora together. No old binary client ABI is assumed.
- The command audit inspected 2579
  target compilation commands across 10 Ninja/CMake components: all
  selected target commands use `btver2`; none carries PS5 target flags. Musl/bzip2
  Make commands and rebuilt archive hashes remain in the full SDK-support log.
- Fresh extraction verifies the exact payload, SFO identity, embedded compiled
  identity and ELF/SELF/package hashes. The matching ELF retains symbols and its
  required load layout; wider-atomic observations are in [inspection](inspection.json).
- [Final host checks](host-checks.log): eight tests pass, zero skips, including
  real package acceptance, changed/extra payload rejection and real pinned-source
  renderer acceptance/changed-context rejection. Python compilation and all shell
  syntax checks pass. The clean target build typechecks the C/C++ interfaces.
- The existing SDK/module notice audit ran for this package too; its unresolved
  distribution status remains recorded in [license-audit.json](license-audit.json).

## Host behavior and negative trials

[Host renderer evidence](host-renderer.json) identifies the compiled program,
reused host Dawn/SDL3 archives and generated headers, host zlib/libpng source
trees, compiler, driver and invocation. This is not an independent host clean
build. Actual shader creation and asynchronous GPU readbacks run on Vulkan
llvmpipe (Mesa 25.2.8, LLVM 20.1.2) under Xvfb.

The [cold](host-cold.log), [warm](host-warm.log) and
[controlled corrupt-cache](host-corrupt.log) processes each exit zero with
`END failures=0`. Each executes all 18 known-result pixel samples before and after
target recreation: 36 comparisons of 1,024 RGBA pixels per process. Both invalid
45-byte cache databases are detected, deleted and recreated in the corrupt trial.
Original caches from before corruption are preserved locally.

Earlier host setup failures remain separate: [missing ICD path](negative-missing-icd.log),
[CPU adapter disabled](negative-cpu-adapter-disabled.log), and
[missing cache directory](negative-missing-cache-directory.log). The first two
were corrected by selecting the actual host ICD and allowing a CPU adapter in
the host harness; the harness now creates its cache directory. Their observations
are not attributed to the final candidate.

The shared checks cover true/false TEV alpha compares, lit SRTG, three-vertex
quads, zero-brightness attenuation, GX EFB copy-to-texture and independent content
scale/allocation behavior. The PS4 loop retains its textured depth/blend/purple,
EFB/offscreen white, target recreation, runtime/audio/input/persistence, resource
and drained shutdown checks. Actual PS4 execution remains untested.

## Review and remaining gate

[Independent Standards and Spec review](REVIEW.md): no documented standard or
spec defects; one optional low-severity maintainability heuristic was retained
with an explicit disposition. The final retained evidence and source/package
identity comparison were completed after the agents reviewed the implementation.

#15 still requires two independent clean builds with explained differences and
one cold plus two warm 600-second owner console runs associated with the actual
installed PKG. This single clean build is preparation for that gate. Use the
[candidate checklist](../../Renderer-checklist.md). Host llvmpipe does not validate
PS4 RADV/VideoOut behavior, PS4 cache recovery, presentation pacing or all texture
cache/game TEV cases. Historical 01.02/01.03 evidence establishes no result for
this binary. Game integration and game graphics correctness remain later work.
