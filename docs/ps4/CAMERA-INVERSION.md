# Camera and aiming inversion (#97)

This is the source-path inventory for the post-first-playable #78 contract.
Hardware acceptance belongs to #98. It does not extend #12, #18 or #20, or
establish full-game camera validation.

## Configuration and publication

Controls exposes **Invert camera X** and **Invert camera Y**, each Off by
default. Cross toggles one pending value per fresh press. Each row shows its
pending and applied value. The same switches govern camera look and aiming.
Apply saves all six bindings and both switches before publishing a complete
applied generation. Discard, failed Apply and uncertain completion leave the
previous in-memory generation active. Retry saves the whole pending value.

`pswaker_publish_controls` initializes and updates the pinned
`pc_camera_invert_x/y_set` APIs from the authoritative applied snapshot, under
the publication mutex. Startup and menu Apply execute on the game thread,
before game logic can run or resume; native camera/aiming readers run on that
thread. Snapshot readers cannot observe publication before both setters finish.
The native setters are game-thread APIs, not a second concurrent configuration
interface. Pending editor operations never call them. Startup publishes after
`PortSettings::check`, including complete default/fallback configurations, so
desktop environment defaults cannot override the port profile.

The maintained runtime patch `0004-ps4-runtime.patch` bypasses desktop
`menuInit`/settings setup on PS4. The profile and port applied lookup supply
configuration independently of that setup. No raw PADStatus axis or shared
controller cache is negated. New game-source changes live in
`0011-camera-aiming-inversion.patch`, applied by `prepare-game.py` after the
earlier maintained game patches.

## Pinned source inventory

Paths below are relative to SwitchWaker
`ba8d0a31446cd53ceaebd6b7269cca641e73bf4c`, recorded in `game.lock.json`.
References use function names so the inventory survives patch line shifts.

| Context | Input reader and semantic hook | Coverage and limits |
| --- | --- | --- |
| Ordinary free camera | `game/src/d/d_camera.cpp`: `dCamera_cStickX/Y`, reached by `initPad` and `updatePad` via local `CPad_GET_SUBSTICK_POS_X/Y` macros; cached in `mStickCPosX/YLast` | Existing pinned hook reverses C-stick camera axes. `manualCamera` applies its native curves/limits afterward. Camera mode switching in `nextMode` and subject zoom also use that camera-local cache. Allowed rotation/tilt depends on scene and mode. |
| Other C-stick camera consumers | Same cache in `lockonCamera`, `subjectCamera`, `tornadoCamera`, `hungCamera` | These inherit the same direction preference. Scripted targets, lock-on, collision and contextual restrictions may limit visible changes; no separate hardware acceptance is claimed. |
| First-person look, telescope and Picto Box | `dCamera_c::CalcSubjectAngle`: direct `CPad_GET_STICK_POS_X/Y(mPadId)`; called by `subjectCamera` and the player bridge below | New PS4 hook reverses the local horizontal/vertical aim inputs before saturation, ground/crawl restrictions, limits and smoothing. This bypasses the ordinary C-stick reader. |
| Player item aiming | `game/src/d/actor/d_a_player_main.cpp`: `setBodyAngleToCamera` calls `CalcSubjectAngle` and transfers its pitch/yaw to the player | `procSubjectivity`, bow `procBowSubject`, boomerang `procBoomerangSubject`, hookshot `procHookshotSubject`, grappling-hook `procRopeSubject`, ship bow/boomerang/hookshot procedures and crawl subject look share this bridge. Automatic lock-on branches keep target-directed behavior. |
| Ship cannon aim | `game/src/d/actor/d_a_ship.cpp`: `procCannon`, cached `mStickMVal`/`mStickMAng` from `CPad_GET_STICK_VALUE/ANGLE` in `execute` | New PS4 hook reverses only the local sine/cosine aim increments before applying cannon limits. Sailing, steering, speed, R-lock and automatic targeting retain native behavior. This path bypasses both camera readers above. |
| Cannon minigame aim | `game/src/d/actor/d_a_canon.cpp`: `daCanon_c::PadMove`, direct `g_mDoCPd_cpadInfo[0].mMainStickPosX/Y` | New PS4 hook reverses local aim values before the minigame dead zone, angle limits and smoothing. It does not alter the pad fields. This is another bypass path. |

The player bridge's item callers live in `d_a_player_bow.inc`,
`d_a_player_boomerang.inc`, `d_a_player_hook.inc`, `d_a_player_rope.inc`,
`d_a_player_ship.inc` and `d_a_player_crawl.inc`. The camera's movement/follow
`mStickMainPosX/YLast` cache stays raw; only `CalcSubjectAngle` interprets that
stick with the aiming preference. Walking and native menus read the original
pad state. Representative non-camera consumers also retain it: Wind Waker
baton direction in `m_Do_audio.cpp::mDoAud_getTactDirection`, figure rotation/
zoom in `d_a_obj_figure.cpp`, rope manipulation, and controlled bird flight.
These actions must not acquire camera inversion merely because they use a stick.

## Verification and observation limits

`test_controls.py` drives real controls/storage and the pinned
`native/src/pc/features/pc_controls.cpp` through simulated console services.
It covers all four pending/applied combinations, whole binding/inversion
publication, default initialization despite environment overrides, failure,
uncertainty, Retry/Discard and reloaded preferences. PADStatus checks preserve
both sticks, fixed D-pad and partial/full triggers. Existing restore scenarios
exercise clearing the pending switches along with the bindings.

`test_camera_inversion.py` checks the prepared source routes and compiles the
actual scoped reader expressions for C-stick, subject, ship cannon and minigame
cannon against the pinned inversion API. All four combinations are compared
with explicit baseline values for positive, negative and neutral input. The
polar-reader check substitutes mathematical components; it does not execute
ship dynamics. Preparation verifies the locked source archive and ordered
patch application. A PS4 target compile checks the complete translation units.

These are source-integration and host checks. They do not run native camera
state machines, collision, item mechanics, rendering or physical console input.
Use the #97 section of [Controls-checklist.md](Controls-checklist.md) for
focused owner observations, and [Persistence-checklist.md](Persistence-checklist.md)
for saved preference behavior. Missing contexts remain explicitly unobserved;
full-game camera testing is out of scope.
