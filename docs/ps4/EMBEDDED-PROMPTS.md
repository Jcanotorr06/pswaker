# Embedded controller instructions (#103)

This post-first-playable slice replaces the stock title instruction at runtime.
It does not complete #79, expand #12/#18, load an HD pack or claim a stock/HD
transition. Other unreviewed embedded images and shared atlases remain unresolved
in [the coverage inventory](../../platform/ps4/prompt-coverage.json).

## Local source and resource audit

The audit used the pinned SwitchWaker/decomp sources in `game.lock.json`, the
maintained Aurora source and ordered patches, and the owner's local USA GZLE01
revision 0 image. The existing read-only `disc_image.py` handling reads the FST,
expands Yaz0 and resolves RARC members in memory. Inspection decoded selected
RGB5A3 images locally; no extracted bytes, text, images, derived game artwork or
pack content enter git. This record retains only identifiers and structural
metadata. It is a representative audit, not a full-game census.

| Resource identifier | Metadata and coverage decision |
| --- | --- |
| `res/Object/TlogoE.arc::timg/press_start.bti` | RGB5A3, 280×40, standalone whole instruction; replaced with accurate project text, `text-fallback` |
| `TlogoE.arc::title_logo_e.blo[pres]` | Retains the existing slot, alpha, pulse, visibility and layout |
| `TlogoE.arc::bdlm/subtitle_start_anim_e.bdl::TEX1[logo_sub]` | RGB5A3, 256×128; logo artwork, preserved |
| `TlogoE.arc::bdlm/subtitle_start_anim_e.bdl::TEX1[logo_sub_e]` | RGB5A3, 256×64; logo artwork, preserved |
| `TlogoE.arc::bdlm/subtitle_start_anim_e.bdl::TEX1[zel_grad_128x8_i8]` | I8, 128×8; shared gradient, preserved |

`daTitle_proc_c::proc_execute` and `daTitle_c::execute` accept A, B or Start.
`pswaker_title_instruction` resolves each alternative from the same applied
snapshot in native-game-menu context. The replacement says `PRESS` followed by
the three accurate PS4 names, separated by slashes. It never guesses a binding
or advertises a hold, analog travel or movement. Unreviewed resources with those
distinctions remain unresolved; no whole-atlas replacement is attempted.

## Runtime artwork and refresh

Game patch `0017-embedded-title-prompts.patch` identifies the stock BTI pixel
pointer after the layout loads and unregisters it before the title proc releases
its heaps. `embedded-prompts.cpp` owns the project pixels. `embedded-textures.cpp`
registers them as a synchronous raw RGBA8 replacement through Aurora, with no
filesystem, pack loader or GPU work in the title hook. The source pixel pointer
remains unchanged, so the existing J2D/GX path resolves the replacement normally.

Artwork is original project source under GPLv3. The instruction reuses the
hand-defined 5×7 letters in `prompt-art.cpp`, adding an original slash and a dark
outline. A 560×80 transparent image is displayed in the 280×40 stock slot.
Names are used deliberately as the accurate text fallback, including Options,
Triangle, L3 and R3. Licence/provenance are the same as the owner-approved
[prompt artwork](PS4-PROMPTS.md#prompt-artwork-licence-and-provenance).

The adapter registers at the shared prompt refresh boundary. On a new applied
generation it builds new pixels, unregisters the old raw registration before
changing borrowed memory, and registers the new image before returning success.
Aurora clears retained GX objects and invalidates bindings on these mutations;
the render thread consumes those invalidations before using retained bindings.
The neutral-release gate cannot resume on a failed refresh. Pending edits,
discard and failed Apply do not publish a generation. Startup publishes the
saved/default configuration before the title is created. An unresolved semantic
request registers transparent artwork and reports `embedded-title`, keeping play
usable without displaying an incorrect controller. A failed GPU upload must also
suppress the original controller image.

## Public precedence rule for #80

[replacement-policy.hpp](../../platform/ps4/game/replacement-policy.hpp) exports
`promptPriority`, `packMaximumPriority`, matching-key families and `select`.
Only the project prompt layer may register at `promptPriority` (`INT32_MAX`).
All pack registrations must use a priority at or below `packMaximumPriority`.

Game-platform patch `0008-prompt-replacement-precedence.patch` applies this rule
inside Aurora before consulting the winning replacement's cache:

1. Enumerate the matching pointer, exact source hash, palette wildcard and
   texture wildcard registrations.
2. Prompt ownership wins across all matching families, in either registration
   order. An ordinary pointer registration cannot hide a prompt source hash;
   an exact pack hash cannot hide a prompt wildcard.
3. Within the same ownership class retain existing family specificity (pointer,
   exact source, palette wildcard, texture wildcard), then higher priority and
   latest registration within that key.
4. Cache entries are usable only for the selected registration ID. Registration,
   removal and prompt rebuild must invalidate retained GX objects/bindings.
   A future loader must remove only its own registrations, never clear the
   shared registry or unregister an entire prompt-owned key.

Stock mode still uses `stock-textures.cpp`; there is no HD-loader dependency.
Synthetic pack competitors in hosted checks are not pack-loading support.

## Validation limits

`test_prompts.py` compiles the public rule and title adapter with synthetic data.
It checks all family pairs, registration order, all accepted title alternatives
and a retained applied-generation rebuild. The optional hosted
`replacement-precedence-check` target runs the actual patched Aurora registry
and GX caches, replacing only GPU allocation with CPU handles. Set
`PSWAKER_REPLACEMENT_CHECK` to that binary when running the Python suite.

Physical stock-mode readability, surrounding art, pulse, retained refresh,
relaunch and disconnect observations remain pending. Use
[the console checklist](Embedded-prompts-checklist.md) and retain observations
for the exact installed build; compilation cannot establish those results.

The follow-up [title/start slice (#104)](TITLE-PROMPTS.md) verifies the actual
layout binding, suppresses registration failures, audits all title model/material
paths and prepares a dedicated startup/refresh hardware checklist.
