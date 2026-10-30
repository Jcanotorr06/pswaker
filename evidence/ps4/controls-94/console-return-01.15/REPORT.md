# Returned applied-controls evidence — version 01.15 (#94)

The owner confirms that profile 03 functioned with its custom mapping after a
full close and relaunch, and that all other supplied profiles used the defaults.
In follow-up, the owner confirms both legends matched the custom layout,
profiles 04–08 displayed fallback warnings, and profiles 01–03 displayed none.
The owner also confirms all fixed-input and recovery checks below passed under
profile 03. These are focused hardware passes for this candidate; they do not
extend the historical #18/#20 acceptance or complete the later #78 slices.

## Candidate and original files

All nine unique log captures identify build `6d2368a5373b00387dc9`. Each embedded
complete-package manifest matches the locally inspected candidate manifest:
version `01.15`, title `PSWK00001`, content ID
`IV0000-PSWK00001_00-PSWAKERGAME00000`. The expected package SHA-256 is
`07e8e26eef394b745cfe3d8819d22dad2cc3ffa2b62726761e57ba5ec4e194f0`.
[candidate.json](candidate.json) records the matching source commit and ELF/SELF
hashes. Manifest agreement associates the captures with the candidate; it is not
a new console-side hash of the running executable or installed package.

The owner returned folders 1–8 in the private validation kit. Original logs and
settings remain unchanged outside git. [original-files.json](original-files.json)
records sizes, SHA-256 values and line counts for all 28 returned files.
Repeated previous logs are deduplicated by hash in [summary.json](summary.json).
[selected-records.txt](selected-records.txt) retains only relevant control,
storage and identity lines, with their original relative paths and line numbers.
No game data, saves, raw log archive or personal paths are published here.

## Owner observations and log corroboration

| Profile | Owner-observed mapping and feedback | Returned-file corroboration |
| --- | --- | --- |
| 01, controls absent | Defaults; no warning | No controls warning in the log; settings file not returned |
| 02, complete defaults | Defaults; no warning | No controls warning in the log; settings file not returned |
| 03, custom layout | Custom mapping; both legends match; no warning; persists after close/relaunch | L3 → A, R3 → B and Circle → Start appear in sampled input; another custom-mapping capture appears in `4/platform.prev.log` |
| 04, incomplete | Defaults; warning | Expected incomplete-controls reason; extracted settings match fixture byte for byte |
| 05, duplicate target | Defaults; warning | Expected shared-button reason; extracted settings match fixture byte for byte |
| 06, reserved target | Defaults; warning | Expected unsupported/reserved reason; extracted settings match fixture byte for byte |
| 07, unsupported version | Defaults; warning | Expected unsupported-version reason; extracted settings match fixture byte for byte |
| 08, malformed | Defaults; warning | Expected malformed-controls reason; extracted settings match fixture byte for byte |

All 801 gameplay samples across nine unique captures agree with the expected
custom/default button layout, fixed D-pad and trigger terminal-click bits.
Every one of the 235 paused/releasing/disconnected samples is neutral for
game-facing buttons, sticks and analog triggers. Short presses can fall between
the one-second samples: custom X/Y/Z presses are not captured, and the physical
action verdict comes from the owner's observations, not from inferred samples.

The custom-layout capture `3/platform.log` records settings/legend navigation,
input loss, explicit confirmation and release-gated return, then the delayed
failed-read check: scheduling at line 872, injected failure at 883, input loss at
885, explicit confirmation at 891 and return to gameplay at 893. The trace
corroborates recovery transitions; the owner separately confirms visible pause,
physical disconnect, deliberate resume and absence of held-input leakage.

[owner-observations.json](owner-observations.json) retains the original statement
and both follow-up questions/answers. Owner-confirmed passes under profile 03:

- Fixed movement/right stick/D-pad and distinct partial/full L2/R2 actions.
- Touchpad settings, fixed Cross/Circle navigation and both matching legends.
- Physical disconnect and the five-second failed-read check, with deliberate
  resume and no held inputs leaking into gameplay.

## Limits and remaining broader checks

The five extracted settings files independently corroborate non-rewriting for
profiles 04–08. No extracted settings were returned for profiles 01–03; their
file-byte preservation is covered by host tests, not this console return.
Per-action item/scene details were not supplied. The compiled platform string
names the expected Slim/9.00/GoldHEN environment; it does not detect it anew.

Text-size-change persistence, a separately versioned package update, cache-only
clearing, controlled unreadable/unwritable storage, and normal orderly Quit were
not reported as tested in this return. No passes are inferred for those checks.
Camera/aiming inversion, the controls editor and in-game PS4 prompts remain later
work; the saved inversion flags in this slice do not establish camera behavior.
