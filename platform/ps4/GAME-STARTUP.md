# Installed-game startup checkpoint (#17)

The follow-up [route/audio checkpoint](ROUTE-AUDIO.md) adds repeated audio defect
counters and card/audio/GPU shutdown coordination. Its candidate and owner
checklist supersede the startup-only shutdown limits below for new builds.

This integrates pinned SwitchWaker with the maintained PS4 platform. Acceptance
requires owner observations of title, name entry, prologue and access to Outset
on PS4 Slim / 9.00 / GoldHEN v2.4b18. Building a package does not establish that
console result. The [candidate report](evidence/startup-17/REPORT.md) records
actual artifacts and outstanding owner checks.

## Build and package privately

Use the locked Linux/WSL2 host and an explicit maintained platform root that
passed #15. The game uses its source-built Dawn, SDL3, Mesa and runtime and
builds a separate game-local Aurora with DVD, THP and GCI support. The verified
diagnostic tree is preserved.

    PLATFORM_ROOT="$HOME/.cache/pswaker/maintained-15-a"
    GAME_ROOT="$HOME/.cache/pswaker/game-17"
    bash platform/ps4/build-game.sh "$GAME_ROOT" "$PLATFORM_ROOT" 01.00

    python3 platform/ps4/complete-package.py assemble \
      --image "/absolute/path/to/your/USA-revision-0.iso" \
      --program-stage "$GAME_ROOT/build/program-stage" \
      --elf "$GAME_ROOT/build/switchwaker" \
      --platform-root "$PLATFORM_ROOT" --kind game --app-version 01.00 \
      --output "$HOME/.local/share/pswaker-private/startup-17-01.00"

    python3 platform/ps4/complete-package.py inspect \
      "$HOME/.local/share/pswaker-private/startup-17-01.00" \
      --platform-root "$PLATFORM_ROOT"

The output's parent must exist. Complete packages stay outside the repository.
See [COMPLETE-PACKAGES.md](COMPLETE-PACKAGES.md) for private output and inspection.
Game identity is PSWK00001 / IV0000-PSWK00001_00-PSWAKERGAME00000. Versions
change SFO metadata, never that identity.

Use a fresh game root for different source/patch inputs. The source lock includes
the decompilation used to generate data-free headers and RecompCore's DSP HLE.
Preparation reconstructs expected patched sources and rejects unrecorded edits.
The 163 stub arrays are filled from pinned installed DOL/REL objects at runtime.
No image, extracted arrays, PS5 binary or imported shader cache is compiled in.

The compiled build ID covers port files, prepared sources/stubs, actual platform
archives/runtime/toolchain and tool versions. The full inventory remains in
game-build-inputs.json. Staging rejects drift and requires a matching unstripped
ELF with source lines. The build audits Jaguar flags and TLS initializer imports
and uses the checked ELF → SELF → GP4 → PKG path.

