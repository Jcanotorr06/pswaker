# Applied PS4 prompts: resolver and port legend (#99)

This is the first #79 slice, after first playable. The port legend and fixed
port instructions use the semantic resolver. In-game pictures and written
instructions remain unresolved; this does not extend #12/#18 acceptance or
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
unchanged input bridge (229/255 versus 230/255). Base stick/trigger icon IDs are
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
python3 -m unittest discover -s tests/ps4 -p test_prompts.py -v
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
Real HUD/dialog/native-menu refresh belongs to the later adapters and needs new
console evidence; the synthetic retained presentations are not such evidence.
