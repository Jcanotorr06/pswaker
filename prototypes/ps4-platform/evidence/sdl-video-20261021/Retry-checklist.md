# Version 01.01 console retry

Install **PSWaker-Platform-Diagnostic-01.01.pkg** using the existing USB package
workflow. Confirm the installer shows **PSWaker Platform Diagnostic**, title ID
`PSWK00010`, version **01.01**. The original 01.00 package remains in the parent
artifact folder; select this replacement from `sdl-video-fix/`.

Expected build ID: `3a73181f6dfdb86ca4b4`.

Package SHA-256:
`6544219acf0beed6a64361f2839721c06b06b9168c82fbd388bcdcb9b1ec9080`.

1. Report whether the console is still PS4 Slim / firmware 9.00 / GoldHEN v2.4b18,
   or provide the actual versions. Fully close the application before installing.
2. Keep the existing logs/state and their retrieved copies. For a cold-cache run,
   remove only `/data/pswaker-diagnostic-prototype/cache` through FTP if present.
3. Launch the full diagnostic and watch the first minute. Expect a white background,
   RGB triangle, purple swatch, summary text and quiet continuous tone.
4. If it crashes, hangs or remains black, record the outcome/error/time and retrieve
   the new files immediately. Report any displayed text or audio. A black screen
   is not the expected success state for this full diagnostic.
5. If the UI and tone appear, continue the full ten-minute loop. Test controller
   disconnect/reconnect once, releasing Cross before deliberately pressing it to
   resume. After at least 600 seconds, close with Options and fully close the app
   from the shell if necessary. Retrieve evidence before another launch.
6. Once the cold run succeeds, repeat two warm-cache ten-minute runs, retaining
   cache and state and fully closing between runs. Keep each run's observations
   and retrieved files separately identifiable.

Retrieve these from `/data/pswaker-diagnostic-prototype/` after each attempt:

- `diagnostic.log`
- `runtime-preflight.log`
- `preflight-state.txt`
- `platform.log` and `platform.prev.log` when present

Place the new files in a separate local folder under `sdl-video-fix/` and share
that folder path with the outcome. The diagnostic log appends runs: inspect the
latest `BEGIN build=3a73181f6dfdb86ca4b4` block. The corrected boundary should show
`PASS SDL-dummy-video-selected`, then `SDL_VIDEO active=dummy` after Aurora returns.
If startup fails later, the final stage/error is the useful result. Confirm useful
file retrieval and report visual/audio defects and controller behavior too.

This retry addresses the logged SDL startup failure. Hardware acceptance still
requires the three complete runs, checked graphics/runtime results, persistent
state and resource review. The host reproduction does not certify the console fix.
