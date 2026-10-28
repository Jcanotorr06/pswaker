# PS4 platform research

Investigated 2026-10-18. Target supplied by the user: PS4 Slim, firmware 9.00.
This is source research; no SDK build or console test was performed here.

## Verified findings

**Dusklight PS4 is the closest platform reference found.** The user supplied
`BgbrhrWatchinOVO/dusklight-ps4`; its [README][dusklight] reports a native
OpenOrbis/Mesa RADV/Dawn program tested on PS4 Pro. Its [build manifest][dusklight-build]
pins a PS5 Dusklight base, Aurora, Dawn, SDL3, Mesa 26.0.8 and a DolphinPS4
runtime. Public [Aurora][dusklight-aurora], [Dawn][dusklight-dawn] and
[SDL3][dusklight-sdl] patches demonstrate the PS4 platform integration in source,
including direct-display surfaces and PS4 audio configuration. This is stronger
evidence than a generic Vulkan triangle, but the author explicitly says a fresh
rebuild from the published repository has not been verified end to end. The
PS4 Pro performance claims are not measurements of Wind Waker on this Slim.
Concrete publication gaps also need resolving: [build-dawn.sh][dusklight-build-dawn]
and [build-sdl3.sh][dusklight-build-sdl] name `toolchain/ps4.cmake`, while
[build-probe.sh][dusklight-build-probe] names `probe-dawn/`; those root paths are
absent from the published tree at this revision. The reference is implementation
evidence, not a complete probe that can already be run unchanged.

**Native PS4 Vulkan is a real candidate.** `orbis-ports/mesa-ps4` has an Orbis
RADV port, including a GPU memory/submission implementation, Liverpool/Gladius
families, and `sceVideoOut` presentation. These are native Orbis paths, distinct
from running Mesa under Linux on a PS4. The maintainer explicitly corrects an
obsolete statement that presentation was unfinished and reports OpenGothic and
RetroArch displaying frames. See the pinned [driver status and correction][mesa],
[native submission implementation][drm], and [presentation implementation][wsi].

**This is not established as a fully validated driver.** The maintainer's
[CTS record][cts] reports six passing Vulkan smoke tests on Liverpool, followed
by a partial suite with 5,339 passes, 443 failures and 808 unsupported cases.
That is historical coverage, not a current conformance result. Later entries
record fixes and remaining failures, including multiview combinations and a
multiview/MSAA run that halted. The [handoff][handoff] also records intermittent
GPU stalls. A successful triangle therefore establishes a starting point;
Aurora's actual workloads still need testing.

**An alternative toolchain's dependencies are moving.** OpenOrbis supplies a public homebrew
toolchain with headers, library stubs, musl and libc++ components, without using
Sony's official SDK ([OpenOrbis README][openorbis]). The public
`orbis-porting-kit` contains CMake/toolchain integration, a Vulkan loader shim,
packaging and a SPIR-V triangle example. However, its [pinned README][kit]
declares it archived and superseded by `orbis-ports/orbsdk`. That successor
returned HTTP 404 through GitHub's public API and raw README on this research
date; its visibility or availability is unresolved. The archived kit and public
Mesa sources are a reproducibility fallback to investigate, not a selected or
confirmed working dependency set. This is a separate stack from Dusklight PS4's
Mesa/DolphinPS4 integration; mixing their loaders, runtime shims and drivers
without validating their contracts is not a build recipe.

**The surface API depends on the chosen stack.**
PS5_SwitchWaker pins Aurora's Dawn revision and patches Dawn to link the console
RADV directly; its [Dawn setup][ps5-dawn] uses `VK_KHR_display`. The public PS4
kit's [triangle][triangle] uses `VK_EXT_headless_surface` with the Orbis WSI.
Dusklight PS4 instead extends its inherited direct-display path for Orbis.
Reusing the game/Aurora layer requires selecting a coherent driver, loader and
surface implementation and adapting their patches to SwitchWaker's pinned
versions. These are source-level integration tasks, not a compiler-target rename.

**SDL3 has a public PS4 integration reference.** The PS5 port explicitly builds
Aurora's pinned SDL3 and adds its own video/audio/controller drivers
([setup][ps5-sdl]). A public [PS4 SDL2 fork][sdl2] has Orbis video, audio and
joystick drivers; its video driver uses Mesa EGL/zink/RADV. More directly useful,
Dusklight PS4's [SDL3 patch][dusklight-sdl] extends the inherited PS5 port for
Orbis. It must be reviewed with that upstream PS5 SDL3 base, rather than treated
as a complete patch against arbitrary upstream SDL3. Switching Aurora to SDL2
would be a separate compatibility project.

