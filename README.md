# PSWaker

A PS4 homebrew port of *The Legend of Zelda: The Wind Waker* (GameCube), built
from your own disc.

PSWaker runs the game natively on the PS4. It compiles
[SwitchWaker](https://github.com/centollOS/SwitchWaker), which builds the
[Wind Waker decompilation](https://github.com/zeldaret/tww) and draws it with
[Aurora](https://github.com/encounter/aurora), for the PS4. A Windows desktop
app combines the prebuilt PS4 program with your own disc image to create a
**complete package** (`.pkg`). You then install the package on a PS4 running
GoldHEN.

The repository and its releases contain no game data, disc images or keys.

## Project status

PSWaker is **early and pre-release**. The first release candidate, 0.1.0 RC1,
is a private pre-release for testing. It is not a public or final release.

- The game has been played on the console from the title screen through
  Outset, Forsaken Fortress and Windfall to Dragon Roost Island. No graphics or
  audio glitches were observed during that run.
- Saves and settings survive a full relaunch and an update to a newer package.
- Controls use a fixed DualShock 4 mapping with PlayStation-style menus.
- Final console acceptance of the bundled program, PS4 testing of packages
  created by the desktop app and clean-system Windows testing are still pending.

The full checkpoint history with links to its evidence is in
[docs/STATUS.md](docs/STATUS.md).

## Tested platform

Nothing else has been tested. Other PS4 models, firmware versions and GoldHEN
versions may not work.

| | Tested |
| --- | --- |
| Console | PS4 Slim, firmware 9.00, GoldHEN v2.4b18 |
| Game disc | USA *The Wind Waker*, `GZLE01`, revision 0 |
| PC | Windows 11 Pro x64, build 26200 (the development machine, not a clean system) |

## Requirements

To create a package:

- **Windows 10 or Windows 11, x64.** Administrator access, Python, .NET and a
  network connection are not needed. ARM64 and 32-bit Windows are not
  supported.
- **Your own disc image.** Dump your own USA *The Wind Waker* disc (`GZLE01`,
  revision 0) as a full raw `.iso` or `.gcm` of exactly 1,459,978,240 bytes.
  See Dolphin's [guide to dumping games](https://dolphin-emu.org/docs/guides/ripping-games/).
  Scrubbed, trimmed and compressed images (RVZ, CISO, WBFS and similar) are
  rejected, as are other regions and revisions.
- **Free disk space on the output drive.** The app checks this before it starts
  and tells you if there isn't enough.

To play:

- **A PS4 running [GoldHEN](https://github.com/GoldHEN/GoldHEN).** This project
  does not explain how to prepare the console.
- **A USB drive** formatted as exFAT (or FAT32 for files under 4 GB) to copy the
  package to the console.
- **A DualShock 4 controller.**

## Creating a package

1. **Install PSWaker.** Run `PSWaker-<version>-win-x64-setup.exe` from the
   release. It installs for your account only, under
   `%LOCALAPPDATA%\Programs\PSWaker`. Alternatively, extract the portable
   `.zip` and keep the whole `PSWaker` folder together. The executables are not
   code-signed, so Windows SmartScreen may warn before the first run.
2. **Open PSWaker** from the Start menu, or run `PSWaker.exe` from the portable
   folder.
3. **Select your disc image** and a **parent folder** for the output. PSWaker
   creates a new `PSWaker-NN.NN` folder inside the parent folder.
4. Select **Validate image**, then **Create package**. PSWaker checks the image,
   builds the package, then extracts and checks the result. When it shows
   **Package verified**, select **Open folder**.
5. **Copy the `.pkg`** to the root of the USB drive and connect the drive to the
   PS4.
6. On the PS4, open **Settings → GoldHEN → Debug Settings → Package Installer**
   and install the package.
7. **Launch PSWaker** from the home screen. Once it's installed, remove the USB
   drive; the game doesn't need it.

To update, close PSWaker and run the newer installer. Then create a new package
and install it over the old one on the PS4. Saves and settings are kept. Keep
your disc image and packages private.

For progress and cancellation, the files kept next to the package, private
troubleshooting reports, updating and uninstalling, see the
[desktop app guide](docs/desktop/README.md).

To build PSWaker yourself, see [BUILDING.md](BUILDING.md).

## Known issues

- **Console acceptance is pending.** Final integrated testing of the bundled
  program (01.13) on the console hasn't finished, and no package created by the
  desktop app has been tested on the PS4 yet
  ([#49](https://github.com/Jcanotorr06/pswaker/issues/49)).
- **Clean Windows testing is pending.** The desktop app has only been tested on
  the development machine, not on clean Windows 10 or Windows 11 systems.
- **Pauses and frame pacing.** Expect brief pauses while areas load and the first
  time an effect appears. With an empty shader cache, frame pacing falls short of
  the target. Improving it is deferred to
  [#51](https://github.com/Jcanotorr06/pswaker/issues/51).
- **Shutdown logging.** The program includes a fix for an earlier crash when
  quitting after the memory card goes idle. Quit looks normal on screen, but
  console logs haven't yet confirmed that shutdown completes internally.
- **One disc only.** Only the USA `GZLE01` revision 0 raw image is supported.
- **Limited route.** Only the route through Dragon Roost Island has been played.
  No claim is made about the rest of the game.
- **Windows x64 only.** There is no desktop app for macOS or Linux. The
  installer and app are not code-signed.
- **Redistribution review is incomplete.** Some inherited SDK modules and stubs
  in the bundled program still have open licensing questions
  ([#47](https://github.com/Jcanotorr06/pswaker/issues/47)). See
  [licensing](docs/ps4/LICENSING.md).

## Documentation

| Document | Contents |
| --- | --- |
| [docs/STATUS.md](docs/STATUS.md) | Checkpoint history and evidence |
| [docs/desktop/README.md](docs/desktop/README.md) | Desktop app details, troubleshooting and lifecycle |
| [docs/ps4/README.md](docs/ps4/README.md) | PS4 platform build and checks |
| [BUILDING.md](BUILDING.md) | Building the PS4 program, desktop app and installer from source |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to report issues and contribute changes |
| [docs/RELEASING.md](docs/RELEASING.md) | Maintainer release process |
| [docs/ps4/LICENSING.md](docs/ps4/LICENSING.md) | Third-party licenses and outstanding distribution work |
| [GLOSSARY.md](GLOSSARY.md) | Project vocabulary |

## Credits

PSWaker stands on the work of many other projects.

### Built on and inspired by

- [centollOS/SwitchWaker](https://github.com/centollOS/SwitchWaker): native
  Nintendo Switch port of *The Wind Waker* (GameCube), and the game code this
  port compiles.
- [griches/PS5_SwitchWaker](https://github.com/griches/PS5_SwitchWaker): PS5
  homebrew port of SwitchWaker, used as the main game-side reference.
- [BgbrhrWatchinOVO/dusklight-ps4](https://github.com/BgbrhrWatchinOVO/dusklight-ps4):
  native *Twilight Princess* port with PS4 adaptations for Aurora, Dawn, SDL3
  and Mesa, used as the main platform reference.
- [mshivam019/dusklight-ps5](https://github.com/mshivam019/dusklight-ps5):
  Dusklight's PS5 port, whose Aurora fork is the selected renderer.
- [zeldaret/tww](https://github.com/zeldaret/tww): *The Wind Waker*
  decompilation. A pinned fork, [snrubrm/tww](https://github.com/snrubrm/tww),
  is used.
- [encounter/aurora](https://github.com/encounter/aurora): GameCube/Wii
  graphics and platform layer.
- [elliotttate/RecompCore](https://github.com/elliotttate/RecompCore): DSP
  high-level emulation.

### Third-party components and tools

- [iHaiDeeZ/DolphinPS4](https://github.com/iHaiDeeZ/DolphinPS4): PS4 runtime
  and packaging scripts.
- [OpenOrbis PS4 Toolchain](https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain),
  with [PacBrew](https://github.com/PacBrew/ps4-openorbis) packaging: the
  homebrew SDK.
- [OpenOrbis/LibOrbisPkg](https://github.com/OpenOrbis/LibOrbisPkg): PS4
  package creation.
- [Mesa](https://gitlab.freedesktop.org/mesa/mesa),
  [Dawn](https://dawn.googlesource.com/dawn),
  [SDL3](https://github.com/libsdl-org/SDL) and
  [LLVM](https://github.com/llvm/llvm-project): graphics, platform and
  compiler.
- [GoldHEN](https://github.com/GoldHEN/GoldHEN): the console homebrew
  environment used for testing. It is not included.
- [PyInstaller](https://pyinstaller.org) and
  [Inno Setup](https://jrsoftware.org/isinfo.php): the Windows app bundle and
  installer.

The pinned versions and their licenses are listed in the
[lock files](platform/ps4/) and [licensing notes](docs/ps4/LICENSING.md).

## License

PSWaker's own code is licensed under the [GNU General Public License v3.0](LICENSE).
Third-party components keep their own licenses and per-file notices. Some of
them, as well as the combined program, are still under review
([licensing](docs/ps4/LICENSING.md)).

## Disclaimer

PSWaker is not affiliated with, endorsed by or sponsored by Nintendo, Sony
Interactive Entertainment or any other video game company. No game data, disc
images or keys are included or distributed. You must supply a disc image dumped
from a disc you own.

*The Legend of Zelda*, *The Wind Waker* and *Nintendo GameCube* are trademarks of
Nintendo. *PlayStation*, *PS4* and *DualShock* are trademarks of Sony
Interactive Entertainment. All other trademarks belong to their respective
owners.

PSWaker is provided as is, without warranty of any kind. Use it at your own risk.
