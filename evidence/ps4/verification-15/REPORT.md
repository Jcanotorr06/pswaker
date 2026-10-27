# Maintained platform verification — issue #15

**PASS — bounded maintained-platform gate for the owner-confirmed 01.04 candidate.**
Two independent clean Linux/WSL2 builds completed and passed artifact inspection.
Their recorded inputs match the installed candidate, whose own cold/warm/warm
console gate passed. The rebuilt binaries have separate hashes and no console
results; neither byte identity nor formal semantic equivalence is claimed.

This report applies [issue #15](https://github.com/Jcanotorr06/pswaker/issues/15)
and the [parent's platform contract](https://github.com/Jcanotorr06/pswaker/issues/12).
It combines new independent build evidence with the already returned, reviewed
01.04 console evidence. Rebuilding does not create another console observation.

## Installed candidate

| Item | Identity |
| --- | --- |
| App / title ID / version | PSWaker Platform Diagnostic / `PSWK00010` / `01.04` |
| Source/toolchain build ID | `60975dcf4480aa914369` |
| Owner-confirmed installed PKG SHA-256 | `edeaebf3a68413c1f3a23a8224b0125240e6419710b9247b2132ccfccd5d6522` |
| Matching ELF SHA-256 | `1cb796480f3961447158d6658c56e7bb309f3fc2a290ef2195b38d4b1c6e40e6` |
| Matching SELF SHA-256 | `5d3438436d381fef0facd0cd2397461e9d3f9741b52f996b88c8e7b89952c036` |
| Original build root | `/home/joseph_cano/.cache/pswaker/maintained-14` |
| Owner package on PC | `local-research/diagnostic-artifacts/renderer-14/PSWaker-Platform-Diagnostic-01.04.pkg` |
| Recorded source archive SHA-256 | `5adbf0b576d7ac4c84308618d79c61a3348cddbbdd6d8eab0b1003ea29304967` |

The source archive is retained at
`/home/joseph_cano/.cache/pswaker/maintained-source-14.tar` and with the PC artifacts.
All 99 maintained input paths/hashes match the installed candidate's compiled
manifest and the current workspace. Each new source directory was independently
extracted from that verified archive. This issue changes evidence tooling and
documentation only; analysis scripts live under `evidence/`, which is excluded
from the diagnostic's source/toolchain build identity.

The owner confirmed the exact installed package in the retained review, recorded
by commit `c5278db`. The original report's stale `01.03` field and blank package
hash are preserved in [the unedited owner report](console/owner-report-original.md).
The complete manifest logged by each selected 01.04 launch matches the candidate's
packaged manifest, including its SELF hash. The new extraction/inspection also
rechecks the original PKG/ELF/SELF hashes. The executable's original `untested` /
`hardware gate incomplete` strings describe build-time status; evidence review
does not rewrite the tested binary or those original records.

## Two independent clean builds

Each destination was absent. The two source/build/SDK/runtime/packager trees are
separate; they share the recorded Ubuntu 24.04 x86-64 WSL2 host and run concurrently
with six jobs each. They are independent clean builds, not two independently
provisioned machines. The existing root supplies only `downloads/`; all locked
downloads are checked again and all target implementation libraries, renderer,
diagnostic and LibOrbisPkg are compiled anew. Pinned SDK import stubs, headers,
converter tools and sample modules remain disclosed SDK inputs, not newly built
implementation libraries. No game source/data or private SDK tree is used.

After verifying/extracting the recorded source archive into the two new source
directories, run:

```bash
JOBS=6 CCACHE_DISABLE=1 bash "$HOME/.cache/pswaker/maintained-source-15-a/platform/ps4/clean-build.sh" \
  "$HOME/.cache/pswaker/maintained-15-a" "$HOME/.cache/pswaker/maintained-14"
JOBS=6 CCACHE_DISABLE=1 bash "$HOME/.cache/pswaker/maintained-source-15-b/platform/ps4/clean-build.sh" \
  "$HOME/.cache/pswaker/maintained-15-b" "$HOME/.cache/pswaker/maintained-14"
```

For a future repetition, use new absent build destinations and retain each failing
root instead of reusing it. A current host that differs from `host.lock.json`
requires explicit recovery of the recorded host or a deliberate lock change and
renewed evidence.

### Host drift and recovery

Both initial attempts stopped at host verification, before their destinations
were created: `zlib1g:amd64` had advanced from locked
`1:1.3.dfsg-3.1ubuntu2.2` to `1:1.3.dfsg-3.1ubuntu2.3`. The build guard was not
bypassed and no dependency lock was changed. For this experiment the recorded
package was temporarily restored from the Ubuntu snapshot at
`https://snapshot.ubuntu.com/ubuntu/20261021T000000Z/`.

`gpgv` verified `noble-updates/InRelease` with the installed Ubuntu archive keyring;
its SHA-256 authenticated the `main/binary-amd64/Packages.xz` index, which in turn
authenticated the package hash
`84b9cf5752b29c9f92c27cd4c4ba9bbcc70b5ccf9b1b515421a28ae23212e273`.
The restored host's complete package inventory matches the installed candidate's
record, in addition to the required-package/tool checks. The current `.2.3`
package was downloaded through APT for restoration after the builds; its hash is
`376249c8de139568221dbb242318cc8cb8f02299e3a62b7432948e1754fbddf9`.
Host recovery files remain at
`/home/joseph_cano/.cache/pswaker/verification-15-host`.
The original current `.2.3` package was restored after both builds completed;
[host-recovery.json](host-recovery.json) records the signed inputs and restored
version. Both build manifests captured the exact original host inventory before
restoration. Future builds on the current host will correctly reject that drift
until the recorded build environment is restored again.

### Build outputs and differences

| Build | Start / completion, UTC on 2026-10-24 | Result |
| --- | --- | --- |
| A, `maintained-15-a` | 19:13:51 / 19:36:58 | Clean build and inspection pass |
| B, `maintained-15-b` | 19:13:51 / 19:37:11 | Clean build and inspection pass |

Every ELF is 47,494,376 bytes, SELF 41,763,824 bytes and PKG 43,909,120 bytes.
The [separate build identities and runtime outputs](build-summary.json) retain
sizes/hashes; matching sizes do not establish matching contents.

| Output | Build A SHA-256 | Build B SHA-256 |
| --- | --- | --- |
| ELF | `f97123d555dfef871de7483140aa84b738696b397afdc9a54cd95fd20e6d0d84` | `9f61eb8410011683652bf2856d79d7e68bc1f82ce79d550b385640d4f755f634` |
| SELF | `f62940819abeb92ea4af228442f8fb83c00a33199861b1e38b78e9b20e9ffd7a` | `cb8241d20550de0a4d6ef70170359c0e3d5355c5d570cf4c9a8f105dcd3b4497` |
| PKG | `30c91dd26524bcc5535380c57b1c9066a3fc3539e93ec5a8051c9853224744e5` | `e565ef5b75399735fe0bd90361f4986bc838950480efef94bf7f9ec886877ba9` |

Shared [build A](../../../platform/ps4/evidence/verification-15/build-a) and [build B](../../../platform/ps4/evidence/verification-15/build-b) records include source/host/runtime
closures, patch records, exact tool identities, ordered stage logs, ELF headers,
package/SELF inspection, command audits and complete local-evidence inventories.
The full build logs, commands, decoded unwind records, source/download trees,
notice corpus and binaries remain in their respective Linux roots. Each inventory
records every retained evidence file's size and SHA-256. The installed candidate's
[fresh inspection and PC-export hashes](installed-candidate/reinspection.json)
remain separate.

Both audits cover 2,575 C/C++ compilation commands, all with `btver2`, plus nine
assembly commands, with no PS5 target flags. All nine assembly objects are
[byte-identical across the installed candidate and both rebuilds](assembly-comparison.json).
The source/dependency/SDK/host/tool fields and all 99 maintained-file hashes match
in all three comparisons. Only `rebuilt_sdk_archives` differs in the normalized
closure: those are newly compiled **output** hashes, not changed dependency inputs.
The actual hashes are retained instead of pretending these outputs match.

### Bounded binary-difference review

[A versus B](comparisons/a-b.json), [installed versus A](comparisons/candidate-a.json)
and [installed versus B](comparisons/candidate-b.json) report every section's
address/size/hash, all disassembly addresses and relocation counts. All three
retain the same 5,347,803 instruction addresses and 45,238 dynamic relocation
records. The disassembly comparison observes these categories:

| Instruction observation | A / B | Installed / A | Installed / B |
| --- | ---: | ---: | ---: |
| Identical disassembly | 5,288,729 | 5,277,878 | 5,277,746 |
| Same operation, equal normalized ASCII string target | 58,007 | 59,128 | 59,260 |
| Same operation, equal empty/binary NUL prefix | 1,067 | 6,588 | 6,588 |
| Same operation, equal first eight relative-table words/destinations | 0 | 3,965 | 3,965 |
| Same operation, equal complete 16-byte broadcast constant | 0 | 39 | 39 |
| Same operation, relocated unwind-section base | 0 | 9 | 9 |
| Same operation and data-layout shift; target data unchecked | 0 | 196 | 196 |
| Other differences / missing instructions | 0 / 0 | 0 / 0 | 0 / 0 |

A/B differences are references into differently ordered read-only string data;
resolved normalized ASCII string multisets match. For the installed comparison,
257 embedded build paths grow by two characters (514 bytes), with a resulting
512-byte section growth after layout/alignment. Binary tables and following
unwind/exception sections consequently move. The normalized raw read-only section
still differs; NUL splitting includes binary tables and is not a complete data
canonicalization. A/B's full NUL-split multiset also differs for binary data.

The initial eight-KiB string comparison left one shader reference unclassified.
The complete 10,995-byte WGSL string is identical (SHA-256
`883fc4a93adc212d4664a17272e84a9eff365621008a98678964d2b280d05428`).
LLVM's lane-content comments also omitted numeric addresses for some vector
instructions; decoding their RIP targets using the following instruction resolved
those parser residuals. Initial analysis reports remain at the local host-evidence
directory as `initial-*.json`; they are analysis limitations, not failed console runs.

[Decoded layout analysis](layout-analysis.json) compares 1,189,386 unwind lines:
A/B are identical. Installed/A differ only in 1,371 LSDA addresses shifted by 512
and one personality-pointer encoding reduced by 512 to preserve its absolute
target. All 47,450 unwind-header entries retain identical code PCs and offsets
within the frame section. The four differing 32-bit exception-table fields also
retain the same PC-relative destinations. All 71,003 symbol records retain their
metadata, and all function addresses are unchanged; data-symbol addresses reflect
the pool/table layout changes. The nine differing unwind references point to the
corresponding inspected section bases. The moved frame-base dynamic relocation
retains the same initial CIE; other differing relocations resolve to equal bounded
NUL-terminated targets. No unmatched/other relocation records remain.

SFO identity, title/version and fixed supporting payload hashes match. Compared to
the installed candidate, `PUBTOOLINFO` changes `c_date=20261023` to `20261024`.
The embedded manifests differ in build-root/output details and SELF hashes, and
SELF/PKG contents reflect the differing linked ELF. Fresh payload inspection
verifies those associations. Whole-container timestamp/metadata bytes are not
canonicalized into a byte-identity claim.

These checks deliberately stop short of equivalence: an empty/binary NUL prefix
is not a whole constant; eight table words are not a complete table; the 196 data
references only establish equal operation/offset shifts, with **no target-data
equality claim**. The inspected source closure and the actual installed candidate's
own hardware evidence support the bounded gate. Rebuilt artifacts are not assigned
the installed candidate's console results.

The command audit distinguishes C/C++ compilation from five handwritten LLVM-12
x86-64 assembly routines (three integer-to-floating-point builtins and two unwind
register routines). Those assembly commands have no `-march` flag. Their emitted
fixed x86-64/x87/SSE instructions were inspected separately; the report does not
claim that every assembly command carries `btver2`. Four additional Mesa BLAKE3
assembly objects carry the flag but include explicit SSE/AVX2/AVX512 variants;
`blake3_dispatch.c` checks CPUID and XGETBV state before selecting a variant.
A CPU flag does not restrict explicitly written assembly instructions. All nine
objects are inventoried and disassembled; their presence is disclosed rather than
treated as evidence of generated PS5 code. Musl/bzip2 Make commands remain in the
complete SDK-support log. SDK sources and runtime overlays remain exactly the
selected inputs.

## Returned console gate

The owner already reconfirmed PS4 Slim / firmware 9.00 / GoldHEN v2.4b18, installation
and FTP retrieval. No additional physical action is claimed here. The precise
[01.04 checklist](../../../docs/ps4/Renderer-checklist.md) records package identity, cache
preparation, expected visible/audible behavior, controller sequence, full closes,
files to retrieve and failure handling.

[The original review](../renderer-14/console-01.04/REPORT.md) and
[per-run summary](../renderer-14/console-01.04/summary.json) remain controlling for
owner observations and resource interpretation. The new
[console recheck](console/console-recheck.json) verifies all 47 original file
hashes, complete logged candidate manifests, known-result sample counts, allocated
targets, runtime blocks, resource samples, persistence counters and append history.
The shared `console/run-*` files contain exact selected blocks and last-stage
excerpts, with original byte ranges and hashes. Full append logs, earlier failures,
cache databases and backups remain local at
`local-research/diagnostic-artifacts/renderer-14/console-01.04-evidence/`, covered by
the [immutable inventory](../renderer-14/console-01.04/original-files.json).

| Observation | Cold | Warm 1 | Warm 2 |
| --- | ---: | ---: | ---: |
| Launch/state counter | 13 | 14 | 15 |
| Cache entries before Aurora | 0 | 2 | 2 |
| At least 600 seconds, checked with monotonic clock | PASS | PASS | PASS |
| Repeated platform check cycles | 120 | 120 | 120 |
| Renderer sweeps: startup + after target recreation | 1 + 9 | 1 + 9 | 1 + 9 |
| Renderer / EFB white / offscreen white / purple samples | 180 / 120 / 120 / 120 | 180 / 120 / 120 / 120 | 180 / 120 / 120 / 120 |
| Successful asynchronous map callbacks | 540 | 540 | 540 |
| Allocated 1280x720 EFB observations | 120 | 120 | 120 |
| Failed checks / pixel mismatches / audio API errors | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| Runtime, input resume, persistence and orderly shutdown | PASS | PASS | PASS |
| Owner scene, continuous tone, controls, no crash/hang | PASS | PASS | PASS |

Output is independently recorded as 1920x1080 at 59.94 Hz. Runtime preflight
checks constructors, thread-local isolation/destructors, pthread-once, mutex-backed
condition-variable synchronization, atomic wait/notify and flushed/synced file
replacement. State progresses 12 → 13 → 14 → 15 across full closes/relaunches.
All runs drain the GPU, complete Aurora destruction and exit with status zero.
Intentional device-destroyed / unsupported-screensaver shutdown messages are
preserved. The reported blue and white/black-quarter flashes match the explicit
startup/periodic known-result test frames; the normal scene returns.

The cold launch starts with zero cache files; each warm launch starts with two.
Retrieved Dawn databases remain 536,576 bytes, with a distinct hash after each
launch; the 65,536-byte pipeline database keeps the same hash. This establishes
the observed create/reuse/retention lifecycle, not arbitrary corruption recovery
on the PS4. Earlier backups and cache hashes remain in the original inventory.

### Resource methods and limits

About every 30 seconds the diagnostic records driver garlic/onion bytes and buffer
count, main-mspace allocated bytes, fixed heap capacity and available flexible
memory. After the first 30-second sample, all runs plateau at garlic 438,697,984,
onion 835,584, 44 buffers and flexible availability 396,361,728 bytes. Heap capacity
stays 536,870,912 bytes. Main-mspace fluctuations are bounded:

| Run | Minimum allocated bytes after startup | Maximum |
| --- | ---: | ---: |
| Cold | 4,679,568 | 4,689,024 |
| Warm 1 | 4,398,432 | 4,489,824 |
| Warm 2 | 4,482,800 | 4,489,680 |

There is no steadily growing measured resource use in these three runs. These
counters include driver/allocator accounting, not complete RSS or per-allocation
leak tracking; the ten-minute observations do not prove universal leak freedom.
Audio source-frame counts/API errors do not measure hardware underruns. The owner's
continuous-tone observations supply the audible evidence. Photos/video, total
startup timing and some output-device metadata were not recorded; their absence
does not substitute for or erase the supplied observations/logs.

## Validation and scope

[Final host checks](host-checks.log): the full suite ran once, **8 tests passed,
zero skips**. It includes real package acceptance/extra-payload rejection and
pinned-source renderer preparation/rejection. Python compilation and all seven
shell syntax checks pass. Both complete cross-builds typecheck the selected C/C++
interfaces. Earlier individual artifact/renderer test files also passed. Controlled
different-package and changed-source trials fail before writing success reports.
[host-checks.json](host-checks.json) records commands and boundaries.

[Independent Standards/Spec review](REVIEW.md): **0 findings on each axis**.
The reviewers independently verified maintained inputs, artifact identities,
retained inventories and owner evidence. Their reports and the reviewed revision
are preserved without assigning the rebuilds any console results.

To regenerate supporting records from the retained roots, run from the repository
root on Linux/WSL2 (choose fresh output paths for a separate review):

```bash
verification_base="$HOME/.cache/pswaker"
python3 platform/ps4/evidence/verification-15/collect-console.py \
  local-research/diagnostic-artifacts/renderer-14/console-01.04-evidence \
  "$verification_base/maintained-14" /tmp/pswaker-console-recheck
python3 platform/ps4/evidence/verification-15/collect-build.py \
  "$verification_base/maintained-15-a" /tmp/pswaker-clean-a-record
python3 platform/ps4/evidence/verification-15/explain-differences.py \
  "$verification_base/maintained-15-a" "$verification_base/maintained-15-b" \
  --first-source "$verification_base/maintained-source-15-a" \
  --second-source "$verification_base/maintained-source-15-b" \
  --output /tmp/pswaker-a-b.json
```

Repeat collection for build B and comparison for the installed candidate versus
each rebuild, using `maintained-14` / `maintained-source-14` for that candidate.
Run `inspect-layout.py <candidate-root> <build-a-root> <build-b-root> --output <json>`
to regenerate the decoded unwind/header comparison.
The scripts validate recorded files and report observations; they do not execute
PS4 code or independently supply owner observations.

Synthetic geometry/audio and diagnostic file replacement establish the bounded
platform operations tested. They do not establish game renderer coverage, DSP
correctness, saves/update durability, gameplay timing or first-playable acceptance.
Public release remains outside scope; the existing SDK/module redistribution
questions in [LICENSING.md](../../../docs/ps4/LICENSING.md) remain unresolved. Shared evidence
contains diagnostic data, hashes and public provenance, without game data, keys,
credentials or private network details.

The selected official Mesa 26.0.8 plus published PS4 patch remains the explicitly
experimental replacement recorded by the architecture decision; this verification
does not claim equivalence to the author's unresolved `80c7811` tree.

If later evidence invalidates this stack, return to
[Choose the PS4 platform stack and upstream integration strategy](https://github.com/Jcanotorr06/pswaker/issues/6#issuecomment-6257468588).
Do not silently change dependencies or bypass the platform gate with game integration.
