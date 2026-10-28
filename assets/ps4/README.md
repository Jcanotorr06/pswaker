# PS4 game artwork

These prepared PNGs are included so anyone can build the game program from a
checkout. They are separate from the in-game title screen and HUD and from the
Windows executable's [waker.ico](../../tools/pswaker/waker.ico), which is already
tracked and covered by the same redistribution decision.

| File | Role | Dimensions | SHA-256 |
| --- | --- | --- | --- |
| [icon0.png](icon0.png) | Game icon / `ICON0_PNG` | 512 x 512 | `d3e22130a3c119d1f75daf19de2636cf9162e65575eba6a6ca20a590cb1db03e` |
| [splash_art.png](splash_art.png) | Launch splash / `PIC1_PNG` | 1920 x 1080 | `35fe1f42fab83f27841e9049c650662b5d8cbe505edc94eab8fbb3f1ae8a99b4` |

Both are non-interlaced, opaque 8-bit RGB PNGs, without alpha or `tRNS`
transparency. They are included byte-for-byte as supplied by the project owner;
no conversion or editing was performed for inclusion.

## Redistribution authorization

On 2026-10-28, Joseph Cano confirmed in the release-preparation conversation
that the provided artwork can be redistributed without restriction and requested
including it in the repository for other builders. The
[recorded decision](../../docs/RELEASING.md#artwork-redistribution-blocker)
identifies the evidence, reviewer, date, exact hashes and permitted scope. It
covers repository distribution as well as program releases, desktop bundles,
portable archives and installers. No additional license or authorship is
inferred from that authorization.

The authorization applies to these exact files. Replacements or modifications
need a separate decision. Private provenance records and build outputs remain
outside git.

See [BUILDING.md](../../BUILDING.md#2-build-the-game-program) for the build
command using these files and the [artwork guide](../../docs/ps4/OWNER-ARTWORK.md)
for validation, restaging and replacement artwork.
