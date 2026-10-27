# Wind Waker (GameCube) for PlayStation 4

This project aims to port [SwitchWaker](https://github.com/centollOS/SwitchWaker) to PS4 homebrew, using [PS5_SwitchWaker](https://github.com/griches/PS5_SwitchWaker) as a reference. SwitchWaker compiles The Wind Waker's GameCube decompilation and draws it with [Aurora](https://github.com/encounter/aurora).

## Status

The native game is integrated with the verified PS4 platform. The owner [reports gameplay through Outset, Forsaken Fortress and Windfall to Dragon Roost Island](evidence/ps4/startup-17/console-2026-10-25/REPORT.md), with no observed graphics/audio glitches and brief loading/first-effect pauses. Controlled content failures, repaired startup and owner-confirmed seeded save/settings comparisons complete the bounded [startup checkpoint evidence review](evidence/ps4/startup-17/REPORT.md). The confirmed hardware is a **PS4 Slim running firmware 9.00 / GoldHEN v2.4b18**, with USA disc `GZLE01`, revision 0.

The [maintained disc-free platform diagnostic](docs/ps4/README.md) passed its [bounded platform gate](evidence/ps4/verification-15/REPORT.md). Those synthetic checks do not validate the game candidate. Complete route/audio evidence, full storage-failure recovery and performance remain separate acceptance checkpoints.

The [Outset/forest route and audio checkpoint](docs/ps4/ROUTE-AUDIO.md) adds repeated audio-defect counters and pending-card/audio/GPU shutdown coordination. The [owner's follow-up to the 01.06 handoff](evidence/ps4/route-19/owner-return-01.06/REPORT.md) confirms the requested title-through-Outset scenes/actions without visual or audible anomalies in both empty-cache and retained-cache runs, completed-save relaunch and clean normal port Quit. Logs could not be retrieved; candidate/cache corroboration and internal shutdown-stage evidence remain outstanding.

The canonical planning map is [Plan the first playable Wind Waker port for PS4 Slim 9.00](https://github.com/Jcanotorr06/pswaker/issues/1). It tracks the decisions needed before implementation. The [initial porting investigation](docs/PORTING_PLAN.md) and [platform research](docs/research/ps4-platform.md) provide background, using [Dusklight's PS4 port](https://github.com/BgbrhrWatchinOVO/dusklight-ps4) as the main platform reference.

This repository and the releases contain no game data and no keys. You need your own disc, dumped yourself.

The [returned save/settings checkpoint](evidence/ps4/persistence-20/console-return-2026-10-26/REPORT.md)
confirms persistence after full relaunch, a separate complete-package update,
cache-only clearing and Quit without saving unsaved gameplay. Runtime manifests
and byte-identical settings snapshots corroborate the owner's results. A logged
Quit panic after an idle card remains an unresolved internal shutdown finding;
full storage-failure recovery remains separate.

The [storage recovery candidate](docs/ps4/STORAGE-RECOVERY.md) adds whole-save
staging, previous valid backups, explicit corruption recovery and a regression
for the captured GBA shutdown panic. Its [controlled owner checklist](docs/ps4/Storage-recovery-checklist.md)
isolates genuine progress and exercises failure/pending-write behavior. Installed
console acceptance remains pending for that exact binary.

The [frame-pacing instrumentation](docs/ps4/FRAME-PACING.md) records completed
PS4 game-frame flips, independent Outset/forest samples, shader waits and separate
startup/loading phases. The [01.12 return](evidence/ps4/performance-22/console-return-01.12/REPORT.md)
preserves warm numerical successes, cold shortfalls and unverified physical timing.
The owner [accepts current performance for the initial release candidate](evidence/ps4/performance-22/OWNER-DECISION.md)
and defers further optimization to [#51](https://github.com/Jcanotorr06/pswaker/issues/51).

The [integrated first-playable review](evidence/ps4/integrated-23/REPORT.md)
uses the existing **01.13** complete package, retaining its exact identity and
the performance exception. The [consolidated owner checklist](docs/ps4/Integrated-checklist.md)
covers the 01.12-to-01.13 update, repeated route, controls/audio, save/recovery,
shutdown and evidence return. **Final integrated console acceptance remains pending.**

## Repository map

| Area | Ownership |
| --- | --- |
| [tools/pswaker](tools/pswaker/) | Maintained host commands and build-input ownership |
| [platform/ps4](platform/ps4/) | PS4 runtime, CMake/toolchain definitions, locks, patches, provenance and target notices |
| [tests/ps4](tests/ps4/) | Python tests, native harnesses and synthetic fixtures |
| [docs/ps4](docs/ps4/README.md) | Maintained PS4 build instructions and owner checklists |
| [evidence/ps4](evidence/ps4/) | Retained checkpoint groups and their original records |

Project planning, research, domain vocabulary and agent guidance remain at their
project-level locations. Start with the [diagnostic workflow](docs/ps4/README.md)
or [installed-game workflow](docs/ps4/GAME-STARTUP.md).

The compiled [host renderer reference](platform/ps4/host-renderer/) and its CMake
recipe remain target inputs, separate from the regression harnesses. The
[frame-pacing owner example](platform/ps4/frame-pacing-owner.example.json) also
remains target-associated maintained data.

## Standing on the shoulders of others

This repository draws inspiration from several community projects.

- [centollOS/SwitchWaker](https://github.com/centollOS/SwitchWaker): Native Nintendo Switch port of The Legend of Zelda: The Wind Waker (GameCube).
- [griches/PS5_SwitchWaker](https://github.com/griches/PS5_SwitchWaker): A PS5 homebrew port of SwitchWaker.
- [BgbrhrWatchinOVO/dusklight-ps4](https://github.com/BgbrhrWatchinOVO/dusklight-ps4): A native Twilight Princess port with PS4 adaptations for Aurora, Dawn, SDL3 and Mesa.
