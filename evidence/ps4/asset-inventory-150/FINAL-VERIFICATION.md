# Final independent generation verification (#150)

This completes the automated repeat check that was pending in
[the implementation reviews](REVIEW.md). The original
[generation record](README.md), [coverage report](coverage.json), frozen manifest
and candidate remain unchanged. The additional results are retained in
[repeat.json](repeat.json).

The fresh public `batch` run exercised all 19 selected resources again from the
same 301-description baseline and frozen manifest. Its native collections match
the independent probes/control in resource, collector/build, image, target
contract, observed seed bytes, draw/material counts, pipeline lookups and layout.
The two preparations produce **identical complete seed database and provenance
manifest bytes**, with identical configuration-to-source mappings. Both inventory
freezes also produce identical complete manifest bytes.

The independent coverage command compares **38 validated snapshots** from the
two real runs by configuration identity and complete description bytes. All
**33 distinct collected descriptions** match the frozen seed, with zero missing
or conflicting descriptions. One was already baseline-covered; 32 additions
produce the final **333-description** seed. All 301 earlier descriptions and
their prior provenance are preserved. The input image, baseline asset directory,
collector build directory and fixed plan inventories agree before/after the
entire operation.

The separate fresh package inspection identifies this exact seed:

| Artifact | SHA-256 |
| --- | --- |
| Seed database | `e3559efe1e2920ef3880e73f9ae387ae856256dc71ba1c4aabe9e3004c46428a` |
| Seed provenance manifest | `4783c97a24747b93381d14ce54b2562d315806e5384daa746b13bac77f73c985` |
| Complete package | `9c4bf9271bccc43396ba2d0e2e567daf3dfdc5e985c2690f0accbd41ec78adea` |
| Fresh inspection | `8ecacba4ff050990ce767e544984db3877e0e0a2cfaad8c2b2bfd97c1d12f922` |

Thus both real-run unions match the exact packaged seed. Inspection and hash
equality connect the standalone full-description comparison to the packaged
bytes; no learned runtime database is substituted for bundled membership.
The complete package is 1,521,287,168 bytes. Its unchanged 01.24 program uses
build `35a453336a0e4b0d432c` and the matching ELF recorded in [candidate.json](candidate.json).

The private Windows handoff is `PSWaker-01.24-asset-inventory-150`, with the
complete package, matching ELF, seed assets, frozen plan/manifest, reports and
bounded console instructions. Package/ELF/seed hashes were checked after copying.
Exact private commands/settings, collector build inputs and all original run
reports/logs remain in the `asset-inventory-150` artifact group. Earlier inputs
and the previous default assembly asset were not replaced.

The full reference-enabled WSL suite passes **264 tests with 60 platform/environment
skips**, including the real-tool batch-to-package test and ten initialized-renderer
startup checks. Focused final manifest/resource rejection checks, Pyright, Python
compilation, shell syntax checks and the native collector build pass. Independent
Standards and Spec reviews each returned **zero actionable findings**; this record
supplies the repeat/comparison evidence that was pending when they reviewed.

This is generated asset/material evidence. The 67 unsupported and 48 missing
rows, 1,264 out-of-boundary archives, separately owned dynamic paths and new
candidate PS4 observations remain explicit gaps. No generated row is physically
verified, no earlier console result transfers to the changed seed, and no
outstanding #149/#157 observation is waived. Use the
[bounded console selection](../../../docs/ps4/Asset-inventory-checklist.md)
for the next physical work; no story progression is required.
