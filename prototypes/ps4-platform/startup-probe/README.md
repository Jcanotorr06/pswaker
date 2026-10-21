# Startup failure isolation — temporary diagnostic

The owner reported that the original build `97fc99208640c483fdc2` showed a black
screen for about ten seconds, no sound, then `CE-34878-0`, with no files in either
`/data/pswaker-diagnostic-prototype/` or `/data/DolphinPS4/`. Firmware and GoldHEN
were unchanged: PS4 Slim, 9.00, GoldHEN v2.4b18.

That is a failed hardware run. Its cause is **unknown**. WSL2 cannot reproduce
the actual PS4 launch. We are building the console feedback loop, not declaring
a root cause or a fix from compilation. The old full diagnostic package is retained.

## Short owner retry

Install **PSWaker Startup Probe**, title ID `PSWK00011`, version `01.00`, alongside
the original `PSWK00010` diagnostic. Check this probe's `artifacts.json` for its
build ID and package SHA-256. No firmware/homebrew change is required.

1. Launch **PSWaker Startup Probe** once. **Black screen and silence are expected**
   in this small probe. It has no graphics/audio initialization. After the runtime
   preflight it waits about 30 seconds and returns from `main`.
2. Observe up to 60 seconds. Record whether it crashes, returns normally, or stays
   open, the elapsed time and any error code. Close it manually if still open.
3. Retrieve these through the existing FTP workflow, before another launch:
   - `/data/pswaker-startup-probe/entry.log`
   - `/data/pswaker-startup-probe.log` (independent fallback)
   - Any files under `/data/pswaker-startup-probe/`, including runtime-preflight log
     and scratch state.
   - Any newly created files under `/data/DolphinPS4/`.
4. Return the outcome and files, or explicitly report which files/directories are
   absent. No need to repeat the three ten-minute graphics runs yet.

Expected entry stages: `ENTRY before __libc_start_main` with build ID,
`CONSTRUCTOR priority=102 reached`, `MAIN`, `PREFLIGHT PASS` or `FAIL`, `WAIT`,
then `RETURN from main`. A `RETURN` marker alone does not establish clean shutdown;
the owner must report the shell outcome. Primary-write status is recorded in the
fallback. A nonzero `mkdir` status may just mean the directory already exists.

The first breadcrumb uses only direct kernel imports, stack data and literal
strings. It runs before the selected CRT's `__libc_start_main` handoff. The CRT's
process parameters, malloc replacement table, runtime implementation and package
authority/SFO style stay selected as before. Constructor and runtime checkpoints
are later boundaries. Failure before the first breadcrumb remains possible;
absence of a file is not proof that the entry point was never reached.

This probe removes Aurora/Dawn/Mesa/SDL and their startup work to narrow the
measurement. It does not replace the selected architecture, exercise the full
binary's initialization, or establish that the original crash is fixed. Even a
complete successful startup-probe run leaves the original diagnostic gate open.
All `[DEBUG-pswaker-startup]` instrumentation is deliberately isolated here and
must be removed when the failure is understood, or kept only in this marked
throwaway location.

## Structured observation capture

The retry loop follows `diagnosing-bugs/scripts/hitl-loop.template.sh`. The human
performs the console steps; it does not claim unattended PS4 access. From WSL:

```bash
bash prototypes/ps4-platform/startup-probe/retry.sh startup /path/to/local/results
```

It writes `observation.json`. Use `full` for the original binary. Adding
`--record-existing` records an already observed run without repeating it; that
mode must not be presented as a new reproduction. The classifier reports the exact
original crash/no-log symptom as red; all other outcomes require review, including
a successful small probe. There is no automatic “original bug fixed” verdict.

## Host preparation and checks

The earlier `/tmp` build roots disappeared across the WSL restart. Re-fetch locked
SDK/source inputs and rebuild selected runtimes in a persistent cache directory,
using `lock-sdk.py fetch`, `prepare-sources.py`, `adapt-platform.py` and
`build-runtime.sh` from the parent directory. Then:

```bash
python3 prototypes/ps4-platform/startup-probe/build.py /path/to/prepared/root
```

The builder verifies that the early logger imports only its six allowed kernel
functions, inspects the linked entry hook, applies the selected OELF segment check,
extracts the produced package, and verifies payload identity, inventory and SFO.
These checks validate the host artifact and instrumentation placement. They do not
validate the early kernel calls on this console or reproduce `CE-34878-0`.

Native open flags follow [FreeBSD's native definitions](https://github.com/freebsd/freebsd-src/blob/releng/9.0/sys/sys/fcntl.h),
rather than musl-facing header flags. Calls use the selected SDK's declarations;
the [OpenOrbis libkernel documentation](https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/master/docs/MD/PS4%20Libraries/Libkernel.md)
describes its role as the native syscall wrapper library. No kernel changes are
made. Original source/SDK notice and provenance limits still apply to local packages.
