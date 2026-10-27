# Owner decision: performance sufficient for the initial release candidate

The owner directed:

> I consider the current performance sufficient to move forward with the initial release candidate.
> Leave further improvements for a future version release

Performance is accepted as sufficient to proceed with the initial release
candidate. Further frame-pacing optimization and attempts to eliminate the
remaining cold shader stalls are deferred to a future version. Additional
optimization candidates or strict numerical-target passes are not prerequisites
for moving forward with this initial release candidate.

The original average >=29.5 FPS, p95 <=35 ms, p99 <=50 ms and maximum <=100 ms
targets remain recorded as reference goals for future improvements. The owner's
decision changes the initial release-candidate performance gate; it does not
change historical measurements or relabel failed samples as numerical passes.
The accepted basis is the owner's assessment of current performance, with the
returned diagnostic measurements and their known limits retained.

## Evidence and handoff

- The latest returned measurements are [01.12](console-return-01.12/REPORT.md):
  both warm samples meet the numerical targets; both cold samples have shortfalls.
- [01.13](candidate-01.13/REPORT.md) is the latest prepared package, with a
  validated 287-record pipeline-description seed. No 01.13 console run has been
  returned here. This decision is not evidence that its seed removed cold stalls
  or that a particular package has completed integrated validation.
- Physical presentation timing remains unverified. The owner confirmed clean
  visible Quit for 01.12, while its logs lack internal shutdown completion.
  Retain these as known evidence limits in the release-candidate review.
- Existing failures, raw evidence, package/build/seed identities and original
  owner reports remain preserved. No new binary, quality reduction or threshold
  rewrite is required to record this decision.

Proceed to the integrated release-candidate work associated with issue #23 under
this owner-approved performance exception. Identify the actual package used for
that work and retain its results. Functional correctness, stability, controls,
audio, saves/settings, packaging/provenance and distribution review remain
separate responsibilities; this decision does not declare the integrated
candidate accepted or authorize publication. Future performance work can reuse
the existing recorder, analysis workflow, seed tooling and preserved shortfalls.
