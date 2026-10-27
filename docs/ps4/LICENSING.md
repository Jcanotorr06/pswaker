# Source, patch and artifact audit

This preparation does not clear public binary distribution. The local diagnostic
uses inherited runtime and SDK artifacts whose per-file rights must be resolved
for a combined distribution. No game data, disc images or private keys are inputs.
The packager's generated fake-PKG keystone is packaging metadata, not an owner's
game/decryption/signing key.

The [#47 inherited-program audit](INHERITED-PROGRAM-AUDIT.md) adds a rechecked
game/module/stub inventory, retained notice texts and primary-source research.
It finds published source candidates for all three sample modules and narrows
the remaining binary/source and grant questions. Distribution remains blocked;
the issue stays open. Earlier evidence files retain their historical conclusions.

## Verified provenance

All 14 committed PacBrew `PKGBUILD` files match the `pkgbuild_sha256sum` in the
corresponding locked binary package's `.BUILDINFO`. See
`provenance/sdk-recipes.json`. Toolchain recipes come from
`PacBrew/ps4-openorbis@16f27e38760ea21eaf1187d0edbf4342c4a44021`; portlibs recipes
come from `PacBrew/ps4-openorbis-portlibs@d6a523a5a4a7b86846d91134d40a34357721a273`.
Their original comments and source URLs/checksums remain intact. This verifies
the packaging recipe chain; it does not invent missing source for binary inputs.

The linked SDK C runtime source is
`PacBrew/ps4-openorbis-musl@140a653299ffcb1457bc63a5ab1f507d7bb37c54`.
OpenOrbis headers/linker material and sample modules come from
`OpenOrbis/OpenOrbis-PS4-Toolchain@cd480230b946239f758333ef0dff40d67c5f0c20`.
The SDK LLVM-12 release source is
`fed41342a82f5a3a9201819a82bf7a48313e296b`; runtime C++ libraries are replaced by
the selected LLVM 21 source. Archive digests are checked before preparation.
SDK zlib/libpng/bzip2 implementations are replaced by source builds with the
selected compiler/CPU flags. SDK libc++12 is not linked into the diagnostic.

`audit-inputs.py` rechecks those recipe hashes against the actual fetched SDK,
inventories retained notice files, and compares all three packaged sample modules
byte-for-byte against the pinned OpenOrbis source archive. It writes the module
hashes, archive paths and unresolved status into `evidence/license-audit.json`.
The exact payload allowlist rejects additional private modules or other files.

## Notices and outstanding distribution work

| Component | Retained source notices / obligations to review for the actual combination |
| --- | --- |
| DolphinPS4 runtime and Dusklight PS4 changes | GPL runtime files and per-file MIT/other notices remain in their source trees. Preserve the complete corresponding source and build/patch recipes for any permitted combined distribution. |
| OpenOrbis SDK | The pinned source has a GPLv3 top-level license, but this alone does not settle per-file CRT/libc/stub/module terms. The musl source has its own COPYRIGHT with MIT and additional permissive per-file terms. Preserve both. |
| Mesa and PS4 DRM | Preserve Mesa's complete license directory and per-file notices, including the DRM replacement. Do not replace its notices with a single project label. |
| Dawn, Abseil, SDL3, Aurora and fetched dependencies | Retain their exact source trees, licenses and third-party notices; the notice inventory includes nested fetched sources. |
| LLVM 12 / LLVM 21 | Preserve Apache-2.0 with LLVM exception and all relevant runtime/third-party notices from the pinned trees. |
| LibOrbisPkg | Preserve its source license and the provenance of the selected PS4 patch; a source-built host packager is separate from target runtime code. |
| SDK sample libSceFios2.prx, libc.prx, right.sprx | Exact binary provenance is verified. OpenOrbis publishes module source candidates and GPLv3 project/build-script evidence; reconcile the exact prebuilts, CRT and embedded assets with that source and applicable terms. See the #47 audit. Presence in the SDK/source archive alone is not clearance. |
| SDK import stubs | The matching orbis-lib-gen recipe names a checksummed release binary pool and a separately checksummed libSceLibcInternal.so. Preserve that provenance; do not claim these are rebuilt implementation libraries or that a database version supplies their missing source. |

Before distribution, resolve the outstanding per-file/module/stub rights and
combined terms, retain all notices, and make the exact corresponding sources,
local changes, host/input locks and build instructions available as required.
Wind Waker renderer patch originals, immutable source URLs, hashes, individual
dispositions and adapted diffs are retained in `provenance/wind-waker/`,
`renderer.lock.json` and `patches/wind-waker/`; preserve them with corresponding
Aurora/SwitchWaker source and per-file notices. Excluded PS5 reference patches
are provenance inputs rather than linked platform implementations.
The source archives and generated notice corpus are retained with each local
build. A top-level license cannot substitute for this audit. Public release is
outside #13 and remains outside the first-playable scope.
