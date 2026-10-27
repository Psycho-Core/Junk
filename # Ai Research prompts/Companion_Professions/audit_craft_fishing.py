#!/usr/bin/env python3
"""Audit Craft_Fishing.txt - STEP 136.

Families: S title/headings, 1 skill lines/learn map, T trainers, R routes,
C cross/materials, M costs, 6 level, 7 TC lines, 8 cannot-do, 9 conflicts,
10 sources, H hygiene.
Each check is a plain substring containment on the payload text; every needle
must appear on a single line (wrap-safe). Self-test mutates the payload and
requires >= 1 failing check per mutation; each mutation literal must occur
exactly once in the payload.
"""
import sys
from pathlib import Path

PAYLOAD = Path(__file__).resolve().parent / "Craft_Fishing.txt"
CHECKS = []


def add(fam, *needles):
    for n in needles:
        CHECKS.append((fam, n))


# --- S: title, date, headings, scope verdict ------------------------------
add("S",
    "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - FISHING FOR A SERVER-SIDE COMPANION",
    "fetched this week (2026-10-27); anything without a readable source says",
    "levels Fishing on a TrinityCore-based 8.3.7 server. Short answer: it can - Fishing",
    "1. THE SKILL LINES AND HOW A COMPANION LEARNS THEM",
    "2. TRAINERS AND THEIR POSITIONS",
    "3. CHEAPEST ROUTE 1 TO THE CAP OF EACH LINE",
    "4. MATERIALS AND WHERE EACH COMES FROM",
    "5. TRAINER COSTS",
    "6. LEVEL NEEDED",
    "7. WHAT THE CORE MUST DO FOR A CRAFT TO SUCCEED",
    "8. WHAT A SERVER-SIDE CHARACTER (NO CLIENT) CANNOT DO",
    "9. CONFLICTS AND UNVERIFIED INDEX",
    "10. SOURCES",
    "the code itself labels \"guessed\".",
    )

# --- 1: skill lines and learn map ----------------------------------------
add("1",
    "Parent skill line: SKILL_FISHING = 356 (TrinityCore",
    "KUL_TIRAN_FISHING 2585, LEGION 2586,",
    "DRAENOR 2587, PANDARIA 2588, CATACLYSM 2589, NORTHREND 2590, OUTLAND 2591,",
    "CLASSIC 2592.",
    "\"Fishing skill progression is region-based, with separate",
    "skill levels for different expansion areas rather than a single global value.",
    "To begin fishing in a region, players must learn the appropriate skill from a",
    "(2018-07-17) row on the same page: \"Each expansion now has a separate",
    "gigantic profession skill bar for all expansions put together.\"",
    "271616 \"Fishing\"        300    none shown  8.0.1    no Taught-by table",
    "271656                  75     \"10\"        8.0.1    45 NPCs",
    "271658                  75     \"10\"        8.1.0    45 NPCs",
    "271660                  75     \"10\"        8.1.0    45 NPCs",
    "271662                  75     \"10\"        8.1.0    45 NPCs",
    "271664                  100    \"10\"        8.0.1    45 NPCs",
    "271672                  100    \"10\"        8.1.0    45 NPCs",
    "271675                  175    \"10\"        8.0.1    29 NPCs (A-side)",
    "271677                  175    \"10\"        8.1.0    23 NPCs (H-side)",
    "300068                  175    not captured 8.2.0   no Taught-by table",
    "- Spell 271616 tooltip: \"Allows for players to gather fish from bodies of water",
    "- Every other main prints \"Requires Fishing (1)\" plus \"Training cost: 10\" and",
    "- Spell 271677 (Zandalari) prints \"Faction: Horde\" and the flag \"Horde Specific",
    "2585 - the same shared-skill label bug as Craft_Tailoring/Craft_Cooking",
    "- Spell 300068 Abyssal Fishing: \"Added in patch 8.2.0 'Rise of Azshara'\",",
    "Fishing) Value: 2\" - the only Value-2 grant (section 9 item 1).",
    "- Wiki caps table (warcraft.wiki Fishing): Classic 1-300; Outland/Northrend/",
    "Cataclysm/MoP each 1-75; Draenor 1-100; Legion 1-100; BfA 1-175 (skill names",
    "600-750, Legion 750-900.",
    "section-5 cost, gain the sub-skill; then Player::GetProfessionSkillForExp",
    "(Player.cpp line 5874) selects which of the nine sub-skills a given",
    "expansion's fishing activity touches.",
    )

