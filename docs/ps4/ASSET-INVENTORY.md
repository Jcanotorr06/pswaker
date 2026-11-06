# Bounded asset/material inventory (#150)

This maintainer workflow extends the [model collector](MODEL-COLLECTOR.md) over
an explicit resource/state plan. Use Linux/WSL2, the supported USA GZLE01
revision-0 image, and a collector built against the selected PS4 renderer.
Images, resource bytes, generated descriptions, logs and complete packages stay
private. The plan, hashes and coverage classifications contain no game data.

## Freeze the inputs

Build the collector using the existing `collect-model-seed.py build` command.
Use a new private output directory, the matching prepared game source and
source-built host dependencies. The complete host/PS4 contract witness and
known-runtime full-description controls are unchanged from the pilot.

A plan fixes stable resource/family IDs, source-code references, content/mode/state
dimensions, assumptions and dynamic-path exclusions with separate ownership.
Every selected archive's inventoried BDL/BMD members remain explicit, including
unexercisable members. A list of filenames does not establish draw coverage.
The retained [plan and generation record](../../evidence/ps4/asset-inventory-150/README.md)
define this bounded slice and the larger families left for follow-up.

```bash
python3 tools/pswaker/collect-model-seed.py freeze-inventory \
  --plan evidence/ps4/asset-inventory-150/inventory-plan.json \
  --collector "$COLLECTOR" --image "$IMAGE" \
  --output "$PRIVATE_ROOT/inventory.json"
```

Freezing validates the full image, verifies the collector binary and both target
contract witnesses, reads resources through the existing disc/archive interfaces,
and binds the plan, image, collector/build, archive and expanded-model hashes.
It checks input immutability and refuses existing output. Repeat with the exact
same inputs to reproduce the manifest bytes. A changed collector requires a new
manifest and evidence; it does not inherit another build's console observations.

## Row contract

The schema-1 manifest has `id`, `image_sha256`, `contract_sha256`,
`collector: {sha256, build_sha256}`, `dynamic_exclusions` and `rows`.
Each row contains:

- `id` and `family`: stable lowercase kebab-case identifiers.
- `resource`: an exact `/res/archive.arc:directory/model.bdl` or `.bmd` reference.
- `source_references`: the pinned game loader and relevant use-site source.
- `input_identity`: `archive_sha256`, expanded `model_sha256`, and `model_bytes`.
- `dimensions`: nonempty `content`, `mode` and `state` lists.
- `assumptions` and one `action`: `exercise`, `shared`, `unsupported`, or `missing`.

`exercise` uses `state: ["stock-bdl-v1"]`. The native process mounts the requested
archive with `JKRArchive`, loads the BDL with `loadBinaryDisplayList(..., 0x2020)`,
and creates the model with flags `0` and `0x11000084`. It draws three frames
through the real J3D update/view/draw-buffer paths. The camera, GX setup,
synchronous creation, stock textures, single sample and 1280x720 target match
the pilot recipe. No stage, game logic loop, save or settings profile is loaded.
The production program retains its original 30 Hz logic and runtime fallback.

This recipe exercises a model's stock draw state. A loaded material count is
not proof that every material/state was drawn. It does not reproduce actor
lighting, fog, animation, material substitutions, scene-specific model flags,
dynamic effects or render-pass/layout variations. The use-site references and
assumptions expose those differences. BMD and material-animation loader families
remain unsupported by this recipe; do not relabel them as collected BDL states.

`shared` must point directly to an exercised row with the identical archive/member,
resource hashes and stock state, and provide `shared_with` plus `justification`.
The report retains both source IDs. Distinct models that independently produce
identical configurations are both exercised and mapped to the deduplicated
configuration. Sharing an archive, filename, or material count is insufficient.
`unsupported` and `missing` require a reason; retain evidence references and
follow-up ownership in the plan. No classification establishes physical verification.

## Run and repeat

```bash
python3 tools/pswaker/collect-model-seed.py batch \
  --manifest "$PRIVATE_ROOT/inventory.json" --collector "$COLLECTOR" \
  --image "$IMAGE" --baseline "$BASELINE_ASSETS" \
  --output "$PRIVATE_ROOT/batch-a"
python3 tools/pswaker/collect-model-seed.py batch \
  --manifest "$PRIVATE_ROOT/inventory.json" --collector "$COLLECTOR" \
  --image "$IMAGE" --baseline "$BASELINE_ASSETS" \
  --output "$PRIVATE_ROOT/batch-b"
cmp "$PRIVATE_ROOT/batch-a/prepared/assets/initial_pipeline_cache.db" \
    "$PRIVATE_ROOT/batch-b/prepared/assets/initial_pipeline_cache.db"
```

Each exercised row gets an isolated native process, normal-renderer recorder
comparison and baseline round-trip check. Every process has the pilot's existing
180-second timeout. This isolation costs repeated baseline preparation and image
validation; choose finite families and record oversized ones for follow-up.
The batch never silently skips a failed exercise. It retains the failed attempt
and logs at the requested output; inspect the failure and choose a new output.
Use only a successfully completed batch as a candidate.

`prepared/batch-report.json` retains the frozen manifest, per-row classifications,
per-configuration identities/full-description hashes and every source mapping,
baseline-covered/new counts, residual gaps and immutable input inventories.
`prepared/validated/<id>/collection-report.json` retains detailed collection
provenance, commands, actual draw counts, layout and per-resource descriptions.
`batch-run.json` binds the tool sources, inputs and report. All generated and
shared rows have `physical_verification: false`.

Configuration deduplication compares `(type, hash)` and the complete version,
size and description bytes; first-use frame metadata is excluded from identity.
Baseline/pilot descriptions and original provenance survive. A zero-addition
batch preserves both baseline asset files byte-for-byte. Any incompatible record,
same-identity/different-description conflict or resource/collector/image/contract
attribution mismatch rejects preparation. Existing outputs and inputs are preserved.

To consolidate already retained independent collections without rendering again:

```bash
python3 tools/pswaker/collect-model-seed.py prepare-batch \
  --manifest "$PRIVATE_ROOT/inventory.json" \
  --collections "$PRIVATE_ROOT/batch-a/collections" \
  --baseline "$BASELINE_ASSETS" --output "$PRIVATE_ROOT/prepared-again"
```

The collections directory contains one directory named by each exercised row ID.
Missing collections fail preparation. Rows explicitly classified as missing or
unsupported remain gaps in a successful report; `inventory_complete` refers only
to the listed stock-resource rows and does not imply full-game or dynamic coverage.

## Package and select physical observations

Pass `batch-a/prepared/assets` to the ordinary complete-package `assemble --kind
game --assembly-assets` interface, using the matching verified production program
and ELF. Run a separate fresh `inspect` and compare the exact extracted seed,
asset manifest, package, program/build and ELF identities. Keep the frozen plan,
report and per-row collections with the private package. Host compiled driver
objects are never shipped as portable descriptions.

The retained generation record supplies the identified candidate and bounded
console selection. Choose accessible ordinary-save scenarios, first use and
repeat actions, successful cold preparation and separate compatible warm reuse.
Check raw creation/wait events and every returned complete description against
the frozen packaged seed independently. Preserve saves/settings separately from
disposable caches. Asset generation and package inspection cannot establish PS4
preparation, appearance, layout coverage or startup/resource viability.

On 2026-11-06 the owner explicitly authorized this expansion despite #149's
remaining acceptance gaps. That authorizes generation; it does not waive or
retroactively satisfy those physical evidence requirements, or change #136.
