# PS4 porting plan

The canonical decision map is [Plan the first playable Wind Waker port for PS4 Slim 9.00](https://github.com/Jcanotorr06/pswaker/issues/1).
This document preserves the initial investigation and candidate milestones;
the map's decision tickets hold subsequent answers and the approved specification.

Investigated 2026-10-18. Target supplied by the project owner: PS4 Slim,
firmware 9.00. All milestones below are pending; this repository currently
contains documentation, with no PS4 implementation.

## Proposed approach

Retain SwitchWaker's game code, runtime asset loading and Aurora compatibility
layer. Use **Dusklight's PS4 port as the primary platform reference**, and the
PS5 Wind Waker port for game-specific fixes and asset integration. Adapt and
validate the PS4 platform code against Wind Waker's dependency versions.
Treat this as a candidate architecture until it runs on the target hardware.

The candidate rendering path is:

```text
SwitchWaker game code -> Aurora -> Dawn/WebGPU -> PS4 Mesa RADV/GNM -> video output
```

The PS5 build already integrates Aurora, Vulkan-only Dawn, custom SDL3 drivers
and a disc reader. It also explicitly compiles for `znver2` and invokes a PS5
link recipe. Those settings cannot be carried into the PS4 build unchanged.
See its [CMake integration][ps5-cmake] and [build entry point][ps5-build].

[Dusklight PS4's build inventory][dusklight-build] supplies a directly relevant
OpenOrbis/DolphinPS4 runtime, Mesa 26.0.8, Dawn and SDL3 combination. Its
[Aurora patch][dusklight-aurora] adapts direct-display presentation and other
console behavior. This is stronger evidence than a standalone Vulkan driver,
but it does not establish Wind Waker compatibility on firmware 9.00. See the
[platform research](research/ps4-platform.md) for evidence and limits.

## Source baseline

Use immutable revisions for the first experiment, then update deliberately.
The PS5 port's pinned SwitchWaker revision gives its patches a known base.

| Component | Investigated revision | Role |
| --- | --- | --- |
| PS5_SwitchWaker | `3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0` | Reference platform integration and game fixes |
| SwitchWaker | `ba8d0a31446cd53ceaebd6b7269cca641e73bf4c` | Game baseline pinned by the PS5 port |
| Aurora | `3227d76c60e1e782ca576610bce61c9e7744d8be` | Baseline pinned by that SwitchWaker revision |
| Dusklight PS4 | `fd483cf5d4f04b0f4d887ff412d0e8691925de08` | Primary PS4 platform reference |

Sources: [PS5 submodule][ps5-submodule] and [SwitchWaker's Aurora configuration][aurora-pin].
Apply SwitchWaker's Aurora patches before the relevant console adaptations;
the unpatched Aurora revision alone is not the PS5 port's dependency tree.
Its [source preparation script][ps5-source] records that ordering.

Dusklight PS4 patches a different Aurora baseline (`e281999cdb4f`) and uses its
PS5 ancestor's Dawn/SDL3 dependency tags. Port the relevant changes deliberately;
do not mix archives or expect its patches to apply directly to Wind Waker's
pins. Its [build inventory][dusklight-build] records Mesa `80c7811` and the
DolphinPS4 runtime `b1879cc` as starting points to resolve to full commits.

The published Dusklight scripts are a reference, not yet a turnkey clean build.
The maintainer explicitly says end-to-end rebuilding is unverified. At the
revision above, [build-dawn.sh][dusklight-dawn] and
[build-sdl3.sh][dusklight-sdl] require a root `toolchain/ps4.cmake`, while
[build-probe.sh][dusklight-probe] requires `probe-dawn/`; those paths are absent
from the published tree. Resolve or reconstruct these inputs before presenting
the scripts as usable build instructions.

The separate [mesa-ps4][mesa] and archived [orbis-porting-kit][kit] remain
alternative references. The kit's advertised `orbsdk` successor returned 404
during investigation. Do not introduce it as a required dependency.

## Work to retain and replace

| Area | PS4 work |
| --- | --- |
| Game and SDK compatibility | Retain the upstream game/Aurora structure; inspect the PS5 game's fixes individually |
| Graphics | Adapt Dusklight's PS4 Mesa/Dawn/Aurora integration; verify shader compilation, presentation and caches |
| CPU and C++ runtime | Start from Dusklight's `-march=btver2` and runtime adaptations; verify required atomics, threads, TLS, constructors and C++ features |
| SDL3 | Adapt Dusklight's audio/console integration and input handling against Aurora's pinned SDL3 API |
| Input | Implement DualShock 4 controls, analog triggers, disconnect/reconnect and an options-menu binding |
| Audio | Connect the existing DSP output through the PS4 audio backend and verify pacing by listening on hardware |
| Files | Define and test disc, log, settings and save locations, including write access and restart persistence |
| Packaging | Produce a PS4 application package and metadata using the selected public toolchain |
| Diagnostics | Provide logs and PS4 crash reporting; adapt signal handling only against verified PS4 ABI definitions |

The PS5 [platform implementation][ps5-platform] is a behavioral reference,
not proof that the same API declarations or controller structures work on PS4.
The [game patch][ps5-patch] includes integer-division, floating-point lookup and
callback-return fixes worth retaining for evaluation. Its PS5 signal-context
handling and generated division table require a separate PS4 review.

## Validation milestones

1. **Reproducible platform and native graphics test.** Inventory Dusklight's
   published inputs, resolve immutable dependency pins and replace missing build
   files with reviewed equivalents. Build a minimal PS4 Dawn graphics probe
   without game data against one coherent runtime/Mesa/Dawn combination.
   Run it on the Slim with firmware 9.00 under the owner's homebrew environment.
   Record the loader/homebrew version, toolchain and driver revisions, GPU
   identification, Vulkan features/limits, frame presentation, shutdown behavior
   and logs. A successful build alone does not pass this milestone.
2. **Aurora and SDL3 test.** Extend the probe to exercise Aurora. Create an
   adapter/device with the required features;
   render a textured scene with depth, blending and render-target changes. Check
   shader compilation, frame readback, DualShock 4 input, audio and writable
   storage. Resolve missing Vulkan capabilities before importing the full game.
3. **Game startup.** Integrate the pinned game baseline, stub asset headers and
   runtime-assets mode. Verify useful errors for missing/wrong discs and reach
   the title screen using the owner's `GZLE01` revision 0 dump.
4. **Playable baseline.** Verify name entry, prologue, Outset, transitions,
   controller reconnect, audio and saving/reloading across application restarts.
   Revisit the PS5 port's known crash scenes and measure CPU/GPU frame times.
5. **Release candidate.** Complete longer gameplay checks, package/license
   validation and repeatable installation/update instructions. Publish measured
   compatibility and known failures for the tested console and firmware.

Use stock textures, no frame interpolation, and a modest render resolution for
the first playable baseline. Keep the original 30 Hz game logic. Choose a
resolution and performance target after measurement; PS5 results do not
establish PS4 performance.

## Assets and build environment

Keep game data external to source control and release packages. The PS5 build
uses `COS_RUNTIME_ASSETS=ON` with stub headers so its build requires no disc;
retain that approach. See its [build configuration][ps5-build].

Use Linux tooling through WSL2 or a Linux container on the Windows development
machine, subject to the selected SDK's requirements. During investigation,
WSL Ubuntu and Docker with a Linux engine were detected; CMake, Ninja and Clang
were not available on the Windows PATH. No PS4 toolchain was installed or
console deployment attempted as part of this investigation.

Before importing upstream code, preserve the applicable licenses and notices.
The PS5 project has a [licensing inventory][licensing]; keep a dependency record
for the actual PS4 build rather than inheriting its PS5 binary dependencies or
shader caches.

[ps5-cmake]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/cmake/ps5-game.cmake
[ps5-build]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/tools/build.sh
[ps5-submodule]: https://github.com/griches/PS5_SwitchWaker/tree/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/vendor/switchwaker
[aurora-pin]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/cmake/Aurora.cmake
[ps5-source]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/tools/setup-source.sh
[ps5-platform]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/src/platform.c
[ps5-patch]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/patches/switchwaker.patch
[mesa]: https://github.com/orbis-ports/mesa-ps4
[kit]: https://github.com/orbis-ports/orbis-porting-kit
[licensing]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/LICENSING.md
[dusklight-build]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/BUILDING.md
[dusklight-aurora]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/patches/aurora-ps4.patch
[dusklight-dawn]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/tools/build-dawn.sh
[dusklight-sdl]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/tools/build-sdl3.sh
[dusklight-probe]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/tools/build-probe.sh
