# Storage recovery candidate (#21)

Implementation is on `feature/21-storage-recovery`, based on develop
`198a0d90021d3531f1e4d43f689b67615d03b406`, in commits `27b7436` and `0cfb6b6`.
**Implementation, host verification and private candidate preparation are ready;
installed-console acceptance is pending the owner's return for this binary.**
No #21 hardware row is marked passed and the issue remains open.

The [behavior record](../../STORAGE-RECOVERY.md) describes whole-store staging,
validated previous backups, explicit corruption recovery, retained affected
bytes, failure propagation and pending-card/audio/GPU shutdown. The
[owner checklist](../../Storage-recovery-checklist.md) supplies exact isolated
controlled cases, expected feedback, genuine-progress protection and retrieval.
The `storage-cases.py` tool creates private inputs from a **disposable** completed
in-game GCI; it never transfers or alters console data.

## Checks and review

[All 58 host tests passed with zero skips](host-checks.log). Python byte
compilation, all eight shell scripts' syntax checks and Git whitespace checks
passed. Real host SDL/GCI tests cover data and metadata completion, failed
multi-write stores with unchanged primary bytes, explicit restore versus decline,
corruption with/without backup, metadata-only corruption, oversized evidence,
missing-primary protection and a real staged I/O error under the owner-controlled
fault mode. An invalid test marker cannot offer restoration of healthy progress.
Synthetic progress used by tests does not establish actual in-game loaded results.

The previous console [Quit panic evidence](../persistence-20/console-return-2026-10-26/REPORT.md)
remains intact. A deterministic host regression using the real JUTGba worker
and SDK message queues reproduced `UNKNOWN GBA COMMAND` at line 623 before the
fix. The SDK's shutdown wake returned no message, but the game dispatched an
uninitialized command. The corrected worker returns on that wake and reads a
pointer-sized host message before converting the command. All four workers now
join without the panic. This host result is not a new console shutdown pass.

Target compilation/linking typechecked the combined C/C++ game, retained debug
lines in its matching unstripped ELF, checked Jaguar/btver2 compilation commands
and absence of unresolved TLS initializers, then generated SELF and passed the
OELF segment check. The [ABI audit](game-abi-audit.json) and
[emitted transaction-call audit](storage-link-audit.json) associate these checks
with the final ELF. The [provenance record](provenance.json) retains source pins,
ordered patches, port-input hashes and private inventory hashes. All 10,989
verified platform input files match the prior 01.08 game build; no graphics,
runtime archive, compiler or driver stack change is introduced.

The first full compile completed, but the existing staging guard correctly
rejected intervening source changes. No rejected artifact was handed off.
After review corrections the final source/input closure was reconfigured,
rebuilt, staged and rechecked read-only against the current files.
[Host recovery](host-recovery.json) records the retained hash-checked locked
zlib package used for builds/assembly and restoration of current `.2.3` afterward.
No host guard or dependency lock was bypassed.

Independent [Standards and Spec reviews](REVIEW.md) found two actionable cases:
marker errors could offer a rollback of healthy progress, and save validation
needed the game's load-required metadata. Both had failing regressions before
correction; both reviewers confirmed resolution. No findings remain outstanding.

## Exact candidate

Application **PSWaker**, version **01.09**, retains title ID `PSWK00001` and
content ID `IV0000-PSWK00001_00-PSWAKERGAME00000`. Compiled build:
**`d560ee2a9e873f83dc20`**.

| Artifact | Identity |
| --- | --- |
| Private Windows package | `local-research/storage-21-artifacts/PSWaker-storage-01.09.pkg` |
| Package size | 1,516,634,112 bytes |
| Package SHA-256 | `0b3259d464d99900897dcfbee1852622c19a83ce1999cec45e91dc2500a00e63` |
| Matching unstripped ELF SHA-256 | `ea28f5aa548a724e4038d5089087940e8b5082a4d55586514b5e5627712ed353` |
| SELF SHA-256 | `5c9396983bd26d0597df2668aed7d9b3b5825a546ef2dbbb2e58c837fa2ef1b9` |
| Owner USA GZLE01 revision-0 image SHA-1 | `6b5f06c10d50ebb4099cded88217eb71e5bfbb4a` |
| Image SHA-256 | `ec2d4ee790f48bee3d4c10feed166370df895f474e8db3f9af3b16ee001436df` |

Assembly extraction/inspection and a second fresh extraction/inspection passed.
The exported Windows package and ELF hashes match the inspected originals.
[inspection-01.09.json](inspection-01.09.json) and [artifacts.json](artifacts.json)
retain package/SFO/image/program associations. The inherited inspection status
mentions issue #16's tooling origin; this report's **untested #21 candidate**
status controls the actual hardware handoff. No save, settings, test marker or
recovery file is bundled in the package.

Installed content remains `/app0/game.iso`; shared user data remains
`/data/pswaker/`, with card channels at `saves/USA/Card A` and `Card B`.
The new disposable cache is `/data/pswaker/cache/d560ee2a9e873f83dc20/`.
Prepared sources/build/full evidence remain in `~/.cache/pswaker/game-21/`.
Private complete assembly, tool logs, notices, input inventories and fresh
inspection remain in `~/.local/share/pswaker-private/storage-21-01.09/` and
the Windows `local-research/storage-21-artifacts/` handoff directory. The latter
also contains matching `switchwaker.elf` and the complete build evidence.
Prior packages and original owner evidence are retained.

The [combined-artifact license review](game-license-review.json) associates the
actual inspected package, image, program and inherited notices. SDK module/stub
rights and combined distribution terms remain unresolved under
[LICENSING.md](../../LICENSING.md); all artifacts remain private. No game image,
save, executable, package, credential or private network detail is committed.

## Outstanding owner acceptance

Run the checklist's startup Retry/Exit cases, corruption with valid backup,
decline, corruption without a valid backup, controlled failed save, failure
relaunch/recovery, observed pending-write Quit, completed-save relaunch and
unsaved-gameplay Quit. Retain original inputs/failures/choices/results and
`PACKAGE_MANIFEST`/`BEGIN` identity records before subsequent launches rotate
logs. Confirm actual loaded player name, landmark and setting and the complete
card/audio/GPU shutdown stages; an idle-only Quit is not a pending-write test.
Restore and hash-check genuine progress/settings after isolating test data.

File/directory errors after a visible rename remain uncertain completion,
reported as failure with previous backup retained. Final stage-removal sync
failure can leave a valid newer primary visible at relaunch; do not call that
visibility a confirmed prior save. No host test proves power-loss behavior,
every possible corruption, physical media faults, actual PS4 persistence or
hardware audio/GPU teardown. Broader compatibility, performance acceptance and
public release remain outside this checkpoint.
