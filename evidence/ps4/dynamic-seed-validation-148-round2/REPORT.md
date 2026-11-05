# 301-description candidate: bounded seed checks pass

Assessed 2026-11-05 for #148. This is the physical return of the
[second seed correction](../dynamic-seed-correction-148-round2/README.md), package
SHA-256 `107e13f80423e89324aabb3aca453f46f2a0ea13569e0be6a509588fc9835a3d`.
The exact bundled seed has 301 descriptions and SHA-256
`06b8ef5d5df64e6a1218728550eab209f6a841926392ac18064effce64f17fd8`.
The ordinary 01.23 program/ELF and build/cache ID `6e885683f47a49a119ae`
are unchanged. A new inspection of the retained package reproduces frozen
inspection SHA-256 `2076142fad4075fb11462f84beaefc05f172837e827e11082299e64d6fb62cdb`.

## Independent replay

| Measured Outset sample | Cold | Warm |
| --- | ---: | ---: |
| Duration (seconds) | 120.019 | 120.003 |
| Descriptions matching the exact bundled seed | 301 / 301 | 301 / 301 |
| Missing / conflicting descriptions | 0 / 0 | 0 / 0 |
| Raw missing-pipeline wait events | 0 | 0 |
| Cumulative frame-counter wait delta | 0 calls, 0 ms | 0 calls, 0 ms |
| Average FPS | 30.0035 | 29.9993 |
| p95 interval (ms) | 33.4006 | 33.3976 |
| p99 interval (ms) | 50.0472 | 33.4519 |
| Maximum interval (ms) | 50.0943 | 50.1356 |
| Intervals over 35 ms | 50 | 31 |
| Shader-correlated hitches | 0 | 0 |
| Completed recorder shutdown | No | No |

Both original summaries reproduce byte-for-byte through the maintained analyzer.
Fresh standalone snapshots reproduce the original snapshot database bytes and
manifests. Both full-configuration coverage commands return 0: every captured
identity has identical version, size and configuration bytes in the frozen seed,
and there are no additions or conflicts. Different database-file digests reflect
capture/container metadata, not different configurations.

There are no `shader-wait-ns` events anywhere in either available raw launch log,
including outside the measured sample. Final-minus-initial cumulative frame
counters independently show zero calls and zero wait time. Counts alone are not
used as configuration-coverage evidence. The returned records support retaining
this exact 301-description seed without another correction for this route.

## Preparation and owner observations

Cold has zero build-specific files before initialization, and logs merging all
301 bundled records with zero skipped. Warm has four compatible cache files;
the cold pipeline database/WAL sizes and digests match warm's before-init log.
Both runs reach ready=301, total=301, pending=0, complete=1 and
`known-shaders-prepared` with zero preparation errors before gameplay.

| Logged preparation | Cold | Warm |
| --- | ---: | ---: |
| Full shader preparation (ms) | 17,377.5 | 617.1 |
| Final drain only (ms) | 15.0 | 326.3 |
| Startup to preparation complete (ms) | 43,277.4 | 1,684.9 |

Use the explicit `TIMING` full preparation measurement. The recorder's short
final `shader-preparation` phase is not the full preparation duration, and neither
measure is a filmed launch-to-first-control time. No memory/resource measurements
or broader scaling result are inferred.

The [owner confirmation](owner-followup.md) supplied with this return confirms
the same Outdoor Bath pots and approximate 10 s / 40 s break sequence, then rolls
through the two-minute sample. First and second breaks rendered correctly. Normal
Quit showed CE-34878-0 in both cold and warm runs. First break method and
unmentioned pauses remain unknown. The original owner JSON marks active gameplay
and graphics/audio correct; its template action text is preserved unchanged.

## Acceptance limits

The bounded seed coverage and zero-wait checks pass on the returned evidence.
**Overall acceptance remains incomplete.** Both logs stop at
`shutdown-sdk-stop-requested`, after an intended `EXIT code=0` and idle card;
neither recorder contains completed shutdown. The Quit failure remains #159 and
its cause is unestablished. No shutdown code or package changed during assessment.

Both analyzer runs return 2 because VideoOut timestamp semantics are unverified
and recorder shutdown is incomplete. Cold p99 also exceeds the 50 ms numerical
limit by approximately 0.0472 ms. Neither sample is an accepted general
frame-pacing pass; the forest scene is outside this bounded return. Save/settings
preservation, filmed progress and broader game coverage are not established here.
Runtime supplementation does not expand the isolated generated collector's
scenario or resolve source/effect attribution of the previously added records.

The original report's cold maximum is written as `50.059s`. That text is preserved
exactly. The replayed recorder maximum is 50.0943 **ms**; no 50-second interval is
present in the measured raw frames. The report text is not used to override raw
timing evidence or silently corrected.

## Preservation and checks

All 31 original returned files were privately archived, compared byte-for-byte,
and verified unchanged after inspection, analysis and snapshotting.
[original-file-inventory.json](original-file-inventory.json) retains source-relative
sizes and SHA-256 values. Original report, owner JSON and analyzer summaries are
preserved exactly; database/WAL, raw logs, game data, package and ELF stay private.
[assessment.json](assessment.json) records replay results, selected preparation
and shutdown markers, owner confirmation and explicit limits.

Existing analyzer and Outset-coverage suites ran 26 tests with one skip and no
failures. No maintained implementation or tests changed. Earlier failed
candidates, their evidence and the frozen 301-description generation record remain
intact. No new package is needed for the bounded seed correction on these results.
