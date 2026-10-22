# Throwaway Aurora boundary reproduction

This uses the selected, already extracted Aurora/Dawn/SDL source pins. It builds
separate **Linux** libraries and runs the diagnostic's GX triangle, frame,
EFB/offscreen resolve and readback calls through Vulkan software rendering.
It does not execute the PS4 binary, Mesa's PS4 driver, direct-display surface,
audio, input or persistence. A local result cannot clear the Slim hardware gate.

`baseline-scene.hpp` preserves the triangle function from the failed diagnostic
revision `605d57a581e3657ce4a485140f17552b1c6119d2`. The reproduction checks all
1024 pixels in each 32x32 white region, reports mapping status separately from
pixel mismatch, and prints the actual texture dimensions and format.

On the recorded Ubuntu/WSL2 host, install X11 development libraries, Xvfb and the
Vulkan loader/development files. The existing locked platform root must already
contain the fetched Dawn dependencies and the diagnostic's CMake dependency
sources. No target libraries are reused by the host build.

```bash
bash prototypes/ps4-platform/aurora-repro/build.sh \
  /home/joseph_cano/.cache/pswaker/startup-20261021 \
  /home/joseph_cano/.cache/pswaker/aurora-host-20261022
bash prototypes/ps4-platform/aurora-repro/run.sh \
  /home/joseph_cano/.cache/pswaker/aurora-host-20261022
```

The run uses Xvfb and the host's installed lavapipe ICD, with a 30-second timeout.
It opens no interactive desktop window. The input sources are pinned; the host
ICD and native Linux ABI are distinct from the selected console build. Dawn is
compiled without host optimization to keep this diagnostic build inexpensive;
no timing or performance claim is made.
