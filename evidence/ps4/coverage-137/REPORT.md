# Windfall campaign preparation and pilot handoff (#137)

Prepared 2026-11-02 for [#137](https://github.com/Jcanotorr06/pswaker/issues/137),
part of [#136](https://github.com/Jcanotorr06/pswaker/issues/136).

**Candidate 137-D1 is assembled, freshly inspected and ready for owner discovery
on Windfall. Physical capture, expanded-seed preparation and frozen pilot
acceptance remain pending.** No post-Outset coverage, full-game pass, zero pilot
discoveries or accepted owner waiver is claimed. Keep #137 open; the next
required action is physical PS4 work.

## Prepared artifacts

The owner selected a Windfall ordinary save or normal early-story progression
to it. The [checklist](../../../docs/ps4/Windfall-coverage-checklist.md) fixes P01:
boat-side dock, square/vendor dialogue, bomb shop exterior, school/native menus
and return to the dock, followed by two repeats. No bombs/edited saves are needed.
CP-P01-entry/exit need actual owner backup references; none has been returned.

The [campaign](../../../docs/ps4/COVERAGE-CAMPAIGN.md) and
[inventory revision 1](../../../docs/ps4/COVERAGE-INVENTORY.md) define stable IDs,
all 49 sea sectors, story/dungeons/bosses, optional/interior routes, equipment/
enemies/effects, menus/cutscenes, world/camera states, overlaps and second quest.
Four fixed cohorts bind ordinary save checkpoints, cumulative snapshots and
deferred gates. All scenarios are planned; P01 is awaiting console. Detailed
room/variant observations remain private checklists, never assumed completion.

## Candidate identity

[candidate.json](candidate.json) records actual private snapshot/comparison/
assembly/fresh-inspection execution. No program/renderer code changed. The
verified #101 01.23 program was reused with the existing required default seed
selected automatically by normal game assembly.

| Item | Identity |
| --- | --- |
| Candidate / purpose | `137-D1` / Windfall discovery |
| App version / title | `01.23` / `PSWK00001` |
| Program build/cache ID | `6e885683f47a49a119ae` |
| PKG SHA-256 | `b410b25cd7dabc7ca1abe648e24254c214cb6faf4ca768b08fa2a39dca73f0b0` |
| Matching ELF SHA-256 | `400de6f1bb42fb4fc79f9399f290d2f0ee292e58ea03e4f8eea9c2e4dd7c32ab` |
| EBOOT SHA-256 | `bc142562457d3acfd7d90c126aa6ca75753889d07dd01b02661448fc4a8d9811` |
| Bundled seed SHA-256 | `7e3f8527203dc488b5ae646904c986ac596d7d4017db45a0fcb18ae29de51dc1` |
| Seed bytes / descriptions | 1,200,128 / 287 (1 clear, 286 GX) |
| Asset manifest SHA-256 | `e8d4b523aa45f58e272ccde4c258d76388200e26f28a9060b804f9969b4493fb` |
| Assembly report SHA-256 | `f00542ee5ee6be4a9c2b3134bc26d96d4c90e8ef0f8a419a4a490eb6fcc2316d` |
| Fresh inspection SHA-256 | `c74d1414cd597c893e1c24546ec008cdfc7db854e9472255609dee163ead3668` |
| Game image | USA `GZLE01`, revision 0; hash in campaign |
| Supported console | PS4 Slim / 9.00 / GoldHEN v2.4b18; actual pilot confirmation pending |

Normal `complete-package.py assemble --kind game` required no seed opt-in.
Assembly's extracted-payload inspection and a separate fresh `inspect` passed.
The Windows handoff PKG/ELF hashes matched; another extraction/inspection of
that copy reproduced inspection byte for byte. This establishes package/asset
identity, not console behavior.

## Initial cumulative milestone C000

The #112 warm database/WAL was freshly snapshotted with `pipeline-seed` into a
new private directory. #111's `verify-coverage.py` found all 287 configuration
identities/full description bytes in D1's seed, no conflicts and zero required
additions **from the historical capture**. This is not a pilot discovery result.

Snapshot: 1,208,320 bytes, SHA-256
`431578ed91f8f4831b1dcbf41876cfaa2cad77f931838c0a15742ad03d8bbdef`, matching
archived #112. Source DB/WAL hashes and the bundled seed's separate provenance
remain in candidate.json. Six source files (historical pair, default asset pair,
previous assembly/inspection) were hashed before/after, all unchanged. No
captures were merged/rewritten. Historical completed normal-Quit evidence was
missing; that limitation remains. C000 retains descriptions, not new observations.

The private artifact root retains `coverage-137/C000`, `C000-membership.json`,
`D1-complete-01.23`, `candidate.json` and execution logs. Windows Downloads holds
`PSWaker-137-Windfall-D1`, with matching ELF, manifests, `frozen-D1-seed`, C000,
checksums and owner instructions. Actual saves/seeds/descriptions/images/PKGs/
video and personal paths are absent from git. Earlier artifacts are preserved.

## Return, validation and unresolved evidence

The [record template](pilot-record.example.json) leaves unobserved values null.
Return actual entry/exit save references, three timecoded circuits, startup/
progress/effect/resource observations, normal Quit and complete closed-app
database/WAL/log exports. Warm data stays separate. Preserve failures and raw
waits of every duration.

On return, snapshot without changing sources, check full-byte membership and raw
`shader-wait-ns` events/frame counters throughout the route. The existing analyzer
only accepts Outset/forest targets; never relabel Windfall to get a pass. Use
raw artifacts at the agreed package/console boundary and fix only tooling gaps
demonstrated by the pilot. No private renderer queue test seam was added.

If discoveries require expansion, preserve provenance/all cumulative descriptions,
assemble/freshly inspect a new frozen candidate and replay CP-P01-entry with empty
runtime/driver caches. If additions are zero, still confirm frozen identity and
perform clean-cache validation with identifiable first uses. Observed missing
pipelines/waits require correction and replay. Eligible observation gaps require
named risk and explicit owner acceptance; no waiver is currently accepted.

Cold/warm startup, expanded-seed resource feasibility, correct rendering,
save/settings preservation and physical timing remain pending for this build/
route. C000 and #107 acceptance do not establish them. Next ordinary checkpoints
are CP-P01-exit and later CP-E1; neither has a returned artifact reference.
The pilot cannot be declared end-to-end complete until return and validation.