# --- T: trainers ----------------------------------------------------------
add("T",
    "Source: warcraft.wiki \"Fishing trainer\" page, full table read (6 chunks,",
    "Steven Stagnaro (N), Darkmoon Island [52.6, 88.6] - only",
    "Journeyman level. Available only to starting Goblins.",
    "Lee Brown (A), Crystal Lake, Elwynn Forest [47.5, 62.3]",
    "Paxton Ganter (A), Iceflow Lake, New Tinkertown [62.2, 38.3]",
    "Whilsey Bottomtooth (A), Stormglen, Gilneas - no",
    "Warg Deepwater (A), The Loch, Loch Modan [40.6, 39.5]",
    "Matthew Hooper (A), Lakeshire, Redridge [27.0, 50.1]",
    "Harold Riggs (A), Menethil Harbor, Wetlands [8.1, 58.5]",
    "Arnold Leland (A), The Canals, Stormwind [55.1, 69.5]",
    "Grimnur Stonebrand (A), The Forlorn Cavern, Ironforge",
    "Myizz Luckycatch (N), Booty Bay, Cape of Stranglethorn",
    "Clyde Kellen (H), Brightwater Lake, Tirisfal Glades",
    "Katoom the Angler (H), Revantusk Village, The Hinterlands",
    "Armand Cromwell (H), The Magic Quarter, Undercity",
    "Drathen (H, BC), Walk of Elders, Silvermoon [76.5, 67.8]",
    "Androl Oakhand (A), Rut'theran Village, Teldrassil [55.9, 93.5]",
    "Diktynna (A, BC), Ammen Ford, Azuremyst Isle [61.1, 54.2]",
    "\"Dirty\" Michael Crowe (A), Theramore, Dustwallow Marsh",
    "Brannock (A), Feathermoon Stronghold, Feralas [45.2, 41.4]",
    "Astaia (A), The Temple Gardens, Darnassus [47.6, 56.7]",
    "Erett (A, BC), The Crystal Hall, The Exodar [31.6, 14.8]",
    "[57, 50.5] - \"Teaches only up to Journeyman level.\"",
    "Lau'Tiki (H), Darkspear Strand, Durotar [53.2, 81.5]",
    "Uthan Stillwater (H), Stonebull Lake, Mulgore [44.5, 60.7]",
    "Kil'Hiwana (H), Zoram'gar Outpost, Ashenvale [10.9, 33.7]",
    "Lui'Mala (H), Shadowprey Village, Desolace [22.8, 72.4]",
    "Lumak (H), Valley of Honor, Orgrimmar [66.6, 41.6]",
    "Old Umbehto (H), Valley of Spirits, Orgrimmar [35.1, 67.4]",
    "Kah Mistrunner (H), High Rise, Thunder Bluff [56.1, 47.0]",
    "Old Man Barlo (N), Silmyr Lake, Terokkar Forest [38.6, 12.8]",
    "Juno Dufrain (N), Cenarion Refuge, Zangarmarsh [78.0, 65.3]",
    "Zurjaya (H), Zabra'jin, Zangarmarsh [32.3, 49.6]",
    "Old Man Robert (A), Valiance Keep, Borean Tundra [57.8, 71.6]",
    "Byron Welwick (A), Valgarde, Howling Fjord [60.3, 64.0]",
    "Fishy Ser'ji (H), Warsong Hold, Borean Tundra [41.8, 54.5]",
    "Angelina Soren (H), Vengeance Landing, Howling Fjord",
    "Northrend: Marcia Chase (N), The Eventide, Dalaran [52.8, 64.9]",
    "Ben of the Booming Voice (N), Halfhill, Valley of the Four Winds",
    "Nat Pagle (N), Anglers Wharf, Krasarang Wilds [68.3, 43.4]",
    "Master Lo (N), Peak of Serenity, Kun-Lai Summit [51.0, 40.2]",
    "Ron Ashton (A), Fishing Shack, Lunarfall [55.2, 15.8]",
    "Lester Scaleworth (A), Lunarfall Shipyard, Shadowmoon Valley (DR)",
    "Nuraa (A), Karabor, Shadowmoon Valley (DR) [66.8, 35.2]",
    "Austin Windmill (A), Stormshield, Ashran [55.6, 77.8]",
    "Mak'jin (H), Fishing Shack, Frostwall [38.6, 72.6]",
    "Sverre (H), Frostwall Shipyard, Frostfire Ridge [41.0, 73.8]",
    "Brix Rocketcast (H), Warspear, Ashran [69.6, 16.6]",
    "Broken Isles: Marcia Chase (N), The Eventide, Dalaran [52.6, 65.6]",
    "Conjurer Margoss (N), Margoss's Retreat, Dalaran - no",
    "Alan Goyle (A), Tradewinds Market, Boralus [74.2, 5.7]",
    "Akan (N), Anyport, Drustvar [20.0, 44.8]",
    "\"Flops\" Fizzlok (H), Krazzlefrazz Outpost, Drustvar [37.4, 24.8]",
    "Silent Tali (H), The Sliver, Dazar'alor [50.6, 23.2]",
    "EXCLUDED era rows the wiki also prints (post-8.3.7): Shadowlands - Retriever",
    "Au'prin, Hall of Shapes, Oribos [47.6, 24.0]",
    "[81.2, 31.4] / [81.0, 29.0]",
    "the six neutral-region mains (271656/58/60/62/64/72) each show 45 NPCs -",
    "the tables contain BOTH faction capitals (e.g. Alan Goyle Boralus and Armand",
    "Cromwell Undercity appear in the same list); 271675 shows 29; 271677 shows 23",
    "271616 renders no Taught-by section at all (section 9",
    "Distributor Ba'nacl, npc 244485, K'aresh, level 80.",
    "Trainer-page patch rows: 4.0.3a (2010-11-23) \"All trainer ranks equalized\";",
    "3.1.0 (2009-04-14) \"Old Man Heming no longer sells [Expert Fishing - The Bass",
    )

