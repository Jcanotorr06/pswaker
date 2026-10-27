# Offline installer development-host evidence (#46)

Private observations on 2026-10-27, Windows 11 Pro x64, build **26200**.
No installers, game images, extracted content, keys or complete packages are
committed or uploaded. Candidates remain private pending #47/#48/#49/#50 gates.

## Candidate identities

Both candidates were built with CPython **3.12.10**, PyInstaller **6.22.3** and
Inno Setup **6.7.3**. Each private `installer-release.json` retains the complete
installed file inventory, desktop/program/tool manifests, installer recipe hash
and compiler-file inventory. Installer building did not read the owner image.

| Desktop version | Installer SHA-256 | Installed application manifest SHA-256 |
| --- | --- | --- |
| 0.46.0.0 | `4a56838bff28e6f014b2dd4b05aa07453110631d80e6a20168dc8a195cb7f68d` | `187a44c074766f1e27a7edd2c0b5a9569874109f6b159ef866947c8a99836642` |
| 0.46.1.0 | `8eec0002d4007ec044acf0c449677c1565249e7ff6e68c5d2a5da14de4b0a086` | `8f029a87b22316be8b877cf6cf6282bead5d99a73502fdf63ba8f2582f738a0b` |

Both carry the same game program **01.13**, compiled build
`f236a035ac406940e76a`, and the self-contained Windows LibOrbisPkg closure from
revision `594021fdc435409f755a6ae0781b65ec6cec846c`, built with SDK **8.0.427**.
Program SELF SHA-256 remains
`a95ea92a37b5d080937cba386f0f0cb43a8e450999cbafb4da5c7861ac5e624e`;
matching ELF SHA-256 remains
`a99bcca89c4c0a54d808400ddffbfdca6d8df620d601b814386bf2fcd38e9ebb`.
The program remains a private, unaccepted performance candidate.

## Installed production-image lifecycle

1. Installed 0.46.0.0 using its real per-user installer at the default local
   application location. The HKCU registration reported 0.46.0.0, and its Start
   menu shortcut resolved to that installed executable.
2. The installed closure probe accepted every executable/runtime, tool, program
   and contract file and reported the matching application manifest above.
3. Launched the installed frozen app outside the checkout with system-only PATH,
   empty PYTHONPATH and an absent external DOTNET_ROOT. Native Windows dialogs
   selected the real supported image and a custom output parent. The actual app
   validated, assembled and freshly inspected the production package. No
   validation/assembly/inspection function or native tool was substituted.
4. Independently repeated `windows_package.inspect_output` on the retained
   artifact using the installed fixed tool bundle; inspection passed.
5. Installed 0.46.1.0 manually over the existing per-user installation. Its
   registration, Start menu shortcut and installed closure probe identified the
   new complete runtime. Repeated the actual desktop flow at another custom
   destination and independently reinspected its package. The previous package
   remained unchanged.
6. Ran the real uninstaller. Subsequent checks confirmed the whole installation
   directory, per-user registration and Start menu shortcut were removed. Both
   completed packages and the original image remained intact.

The observation driver initially asserted directory absence immediately after
the uninstaller returned, before its self-deletion finished. A subsequent
independent check confirmed complete removal, then rehashed both retained
packages and the original image. This timing detail is retained rather than
presenting that first driver invocation as an uninterrupted passing test.

| Desktop version | Freshly inspected complete-package SHA-256 |
| --- | --- |
| 0.46.0.0 | `eeabb5d247d6b9e3d21e0ba251af92ad5f3665a5b90be3a20182c7cfac9d6a8e` |
| 0.46.1.0 | `3f0a974fa9ea8993028588e16c1779fb39d4118ee5e06cb1312fbfe88f1fce5c` |

Source SHA-256 before/after matched
`ec2d4ee790f48bee3d4c10feed166370df895f474e8db3f9af3b16ee001436df`.
Both results retain `PSWK00001` /
`IV0000-PSWK00001_00-PSWAKERGAME00000`, program version **01.13** and installed
`/app0/game.iso`. This exercises a desktop-only update, not a native program
update or console save/settings acceptance.

## Automated checks

- Full Linux suite after the diagnostics correction: **143 tests**, passed,
  **70 environment-dependent skips**; real reference package tools were enabled.
- Native Windows desktop suite: **26 tests**, passed, including distinct
  desktop/program versions in validation and successful-package diagnostic exports.
- Native Windows packaging suite: **15 tests**, passed.
- Real installed lifecycle test: **1 test**, passed. Two data-free candidate
  installers exercised native dialogs, actual frozen apps, package inspection,
  manual update, missing-runtime rejection and uninstall. It checked unchanged
  input/prior output and preservation of an untracked file inside the install
  directory; all installed release directories were removed.
- Pyright: **0 errors, 0 warnings**. Python compilation and diff checks passed.

Synthetic contracts/programs remain confined to temporary test copies. The
shipping validator has no fixture bypass and retains its production image policy.

## Standards review

No documented-standard violations. One optional **possible Duplicated Code**
finding: installed startup and package creation both validate bundled release
inventory/version/contract identity. A shared verifier could consolidate future
changes; startup currently requires the installed manifest while packaging also
supports older developer bundles. This is a non-blocking refactoring suggestion.
The diagnostics/lifecycle follow-up review found no new actionable findings.

## Spec review

No implementation mismatches found against #46 and parent #39. Required human
acceptance remains open as described below.

Standards: **0 hard violations, 1 optional finding**. Spec: **0 implementation findings**.

## Remaining acceptance

This host used a **non-elevated token** (`IsUserAnAdmin` false), but its account
belongs to Administrators with that SID marked **deny only**. These observations
therefore establish non-elevated operation, not a separate standard-account run.
Networking was not physically disabled. Unreachable proxy settings and absent
developer PATH/runtime locations exercised local runtime closure; they cannot
substitute for network isolation.

Keep #46 open for actual standard-account/offline lifecycle evidence. Complete
the [installer checklist](../../../docs/desktop/Installer-checklist.md) on clean
Windows 10 and Windows 11 x64 with a separate standard account and networking
disabled before installation; final clean-system evidence belongs to #48.
Console program-update/save/settings evidence remains #49. Public redistribution
and release gates remain #47/#50. None of the container or host checks establish
console acceptance or distribution clearance.
