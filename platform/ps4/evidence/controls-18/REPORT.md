# Controls candidate for issue #18

The updated complete package is built and freshly extracted/inspected. The
[returned controls review](console-return-01.05/REPORT.md) associates the current
log with this exact 01.05 binary and records the owner's confirmation that
mapped buttons remain functional as expected. Sampled input includes partial
and terminal trigger values, plus a neutral input-loss state. The owner subsequently
confirms **all three requested focused checks passed**: actual partial/full L2/R2
actions, touchpad settings/legend with Cross confirm/Circle cancel, and held-input
disconnect/reconnect plus the delayed failed-read check. The 90% terminal-click
threshold is therefore owner-validated on this candidate. These follow-up passes
are owner observations; their full sequences are absent from the supplied capture.
Normal Quit/orderly shutdown remains separately unverified in this return. The
previous log is 01.04 and is not counted as another controls-candidate run.

## Candidate identity

- Version: 01.05; PSWaker / PSWK00001 /
  IV0000-PSWK00001_00-PSWAKERGAME00000 (stable update identity).
- Compiled build ID: d532217ac6a319ff6ad3.
- Package: PSWaker-controls-01.05.pkg; 1,516,568,576 bytes.
- Package SHA-256: 8e572e447d5da87d8026911602119cbdcb898c93f10485b5ee64a315f08d3c5c.
- Matching unstripped ELF SHA-256: 7614549b1f2e5b0aa636f8858daef6d90c56e967fd86095aa6d941ba5d3743f8.
- SELF SHA-256: 056683cd1020158aa02063500699f99d291b4bad9ef061e860883a9c033b0a9b.
- Image SHA-256: ec2d4ee790f48bee3d4c10feed166370df895f474e8db3f9af3b16ee001436df.
- Image SHA-1: 6b5f06c10d50ebb4099cded88217eb71e5bfbb4a; USA GZLE01 revision 0.
- Installed content: /app0/game.iso; user root: /data/pswaker/.
- Disposable cache: /data/pswaker/cache/d532217ac6a319ff6ad3/.

The [artifact inventory](artifacts.json), [package inspection](inspection-01.05.json)
and [provenance](provenance.json) preserve the full association. Original
build-time UNTESTED labels are retained as historical build evidence;
the returned controls review above supplies the subsequent owner verdict.
Internal rendering remains 1280x720 with original 30 Hz game logic and stock textures. Support stays
PS4 Slim / firmware 9.00 / GoldHEN v2.4b18, to be reconfirmed by the owner.

## Implementation and host verification

The [controls notes](../../CONTROLS.md) describe fixed mappings, shared native
sample/pause state, drawn PlayStation symbols, first-launch/settings legend,
Cross confirm/Circle cancel, separate Quit confirmation and fresh deliberate
resume. The delayed installed read check returns failure from one native API
call five seconds after gameplay resumes, allowing held-input testing during
active play. Physical disconnect observations remain a separate owner check.

The final locked-host build compiled and linked the PS4 game against the
unchanged verified #15 platform, converted ELF to SELF and staged successfully.
The [ABI audit](game-abi-audit.json) verifies Jaguar compile flags, unresolved TLS
imports and retained symbols/source lines. The [emitted-link audit](controls-link-audit.json)
ties actual PADRead/input-hook/native-read calls to the controls bridge and
failed-read wrapper in the matching ELF; it does not claim console execution.

[All 32 host tests passed with zero skips](host-checks.log), including seven
compiled input scenarios using the production controls code, actual native
reader and pinned Dolphin headers. Only external console services and time are
simulated. Tests cover the legend/confirmation gate, all agreed mappings and
directions, analog travel on either side of the terminal threshold, disconnect,
failed reads containing stale held bytes, repeated loss, menus and a delayed
failure interrupting active game-facing held input. The other tests exercise
preparation, image contracts, stopped installation errors and real package tools.
Python byte-compilation and git diff --check passed. Full package assembly and
an independent second extraction/inspection verified executable/payload hashes,
image identity, metadata and matching ELF/SELF.

The initial compile completed while source refinements were in flight. Staging
correctly rejected its changed-input closure; it was not handed off. Those logs
remain under game-18/evidence/intermediate-drift-rejected. The final configuration
captured the corrected source and rebuilt affected units before successful
staging. The temporary locked zlib was restored to the current host version
after both attempts; [host recovery](host-recovery.json) records the successful
final build and restoration. No dependency lock or build guard was bypassed.

The independent [Standards and Spec reviews](REVIEW.md) have zero remaining
findings after the shared named-menu-action correction. No hardware pass is
inferred from compilation, linkage, synthetic input or prior gameplay.

## Private retention and owner handoff

- Windows handoff: local-research/controls-18-artifacts/ in this checkout,
  containing PSWaker-controls-01.05.pkg, switchwaker.elf, full input inventories,
  build logs, notices and checkpoint evidence.
- Linux complete package: ~/.local/share/pswaker-private/controls-18-01.05/.
- Prepared sources/build/full manifests/notices: ~/.cache/pswaker/game-18/.
- Matching SELF: game-18/build/program-stage/eboot.bin.
- Verified platform: ~/.cache/pswaker/maintained-15-a/; the game-17 tree and its
  historical artifacts are preserved.

The [artifact-specific license review](game-license-review.json) retains the
actual program hashes, pinned source notices and platform-audit association.
Inherited SDK module/stub rights and combined distribution terms remain
uncleared under [LICENSING.md](../../LICENSING.md). Artifacts stay private;
no image, extracted data, save, ELF or PKG is committed.

Return mapping/menu/action observations, both partial/full trigger cases,
physical held-input loss/reconnect and the delayed installed read check using
the owner checklist. Retrieve platform.log, platform.prev.log, last-stage.txt
and useful crash/boot traces before rotation. Preserve exact run/build/cache
associations. Logs record raw/game-facing samples, native loss, menu changes,
explicit confirmations and check scheduling/failure markers; they do not prove
rendered actions, physical controller behavior or visible gameplay freeze.
Existing runtime and audio/GPU shutdown contracts continue. Persistent settings,
save durability, route/performance acceptance and public release are later work.
