# Required seed delivery (#109)

Recorded 2026-10-30. Host packaging and inspection evidence only; no console
performance or Outset action-coverage acceptance is claimed.

## Private game package

The ordinary Linux/WSL2 `complete-package.py assemble --kind game` path produced
and freshly extracted a complete package from the existing verified 01.19 game
program and owner's supported image. No `--pipeline-cache` or shader opt-in was
supplied. The prepared platform root carried the existing validated seed at its
default `assembly-assets` location. Existing completed packages were retained.

The private output is retained as `seeded-109-complete-01.19` under the existing
private artifact root, together with `assembly.json`, `inspection.json`, tool
logs, command history and matching ELF. Its platform input is retained as
`seeded-109-platform`; the original prepared seed is `performance-22-seed-01.13`.
No actual seed, image, package or private input paths are committed here.

| Identity | Value |
| --- | --- |
| Program build ID | `48d0196e605f00284b21` |
| Package filename | `IV0000-PSWK00001_00-PSWAKERGAME00000.pkg` |
| Package SHA-256 | `e5f82d4294b508cd1c866a1f2dee7a9a358bbe9c849a1ba3bbb2536895477ed5` |
| Installed seed | `/app0/initial_pipeline_cache.db` |
| Seed bytes | 1,200,128 |
| Seed SHA-256 | `7e3f8527203dc488b5ae646904c986ac596d7d4017db45a0fcb18ae29de51dc1` |
| Asset manifest SHA-256 | `e8d4b523aa45f58e272ccde4c258d76388200e26f28a9060b804f9969b4493fb` |
| Descriptions | 287: one type 0/version 5/8-byte configuration; 286 type 1/version 13/2772-byte configurations |
| Assembly report SHA-256 | `db690dd50ec8c93d854bab2aeb7d33e60fbc4556dbc2563f661b603415022aaa` |
| Inspection report SHA-256 | `e8870caeab12b69f707f4f8bc55a972be4a1d715c5115b2e2009b7d38dfab191` |

The extracted seed's SHA-256, byte size and database records matched the embedded
complete-package manifest. The original database/WAL provenance from the seed
asset survived in both the embedded manifest and inspection report. A bytewise
comparison confirmed the original prepared seed and its assembly asset copy
remained identical after packaging. Preparation's existing database/WAL snapshot
and source-immutability tests remain in place.

For independent reinspection, use the retained private artifact root:

```bash
python3 tools/pswaker/complete-package.py inspect \
  "$PRIVATE_ROOT/seeded-109-complete-01.19" \
  --platform-root "$PRIVATE_ROOT/seeded-109-platform"
```

## Public workflow regression evidence

The tests use synthetic descriptions and images in isolated repositories, with
the real selected Linux and native Windows packaging tools. The production
content contract still rejects synthetic images.

- The CLI game assembly/release round trip includes the default seed and verifies
  its extracted identity, counts and original provenance without an opt-in.
- Normal Windows desktop controls select an image and output, validate, create,
  and reach **Package verified** with the seed bound to the extracted payload.
  Missing required seed bytes instead produce an actionable failure and no
  published package.
- Required-input cases cover missing, empty, corrupt and incompatible databases,
  changed hashes/counts/provenance, and malformed asset manifests. Existing
  completed output and source inputs are preserved.
- Real package rebuilds remove the seed manifest or change its hash, counts or
  byte size while updating the outer package/report inventories. Fresh inspection
  rejects those inconsistencies and removes the prior success report.
- Replacing the seed while retaining identical program bytes changes the seed,
  asset-manifest and complete-package identities. Tests compare counts to their
  generated source asset rather than requiring the real seed's fixed count.

The first new Windows inclusion assertion failed with `KeyError: pipeline_seed`
before implementation. The missing-manifest inspection case also initially
passed incorrectly; it now fails inspection as required. Both regression tests
passed after the corresponding changes.

## Validation results

- Full Linux/WSL2 suite: 211 tests, 100 environment/platform skips, no failures.
  Real reference packaging was enabled; the complete-package file separately
  passed all 32 tests with its one Windows-interop skip.
- Native Windows: all 26 desktop tests, 20 workflow tests, 21 package tests and
  the Windows tool-preparation test passed. The CLI and Windows required-input
  tests were rerun after the malformed-metadata repair and passed.
- A synthetic private desktop build through `build-desktop.py --assembly-assets`
  succeeded with the pinned PyInstaller; the built executable's
  `--check-installation` verified its complete installed closure successfully.
- The real installer test passed its install, installed-UI package creation,
  update and uninstall cycle, preserving owner files. The initial run exited
  while the UI automation was opening the destination picker; an unchanged
  retry passed both installed versions. Both logs are retained privately;
  the initial failure is not treated as a pass.
- Pyright: zero errors or warnings. Python compilation and all maintained shell
  syntax checks passed.
- Standards review: zero findings. Spec review: zero remaining findings after
  repairing the actionable malformed-metadata error.

A separate `inspect` invocation freshly extracted the retained real package
again with the final validator and reproduced the inspection report SHA-256
above. The full logs remain in the private validation/artifact workflow.
