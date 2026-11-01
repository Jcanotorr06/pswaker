# Applied PS4 prompts

Post-first-playable #79 slices. #99 added the semantic resolver, port legend
and refresh boundary. #100 converts message boxes and tutorials that use button
pictures. #101 adapts the meter's HUD controls and separate action-description
textures. Native-menu layouts, title, file selection and written instructions
remain unresolved. This does not extend #12/#18 acceptance or
claim that the whole game now shows PS4 prompts.

## Public contract

`platform/ps4/game/prompts.hpp` is the single new semantic seam. A `PromptRequest`
names a `GameAction` or `FixedControl`, gameplay/native-game-menu/port-menu
context, press/hold gesture, variant and direction. `resolve_ps4_prompt` consumes
one `AppliedControls` copy from `pswaker_applied_controls()`. That existing value
and its lookup declarations now live in the game-header-free
`controls-config.hpp`; `controls.cpp` still owns publication and synchronization.
No prompt settings, persistence, default configuration or pending lookup is added.

Results carry the snapshot generation and preserve gesture, variant and direction:

- `Icon`: public `Ps4Icon` identifier and accurate PS4 name, only when the
  adapter's availability function reports artwork it can actually render.
- `TextFallback`: the same accurate PS4 name, without an icon. A null availability
  function means text fallback, including for every action in the port legend.
- `Unresolved`: empty name, no icon and a nonempty coverage reason. Unknown
  controls, invalid applied bindings and incompatible variants never guess.

The nine action targets come from the existing applied bindings. Native game
menus use those same bindings. In port context A/Confirm is Cross, B/Cancel is
Circle and Start/Settings is Touchpad click, regardless of gameplay remapping;
other game actions have no assumed port meaning. Explicit port-control requests
require port context. D-pad navigation remains fixed.

Fixed stick movement, eight directions, clockwise/counterclockwise rotation and
horizontal/vertical animation remain distinct. An action bound to L3/R3 can
request a stick click; a fixed GameCube stick cannot invent a click binding.
Partial L2/R2 travel is below 90%; full travel begins at 90%, matching the
unchanged input bridge (229/255 versus 230/255). `TriggerPress` is a plain
L2/R2 press that does not require full travel, for GameCube L/R used as buttons.
Base stick/trigger icon IDs are
accompanied by the semantic variant and accurate qualified name; adapters must
preserve those qualifiers rather than display a bare icon that loses meaning.
Resolve each accepted alternative separately, keeping its gesture and variant;
an unresolved alternative is a coverage defect, not permission to omit it.

## Refresh and integration

Adapters register `pswaker_register_prompt_adapter(context, callback)` once on
the game thread with a lifetime through shutdown. Each callback receives the
whole applied snapshot and returns true only after rebuilding its retained
presentation. It must not publish controls or change registrations. Its first
refresh runs even for generation 0; later refreshes run when its generation
differs. Failed adapters are retried while successful peers retain their work.
An adapter registering later also refreshes before the next resume.

At the existing neutral-release gate, `controls.cpp` calls
`pswaker_refresh_prompts` before entering Game. Any false result keeps gameplay
paused and every game-facing input neutral. The port displays “Updating control
prompts...” until ready. Newly held input requires neutral release again.
Disconnect cancels the pending resume and still requires fresh fixed Cross
confirmation and neutral release. Apply, discard and storage semantics are
unchanged: only confirmed persistence publishes a new generation.

`main.cpp` registers the port presentation adapter before the first playable
frame. It rebuilds the entire legend and fixed descriptions into one value.
Opening the legend also rebuilds it on demand, so an Apply is visible there
before resume. Fixed Cross/Circle instructions resolve to the existing line/shape
symbols; Touchpad and D-pad instructions use accurate text. Long fixed-control
descriptions wrap. No raster artwork is introduced.

The maintained `game/CMakeLists.txt` compiles `prompts.cpp` into `pswaker_entry`.
The ordered patch series already connects this path: game-platform
`0002-complete-controls.patch` calls `pswaker_poll_controls` from the native
input hook and routes `PADRead` through the neutralization gate; game
`0004-ps4-runtime.patch` calls `pswaker_frame_boundary` after event pumping and
before the game frame begins. The resolver and refresh gate extend these hooks
without adding another game/input interception point. The normal maintained
input inventory includes the new source in build identity.

