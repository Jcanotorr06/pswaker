# Console frame pacing (#22)

The [owner accepts current performance for the initial release candidate](../../evidence/ps4/performance-22/OWNER-DECISION.md)
and defers further optimization to a future version. The numerical targets and
sampling procedure below remain reference goals and diagnostic tools. More
optimization runs are not required before proceeding with the initial release
candidate; existing measurements and verification limits remain recorded.

This instruments the existing playable baseline. A built candidate is **untested
on the console** until its owner return identifies the installed package and
binary. Outset and forest are independent samples; extended play to Dragon
Roost, startup timings and increasing pipeline counts do not establish a pass.
Final integrated acceptance remains issue #23.

## Measurement boundary

The original 30 Hz logic, stock textures, synchronous pipelines, selected
renderer and 1280x720 allocation remain fixed. The game tags each recording with
`pc_frame_count()+1`; port/preparation screens carry zero. Aurora captures that
tag with its render callback and queues it immediately before surface present.
The selected Mesa WSI waits for the GPU fence and submits FIFO flips in order.
The `sceVideoOutSubmitFlip` linker wrapper associates that queue with Mesa's
unique flip argument. This does not wait for completion on the game thread.

A separate observer polls `sceVideoOutGetFlipStatus` every 1 ms. Only a changed
completed-flip count produces a row. Its argument must match a submitted record.
Repeated refreshes of an unchanged buffer generate no extra game frames. Raw
VideoOut process time, TSC timestamp, completion count and argument are preserved
alongside the independent monotonic observation time. Intervals use completed
flip TSC differences divided by `sceKernelGetTscFrequency`, not submission time,
CPU loop throughput, VI retraces, polling times or a host FPS overlay.

This interpretation is a **candidate timing method requiring hardware
verification**, not a claim that reverse-engineered headers prove physical
display timing. ABI source: the unchanged selected Mesa
`src/vulkan/wsi/wsi_common_videoout.c` and selected OpenOrbis
`include/orbis/_types/video.h`. Their 64-byte layouts agree. The recorder checks
timestamps against `sceKernelReadTsc`, rejects timestamps changing without a
completion, rejects skipped counts/arguments, and retains both raw clock fields.
New captures also export `read_tsc`, the kernel clock at observation time.
The analyzer compares that clock with monotonic observations (100 ms tolerance)
and requires timely completion observations at both launch endpoints. A late
observation with consecutive completions records `observer-delay-ns`; age alone
does not disable later samples. Future/nonmonotonic timestamps and missing
completions remain invalid. Legacy captures without `read_tsc` retain the
conservative completed-flip versus observation-clock check. Every
completion must remain mapped, ordered and monotonic; it never interpolates
missing timing. Driver clock semantics and the tagged output still need owner
verification against what the console actually displays. If unavailable or
unreliable, return the limitation and obtain owner agreement on substitute
evidence **before claiming a pass**. Do not set `timing_method_verified` merely
because host compilation or rate checks succeeded.

## Sample and hitch accounting

In port settings, choose **Measure Outset** or **Measure forest**. Cross arms a
new numbered sample and resumes after neutral release. Its first completed game
presentation establishes the baseline; the first subsequent presentation at or
after 120 seconds closes it. Include the whole closing interval, even if it
contains a long freeze; never clip that interval at the deadline. Average FPS
is the number of intervals divided by their total elapsed presentation time.
Percentiles use nearest rank, `ceil(p*N)`, on all positive intervals. Each sample
independently targets average >=29.5 FPS, p95 <=35 ms, p99 <=50 ms, max <=100 ms.

The resume marker and time to the first observed game frame are retained
separately so a slow first resumed frame is visible rather than silently lost
at the baseline. Do not claim an overall gameplay pass while an unexplained
resume freeze remains. Port pauses, input recovery, actual stage changes,
missing frames and unfinished shutdowns produce incomplete/invalid samples;
they are retained, never silently dropped in favor of a later successful run.
A queued game frame can complete after a manual pause ends a sample. Analysis
uses the explicit monotonic end marker, counts these outside-boundary arrivals,
and preserves them in the full raw launch rather than changing the ended sample.
Scene-creation requests are observations, not proof of a visible transition:
they do **not** automatically reclassify an active-gameplay hitch as loading.

