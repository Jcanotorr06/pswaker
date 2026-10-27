# Native Windows complete-package observations (#42)

Private development-host observations on 2026-10-27, Windows 11 x64. No owner
image, package, extracted game data or native program is committed here.

## Production-image desktop run

The actual Tk desktop controls/workers selected the privately available owner
image and a new private destination. Only native dialog answers were substituted.
The production validator, bundled game release, native Windows packager and
fresh artifact inspection ran without substitutes. A second independent
`windows_package.inspect_output` invocation accepted the retained output.

- Program: game release **01.13**, compiled build `f236a035ac406940e76a`.
- Program SELF SHA-256:
  `a95ea92a37b5d080937cba386f0f0cb43a8e450999cbafb4da5c7861ac5e624e`.
- Program ELF SHA-256:
  `a99bcca89c4c0a54d808400ddffbfdca6d8df620d601b814386bf2fcd38e9ebb`.
- Accepted image SHA-256:
  `ec2d4ee790f48bee3d4c10feed166370df895f474e8db3f9af3b16ee001436df`.
  The source's before/after hashes matched.
- Verified package: `IV0000-PSWK00001_00-PSWAKERGAME00000.pkg`.
- Package SHA-256 for this run:
  `b6b84ac782c11ff1f5909122402c9e0292cc70d8101e31f26a1b8cb1e44a74b3`.
- Measured stages: validation **1.703 s**, bundled-input checks **2.328 s**,
  assembly **20.094 s**, fresh inspection **13.063 s**. These observations do
  not establish a Windows performance budget.

The retained private reports contain exact payload hashes, metadata, program and
tool identities, measured timings and installation instructions. Completed
outputs stayed outside the checkout and were never uploaded.

## Reproducible automated coverage

Final host checks passed: **8 desktop tests**, **6 native Windows package
tests**, and **114 tests** in the full Linux suite with real reference packaging
tools (**41 environment-dependent skips**). Pyright reported **0 errors and
0 warnings**; Python compilation checks passed.

Use `PSWAKER_WINDOWS_TOOLS` to select the maintainer-prepared closure, then run
the desktop and Windows package test files described in
[the desktop documentation](../../../docs/desktop/README.md).

Actual native package round trips exercise fixed application/content identity,
image/program hashes, fresh extraction, changed-source rejection, changed
program/tool/runtime rejection, altered PKG headers, unexpected extracted files,
existing/racing destinations and cleanup. Actual desktop controls exercise
verified success, folder opening/manual instructions and failure followed by
validation/retry. Synthetic images/programs are data-free, isolated fixtures;
the unchanged shipping contract rejects them.

## Remaining acceptance

These observations are not clean-machine Windows 10/11 or offline-installer
acceptance (#46/#48), console acceptance (#49), or distribution clearance
(#47/#50). The bundled 01.13 program remains an unaccepted performance candidate.
The package's successful container inspection must not inherit earlier console
results from a different program or package.

For release acceptance, install the exact candidate as an ordinary user on both
clean supported Windows versions with networking unavailable. Validate/create
using a private supported image, inspect the result and preserve owner data and
previous output. Then install the desktop-created package manually on the stated
PS4 baseline, remove USB for play, and run the existing route/audio/save/settings
and update-preservation checklists with that package's identity.
