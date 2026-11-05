# Corrected 291-description candidate: failed physical validation

Assessed 2026-11-05 for #148. The exact returned package is the first
[seed correction](../dynamic-seed-correction-148/README.md), SHA-256
`058bd19c4fc4be1782b631ad4e808dbddea4b31530f0e3a599c38d71b93090e0`.
A fresh package inspection reproduces the frozen inspection byte-for-byte.

## Independent replay

| Measured Outset sample | Cold | Warm |
| --- | ---: | ---: |
| Duration (seconds) | 120.003 | 120.019 |
| Returned descriptions / bundled descriptions | 291 / 291 | 301 / 291 |
| Missing descriptions (full configuration comparison) | 0 | 10 |
| Conflicting descriptions | 0 | 0 |
| Raw missing-pipeline wait events | 0 | 10 |
| Total raw wait time (ms) | 0 | 4.890056 |
| Average FPS | 29.9993 | 30.0035 |
| p95 interval (ms) | 33.3985 | 33.3976 |
| p99 interval (ms) | 33.4442 | 50.0012 |
| Maximum interval (ms) | 50.0538 | 50.1175 |
| Intervals over 35 ms | 29 | 37 |
| Shader-correlated hitches | 0 | 0 |
| Completed recorder shutdown | No | No |

The candidate fails the zero-miss requirement. Warm's ten raw waits fall between
58.238782 and 58.538891 seconds after sample resume. Each lasts 0.448915 to
0.569715 ms; being below the hitch threshold does not satisfy zero waits. Raw
events and differences in cumulative per-frame counters independently agree on
ten calls and 4.890056 ms. Cumulative counters were not summed across frames.

Both snapshots preserve all 291 bundled configuration byte sequences. Warm adds
ten GX version-13 descriptions of 2,772 bytes each. Their identities, configuration
digests and capture metadata are in [assessment.json](assessment.json). Capture
`first_frame_used` values are not recorder frame numbers or action timestamps.
Equal counts do not establish a one-to-one mapping between a description and a
wait event. Exact effect, source path and gameplay action attribution remain unknown.

Cold began with no build-specific cache files; preparation completed all 291
descriptions before gameplay, with no preparation errors. Warm retained the cold
database/WAL pair, corroborated by size and digest against its before-init log,
and also completed preparation of all 291 bundled descriptions. Full preparation
took 15,209.6 ms cold and 440.4 ms warm; final drain alone was 14,604.0 and
203.7 ms respectively. Ready counts alone did not predict the later warm misses.

## Owner observations and limits

The [original owner report](owner-report-original.md) reports CE-34878-0 on Quit
again. The returned owner JSON marks active gameplay and graphics/audio correct,
but its action text remains the template. Location, actual action times, first
and repeated break observations, pauses, and whether the error appeared in both
new runs await explicit owner clarification. Earlier observations belong to the
earlier candidate and are not transferred to this package.

Both logs end at `shutdown-sdk-stop-requested`, after an intended `EXIT code=0`
and an idle card. Neither has completed recorder shutdown. These markers do not
establish the crash cause or a successful exit; Quit diagnosis remains #159.
No program or shutdown change is included in this work.

Fresh analyzer runs reproduce both original summaries exactly and return 2.
VideoOut timestamp semantics remain unverified, shutdown is incomplete, and warm
p99 is slightly above the 50 ms numerical limit. No general frame-pacing pass is
claimed. The missing forest sample is outside this bounded Outset return.

## Preservation and next candidate

All 31 original returned files were archived privately and checked unchanged
after replay and correction. [original-file-inventory.json](original-file-inventory.json)
records source-relative sizes and SHA-256 values. Original reports, owner JSON and
summaries are preserved byte-for-byte here; databases, WAL files, executable,
package and raw runtime logs remain private.

The ten discoveries have been incorporated with runtime-capture provenance into
a separate [301-description candidate](../dynamic-seed-correction-148-round2/README.md).
That replacement has passed seed and package checks but has no physical
validation yet. This failed 291-description candidate and its return are retained.
