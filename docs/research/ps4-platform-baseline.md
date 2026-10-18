# PS4 SDK and graphics baseline investigation

Investigated 2026-10-18 for [Identify a reproducible PS4 SDK and graphics dependency set](https://github.com/Jcanotorr06/pswaker/issues/2). Scope: planning a native Wind Waker port for PS4 Slim 9.00, with Linux tooling through WSL2. No SDK compilation, package installation, game integration or hardware test was performed.

## Finding

**Recommend Dusklight's OpenOrbis/DolphinPS4/Mesa combination as the candidate for a bounded reproducibility experiment. It is not yet a reproducible, validated baseline.** Its runtime, direct ICD loading, VideoOut presentation and package scripts form a traceable public source chain. Recovering missing configuration and freezing SDK inputs are necessary first. The subsequent human decision selects the architecture.

The [published tree][tree] lacks `toolchain/ps4.cmake` and `probe-dawn/`, although its scripts require them. The [build inventory][inventory] itself disclaims a verified clean rebuild. Its PS4 Pro claim is not evidence for this Slim, firmware 9.00, or Wind Waker's 720p30 target.

## Immutable source inventory

Apply Dusklight's patches from `fd483cf5d4f04b0f4d887ff412d0e8691925de08`; these are modifications to the listed bases, not interchangeable upstream releases.

| Input | Resolved public revision / contract |
| --- | --- |
| DolphinPS4 runtime and toolchain | [`b1879cc0267a2a4f0949d7b80478fcf2abca24f6`][dolphin], plus Dusklight's runtime patch and replacement `tools/ac_ps4_drm.c` |
| Mesa | Official `mesa-26.0.8` tag object `f32a91e2ae2d2d9018f0177dbf8782e8369d0363` peels to [`60e95b787857afbc9a00b693b91c0d9c8923a430`][mesa-release]. Manifest shorthand `80c7811` remains unresolved. |
| LLVM runtimes 21.1.6 | [`a832a5222e489298337fbb5876f8dcaf072c5cca`][llvm], with DolphinPS4 preparation and Dusklight atomic-wait changes |
| Dusklight PS5 source | [`5811958531cb0a9eafeb293fafcb36071883bfdf`][ps5], peeled from annotated `ps5-v0.1.0`; source reference only |
| Aurora / Borealis | [`e281999cdb4fee6127525a9a9e97979480db4bf3`][aurora] / [`4ac5e7052a8c49a122f8d57f626b5c75c5ca6968`][borealis] |
| Dawn / SDL3 | [`652a3104791369cd23605856fbc041375ccda875`][dawn-base] / [`68159af2b34cc4fe5b3548faa89e87a69e4d2dce`][sdl-base], from Dusklight PS5 dependency tags |
| Abseil | [`5c695e68fcd3e7483ed300b6591d1ec49ae37cf4`][abseil], from `deps/abseil-20240722-ps5` |
| LibOrbisPkg | [`594021fdc435409f755a6ae0781b65ec6cec846c`][pkg], with published patch; patched source tarball is also present under Dusklight `third_party/` |

The upstream Mesa release was inspected using a shallow clone; `git apply --cached --check` accepted Dusklight's Mesa patch against its index. This establishes patch applicability, **not compilation or equivalence to the author's unresolved `80c7811` tree**. Public git/GitHub ref inspection resolved the other full commits above. Aurora/Dawn/SDL pins here document Dusklight's platform reference; they are not a choice to replace Wind Waker's different dependency pins.

## SDK and runtime contract

[fetch-openorbis.sh][sdk-fetch] downloads 15 PacBrew packages, including Clang, headers, musl, libc++, `create-fself`, `create-gp4`, pkgtools, library-stub generation and compression libraries. It checks package SHA-256 values against the **current remote database**, not a committed lock. The database was publicly downloadable during this investigation; its observed SHA-256 was `0e9357222106ccd3bda8e5404772e2e207407acdf27b64976af602151974cf40`. Entries included Clang/libc++ `12.0.1-1`, headers `0.5.2-4`, musl `1.5-2`, create-fself `1.2-3`, and pkgtools `0.2.231-5`. The hash identifies an observation, not a durable download guarantee. No SDK package binaries were downloaded or verified here. A real lock needs every filename, checksum, source revision and preserved obtainable artifact.

[ps4-love-modern.cmake][modern] includes PacBrew's SDK CMake file, then selects host Clang 21 and static libc++/libc++abi 21 with SDK libunwind. It targets `x86_64-pc-freebsd12-elf`; the platform uses `-march=btver2`. [prepare-sysroot.sh][overlay] corrects header/API mismatches such as clock identifiers, mmap flags and signal definitions. These overlays and link order are part of the ABI contract.

[ps4-love-style.cmake][style] supplies allocator and pthread-once wrapping, CRT selection, prioritized constructor collection, `.data.*` and TLS subsection collection, whole-archive Mesa linking, SELF conversion and output checks. [ps4_runtime.cpp][runtime] implements thread-exit destructor registration and uses initial-exec TLS. These are concrete compatibility adaptations, not proof every C++ feature works. Probe static constructors, per-thread TLS isolation/destructors, pthread once, mutex/condition-variable behavior and ordinary atomics. Wider atomics must be checked against actual generated references rather than assumed lock-free.

[build-libcxx.sh][libcxx-build] rewrites FreeBSD-specific libc++ paths for the musl-based environment and disables unavailable syscall paths. Dusklight's [atomic-wait patch][atomic] adds condition-variable-backed wait buckets. Its paths are `a/atomic.cpp`, so apply it explicitly in LLVM's `libcxx/src`, with preparation/patch order recorded; the generic per-tree patch instruction is insufficient. Avoid the builder's opportunistic local LLVM source-copy path for a clean experiment.

## Graphics, loader and packaging coherence

Dusklight's [Dawn patch][dawn-patch] gets `vkGetInstanceProcAddr` directly through `vk_icdGetInstanceProcAddr`, without the desktop shared-library loader. DolphinPS4's [Mesa build][mesa-build] creates static RADV/ACO/NIR libraries and replaces the amdgpu kernel interface with PS4 GNM calls. Dusklight's [Mesa patch][mesa-patch] adds VideoOut WSI behind `VK_KHR_display`. Preserve this group together; a separate Vulkan loader binary is not an assumed dependency.

The missing `toolchain/ps4.cmake` for Dawn/SDL3 can be reconstructed from the public modern toolchain contract, but identical settings cannot be asserted: record compiler flags, include ordering, sysroot, CMake discovery and static-library behavior explicitly. The missing probe source must be authored or replaced with a minimal public example adapted to this loader/surface contract. Also freeze Linux distribution, Clang/LLVM 21 tools, CMake, Ninja, Meson, Python/Mako/PyYAML, pkg-config, Git, curl, tar, GitHub CLI, libdrm headers (`libdrm-2.4.125`) and Dawn's fetched dependency revisions. The scripts describe Linux x86_64; WSL2 execution remains untested.

[package-game.sh][package] delegates to patched DolphinPS4 packaging: ELF → fake SELF/`eboot.bin`, staged metadata → GP4 → PKG. It checks the first executable segment at address zero and supports a patched LibOrbisPkg executable for large packages. Building that tool needs a pinned .NET SDK as well. The [underlying packager][make-pkg] otherwise copies optional Sony module files; Dusklight explicitly redirects the external module directory to `/nonexistent`. Inventory the remaining SDK sample `.prx`/`right.sprx` inputs and notices rather than silently treating a clean SDK extraction as sufficient. The initial graphics probe should contain no disc data, texture packs or PGO profile.

## Alternatives, notices and next evidence

The separate [`orbis-ports/mesa-ps4`][alternative] uses its own native driver/WSI contract. Its [archived porting kit][kit] provides another toolchain, loader and triangle path, with an `orbis-compat` overlay dependency. The advertised `orbis-ports/orbsdk` successor returned public GitHub API HTTP 404 here. The archived public kit is investigable; it is not a maintained replacement established by this research. Do not combine its loader/runtime artifacts with Dusklight's without an explicit ABI and surface adaptation experiment.

Preserve per-file licenses and distribution notices. Dusklight's [license inventory][licenses] identifies GPL-2.0-or-later Dolphin runtime components and distributes the combined application under GPLv3; Mesa/PS4 DRM components are principally MIT, Dawn BSD-3-Clause, SDL zlib, and LLVM runtimes Apache-2.0 with LLVM exception. It identifies LibOrbisPkg as LGPL-3.0 and explicitly leaves OpenOrbis runtime (`crt1.o`, `libc.a`) licensing unconfirmed before public release. Resolve that ledger, including SDK sample modules and tools/linker material, for the exact artifacts chosen. Runtime reuse also needs a corresponding-source/build-recipe distribution plan; a top-level permissive license alone is insufficient. This records upstream declarations, not a legal compatibility determination for future code.

Smallest useful experiment: freeze the inputs, fill the missing toolchain/probe contract, build and package a disc-free runtime-plus-Dawn clear/triangle twice in clean Linux environments, and retain manifests, logs and ELF/package comparisons (explain timestamps rather than presuming bit identity). On the owner's Slim 9.00, record homebrew version, device/extensions/limits, constructor/TLS/thread/atomic checks, visible repeated presentation and clean close/relaunch. Neither public PS4 Pro reports nor a clean host build establish these results. Only then can the stack decision rely on measured target evidence.

[tree]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/tree/fd483cf5d4f04b0f4d887ff412d0e8691925de08
[inventory]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/BUILDING.md
[dolphin]: https://github.com/iHaiDeeZ/DolphinPS4/tree/b1879cc0267a2a4f0949d7b80478fcf2abca24f6
[mesa-release]: https://gitlab.freedesktop.org/mesa/mesa/-/commit/60e95b787857afbc9a00b693b91c0d9c8923a430
[llvm]: https://github.com/llvm/llvm-project/tree/a832a5222e489298337fbb5876f8dcaf072c5cca
[ps5]: https://github.com/mshivam019/dusklight-ps5/tree/5811958531cb0a9eafeb293fafcb36071883bfdf
[aurora]: https://github.com/mshivam019/dusklight-ps5/tree/e281999cdb4fee6127525a9a9e97979480db4bf3
[borealis]: https://github.com/encounter/borealis/tree/4ac5e7052a8c49a122f8d57f626b5c75c5ca6968
[dawn-base]: https://github.com/mshivam019/dusklight-ps5/tree/652a3104791369cd23605856fbc041375ccda875
[sdl-base]: https://github.com/mshivam019/dusklight-ps5/tree/68159af2b34cc4fe5b3548faa89e87a69e4d2dce
[abseil]: https://github.com/mshivam019/dusklight-ps5/tree/5c695e68fcd3e7483ed300b6591d1ec49ae37cf4
[pkg]: https://github.com/OpenOrbis/LibOrbisPkg/tree/594021fdc435409f755a6ae0781b65ec6cec846c
[sdk-fetch]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/tools/fetch-openorbis.sh
[modern]: https://github.com/iHaiDeeZ/DolphinPS4/blob/b1879cc0267a2a4f0949d7b80478fcf2abca24f6/toolchain/ps4-love-modern.cmake
[overlay]: https://github.com/iHaiDeeZ/DolphinPS4/blob/b1879cc0267a2a4f0949d7b80478fcf2abca24f6/toolchain/prepare-sysroot.sh
[style]: https://github.com/iHaiDeeZ/DolphinPS4/blob/b1879cc0267a2a4f0949d7b80478fcf2abca24f6/toolchain/ps4-love-style.cmake
[runtime]: https://github.com/iHaiDeeZ/DolphinPS4/blob/b1879cc0267a2a4f0949d7b80478fcf2abca24f6/port/ps4_runtime.cpp
[libcxx-build]: https://github.com/iHaiDeeZ/DolphinPS4/blob/b1879cc0267a2a4f0949d7b80478fcf2abca24f6/toolchain/build-libcxx.sh
[atomic]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/patches/libcxx-ps4-atomic-wait.patch
[dawn-patch]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/patches/dawn-ps4.patch
[mesa-build]: https://github.com/iHaiDeeZ/DolphinPS4/blob/b1879cc0267a2a4f0949d7b80478fcf2abca24f6/scripts/build-mesa.sh
[mesa-patch]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/patches/mesa-26.0.8-ps4.patch
[package]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/tools/package-game.sh
[make-pkg]: https://github.com/iHaiDeeZ/DolphinPS4/blob/b1879cc0267a2a4f0949d7b80478fcf2abca24f6/scripts/make-pkg.sh
[alternative]: https://github.com/orbis-ports/mesa-ps4/tree/1a59cc147b54e3970814b37313e2f27357672e9d
[kit]: https://github.com/orbis-ports/orbis-porting-kit/blob/213b0c38ff25ea7ca402c8844a6494086d0f1cae/README.md
[licenses]: https://github.com/BgbrhrWatchinOVO/dusklight-ps4/blob/fd483cf5d4f04b0f4d887ff412d0e8691925de08/THIRD_PARTY_LICENSES.txt
