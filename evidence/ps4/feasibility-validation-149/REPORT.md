# 01.24 bounded feasibility return: seed passes, gate incomplete

Assessed 2026-11-05 for #149. The owner returned cold and retained-cache warm
evidence for the [frozen candidate](../feasibility-149/README.md): program **01.24**,
build `35a453336a0e4b0d432c`, package SHA-256
`578f0d946ebfb3a96cc6d68a0feae040a7d205da1970a9ffdfc9f5d0f8cfc516`.
Independent fresh package inspection reproduces frozen inspection SHA-256
`5c3e316c7146960d129fed75b5cf982c4388317984ade1ba8ec02f4e2109ec44`.
The exact bundled seed remains 301 descriptions, SHA-256
`06b8ef5d5df64e6a1218728550eab209f6a841926392ac18064effce64f17fd8`.

**The seed/membership and observed-wait checks pass. The physical gate remains
incomplete.** The owner confirms correct first/repeated pot breaks, responsive
cold progress, a warm screen lasting less than a second, and preserved saves.
Both normal Quits show `CE-34878-0` and lack completed recorder shutdown. #159
remains the shutdown blocker; no new diagnosis or shutdown fix is claimed.

## Independent replay and preservation

All **45** original returned files were hashed, privately archived and verified
unchanged after analysis. The original narrative, owner forms, analyzer results,
raw logs, database/WAL pairs and all previous candidates are retained.
[original-file-inventory.json](original-file-inventory.json) lists relative names,
sizes and digests. Actual packages, descriptions, captures and ordinary logs remain
private. [assessment.json](assessment.json) records the data-free result and limits;
[owner-followup.md](owner-followup.md) records the separate owner clarifications.

Both original analyzer summaries reproduce byte-for-byte. Fresh public
`pipeline-seed` commands reproduce both returned standalone databases **and**
manifests. The public full-description comparator passes independently for cold,
warm, and a combined comparison including the static/dynamic observation assets
and prior compatible corpus. All returned type/hash identities, versions, sizes
and complete description bytes are in the frozen seed; missing/conflicting
descriptions and additions are zero. Different snapshot file hashes reflect
capture metadata rather than different configurations. No seed correction or new
package is indicated by this return's description coverage.

The existing analyzer and coverage regression suites pass **26 tests, one
environment skip, no failures**. Runtime/tool code is unchanged; the preparation
commit's full-suite result remains the separate 254-test record. New evidence
links/JSON, original-file preservation and Git whitespace checks are also verified.

The supplied narrative says version `01.23` and repeats performance values that
disagree with this return. The installed manifest, freshly inspected SFO/package,
ELF/build identities and raw recorder bind **01.24**. The raw cold maximum is
50.0552 **ms**, not the narrative's `50.059s`; warm is 50.0823 ms. Originals were
not edited. Measurements below come from the replayed raw evidence.

## Preparation, caches and observed actions

| Measurement | Cold | Retained-cache warm |
| --- | ---: | ---: |
| Build-specific files before initialization | 0 | 4 |
| Full preparation, seed loading through creation/cleanup (ms) | 17,392.8 | 446.8 |
| Final preparation-screen drain only (ms) | 10.5 | 228.7 |
| Launch-clock time to preparation handoff (ms) | 44,315.9 | 1,359.8 |
| Ready / total at successful handoff | 301 / 301 | 301 / 301 |
| Pending / preparation errors | 0 / 0 | 0 / 0 |
| Captured descriptions matching frozen seed | 301 / 301 | 301 / 301 |
| Raw missing-pipeline wait events in available whole-launch log | 0 | 0 |
| Full-launch frame shader counter delta | 0 calls, 0 ns | 0 calls, 0 ns |

The cold return logs an empty build directory and import of all 301 rows with
zero skipped. Each of the four cold-return cache files matches the warm
before-initialization size and SHA-1: pipeline database/WAL and Dawn database/WAL.
Warm logs that the exact bundled seed is already merged. This establishes
compatible retained-cache reuse, including driver caches, rather than treating
the owner's cold/warm labels alone as proof.

Both logs reach complete=true, pending=0 and `known-shaders-prepared`, without
preparation errors, before the recorded gameplay phase. Raw target dimensions are
1280x720 and the surface is RGBA8Unorm. The full preparation measurement uses the
retained performance-clock start/end timestamps, not the brief foreground
`shader-preparation` phase. Cold content validation lasts 42.513 seconds and
overlaps worker preparation; warm reuses the image-check record. Do not add
overlapping phases or attribute the entire launch difference to shaders. These
times are **not** filmed launch-to-first-control measurements; those were not
supplied. The owner separately confirms responsive cold progress and a warm
checking/preparation screen shorter than one second.

The owner followed the visible-ready marker and timed two-minute Outset sample:
view intact pot about 10 s, first break about 10 s, second about 40 s, then
movement/turns/rolls, followed by three additional minutes in the area. Both breaks
rendered correctly in both runs. Exact action timestamps/methods and unmentioned
pauses are not independently established. Imported seed entries do not prove
every effect was physically exercised. No hidden warmup or additional discovery
route is reported or required.

There are zero raw `shader-wait-ns` events, including outside the measured sample,
and full-launch frame counters stay at zero. This is independent of membership
and hitch-threshold classification. The crash prevents confirmation of final
recorder flush/close; the zero-wait claim is limited to the returned recording.

The available corpus remains **301**, with no growth during this return. Its
history is 287 runtime baseline + one generated static addition + 13 runtime
corrections. The isolated dynamic description was already covered. The two
generated controls cover two distinct descriptions; they do not turn the entire
corpus into automatically generated or physically observed content.

