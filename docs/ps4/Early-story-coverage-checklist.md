# Early-story cohort E: owner capture checklist (#139)

Use with [inventory revision 1](COVERAGE-INVENTORY.md) and the
[campaign protocol](COVERAGE-CAMPAIGN.md). The current
[cohort matrix](../../evidence/ps4/early-story-139/scenario-matrix.json) records
pending observations; the [preparation report](../../evidence/ps4/early-story-139/REPORT.md)
identifies the discovery package. This checklist does not claim console coverage.

## Package and entry checkpoint

The private Downloads folder `PSWaker-139-Early-story-D1` contains candidate
**139-D1**, the exact **137-D1** package bytes reused for early-story discovery:
app **01.23**, build **`6e885683f47a49a119ae`**, PKG SHA-256
`b410b25cd7dabc7ca1abe648e24254c214cb6faf4ca768b08fa2a39dca73f0b0`.
Install `out/IV0000-PSWK00001_00-PSWAKERGAME00000.pkg`. Retain its matching ELF,
assembly/inspection records, `frozen-D1-seed`, C000, checksums and source
provenance. The 287-description seed is the starting corpus, not an expanded
early-story result. No #137 physical pilot return is available at preparation.
If a later compatible cumulative return becomes available, have it analyzed and
incorporated before starting another discovery branch; do not silently replace
an independently accumulated database.

Use PS4 Slim / firmware 9.00 / GoldHEN v2.4b18 and the supported USA `GZLE01`
revision 0 image. Keep stock quality, 1280x720 internal target, 30 Hz game logic,
the current synchronous renderer and the same applied controls. Record actual
configuration and discrepancies. New package installation alone is not evidence.

1. Fully close the application. Back up all `/data/pswaker/` privately, with
   readable copies and file sizes/SHA-256. Preserve `/data/pswaker/saves/` and
   `/data/pswaker/settings.ini` independently of disposable caches.
2. Create **CP-E0**, an ordinary new original-quest test file before Outset
   departure. Retain the earliest save and additional pre-event backups before
   forest rescue, shield/departure and each irreversible event. Film new-file,
   name entry and prologue from file creation: loading a post-prologue save
   cannot replay them. Back up other slots before using a disposable slot.
3. Record the actual file/hash, reload location, equipment, flags and approach.
   A save alias in the matrix is a request, not a supplied save. If only a
   Windfall/later save exists, keep it and start a separate ordinary test slot
   for S01-S03; do not count those rows from later progress.
4. Retain **CP-<S/B/I ID>-entry/exit** around each row and a pre-boss backup
   before triggering either boss. Multiple IDs may reference the same actual
   backed-up save. Ordinary saves may reload at a dungeon entrance: record and
   film the entire re-entry walk. Use no edited saves, debug warp or stage select.

## Discovery launches and cumulative milestones

Film from launch through normal Quit and keep timecoded notes. Use
`scenario-record.example.json` privately per scenario/variant/launch and
`action-notes.csv` for identifiable actions. Record stage/room IDs from actual
logs, not guessed place-name mappings. Keep unknown observations null.

For the first discovery launch, archive and rename only
`/data/pswaker/cache/6e885683f47a49a119ae/` to an unused sibling while closed;
record absence if missing. This empties runtime and driver caches together.
The bundled seed supplies all C000 descriptions, as checked by full-byte
membership. Keep C000 separately. If continuing an analyzed compatible #137
return instead, record its identity and retained-cache state explicitly.

For later discovery launches on this same build, **retain** the accumulating
runtime database and driver caches, even when restoring an earlier ordinary
save. Never clear the discovery corpus to replay an event. Each launch must
show preparation completion/cleanup, ready/total, pending zero, errors zero and
`known-shaders-prepared` before gameplay. Record full preparation, final drain,
visible launch-to-control, progress/input responsiveness and available memory
observations separately. Startup phases overlap; there is no time ceiling.

At each S-row and boss milestone, ordinary-save, use **Quit game...**, observe
`shutdown,complete`, fully close, then retrieve before any new launch. Preserve
immutable `C-E-S01` through `C-E-S07` milestones and boss/interior/optional
sub-milestones when separate. A milestone contains the source DB and adjacent
WAL/SHM (or explicit absence), hashes, logs, save references and action notes.
Never copy a live SQLite database or overwrite an earlier milestone. A crash
return is retained as a failure and cannot claim normal shutdown.

