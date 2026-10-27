# Maintained diagnostic build evidence — issue #13

One uninterrupted clean Linux/WSL2 host build completed from a frozen maintained
source snapshot. It produced and inspected the disc-free `PSWK00010` version
`01.03` program package, matching unstripped ELF, SELF and OELF. This is host
evidence only; no maintained artifact was run on a console.

Build identity: `f89abcb363a45bfbe8cc`.
Pre-build Git tree: `3482b018a584d4795b2bc97d69558a9966707737`.
The archive contains the selected `platform/ps4` tree before generated evidence;
its SHA-256 is `e2b6f1a8e2294869678b3fb78f65a5b2481e6d828e112e0868b37542770d4105`.
The final workspace matches all 56 compiled/preparation input files
and computes the same embedded build identity. Documentation, tests and generated
evidence are outside that identity.

## Reproduction and retained artifacts

```bash
JOBS=12 bash /home/joseph_cano/.cache/pswaker/maintained-source-13-complete/platform/ps4/clean-build.sh /home/joseph_cano/.cache/pswaker/maintained-13-complete /home/joseph_cano/.cache/pswaker/maintained-13-final
```

The destination did not exist. The cache supplied verified downloads only;
all target implementation libraries were rebuilt. The frozen source was not
edited during the run. Stage times (UTC) are retained below:

```text
STAGE fresh-download-cache 2026-10-23T04:18:04+00:00
STAGE pinned-sources 2026-10-23T04:18:41+00:00
STAGE sdk-target-support 2026-10-23T04:19:08+00:00
STAGE runtime 2026-10-23T04:19:43+00:00
STAGE graphics-inputs 2026-10-23T04:20:14+00:00
STAGE graphics-libraries 2026-10-23T04:21:05+00:00
STAGE diagnostic 2026-10-23T04:31:55+00:00
STAGE package 2026-10-23T04:33:17+00:00
COMPLETE host-build-only 2026-10-23T04:33:31+00:00
```

Local exports and the complete evidence directory are retained at
`local-research/diagnostic-artifacts/maintained-13/`. The complete build root is
`/home/joseph_cano/.cache/pswaker/maintained-13-complete`. Binaries, source archives, notices and full command/build
logs remain local; the committed JSON records identify their exact inputs and hashes.

| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `PSWaker-Platform-Diagnostic-01.03.pkg` | `1f5ae5da58bdb6283a5abff15beee3e36aa61be0c4d6655d346acb24b9dcf0a8` | 43,778,048 |
| `platform_diagnostic.elf` | `e1a42f297207f3df164600d95f44ec3bb0b45858cd660d61a863a5d36dbc9a3a` | 47,441,504 |
| `eboot.bin` | `1bb0000e6eabf128a8854bfe3a0d315a63ffddcaa735a1fac17096c960fdd9da` | 41,730,000 |
| `platform_diagnostic.oelf` | `f9cb057c77e876954b52156a95a500a3baccc9712cbb95e7eae2c89b3018f5fc` | 48,541,248 |

## Verification

- Six CLI tests passed, with no skips: accepted and changed locked input,
  SDK source symlink preservation, changed package rejection, real package
  acceptance, and an extra payload file rejected after real package creation.
- Python compilation and syntax checks for every maintained shell script passed.
  The clean cross-build compiled the C/C++ code against the selected interfaces.
- Fresh PKG extraction verified the exact eight-file payload, SFO identity,
  compiled build identity, manifest and matching ELF/SELF hashes. ELF is x86-64,
  contains its symbol table, and has the required zero-based first load segment.
- Final unresolved wider-atomic references: 0.
  Archive-emitted wider-atomic references observed: 0.
- The recorded command audit covers 2,578
  target compilation commands across 10 CMake/Ninja components: all use
  `btver2`, with no PS5 CPU/target flags. Musl and bzip2 Make commands and archive
  hashes are also retained in the SDK-support log.
- All 14 SDK package URLs responded successfully; all 14 raw recipe hashes
  matched the fetched package BUILDINFO records. The license audit retained
  103 notice files and verified all three inherited
  sample modules against the pinned source archive.

See [review results](REVIEW.md), [inspection](inspection.json),
[source closure](input-closure.json), [snapshot comparison](source-snapshot.json),
[command audit](target-command-audit.json), [SDK/license audit](license-audit.json),
[test commands](host-checks.json), [test results](host-checks.log), and the
[clean-build driver log](clean-build.log).

## Remaining gates

Issue #15 owns the maintained clean-build pair and renewed owner console runs
tied to the actual installed PKG. Historical 01.02 results do not validate this
01.03 artifact. Issue #14 owns renderer reconciliation. SDK module/stub and
combined redistribution obligations remain unresolved as recorded in
[LICENSING.md](../../../docs/ps4/LICENSING.md); distribution is not cleared. No game data or
private keys are inputs to this diagnostic.
