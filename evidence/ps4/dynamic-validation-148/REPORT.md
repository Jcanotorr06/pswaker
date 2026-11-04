# Returned dynamic pilot assessment (#148)

Assessed 2026-11-04 for [#148](https://github.com/Jcanotorr06/pswaker/issues/148).
**This return does not pass the pilot's physical validation.** Both snapshots
contain three descriptions absent from the frozen seed. The cold recording has
three missing-pipeline waits, including 61.035 ms during the measured pot sample.
The owner confirms `CE-34878-0` on **Quit game** in both runs; neither recorder
has a completed shutdown. Warm's zero waits follow reuse of the learned cache
and do not establish coverage by the shipped seed.

The original generated pilot [report](../dynamic-collector-148/README.md) and
[identities](../dynamic-collector-148/pilot.json) remain unchanged.
[assessment.json](assessment.json) records the replayed results, exact missing
identities, source hashes and selected log evidence. This is an assessment of
the returned candidate, not a corrected package or an acceptance waiver.

## Exact candidate and preserved return

| Item | Identity |
| --- | --- |
| Program / cache ID | `01.23` / `6e885683f47a49a119ae` |
| Complete package SHA-256 | `14069c0c7776e330ae9441f81e7537ba95859dfa70bd4b65059d6ec5374b4328` |
| Matching ELF SHA-256 | `400de6f1bb42fb4fc79f9399f290d2f0ee292e58ea03e4f8eea9c2e4dd7c32ab` |
| Frozen seed SHA-256 | `37779b102fff3c8bd71330c77a78efd49ac9881b89bd17c5743bacb4daa281b4` |
| Frozen seed size / descriptions | 1,204,224 bytes / 288 |
| Fresh inspection SHA-256 | `8afea3c9d7e0f290724eb6cc56868b76deb2ad704e1bf0e7f8791e56d99424da` |
| Owner-reported console | PS4 Slim / firmware 9.00 / GoldHEN v2.4b18 |

A new extraction/inspection of the supplied package, using its matching ELF
and a separate private working directory, reproduced the frozen inspection
exactly. Both returned analyzer inspections also match. The package, seed and
program were not modified or repackaged for this assessment.

[original-file-inventory.json](original-file-inventory.json) inventories all
**127** returned files, including the extra host-tool copies in the cold folder.
The complete return was copied to a new private archive and verified against
that inventory before replay. All original hashes remained unchanged afterward.
[owner-report-original.md](owner-report-original.md), both owner JSON files and
both original summaries are retained byte-for-byte. A narrow Git whitespace
attribute preserves the original report's CRLF and trailing spaces.
Actual databases/WALs, ordinary logs, raw recordings, package and ELF stay
private. The original analysis, booleans and missing observations were not edited.

## Owner-confirmed actions

The separate [owner clarification](owner-followup.md) confirms both runs used
the two pots next to the Outdoor Bath on Outset Island. The owner viewed them
for about ten seconds, broke the first around 10 seconds, broke the second
with the sword around 40 seconds, and rolled back and forth until two minutes
had elapsed. The breaks rendered correctly. Both runs showed `CE-34878-0` on Quit.
The first break method was not specified; it is not relabeled as the originally
planned lift/throw. These times are approximate, without frame-annotated video.

The raw sample is `sea`, room 44, in both launches. One complete two-minute
sample per launch was supplied. The owner JSON also contains a sample-2 template;
there is no second raw sample, so none is inferred. Its action text is still the
handoff placeholder. The later clarification supplies action context separately
and does not rewrite that original JSON or retroactively verify physical timing.

## Preparation and compatible-cache reuse

| Observation | Cold | Warm |
| --- | ---: | ---: |
| Build-cache files before initialization | 0 | 4 |
| Configurations ready / total at preparation completion | 288 / 288 | 291 / 291 |
| Full preparation, including work before final screen | 14,672.6 ms | 440.9 ms |
| Final preparation-screen drain | 14,131.8 ms | 278.8 ms |
| Logged startup to preparation complete | 15,813.7 ms | 1,626.9 ms |

Cold logs 288 bundled rows merged and zero skipped, then ready=total, pending=0,
complete=1 and `known-shaders-prepared`, with checked errors zero, before loading.
Warm logs that the bundled seed was already merged and prepares 291 known
descriptions. The cold returned database and WAL SHA-1/size pairs exactly match
warm's `CACHE before-init` inventory. This corroborates compatible cache reuse,
including the learned records; it does not turn them into bundled descriptions.

The total-preparation clock starts before the final screen: the final drain
alone understates full preparation. Logs establish completion for included
configurations on this PS4, but no video or separate visible-progress observation
was supplied. No memory/resource-scaling pass is inferred; #149 retains that work.
Save/settings backup and preservation inventories were not returned.

## Independent seed membership and raw waits

Fresh `complete-package.py pipeline-seed` snapshots reproduced both returned
seed reports and database bytes exactly. Each snapshot has 291 descriptions:
all **288** frozen descriptions with identical full bytes, plus the same
**three** absent identities. There are zero same-identity/description conflicts.
The unchanged public `verify-coverage.py` rejects each snapshot with exit **1**,
`contains configurations missing from the candidate; extend coverage first`.

| Missing type-1 identity | Complete 2772-byte description SHA-256 |
| ---: | --- |
| `-998174050250713549` | `8953b0009777ab7de30f1112e943f8d404a96ba8015729a8d8fcd11dee6b60fe` |
| `1288118228291800766` | `29b1cbf3caf484e4347b671e6eb781ae0c515b86de6ca120189a1f7ab91596de` |
| `3435039316153706867` | `7821518846c80640c4d340e8ba7acba4a59f19adad2b43179ac2b433589d5bdf` |

All 291 cold/warm descriptions agree by identity and complete bytes. Their
standalone SQLite hashes differ because one `first_frame_used` metadata value
differs; that field is not configuration identity or a verified action timestamp.
No direct association between a missing identity and a particular actor/effect
is present in the raw wait events, so none is invented from counts or frame numbers.

The original isolated static-pot description and dynamic `0x0018` description
are both present byte-for-byte. Presence in a seeded runtime database alone
does not prove a new draw of a preloaded row. The owner-confirmed visible breaks
provide bounded physical effect observations, but do not establish coverage of
the entire pot-break code path. The companion model shards and environment
variations were explicit exclusions from the automated pilot. The three misses
must be traced; they are not automatically attributed to those exclusions.

The independent raw-wait check finds:

- Cold: **three** `shader-wait-ns` events totaling **139.496830 ms**. Two are
  outside the sample during loading: 50.652395 and 27.809723 ms. The latter is
  below the 35 ms hitch threshold and still counts as a missing-pipeline wait.
- Cold sample: **one** wait, **61.034712 ms**, at **13.428768589 seconds** after
  sample resume. The next recorded counter increase coincides with the sample's
  100.103492 ms interval. This is near the approximately ten-second first break;
  it is correlation, not a verified assignment to a particular description.
- Warm: **zero** raw wait events and zero cumulative-counter increase. The warm
  cache already contains the three discoveries and prepares 291 descriptions.
  A learned-cache success cannot satisfy the frozen seed's zero-miss criterion.

Whole-launch cumulative frame-counter deltas independently agree with three
calls / 139.496830 ms cold and zero warm. Per-frame counter values are cumulative;
they are never summed as if they were individual waits. No observed wait is
waived by the near-30-FPS averages or by the dynamic pilot's covered identity.

## Measured sample and failed Quit

Both existing analyzer invocations reproduced the original summary bytes and
exit **2**. `target_met` is false in both. The invalid reasons remain unverified
VideoOut timestamp semantics and missing completed recorder shutdown. The absent
forest result is expected for this bounded pilot and does not require story play.

| Recorded sample | Cold | Warm |
| --- | ---: | ---: |
| Duration | 120.004929 s | 120.004934 s |
| Average | 29.990435 FPS | 29.998766 FPS |
| p95 / p99 | 33.397 / 33.430 ms | 33.397 / 33.435 ms |
| Maximum interval | 100.103492 ms | 50.060791 ms |
| Intervals above 35 ms | 18 | 26 |
| In-sample shader calls / wait | 1 / 61.034712 ms | 0 / 0 ms |

Cold also exceeds the existing numerical 100 ms maximum threshold by about
0.103 ms. Warm has no numerical shortfall, but still lacks valid timing/shutdown
evidence and fails shipped-seed membership. Residual non-compilation intervals
are retained without claiming their cause or a general performance fix.

Both platform logs record the confirmed menu sequence, `EXIT code=0`, idle card
status and `shutdown-card-finished`, then SDK-stop request markers. Cold ends at
280,758.6 ms; warm at 224,975.1 ms. Both `last-stage.txt` files identify
`shutdown-sdk-stop-requested`. Neither raw recorder contains `shutdown,complete`.
`EXIT code=0` is the application's requested exit, not proof of clean completion.

The owner explicitly reports the same PS4 Quit error in both launches. No crash
dump/stack or executable console reproduction was supplied. A retained-log replay
can establish missing shutdown completion but cannot reproduce or fix
`CE-34878-0`. No root-cause hypothesis or runtime patch is justified by the
last log marker alone. The normal Quit failure remains
a separate required fix and blocks clean-shutdown acceptance.

## Disposition and reproducibility

Keep #148 open. Observed missing-pipeline waits require correction, rather than
an owner waiver or a repeat of the unchanged package. Next work is to trace the
three compatible runtime discoveries, add them with honest runtime provenance
to a validated seed while preserving every original input, fix/reproduce Quit,
and assemble/freshly inspect a newly identified candidate. Repeat the affected
bounded cold/warm pot sequence after correction; no story progression or
completed-save acquisition is required. Existing generated evidence remains
valid for its documented paths and does not become full-pot/full-game coverage.

This assessment changes no runtime, seed, package, analyzer, parent issue or
prior evidence record. It does not claim a new implementation or a physical pass.
Private replay artifacts are under `dynamic-validation-148-20261104` in the
existing private artifact store. Use fresh output paths to reproduce:

```bash
python3 tools/pswaker/frame-pacing.py "$RETURN/cold/analysis/raw-launch" \
  --inspection "$RETURN/cold/analysis/inspection.json" \
  --owner "$RETURN/cold/analysis/owner.json" --output "$NEW/cold-analysis"
python3 tools/pswaker/frame-pacing.py "$RETURN/warm/analysis/raw-launch" \
  --inspection "$RETURN/warm/analysis/inspection.json" \
  --owner "$RETURN/warm/analysis/owner.json" --output "$NEW/warm-analysis"
python3 tools/pswaker/complete-package.py pipeline-seed "$RETURN/cold/pipeline_cache.db" \
  --output "$NEW/cold-snapshot"
python3 tools/pswaker/complete-package.py pipeline-seed "$RETURN/warm/pipeline_cache.db" \
  --output "$NEW/warm-snapshot"
python3 evidence/ps4/outset-coverage-111/verify-coverage.py "$FROZEN_ASSETS" \
  "$NEW/cold-snapshot" "$NEW/warm-snapshot" --output "$NEW/coverage.json"
```

Analyzer exit 2 and coverage exit 1 are expected for this failed candidate;
run commands separately without treating those failures as passing checks.
The database snapshotter copies the database/WAL before opening, preserving
the original pair. Package reinspection used copied `assembly.json` and links
to the exact supplied package/ELF in a new private directory, leaving original
inspection reports unchanged.

## Assessment checks

The existing frame-pacing suite passed **22 tests**; the public seed-coverage
suite passed **4 tests**, with no failures or skips. Original hashes, private
archive copies, byte-identical public report/owner/summary copies, assessment
bindings and a personal-path scan all passed. Git whitespace checks passed.
No executable or analysis implementation changed, so no new test seam or
runtime test was added. These checks validate the assessment process and do
not convert the failing physical candidate into a pass.

[comparison.html](comparison.html) contains the data-free cold/warm chart.
