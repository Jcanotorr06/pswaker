# Building PSWaker from source

This guide builds everything a release contains, starting from a clean
checkout: the PS4 game program, the Windows packaging tools, the desktop app and
its installer. End users don't need any of this; they install a release and
follow the [README](README.md).

No step reads a disc image except creating a complete package, which is the
owner's job. Never put a disc image, extracted game files, keys or complete
packages inside the repository. The approved game icon and launch splash are
included in [assets/ps4](assets/ps4/README.md). Keep replacement artwork, private
provenance records and all build outputs outside git; use a private directory
such as `$HOME/pswaker-private` on Linux or `C:\private\pswaker-private` on Windows.

## Overview

| Step | Host | Command | Output |
| --- | --- | --- | --- |
| 1. PS4 platform | Linux / WSL2 | `clean-build.sh` | Verified platform root: SDK, Mesa, Dawn, SDL3, runtime, packager |
| 2. Game program | Linux / WSL2 | `build-game.sh` | Developer game build |
| 3. Program release | Linux / WSL2 | `complete-package.py release-program` | Relocatable, data-free program release |
| 4. Windows packaging tools | Windows x64 | `prepare-windows-tools.py` | Self-contained LibOrbisPkg tool closure |
| 5. Desktop app | Windows x64 | `build-desktop.py` | `PSWaker` app folder |
| 6. Installer | Windows x64 | `build-installer.py` | `PSWaker-<version>-win-x64-setup.exe` and its audit manifest |

Steps 1–3 run on Linux. Steps 4–6 run on Windows and take the program release
from step 3 as input. All commands run from the repository root. Every output
directory must be new.

## Linux: PS4 program

### Host

Use Ubuntu 24.04 x86-64, natively or in WSL2. The exact environment is locked in
[host.lock.json](platform/ps4/host.lock.json): 188 build-tool packages with
their versions, including Clang 21.1.8, LLVM runtimes 21.1.6 and .NET 8.

```bash
# Optional first-time provisioning on a matching Ubuntu installation, as root:
bash tools/pswaker/install-host.sh

# Rejects a different OS, architecture, tool or required package version:
python3 tools/pswaker/inputs.py host /tmp
```

Keep build roots on the Linux filesystem, with no spaces in their paths. The
inherited toolchain embeds paths in compiler flags. The repository itself may be
in a path with spaces.

### 1. Build the PS4 platform

```bash
PLATFORM_ROOT="$HOME/.cache/pswaker/platform"
bash tools/pswaker/clean-build.sh "$PLATFORM_ROOT"
python3 tools/pswaker/inspect-artifacts.py "$PLATFORM_ROOT"
```

This fetches every locked input, checks its hash and builds the SDK support,
graphics stack, runtime and the disc-free platform diagnostic. `JOBS=5` is the
default. The command stops at the first failed stage and keeps its evidence
directory. To reuse downloads from an earlier root, pass that root as a second
argument. For the full source closure, patches and checks, see the
[PS4 platform guide](docs/ps4/README.md).

### 2. Build the game program

```bash
GAME_ROOT="$HOME/.cache/pswaker/game"
ARTWORK_ROOT="$PWD/assets/ps4"
bash tools/pswaker/build-game.sh "$GAME_ROOT" "$PLATFORM_ROOT" 01.13 \
  "$ARTWORK_ROOT/icon0.png" "$ARTWORK_ROOT/splash_art.png"
```

The third argument is the console program version (`NN.NN`). It changes only
the package's version metadata; the application identity stays `PSWK00001` /
`IV0000-PSWK00001_00-PSWAKERGAME00000`. The build prepares pinned SwitchWaker
and the decompilation, applies the ordered patches, compiles the program and
stages it. The compiled build ID covers every input, so a different source,
patch or toolchain gives a different ID. See the
[installed-game guide](docs/ps4/GAME-STARTUP.md) for details.

A new build is a new binary. Console results recorded for another build ID don't
carry over to it.

Arguments four and five are required artwork paths. The command above uses the
approved images included in the checkout:

| Role | Package resource | Required dimensions |
| --- | --- | --- |
| Game icon (PS4 home screen and library) | `sce_sys/icon0.png` / `ICON0_PNG` | 512 x 512 |
| Launch splash (shell artwork until the first rendered frame) | `sce_sys/pic1.png` / `PIC1_PNG` | 1920 x 1080 |

Both files must fully decode as 24-bit opaque RGB PNGs (8 bits per channel),
non-interlaced, with no alpha channel or `tRNS` transparency. Indexed, grayscale
and RGBA images are rejected. The build copies their bytes unchanged without
resizing, cropping or conversion, then freshly inspects the program package.
Missing or invalid artwork stops packaging; there is no fallback.

