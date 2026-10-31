# Owner decision: accept the assembled Outset evidence as returned

On 2026-10-31, after reviewing the [01.20 assessment](REPORT.md) and its
unconfirmed observations, the owner directed:

> accept the evidence as is

The returned cold and retained-cache launches are accepted as the bounded
hardware evidence for #112 under #107. No further capture is required to close
#112. This decision supersedes the assessment's recommendation to keep #112
open; the archived assessment and all original records remain unchanged.

## Accepted scope

- Normally assembled #111 complete package version `01.20`, build/cache ID
  `9f79516d60da618241a1`, package SHA-256
  `cc26a2526f9cb4b81383b2875c66fa6521519f3d2d991d3be5be08f1d91ae8f5`.
- Installed 287-description seed SHA-256
  `7e3f8527203dc488b5ae646904c986ac596d7d4017db45a0fcb18ae29de51dc1`.
- PS4 Slim / firmware 9.00 / GoldHEN v2.4b18, with an empty disposable cache
  and a corroborated compatible retained-cache relaunch.
- Recorded preparation before loading, zero missing-pipeline waits, and reduced
  cold-sample spikes against the accepted unseeded 01.19 baseline. Full cold
  preparation cost remains 14.621 seconds.

## Retained limits

Acceptance does not supply missing observations. Physical presentation timing,
normal recorder shutdown, actual first-action times/video and the approach,
visible preparation progress, incompatible-update behavior, save/settings
preservation and detailed correctness checks remain unverified as described in
the assessment. Only one sample per launch was returned. Residual approximately
50 ms intervals remain, including the increased warm interval count.

Both analyzer summaries remain unchanged with exit 2, invalid timing/shutdown
evidence and `target_met: false`. No verified numerical performance pass is
claimed. Remaining observations are accepted as limitations of this return,
rather than marked as completed tests.

This decision applies only to the identified package and bounded Outset route.
It does not establish full-game or broader Outset/forest coverage, close #107
or #51, resolve residual slow frames, transfer acceptance to another build, or
change the initial release candidate's previously accepted performance gate.
Game-derived artifacts remain private.
