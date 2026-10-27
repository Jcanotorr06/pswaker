# Ticket 58 verification

- Branch: feature/58-test-ownership; commit: 5b87545a5297f991d7220a1c44210e0a5ca01d2a.
- Based on integration e7793c5; merged integration #56 at 3cc0b9f and latest #57 tip 549f154 at task branch tip 4822e56.
- All 14 Python test modules, synthetic-disc generator, and six C++ harnesses moved to tests/ps4. Tests resolve commands, target source, and harnesses through shared Locations. Fixtures clone maintained checkout layout and resolve contract under platform.
- Maintained-input membership before/after test relocation: identical 144 repository-relative names. ownership.json content changes intentionally; test/harness/cache content remains excluded.
- All maintained Python and shell syntax passed under WSL. Six C++ harness contents equal original e7793c5 bytes. CI path filters checked on both push/pull_request for source, tools, tests, and workflow; compileall/discovery updated and shell syntax accepts either mixed command ownership.
- All four test_game.py cases pass from /tmp using absolute relocated discovery path.
- First full all-reference suite hit a route-audio setup naming collision (PLATFORM path versus existing environment variable). Fixed by naming reference environment REFERENCE. Final full rerun passed all 90 tests with no skips in 134.246 seconds; log /tmp/pswaker-58-tests.log. First attempt retained /tmp/pswaker-58-tests-first.log.
- Full-suite environment references unchanged read-only inputs from baseline-validation.json: maintained-15-a, game-23-a, aurora-host-20261022. All generated/mutated fixture/package/native outputs are temporary. No console acceptance claimed.

Merge notes: retained #56 added relocated-checkout CLI rejection test and #57 added PrivateOutputTests/storage rejection assertion. Post-#56 focused diagnostic suite: 15 tests passed in 16.788 seconds (/tmp/pswaker-58-after-diagnostic-merge.log). Relocated synthetic_disc.generate now takes the repository explicitly; its main caller uses LOCATIONS.repository. Keep this consistent when transplanting tests from other branches. Native runtime code and protected historical evidence untouched.



Post-#57 merge focused game/complete-package/private-output/storage/frame suite: 29 tests passed, no skips, in 30.210 seconds from /tmp (/tmp/pswaker-58-after-game-merge.log). Python/shell syntax rechecked after final merge. Inventory again matches all 144 baseline names after accounting for canonical diagnostic/game command renames. Final branch tip 4822e56 includes integration tip549f154, with clean working tree.
