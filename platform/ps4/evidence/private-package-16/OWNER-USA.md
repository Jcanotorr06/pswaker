# Owner USA-image assembly and inspection

On 2026-10-24 the owner supplied a local full raw USA GZLE01 revision-0 image.
Production validation, private complete-package assembly using the explicit
data-free #15 build-A diagnostic program, and a separate fresh-extraction
inspection all passed. The package is **NONPLAYABLE** and remains private,
outside this repository. No new console checkpoint or game acceptance is claimed.

## Corrected whole-image restriction

The original CLI rejected this image only at its final whole-image SHA-1 check.
Its raw format, full size, game ID, disc number, revision, FST/DOL bounds and
all eight required executable-object hashes had already passed. Independent
whole-file hashing confirmed SHA-1
`6b5f06c10d50ebb4099cded88217eb71e5bfbb4a`, matching the catalogued retail
USA/Canada disc in [entry 1086](https://redump.info/disc/1086), corroborated by
[GameTDB GZLE01](https://www.gametdb.com/Wii/GZLE01).

The cause was an overly restrictive host allowlist: the implementation admitted
only the fingerprint of the upstream author's image,
`0289e70f470dc758c73be9b8bcd8c865fb82d8ae`, which differs from the catalogued
retail fingerprint. The corrected generated content contract retains that
upstream value and adds the independently documented retail fingerprint with
its metadata sources and verification date. The game source revision and every
required DOL/REL hash remain unchanged. The reason for the two different
whole-image fingerprints has not been established, and their bytes are not
claimed equivalent.

This is an exact, documented allowlist correction for the selected USA revision
0; no user-supplied hash, runtime override, content-validation bypass or image
rewrite was introduced. A data-free CLI regression first failed, then passed
with the fix, and verifies that even an allowlisted image cannot bypass the
required DOL hash. Existing corruption/revision/format cases remain covered.

## Real private result

| Item | Value |
| --- | --- |
| Image identity | GZLE01, disc 0, revision 0 |
| Raw image bytes | 1,459,978,240 |
| Image SHA-1 | `6b5f06c10d50ebb4099cded88217eb71e5bfbb4a` |
| Image SHA-256 | `ec2d4ee790f48bee3d4c10feed166370df895f474e8db3f9af3b16ee001436df` |
| Package SHA-256 | `e66f10db989ea47aae81e464e9a31661df7b5cb30b499f7b167af47bbff3d4ea` |
| Package bytes | 1,504,968,704 |
| Title / version | PSWaker Diagnostic NONPLAYABLE / 01.05 |
| Title ID | `PSWK00010` |
| Content ID | `IV0000-PSWK00010_00-PSWAKERPROBE0000` |
| Installed image | `/app0/game.iso` |

The private result is at
`$HOME/.local/share/pswaker-private/diagnostic-complete-01.05-usa-16/` in the
owner's Ubuntu WSL distribution. It contains the complete package, matching
unstripped ELF/SELF/OELF, assembly commands, input/tool/source hashes and
inspection evidence. Detailed paths and logs stay alongside the private output.
The image and package themselves are not committed or published.

Host execution used the [documented commands](../../COMPLETE-PACKAGES.md), with
the owner-supplied image, `maintained-15-a` platform root and original
`build/probe/platform_diagnostic` ELF and `build/probe-stage` program payload.
Observed wall times on this host were 6.331 seconds for validation, 74.223
seconds for assembly including its built-in inspection, and 25.101 seconds for
the separate inspection. These are single observations, not performance budgets
or gameplay measurements.

[Structured data-free inspection evidence](owner-usa-inspection.json) records
the package/header/SFO, actual image and executable identities and per-file
hashes. Fresh extraction independently revalidated the packaged image and all
required DOL/REL objects; its SHA-256 equals the independently hashed original.
The source image was opened read-only, and its bytes were copied without
compaction or rewriting. The diagnostic SELF is still
`f62940819abeb92ea4af228442f8fb83c00a33199861b1e38b78e9b20e9ffd7a`.

## Final host checks and independent review

After the fingerprint correction and real assembly, the full host suite passed
**21 tests with no skips**, using the actual selected #15 packaging tools.
See [the full test output](host-checks-usa.log). Python compilation, shell
syntax checks and regeneration of the committed content contract also passed.
The original owner-image CLI invocation now succeeds without changing the
supplied image, completing the diagnosis loop.

Independent Standards and Spec reviews of `ab42038` against `d39380b` found
no findings. They checked that the exact additional fingerprint matches its
public metadata, every required executable/identity check remains in place,
and the data-free evidence matches the committed preparation files. See the
[follow-up review record](REVIEW.md#retail-image-follow-up).

No installed-console read, game startup, save/update preservation, game audio,
rendering or gameplay performance was tested. Those remain later acceptance
work. Keep the actual combined artifact's license/notices/provenance review
under [LICENSING.md](../../LICENSING.md); successful host assembly does not
clear distribution.
