# PS4 message icons and tutorial prompts (#100)

Host and target-compile validation on 2026-10-31, against task base
`f29a4bfe387f9aff8d4185399979716c68859671` (`develop`).

## Changes exercised

- Original prompt artwork drawn by project code (`prompt-art.cpp`): face symbols,
  shoulder/trigger/stick-click/Options/Touchpad labels, D-pad, sticks (neutral,
  moving, eight tilts) and partial/full trigger gauges. Licence and provenance
  are in the [contract](../../../docs/ps4/PS4-PROMPTS.md#prompt-artwork-licence-and-provenance).
- Message picture adapter (`message-prompts.cpp`). It maps `fopMsgM_buttonTex`
  picture numbers to resolver requests, encodes GX RGBA8 `ResTIMG` images in
  host memory, and retains pictures until `~J2DPicture`. It joins the #99
  refresh boundary and reports unresolved coverage.
- Resolver `Trigger` variant for L/R tags, which make no travel distinction.
- Ordered game patch `0013-message-prompts.patch`: `fopMsgM_outFontSet` (both
  overloads), `fopMsgM_outFontDraw`/`Draw2`, `dDlst_2DOutFont_c::iconset` and its
  stick animations, `fopMsgM_blendDraw` (releases reused pictures) and the
  `J2DPicture` destructor.
- [Coverage inventory](../../../platform/ps4/prompt-coverage.json): message tag
  kinds, retained-picture owners and representative message contexts. Native
  menu layouts, HUD, title, file selection, written instructions and
  embedded artwork stay unresolved.

## Verification

- Independent Standards and Spec reviews ran before commit. The spec review found that a refresh could overwrite a picture the game reused through `fopMsgM_blendDraw`, and that missing-art text was unreachable through cache exhaustion. Both are fixed, and the target build and suites were rerun.
- Red/green tracers: the resolver check first failed to compile without the
  `Trigger` variant. The art and adapter checks failed on their missing sources
  before implementation.
- `test_prompts.py`: 4 passed. These are the public resolver contract, the
  artwork check, the message adapter check and the asset-free inventory check,
  compiled with Clang 21, C++23, `-Wall -Wextra -Werror`. No game headers, game
  data or GPU are involved.
- `test_controls.py`: 30 passed against a fresh maintained game root prepared
  by `prepare-game.py` with patches 0001-0013. The prompt scenarios keep a real
  adapter picture open through Apply, discard, failed Apply and uncertain Apply.
  It shows R3 before the gate releases gameplay, and only after a successful
  Apply.
- The prepared root differs from the previous maintained root (`shader-110`)
  only in the four files touched by `0013-message-prompts.patch`.
- Full Linux host suite with that prepared root: **230 tests, 131 passed, 99
  skipped** (unavailable platform, GUI or tool requirements), no failures, in
  99.7 seconds (rerun after the review fixes).
- Pyright with the repository configuration: zero errors, warnings or
  informational diagnostics. Changed Python compiles and `git diff --check`
  passes.
- Maintained PS4 CMake target `switchwaker_eboot`, configured fresh against the
  prepared root: compilation, ELF link and `eboot.bin` generation passed, and
  `check-oelf` reported segments OK. The touched game, adapter and art units
  produced no warnings. The diagnostic ID is `unverified-100-compile`; it is
  not a packaged or independently inspected program candidate.

The artwork was reviewed as PNG previews from `PSWAKER_PROMPT_ART_PREVIEW`
(kept outside git). Every icon reads clearly at its native 64 x 64 size.

No disc data was used. No game text, game images, texture-pack content or
asset-bearing outputs were added. No packaged candidate is claimed, and no
existing console evidence was changed.

## Limits

Host checks use synthetic picture handles. They cannot prove the real
`J2DPicture`/GX path, artwork readability at message size, layout fit,
animation on hardware, or that an open dialog visibly changes on console.
Those are owner checks 1-6 in the
[validation section](../../../docs/ps4/PS4-PROMPTS.md#validation-and-owner-follow-up),
to be recorded against an identified PS4 candidate. No new hardware pass or
first-playable acceptance is claimed.