## Startup and subsequent resource observations

There are **116 cold** and **79 warm** resource observations. All flexible-memory
queries return zero (success). Startup has 42 cold and five warm observations,
through the successful preparation handoff:

| Sampled startup quantity | Cold | Warm |
| --- | ---: | ---: |
| Maximum tracked garlic allocation (MiB) | 418.797 | 473.719 |
| Maximum main-mspace allocated (MiB) | 20.405 | 17.493 |
| Minimum flexible memory available (MiB) | 369.000 | 369.000 |

These are **sampled maxima**, not true peaks. Warm's final-drain sample is higher
than its post-cleanup sample; cold has already finished worker preparation during
content validation. The different sample timing cannot establish that cold's true
peak is lower. Before-renderer zero driver counters also mean no tracked device
yet. There is no evidence of a startup allocation failure in these logs.

The timed sample has 23 interior resource observations per run. Subsequent logged
resource observations after sample end span 175.652 s cold (36 samples) and
180.515 s warm (37 samples):

| Subsequent sampled quantity | Cold | Warm |
| --- | ---: | ---: |
| Garlic allocation (bytes) | 456,458,240–456,523,776 | 456,458,240–456,523,776 |
| Onion allocation (bytes) | 5,996,544 | 6,078,464 |
| Buffer count | 57 | 58 |
| Main-mspace allocated (bytes) | 316,265,248–318,328,016 | 314,793,616–317,275,664 |
| Flexible memory available (bytes) | 362,807,296 | 362,807,296 |

Flexible availability holds at **346 MiB** throughout both timed samples and the
subsequent observation windows. Garlic grows by 64 KiB over each subsequent
window, onion/buffer counts remain constant, and main-mspace varies within about
2–2.5 MiB rather than showing unbounded growth in this short return. These
observations support bounded startup/subsequent-gameplay resource viability for
this corpus. They are not a leak test, a full-game budget or evidence of normal
termination.

The first subsequent resource observation is about 40.735 s after sample end in
cold and 23.947 s in warm. Do not fill those gaps or infer continuous active play
from the owner's stated three minutes. Sample-relative alignment is approximate:
it relates the preparation RESOURCE launch clock to the immediately following
loading-phase performance timestamp. Raw observation times and per-phase ranges
are retained in [resource-observations.json](resource-observations.json).

Garlic/onion count driver buffers/images; main-mspace includes reserved thread
arenas; flexible availability is a separate pool query. They are not additive
process-memory totals. Heartbeats tagged gameplay can include loading/title/menu
activity, so active-sample and subsequent windows are separated in the assessment.
Sampling misses transients, especially blocking initialization/synchronization;
no cost or coverage is extrapolated to a larger/full-game corpus.

The [interactive timing/resource chart](observations.html) shows the logged
durations and all sampled counters without exposing private capture content.

## Layout compatibility and timing limits

The host/PS4 schema/configuration contract is unchanged and all 301 complete
descriptions match real target recordings. Host BGRA driver objects are not
installed; the PS4 prepares its own RGBA pipelines. The source identified by the
candidate schedules scene/offscreen layouts and deduplicates equal keys; readiness
includes successful creation and cleanup. Source analysis using the retained
host/target contract offsets finds 295 GX descriptions without destination-alpha
replacement and five requiring replacement. None of the 300 GX descriptions
requires source-alpha blending with destination-alpha, so no extra alpha prepass
is required by that branch for this frozen corpus. The remaining description is
the type-0 v5 record.

However, the returned logs expose aggregate readiness/native creation counts,
not a per-configuration compiled layout-key/pass trace. This source reconciliation
and absence of observed waits support the selected run, but do **not** independently
certify every required layout variant. Explicit per-variant trace evidence remains
an open requirement. Other cameras/effects, companion model shards, actor
lighting/collision and the full-game inventory remain outside the generated pilot.

Both two-minute samples average about 30 FPS. Raw cold p99 is 33.4606 ms and maximum
50.0552 ms; warm p99 is 33.4694 ms and maximum 50.0823 ms. Both analyzers return 2:
VideoOut timestamp semantics are still unverified and completed recorder shutdown
is absent. Forest is outside this bounded route, rather than a new owner task.
Neither return is accepted as a general frame-pacing or physical timing pass.

## Disposition and next work

Both logs show intended `EXIT code=0`, idle card status and
`shutdown-card-finished`, then stop at `shutdown-sdk-stop-requested`. Neither raw
recorder has `shutdown,complete`. The owner reports `CE-34878-0` for both. The
failure persists on 01.24; the final marker is not a root-cause diagnosis.

Saves are owner-confirmed preserved from previous runs. Before/after byte
inventories and a settings-preservation confirmation were not supplied, so do not
upgrade that observation into byte-identical profile preservation. Exact visible
launch-to-control and per-variant traces also remain unavailable.

Keep #149 **open**, with expansion gated. The next agent work is resolving #159's
shutdown diagnosis/fix and arranging targeted layout evidence; do not send the
owner through another unchanged-candidate run. Then freeze the corrected candidate
and repeat affected physical checks, carrying forward this valid bounded evidence
without inheriting a pass across build identities. Remaining eligible observation
gaps need actual evidence or an explicit owner decision; observed failures cannot
be waived as performance averages.

Owner options are to resolve the known blocker and repeat the bounded checks;
request targeted instrumentation/evidence for remaining gaps; or explicitly
re-scope downstream expansion. This return does not establish resource/generation
infeasibility, close the gate, change #136 or restore a manual campaign.
