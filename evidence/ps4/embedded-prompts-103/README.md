# Embedded prompt implementation validation (#103)

[validation.json](validation.json) records the exact implementation inputs,
host checks and the compiled PS4 target identities. The build is a compile-only
candidate (`unverified-103-compile`); no installed program/package or console
observations are asserted.

The title BTI and shared logo/gradient resources were inspected locally, with
only identifiers and structural metadata recorded in
[the audit](../../../docs/ps4/EMBEDDED-PROMPTS.md). No game pixels, extracted
text, captures, pack content or converted outputs are retained here.

Hosted checks exercise the real patched Aurora registry and GX object caches
with synthetic competing pointer/source replacements. Only GPU allocation is
stubbed. They cover either registration order, cached pack/prompt results,
applied artwork rebuild and failed upload suppression. The controls harness
also carries a retained embedded instruction through Apply/discard/failed Apply,
the shared resume gate and disconnect recovery.

Stock-mode physical observations remain **UNTESTED**. Run the
[console checklist](../../../docs/ps4/Embedded-prompts-checklist.md) on an exact
installed build and add a new observation record. This evidence establishes no
full-game coverage, HD-loader behavior or #79 hardware acceptance.
