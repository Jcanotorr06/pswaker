# Full-game pipeline coverage campaign (#137)

This is the runnable campaign for [#137](https://github.com/Jcanotorr06/pswaker/issues/137),
part of [#136](https://github.com/Jcanotorr06/pswaker/issues/136).
Start with the [Windfall pilot](Windfall-coverage-checklist.md). The
[inventory](COVERAGE-INVENTORY.md) defines the finite scope; the
[pilot report](../../evidence/ps4/coverage-137/REPORT.md) identifies the prepared
candidate and distinguishes completed host preparation from pending PS4 work.

## Supported configuration

Use the validated USA GameCube `GZLE01` revision 0 image, SHA-256
`ec2d4ee790f48bee3d4c10feed166370df895f474e8db3f9af3b16ee001436df`, on
PS4 Slim / firmware 9.00 / GoldHEN v2.4b18. Retain the current renderer/driver,
1280x720 internal target, stock textures, original 30 Hz logic and synchronous
drawing. Record the actual configuration each time; a mismatch stops acceptance
for this campaign. The PS4 scanout and physical presentation timing need their
own observations. This inventory does not cover HD/Wii U content or randomizer
changes. The second quest is the original game's cleared-file playthrough.

## Fixed cohorts and ordinary checkpoints

Back up `/data/pswaker/saves/` and `settings.ini` separately before starting.
Use ordinary in-game saving and the maintained PS4 save workflow only. No debug warp,
stage-select, save-state, save editor or automated gameplay is part of this
campaign. In-game sailing and normally learned songs are allowed.

| Cohort | Fixed membership | Entry ordinary save | Exit ordinary save | Cumulative milestone |
| --- | --- | --- | --- | --- |
| E: early story | S01-S07, B01-B02, I01-I11 and E-tagged action rows | CP-E0: new original-quest file, before Outset departure; retain before its one-time scenes | CP-E1: Farore's Pearl obtained, before departing Forest Haven for Greatfish | C-E: C000 plus E discoveries |
| M: middle story | S08-S12, B03, I12-I13 and M-tagged action rows | CP-E1 | CP-M1: first Hyrule visit complete, Master Sword obtained, before second Forsaken Fortress visit | C-M: C-E plus M discoveries |
| L: late story | S13-S22, B04-B09, I14-I18 and L-tagged action rows | CP-M1 | CP-L1: outside the final battle with full equipment and Triforce; CP-CLEAR: ordinary cleared-file save after credits, separately backed up | C-L: C-M plus L discoveries, including final battle/credits |
| A: alternate and remaining variations | A01-A10, O01-O20, SEA01-SEA49, C01-C22, V01-V12, X01-X10, N01-N08 | CP-L1 for original-quest optional circuits; CP-CLEAR for second quest; earlier retained checkpoints where content has disappeared | CP-A1: optional circuits complete with private checklist; CP-A2: second-quest cleared-file save | C-A: C-L plus all compatible A discoveries |

Q and F rows have fixed E/M/L/A membership by their `First cohort` column. Their
explicit upgraded/late variants belong to A. Pilot P01 is the bounded Windfall
subset of S04; it does not complete S04 or the cohort. Inventory aliases denote
shared evidence, not extra implicit scenarios. A cohort is complete only when
every listed row and its enumerated variants has evidence or an eligible accepted
waiver. Original story evidence does not automatically cover the alternate mode.

Before each S/B/I row, retain `CP-<ID>-entry`: the last ordinary save from which
that route can be repeated, recording actual reload location, inventory, story
flags and approach. After the row retain `CP-<ID>-exit`. An ordinary save may
reload at a dungeon entrance rather than in the saved room; record the actual
re-entry walk and film it. Never promise a boss/cutscene can be repeated from a
post-boss save. Keep the pre-event backup before proceeding. For optional rows,
record the nearest entry save and the boat's mooring, then return to that mooring
and save at exit. Save aliases are plans until an actual private file/hash is
entered in the scenario record; none is claimed available merely by naming it.

Do each story row in order. Traverse the entire named dungeon, including its
normally reachable side rooms, switches, map/compass/big-key chests, miniboss
and boss approaches. At each entry/exit record actual stage/room IDs from the
recorder and a private room checklist. Record first room entry, each new enemy,
item use, puzzle/effect and cutscene before repeats. Record transitions as well
as fights. Do not silently skip a side room because it has no required story item.
The inventory fixes content scope, not a claim of every possible state product.

Reachability does not grow a cohort indefinitely: an optional gate not yet open
is entered in the deferred ledger as `(original ID, prerequisite, A route,
checkpoint, status)`. Revisit in A; retain the original ID. Story-critical gates
are resolved within their story cohort. Content that vanishes later must be
captured from its retained pre-event save, including first fortress stealth,
pre-rescue Windfall, frozen Hyrule and the pre/post Greatfish storm. An inability
to return is a missing observation, not coverage. New content found outside the
inventory gets an appended stable ID and a visible inventory revision; never
renumber old rows or hide it in a completed cohort.

## Cumulative database and frozen validation

The private `coverage-137/C000` milestone is a fresh standalone snapshot of the
historical #112 warm database/WAL. Its 287 descriptions all match the existing
default seed. Historical normal-Quit evidence was missing; this snapshot does
not repair that gap or establish any post-Outset observations.

Keep one compatible cumulative discovery database. For P01, launch with empty
runtime/driver caches and bundled seed, then retain the resulting database after
normal Quit. For later discovery launches on the same build, retain that cache
and accumulate normally. Snapshot at every row/cohort milestone with the app
closed, before the next launch rotates logs. Preserve the source database and
adjacent WAL together, plus a hash inventory; retain absent-WAL observations.
`pipeline-seed` reads the adjacent WAL and snapshots without changing the source.
Never copy a live database, concatenate SQLite files, or discard descriptions
merely to force a seed count to grow.

If restoring an older save, retain the cumulative cache: gameplay progress and
description discovery are separate. Empty caches are required again for frozen
acceptance. Archive the cumulative database/WAL before renaming that build's
cache, and retain it independently of acceptance captures. A changed build must
pass the existing schema/configuration compatibility validation; do not copy
driver binaries between builds. If multiple independent databases become
necessary, stop for validated consolidation with conflict/provenance checks;
the existing comparison command checks membership and does not merge inputs.

For every returned source, use a new private output directory:

```bash
python3 tools/pswaker/complete-package.py pipeline-seed \
  "$RETURN/cache-after/pipeline_cache.db" --output "$PRIVATE_ROOT/P01-discovery-seed"
python3 evidence/ps4/outset-coverage-111/verify-coverage.py \
  "$FROZEN_SEED" "$PRIVATE_ROOT/P01-discovery-seed" \
  --output "$PRIVATE_ROOT/P01-discovery-membership.json"
```

A discovery comparison can fail because descriptions are missing. Retain its
failure log and source snapshot. Validate and use the complete cumulative
snapshot as the next assembly asset; retain its `pipeline-seed.json` source
provenance. Compare the prior seed against the expanded candidate too, to prove
that accumulated coverage was not lost. A union is not obtained by comparing.
Report distinct new identities and conflicts against the previous seed. Report
zero additions if identical; pending capture has an unknown count, not zero.

Assemble through the existing normal game workflow, using the validated asset
at the platform's standard `assembly-assets` location or explicit maintainer
`--assembly-assets`. Then separately run `complete-package.py inspect` on the
new output. Freeze the exact PKG, ELF, program, seed and inspection identities
before acceptance. New Windows bundles must carry that exact validated asset
through their required `--assembly-assets` input. Never add an owner shader
selection. Existing desktop bundles are unchanged until their asset is rebuilt.

For acceptance, back up and rename only `/data/pswaker/cache/<build-id>/` to an
unused sibling with the app closed. Start with empty runtime **and** driver
caches, the frozen bundled seed and no unrecorded gameplay warmup. Replay from
the same ordinary save and include the approach. Require:

- All included configurations/layout variants ready, pending zero, errors zero,
  cleanup complete and `known-shaders-prepared` before loading/gameplay.
- Zero raw missing-pipeline creation/wait events over the recorded route, including
  loading/approach, first resumed frame, first actions and repeats. Any ambiguous
  interval stays unresolved. Check `shader-wait-ns` records and frame counter
  deltas, not only the >35 ms hitch summary.
- Every captured configuration identity **and full description bytes** in the
  frozen seed. Ignore only capture metadata such as first-use frame number.
- Correct visible effects, representative controls/audio, preserved save/settings
  identities and normal Quit followed by a closed-app database/WAL return.

Seed membership alone cannot show an action happened: a seeded database already
contains the seeded rows. Video/action notes and raw waits are independent
requirements. A missing description, conflicting bytes or observed missing wait
requires correction, new candidate identities and another clean-cache replay.
Warm relaunches are a separately labelled comparison; they cannot pass a cold
candidate. No observed missing-pipeline wait is eligible for a waiver.

## Evidence record and decisions

Copy [pilot-record.example.json](../../evidence/ps4/coverage-137/pilot-record.example.json)
privately per inventory ID/variant and launch. Fill actual values, keep unknown
fields null, and retain failed attempts. Each record binds:

- Scenario/cohort/variant, entry and exit save IDs/hashes and actual route/room list.
- PKG, app version, program build/ELF/EBOOT, seed/asset manifest and fresh inspection.
- Actual platform/quality, cache listing/backup/rename and source cumulative snapshot.
- Timed first uses/repeats and visible effect observations, video and raw recorder
  IDs/hashes, preparation and shutdown evidence, database/WAL hashes/provenance,
  membership results and next ordinary-save references.
- Full cold preparation, final drain and compatible warm duration separately;
  launch-to-control observation; progress responsiveness and available memory
  observations through preparation and subsequent gameplay. Startup phases overlap.

There is no cold/warm duration ceiling. If the expanded seed cannot complete
reliably or leaves inadequate resources, return measured evidence for a design
decision before changing scope or moving preparation into gameplay. C000's
small seed is no full-game scaling result. Sample existing memory telemetry
through startup if available; otherwise explicitly request an instrumented
measurement before claiming expanded-seed memory viability. The parent campaign
requires an early expanded-capture scaling measurement and a final-candidate one.

Permitted statuses: `planned`, `awaiting-save`, `awaiting-console`,
`awaiting-analysis`, `failed-coverage`, `missing-observation`, `observed-pass`,
`accepted-with-gap`. Every inventory row starts `planned`; P01 is
`awaiting-console`. No inherited #107 acceptance changes those statuses.

Missing-observation waivers must record scenario/variant, missing evidence,
risk, exact candidate, explicit owner's acceptance text, date and decision
reference. Null acceptance is a request, never approval. Leave observed
failures in the report even after correction. Keep all actual saves, packages,
seeds, captures, video, private paths and raw logs in the existing private
artifact workflow. Publish only sanitized identities, observations and decision
references under `evidence/ps4/coverage-137`; append new reports without rewriting
archived evidence. Keep #137 open and `ready-for-human` while console work is next.
