# HUD and contextual PS4 prompts (#101)

This post-first-playable slice of #79 converts the maintained meter paths. It
does not extend #12/#18 acceptance. Hardware observations are still required;
source inventory and host checks do not establish full-game visual coverage.

`hud-prompts.cpp` translates meter controls to the existing semantic resolver.
It consumes a whole applied snapshot, seeded after startup publication and
refreshed at the shared before-resume boundary. Each live picture records its
generation. Layout pictures and action descriptions rebuild together after
successful Apply. Pending edits, discard and failed or uncertain Apply do not
publish a snapshot and leave the presentation unchanged.

The ordered game patch `0014-hud-prompts.patch` follows the message patch. It
hooks meter layout setup and every assignment of `actionTex[0..2]`. The HUD
adapter has no dependency on message-tag conversion: both adapters use
`prompt-textures.cpp`, the shared GX RGBA8 cache, and the original project-owned
artwork in `prompt-art.cpp`. Licence and provenance remain recorded in
[PS4-PROMPTS.md](PS4-PROMPTS.md#prompt-artwork-licence-and-provenance): original
geometry and hand-defined letters, GPLv3, no game or pack artwork or fonts.
`game/CMakeLists.txt` includes the adapter and shared cache in `pswaker_entry`.
Stock textures work independently of optional HD support; no HD loader or
embedded-artwork replacement rule is introduced here.

The maintained source was rechecked at SwitchWaker
`ba8d0a31446cd53ceaebd6b7269cca641e73bf4c` with patches 0001–0014. Read-only local
inspection of the owner's USA revision-0 layout verified picture tags, texture
identifiers and dimensions. No disc data, extracted pictures, text or converted
outputs are included in this repository.

| Meter pictures / texture paths | Semantic control |
| --- | --- |
| `main_parts1.blo`: `baa`, `baa2` | Applied A, including the alternate/parry presentation |
| `bab` | Applied B |
| `bax1`, `bay`, `baz` | Applied X, Y, Z |
| `bar1`, `r` / `l` | Fixed R2 / L2 plain press |
| `crs1`–`crs4` | Fixed D-pad; native direction arrows retained |
| `actionTex[0]`: `weit`, `witk`, `bawd` | B: weapon/action description from `AStatus` |
| `actionTex[1]`: `yum`, `yumk`, `bawp` | A: contextual description from `DoStatus` |
| `actionTex[2]`: `basv` | R2: description from `RStatus` |

`AStatus` is a historical name for B/sword actions. The player's `doTrigger()`
reads A, while `swordTrigger()` reads B. The adapter follows these actual input
consumers. Action descriptions keep their game-owned words and weapon art;
their separate control pictures show the applied physical button. Changing a
binding therefore preserves talk/pick-up/climb meaning and any press/hold
description. It does not substitute a generic legend. No alternatives, stick
direction arrows, counters or item pictures are removed. The inspected HUD has
no Start or stick-motion label to replace; these remain available in the resolver
and their other presentation surfaces keep their own coverage status.

The original 16-pixel letter overlays expand around the same centre to 32×24
slots, including Options and R3. Pane position and size metadata are updated so
the meter's movement and scaling routines keep the extra space. The Z picture
uses 40×32. Original contextual descriptions and their shadows keep their native
spacing, colours, animation and alpha. Control artwork has untinted colours and
an opaque contrasting body. Final readability and overlap checks remain on PS4.

New pictures immediately use the adapter's applied snapshot. Destruction and
`fopMsgM_blendDraw` reuse release retained records so refresh never accesses a
dead picture or paints over a reused item/number picture. Action buffers remain
game-owned; each context update records the new status and texture. Texture and
resolver allocations use host memory, outside the current game heap.

All currently requested icons have original artwork. A missing image tries a
compact accurate PS4 text tile through the same cache. Exhausted texture memory,
an invalid snapshot or unknown control suppresses the affected picture with a
transparent texture and reports `PROMPT unresolved surface=hud-layout-picture`
or `hud-action-description`. Reports are deduplicated by control/action status
and applied generation. A full retention registry also suppresses and reports
the untracked picture, preventing a stale binding after Apply while play remains
usable. There is no option to return to GameCube artwork.

The asset-free [inventory](../../platform/ps4/prompt-coverage.json) lists each
layout tag, all seven description pictures and every known `dMeter_actionTex`
status. An unlisted action status is explicitly unresolved: the game otherwise
silently substitutes its first action texture. The patch suppresses and reports
such a description instead of guessing. An unresolved observation must be added
to the inventory before declaring that context covered. Native-menu layouts,
title/file-select, literal names and unreviewed embedded instructions remain
unresolved under the other #79 slices.

Validation uses the pre-agreed #79 boundaries. The resolver checks all 54
action/target combinations, gestures and fixed-control variants. The installed
controls harness keeps synthetic HUD control and description pictures alive
through Apply, pending edits, discard, failed/uncertain Apply, delayed refresh,
disconnect and neutral release. It checks the new binding before resume and
preserves the context texture. These checks do not test real game assets or
prove layout fit. Run `test_prompts.py`, `test_controls.py` with prepared sources,
and a maintained PS4 target build; then complete the
[console checklist](HUD-prompts-checklist.md).
