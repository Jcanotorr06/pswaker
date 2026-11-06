# Final automated verification of #154

Compared with starting `develop` commit
`f47aba58b8b3e23196434e42df591f94cd6c4014`. Candidate and complete source identities
are recorded in [candidate.json](candidate.json), with the independent reviews in
[REVIEW.md](REVIEW.md).

## Automated checks

- Full reference-enabled WSL suite: **286 tests, 60 platform/environment skips,
  no failures**, 527.688 seconds. Unavailable Windows/UI and other integrations
  are not represented as tested.
- Focused files: four scene, four enemy, three equipment, three particle, six
  inventory and 28 model-collection tests pass.
- Public scene fixture rejection covers malformed layout scalar types and 25
  incomplete/incompatible cases: oversized/duplicate requests, unsupported sharing,
  unowned gaps, changed recipes/resources/archives/collector/target, missing/reordered
  or empty states, invalid/invented/unmapped keys, wrong method/scenario, missing or
  incompatible state/preparation layouts, description conflicts and incompatible
  seed records. Rejection publishes no output and preserves all inputs.
- Real-tool synthetic scene batch → complete package → fresh inspection: pass.
  The public external collector-process fixture also exercises freeze and batch,
  input hashes, exact dispatched recipe/resource, immutable inputs and repeat output.
- Pyright: **zero errors and warnings**. Python compilation, maintained shell
  syntax and Git whitespace checks pass.
- All **17 manifest source references** name existing files and cited symbols in
  the selected game sources; new documentation links resolve.
- Observed failing first: the unsupported scene batch, then boolean layout values
  incorrectly accepted as integer fields. Both now pass. Remaining fixtures verify
  implemented behavior and are not claimed as additional red/green cycles.

## Real collection and exact artifacts

The native collector builds from the verified selected sources. Its complete
host/PS4 representation witnesses match, 2,872 bytes. Every real process recomputes
known-runtime description identities and checks complete baseline/observed bytes
against the ordinary synchronous recorder. Scene packets require real draws and
lookups in every fixed state, after validated runtime constant-asset loading.

Two fresh three-recipe batches agree on all observed assets and provenance bytes,
state scripts/mappings, counts, layouts, inputs and collector identities. Their
union has 11 descriptions, nine new, yielding 310 total. All 301 pilot descriptions,
frame metadata and source provenance survive unchanged. Each generated complete
description belongs to the frozen seed.

The only manifest correction fixes the logo source symbol to `dScnLogo_Delete`.
Both corrected manifests were freshly frozen, and both retained batches revalidated
without editing any source capture. Their seed and provenance bytes exactly equal
the originals; the complete package is unchanged. Earlier frozen records and the
correction procedure remain private.

The arrow and boss-water controls reproduce the two descriptions each retained
from #152/#153. All three scene exercises rerun against the final seed; host
preparation/cleanup completes before drawing, and every observed description still
matches the seed. Both stock scene/offscreen preparation roles are recorded,
including their equal host key. No host driver object is used as a portable asset.

The exact private complete package is assembled and independently extracted and
inspected. The full pinned payload, packaged seed bytes, source manifest, package
hash and inspection report match the candidate. Input preservation and final
source/hash checks pass. Native collector source inventory and recorded validation
source hashes still match the current tree.

Private artifact group `scene-154` retains full/focused/package check logs,
collection/build/replay commands and scripts, successful and failed attempts,
input-preservation records, final verification and the inspected complete package.

## Pending evidence

Physical PS4 preparation, appearance, raw creation/wait events, startup/resource
scaling, normal Quit and save/settings observations remain pending. Nine automation
families are explicitly unsupported, and the extra alpha description selected by
the overlap has no established causal explanation. The
[workflow](../../../docs/ps4/SCENE-COLLECTOR.md) supplies the bounded physical
selection and its limits. No prior physical pass or owner waiver is transferred
to this changed seed.
