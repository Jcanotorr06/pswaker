# Final automated verification of #153

The verified implementation is commit `13296d2`, compared with starting `develop`
commit `f13e343dc6ad03a143fa98a51585b4e8f5e47c7b`. Its collector, seed and package
identities come from a full fresh rerun of the corrected sources. Candidates from
`69bfff4` and `98f9922` are superseded and retained privately. The final commit adds
review and verification records only.

## Automated checks

- Full reference-enabled WSL suite: **280 tests, 60 platform/environment skips, no
  failures**, 441.517 seconds. Skipped native Windows/UI and unavailable integrations
  are not represented as tested.
- Focused files: four enemy, three equipment, three particle, six inventory and
  27 model-collection tests pass.
- The 23 enemy rejection cases cover oversized/duplicate requests, unsupported sharing
  and gaps, altered setup, missing/extra/wrong companions, missing/reordered states,
  no draws, wrong method, missing/invented mappings, malformed keys, wrong
  resource/input/collector/contract identities, unknown scenarios, unfinished
  lifetimes, identity/description conflicts and incompatible seed records. None
  publish output.
- Real-tool synthetic enemy batch-to-package assembly and fresh inspection: pass.
- Pyright: zero errors/warnings. Python compilation, maintained shell syntax and Git
  whitespace checks: pass.
- Every manifest source reference names an existing file, and every cited symbol
  exists in the pinned source.
- Observed failing first: the mixed enemy batch and the generic particle refusal.
  Other fixtures verify implemented behavior and are not claimed as red/green cycles.

## Real collection and exact artifact checks

Both fresh real eight-recipe batches complete independently. Complete standalone seed
and provenance bytes, frozen manifests, observed per-scenario assets and source
manifests agree. Scripts, state/variation/tick mappings, draw/lookup counts, target and
collector/resource identities agree. All 301 baseline full descriptions and every
source-provenance record remain unchanged. Every observed full description is present
unchanged in the combined seed: 342 descriptions, 41 added.

The changed collector reproduces the complete retained #152 descriptions for the arrow
(2), normal bomb (107) and cheap bomb (35) recipes.

The source tree matches the retained native collector build inventory and every
recorded validation-tool hash. Both runs' collection-tool hashes match the current
implementation. The 2,872-byte complete host/PS4 contract witnesses agree, with the
known-runtime identity/ordinary-recorder controls checked in each process. No host
driver objects are treated as portable shaders.

Ordinary assembly and a subsequent independent extraction/inspection identify the exact
candidate seed bytes and complete source provenance. The full payload, package hash and
inspection report agree with the frozen [candidate](candidate.json). Immutable
image/baseline, collector/plan/manifest, prepared assets and matching program/ELF
identities remain preserved.

Private artifact group `enemy-153` retains `full-checks.log`, `focused-checks.log`,
`package-checks.log`, `repeat.json`, `package-inputs-preserved.json`,
`final-verification.json`, both real batches, controls, the collector, replay scripts
and inspected complete package. Public fixtures contain synthetic descriptions/resources
only.

## Pending evidence

Physical PS4 preparation, appearance, raw missing-pipeline waits, startup/resource
scaling, normal Quit and save/settings observations remain pending for this changed
seed. The [handoff](../../../docs/ps4/ENEMY-COLLECTOR.md) selects first/repeated kill and
freeze scenarios plus regression controls, using only what an ordinary save reaches.
Fifteen unsupported families remain explicit follow-up gaps, and Jalhalla's first-frame
difference remains unexplained. No physical result or owner waiver is inferred.