Startup still publishes exactly the profile selected by the shared storage
check: restored custom controls or complete-default recovery, with the existing
feedback and no fallback rewrite. The legend, resolver and gameplay then consume
that same applied generation from the first frame.

## Message pictures and tutorials (#100)

Message control tags become pictures, not font glyphs: `fopMsgM_outFontSet`
appends a `fopMsgM_buttonTex` BTI to a retained `J2DPicture` (plus a shadow),
and `fopMsgM_outFontDraw`/`Draw2` animate and draw it. The 2D out-font in native
game menus (`dDlst_2DOutFont_c::iconset` and its stick animations) does the same.
Because these paths are shared, message pictures inside the item, collection,
option and map menus are converted too. Those menus' own layouts remain for the
native-game-menu slice.

`platform/ps4/game/message-prompts.hpp` is the thin adapter. `plan_message_icon`
maps each picture number, after the game's own aliasing, to a resolver request:

| Picture | Request | Artwork |
| --- | --- | --- |
| 0x00 A, 0x14 flashing A, 0x01 B, 0x05 X, 0x06 Y, 0x07 Z | applied action binding | target icon |
| 0x02 C-stick | right stick movement | right stick with movement arrows |
| 0x03 L, 0x04 R | `TriggerPress` | L2 / R2, no travel gauge |
| 0x08 D-pad | D-pad | D-pad |
| 0x0E-0x11 Control Stick up/down/left/right | left stick direction | tilted left stick |
| 0x09 Control Stick | left stick clockwise | tilt follows the game's turn |
| 0x12 / 0x13 Control Stick up-down / left-right | left stick oscillation | tilt follows the game's turn |
| 0x0A-0x0D arrows, 0x15-0x17 heart, note, starburst | not controls | game picture kept |

Owner decisions recorded on 2026-10-31 for this slice:

- `TriggerPress` extends the #79 variant list. The original GameCube L/R are not
  used as triggers here, so L2/R2 prompts must not require full travel. Wind
  Waker's L-targeting and R-shield locks compare analog travel against
  `g_HIO.mTriggerThreshLo/Hi`, which a partial press passes. Any written
  instruction that distinguishes travel belongs to the literal-name slice.
- The project-owned prompt artwork below is approved for commit and
  distribution.
- Converting the message pictures inside native game menus, a side effect of
  the shared hooks, is approved.

Some game code reads the digital L/R bits instead (`CPad_CHECK_TRIG_L/R`, for
example in `d_menu_save.cpp`, `d_file_select.cpp`, `d_picture_box.cpp`,
`d_menu_fmap.cpp`, `d_a_agb.cpp` and `d_a_player_main.cpp`). The unchanged
input bridge sets those bits only at 90% travel. The prompt still shows a plain
press; whether those inputs should also accept partial travel is a gameplay
input change outside this presentation slice.

The ordered game patch `0013-message-prompts.patch` keeps the game's own
`remove`/`append` and heap use, then calls `fopMsgM_ps4Set`. A control picture
gets the PS4 texture through `J2DPicture::changeTexture` (no allocation), with
untinted colour and an unchanged black shadow. Animated sticks crossfade texture
0 with the tilted picture, so texture 0 becomes the neutral PS4 stick. The game
turns stick pictures clockwise from a left-tilted base; after each turn,
`fopMsgM_ps4Turned` swaps to counter-turned artwork. Labels stay upright, and
the displayed tilt matches the tag. `~J2DPicture` releases retained pictures.
So does `fopMsgM_blendDraw`, before the game puts its own texture on a picture,
for example the collection menu's selection arrow. A refresh never paints over
a reused picture.

Refresh joins the #99 boundary: `main.cpp` registers
`pswaker_refresh_message_prompts`. It also seeds the adapter with the startup
publication, so pictures created before the first resume already match. Each
retained pair records the generation it shows. After a successful Apply, the
gate rebuilds every live retained picture before gameplay resumes, including an
open dialog or tutorial. New pictures use the refreshed snapshot. Pending edits,
discard and failed or uncertain Apply keep the previous generation.

