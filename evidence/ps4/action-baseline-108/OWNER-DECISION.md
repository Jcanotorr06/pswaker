# Owner decision: accept the Outset action baseline as returned

On 2026-10-30, after reviewing the [baseline report](REPORT.md), the owner directed:

> accept the evidence as is

The returned 01.19 cold and warm launches are accepted as the #108 baseline
for the #107 coverage update. No further capture is requested to close the
gaps listed in the report.

## What the decision covers

- The baseline identity: unseeded 01.19 package
  `b7739a9c2fb6490dc2faceffe44e706a6f1ecc412805ffb76aaa13ec7fc1319e`, build
  `48d0196e605f00284b21`, on PS4 Slim / 9.00 / GoldHEN v2.4b18.
- The cold and warm measurements, and the correlation of spikes with shader
  waits within the planned route windows.
- The returned snapshots: 258 configurations after cold and 259 after warm.
  All 259 are present, byte-identical, in the 287-record 01.13 seed.

## What it does not change

- The gaps remain recorded and are not waived as observations:
  - no per-action timings or video
  - an undescribed walk
  - one sample per launch
  - no normal-Quit shutdown evidence
  - a warm database probably copied while running
  - no backup or cache-rename record
  - unverified physical timing

  Later conclusions must stay within those limits.
- Neither sample is a numerical or timing pass. The cold shortfalls and the
  uncorrelated spikes remain, and the uncorrelated spikes still need separate
  investigation under #107.
- Hardware validation of a seeded package remains #107 work. This decision
  does not make it unnecessary.
- The game-derived databases, snapshots and logs stay private.