# --- R: route -------------------------------------------------------------
add("R",
    "- Skill gains only in the matching region: \"Skill is increased by fishing in",
    "that region\" (wiki), and wow-professions' Legion guide states it flatly:",
    "\"You can only level your Legion fishing at Broken Isle zones, you won't gain",
    "Legion Fishing skill if you fish elsewhere.\" TrinityCore implements this as:",
    "(GameObject.cpp line 2993 UpdateFishingSkill(areaContentTuning->ExpansionID))",
    "- The rate is hook-count-driven, identical in every zone of that region, and",
    "100*10 = always-take (Player.cpp lines 5519-5524). Consequence: choosing a",
    "junk catches still advance the bar (the wiki's 3.1.0 row: \"Every catch has",
    "the potential for fishing skill gains, but you are likely to catch worthless",
    "skill 1 gives TC-model hooks per cap: 1->75 = 74 hooks; 1->100 = 111 hooks;",
    "1->175 = 304 hooks; 1->300 = 919 hooks. These are TC-model numbers only,",
    "retail-actual counts are unverified (section 9 item 6).",
    "\"If you start from Legion Fishing skill 1, you need to catch around 180",
    "Fish to reach 100, which takes around 45 minutes\" and, with auction baits,",
    "you only have to do around 5 minutes of Fishing\"; its school-fishing loop -",
    "\"You can usually get 17-22 [Oodelfjisk] in 5 minutes, which means you will",
    "1-100 = 100 fish / 34 min at 3 fish/min, 100-200 = 160 / 54, 200-300 = 190 /",
    "64, 300-450 = 540 / 180, 450-600 = 825 / 260, totals ~1800 fish / ~600 min.",
    "1) Learn Classic Fishing (271616) at any trainer - it is the only main with",
    "2) For each further region: pay 10 at any trainer in section 2 for that",
    "3) Loot quality while below an area's skill level follows TC's chance =",
    "(player/area)^2 * 100 (minimum 1 percent) at GameObject.cpp 3001-3009;",
    "4) Legion shortcut as printed by wow-professions: train at Marcia Chase in",
    "5) Pools are friendlier than open water by loot, not by rate: \"Fishing pools",
    "have no skill requirement as of patch 3.3.0 (undocumented change)\"",
    "skips the chance roll entirely (line 3017 condition). Wiki extras read:",
    "6) Expect junk early in each new region - the wiki's skills section says",
    )

