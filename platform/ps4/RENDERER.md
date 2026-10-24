# Wind Waker renderer reconciliation — issue #14

The selected Aurora fork remains `mshivam019/dusklight-ps5` at
`e281999cdb4fee6127525a9a9e97979480db4bf3`, followed by the locked Dusklight
`aurora-ps4.patch`. `reconcile-renderer.py` then applies the reviewed Wind Waker
changes in filename order. It rejects a changed preparation context before
applying anything, verifies original and reconciled patch digests, and checks
the final source hashes. `renderer.lock.json` is the machine-readable inventory;
`evidence/renderer-reconciliation.json` travels in the package's build manifest.

Original patches are retained verbatim under `provenance/wind-waker/`, with
immutable source URLs and digests. Adapted patches live in `patches/wind-waker/`.
Their source is SwitchWaker `ba8d0a31446cd53ceaebd6b7269cca641e73bf4c`, originally
applied to encounter/Aurora `3227d76c60e1e782ca576610bce61c9e7744d8be`.
The [original-hunk applicability record](evidence/renderer-14/patch-applicability.json)
retains 223 hunk headers, application diagnostics, and individual resolutions.
Application success is context evidence; the synthetic checks below supply
bounded behavioral evidence.

## Ordered disposition

| Patch | Resolution on the maintained PS4 fork |
| --- | --- |
| 0001 alpha-stage channel compares | Apply. Latch colour inputs before colour writes; use vectors for alpha R8/GR16/BGR24 comparisons. |
| 0002 SRTG lit colour | Apply. Mark the colour channel sampled and use its lit output for toon-ramp coordinates. |
| 0003 three-vertex quads | Apply. Emit whole quads and one triangle for a remainder of three; omit one/two trailing vertices. |
| 0004 zero-brightness attenuation | Apply. Brightness zero disables distance attenuation, avoiding infinite coefficients. |
| 0005 blocking pipelines | Adapt around fork census/priority context. Append the opt-in config field; preserve asynchronous default. All consumers rebuild against the same header. |
| 0006 FIT aspect | Apply optional API with its zero default. Diagnostic sizing keeps its established native viewport and VI base. No game widescreen option is selected here. |
| 0007 SQLite recovery | Adapt both caches. Preserve PS4 `unix-none` opens, centralize exclusive WAL pragmas, preserve the fork's seed-identity optimization and return `SQLITE_OK` on its early exit. Carry statement cleanup, bounded recovery and error limiting. |
| 0008 draw census/debug markers | Apply optional instrumentation, disabled by default. |
| 0009 EFB content scale | Apply viewport/scissor, copy-destination and depth-snapshot mapping. Smaller content occupies part of an unchanged allocation; offscreen mapping remains independent. |
| 0010 replacement streaming | Exclude HD-texture streaming/budget policy from stock-texture scope; retain the fork's implementation. |
| 0011 smooth replacement publish | Exclude the HD rescan/streaming behavior and dependency on 0010. |
| 0012 object-cache image check | Adapt independently of 0010/0011. Validate dimensions, format, mip count and bound image/sampler registers, retaining the fork's existing invalidation behavior. |
| 0013 Linux local time | Apply host fallback; PS4 path unchanged. |
| 0014 game-name termination | Apply NUL-termination correction. |
| 0015 DVD queue allocation | Apply allocation/free pairing; the disc-free build disables DVD and does not exercise this path. |
| 0016 cache-load abort return | Apply after 0007. Return immediately after abort finalizes the load statement. |
| 0017 copy-texture lookup | Apply the accessor to avoid external access to compiler-dependent `GXState` layout. Callers must first synchronize FIFO processing. |
| 0018 async end frame | Exclude the opt-in one-frame-ahead scheduling change. Preserve the selected fork's worker, synchronous frame-end drain, render-worker handoff and surface/resize synchronization. No 30 Hz game caller requires this optional mode yet. |
| 0019 view delta | Exclude interpolated repaints; original 30 Hz logic remains the contract. |
| 0020 FIFO profiler | Exclude the optional sampler and its async-frame dependency. Keep existing timing/resource evidence. |
| 0021 FIFO fast paths | Exclude optional 60 Hz memoization/index optimizations and dependencies. Keep the fork's current FIFO/draw cache; no throughput equivalence is asserted. |

Exclusion means no new API from that patch is available to a later game caller.
Game integration must deliberately adapt its optional configuration calls rather
than assume that the entire SwitchWaker renderer patch series was transplanted.

## Platform API, ABI and ordering

The PS5 reference is `griches/PS5_SwitchWaker` at
`3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0`. Its Aurora and Dawn patches are retained
as excluded reference inputs in the lock, including their individual file lists.
Its Aurora patch has three hunks: the Switch-window-token surface shim is
superseded by PS4 `SurfaceSourceDirectDisplay`; PS5 pad mapping belongs to later
controller work; suppressing ImGui debug groups is not carried into the matched
PS4 stack. Its Dawn platform/loader/surface changes are superseded by the selected
matched Dawn fork and PS4 patch, rather than mixed with them.

