# Repository migration verification records

The [maintained verification report](../../../docs/ps4/REPOSITORY-MIGRATION.md)
describes scope, outcomes, ownership exceptions and limits for issues #54–#60.

- `baseline-inputs.json`, `baseline-protected.json` and
  `baseline-validation.json` record the original commit, 142 maintained files,
  474 protected hashes, reference roots and 84 passing baseline cases.
- `pswaker-54-baseline-tests.log` and `pswaker-54-baseline-gci.log` preserve
  the original baseline runs, including the separately supplied GCI prerequisite.
- `validation-56.json` and the ticket #57–#59 summaries retain preceding
  implementation-slice checks. Their original temporary log paths are historical
  run locations, not maintained navigation links.
- `final-inputs.json` and `migration-comparison.json` account for all 142 mapped
  original inputs plus the two new shared ownership inputs.
- `committed-protected-comparison.json` independently checks original and final
  Git blobs: 455 exact matches, 19 navigation-only Markdown changes, zero errors.
- `validation-60.json`, `pswaker-60-tests.log` and `audit-60.json` record the
  consolidated 93-test run, syntax, CI coverage and migration audit.
- `link-check.json` records the original external local-link checker result;
  `tracked-link-check.json` also requires every local destination to be a tracked
  file or directory, preventing ignored checkout remnants from hiding broken links.

Verification used WSL Python 3 with the three existing reference roots supplied
through `PSWAKER_REFERENCE_BUILD`, `PSWAKER_GAME_ROOT` and `PSWAKER_HOST_ROOT`.
Discovery ran from `/tmp` against the absolute `tests/ps4` path. References were
read-only inputs; generated native binaries, synthetic data, package extraction
and mutation stayed in temporary directories. WSL Git audits used equivalent
`GIT_DIR`/`GIT_WORK_TREE` paths because Windows-created worktree pointers are not
directly interpretable by WSL Git; shared metadata was left unchanged.

Two stale historical build-directory links were repaired after the fresh-worktree
check exposed them. Only navigation destinations changed. The previous
intermediate unmatched shell-glob CI failure is documented in
`transient-ci-note.md` and fixed by the final find-based scan. The consolidated
run has no skips, failures or regressions. Host/source migration checks confer
no console acceptance on a new package.

These records, tests, documentation and caches are excluded from maintained build
identity selection. Previous packages and console evidence retain their original
identities; no historical manifests, raw captures or hash-recorded helpers were
regenerated.
