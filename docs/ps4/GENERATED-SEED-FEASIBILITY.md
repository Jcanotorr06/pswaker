# Generated-seed PS4 feasibility gate (#149)

This is the bounded physical gate for #136, using the static/dynamic pilot from
#147/#148. The [candidate record](../../evidence/ps4/feasibility-149/README.md)
identifies the private complete package, matching ELF, frozen seed and fresh
inspection. Do not substitute an earlier 01.23 package or infer console acceptance
from a host build. #149 stays open through returned evidence and owner review;
downstream expansion remains gated until a successful result and explicit handoff.

The prior [301-description console return](../../evidence/ps4/dynamic-seed-validation-148-round2/REPORT.md)
passes bounded seed membership and raw-wait checks, but lacks startup resource,
visible progress and save/settings preservation evidence. Normal Quit crashes in
both runs; #159 owns diagnosis. The new candidate adds memory observations, not a
Quit fix. It can collect the remaining observations now, but a repeat crash blocks
acceptance. A subsequent shutdown correction needs its own identified candidate
and affected checks repeated. Do not ask the owner to repeat a known failure as
though success were expected.

## Selection, prerequisites and effort

Use USA `GZLE01` revision 0, stock rendering, 1280x720 internal target, original
30 Hz logic and synchronous missing-pipeline creation/recording. Confirm the
actual console model, firmware and GoldHEN; the supported reference is PS4 Slim,
9.00, v2.4b18. Preserve original inputs, earlier candidates and failed returns.
Actual resources, seeds, packages, ordinary saves, videos and logs remain private.

| Scenario | Why selected | Physical observation and limit |
| --- | --- | --- |
| `always-small-pot-stock-v1` | Real opening-game static model/material path; three generated draws | View an intact small ceramic pot beside Outset's Outdoor Bath before breaking it. This is a static regression control, not exact host camera/state equivalence. |
| `common-pot-debris-lifecycle-v1` | Real common-particle emitter calculation, draw and retirement; two texture selections, 40 generated draws | Break a first and second nearby pot; observe debris and disappearance. A whole pot break includes uncollected companion shards and actor lighting. The physical route does not certify both generated texture variations. |
| Ordinary movement, turns and dry-ground rolls | Representative subsequent gameplay and controls/audio regression | Continue the same two-minute sample, then remain in the same area for three more minutes to obtain five-second resource observations. No new story progression. |

Use the owner's already available ordinary Outset save, at the Outdoor Bath pots
used in the #148 return. The exact prior save file digest was not recorded; record
the selected file/card/slot, private digest and landmark before this experiment.
Do not overwrite a slot, create progression, acquire a completed save or replace
the owner's profile to obtain a scenario. If the save or two pots are unavailable,
return that gap for maintainer setup. Use the same unmodified starting save and
route for both launches. First break by lift/throw needs no sword; record the
actual repeat method and any change from the earlier sword repeat.

Allow about 20–30 minutes for two bounded runs, backup/cache handling and retrieval,
plus actual startup and transfer time. No cold/warm startup ceiling is imposed.
No hidden gameplay warmup, full-game replay or manual discovery campaign is needed.

## Owner run: cold, then separate retained-cache warm

1. Close PSWaker completely. Back up `/data/pswaker/saves/` and
   `/data/pswaker/settings.ini` independently of caches, including recovery files
   and the chosen ordinary save. Keep a private relative-path/size/SHA-256
   inventory before and after each run. Retain absent-file observations too.
   Install the exact candidate and verify its package digest. With the app closed,
   rename only `/data/pswaker/cache/<candidate-build-id>/` to a new retained sibling
   if present. Record the directory before/after. Do not clear the whole profile,
   image-check record, previous build caches, saves or settings. This empties both
   build-specific runtime-description and driver caches. Installation alone does
   not empty them. The cold log must show `files-before-init=0`.
2. Film from selecting Launch through first controllable gameplay, with an external
   timer. Note shell splash, checking/preparation screens, changing progress,
   responsiveness, freezes, errors and actual first control. Leave startup's
   normal content checking in place. Record filmed launch-to-control separately
   from logged preparation; a new build may require a full image check while
   warm reuses it. Do not attribute that entire difference to shader compilation.
3. Load the selected save. At first visible control choose **Mark visible gameplay
   ready and resume** in the port menu. Film the entire approach to the pots;
   record its actions and pauses too. Arm **Measure Outset (resume for two
   minutes)** at the pots and start the timer on resume. View the intact pot for
   about ten seconds, break the first at about 10 s, then the second at about
   40 s. Note actual times, first/repeated effect appearance, retirement, pauses,
   method, controls and audio. Move/turn/roll for the remainder. After sample end,
   stay in this area for three additional minutes of representative movement;
   keep this interval identifiable in video/notes. Do not save changed progress
   or change settings during the experiment.
4. Choose **Quit game...** normally. Record full closure, any CE error and the time;
   intended `EXIT code=0` is not clean termination. Preserve a failure without
   clearing data or trying alternate shutdown paths. Retrieve the cold evidence
   below before another launch rotates logs. If closure is uncertain, do not
   copy a live database: record the failure and close the application first.
5. Relaunch the exact candidate with its newly populated compatible cache retained.
   Do not rename it again or reinstall a different package. Repeat the same
   starting save, route, two-minute sample, additional three minutes and normal
   Quit. Retrieve into a separate warm folder. Record visible progress and
   launch-to-control independently. Compare save/settings inventories against
   the backups; explain every changed or missing file before claiming preservation.
   Keep both backups, both returns and the earlier renamed cache.

For **each** run retrieve privately, preserving directory structure:

- Entire `/data/pswaker/logs/performance-XXXXXX/` (`identity.json`, `events.csv`,
  `frames.csv`, `samples.csv` and any additional files).