Every icon this surface uses has artwork. A presentation that lacks artwork for
an icon passes an availability function. The resolver then returns accurate
text, and the adapter shows a compact PS4 text tile (`OPTIONS`, `L STICK`). If
texture memory runs out, the picture is hidden and reported. An unresolved
control, for example an invalid applied snapshot, shows a
transparent picture: never a GameCube picture or a guessed binding. It is logged
once per picture number and generation as
`PROMPT unresolved surface=message-picture`. The message stays usable. Textures
are encoded once into host memory, never the game's current JKR heap. Resolver
text during game hooks also uses host allocation.

### Prompt artwork: licence and provenance

The owner-approved #79 contract requires this artwork: "Original, project-owned
DualShock 4 prompt artwork, committed with a recorded licence and provenance."
It is not a replacement for the hash-pinned game icon, launch splash or Windows
icon covered by the artwork rule in `CONTRIBUTING.md`.
`platform/ps4/game/prompt-art.cpp` draws all prompt artwork at run time, from
geometric shapes and a hand-defined 5x7 letter set. The artwork is original
work authored for this project and committed as source under PSWaker's
[GNU General Public License v3.0](../../LICENSE). No image files, Sony artwork,
game textures, texture-pack content or third-party fonts are used. The face
symbols are plain geometric shapes in the conventional PlayStation hues.
Shoulder buttons, triggers, stick clicks and Options are rounded bodies with
accurate labels (`L1`, `R2`, `L3`, `OPTIONS`). Sticks are a well and cap
lettered `L`/`R`. Movement arrows, tilts and the partial/full trigger gauge are
distinct poses. Every image is a 64 x 64 RGBA picture with a transparent
surround, sized for the existing square message slots. Other adapters can reuse
`render_prompt_art` and `render_prompt_label`; nothing here depends on the
game. To review the artwork, set `PSWAKER_PROMPT_ART_PREVIEW` to a directory
when running `test_prompts.py`; it writes PNG previews there, outside git.

## HUD and contextual action descriptions (#101)

The meter's layout controls and its separate `actionTex[0..2]` description paths
now resolve applied controls and retain their generation through the shared
refresh boundary. They reuse the original artwork through `prompt-textures.cpp`,
independently of message tags. See [HUD-PROMPTS.md](HUD-PROMPTS.md) for source
identifiers, the historical AStatus/B-action distinction, fallback behavior and
remaining coverage, and the [hardware checklist](HUD-prompts-checklist.md) for
default/remapped layouts and real retained-picture refresh observations.

## Coverage and source verification

[prompt-coverage.json](../../platform/ps4/prompt-coverage.json) contains identifiers
and `converted`, `text-fallback` or `unresolved` statuses only. Later adapters
extend it with individual layout/message/resource IDs. A listed unresolved
surface prevents calling that surface complete. Resource identifiers come from
code; no extracted messages, images or asset-bearing outputs are retained.

Rechecked against the source selection in `game.lock.json` and
`renderer.lock.json`, using prepared maintained sources:

- SwitchWaker `ba8d0a31446cd53ceaebd6b7269cca641e73bf4c`, with the maintained
  ordered game patches: `native/src/pc/runtime/pc_frame.cpp::pc_frame_begin`
  pumps events before the port boundary and before `aurora_begin_frame`.
- `game/src/f_op/f_op_msg_mng.cpp::fopMsgM_buttonTex` indexes 0x00–0x17 name
  BTI resources. The `fopMsgM_outFontSet` overloads replace `J2DPicture`
  textures; `fopMsgM_outFontDraw` and `fopMsgM_outFontDraw2` retain/draw those
  pictures. Changing resolver output alone cannot refresh them.
- #100 (prepared root with patches 0001-0013): the `fopMsgM_outFontSet`
  overloads are called from `d_msg.cpp`, `d_message.cpp`, `d_message_paper.cpp`,
  `d_mesg.cpp`, `d_scope.cpp`, `d_picture_box.cpp`, `d_menu_item.cpp`,
  `d_menu_collect.cpp`, `d_menu_option.cpp` and `d_menu_dmap.cpp`.
  `dDlst_2DOutFont_c::iconset` appends `fopMsgM_outFontTex` pictures directly.
  Stick animations rotate in multiples of -90 degrees and crossfade textures 0
  and 1. L/R locks (`mDoCPd_L/R_LOCK_*`) compare analog travel against
  `g_HIO.mTriggerThreshLo/Hi`.
