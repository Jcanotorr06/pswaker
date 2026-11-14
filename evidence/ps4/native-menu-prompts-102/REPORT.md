# Native menu prompts #102: implementation verification

Source baseline: `develop` at `a20687e5358c28e69c5bdc9db474e43ed2395c25`.
The exact changed compile/test inputs and output hashes are recorded in
[validation.json](validation.json). No game assets or converted asset outputs
are retained here.

## Host and target checks

- Red/green check at the existing installed-controls seam: keeping a native
  menu picture open failed with an unpublished menu snapshot before the adapter
  joined refresh, then passed with registration. The successful run checks
  applied A/B/Start labels, fixed port controls, pending edits, discard, failed
  and uncertain saves, delayed refresh, reconnect and neutral release.
- The resolver suite passes all six actions across nine targets in native-menu
  context, as well as fixed controls, variants, text fallback and unresolved
  requests. The full installed-controls file passes its 30 tests.
- Compileall, shell syntax, Pyright and the full hosted suite pass; counts and
  skips are in `validation.json`. Platform-dependent skipped checks are not
  console evidence.
- Fresh pinned game archives and the entire ordered game/platform patch series
  were prepared and reverified without disc data. The maintained
  `switchwaker_eboot` target compiles and links, and `check-oelf` reports valid
  segments after the final conducting-state correction.

The build uses the explicit identity `unverified-102-compile`. It is a compile
check, not a staged or packaged hardware candidate or a verified program release.
No console observations or package acceptance are inferred from its hashes.

## Standards

Independent review found no documented-standard violations. One low-priority
judgment call noted duplicated texture fallback and retained-picture lookup
between the menu and HUD adapters. They remain thin surface adapters with
different lifetimes and semantic mappings; a shared registry abstraction is
deferred until a change needs both.

## Spec

Independent review found one P2 omission: `COLLECT_MOVE_TACT` accepts B or Start
but lacked the Close footer. The final patch includes it with the same native
note/mode guards; the inventory and console checklist include that state. The
corrected patch series and target were reverified. No other spec findings were
reported.

Review totals: Standards 1 low-priority judgment call, 0 rule violations;
Spec 1 P2 finding, corrected.

## Hardware and resource limits

All installed-console observations remain **UNTESTED** for this change. Use the
[native-menu checklist](../../../docs/ps4/Native-menu-prompts-checklist.md) for
default/remapped instructions, conducting collection, already-open refresh,
fixed port navigation, relaunch, disconnect, readability and fit. Expected
values are preparation for those observations, not recorded hardware results.

The [coverage inventory](../../../platform/ps4/prompt-coverage.json) explicitly
retains unresolved native menu family/resource audits. Literal button names,
embedded controller artwork and shared instruction atlas regions require the
dedicated #79 slices. Source adaptation and representative samples cannot prove
complete menu or full-game coverage. #102/#79 physical acceptance stays open.
