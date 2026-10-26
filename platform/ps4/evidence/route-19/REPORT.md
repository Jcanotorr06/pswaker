# Route/audio candidate for issue #19

The 01.06 private complete package is built and independently extracted/inspected.
It preserves the owner-tested route baseline and adds repeated audio-failure
counters and normal card/audio/GPU shutdown coordination. The
[owner return](owner-return-01.06/REPORT.md) now confirms the requested title-to-
end-of-Outset scenes/actions without visual or audible anomalies, and confirms
relaunching a completed save works. The owner further confirms both empty-cache
and retained-cache runs and clean Touchpad → Quit → Cross closure without hanging
or lingering audio. **Logs could not be retrieved.** Association
with 01.06 is contextual to the handoff; installed binary identity, cache state,
audio counters and shutdown stages are not independently corroborated. #19
remains open for its outstanding log/candidate corroboration and internal
shutdown-stage evidence. No pending-write overlap is claimed.

Use [ROUTE-AUDIO.md](../../ROUTE-AUDIO.md) for the source review, behavior and
limitations, and the [owner checklist](../../Route-audio-checklist.md) for the
required cold/warm route, focused rendering/audio, normal Quit and log return.
The historical [#17 route observation](../startup-17/console-2026-10-25/REPORT.md)
and [#18 controls observation](../controls-18/console-return-01.05/REPORT.md)
remain associated with their original binaries. The startup owner reached
Dragon Roost after Outset, the forest, Forsaken Fortress and Windfall without
reported visual/audio glitches. Its pauses on large-area entry/first effects
remain a measured-performance follow-up in #22. No specific uncertain visual
defect was supplied for an original-game comparison; the checklist requires
one for any uncertainty in this candidate's return.

## Candidate identity

- Application: PSWaker / PSWK00001 / IV0000-PSWK00001_00-PSWAKERGAME00000.
- Version: 01.06; compiled build ID: be1a11cf3fcabee4911d.
- Package: PSWaker-route-audio-01.06.pkg; 1,516,568,576 bytes.
- Package SHA-256: 4df6f80a5e1cc8308ba8c342a1edd4f69ed187dd73c476beaf08dd6d068f6101.
- Matching unstripped ELF SHA-256: b14c5f12212d9835bb3793869bcf6f79131fb2353fcc6a7087cbbfae86ce936f.
- SELF SHA-256: 334b28b9e30d2d2b1111110e4cb96430d1dd34fc41be00fe7ce93e639fe4d83a.
- Image: USA GZLE01 revision 0; SHA-1 6b5f06c10d50ebb4099cded88217eb71e5bfbb4a;
  SHA-256 ec2d4ee790f48bee3d4c10feed166370df895f474e8db3f9af3b16ee001436df.
- Installed content: /app0/game.iso; shared user root: /data/pswaker/.
- Disposable cache: /data/pswaker/cache/be1a11cf3fcabee4911d/.

[artifacts.json](artifacts.json), [fresh inspection](inspection-01.06.json) and
[provenance](provenance.json) preserve exact associations. Stable update identity,
stock textures, original 30 Hz logic and 1280×720 internal rendering remain.
The owner return uses the earlier PS4 Slim / firmware 9.00 / GoldHEN v2.4b18
baseline; this follow-up did not separately reconfirm the environment.

## Host checks and review

The locked-host build compiled the actual game, linked the unchanged verified
#15 platform archives, converted ELF to SELF and staged the program with its
input-closure guard intact. The [ABI audit](game-abi-audit.json) records Jaguar
flags, retained symbols/source lines and no unresolved TLS initializers.
The first compile caught a missing logging declaration in the new evidence
unit; the include was corrected and the successful build reconfigured before
staging. Its final manifests cover the corrected source. No failed executable
was handed off. [Host recovery](host-recovery.json) records successful build and
restoration of the current zlib after the documented temporary locked version.

[All 39 host tests passed with zero skips](host-checks.log). Five new audio
scenarios run real DMA/SDK threads and Aurora address conversion with SDL
services simulated: literal big-endian right/left PCM, format retry, repeated
queue drops, queue-query failure and stream-drain failure. They establish
producer join before stream destruction, not game DSP or audible PS4 output.
Two card scenarios run the real game card manager and SDK mutex/thread code
through public initialization/update/save/status/SaveSync APIs. Simulated
storage blocks/fails a requested store; tests verify queued/active work is busy,
completion/failure is preserved, and observation creates no additional store.
Imported JKR thread-registration/heap services are inert in that harness; no
GCI data, game assets or durable writes are exercised.

Existing controls tests verify deliberate menu Quit; the complete application's
card → SDK/audio → GPU → Aurora sequence is source-reviewed. Clean normal console
Quit is now owner-confirmed, but internal completion stages were not returned.
The [emitted-link audit](route-link-audit.json)
ties card observation, SDK shutdown, producer join/stream teardown and both
selected SDL backend output/drain calls to this ELF. It establishes emitted
calls, not dynamic ordering or console results. Python byte-compilation and
git diff --check passed. Complete assembly and a second fresh extraction verify
package metadata, installed payload hashes and matching ELF/SELF/image.

Independent [Standards and Spec reviews](REVIEW.md) have zero outstanding
findings after the card-observer tests addressed their initial validation gap.

## Private retention and owner handoff

- Windows: local-research/route-19-artifacts/ in this checkout, containing
  PSWaker-route-audio-01.06.pkg, switchwaker.elf, complete input inventories,
  configure/compile logs, notices and host evidence.
- Linux complete package: ~/.local/share/pswaker-private/route-19-01.06/.
- Prepared sources/build/full manifests: ~/.cache/pswaker/game-19/.
- Matching SELF: game-19/build/program-stage/eboot.bin.
- Verified platform: ~/.cache/pswaker/maintained-15-a/; earlier game-17/game-18
  trees and owner evidence remain preserved.

The [artifact-specific license review](game-license-review.json) retains program
hashes, pinned notice inventory and platform-license association. Inherited SDK
module/stub rights and combined distribution terms remain unresolved under
[LICENSING.md](../../LICENSING.md). Artifacts stay private; no disc, extracted
data, save, ELF or package is committed.

Requested route scenes/actions and absence of visual/audible anomalies are now
owner-confirmed in both empty-cache and retained-cache runs, together with
completed-save relaunch and clean normal port Quit. Per-launch log/candidate/cache
corroboration and internal shutdown-stage evidence remain outstanding; no console
log was available for this return. Keep these limits
alongside the [original owner statement](owner-return-01.06/owner-observations.json).
The selected backend exposes no documented hardware underrun count. Repeated
software queue drops, DMA skips, stream/backend errors or audible defects require
investigation; clean counters cannot prove hardware underrun absence. A failed
store/30-second pending-work timeout offers Retry or explicit error Exit without
claiming a successful save. Stream conversion drain has a two-second deadline.
Full persistence/failure recovery and six-sample frame-pacing acceptance remain
separate work. No automatic gameplay save or broader compatibility is introduced.
