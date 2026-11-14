# Native game menu PS4 prompts (#102)

This post-first-playable slice of #79 uses applied gameplay bindings in native
game menus. Port settings, confirmation and reconnect screens retain their fixed
Cross/Circle/Touchpad instructions. It does not expand #12 or #18 acceptance.

## Source ownership

Audited against `game.lock.json`'s SwitchWaker `ba8d0a3`, with ordered game
patches through `0016-native-menu-prompts.patch`. No disc resources were read.

| Native menu family | Instruction path | Presentation |
| --- | --- | --- |
| Inventory, item descriptions and bags | `d_menu_item.cpp::itemnoteSet/outFontDraw`, `dDlst_2DOutFont_c`, and the meter's A/B/X/Y/Z pictures | Existing message and HUD adapters resolve the applied actions; native words, item art, directions and gestures stay intact. X/Y/Z assignment prompts remain separate, in the existing item slots. |
| Window and collection | `d_menu_window.cpp::dMs_Draw/dMs_Execute`, `d_menu_collect.cpp::outFont*`, meter pictures | Existing message/HUD adapters plus a native footer naming both B and Start for Close. It is queued in `ITEM_MOVE`, `COLLECT_MOVE` and `COLLECT_MOVE_TACT`, whose input conditions accept both, never in an item explanation, subwindow, save dialog or page animation. |
| Native options, save and dungeon map | `d_menu_option.cpp::outFont*`, `d_menu_save.cpp` message processing, `d_menu_dmap.cpp::outFont*` | Shared message pictures; these are native menus, including native confirmations, and follow gameplay bindings. They are distinct from the port's settings and confirmation screens. |
| Sea chart and chart comparison | `d_menu_fmap.cpp::outFont`, `d_menu_fmap2.cpp::screenSet` | Shared message pictures plus retained L/R pictures and shadows at `f_hikaku_1.blo[KL,KL2,KR,KR2]`. Fixed L2/R2 preserve the native page arrows and shadow tint. |
| File selection and name scene | `d_s_name.cpp::buttonIconCreate`, `main_parts_fileselect.blo[baa,bab]` | Retained applied A/B pictures, including while the scene changes between file, name and native save screens. Select/Back words and native visibility/animation remain. |
| File selection accepted alternatives | `d_file_select.cpp::dataSelect/dataSelectEx`, `_draw`, `dDlst_FileSel_c::draw` | Accurate text names both A and Start for Select only when the active native procedure accepts both. Copy/erase confirmations, memory-card errors, name entry and transitions do not inherit that alternative. |

`menu-prompts.cpp` is a thin adapter to `resolve_ps4_prompt` in
`NativeGameMenu` context. It adds no binding authority or pending-controls lookup.
The message/HUD adapters remain shared with gameplay; their native menu callers
consume the same applied snapshot. Port menus do not call the native adapter.

## Retained presentation and fit

The adapter joins the shared before-resume refresh boundary in `main.cpp`, and
is seeded after startup publishes saved controls. Pictures record a generation,
rebuild when that generation changes and unregister in `J2DPicture` destruction.
Context-specific alternative strings are rebuilt from that same snapshot before
resume. Pending edits, discarded restores and failed/uncertain Apply do not
publish a new generation. Input processing and the neutral release gate are
unchanged.

File-selection control slots grow around their original centres to 32x32 before
pane data captures their dimensions. This preserves circular proportions and
gives R3/Options the same space as face controls. The chart controls retain their
24x24 slots. Both reuse the original geometric PS4 artwork, with accurate compact
text fallback; [licence and provenance](PS4-PROMPTS.md#prompt-artwork-licence-and-provenance)
remain GPLv3, project-authored source with no external images or fonts.

Accepted-alternative text uses the game's existing message font in a separate
544-pixel footer at native UI coordinates (32,424), 16-pixel type. Even the
longest two legal target names plus the action fit that width. The footer keeps
the original context instructions and item artwork, rather than replacing them
with a mapping legend. Actual overlap, contrast, readability and clipping still
require the [hardware checklist](Native-menu-prompts-checklist.md).

Missing expected panes are reported as `PROMPT unresolved surface=menu-*`.
Unknown controls, unresolved requests and registry/texture exhaustion suppress
the affected picture and report a reason, never substituting a GameCube tile or
a guessed binding. These coverage failures do not hold the input gate closed.

## Coverage limits and embedded-artwork handoff

The [asset-free inventory](../../platform/ps4/prompt-coverage.json) records the
source paths and individual layout tags above. Converted means the source path
is adapted; it does not claim console acceptance or an audit of every resource.

The native menu family aggregates remain **unresolved** until the owner's stock
resources and returned console observations establish the remaining literal and
embedded instructions. Native name-entry artwork (including controller diagrams
or Y/Z alternatives), window cloth/model artwork, file-selection resource text,
and any shared instruction atlas require the dedicated embedded-artwork and
literal-instruction slices. Preserve exact resource IDs and statuses in the
inventory when they are discovered; do not commit extracted text or images.
This change does not implement texture replacements or the HD loader. It uses
stock textures and does not depend on a pack. It cannot claim complete menu
coverage while those gaps remain.

## Verification

Use #79's pre-agreed resolver and installed-controls seams. `test_prompts.py`
already covers every action on all nine targets in native-menu context, fixed
movement/D-pad/trigger semantics, gestures, missing icons and unresolved results.
`test_controls.py` now keeps native menu pictures open beside HUD/message pictures
through remapped A/B/Start, successful Apply, pending edits, discard, failed and
uncertain saves, delayed refresh and reconnect. It checks new pictures and both
accepted-alternative strings before resume, fixed L2 and fixed port navigation.
Real layout assets and fit require console evidence; hosted checks do not prove
that a resource path is fully converted.
