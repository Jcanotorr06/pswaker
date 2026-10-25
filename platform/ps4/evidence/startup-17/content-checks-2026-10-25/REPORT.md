# Controlled content failures and repair — 2026-10-25

All three returned failure launches stop with the intended installation error,
computer-side rebuild/reinstall guidance and exit code 14. The repaired 01.04
launch validates the installed image and reaches file selection/gameplay with
zero checked errors, consistent with the owner's report that it launched as
expected. The behavioral failure and startup-recovery checks pass for the
recorded candidates. Seeded save/settings byte preservation is still pending.

## Candidate and evidence association

Each selected platform.log has one BEGIN block for build 6ebc07987fe3b6c6064a.
Its logged manifest version, complete program object and variant/image fields
match the retained [01.01](../inspection-01.01.json),
[01.02](../inspection-01.02.json), [01.03](../inspection-01.03.json) or
[01.04](../inspection-01.04.json) inspection. All use the same ELF and SELF as
the [startup candidate](../REPORT.md). Package hashes are retained in
[summary.json](summary.json); the logs identify the installed version and
embedded program/content manifest rather than hashing the whole installed PKG.

Original files remain unchanged in the four owner-specified directories under
local-research/game-17-artifacts/evidence/.
[original-files.json](original-files.json) inventories all 12 supplied log/stage
files by path, size and SHA-256. [selected-records.txt](selected-records.txt)
retains relevant lines with original line numbers.
[owner-observations.json](owner-observations.json) records the supplied visible
messages and repair result separately from the parsed logs.

The platform.prev.log in each directory is the preceding package's launch:
01.00 before missing, 01.01 before unreadable, 01.02 before invalid, and 01.03
before repair. Those rotated records are retained and are not counted as
additional runs of the directory's named check.

## Results

| Package | Observed result | Stop stage, main clock | Logged exit |
| --- | --- | ---: | --- |
| Missing 01.01 | Cannot open COS_DISC=/app0/game.iso: No such file or directory | 1.197 s | 14 at 27.054 s |
| Unreadable 01.02 | /app0/game.iso is not a regular file with a disc header | 1.243 s | 14 at 15.385 s |
| Invalid 01.03 | Installed image checksum is invalid | 48.268 s | 14 at 105.471 s |
| Repair 01.04 | Installed image and runtime assets validated; file selection and game scene/resource activity | No installation error | No exit captured |

Each failure records installation-error-stopped-before-gameplay. None records
installed-image-validated, writable-storage-checked, runtime-assets-validated,
game-scene milestones or gameplay heartbeats. Missing/unreadable stop at the
early fixed-path disc check; the invalid image reaches the full checksum guard.
Graphics initialized afterward for an error display do not imply gameplay.
The owner's quoted on-screen messages confirm rebuild/reinstall guidance and
Circle: Exit. No external-image prompt or fallback was reported; logs retain
the fixed /app0/game.iso path. One checked error per fault is the expected
installation failure, rather than an additional unrelated failure.

Repair 01.04 logs installed-image-validated at 47.917 s, known-shader preparation
complete at 47.987 s and runtime-assets-validated at 48.183 s. It reports allocated
internal 1280x720 and output 1920x1080. The subsequent name/file-selection records
and /res/Stage/M_NewD2/Room2.arc activity support recovery into a game scene; the
owner confirms the expected launch without an error. The last heartbeat is at
85.920 s with zero checked errors. A later disconnect pause is recorded; no
normal shutdown/audio-join sequence is present. This is startup recovery evidence,
not a repeated full-route or save-durability acceptance run.

## Preservation evidence still needed

The supplied evidence tree contains one unlabelled GCI save snapshot,
saves/USA/Card A/01-GZLE-gczelda.gci, and imgui.ini. Their sizes and hashes are
retained as private-snapshot metadata in the inventory; no save bytes are
committed. There is no settings.ini, labelled pre-test baseline, per-fault
post-test snapshot, repair-before-launch snapshot or comparison record in these
directories. imgui.ini is not the specified /data/pswaker/settings.ini consumer.
The single save snapshot cannot establish unchanged bytes across all updates.

The runtime's visible "saves/settings are preserved" guidance is not itself a
measurement of the seeded files. The owner's earlier no-issues-saving report
also does not replace this comparison. A question about existing comparisons or
their local paths is pending; there is no claim that files changed or were lost.

#17 therefore remains open only for this required preservation evidence. If no
before/after comparison was made, use the [controlled-failure checklist](../../../Startup-checklist.md)
with a backed-up valid save and identifiable settings seed, compare each stopped
launch and the repaired installation before gameplay can legitimately change
those files. The successful gameplay route does not need repeating.

Host verification for this review checks logged-manifest equality against all
four retained inspections, expected error/stage/exit records, lack of gameplay
records in faults, repair validation/dimensions/zero-error heartbeats, and original
file hashes plus excerpt line correspondence. No executable/package change or
performance fix is made by this evidence review.
