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
  /home/joseph_cano/.cache/pswaker/aurora-host-20261022 baseline
# The differential regression expects failed baselines and a passing correction:
bash prototypes/ps4-platform/aurora-repro/check.sh \
  /home/joseph_cano/.cache/pswaker/aurora-host-20261022
```

The run uses Xvfb and the host's installed lavapipe ICD, with a 30-second timeout.
It opens no interactive desktop window. The input sources are pinned; the host
ICD and native Linux ABI are distinct from the selected console build. Dawn is
compiled without host optimization to keep this diagnostic build inexpensive;
no timing or performance claim is made.

Every run creates a separate disposable data/cache directory under the host build
root's `runs/`; no previous pipeline cache can disguise a first-frame result.
`corrected` calls the same setup, draw, pipeline preparation, exact-white checker
and GPU-drain helpers as the full PS4 diagnostic. Its 30 frames must all pass,
including the first checked frame. `check-source.py` verifies that the shared draw
is identical to the failed baseline's draw; the change is its setup and sizing.

The differential variants change explicit draining, sizing, initialization and
alpha mode in sequence. `baseline`, `repeat` and `drain` retain black results;
`scale` fixes only size; `initialize-repeat` produces white RGB with offscreen
alpha zero; `alpha` fixes those pixels but retains the wrong size; `corrected`
passes the full local loop. Pipeline preparation is separately bounded at 30
seconds and waits on Aurora's queue counter, rather than retrying pixel checks
until they happen to pass.

The recorded host setup additionally installed `libx11-dev`, `libxext-dev`,
`libxrandr-dev`, `libxcursor-dev`, `libxi-dev`, `libxfixes-dev`, `libxss-dev`,
`libxtst-dev`, `libxinerama-dev`, `libxkbcommon-dev`, `libx11-xcb-dev`,
`libxcb-randr0-dev`, `xvfb` and `libvulkan-dev`. Aurora's `allowCpuAdapter` is
enabled only here. The preliminary Aurora compilation used already generated
Dawn API headers; their hashes match the finished Linux generation exactly.
No PS4 object library is linked into the Linux executable.
