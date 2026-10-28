# New research prompts (2026-10-28)

Each prompt file is ONE step: paste it into a new chat, wait for the one text file it asks for, then send the next. Save the answer in `Bfa-8.3.7 Research/# Ai Research prompts` next to the older answers, in a folder named after the group with `-completed` at the end, and tell Claude; Claude cross-checks it against the client data before it is used.

Why these: the list of what is missing is `Dev/Sort-out/MISSING_AND_INCOMPLETE.txt`, the comparison with the playerbots guide is `modules/mod-psychobot/PLAYERBOTS-COMPARISON.md`. These prompts ask for what code cannot be written without: the content of the warfronts, the exact numbers of the Mythic+ affixes, the item lists, the dungeon routes and the scoreboard protocol.

Suggested order: Bots_Other/06 (the scoreboard) first, then MythicPlus_Affixes, then Bots_BiS_Per_Class and Bots_Other, and Warfronts last (the biggest project).


## Warfronts (7 prompts)

- `Warfronts/01_Stromgarde_Horde_Attack.txt`: the Battle for Stromgarde as the Horde attacker (map 1876, scenario 1346) in 8.3.7: every creature and object of the battle.
- `Warfronts/02_Stromgarde_Alliance_Attack.txt`: the Battle for Stromgarde as the Alliance attacker (map 1943, scenario 1568) in 8.3.7: every creature and object of the battle.
- `Warfronts/03_Darkshore_Alliance_Attack.txt`: the Battle for Darkshore as the Alliance attacker (map 2105, scenario 1697) in 8.3.7: every creature and object of the battle.
- `Warfronts/04_Darkshore_Horde_Attack.txt`: the Battle for Darkshore as the Horde attacker (map 2111, scenario 1701) in 8.3.7: every creature and object of the battle.
- `Warfronts/05_Troops_Buildings_Vehicles.txt`: the buildings, troops, heroes and vehicles of the warfronts of Battle for Azeroth 8.3.7.
- `Warfronts/06_Commanders_And_Bosses.txt`: the commanders and bosses of the warfronts of Battle for Azeroth 8.3.7: abilities and timings.
- `Warfronts/07_Contribution_And_Zone_Control.txt`: the contribution system and the zone control phase of the warfronts of Battle for Azeroth 8.3.7.

## Mythic+ affixes (6 prompts)

- `MythicPlus_Affixes/01_Reaping.txt`: the Reaping affix of Mythic+ (Battle for Azeroth season 2) as it worked in the 8.3.7 client.
- `MythicPlus_Affixes/02_Infested.txt`: the Infested affix of Mythic+ (Battle for Azeroth season 1) as it worked in the 8.3.7 client.
- `MythicPlus_Affixes/03_Beguiling.txt`: the Beguiling affix of Mythic+ (Battle for Azeroth season 3) as it worked in the 8.3.7 client.
- `MythicPlus_Affixes/04_Awakened.txt`: the Awakened affix of Mythic+ (Battle for Azeroth season 4) as it worked in the 8.3.7 client.
- `MythicPlus_Affixes/05_Obelisk_And_Emissary_Positions.txt`: where the Awakened obelisks and the Beguiling Emissaries stood in each dungeon of season 4 in 8.3.7.
- `MythicPlus_Affixes/06_Scaling_And_Rewards.txt`: the numbers of Mythic+ in 8.3.7: key level scaling, affix numbers and rewards.

## Best-in-slot per class (12 prompts)

- `Bots_BiS_Per_Class/01_Warrior.txt`: the best-in-slot gear of every Warrior specialization in Battle for Azeroth 8.3.7.
- `Bots_BiS_Per_Class/02_Paladin.txt`: the best-in-slot gear of every Paladin specialization in Battle for Azeroth 8.3.7.
- `Bots_BiS_Per_Class/03_Hunter.txt`: the best-in-slot gear of every Hunter specialization in Battle for Azeroth 8.3.7.
- `Bots_BiS_Per_Class/04_Rogue.txt`: the best-in-slot gear of every Rogue specialization in Battle for Azeroth 8.3.7.
- `Bots_BiS_Per_Class/05_Priest.txt`: the best-in-slot gear of every Priest specialization in Battle for Azeroth 8.3.7.
- `Bots_BiS_Per_Class/06_Death_Knight.txt`: the best-in-slot gear of every Death Knight specialization in Battle for Azeroth 8.3.7.
- `Bots_BiS_Per_Class/07_Shaman.txt`: the best-in-slot gear of every Shaman specialization in Battle for Azeroth 8.3.7.
- `Bots_BiS_Per_Class/08_Mage.txt`: the best-in-slot gear of every Mage specialization in Battle for Azeroth 8.3.7.
- `Bots_BiS_Per_Class/09_Warlock.txt`: the best-in-slot gear of every Warlock specialization in Battle for Azeroth 8.3.7.
- `Bots_BiS_Per_Class/10_Monk.txt`: the best-in-slot gear of every Monk specialization in Battle for Azeroth 8.3.7.
- `Bots_BiS_Per_Class/11_Druid.txt`: the best-in-slot gear of every Druid specialization in Battle for Azeroth 8.3.7.
- `Bots_BiS_Per_Class/12_Demon_Hunter.txt`: the best-in-slot gear of every Demon Hunter specialization in Battle for Azeroth 8.3.7.

## Other gaps of the bot module (6 prompts)

- `Bots_Other/01_Consumables.txt`: the consumables of Battle for Azeroth 8.3.7 for a computer-controlled character.
- `Bots_Other/02_PvP_Gear.txt`: the PvP gear of Battle for Azeroth 8.3.7 (season 4) for a computer-controlled character.
- `Bots_Other/03_Dungeon_Routes_A.txt`: the route through four dungeons of Battle for Azeroth 8.3.7: Atal'Dazar, Freehold, King's Rest, Shrine of the Storm.
- `Bots_Other/04_Dungeon_Routes_B.txt`: the route through four dungeons of Battle for Azeroth 8.3.7: Siege of Boralus, Temple of Sethraliss, The MOTHERLODE!!, The Underrot.
- `Bots_Other/05_Dungeon_Routes_C.txt`: the route through four dungeons of Battle for Azeroth 8.3.7: Tol Dagor, Waycrest Manor, Operation: Mechagon - Junkyard and Workshop.
- `Bots_Other/06_Scoreboard_Protocol.txt`: how the battleground scoreboard works in the 8.3.7 client and what a server must send for it to open.

Not asked on purpose: arena pillar coordinates and fixed positions around bosses (three earlier research rounds found no coordinates for them; the module finds cover by line of sight instead), bot professions (the owner decided against them for now).
