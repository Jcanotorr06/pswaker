# Version 01.01 console result: startup recovered, graphics gate failed

The owner installed and ran version 01.01 as instructed and reconfirmed PS4 Slim,
firmware 9.00, GoldHEN v2.4b18 on 2026-10-22. Their observation: no RGB triangle was
ever visible, the background was black, and the purple swatch, summary text and
quiet continuous tone were present as expected. The supplied three run folders
are under `local-research/diagnostic-artifacts/sdl-video-fix/output_logs`.

This records supplied evidence, not a new console execution or a fix. The tested
build is `3a73181f6dfdb86ca4b4`; its package/source identities remain in the
[version 01.01 build report](../sdl-video-20261021/status.md).

## Capture and association

[capture.py](capture.py) reads the original files without changing them. It hashes
all 27 supplied files, including cache databases, in
[retrieved-files.json](retrieved-files.json), extracts only the latest `BEGIN`
block from each appended diagnostic/runtime log, and checks identity, failure
counts, successful purple readback counts and persistence association. Original
files and cache databases remain local; only stage/runtime/display extracts and
their summary are published on this disposable source branch. Embedded manifests
are omitted from extracts because the inspected build already preserves them.

```text
Run 1: launch=2 checks=120 failures=241 purple=120/120; evidence captured
Run 2: launch=3 checks=120 failures=241 purple=120/120; evidence captured
Run 3: launch=4 checks=120 failures=241 purple=120/120; evidence captured
```

Reproduce the evidence summary in WSL2, passing the original `output_logs` path:

```bash
python3 prototypes/ps4-platform/evidence/aurora-results-20261022/capture.py /path/to/output_logs
```

The original diagnostic snapshots contain two, three and four `BEGIN` blocks,
respectively, including earlier history. Counting entire files would duplicate
previous launches. The per-run folders here contain the isolated current blocks;
[summary.json](summary.json) holds their derived results and resource ranges.

## Demonstrated operations and failed checks

| Owner run | Runtime launch | Cache entries before Aurora | Loop frames | Checks | Failures |
| --- | --- | --- | --- | --- | --- |
| 1 | 2 | 0 | 36,772 | 120 | 241 |
| 2 | 3 | 2 | 35,979 | 120 | 241 |
| 3 | 4 | 2 | 35,872 | 120 | 241 |

Each current run reaches shutdown after at least 600 seconds. The user followed
the cold/warm instructions; the initial cache counts corroborate that sequence.
All runs select SDL's dummy placeholder and create Aurora's Vulkan adapter/device.
The adapter reports AMD Liverpool (PS4), RADV BONAIRE, Mesa 26.0.8
`git-60e95b7878`. The platform reports a 1920x1080 display at 59,940 mHz and FIFO
presentation. This supersedes the earlier startup failure; it does not validate
the whole graphics stack.

Every run has precisely these failed checks before its final counter:

- One `internal-render-size`: observed **569x320**, required **1280x720**. The
  1920x1080 display surface is a separate setting and cannot satisfy this check.
- 120 `Aurora-EFB-known-white-readback` failures.
- 120 `Aurora-offscreen-known-white-readback` failures.

The failed white checks agree with the owner's missing geometry/black-background
observation. The current checker records only a Boolean failure, so these logs
do not distinguish a bad pixel value from incomplete mapping, identify a bad
coordinate, or prove that the driver is responsible. Successful copy/create/
resolve return values do not override failed output comparisons.

In contrast, all 120 raw WebGPU textured depth/blend/copy/readback checks in each
run return `(128,0,127,255)` as expected. The owner sees that purple swatch and the
text overlay. These prove those particular operations/presentation, not Aurora GX
geometry, EFB correctness or game performance. The raw test and the GX tests are
different paths.

Constructor/TLS/once/condition-variable/atomic-wait/file-replacement preflight
ends with zero failures on each run. Previous-launch checks pass; preserved
state advances 2 -> 3 -> 4. Each run logs disconnect/reconnect transitions and a
passing deliberate-resume check, with no logged neutral-input failure. Synthetic
audio ends with zero API errors, and the owner reports the expected continuous
tone. Source audio-frame counters are not hardware-underrun measurements.
Useful files were retrieved after all three runs. These are synthetic runtime,
input/audio and file-persistence observations, not game DSP or save validation.

## Resource and teardown limits

All runs have 21 resource samples through approximately 600.3 seconds. From the
60-second sample onward, driver garlic bytes are fixed at 430,276,608, onion at
835,584, buffer count at 42 and available flexible memory at 396,361,728 bytes.
The startup increase is followed by a plateau. Main-mspace allocation ranges
over that interval are 3,979,904-3,994,016; 3,734,096-3,830,672; and
3,816,640-3,830,672 bytes, respectively. They fluctuate and have a small final
increase; no growing driver allocation trend is observed. This instrumentation
does not measure every live allocation or certify absence of leaks.

After every final `END ... failures=241`, teardown logs buffer-mapping abortion
because a buffer was destroyed, device loss because the device was destroyed,
and an unsupported screensaver operation. These messages are outside the printed
final counters. They must be reviewed during the follow-up; the supplied evidence
does not establish an in-loop device loss, a crash, or clean callback draining.

## Decision and next boundary

The bounded platform trial has a **negative result**: version 01.01 fixes the
observed SDL startup boundary and demonstrates several platform operations, but
fails the agreed diagnostic graphics acceptance. It cannot unblock game
integration or final specification approval, and it establishes no 720p game
result. No replacement package was built in this evidence-review session.

The newly sharp question is whether a corrected/instrumented Aurora harness can
produce visible GX geometry, known EFB/offscreen pixels and actual 1280x720
internal rendering on the same stack. First distinguish diagnostic configuration
and GX state/coordinate/frame contracts from a rendering-stack defect. Any host
reproduction must identify its seam; an evidence parser is not a rendering replay.
If hardware evidence invalidates the selected candidate, reopen the existing
architecture decision rather than silently substituting a stack.

Use a bounded follow-up prototype for that question, including sampled expected/
actual pixels and completion statuses, actual sizing after queued changes, and
teardown callback completion as needed. A correction still needs the owner to
observe geometry/background and repeat all three successful cold/warm ten-minute
runs with zero failed checks under the existing acceptance contract. Unchanged
01.01 runs cannot clear these deterministic failures.
