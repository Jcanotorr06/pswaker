# Returned 01.04 console evidence — 2026-10-24

Follow-up: [issue #15 verification](../../verification-15/REPORT.md) completed the
outstanding clean-build pair and binary-difference review. This original console
review retains its observations and scope below.

All three supplied runs pass the instrumented disc-free checks and the owner's
written visual, audio and controller observations. The executed build and embedded
SELF identity match the prepared 01.04 candidate. The owner subsequently confirmed
in this conversation that they installed `PSWaker-Platform-Diagnostic-01.04.pkg`
with SHA-256 `edeaebf3a68413c1f3a23a8224b0125240e6419710b9247b2132ccfccd5d6522`:
“Yes, that exact package.” The bounded three-run console gate passes for this
confirmed candidate. The original report's stale `01.03` field and blank package
hash remain preserved without editing the supplied evidence.

The owner reconfirmed PS4 Slim / firmware 9.00 / GoldHEN v2.4b18. This review
covers the returned runs; #15's two independent clean builds and explained binary
differences remain outstanding. It does not establish game compatibility.

## Candidate and original evidence

| Identity | Value |
| --- | --- |
| Logged build ID | `60975dcf4480aa914369` |
| Embedded manifest version | `01.04` in every selected run |
| Expected/local-verified PKG SHA-256 | `edeaebf3a68413c1f3a23a8224b0125240e6419710b9247b2132ccfccd5d6522` |
| Embedded/matching SELF SHA-256 | `5d3438436d381fef0facd0cd2397461e9d3f9741b52f996b88c8e7b89952c036` |
| Matching retained ELF SHA-256 | `1cb796480f3961447158d6658c56e7bb309f3fc2a290ef2195b38d4b1c6e40e6` |

Original files remain at
`local-research/diagnostic-artifacts/renderer-14/console-01.04-evidence/`.
[original-files.json](original-files.json) inventories all 47 supplied files by
path, size and SHA-256, including backups and cache databases. Files and earlier
launch history were preserved. No files were removed, rewritten or relabelled.
Retrieval timestamps are not measurements of console frame timing.

[summary.json](summary.json) records selected block line ranges, per-case counts,
runtime/shutdown evidence, resources and cache identities. Parsing validates the
supplied records; it does not independently render frames or verify audible output.
Only the last BEGIN block of each run snapshot is attributed to that run. The
before snapshot ends with build `f89abcb363a45bfbe8cc`, version 01.03, launch 12;
that historical run is excluded from the 01.04 results below.

## Three-run results

| Observation | Cold | Warm 1 | Warm 2 |
| --- | ---: | ---: | ---: |
| Launch / state counter | 13 | 14 | 15 |
| Cache entries before Aurora | 0 | 2 | 2 |
| Final logged frames | 36,696 | 35,669 | 35,699 |
| Check cycles | 120 | 120 | 120 |
| Renderer sweeps: startup + recreation | 1 + 9 | 1 + 9 | 1 + 9 |
| New renderer RGBA samples | 180 | 180 | 180 |
| Original EFB + offscreen white samples | 120 + 120 | 120 + 120 | 120 + 120 |
| Textured depth/blend/copy purple samples | 120 | 120 | 120 |
| Successful map callbacks | 540 | 540 | 540 |
| Failed checks / mismatched pixels | 0 / 0 | 0 / 0 | 0 / 0 |
| Timed loop check: at least 600 seconds | PASS | PASS | PASS |
| Existing GX preparation, ms | 138.8 | 35.0 | 33.8 |
| Drained GPU / explicit shutdown / exit 0 | PASS | PASS | PASS |

Each RGBA sample checks 1,024 pixels. All 12 true/false alpha compare cases, lit
SRTG, three-vertex quads, zero-brightness attenuation, GX EFB copy-to-texture and
both content-scale corners pass on each sweep. All 120 allocated EFB snapshots
per run are 1280x720. The platform independently reports 1920x1080 at 59,940 mHz
(59.94 Hz) output. Texture dimensions, format values, map status and pixel values
are present in the actual console logs.

The runtime preflight passes constructors, TLS isolation/destructors, pthread-once,
condition variables, atomic wait/notify and persistent file replacement for all
three launches. State advances 12 → 13 → 14 → 15. Successive diagnostic and runtime
log snapshots preserve the previous file as a byte prefix. The owner reports full
close/relaunch, working controls/triggers, neutral disconnect, deliberate Cross
resume, the expected steady scene and uninterrupted quiet audio in every run.

The owner's run-2 screen observation of `599.9` seconds precedes closing. The
subsequent `PASS ten-minute-loop` records the source's monotonic-clock comparison
against 600 seconds; it is not treated as an early-exit failure. Preparation values
above cover the existing initial GX pipeline stage, not total application startup
or the complete added renderer sweep. No total-startup limit was agreed.

Shutdown records `PASS GPU-queue-drained`, Aurora shutdown begin/completion and
zero-failure END blocks, followed by platform exit status 0. Device-destroyed and
unsupported-screensaver warnings appear inside intentional teardown; their timing
is retained rather than classifying an intentional destruction callback as a
runtime device failure. These logs are not crash dumps.

## Reported flashes

The owner reported a startup dark-blue flash, a white screen with a black upper-left
quarter, then the normal prototype. They also reported dark-blue flashes every
12 checks, approximately once a minute.

These observations match the diagnostic's explicit test-frame sequence:

- `renderer_case()` begins and ends frames while rendering offscreen cases. The
  normal triangle/UI is not drawn in these intermediate frames, exposing the EFB
  clear colour configured as `{8,12,28,255}` in `gx-scene.hpp`.
- `renderer_checks()` draws a white EFB, then a black triangle at half content scale.
  Its expected black upper-left quarter and white lower-right area are precisely
  the known-result allocation/scaling test, with successful readbacks in every run.
- `main.cpp` runs the sweep at startup and whenever `checks % 12 == 0` during
  periodic target recreation. Each run logs the expected nine repetitions.

This is an explanation from the executed source sequence and successful samples,
corroborated by the owner's observed pattern and cadence. No video was supplied
to time individual transient frames. The checklist previously omitted these
visible transitions; it now describes them. No renderer code or tested binary
was changed to suppress the checks or their visible frames.

## Resource observations and limits

The diagnostic samples driver-reported garlic/onion allocation and buffer counts,
main-mspace allocated bytes, fixed heap capacity and available flexible memory.
These are bounded counters from the selected runtime/driver, not a complete
per-allocation leak detector or a measurement of process RSS.

After the first 30-second sample, all three runs hold garlic at 438,697,984 bytes,
onion at 835,584 bytes, driver buffers at 44 and available flexible memory at
396,361,728 bytes. Heap capacity remains 536,870,912 bytes. Main-mspace allocated
bytes fluctuate within these ranges:

| Run | Minimum | Maximum |
| --- | ---: | ---: |
| Cold | 4,679,568 | 4,689,024 |
| Warm 1 | 4,398,432 | 4,489,824 |
| Warm 2 | 4,482,800 | 4,489,680 |

There is startup allocation followed by a plateau in driver counters and bounded
allocator fluctuations, without sustained growth in these observations. Main-mspace
accounting includes reserved thread arenas; fluctuations across launches do not
prove a leak. Audio API errors remain zero; the owner's uninterrupted-tone report
supplies the audible observation. Source-frame counts alone do not measure hardware
underruns or establish game DSP correctness.

No photos/video or display/audio-output device details were supplied. Startup wall
times and some report metadata remain blank. Those limitations are retained; no
game-frame pacing or gameplay performance is inferred. Exact installed package
identity is now owner-confirmed; #15's clean-build pair and binary-difference
review remain outstanding before the maintained platform gate is complete.
