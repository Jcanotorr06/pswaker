# Renderer-reconciled diagnostic 01.04: handoff to #15

Use the exact build ID, package SHA-256 and matching ELF in
[the build report](evidence/renderer-14/REPORT.md). Keep title ID `PSWK00010` and
version `01.04`. The existing [01.03 checklist](Console-checklist.md) remains the
record for that older package; substitute the new identity for this candidate.

Before declaring the maintained platform verified, #15 must retain two independent
clean Linux/WSL2 builds from the reviewed inputs, inspect both ELF/SELF/PKG outputs,
and explain any binary differences. Neither rebuilding nor the host pixel checks
counts as a console run.

For the candidate actually installed by the owner:

1. Confirm PS4 Slim, firmware 9.00 and GoldHEN v2.4b18. Verify the PC package hash
   and record the build ID shown by the app. Back up earlier console evidence.
2. Perform one launch with only disposable caches absent and two launches with
   generated caches retained. Fully close between launches. Preserve state/logs
   and keep all three runs associated with the installed PKG hash.
3. Complete each 600-second loop and the controller disconnect/reconnect/Cross
   resume sequence. Confirm the RGB triangle, white background, purple preview,
   readable text and continuous quiet tone. Report startup/preparation duration
   and any visible/audio defect. No game or disc image is needed.
4. Retrieve the complete `diagnostic.log`, `runtime-preflight.log`,
   `preflight-state.txt`, `platform.log` and optional `platform.prev.log` from
   `/data/pswaker-diagnostic-prototype/` after every close. Preserve failed runs
   separately and record cache directory listings and owner observations.
5. Review the matching BEGIN/build blocks for zero failed checks, known-result
   renderer sweeps at startup and after target recreation, repeated original
   EFB/offscreen/purple checks, allocated 1280x720 targets, independent actual
   display mode, runtime/input/audio/persistence results and bounded measured
   resource observations. Keep map failures and actual formats/dimensions.
6. Require `PASS GPU-queue-drained`, ordered Aurora shutdown stages and a final
   zero-failure END block. The on-screen count before closing does not cover
   shutdown. Last-stage files are not crash dumps.

Expected new renderer names include `GX-alpha-*` (both true and `-false` cases),
`GX-lit-SRTG`, `GX-three-vertex-quad`, `GX-zero-brightness-attenuation`,
`GX-EFB-copy-to-texture-known-white`, `GX-content-scale-allocation`,
`GX-content-scale-upper-left` and `GX-content-scale-lower-right`.

Retain this candidate's own logs/photos/observations. No historical console pass
validates it. Game integration and graphics acceptance remain later work.
