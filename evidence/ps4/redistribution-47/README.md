# Inherited program audit evidence (#47)

Read the [audit outcome](../../../docs/ps4/INHERITED-PROGRAM-AUDIT.md) and
[upstream findings](../../../docs/research/inherited-program-rights.md) together.
Distribution is uncleared and #47 remains open. This checkpoint adds no native
candidate, changes no maintained build inputs and grants no installer release.

## Collection

The 2026-10-27 collection used the existing WSL Ubuntu build host and these
read-only retained roots under `/home/joseph_cano/.cache/pswaker/`:

- `maintained-15-a`: platform, SDK, checked downloads, source trees, local diffs,
  notices, compile records and earlier platform inspection.
- `game-23-a`: game source archives, prepared source trees, exact build-input
  record, native build, unstripped ELF and seven-file data-free program stage.
- `source-23-a`: historical repository snapshot; every one of its 142 recorded
  port inputs was rehashed against the game build's actual input manifest.

Run from any directory, providing a **new** output directory:

```bash
python3 /path/to/pswaker/evidence/ps4/redistribution-47/collect.py \
  /path/to/pswaker \
  /home/joseph_cano/.cache/pswaker/maintained-15-a \
  /home/joseph_cano/.cache/pswaker/game-23-a \
  /tmp/pswaker-audit-47-new \
  --source-snapshot /home/joseph_cano/.cache/pswaker/source-23-a
```

`collect.py` writes metadata and notice texts only. It fails on provenance
mismatches and unexpected staged files. It neither packages nor copies modules,
ELF/SELF, SDK stubs, complete packages, game data or keys. The successful output
was copied into `checked/`. The additional `maintained-inputs.json` records the
current checkout through `build_inputs.maintained_inventory()` and is compared
again during final validation. The collector is checkpoint evidence rather
than a maintained build command.

## Record interpretation

| Record | Meaning and limit |
| --- | --- |
| `checked/program.json` | Rehashed ELF/SELF and exact data-free stage. This does not inspect a new complete package. |
| `checked/modules.json` | Byte equality of three staged/SDK/archive modules and inventory of published module source candidates. Archive inclusion supplies provenance, not permission or source correspondence. |
| `checked/import-stubs.json`, `checked/elf-dynamic.txt` | Nine direct ELF imports; stub bytes match both the locked package and original game input record. The release pool and PacBrew override retain separate provenance. |
| `checked/link-rule.txt`, `checked/link-inputs.json` | Native link rule and library argument order with actual hashes. This is not a linker map of extracted archive members; individual object response files remain private in the retained build tree. |
| `checked/retained-downloads.json` | 51 checked SDK/source/dependency downloads. These are existing private retained files, not a published corresponding-source bundle. |
| `checked/retained-source-snapshot.json` | Exact historical port files, including ordered patch declarations, patches, provenance, host/input locks and scripts. |
| `checked/retained-records.json` | Hashes of original preparation, build-input, local-adaptation, patch-application, license and compile records. Preserve those records and their source trees. |
| `checked/notice-index.json`, `checked/notices/` | 126 checked source notice records, 96 distinct original texts. No replacement project license or assertion of complete per-file coverage. |
| `checked/tools.json` | Actual collector/interpreter/inspection tool identities. The original candidate's tool closure remains in its retained host/input records. |
| `module-source-inspection.json` | Read-only SELF code/data comparison with published source candidates; see the upstream report for findings and limits. |
| `inspect_module_sources.py` | Reproduces bounded SELF inspection with Linux `objdump`: `python3 inspect_module_sources.py PLATFORM_ROOT OUTPUT_JSON`. Extracted segment bytes exist only in temporary scratch directories. |
| `module-source-candidates.json`, `module-source-candidates/` | 22 exact source/notice files at immutable revisions, including the historical libc example, right text/logo source, SPRX template and CRT metadata. Original license text remains with each source revision. |
| `upstream.json` | Selected read-only GitHub API facts: tag, release, file histories, commits and tree/license inventory. Immutable source links and interpretations live in the upstream report. |
| `source-validation.json` | All 22 exact source/notice files rehashed, bounded module inspection independently reproduced, and all 160 maintained inputs unchanged. |
| `REVIEW.md` | Independent standards/spec review, corrected wording finding and the two unresolved acceptance requirements. |

The public bundle excludes the private archive/tree bytes. Preserve existing
private source archives, prepared trees, Git dependency commits, generated local
diffs and the historical repository snapshot alongside these records. If a
later permitted distribution requires corresponding-source delivery, assemble
and verify that exact source set and supply it by the selected terms' required
method. Do not call this metadata/notice bundle corresponding-source delivery.

No inherited binary or implementation was replaced, removed or rebuilt for this
checkpoint. New source/grant evidence can narrow the unresolved list; changing
native inputs requires the build/inspection/hardware renewal described in the
audit. Final Windows installer/tool/desktop closure remains a separate gate.

## Validation

`full-suite.log` records 143 discovered cases: 101 passed, 42 Windows/tool
prerequisite skips, zero failures/errors (165.770 seconds). Existing reference
platform, prepared game and host SDL roots were supplied read-only; synthetic
fixtures, native harnesses and package round trips use temporary work areas.
`focused-inputs.log` records seven passing input-ownership tests. A separate
focused real package round trip passed both cases. No product behavior changed;
existing public-boundary coverage was reused rather than adding implementation
tests for documentation.

`typecheck.log` records zero errors/warnings. `host-validation.json` records
notice rehashing, JSON parsing, checkpoint Python syntax and local documentation
links. `validation.json` records the suite outcomes and confirms the 160 current
maintained inputs remain unchanged. These host checks establish neither new
hardware results nor public redistribution rights.
