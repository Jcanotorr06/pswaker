# Inherited program distribution audit (#47)

**Outcome on 2026-10-27: distribution remains blocked; keep #47 open.**
The audit establishes exact inherited inputs and narrows their source questions.
It does not establish a distributable program release. No program, module,
build, packaging input or runtime/renderer architecture was changed.
The eventual release must separately audit the exact Windows installer, desktop
dependencies, tools and bundled program. This ticket authorizes no installer
publication.

## Inspected scope

The retained #23 game candidate is version `01.13`, build ID
`f236a035ac406940e76a`, ELF SHA-256
`03e59e17a5a11265c9d307a47c43b28de9b91811fcdfa8e8a09fbd91f0f2237a`,
and SELF SHA-256
`64e75636d2a8ad31ef5f875b5439f1e05c5c1d004c9ae98ed650043aeda4c89c`.
Its seven-file data-free stage matches [the collected inventory][program].
This is a retained candidate, rather than a newly rebuilt program from today's
repository layout. Its earlier hardware observations remain bounded by the
[#23 report][integrated]. None are renewed by this audit.

The [collector][collector] reads the existing platform/game roots and verifies:

- All three packaged modules match the actual SDK and their members in the
  SHA-256-locked OpenOrbis archive.
- Nine ELF `DT_NEEDED` import stubs match the locked PacBrew package and the
  actual input hashes recorded when this game was built.
- Every listed native link library exists; [link order and hashes][link-inputs]
  preserve the selected static runtime, renderer and support libraries.
- 51 retained downloads match their recorded hashes; all 142 historical port
  inputs match the retained repository source snapshot.
- 103 platform and 23 game notice records match actual retained source files.
  Their 96 distinct texts are preserved in the [notice corpus][notices].

The current maintained input inventory is also [retained][maintained] to make
the audit-only nature of this branch checkable. Documentation and checkpoint
evidence are excluded from the build identity; historical input names remain
with their historical candidate.

## Module decisions

All three come from
`OpenOrbis/OpenOrbis-PS4-Toolchain@cd480230b946239f758333ef0dff40d67c5f0c20`;
the source archive SHA-256 is
`b77f9ba633cfe1cc829220321ea808b8990f4a625ccbad75b4f8f7686a9d8161`.
The [module inventory][modules] records exact archive members, sizes and source
candidate hashes. The [upstream research][research] cites the original code,
build scripts, project grant and relevant history.

| Stage path | Actual SHA-256 | Evidence-supported disposition |
| --- | --- | --- |
| `sce_module/libSceFios2.prx` | `905cf6b7c699eccb6b95291fc4dcaf5ce2d2605f450f36496d9b973777afa745` | Export and single `ret` body match the published SPRX template's `void dummy() {}` rather than the named module's C dummy function. Retain unchanged pending complete reconciliation. |
| `sce_module/libc.prx` | `8ac205d14351edb241238b372b2f1c3350a6385a271483d4867fe9a33bc6e4d3` | Actual body prints a test message and returns `0x1337`, matching the library-example source rather than the named module's dummy function. Retain unchanged pending complete reconciliation. |
| `sce_sys/about/right.sprx` | `1d7b1298bf219ad62a3452fd8ab7fe35fccf674431a24783336a6cb37f45dfed` | Published logo bytes match; embedded text matches the historical CRLF source, not the current LF source. Retain unchanged pending exact code/assets/CRT reconciliation and notice review. |

The OpenOrbis GPLv3 declaration, authored source and `build-and-copy.sh`
connection provide substantive grant/source evidence. The remaining question is
whether that source set and its applicable terms account for these exact
prebuilts, including embedded data, CRT, linker and conversion inputs.
The [read-only SELF inspection][module-inspection] demonstrates actual source
differences, rather than treating a plausible filename as correspondence.
The right source addition follows the Piglet binary commit, and its text source
later changes. The library example provides a stronger libc candidate than the
named dummy-module source; neither establishes the whole binary's provenance.
All inspected exported function bodies now have identified source candidates;
`module_start` and `module_stop` are undefined weak symbols. Module parameter
size/magic agree with published assembly, while the SDK-version metadata differs
from the retained historical and pinned sources. This is a generation-record
gap, not evidence that implementation source is absent or a requirement for
byte-identical compiler output. The [22 exact source/notice files][candidates]
retain the historical implementations and assets under their original notices.
The previous audit's unresolved status must not be read as proof that module
implementation sources do not exist, or that the names identify proprietary
Sony implementations. Equally, archive membership alone grants no rights.

## Stub and combined-artifact decisions

The ELF imports `libSceSysmodule.so`, `libSceSystemService.so`,
`libSceUserService.so`, `libSceVideoOut.so`, `libSceAudioOut.so`, `libScePad.so`,
`libSceNet.so`, `libkernel.so` and `libSceLibcInternal.so`.
[Exact stub hashes and package members][stubs] match
`ps4-openorbis-orbis-lib-gen-1.3-2-any.pkg.tar.xz`, SHA-256
`5ea71a7137a1a98eac09e33c4ed36806ecdf1412a4233e1eb0745e497899ec52`.
These are link inputs; the seven-file program stage does not separately ship
the `.so` pool. That observation does not itself decide output rights or the
required corresponding-source scope.

The [locked recipe][recipe] uses two distinct inputs: the v1.3 release pool
(`050b4898510dc6836c0d14a54d740c81be9ce376b1f2f8a5e57699eb82d584cf`)
and a PacBrew `libSceLibcInternal.so` override
(`b13d45fb931c6eb3515bf5c3eafd8d0ca028b9af0dd32807760d6ce1c0cce617`).
The generator/workflow source is published, but the reviewed generator and
export-database trees provide no explicit license grant. The workflow's `5.05`
database ref does not establish its exact historical input commit. PacBrew's
override introduction supplies a binary and recipe comment, without the precise
source/transformation that produced it. The recipe's `GNU GPL` package label
does not settle these independent inputs. See [primary-source findings][research].

The combination includes GPL game/runtime components and separately licensed
musl, LLVM, Mesa/DRM, Dawn, SDL, Aurora and fetched dependencies. The actual
static library arguments are recorded, rather than inferred from SDK contents.
Per-file exceptions, modification notices, embedded assets, source delivery and
any claimed System Library exclusion still need reconciliation against the
chosen distributable output. The preserved notice corpus is evidence, not an
assertion that filename-based notice discovery is a complete per-file audit.
No project-level license replaces this work.

## Concrete blockers and what would clear them

| Blocker | Required evidence / next action |
| --- | --- |
| Complete module source/build record | Consolidate the identified historical implementation/asset sources, applicable notices and generation instructions with the actual module source set. Document the original module-metadata difference; do not turn byte-identical reproduction into a licensing requirement or describe the implementation source as missing. |
| Stub grants and source chain | Establish applicable rights and exact generation inputs for the nine retained link stubs, including the separately modified libc stub; or substantiate why particular inputs are outside the required distribution/source closure. Keep the override distinct from the release pool. |
| Combined program and source delivery | Finish per-file compatibility/obligation review of the actual output, choose the compliant source-delivery method and assemble its exact data-free corresponding-source set with local modifications and scripts. A hash manifest or private retention alone is not source delivery. |

Removal and replacement are possible engineering resolutions, not established
outcomes. An absent direct ELF import does not prove that the console loader or
shell never uses a packaged module. Do not remove the modules simply to obtain
an empty blocker list. Any changed program/module/build/package input requires
a new build, fresh package extraction and closure inspection, matching ELF/SELF
identities, ABI/CPU/TLS checks, and renewed affected hardware evidence on the
selected Slim / firmware 9.00 / GoldHEN v2.4b18 environment. Check installation
and startup, route/renderer/audio/controls, and save/settings continuity where
affected; performance evidence belongs to the changed candidate as well.

## Retention and reproduction

The [evidence guide][evidence] specifies the private retained platform, game and
historical repository roots. [Retained download hashes][downloads],
[source-snapshot hashes][snapshot] and [build-record hashes][records] identify
the sources, locks, ordered patches, local adaptations and compile/link records
without publishing native binaries or owner content. The existing
[platform build instructions](README.md#reproduce-on-linux--wsl2) and
[game build instructions](GAME-STARTUP.md) remain applicable to development.
Use the retained historical snapshot to reproduce this candidate's inputs;
today's relocated checkout produces different identities.

No owner disc image, extracted game data, save, key, pipeline-cache database or
private complete package is an audit input or a public evidence output. Only
metadata, research and verified notice text are retained here. Existing private
archives/trees must remain available until a permitted source-delivery bundle
is established; they do not fill the unresolved source/grant gaps by themselves.

[program]: ../../evidence/ps4/redistribution-47/checked/program.json
[collector]: ../../evidence/ps4/redistribution-47/collect.py
[integrated]: ../../evidence/ps4/integrated-23/REPORT.md
[link-inputs]: ../../evidence/ps4/redistribution-47/checked/link-inputs.json
[notices]: ../../evidence/ps4/redistribution-47/checked/notice-index.json
[maintained]: ../../evidence/ps4/redistribution-47/checked/maintained-inputs.json
[modules]: ../../evidence/ps4/redistribution-47/checked/modules.json
[research]: ../research/inherited-program-rights.md
[stubs]: ../../evidence/ps4/redistribution-47/checked/import-stubs.json
[recipe]: ../../platform/ps4/provenance/pacbrew-toolchain/orbis-lib-gen.PKGBUILD
[evidence]: ../../evidence/ps4/redistribution-47/README.md
[downloads]: ../../evidence/ps4/redistribution-47/checked/retained-downloads.json
[snapshot]: ../../evidence/ps4/redistribution-47/checked/retained-source-snapshot.json
[records]: ../../evidence/ps4/redistribution-47/checked/retained-records.json
[module-inspection]: ../../evidence/ps4/redistribution-47/module-source-inspection.json
[candidates]: ../../evidence/ps4/redistribution-47/module-source-candidates.json
