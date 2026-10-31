# Owner return: assembled Outset preparation validation (#112)

Assessed 2026-10-31 for [#112](https://github.com/Jcanotorr06/pswaker/issues/112),
part of [#107](https://github.com/Jcanotorr06/pswaker/issues/107).

**The returned seeded 01.20 recordings show preparation before loading, zero
missing-pipeline waits throughout both recorded launches, and substantially
smaller cold-sample spikes than the accepted unseeded 01.19 baseline.** Cold
maximum falls from 333.669 ms to 50.114 ms; 3,531.310 ms of in-sample shader
waits becomes zero. All 287 descriptions are ready before loading starts.

This is bounded evidence of improvement, not a verified numerical performance
pass. Both analyzer results remain invalid because physical presentation timing
is unverified and completed recorder shutdown is absent. Actual action times,
visible preparation observations, an incompatible-update test and save/settings
preservation evidence were not returned. **Keep #112 open, ready for human
validation.** The accepted baseline's limitations remain in force.

## Package, program, seed and platform

| Item | Identity |
| --- | --- |
| Console | Owner reports PS4 Slim / firmware 9.00 / GoldHEN v2.4b18 |
| Changed program | `01.20`, build/cache ID `9f79516d60da618241a1` |
| Complete package | `IV0000-PSWK00001_00-PSWAKERGAME00000.pkg` |
| Package SHA-256 | `cc26a2526f9cb4b81383b2875c66fa6521519f3d2d991d3be5be08f1d91ae8f5` |
| Matching ELF SHA-256 | `06417d1c34cdf58b70baee9e679f83e77899b12405ce47f8a9b12bf578790f90` |
| EBOOT SHA-256 | `ac4e2bb217608637b5dd9be430f1f307112286d4c0e112a547b961afcafe690c` |
| Installed seed | `/app0/initial_pipeline_cache.db`, 1,200,128 bytes, 287 descriptions |
| Installed seed SHA-256 | `7e3f8527203dc488b5ae646904c986ac596d7d4017db45a0fcb18ae29de51dc1` |
| Fresh inspection SHA-256 | `9f9203539d945b8a8a75d0975cec887dff30b37d3660c4331b10205e80c1e0ee` |

This is the exact normally assembled [#111 delivery](../outset-coverage-111/README.md),
including the #110 preparation fix, supplied in the owner's 01.20 validation
folder. Fresh inspection of that supplied package on 2026-10-31 extracted its
payload and checked its hashes, program, seed, manifest, artwork and disc image.
It reproduced both returned inspection files byte for byte. Inspection ran in
a separate private working directory; the supplied package directory and its
existing reports were preserved. No program, seed or package was changed for
this assessment. The inspection's generic `hardware_status: Untested` describes
what inspection alone establishes; this report records the subsequent return.

The [accepted baseline](../action-baseline-108/OWNER-DECISION.md) is **unseeded
01.19**, build `48d0196e605f00284b21`, package SHA-256
`b7739a9c2fb6490dc2faceffe44e706a6f1ecc412805ffb76aaa13ec7fc1319e`, on the same
reported platform. It is not the earlier 01.12 or unplayed 01.13 candidate.
The baseline [report and original measurements](../action-baseline-108/REPORT.md)
are unchanged. The owner's acceptance of those baseline records does not waive
the final validation criteria or verify either build's physical timing.

## Cold launch and compatible retained-cache relaunch

Cold `CACHE` reports zero files before initialization. Aurora merges all 287
bundled descriptions, skipping zero. Progress advances from ready=7/pending=280
to ready=287/total=287/pending=0/complete=1, then logs `TIMING` and
`known-shaders-prepared`, errors=0, before the recorder enters loading.

Warm starts with four cache files and reports the bundled seed already merged.
The returned cold pipeline database and WAL SHA-1 hashes match the warm
`before-init` listing. This corroborates retention between these launches;
it does not establish normal Quit. Warm preparation reaches the same complete
state and all gameplay heartbeats retain created=287, queued=0.

The full recorder exports contain **zero `shader-wait-ns` events in both
launches**, including loading, the walk, first sample resume and the whole
sample. Recorded shader counters remain zero. There is no observed synchronous
missing-pipeline creation/wait during the covered recordings.

The post-run snapshot reports [cold](seed-cold.json) and [warm](seed-warm.json)
are identical: 287 descriptions, 1,208,320 bytes, SHA-256
`431578ed91f8f4831b1dcbf41876cfaa2cad77f931838c0a15742ad03d8bbdef`.
Fresh snapshotting of each returned database/WAL pair reproduces these reports.
[coverage.json](coverage.json), generated with the existing #111 CLI, confirms
that every recorded `(type, hash)` and configuration byte matches the installed
default asset: 287 represented, zero missing/conflicting descriptions, zero
additions. Snapshot bytes differ from installed seed bytes because database
layout/capture metadata is separate from configuration identity. The original
installed seed hash above remains the package identity. This is not proof of
which description belongs to an individual action or of full-game coverage.

## Startup cost and the longer-first-launch tradeoff

| Ordinary log measurement | Cold ms | Warm ms |
| --- | ---: | ---: |
| Full preparation elapsed, including overlap with earlier startup | 14,621.2 | 553.9 |
| Final drain | 14,052.0 | 482.9 |
| Preparation outside final drain (difference) | 569.2 | 71.0 |
| Launch to preparation completion | 15,996.6 | 1,690.1 |

| Recorder phase or boundary | Cold ms | Warm ms |
| --- | ---: | ---: |
| startup | 125.999 | 537.475 |
| renderer-initialize | 1,033.031 | 586.185 |
| content-validation | 33.207 | 1.591 |
| storage-check | 262.471 | 54.029 |
| shader-preparation | 14,053.437 | 484.424 |
| Recorder start to loading | 15,508.145 | 1,663.704 |
| loading to owner gameplay-ready marker | 30,593.660 | 36,015.503 |
| Recorder start to owner gameplay-ready marker | 46,101.805 | 37,679.206 |
| Gameplay-ready marker to sample arm (walk/menu latency included) | 20,773.059 | 18,506.005 |
| Sample resume to first observed game frame | 33.427 | 26.543 |

The ordinary log measures from an earlier launch boundary than the recorder;
these totals must not be substituted for one another. The full preparation
measurement starts before the recorder's named preparation phase. Reporting
only its final drain would omit 569.2 ms cold and 71.0 ms warm of preparation
elapsed outside that drain. These are elapsed measurements, not summed CPU
compilation time or visible-screen durations.

Cold spends about **14.31 seconds longer to preparation completion** than warm
on the ordinary log's boundary. The accepted unseeded baseline had only 1.8 ms
in its cold preparation phase and instead incurred 13,641.9 ms of blocking
shader waits across loading, the walk and its sample. The new launch moves
known work before gameplay; it does not remove its cost. Compatible caches
shorten preparation but do not eliminate construction of runtime pipelines.
Title/file selection and the gameplay-ready marker are owner-paced; the total
loading times are not an automated startup benchmark. No startup budget was
agreed. Visible progress and the exact visible boundaries still need owner
observations or video; log progress alone does not confirm their appearance.

## Recorded frame intervals against the accepted baseline

Both returned summaries are reproduced exactly by the existing
`tools/pswaker/frame-pacing.py`, each with exit **2**. The unchanged invalid
reasons are `VideoOut timestamp semantics unverified; obtain agreement before
substituting evidence` and `launch has no completed recorder shutdown`.
`target_met` remains false. The tool also reports missing `forest`, expected
for this bounded route; no forest result is inferred.

| Package / cache | Seconds | FPS | p95 ms | p99 ms | Maximum ms | Shader calls / wait ms | Intervals >35 ms / shader-correlated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline 01.19 cold | 120.004938 | 29.348792 | 33.400989 | 66.733669 | 333.668729 | 82 / 3,531.310 | 62 / 47 |
| Changed 01.20 cold | 120.021618 | 30.002928 | 33.394284 | 33.424693 | 50.113906 | 0 / 0 | 14 / 0 |
| Baseline 01.19 warm | 120.021617 | 30.002928 | 33.394892 | 33.424658 | 50.138269 | 1 / 0.426 | 14 / 0 |
| Changed 01.20 warm | 120.004931 | 29.998767 | 33.398501 | 33.442120 | 50.109357 | 0 / 0 | 31 / 0 |

The new samples have no numerical shortfalls against the reference limits
(average >=29.5 FPS, p95 <=35 ms, p99 <=50 ms, maximum <=100 ms). This fact
does not override invalid timing/shutdown evidence. Pause-menu readings in the
[original owner report](owner-report-original.md) agree with the rounded
recomputed values, but use the same recorder and are not independent physical
presentation corroboration.

Residual intervals remain: cold has 14 approximately 50 ms intervals, warm 31.
**Warm has more >35 ms intervals than the baseline warm sample's 14**, despite
similar percentiles/maximum and no shader waits. One sample per cache state
does not establish the cause or significance of that difference. Keep it for
separate diagnosis under #107/#51; no hitch-free or warm-regression-free claim
is made. The recorded fixed contract remains stock textures, 1280x720, 30 Hz
logic and synchronous pipelines. This assessment changes no runtime behavior.

### Planned action windows, first-use regions and repetitions

The returned owner JSON repeats the planned timeline; it contains no actual
first-action times or video. The following are **planned windows**, not verified
action attribution. [correlation.json](correlation.json) uses the existing
#108 correlation function unchanged, preserves every interval >35 ms, and
places each interval at its closing presentation's monotonic observation.

| Planned window | Baseline cold max ms | Changed cold max ms / >35 ms intervals | Changed warm max ms / >35 ms intervals |
| --- | ---: | ---: | ---: |
| 0-10 s still | 333.669 | 50.053 / 2 | 50.109 / 8 |
| 10-40 s five rolls | 250.260 | 50.061 / 5 | 50.043 / 1 |
| 40-70 s five sword swings | 283.618 | 50.050 / 2 | 50.057 / 14 |
| 70-110 s water entry/swimming | 116.784 | 50.114 / 5 | 50.053 / 8 |
| 110 s to sample end, shore/still | No >35 ms interval | No >35 ms interval | No >35 ms interval |

All changed-package windows have zero shader waits. In cold, the first >35 ms
roll-window interval occurs at 31.967 s, sword at 51.270 s and swim at 81.600 s.
There are no such intervals at the baseline's severe first-use regions
(11.96-15.15 s rolls, 43.21/44.04 s sword, 72.96/73.94 s water entry).
Later planned repetitions still contain the 50 ms intervals listed above.
Warm includes 50 ms intervals early in the roll and sword windows and later
in the sword/swim windows. Without actual action times, first occurrences and
individual repetitions cannot be isolated or assigned numerical verdicts.
The return describes five rolls and five swings per sample, plus swimming,
but only **one** sample per launch was returned; the handoff requested two.
The two-minute recorder ends around 120 s, so the planned final segment through
125 s is not fully part of the sample.

Before the sample, the changed cold walk contains two >35 ms intervals, maximum
50.055 ms; warm has one, 50.051 ms. Both have zero waits. The baseline cold
walk had 2,426.7 ms of waits and a 784.1 ms maximum. Neither return describes
the exact landmark/approach or rules out covered actions during that walk.
The full changed recordings also retain pre-gameplay/loading intervals up to
316.976 ms cold and 417.084 ms warm, and post-sample intervals. These are not
removed from the raw exports. Sample gameplay is not reclassified as loading.

## Preserved originals and reproducibility

[original-file-inventory.json](original-file-inventory.json) records sizes and
SHA-256 hashes of all **31** returned files. Paths are relative to the original
private `local-research/action-validation-112/` directory: `launch-1` is cold,
`launch-2` warm. All 31 hashes were unchanged after this assessment.

The public `cold/` and `warm/` directories retain byte-identical raw recorder
CSVs/identity, owner JSON, inspection and original summaries. Seed reports and
the original owner report are also copied unchanged. Each retained summary's
`evidence_sha256` binds its raw inputs; its original sample JSON hash remains
in the inventory, and that JSON can be regenerated by the analyzer. No owner
booleans or timing verification fields were changed. [assessment.json](assessment.json)
binds the fresh inspection, #111 delivery, baseline identity, full preparation
timings, retained-cache hash match, source immutability and reproduced results.

Databases, WALs, seed bytes, ordinary logs containing personal build paths,
package and ELF stay private. Original ordinary logs, including both
`platform.prev.log` files and last-stage files, remain inventoried. Cold's
previous log records an **additional cold startup of the same 01.20 build**
(16,025.8 ms to preparation completion); no corresponding recorder export or
action report was supplied. It is not silently counted as a second sample or
an incompatible-update result. Warm's previous log retains the assessed cold
startup. Neither supplies completed Quit/EXIT evidence.

Reproduce with existing tools on Linux/WSL2, choosing fresh private output paths:

```bash
python3 tools/pswaker/frame-pacing.py "$RETURN/launch-1/analysis/raw-launch" \
  --inspection "$RETURN/launch-1/analysis/inspection.json" \
  --owner "$RETURN/launch-1/analysis/owner.json" --output "$NEW/cold-analysis"
python3 tools/pswaker/frame-pacing.py "$RETURN/launch-2/analysis/raw-launch" \
  --inspection "$RETURN/launch-2/analysis/inspection.json" \
  --owner "$RETURN/launch-2/analysis/owner.json" --output "$NEW/warm-analysis"
python3 tools/pswaker/complete-package.py pipeline-seed "$RETURN/launch-1/pipeline_cache.db" \
  --output "$NEW/cold-snapshot"
python3 tools/pswaker/complete-package.py pipeline-seed "$RETURN/launch-2/pipeline_cache.db" \
  --output "$NEW/warm-snapshot"
python3 evidence/ps4/outset-coverage-111/verify-coverage.py "$DEFAULT_ASSETS" \
  "$NEW/cold-snapshot" "$NEW/warm-snapshot" --output "$NEW/coverage.json"
python3 evidence/ps4/action-baseline-108/correlation.py \
  "$RETURN/launch-1/analysis/raw-launch" "$RETURN/launch-2/analysis/raw-launch"
python3 tools/pswaker/complete-package.py inspect "$NEW/package-inspection" \
  --platform-root "$PLATFORM_ROOT"
```

Each analyzer invocation is expected to exit 2; run them independently. The
correlation CLI prints the same cold/warm results as `correlation.json`, with
the original #108 method/usage text. Prepare the isolated inspection directory
with a copy of the unchanged `assembly.json` and links/copies of the exact
supplied `out/` package and `elf/` binary, rather than overwriting retained
inspection reports. Private replay outputs/logs are retained under
`action-validation-112` in the existing private artifact store.

## Acceptance criteria and remaining owner evidence

| #112 criterion | Assessment |
| --- | --- |
| Exact normally assembled package, program, seed, platform/cache and fresh inspection | Met for identified 01.20 return; identities agree and fresh extraction reproduces inspection |
| Empty cache, first actions/repetitions, comparable retained-cache relaunch, preserve saves/settings | Partial: empty and retained caches corroborated; one sample each; actual first actions, approach and save/settings preservation unconfirmed |
| Default seed prepared before gameplay, visible progress, full startup/preparation/loading and tradeoff | Logs establish inclusion, completion and full timing; visible progress/boundaries unconfirmed |
| Zero missing-pipeline events and reduced cold spikes; separate first/repeated/warm results | Zero waits and reduced sample/window spikes demonstrated in records; individual first/repeated action attribution remains unavailable |
| Re-preparation across incompatible update and compatible reuse, preserving identities/saves/settings | Compatible reuse corroborated; no incompatible-update run or save/settings comparison returned |
| Visible-output timing corroboration, preserve timing/shutdown gaps and all samples | Gaps preserved; timing remains false and recorder shutdown absent in both launches; no verified numerical pass |
| Correct action effects, quality/speed, controls/audio, representative warm behavior | Owner JSON says active gameplay and graphics/audio correct; detailed roll/swim/sword appearance, controls and speed observations absent; residual warm intervals retained |
| Preserve recordings, logs, notes/video, identities and analysis; broader goals | All supplied records inventoried/preserved; no notes/video supplied; no forest or broader-route conclusion |
| Honest result and residual failures; no full-game or release-gate claim | Bounded improvement supported; remaining evidence prevents completion of #112; initial release-candidate exception unchanged |

To complete the unverified portions, use the same exact #111 package and the
[existing handoff](../outset-coverage-111/README.md#console-handoff-and-limits),
[action checklist](../../../docs/ps4/Action-baseline-checklist.md) and
[preparation guide](../../../docs/ps4/SHADER-PREPARATION.md#console-handoff).
Return actual timed first actions and repetitions, the landmark/approach and
visible startup/progress/output observations; record normal **Quit game...**
before retrieving the full recorder/database/WAL; document backup and unchanged
saves/settings. Verify compatible reuse and necessary re-preparation across an
identified incompatible update, without deleting progress. Any material
package/program/seed change requires renewed affected evidence. New notes
cannot retroactively fill gaps in the accepted baseline or these recordings.

This focused Outset route does not replace broader Outset/forest validation,
establish coverage elsewhere, or reopen the initial release candidate's
previously accepted performance gate. Residual non-compilation slow frames
remain separate work; no effects or quality are sacrificed by this assessment.

## Host validation

No runtime, packaging implementation or analyzer contract changed; this work
uses the existing public package and exported-record boundaries. No new test
seam or synthetic test was introduced for the archived evidence.

- Both original analyzer summaries reproduced exactly, exit 2, preserving all
  invalid reasons. Fresh package inspection and both snapshots passed; the
  existing coverage CLI found all descriptions identical to the default seed.
- Focused frame-pacing suite: 22 tests, one environment skip, no failures.
- Full Linux/WSL2 suite: 225 tests in 308.492 s, 60 environment/platform skips,
  no failures. It used the retained reference platform and #110 real-renderer
  shader-startup check binary.
- Pyright: zero errors/warnings. Python compilation, maintained shell syntax,
  JSON/hash bindings, personal-path scan and Git whitespace checks passed.
- All 31 original input hashes remained unchanged. The original owner's report
  retains its exact whitespace through a narrowly scoped Git attribute.

Focused/full-suite logs and fresh inspection/reanalysis/snapshot outputs remain
in the private artifact store's `action-validation-112` directory. Passing
host checks do not resolve the outstanding owner evidence above.

## Standards

No findings. Independent review checked repository evidence/privacy rules,
archived-byte preservation and the distinction between host checks and console
acceptance. All 31 original source hashes still match. The narrow Git whitespace
exception preserves the original owner report's CRLF and trailing spaces.

## Spec

No actionable findings. Independent review reproduced the retained identities,
raw input hashes, summaries, snapshot/coverage results and planned-window
correlation. It confirmed the remaining owner requirements above are recorded
as incomplete and that no numerical pass or full-game coverage is claimed.

Review totals: Standards 0 findings; Spec 0 actionable findings. This reviews
the evidence assessment; it does not complete the missing hardware checks.
