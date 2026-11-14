# Integrated PS4 prompt hardware handoff (#106)

Status: **prepared, hardware UNTESTED**. Issue #106 stays open with
`ready-for-human`. No installation, console observation or owner confirmation
has been returned for this record. This is post-first-playable #79 work and does
not expand the original #12/#18 acceptance or inherit historical console passes.

Use the [integrated checklist](../../../docs/ps4/Integrated-prompts-checklist.md).
[candidate.json](candidate.json) identifies the unchanged #105 complete package
01.27, build `a21e4fc7a440bcaa3359`, compiled from
`99ff3dcf70b599e81fabd73b71bc341700114aa0` (merged through PR #174).
All maintained program inputs match this branch's starting point
`786ad334685cf77e1f525db9a63b5fdecff52e4c`. Documentation and evidence preparation
does not create a new binary. One stock package serves defaults and all focused
layouts; applying a layout does not require another package. Any changed program
or assembly input needs a separately identified candidate and new observations.

The complete package and matching ELF remain private. Fresh inspection of the
retained assembly passed again for #106, reproducing its previous inspection
report. The delivered package and ELF were rehashed, the 19 game patches match
the maintained series, and the package carries the validated 493-description
seed. Hashes and exact metadata are in the candidate record; raw assembly/build
records remain private because they contain local paths and asset identities.
No game data, extracted text, captures, pack artwork or asset-bearing outputs
are committed here.

## Coverage reconciliation

[coverage-review.json](coverage-review.json) snapshots the maintained
[identifier-only inventory](../../../platform/ps4/prompt-coverage.json):
514 entries, **455 converted / 35 text fallback / 24 unresolved**. Source paths,
resource entries and context entries overlap; these counts are not distinct
screens, instructions or a full-game completion percentage. No status was
promoted for this handoff. Converted means an implementation path exists;
text fallback means an accurate PS4 name is intended; neither is a hardware pass.

| Area | Reviewed implementation and remaining limits |
| --- | --- |
| HUD/context | Meter layout/control pictures, separate action descriptions and message pictures use applied bindings. Unknown action status remains unresolved; verify contextual words, both shadows and the historical HUD squash fix physically. |
| Message tags/pictures and tutorials | Shared retained message/out-font adapters convert the reviewed control-picture tags; direction and animation remain in the contract. Real dialogs/tutorials and refresh remain unobserved. |
| Native menus/file selection | Applied menu pictures and accepted alternatives are implemented. Item/window, name-entry embedded artwork and file-select literal resources remain unresolved, as do their broad source-family aggregates. |
| Title/start | Reviewed stock title instruction, accepted A/B/Start alternatives, pulse and model/material identifiers are implemented/audited. Unaudited layout/model/material resources and other languages/revisions remain unresolved. |
| Written names | #105's retained audit reviewed 4,426 BMG entries: 305 instruction messages, comprising 292 converted, four text fallback (816, 817, 1108, 3008), nine unresolved system/peripheral messages. This handoff reconciles those existing identifiers; it does not claim a new disc-resource audit. Console fit/readability and broader resource/language coverage remain unresolved. |
| Embedded images/shared atlases | Only the reviewed title replacement and adjacent audited identifiers have implementation evidence. The general embedded/shared-atlas family remains unresolved; a title sample cannot clear it. |
| Partial/full triggers | Resolver variants and unchanged 90% terminal click have host coverage. Reviewed written resources identified no literal travel instruction; the general trigger-context inventory remains unresolved pending actual contexts. Plain L2/R2 icons do not establish travel distinctions. |
| Port UI | Legend uses applied controls with accurate text fallback. Cross/Circle/Touchpad and navigation stay fixed; physical agreement and input safety need owner observation. |

The exact 24 unresolved identifiers are retained in `coverage-review.json`.
The nine unsupported system/peripheral messages remain defects even if their
neutral notice is readable and dismissible. Historical source-inspection
paragraphs in individual slice docs describe their own checkpoints, not the
current integrated scope. Representative samples never establish full-game
coverage. A known gap prevents declaring the affected surface complete.

## Supporting checks and owner return

[validation.json](validation.json) records this handoff's host checks. The
pre-agreed #79 seams are the semantic resolver and installed-controls harness;
the existing synthetic written-translation and exported precedence-rule checks
also run. No new runtime behavior or test seam is introduced. Host compilation,
synthetic retained refresh and package inspection cannot prove installed visual
refresh, fit, contrast, actual actions or disconnect/resume behavior.

[observations.json](observations.json) is an **unfilled template**, with expected
candidate identity, defaults, nine matrix layouts and all focused cases. `runs`
is empty; observations and owner confirmations are null. For each actual run,
copy it to a new private file, fill the installed identity and associate results
with run/context/layout. Return reviewed asset-free metadata as a new evidence
record. Preserve FAIL/BLOCKED/UNTESTED results and every stated limit. Do not
overwrite archived files or turn expected results into observations.

## Handoff to #80

The [exported rule](../../../docs/ps4/EMBEDDED-PROMPTS.md#public-precedence-rule-for-80)
reserves `promptPriority` (`INT32_MAX`) for prompt ownership and caps pack
priority at `packMaximumPriority`. Prompt ownership wins across matching pointer,
exact source hash, palette wildcard and texture wildcard families in either
registration order. Within an ownership class retain specificity, priority and
registration ordering. Registry mutations invalidate retained GX objects and
bindings; future loaders remove only their own registrations. Host checks are
supporting evidence for this rule. Actual HD loader, conflicting pack, fallback
and loading-transition tests remain #80 work. Stock-mode validation comes first.