The included images have a recorded
[redistribution approval](docs/RELEASING.md#artwork-redistribution-blocker), so
building with them needs no private artwork or provenance setup. To use different
artwork, supply prepared files from a private directory outside git and record
their origin and provenance there before staging. See
[owner artwork](docs/ps4/OWNER-ARTWORK.md) for replacement artwork, the restaging
command, packaging evidence and existing splash handoff. Local use does not
grant permission to commit or redistribute replacement images.

### 3. Derive a program release

```bash
python3 tools/pswaker/complete-package.py release-program \
  --platform-root "$PLATFORM_ROOT" \
  --program-stage "$GAME_ROOT/build/program-stage" \
  --elf "$GAME_ROOT/build/switchwaker" --kind game \
  --output "$HOME/pswaker-private/program-release"
```

The program release is a data-free directory: the staged program, its matching
ELF and `program-release.json`. It can be copied anywhere, including to the
Windows machine for steps 4–6. See
[relocatable program release](docs/ps4/COMPLETE-PACKAGES.md#relocatable-program-release).

A game program release carries both owner-supplied images alongside the
disc-free program. Complete-package assembly carries them forward from the
selected stage or release; it does not take a second artwork selection. Match
both artwork hashes against the
[approved redistribution decision](docs/RELEASING.md#artwork-redistribution-blocker).
Different artwork remains private pending a separate decision. The release's
public-readiness gate still applies.

Optionally, assemble and inspect a complete package on Linux with your own disc
image, as described in [complete packages](docs/ps4/COMPLETE-PACKAGES.md).

## Windows: desktop app and installer

### Prerequisites

On Windows x64, install:

- **CPython 3.12** with Tcl/Tk. Then run
  `python -m pip install -r tools/pswaker/desktop-requirements.txt`, which pins
  PyInstaller 6.22.3.
- **.NET SDK 8.0.427**, used only to publish the packaging tools.
- **Inno Setup 6.7.3**, only for the installer. Get it from
  [Inno Setup's official downloads](https://jrsoftware.org/isdl.php) and check
  its publisher signature and record the archive's identity. The build rejects
  any other compiler version. CI additionally checks the pinned download's
  SHA-256 before installing it.

Users of the built app need none of these.

### 4–6. Build the tools, app and installer

```powershell
python -m pip install -r tools/pswaker/desktop-requirements.txt
python tools/pswaker/prepare-windows-tools.py --dotnet C:\maintainer\dotnet\dotnet.exe --output C:\private\windows-tools
python tools/pswaker/build-desktop.py --program C:\private\program-release --packaging C:\private\windows-tools --app-version 0.1.0.1 --output C:\private\desktop-build
python tools/pswaker/build-installer.py --program C:\private\program-release --packaging C:\private\windows-tools --app-version 0.1.0.1 --iscc 'C:\maintainer\Inno Setup 6\ISCC.exe' --output C:\private\installer-0.1.0.1
```

- `prepare-windows-tools.py` fetches the pinned LibOrbisPkg archive, checks its
  SHA-256, retargets it from net6.0 to net8.0 and publishes a self-contained
  Windows x64 build. This is the only step that needs the network.
- `build-desktop.py` bundles the program release, the tools and the production
  content contract into a `PSWaker` folder with a hash inventory. Keep the whole
  folder together, including `_internal` and `application-release.json`.
- `build-installer.py` builds the same bundle and compiles a per-user installer.
  Its output folder holds the setup executable and `installer-release.json`,
  which records the installer SHA-256, app version, full file inventories,
  Python/PyInstaller versions, recipe digest and compiler inventory. Keep both
  files privately for audit and acceptance.

No step reads a disc image; the builders seal only the data-free program, tool
and contract inventories, and reject any other program files.

The desktop app folder, portable zip and Windows installer bundle the program
release's artwork. Keep them and their audit manifests outside git. The
[artwork redistribution decision](docs/RELEASING.md#artwork-redistribution-blocker)
permits redistribution when both artwork hashes match its approval; otherwise,
keep them private pending a separate decision. A passing inventory or installer
check does not grant redistribution permission or clear the public-readiness
gate.

App versions have four numeric parts, each 0–65535. Give every desktop build
you hand out a new version. The desktop version is independent of the console
program version. Both executables embed
[waker.ico](tools/pswaker/waker.ico). Release builds follow the version scheme
in [RELEASING.md](docs/RELEASING.md).

To check an installed copy without changing it, run the installed
`PSWaker.exe --check-installation C:\private\new-installation-report.json`.
It returns zero and writes a new identity report only when the whole installed
app matches its inventory.

For the bundle's integrity rules and what the hash inventories do and don't
prove, see [content and release integrity](docs/desktop/README.md#content-and-release-integrity).

## Checks

The Linux and Windows test commands, including the environment variables the
Windows suites need, are in [CONTRIBUTING.md](CONTRIBUTING.md#checks).