## Fixed story, boss and interior routes

This table instantiates the inventory's fixed E membership. Traverse every
normally reachable room and side room, not just the shortest story path. Keep
a private room/branch/reward checklist; record locked gates in the deferred
ledger below. Record first entry, each transition/item-get/cutscene and each
new enemy/effect before repeating. Retain pre-event saves before advancing.

| IDs | Repeatable route and identifiable observations |
| --- | --- |
| S01; I01-I04 | New-file/name/prologue; Outset home and healthy family, under-house crawl/chest, Orca tutorial, Sturgeon/Mesa/Rose dialogue/objects; village, forest rescue, shield and departure. Pan interior/exterior, foliage/water/sky and near walls; identify dialogue-to-control transitions. |
| S02; I05 | Ship deck, pirate hold and first rope course including falls/recovery, reward and fortress arrival/launch. Record rope/climb/camera and cutscene transitions. Second rope course belongs to S09/I12. |
| S03 | First fortress stealth/searchlights, detection and recovery, prison/yard and all reachable interiors/side rooms, enemy weapons, sword recovery, tower and ejection. Keep this pre-ejection route replayable; second/third visits do not substitute for it. |
| S04; I06-I09 | Windfall arrival/boat dialogue, sail purchase, jail/switch/Tingle/maze/Picto Box, school/teacher/children, Lenzo ground floor, cafe/potion shop/mansion, departure. Attempt optional tasks below before story changes; record closed interiors and actual gates. P01 can share timed observations but covers only its bounded subset. |
| S05; I10 | Dragon Roost approach/boat/shore, Wind Waker/song acquisition and conducting, Rito hall/mail desk and Komali room, Medli interaction and cavern access. Retain pre/post cavern NPC states. |
| S06; B01; I10 | Entire Dragon Roost Cavern room/side-room/switch/map/compass/big-key route, water/lava/fire, grapple acquisition/use, miniboss and approach. Gohma introduction, grapple/debris/shell phases, exposed eye, defeat/heart/portal and Din's Pearl; then post-cavern Rito revisit. Keep pre-boss save, actual entrance reload and approach. |
| S07; B02; I11 | Forest Haven/Deku Tree introduction, Hollo shop, waterfall/Makar area, leaf acquisition/flight, entire Forbidden Woods room/side-room/switch/chest/miniboss route, boomerang acquisition and Mothula. Kalle Demos introduction, vine severing, core/recovery, defeat/heart/portal and Farore's Pearl; post-woods NPC revisit. Stop at CP-E1 before departure for Greatfish. |

For both bosses capture each phase and visible effects, damage/block and rewards.
Repeat a boss/cutscene only from its retained pre-event checkpoint, keeping the
cumulative discovery cache. A post-boss save cannot prove its introduction.

## E actions, enemies, menus and rendering variations

Every Q row needs acquisition/native-menu assignment, identifiable **first use
and at least three repeats**, successful and blocked/empty responses where
applicable. Log each repeat individually; one vague "combat done" note is
insufficient. For consumables/irreversible scenes retain pre-use saves. An
unavailable variant stays visible with its later ID/route.

| IDs | Actions to identify on the preceding routes |
| --- | --- |
| Q01 | Walk/run/roll/crouch/crawl, ledges/jump/climb, ladder/rope, swim/splash and drown recovery. |
| Q02 | Sword standing/combo/thrust/jump/spin/parry, shield raise/deflect; record actual attacks/targets. Master Sword stages/Hurricane Spin stay later variants. |
| Q03 | Carry/throw/drop/break pots, rocks, barrels, sticks and enemy weapons; torch light/extinguish. |
| Q04 | Telescope zoom; Picto Box aim/capture/album. Deluxe/night/legendary photos stay named later variants. |
| Q05-Q07 | Boat sail start/stop/turn/jump and grapple salvage; Wind Waker learned songs/invalid melody; grapple swing/climb/spoils/failed target. Cannon is M/Q11; later songs/cyclone travel stay later variants. |
| Q08 | Bottle acquisition, empty/fairy/firefly/water/Forest Water/potion use/release/refill and expiry when reachable. Soup is S10/O19; absent contents need ledger entries. |
| Q09-Q10 | Leaf fan/glide/land/updraft/wind/empty magic; boomerang single/five targets/obstruction/return/catch/vines. |
| Q16-Q17 | Bait Bag/bait/seagull when reachable; damage/knockback/fire/hearts/rupees/spoils, fall/void/water/lava and game over/continue. Retain a disposable backed-up save for destructive outcomes. Merchant delivery items, Hero's Charm and Magic Armor remain later variants. |
| F01-F04 | At actual encounter rooms: Bokoblins/weapons/colors, Miniblins, Moblins/searchlights; Keese/fire Keese, rats/bomb carriers, red/green ChuChus; Magtails, Kargarocs, Peahats, Boko Babas; Morths, winged/wingless Mothula, land/sea Octoroks. Log introduction, each state/attack, player hit/block, defeat/drops and encountered variants. Record unseen families/variants rather than assuming them. |

