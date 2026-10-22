# Aurora diagnostic correction: local pass, Slim verdict pending

Progress on [Validate Aurora geometry and internal resolution after the failed Slim diagnostic](https://github.com/Jcanotorr06/pswaker/issues/11).
This is a disposable diagnostic branch, not game implementation or a stack change.
The ticket remains open and final specification approval remains blocked.

## Feedback loop and starting evidence

The [frozen 01.01 console result](../aurora-results-20261022/status.md) has three
ten-minute runs with missing RGB geometry, 569x320 reported internal dimensions,
and failed Aurora white comparisons. Those logs do not contain actual failed
pixels. They establish the original hardware failure, not its root cause.

A new [Linux reproduction](../../aurora-repro/README.md) builds the selected
Aurora, Dawn and SDL sources for the host and calls the real GX, frame,
EFB/offscreen resolve, submission and asynchronous readback code. It uses Xvfb,
lavapipe (Mesa 25.2.8 / LLVM 20.1.2), and explicit `allowCpuAdapter=true` only in
the host harness. Its original draw is checked against failed revision
`605d57a581e3657ce4a485140f17552b1c6119d2`. No driver is mocked and no log parser
stands in for executing the render path.

The loop was run before testing corrections:

```bash
bash prototypes/ps4-platform/aurora-repro/run.sh \
  /home/joseph_cano/.cache/pswaker/aurora-host-20261022 baseline
```

It exits 1 in seconds: actual size 569x320; mapping succeeds; EFB pixels are
`0,0,0,255` and offscreen pixels `0,0,0,0`. All 1024 pixels in each checked region
mismatch exact white. One frame already reproduces these failures. Thirty
repeated frames preserve them, excluding a transient first-frame explanation
for the uninitialized baseline. This is a reproduction of the failing Aurora
boundary on Linux, not execution of a PS4 binary or proof of an identical
console mechanism.

Ranked predictions shared before testing were: GX-to-resolve ordering; scale
relative to VI rather than display size; missing GX state/coordinate contract;
and first-frame pipeline readiness. The retained differential changes one
factor at a time, then combines the corrections:

| Variant | Observed result |
| --- | --- |
| Original / 30 repeated frames | 569x320; both checked regions black |
| Explicit GX drain | Same failure; direct resolve already drains the FIFO |
| Scale alone | 1280x720 allocated EFB; both white checks still fail |
| GX initialization, repeated | White EFB; offscreen RGB white but alpha zero |
| Initialization plus alpha-capable mode | Exact white from both paths; original size still wrong |
| Shared full correction plus pipeline preparation | 1280x720; all 30 frames pass both 1024-pixel RGBA comparisons |

The [differential regression output](host-repro/differential-check.log) and
[individual run logs](host-repro/) are preserved. Each retained run starts with
its own empty cache directory. The final corrected revision was checked again
through the complete matrix; it has no failed comparisons or aborted mapping
messages. Its first checked frame passes. Source/geometry equality and real
texture dimensions are asserted, rather than reproducing the implementation in
a model test.

## What the correction changes

1. **Initialize GX.** Aurora initializes its renderer and FIFO but the application
   still calls `GXInit`. The diagnostic omitted it. In the pinned
   `lib/dolphin/gx/GXManage.cpp`, that call initializes shadow BP register command
   bytes and defaults used by the GX setters. Calling individual setters on the
   zeroed shadow structure does not establish the intended scene state.
2. **Use the VI scale contract.** The pinned `lib/window.cpp` scales
   `vi::configured_fb_size()`, not the output surface. With the default 640x480
   VI base, 2/3 gives 320 pixels high, expanded to 569x320 at 16:9. The diagnostic
   now explicitly selects that VI base and uses 1.5x, yielding 1280x720.
   The projection and triangle coordinates remain identical to the baseline.
3. **Request alpha storage.** GX's RGB8 mode does not enable EFB alpha writes;
   `lib/gx/gx.cpp` gates them on `efb_has_alpha`. A cleared offscreen texture
   therefore retained alpha zero even with white RGB after initialization.
   Selecting `GX_PF_RGBA6_Z24` makes the exact four-channel check meaningful.
   The checker still requires every tested byte to equal 255. It accepts the
   explicitly identified RGBA8/BGRA8 snapshot layouts, where white bytes match.
4. **Separate shader preparation from validation.** The pinned pipeline cache
   asynchronously queues normal GX pipelines, so a cold first draw may precede
   availability. One bounded preparation frame queues the same white EFB,
   white offscreen and RGB EFB configurations, then waits at most 30 seconds for
   the atomic queue counter to reach zero. It does not poll pixels until they
   pass or excuse failed comparisons. The ten-minute checked loop starts after
   preparation; every comparison in that loop remains binding.

The PS4 diagnostic and Linux correction share setup, draw, pipeline preparation,
white-check and GPU-drain helpers. White checks now record dimensions/format,
mapping status/message, timeout versus map failure, the first actual pixel,
first mismatching coordinate/value and mismatch count. Every captured EFB also
checks its allocated snapshot dimensions; a size getter alone cannot pass it.

## Shutdown review

The earlier post-END mapping abort is consistent with destruction of Aurora's
asynchronously mapped staging buffers: `lib/gfx/frame.cpp` schedules the maps
and its shutdown releases those buffers. Render-worker synchronization alone
does not wait for GPU completion. The candidate now synchronizes the worker,
waits on a bounded queue-completion callback and processes events before
releasing its targets and calling Aurora shutdown. The local corrected run
contains no mapping-abort warning. The console effect is untested.

The local trace still reports `Device lost: Device was destroyed` during
intentional device shutdown. That reason is preserved, not presented as an
in-loop fault or silently removed. Aurora shutdown has explicit begin/complete
stages and the final END is written afterward, with the evidence stream kept
valid for late callbacks. The SDL dummy screensaver warning may still occur.
All messages in the next console evidence must be reviewed by stage and reason.

## Native build and package

Compiled diagnostic source: **`b45d5e29246bd1c86d78f9ca165cbc3f7b4d6e5b`**.
The candidate finished on the recorded WSL2 host at **2026-10-22 21:45:43 UTC**.

| Field | Value |
| --- | --- |
| Title ID / version | `PSWK00010` / **01.02** |
| Build ID | `4b1830b0443ff170425e` |
| PKG SHA-256 | `9764e1acb1e7fa8a17c8c7aee9ca3793ac908da38368188b52de33a49dd399be` |
| SELF SHA-256 | `af8e612f623f1a2142ce5f9fab73f2429751993b1a5bde67e9d84ad87de1b8c9` |
| ELF SHA-256 | `07e7dd55d78939de352343cc5d3cc46616de5af7176a940e834eb1f0c20fdb9a` |

This is **one incremental candidate build**, reusing the selected native graphics
libraries and runtime. It recompiles the diagnostic/runtime support objects and
packages with source-built LibOrbisPkg. Source pins, SDK, platform adaptations,
cached runtime archive hashes, Mesa/libdrm revisions and Dawn dependency records
match the preceding 01.01 inputs. The Linux reproduction links separate native
Linux libraries; its initially reused generated Dawn API headers match the
finished Linux generation by hash. New X11 host packages are recorded in the
current input closure and do not replace console libraries.

The host build was resumed after missing X11 development headers were installed;
its logs are exploratory build evidence. The PS4 compile exposed libc++ 21's
unsupported `atomic_ref<const T>` load; the retained failed compile records that
attempt. The corrected shared counter read uses the atomic builtin used by the
selected platform, then passed the host loop and PS4 build. No target SDK or
rendering-stack source was changed.

The SELF/OELF segment check passed. Fresh package extraction checked the expected
eight-file payload, SFO title/category/version, manifest/executable hash,
compiled identity and new checkpoints. Earlier extraction and baseline outputs
were preserved, avoiding reuse of old files as inspection evidence. See
[native build/package records](native/), [inspection](native/aurora-retry-inspection.json)
and [hash inventory/closure checks](summary.json).

Local owner artifact:

```text
C:\Users\Joseph Cano\Code\pswaker\local-research\diagnostic-artifacts\aurora-gx-fix\PSWaker-Platform-Diagnostic-01.02.pkg
```

Matching ELF, SELF, manifest, hashes and checklist are beside it. The copied
Windows package/ELF/SELF hashes match. The 01.01 local package hash remains
`6544219acf0beed6a64361f2839721c06b06b9168c82fbd388bcdcb9b1ec9080`.
No binary is published to GitHub; the disposable branch holds source and evidence.

## Pending hardware and acceptance

Follow the [01.02 owner checklist](Retry-checklist.md), observing the first minute
before continuing the required cold-cache and two warm-cache ten-minute runs,
each with complete close/relaunch and evidence retrieval. Return the visible RGB
triangle, white background, purple swatch, tone, controller and persistence
observations alongside full logs. Earlier positive runtime/audio observations
remain historical; they do not validate this new binary.

**Two renewed clean builds of the corrected final source remain required** by
the existing acceptance contract. The historical pair is not reassigned to this
candidate. A short isolating console trial can guide the correction, while the
full hardware/clean-build gates remain unsatisfied.

There is no new owner reaction or 01.02 console evidence in this session.
The local findings support a faulty diagnostic and do not invalidate the selected
stack. No architecture decision is reopened, no threshold is lowered and no game
code is integrated. The current ticket already captures the next precise question;
no newly sharp decision or fog graduation is justified before the owner's retry.