# --- C: materials ---------------------------------------------------------
add("C",
    "- Fishing Pole, id 6256, no skill bonus, \"Vendors\", req Fishing (1) (wiki",
    "- Strong Fishing Pole, id 6365, +5, req Fishing (10), min level 3, Vendors",
    "- Darkwood Fishing Pole, id 6366, +8, req Fishing (50), min level 7, \"(very",
    "- Big Iron Fishing Pole, id 6367, +10, req Fishing (100) per wiki poles",
    "step: unverified); the skill-2592 required-by page separately verifies",
    "Nat Pagle's Extreme Angler FC-5000 19022 and Nat's Lucky Fishing Pole",
    "- Arcanite Fishing Pole 19970, +14, \"Classic Fishing (300)\", Stranglethorn",
    "- Ephemeral Fishing Pole, +14, Garrison fishing, 1 Day duration, pre-BfA",
    "- Underlight Angler, +15, Legion Fish Frenzy [10-45], teleports to nearby",
    "- Powered Piscine Procurement Pole 168804, +15, req Fishing (1), source",
    "id, \"looted from Deepwater Maw\", \"Added in Battle for Azeroth\").",
    "12225 (+3, quest), Seth's",
    "Graphite 25978 (+10, Outland req, \"prior to BfA gave +20\"), Pandaren 84660",
    "- Glass Fishing Bobber 67404: +2, min 0, 10 min, racial capital dailies.",
    "- Shiny Bauble 6529: +3, min 0, 10 min, Vendors (50c).",
    "- Aquadynamic Fish Lens 6811: +5, min 50, 10 min, Stendel's Bane (Westfall).",
    "- Nightcrawlers 6530: +5, min 50, 10 min, Vendors (1s), various undead.",
    "- Flesh Eating Worm 7307: +7, min 100, 10 min, Rotted One (Duskwood); id",
    "- Bright Baubles 6532: +7, min 100 (Classic fishing), 10 min, Vendors",
    "- Aquadynamic Fish Attractor 6533: +9, min 100 (Classic fishing), 10 min,",
    "- Sharpened Fish Hook 34861: +9, min 1 (Outland fishing), 10 min, Outland",
    "- Glow Worm 46006: +9, min 1 (Northrend fishing), 60 min, Northrend dailies.",
    "- Feathered Lure 62673: +9, min 75 (Cataclysm fishing), 10 min, wiki source",
    "    Item Enhancements (Temporary) category. Added in World of Warcraft:",
    "- Day-Old Darkmoon Doughnut 124674: +10, min 1, 10 min, Darkmoon Faire.",
    "- Heat-Treated Spinning Lure 68049: +10, min 1 (Cataclysm fishing), 15 min,",
    "    Engineering; Craft_Engineering.txt line 381 records the craft as spell",
    "- Worm Supreme 118391: +10, min 100 (Draenor fishing), 10 min, Draenor",
    "- Rule from wiki Fishing_lure: \"Only one lure can be used at a time,",
    "Reinforced Fishing Line +1 (Stendel's Bane); Spun Truesilver Fishing Line",
    "Dalaran chance + STV Extravaganza; id also on wowhead",
    "Head - Darkmoon Fishing Cap +5 (summons Shipwreck Debris, Darkmoon",
    "STV); Boots of the Bay +10 (min 1 Northrend, STV); Anglin' Art's Sandals /",
    "Glove enchants - Formula: Enchant Gloves - Fishing +2 (murlocs",
    "E) Consumables (wiki): Captain Rumsey's Lager +5 for 3 min (Cooking recipe);",
    "\"Fragrant\" Pheromone Fish +5, expires after 1 min (Draenor Fishing).",
    "Arcane Lure 139175 - \"Increases the chance to catch bait items in the Broken",
    "School-reveal pairs with ids from the guide's own links: Rusty",
    "Queenfish Brooch 133704 (buff spell 201807, 5 min, reveals Ghostly Queenfish",
    "133727 schools in Azsuna); Ancient Vrykul Ring 133715 (buff spell 201818,",
    "24110 (Stormheim), Runescale Koi 124111 (Suramar),",
    "Black Barracuda 124112 (Great Sea), Coldriver Carp 133732 (guide quote:",
    "Currency ids are from the AdiBags \"Fishing Friends Currency\" list (section",
    "9 item 11).",
    )

