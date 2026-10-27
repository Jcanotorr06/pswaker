# Owner return: 01.10 cold and warm performance

The owner returned samples for build `8c892c5b54b28d9f41da`, complete package
SHA-256 `b6b47e7031c83eee06583e78eac456cec625b5477aff1765476fdb7f1d1a47f8`.
Runtime manifests, both identity files and inspections agree with this binary.
The owner confirmed Slim / 9.00 / GoldHEN v2.4b18, active gameplay and correct
representative graphics/audio, with comparable running, rolling, cutting grass
and trees in Outset and the first two forest sections. Both ordinary logs show
an allocated 1280x720 internal target. Cold startup lists zero cache files;
warm startup lists four retained Dawn/pipeline database and WAL files.

**All four samples retain measured shortfalls. No performance pass is claimed.**
The owner subsequently clarified that these files were copied **before Quit**
and there was **no video comparison**. Missing shutdown markers therefore do
not establish a shutdown failure. The original owner JSON's true timing flag
and example verification notes are preserved unchanged as `owner-*-original.json`.
Reviewed copies set the flag false and record the clarification. Clock/count/
mapping checks support diagnostic use, but physical timing verification is still
pending; no substitute method or relaxed target is approved.

## Individual measurements

Values below use raw completed-flip evidence within the explicit sample markers
and agree with `samples.csv`. Limits remain average >=29.5 FPS, p95 <=35 ms,
p99 <=50 ms, maximum <=100 ms. Strict misses slightly above 50 or 100 are retained;
59.94 Hz scanout quantization is not permission to round a miss into a pass.

| Launch / scene | Duration (s) | FPS | p95 ms | p99 ms | Max ms | Outcome |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Cold Outset | 108.826939 | 28.402894 | 33.415084 | 83.419660 | 1051.065828 | Paused early; average, p99 and maximum miss |
| Cold forest | 120.021590 | 29.711321 | 33.398314 | 50.016825 | 233.526269 | p99 and maximum miss |
| Warm Outset | 120.004933 | 29.773776 | 33.401282 | 50.052677 | 100.097233 | p99 and maximum miss |
| Warm forest | 120.021616 | 29.769638 | 33.398196 | 50.049602 | 133.471049 | p99 and maximum miss |

The owner's transcribed cold-Outset p99 was 50.03 ms. Both returned `samples.csv`
and reanalysis give 83.419660 ms; this discrepancy is retained, not averaged.
The 108.83-second Outset attempt is useful failure evidence but does not meet the
two-minute sample requirement. One frame tagged before the pause completed after
the end marker. The old analyzer counted it and reported 108.860306 seconds /
3092 intervals rather than the console's 108.826939 / 3091. The corrected analyzer
excludes it from that ended sample, reports one outside-boundary presentation,
and preserves it in the complete launch CSV. The sample remains failed/incomplete.

`cold/summary.json` and `warm/summary.json` retain every scene independently.
All remain invalid for acceptance because timing verification and post-Quit
retrieval are missing; the numerical shortfalls are reported separately.
The original supplied analysis summaries remain alongside the reviewed results.
[original-file-inventory.json](original-file-inventory.json) identifies every
supplied original file by hash/size, including private duplicate sample exports.
Required raw CSVs, manifests, original owner reports and ordinary logs are
preserved here; the entire original return remains in the private handoff tree.

## Diagnosis and its limits

Trace replay through `frame-pacing.py` deterministically reproduces the
shortfalls. These are recorded console measurements, not a host gameplay replay.
Four hypotheses were ranked before probing: cold shader waits, synchronous
diagnostic output, CPU/GPU deadline misses, and recorder flush/lock overhead.

The cold Outset sample records **87 shader waits over 35 ms**, totaling
6460.038942 ms of blocking pipeline work. Of 26 intervals over 90 ms, 25 carry
shader work. The 1051.065828 ms interval at game frame 3773 carries
1015.052152 ms of shader wait across 11 missing-pipeline calls. This is strong
evidence of a shader contribution, not proof that shaders explain all frame time.
Cold forest records two >35 ms shader waits totaling 299.912052 ms; its
233.526269 ms maximum carries 203.974 ms of shader work.

Warm Outset records three >35 ms shader waits (four wait calls totaling
150.958116 ms). Warm forest records zero shader waits, yet has 133.471049 ms and
116.763 ms intervals. Those residual stalls cannot be blamed on shader creation.
[correlation-cold.json](correlation-cold.json) and
[correlation-warm.json](correlation-warm.json) retain the longest intervals and
associated counters. The cold diagnostic selection also retains the late frame;
the acceptance metrics above use the explicit boundary.

Warm heartbeat-to-resource log timestamps span about 44–45 ms for the periodic
diagnostic burst. Many non-shader 66–83 ms intervals follow its five-second
cadence. The real native `say()` path writes the FTP log and synchronously calls
`sceKernelDebugOutText` for every line, even though this game sets
`PS4_DEV_TOOLS=0`. A recorder regression using that actual native function and
a deterministic slow external debug service produced a 103 ms presentation
interval instead of 33 ms for seven diagnostic lines. Suppressing the unused
debugger sink in release mode makes that test pass while preserving all seven
log lines. It demonstrates the mechanism; it does **not** measure the actual
console syscall's isolated cost or establish that every warm stall is fixed.

The follow-up candidate removes only that release debugger duplication, retains
the FTP log and adds durable diagnostic-cost event records for input logging,
heartbeat logging and recorder flushes. These targeted measurements distinguish
the remaining hypotheses on the next console return. They do not change stock
textures, 720p, 30 Hz logic, synchronous shaders, rendering or audio quality.
The cold shader hitches and unexplained residual spikes remain open.

Content validation lasted approximately 45.36 s cold and 40.38 s warm. Phase
markers include storage/preparation/initial loading separately, but the initial
loading-to-owner-marker interval includes time spent at menus and owner action;
it is not a pure loading-time measurement. Manual transition markers span
22.76 s cold and 8.41 s warm and similarly include port-menu/owner latency.
No loading-time target is invented. Returned resource and audio counters remain
in the ordinary logs; they do not replace the owner's correctness observations
or establish leak freedom, underrun freedom or post-Quit drain success.
Across these captured launches, garlic allocation reaches 456,327,168 bytes,
onion 5,996,544 bytes and 57 tracked buffers. Main-mspace allocation peaks at
318,738,672 bytes cold / 318,876,624 warm and ends at 318,682,384 / 318,505,920;
available flexible memory ends at 365,953,024 bytes in both. These are whole-route
observations including startup and menu time. Captured queue-drop, clock-skip,
stream-error and backend-output-error counters remain zero in both logs;
physical underruns are unsupported and shutdown/drain was not captured.

## Next checkpoint

Use the new candidate's report and exact hashes. Repeat both independent full
two-minute scenes, preserve the first resumed frame's latency, retrieve after
normal Quit, and provide visible timing corroboration or report why it is
unavailable. Retain this failed/partial 01.10 evidence. A new binary's results
must not inherit these measurements or any older platform pass.