If the host's zlib has advanced, recover the locked host using the
[documented temporary recovery and restoration](evidence/verification-15/REPORT.md#host-drift-and-recovery),
or recover the recorded environment independently. Do not bypass verification.

## Reviewed adaptations

The three PS5 reference game fixes remain separate ordered patches:

| Fix | Review and PS4 disposition |
| --- | --- |
| Division | Guard three cLib angle-calculation divisions when scale is zero. Callers use a short difference/scale or the game's bounded angle domain. Avoid x86 faults without a foreign signal recovery handler. This does not audit every game division. |
| Floating-point lookup | Bound the scaled atan-table index, including NaN/infinity, before integer conversion; select entry zero for invalid input, following the reference's GameCube wraparound analysis. Retain finite in-range indexing. |
| Callback returns | Mask the low byte for Execute/IsDelete/Delete callbacks that can return bool through an int interface. Preserve Create's phase codes. Address the x86-64 return-register mismatch without adopting a foreign calling convention. |

The integration patch adapts PS4 startup/paths, retains synchronous FIFO ordering
and avoids excluded HD-streaming and 60 Hz APIs. Original prompts, stock textures
and original 30 Hz logic remain. The raw reader is platform-independent MIT C++
from the pinned reference; broader reader formats cannot bypass full-image
validation at the fixed installed path.

PS4 ABI handling uses the selected DolphinPS4 CRT, constructors, TLS,
synchronization and signal logger. Constinit declarations describe the actual
zero-initialized current-heap/thread TLS variables, removing weak initializer
imports rejected by the SELF converter. Runtime units are executable objects:
an archive would discard startup-only constructors and the weakly referenced
crash logger.

The logger's PS4 FreeBSD signal numbers, SA_SIGINFO=0x40, measured context offset
0x40, register indexes and fault-address offset are PS4 runtime assumptions,
not PS5 layouts. No PS5 division table or instruction-skipping handler is used.
Diagnostic evidence does not prove game-fault reporting; retain the matching
ELF and return available traces.

## Runtime and evidence

- Game content is read-only at /app0/game.iso. Check full size and accepted
  SHA-1, then retain pinned runtime DOL/REL checks. Missing, unreadable or invalid
  content stops with visible rebuild/reinstall guidance. No external search.
- GCI saves use /data/pswaker/saves/USA/Card A and Card B. The settings consumer
  is fixed at /data/pswaker/settings.ini. Quality remains fixed; the desktop
  developer-settings section is not loaded. Full settings/persistence follow
  in the next slice.
- Disposable caches use /data/pswaker/cache/<compiled-build-id>/. Startup
  records existing file names, sizes and SHA-1 before Aurora opens them.
- The first game frame shows the DualShock 4 legend; touchpad opens the basic
  port menu. Failed/disconnected reads clear input and stop at a frame boundary.
  Reconnection requires release and a deliberate Cross press. The initial
  terminal-click threshold is 90%, pending hardware checks.
- Keep clock-driven DMA/DSP conversion through SDL3's PS4 backend. Setup,
  format and queue failures are logged. Heartbeats include DMA frame/energy
  counters; these do not prove audible output or route correctness.
- Normal exit requests SDK shutdown and joins the DMA producer before Aurora
  destroys SDL audio. Fatal paths preserve those objects until process exit.
  Full write coordination and persistence acceptance remain later work.
- Content validation and known-shader preparation show progress before gameplay.
  Cold startup has no imported game pipeline cache; the actual known queue may
  be zero. New shaders compile synchronously when encountered; gameplay stalls
  remain part of later performance tests.
- Record startup/preparation time, allocated internal/output dimensions, scene
  creation requests/intervals, game-frame/resource state, errors and last
  completed stage. Scene requests do not claim visible loading/transition
  completion; pair timestamps with owner observations of usable scenes.

Retrieve /data/pswaker/logs/platform.log, platform.prev.log and last-stage.txt
after each launch, plus /data/DolphinPS4/crash.log and xmb-trace.log/boot-trace.log
if present. Keep host package/SELF/ELF hashes with these build/cache identities.
Collect before another launch rotates the current log.

The program checks the allocated internal texture for 1280×720 and records
scanout dimensions separately. No reduced resolution, faster logic or alternate
textures are selected.

## Controlled content failures

    python3 platform/ps4/content-failure-package.py \
      "$HOME/.local/share/pswaker-private/startup-17-01.00" \
      --platform-root "$PLATFORM_ROOT" --variant missing --app-version 01.01 \
      --output "$HOME/.local/share/pswaker-private/startup-17-missing-01.01"

Repeat with unreadable/01.02 and invalid/01.03. Missing omits the image;
unreadable installs a directory at its path; invalid keeps full length and a
valid header, flipping one non-header byte. The tool reinspects the valid
parent, preserves its executable and freshly extracts the fault package to
check its identity, payload and intended fault. No runtime bypass is introduced.

Build a repaired complete package with the normal assembly CLI and version
01.04. Back up and hash seeded saves/settings on the PC before installation,
retrieve those files after each stopped launch and compare bytes. Keep cache
operations separate. Returned console evidence is required for preservation.

Keep artifacts private. Retain game-license-review.json, its game/DSP notice
corpus, the platform license audit and actual package inspection together.
Inherited SDK module/stub rights and combined distribution terms remain
unresolved under [LICENSING.md](LICENSING.md).
