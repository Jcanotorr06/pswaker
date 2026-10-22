# Version 01.02 console evidence

Evidence for [Validate Aurora geometry and internal resolution after the failed Slim diagnostic](https://github.com/Jcanotorr06/pswaker/issues/11),
on the disposable `prototype/ps4-platform-diagnostic` branch.

The owner installed version 01.02, ran it as instructed, reconfirmed PS4 Slim /
firmware 9.00 / GoldHEN v2.4b18, and reported the expected RGB triangle, white
background, purple swatch, summary text and quiet continuous tone. Their
[photo](visual.jpg) shows those visuals and reports build
`4b1830b0443ff170425e`, internal 1280x720, surface 1920x1080, and zero failures
at 62.9 seconds. The photo supplements the complete logs; it does not itself
establish the ten-minute result or measure color accuracy.

## Evidence association

[capture.py](capture.py) hashes every supplied file, reads only the latest
`BEGIN` block of each appended diagnostic/runtime snapshot, and asserts its
build, manifest, counts, pixel comparisons, runtime state, cache sequence and
shutdown ordering. It reconstructs long manifest lines from the application's
1023-byte `fgets` chunks before comparing the embedded manifest with the
[inspected candidate](../aurora-correction-20261022/native/build-info.json).
This is an evidence parser, not a rendering reproduction or a new console run.

The original snapshots contain seven, eight and nine launches, including older
failed versions; counting whole files would duplicate history and mix binaries.
Original files and cache databases remain untouched under
`local-research/diagnostic-artifacts/aurora-gx-fix/output`. Their sizes/hashes,
including the unchanged photo, are in [retrieved-files.json](retrieved-files.json).
Only isolated current-run diagnostic/runtime/display extracts and the photo are
captured on this branch. The [summary](summary.json) contains derived counts and
resource ranges. Reproduce in WSL2:

```bash
python3 prototypes/ps4-platform/evidence/aurora-pass-20261022/capture.py \
  '/mnt/c/Users/Joseph Cano/Code/pswaker/local-research/diagnostic-artifacts/aurora-gx-fix/output'
```

| Supplied run | Launch | Cache entries before Aurora | Frames | Checked cycles | Failures |
| --- | --- | --- | --- | --- | --- |
| Cold | 7 | 0 | 35,836 | 120 | 0 |
| Warm 1 | 8 | 2 | 35,992 | 120 | 0 |
| Warm 2 | 9 | 2 | 35,908 | 120 | 0 |

Each run records about 600.3 checked-loop seconds, excluding shader preparation,
and a passing ten-minute check. Preparation takes 111.6 ms cold and 34.9 / 35.4 ms
in the warm runs.
Cache counts corroborate the owner's cold/warm labels and followed instructions.
State advances 7 -> 8 -> 9 and the platform exits with status zero each time,
supporting the close/relaunch and persistence sequence.

## Demonstrated operations

All runs select the matched Vulkan platform: AMD Liverpool (PS4), RADV BONAIRE,
Mesa 26.0.8 `git-60e95b7878`, FIFO presentation. Display logs report 1920x1080
at 59,940 mHz. The internal size check and all 120 allocated EFB snapshots per
run independently report **1280x720**; scanout size is not used as internal proof.

Every run passes all 120 EFB white comparisons and all 120 offscreen white
comparisons: each checks 1,024 RGBA pixels against `(255,255,255,255)` with zero
mismatches. Mapping succeeds and logs texture dimensions/format. The 120 raw
WebGPU textured depth/blend/copy/readback comparisons per run also pass their
unchanged purple expectation `(128,0,127,255)` with tolerance one. Visible GX
geometry comes from the owner's observation/photo, rather than an inference
from the separate raw WebGPU check. There are ten target creations per run,
including initial allocation and nine in-loop recreations with checks afterward.

Constructor, TLS isolation/destruction, once, condition-variable, atomic-wait,
file read/flush/sync/close and rename checks pass. Each run records two controller
disconnect/reconnect cycles and passes deliberate resume; no neutral-input
failure is logged. Synthetic audio reports zero API errors in every resource
sample and at shutdown, consistent with the owner's continuous-tone observation.
Audio-frame production counters do not measure hardware underruns. Retrieved
logs demonstrate the agreed evidence workflow.

## Resources and teardown

There are 21 resource samples per run. After startup, garlic bytes plateau at
438,665,216, onion at 835,584, buffers at 43 and available flexible memory at
396,361,728. Main-mspace allocation ranges after 60 seconds are
4,002,032-4,016,192, 3,825,936-3,840,112 and 3,826,032-3,840,096 bytes,
respectively. Allocation fluctuates within a small band and has a small final
increase; per-run endpoints are preserved in the summary. No sustained growth
trend is observed in the sampled driver counts
or main-mspace allocation. This bounded observation does not measure every
allocator or prove absence of all leaks.

All runs pass `GPU-queue-drained`, enter intentional Aurora shutdown, report
`Device lost: Device was destroyed` and the unsupported screensaver warning,
then complete shutdown and write `END ... failures=0`. Neither warning occurs
during the checked loop. The earlier buffer-mapping-abort message is absent.
The original warnings remain in the evidence; passing counters alone do not
override their review. Platform logs confirm exit status zero.

## Build and decision status

The console-tested package remains version 01.02, build
`4b1830b0443ff170425e`, compiled source
`b45d5e29246bd1c86d78f9ca165cbc3f7b4d6e5b`, PKG SHA-256
`9764e1acb1e7fa8a17c8c7aee9ca3793ac908da38368188b52de33a49dd399be`.
The full manifest and ELF/SELF identities remain in the
[correction/build report](../aurora-correction-20261022/status.md).

Two renewed clean builds completed successfully from previously absent roots:
`/home/joseph_cano/.cache/pswaker/aurora-clean-a-20261022` and the corresponding
`aurora-clean-b-20261022`. Only verified download archives were reused; each root
independently prepared/patched sources and compiled LLVM runtimes, SDL, Dawn,
Mesa, Aurora, the diagnostic and LibOrbisPkg. Both complete `clean-build.sh`
invocations succeeded without a resumed compile. The script uses the historical
01.00 SFO default, so [package-clean.sh](package-clean.sh) then packaged the same
compiled objects as 01.02. Both package-version steps succeeded. No diagnostic
source changed: excluding Markdown/evidence, it matches the console candidate's
compiled revision, and the build identity remains `4b1830b0443ff170425e`.

| Build | Fresh preparation start (UTC) | Final 01.02 packaging complete (UTC) |
| --- | --- | --- |
| clean-a | 2026-10-22 22:52:22 | 2026-10-22 23:15:38 |
| clean-b | 2026-10-22 22:52:32 | 2026-10-22 23:15:37 |

[collect-clean.py](collect-clean.py) verifies the new pair against each other
and against the inspected console candidate: source archives, SDK, adaptations,
host versions/packages, Dawn DEPS, Mesa/libdrm pins, NuGet locks and normalized
CMake download closure. Package extraction verifies the eight-file payload,
01.02 SFO/title/category, SELF/hash association, compiled identity and corrected
checkpoints. Native build logs also pass OELF segment checks.
See [clean-summary.json](clean-summary.json), [comparison.json](comparison.json),
and the full [clean-a](clean-a/) / [clean-b](clean-b/) manifests/logs.

| SHA-256 | clean-a | clean-b |
| --- | --- | --- |
| PKG | `1fb55a00c292ff80084b9f037167376d92f9c2f32ec3a54100a4f703a77e6dfb` | `6334121bfe8995b36940614fb9903ebafb344169bf0b280b487b789b3e7bf605` |
| SELF | `113d7a42f67609687885e8f5506fb377bdc870a3f36d3f45ef9c564fcf6d3265` | `b329edc3d4d4e3242a112e5ca4a3ea51e3331d9612abdeff02a8b2264d406a2a` |
| ELF | `011aea33d700fcc57eb12e7c5959223ff562c0766372d0776d2397d201a5a771` | `af00a18171df85c1d2efe97cb8300645840a38debf12e0a1b126595819ae2512` |

The two new packages/ELFs are not byte-identical. Within the logical package
payload, only `eboot.bin` and `build-info.json` differ. Allocated ELF section
differences are confined to `.text`, `.rodata` and `.rela.dyn`. The
[bounded difference audit](difference-analysis.json), using the existing audit
with explicit roots, finds 57,889 changed instructions referring to equal
normalized nonempty ASCII strings and 1,060 referring to equal empty/non-ASCII
NUL-terminated bytes. No other changed instruction remains. All 11,881 changed
relocations retain their location/type and refer to equal normalized
NUL-terminated rodata targets. This supports build-path/constant-pool layout
differences; the audit does not prove arbitrary binary constants or runtime
semantics equal. No bit-for-bit reproducibility claim is made.

The evidence collector's first metadata capture failed because Linux Git cannot
read this Windows worktree's Git pointer. The final capture takes the full base
revision verified with Windows Git explicitly; this did not alter or resume
either successful clean build. Reproduce collection from PowerShell in this
worktree (the original clean roots remain local):

```powershell
$revision = git rev-parse ef3763e
wsl --exec python3 prototypes/ps4-platform/evidence/aurora-pass-20261022/collect-clean.py `
  /home/joseph_cano/.cache/pswaker/aurora-clean-a-20261022 `
  /home/joseph_cano/.cache/pswaker/aurora-clean-b-20261022 `
  /home/joseph_cano/.cache/pswaker/startup-20261021 --evidence-base-revision $revision
```

These are newly compiled host artifacts, not additional console runs. Their
hashes are not substituted for the installed candidate, and the installed local
01.02 package still has its original recorded SHA-256. Together, the reviewed
owner evidence on that exact candidate and the renewed source-matched build pair
satisfy the bounded disc-free diagnostic gate. The historical failed builds and
01.01 console result remain preserved.

The correction addresses a diagnostic contract error without evidence requiring
a different architecture. The tested scope is disc-free platform readiness;
game integration, game DSP, game saves, gameplay performance and the agreed
first-playable route still require their own implementation and hardware checks.
Final specification approval remains a separate human decision.
