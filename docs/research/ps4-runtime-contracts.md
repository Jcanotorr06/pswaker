# PS4 runtime contracts

Investigated 2026-10-18 for [Determine the PS4 runtime requirements for assets, controls, audio and saves](https://github.com/Jcanotorr06/pswaker/issues/4). Source research only: no build, disc extraction or console test. Scope: native Slim/9.00, GZLE01 revision 0, title/name/prologue/Outset and forest, stock textures, 30 Hz logic, target 720p30, save/reload across application restarts, Windows through WSL2/Linux.

Baselines: PS5_SwitchWaker `3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0` (P); its SwitchWaker `ba8d0a31446cd53ceaebd6b7269cca641e73bf4c` (S); Aurora `3227d76c60e1e782ca576610bce61c9e7744d8be` (A); Dusklight PS4 `fd483cf5d4f04b0f4d887ff412d0e8691925de08` (D). D's inherited SDL3 tag resolves to `68159af2b34cc4fe5b3548faa89e87a69e4d2dce` (L). D patches a different Aurora baseline; adaptation is required. [Inventory][D-build]

## Assets and disc access

P builds with `COS_RUNTIME_ASSETS=ON` and stub headers, without an owner disc. Preparation applies S's Aurora patches before P's and fetches Dolphin DSP HLE. [Build][P-build], [preparation][P-prep]

S fills registered arrays from the owner's `main.dol`, REL files and Yaz0/RARC content after Aurora DVD opens and before game initialization. DOL/REL SHA-1 checks reject mismatching content; typed float arrays receive endian conversion. Models, stages, messages and audio continue through DVD reads. This is runtime loading, not installation of an extracted game tree. [Loader][S-assets], [startup][S-main]

S requires a readable regular file, GameCube magic `0xC2339F3D`, ID `GZLE01`, revision byte zero; failures produce `PC_EXIT_DISC`. P discovers the first `.iso`, `.gcm` or `.ciso` in `/app0`, then `/mnt/usb0` and `/mnt/usb1`. Its nod shim handles raw GameCube images and sparse CISO; unpatched S rejects CISO. Arbitrary compressed formats are not established. [Validation][S-disc], [P discovery/validation][P-game], [reader][P-nod]

D substitutes a nod-compatible reader supporting GameCube ISO plus a separate decrypted-Wii path, unnecessary here. Its entry prefers embedded `/app0/game.iso`, otherwise `/data/dusklight-ps4/game.iso`. Embedded game data contradicts this project's external-assets scope: reuse the root separation, not that packaging option. [Entry/reader][D-game]

**Human choices:** fixed external filename, configured path or deterministic discovery; internal `/data/<project>/` or USB input; raw ISO/GCM only or also CISO; missing/wrong disc screen with retry/exit or notification then exit. P demonstrates notification plus shell exit, not a file picker. Define multiple-candidate and USB-removal behavior. No game assets or keys belong in source or public distribution. [P failure UI][P-game]

## Writable data, settings and saves

| Consumer | Source contract | PS4 implication |
| --- | --- | --- |
| Package | D treats `/app0` as read-only | Executable/resources/defaults separate from mutable data. |
| Mutable roots | D creates `/data/dusklight-ps4/{user,logs,cache}`; copies config only when absent | Candidate layout; project path and firmware access remain unselected/untested. |
| S user/cache | User root derives from executable; `COS_CACHE_DIR` overrides cache only | `COS_RUN_DIR` alone does not redirect saves/settings. |
| S settings | `COS_SETTINGS` override; default executable-relative `user/settings.ini` | Redirect before early settings load. |
| A cards | Default GCI folders; raw images optional | `<user>/<region>/Card A` or `Card B`; alternatively `MemoryCardA.<region>.raw`. |

Sources: [D entry][D-game], [S paths][S-main], [settings][S-settings], [cards][A-card]. P's writable `/app0/user` is a PS5 homebrew-folder assumption, unsuitable as the PS4 storage contract. [P paths][P-game]

A's GCI writes use atomic-file updates: flush/close temporary SDL stream, then rename over destination. S settings independently use stdio temporary file, flush, close and rename, without explicit `fsync`. These mechanisms do not establish PS4 power-loss durability. Preserve checked write failures and existing saves; verify selected SDL/filesystem replacement semantics. [GCI][A-gci], [file updates][A-file], [atomic commit][A-io], [settings][S-settings]

**Human choices:** shared versus console-user-specific roots; GCI versus raw card; backup/export, corruption recovery and persisted settings; update/uninstall preservation policy. D's first-run config copy preserves an existing config in source, not proven package-update persistence. Sources do not establish PS4 system SaveData-service integration. Acceptance must save through the game UI, wait for completion, close, relaunch and load the same name/progress; separately test package update without overwriting external data. [D entry][D-game], [card backend][A-card]

## DualShock 4 input

| Reference | GC A / B / X / Y | Menu/start |
| --- | --- | --- |
| A baseline PS4 | Cross / Circle / Square / Triangle | Options = Start. |
| P patched PS5 | Cross / Square / Circle / Triangle | Touchpad click = SDL Back/options menu. |
| D patched PS4 | Circle / Cross / Triangle / Square | Touchpad = Back/menu; Share reserved for shell; Options = Start. |

All map R1 to Z and translate sticks/D-pad. Defaults conflict: owner selection must also govern HUD glyphs and menu confirm/cancel. [A mapping][A-pad], [P mapping][P-aurora], [P menu][P-game], [D input][D-game], [D mapping][D-aurora]

D uses `scePadReadState`, a 120-byte sample (connection `0x4c`, timestamp `0x50`), 0.12 stick dead zone and trigger bytes normalized to 0..1. Virtual joystick triggers become signed SDL axes. A preserves analog travel and emulates digital L/R via thresholds; digital activation forces analog value 180. DS4 lacks the GameCube terminal click: partial/full trigger behavior needs an explicit policy. [D pad][D-game], [A triggers][A-pad]

D rescans users every second and neutralizes shell-intercepted input. Failed/disconnected reads skip updating the last sample; `pad_player` checks handle existence. **Source inference:** held movement can remain stale, not a hardware observation. Decide neutralization, pause/prompts and controller ownership. Test disconnect while moving/holding triggers, reconnect, shell return, no-pad startup and menu input suppression. [D polling][D-game]

## Audio, threads and exit

S's Dolphin DSP HLE feeds a clocked AI DMA thread: 32/48 kHz big-endian signed-16 stereo, right channel first, converted for SDL. Interrupts advance independently of rendering; queued output caps at 200 ms and drops excess. Audio startup failure may leave DMA running silently. [AI][S-ai], [DSP][S-dsp]

D enables inherited SDL driver `ps5` on PS4. L opens `SceAudioOut` at 48 kHz float stereo, 256-frame grains, with 64-byte-aligned buffer and blocking submissions; close submits null before closing. Keep S's DMA pacing plus SDL conversion; P's standalone platform-audio helper does not replace it. Validate channel order, resampling, underruns, latency and transition audio on Slim/9.00. [D SDL][D-sdl], [driver][L-audio]

Required runtime behavior includes pthreads, monotonic clocks, TLS, mutexes/condition variables and C++ threads/atomics. D links pthread stubs and replaces unavailable application `_umtx_op` atomic waits with condition-variable waits. Verify S's actual workers against that runtime. [D link][D-game], [atomic adaptation][D-atomic], [DSP workers][S-dsp]

P/D request `sceSystemServiceLoadExec("exit", ...)`; P bypasses game static destructors through its exit hook. This does not prove worker draining or persistence of an interrupted save. Define normal quit behavior; validate repeated launch/close, completed saves, audio teardown and logs. All Slim/9.00 API, permission, update and performance outcomes remain untested. [P exit][P-game], [D exit][D-game]

[P-build]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/tools/build.sh
[P-prep]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/tools/setup-source.sh
[P-game]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/patches/switchwaker.patch
[P-nod]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/nod/nod.cpp
[P-aurora]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/patches/aurora.patch
[S-assets]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/src/pc/runtime/pc_assets.cpp
[S-main]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/src/pc/runtime/pc_main.cpp
[S-disc]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/src/pc/runtime/pc_disc.cpp
[S-settings]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/src/pc/features/pc_settings.cpp
[S-ai]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/sdk/src/audio/AI.cpp
[S-dsp]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/sdk/src/audio/DSP.cpp
[A-card]: https://github.com/encounter/aurora/blob/3227d76c60e1e782ca576610bce61c9e7744d8be/lib/dolphin/card.cpp
[A-gci]: https://github.com/encounter/aurora/blob/3227d76c60e1e782ca576610bce61c9e7744d8be/lib/card/CardGciFolder.cpp
[A-file]: https://github.com/encounter/aurora/blob/3227d76c60e1e782ca576610bce61c9e7744d8be/lib/card/FileIO.cpp
[A-io]: https://github.com/encounter/aurora/blob/3227d76c60e1e782ca576610bce61c9e7744d8be/lib/io.cpp
[A-pad]: https://github.com/encounter/aurora/blob/3227d76c60e1e782ca576610bce61c9e7744d8be/lib/dolphin/pad/pad.cpp
[D-build]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/BUILDING.md
[D-game]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/patches/dusklight-ps4.patch
[D-aurora]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/patches/aurora-ps4.patch
[D-sdl]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/patches/sdl3-ps4.patch
[D-atomic]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/patches/libcxx-ps4-atomic-wait.patch
[L-audio]: https://github.com/mshivam019/dusklight-ps5/blob/68159af2b34cc4fe5b3548faa89e87a69e4d2dce/src/audio/ps5/SDL_ps5audio.c
