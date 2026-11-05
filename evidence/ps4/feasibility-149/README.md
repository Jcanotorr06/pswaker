# Prepared PS4 feasibility candidate (#149)

Prepared 2026-11-05. **Physical return pending; the gate is not complete.**
This candidate adds startup memory observations to the ordinary player program
and retains the exact final #148 seed. #159's known normal-Quit failure is
unchanged and blocks successful clean-shutdown acceptance. No new console
observation, full-game coverage or scaling result is claimed.

## Frozen candidate

| Artifact | Identity |
| --- | --- |
| Program version | `01.24` |
| Build / disposable cache ID | `35a453336a0e4b0d432c` |
| Program ELF SHA-256 | `c2d48776ed9f79d90ec71d61cc0732a3b2b673da361ca57d7c4a10596a2392fc` |
| Eboot SHA-256 | `76ddd46e09966d6372cb597f16329285b4bbea1450f6ead03102c66539ad97bc` |
| Complete package SHA-256 | `578f0d946ebfb3a96cc6d68a0feae040a7d205da1970a9ffdfc9f5d0f8cfc516` |
| Complete package bytes | 1,521,156,096 |
| Frozen seed descriptions / bytes | 301 / 1,257,472 |
| Seed SHA-256 | `06b8ef5d5df64e6a1218728550eab209f6a841926392ac18064effce64f17fd8` |
| Seed manifest SHA-256 | `4caf1f6ba2572dd7faeb3d77aa99a38c3fbdc8a0e0ed0e4d1ca186183646a6a4` |
| Fresh complete-package inspection SHA-256 | `5c3e316c7146960d129fed75b5cf982c4388317984ade1ba8ec02f4e2109ec44` |
| Source-built platform diagnostic ID | `60975dcf4480aa914369` |
| Host / PS4 description-contract SHA-256 | `8c3392d2bf28dae71adecc908ed8056d987a6b2db36bb27ddcf07cc138825700` |

[candidate.json](candidate.json) binds platform/toolchain locks, source preparation,
the actual static/dynamic control runs, full-description coverage and inspection
identities. The target build uses the locked host/toolchain and existing verified
source-built platform. Temporarily recovered .NET/PCRE packages were verified
against retained package identities and restored afterward; the complete installed
package-version inventory matches its pre-build state. A PowerShell/WSL wrapper
reported exit 1 despite completed build/inspection/restoration records; independent
program reinspection and complete-package assembly/fresh inspection pass.

The private artifact group is `feasibility-149`, with `complete-01.24`, matching
ELF, frozen `assets`, generation controls and raw build/inspection logs. The Windows
handoff folder is `PSWaker-01.24-feasibility-149`. Game resources, seed databases,
complete package, ELF and captures remain outside git. Installing this package
does not prove caches are empty; use the exact new build path above.

## Host generation and compatibility

Fresh real collector runs use the retained build-identified executable from #148:
the static `always-small-pot-stock-v1` emits three draws/lookups and one description;
the dynamic `common-pot-debris-lifecycle-v1` emits 40 draws/lookups and one
description across two texture selections and finite retirement. Each run verifies
all 301 seeded identities and round-trips all 301 complete descriptions through
the ordinary recorder unchanged. Their union contains two descriptions; both
match the frozen seed in full and add **zero** records.

The corpus grew from 287 runtime descriptions to 288 with one static-generated
addition, then to 291 and 301 with 13 honestly attributed runtime discoveries.
The isolated dynamic description was already covered. The 301 records comprise
300 GX v13 descriptions of 2772 bytes and one type-0 v5 description of eight bytes.
There is no claim that all 301 were automatically generated or physically exercised.

The prepared game/source inventory is byte-identical to 01.23; only maintained
port diagnostics change. Source-built renderer/platform identities and the
2,872-byte host/target contract witness remain retained. The host collector uses
a Vulkan BGRA layout, while PS4 must create its own required RGBA scene/offscreen
and destination-alpha variants. Matching descriptions do not imply portable host
driver objects or physical variant completion. The exact candidate requires its
own PS4 preparation and appearance evidence.

Normal complete-package assembly and separate fresh extraction/inspection agree
byte-for-byte on the inspection, including the exact bundled seed. Five retained
source files (seed database/manifest, program ELF/eboot, collector executable)
were hashed before/after assembly and remain unchanged. The public collector
commands independently enforce immutability of their full image, baseline and
collector inputs. Earlier candidates and returned evidence are preserved.

## Physical handoff and open obligations

Follow [the bounded procedure](../../../docs/ps4/GENERATED-SEED-FEASIBILITY.md),
using the existing ordinary Outset save and Outdoor Bath pots. Allow 20–30 minutes
plus startup/transfer time for cold and separate retained-cache warm runs, timed
first/repeat breaks, five minutes of representative gameplay per run, normal Quit
and private retrieval. Preserve save/settings backups independently from disposable
caches. Return unavailable save/scenario prerequisites rather than acquiring story
progression or a completed save.

The earlier [01.23 return](../dynamic-seed-validation-148-round2/REPORT.md) establishes
bounded membership/zero-wait evidence for that earlier binary only. It does not
establish this instrumented candidate's startup resources, filmed progress,
profile preservation, required layout completion or normal shutdown. The new
`RESOURCE` phase samples expose startup and gameplay allocations with explicit
failed-query handling, but cannot establish exact transient peaks or full-game cost.

Keep #149 open and downstream expansion gated through the returned physical
evidence and explicit owner decision. Known missing-pipeline waits or conflicting
descriptions require correction and revalidation. Resolve #159 and revalidate its
corrected candidate before accepting clean shutdown. The handoff lists measured
blocker/owner decision options without restoring a manual campaign or modifying #136.
