# Early-story preparation and owner handoff (#139)

Prepared 2026-11-02 for [#139](https://github.com/Jcanotorr06/pswaker/issues/139),
part of [#136](https://github.com/Jcanotorr06/pswaker/issues/136).

**139-D1 is identified and freshly inspected for discovery. Physical early-story
captures, seed expansion, frozen clean-cache validation, CP-E1 and C-E remain
pending.** The issue stays open with physical PS4 work next. No early-story or
full-game acceptance, zero new discoveries, or owner-approved waiver is claimed.

## Fixed scope and owner instructions

The [checklist](../../../docs/ps4/Early-story-coverage-checklist.md) supplies
ordinary-save routes from CP-E0 (new original-quest file before departure) to
CP-E1 (Farore's Pearl, before departure from Forest Haven for Greatfish).
It covers the inventory's **36 E rows**: S01-S07, B01-B02, I01-I11,
Q01-Q10/Q16-Q17 and F01-F04. P01 is a shareable Windfall subset, not a
substitute for S04 or the cohort. Original inventory IDs/boundaries are unchanged.

The [scenario matrix](scenario-matrix.json) binds every E row to planned entry/
exit saves and the discovery identity, leaving observed candidate/cache,
actions, capture/membership/wait results and evidence references unfilled.
Its 42 C/O ledger rows keep E reachability unknown until observed and assign
remaining content to named A routes under the same IDs. The checklist assigns
later equipment/interior/enemy/menu/world/overlap variants explicitly. No
unobserved gate is claimed inaccessible or completed. C/O IDs retain A membership.

The [launch record template](scenario-record.example.json) captures first uses/
repeats, exact identities, cache state, preparation/progress/resources, video/
raw logs, shutdown, database/WAL provenance, comparisons and eligible waivers.
Unknowns remain null. Q rows need first use plus at least three repeats. Save
aliases and CP-E1 are plans until an actual private backup/hash is returned.

## Prepared candidate and corpus

[candidate.json](candidate.json) records the freshly checked artifacts.
**139-D1 reuses the exact 137-D1 package/build/seed bytes**. No renderer,
program, package payload, seed asset or desktop bundle changed; no replacement
or expanded seed has been invented in the absence of new descriptions.

| Artifact | Identity |
| --- | --- |
| App / title | `01.23` / `PSWK00001` |
| Program / disposable cache build | `6e885683f47a49a119ae` |
| Complete package SHA-256 | `b410b25cd7dabc7ca1abe648e24254c214cb6faf4ca768b08fa2a39dca73f0b0` |
| Matching ELF SHA-256 | `400de6f1bb42fb4fc79f9399f290d2f0ee292e58ea03e4f8eea9c2e4dd7c32ab` |
| Seed SHA-256 | `7e3f8527203dc488b5ae646904c986ac596d7d4017db45a0fcb18ae29de51dc1` |
| Seed descriptions | 287 actual historical descriptions: 1 clear, 286 GX |
| Fresh inspection SHA-256 | `c74d1414cd597c893e1c24546ec008cdfc7db854e9472255609dee163ead3668` |
| C000 snapshot SHA-256 | `431578ed91f8f4831b1dcbf41876cfaa2cad77f931838c0a15742ad03d8bbdef` |

The copied Windows handoff was freshly extracted/inspected with the maintained
package CLI. Its inspection reproduces #137's record byte for byte. PKG, ELF,
seed and C000 hashes match the source. C000 was independently snapshotted and
validated again; all 287 configuration identities **and complete description
bytes** are present in the frozen D1 seed. Eight original files were hashed
before/after and unchanged. Original source DB/WAL provenance and C000's
original manifest are retained separately from the new snapshot's provenance.

This is a historical membership check, not an early-story discovery count or
gameplay observation. C000 derives from #112, whose normal-Quit evidence was
missing; revalidation does not repair that limitation. #137's physical pilot
has no returned capture available here. There is no later compatible cumulative
corpus to incorporate yet. An independently accumulated later return would
require compatibility/conflict/provenance review before continuation.

The private Downloads handoff `PSWaker-139-Early-story-D1` contains the PKG,
matching ELF, manifests, frozen seed, C000/source provenance, checksum inventory,
current checklist/matrix, blank per-scenario records and action-note sheet.
Private `early-story-139` retains fresh inspection, C000 revalidation/membership,
source-preservation records and host-check logs. No packages, saves, databases,
gameplay captures, private paths or game data are committed here. Archived #137
records and its handoff remain unchanged.

## Return, iteration and middle-story boundary

The owner must back up saves/settings separately, preserve pre-event/pre-boss
ordinary checkpoints, run the routes physically, Quit normally, and retrieve
immutable closed-app DB/WAL/log/video/action/save milestones before relaunch.
Keep one compatible cumulative discovery database across save restorations.

On return the agent will validate cumulative standalone snapshots, compare all
identities/description bytes, retain failures/source provenance and prepare an
expanded seed from actual descriptions. Assemble and freshly inspect a new
identified frozen validation candidate, then request clean runtime/driver-cache
replay with no hidden gameplay warmup. Correct observed missing descriptions/
creation/waits and replay; retain a separate compatible warm comparison. Raw
waits and frame-counter deltas, preparation before gameplay, full-byte membership
and identifiable physical actions are independent requirements. Discovery and
learned caches cannot establish the bundled seed's coverage.

CP-E1 and cumulative **C-E** must be returned with actual save/DB/WAL hashes,
reload location, equipment/flags, compatible build, validated standalone seed/
source provenance and outstanding ID/variant ledger for
[#140](https://github.com/Jcanotorr06/pswaker/issues/140). Both artifact references
are currently null. S08/Greatfish is beyond this cohort. Later optional circuits
retain their named inventory IDs under #142; story-dependent variants pass to
the named M/L routes. Pre-event backups remain necessary for disappearing content.

Rendering/effect correctness, residual stalls, save/settings behavior, expanded
preparation/resource feasibility and cold/warm timing all await physical
evidence. #138's scaling and #144's final full-game acceptance remain separate.
Every missing-observation waiver needs the exact scenario/variant, missing
evidence, risk, candidate, explicit owner text/date/decision. None is accepted.
Observed missing-pipeline creation/waits cannot be waived. Passing host checks
or merging preparation does not close #139.

See [validation and independent review](VALIDATION.md) for host results and
their limits.
