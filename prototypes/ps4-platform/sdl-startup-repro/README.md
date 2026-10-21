# SDL startup reproduction (host only)

This throwaway regression harness compiles the locked, patched SDL source for the
Linux host with the console build's video choices: desktop/Vulkan/OpenGL backends
disabled, dummy and offscreen enabled. It invokes the same SDL video/events startup
and external-context placeholder-window pattern used by Aurora. It does not execute
PS4 code, Aurora, Dawn, Mesa, audio or a real display surface.

```bash
ROOT=/home/joseph_cano/.cache/pswaker/startup-20261021
bash prototypes/ps4-platform/sdl-startup-repro/build.sh "$ROOT"
bash prototypes/ps4-platform/sdl-startup-repro/check.sh "$ROOT"
```

The check requires the original automatic-selection path to fail specifically with
`No available video device`, then requires the candidate path to initialize and
create a 1920x1080 external-context window with driver `dummy`. The candidate calls
the same [configuration helper](../probe/sdl-video.hpp) as the console diagnostic.
Both outputs are recorded under the prepared root's `evidence/` directory. Building
is separate so repeat checks take seconds.

The selected PS4 publication already selects SDL's dummy driver in its application
entry point (`dusklight-ps4.patch`, PS4 main), while Aurora's PS4 BackendBinding
creates a Dawn `SurfaceSourceDirectDisplay`. The initial standalone diagnostic
omitted that application-level SDL setting. The dummy SDL driver itself requires
an explicit hint and returns no device without it. This harness checks that failure
and the setting; it cannot certify a fix for the owner's PS4 crash.
