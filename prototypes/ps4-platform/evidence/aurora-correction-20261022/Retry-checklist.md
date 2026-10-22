# Version 01.02: Aurora geometry retry

This is the full disc-free diagnostic with a bounded graphics correction.
It is ready for owner testing, **not a PS4 pass**. The failed 01.01 package and
evidence remain preserved. No game image or game program is needed.

| Identity | Value |
| --- | --- |
| Title | PSWaker Platform Diagnostic |
| Title ID / version | `PSWK00010` / **01.02** |
| Build ID | `4b1830b0443ff170425e` |
| PKG SHA-256 | `9764e1acb1e7fa8a17c8c7aee9ca3793ac908da38368188b52de33a49dd399be` |

Install this local file through the existing USB package installer:

```text
C:\Users\Joseph Cano\Code\pswaker\local-research\diagnostic-artifacts\aurora-gx-fix\PSWaker-Platform-Diagnostic-01.02.pkg
```

The matching ELF, SELF, build manifest and artifact hashes are beside it.
The copied package/ELF/SELF hashes have been checked. Install as the existing
diagnostic title's update; keep its persistent state and earlier evidence.

1. Confirm the console is still PS4 Slim / firmware 9.00 / GoldHEN v2.4b18,
   or report the actual versions. Keep the three earlier evidence sets.
2. For the first **cold-cache** run, remove only
   `/data/pswaker-diagnostic-prototype/cache` through FTP. Preserve the other
   files, especially `preflight-state.txt`. The application recreates the cache.
3. Launch 01.02. A short shader-preparation stage precedes the checked loop.
   During the first minute, expect a **white background, visible RGB triangle,
   purple swatch, text summary, continuous quiet tone**, and **1280x720 internal**
   rendering. The surface/display remains independently reported at 1920x1080.
   Record the build ID and anything missing or wrong. A photo/video helps with
   visual or audible failures. A local Linux pass does not predict the console
   result with certainty.
4. If those appear, continue the same launch for **at least 600 displayed loop
   seconds**, excluding preparation. Once during the run, hold a direction or
   button, disconnect the controller, reconnect, release Cross, then press Cross
   deliberately to resume. Observe neutral input while disconnected and record
   disconnect/reconnect counts, sound continuity and any corruption or hitch.
5. After 600 seconds, release and press Options to exit. Fully close the
   application from the shell if needed. If it crashes, hangs, reports failures
   or lacks the triangle, report the time and error; retrieve the files below.
   A short failed isolating trial is useful evidence and is not an accepted
   ten-minute run.
6. Retrieve these files through FTP **after closing and before relaunching**:
   `diagnostic.log`, `runtime-preflight.log`, `preflight-state.txt`, `platform.log`
   and `platform.prev.log` from `/data/pswaker-diagnostic-prototype/`. Keep full
   copies labeled **01.02 cold**, **01.02 warm 1**, **01.02 warm 2**, rather than
   only screenshots or selected lines. Include inherited runtime logs if a
   crash leaves them under `/data/DolphinPS4/`.
7. Run twice more for 600 seconds each, with the same controller check and full
   close/retrieval between launches. Retain the cache for these **warm-cache**
   runs. The persistent launch counter should advance across launches.

Return your observations for each run: triangle/background/swatch, internal size,
tone continuity, controller behavior, displayed failure count, any error and
whether file retrieval worked. Keep credentials and private network details out
of the report.

The evidence review expects the latest `BEGIN` block for build
`4b1830b0443ff170425e`, successful pipeline preparation, allocated EFB size
1280x720, exact-white EFB/offscreen pixels, passing purple checks, zero failed
checks, the required runtime/audio/input/persistence checks and stable resource
observations. The new shutdown stages must show `PASS GPU-queue-drained`,
`Aurora-shutdown-complete`, then `END`. Preserve any mapping/device messages so
their timing and reason can be reviewed; an expected destruction warning is
distinct from device loss during rendering.

This candidate is one incremental build reusing recorded platform libraries.
**Two renewed clean builds of the corrected source remain required** before the
platform gate can be cleared. The historical 01.00 pair does not count as those
builds. The same three successful Slim runs remain required; no acceptance
threshold, known-pixel comparison or architecture decision has been changed.
