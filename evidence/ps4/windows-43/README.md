# Windows package-creation failure checks (#43)

Development-host observations on 2026-10-27, Windows 11 x64, using CPython
3.12.10, actual Tk controls/workers and the existing pinned native Windows
LibOrbisPkg tool closure. No owner image or complete package is committed here.

## Failure and retry outcomes

The tests use isolated copies of the app with tiny, data-free synthetic images
and program releases. The shipping content contract is unchanged and rejects
these images. Packaging, extraction and final inspection use the real Windows
tools and production code; storage faults are injected at OS boundaries.

Desktop checks exercise insufficient capacity, partial image-copy disk
exhaustion, lost write access, inaccessible destinations, failed publication
access, real packager errors from malformed GP4 input, inspection rejection of
an altered actual PKG, and a destination created during packaging. Further
checks exercise cleanup access loss and an unwritable local diagnostic location.

For each new desktop failure scenario:

- Create a real, freshly inspected prior complete package and record its hash.
- Validate through the desktop, trigger creation and apply the controlled fault.
- Observe the failed stage and corrective guidance; verify that package-opening
  and installation actions remain disabled and validation/selections are enabled.
- Compare the source-image and prior-package SHA-256 values before/after failure.
- Confirm there is no new completed output. A racing owner package remains
  byte-identical; a cleanup failure names the exact retained private workspace
  and preserves the original write error.
- Remove the fault, correct the destination through the desktop when necessary,
  validate again and create a package successfully. Compare the resulting
  package hash and image hash with its fresh inspection report, and verify the
  prior package remains unchanged.

The package-creation boundary additionally checks that capacity includes the
real self-contained tool snapshot, workspace-creation disk exhaustion has a
reported stage, and every subprocess receives destination-local private scratch
through `TEMP`/`TMP`. A real tool failure retains its operation, exit code and
full output in a local diagnostic log while the visible error remains concise.

## Validation

- **18 desktop tests passed** with a native Windows Tk display and real tools.
- **10 native Windows package tests passed**; the final compact-error/log
  regression also passed after the review adjustment.
- Pyright: **0 errors, 0 warnings**. Python compilation and `git diff --check`
  passed.
- Full suite under Linux/WSL: **129 tests, 70 environment-dependent skips, no
  failures**. Native Windows desktop/package cases ran separately as above;
  prepared game/reference-build fixtures were unavailable for the other skips.
- Standards review: **0 remaining findings**; the visible tool-error size
  observation was resolved. Spec review: **0 findings**.

The [desktop documentation](../../../docs/desktop/README.md) gives the commands
and the storage/error policy. These controlled checks establish failure handling
on this development host. They do not establish clean Windows 10/11 installer
acceptance, console acceptance, cancellation or interrupted-session recovery.