Aurora's blocking pipeline lookup records time spent creating or waiting for a
missing pipeline, including the first resumed frame. An active shader wait
over 35 ms is counted separately as a shader hitch. Raw wait events and totals
remain available for smaller stalls. A presentation interval >35 ms with >=1 ms
of shader wait is also counted as **shader-correlated**. Correlation does not
prove the entire pause was shader compilation: scheduling, GPU work, resource
loading and I/O can overlap. Prepared shaders never excuse active-gameplay
freezes. The 01.13 candidate uses the selected renderer's existing bundled
pipeline-description seed path to prepare the 287 configurations recorded on
the returned 01.12 route. Seed bytes, source database/WAL hashes and counts are
bound to the complete-package manifest and fresh inspection. Driver shader
binaries are not bundled; a cold disposable cache still starts empty. Known
pipelines can compile during renderer startup, overlapping other startup work,
before the existing preparation screen drains the remaining queue. Its final
wait is not the total compilation time. Record startup/preparation separately
and preserve the ordinary log's seed merge/count observations. New state/effect
combinations may remain uncovered; their gameplay stalls still count. No quality,
target, synchronous missing-pipeline policy or selected driver stack is changed.

Startup, installed-content validation, storage checks, shader preparation and
initial loading have separate monotonic phase markers. The owner can mark
loading/transition start before a doorway, and visible gameplay ready afterward.
Those manual measurements include port-menu operation latency; record the
visible boundary in notes/video as well. Stage-ready and scene-request records
are diagnostic landmarks, not substitutes for visible completion. No numerical
loading-time limit is introduced.

## Preserved evidence and analysis

Each launch creates `/data/pswaker/logs/performance-XXXXXX/` without reusing an
earlier launch. Retrieve its whole directory, plus `platform.log`,
`platform.prev.log` if applicable, `last-stage.txt`, and any crash log **before
another launch overwrites the ordinary logs**. The unique directory contains:

| File | Contents |
| --- | --- |
| `identity.json` | Compiled build, cache path, timing method/frequency, fixed quality contract |
| `frames.csv` | Completed flips, raw clocks, game/sample tags, stage/room, queued time, shader counters |
| `events.csv` | Phase boundaries, sample arm/resume/end, scene/stage observations, shader waits and timing errors |
| `samples.csv` | FTP-readable per-sample duration, FPS/percentiles/max, shader correlation count and provisional numerical target |

The live status is also visible in port settings. A zero shader-correlated
count does not prove hitch freedom. A zero/empty summary is not a pass. A crash
may leave the final buffered rows missing; such a sample is incomplete.
Logging and polling have overhead; measurements describe the instrumented
candidate. Keep the exact instrumented binary and all failures. Resource
observations (driver garlic/onion/buffer bytes, main-mspace allocation,
available flexible memory) and audio DMA/output diagnostics accompany the
ordinary five-second heartbeat. They are observations, not universal leak or
audio-correctness guarantees.

Follow-up builds record `diagnostic-input-ns`, `diagnostic-heartbeat-ns` and
`diagnostic-recorder-flush-ns` events to measure these operations directly.
They are elapsed CPU/operation durations, not proof of GPU cost or sole stall
causality. The selected release game keeps FTP log output but omits duplicate
`sceKernelDebugOutText` output when `PS4_DEV_TOOLS=0`; developer builds retain it.
Evidence rows use a bounded 1024-row writer queue. Only its worker writes or
flushes the CSV streams during gameplay; storage cannot hold the recorder's
frame/submission lock. Queue exhaustion and write/flush errors invalidate the
launch rather than silently dropping evidence. Sample-end durability is queued;
normal Quit drains the queue before final flush/fsync/close. A crash can still
lose queued or buffered rows. Writer-flush duration events describe storage
work, which can overlap gameplay, rather than a synchronous frame-thread stall.

Copy [frame-pacing-owner.example.json](../../platform/ps4/frame-pacing-owner.example.json) into
the private returned launch, fill in actual package/build/platform/cache and
sample observations, then run on Linux/WSL2:

```bash
python3 platform/ps4/frame-pacing.py /path/to/returned-launch \
  --inspection /path/to/inspection.json \
  --owner /path/to/owner.json \
  --output /path/to/new-analysis-directory
```

Keep ordinary logs inside `returned-launch` as additional original files.
The tool copies the launch, inspection and owner return, inventories their
SHA-256 hashes, exports each sample's raw rows separately, and writes
`summary.json`. It reports every sample and every shortfall; no aggregate FPS
can hide a failing sample or scene. Exit 0 means all supplied samples meet the
individual criteria and both scenes are present; 2 means invalid/incomplete
samples, missing scenes or measured shortfalls; 1 means an input/identity error.
These exit codes never accept the final integrated package or replace the
required cold/warm/relaunch coverage. Preserve separate analyses for separate
launches and return all of them.

The [owner checklist](Frame-pacing-checklist.md) specifies comparable actions,
cache handling and evidence renewal. A material graphics/runtime/build change
requires new affected platform evidence; an earlier binary's pass is retained
only as history.