On each route include native inventory/owned item icons, assignment, sea/dungeon
charts/maps, dialogue/choices/purchases/item-get, save/reload/game-over and song/
pictograph UI. Film mandatory cutscenes and the first resumed frame. Cross-link
these observations to N01-N08; those A rows remain incomplete for later icons,
credits and variants. Observe camera close/far/low/overhead/occlusion/lock-on/
aiming indoors, outdoors and on boat, water/sky silhouettes, reachable lighting/
weather/day states, pre/post dungeon switches and NPC changes. Cross-link V01-V12
without claiming late storm/Hyrule/ice/mirror observations. Include reachable
leaf/foliage/projectile overlap X06 and lava/smoke/grapple/debris/enemy fire X08;
remaining overlap variants stay with their named later routes.

## Reachable optional content and deferred ledger

At each safe visit attempt the following normally reachable content with owned
equipment. Record the actual gate, prerequisite, entry-save/mooring and outcome.
Do not bypass a gate or advance past CP-E1 to finish a side task. C/O/SEA/N/V/X
IDs retain their inventory A membership: an E discovery is shared evidence,
and never silently completes their remaining variants. Every deferred entry
needs `(ID/variant, observed prerequisite, later cohort/route, checkpoint, status)`.
The matrix contains these named assignments; fill the actual reachability and
private references before calling the reachable-optional scope reconciled.

| Original IDs | E opportunity / explicit later assignment |
| --- | --- |
| O01/I03/Q02 | Orca endurance if accessible; crest/Hurricane Spin later at A/O01 from CP-L1 with crests. |
| O02/I07 | Killer Bees and available pendant presentations; remaining pendant/deed/charm outcomes at A/O02 from CP-L1, retaining pre-reward saves. |
| O03/I08/Q04/Q08 | Lenzo tasks, firefly and Deluxe upgrade if normally reachable before CP-E1; remaining assistant/couple/legendary variants at A/O03 from CP-L1 or retained pre-task saves. |
| O04-O06/I09/Q08 | Available auction, mansion/dialogue and potion/bottle interactions; later wealth/mail/Moblin-letter chain O05 after S13, all prizes/jelly unlocks at A/O04-O06 from CP-L1/pre-reward backups. |
| O07-O08 | Windfall Squid Hunt, Rito mail sorting, reachable flight/course/cannon games; absent locations/equipment and remaining reward/failure variants at A/O07-O08 from CP-L1. |
| O12/Q16 | Beedle normal shop, bags/bait/purchases; special shop/membership/sold-out variants at A/O12 from CP-L1/pre-purchase backups. |
| O14-O15/I11/Q08 | Gallery entrance/photo opportunities and Forest Water/saplings when reachable; full seven-hall/missable-photo/figure circuit and eight-site timed watering at A/O14-O15 from CP-L1 plus retained pre-boss/pre-NPC saves. Preserve early photos/checkpoints now. |
| O16 | Available merchant/decoration exchanges; post-rescue Mila and bomb-dependent lighthouse/remaining chain at A/O16 from CP-L1 with retained pre-event saves. |
| O19/I01/Q08 | Available pig/carry/fairy interactions; soup at M/S10, fountain and later pigs/dungeon statues at A/O19 from CP-L1. Tingle Tuner support is unconfirmed; preserve a named observation gap rather than claiming statues. |
| C02/C04/C05/C17-C22; O17 | Attempt only entrances/puzzles ordinarily accessible on permitted E sailing legs with current equipment. Record each visited gate separately. All remaining cave/fountain/optional branches return at A under the same ID from CP-L1 with pre-upgrade backups. |
| C01/C03/C06-C16; O09-O11/O13/O18/O20 | Equipment/story/route-dependent content remains named A circuits at CP-L1: hookshot/bracelet/elemental/bomb/boots caves, charts/Ghost Ship/cabana, sea combat, Labyrinth and fortress revisit. If an early subset is encountered, record it under its original ID without dropping later branches. |
| SEA01-SEA49; N01-N08; V01-V12; X01-X10; A01-A10 | Record E transit/menu/world/overlap subsets by original ID. Full sector circuits and remaining variations use CP-L1 in A/#142; second quest uses CP-CLEAR. Bomb/cannon overlaps X01-X02/X07 first become relevant in M/Q11; ice/mirror/companion X04-X05/X09 in L. |

