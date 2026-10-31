# Private complete packages

Issue [#16](https://github.com/Jcanotorr06/pswaker/issues/16) adds Linux/WSL2
preparation of an owner-built complete package. The game image installs at the
approved fixed path **`/app0/game.iso`**. Runtime and save locations stay fixed.
Validated pipeline-description seeds are required game assembly assets described below;
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
A [program release](#relocatable-program-release) removes that path requirement
for later assembly.

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

## Relocatable program release

Issue [#40](https://github.com/Jcanotorr06/pswaker/issues/40) separates the
prebuilt program from the developer build that produced it. A maintainer derives
a **program release** once, on the build machine; whoever later assembles a
complete package receives only that release. It needs neither the original
build path nor a port compilation:

```bash
python3 tools/pswaker/complete-package.py release-program \
  --platform-root "$PLATFORM_ROOT" \
  --program-stage "$GAME_ROOT/build/program-stage" \
  --elf "$GAME_ROOT/build/switchwaker" --kind game \
  --output /private/new-program-release

python3 tools/pswaker/complete-package.py assemble \
  --platform-root "$PLATFORM_ROOT" --program /any/location/program-release \
  --kind game --app-version 01.00 \
  --image '/path/to/owner/GZLE01.iso' --output "$PRIVATE_ROOT/game-complete-01.00"
```

`release-program` first verifies the developer build exactly as `assemble
--program-stage/--elf` does, so the ELF must still be at its original path. It
then converts the same ELF again from its **bare filename**, so the SELF's
`DT_SCE_FILENAME` holds `switchwaker` rather than a developer path. Converting
from that filename gives identical bytes in any directory. The release stage
records the new `eboot_sha256`, plus `program_release` with the converter input
and the verified developer SELF hash. The release is accepted only after it
verifies exactly as assembly will verify it. The data-free release contains
exactly:

- `program-release.json`: kind, build identity, ELF/SELF hashes, every stage
  file hash, converter input and SHA-256, the verified developer SELF/payload
  hashes and tool provenance. It contains no build paths and has
  `distribution_cleared: false`;
- `stage/`: the program staging allowlist above;
- `elf/<name>`: the matching unstripped ELF.

The release directory can be moved or copied anywhere. `assemble --program`
replaces `--program-stage/--elf`; giving both forms, or neither, is an error.
Before packaging, assembly rejects any extra or missing release entry, any stage
file or ELF that differs from the manifest, a different converter and a kind
mismatch. Changing the release manifest's `kind` alone cannot relabel a
diagnostic, because its `build-info.json` must also agree. Integrity checks
remain enabled: the ELF must still reproduce the shipped SELF byte for byte
from a private copy. A tampered ELF, or a genuine SELF converted elsewhere such
as the developer build's SELF, is rejected even when the manifest hashes are
rewritten to match. `assembly.json` records the release location and the
program's `release` identity. Application/content IDs, installed image path,
image contract and output rules are unchanged.

The release manifest is **not signed**. These checks catch changed, mixed or
inconsistent payloads, but not a deliberately rewritten build manifest with a
reconverted SELF. The recorded developer hashes are provenance for comparing
against build evidence; assembly cannot re-verify them without the developer
build. Obtain releases only from the maintainer's own verified preparation.

A program release is still a private build artifact. The converter, packager and
tool provenance come from `--platform-root`, so this remains the Linux/WSL2
workflow. Whoever assembles still needs that prepared tool root, though no port
build. Bundling the tools with the desktop application is later #39 work.
It does not establish native Windows operation, a desktop
application, console acceptance for a newly converted SELF, or redistribution
clearance. Earlier console evidence for a developer SELF does not carry over to
its release SELF.

## Packaging operation boundary

`create_package(request, observe)` in `complete-package.py` is the single
operation behind `assemble`, for use by a later desktop adapter. A
`PackageRequest` names the image, the `Program` (a release, or a developer stage
and ELF), kind, version, tool root, output and verified assembly assets. The
operation runs these stages in order:

| Stage | Covers |
| --- | --- |
| `validate` | absent output outside the repository, version format, full image validation, existing output parent |
| `verify-program` | tool provenance; program snapshot and allowlist; kind; release manifest; ELF → SELF reproduction |
| `assemble` | image copy and revalidation, manifest, packager, payload/SFO checks |
| `inspect` | fresh extraction against program, image and application identities |
| `publish` | remove private staging, recheck the output is absent, rename the inspected result |

`observe` receives `{"stage", "event": "started"}`, then either `passed` or
`failed` with measured `seconds`. A failure also includes its `error` message,
and `StageFailure.stage` names the failed stage. `assemble --progress` writes
the same events as JSON lines to stderr. Its stdout result and the final
`complete-package:` error line are unchanged. The output directory appears only
after `inspect` passes. The source image is only read. A non-empty existing
output, such as a completed package, is never replaced. On success,
`stages.json` keeps the measured durations of the first four stages.

## Required pipeline-description seed

Every `assemble --kind game` includes a validated, standalone
`/app0/initial_pipeline_cache.db` automatically. The fixed private asset directory
defaults to `PLATFORM_ROOT/assembly-assets`; maintainers may locate the same
verified inputs elsewhere with `--assembly-assets /private/validated-seed`.
There is no player performance flag or shader selection. Missing, empty, corrupt,
changed or renderer-incompatible seeds fail assembly before publication. Existing
completed output is retained. Diagnostic packages are not the game acceptance target;
their optional `--pipeline-cache` input remains available for diagnostics only.

The standard asset is the retained 287-description seed SHA-256
`7e3f8527203dc488b5ae646904c986ac596d7d4017db45a0fcb18ae29de51dc1`, with asset
manifest SHA-256 `e8d4b523aa45f58e272ccde4c258d76388200e26f28a9060b804f9969b4493fb`.
The [accepted Outset capture](../../evidence/ps4/action-baseline-108/OWNER-DECISION.md)
and [reproducible coverage/delivery record](../../evidence/ps4/outset-coverage-111/README.md)
establish that all 259 recorded configurations are already present byte for byte;
zero descriptions were added and all existing compatible descriptions remain.
Use this same private asset for the CLI default directory and Windows app/installer
`--assembly-assets` inputs. Owners need no prerequisite gameplay capture. This
bounded configuration comparison does not establish gameplay smoothness.

To prepare a replacement, supply the adjacent `pipeline_cache.db-wal` if present and keep the
application closed during retrieval. The preparation CLI copies the database/WAL
before opening SQLite, checks integrity and the
selected renderer's schema/version/size contract, and backs up their committed
view into a DELETE-journal database. It checks the originals stayed unchanged.
The runtime's optional `aurora_seed` merge identity is validated and omitted from
the output. Unsupported configurations, unrelated schema objects and empty seeds
are rejected rather than silently discarding records. Renderer-target compile-time
assertions guard the clear/GX ABI declared by the preparation tool.

To prepare and inspect that snapshot without assembling a complete package:

```bash
python3 tools/pswaker/complete-package.py pipeline-seed /private/pipeline_cache.db \
  --output "$PLATFORM_ROOT/assembly-assets"
```

The new private directory contains `initial_pipeline_cache.db` and
`pipeline-seed.json` with source hashes, configuration counts and seed SHA-256.
Existing prepared seeds are compatible. Assembly verifies the seed against its
asset manifest and selected renderer contract, copies those exact standalone
bytes, and preserves original database/WAL provenance. It binds the seed size,
SHA-256, configuration counts and asset-manifest SHA-256 to `complete-package.json`
and `assembly.json`; fresh extraction revalidates the installed bytes and counts.
Neither preparation nor assembly modifies source databases or WAL files.
The seed is a separate asset;
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

The Windows maintainer supplies this same directory to `build-desktop.py` or
`build-installer.py` with required `--assembly-assets`. It is shipped beside
`program`, `packaging` and `platform` as `assembly-assets` and included in the
verified desktop inventory. The normal owner flow selects only the image and
output location; it includes and freshly inspects the seed automatically. A
program release and a program package remain data-free and do not contain this
private asset. Rebuild the private desktop bundle when changing the seed.

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
  identity. The extracted `build-info.json` must name the same SELF hash, kind
  and build identity as the verified program. A failed reinspection removes the
  previous success report.
- `stages.json`: measured `validate`, `verify-program`, `assemble` and
  `inspect` durations for this assembly.
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
python3 -m unittest discover -s tests/ps4 -p test_complete_package.py -v
PSWAKER_REFERENCE_BUILD="$HOME/.cache/pswaker/maintained-15-a" \
  python3 -m unittest discover -s tests/ps4 -p test_complete_package.py -v
python3 -m compileall -q tools/pswaker tests/ps4
```

The tests generate tiny synthetic DOL/REL/FST/Yaz0/RARC structures and copy the
CLI into an isolated temporary repository with a synthetic hash contract.
The actual CLI's production contract is also exercised and rejects that tiny
image. No production test flag, alternate-contract argument, game fixture or
decryption key is introduced. Real packaging tests use the explicit diagnostic
ELF/stage, real converters/packager and synthetic image, checking extraction,
nonplayable labelling, stable IDs across versions and rejection behavior.
Relocation tests convert the reference diagnostic ELF in a temporary developer
build and derive a release from it. They delete that build and move the
release before assembly and fresh inspection, and check the stage events. They
also cover tampered and rehashed releases, a developer SELF substituted for the
release SELF, and diagnostic-to-game relabelling.

The owner's PAL `GZLP01` image is rejected with a USA-region instruction.
The subsequently supplied full USA `GZLE01` revision-0 image passed production
validation and real private assembly with the explicit #15 diagnostic payload,
followed by independent fresh-extraction inspection. See the
[owner-image verification](../../evidence/ps4/private-package-16/OWNER-USA.md) for hashes,
the exact fingerprint correction and evidence limits. The complete package
remains private and NONPLAYABLE. There is no console-startup or playable result
in #16; installed game content is checked with an actual game program in #17.
