# Title and start instructions (#104)

The title uses applied controls from startup, including saved custom controls and
complete-default recovery. This extends the stock-mode replacement from #103;
it does not expand first-playable acceptance or complete full-game coverage.

## Maintained presentation paths

The audit used the pinned sources in `game.lock.json`, the ordered game patches,
and read-only, in-memory inspection of the owner's USA GZLE01 revision 0 image
through `disc_image.py`. Only identifiers and structural metadata are retained.
No extracted game text, pixels, converted outputs or pack assets are committed.

| Path | Finding and treatment |
| --- | --- |
| `daTitle_proc_c::proc_init2D` / `title_logo_e.blo[pres]` | One picture at (181, 336), 280×40; the standalone `timg/press_start.bti` is the identified controller instruction. Resolve A, B and Start from one applied snapshot. |
| `daTitle_proc_c::proc_execute` / `daTitle_c::execute` | Both accept A, B or Start. Preserve all three alternatives, including the press that skips the introduction. Input predicates are unchanged. |
| `daTitle_proc_c::calc_2d_alpha` / `proc_draw` | Keep introduction visibility, alpha and pulse. Check replacement readiness before drawing the retained picture. |
| `subtitle_start_anim_e.bdl::MAT3[subtitle]` | Audited subtitle artwork; `TEX1[logo_sub]`, `TEX1[logo_sub_e]` and `TEX1[zel_grad_128x8_i8]` contain no controller instruction. Preserve model, material and BTK animation. |
| `subtitle_kirari_e.bdl::MAT3[subtitle]` | Audited subtitle/glint artwork; `TEX1[logo_sub]`, `TEX1[logo_sub_e]` and `TEX1[zel_smalgrad_128x8_e_i8]` contain no controller instruction. Preserve material and looping BTK animation. |
| `title_ship.bdl::MAT3[ship_m_fn_eye,ship_m_fn_main_hashi,ship_m_fn_neck]` | Audited ship artwork; `TEX1[fn_head1,fn_main1,new_fn_eye]` contains no controller instruction. Preserve model, BCK and BPK animation. |
| `title_logo_e.blo[BACK,ROOT,nint,zelj,zeld,eft1,eft2]` | Background, logo, copyright and effect anchors; preserve surrounding artwork. |

The three models are loaded by `proc_init3D` and drawn by `model_draw`; they are
not message pictures or HUD controls. There are no identified directional,
animated-stick or trigger-travel instructions in these audited title paths.
Their visual animations are artwork, not directions to the player. Other
revisions, languages and unreviewed model/material instruction paths remain
explicitly unresolved in the asset-free coverage inventory.

## Binding, fallback and retained lifetime

Game patch `0018-title-start-prompts.patch` checks the actual `pres` pane is a
single-texture J2DPicture backed by the audited RGB5A3 280×40 BTI, including its
pixel offset. It registers only that texture through the #103 stock-mode Aurora
replacement mechanism. Prompt-over-pack precedence remains the exported #103
rule. CMake already links `embedded-prompts.cpp` and `embedded-textures.cpp`;
the source-preparation tool applies the new ordered patch to the PS4 build.

`pswaker_title_instruction` uses the semantic resolver in native-game-menu
context, preserving the accepted A/B/Start alternatives as `PRESS` plus accurate
PS4 names. It deliberately uses the project-owned text fallback, independent of
icon availability. The original 5×7 glyphs, slash and outline in `prompt-art.cpp`
use the recorded [GPLv3 licence and provenance](PS4-PROMPTS.md#prompt-artwork-licence-and-provenance).
The existing 560×80 runtime image fits the original slot, including the longest
three distinct names (Triangle, Options and Square). This is an instruction in
the title slot, not the port legend; hardware readability still needs checking.

Startup publishes controls after successful settings loading and before the title
is created. The registered refresh adapter records applied generations and
rebuilds the retained texture before the shared neutral-release gate resumes.
Pending edits, discard, failed Apply and discarded defaults keep the published
snapshot. Successful Apply and applied defaults publish a new generation.

If registration fails after startup refresh, readiness suppresses the title pane
and retries on drawing; the stock controller artwork is never used as fallback.
A failed registration during refresh still returns failure to the resume gate.
Repeated failures report once per retained source/applied generation. An invalid
semantic request yields transparent artwork and an unresolved coverage report.
Missing or changed layout/texture paths report `surface=title-layout item=pres`
(the item is logged in hexadecimal), suppress the suspect instruction, and keep
play usable. An absent `pres` pane skips its alpha dereference. Unregister the
replacement before the title releases its archive/heap; a later title registers
its own resource again.

The hosted controls scenarios cover startup default recovery and a saved layout
with Start on Circle, alongside the existing retained Apply/discard/failure and
disconnect gate scenarios. The synthetic title check covers late registration
failure/retry, owner lifetime, unresolved suppression and longest-label fit.
Real J2D layout and J3D model/material presentation require the
[stock-mode hardware checklist](Title-prompts-checklist.md). Host compilation
does not establish physical observations or full-game coverage.