Dawn stays at `652a3104791369cd23605856fbc041375ccda875`, SDL3 at
`68159af2b34cc4fe5b3548faa89e87a69e4d2dce`, and experimental official Mesa 26.0.8
plus the locked PS4 patch stays selected. No runtime, CPU, WSI or static-ICD patch
changes in this slice. Source-built Dawn exports its own generated C/C++ WebGPU
headers to both Aurora and the diagnostic. PS4 `btver2`, initial-exec TLS,
constructor/runtime link order, static `vk_icdGetInstanceProcAddr`, direct-display
mode selection and VideoOut memory/fence/flip behavior remain together.

`AuroraConfig` grows by the appended `blockingPipelines` field. This requires
recompiling clients and Aurora together; no old binary client is ABI-compatible
by assumption. FIFO/public GX commands carry content scale in order. Frame-end
draining stays synchronous, and readbacks run after render-worker synchronization.
Target replacement and shutdown retain GPU draining and explicit destruction
stages. No PS5 archives, shaders or driver caches are imported.

## Observable checks and limits

The console diagnostic and Linux host reproduction share the GX scene and
readback code. Each renderer sweep checks 1,024 RGBA pixels per sample:

- Six alpha compare operations, each with independently chosen true and false
  inputs. Colour overwrites its input register before the alpha result; expected
  black has alpha 255 or 0, checking latching and comparison behavior.
- Lit SRTG sampling with black vertex colour, white lit colour and a ramp whose
  origin is black: the correct lit coordinate selects white.
- Three-vertex `GX_QUADS` coverage and zero-brightness distance attenuation,
  both with known-white output. This quad sample alone does not prove absence of
  every possible out-of-range index; the index-generation source is reviewed too.
- Actual `GXCopyTex` from a white EFB, resampled to a 32x32 copy texture, then
  sampled into an offscreen pass and compared against white. CPU backing starts
  zero, so a missing copy cannot satisfy the comparison.
- Full white EFB followed by a black draw at half content scale: upper-left
  samples must be black, lower-right white, and allocation must remain 1280x720.

The sweep runs at startup and after periodic diagnostic target recreation.
Its intermediate frames can briefly present dark blue, and the content-scale
sample can present white with a black upper-left quarter. The sweep repeats every
12 capture cycles, explaining the brief once-a-minute flashes before the normal
diagnostic scene returns.
The original EFB/offscreen white checks and raw WebGPU purple depth/blend/copy
checks remain in the ten-minute loop. Logs retain actual texture dimensions,
formats, map status and mismatch diagnostics. Blocking draw pipelines are enabled
only in these diagnostic configurations, preserving explicit preparation and
avoiding comparisons against skipped draws. This is not a game shader-hitch policy.

Host cold/warm/cache-corruption runs exercise the actual cache implementations;
corruption is confined to disposable host cache copies. They use host Vulkan
llvmpipe, host-compiled Dawn/SDL3 and the reconciled Aurora source. They cannot
establish PS4 RADV/VideoOut behavior, performance, hardware cache recovery, game
TEV coverage, every texture-object reinterpretation, or gameplay correctness.
The new package needs #15's two clean builds and renewed owner console gate.

## Repeat the host observation

The host harness consumes an explicitly supplied host-built Dawn/SDL3 pair and
host zlib/libpng source directories; it does not build the PS4 libraries as host
libraries. The recorded host archive/header/source hashes and environment are in
`evidence/renderer-14/host-renderer.json`. With those recorded local inputs:

```bash
cmake -S platform/ps4/host-renderer -B /tmp/pswaker-renderer-host -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=clang-21 \
  -DCMAKE_CXX_COMPILER=clang++-21 \
  -DPLATFORM_ROOT="$HOME/.cache/pswaker/maintained-14" \
  -DHOST_ROOT="$HOME/.cache/pswaker/aurora-host-20261022"
cmake --build /tmp/pswaker-renderer-host --parallel 12
mkdir /tmp/pswaker-renderer-run
cd /tmp/pswaker-renderer-run
SDL_VIDEODRIVER=x11 XDG_RUNTIME_DIR=/tmp \
  VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json \
  xvfb-run -a /tmp/pswaker-renderer-host/renderer-check
```

Repeat the last command in the same run directory for a warm cache. Preserve a
copy before corrupting disposable host cache files for a recovery trial. Use a
fresh run directory for a cold trial. This recipe reuses recorded host archives;
the maintained target clean build is the independent PS4 compilation path.

See [build and host evidence](evidence/renderer-14/REPORT.md) and the
[renderer candidate checklist](Renderer-checklist.md). The historical 01.02
and maintained 01.03 packages establish no hardware result for 01.04.
The subsequent [01.04 owner evidence review](evidence/renderer-14/console-01.04/REPORT.md)
records observations and logs from this candidate separately from these host checks.
