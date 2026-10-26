# Frame-pacing candidate (#22)

This branch adds completed-console-flip instrumentation and the
[owner sampling workflow](../../Frame-pacing-checklist.md) to the existing
playable baseline. **Installed-console measurements and acceptance remain
pending for this binary.** No numerical performance target or hardware row is
marked passed. Issue #22 remains open for the owner return and any measured
bottleneck correction; final integrated acceptance remains #23.

The [measurement contract](../../FRAME-PACING.md) documents FIFO game-frame
tagging, VideoOut completion timestamps, reliability checks, sample boundaries,
shader hitch/correlation definitions, separate startup/loading phases, fixed
quality and evidence renewal. No resolution, texture, logic-rate, selected
driver archive or speculative performance fix is changed.

Host validation and artifact identities are recorded below after final review
and private candidate inspection. Synthetic traces and mocked console service
tests verify recording/analysis behavior; they are never console evidence.

The existing owner edit to root `GLOSSARY.md` is outside this task and is not
included in its commits.
