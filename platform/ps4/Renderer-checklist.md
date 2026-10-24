# Renderer-reconciled diagnostic 01.04: owner checklist

Use this candidate's identity. The [01.03 checklist](Console-checklist.md) remains
the record for that older package. The package below is already installed and
owner-confirmed in the [returned evidence review](evidence/renderer-14/console-01.04/REPORT.md).
Follow this procedure again if renewed console evidence is needed.

| Item | Expected value |
| --- | --- |
| App / title ID / version | PSWaker Platform Diagnostic / `PSWK00010` / `01.04` |
| Build ID shown in the app | `60975dcf4480aa914369` |
| Local package | `local-research/diagnostic-artifacts/renderer-14/PSWaker-Platform-Diagnostic-01.04.pkg` |
| Package size | 43,909,120 bytes |
| PKG SHA-256 | `edeaebf3a68413c1f3a23a8224b0125240e6419710b9247b2132ccfccd5d6522` |
| Matching unstripped ELF SHA-256 | `1cb796480f3961447158d6658c56e7bb309f3fc2a290ef2195b38d4b1c6e40e6` |
| Packaged SELF SHA-256 | `5d3438436d381fef0facd0cd2397461e9d3f9741b52f996b88c8e7b89952c036` |
| Console baseline | PS4 Slim / firmware 9.00 / GoldHEN v2.4b18 |

Verify the package on the PC, from the repository root:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'local-research/diagnostic-artifacts/renderer-14/PSWaker-Platform-Diagnostic-01.04.pkg'
```

Keep the matching ELF, package, [build manifest](evidence/renderer-14/input-closure.json)
and logs together. Rebuilt host packages have their own hashes even when they show
the same source/toolchain build ID; record the package actually installed.

Before declaring the maintained platform verified, #15 must retain two independent
clean Linux/WSL2 builds from the reviewed inputs, inspect both ELF/SELF/PKG outputs,
and explain any binary differences. Neither rebuilding nor the host pixel checks
counts as a console run.

For the candidate actually installed by the owner:

1. Confirm PS4 Slim, firmware 9.00 and GoldHEN v2.4b18 and working existing FTP
   access. Record date/time zone and display/audio output. Verify the PC package
   hash and record the build ID shown by the app. Back up the complete console
   directory before installation or cache changes. Install the verified package
   using the existing USB workflow; record any installer error exactly.
2. Perform one launch with only disposable caches absent and two launches with
   generated caches retained. While the app is fully closed, rename `cache` under
   `/data/pswaker-diagnostic-prototype/` to `cache-before-01.04-<date-time>` and
   create an empty `cache` directory (or record that no previous cache exists).
   Preserve `preflight-state.txt`, logs and backup caches. Fully close between
   launches, retrieve evidence after each, and keep the same installed PKG.
3. Complete each 600-second loop and the controller disconnect/reconnect/Cross
   resume sequence. Confirm the RGB triangle, white background, purple preview,
   readable advancing text and continuous quiet 440 Hz tone. Exercise ordinary
   buttons and partial/full L2/R2 travel. Hold an input while disconnecting; check
   neutral buttons/triggers, reconnect, release Cross and deliberately press Cross
   to clear the waiting prompt. The scene/timer continues during this diagnostic
   prompt; this does not establish gameplay pause behavior. Report any stuck input.
   Wait for the loop-complete message with zero failures/audio errors, then press
   Options for orderly exit. Confirm the app has fully closed before relaunching.
   Report startup/preparation duration and any visible/audio defect separately
   from the ten-minute loop. No game or disc image is needed.
   Brief dark-blue flashes can appear during the renderer sweep at startup and
   every 12 check cycles (about once a minute). The content-scale check can also
   briefly show white with a black upper-left quarter. These frames are deliberate
   diagnostic test content; the normal triangle/preview panel then returns.
4. Retrieve the complete `diagnostic.log`, `runtime-preflight.log`,
   `preflight-state.txt`, `platform.log` and optional `platform.prev.log` from
   `/data/pswaker-diagnostic-prototype/` after every close. Preserve failed runs
   separately and record cache directory listings and owner observations. Download
   cache databases too, preserving before/after snapshots. Use separate folders
   `before-01.04`, `run-1-cold`, `run-2-warm`, `run-3-warm` and additional folders
   for any extra attempts. Keep full append logs, including older failures.
5. Review the matching BEGIN/build blocks for zero failed checks, known-result
   renderer sweeps at startup and after target recreation, repeated original
   EFB/offscreen/purple checks, allocated 1280x720 targets, independent actual
   display mode, runtime/input/audio/persistence results and bounded measured
   resource observations. Keep map failures and actual formats/dimensions.
6. Require `PASS GPU-queue-drained`, ordered Aurora shutdown stages and a final
   zero-failure END block. The on-screen count before closing does not cover
   shutdown. Last-stage files are not crash dumps.

If the app fails or hangs, record the cache state, last displayed stage, elapsed
time, exact error and any forced close/reboot. Retrieve the same files before
reinstalling, clearing caches or retrying. Keep the failed attempt separately.
Return an invalidating result to the architecture decision linked by #12; do not
change the stack or begin game integration to bypass the gate.

Report each run's visible/audible/input observations, final timer/frames/checks,
launch counter, shutdown result and any interruption, with the installed PKG hash.
Use `not recorded` for unavailable timings, output-device details or photos/video;
written observations plus matching logs remain required. Share diagnostic data
only: exclude game data, keys, credentials and private network details.

Resource review uses driver-reported garlic/onion allocation and buffer counts,
main-mspace allocated bytes, heap capacity and available flexible memory sampled
about every 30 seconds. Review startup separately from the later trend; report
all samples and fluctuations. These counters do not measure full process RSS or
establish universal leak freedom. Synthetic audio tests pacing and API errors;
owner listening is required and does not establish game DSP correctness.

Expected new renderer names include `GX-alpha-*` (both true and `-false` cases),
`GX-lit-SRTG`, `GX-three-vertex-quad`, `GX-zero-brightness-attenuation`,
`GX-EFB-copy-to-texture-known-white`, `GX-content-scale-allocation`,
`GX-content-scale-upper-left` and `GX-content-scale-lower-right`.

Retain this candidate's own logs/photos/observations. No historical console pass
validates it. Game integration and graphics acceptance remain later work.

Returned evidence for build `60975dcf4480aa914369` is reviewed in the
[01.04 console evidence report](evidence/renderer-14/console-01.04/REPORT.md).
The completed [#15 verification report](evidence/verification-15/REPORT.md) adds
the independent clean-build pair and bounded binary-difference review.
