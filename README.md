# Wind Waker (GameCube) for PlayStation 4

This project aims to port [SwitchWaker](https://github.com/centollOS/SwitchWaker) to PS4 homebrew, using [PS5_SwitchWaker](https://github.com/griches/PS5_SwitchWaker) as a reference. SwitchWaker compiles The Wind Waker's GameCube decompilation and draws it with [Aurora](https://github.com/encounter/aurora).

## Status

The [maintained disc-free platform diagnostic](platform/ps4/README.md) has passed its [bounded platform gate](platform/ps4/evidence/verification-15/REPORT.md): two independent clean builds and the installed 01.04 candidate's own three owner-observed console runs. The rebuilt artifacts have separate hashes and no console results. There is no integrated playable game yet. The initial hardware target is a **PS4 Slim running firmware 9.00**, with USA disc `GZLE01`, revision 0. Game rendering, audio, persistence and performance remain later acceptance checkpoints.

The canonical planning map is [Plan the first playable Wind Waker port for PS4 Slim 9.00](https://github.com/Jcanotorr06/pswaker/issues/1). It tracks the decisions needed before implementation. The [initial porting investigation](docs/PORTING_PLAN.md) and [platform research](docs/research/ps4-platform.md) provide background, using [Dusklight's PS4 port](https://github.com/BgbrhrWatchinOVO/dusklight-ps4) as the main platform reference.

This repository and the releases contain no game data and no keys. You need your own disc, dumped yourself.

## Standing on the shoulders of others

This repository draws inspiration from several community projects.

- [centollOS/SwitchWaker](https://github.com/centollOS/SwitchWaker): Native Nintendo Switch port of The Legend of Zelda: The Wind Waker (GameCube).
- [griches/PS5_SwitchWaker](https://github.com/griches/PS5_SwitchWaker): A PS5 homebrew port of SwitchWaker.
- [BgbrhrWatchinOVO/dusklight-ps4](https://github.com/BgbrhrWatchinOVO/dusklight-ps4): A native Twilight Princess port with PS4 adaptations for Aurora, Dawn, SDL3 and Mesa.
