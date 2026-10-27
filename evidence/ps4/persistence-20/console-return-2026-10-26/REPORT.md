# Returned persistence evidence — 2026-10-26

The supplied logs corroborate the actual 01.07 → 01.08 complete-package
transition, the shared storage check and the persisted Standard text setting.
All four returned settings copies are byte-identical. The owner reconfirms
**PS4 Slim / firmware 9.00 / GoldHEN v2.4b18**, reports no settings.ini before
the first run, and says saves across all runs behaved as expected.

The owner subsequently confirms the text visibly changed and stayed Standard
after full close/relaunch, separate 01.08 installation and clearing only the
cache. Quit returned normally to the owner; relaunch loaded the last completed
save and did not retain the unsaved gameplay action. Together with matching
runtime manifests and settings comparisons, this completes the **bounded #20
persistence checkpoint** for this candidate.

This does **not establish clean internal shutdown**: a deliberate port Quit
confirms an idle card, then logs a JUTGba panic and exits with code 12. Preserve
that unresolved lifecycle finding for the #19 shutdown follow-up and #21
pending-write work; do not describe the panic as fixed or the audio/GPU teardown
as complete. It does not contradict the observed completed-save preservation
and absence of automatic saving required by #20.

## Build and returned-file association

Original files remain unchanged under
`local-research/persistence-20-artifacts/evidence/`. The
[original inventory](original-files.json) retains relative paths, sizes and
SHA-256 values for all 19 files. No save or raw settings file is committed.
The [summary](summary.json) retains parsed launch/settings records and
[selected records](selected-records.txt) identify the original log line numbers.
[Owner observations](owner-observations.json) remain separate from parsed facts.

Every selected 01.07/01.08 launch logs build `9ac6fb9b2da43e02d642`. Its complete
program and image objects match the retained [01.07](../inspection-01.07.json)
or [01.08](../inspection-01.08.json) inspection, including ELF/SELF/image hashes.
The title/content IDs match `PSWK00001` /
`IV0000-PSWK00001_00-PSWAKERGAME00000`. This associates the observations with
the inspected packages through the embedded manifest and compiled identity;
the supplied logs do not independently hash the installed PKG or executable.
Retain the original package hashes in [artifacts.json](../artifacts.json).

There are **five distinct candidate launches**, rather than one launch per
supplied log file. `logs-2/platform.prev.log` equals `logs-1/platform.log`;
`logs-4/platform.prev.log` equals `logs-3/platform.prev.log`;
`logs-5/platform.prev.log` equals `logs-4/platform.log`. In addition,
`logs-3/platform.log` is an exact byte prefix of `logs-4/platform.log`: those
are earlier/later captures of the same launch. All relationships were checked
against original bytes. `logs-1/platform.prev.log` is the historical 01.06
binary and is excluded from this candidate's results.

## Persistence results

| Selected launch | Version | Cache files before init | Loaded port setting | Result supported by return |
| --- | --- | ---: | --- | --- |
| `logs-1/platform.log` | 01.07 | 0 | Large | Storage check succeeds; logs `SETTINGS saved=1 port-text=standard`. Owner reports no initial settings.ini. |
| `logs-2/platform.log` | 01.07 | 4 | Standard | A new process loads the changed preference at the same application version. |
| `logs-3/platform.prev.log` | 01.08 | 4 | Standard | Newer complete-package manifest loads the same preference with stable app/program/image identity. |
| `logs-4/platform.log` (also prefix captured in logs-3) | 01.08 | 0 | Standard | Same build starts with no cache files, retains the preference and reaches gameplay; later port Quit hits the shutdown panic. |
| `logs-5/platform.log` | 01.08 | 4 | Standard | Subsequent launch retains the preference; owner reports saves still behaved as expected. |

All five complete the checked shared-profile storage gate, installed-image
validation and runtime-asset validation. Gameplay heartbeats retain
`checked-errors=0`; that counter **does not include the later panic**, so its
zero value is not treated as proof of an error-free Quit. The successful target
storage checks and setting write exercise file/directory sync on this console
under available-storage conditions. They do not establish power-loss durability
or the controlled unavailable-storage Retry/Exit path.

The four private files `settings.ini 2`, `settings.ini 3`, `settings.ini 4` and
`settings.ini 5` are each 21 bytes and contain the Standard preference
(`PSWAKER_LARGE_TEXT=0`). Each SHA-256 is
`9a017da4410aec1edb9b5deefacacdfe7dd7e7c078b1d8d47fdbfc87a756acdc`.
Their byte equality is independently verified across the returned sequence.
Absence before the first run is owner-confirmed, rather than inferred from an
unprovided initial file. There are no GCI files in this return: save/load
behavior is owner-observed, not an independent before/after GCI comparison.
No agent operation changed real owner progress or restored seeded data.

## Quit finding and evidence limits

`logs-4/platform.log` lines 797–804 record deliberate Settings → Quit → Exit
confirmation and release. Line 805 records `EXIT code=0` at 171.226 seconds;
lines 806–807 enter the card wait and report `card-status=1` (idle). Line 809
then records a panic in `JSystem/JUtility/JUTGba.cpp:623`; line 811 records
`EXIT code=12`, followed by asking the shell to close the title. The last-stage
file remains `shutdown-waiting-for-card`, consistent with that stop.

No `audio-producer-joined`, `gpu-synchronized` or `shutdown-complete` record is
present. This is a captured abnormal shutdown after the card was idle; it is
not evidence of a failed save, a pending-write overlap, or completed orderly
audio/GPU teardown. Successful save behavior after relaunch does not remove
the panic from the record. This evidence review makes no root-cause diagnosis
or executable change and does not transfer a future fix's hardware status to
this binary.

The owner answered both focused follow-up questions explicitly: all three
visible setting-retention checks passed; Quit returned normally, the last
completed save loaded, and the unsaved action was absent. These are owner
observations, not inferred from filenames or time. They complete the requested
relaunch, distinct update, cache-only clearing and Quit-persistence outcomes.
The successful startup/storage path is exercised on target; unavailable-storage
Retry/Exit remains implemented/host-checked, with controlled target failure
trials assigned to #21. Full storage failure/corruption recovery, previous-valid-
save backups and controlled pending writes remain #21; the complete first-
playable acceptance and orderly internal shutdown are not declared here.

Validation for this review parsed every returned manifest, checked selected
program/image/identity equality against both retained package inspections,
verified all original-file hashes and log duplicate/prefix relationships, and
compared all four settings byte strings. No runtime, package, source pin or
build manifest was changed, so the earlier 48-test and target-build results
remain associated with the unchanged executable rather than being rerun for
this documentation update.
Independent [Standards and Spec reviews](REVIEW.md) verified the original-file
inventory, excerpts, manifest associations and stated acceptance limits, with
zero outstanding actionable findings.