# --- M: costs -------------------------------------------------------------
add("M",
    "- The nine mains' wowhead Quick Facts as printed: \"Training cost: 10\" on",
    "271656, 271658, 271660, 271662, 271664, 271672, 271675 and 271677.",
    "Classic 271616 prints NO cost line at all; Abyssal 300068: no cost line was",
    "quick-facts line - unverified (section 9 item 8), same convention as",
    "1s, journeyman 5s, expert 1g, artisan 2g50s, master 10g, grand master 15g,",
    "illustrious 25g, zen master 30g, Draenor master from the \"Fishing Guide to",
    "None of these are spendable on 8.3.7 - history only.",
    "- Vendor prices for gear, where printed: Shiny Bauble 50c, Nightcrawlers 1s,",
    "Bright Baubles 2s50c, Aquadynamic Fish Attractor 2s50c (wiki lures table);",
    )

# --- 6: level needed ------------------------------------------------------
add("6",
    "- The profession learn itself: no character level is printed in the Quick",
    "Facts of any of the nine mains (wowhead pages read) - unverified whether",
    "8.3.7 adds one. Every main except Classic 271616 prints \"Requires Fishing",
    "(1)\" - a skill requirement on the BASE skill, not a character level (same",
    "levels - Strong Fishing Pole 3, Darkwood Fishing Pole 7; skill reqs Fishing",
    "10 / 50 respectively; Big Iron req 100;",
    "player requirements): Alan Goyle 60 (Boralus), Arnold Leland 5-90",
    "Classic-era level gates seen only in era-flagged material: \"reach level 5",
    "and find a Fishing trainer\" (wow-professions classic guide, search snippet,",
    )

# --- 7: TC core lines -----------------------------------------------------
add("7",
    "src/server/shared), HEAD dc5955decd1be4877cbecad03bb41164d57014c8 - master",
    "moved from 209d6d51d1 (the HEAD named in the First Aid/Cooking/LW/Tailoring",
    "a) Identity and selection: SKILL_FISHING 356 (SharedDefines.h 5939);",
    "sub-skill map 6155-6162; Player::GetProfessionSkillForExp (Player.cpp",
    "b) Cast and bobber spawn: SpellEffects.cpp case GAMEOBJECT_TYPE_FISHINGNODE",
    "to be usable\" -> SetChannelObject(0, bobberGuid) line 4553, AddGameObject",
    "4559-4564: lastSec = urand(0,2) -> 3 / 7 / 13 seconds; catch-window end",
    "math line 4567: duration = min(duration, duration - lastSec*ms +",
    "(GameObject.h line 170, \"5 sec for bobber catch\"); destination",
    "TARGET_DEST_CASTER_FISHING = 39 (SharedDefines.h 2999).",
    "c) Hook handling: GameObject.cpp case GAMEOBJECT_TYPE_FISHINGNODE (17) line",
    "2960 in Use(): owner check lines 2966-2967 (only the caster may click);",
    "UpdateFishingSkill(area expansion) line 2993; areaFishingLevel =",
    "playerFishingSkill =",
    "irand(1,100) line 3001; chance = 100, or if player < area,",
    "(player/area)^2 * 100 floored at 1 (lines 3002-3009); pool lookup",
    "LookupFishingHoleAround(20.0f + CONTACT_DISTANCE) line 3013; pass =",
    "\"chance >= roll || fishingPool\" line 3017 (with the comment \"Fishing pools",
    "have no skill requirement as of patch 3.3.0 (undocumented change)\" lines",
    "3015-3016) -> pool->Use() or GetFishLoot + SendLoot lines 3026-3033; fail",
    "-> GetFishLootJunk + SendLoot line 3038; any other loot state (clicked too",
    "early / wrong state) -> FishNotHooked packet line 3048",
    "(WorldPackets::GameObject::FishNotHooked, SMSG_FISH_NOT_HOOKED,",
    "d) Skill-up arithmetic: GetFishingStepsNeededToLevelUp (Player.cpp 5491):",
    "comment line 5493 \"These formulas are guessed to be as close as possible",
    "to how the skill difficulty curve for fishing was on Retail\"; <75 -> 1",
    "(5494-5495), <=300 -> skill/44 (5497-5498), else skill/31 (5500).",
    "Player::UpdateFishingSkill(int32 expansion) line 5503: skill resolve",
    "5507, HasSkill guard 5508, max-skill guard 5513-5514, ++m_fishingSteps",
    "5517, reset + UpdateSkillPro(fishingSkill, 100*10,",
    "CONFIG_SKILL_GAIN_GATHERING) lines 5519-5524. UpdateSkillPro line 5531:",
    "bonusSkillLevels[] = {75,150,225,300,375,450,525,600,700,850} line 5535;",
    "crossing one calls LearnSkillRewardedSpells (lines 5574-5581) - rank",
    "e) Loot generation: GameObject::GetFishLoot line 1860 and GetFishLootJunk",
    "line 1883: both walk areaId -> areaEntry->ParentAreaID until the template",
    "LOOT_MODE_JUNK_FISH) with",
    "LOOT_FISHING and",
    "LOOT_FISHING_JUNK = 22 (Loot.h line 114, commented \"unsupported by client,",
    "sending LOOT_FISHING instead\"); LOOT_MODE_JUNK_FISH = 0x8000",
    "(SharedDefines.h line 82). Loot intake: LootHandler.cpp lines 292-300 -",
    "f) World data the core reads: skill_fishing_base_level loaded at",
    "ObjectMgr.cpp line 8948 (\"SELECT entry, skill FROM",
    "skill_fishing_base_level\", empty-table log 8952, orphan area error 7985,",
    "missing area error 8967); GetFishingBaseSkillLevel (ObjectMgr.cpp 7971)",
    "g) Related enums: SPELL_FAILED_FISHING_TOO_LOW = 227 (SharedDefines.h 1940);",
    "LOCKTYPE_FISHING = 19 (4920, mapped to SKILL_FISHING at 6277);",
    "QUEST_SORT_FISHING = 101 (5654, mapped to SKILL_FISHING at 6363).",
    )