**Piglet is an alternative requiring its own renderer and shader investigation.**
OpenOrbis's [Piglet sample][piglet] requests an OpenGL ES 2 context, loads
precompiled shaders from a firmware shader module and passes PSSL binaries to
`glShaderBinary`. That sample does not demonstrate a general runtime shader
compiler or compatibility with Dawn/Aurora. RADV instead has its own shader
compiler path; the PS4 [tools][mesa] include SPIR-V/ACO pipeline probes. The kit
triangle compiles GLSL to SPIR-V on the host using `glslangValidator`. Shader
caches produced for the PS5 are not validation of the PS4 compiler path; begin
with fresh caches on the target GPU.

**GPU command compatibility must be validated.** The PS4 driver explicitly
implements GFX7 submission/fence handling and console-specific workarounds
([implementation][drm]); its [handoff][handoff] records indirect-multi-draw
packets hanging this command processor and a replacement using plain indirect
draws. The PS5 driver's behavior cannot establish PS4 correctness, even where
both applications use Vulkan.

## Unknowns and first validation milestone

GoldHEN's [own repository][goldhen] publishes a firmware 9.00 binary and lists
package installation, FTP and logging facilities. That establishes a homebrew
deployment route in principle; it does **not** prove this RADV/SDK combination
works on the user's firmware, model or currently installed GoldHEN version.
Dusklight PS4's published testing statement names PS4 Pro, not Slim or firmware
9.00. Exact firmware compatibility, SDK reproducibility, Dawn feature/limit support,
SDL3 integration and game correctness remain open. No performance target is
supported by these sources for this PS4 Slim.

The first milestone should be a **disc-free native PS4 graphics probe**. First
try to reproduce Dusklight PS4's coherent SDK/Mesa/runtime combination and use
its platform integration to build a minimal Vulkan/Dawn program, supplying the
missing toolchain/probe pieces explicitly. Install and
run it on the user's Slim
9.00, capture device/features/extensions and checked return values, verify
visible repeated presentation, and repeat after closing and reopening. Record
the exact SDK, driver, firmware and homebrew-enabler versions. Validate a
minimal Aurora render next using the same loader/WSI. The immediate
blockers are identifying an obtainable, reproducible SDK/driver combination
and validating it on this console; neither requires importing game assets.

[dusklight]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/README.md
[dusklight-build]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/BUILDING.md
[dusklight-aurora]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/patches/aurora-ps4.patch
[dusklight-dawn]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/patches/dawn-ps4.patch
[dusklight-sdl]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/patches/sdl3-ps4.patch
[dusklight-build-dawn]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/tools/build-dawn.sh
[dusklight-build-sdl]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/tools/build-sdl3.sh
[dusklight-build-probe]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/tools/build-probe.sh
[mesa]: https://github.com/orbis-ports/mesa-ps4/blob/1a59cc147b54e3970814b37313e2f27357672e9d/build-support/orbis/README.md
[drm]: https://github.com/orbis-ports/mesa-ps4/blob/1a59cc147b54e3970814b37313e2f27357672e9d/src/amd/common/ac_orbis_drm.c
[wsi]: https://github.com/orbis-ports/mesa-ps4/blob/1a59cc147b54e3970814b37313e2f27357672e9d/src/vulkan/wsi/wsi_orbis.c
[cts]: https://github.com/orbis-ports/ps4-mesa-docs/blob/deb190361652acbc3b0ff49fc8edac1820f16842/cts.md
[handoff]: https://github.com/orbis-ports/ps4-mesa-docs/blob/deb190361652acbc3b0ff49fc8edac1820f16842/docs/HANDOFF.md
[openorbis]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/0a1aaf9dd4a92695538bdeb09fb056d06dd11725/README.md
[kit]: https://github.com/orbis-ports/orbis-porting-kit/blob/213b0c38ff25ea7ca402c8844a6494086d0f1cae/README.md
[triangle]: https://github.com/orbis-ports/orbis-porting-kit/tree/213b0c38ff25ea7ca402c8844a6494086d0f1cae/examples/triangle
[ps5-dawn]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/tools/setup-dawn.sh
[ps5-sdl]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/tools/setup-sdl.sh
[sdl2]: https://github.com/orbis-ports/SDL2/tree/8967814a1e2c1a7ffd9da5c3eb8ffbeec4aed81a/src/video/orbis
[piglet]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/0a1aaf9dd4a92695538bdeb09fb056d06dd11725/samples/piglet/piglet/PigletApplication.cpp
[goldhen]: https://github.com/GoldHEN/GoldHEN