## Retrieve, expand, freeze and replay

After **each** normal Quit and before another launch, return the unique
`/data/pswaker/logs/performance-XXXXXX/` directory, `platform.log`,
`platform.prev.log`, `last-stage.txt` and crash logs if any; the entire closed-app
build cache including `pipeline_cache.db` and adjacent WAL/SHM or absence; video,
timecoded notes and entry/exit save/settings backups with hashes. Use separate
private launch folders and never upload game-derived artifacts to GitHub.

The agent snapshots each cumulative source with `complete-package.py pipeline-seed`
and compares full configuration identities/description bytes with
`verify-coverage.py`, preserving source hashes/provenance. See the exact commands
in the [campaign](COVERAGE-CAMPAIGN.md#cumulative-database-and-frozen-validation).
Check old C000/prior milestones against each expanded seed too; report distinct
additions and conflicts, never invent configurations or infer additions from
row count alone. Keep failed comparisons. No database consolidation is implied.

After discoveries, the agent validates the standalone asset, assembles and
freshly inspects the expanded complete package and identifies **139-V1** (or a
later iteration). V1 is currently unsupplied. Freeze PKG/build/ELF/seed/inspection
identities; a changed seed requires a new candidate and another validation.
The existing desktop bundle is unchanged by this discovery handoff.

Archive the cumulative discovery DB/WAL **before** clean validation. For every
accepted cold launch back up/rename only the identified build's runtime/driver
cache, restore the exact ordinary entry save, and film startup plus the full
approach/route without hidden gameplay warmup. Included configurations/layouts
must prepare/clean up before gameplay. Analyze every raw `shader-wait-ns` event
and frame shader counter delta, including sample 0, small waits, loading and
first resumed frames; require zero missing-pipeline creation/waits and full-byte
seed membership. Preserve timing uncertainty, invalid/incomplete intervals,
rendering faults and residual non-compilation stalls. The Outset/forest-only
analyzer cannot certify these routes; do not relabel scenes to get a pass.

Retrieve the cold return first, then replay the same ordinary save/route/package
with retained caches for a **separate compatible warm comparison** and retrieve
again before logs rotate. Warm evidence cannot pass cold coverage. Observe
rendering/effects, representative controls/audio, save/settings preservation,
progress and preparation/gameplay resource viability. No startup-time ceiling
or full-game feasibility claim follows from the small seed. Expanded resource
measurement also belongs to #138; final campaign acceptance belongs to #144.

## Exit artifacts for middle story (#140)

Stop after Farore's Pearl, **before departing Forest Haven for Greatfish**.
Return **CP-E1** as an actual ordinary save backup with private reference,
SHA-256, actual reload location/approach, equipment/flags, settings and compatible
build ID. Verify its ordinary reload without passing the exit boundary; retain
the reload launch separately. Keep CP-E0 and all pre-boss/pre-event backups.

Return **C-E**: the compatible cumulative closed-app database/WAL pair (or
explicit absent sidecar), hash inventory, validated standalone snapshot and
`pipeline-seed.json` provenance, source milestone chain and membership reports.
Keep discovery C-E independently of cold/warm validation caches. Bind CP-E1/C-E
to the exact candidate and inventory revision; list every outstanding optional
ID/variant, prerequisite and named later route from the ledger. Neither artifact
currently has an owner-returned file reference. #140 starts at CP-E1; S08 storm
arrival and later scenes are outside this cohort.

Update each matrix row with actual candidate/cache identities, actions, capture
references and results. Missing observations require a named scenario/variant,
missing evidence, risk, exact candidate and **explicit owner acceptance** with
date/decision reference. No waiver is currently accepted. Observed missing
pipeline creation/waits require correction and clean replay and cannot be waived.
Keep #139 open and `ready-for-human` while physical work is next; passing this
cohort would not establish final full-game acceptance.