# --- 8: cannot-do ---------------------------------------------------------
add("8",
    "- See or hear the splash. The wiki tips (read this step): \"As of patch 2.2,",
    "each cast of fishing will result in a bobber splash; the splash can occur",
    "when there are approximately 17, 13, 7, or 3 seconds left of the Fishing",
    "channeled spell\", plus its gallery caption \"Wait patiently for up to 19",
    "seconds before clicking the bobber\". TC server side randomizes its own",
    "window (3/7/13 s lead, 5 s ready time - section 7b). A headless companion",
    "UI to watch, and the exact 8.3.7 live window versus TC's",
    "- Aim the cast. The wiki's school technique is pure client play: \"always cast",
    "into the circle of the school or at its edge... re-cast your line at any",
    "only checks whether a pool GO exists within",
    "20yd + CONTACT (GameObject.cpp 3013). Pool positions live on the map/minimap",
    "- Client conveniences the wiki lists: right-click/auto-loot behavior, first-",
    "- World-DB contents: which fish/items each area's LootTemplates_Fishing row",
    "can drop, where lures/poles are sold, vendor prices beyond the printed ones",
    "in section 4, and the numeric skill_fishing_base_level per area - none of",
    "- Event and reputation content behind materials: Stranglethorn Fishing",
    "Extravaganza and the Darkmoon Faire schedules (hats, Arcanite pole,",
    "Pagle exalted gear. A server-side character can hold the items and use",
    "- Time-gated loops are borderline: Legion's 5-minute school buffs and the",
    "wiki's 18:00-00:00 nocturnal window are computable from the in-game clock,",
    )

# --- 9: conflicts ---------------------------------------------------------
add("9",
    "1) Abyssal tier semantics: spell 300068 (8.2.0) grants Kul Tiran Fishing with",
    "2) Spell 271677 (Zandalari, Horde) Effect reads \"Learn Skill (Kul Tiran",
    "3) Classic main 271616 renders no \"Taught by\" table and no cost line on",
    "4) Is a pole required? warcraft.wiki patch 5.0.4 row: \"Fishing no longer",
    "5) Which spell is the action button? Candidates on wowhead's skill-356 list",
    "6) Skill-up counts: TC model 74/111/304/919 hooks (section 3, formula labeled",
    "7) Splash window values: wiki tips 17/13/7/3 s left (patch 2.2 row), gallery",
    "8) Cost currency unit: wowhead quick facts print the bare number \"10\" with",
    "9) Era mixing on source pages: the wiki trainer table includes Shadowlands",
    "10) Shiny Bauble name collision: lure item 6529 (+3, vendor 50c) vs the",
    "11) Id provenance: pole/lure ids not present on any wiki page read (wiki item",
    "12) Rank-era annotations still on the wiki trainer table: KTC Train-a-Tron",
    "13) Feathered Lure learnability: wiki lists source \"1 Cataclysm Cooking\"",
    "14) Method dead ends (recorded so they are not retried): wowhead",
    "subcategory spell URLs (spells=11.356 and the fishing-skill-ranks",
    "271666 / 271654 resolve to unrelated spells (Light of the Loa, Crab, Maw",
    )

