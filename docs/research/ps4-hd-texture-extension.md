# Optional PS4 HD texture replacement: source investigation

Research date: 2026-10-25. Decision input for [Investigate PS4 reuse of SwitchWaker HD texture replacement](https://github.com/Jcanotorr06/pswaker/issues/31), under [Plan configurable controls and optional HD textures after first playable](https://github.com/Jcanotorr06/pswaker/issues/29).

## Finding and evidence boundary

SwitchWaker supplies a plausible conversion, lookup and streaming design to adapt. The maintained PS4 port does **not** currently enable that feature: its build removes `pc_hd_textures.cpp`, substitutes always-off stubs, and deliberately excludes the two Aurora patches its loader requires. Enabling an environment variable is insufficient. A focused port of those interfaces and their renderer interactions is preferable to assuming an upstream dependency upgrade is safe. This is a source-derived option, not an owner decision or a tested PS4 implementation. [PS4 build][ps4-cmake], [stubs][ps4-stubs], [renderer reconciliation][renderer-lock].

Both extension features remain after first playable; HD textures have lower priority than controls. Stock-texture first-playable acceptance is unchanged. No pack, game data, converted artwork, PS4 build, performance experiment or hardware validation was obtained or performed for this investigation. Hypatia compatibility remains a target requiring the owner's own pack and evidence. [Extension map][map].

## Inspected revisions

| Source | Immutable revision and use |
| --- | --- |
| Maintained PS4 integration | `Jcanotorr06/pswaker@2b95ad45e2620a7898c2a79789510ec7565d7364`, the `develop` base inspected here |
| Maintained SwitchWaker source | `centollOS/SwitchWaker@ba8d0a31446cd53ceaebd6b7269cca641e73bf4c`: guide, loader, converter, preparation/deployment scripts, public headers |
| Current SwitchWaker comparison | `centollOS/SwitchWaker@f4c5faa9613ca615ba5267bea3c62f6db859675c`: guide only; its bytes match the maintained guide (SHA-256 `6258e074a7daaafa228202d9d480f1d65c4256b38ae55a4240ec198fb644d0901`) |
| Selected Aurora fork | `mshivam019/dusklight-ps5@e281999cdb4fee6127525a9a9e97979480db4bf3`: replacement public API, registry, GX resolver, DDS reader and WebGPU texture/device code |
| Original Aurora patch base | `encounter/aurora@3227d76c60e1e782ca576610bce61c9e7744d8be`, identified by the PS4 reconciliation lock; not substituted for the selected fork |
| Dolphin cross-check | `dolphin-emu/dolphin@3eb30c7620b4475b2e0404228ba0d2b238a132f1`: `TextureInfo.cpp` and `HiresTextures.cpp` |
| Converter codec pin | `richgel999/bc7enc_rdo@b9438627eef73a1157e84201b6fa6eb2ffd6d9f0`, declared by the inspected host-tool CMake file; codec internals were not audited |

The maintained game lock also pins decomp `b09eebc39852e18397031d9a563a8eae124f21f1`, RecompCore `8ab24daee9c641634fda5cac30389ad4b2cfda5e`, and PS5 reference `3c0f213f2d4c17606ac8637eda2c5da6cbcc73b0`. The graphics source locks select Dawn `652a3104791369cd23605856fbc041375ccda875` and Mesa `60e95b787857afbc9a00b693b91c0d9c8923a430`. These are dependency context, not newly inspected or upgraded implementations. [Game pins][game-lock], [source pins][source-lock], [dependency pins][deps-lock], [host-tool pin][converter-cmake], [current guide][current-guide].

## Matching and artwork scope

Aurora parses `tex1_<width>x<height>[_m]_<texture hash>[_<palette hash>]_<GX format>[_arb].dds` or `.png`. Source dimensions and format describe the original GX texture, not the replacement resolution. The source hash is XXH64 with seed zero over the base level in its stored GX layout; block padding matters. Palette textures hash the contiguous TLUT span between the minimum and maximum referenced indexes. Lookup tries the exact key, then a palette wildcard `$`, then a texture wildcard `$`. `_m` and `_arb` do not add key fields. [Replacement implementation][replacement].

Dolphin independently confirms block-expanded base data and used-palette-span hashing. There is a concrete C14X2 caveat: the inspected Dolphin expression is `Common::swap16(m_data[i])`, with `m_data` a byte span, whereas Aurora copies a full 16-bit value before swapping. Their expressions differ; do not promise general C14X2 palette-hash equivalence. The upstream guide says its examined pack uses palette wildcards for C14X2, which can avoid that particular hash difference, but the player's download was not inspected. [Dolphin naming][dolphin-info], [guide][guide].

The GX resolver prioritizes EFB copy textures and uses replacement lookup for static sampled textures. Existing wrapping/filtering survives; replacement mips affect allowed LOD. Preserve that separation to avoid replacing render targets or changing stock materials. Patch `0010` also adds the arbitrary-mipmap LOD behavior. Retain the already reconciled `0012` texture-object image checks and subsequent copy-lookup integration when adapting `0010`/`0011`; the upstream patches were authored against another base and are not established as cleanly applicable here. [GX resolver][gx-texture], [samplers/uploads][gpu-texture], [streaming patch][patch10], [renderer lock][renderer-lock].

## Local preparation and supported formats

The host converter recursively selects Dolphin-named `tex1_*.dds` files. It accepts BC1, BC3, BC7 and specified uncompressed RGBA/BGRA/RGBX/BGRX DDS variants; it keeps compressed families and encodes uncompressed input as BC7. This is narrower than arbitrary Dolphin texture-pack support: PNG input and other compression families are outside this converter's implemented input set. It caps resolution by choosing an existing mip or reducing, preserves usable authored mip levels, and fills the chain with generated levels. Optional input directories override same-named files. Failed conversions produce a nonzero exit code even though output can already exist; installation must reject unfinished conversion results. [Converter source][converter].

Preparation needs Bash, `bsdtar` for archives, CMake, Ninja, a C++20 compiler, threads and the pinned codec source fetched by CMake. The wrapper finds a `GZL` directory and excludes optional folders unless explicitly supplied. Its default directories are under `build/`; it is a host workflow, not an in-game archive importer, and native Windows execution is unproven. A WSL/Linux host workflow or an adapted Windows wrapper is a decision option. Do not copy the wrapper's recursive extraction deletion into a new platform workflow without checking its resolved target. [Preparation script][prepare], [host build][converter-cmake].

Output is a little-endian `COSHDIX1` version-1 index plus `data00.bin`, `data01.bin`, etc. DDS payloads have DX10 headers and mip chains; data chunks are limited to 1 GiB and entries aligned to 512 bytes. The index contains names, file identifiers, offsets, sizes and mip/format metadata. This permits positioned reads and skipping oversized mip levels instead of loading a whole archive. Conversion cap and runtime cap are separate choices; a small converted pack cannot later recover discarded detail. [Writer][converter], [reader][loader].

The selected runtime DDS reader recognizes a different, broader set (including BC5 and ASTC); that does not make those formats valid converter inputs or guaranteed PS4 formats. It recognizes the converter's BC1/BC3/BC7 DXGI outputs. The converter normalizes sRGB variants to its linear output codes; color/alpha appearance needs visual acceptance rather than an assumption of byte-preserving conversion. [DDS decoding][dds], [converter][converter].

## Required PS4 integration and bounded costs

1. Reconcile `0010` streaming configuration/statistics/source observation and `0011` batch registration, gradual removal/rescan, cached reload and estimated publication-cost APIs onto the **selected** Aurora plus existing PS4 patches. The selected public API already supports individual virtual registrations, but lacks these added interfaces. Change the maintained patch manifest and recorded file hashes as part of a later implementation, with explicit review of overlap in GX caches, sampler behavior and frame ownership. [Public API][api], [streaming patch][patch10], [publication patch][patch11], [reconciliation][renderer-lock].
2. Replace the stock stubs only after the loader compiles with that reconciled API. Wire startup, settings subscriptions and the existing after-frame hook consistently with the PS4 runtime. The upstream loader has a helper-thread opening phase, incremental registration and removal, and a synchronous startup wait if HD was saved on. Its loose-directory fallback registers synchronously; importing it wholesale would not establish a bounded console toggle. [Loader][loader], [PS4 runtime patch][runtime-patch].
3. Set PS4-specific memory, worker and publication defaults. The loader's non-Switch branch otherwise inherits desktop defaults (1024 MiB replacement cache, 12 MiB publication allowance and automatic worker count). Neither those nor Switch defaults are measured PS4 budgets. [Loader defaults][loader].

Patch `0010` budgets replacement GPU residency, avoids evicting textures bound in the recent frame window, and delays retry after a budget rejection. Patch `0011` spreads cache rescan and estimates upload/creation cost per texture, mip and MiB. These are soft scheduling controls: at least one texture can publish even if it exceeds that frame's allowance. GPU residency is not a total process-memory bound: originals, decoded/in-flight data, index/registry storage and upload staging also exist. A PS4 contract needs separate limits on pending jobs/bytes and maximum decoded entry size, plus measurements under memory pressure. [Streaming implementation][patch10], [publication implementation][patch11].

There is encouraging **existing** console evidence: the committed verification log identifies PS4 Liverpool/RADV and enables `TextureCompressionBC`. Aurora requests that feature if exposed and rejects BC replacements when it is absent. Replacement upload creates a WebGPU texture/view and writes every mip through the normal upload path. This supports investigating native BC1/BC3/BC7 reuse; it does not prove the HD path's individual formats, small compressed mip uploads, color correctness or latency on PS4. [Console log][console-log], [device feature selection][device], [replacement upload][replacement], [texture uploads][gpu-texture].

Switch GL upload patches are not an automatic PS4 requirement: this PS4 build selects Vulkan and disables GL/GLES. The guide's Mac measurements and Switch anecdotes/estimates are platform-specific references. Establish PS4 costs on its pinned Dawn/Mesa path before selecting a cap, cache allowance or frame-time acceptance target. [PS4 graphics selection][ps4-cmake], [guide][guide].

## Storage, settings and failure options for the owner

The existing runtime supplies `/data/pswaker` for writable user data, `/data/pswaker/settings.ini` for settings and `/app0` for installed resources. The upstream default `<user>/hd_textures` naturally maps to `/data/pswaker/hd_textures`, but that path is a proposed extension, not a working installer. Keep HD data outside the build-specific disposable pipeline-cache directory and outside saves. [PS4 entry][main], [loader path][loader].

| Option to decide | Implications and required evidence |
| --- | --- |
| Converted pack in writable user storage | Reuse the default reader path; a separate owner-controlled transfer/preparation step is needed. Install into a staging/versioned directory and switch only after validation. Storage capacity, permissions, update preservation and transfer behavior need PS4 checks. |
| Converted pack bundled in an owner-built complete package | Read from a chosen `/app0` subdirectory; private package assembly, inventory and manifest checks must be extended explicitly. It increases package size and requires replacement packages for artwork changes. Program packages remain data-free. |
| USB/external path | Requires an explicit supported mount/path and disconnect contract. The current PS4 integration establishes no HD external-storage workflow; do not advertise one from Switch's SD/MTP script. |
| Loose Dolphin directory | Useful for diagnostics, but synchronous registration and uncapped files weaken predictable loading/memory bounds. Prefer converted-only player support unless the owner accepts and validates a second path. |

These are alternatives to choose, not commitments. Existing complete-package tooling assembles and verifies the owner's game image; it has no declared HD-pack contract. The Switch script's data-first/index-last transfer and readback are useful precedents, but replacing data beneath an old live index is not an atomic pack update. A staging directory with verification before activation avoids promising more than that script guarantees. [Package assembly][package], [complete-package contract][packages-doc], [Switch transfer][transfer].

Upstream settings provide `COS_HD_TEXTURES`, saved values and subscriptions, with runtime requests applied at frame end. Missing-pack activation can fail, and an unusable pack returns to off; the requested/persisted setting and actual enabled state can differ while opening or after failure. The owner must choose how the PS4 menu shows unavailable/loading/active/error, whether enablement is saved before successful activation, whether changes require restart, and how restore-defaults treats HD (off is the source default). Switch docked/handheld size settings need an intentional PS4 policy. [Settings API][settings], [loader state machine][loader].

The reader checks index magic/version, broad table boundaries and whether named data files open. Short reads and unsupported/invalid DDS replacements can fall back to original textures. Individual bad name ranges are skipped; index admission does not prove every entry's offset/size fits its file. Malformed counts, oversized entries, invalid mip metadata, corrupted chunks and partial conversion therefore need explicit validation and allocation limits before being described as safe. An index can open yet contain no useful replacements; distinguish structural failure from legitimate incomplete coverage. Decide whether to reject the whole pack or continue per texture, report actionable errors, and define retry/reinstallation behavior. [Reader validation][loader], [DDS validation][dds], [replacement failure handling][replacement].

## Asset isolation and acceptance still to decide

Use an owner-only preparation root outside the checkout, or root `build-hd/` (covered by `/build*/`). Keep `downloads/`, `extracted/`, `converted/`, transfer staging/readbacks and asset-bearing complete packages under that root. Only generic source, format documentation and data-free reports belong in git. Existing ignores cover root build directories and packages but do **not** generally exclude `.dds`, `.png`, archives or arbitrary `.bin` anywhere in the repo. A future tool must constrain output locations and explicitly inspect its staged changes; an ignore rule alone is no permission to stage derived assets. No preparation output was created in this research branch. [Current ignore rules][ignore], [preparation defaults][prepare], [map ownership boundary][map].

Before calling the feature supported, agree evidence for: BC1/BC3/BC7 plus compressed mip tails; palette/wildcard and `_arb` matching; EFB exclusion; NPC material variants; stock-only launch; on/off/rapid toggle/restart behavior; missing, truncated, unsupported and partial packs; memory-pressure fallback; asynchronous loader lifetime/cancellation; installation interruption and package update preservation. Measure frame distributions and worst hitches, process/CPU staging/GPU residency, pending work, registration and upload costs on the retained PS4 Slim/9.00/GoldHEN baseline. Compare HD-off after use to an equivalent never-enabled run, with scene/time control; upstream screenshot observations are not this evidence. The owner still chooses the supported pack/conversion preset, installation option, menu contract, limits and acceptance thresholds. [Baseline scope][map], [diagnostic hooks][loader], [cache/publication mechanics][patch11].

[map]: https://github.com/Jcanotorr06/pswaker/issues/29
[ps4-cmake]: https://github.com/Jcanotorr06/pswaker/blob/2b95ad45e2620a7898c2a79789510ec7565d7364/platform/ps4/game/CMakeLists.txt
[ps4-stubs]: https://github.com/Jcanotorr06/pswaker/blob/2b95ad45e2620a7898c2a79789510ec7565d7364/platform/ps4/game/stock-textures.cpp
[renderer-lock]: https://github.com/Jcanotorr06/pswaker/blob/2b95ad45e2620a7898c2a79789510ec7565d7364/platform/ps4/renderer.lock.json
[game-lock]: https://github.com/Jcanotorr06/pswaker/blob/2b95ad45e2620a7898c2a79789510ec7565d7364/platform/ps4/game.lock.json
[source-lock]: https://github.com/Jcanotorr06/pswaker/blob/2b95ad45e2620a7898c2a79789510ec7565d7364/platform/ps4/sources.lock.json
[deps-lock]: https://github.com/Jcanotorr06/pswaker/blob/2b95ad45e2620a7898c2a79789510ec7565d7364/platform/ps4/dependencies.lock.json
[current-guide]: https://github.com/centollOS/SwitchWaker/blob/f4c5faa9613ca615ba5267bea3c62f6db859675c/docs/HD_TEXTURES.md
[guide]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/docs/HD_TEXTURES.md
[replacement]: https://github.com/mshivam019/dusklight-ps5/blob/e281999cdb4fee6127525a9a9e97979480db4bf3/lib/gfx/texture_replacement.cpp
[dolphin-info]: https://github.com/dolphin-emu/dolphin/blob/3eb30c7620b4475b2e0404228ba0d2b238a132f1/Source/Core/VideoCommon/TextureInfo.cpp
[gx-texture]: https://github.com/mshivam019/dusklight-ps5/blob/e281999cdb4fee6127525a9a9e97979480db4bf3/lib/gx/texture.cpp
[gpu-texture]: https://github.com/mshivam019/dusklight-ps5/blob/e281999cdb4fee6127525a9a9e97979480db4bf3/lib/gfx/texture.cpp
[patch10]: https://github.com/Jcanotorr06/pswaker/blob/2b95ad45e2620a7898c2a79789510ec7565d7364/platform/ps4/provenance/wind-waker/0010-texture-replacement-streaming.patch
[patch11]: https://github.com/Jcanotorr06/pswaker/blob/2b95ad45e2620a7898c2a79789510ec7565d7364/platform/ps4/provenance/wind-waker/0011-texture-replacement-smooth-publish.patch
[converter]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/tools/hd_pack/cos_hd_pack.cpp
[converter-cmake]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/tools/hd_pack/CMakeLists.txt
[prepare]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/scripts/hd/build_hd_pack.sh
[loader]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/src/pc/features/pc_hd_textures.cpp
[dds]: https://github.com/mshivam019/dusklight-ps5/blob/e281999cdb4fee6127525a9a9e97979480db4bf3/lib/gfx/dds_io.cpp
[api]: https://github.com/mshivam019/dusklight-ps5/blob/e281999cdb4fee6127525a9a9e97979480db4bf3/include/aurora/texture.hpp
[runtime-patch]: https://github.com/Jcanotorr06/pswaker/blob/2b95ad45e2620a7898c2a79789510ec7565d7364/platform/ps4/patches/game/0004-ps4-runtime.patch
[console-log]: https://github.com/Jcanotorr06/pswaker/blob/2b95ad45e2620a7898c2a79789510ec7565d7364/platform/ps4/evidence/verification-15/console/run-1-cold/diagnostic.log
[device]: https://github.com/mshivam019/dusklight-ps5/blob/e281999cdb4fee6127525a9a9e97979480db4bf3/lib/webgpu/gpu.cpp
[main]: https://github.com/Jcanotorr06/pswaker/blob/2b95ad45e2620a7898c2a79789510ec7565d7364/platform/ps4/game/main.cpp
[package]: https://github.com/Jcanotorr06/pswaker/blob/2b95ad45e2620a7898c2a79789510ec7565d7364/platform/ps4/complete-package.py
[packages-doc]: https://github.com/Jcanotorr06/pswaker/blob/2b95ad45e2620a7898c2a79789510ec7565d7364/platform/ps4/COMPLETE-PACKAGES.md
[transfer]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/scripts/switch/push_hd_pack.sh
[settings]: https://github.com/centollOS/SwitchWaker/blob/ba8d0a31446cd53ceaebd6b7269cca641e73bf4c/native/include/pc/pc_settings.h
[ignore]: https://github.com/Jcanotorr06/pswaker/blob/2b95ad45e2620a7898c2a79789510ec7565d7364/.gitignore
