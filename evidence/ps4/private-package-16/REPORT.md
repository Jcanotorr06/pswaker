# Private complete-package preparation (#16)

Initial host implementation and data-free verification completed on 2026-10-24.
The later [owner USA-image verification](OWNER-USA.md) supersedes the pending
real-image status in this initial report and records the private package hashes.
**At the initial review, no supported USA owner image had been supplied for
positive production validation/assembly, and no game-containing complete package
had been produced.**
The available owner's image is PAL `GZLP01` and is correctly rejected with:

```text
complete-package: Wrong game/region/revision (GZLP01 revision 0); supply USA GZLE01 revision 0 (disc 0)
```

Both production `validate` and `assemble` returned exit 1. The absent requested
private output directory remained absent: no package was produced for that input.
The source image was opened read-only and was not modified.

## Implementation and inputs

Implementation commit `c77b359` is based on
`develop@f99ac2a579796590f533b6b50ebce8a41c795aa0`.
The follow-up commit containing this report preserves tool-command history
across standalone inspection and records its regression check and reviews.

The new CLIs and [workflow](../../../docs/ps4/COMPLETE-PACKAGES.md) preserve the data-free
program build. Host validation checks raw ISO/GCM identity, structure and the
pinned DOL/REL/full-image content contract. Assembly accepts explicit ELF/stage
inputs, uses the selected ELF/SELF/GP4/PKG path, installs the image at
`/app0/game.iso`, and verifies fresh extracted payload/metadata/header hashes
before exposing a completed private output directory. Application IDs remain
stable across versions. Diagnostic outputs are explicitly NONPLAYABLE.

Content-contract regeneration fetched four public source files with committed
SHA-256 checks, reproducing the committed JSON exactly (comparison as parsed
JSON). Sources are SwitchWaker
`ba8d0a31446cd53ceaebd6b7269cca641e73bf4c` and its recorded decompilation
`snrubrm/tww@b09eebc39852e18397031d9a563a8eae124f21f1`.
The 163-array contract requires main.dol plus seven REL objects, two inside
RELS.arc. No game data or keys were used to generate the contract.

Real-tool tests used the retained #15 build A (`maintained-15-a`) and its
explicit data-free diagnostic program:

| Input | SHA-256 |
| --- | --- |
| Unstripped diagnostic ELF | `f97123d555dfef871de7483140aa84b738696b397afdc9a54cd95fd20e6d0d84` |
| Diagnostic SELF | `f62940819abeb92ea4af228442f8fb83c00a33199861b1e38b78e9b20e9ffd7a` |

Tests reproduce that SELF from the original ELF path using the selected SDK
converter, OELF check, selected DolphinPS4 packaging script and source-built
patched LibOrbisPkg. No new target dependencies or diagnostic binaries were
built, and no earlier console result was attributed to a new package.

## Verification

The final full suite ran once after the implementation and review correction:

```bash
PSWAKER_REFERENCE_BUILD="$HOME/.cache/pswaker/maintained-15-a" \
  python3 -m unittest discover -s platform/ps4/tests -v
python3 -m compileall -q platform/ps4
for script in platform/ps4/*.sh; do bash -n "$script"; done
```

**20 tests passed, no skips**; see [complete test output](host-checks.log).
Python compilation and every shell syntax check passed. The new focused file's
12 checks were also run during implementation, including real packaging.
Observed failing regressions were corrected for renamed compressed inputs,
outer PKG content-ID validation and command-history retention.

The generated-image cases cover raw ISO/GCM acceptance, wrong region/revision/
disc, size and file-range errors, required DOL/REL mismatches, nested Yaz0/RARC
content, renamed compressed input and full-image mismatch. Real-tool cases
cover explicit program/ELF matching, rejection of additional payload files,
diagnostic labelling, fresh package inspection, header/hash corruption,
retention of assembly commands after reinspection, and stable identity across
versions 01.05 and 01.06. Existing preparation/renderer/program-package tests
also passed. Tests observe preparation and package CLIs, not parser internals.

All accepted-image tests used a generated 32 KiB synthetic image and a
**separately copied CLI with a synthetic contract**, in temporary directories.
The unchanged production CLI rejects that image. There is no production
alternate-contract flag or acceptance bypass. Synthetic test packages and
extracted data were temporary and contained no game data; none were committed
or published. No game data or keys are in this report or test log.

## Limits and handoff

At this initial checkpoint, positive production-contract validation and private
assembly of the owner's actual supported USA GZLE01 revision-0 image remained
unverified. The subsequent supplied image, fingerprint correction, real
assembly and fresh inspection are recorded in [OWNER-USA.md](OWNER-USA.md).
Synthetic small-image tests do not establish full-image performance, installed
game startup or playability.

There is no console checkpoint in #16. #17 verifies installed game content and
startup with an actual game program. Save/settings behavior, installed update
preservation, game audio/rendering and performance retain their later gates.
Successful host assembly does not clear distribution: retain and review the
actual combined licenses, notices and source/module provenance described in
[LICENSING.md](../../../docs/ps4/LICENSING.md). Private complete packages must not be published.