# --- 10: sources ----------------------------------------------------------
add("10",
    "All pages fetched 2026-10-27; nothing fetched is stored in the repository.",
    "Fishing (13; official blurb, how-to (channel ~21 s, splash click, shallow",
    "Fishing Journal, pools (about five fish), Find Fish via Weather-Beaten",
    "lures table, Legion bait table, fishing apparel + glove formulas,",
    "patch changes 8.0.1 -> 0.6, See also, external link skill 356,",
    "oldid 6784755, category \"Outdated articles\")",
    "Fishing trainer (6; full table reproduced in section 2, darkmoon through",
    "Zandalar rows with coordinates, KTC/Whilsey annotations, 4.0.3a and 3.1.0",
    "Fishing_lure / Template:Fishing_lures / Category:Fishing_lures (search",
    "271616 Fishing (Classic main; no cost/no taught-by; See also 13 list),",
    "271664 Draenor, 271672 Legion, 271677 Zandalari (Horde flag, label bug),",
    "skill 2592 Classic Fishing (Required by (9): 6367, 6532, 6533, 7307,",
    "19022, 19971, 19970, 45858, 45991)",
    "item 62673 Feathered Lure (search result page text: crafted, Item",
    "Legion Fishing Leveling Guide 1-100 (full page read: trainer Marcia Chase",
    "npc 95844, \"won't gain skill elsewhere\", zone-fish item ids,",
    "cast/learn spell mapping searches: 7731 as the Fishing cast across",
    "wowhead variants; wowdb 131474; 271675/271677 taught-by counts; the",
    "addon_supported_items.md), FishermansFriend poleIDs comment (WowAce),",
    "TrinityCore (clone #6, blobless sparse, HEAD",
    "Cross-references inside this repo: Craft_First_Aid.txt (document format,",
    "Craft_Engineering.txt line 381 (Heat-Treated Spinning Lure spell",
    "84430), Craft_Tailoring.txt (conflict 15 label-bug precedent).",
    )


# --- H: hygiene -----------------------------------------------------------
def hygiene(text):
    lines = text.split("\n")
    problems = []
    if any(ord(c) > 127 for c in text):
        problems.append("non-ascii")
    if any(len(l) > 100 for l in lines):
        problems.append("line > 100 cols")
    if any(l != l.rstrip() for l in lines):
        problems.append("trailing whitespace")
    if not lines[0].startswith("BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - FISHING"):
        problems.append("bad title")
    for i in range(1, 11):
        if not any(l.startswith(f"{i}. ") for l in lines):
            problems.append(f"missing section {i}")
    if "unverified" not in text:
        problems.append("no unverified marker")
    if "Short answer: it can - Fishing" not in text:
        problems.append("missing scope verdict line")
    return problems


def load():
    return PAYLOAD.read_bytes().decode("ascii")


def run_checks(text):
    return [(fam, n) for fam, n in CHECKS if n not in text]


