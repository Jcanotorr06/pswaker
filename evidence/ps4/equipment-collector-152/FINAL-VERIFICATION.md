# Final automated verification of #152

The reviewed implementation is commit `8fdc101`, compared with starting
`develop` commit `c85e8ec9ce8bfecf94bb5e19f9fe35e92db48704`. No implementation
changes were needed after the independent [Standards/Spec reviews](REVIEW.md).
The final commit adds review and verification records only.

## Automated checks

- Full reference-enabled WSL suite: **274 tests, 60 platform/environment skips,
  no failures**, 401.754 seconds. This includes real packaging tools and all ten
  initialized-renderer startup/preparation checks. Skipped native Windows/UI
  and unavailable integrations are not represented as tested.
- Focused public collection/preparation/correction file: all 26 tests pass,
  including the equipment external-process dispatch/freeze/batch regression.
- Three equipment, three particle and six inventory tests: all pass. Equipment
  rejection subcases cover oversized/duplicate requests, unsupported sharing,
  altered setup, missing/reordered states, no draws, missing/invented mappings,
  malformed keys, wrong resource/input/collector/contract identities, unfinished
  lifetimes, identity/description conflicts and incompatible seed records.
- Real-tool synthetic mixed equipment batch-to-package assembly and independent
  fresh inspection: pass. Exact prepared seed and full source provenance survive.
- Pyright: zero errors/warnings. Python compilation, all eight maintained
  top-level shell syntax checks and Git whitespace checks: pass.
- The initial mixed equipment batch preparation test was observed failing
  before the implementation, then passing afterward. Later fixtures verify
  implemented rejection, process and package behavior; they are not claimed
  as additional observed red/green cycles.

## Real collection and exact artifact checks

Both fresh real three-recipe batches complete independently. Complete standalone
seed and provenance bytes, frozen manifests, observed per-scenario assets and
source manifests agree. Scripts, state/variation/tick mappings, draw/lookup
counts, target and collector/resource identities agree. All 301 baseline full
descriptions and every source-provenance record remain unchanged. Every observed
full description is present unchanged in the combined seed.

The source tree matches the retained native collector build inventory and every
recorded validation-tool hash. Both runs' recorded collection-tool hashes match
the current implementation. The 2,872-byte complete host/PS4 contract witnesses
agree, with the known-runtime identity/ordinary-recorder controls checked in each
process. No host driver objects are treated as portable shaders.

Ordinary assembly and a subsequent independent extraction/inspection identify
the exact candidate seed bytes and complete source provenance. Inspection also
pins the standalone source-manifest SHA-256 in the packaged complete-package
manifest; the standalone `pipeline-seed.json` file is not separately installed.
The full payload, package hash and inspection report agree with the frozen
[candidate](candidate.json). Immutable image/baseline, collector/plan/manifest,
prepared assets and matching program/ELF identities remain preserved.

Private artifact group `equipment-152` retains `full-checks.log`,
`focused-checks.log`, `package-checks.log`, `repeat.json`,
`package-inputs-preserved.json`, `final-verification.json`, both real batches,
the collector, replay scripts and inspected complete package. Public fixtures
contain synthetic descriptions/resources only.

## Pending evidence

Physical PS4 preparation, appearance, raw missing-pipeline waits, startup/resource
scaling, normal Quit and save/settings observations remain pending for this
changed seed. The [handoff](../../../docs/ps4/EQUIPMENT-COLLECTOR.md) selects
first/repeated arrow-tip and bomb/overlap scenarios plus regression controls,
using only already available equipment. Nine unsupported families/states remain
explicit follow-up gaps; no physical result or owner waiver is inferred.
