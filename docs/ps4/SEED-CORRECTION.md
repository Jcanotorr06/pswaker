# Correct a pilot seed from compatible runtime discoveries

This is the seed-only follow-up to the
[#148 failed candidate assessment](../../evidence/ps4/dynamic-validation-148/REPORT.md).
It preserves the generated static/dynamic pilot and supplements its seed with
actual compatible runtime descriptions. It does not diagnose or fix the Quit
failure tracked by [#159](https://github.com/Jcanotorr06/pswaker/issues/159).
The old package, seed, original return and failed validation record remain intact.

## Correction contract

`collect-model-seed.py correct` accepts an existing validated baseline asset and
one or more **standalone** runtime snapshot assets from the existing
`complete-package.py pipeline-seed` command. It uses the selected renderer's
existing schema/config-version/description-size validator and compares each
common `(type, hash)` by complete version/size/description bytes. Conflicts
between either the baseline and a capture or two captures reject the entire
correction. Corrupt, mismatched, incompatible, or live-sidecar-bearing assets
are rejected before publishing an output.

The command preserves every baseline row, including its first-use metadata,
and inserts each new compatible identity once. First-use frame is capture
metadata, not configuration identity or a verified action timestamp. Input
order is recorded as `runtime-1`, `runtime-2`, etc.; the first supplied snapshot
provides an added row's stored metadata. Each addition also records every
source containing it and each source's first-use value. Fix the input order
when checking byte-for-byte repeatability.

The seed manifest preserves original source inventories under `baseline:` and
runtime source inventories under their respective labels. `correction-report.json`
records input asset/manifest hashes, baseline and source manifests, full-description
hashes, additions and source mappings. Its provenance is `runtime-capture-correction`,
not generated particle coverage. With no additions, both baseline asset files
remain byte-identical and the report retains the supplemental evidence separately.
Inputs are checked unchanged before publication; existing outputs and outputs
inside source assets are refused. Assets and reports remain private.

The validator checks the selected representation contract; it does not make
arbitrary captures from other targets/builds equivalent. Before using this
workflow, verify that the captures belong to the identified supported program,
renderer settings and game revision. Retain their inspection, recorder identity,
owner context, database/WAL hashes and the matching ELF. Keep the original
capture-to-snapshot chain alongside the correction report.

No fabricated raw configurations or host driver binaries enter the seed.
The three discoveries from this return are known PS4 runtime descriptions;
their precise source-code/effect attribution remains explicitly unresolved.
Their presence in a corrected package does not prove successful first-use
preparation, zero waits, correct physical timing or broader game coverage.

## Reproduce privately

Use new output directories outside the repository, preserving the original
database and adjacent WAL. The snapshot command copies them before opening.
`BASELINE_ASSETS` is the frozen 288-description static/dynamic pilot asset.
`COLD_RETURN` and `WARM_RETURN` are the preserved original return directories.

```bash
python3 tools/pswaker/complete-package.py pipeline-seed \
  "$COLD_RETURN/pipeline_cache.db" --output "$PRIVATE_ROOT/cold-snapshot"
python3 tools/pswaker/complete-package.py pipeline-seed \
  "$WARM_RETURN/pipeline_cache.db" --output "$PRIVATE_ROOT/warm-snapshot"
for run in a b; do
  python3 tools/pswaker/collect-model-seed.py correct \
    --baseline "$BASELINE_ASSETS" \
    --runtime-snapshot "$PRIVATE_ROOT/cold-snapshot" \
    --runtime-snapshot "$PRIVATE_ROOT/warm-snapshot" \
    --output "$PRIVATE_ROOT/corrected-$run"
done
cmp "$PRIVATE_ROOT/corrected-a/assets/initial_pipeline_cache.db" \
    "$PRIVATE_ROOT/corrected-b/assets/initial_pipeline_cache.db"
cmp "$PRIVATE_ROOT/corrected-a/assets/pipeline-seed.json" \
    "$PRIVATE_ROOT/corrected-b/assets/pipeline-seed.json"
cmp "$PRIVATE_ROOT/corrected-a/correction-report.json" \
    "$PRIVATE_ROOT/corrected-b/correction-report.json"
python3 evidence/ps4/outset-coverage-111/verify-coverage.py \
  "$PRIVATE_ROOT/corrected-a/assets" "$BASELINE_ASSETS" \
  "$PRIVATE_ROOT/cold-snapshot" "$PRIVATE_ROOT/warm-snapshot" \
  "$STATIC_COLLECTION/assets" "$DYNAMIC_COLLECTION/assets" \
  --output "$PRIVATE_ROOT/corrected-coverage.json"
python3 tools/pswaker/complete-package.py assemble --kind game \
  --platform-root "$PLATFORM_ROOT" --program-stage "$PROGRAM_STAGE" \
  --elf "$PROGRAM_ELF" --app-version 01.23 --image "$IMAGE" \
  --assembly-assets "$PRIVATE_ROOT/corrected-a/assets" \
  --output "$PRIVATE_ROOT/seed-corrected-complete"
python3 tools/pswaker/complete-package.py inspect \
  "$PRIVATE_ROOT/seed-corrected-complete" --platform-root "$PLATFORM_ROOT"
```

Reuse the matching 01.23 program and ELF: this task changes the seed and package,
not the executable or its shutdown behavior. Re-running the isolated model and
particle collectors against the corrected baseline also checks its identity
hashes and normal-recorder round trip through the selected host renderer. Those
control runs are useful compatibility evidence, not physical PS4 revalidation.
Keep the existing generated source mappings and explicit scenario exclusions.

## Identified replacement and future console evidence

The first 291-description correction subsequently failed its returned warm run:
see [the preserved assessment](../../evidence/ps4/dynamic-seed-validation-148/REPORT.md).
The current separate replacement has 301 descriptions, incorporating ten further
runtime discoveries. Its identities and checks are in
[the second correction](../../evidence/ps4/dynamic-seed-correction-148-round2/README.md).
Its private complete-package directory is
`dynamic-148-seed-corrected-round2-complete-01.23`; its Windows handoff is
`PSWaker-01.23-dynamic-pilot-148-seed-correction-round2`. It has no physical
validation yet. The earlier identities below are retained as history.

The corrected candidate's exact seed/package/ELF/inspection identities and executed
checks are in [the correction report](../../evidence/ps4/dynamic-seed-correction-148/README.md)
and [candidate.json](../../evidence/ps4/dynamic-seed-correction-148/candidate.json).
Use those identities instead of the failed candidate's package hash. The private
complete-package directory is `dynamic-148-seed-corrected-complete-01.23`; the
Windows handoff is `PSWaker-01.23-dynamic-pilot-148-seed-correction`.

The same program/cache ID `6e885683f47a49a119ae` remains in use. Installing a new
package is not a cold launch. For a selected future clean-cache test, fully close
the application and back up `/data/pswaker/`, then retain/rename only
`/data/pswaker/cache/6e885683f47a49a119ae/` to a new sibling. Preserve all saves,
settings, previous caches and returned records. A warm run using the old learned
291-description cache cannot establish that the corrected seed was bundled.

Use the confirmed route: Outset's two pots next to the Outdoor Bath, view them
for about ten seconds, first break around ten seconds, second break with the
sword around forty seconds, then rolls through a two-minute sample. Record the
actual break method and times, approach, appearance, controls/audio and visible
startup/progress. No story progression or completed-save acquisition is needed.
The earlier [bounded handoff](DYNAMIC-COLLECTOR.md#bounded-staticdynamic-console-handoff)
provides normal Quit, private retrieval and separate retained-cache sampling
steps. Plan roughly 15–25 minutes plus actual preparation and transfer time when
a new console test is arranged; this seed-only delivery does not claim that test.

Check the exact installed package/seed before attributing new results. Require
successful preparation of all included configurations and required target-layout
variants before gameplay, zero raw missing-pipeline waits, and independent
full-description membership for every returned snapshot. Preserve failed or
incomplete evidence; do not waive an observed wait based on average FPS.

**The known Quit failure is unchanged.** Retain any failed shutdown evidence and
keep it associated with #159; a seed correction is not a clean-Quit fix or final
hardware acceptance. Normal Quit and completed recorder/database closure remain
required for an accepted return. If #159 later changes the program, assemble and
inspect a new candidate with its matching ELF and renew affected physical checks.
