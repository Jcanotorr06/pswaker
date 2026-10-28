# Inherited native program rights: upstream evidence

Research date: 2026-10-27. Scope: issue [#47][issue], the locked OpenOrbis
sample modules, import stubs and their source/grant relationship. This is an
evidence assessment; it does not authorize publication or clear a later installer.
The actual program bytes, link inputs and retained notices must be reconciled
with this report; see [the existing audit][audit] and [input locks][locks].

## Outcome supported by the sources

Upstream publishes actual source candidates for **all three sample modules**.
It is inaccurate to say their implementation source is simply absent. The
OpenOrbis project expressly declares GPLv3, and its build script builds those
modules and copies them into the sample layout. That is substantive licensing
and source evidence, beyond a binary happening to appear in an archive.
Read-only SELF inspection also finds specific source/body/export and asset
correspondence, including historical sources different from the named module
directories. The original build recipes and complete source closure still need
reconciliation. [Project declaration][oo-readme], [copy script][module-copy],
[binary commit][piglet-commit], [source additions][module-commit].

The entire inherited closure remains uncleared by this upstream research alone.
The v1.3 stub release's generation process is available, but its reviewed source
tree contains no license file or explicit grant for the generator/templates or
output. The PacBrew replacement stub additionally lacks a checked-in generation
patch/source recipe. Neither a package's `GNU GPL` label nor OpenOrbis's separate
project license establishes those independent repositories' per-file rights.
No source, module, program or packaging input was changed by this research.
[Generator tree][gen-tree], [generator README][gen-readme], [PacBrew recipe][recipe],
[replacement commit][replacement].

## Sample modules: source and limits

All paths below belong to
`OpenOrbis/OpenOrbis-PS4-Toolchain@cd480230b946239f758333ef0dff40d67c5f0c20`.
Its README describes an SDK built without the official Sony SDK and explicitly
licenses the project under GPLv3. No module-directory license or contrary
per-file licensing header appears in the reviewed module C/header/build files.
This supports GPLv3 for the authored module sources; it does not automatically
license unrelated dependencies or prove any given prebuilt contains only them.
[README][oo-readme], [complete pinned tree][oo-tree], [license][gpl].

| Packaged sample path | Published implementation candidate | What it establishes / remaining comparison |
| --- | --- | --- |
| `samples/piglet/sce_module/libSceFios2.prx` | [SPRX template `lib.cpp`][template-c] | Export NID `AS45QoYHjc4` matches C++ `dummy()`: a one-byte `ret` at virtual offset `0x20`, size 1, agrees with the template's empty function. The named module's [dummy returning zero][fios-c] has a different NID. |
| `samples/piglet/sce_module/libc.prx` | [Historical library example `lib.cpp`][library-c] | Export NID `peyA1QBswPc` matches C++ `testLibraryFunction()`: 28 bytes at `0x20` call imported `printf` then return `0x1337`. Body and embedded text agree with this historical example, not the [named module source][libc-c] or the changed current example. |
| `samples/piglet/sce_sys/about/right.sprx` | [Historical right source][old-right], including `string_data.h`, `logo_data.h`, `right.version` | All five getter NIDs and bounded bodies match the source structure. The CRLF text and 25,095-byte PNG occur exactly in the binary; current LF text does not. The module README attributes it to IDC. |

[`src/modules/build-and-copy.sh`][module-copy] builds `libc`, `libSceFios2` and
`right`, then copies the outputs into each eligible sample's `sce_module` and
`sce_sys/about`. This is the direct source-to-layout connection.

The Linux [`libc`][libc-make] and [`libSceFios2`][fios-make] Makefiles use
`clang --target=x86_64-pc-freebsd12-elf -fPIC -funwind-tables`, the SDK headers,
`ld.lld -m elf_x86_64 -pie`, SDK `link.x`, `lib/crtlib.o`, `-lSceLibcInternal`
and `-lkernel`. [`right`][right-make] uses Clang's
`-cc1 -triple x86_64-scei-ps4-elf`, its export version script and the same CRT,
linker script and library names. All call `create-fself` with paid
`0x3800000000000011`; right adds library name `sceGameRight`. The compiler/tool
versions and CRT actually used for the inherited sample binaries are not pinned
by these Makefiles. [`src/crt`][crt] contains CRT sources, but its presence alone
does not establish the contents of a particular prebuilt `crtlib.o`.

The three Piglet binary paths' histories through the locked commit contain only
their original addition in `b6c1869489a42bdcea7f6607308a9e1368532814`
(2021-12-12). Named libc/Fios dummy source already existed since
`d03b1c9ae64e8304cb947488efdf52d8bc8fa9cc` (2020-08-02); right source arrives in
`39414b5d40c20026466fee6dc3f29cf6c05eebee` (2021-12-18). The right text subsequently
changes from a byte array with CRLF to a C string with LF in
`2931a94c805009c7764be4bfa648ea41917de45e`. Therefore, retaining only the latest
file is not evidence of source correspondence for the earlier binary.
[Binary addition][piglet-commit], [source addition][module-commit],
[right source/build changes][llvm14].

The [inspection JSON][inspection] records SELF/ELF offsets, segment/function
hashes, exact exported symbol bounds, NID comparisons and bounded disassembly.
[`inspect_module_sources.py`][inspection-script] reproduces it without changing
build inputs or publishing extracted binaries. `module_start` and `module_stop`
are undefined weak symbols in all three modules; no startup bodies need mapping.
Module size/magic match CRT assembly; SDK metadata `0x4508101` differs from both
historical `0x4508001` and pinned `0x1000051`. Original generation metadata remains
unreconciled, not missing function implementations. The exact
[source candidates and notices][candidates] are retained at immutable revisions;
no bit-identical compiler output is demanded as a licensing condition.

## Import stubs: release pool and PacBrew override are separate inputs

`OpenOrbis/orbis-lib-gen` tag `v1.3` resolves to
`310dcba1f99b180a9361cc88e6352eeeca482a76`. The release asset `lib.tar.gz`
is a binary pool, not implementation source. The locked recipe expects SHA-256
`050b4898510dc6836c0d14a54d740c81be9ce376b1f2f8a5e57699eb82d584cf`.
[Tag API][tag], [release][release], [recipe][recipe].

Its [release workflow][workflow] checks out `idc/ps4libdoc` at `ref: 5.05`,
runs `generate.py ps4libdoc/system/common/lib`, runs `gen_makefile.py`, builds,
removes `libc.so` and archives the remaining `.so` files. The
[generator][generator] emits empty/infinite-loop function bodies from exported
symbol names; the [makefile generator][make-generator] compiles these as shared
libraries using `gcc -ffreestanding -nostdlib -fno-builtin -fPIC`. They are link
stubs, not source builds of the console implementations they name.

The reviewed v1.3 tree has only README, scripts, templates and a workflow; no
`LICENSE`, `COPYING` or explicit licensing statement appears there. The reviewed
`idc/ps4libdoc` `5.05` tree likewise has no license file; its README says library
documentation. At research time that ref resolves to
`62d172c83a819234a8bf61a89c10ae781669a67b`, which does **not** prove the release
workflow checked out that commit in 2022. A database version name and current
ref resolution do not establish exact release source or grant terms.
[Generator tree][gen-tree], [templates/source][gen-template],
[database tree][db-tree], [database README][db-readme].

PacBrew's locked recipe at
`16f27e38760ea21eaf1187d0edbf4342c4a44021` first copies that pool, then overwrites
`libSceLibcInternal.so` with a separate local binary, SHA-256
`b13d45fb931c6eb3515bf5c3eafd8d0ca028b9af0dd32807760d6ce1c0cce617`.
Its comment says allocation symbols were removed to route calls through musl's
wrapper. [The introduction commit][replacement]
`536567a9b45b6d30cc0bad12fa76450fff2ee94d` adds the binary and recipe change,
without generated source or the commands/patch that produce the reduction.
The two stubs must not be conflated. Concrete missing evidence is the override's
exact generation inputs/transformation and an applicable grant for its contents,
as well as the corresponding evidence for retained release-pool inputs.
[Locked recipe][recipe], [PacBrew pinned tree][pacbrew-tree].

## Combined distribution and a supported way forward

GPLv3 section 1 requires the preferred modification sources and scripts needed
to generate/install/run the work; qualifying System Libraries are excluded.
Sections 4-6 require preserved notices, modification notices where applicable,
and a compliant source-delivery method for object-code conveyance. Section 5
distinguishes a combined program from independent aggregation; putting files
beside one another does not settle that distinction. Section 2 does not apply
the generator's license to outputs automatically. These rules supply obligations,
not missing rights for third-party binaries. [GPLv3 sections 1-6][gpl].

For this closure, preserve the actual runtime/dependency per-file terms, source
archives, local changes, ordered patches, locks, linker/build/install recipes,
embedded module assets and notices. Assess actual linkage and runtime loading
before invoking a System Library exception or labeling the package an aggregate.
The current project [licensing audit][audit] already records that combined-work
and per-file review remains required.

The supported next steps are evidence work, not an asserted clearance:

1. Compare each sample binary's code/data/exports/CRT against its published
   candidates and relevant historical versions. Preserve results and identify
   the actual applicable GPL source set. A reproducible scratch build can help;
   exact byte identity is strong evidence but is not itself a license requirement.
2. Establish rights and exact source/generation inputs for the retained stub
   pool and PacBrew override, or substantiate why a particular input is outside
   the distributed/required corresponding-source closure. Link-only status must
   be evidenced against the actual output, not inferred from `.so` names.
3. Only adopt removal or replacement after establishing necessity and behavior;
   changed inputs require a rebuilt/inspected closure and renewed affected native
   and hardware verification under [#47][issue]. This report makes no replacement.

Until those points and the actual deliverable/source bundle are established,
there is no evidence-supported declaration that the whole inherited program is
distributable. Module function/data source correspondence and a project grant
are now evidenced; original generation/source-delivery records and the independent
stub grant/source chain still require resolution. Keep #47 open while any required
question remains unresolved. Owner game data, keys and private complete packages
are outside this research and any public evidence/source bundle. [Issue scope][issue].

[issue]: https://github.com/Jcanotorr06/pswaker/issues/47
[audit]: ../ps4/LICENSING.md
[locks]: ../../platform/ps4/dependencies.lock.json
[oo-readme]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/cd480230b946239f758333ef0dff40d67c5f0c20/README.md#license
[oo-tree]: https://api.github.com/repos/OpenOrbis/OpenOrbis-PS4-Toolchain/git/trees/cd480230b946239f758333ef0dff40d67c5f0c20?recursive=1
[gpl]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/cd480230b946239f758333ef0dff40d67c5f0c20/LICENSE
[template-c]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/cd480230b946239f758333ef0dff40d67c5f0c20/src/templates/PS4%20SPRX%20Project/PS4%20SPRX%20Project/lib.cpp
[library-c]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/b6c1869489a42bdcea7f6607308a9e1368532814/samples/library_example/library_example/lib.cpp
[old-right]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/tree/39414b5d40c20026466fee6dc3f29cf6c05eebee/src/modules/right
[inspection]: ../../evidence/ps4/redistribution-47/module-source-inspection.json
[inspection-script]: ../../evidence/ps4/redistribution-47/inspect_module_sources.py
[candidates]: ../../evidence/ps4/redistribution-47/module-source-candidates.json
[fios-c]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/cd480230b946239f758333ef0dff40d67c5f0c20/src/modules/libSceFios2/libSceFios2/lib.c
[libc-c]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/cd480230b946239f758333ef0dff40d67c5f0c20/src/modules/libc/libc/lib.c
[right-c]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/tree/cd480230b946239f758333ef0dff40d67c5f0c20/src/modules/right
[module-copy]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/cd480230b946239f758333ef0dff40d67c5f0c20/src/modules/build-and-copy.sh
[libc-make]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/cd480230b946239f758333ef0dff40d67c5f0c20/src/modules/libc/Makefile
[fios-make]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/cd480230b946239f758333ef0dff40d67c5f0c20/src/modules/libSceFios2/Makefile
[right-make]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/cd480230b946239f758333ef0dff40d67c5f0c20/src/modules/right/Makefile
[crt]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/tree/cd480230b946239f758333ef0dff40d67c5f0c20/src/crt
[piglet-commit]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/commit/b6c1869489a42bdcea7f6607308a9e1368532814
[module-commit]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/commit/39414b5d40c20026466fee6dc3f29cf6c05eebee
[llvm14]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/commit/2931a94c805009c7764be4bfa648ea41917de45e
[tag]: https://api.github.com/repos/OpenOrbis/orbis-lib-gen/git/ref/tags/v1.3
[release]: https://github.com/OpenOrbis/orbis-lib-gen/releases/tag/v1.3
[workflow]: https://github.com/OpenOrbis/orbis-lib-gen/blob/310dcba1f99b180a9361cc88e6352eeeca482a76/.github/workflows/release-stable.yml
[generator]: https://github.com/OpenOrbis/orbis-lib-gen/blob/310dcba1f99b180a9361cc88e6352eeeca482a76/generate.py
[make-generator]: https://github.com/OpenOrbis/orbis-lib-gen/blob/310dcba1f99b180a9361cc88e6352eeeca482a76/gen_makefile.py
[gen-tree]: https://api.github.com/repos/OpenOrbis/orbis-lib-gen/git/trees/310dcba1f99b180a9361cc88e6352eeeca482a76?recursive=1
[gen-readme]: https://github.com/OpenOrbis/orbis-lib-gen/blob/310dcba1f99b180a9361cc88e6352eeeca482a76/README.md
[gen-template]: https://github.com/OpenOrbis/orbis-lib-gen/blob/310dcba1f99b180a9361cc88e6352eeeca482a76/data/source.template
[db-tree]: https://api.github.com/repos/idc/ps4libdoc/git/trees/62d172c83a819234a8bf61a89c10ae781669a67b?recursive=1
[db-readme]: https://github.com/idc/ps4libdoc/blob/62d172c83a819234a8bf61a89c10ae781669a67b/README.md
[recipe]: https://github.com/PacBrew/ps4-openorbis/blob/16f27e38760ea21eaf1187d0edbf4342c4a44021/orbis-lib-gen/PKGBUILD
[replacement]: https://github.com/PacBrew/ps4-openorbis/commit/536567a9b45b6d30cc0bad12fa76450fff2ee94d
[pacbrew-tree]: https://api.github.com/repos/PacBrew/ps4-openorbis/git/trees/16f27e38760ea21eaf1187d0edbf4342c4a44021?recursive=1
