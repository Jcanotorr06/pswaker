# Save/settings persistence candidate (#20)

Implementation is prepared on `feature/20-save-settings-persistence` from
develop `7364a4fc197ae54ccd2ee4eba365dc9c9fb9754c`. The
[returned console review](console-return-2026-10-26/REPORT.md) completes the
**bounded #20 persistence checkpoint**: the owner confirms save behavior and
visible setting retention after full relaunch, separate 01.08 installation and
cache-only clearing, plus preservation of the last completed save without
automatic saving of an unsaved action on Quit. Runtime identities and returned
settings corroborate that sequence. A logged shutdown panic remains unresolved;
orderly internal shutdown and #21's full recovery guarantees are not accepted.

The owner's prior Dragon Roost progress/no-save-problem report and the
[byte-identical GCI / owner settings preservation checks](../startup-17/content-checks-2026-10-25/REPORT.md)
remain the historical baseline. The [01.06 return](../route-19/owner-return-01.06/REPORT.md)
also reports completed-save relaunch and clean normal Quit, with no returned
logs. Neither establishes this candidate's UI setting or complete update cycle.

See [PERSISTENCE.md](../../PERSISTENCE.md) for storage consumers, replacement
behavior and host-test boundaries; use the [owner checklist](../../Persistence-checklist.md)
to protect existing progress and return focused evidence. Full backups,
controlled corruption/failure recovery and pending-write acceptance remain #21.

## Implementation and host checks

The checkpoint adds a persistent port-menu text-size preference, probes the
settings root and both actual GCI card directories before gameplay, explicitly
selects GCI for both channels and checks file/directory synchronization before
reporting replacement success. Existing GCI paths, shared-profile identity and
owner data remain unchanged. The desktop settings/developer environment loader
stays disabled; unrelated settings-file content is preserved. Game readback
checksum and metadata errors now reach existing save-failure handling.

[All 48 host tests passed with zero skips](host-checks.log). Python byte
compilation, shell syntax checks and git whitespace checks passed. Tests cover
actual Aurora GCI file/data/metadata replacement with real host SDL I/O,
reopen/readback, injected sync and rename errors retaining byte-identical prior
data, settings reload after exec, unavailable storage/retry, invalid/unreadable
settings preservation, write/close/rename failures and uncertain post-rename
directory-sync completion. The menu test writes/reloads real profile files and
checks that holding Cross does not repeat writes. Synthetic progress is not an
in-game save; the additional game save-routine propagation fixes are source-
reviewed and target-compiled, not a claim of game execution in those host tests.

The original GCI sync-failure test failed against the prior prepared game-19
backend because it returned success without syncing. It passes against the
patched backend. The [emitted-link audit](storage-link-audit.json) confirms this
ELF's Aurora commit calls the new port commit, which imports `fsync` and
`rename`; it establishes emitted calls rather than target durability.

The target build compiled/linked the actual game against unchanged verified
#15 platform inputs and converted its ELF to SELF. The
[ABI audit](game-abi-audit.json) checks 1,391 C/C++ compilation commands for
Jaguar/btver2 flags, retained symbols/source lines and no unresolved TLS
initializers. The initial staging attempt correctly rejected source/input drift
after review corrections. Reconfiguration and rebuilding succeeded with the
final closure; the rejected attempt produced no handed-off candidate.
The [host recovery record](host-recovery.json) records hash-checked restoration
of the locked zlib for the build and restoration of the current `.2.3` package
after both complete packages and fresh inspections finished. No host guard or
dependency lock was bypassed.

Independent [Standards and Spec reviews](REVIEW.md) leave zero outstanding
actionable findings after correcting the exact card paths in the storage log.
The later owner return and its known shutdown limit are reviewed separately
below; they do not rewrite the original build-time untested manifests.

## Candidate and update identity

Application PSWaker retains title ID `PSWK00001` and content ID
`IV0000-PSWK00001_00-PSWAKERGAME00000`. Both complete packages use compiled
build **`9ac6fb9b2da43e02d642`**. Versions 01.07 and 01.08 deliberately contain
the same program/image and different package version metadata: installing the
newer complete package is the controlled update-preservation check, separate
from full relaunch. The program's embedded build manifest records program-stage
version 01.07; the installed SFO and complete-package manifest distinguish the
01.08 update. No profile is packaged or restored during either assembly.

