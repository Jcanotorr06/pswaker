# Startup checkpoint #17: candidate handoff

The native game builds and the private complete startup, controlled-failure and
repair packages pass host extraction/inspection. The [returned console review](console-2026-10-25/REPORT.md)
records the owner's successful startup/Outset observations and exploratory play
through Dragon Roost Island, with no reported graphics/audio glitches and brief
loading/first-effect pauses. Both logs match this candidate's build and manifest.
The owner confirms Slim / 9.00 / GoldHEN v2.4b18, USB-free play, a fresh first
cache and no issues saving. The [returned controlled-failure/repair review](content-checks-2026-10-25/REPORT.md)
confirms all three intended error stops and successful repaired startup.
**#17 remains open only for seeded save/settings byte-preservation evidence.**

Use the [owner checklist](../../Startup-checklist.md) with these exact artifacts.
The scope is startup through access to Outset on PS4 Slim / 9.00 /
GoldHEN v2.4b18. Full-route, save durability and performance are later checkpoints.

## Candidate identity

- Application: PSWaker / PSWK00001 / IV0000-PSWK00001_00-PSWAKERGAME00000.
- Compiled build ID: 6ebc07987fe3b6c6064a.
- Unstripped ELF SHA-256: a191be91af014df4ffa983cb672544621c7de489994b898bb478e0efabadbe95.
- SELF SHA-256: bf3bdd961ab9e652c72996b5038f8a95d371ad4b6b6d7923f8d8620988b51bd2.
- Installed image SHA-256: ec2d4ee790f48bee3d4c10feed166370df895f474e8db3f9af3b16ee001436df.
- Installed image SHA-1: 6b5f06c10d50ebb4099cded88217eb71e5bfbb4a; USA GZLE01 revision 0.
- Read-only content: /app0/game.iso; writable user root: /data/pswaker/.
- Disposable cache: /data/pswaker/cache/6ebc07987fe3b6c6064a/.

| Version | Private package filename | Bytes | Package SHA-256 |
| --- | --- | ---: | --- |
| 01.00 | PSWaker-startup-01.00.pkg | 1516568576 | 0b619d1b85d51f6c2bebae12369c170f88446c543747bf0d1c24c1fe97643ac1 |
| 01.01 | PSWaker-CONTENT-FAILURE-missing-01.01.pkg | 55574528 | 3d61d258bf86727832d22b08c18a698c3f08d2bcde172b9e26707b00c65ca2dd |
| 01.02 | PSWaker-CONTENT-FAILURE-unreadable-01.02.pkg | 55705600 | 829320640034436560d174b7b2c43c3864953b1b8adf0ed525003cb9bb08583e |
| 01.03 | PSWaker-CONTENT-FAILURE-invalid-01.03.pkg | 1516568576 | 0f39c301fc784b9ac95ca105515aa032f74ba091e381eaa682800297cfef9e98 |
| 01.04 | PSWaker-repair-01.04.pkg | 1516568576 | a4423a4feff53678b5617d56d1187964bbc894dff9aec7cb1b600525c791fb14 |

01.00 is the normal startup candidate. 01.01 omits the image, 01.02 installs a
directory at its path, and 01.03 flips one non-header byte in a full-size image.
01.04 repairs the installation with the valid image. All five retain the same
application identity and executable. Install in that order and retain each
launch's logs and seed comparisons. A package version does not change the build ID.

## Host evidence

The final locked-host build compiled the game, linked it against the source-built
maintained #15 stack, and converted the Jaguar ELF to SELF with the segment check.
The [ABI audit](game-abi-audit.json) checks every compilation command, unresolved
TLS initializers, symbol table and source-line information. The [provenance](provenance.json)
records source/patch pins and the private complete input-inventory digests.
The three reviewed PS5 game fixes and independent PS4 ABI/signal decisions are
explained in [GAME-STARTUP.md](../../GAME-STARTUP.md).

Fresh extraction verified metadata, exact payload hashes, compiled identity and
matching ELF/SELF. The normal package was independently reinspected; each fault
tool also reinspected its valid parent and freshly extracted the intended fault.
The valid repair passed the ordinary complete-package inspection. See each
inspection-01.xx.json and [artifact identities](artifacts.json).

[All 25 host tests pass with zero skips](host-checks.log), including real packaging
tools, mismatched-ELF/payload rejection, preparation drift, full-image contract
and stopped content errors preserving seeded test bytes. The actual production
installed-content checker also [verified the owner's full image on the host](installed-content-host.json).
Python byte-compilation, shell syntax checks and git diff --check pass. These
host checks do not establish console behavior or valid game-save durability.

The build temporarily restored locked zlib 1:1.3.dfsg-3.1ubuntu2.2 from the
previously verified archive, verified the host, then restored the current
1:1.3.dfsg-3.1ubuntu2.3. [Recovery evidence](host-recovery.json) records hashes,
the wrapper-status anomaly and independently successful staging/restoration.

The [independent reviews](REVIEW.md) have no unresolved source findings on either
axis after corrections. The [artifact-specific license review](artifact-license-review.json)
associates the actual image/packages and verified SDK modules with retained game
and platform notices. Distribution remains uncleared under [LICENSING.md](../../LICENSING.md).

## Retention and practical limits

Private Windows handoff: local-research/game-17-artifacts/ in this checkout,
including five labelled PKGs, switchwaker.elf and build/checkpoint evidence.
Private Linux packages: ~/.local/share/pswaker-private/startup-17-candidate2/.
Full game sources/build/inputs/notices: ~/.cache/pswaker/game-17/;
verified platform: ~/.cache/pswaker/maintained-15-a/.
Older local build artifacts are superseded and are not this candidate.
No image, extracted assets, save, ELF or PKG is committed to the repository.

Cold preparation may have zero known shaders; new pipelines compile synchronously
when encountered. Scene creation logs mark requests/intervals rather than visible
transition completion. DMA counters do not prove audible audio. Pair these logs
with owner observations. Full image hashing adds an unmeasured console startup
cost. Initial controls and trigger thresholds still require hardware checks.

The returned logs confirm allocated internal 1280x720 and output 1920x1080,
installed-image/runtime-asset validation and basic pause/resume events. The
owner reports the startup route and game audio/rendering. Remaining evidence
is seeded save/settings byte preservation through the failure updates and repair;
error guidance and repaired startup are now observed. One earlier card-file-open
error remains in the log, despite
no owner-observed error or saving issue. See the returned review for identity
confirmation, timings, artifact-association limits and later acceptance work.
