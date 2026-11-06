# Independent review of #153

Fixed point: `f13e343dc6ad03a143fa98a51585b4e8f5e47c7b` (starting `develop`).
Reviewed commit: `69bfff4`; fixes `98f9922` and `13296d2`.
Diff: `git diff f13e343...HEAD`.

Two independent agents reviewed Standards and Spec in parallel at `69bfff4`. A third
independently re-checked the Spec fixes at `98f9922`. None edited the implementation.
Spec reviewers compared each recipe with the pinned game source.

## Spec, at `69bfff4`

The review found real recipe defects, each confirmed against the pinned source
before any change. The seed and package from `69bfff4` were superseded.

- **Jalhalla possession drew the wrong model.** `tori_useHeapInit` builds the body
  model; the recipe drew the lantern. Fixed. The lantern is now its own state,
  following `kantera_draw`.
- **Chuchu freeze omitted invisible packets.** `daCC_Draw` passes a real
  `mDoExt_invisibleModel`; the recipe passed `nullptr`, silently losing descriptions.
  Fixed. The frozen state rose from two descriptions to four.
- **Bokoblin weapon states were mislabelled.** That model is the swing blur drawn by
  `br_draw`, with one shape shown. Fixed as four blur states.
- **Green/pink sharing was overstated.** Those variants also draw a shield and a
  telescope. Fixed. Both props are now exercised.
- **Unnamed paths.** The Chuchu breakup branch is now exercised. The Seahat variant
  and Jalhalla's alpha spheres are now unsupported rows.
- **Scope.** The generic particle scenario accepted the death effects, and 0x0015
  received the stripes callback under any setup. Both are now gated to the enemy
  recipes, with a public test.

The `scripted_collection.py` extraction and equipment rewrite were not requested.
They are retained: the #152 recipes reproduce their retained descriptions exactly.

## Spec re-check, at `98f9922`

All six findings were confirmed fixed, with no test weakened. The re-check found:

- Uncited `br_draw`, `kantera_draw` and `tori_useHeapInit` source references. Fixed.
- Create-time work credited to `VERSION_DEMO`-only `daBk_Create`, and likewise
  `daBtd_Create`. Fixed: retail uses `useHeapInit`.
- "Blur do not run" had become misleading. Fixed: "screen blur".
- The claim that Jalhalla's states shared the default set could not be checked
  publicly. It was wrong. `coverage.json` now names each matching state, and a new
  `default-repeated` state showed the difference is order-dependent. The cause is
  not established; [README.md](README.md) records this as an open limitation.

The final fixes were not independently re-reviewed. They change provenance text, one
repeated state and evidence wording; the seed bytes did not change.

## Standards, at `69bfff4`

No documented-standard breaches found. Seven nonblocking judgement calls:

- **Applied:** repeated family dispatch (`scripted_family`, module `PROVENANCE`),
  duplicated identity checks (`sized_hashes`), the Jalhalla alpha loop, positional
  actor tuples (`ActorRecipe`), and the `EffectStep.texture` name carried from #152
  (now `variant`).
- **Retained, duplicated test scaffolding:** the rejection cascade and row builders
  mirror the equipment tests deliberately, so each slice reads alone.
- **Retained, possible Divergent Change:** `model-collector.cpp` now holds six actor
  recipes as well as the runtime and reports. The earlier recipes follow this shape.
  Moving recipes to their own translation unit suits a separate change.

Process reminder: CONTRIBUTING.md asks for `ready-for-human` once an issue waits on
console testing. That label change is left to the owner.

Standards: 0 hard breaches, 7 judgement calls (5 applied, 2 retained). Spec: 6
findings and 4 re-check findings, all resolved; 1 open evidence limitation.
