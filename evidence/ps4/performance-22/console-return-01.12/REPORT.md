# Owner return: 01.12 cold and warm performance

The requested database/WAL were subsequently supplied and validated. The
[01.13 candidate](../candidate-01.13/REPORT.md) bundles their 287 descriptions
for startup preparation. The return and request below remain historical evidence;
new cold/warm results for the changed package are still required.

The returned identities, inspections and runtime manifests identify build
`bc90c33b639295f36912`, complete package SHA-256
`d60c319ac16f3e17a5de9357a9f12a897f8209873f42fe6b25715190785af534`.
The owner labels cold/warm, confirms PS4 Slim / 9.00 / GoldHEN v2.4b18 and
representative graphics/audio correctness, and describes comparable running,
rolling, swimming and sword actions in Outset and the first forest sections.
Both logs retain allocated 1280x720 rendering and original 30 Hz logic.

**Both warm samples meet every numerical limit. Both cold samples still fail.**
All four samples complete their two-minute windows. These are provisional
numerical results: physical timing verification remains false, and neither
launch contains a completed recorder shutdown marker. No acceptance is claimed.
Final integrated acceptance remains #23; issue #22 remains open.

## Independent measurements

Limits remain average >=29.5 FPS, p95 <=35 ms, p99 <=50 ms, maximum <=100 ms.
Values below come from raw completed flips and agree with `samples.csv`.

| Launch / scene | Seconds | FPS | p95 ms | p99 ms | Maximum ms | Numerical result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Cold Outset | 120.021617 | 28.753154 | 33.407429 | 66.765600 | 1234.577616 | Average, p99 and maximum miss |
| Cold forest | 120.021611 | 29.969603 | 33.397178 | 33.432956 | 150.151814 | Maximum misses |
| Warm Outset | 120.004939 | 29.998765 | 33.397943 | 33.448591 | 50.060029 | Meets all numerical limits |
| Warm forest | 120.021617 | 30.002929 | 33.396785 | 33.428238 | 50.085830 | Meets all numerical limits |

The transcribed forest `p00` values are identified as p99 by the raw summary.
Maximum intervals slightly over 50 ms do not fail the maximum criterion of
100 ms; their low frequency keeps each warm p99 below 50 ms. No threshold or
quality setting is changed, and no rounding is used to manufacture a pass.
Every scene and launch remains separate in the reviewed analyses.

## Recorder and shutdown evidence

There are 16,554 cold and 17,633 warm completed-flip rows. Both launches have
consecutive raw completion counts/arguments, monotonic presentation/observation
and kernel-read clocks, no recorder `invalid` events and no missing scene.
Maximum kernel-read versus monotonic calibration error relative to the first
row is about 0.0010 ms cold and 0.0013 ms warm. These checks support the
recording method but do not prove physical presentation timing. Both original
owner reports explicitly leave `timing_method_verified=false` with empty notes;
their bytes are preserved. Reviewed metadata records the subsequent clarification.

The owner confirms retrieval **after normal port Quit**, which **returned cleanly
to the PS4 menu**. Unlike the previous return, both ordinary logs now record the
explicit Settings → Quit → Exit sequence, `EXIT code=0`, idle card status and
stages through `shutdown-sdk-stop-requested`. Both last-stage files identify
that stage. There is no later audio-producer-joined/GPU-synchronized/shutdown
completion or recorder `shutdown,complete` marker in the supplied files.
The visible clean return and missing internal completion evidence are both
retained; neither an early retrieval nor a successful internal drain is inferred.
Source order places recorder shutdown after the audio join and GPU synchronization,
so moving file I/O to a worker cannot by itself establish why this later marker
is absent. The underlying shutdown cause is not yet reproduced on the host.

The CLI replay uses the original owner false flag and returns **exit 2** for
both launches. Warm `shortfalls` arrays are empty, but `target_met` remains
false because timing verification and recorder shutdown evidence are missing.
The reviewed analyses retain those invalid reasons rather than overriding them
with the menu's provisional numerical target flag.

## Measured cold bottleneck

Cold Outset records **6,607.918540 ms of blocking shader waits**, with 130 calls,
89 waits over 35 ms and 68 shader-correlated presentation hitches. The maximum
1234.577616 ms interval contains 1195.708258 ms of shader waits across 14 calls.
Cold forest has two waits, 51.533896 and 122.379947 ms; the latter coincides with
its 150.151814 ms maximum. Both warm samples contain **zero shader waits**.
[diagnosis.json](diagnosis.json) retains the largest intervals and counters.
Correlation does not prove every millisecond was compilation, but it identifies
the dominant measured cold-run mechanism without excusing the freezes.

The cold log lists zero cache files before initialization, no bundled
`/app0/initial_pipeline_cache.db`, and zero created/queued pipelines at the first
heartbeat. Its preparation phase lasts about 1.50 ms because there are no known
pipeline descriptions to prepare. The warm log lists retained Dawn/pipeline
databases and WAL files, and the first heartbeat already has 287 created pipelines.
This supports working cache reuse and inadequate cold pipeline coverage rather
than a general inability to hold 30 Hz in these scenes.

During active samples, recorder-flush event durations reach only 0.095670 ms
cold and 0.178120 ms warm. The launch-wide maxima of 2291.283536 and 1306.203344 ms
occur during startup, before the gameplay samples. They are writer operation
durations and are not claimed as synchronous frame-lock stalls. Median heartbeat
diagnostic costs are 1.610937 ms cold and 1.570905 ms warm; isolated input/logging
and OS delays remain possible. The current evidence does not make them the
primary explanation for the two cold maximum intervals.

## Next concrete input

The selected renderer already supports merging a bundled pipeline-description
seed and preparing its known pipelines before gameplay. Its schema checks and
per-configuration version/size checks must remain intact. A validated seed from
the measured route is the next bounded correction to investigate; it is not
yet implemented, packaged or proven to meet cold targets. Fresh effect/state
combinations may still miss coverage and must remain counted if encountered.

This return contains timings and logs but no **01.12 pipeline database**. With
the application fully closed, copy these files together from
`/data/pswaker/cache/bc90c33b639295f36912/` into a new private folder such as
`local-research/performance-22-artifacts/candidate-01.12/evidence/cache-after-warm/`:

- `pipeline_cache.db`
- `pipeline_cache.db-wal` and `pipeline_cache.db-shm`, if present

Keep the originals and sidecars together; do not send only the main database if
a WAL exists. This allows an integrity-checked consistent snapshot and inspection
of actual pipeline descriptions before staging any private seed. No new console
sampling run is needed just to retrieve these files. Existing older diagnostic
cache copies are not substituted for this gameplay route's coverage. The data
will remain private; no driver shader binary or game data is committed.

[original-file-inventory.json](original-file-inventory.json) records supplied
original hashes/sizes. Raw launches, original owner reports, original analyses,
inspections and ordinary logs are retained alongside reviewed copies. There is
no runtime change or new package in this evidence follow-up. Renew measurements
after a material preparation/runtime change, keeping all earlier failures.