- `/data/pswaker/logs/platform.log`, `platform.prev.log`, `last-stage.txt`, and any
  available crash/debugger artifacts. Associate the matching BEGIN/build block.
- The entire `/data/pswaker/cache/<candidate-build-id>/`, including
  `pipeline_cache.db` and adjacent `-wal`/`-shm` files when present, driver cache
  files and seed merge identity. Copy together after full closure; never overwrite
  a prior return. Keep before-init and after-run inventories.
- Video/timing/action notes, platform confirmation, cache rename/reuse evidence,
  before/after save/settings inventories, and the filled
  [observation form](feasibility-owner.example.json). Null means
  unobserved; do not turn template values into confirmations. Keep the existing
  frame-pacing owner JSON separately for the analyzer; this form does not replace it.

## Maintainer analysis of the returned evidence

Archive and hash originals first, then work in new private output directories.
Freshly inspect the exact complete package again. Check package/build/ELF,
installed seed merge identity, recorder identity, platform and owner notes all
refer to the frozen candidate. Snapshot cold and warm database/WAL pairs through
`complete-package.py pipeline-seed`; compare **every** returned type/hash,
version, size and full description bytes against the packaged seed using
`evidence/ps4/outset-coverage-111/verify-coverage.py`. Also compare both generated
observation assets and the retained compatible corpus. Matching row counts or
database-file hashes alone cannot prove membership. Retain source inventories
and verify originals unchanged after analysis.

```bash
python3 tools/pswaker/complete-package.py inspect "$COMPLETE" --platform-root "$PLATFORM_ROOT"
python3 tools/pswaker/complete-package.py pipeline-seed "$COLD/pipeline_cache.db" --output "$CHECK/cold"
python3 tools/pswaker/complete-package.py pipeline-seed "$WARM/pipeline_cache.db" --output "$CHECK/warm"
python3 evidence/ps4/outset-coverage-111/verify-coverage.py "$FROZEN_ASSETS" \
  "$CHECK/cold" "$CHECK/warm" "$STATIC_OBSERVATIONS" "$DYNAMIC_OBSERVATIONS" \
  --output "$CHECK/coverage.json"
```

Inspect raw creation/error messages, `shader-wait-ns` events and cumulative frame
shader counters across the **whole launch**, approach, first/repeated actions and
later gameplay, including waits below the hitch threshold. Keep raw data as well
as the existing frame-pacing analyzer output. Separate unverified VideoOut timing
and unrelated loading stalls from pipeline misses; average FPS cannot waive a
miss. Missing/conflicting descriptions or missing-pipeline waits require
correction and revalidation of the changed candidate.

Require successful seed import with no skipped incompatible descriptions, all
required configuration/layout jobs ready, pending zero, complete true, no creation
errors and `known-shaders-prepared` before gameplay. Configuration count differs
from native pipeline count: scene/offscreen layout keys and destination-alpha
prepasses are renderer-managed. Retain `SHADERS` progress, creation messages and
target/layout records; reconcile required variants with the identified renderer's
`rebuild_pipeline_cache`/creation paths. An aggregate count alone does not certify
an unlogged layout variant; report missing variant evidence explicitly.

Use `TIMING shader-preparation_ms` from seed loading through creation/cleanup,
and `shader-final-drain_ms` for the final screen only. Record their raw start/end
timestamps, startup-to-preparation-complete and filmed launch-to-control. Content
validation/storage/layout work overlaps preparation: do not add overlapping
durations. Warm still creates runtime objects, and may avoid a full image check.
Report actual before/after cache sizes and description growth for each run.

`RESOURCE` now records launch-clock `ms` and `phase`: before-renderer,
graphics-initialized, content-validation (at most once per second plus completion),
before-render-target, shader-final-drain (at most once per second),
known-shaders-prepared and gameplay (the existing five-second heartbeat).
Garlic/onion measure driver buffer/image allocations in bytes; buffers is a count.
Main-mspace allocated bytes include reserved thread arenas, not precise live
game allocations. Flexible available bytes are valid only for query-result zero;
failed queries say `unavailable`. These counters are not additive total process
memory. Report per-phase sampled maxima/minima, later growth, allocation failures,
crashes and observation duration. They miss transients between samples and inside
blocking initialization/synchronization; before/after values are not measured
peaks. Before renderer creation, zero driver counters can also mean no tracked
device yet. There is no demonstrated full-game resource budget or linear scaling law.

Require normal application closure, completed recorder shutdown/drain and a clean
subsequent relaunch, plus preserved saves/settings. #159 remains a known blocker
until corrected and physically revalidated. Report retained-cache evidence even
when shutdown or presentation timing prevents overall acceptance.

## Gate decision and expansion handoff

Publish a data-free report tying every result or gap to the exact candidate and
cold/warm evidence. Separate generated coverage, runtime supplementation and
physical observations. The small corpus cannot establish full-game startup cost
or coverage; additional generated draws need not add configurations.

If compatibility, generation, preparation or resources are infeasible, give
measured blockers and owner options: resolve the bounded blocker and repeat;
improve targeted instrumentation and return missing evidence; or explicitly
re-scope/pause the downstream plan by owner decision. Do not quietly reinstate
a manual campaign or change rendering quality, logic rate or synchronous policy.

Only a successful bounded feasibility result, resolved required gaps and explicit
owner acceptance permit the expansion handoff to #136's next automated collector
work. Carry forward exact corpus size/growth, supported contract/layouts, measured
cold/warm startup/resource limits and unsupported paths (companion shards, actor
lighting/collision, other effects/cameras and full-game inventory). Host checks,
this document and a merged PR do not close #149. When physical work is next,
replace `ready-for-agent` with `ready-for-human` and retain the open issue.
