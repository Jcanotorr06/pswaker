# Environment/scene collection (#154)

This independent slice of [#154](https://github.com/Jcanotorr06/pswaker/issues/154)
uses the corrected #149 pilot baseline. The [workflow](../../../docs/ps4/SCENE-COLLECTOR.md)
describes the real paths, replay commands, compatibility limits and targeted physical
handoff. Actual game resources, description bytes, seeds, packages and captures
remain private. These observations are generated host evidence.

## Fixed boundary

[manifest-plan.json](manifest-plan.json) fixes three recipes and nine unsupported
families. [manifest.json](manifest.json) binds the exact image, both resource archives,
collector/build and target representation. The plan records numeric camera, world,
fog, grid, shadow-plane, alpha and overlap parameters, not open-ended state ranges.
Fifteen frames run the game's actual ocean, simple-shadow and alpha packet draw code.
The ocean grid is flat; stage/player/weather and wave controllers do not execute.
Supplied planes replace collision queries. No production startup or owner storage
path is entered.

Scene recipes initialize the game's validated DOL/REL-backed constants before
drawing. Two earlier native attempts failed with zero sphere draws because those
arrays were still stubs; they remain retained privately as failed evidence. The final
collector runs `pc::loadAssets`, which validates the pinned disc inputs and fills 163
constant arrays. No fabricated configuration bytes or asset-only counts are used.

## Generated result and equivalence limits

The three-recipe union contains **11 observed descriptions**, including **nine
additions** to the 301-description pilot, for **310 combined descriptions**. Every
baseline record, frame metadata value and source-provenance entry survives unchanged.
This candidate does not incorporate the independent #150–#153 expansions.

[coverage.json](coverage.json) records the fixed rows, description/source mapping,
per-state counts, observed layout keys, both preparation contracts and matching-state
sets. Numeric register, camera, scroll and plane changes only establish pipeline
equivalence where complete descriptions agree. Equal configurations do not imply
identical appearance or coverage of an unexercised scene/controller.

Ocean exercise observes four descriptions across six frames/twelve draws: two
new descriptions for day/night, dense fog, raised camera and repeated
day, and two pilot-covered descriptions for range adjustment. Changing numeric fog distances,
colors and view values does not change the observed set in those selected states.
Shadow exercise observes five new descriptions across four frames/nineteen draws:
the untextured four-pass set gains one texture-seal description; slope, caster height,
rotation, elongation and the raised view preserve the textured set.

Alpha/overlap exercise observes nine new descriptions across five frames/twelve
draws. Sphere, cube, faded sphere and repeated sphere share one description. The
overlap has eight: five shared with the textured shadow recipe, two shared with
the ocean recipe and one alpha description absent from isolated sphere drawing.
The cause of that alpha difference is not established; it is retained as a bounded
order/state observation, not evidence of a reached gameplay effect combination.

The selected overlap exercises ocean, textured simple shadow and faded alpha sphere
in one renderer frame. It does not prove real gameplay ordering equivalence or all
overlapping effects. Inherited GX state can affect a later packet, so its results
are attributed to the overlap rather than silently transferred to isolated effects.
Repeated control states retain any first-use/order-dependent descriptions.

The host scene/offscreen preparation roles have the same stock key
`16288162637680331091`: BGRA8, Depth24Plus, one color, one sample, 1280×720. Both
roles are retained explicitly; no offscreen image capture is claimed by these recipes.
PS4 uses its RGBA target and normal applicable creation variants. The 2,872-byte
host/PS4 complete representation witnesses match, SHA-256
`8c3392d2bf28dae71adecc908ed8056d987a6b2db36bb27ddcf07cc138825700`.
Every process additionally recomputes known-runtime identities and compares complete
baseline and observed descriptions with the ordinary synchronous recorder. This
supports portability of descriptions, not portability of host driver objects.

## Repeat, package and private retention

[repeat.json](repeat.json) records complete standalone seed/provenance and frozen
manifest equality across two fresh runs. Every scenario's script, state mapping,
counts, layouts, resource/collector identities and complete observed assets agree.
Every generated full description belongs to the combined seed.

One source-reference correction replaces the nonexistent logo `create` symbol with
the actual `dScnLogo_Delete` setup site. Both corrected manifests were freshly frozen
and the unchanged retained collections independently revalidated. Their complete seed
and source-manifest bytes still equal both original runs. Original manifests, plan,
reports and candidate remain private immutable records; the candidate records this
metadata-only correction and the unchanged package identity explicitly.

The changed collector reproduces the two complete retained arrow descriptions
from #152 and the two boss-water descriptions from #153. All three scene recipes
also rerun against the frozen 310-description seed: preparation and cleanup complete
before drawing, their observed description sets match the pilot-based runs, and
every full observed description belongs to that seed. This is host preparation
evidence; no PS4 preparation/resource observation is inferred.

[candidate.json](candidate.json) identifies the unchanged verified **01.24** program,
build `35a453336a0e4b0d432c`, matching ELF, exact seed, assembly and fresh inspection:

- Seed SHA-256: `fb0b83f4fc876ad572de7146b3d1b61b015051fde8f8c7777c96c06d72dbb9e6`.
- Complete package SHA-256: `7b7c90c42c1947085f43b90f3f1976b9ecfdcac78d2467ab23293c713cf6b3ed`.
- Fresh inspection SHA-256: `a87c75f35c26ecf0d765355e6fd4760d187c8e457b6fb4dea76eb7c15f9b8552`.

Ordinary complete-package assembly inspects the output. Independent subsequent
inspection freshly extracts it, reproduces the assembly inspection and checks the
full pinned payload, exact seed bytes and complete source manifest. Image, baseline,
collector/build, frozen plan/manifest, prepared assets and program/ELF identities
remain preserved. Default assembly assets are not replaced.

Private artifact group `scene-154` retains collectors `a`/`b` and failed batches
`a`/`c`; final `collector-c`, successful `batch-e`/`batch-f`, both frozen manifests,
corrected `manifest-g`/`manifest-h` and `prepared-g`/`prepared-h`, `controls`,
`candidate-controls`, `complete-01.24`, input preservation, full reports,
commands and logs. The retained build, run, verification and package scripts reproduce
the actual procedure; the public workflow uses the maintained CLI directly.

## Residual gaps and physical handoff

All three exercised rows are generated, and none are physically verified. The nine
unsupported rows name wave/storm controllers, real shadow receivers/capture,
rectangular shadow textures, mirrors/reflections, weather packets, sky/underwater
stages, waterfall/dungeon water, other alpha accumulators and other world/camera/
overlap combinations. Their reasons, source references and follow-up ownership are
part of the manifest. They remain automation gaps, without inferred owner acceptance.

Physical PS4 preparation/cleanup, effect appearance, raw missing-pipeline waits,
startup/resource scaling, normal Quit and save/settings observations remain pending
for this changed seed. The workflow selects first/repeated shoreline water and
simple shadows under camera movement, the ordinary Outset regression route, and a
separate compatible warm comparison. No story progression or full-game simulation
is required. Inaccessible alpha/weather/capture states remain explicit physical gaps.
Known missing descriptions or observed missing-pipeline creation/waits require a fix;
earlier physical acceptance does not transfer to these changed seed bytes.
