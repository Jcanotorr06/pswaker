# Private complete packages

Issue [#16](https://github.com/Jcanotorr06/pswaker/issues/16) adds Linux/WSL2
preparation of an owner-built complete package. The game image installs at the
approved fixed path **`/app0/game.iso`**. Runtime and save locations stay fixed.
Optional pipeline-description seeds are preparation assets described below;
assembly introduces no console checkpoint.
Game startup and installed-content failure handling belong to #17.

The program build remains [disc-free](README.md). Do not give a disc image to
`clean-build.sh`, or add game bytes to public source, program packages, tests or
logs. Complete packages are private and must be assembled **outside this Git
repository**. Nothing in this workflow publishes them.

## Validate the owner's image

Run from the repository root in the selected Linux/WSL2 environment. Quote paths
containing spaces. The validator uses Python 3.11+ and its standard library;
the maintained host provides Python 3.12.

```bash
python3 tools/pswaker/complete-package.py validate '/path/to/owner/GZLE01.iso'
# A raw .gcm is also accepted, including uppercase extensions.
```

Only the full, unmodified USA GameCube **GZLE01, disc 0, revision 0** raw image
is supported: 1,459,978,240 bytes, with an exact full-image SHA-1 allowlist.
Scrubbed, compacted, compressed and other container
formats are unsupported even if renamed `.iso`. Export a full raw ISO/GCM from
the owner's original disc instead. A PAL `GZLP01` image is rejected; renaming
the file or changing its disc label does not make its content supported.

Validation checks the header, identity/revision, full size, FST hierarchy and
file bounds, DOL section/file bounds, and the pinned content hashes. The eight
required objects are `sys/main.dol`, five standalone RELs, and two RELs inside
`RELS.arc`. Yaz0-compressed required files, archives and members are expanded
only in bounded host memory for checking, never rewritten into the image.
Finally the entire image must match an allowlisted SHA-1. Every accepted image also
gets a SHA-256 for artifact association. No timestamp/path validation cache is
trusted, and there is no CLI switch to change the production content contract.

`content-contract.json` comes from
SwitchWaker `ba8d0a31446cd53ceaebd6b7269cca641e73bf4c` and the decompilation it
names in `game/UPSTREAM`, `snrubrm/tww@b09eebc39852e18397031d9a563a8eae124f21f1`.
It uses the same module selection as `gen_asset_stubs.py`: main.dol and every
REL with extracted arrays (163 arrays total). Only upstream paths, hashes and
counts are committed; no disc-derived bytes or keys are needed. To reproduce
the contract from its four checksum-locked public source files (network and
PyYAML required only for this maintenance command):

```bash
python3 tools/pswaker/prepare-content-contract.py /tmp/pswaker-content-contract.json
diff -u platform/ps4/content-contract.json /tmp/pswaker-content-contract.json
```

The full-image allowlist retains the pinned upstream oracle's
`0289e70f470dc758c73be9b8bcd8c865fb82d8ae` and the independently catalogued
USA/Canada retail disc's `6b5f06c10d50ebb4099cded88217eb71e5bfbb4a`.
The latter comes from [disc catalogue entry 1086](https://redump.info/disc/1086),
corroborated by [GameTDB GZLE01](https://www.gametdb.com/Wii/GZLE01), checked
2026-10-24 and recorded in `additional_images`. These are two explicit whole-image
fingerprints, not permission to accept arbitrary data with a matching label.
Both must pass the same unchanged upstream DOL/REL hashes, identity/revision,
structure and size checks. The cause of the difference between the two full-image
fingerprints is not established; no byte equivalence between them is claimed.

## Assemble with an explicit program

Use an already prepared, inspected platform build root from #15. This does not
rebuild the renderer or borrow an unrelated packager. Supply both the original
unstripped program ELF and its data-free staging directory explicitly.

The current diagnostic can exercise assembly, but the result is
**NONPLAYABLE**. With a supported owner image, substitute existing local paths:

```bash
PLATFORM_ROOT="$HOME/.cache/pswaker/maintained-15-a"
PRIVATE_ROOT="$HOME/.local/share/pswaker-private"
mkdir -p "$PRIVATE_ROOT"

python3 tools/pswaker/complete-package.py assemble \
  --platform-root "$PLATFORM_ROOT" \
  --program-stage "$PLATFORM_ROOT/build/probe-stage" \
  --elf "$PLATFORM_ROOT/build/probe/platform_diagnostic" \
  --kind diagnostic --app-version 01.05 \
  --image '/path/to/owner/GZLE01.iso' \
  --output "$PRIVATE_ROOT/diagnostic-complete-01.05"

# Fresh extraction and validation; does not need the original source image.
python3 tools/pswaker/complete-package.py inspect \
  "$PRIVATE_ROOT/diagnostic-complete-01.05" --platform-root "$PLATFORM_ROOT"
```

Choose an absent output directory under an existing private parent. The CLI
validates the original image before packaging, snapshots the program, copies
and revalidates the staged image, and requires the exact same image hashes.
It runs the selected SDK `create-fself`, the retained OELF segment check, and
the selected DolphinPS4 `make-pkg.sh` with the source-built patched LibOrbisPkg
override. Extra modules are disabled. Its GP4 is generated by the selected SDK
`create-gp4`. The exact ELF must reproduce the staging directory's SELF before
assembly continues. The pinned converter embeds the **full original input
path** in `DT_SCE_FILENAME`, so keep the ELF at its original build path when
checking that byte identity. The output retains a separate matching ELF copy.

The program staging directory must contain exactly:

- `eboot.bin`, `build-info.json`;
- `sce_sys/icon0.png`, `sce_sys/param.sfo`, `sce_sys/about/right.sprx`;
- `sce_module/libSceFios2.prx`, `sce_module/libc.prx`.

No symbolic links or additional payload files are accepted. The program
manifest must record `eboot_sha256` and a build identity present in the ELF:
`diagnostic_build_id` for diagnostics, `program_build_id` for a future game
program. A diagnostic manifest cannot be passed as `--kind game`. The allowlist
is the current selected payload closure; review any future additions explicitly.

Application identity is fixed by program kind and independent of the image,
version and build hashes. These values are compatibility contracts for later
update tests:

| Program | Title ID | Content ID | Package title |
| --- | --- | --- | --- |
| Diagnostic | `PSWK00010` | `IV0000-PSWK00010_00-PSWAKERPROBE0000` | PSWaker Diagnostic NONPLAYABLE |
| Game | `PSWK00001` | `IV0000-PSWK00001_00-PSWAKERGAME000000` | PSWaker |

`--app-version NN.NN` is explicit and changes version metadata, never those IDs.
The separate game identity prevents a diagnostic from replacing the game.
The [startup game build](GAME-STARTUP.md) supplies an integrated program for #17.
`--kind game` identifies an explicitly supplied program; it grants no game,
hardware or performance acceptance.

## Optional pipeline-description seed

For a performance candidate, `assemble --pipeline-cache /private/pipeline_cache.db`
adds a validated, standalone `/app0/initial_pipeline_cache.db`. Supply the adjacent
`pipeline_cache.db-wal` if present and keep the application closed during retrieval.
The CLI copies the database/WAL before opening SQLite, checks integrity and the
selected renderer's schema/version/size contract, and backs up their committed
view into a DELETE-journal database. It checks the originals stayed unchanged.
The runtime's optional `aurora_seed` merge identity is validated and omitted from
the output. Unsupported configurations, unrelated schema objects and empty seeds
are rejected rather than silently discarding records. Renderer-target compile-time
assertions guard the clear/GX ABI declared by the preparation tool.

To prepare and inspect that snapshot without assembling a complete package:

```bash
python3 tools/pswaker/complete-package.py pipeline-seed /private/pipeline_cache.db \
  --output /private/new-seed-directory
```

The new private directory contains `initial_pipeline_cache.db` and
`pipeline-seed.json` with source hashes, configuration counts and seed SHA-256.
Assembly performs the same snapshot itself; pass the original database/WAL pair
to preserve its provenance in the package manifest. The seed is a separate asset;
the data-free program staging allowlist above stays unchanged. Fresh package
inspection validates the extracted seed's bytes and configuration counts against
`complete-package.json`. Package/seed hashes distinguish different preparation
assets even when executable code is identical. Never transfer a previous package's
performance verdict to a different seed or cache state.

The seed contains pipeline descriptions, not driver shader binaries. The existing
renderer compiles known pipelines before gameplay. Cold disposable caches still
start empty; preparation and its duration remain visible startup work. This does
not guarantee coverage of every future draw/effect or a console performance pass.
Keep actual seeds and complete packages private.

## Inspection and retained private evidence

Only after a fresh extraction passes does the temporary directory become the
requested output. Failure leaves no completed output directory or package.
The private directory uses owner-only permissions on Linux. Budget disk space
for the image, package and fresh extraction (at least 5 GB free, plus program
artifacts); the small synthetic tests do not establish full-image throughput.

Retained files include:

- `out/*.pkg`: private complete package; never publish it.
- `assembly.json`: original input paths, replayable top-level command, exact
  tool/script/source-closure hashes, payload hashes and output identity/hash.
- `commands.json`, `tools.log`: invoked tool arguments and build/inspection logs.
  Temporary stage paths in the detailed log are historical; replay the
  `assembly_argv` with a new output directory to assemble again.
- `inspection.json`: outer PKG header identity/size, SFO application/content
  IDs, title, version and launch metadata, exact extracted file inventory,
  per-file hashes, required-content checks, image hash and matching ELF/SELF
  identity. A failed reinspection removes the previous success report.
- `elf/`, `self/`, `elf-sections.txt`: matching unstripped ELF and converter/OELF
  artifacts. These must remain associated with this package's own hashes.

The packager adds `PUBTOOLINFO` (creation date/image sizes) and `PUBTOOLVER` to
the SFO. Those generated values and the actual packaged SFO hash are recorded
separately; all preexisting application fields must survive unchanged.
Repeatable commands do not imply byte-identical packages across timestamps.
Inspection never reuses an earlier extraction, checks both the outer header
and SFO identity, and rejects extra files or mismatched executable/image hashes.
The package contains `complete-package.json` with the same image/program identity
and nonplayable/unverified status. No console result is claimed.

Both complete-package metadata and reports mark distribution as uncleared.
Retain the source build's notice corpus and provenance audit alongside the
private result. Review the **actual combined artifact**, including its program,
game content, SDK modules and inherited licenses/notices before any distribution;
[LICENSING.md](LICENSING.md) records unresolved module/stub rights. Successful
assembly is neither licensing clearance nor first-playable acceptance.

## Data-free verification and current limits

Tests stay at the existing preparation and artifact-inspection CLI boundaries:

```bash
python3 -m unittest discover -s platform/ps4/tests -p test_complete_package.py -v
PSWAKER_REFERENCE_BUILD="$HOME/.cache/pswaker/maintained-15-a" \
  python3 -m unittest discover -s platform/ps4/tests -p test_complete_package.py -v
python3 -m compileall -q platform/ps4
```

The tests generate tiny synthetic DOL/REL/FST/Yaz0/RARC structures and copy the
CLI into an isolated temporary repository with a synthetic hash contract.
The actual CLI's production contract is also exercised and rejects that tiny
image. No production test flag, alternate-contract argument, game fixture or
decryption key is introduced. Real packaging tests use the explicit diagnostic
ELF/stage, real converters/packager and synthetic image, checking extraction,
nonplayable labelling, stable IDs across versions and rejection behavior.

The owner's PAL `GZLP01` image is rejected with a USA-region instruction.
The subsequently supplied full USA `GZLE01` revision-0 image passed production
validation and real private assembly with the explicit #15 diagnostic payload,
followed by independent fresh-extraction inspection. See the
[owner-image verification](../../evidence/ps4/private-package-16/OWNER-USA.md) for hashes,
the exact fingerprint correction and evidence limits. The complete package
remains private and NONPLAYABLE. There is no console-startup or playable result
in #16; installed game content is checked with an actual game program in #17.
