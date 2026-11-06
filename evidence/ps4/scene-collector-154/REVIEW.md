# Independent review of #154

Two independent agents reviewed the staged implementation against starting
`develop`, commit `f47aba58b8b3e23196434e42df591f94cd6c4014`. The review command was
`git diff --cached f47aba58b8b3e23196434e42df591f94cd6c4014`; no task commits existed
yet. The staged comparison included all new files. Reviewers did not edit files or
rerun the ongoing full suite.

## Standards

No Standards findings.

The staged changes follow the documented rules:

- New evidence contains identities, counts, mappings and explicit gaps; no game
  bytes, build outputs or personal paths are committed (`CONTRIBUTING.md`, “Ground
  rule: no game data”).
- Generated host evidence consistently marks physical verification pending and
  ties the candidate to exact build/package/seed identities (`CONTRIBUTING.md`,
  “Console and owner evidence”).
- Existing evidence records remain untouched. Source provenance continues through
  the existing seed-union path.
- Synthetic fixtures remain data-free. Shared validation uses
  `scripted_collection`; the small amount of scenario setup repeated between
  collection and package tests does not warrant another abstraction.

## Spec

One finding: **[P2] Reversed ocean baseline attribution** in the evidence README.

The spec requires “source/scenario/layout-contract mapping” and “honest
provenance.” The README calls the ordinary ocean states pilot-covered and range
adjustment new. Both retained reports and public `coverage.json` show the reverse:
ordinary states contribute two new descriptions; range adjustment uses two
pilot-covered descriptions. Correct the prose; configuration counts and seed/package
evidence remain valid.

No other missing requirements, scope creep, or incorrect behavior found within
the agreed boundaries. Physical verification and unsupported families are explicitly
identified as pending gaps.

## Resolution

Corrected the prose. A direct baseline query and each retained state mapping
confirm ordinary ocean hashes `-6811978204254739052` and `587858538552342752` are
new; range-adjusted hashes `4251643188918909934` and `2531376136326673965` already
belong to the pilot. The generated mapping, description bytes, seed and package
never changed. This documentation fix required no collector rerun.

Standards: **0 findings**. Spec: **1 documentation finding, fixed**; no unresolved
finding in either axis.
