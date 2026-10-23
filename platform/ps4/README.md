# Maintained PS4 platform diagnostic

Implements the preparation slice in [issue #13](https://github.com/Jcanotorr06/pswaker/issues/13).
This builds a **disc-free program package**, title ID `PSWK00010`, version `01.03`.
It contains synthetic test content only. Game integration, renderer reconciliation,
the maintained clean-build pair and renewed console gate belong to #14 and #15.

## Reproduce on Linux / WSL2

Use the recorded Ubuntu 24.04 x86-64 environment in `host.lock.json`. It identifies
the observed installed package inventory, a lock for 188 build-tool packages
including their transitive dependencies, and tool hashes/versions, including
Clang 21.1.8, LLVM runtimes 21.1.6 and .NET 8. `install-host.sh` installs the exact
recorded build-package versions using Ubuntu and the fingerprint-checked
LLVM repository; it does not recreate an OS image. `inputs.py host` rejects a
different OS, architecture, tool or required build-package version. Additional
unrelated installed packages are allowed. Preserve/export the
recorded WSL distribution when long-term host recovery is needed. Unavailable
recorded packages require a deliberate lock update and renewed build evidence.

Run from the repository root, with the **build directory on the Linux filesystem**:

```bash
# Optional first-time provisioning, on a matching Ubuntu installation, as root:
bash platform/ps4/install-host.sh

python3 platform/ps4/inputs.py host /tmp
# Destination must not exist. Fetches recorded inputs without the live SDK database.
bash platform/ps4/clean-build.sh "$HOME/.cache/pswaker/diagnostic-01.03"

# Alternatively, reuse downloads from a previous root. No source/build libraries
# are copied; every locked download is checked again before use.
bash platform/ps4/clean-build.sh "$HOME/.cache/pswaker/diagnostic-01.03-new" \
  "$HOME/.cache/pswaker/diagnostic-01.03"

# Repeat inspection without rebuilding; extraction is always fresh:
python3 platform/ps4/inspect-artifacts.py "$HOME/.cache/pswaker/diagnostic-01.03"
```

`JOBS=5` is the default. Build paths must not contain spaces because the inherited
toolchain embeds paths in compiler/linker flag strings. Repository paths may
contain spaces. The command stops at the first failed stage; keep its evidence
directory. For a clean retry, use another absent destination.

## Ordered source and build closure

`sources.lock.json` pins the selected public source archives; `sdk.lock.json`
locks all 14 SDK package filenames and SHA-256 values. `dependencies.lock.json`
adds exact Dawn DEPS commits, Mesa/libdrm commits, hashed Python wheels, CMake
archives and SDK runtime source archives. `patch-series.json` records patch
owners, hashes, component order and application directories. `apply-patches.py`
checks both digest and context. The atomic-wait patch applies in **libcxx/src**.
Inherited Dusklight PS5 preparation reference
`5811958531cb0a9eafeb293fafcb36071883bfdf` is provenance for the selected fork
sources' existing adaptations, not a source of binary libraries for this build.

1. Verify host/download inputs and extract the SDK. Prepare the selected
   DolphinPS4 runtime and LLVM overlay. Rebuild the linked musl/CRT, compiler
   builtins, unwinder, zlib, libpng and bzip2 with Clang 21 / `btver2`, then libc++/libc++abi 21
   and the runtime preflight. SDK stubs and sample modules remain explicitly
   inventoried SDK inputs, not newly compiled target libraries.
2. Prepare official Mesa 26.0.8 at `60e95b787857afbc9a00b693b91c0d9c8923a430`,
   libdrm headers and the matched PS4 DRM replacement. **This official Mesa plus
   Dusklight patch is experimental; it is not claimed equivalent to the author's
   unresolved `80c7811` tree.** Apply the selected Abseil/Dawn/SDL3 PS4 changes.
   Build Mesa, SDL3 and Dawn, preserving static ICD loading, VideoOut WSI and
   generated WebGPU bindings from this Dawn build.
3. Apply the selected Aurora PS4 changes and build the corrected diagnostic.
   Its source requires C++23; the other dependencies retain their own language
   requirements. No PS5 binaries, `znver2` flags, signal contexts or caches are
   imported. The SDK's selected LLVM-12 builtins/unwinder source is rebuilt using
   Clang 21; it does not supply libc++12 to the application. The unwinder explicitly
   includes musl's `alloca.h` rather than relying on a FreeBSD stdlib declaration.
4. Build pinned LibOrbisPkg with the recorded .NET SDK and locked NuGet graphs
   containing its internal project reference and no external packages.
   Package through ELF → SELF → GP4 → PKG. Extract the new PKG
   and inspect its metadata, exact payload, compiled identity and hashes; retain
   the matching unstripped ELF. Record emitted/unresolved wider-atomic references
   rather than assuming all atomic widths are lock-free.

`adapt-platform.py` retains the local Jaguar/initial-exec TLS flags, heap
observations, neutral failed pad reads and packaging-tool override as generated
diffs with prepared-file hashes. The upstream overlay/build scripts preserve
constructor priority, TLS sections, pthread-once wrapping, allocator replacement
and runtime/link order. The inherited native platform changes are extracted only
for its four diagnostic support files, preserving their per-file notices.

## Outputs and inspection

Each build root retains:

- `out/*.pkg`: local installable program package.
- `build/probe/platform_diagnostic`: matching unstripped ELF.
- `build/probe/platform_diagnostic_eboot/`: SELF, OELF and converter evidence.
- `evidence/`: ordered stage/build logs, actual source/host/dependency closure,
  rebuilt runtime hashes, patch records, manifest, package/ELF/SELF hashes,
  package extraction log, metadata/payload inspection, atomic-symbol observations
  and notice/module audit.
- `downloads/`, `src/`, `refs/`: exact inputs, source trees and inherited recipes.

The program embeds `build-info.json` and logs its source/toolchain build identity.
The manifest labels console status as untested. Keep the PKG hash, matching ELF,
manifest and all logs together; later console results must identify that PKG.
See [licensing and provenance](LICENSING.md) before distributing any artifact.
The first maintained clean build's [report and hashes](evidence/maintained-13/REPORT.md)
record the inspected 01.03 artifact and its exact source identity.

## Diagnostic behavior and next gate

The retained checks cover known-result textured depth/blend/copy/readback output,
exact-white GX EFB/offscreen pixels, map status and sampled pixel diagnostics,
allocated 1280x720 EFB dimensions, target recreation and pipeline readiness.
Explicit SDL dummy-video selection precedes the independent PS4 presentation
path. GX initialization, an alpha-capable framebuffer and an explicit 640x480 VI
base at 1.5x retain the corrected sizing/state contract. Scanout is independently
reported as 1920x1080/59.94 Hz.

Runtime checks cover constructors, thread-local state/destructors, pthread-once,
condition variables, atomic wait/notify and persistent file replacement. The
main loop exercises fresh controller reads, neutral disconnect state and
deliberate Cross resume; synthetic 48 kHz stereo audio; cache/persistence checks;
and garlic/onion/main-mspace/flexible-memory observations. It drains queued GPU
work before destroying resources and records ordered shutdown stages.

Evidence remains at `/data/pswaker-diagnostic-prototype/` for compatibility:
`diagnostic.log`, `runtime-preflight.log`, `preflight-state.txt`, `platform.log`,
`platform.prev.log`, and `cache/`. The first two logs append launches: associate
only the matching BEGIN/build block with a run. Do not mistake older records for
this package. Last-stage files are not established crash dumps.

#15 owns the owner checklist and renewed gate: one cold-cache and two warm-cache
600-second runs, full close/relaunch, expected RGB triangle/white/purple/text,
continuous quiet tone, controller exercise, persistence and evidence retrieval,
with no failures/crashes/hangs or sustained resource growth. No current host
inspection establishes those outcomes. Synthetic audio/storage and the historical
pass establish no game DSP, game-save correctness or gameplay performance.

## Host checks

The agreed test boundaries are the preparation and artifact-inspection CLIs:

```bash
python3 -m unittest discover -s platform/ps4/tests
python3 -m compileall -q platform/ps4
for script in platform/ps4/*.sh; do bash -n "$script"; done
# After a build, also exercise the actual packaging tools and payload rejection:
PSWAKER_REFERENCE_BUILD="$HOME/.cache/pswaker/diagnostic-01.03" \
  python3 -m unittest discover -s platform/ps4/tests
```

The target build itself typechecks the C/C++ interfaces against the selected
headers. These checks require no game data. See [history](HISTORY.md) for the
retained negative trials and historical corrected hardware pass.
