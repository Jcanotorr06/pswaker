# First console failure and startup feedback loop

**Superseded by retrieved console logs:** the owner subsequently supplied files
showing successful runtime preflight and an SDL video initialization failure.
See the [current investigation](../sdl-video-20261021/status.md). This historical
no-output assumption and proposed startup-only retry are no longer the next step.

The owner reported on 2026-10-21: installed original build `97fc99208640c483fdc2`,
black screen for about ten seconds, no sound, crash `CE-34878-0`, no emitted logs.
In the follow-up, the owner confirmed no console/firmware/GoldHEN changes and that
both documented directories had been checked. This fails the diagnostic hardware
gate. The crash's cause remains unknown. Do not treat it as proof that the chosen
stack is impossible or silently substitute another architecture.

The [structured observation](owner-baseline/observation.json) was captured with:

```text
bash prototypes/ps4-platform/startup-probe/retry.sh full \
  prototypes/ps4-platform/evidence/startup-20261021/owner-baseline --record-existing
RED_REPORTED: .../owner-baseline/observation.json
This records observations; it is not an unattended console test or a proof of a fix.
```

Answers came from the owner's two messages. This invocation classifies the already
reported failure; it does not execute the app or constitute a fresh reproduction.
No unattended console access is available. Diagnosis is still establishing the
feedback loop and has not advanced to a verified root-cause hypothesis or fix.

## Prepared measurement

The isolated [startup probe](../../startup-probe/README.md) retains the selected
SDK, modern libc++/ABI runtime, process parameters, malloc replacement and package
authority/SFO path, with an early kernel-only breadcrumb hook. It omits the full
graphics/audio stack. This is a measurement/minimization aid, not a corrected full
diagnostic or substitute architecture. A pass does not establish that the original
binary's startup or any graphics gate works.

The earlier `/tmp` roots had disappeared across a WSL restart. Locked SDK/source
archives were fetched and digest-verified again into persistent host cache
`/home/joseph_cano/.cache/pswaker/startup-20261021`, and the selected runtimes were
rebuilt. The startup package then compiled and passed its host inspection. An
initial inspection filename error was corrected: the selected packaging script
truncates the content label to sixteen characters; the final label is exactly
`PSWAKERSTARTUP01`. That host-script error is unrelated to the console crash.

Final startup build: `1a43c6a7cd47a32a0a3d`, title `PSWaker Startup Probe`,
title ID `PSWK00011`, version `01.00`.

Local package:
`C:\Users\Joseph Cano\Code\pswaker\local-research\diagnostic-artifacts\startup-probe\PSWaker-Startup-Probe.pkg`

SHA-256: `9d7473867e2cb0ad53d1de30cc9683bb2e1ea5626b6f6c9cff79b2a3addf9cb0`.

The copied Windows package hash matches. Matching unstripped ELF, hashes, input
manifest and checklist are retained beside it. No binary is pushed to GitHub.

## Host checks completed

- Selected SELF/OELF segment check passed.
- `early.c` object imports exactly the six intended kernel functions, with no heap,
  stdio or TLS dependency introduced by that object.
- Linked `_start` disassembly calls the breadcrumb hook before the selected
  `_start_ps4_c` / `__libc_start_main` handoff; it preserves the argument pointer,
  incoming stack and callee-saved register it uses.
- Extracted PKG payload matches the built SELF and manifest. Exact file inventory,
  compiled identity and extracted SFO title ID/version/category were checked.
- `retry.sh` parsed successfully and recorded the owner's baseline as red, with
  the explicit reported-observation distinction above.

These are host-artifact checks. Native logging before CRT initialization has not
been tested on the PS4. A missing entry file remains ambiguous and is not proof
that execution never reached the entry point. No regression test currently reaches
the actual console-only failure from this host, so none is claimed.

## Next owner result required

One short startup-probe launch, up to sixty seconds, followed by the shell outcome
and retrieved entry/fallback/runtime files. Black screen and silence are expected
for this small probe; it waits about thirty seconds after runtime checks and
returns from `main`. Report a crash/error code, normal return, or continued running.
Retrieve any new inherited `/data/DolphinPS4/` files too.

Keep [Test the candidate PS4 platform with a disc-free diagnostic prototype](https://github.com/Jcanotorr06/pswaker/issues/10)
open and final specification approval blocked. The original known-result graphics,
three cold/warm ten-minute runs, audio, controller, resource and retrieval gates
still need to pass after startup is understood.
