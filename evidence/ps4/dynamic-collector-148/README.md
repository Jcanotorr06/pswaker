# Dynamic-effect collector pilot (#148)

Recorded 2026-11-02 for [#148](https://github.com/Jcanotorr06/pswaker/issues/148),
part of #136. The real particle scenario, compatible combined seed, ordinary
complete-package assembly and separate fresh inspection passed. Physical
preparation, appearance and resource/scaling observations for this candidate
remain pending. [pilot.json](pilot.json) records data-free identities; actual
resource/description bytes, builds, captures and packages remain private.
The [runnable workflow and bounded console handoff](../../../docs/ps4/DYNAMIC-COLLECTOR.md)
give prerequisites, actions, cache handling and retrieval steps without story
progression or completed-save acquisition. The parent issue and retained prior
evidence were not changed.

## Executed dynamic path

`common-pot-debris-lifecycle-v1` loads `common.jpc` through the real game DVD
loader, uses `JPAResourceManager`/`JPAEmitterManager` to construct effect `0x0018`
(`ID_AK_JN_TUBOKONAGONA`), advances its particle simulation and draws through
the game's JPA/GX code. This is the sprite-debris component requested by
`daTsubo::Act_c::eff_break_tsubo`, with selected setup from `dPa_control_c::set`
and the game's `dPa_selectTexEcallBack`. The collector uses narrow direct setup;
it does not execute the actor's entire break routine, stage initialization or
companion model-shard effect `0x0017`.

Each run starts with an empty manager and exercises two sequential variations:
texture selection 0 and 1, random seed 0, origin, unit scale and opaque white
colors. The actual emitter creates particles, updates their dynamic state,
draws the callback-selected texture and retires naturally. This is evidence of
effect construction/update/draw/destruction transitions beyond loading or
redrawing an unchanged material. Destruction here means returning the expired
emitter to its normal pool, not invoking a fully booted game's global teardown.
The script fails instead of claiming completion if no particles/draws occur or
the manager has not returned to empty by 180 original particle ticks.

Two final fresh runs (`collection-c` and `collection-d`, build-b) reproduced:

- 22 ticks per variation, 20 peak live particles, 20 draws/lookups each;
  44 ticks and 40 actual particle draws/lookups per run.
- Draw-description mapping at ticks 1–20 for both texture selections. Ticks
  21–22 draw no particles; tick 22 has zero live particles and emitters.
- The same single type-1/version-13/2772-byte description, signed SQLite identity
  `3379288233266289835`, SHA-256
  `0d00768a54622e8322830f81f12c7677f42f488661f56081dc0f2a382b3f9013`.
- Identical complete observation assets, per-tick lifetimes, mappings, combined
  seed bytes and source-manifest bytes.

Texture selection and lifetime alter actual effect state but share a pipeline
configuration here. **One collected, one baseline-covered, zero added, 288
combined.** The original 287 runtime descriptions and the static pilot's one
generated pot description all remain byte-identical. Zero additions are reported
honestly; the purpose is demonstrated dynamic-path collection, not a larger count.
Both preparation calls preserve the baseline database and manifest exactly.
Their adjacent reports retain `dynamic-effect-draw` provenance and per-texture/
tick attribution; the unchanged seed manifest continues to identify its original
runtime/static sources. No generated row is presented as observed PS4 gameplay.

The new executable also reran `always-small-pot-stock-v1` as `collection-static-e`:
three actual draws reproduced the static pilot's full pot description and mapping.
It was already in the selected static baseline, so this regression run also
preserved the exact combined asset. The original #147 report remains unchanged.

## Compatibility and independent runtime comparison

The selected prepared sources are unchanged from #147: SwitchWaker
`ba8d0a31446cd53ceaebd6b7269cca641e73bf4c`, decomp
`b09eebc39852e18397031d9a563a8eae124f21f1`, and the reconciled PS4 Aurora inventory
`e8c95694065f153501f6d4217328d42605fc9cd318f975f437b2ffad63399dab`.
The supported image remains USA `GZLE01`, revision 0. Build-b records source,
adapter, executable, compiler, source-built host dependencies and runtime-library
identities. The production 01.23 program and matching ELF are reused unchanged.

The actual host and PS4 compiler commands produced identical **2,872-byte**
contract sections: schema/config versions, hash width, field offsets and complete
default objects. Both actual runs recomputed all 288 baseline identities using
the selected seeded XXH3 implementation and passed all 288 complete descriptions
through the normal host recorder unchanged. Actual dynamic observations also
matched that recorder byte-for-byte; imported controls are separate from draws.

Independently, a fresh public `pipeline-seed` snapshot of the retained compatible
#112 launch-2 database/WAL reproduced its existing snapshot SHA-256
`431578ed91f8f4831b1dcbf41876cfaa2cad77f931838c0a15742ad03d8bbdef`.
The dynamic identity and **all 2772 description bytes** match that actual PS4
runtime sample. The public coverage comparator also confirms every description
in the final dynamic runs, retained static export and runtime snapshot belongs
to the frozen combined seed. No missing/conflicting record was observed.
This is known-description equivalence, not a newly performed console test.

The host selected Vulkan BGRA8Unorm/Depth32Float, one sample/attachment and
1280x720 (layout key `16288162637680331091`). PS4 uses RGBA8Unorm; compiled
pipeline identity additionally includes its own target layout. The seed stores
full descriptions, not host driver shaders. PS4 creates its own scene/offscreen
layout and required destination-alpha variants through normal preparation.
Witness agreement, host rendering and one known-runtime byte match do not prove
all host states portable, physical preparation for this exact candidate, or
resource viability. Original 30 Hz logic, synchronous creation/recording and
stock quality are unchanged.

Explicit unhandled states are companion model shards, actor lighting/collision,
other pot textures, overlapping effects and other cameras. Other effects,
water/shadows, stage variations and the complete game were not exercised.
The static pot's isolated material description still has no identical known
PS4 runtime sample. Neither that gap nor #138's pending physical/scaling work
is erased by the dynamic description's known-runtime match.

## Frozen private combined package

Normal `assemble --kind game --assembly-assets` built the pilot with the matching
01.23 program and ELF. Its own inspection and a separate fresh `inspect` command
both verified the exact combined database extracted from the package.

| Item | Identity |
| --- | --- |
| Program / cache ID | `01.23` / `6e885683f47a49a119ae` |
| Matching ELF SHA-256 | `400de6f1bb42fb4fc79f9399f290d2f0ee292e58ea03e4f8eea9c2e4dd7c32ab` |
| Combined seed | 288 descriptions, 1,204,224 bytes |
| Seed SHA-256 | `37779b102fff3c8bd71330c77a78efd49ac9881b89bd17c5743bacb4daa281b4` |
| Complete package SHA-256 | `14069c0c7776e330ae9441f81e7537ba95859dfa70bd4b65059d6ec5374b4328` |
| Fresh inspection SHA-256 | `8afea3c9d7e0f290724eb6cc56868b76deb2ad704e1bf0e7f8791e56d99424da` |

Private artifacts are retained under the existing artifact root as
`dynamic-148-build-b`, `dynamic-148-collection-c`/`-d`,
`dynamic-148-collection-static-e`, their corresponding `dynamic-148-seed-*`
results, and `dynamic-148-complete-01.23`. `dynamic-148-pilot` retains commands,
logs, coverage comparison, fresh runtime snapshot, private summary and input
immutability inventory. All **34** tracked source files kept identical hashes
before the final collections and after packaging/reinspection, including the
image, ELF, collector build, runtime database/WAL, original baseline and retained
static inputs. No default assembly asset or prior package was replaced.

A private Windows Downloads handoff named `PSWaker-01.23-dynamic-pilot-148`
contains the package, matching ELF, assembly/inspection, generation and coverage
reports, console instructions, unfilled cold/warm owner templates and hash list.
Fresh inspection of that copied handoff reproduced the same package, seed and
inspection identities. The copy is delivery evidence, not a physical-console run.

Earlier build-a and collection-a/b attempts remain private with their successful
observations; final build-b also reproduces their observation/combined seed bytes.
The final runs bind the final source/build identities and repeat the static
control. The native build and actual collection attempts had no failures.

## Public verification and physical boundary

Synthetic, data-free command tests exercise dynamic selection, exact resource/
build attribution, repeatability and immutable inputs through the external
collector-process boundary. Preparation tests cover per-state attribution,
deduplication, both covered and new descriptions, finite retirement, missing or
invented mappings, malformed input, incompatible records, full-byte identity
conflicts, input preservation and refusal to overwrite earlier outputs.
The real-tool synthetic package test combines static and dynamic exports,
assembles a game package and freshly inspects the exact combined seed bytes.

The dynamic lifetime preparation test first failed because only static metadata
was accepted; the command test first failed because `--scenario` was absent.
The invalid-lifetime/mapping test exposed accepted incomplete particle evidence
before validation was implemented. Those checks pass after their respective
changes. Final focused checks pass **15 collector/preparation tests** and the
real-tool static/dynamic packaging test. Pyright reports zero errors/warnings;
Python compilation, maintained shell syntax and Git whitespace checks pass.
The full reference-enabled WSL suite completed **246 tests, 60 platform/environment
skips, no failures**, in 359.028 seconds, including all ten real initialized-renderer
startup checks. The prepared game source, host renderer and real package tools
were enabled. Native Windows tool/desktop checks were among the environment skips;
this change does not alter the installed program or desktop player workflow.

No new physical-console result is claimed. The handoff requires a cold build
cache, first/repeated pot actions, separate retained-cache relaunch, ordinary
Quit, database/WAL retrieval and independent raw-wait versus full-description
membership checks. It states exact identities, expected owner effort and gaps.
PS4 preparation/appearance and early scaling remain for that bounded handoff
and #138, without requiring a manual story campaign or modifying #136.

## Standards

Independent review of all ten staged files against the pinned `develop` base
`e0231e5d1f05f21625b493a420d283478884aedc` found no documented-standard breaches
or actionable optional code smells. Evidence preserves prior records, contains
data-free identities and clearly leaves physical-console acceptance pending.
The review's temporary full-suite-record note was resolved with the result above.

## Spec

Independent review found no findings against the six acceptance criteria:
actual bounded particle lifecycle, reproducible full-description mappings,
compatible PS4 runtime comparison, preserved combined seed and inspected package,
public synthetic verification and concrete console handoff. It confirmed the
honest baseline-covered/zero-addition result, pending physical observations and
absence of scope creep or unsupported portability claims.

Review totals: Standards 0 findings; Spec 0 findings. No known finding remains
within either axis. The final test/review notes were added after the code review;
no implementation changes were needed.
