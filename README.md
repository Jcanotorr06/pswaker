# Wind Waker (GameCube) for PlayStation 4

This project aims to port [SwitchWaker](https://github.com/centollOS/SwitchWaker) to PS4 homebrew, using [PS5_SwitchWaker](https://github.com/griches/PS5_SwitchWaker) as a reference. SwitchWaker compiles The Wind Waker's GameCube decompilation and draws it with [Aurora](https://github.com/encounter/aurora).

## Status

The native game is integrated with the verified PS4 platform. The private [startup candidate](platform/ps4/evidence/startup-17/REPORT.md) targets title, name entry, prologue and access to Outset; its [owner console checkpoint](platform/ps4/Startup-checklist.md) is pending. Host builds and package inspection do not establish playable acceptance. The hardware target is a **PS4 Slim running firmware 9.00 / GoldHEN v2.4b18**, with USA disc `GZLE01`, revision 0.

The [maintained disc-free platform diagnostic](platform/ps4/README.md) passed its [bounded platform gate](platform/ps4/evidence/verification-15/REPORT.md). Those synthetic checks do not validate the game candidate. Full-route rendering/audio, save durability and performance remain later acceptance checkpoints.

The canonical planning map is [Plan the first playable Wind Waker port for PS4 Slim 9.00](https://github.com/Jcanotorr06/pswaker/issues/1). It tracks the decisions needed before implementation. The [initial porting investigation](docs/PORTING_PLAN.md) and [platform research](docs/research/ps4-platform.md) provide background, using [Dusklight's PS4 port](https://github.com/BgbrhrWatchinOVO/dusklight-ps4) as the main platform reference.

This repository and the releases contain no game data and no keys. You need your own disc, dumped yourself.

## Standing on the shoulders of others

This repository draws inspiration from several community projects.

- [centollOS/SwitchWaker](https://github.com/centollOS/SwitchWaker): Native Nintendo Switch port of The Legend of Zelda: The Wind Waker (GameCube).
- [griches/PS5_SwitchWaker](https://github.com/griches/PS5_SwitchWaker): A PS5 homebrew port of SwitchWaker.
- [BgbrhrWatchinOVO/dusklight-ps4](https://github.com/BgbrhrWatchinOVO/dusklight-ps4): A native Twilight Princess port with PS4 adaptations for Aurora, Dawn, SDL3 and Mesa.
