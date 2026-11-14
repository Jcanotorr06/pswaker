# Written PS4 control instructions (#105)

The four reviewed USA written Start instructions now name the physical control
from applied controls. The surrounding instruction remains the game's own text;
button pictures beside it keep using the shared message adapter. This is a
post-first-playable #79 slice and does not expand #12/#18 acceptance.

## Local resource inspection

Read-only inspection used the owner's USA GZLE01 revision 0 image, bounded
`disc_image.py` reads, Yaz0 expansion and RARC member lookup. The BMG walk
validated block extents, INF1 entry sizes and DAT1 offsets, and advanced over
control tags by their declared lengths, including embedded zero bytes. It
inspected all 4,411 entries of `res/Msg/bmgres.arc::zel_00.bmg` and all 15 of
`res/Msg/bmgresh.arc::zel_01.bmg`. The latter has no control instructions.
Extracted text and binary inspection outputs stay private and ignored by git.

The review searched written control names, Start aliases, stick/trigger/D-pad
terms, press/hold wording and all message control tags. Broad keyword matches
were reviewed in context: ordinary uses of words such as stick or hold are not
control requests. No literal stick-direction, stick-click or partial/full-trigger
name was identified in these two resources; existing directional pictures,
gestures and analog instructions retain their established semantics.

Only identifiers and statuses enter [the inventory](../../platform/ps4/prompt-coverage.json):

- Message IDs 816, 817, 1108 and 3008 contain written Start instructions and use
  accurate PS4 text fallback. These are native game instructions, not port controls.
- IDs 18, 23, 37, 49, 54, 60 and 96 describe GameCube system operations. IDs 134
  and 612 describe an external peripheral connection without an approved PS4
  equivalent. These nine entries remain **unresolved**. Their unsupported
  instructions are replaced by a short, project-authored unavailable notice,
  and logged once per ID as `PROMPT unresolved surface=written-message`.
  In particular, system A is never mistaken for remappable gameplay A.
- 297 messages contain related control-picture/directional tags. Three also
  contain a written name; two are unsupported peripheral instructions. The
  remaining 292 retain the converted message-picture path. The 305 distinct
  message entries therefore comprise 292 converted, four text fallback and nine
  unresolved. A converted status records implementation, not a hardware pass.

Other languages/revisions, resource families not inspected here, actual layout
readability and the nine unresolved entries prevent a full-coverage claim.
The broader `resource.BMG.literal-control-names` entry stays unresolved.

## Semantic translation and display

`written-instructions.cpp` matches reviewed message IDs and whole control-name
tokens, not arbitrary words globally. The USA-only `getMessage` hooks in game
patch `0019-written-instructions.patch` pass bounded DAT1 content. Unknown IDs
are unchanged. The converter preserves every other byte, including colours,
press/hold wording, alternatives, direction pictures, page breaks and trigger
tags. Missing, duplicate or malformed spans receive a coverage report and a
neutral unavailable instruction; no GameCube binding is guessed.

The converter produces a private six-byte BMG tag for the semantic Start action.
The converted buffer lives through shutdown, uses host allocation rather than
the current game heap, and never changes after a parser receives its address.
Message parsing emits `ESC PS[action]` into the normal retained text and shadow
buffers. It reserves an atomic 4.5-font-cell span in measurement and output;
there is no dependency on PS4 icon artwork. `J2DPrint::parse` measures and draws
the same span, preserving the native font, colour, alpha, baseline, alignment
and shadows. Long names scale horizontally only when their measured advance
exceeds the slot. Options and L3/R3 remain full accurate names. The real font
and the resulting readability still require the console checklist.

The name table resolves all six actions through `resolve_ps4_prompt` from one
applied snapshot. `main.cpp` seeds it after startup controls loading and registers
it at the existing refresh boundary. Successful Apply rebuilds this display
table together with retained message pictures before the resume gate releases
gameplay. Retained strings contain semantic references, so an already-open or
partially typed dialog draws the new names without restarting typing or moving
adjacent pictures. There is no retained expanded old name to invalidate.
Pending edits, discard, failed Apply and discarded defaults leave the applied
table unchanged. Invalid bindings report coverage and show `?`, never a guess.

The maintained CMake target compiles the adapter; ordered source preparation
applies patch 0019 after the message, HUD, native menu and title patches. No
input predicates, storage behavior, recovery gates or prompt toggle change.

## Validation

The approved seams are the semantic resolver, installed-controls harness and
synthetic written-translation boundary. `test_prompts.py` exercises contextual
replacement, embedded-zero tags, malformed/duplicate/missing spans, lifetime,
explicit defects, all 54 action/target names and retained semantic text after
refresh. `test_controls.py` keeps written names beside live message/HUD/menu
pictures through Apply, pending/discard/failure and disconnect during refresh.
Resolver checks retain press/hold, accepted alternatives, fixed movement and
direction, click distinction and partial/full trigger semantics.

Run these on Linux/WSL with Clang 21 and prepared sources:

```sh
python3 -m unittest discover -s tests/ps4 -p test_prompts.py -v
PSWAKER_GAME_ROOT=/private/prepared-game python3 -m unittest discover -s tests/ps4 -p test_controls.py -v
```

Host checks and PS4 compilation do not prove actual dialog rendering or fit.
Use [the console checklist](Written-instructions-checklist.md) and add an
observation record for the exact installed build. Keep game-bearing output private.
