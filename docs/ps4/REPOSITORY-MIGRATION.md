# Repository ownership migration verification

Issue [#54](https://github.com/Jcanotorr06/pswaker/issues/54) reorganizes source
ownership without changing the game or attributing previous console results to
new builds. [Recorded comparisons and test logs](../../evidence/ps4/repository-54/)
retain the pre-migration inventory and protected-file hashes.

| Owner | Contents |
| --- | --- |
| `tools/pswaker/` | Maintained host commands and the shared input/location owner |
| `platform/ps4/` | Runtime integration, diagnostic/preflight source, CMake/toolchain data, locks, patches, provenance and notices |
| `tests/ps4/` | Python tests, native harnesses and synthetic fixtures |
| `docs/ps4/` | Maintained PS4 operating guidance and checklists |
| `evidence/ps4/` | Retained checkpoint records, preserving internal grouping |

Project/domain documentation and agent guidance retain their project-level
locations. The compiled `host-renderer` reference implementation and its CMake
definition deliberately remain target inputs. The frame-pacing owner example is
target-associated input data. Applicable licenses/notices stay with their target.

The final [ownership declaration](../../tools/pswaker/ownership.json) has one
tooling directory for both command groups. Commands import their colocated owner;
only that module derives repository location from script depth. There are no
forwarders at former command locations. Selection still conservatively includes
maintained files under the tooling and platform roots, requires the declared
command/target groups, and includes the owner module and declaration. Markdown,
tests, evidence, bytecode and interpreter caches remain excluded.

## Verification

The original baseline is commit `85ace99de7ef89f0ec4eb0808fae26c891c93d03`:
84 unique tests passed, including 11 GCI cases rerun with the host SDL reference
root after their initial prerequisite skips. The baseline inventory contains
142 maintained inputs and hashes for 474 protected evidence/patch/provenance files.

The preceding slices established the shared public interface (#55), diagnostic
tooling (#56: 91 tests, no skips), game/package tooling (#57: 90 full-suite tests
plus the added private-output case), test discovery/CI (#58: 90 full-suite tests
and subsequent focused integration checks), and documentation/evidence navigation
(#59). Their recorded reports are retained with this verification.

The final inventory has all 142 original members after intended relative-path
renames, plus only `build_inputs.py` and `ownership.json`: 144 inputs total.
All 474 protected files remain accounted for: 455 are byte-identical and 19
historical Markdown files change only existing navigation destinations. Raw
captures, manifests, recorded outputs, historical helper source, patches and
provenance retain their bytes. Committed Git blobs independently confirm this
comparison. The fresh-worktree Markdown navigation check reports zero missing
targets after repairing two stale build-record directory links in the historical
verification report; untracked directories in an older checkout had masked them.

Both identity CLIs detect representative changes to host tools, runtime source,
CMake/toolchain definitions, locks, patches, provenance, licenses, target example
data, and shared ownership. They remain stable for final documentation, tests,
evidence and caches. Checks also cover additions/removals/renames, missing required
groups, deterministic records, invocation outside the repository, and relocated
checkouts containing spaces. Existing negative preparation, prepared-tree drift,
staging, ELF/program identity, package payload and private-output checks remain
in the full suite. Provenance and complete-package preparation retain shared
input inventories alongside their distinct existing records.

The final suite passed all **93 tests in 108.167 seconds**, with zero skips,
failures or errors. Python syntax, all eight shell scripts, and CI filters/check
commands passed. The WSL run uses the three original platform/game/host roots as read-only
references, with native compilation, extraction, assembly and mutations in
disposable work areas. Python/shell syntax, CI path coverage and current command
paths are checked separately. Ownership metadata uses LF in both the working
tree and attribute-controlled fresh checkout.

An intermediate CI run (`40449834221`, job `122009702565`) failed because the
old `platform/ps4/*.sh` syntax loop had no matches after command relocation.
The find-based scan landed in #58 and checks the final tooling/platform roots.
This was a fixed intermediate regression, not a baseline failure.

Final review found zero hard standards violations and zero spec findings. One
standards judgment about duplicated identity assertions was resolved with a
shared test helper that restores changed files in `finally`. The seven focused
tests passed again in 10.678 seconds; Python syntax and diff checks passed.
The recorded 144-input inventory is unchanged. This review-only refactoring did
not rerun the full 93-test suite reported above.

## Identity and validation limits

Repository-relative names, owner code and declaration participate in new build
identities. New IDs and cache directories are expected. Prepare/build in fresh
roots when old records no longer match; retain original identities with existing
packages and console evidence. The diagnostic raw-byte identity and game
sorted-JSON identity remain distinct, as does provenance closure capture.

Historical helpers remain archival and use their recorded original snapshots;
in particular, `repeat-builds.py` retains its original
`91909bfadf14ac6d69ab7fccd61d32103208d907` source/layout assumption documented in
[history](HISTORY.md). Current workflows use
maintained commands outside the archive.

These checks do not provision a new host, rebuild the entire target stack, or
establish console acceptance for any newly produced package. Owner game data,
saves, existing packages and prepared reference roots are not migration outputs.
Any new candidate needs its own separately associated console evidence.
