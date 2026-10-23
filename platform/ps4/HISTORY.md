# Diagnostic history and evidence limits

The maintained diagnostic deliberately adopts the corrected sources and useful
build checks from `prototype/ps4-platform-diagnostic` at
`c7bdf0d584c0bcc0ee330a6564ddb2f07333526c`; no prototype/research branch is merged.
Exploratory startup-only probes, host-renderer reproductions, FTP helpers and
private owner material are not build dependencies of the maintained program.

| Historical trial | Observation and correction |
| --- | --- |
| Original 01.00, build `97fc99208640c483fdc2` | Owner reported black screen, silence and CE-34878-0. Initially believed to have no logs; retrieved logs superseded that assumption. Runtime preflight passed, then SDL reported no available video device. Explicit dummy selection fixed the placeholder-video initialization boundary. |
| SDL retry 01.01 | Three owner runs reached graphics/audio, but Aurora's allocated EFB was 569x320 and white EFB/offscreen comparisons failed. Raw WebGPU purple checks did not establish GX correctness. |
| Corrected 01.02 | Missing GXInit caused black GX output. GX initialization plus RGBA6 preserved exact-white alpha checks; RGB8 left offscreen alpha zero. Explicit 640x480 VI base at 1.5x and 16:9 produced allocated 1280x720 EFBs. Pipeline preparation precedes checked frames. Readbacks report mapping status, dimensions, format and sampled values. GPU completion is drained before teardown. |

Frozen primary evidence:

- [Original crash and superseded no-log assumption](https://github.com/Jcanotorr06/pswaker/blob/c7bdf0d584c0bcc0ee330a6564ddb2f07333526c/prototypes/ps4-platform/evidence/startup-20261021/status.md).
- [Retrieved SDL failure and correction](https://github.com/Jcanotorr06/pswaker/blob/c7bdf0d584c0bcc0ee330a6564ddb2f07333526c/prototypes/ps4-platform/evidence/sdl-video-20261021/status.md).
- [Failed 01.01 console trials](https://github.com/Jcanotorr06/pswaker/blob/c7bdf0d584c0bcc0ee330a6564ddb2f07333526c/prototypes/ps4-platform/evidence/aurora-results-20261022/status.md).
- [Differential reproduction, correction and build](https://github.com/Jcanotorr06/pswaker/blob/c7bdf0d584c0bcc0ee330a6564ddb2f07333526c/prototypes/ps4-platform/evidence/aurora-correction-20261022/status.md).
- [Corrected hardware pass and clean-build evidence](https://github.com/Jcanotorr06/pswaker/blob/c7bdf0d584c0bcc0ee330a6564ddb2f07333526c/prototypes/ps4-platform/evidence/aurora-pass-20261022/status.md).

The historical tested 01.02 package is build `4b1830b0443ff170425e`, compiled
diagnostic revision `b45d5e29246bd1c86d78f9ca165cbc3f7b4d6e5b`, PKG SHA-256
`9764e1acb1e7fa8a17c8c7aee9ca3793ac908da38368188b52de33a49dd399be`.
The owner confirmed PS4 Slim / firmware 9.00 / GoldHEN v2.4b18 and observed the
expected triangle, white background, purple swatch, summary and continuous tone.

Its cold/warm/warm launches 7/8/9 each ran about 600.3 checked seconds, with 120
cycles and zero failures. Each run had 120 allocated 1280x720 EFB checks, 120
exact-white EFB and 120 exact-white offscreen comparisons of 1,024 RGBA pixels,
and 120 purple depth/blend/copy/readback checks. Runtime, input, synthetic audio,
persistence, evidence retrieval and orderly shutdown passed. Twenty-one resource
samples per run showed bounded use after startup; that is not a general leak-free
claim. The earlier mapping-abort warning disappeared; intentional device-loss
messages during destruction remained visible outside the checked loop.

Two renewed historical clean builds also completed. Their ELF/PKG bytes differed;
the frozen comparison and bounded difference audit explain the observations
without claiming bit identity or formal semantic equivalence. They are not runs
of a maintained artifact. **No historical hardware result or binary hash above
is attributed to a newly built 01.03 package.** #15 requires new evidence tied to
the actual installed maintained PKG before game integration.

During maintained preparation, a development run stopped on a duplicate Abseil
patch while staging was being reorganized. SDK-support development exposed a
compiler-rt target-option conflict, an unnecessary default sanitizer build, a
missing libc++ CMake source subtree and libunwind's implicit FreeBSD alloca
declaration. The maintained scripts choose the builtins target explicitly,
extract its required source closure and include musl's alloca.h for unwinder
compilation. The final clean build uses a new absent root. These are host
preparation failures/corrections, not console observations.

The implementation review also caught transitive SDK libpng/bzip2 linkage through
Aurora/FreeType. The maintained preparation now rebuilds their exact recipe
sources with the selected flags; the earlier development root is not treated as
the final clean build.

The `maintained-13-c` development driver later stopped after the graphics libraries
with a shell read-position error because its script had been edited while it was
running. The on-disk script passes `bash -n`. The retained final run starts from
another absent root, using an immutable `git archive` source snapshot and
`JOBS=12`; it recompiles all target libraries and does not reuse the interrupted
run's objects.

That snapshot's final link exposed missing setjmp/longjmp in the rebuilt musl.
The GitHub ZIP represents `src/setjmp/ps4 -> x86_64` as a Unix symlink, while
Python's generic ZIP extraction created a plain text file. The preparation CLI
now restores recorded Unix symlinks within the extraction root. A regression
test first reproduced the missing prepared directory, then passed after the fix.
