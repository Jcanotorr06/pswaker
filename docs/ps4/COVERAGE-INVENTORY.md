# Scenario inventory (#137), revision 1

Use with the [campaign protocol](COVERAGE-CAMPAIGN.md). All rows start `planned`
except P01 (`awaiting-console`). Every row needs the protocol's identity,
checkpoint, first-use/repeat, cache and evidence record for **each** listed
variant; a blank record is missing evidence. Named multi-room routes include
every normally reachable room/side room, with a returned stage/room checklist.
One launch may support several IDs when its timed observations identify them.
Rows bound the campaign; they do not enumerate every possible simultaneous state.

Location names were cross-checked against the unmodified game's supported
revision contract and the primary mapping-tool sources
[island names](https://github.com/LagoLunatic/wwrando/blob/master/data/island_names.txt),
[stage names](https://github.com/LagoLunatic/wwrando/blob/master/data/stage_names.txt)
and [original item-location mappings](https://github.com/LagoLunatic/wwrando/blob/master/logic/item_locations.txt).
Those sources are naming references, not instructions to install a randomizer.
Unused/test stages are excluded; normally reachable transitions, interiors and
variations below are included. Confirm actual stage/room IDs from returned
records instead of guessing them from a place name.

## Story, events and dungeons

Every S row starts at its pre-event backup and exits at the next ordinary save.
Record dialogue, item-get, doors, loading, cutscene and gameplay transitions.
For dungeon rows, perform side puzzles and miniboss routes as well as the boss.

| ID | Cohort | Bounded route and required events |
| --- | --- | --- |
| S01 | E | New file/name entry, prologue, Outset family/tutorial, forest rescue, shield and departure |
| S02 | E | Pirate ship deck and first rope course; arrival/launch toward fortress |
| S03 | E | First Forsaken Fortress: stealth, searchlights, prison/yard/interior, sword recovery, tower and ejection |
| S04 | E | First Windfall: arrival/boat dialogue, sail purchase, town interiors, jail/Tingle/Picto Box and departure |
| P01 | E | Windfall pilot: docks, square/vendor dialogue, bomb shop exterior, school interior and return; see checklist |
| S05 | E | Dragon Roost approach, Wind Waker/song, Rito settlement, Medli and cavern access |
| S06 | E | Dragon Roost Cavern complete room circuit, lava/water/fire, grappling, miniboss, Gohma and Din's Pearl |
| S07 | E | Forest Haven/Deku Tree introduction, potion shop, leaf flight, Forbidden Woods complete room circuit, boomerang, Mothula, Kalle Demos and Farore's Pearl |
| S08 | M | Greatfish storm arrival and ruined island; storm voyage to Windfall |
| S09 | M | Windfall return: bomb shop/pirate events, second rope course, bombs; retain pre/post event saves |
| S10 | M | Outset storm return, family illness/soup, bomb-opened Jabun cave and Nayru's Pearl |
| S11 | M | Place all three pearls, Tower of the Gods rising; water-level/statue room circuit, bow, Darknut, Gohdan and bell |
| S12 | M | First Hyrule: monochrome/frozen castle, Master Sword chamber, restored-color combat and sea return |
| S13 | L | Second fortress: hammer, Phantom Ganon, changed interior/yard, Helmaroc King and Aryll rescue |
| S14 | L | Hyrule return, Zelda revelation and barrier; retain pre/post reveal scenes |
| S15 | L | Cyclos encounter/normal song acquisition; mother-and-child fairy encounter, fire/ice arrows |
| S16 | L | Fire Mountain cooling/cave/bracelets; Ice Ring thawing/cave/boots/inner cave |
| S17 | L | Headstone entrance, Earth God's Lyric, Medli recruitment and Earth Temple full companion/mirror room circuit; Stalfos, mirror shield, Jalhalla, sword upgrade |
| S18 | L | Gale Isle entrance, Wind God's Aria, Makar recruitment and Wind Temple full companion/fan room circuit; Wizzrobe, hookshot, Molgera, sword upgrade |
| S19 | L | Original GameCube Triforce quest: eight chart routes (C11-C16/O09/O10), Tingle deciphering and eight chart-marked salvages, completion sequence |
| S20 | L | Final Hyrule approach: barrier removal, combat, bridge and Ganon's Tower entry |
| S21 | L | Ganon's Tower: four themed wings/rematches, maze, Phantom Ganon, stairs and Puppet Ganon's three forms |
| S22 | L | Rooftop approach, Ganondorf/Zelda battle, ending, credits and cleared-file save |

| Boss ID | Cohort | Encounter variants, entry/exit |
| --- | --- | --- |
| B01 | E | Gohma: introduction, grapple/lava shell stages, exposed-eye phase, defeat/heart/portal; pre/post S06 |
| B02 | E | Kalle Demos: vine severing, exposed core, recovery, defeat/heart/portal; pre/post S07 |
| B03 | M | Gohdan: hands/eyes, inhaling/bombs, arena effects, defeat/heart/portal; pre/post S11 |
| B04 | L | Helmaroc King: ascent/flooding, armor and unmasked attacks, defeat; pre/post S13 |
| B05 | L | Jalhalla: reflected light, carrying/throw, split/reform and defeat; pre/post S17 |
| B06 | L | Molgera: sand, tongue, flying phase, offspring and defeat; pre/post S18 |
| B07 | L | Tower rematches: Gohma, Kalle Demos, Jalhalla, Molgera; all four monochrome/filtered presentations; S21 wings |
| B08 | L | Puppet Ganon: puppet, spider, snake, transitions and defeat; S21 pre-boss backup |
| B09 | L | Ganondorf: sword/parry, Zelda light-arrow phases, reflected arrow, final strike; S22 pre-rooftop backup |

## Interiors not satisfied by an exterior visit

Enter, pan the camera, interact with the named feature/NPC and exit. Return after
story changes listed below; a locked entrance is deferred to A with the same ID.

| ID | Cohort | Interior route and explicit variant |
| --- | --- | --- |
| I01 | E | Outset house: healthy family; later sick/cured states in S10/A |
| I02 | E | Under-house crawlspace/chest |
| I03 | E | Orca: basic tutorial; crest/Hurricane Spin and endurance in O01 |
| I04 | E | Sturgeon, Mesa and Rose houses: dialogue/camera, objects |
| I05 | E | Pirate hold: first rope course; second/bomb reward in S09 |
| I06 | E | Windfall jail including cell, switch and maze/chest |
| I07 | E | School including teacher/children and pendant presentation in O02 |
| I08 | E | Lenzo house: ground floor; assistant/upper-room variants in O03 |
| I09 | E | Windfall cafe, potion shop and mansion; post-rescue wealth/auction/mail variants in O04-O06 |
| I10 | E | Rito main hall/mail desk and Komali room; pre/post cavern NPC state |
| I11 | E | Forest Haven interior, Hollo shop, waterfall/Makar area; pre/post woods state |
| I12 | M | Bomb shop and pirate hold before/after theft event |
| I13 | M | Jabun cave, Hyrule castle interior and sword chamber; frozen/restored variants |
| I14 | L | Second fortress interior, tower and Ganon room; subsequent revisit in A |
| I15 | L | Earth entrance/sage chamber and temple companion transitions |
| I16 | L | Wind entrance/sage chamber and temple companion transitions |
| I17 | L | Restored Hyrule castle, barrier route and final approach |
| I18 | L | Every Tower wing, maze, stairwell, boss chamber and rooftop transition |

## All Great Sea sectors

Each `SEAxx` uses the game's sea room number as its stable suffix. Cohort A's
fixed seven legs run west-to-east across rows north-to-south: SEA01-07,
08-14, 15-21, 22-28, 29-35, 36-42, 43-49. Use CP-L1 equipment. Enter each
sector by ordinary sailing, circle the landmark, land where possible, pan
shore/sea/sky and return to the boat. At each sector exercise its fish/chart
interaction, accessible lookout platforms, rafts/submarines and chart-marked
treasure if present, using a private feature checklist even when absent.
Named caves/fountains have separate rows. Day/night and weather are V01-V03;
pre-destruction/story states have S rows. Do not claim a sector's cave from the
surface leg. Save/back up at each leg's starting/ending mooring and record it.

| ID | Landmark | Additional route/linked gate |
| --- | --- | --- |
| SEA01 | Forsaken Fortress | All three normally reachable visit states: S03/S13/O20 |
| SEA02 | Star Island | Boulder cave C01 |
| SEA03 | Northern Fairy Island | Fountain C17 |
| SEA04 | Gale Isle | Wind gate S18 |
| SEA05 | Crescent Moon Island | Shore/chest and offshore features |
| SEA06 | Seven-Star Isles | Sea combat and Big Octo O13 |
| SEA07 | Overlook Island | Hookshot cave C12 |
| SEA08 | Four-Eye Reef | Cannons, ships and raised chest route |
| SEA09 | Mother and Child Isles | Normal approach plus enclosed fairy visit S15 |
| SEA10 | Spectacle Island | Cannon minigame O07 |
| SEA11 | Windfall Island | P01, S04/S09, I06-I09, O02-O06/O16 |
| SEA12 | Pawprint Isle | Both caves C02-C03 |
| SEA13 | Dragon Roost Island | S05-S06 and secret cave C04 |
| SEA14 | Flight Control Platform | Flight minigame O08 |
| SEA15 | Western Fairy Island | Fountain C18 |
| SEA16 | Rock Spire Isle | Cave C05 and special shop O12 |
| SEA17 | Tingle Island | Tower, charts/statues O09/O19 |
| SEA18 | Northern Triangle Island | Pearl placement S11 |
| SEA19 | Eastern Fairy Island | Fountain C19 |
| SEA20 | Fire Mountain | S16, C06 |
| SEA21 | Star Belt Archipelago | Shore/sea combat and salvage |
| SEA22 | Three-Eye Reef | Cannons, ships and raised chest route |
| SEA23 | Greatfish Isle | Storm/ruin S08, exposed ledges/chest |
| SEA24 | Cyclops Reef | Cannons, ships and raised chest route |
| SEA25 | Six-Eye Reef | Cannons, ships and raised chest route |
| SEA26 | Tower of the Gods | Pre/post rising S11, return water/entrance |
| SEA27 | Eastern Triangle Island | Pearl placement S11 |
| SEA28 | Thorned Fairy Island | Fountain C20 |
| SEA29 | Needle Rock Isle | Fire/light puzzle, cave C07, gold ship O10 |
| SEA30 | Islet of Steel | Cannon breach/interior C11 |
| SEA31 | Stone Watcher Island | Heavy-lift cave C13 |
| SEA32 | Southern Triangle Island | Pearl placement S11 |
| SEA33 | Private Oasis | Cabana, puzzle and labyrinth C14/O11 |
| SEA34 | Bomb Island | Cave C08 |
| SEA35 | Bird's Peak Rock | Seagull puzzle/cave C15 |
| SEA36 | Diamond Steppe Island | Warp-maze cave C16 |
| SEA37 | Five-Eye Reef | Cannons, ships and raised chest route |
| SEA38 | Shark Island | Switches/combat cave C09 |
| SEA39 | Southern Fairy Island | Fountain C21 |
| SEA40 | Ice Ring Isle | S16, C10 including inner cave |
| SEA41 | Forest Haven | S07, I11, gallery O14 |
| SEA42 | Cliff Plateau Isles | Cave C22, upper ledge and tree O15 |
| SEA43 | Horseshoe Island | Golf/puzzle cave O17 |
| SEA44 | Outset Island | S01/S10, I01-I04, labyrinth O18, fountain O19 |
| SEA45 | Headstone Island | Sage gate S17 |
| SEA46 | Two-Eye Reef | Cannons, ships, chest and Big Octo reward O13 |
| SEA47 | Angular Isles | Block puzzle and cave O17 |
| SEA48 | Boating Course | Timed course and hidden cave O08/O17 |
| SEA49 | Five-Star Isles | Submarine/sea combat and salvage |

## Caves, fountains and optional content

All C/O rows belong to A and use CP-L1 unless a pre-event backup is named.
Enter, traverse every normally reachable room/puzzle/combat branch, open the
reward, film the result, return outside and retain exit save. Ordinary fairy
fountain upgrades are one-time scenes: retain a pre-upgrade checkpoint.

| ID | Bounded cave route |
| --- | --- |
| C01 | Star Island boulder cave combat |
| C02 | Pawprint crawlspace/ChuChu cave, all branches |
| C03 | Pawprint hookshot-access Wizzrobe cave |
| C04 | Dragon Roost secret combat cave |
| C05 | Rock Spire cave, fire/Keese/chest |
| C06 | Fire Mountain cave, cooled exterior and hot return variants |
| C07 | Needle Rock cave, fire-arrow/torch puzzle |
| C08 | Bomb Island cave, Magtail/pressure switches |
| C09 | Shark Island cave, waves and reward |
| C10 | Ice Ring outer/inner cave, ice/boots/frozen enemies |
| C11 | Islet of Steel gunboat approach, interior/song/chart |
| C12 | Overlook platforms, hookshot chain and cave combat |
| C13 | Stone Watcher boulder, cave combat rooms |
| C14 | Cabana fireplace/crawlspace labyrinth, all branches/chests |
| C15 | Bird's Peak seagull switches, cave/song/chart |
| C16 | Diamond Steppe cave, all maze destinations/chests |
| C17 | Northern fairy: entrance, upgrade, return |
| C18 | Western fairy: entrance, upgrade, return |
| C19 | Eastern fairy: entrance, upgrade, return |
| C20 | Thorned fairy: entrance, upgrade, return |
| C21 | Southern fairy: entrance, upgrade, return |
| C22 | Cliff Plateau cave, plant/leaf route and upper exit |

| ID | Bounded optional route and variants |
| --- | --- |
| O01 | Orca endurance rewards and crest turn-in/Hurricane Spin; pre-reward save |
| O02 | Killer Bees hide-and-seek; teacher one/21/40-pendant rewards, deed/charm; pre-reward saves |
| O03 | Lenzo three assistant tasks, forest firefly/Deluxe upgrade, legendary pictographs and couple quest; pre-task backups |
| O04 | Windfall auction: bidding, win/lose and each distinct prize presentation |
| O05 | Maggie/mail/Moblin letter chain and necklace trades, pre/post-rescue mansion variants |
| O06 | Potion shop: red/green/blue jelly unlocks, buy/drink and bottle presentations |
| O07 | Squid Hunt and Spectacle cannon games: play, loss, win and reward variants |
| O08 | Rito mail sorting, flight platform, boating course: start, failure, success and reward |
| O09 | Tingle: chart deciphering for all eight original-game Triforce charts, map/fee/error dialogue |
| O10 | Needle Rock gold gunboat, Ghost Ship chart/use, all moon-dependent ship appearances, ship interior/combat/chart |
| O11 | Cabana deed/admission, all sliding-puzzle picture variants, reward/fireplace access |
| O12 | Beedle normal/special shops, bait/bag/purchases, membership rewards and sold-out/closing states |
| O13 | Big Octos (each eye-count variant), cyclone/Cyclos, sharks, Seahats and sea gunboats; fairy/magic upgrade reward |
| O14 | Nintendo Gallery entrance and all seven halls, figure creation/placement, missable-boss/NPC photos from pre-event saves, completion reward |
| O15 | All eight withered saplings: Forest Water bottle/timer, each watering, success and expired-water observation; record sites |
| O16 | Windfall trading/decoration chain and merchant exchanges, town reward, Mila night pursuit, lighthouse/windmill, transparent chest |
| O17 | Horseshoe golf/cave, Angular blocks/cave, Boating Course cave; all branches and rewards |
| O18 | Savage Labyrinth all 50 floors, rest/escape branches, floor-30 and floor-50 rewards; retain pre-entry save |
| O19 | Outset fairy, pig digging/carrying, Grandma soup, five dungeon Tingle statues if reachable in maintained Tingle Tuner workflow; record unsupported peripheral observations as gaps |
| O20 | Fortress third visit/changed enemies, remaining treasure/sea-chart salvages and Light Ring/Platform/Submarine chart routes; reconcile each marked reward on private chart checklist |

## Equipment, actions, enemies and effects

Each action row requires first use, at least three repeats, success and blocked/
empty-resource response where applicable. Show item acquisition, native menu
icon/assignment and visible effect. Upgrades not yet owned are explicit A
variants. Enemy rows require introduction, each attack/state, player hit/block,
defeat and drops where applicable; record actual encounter room and save. The
listed families include their encountered colors, armor/weapon and elemental
variants, recorded separately in the row's private variant checklist.

| ID | First cohort | Action/equipment variants |
| --- | --- | --- |
| Q01 | E | Walk/run/roll/crouch/crawl, ledge hang/climb/jump, ladder/rope, swim/splash/drown recovery |
| Q02 | E | Sword standing/combo/thrust/jump/spin/parry, shield raise/deflect; A: Master Sword power stages and Hurricane Spin |
| Q03 | E | Pick up/carry/throw/drop pots, rocks, barrels, sticks, enemy weapons; torch light/extinguish and breakage |
| Q04 | E | Telescope zoom, Picto Box aim/capture/album; A: Deluxe color/night/legendary photos |
| Q05 | E | Sail/boat start/stop/turn/jump, grappling salvage; M: cannon, A: cyclone travel and all treasure outcomes |
| Q06 | E | Wind Waker conducting, learned songs individually; M/L/A: each of six songs including command/day-night/warp and invalid melody |
| Q07 | E | Grappling hook swing/climb, enemy spoils stealing, failed target and salvage |
| Q08 | E | Bottles: empty/fairy/firefly/water/Forest Water/potions/soup, release/use/refill, expired water |
| Q09 | E | Deku Leaf fan/glide/landing/empty magic, updraft and wind direction |
| Q10 | E | Boomerang single/five-target, return/catch, obstruction and cut vines |
| Q11 | M | Bomb place/carry/throw/explode, bombable wall and cannon splash; empty bombs |
| Q12 | M | Bow draw/fire/aim/enemy impact; L/A: fire, ice and light arrows, thaw/shatter and empty magic/ammo |
| Q13 | L | Skull Hammer enemy/peg/obstacle effects; heavy carried enemy/rock with bracelets |
| Q14 | L | Iron Boots walk/fan resistance/spring launch, hookshot aim/pull/miss and heavy boots underwater where reachable |
| Q15 | L | Mirror Shield light beam, reflected enemy/light-arrow effects, dark-to-solid ChuChu |
| Q16 | E | Bait Bag scatter/seagull control; A: all merchant flowers/flags/statues and delivery/spoils quest items |
| Q17 | E | Damage/knockback/fire, recovery/hearts/rupees/spoils, fall/void/water/lava death, game over/continue; A: fairy revival, Hero's Charm and magic armor consumption |
| Q18 | L | Medli carry/fly/harp, Makar carry/fly/plant, Command Melody switch/return, companion capture/rescue |

| ID | First cohort | Enemy families and required variants |
| --- | --- | --- |
| F01 | E | Bokoblins (all colors/weapons), Miniblins, Moblins/searchlights/stealth detection |
| F02 | E | Keese and fire Keese; rats including bomb carriers; ChuChus red/green, later yellow/blue/dark variants in A |
| F03 | E | Magtails curled/open/fire, Kargarocs flying/carry, Peahats, Boko Babas |
| F04 | E | Morths attached/detached, Mothula winged/wingless, Octoroks land/sea |
| F05 | M | Armos/Armos Knights, Beamos, Wizzrobes normal/fire/summoning, Darknuts shields/armor/colors |
| F06 | L | Floor/Wallmasters, Poes possession/visible/light, ReDeads scream, Stalfos split/reform, red/blue Bubbles |
| F07 | A | Sharks, Seahats, Gyorgs, Big Octo eye counts, cannon boats/towers, explosive barrels, Cyclos |
| F08 | A | Mixed Labyrinth/cave waves, enemy weapons/pickups, all remaining encounter variants found on room checklists |

## Menus, world states, camera and targeted overlap

All rows below are A, except initial menu observations may reference S01.
Retain CP-L1 plus earlier pre-event backups. Each named variant is required;
unreachable combinations are documented with the reason and owner disposition.

| ID | Required bounded observations |
| --- | --- |
| N01 | Title/attract, file select, name entry, new/load/copy/erase confirmations on a disposable backed-up slot |
| N02 | Inventory/equipment, all owned item icons/assignment and descriptions, spoils/bait/delivery bags |
| N03 | Sea chart zoom, each special chart family, dungeon map/compass, treasure/Triforce charts and completed Triforce |
| N04 | Dialogue choices, purchases, rupee shortage, item-get, letter/mail and quest reward windows |
| N05 | Save confirmation/cancel/reload, game over/retry, credits and second-quest creation prompt |
| N06 | Wind Waker song UI, conducting meters, command switch and warp selection/cancel |
| N07 | Pictograph view/delete/album and Nintendo Gallery selection/figurine labels |
| N08 | Port preparation/progress, pause/settings/controls apply-discard, input disconnect/resume and normal Quit; preserve applied settings |
| V01 | Sea/town day, sunset, night and sunrise; Song of Passing separately, story storm pre/post Greatfish |
| V02 | Clear/rain/storm/lightning/cloud/fog conditions when normally encountered, rough/calm sea and cyclone approach |
| V03 | Pre/post fortress rescue NPCs, pre/post Greatfish, pearl/tower rise, Hyrule frozen/restored/barrier states |
| V04 | Camera close/far, overhead/low, wall occlusion, lock-on and first-person aim, indoors/outdoors/boat |
| V05 | Reflection/refraction water views, underwater camera transitions if reachable, sun/moon/sky silhouettes |
| V06 | Lava/fire/heat/smoke, ice/frozen/shatter, sand/wind/dust, foliage/grass cut and particles |
| V07 | Light/shadow, translucent/opaque surfaces, mirror beams, ghost/possession, boss monochrome/rematches |
| V08 | Low/full health/magic/ammo, item empty/refill, damage/invulnerability, fairy revival and game over |
| V09 | Every dungeon before/after switches/water levels/companion commands, shortcut warps opened, boss defeated/revisit |
| V10 | Door/cave/sea transition, scripted cutscene-to-control, dialogue-to-combat, loading and resume first frame |
| V11 | Town decorations, outfit original/second quest, fully upgraded sword/shield, carried enemy weapon and item attachment |
| V12 | Consecutive rooms/sea sectors with retained cache versus clean-candidate replay; shader waits and non-compilation stalls separate |
| X01 | Bomb smoke/explosion against breakable pots/grass with camera close to debris |
| X02 | Boat cannon blast plus water splash/sea enemy/projectile and moving camera |
| X03 | Torch/fire arrow plus foliage/fire enemy and smoke, including extinguishing |
| X04 | Ice arrow freezing plus shattering enemy/debris and nearby normal combat |
| X05 | Mirror light plus dark ChuChu/Poe or Jalhalla split particles and moving camera |
| X06 | Leaf wind/updraft plus foliage/particles and enemy projectiles |
| X07 | Storm/rain/lightning plus sailing, cannon splash and foreground island geometry where normally reachable |
| X08 | Lava/smoke plus grapple movement, falling debris and enemy fire in cavern/Gohma route |
| X09 | Companion command/fly/land plus temple fan/light effects and enemy combat |
| X10 | Mixed Labyrinth enemies/projectiles, sword/parry/spin, drops, damage and fairy recovery |

## Alternate playthroughs and remaining variations

Second quest begins only from the ordinary CP-CLEAR file, in a separate backed-up
slot. Repeat the same fixed E/M/L story route with the alternate outfit/dialogue
and camera/item observations; retain one-time pre-event saves again. Original
quest captures are reference material, not alternate-mode evidence.

| ID | A route and exit |
| --- | --- |
| A01 | Second quest title/file/name/prologue/Outset departure; exit S01 checkpoint |
| A02 | Second quest pirate/first fortress/Windfall; exit S04 checkpoint |
| A03 | Second quest Dragon Roost/cavern/Gohma; exit S06 checkpoint |
| A04 | Second quest Forest Haven/woods/Kalle Demos; exit CP-E1 equivalent |
| A05 | Second quest storm/pirates/Jabun/pearls; exit S10 equivalent |
| A06 | Second quest Tower/Hyrule/Master Sword; exit CP-M1 equivalent |
| A07 | Second quest fortress rescue/reveal/elemental equipment; exit S16 equivalent |
| A08 | Second quest both sages/temples/bosses/upgrades; exit S18 equivalent |
| A09 | Second quest Triforce routes and optional/gallery completion, all altered outfit/dialogue/pictograph states; exit CP-L1 equivalent |
| A10 | Second quest final Hyrule/Tower/rematches/Puppet Ganon/Ganondorf/credits; exit CP-A2 |

Reconcile the private 49-sector, dungeon-room, enemy-variant, eight-chart,
treasure-chart and gallery checklists before claiming full inventory coverage.
Their detailed observations are artifacts, not permission to silently add/remove
scope. A checklist gap stays `missing-observation`; an observed new pipeline is
`failed-coverage` until corrected and replayed. No row in this file currently
claims a physical pass or an accepted waiver.
