# Independent review of issue #16

Fixed point: `develop` at task start,
`f99ac2a579796590f533b6b50ebce8a41c795aa0`.
Reviewed implementation commit: `c77b359` (`Add validated private complete-package preparation (#16)`).

```text
git diff f99ac2a579796590f533b6b50ebce8a41c795aa0...HEAD
git log f99ac2a579796590f533b6b50ebce8a41c795aa0..HEAD --oneline
```

The code-review skill ran independent Standards and Spec agents in parallel.
The final command-history correction received a separate Spec follow-up review.
This report records their findings; the full 20-test host suite then passed.

## Standards

No findings. The changes follow the documented repository standards and
preparation/artifact-inspection CLI test boundaries. No material baseline code
smells identified.

## Spec

No actionable Spec findings.

- Missing/partial requirements: positive validation and assembly using an actual
  supported USA GZLE01 revision-0 image remain unverified. This evidence limit is
  explicitly disclosed in COMPLETE-PACKAGES.md; synthetic acceptance exercises a
  separately copied CLI and contract, without changing production validation.
- Scope creep: none found.
- Incorrect implementations: none found. Required DOL/REL selection matches the
  pinned upstream stub generator, image validation checks both content and
  complete-image hashes, and assembly verifies extracted content at
  `/app0/game.iso` with stable application identity and explicit diagnostic limits.

Optional evidence improvement: Tools.run() overwrites commands.json when a
subsequent standalone inspection creates a new Tools instance, losing earlier
individual assembly tool invocations. The replayable assembly_argv survives,
so this does not constitute a missing repeatability requirement.

**Correction and independent follow-up:** standalone inspection now appends to
existing command history, preserving the assembly invocations. The CLI
regression checks that preservation. No further findings in this delta.

Standards: 0 actionable findings. Spec: 0 actionable findings; real USA-image
acceptance remains unverified. The optional command-history improvement is fixed.

## Retail-image follow-up

The owner subsequently supplied the full USA revision-0 image. Its initial
whole-image rejection, externally verified retail fingerprint, corrected exact
allowlist and successful real assembly/fresh extraction are recorded in
[OWNER-USA.md](OWNER-USA.md). This supersedes the initial pending real-image
status above. Both independent agents reviewed follow-up commit `ab42038` with:

```text
git diff d39380b...ab42038
git log d39380b..ab42038 --oneline
```

### Standards

No findings. No documented-standard breaches or material baseline smells.
The allowlist change preserves the existing identity, structural and executable
checks. Documentation and retained inspection evidence agree, and all four
recorded preparation hashes match the committed files. The added fingerprint
matches Redump entry 1086.

### Spec

No Spec findings in `ab42038`. The added exact retail fingerprint matches
Redump entry 1086. Validation retains every identity, revision, size, structural
and pinned DOL/REL check, without introducing an override.
The new data-free evidence records real private assembly and fresh extraction
with matching image hashes. NONPLAYABLE status, licensing limits and absence
of console acceptance remain explicit. No scope creep or incorrectly
implemented requirement found.

Follow-up totals: Standards 0 findings; Spec 0 findings. The final full host suite
passed 21 tests with no skips after this change.
