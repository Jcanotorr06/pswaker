# Wind Waker / Dusklight PS4 renderer compatibility

Investigated 2026-10-18 for [Determine how Wind Waker can reuse Dusklight's PS4 renderer](https://github.com/Jcanotorr06/pswaker/issues/3). Source inspection only: no patch application, SDK build, or console execution. Target: PS4 Slim 9.00, GZLE01 revision 0, stock textures, 30 Hz logic, initial 720p30 goal. This answers the compatibility investigation; architecture selection remains open.

## Result and actual dependency identities

Dusklight supplies reusable PS4 platform integration, but its patches are **incremental changes over its inherited PS5 forks**, not a replacement renderer that can be dropped into Wind Waker. The shared boundary is Aurora's GX-to-WebGPU renderer, Dawn's Vulkan backend, and the matching native RADV/VideoOut implementation. [Dusklight's manifest and build procedure][manifest] explicitly identify the fork bases and say a rebuild solely from the publication has not been verified end to end.

| Component | Wind Waker reference | Dusklight PS4 reference |
|---|---|---|
| Game wrapper | PS5_SwitchWaker `3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0`, SwitchWaker `ba8d0a31446cd53ceaebd6b7269cca641e73bf4c` | PS4 publication `fd483cf5d4f04b0f4d887ff412d0e8691925de08`, Dusklight PS5 tag `ps5-v0.1.0` |
| Aurora actually used | encounter/aurora `3227d76c60e1e782ca576610bce61c9e7744d8be`, then SwitchWaker patches and PS5 patch | mshivam019/dusklight-ps5 Aurora fork `e281999cdb4fee6127525a9a9e97979480db4bf3`, then PS4 patch |
| Dawn declaration / actual checkout | Aurora declares encounter/dawn `1155e0ed531126f33a1279afa029349651ca1c93`; PS5 setup fetches that and applies its patch | Aurora declares the same upstream revision, but source-fetch uses fork tag `deps/dawn-ps5`, resolving to `652a3104791369cd23605856fbc041375ccda875`, then PS4 patch |

These identities follow [SwitchWaker's Aurora contract][ww-contract], [PS5 source setup][ww-setup], [PS5 Dawn setup][ww-dawn-setup], both [Wind Waker][ww-deps] and [Dusklight dependency declarations][dl-deps], [Dusklight's submodule manifest][dl-submodules], [source-fetch script][dl-fetch], and [Dawn tag identity][dl-dawn-tag]. An upstream declaration does not establish equality with the patched fork.

## API and patch boundary

**Surface descriptor ABI differs.** Wind Waker's [Aurora PS5 patch][ww-aurora] sends `SurfaceSourceSwitchNWindow` with a dummy token. Its [Dawn patch][ww-dawn] interprets that as the first `VK_KHR_display` display/mode. Dusklight's [Aurora fork][dl-binding] instead sends `SurfaceSourceDirectDisplay` with width/height. Its [Dawn fork][dl-surface] validates the requested dimensions, selects a mode up to 61 Hz and a supported plane. Its PS4 patches extend that inherited implementation with `__ORBIS__`. Therefore headers, generated WebGPU bindings, descriptor validation, and Vulkan surface handling must move together; copying only `BackendBinding.cpp` is insufficient.

**Platform mechanisms are reusable with reconciliation.** [Dusklight's Dawn patch][dl-dawn] adds PS4 platform detection, excludes POSIX dynamic-loading and external-memory FD paths, and resolves Vulkan functions through statically linked `vk_icdGetInstanceProcAddr`. Queue/swapchain additions mostly instrument existing operations; they do not independently establish correct PS4 synchronization. Its profiling calls also require matching application/runtime symbols. Wind Waker's Dawn patch covers fewer loader details, so extending its macros alone does not reproduce Dusklight's stack.

**Keep game correctness patches visible.** PS5 setup applies SwitchWaker's [ordered Aurora patch set][ww-patches] before its console patch. This includes TEV alpha comparisons, SRTG lighting, quad handling, EFB scaling/copies, cache recovery, and FIFO/frame behavior. For example, [the alpha-compare fix][ww-alpha] repairs generated WGSL, while [async end-frame][ww-async] changes ordering and synchronization around resizing and presentation. A wholesale Aurora fork swap must reconcile these contracts and their game callers. Patch application and compiler compatibility were not tested here; matching file names or upstream Dawn pins is insufficient evidence of clean application or behavioral equivalence.

## Vulkan, shaders, memory and synchronization

Aurora's [actual device creation][gpu] requests a compatibility-level adapter, `TimedWaitAny`, two storage buffers per shader stage and an immediate-data size derived from `gx::DrawImmediateData`. It conditionally enables core features, BC/ASTC textures, component swizzle and dual-source blending when reported. It creates sampled/renderable `Depth32Float`, WGSL copy/resample pipelines and explicit render targets. Thus a Vulkan version string or triangle cannot establish suitability: capture both raw Vulkan capabilities and Dawn's accepted limits/features, then exercise actual Aurora pipelines and fallback paths.

[Dusklight's Mesa patch][dl-mesa] implements `VK_KHR_display` through VideoOut, advertises RGBA8/BGRA8 UNORM and FIFO presentation, and initially exposes a 1920x1080 mode at 59.94 Hz. It uses three swapchain images, CPU-visible device-local allocations with 2 MiB display-buffer alignment, GPU-fence waits before flips, and retirement of displayed swapchain buffers. This is a coherent surface/memory/submission contract. A 720p *internal render* target and display-mode selection are separate decisions; requesting a 1280x720 DirectDisplay surface unchanged is not supported by the published mode table.

[The accompanying winsys][dl-drm] maps direct memory in the process/GPU address space and submits GFX7 command buffers, tracking completion with end-of-pipe sequence writes. Preserve its allocation, visibility and fence assumptions together with Mesa. [Aurora depth peek][depth] additionally runs compute, copies into readback buffers and maps them asynchronously; test this alongside render-to-texture transitions, rather than inferring correctness from presentation alone.

Shaders remain runtime work: [Dawn's PS4 build][dl-build-dawn] retains Tint's SPIR-V writer and disables release SPIR-V/IR validation checks. Diagnostic builds should retain useful compiler/validation errors. Aurora's [PS4 patch][dl-aurora] adjusts both SQLite caches to `unix-none` with exclusive WAL locking, and contains texture-replacement eviction/render-thread release behavior. The latter addresses HD replacements and is not a stock-texture requirement. Its stated cache budgets are implementation policy, not a measured Wind Waker memory budget. Start with empty target caches; separately verify restart persistence. PS5 [cache seeding][ww-cache] is not proof that its Dawn/driver binaries are reusable on PS4.

CPU correctness is independent of WSI. Wind Waker's [PS5 build][ww-build] targets `znver2`; Dusklight targets Jaguar `btver2` and documents UB guard flags. Retarget every rebuilt dependency, rather than reusing PS5 archives. Wind Waker's [game patch][ww-game] also guards division by zero, bounds NaN-derived atan indices and masks bool/int callback results; its comments identify the forest scene transition affected by the last fix. Carrying those x86 fixes forward is relevant to the requested Outset/forest slice, even if graphics initializes successfully.

## Integration choices and bounded evidence

Two candidate approaches remain for the human decision:

- Preserve Wind Waker's Aurora/Dawn bases and translate the necessary PS4 loader, surface, cache and runtime adaptations. This keeps known game patches close to their intended base but requires reconstructing the complete PS4 platform changes.
- Adopt Dusklight's matched Aurora/Dawn/Mesa/runtime forks, then reconcile Wind Waker's game-facing patches. This starts closer to its published PS4 integration but broadens behavioral regression review, including FIFO synchronization and EFB copies.

Neither source inspection nor PS4 Pro observations establish Slim correctness or 720p30. The sharpened diagnostic question is: **Can one reproducibly built candidate stack on the owner's Slim 9.00 create Aurora's requested device and compile its representative pipelines, then repeatedly render/present depth-tested and blended textured geometry with EFB/offscreen copies and readback across target recreation and application restart?**

Minimum evidence: pin SDK/runtime/driver and record firmware/homebrew versions; log adapter/features/limits, formats, display extent, all failed callbacks/results and pipeline diagnostics; compare known pixel/depth results; run enough frames to recycle every swapchain image repeatedly; recreate targets while work is queued; restart with cold then warm caches; record memory high-water marks and CPU/GPU/present timing separately. A failed adapter, shader, copy or fence test should identify its exact operation. This disc-free probe can settle stack viability; first-playable gameplay and performance acceptance remain later validation.

[manifest]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/BUILDING.md
[ww-contract]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/cmake/Aurora.cmake
[ww-setup]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/tools/setup-source.sh
[ww-deps]: https://github.com/encounter/aurora/blob/3227d76c60e1e782ca576610bce61c9e7744d8be/cmake/AuroraDependencyVersions.cmake
[dl-deps]: https://github.com/mshivam019/dusklight-ps5/blob/e281999cdb4fee6127525a9a9e97979480db4bf3/cmake/AuroraDependencyVersions.cmake
[dl-submodules]: https://github.com/mshivam019/dusklight-ps5/blob/5811958531cb0a9eafeb293fafcb36071883bfdf/.gitmodules
[dl-fetch]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/tools/fetch-sources.sh
[dl-dawn-tag]: https://github.com/mshivam019/dusklight-ps5/commit/652a3104791369cd23605856fbc041375ccda875
[ww-aurora]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/patches/aurora.patch
[ww-dawn]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/patches/dawn.patch
[dl-binding]: https://github.com/mshivam019/dusklight-ps5/blob/e281999cdb4fee6127525a9a9e97979480db4bf3/lib/dawn/BackendBinding.cpp
[dl-surface]: https://github.com/mshivam019/dusklight-ps5/blob/652a3104791369cd23605856fbc041375ccda875/src/dawn/native/vulkan/SwapChainVk.cpp
[dl-dawn]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/patches/dawn-ps4.patch
[ww-patches]: https://github.com/centollOS/SwitchWaker/tree/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/patches/aurora
[ww-alpha]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/patches/aurora/0001-alpha-stage-channel-compares.patch
[ww-async]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/patches/aurora/0018-async-end-frame.patch
[gpu]: https://github.com/encounter/aurora/blob/3227d76c60e1e782ca576610bce61c9e7744d8be/lib/webgpu/gpu.cpp
[dl-mesa]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/patches/mesa-26.0.8-ps4.patch
[dl-drm]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/tools/ac_ps4_drm.c
[depth]: https://github.com/encounter/aurora/blob/3227d76c60e1e782ca576610bce61c9e7744d8be/lib/gfx/depth_peek.cpp
[dl-build-dawn]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/tools/build-dawn.sh
[dl-aurora]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/patches/aurora-ps4.patch
[ww-cache]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/src/startup.c
[ww-build]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/cmake/ps5-game.cmake
[ww-game]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/patches/switchwaker.patch

[ww-dawn-setup]: https://github.com/griches/PS5_SwitchWaker/blob/3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0/ps5/tools/setup-dawn.sh
