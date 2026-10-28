# Owner artwork in the game program package

The game icon is `ICON0_PNG` / `sce_sys/icon0.png`, exactly 512 x 512.
The launch splash is `PIC1_PNG` / `sce_sys/pic1.png`, exactly 1920 x 1080.
Both must fully decode as non-interlaced, 24-bit opaque RGB PNGs (8 bits per
channel), without alpha or `tRNS` transparency. The shared program payload
validator uses the pinned `python3-png` host package. Staging copies the supplied
bytes unchanged.

## Local artwork and provenance

Keep the prepared images in a private local directory outside the checkout,
for example `$HOME/pswaker-private/local-artwork` on Linux/WSL2 or
`C:\private\pswaker-private\local-artwork` on Windows. Artwork selection, creation
and conversion are the owner's responsibility; these tools only validate and
copy the prepared PNGs. These resources are separate from the in-game title
screen and HUD, and from the Windows executable's icon.

Before staging, create a private `provenance.md` alongside the images. For each
image, record:

- Role, filename and SHA-256 of the exact prepared PNG supplied to staging.
- Origin: creator or rights holder if known, source URL or local source
  description, and the date obtained. Mark unknown facts as unknown.
- Preparation: any extraction, editing, cropping or conversion, who performed
  it, and how the prepared PNG relates to the source.
- Rights evidence: license text or permission and its source, retained locally;
  record absent or unresolved permission explicitly.
- Intended local use and current redistribution status. Keep this pending until
  a separate provenance decision identifies the exact artwork hashes, evidence,
  reviewer, date and permitted redistribution scope.

For example, compute the prepared files' hashes with `sha256sum` on Linux or
`Get-FileHash -Algorithm SHA256` on Windows. After staging, associate this record
with the hashes and package identity in `game-program-artifacts.json` described
below. Update the record when an image changes. The tools record technical
identity; they do not collect or approve origin or rights evidence.

Local use, possession of a disc or successful validation does not grant
permission to commit or redistribute artwork. Do not commit or attach the images,
their local provenance record, raw packaging evidence or artwork-bearing outputs
to issues, pull requests or logs. Keep build roots, stages, staging history,
program releases, complete packages, desktop bundles, archives and installers
outside git. The repository ignores directories named `local-artwork/` and
`pswaker-private/` as a safeguard if private files are accidentally placed inside
the checkout; retain those directory names and never force-add their contents.
Check `git status --short` and `git diff --cached --stat` before committing.

Program releases and desktop bundles carry the images even though they contain
no disc image. Publishing them, including a Windows desktop installer or portable
zip, distributes the artwork. They must remain private until the separate
[provenance decision permits redistribution](../RELEASING.md#artwork-redistribution-blocker).

## Build, restage and inspect

Supply both paths to the maintained build command:

```bash
ARTWORK_ROOT="$HOME/pswaker-private/local-artwork"
bash tools/pswaker/build-game.sh "$GAME_ROOT" "$PLATFORM_ROOT" 01.13 \
  "$ARTWORK_ROOT/icon0.png" "$ARTWORK_ROOT/splash.png"
```

To change artwork on an otherwise matching compiled build:

```bash
python3 tools/pswaker/game-build.py stage "$GAME_ROOT" "$PLATFORM_ROOT" \
  --app-version 01.14 --icon "$ARTWORK_ROOT/icon0.png" \
  --splash "$ARTWORK_ROOT/splash.png"
python3 tools/pswaker/inspect-game-program.py "$GAME_ROOT" "$PLATFORM_ROOT"
```

Every attempt validates both inputs before writing a new program stage. There
are no default paths or inherited artwork. The previous stage, program package
and success records move to `evidence/game-staging-history/`. Validation or
packaging failure leaves no current stage or package. The failure remains in
`evidence/game-staging-attempt.json`; previous completed outputs remain in
history. A failed inspection removes the previous inspection result.

Successful staging publishes `build/program-stage/` and `out/program/`.
`build-info.json` records each resource's hash, dimensions and encoding without
source paths. Private `evidence/game-program-artifacts.json` also records the
source paths, full stage inventory, package hash, version, title/content IDs,
compiled build ID, ELF/SELF hashes, build-input inventory hash and cache path.
Keep this local evidence private. Commit neither artwork nor artwork-bearing
outputs.

Inspection checks the package hash before extraction, then freshly extracts the
PFS payload and the `PARAM_SFO`, `ICON0_PNG` and `PIC1_PNG` entries. It compares
the stage inventory and compiled identity, re-decodes the extracted artwork,
and compares it against the packaged manifest and local staging evidence.
`evidence/game-program-inspection.json` records the result. The NONPLAYABLE
diagnostic's inspection command and resources are unchanged.

Artwork paths and bytes are staging inputs; they are absent from the compile
inventory. Changing artwork alone leaves the compiled build ID and cache path
unchanged. Changes to maintained tooling are included in that inventory and
therefore require a new compiled identity; retain the actual values from the
new build's evidence. The application identity remains `PSWK00001` /
`IV0000-PSWK00001_00-PSWAKERGAME00000`.

## Confirmed splash handoff

The maintained preparation selects Aurora at
`mshivam019/dusklight-ps5@e281999cdb4fee6127525a9a9e97979480db4bf3`, applies
the PS4 prerequisite and the renderer/game-platform patches, and selects
`BgbrhrWatchinOVO/dusklight-ps4@fd483cf5d4f04b0f4d887ff412d0e8691925de08`
for the native PS4 layer. See `sources.lock.json`, `renderer.lock.json`,
`prepare-sources.py` and `prepare-game.py`.

Confirmed in the resulting game-local maintained source:

- `src/aurora/lib/aurora.cpp:397-408`: inside `canPresent && g_surface`,
  `g_surface.Present()` supplies the status; only `if (status)` calls
  `ps4_hide_splash()` on PS4.
- `src/platform/native/platform.c:80-90`: the shell's `sce_sys/pic1.png`
  remains during loading; `ps4_hide_splash()` uses a once-only atomic guard
  and calls `sceSystemServiceHideSplashScreen()`.
- `src/platform/native/platform.h:23-25` documents the first-present handoff.

There is no added display delay or startup change. Source inspection confirms
the handoff; visible artwork and timing still require owner console evidence.
