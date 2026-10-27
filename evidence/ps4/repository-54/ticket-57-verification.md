# Ticket #57 verification

Implemented on feature/57-game-tooling, commit 5c718a3, based on integration e7793c5.

Nine game commands moved to tools/pswaker, no forwarding copies. Runtime/CMake, locks, contracts, patches and owner frame example remain platform/ps4. Explicit shared Locations resolve resources, diagnostic inputs, game preparation, package imports and repository restrictions. Active game documentation and CI shell checks updated.

TDD: changed cached-source rejection invoked canonical moved prepare-game path and failed because the new path did not exist. After migration all four game tests passed, including source/staging drift and native installed-content checks.

WSL full suite with PSWAKER_REFERENCE_BUILD=/home/joseph_cano/.cache/pswaker/maintained-15-a, PSWAKER_GAME_ROOT=/home/joseph_cano/.cache/pswaker/game-23-a and PSWAKER_HOST_ROOT=/home/joseph_cano/.cache/pswaker/aurora-host-20261022: 90 tests in 142.366 s, OK, no skips. All three roots used read-only; fixture copying, package extraction/assembly and native harness compilation use temporary areas. This run began before the additional relocated private-output case was added; that new case passed in the focused complete-package rerun (18 tests, 6 reference-prerequisite skips because environment intentionally absent for that focused run). Storage-case focused rerun including added outside-repository negative check: 1 test passed. Thus all 91 current unique cases exercised, six reference-package cases covered by full run.

Python compileall for platform and tools, bash -n for all platform/tools shell scripts: passed. All Python game CLIs --help from cwd=/ succeeded. Canonical command uniqueness, retained game CMakeLists and target resource existence checked. git diff --check passed. No evidence, lock, patch, provenance or target CMake content edited. No new target game build or console acceptance claimed.

Merger notes: keep #57 moved build-game version (TARGET resolved through build_inputs.py, INPUTS command resolved through ownership), reconcile #58's relocated test root and explicit synthetic_disc source=repository version. Preserve added PrivateOutputTests in relocated test_complete_package.py and added storage guard check. #56 may overlap CI shell command; keep canonical tools shell coverage.
