# Throwaway PS4 platform diagnostic

Evidence for [Test the candidate PS4 platform with a disc-free diagnostic prototype](https://github.com/Jcanotorr06/pswaker/issues/10).
This branch is a disposable prototype, not a game port or a merge candidate.
No game data, game code, disc reader, keys or PS5 binary libraries are used.

## What the owner runs

Install the prepared **PSWaker Platform Diagnostic** package through the existing
USB package installer. Its title ID is `PSWK00010`, version `01.00`.
The package filename, build identity and SHA-256 are recorded in the build evidence.
Use the package associated with the clean-build comparison, not an exploratory build.

Confirm that the console is still the PS4 Slim on firmware 9.00 with GoldHEN
v2.4b18, or report the actual versions before comparing results.

Run the following sequence, recording the displayed build identity and any error:

1. **Cold cache:** before the first run, use FTP to remove only
   `/data/pswaker-diagnostic-prototype/cache` if it already exists. Keep the other
   prototype files. The program recreates this cache directory.
2. Launch the diagnostic. Expect a white background, an RGB triangle, a purple
   swatch, a text summary, and a continuous quiet 440 Hz tone. Record any missing
   element, visual corruption, crackling, interruptions, hang or error display.
3. Let the displayed loop run for at least **600 seconds**. Once during the run,
   hold a direction/button, disconnect the controller, then reconnect it. The raw
   inputs should become neutral while disconnected. After reconnecting, release
   Cross, then press Cross deliberately to resume. Record the disconnect and
   reconnect counters and any stale inputs.
4. Once the loop is complete, release and press Options to close. Also fully
   close the application from the PS4 shell if it remains open.
5. Retrieve the files listed below through FTP **before the next run**. Keep a
   copy identified by cold/warm run and build. Report whether file retrieval
   worked. A successful install or picture alone is insufficient.
6. **Warm cache:** launch twice more, each time repeating the ten-minute loop,
   controller check, complete close and evidence retrieval. Retain the cache
   between these two runs. The preflight state counter must increase, and each
   later runtime log must report a successful previous-launch state check.

If the app fails to launch or exits early, report the PS4 error code and retrieve
whatever evidence exists. Do not treat the lack of a log as a pass. A photo/video
is useful when the visible or audible result is wrong.

## Evidence to retrieve

From `/data/pswaker-diagnostic-prototype/`:

- `diagnostic.log`: appended runs, build/input identity, stages, GPU comparisons,
  memory observations, pad transitions and final counters.
- `runtime-preflight.log`: constructor, thread/TLS/once, synchronization,
  atomic wait/notify and writable-file replacement results.
- `preflight-state.txt`: persistent launch counter; keep it between runs.
- `platform.log` and `platform.prev.log`: inherited native platform/Dawn/Mesa output.

If a crash happens before the prototype log opens, the inherited runtime may
also leave files under `/data/DolphinPS4/`. Retrieve those if present, without
assuming that they are a crash dump. The source runtime's paths are retained.
No useful crash dump has been established yet.

Review `RESOURCE` lines separately for each run. They measure driver garlic/onion
buffer bytes and counts, main-mspace allocated bytes, heap capacity and available
flexible memory. Main-mspace usage includes reserved thread arenas; it does not
measure every live allocation inside those arenas. These are observations to
review for steady growth, not an automatic leak-free certification.

## Checks and limits

The synthetic WebGPU test samples a red texel with alpha 128 over opaque blue,
then draws a farther copy that must fail depth. It copies the result and maps a
staging buffer asynchronously. Every pixel must be approximately `(128,0,127,255)`;
a broken depth test would blend twice and change the result. Targets and pipelines
are recreated periodically.

Aurora creates its actual requested adapter/device. Its GX pipeline draws known
white geometry to the EFB and to a separate offscreen pass. Resolved snapshots
are read back asynchronously after render-worker submission; their checked region
must be white. The RGB triangle and textured ImGui swatch also exercise repeated
presentation. Internal rendering is requested at 1280x720, separately from the
1920x1080 display surface; inspect the recorded actual settings and WSI mode.

Audio uses the selected SDL3 SceAudioOut backend with synthetic 48 kHz stereo
samples. API errors and source-frame counts are recorded; these are not hardware
underrun counters. The owner must judge audible continuity and pacing. This does
not test game DSP, game saves or game performance.

The runtime/file checks do not establish power-loss durability or preservation
across a package update. This prototype has no game-specific controller mapping
or gameplay pause state. It checks neutral failed reads and a deliberate reconnect
acknowledgment; later game behavior still needs its own validation.

## Reproduce on the recorded Ubuntu/WSL2 host

The host setup installs Clang/LLVM 21 from the signed LLVM repository and .NET 8
plus build prerequisites from Ubuntu. `install-host.sh` checks the LLVM signing
key fingerprint. Actual package/tool versions are captured with each build; the
setup script is not an independently pinned OS image.

```bash
# First-time host provisioning, as root:
bash prototypes/ps4-platform/install-host.sh

# Fresh builds as the normal user. Each destination must not already exist.
# The cache is a previous fetch/build root containing downloads/, not target libraries.
bash prototypes/ps4-platform/clean-build.sh /tmp/pswaker-clean-a /tmp/pswaker-diagnostic-build
bash prototypes/ps4-platform/clean-build.sh /tmp/pswaker-clean-b /tmp/pswaker-diagnostic-build
```

`sdk.lock.json` fixes all 14 package filenames and hashes; it is used for fetching
without consulting the live package database. `sources.lock.json` fixes fetched
platform archives at the selected commits. `prepare-graphics.sh` checks Mesa and
libdrm commits. Dawn's pinned DEPS and hashed CMake downloads complete the source
closure; `input-closure.json` records what was actually fetched.

SDK `.PKGINFO`/`.BUILDINFO` records are preserved. Package versions and archive
hashes do not by themselves identify the exact source commit of every SDK binary;
unreported source revisions remain explicit in the lock. The current host package
inventory is recorded, not a claim that a fresh OS can recover every package forever.

Each fresh build compiles its own LLVM runtimes, SDL, Dawn, Mesa, Aurora, diagnostic
and patched LibOrbisPkg. Only verified download inputs are copied from the cache.
The selected ELF -> SELF -> GP4 -> PKG path is retained. Its two SDK sample `.prx`
modules and `right.sprx` are inherited packaging inputs; their exact archive hashes
are fixed by the SDK lock. No external private module directory is used.

`adapt-platform.py` emits an ordered local patch record for Jaguar/TLS flags,
diagnostic heap measurement, neutral disconnected reads and the packaging-tool
override missing from the published script. The reconstructed root `ps4.cmake`
selects the public modern ABI/sysroot, FreeBSD platform and patched Abseil.
Tracy remains disabled through the reference's header-only arrangement.

Source and dependency notices must be retained. The native platform files preserve
their MIT notices; downloaded trees preserve their original licenses. The selected
stack's unresolved SDK/sample-module notice questions still apply before public
binary distribution. Prepared packages are local test artifacts for the owner.
