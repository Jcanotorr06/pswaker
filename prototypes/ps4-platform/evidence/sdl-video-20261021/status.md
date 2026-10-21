# SDL video startup failure and candidate correction

The owner reports build `97fc99208640c483fdc2`: black screen for about ten seconds,
silence, then `CE-34878-0`. Supplied files are recorded by original SHA-256 in
[owner/retrieved-files.json](owner/retrieved-files.json); the useful non-manifest
[startup trace](owner/diagnostic-stages.log) and runtime/platform/state files are
preserved beside it. The original transferred files remain unchanged locally.
The [baseline inspection](baseline-inspection.json) verifies the original local
ELF's hash, matches the build ID from the supplied trace, and confirms both dummy
and offscreen bootstraps are actually linked into that ELF.
The existing HITL recording script captures the report as `RED_REPORTED`, expressly
not an unattended launch or a newly executed reproduction. Its former no-files
requirement was removed: a black/silent crash is still a failure when logs exist.

## Observed boundary

The constructor, TLS isolation/destruction, pthread-once, condition variable,
atomic-wait and file replacement checks all report PASS, ending with
`failures=0 launch=1`. The full diagnostic reaches `aurora-initialize`, then logs:

```text
Error initializing SDL: No available video device
Error initializing window
```

Aurora's fatal message reaches the diagnostic logger, which calls `abort()`.
That is a source-and-log explanation for the observed termination; no PS4 crash
dump or instruction-pointer evidence was supplied. Nothing establishes successful
adapter/device creation, rendering or audio. A written first-launch state exists;
persistence across relaunch remains untested.
Useful stage/runtime files have now been recovered from a failed hardware run;
the earlier absence-of-logs assumption is superseded. Evidence retrieval still
needs to be preserved for each later acceptance run.

## Reproduction and hypotheses

The actual console cannot be run unattended from this host. The exact full PS4
crash/black-screen/audio symptom therefore remains a HITL check. The supplied
trace permits a smaller host loop at the actual failing SDL boundary, rather than
waiting on another blind console launch. Phases requiring a full console replay
are deferred, not declared complete.

Ranked predictions shared before testing: (1) available placeholder backends need
explicit selection; (2) an intended backend is present but fails its initialization;
(3) a hint/environment override selects an unavailable backend.

The [host reproduction](../../sdl-startup-repro/README.md) builds the same locked,
patched SDL source with the console's video choices. Its original automatic path
reproduced the exact logged `No available video device` error. Explicit dummy
selection made SDL initialization and a 1920x1080 external-context placeholder
window succeed. The retained regression's candidate invokes the same configuration
helper as the full diagnostic. It does not execute a PS4 surface or prove the full
console crash fixed.

The Linux-host variant additionally lists an evdev placeholder; it does not supply
an automatically available display backend. The original target build's logs and
ELF bootstrap inspection establish the target configuration separately. This is a
bounded SDL-boundary reproduction, not native PS4-binary execution on Linux.

The selected publication already provides the missing contract:
`dusklight-ps4.patch`, PS4 application entry point, explicitly sets
`SDL_VIDEODRIVER=dummy`. SDL's `DUMMY_Available` deliberately returns false without
that hint; the compiled offscreen backend also requires selection. Aurora's PS4
`BackendBinding.cpp` creates Dawn `SurfaceSourceDirectDisplay` using the SDL window
dimensions. The standalone diagnostic copied the platform adapter but omitted the
application entry point's SDL video setting. This supports hypothesis (1).

## Candidate behavior

Before Aurora initialization, the diagnostic now explicitly selects `dummy` using
a checked SDL hint. It lists the compiled drivers and, after initialization,
records the active driver. These are permanent diagnostic stage observations,
not temporary debug logging. Native graphics still use the selected matched
Dawn/Mesa/Aurora stack. The SDL placeholder is not a rendering substitute.

The retry package uses title ID `PSWK00010`, version **01.01**, to distinguish it
from the failed 01.00 baseline. The original local package remains available.
Packaging records and checks the requested SFO version. The original two-clean-
directory comparison applies only to the earlier baseline; this retry is one
incremental candidate build on the recorded persistent cache, reusing the selected
runtime and freshly compiling the graphics libraries. No new clean-build-pair or
byte-reproducibility claim is made.

## Owner retry

Candidate built and inspected on the WSL2 host, completed 2026-10-21 21:55:41 UTC:

| Field | Value |
| --- | --- |
| Version / title ID | `01.01` / `PSWK00010` |
| Build ID | `3a73181f6dfdb86ca4b4` |
| Frozen diagnostic source | `c27246da9f0cac05cd84e28336968824db10d72f` |
| PKG SHA-256 | `6544219acf0beed6a64361f2839721c06b06b9168c82fbd388bcdcb9b1ec9080` |
| SELF SHA-256 | `798188ed7cc04535d06dfdcbf0399f591c3c8fb4a4dcdf7d65d27d3f9775e549` |
| ELF SHA-256 | `0d4cd39b72998fc57e0fa2627262cfacc5a3b8849b4e1df38c78195617d82c5e` |

Local package:
`C:\Users\Joseph Cano\Code\pswaker\local-research\diagnostic-artifacts\sdl-video-fix\PSWaker-Platform-Diagnostic-01.01.pkg`.
The matching ELF, hashes, manifest and `Retry-checklist.md` are beside it. The copied
Windows package hash was checked. Only source/evidence is published on the branch.

The known-failing host SDL path and shared-helper candidate both produced their
required differential outcomes. Native SDL, Dawn, Mesa, Aurora and the probe built;
the SELF/OELF segment check passed. `inspect-candidate.py` checked the package's
eight-file inventory, SFO version/title/category, extracted executable hash,
compiled build identity and new SDL checkpoints. Build logs, input closure and
inspection records (including cached runtime archive hashes) are under [host/](host/).
These are host checks; no version 01.01 console result exists yet.

Install the version 01.01 full diagnostic through the existing USB workflow.
Confirm the actual firmware/GoldHEN baseline. Clear only its disposable cache for
the cold-cache run, preserving test state and prior log copies. Observe startup
for a minute; retrieve the new files immediately if it fails. If the expected
visuals and tone appear, continue the [full checklist](../../README.md).

Look for `PASS SDL-dummy-video-selected`, `SDL_VIDEO active=dummy`, then the next
Aurora/device/graphics stages. If startup still fails, the final stage/error tells
us whether this SDL boundary was crossed. The original three ten-minute cold/warm
runs, controller/audio/persistence/resource checks and retrieval gates remain.
The diagnostic log appends runs: use the most recent `BEGIN build=...` matching
the retry package's `artifacts.json`, preserving earlier evidence too.

[Test the candidate PS4 platform with a disc-free diagnostic prototype](https://github.com/Jcanotorr06/pswaker/issues/10)
remains open. Host reproduction and packaging are evidence for this specific
candidate correction, not hardware acceptance or final specification approval.
