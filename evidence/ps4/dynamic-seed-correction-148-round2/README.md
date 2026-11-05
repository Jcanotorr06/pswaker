# Second seed correction for #148

The [returned first correction](../dynamic-seed-validation-148/REPORT.md) still
missed ten descriptions during its warm sample. This separate candidate preserves
all 291 prior database rows, including capture metadata, and adds precisely those
ten discoveries. No maintained program code changed from `8282b4d`.

## Frozen identities

| Artifact | Value |
| --- | --- |
| App version | 01.23 |
| Build / cache identity | `6e885683f47a49a119ae` |
| Program ELF SHA-256 | `400de6f1bb42fb4fc79f9399f290d2f0ee292e58ea03e4f8eea9c2e4dd7c32ab` |
| Package SHA-256 | `107e13f80423e89324aabb3aca453f46f2a0ea13569e0be6a509588fc9835a3d` |
| Seed descriptions | 301 (300 GX version 13; one ImGui version 5) |
| Seed bytes | 1,257,472 |
| Seed SHA-256 | `06b8ef5d5df64e6a1218728550eab209f6a841926392ac18064effce64f17fd8` |
| Asset manifest SHA-256 | `4caf1f6ba2572dd7faeb3d77aa99a38c3fbdc8a0e0ed0e4d1ca186183646a6a4` |
| Fresh package inspection SHA-256 | `2076142fad4075fb11462f84beaefc05f172837e827e11082299e64d6fb62cdb` |

[candidate.json](candidate.json) records prior/new identities, all ten addition
digests and source captures, real collector control, coverage and immutability.
Actual seed databases, game data, packages and executables remain private.

## Checks and limits

- Two public `correct` command runs produce identical seed, manifest and correction
  report bytes. All 291 baseline rows retain every original column.
- All ten additions come from the new warm capture (`runtime-2`); cold adds none.
  They retain honest runtime-capture provenance and unresolved source attribution.
- A real `common-pot-debris-lifecycle-v1` collector run emits 40 draws/lookups,
  verifies seeded runtime hashes for all 301 descriptions and round-trips all 301
  baseline descriptions through the normal recorder without changing them.
- Full-byte coverage passes for six retained sources: prior 291-description seed,
  new cold and warm captures, prior dynamic and static observations, and this new
  dynamic control. Their union is exactly 301 descriptions, with no conflicts.
- Normal game assembly and a separate fresh inspection verify package contents.
  All 17 retained private input files and all 31 original returned files remain
  unchanged. Previous candidates, artifacts and evidence are preserved.
- The copied private Windows handoff passed another fresh inspection, reproducing
  the frozen inspection digest. Its PKG is 1,521,156,096 bytes and matches the
  package digest above. Existing model-collection, Outset-coverage and frame-pacing
  suites ran 47 tests with one skip and no failures. No test or program code changed.

This does not expand the generated collector's bounded effect coverage or attribute
the new records to that effect. The new package has **not been tested on console**.
Configuration coverage does not establish gameplay correctness, zero future waits,
verified presentation timing, or clean shutdown. Quit is unchanged and remains #159.

For a future cold run, preserve and rename only the existing build-specific cache;
installing this package alone retains the same build/cache identity. Preserve saves,
settings and previous evidence. Repeat the bounded Outset route with explicit
action times and first/repeated visual observations, then retain cold and warm
evidence separately. Compare every returned configuration against these exact
seed bytes and count raw waits even below the hitch threshold.
