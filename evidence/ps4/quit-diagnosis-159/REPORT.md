# Normal-Quit crash: diagnosis and proposed correction (#159)

Assessed 2026-11-06 against [issue #159](https://github.com/Jcanotorr06/pswaker/issues/159).

**Cause, supported by the owner's `crash.log` and a host reproduction: the SDK
shutdown wakes game worker threads blocked on an empty message queue. Blocking
receive then returns `FALSE` with no message, and five worker loops ignore that
result and dispatch anyway.** On 01.25 this produces a null read in a worker, which
enters the crash logger. The logger then faults a second time, which is the fault
GoldHEN reported.

`0015-worker-shutdown.patch` corrects all five loops and passes the host
reproduction. **The owner reports one normal Quit on candidate 01.26 completing
without error and reaching `shutdown-complete`.** The remaining console acceptance
items are listed below; the issue stays open until they are dispositioned.

The owner reports persistence in every subsequent version and confirms PS4 Slim,
firmware 9.00, GoldHEN v2.4b18. This assessment verifies the supplied 01.25
captures and retained candidate; it does not independently audit every intervening
version. It does not change the owner's clarification that #159 is separate from #149.

## Verified inputs

| Input | SHA-256 |
| --- | --- |
| Supplied `logs.txt` (41,571 bytes) | `50911d8ba4b0b8063998b47a88c74fee72e38203493c31c6ec5548bf08df55e7` |
| Supplied `crash.log` (8,314 bytes) | `741595d1046a3c4539832d9cd43ab88a6293c13788e685ae1429ef492ea7dec8` |
| Complete package, version `01.25` | `10ecd0e4a4c72a99aeb9b5ec9979757f62e3e550b1ddaa7d7a96484d815bea41` |
| Matching unstripped ELF | `c2d48776ed9f79d90ec71d61cc0732a3b2b673da361ca57d7c4a10596a2392fc` |
| Selected `DolphinPS4/port/ps4_crashlog.cpp` | `ed2bd04990ec30187edb21411c337272dda9011d2980080549e7f0da3e462d77` |

The retained #155 `presentation-155/complete-01.25` package and ELF independently
hash to the supplied identities. Its manifest records build/cache ID
`35a453336a0e4b0d432c`. The ELF retained in the #149 build also has the same hash;
its earlier package version is not substituted for the 01.25 package. GoldHEN's
launch record independently identifies `appVer={01.25}`. This hash check is not a
new complete-package extraction/inspection or a measurement of installed bytes.

The attachments were copied byte-for-byte to the private artifact groups
`quit-diagnosis-159-20261106` (GoldHEN capture) and
`quit-all-workers-159-20261106` (`crash.log`, this correction). The earlier
three-worker attempt is retained as `quit-crashlog-159-20261106`. Actual logs,
source snapshots and binaries remain private. [assessment.json](assessment.json)
records the GoldHEN stage and [crashlog-assessment.json](crashlog-assessment.json)
records the `crash.log` stage and correction, without including raw logs.

## The two stages of the crash

### First: the original worker fault

The owner supplied `crash.log` from `/data/Dolphin`; the compiled logger path is
`/data/DolphinPS4`. It has 19 appended entries. 17 map to three worker loops, in
the exact ELF, at the first read of the received message:

| ELF instruction | Function and source | Entries | Fault address |
| --- | --- | --- | --- |
| `0x1629c` | `JKRAramStream::run()`, `JKRAramStream.cpp:46` | 5 | `0x0` |
| `0x19420` | `JKRDecomp::run()`, `JKRDecomp.cpp:42` | 7 | `0x8` |
| `0x29802` | `JUTException::run()`, `JUTException.cpp:110` | 5 | `0x0` |

The target build zeroes each local before the call (`-ftrivial-auto-var-init=zero`),
so a receive that delivers nothing leaves a null pointer. Which worker wakes first
varies, which explains the varying location.

The log is append-only with no timestamps or build identities, so its entries are
not attributed to individual attempts. Compatible addresses support, but do not
prove, that they came from this ELF. Entry 1 (signal 6) and entry 2 (no instruction
record) are not explained by this diagnosis. Entry 1's stack addresses do not
symbolize coherently against this ELF, so it is treated as an unattributed entry.

### Second: the fault GoldHEN reported

GoldHEN reports `SIGSEGV`, a user read of a non-present page, at runtime instruction
address `0xb46760`. The executable mapping starts at `0x400000`; the ELF's lowest
`PT_LOAD` virtual address and `__text_start` symbol are zero. Subtracting the load
bias gives ELF virtual address `0x746760`.

With the exact matching ELF selected as `ELF`, these commands reproduce the mapping:

```sh
sha256sum "$ELF"
llvm-addr2line-21 -C -f -i -e "$ELF" 0x746760 0x7467a6 0x7dcdd9 0x7dcdd8
llvm-objdump-21 -d --no-show-raw-insn --start-address=0x746754 --stop-address=0x7467a8 "$ELF"
```

The fault maps to `(anonymous namespace)::crashHandler(int, __siginfo*, void*)`,
`DolphinPS4/port/ps4_crashlog.cpp:119`. The instruction is
`movq (%r13,%r15,8), %rax`: a load from the stack being scanned. The captured
registers reproduce the reported fault address exactly:

```text
scan base 0x7ed4b7f20 + index 28 * 8 = 0x7ed4b8000
```

The scan stops at 2,048 words or 48 candidate addresses, with no readable-stack-bound
check, and ran off the mapped stack after 224 bytes. Entry 19 of `crash.log` is a
`JUTException::run()` fault with the same stack pointer, `0x7ed4b7f20`, and it lists
exactly the four code addresses the captured registers show the scan had found.
That links the two captures: the logger was handling that worker fault when it
crashed. The runtime address `0xbdcdd9` in the kernel backtrace
maps to `cos_sdk::os::ThreadEntry` (`OSThread.cpp:220`), the thread wrapper, and is
consistent with this but does not identify the failing callback by itself.

## Cause

`pswaker_exit` calls `COSSdkRequestShutdown()` immediately before the stage
`shutdown-sdk-stop-requested`, the last one recorded by the cold and warm runs
documented in the issue. That sets the shutdown flag and wakes
every sleeping thread. `SleepLocked` reports the shutdown wake, and blocking
`OSReceiveMessage` returns `FALSE` without writing the message. This is the SDK's
intended contract, and the port's GBA and display loops already honor it.

The original game's receive cannot fail, so its loops do not check the result. Five
long-lived loops are affected, in three different ways:

| Loop | Failed receive reads as | Visible in `crash.log` |
| --- | --- | --- |
| `JKRAramStream::run` | Null command: null read | Yes |
| `JKRDecomp::run` | Null command: null read | Yes |
| `JUTException::run` | Null callback object: null read | Yes |
| `JKRAram::run` | **The previous, already deleted message**: repeated `delete` and DMA dispatch | No |
| `TAudioThread::audioproc` | Zero, meaning "update the DAC": continuous mixing work | No |

The last two share the defect but not the null-read signature, because
`JKRAram::run` declares `message` outside its loop and `audioproc` treats zero as a
valid command. The 01.25 machine code of `JKRAram::run` confirms the unchecked
receive, the single zeroing before the loop, and the unconditional `delete`.
`JKRAram` is resumed at startup and receives every ARAM piece transfer.

A correction limited to the three logged loops would have left both running through
audio output shutdown, GPU synchronization and `aurora_shutdown`. Those are steps
no failed run has reached. Neither loop appearing in `crash.log` is not evidence
that they are safe: their inclusion rests on source, machine code and the host
reproduction, not on a console capture.

## Correction

`platform/ps4/patches/game/0015-worker-shutdown.patch` checks the receive result in
all five loops, under `__ORBIS__`, as `0009-gba-shutdown.patch` does for the GBA
threads. Four return from `run()`. `audioproc` calls `OSExitThread(0)`, its existing
stop path, rather than returning through the `JKRThread` destructor during teardown.

It does not change the crash logger. That defect is real, but fixing it would only
improve diagnostics, and it should be handled separately so that any later fault is
not hidden behind it again. Nothing here changes rendering quality, the 1280x720
target, 30 Hz logic, missing-pipeline behavior, saves or settings.

## Feedback loop

`tests/ps4/test_quit_workers.py` compiles the production loop bodies verbatim with
the real SDK queue, thread, alarm and shutdown code, using the target's zeroing flag.
It has seven scenarios: each loop alone, all five idle, and all five after processing
one real command. It stubs asset decoding, ARAM I/O, exception display, audio mixing
and class construction. Any DMA or DAC dispatch after shutdown aborts the scenario,
because none is pending by then.

```sh
python3 local-research/quit159-regression.py
```

```text
RED: all seven scenarios failed before correction ['-11', '-11', '-11', '-11', '-6', '-6', '-6']
RED: three-worker patch left piece, audio, idle and after-work failing ['-11', '-11', '-6', '-6']
GREEN: all seven individual, idle and post-command scenarios passed
PASS: all five full translation units compile with the PS4 target commands
```

The second line is the result that widened the patch. The first attempt covered
only the three logged loops and passed because the harness also covered only those
three. Against that build, the after-command scenario failed with glibc's
`free(): double free detected`, which is the stale `JKRAram` message.

The full PS4 suite then passed against the corrected prepared tree: 300 tests, no
failures, 70 skipped (log SHA-256
`dbddd698fc478ae0d7e99163949597b12a2dbb55337593a2fb9790771d2e9ff4`, retained
privately). The skips are environmental, including Windows-only packaging, Tk
desktop display and host SDL build requirements, so those paths were not exercised.

The host check establishes the failure mechanism for these loops. It does not
execute a PS4, GoldHEN, the port's shutdown sequence or a real worker's dependencies.

## Remaining limits

- One reported Quit reached `shutdown-complete`, which follows audio join, GPU
  synchronization and `aurora_shutdown`. Its logs have not been returned, so recorder
  completion and the stored cache state of that run are not yet established.
- `JASTaskThread::run` skips a null message, so it does no work on a failed receive,
  but it spins until the process exits. It is left unchanged. `mDoDvdThd`'s loop
  already ends on a failed receive.
- Waits for one in-flight operation (`JKRAramPiece::sync`, `JKRDecomp::sync`,
  `JKRAramStream` sync, `JKRDvdFile`, `JASResArcLoader`) and the movie-player queues
  are unchanged. They can only matter if that work is active at shutdown; the
  owner's route was not shown to depend on them, and Quit during a load or movie
  is untested.
- Cache state and preceding gameplay are not shown to matter, since the mechanism
  needs only idle workers, but this has not been confirmed on the console.

## Candidate 01.26

[candidate.json](candidate.json) records the identities. The package and ELF remain
private in artifact group `quit-candidate-159`.

| Item | Value |
| --- | --- |
| Program version | `01.26` |
| Build/cache ID | `be0a6ae04878271c6c1d` |
| Complete package SHA-256 | `91cc442d97551b5ec43745f6e4edff2c8a369b2170efe26a528b94f2ffa27714` |
| Matching ELF SHA-256 | `7adad72f20bf479c56eeca1b16da8d6c994c72b9a2536a7b803a8741cb060e8e` |
| Pipeline seed SHA-256 (same as 01.25) | `e61cb301a7debdb1ff91abee77cc252ba3e4b634beef75eb296ea02d1c5534e3` |

The package was assembled and passed a fresh inspection that reproduced the
assembly inspection. Disassembly of the matching ELF confirms all five loops test
the receive result. The only program change from 01.25 intended by this work is
the patch, but the build also records a host lock update for Ubuntu security
updates (.NET, `ca-certificates`, `libpcre2`). The compiler, linker, CMake and Ninja
are unchanged. The candidate was built from an uncommitted checkout, so its identity
binds file contents, not a commit.

## Console result

Reported by the owner on 2026-11-06 for this candidate: Quit completed without
error, and `last-stage.txt` contained:

```text
build=be0a6ae04878271c6c1d stage=shutdown-complete elapsed_ms=99224.9 checked_errors=0
```

The build ID matches the candidate. This is the owner's transcription of one
attempt; the file and accompanying logs have not been returned. It satisfies the
`CE-34878-0` and `shutdown-complete` criteria for that attempt only. The report does
not state whether the attempt used empty or retained caches, and does not cover
recorder drain/flush/close, card/settings handling or relaunch.

## Console acceptance

For this candidate, on the owner's PS4 Slim, firmware 9.00, GoldHEN v2.4b18, with
saves/settings preserved:

1. Confirm **Quit game** from the port menu, once with disposable caches empty and
   once with compatible caches retained, and observe no `CE-34878-0`.
2. Confirm `last-stage.txt` reaches `shutdown-complete` and the recorder records
   completed drain, flush and close.
3. Confirm pending card/settings work finishes safely, and that the game relaunches
   cleanly.
4. If it still fails, retrieve the entire `/data/DolphinPS4/crash.log` before
   relaunching, even if incomplete, with `/data/pswaker/logs/platform.log`,
   `platform.prev.log` and `last-stage.txt` from the same attempt. Note its
   existing entries first, or preserve and start from a clean copy, because the
   file appends without timestamps.

Host checks and fixing the secondary logger fault do not establish these outcomes.