- Matching unstripped ELF SHA-256:
  `56361867ddc41680c41a44773f56183e43094dbe68c326c9d56913f840ddeb34`.
- SELF SHA-256:
  `d36208ad52a3b9d6a2fab6fa8f7910e1ecfa1c655fa1ff2f2a7a413204d59ad2`.
- Owner image: USA GZLE01 revision 0; SHA-1
  `6b5f06c10d50ebb4099cded88217eb71e5bfbb4a`; SHA-256
  `ec2d4ee790f48bee3d4c10feed166370df895f474e8db3f9af3b16ee001436df`.
- Installed disc: `/app0/game.iso`; shared profile: `/data/pswaker/`.
- Disposable cache: `/data/pswaker/cache/9ac6fb9b2da43e02d642/`.

Both packages are **1,516,568,576 bytes**. Assembly inspection and a second fresh
extraction/inspection passed for each; the Windows export hashes match.

| Package | SHA-256 | Fresh inspection |
| --- | --- | --- |
| `PSWaker-persistence-01.07.pkg` | `23bcdffaa4fa2cb9a379197a82940b3835fdf2646211b1019b37efd75df3302b` | [01.07](inspection-01.07.json) |
| `PSWaker-persistence-01.08.pkg` | `504a0548f62ad54fdb04b0836c94c8c679d91c66dc0fb51ccfec151527470205` | [01.08](inspection-01.08.json) |

[artifacts.json](artifacts.json) retains the package/update associations.
[provenance.json](provenance.json) retains source/patch hashes, the complete
port-input inventory and private inventory hashes. A comparison against 01.06
confirms the verified platform's archived/runtime/header/toolchain inputs are
unchanged. Both package versions now have matching returned console manifests
and owner observations; original build-time hardware-status labels stay intact.

## Retention and outstanding acceptance

- Windows private handoff: `local-research/persistence-20-artifacts/` in this
  checkout, containing clearly named 01.07/01.08 complete packages, matching
  `switchwaker.elf`, full input inventories, configure/compile logs, license
  review and package inspections. These files are ignored by Git.
- Linux private complete packages:
  `~/.local/share/pswaker-private/persistence-20-01.07/` and
  `persistence-20-01.08/`, with their assembly/tool logs and manifests.
- Prepared sources/build/full evidence:
  `~/.cache/pswaker/game-20-final/`; matching SELF:
  `build/program-stage/eboot.bin`. Older game-17/game-18/game-19 roots and
  historical owner evidence are retained.

The actual combined artifact's [license review](game-license-review.json)
retains pinned notices and platform provenance. Inherited SDK module/stub rights
and combined distribution terms remain unresolved under
[LICENSING.md](../../LICENSING.md); these artifacts stay private. No image,
extracted game data, save, ELF or package is committed.

The [owner return](console-return-2026-10-26/REPORT.md) supplies matching 01.07
and 01.08 manifests, five distinct candidate launches, successful target storage
checks and four byte-identical Standard settings snapshots. The owner confirms
saves behaved as expected, the visible setting survived full relaunch, separate
update and cache-only clearing, and Quit retained completed progress without
saving the unsaved action. No GCI snapshots were supplied for an independent
byte comparison in this return; save/load behavior is owner-reported. The prior
byte-identical GCI preservation evidence remains retained separately.

The bounded persistence checkpoint is complete. Outstanding: the Quit capture
records an idle card followed by a `JUTGba.cpp:623` panic/exit 12, without final
audio/GPU completion stages, despite the owner's normal visible return. This
lifecycle defect remains a #19/#21 follow-up. Controlled target unavailable-
storage, write-failure/corruption and pending-write trials remain #21. No power-
loss guarantee is inferred. File replacement is per write, not an all-or-nothing
multi-block gameplay-save transaction. No first-playable-wide acceptance or
broader compatibility is declared; do not overwrite real owner progress for
later controlled validation.