MUTATIONS = [
    ("fetched this week (2026-10-27); anything without a readable source says",
     "fetched this week (2026-10-26); anything without a readable source says"),
    ("9. CONFLICTS AND UNVERIFIED INDEX", "9. CONFLICTS AND UNVERIFIED INDEY"),
    ("Parent skill line: SKILL_FISHING = 356 (TrinityCore",
     "Parent skill line: SKILL_FISHING = 357 (TrinityCore"),
    ("CLASSIC 2592.", "CLASSIC 2593."),
    ("271664                  100    \"10\"        8.0.1    45 NPCs",
     "271664                  101    \"10\"        8.0.1    45 NPCs"),
    ("Lee Brown (A), Crystal Lake, Elwynn Forest [47.5, 62.3]",
     "Lee Brown (A), Crystal Lake, Elwynn Forest [47.6, 62.3]"),
    ("Lumak (H), Valley of Honor, Orgrimmar [66.6, 41.6]",
     "Lumak (H), Valley of Honor, Orgrimmar [66.7, 41.6]"),
    ("271675 shows 29; 271677 shows 23", "271675 shows 28; 271677 shows 23"),
    ("1->175 = 304 hooks", "1->175 = 305 hooks"),
    ("catch around 180", "catch around 181"),
    ("17-22 [Oodelfjisk]", "17-23 [Oodelfjisk]"),
    ("id 6365, +5, req Fishing (10)", "id 6365, +6, req Fishing (10)"),
    ("Shiny Bauble 6529: +3", "Shiny Bauble 6529: +4"),
    ("Worm Supreme 118391: +10", "Worm Supreme 118391: +11"),
    ("Coldriver Carp 133732 (guide quote:", "Coldriver Carp 133733 (guide quote:"),
    ("\"Training cost: 10\" on", "\"Training cost: 11\" on"),
    ("artisan 2g50s", "artisan 2g60s"),
    ("Strong Fishing Pole 3, Darkwood Fishing Pole 7",
     "Strong Fishing Pole 4, Darkwood Fishing Pole 7"),
    ("Alan Goyle 60 (Boralus)", "Alan Goyle 61 (Boralus)"),
    ("SetChannelObject(0, bobberGuid) line 4553",
     "SetChannelObject(0, bobberGuid) line 4554"),
    ("(GameObject.h line 170, \"5 sec for bobber catch\")",
     "(GameObject.h line 171, \"5 sec for bobber catch\")"),
    ("irand(1,100) line 3001; chance = 100, or if player < area,",
     "irand(1,100) line 3002; chance = 100, or if player < area,"),
    ("{75,150,225,300,375,450,525,600,700,850} line 5535",
     "{75,150,225,300,375,450,525,600,700,850} line 5536"),
    ("SPELL_FAILED_FISHING_TOO_LOW = 227 (SharedDefines.h 1940)",
     "SPELL_FAILED_FISHING_TOO_LOW = 228 (SharedDefines.h 1940)"),
    ("approximately 17, 13, 7, or 3 seconds left",
     "approximately 18, 13, 7, or 3 seconds left"),
    ("20yd + CONTACT (GameObject.cpp 3013)", "21yd + CONTACT (GameObject.cpp 3013)"),
    ("3) Classic main 271616 renders no \"Taught by\" table",
     "3) Classic main 271617 renders no \"Taught by\" table"),
    ("6) Skill-up counts: TC model 74/111/304/919 hooks",
     "6) Skill-up counts: TC model 74/111/304/920 hooks"),
    ("Fishing trainer (6; full table reproduced in section 2, darkmoon through",
     "Fishing trainer (7; full table reproduced in section 2, darkmoon through"),
    ("oldid 6784755", "oldid 6784756"),
]


def self_test():
    original = load()
    total_pass = 0
    for rnd in (1, 2):
        results = []
        for i, (old, new) in enumerate(MUTATIONS, 1):
            if original.count(old) != 1:
                results.append((i, False, f"old literal count={original.count(old)}"))
                continue
            mutated = original.replace(old, new, 1)
            if mutated == original:
                results.append((i, False, "mutation no-op"))
                continue
            fails = run_checks(mutated)
            results.append((len(fails) >= 1, len(fails)))
        bad = [r for r in results if r[0] is not True]
        npass = len(MUTATIONS) - len(bad)
        total_pass += npass
        print(f"self-test round {rnd}: {npass}/{len(MUTATIONS)} {'PASS' if not bad else 'FAIL'}")
        for r in bad:
            print(f"  mutation {r}")
    print(f"self-test total: {total_pass}/{len(MUTATIONS) * 2}")
    return total_pass == len(MUTATIONS) * 2


def main():
    text = load()
    fails = run_checks(text)
    fams = {}
    for fam, needle in CHECKS:
        fams[fam] = fams.get(fam, 0) + 1
    print(f"checks: {len(CHECKS) - len(fails)}/{len(CHECKS)} PASS, {len(fails)} FAIL")
    print("families: " + " ".join(f"{k}-{v}" for k, v in fams.items()))
    h = hygiene(text)
    print("hygiene: " + ("PASS (ascii, <=100 cols, no trailing ws, 10 sections)"
                         if not h else f"FAIL {h}"))
    if fails:
        for fam, n in fails[:40]:
            i = text.find(n[:24]) if n[:24] in text else -1
            ctx = repr(text[max(0, i - 60):i + 90]) if i >= 0 else "NOT FOUND (no partial)"
            print(f"  FAIL [{fam}] {n!r}\n        ctx={ctx}")
        sys.exit(1)
    if h:
        sys.exit(1)
    if "--self-test" in sys.argv:
        ok = self_test()
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
