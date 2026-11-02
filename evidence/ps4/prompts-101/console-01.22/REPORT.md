# Owner HUD observation and aspect-ratio correction

Owner feedback on 2026-11-01, following delivery of the #101 console candidate:

- Version supplied: **01.22**, title ID `PSWK00001`.
- Build supplied: `db037ec69687332f5760`, source
  `75b6f957f8a88f7a7bba50b27bffaee5017a633c`.
- Supplied complete-package SHA-256:
  `9725596fc5463c53a5b565982ea3fd91aef13c1ad771d48afaa11eca18bb30c8`.

This associates the feedback with the candidate handed to the owner. No returned
console log or installed identity was independently checked. The owner reported
that the buttons appear as expected, with circular prompts slightly squashed in
the top-right actions and correctly proportioned elsewhere. The private image
shows the affected HUD prompts and is not committed because it contains game
content. This is a bounded visual observation, not completion of the full
default/remapped, refresh, relaunch or input-safety checklist.

## Diagnosis

The HUD patch set six control pictures to 32×24 and the Z picture to 40×32,
stretching the shared square 64×64 artwork. The other three control slots were
already square. A private, asset-free geometry replay compiled the actual
`dMeter_ps4Button` helper extracted from patch 0014 and used its real call-site
dimensions with the project's original Circle artwork. Its alpha bounds were
projected through the resulting pane dimensions, checking equal displayed width
and height, centre preservation and agreement with the pane size metadata.

Before correction, seven slots failed: six measured 30×22.5 and Z measured
37.5×30. The three square slots passed. Changing those seven slots to 32×32 made
all ten cases pass, with the affected Circle bounds measuring 30×30 and the same
centre. The later HUD child transforms use one scale factor for these pictures.
The fixed L2/R2 and D-pad slots and action-description dimensions are unchanged.

This replay isolates the geometry defect; it uses a minimal pane stand-in and
does not exercise the real J2DPicture/GX presentation. It remains a private debug
artifact rather than a new public testing seam. Real rendering, labels, spacing
and the alternate/parry animation need the corrected candidate checked on PS4.
The [HUD checklist](../../../../docs/ps4/HUD-prompts-checklist.md) includes the
specific aspect-ratio recheck. No corrected-console pass is claimed here.
