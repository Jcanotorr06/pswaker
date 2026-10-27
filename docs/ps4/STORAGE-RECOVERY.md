# Storage failure recovery (#21)

The shared profile, installed image, stable application identity and cache
separation remain those in [PERSISTENCE.md](PERSISTENCE.md). This checkpoint
adds whole-save staging, a previous valid backup and explicit recovery before
gameplay. Hardware acceptance requires the [owner checklist](Storage-recovery-checklist.md)
and returned evidence for the actual installed candidate; host results alone
do not establish PS4 durability or first-playable acceptance.

## Completed-save boundary

Each game card worker store begins a transaction for that channel's
`01-GZLE-gczelda.gci`. Before any CARD mutation, check the existing save and
durably copy a valid completed primary to `.gci.backup`. Initialize an exclusive
`.gci.pending` staging file. Aurora's real GCI creation, block writes, readback
and metadata commit use that stage on the worker thread. Reads outside a
transaction continue to use the primary. A first save leaves the primary absent
until completion; a later save leaves it unchanged throughout the CARD calls.

After all requested blocks, metadata and CARD close succeed, validate the
complete staged USA GCI, then use the checked synchronized replacement to
publish it. Clear/sync the stage before returning success to the game. Failures
return the existing game I/O failure state, retain the previous backup and
affected stage, and prohibit further stores in that process. The port stops at
a frame boundary and surfaces the failure through its Quit error screen; it
does not request a new save. Logs distinguish `save-completed=0/1`.

Validation checks the fixed USA identity/filename/block count/size, the game's
required banner/icon/comment metadata, supported
data version, both block checksums, all three slot checksums in each replica,
and matching replicas. A missing primary with backup data is an error rather
than permission to initialize new progress. Startup checks both channels before
the game/card system starts, and the worker rechecks before loading to prevent
the inherited automatic replica-repair writes. These are detectable format and
checksum failures, not semantic validation of every gameplay field or a claim
to detect every possible bit change.

## Player recovery

Invalid/unreadable saves and interrupted stages stop gameplay with the exact
path and repair guidance. A validated backup enables **Cross: Restore previous
save**. **Circle: Exit** declines without modifying the primary, stage or backup.
Without a valid backup, only Retry after external repair or Exit is available;
there is no reset/initialize action. Unavailable storage retains its separate
startup Retry/Exit gate. Settings failures retain their existing checked-write
feedback; no settings defaults overwrite unreadable/invalid settings.

An explicit restore first copies affected primary and stage bytes to unique
`.evidence-XXXXXX` files beside the originals, including wrong-sized data.
Only after preservation succeeds does it replace the primary from the backup.
The backup and evidence remain after recovery. A failed restore reports failure
and retains those files. Never remove these files as disposable shader caches.

File/directory sync or close errors after a visible rename are **uncertain
completion**, reported as failure. The primary may already contain the newer
bytes; the previous validated backup remains recoverable. A stage normally
gates uncertain/interrupted work at relaunch; if the final stage removal is
visible but its directory sync fails, the next launch can see a valid newer
primary. Do not interpret that visibility as proof of a successful prior save
or power-loss guarantees. Retain the failure log and backup before testing.

## Quit and controlled checks

Quit waits for both queued and active card work. A timeout permits continued
waiting, not abandoning a busy worker. A finished failed save requires an error
acknowledgment before exiting with a nonzero status. Only then request SDK
shutdown, join/drain the audio producer, synchronize GPU work and shut down
Aurora/SDL. Quit never saves unsaved gameplay. New stages bracket card completion
and SDK stop for retrieval. The exact previous `JUTGba.cpp:623` panic was
reproduced with real GBA/SDK queue workers on the host: an unsuccessful blocking
receive during shutdown dispatched an uninitialized command. The patch exits
that worker on the no-message wake and uses pointer-sized host message storage.
The regression joins all four workers; target shutdown evidence remains needed.

Only an owner-created `.gci.test` text marker enables controlled faults:

| Exact bytes | Behavior |
| --- | --- |
| `fail-write\n` | Return ENOSPC from the checked commit of an active staged CARD write. No primary-write fault is injected and no genuine full-disk condition is needed. |
| `hold-publish\n` | Hold a completed requested store for 20 seconds before publication, allowing a pending-write Quit check. |

Marker errors offer Retry/Exit and cannot offer to restore healthy progress.
Startup visibly explains any enabled mode and requires an explicit choice to
continue. Unknown/unreadable markers gate startup. Markers persist until the
owner removes them; they are never bundled in the package. Use only isolated
disposable progress. The same modes run through real GCI I/O; they do not mock
the order of internal calls or establish every physical media failure mode.

`storage-cases.py` prepares private controlled data from an explicitly supplied
disposable completed in-game GCI. It leaves the seed unchanged, rejects invalid
seeds and existing outputs, requires an inspected game package and places cases
outside the Git repository. It never connects to or modifies the console.

## Reproduce

Use the unchanged verified #15 platform inputs and a separate Linux/WSL2 root:

```bash
bash tools/pswaker/build-game.sh "$HOME/.cache/pswaker/game-21" \
  "$HOME/.cache/pswaker/maintained-15-a" 01.09
export PSWAKER_GAME_ROOT="$HOME/.cache/pswaker/game-21"
export PSWAKER_REFERENCE_BUILD="$HOME/.cache/pswaker/maintained-15-a"
export PSWAKER_HOST_ROOT="$HOME/.cache/pswaker/aurora-host-20261022"
python3 -m unittest discover -s platform/ps4/tests -p test_gci_persistence.py -v
python3 -m unittest discover -s platform/ps4/tests -p test_route_card.py -v
python3 -m unittest discover -s platform/ps4/tests -v
python3 -m compileall -q platform/ps4
```

Target compilation is the combined C/C++ typecheck. Real host SDL filesystem
tests observe completed/failed multi-write stores, corruption with/without
backup, decline and explicit restoration, oversized-file evidence, missing
primary recovery and controlled write failure. SDK-thread tests retain the
pending-card observer and reproduce the GBA shutdown bug. GPU, actual in-game
loaded landmarks, physical output and PS4 filesystem behavior require the
installed application and owner return.