- `game/src/d/d_meter.cpp` owns HUD/button presentation;
  `game/src/d/d_menu_item.cpp` changes `J2DPicture` textures. The native menu,
  file-selection and title surfaces still need their own adapters and coverage.
- Selected Aurora base `e281999cdb4fee6127525a9a9e97979480db4bf3`, reconciled
  through the maintained renderer patches: `include/aurora/texture.hpp`
  declares pointer/source key families and `ReplacementOptions::priority`.
  Future embedded-artwork conversion must account for both key families;
  this slice registers no texture replacements or pack precedence rule.
- The PS4 CMake selection still excludes `pc_hd_textures.cpp` and compiles
  `stock-textures.cpp` stubs. This slice has no dependency on an HD loader.

## Validation and owner follow-up

Run on Linux/WSL, with `PSWAKER_GAME_ROOT` pointing to prepared maintained sources:

```sh
python3 -m unittest discover -s tests/ps4 -p test_prompts.py -v  # resolver, art, message adapter
python3 -m unittest discover -s tests/ps4 -p test_controls.py -v
```

The resolver test compiles only the public resolver/configuration and synthetic
requests with Clang 21: no game data, game headers or GPU. It covers defaults,
all 54 action/target combinations, both game contexts, port context, fixed
variants, press/hold, alternatives, icon/text fallback and explicit unresolved
results. The installed harness uses real controls/storage code and simulated
console services. Retained synthetic presentations exercise multi-adapter
refresh, delayed readiness, successful Apply, pending/discard/failed/uncertain
Apply, disconnect during refresh and no held-input leakage. Existing startup
custom/default/fallback and all-target legend scenarios run through the resolver.

Host checks cannot prove real game-picture refresh, symbol readability, layout
fit or console behavior. On the next identified PS4 candidate, check the legend
after startup custom/default recovery, pending edits, Apply and discard/failure;
check fixed Cross/Circle/Touchpad controls after remapping A/B/Start, then
disconnect with held mapped buttons/sticks/triggers and deliberately resume.
Real HUD and native-menu layout refresh needs console evidence; the synthetic
retained presentations are not such evidence.

The #100 checks add the project-owned artwork and the message adapter. The art
check renders every icon and pose. It requires transparent surrounds, distinct
icons, trigger gauges and stick tilts in the right direction. Counter-turned
artwork must look identical after the game's clockwise turn. It also refuses
poses that would misdescribe a control and checks the text tiles. The adapter
check covers every control picture number with default and remapped bindings,
directions and animated turns, and the plain L/R press. It also checks
non-control pictures, missing-art text, unresolved hiding and reporting, and
the GX RGBA8 encoding against an independent decoder. Retained pictures are
checked through set, turn, destruction and refresh. The installed harness keeps
a real adapter picture open through Apply, discard and failed/uncertain Apply.
It must show R3 before the gate releases gameplay, and only after a successful
Apply.

Host checks cannot prove the real `J2DPicture`/GX path, artwork readability at
message size, or console behaviour. For the hardware checklist, with stock
textures, observe these on default and remapped layouts (for example A on R3,
Z on L1):

1. A dialog with A/B pictures, such as Orca's sword lessons on Outset, shows
   Cross/Circle by default and R3 after remapping A. Labels read upright, with no
   clipping, and shadows look right.
2. The telescope (`d_scope.cpp`) and any tutorial with Control Stick pictures:
   directional pictures tilt the correct way, and the animated rotate and
   up/down or left/right pictures animate with an upright `L`.
3. A message with an L or R picture shows L2/R2, and the C-stick picture shows
   right stick movement.
4. Open a dialog showing A, open port settings, remap A, Apply and resume. The
   still-open dialog must show the new binding on the first frame of gameplay.
   Repeat with discard and a failed Apply: the previous binding remains.
5. Relaunch with the custom layout: the first dialog already shows it.
6. Check the log for `PROMPT unresolved` lines. A clean run reports none.
