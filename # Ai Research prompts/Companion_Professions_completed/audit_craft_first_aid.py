#!/usr/bin/env python3
"""Audit Craft_First_Aid.txt - STEP 135.

Families: S section/totals, L removal+learn map, T trainers, R routes,
C cross/materials, M costs, 6 level, 7 TC lines, 8 cannot-do, 9 conflicts,
10 sources, H hygiene.
Each check is a plain substring containment on the payload text; every needle
must appear on a single line (wrap-safe). Self-test mutates the payload and
requires >= 1 failing check per mutation.
"""
import sys
from pathlib import Path

PAYLOAD = Path(__file__).resolve().parent / "Craft_First_Aid.txt"
CHECKS = []


def add(fam, *needles):
    for n in needles:
        CHECKS.append((fam, n))


# --- S: title, date, headings, printed totals ----------------------------
add("S",
    "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - FIRST AID CRAFTING FOR A SERVER-SIDE COMPANION",
    "(2026-10-27); anything without a readable source says \"unverified\" instead of being",
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
    "3.0 There is no First Aid route on 8.3.7: the line has no 1, no cap and no skill",
    "3.1 Classic 1-300 (guide: vanilla-tailoring-leveling; the whole route is bandages;",
    "3.2 Outland 1-75 (guide: outland-tailoring-leveling; bandage recipes from the",
    "3.3 Northrend 1-75 (guide: northrend-tailoring-leveling; bandages from Olisarra",
    "3.4 Cataclysm 1-75 (guide: cataclysm-tailoring-leveling; bandages from Jessara",
    "3.5 Pandaria bandage steps (guide: pandaria-tailoring-leveling; the route also prints",
    "3.6 Draenor bandage step (guide: draenor-tailoring-leveling; the rest of that route -",
    "3.7 Legion bandage steps (guide: legion-tailoring-leveling; the route's gear steps",
    "3.8 BfA 1-60 (guide: zandalari-kul-tiran-bfa-tailoring-leveling)",
    "Bandage crafts printed = 315 (55 + 30 + 55 + 20 + 45 + 20 + 30 + 20 + 30 + 10 -",
    "Bandage crafts printed = 145 (45 + 100); Netherweave 245 = 45 + 200 exact.",
    "Bandage crafts printed = 110 (20 + 90); Frostweave 200 = 20 + 180 exact.",
    "Bandage crafts printed = 105 (25 + 80); Embersilk 185 = 25 + 160 exact.",
    "Bandage crafts printed = 95 (25 + 70); bandage cloth = 165 (25 + 140 exact; the",
    "Main-route bandage crafts = 150 (fur 750 = 150 x 5 exact); alternative = 40 (fur",
    "Bandage crafts printed = 110 (55 + 55); silk 330 = 55 + 275 exact; Leystone 55.",
    "Bandage crafts printed = 100; Tidespray 200 = 100 x 2 exact.",
    "BANDAGE-TOTAL: 315 + 145 + 110 + 105 + 95 + 150 + 110 + 100 = 1130 crafts (main",
    "Draenor step; running the 40-craft Draenor alternative instead: 1020). Every addend",
    "is a printed count. The caps each segment climbs to (300 / 75 / 75 / 75 / 75 / 100 /",
    )

# --- L: removal evidence, skill lines, learn map -------------------------
add("L",
    "Headline: there is NO First Aid skill line in 8.3.7. Nothing to train, no skill points",
    "Azeroth. Bandage crafting was moved to Tailoring, while consumable liquids were",
    "patch row \"Patch 8.0.1 (2018-07-17): Removed. First Aid recipes are now",
    "made with Tailoring due to the removal of First Aid.",
    "Azeroth, First Aid is no longer available on Retail realms. Making bandages is now",
    "Blizzard has confirmed the removal of First Aid",
    "with the exception of First Aid. Tailoring and Alchemy crafts, bandages, and",
    "anti-venoms that used to be in First Aid will have to be re-learned.\"",
    "anti-venoms \"such as Strong Anti-Venom\" (links",
    "spell 7935) classified as Alchemy, First Aid achievements moved to Legacy.",
    "will be removed from the game, and with the removal of First Aid, many of those",
    "TrinityCore master HEAD 209d6d51d1 (fresh blobless sparse clone of src/server/game",
    "grep SKILL_FIRST_AID = 0 hits; the SkillLine",
    "enum (Miscellaneous/SharedDefines.h) jumps SKILL_RACIAL_NIGHT_ELF 126 (line 5886)",
    "to SKILL_STAVES 136 (line 5887) with no 129 entry. Exactly five first-aid names",
    "ItemTemplate.h:658      ITEM_SUBCLASS_FIRST_AID_MANUAL = 7    (recipe subclass)",
    "SharedDefines.h:5575    QUEST_INFO_FIRST_AID_WORLD_QUEST = 114",
    "SharedDefines.h:5670    QUEST_SORT_FIRST_AID = 324",
    "QuestDef.h:130          QUEST_TRSKILL_FIRSTAID = 6            (QuestTradeSkill)",
    "ScriptedGossip.h:41     TRADESKILL_FIRSTAID = 6               (eTradeskill; file",
    "lives at src/server/game/AI/ScriptedAI/ScriptedGossip.h)",
    "Linen Bandage \"Skill: Classic Tailoring\"; spell 267201 Tidespray Linen Bandage",
    "\"Skill: Kul Tiran Tailoring\"; both skill-up/Recipes tables link Tailoring",
    "on 3275 - section 9 item 4.",
    "spell 7934 Anti-Venom quick facts \"Skill:",
    "Classic Alchemy\" (Taught by 12 Alchemy trainers - section 9 item 3); spell 160329",
    "spell 160329's effect renders \"Learn Skill Step (129)",
    "Value: 9\" on wowhead; wowpedia marks First Aid in Draenor Deprecated (8.0.1). No",
    "8.3.7 client DB2 ships SkillRaceClassInfo/SkillTiers rows for 129 at all (section",
    "(Craft_Tailoring.txt section 1: base spell 3908 plus sub-skills 2533-2540, bandage",
    "Antiseptic Bandage 172539 -> Tailoring,",
    "Alchemy (1 Tailoring, 3 Alchemy).",
    )

# --- T: trainers (wiki table + guide sources) ----------------------------
add("T",
    "A) Historical First Aid trainers (warcraft.wiki First_Aid_trainers, full table read).",
    "The table ends at Pandaria - no Draenor, Legion or BfA rows (the same coverage gap",
    "Doc Zapnozzle (H), Shipwreck Shore / Wild Overlook /",
    "Amelia Atherton (Cata), Duskhaven, Gilneas, no coordinate",
    "Thamner Pol, Kharanos, Dun Morogh [47.2, 52.6]",
    "Michelle Belle, Goldshire, Elwynn Forest [43.4, 65.6]",
    "Fremal Doohickey, Menethil Harbor, Wetlands [10.8, 61.3]",
    "Angela Leifeld, Cathedral Square, Stormwind [52.9, 44.8]",
    "Nissa Firestone, The Great Forge, Ironforge [54.9, 58.5]",
    "Nurse Neela, Brill, Tirisfal Glades [61.8, 52.8]",
    "Kanaria (BC), Falconwing Square, Eversong Woods [48.5, 47.6]",
    "Alestus (BC), Walk of Elders, Silvermoon City [77.6, 71.3]",
    "Mary Edras, The Rogues' Quarter, Undercity [73.5, 54.8]",
    "Byancie, Dolanaar, Teldrassil [55.3, 56.8]",
    "Anchorite Fateema (BC), Azure Watch, Azuremyst Isle [48.5, 51.8]",
    "Anchorite Paetheus (BC), Blood Watch, Bloodmyst Isle [54.7, 54]",
    "Doctor Gustaf VanHowzen, Theramore, Dustwallow Marsh [67.6, 48.8]",
    "Dannelor, Craftsmen's Terrace, Darnassus [51.7, 30.4]",
    "Nus (BC), The Crystal Hall, The Exodar [39, 22.5]",
    "Rawrk, Razor Hill, Durotar [54.1, 42]",
    "Vira Younghoof, Bloodhoof Village, Mulgore [46.8, 60.8]",
    "Doc Zapnozzle, Bilgewater Harbor, Azshara [57, 50.5]",
    "Krenk Choplimb, Goblin Slums, Orgrimmar [37.0, 87.2]",
    "Pand Stonebinder, Spirit Rise, Thunder Bluff [29.4, 21.5]",
    "Burko, Temple of Telhamat, Hellfire Peninsula [22.4, 39.3]",
    "Aresella, Falcon Watch, Hellfire Peninsula [26.3, 62]",
    "Anchorite Ensham, Sha'tari Base Camp, Terokkar Forest [30.8, 75.9]",
    "Fera Palerunner, Thunderlord Stronghold, Blade's Edge [53.7, 55]",
    "Mildred Fletcher, Lower City, Shattrath City [66.5, 13.5]",
    "Brynna Wilson, Valiance Keep, Borean Tundra [57.8, 66.4]",
    "Anchorite Yazmina, Valgarde, Howling Fjord [59.7, 62.1]",
    "Nurse Applewood, Warsong Hold, Borean Tundra [41, 54]",
    "Sally Tompkins, Vengeance Landing, Howling Fjord [79, 29]",
    "Olisarra the Kind, First to Your Aid / Magus Commerce Exchange,",
    "Joseph Wilson, Argent Tournament Grounds, Icecrown [71.5, 22.5]",
    "Soraka, Paw'don Village, Jade Forest [45.5, 85.8]",
    "Mishka, \"Various\", no coordinate printed",
    "Healer Nan, Emperor's Step, Shrine of Seven Stars [45.6, 62.6]",
    "Elder Muur, Honeydew Village, Jade Forest [28.2, 15.2]",
    "Ala'thinel, Chamber of Masters, Shrine of Two Moons [29.1, 74.8]",
    "Apothecary Cheng, Binan Village, Kun-Lai Summit [71.6, 92.8]",
    "Master Bier, Peak of Serenity, Kun-Lai Summit [51.0, 40.2]",
    "B) What teaches bandage recipes on 8.3.7 (ids as printed by the wow-professions",
    "Mender Jessara npc 133109 / Krenk Choplimb npc 45540 in Orgrimmar",
    "Pand Stonebinder npc 2798 in Thunder Bluff) /",
    "the bookcase behind Loremaster Skosiris npc 33642 in Shattrath, or",
    "Mildred Fletcher npc 19184 (guide pin 66.6, 13.4, upstairs right)",
    "Aresella npc 18991 (H, Falcon Watch) / Burko npc 18990 (A, Temple",
    "Olisarra the Kind npc 28706 (house left of the tailoring trainer) or",
    "Nurse Applewood npc 29233 [41.6, 54.4] / Brynna Wilson npc 26992 [57.8, 66.2] /",
    "Sally Tompkins npc 26956 [79.4, 29.4] / Anchorite Yazmina npc 23734 [59.8, 62.2].",
    "Ala'thinel npc 65862 (H, Shrine of Two Moons) / Healer Nan npc 64482",
    "Olisarra the Kind npc 93529 (Dalaran, guide pin); wowhead labels her",
    "and Anchorite Lysara npc 126022 \"Bandage Trainer\".",
    "BfA: NO separate bandage trainers - wowhead's Taught by (4) table on 267201 is",
    "Daniel Brineweaver npc 136071 (Boralus,",
    "Instructor Alikana npc 153817 (Nazjatar,",
    "Jada npc 154321 (Nazjatar, level 50, H,",
    "10-60, H, <Tailoring Trainer>).",
    "teaches a \"First Aid\" profession: the profession train option does",
    )

# --- R: route steps, historical caps, anti-venoms -------------------------
add("R",
    "  - 1 - 50: 55 x Linen Bandage spell 3275 (55 Linen Cloth)",
    "  - 50 - 80: 30 x Heavy Linen Bandage spell 3276 (60 Linen Cloth)",
    "  - 80 - 130: 55 x Wool Bandage spell 3277 (55 Wool Cloth)",
    "  - 130 - 150: 20 x Heavy Wool Bandage spell 3278 (40 Wool Cloth)",
    "  - 150 - 190: 45 x Silk Bandage spell 7928 (45 Silk Cloth)",
    "  - 190 - 210: 20 x Heavy Silk Bandage spell 7929 (40 Silk Cloth)",
    "  - 210 - 240: 30 x Mageweave Bandage spell 10840 (30 Mageweave Cloth)",
    "  - 240 - 260: 20 x Heavy Mageweave Bandage spell 10841 (40 Mageweave Cloth)",
    "  - 260 - 290: 30 x Runecloth Bandage spell 18629 (30 Runecloth Cloth - the guide",
    "  - 290 - 300: 10 x Heavy Runecloth Bandage spell 18630 (20 Runecloth Cloth)",
    "  - 1 - 40: 45 x Netherweave Bandage spell 27032 (45 Netherweave Cloth)",
    "  - 40 - 75: 100 x Heavy Netherweave Bandage spell 27033 (200 Netherweave Cloth;",
    "  - 1 - 20: 20 x Frostweave Bandage spell 45545 (20 Frostweave Cloth)",
    "  - 20 - 75: 90 x Heavy Frostweave Bandage spell 45546 (180 Frostweave Cloth;",
    "  - 1 - 25: 25 x Embersilk Bandage spell 74556 (25 Embersilk Cloth)",
    "  - 25 - 75: 80 x Heavy Embersilk Bandage spell 74557 (160 Embersilk Cloth;",
    "  - 10 - 25: 25 x Windwool Bandage spell 102697 (25 Windwool Cloth)",
    "  - 25 - 60: 70 x Heavy Windwool Bandage spell 102698 (140 Windwool Cloth; \"green",
    "  - 2 - 50: 150 x Antiseptic Bandage spell 172539 (750 Sumptuous Fur; \"green for the",
    "  - ALTERNATIVE 1 - 25: 40 x Antiseptic Bandage 172539 (200 Sumptuous Fur; \"yellow,",
    "  - 1 - 30: 55 x Silkweave Bandage spell 202853 (55 Shal'dorei Silk)",
    "  - 60 - 90: 55 x Silkweave Splint spell 202854 (275 Shal'dorei Silk, 55 Leystone",
    "  - 1 - 60: 100 x Tidespray Linen Bandage spell 267201 (200 Tidespray Linen; guide:",
    "initial cap 75 (\"Once learned, players",
    "then as printed - skill 50 raises potential to 150; 125 -> 225; 225 -> 300; 300 ->",
    "375 (Master, BC); 350 -> 450 (Grand Master, WotLK); 425 -> 525 (Illustrious Grand",
    "Master, Cata); 525 -> 600 (MoP); the \"First Aid in Draenor\" recipe 160329 -> 700;",
    "Legion rows run 730 / 750 / 760 / 800 (Silvery Salve + Stabilize, Treat Burns,",
    "800 skill points in first aid\" (wow-professions) - so the removed line's final cap",
    "Death knights begin with 270 First Aid skill ... knowledge of trainer-taught recipes",
    "Craft counts for a pure-First-Aid historical route were never printed by",
    "x3 spell 7934 at First Aid 80 from 1 Small Venom Sac; Strong Anti-Venom x3 at 130",
    "from 1 Large Venom Sac (spell 7935, id from wowhead's news link; learned from",
    "Venom Sac (Formula: sold by the Argent Dawn at Honored for 10g; spell id",
    )

# --- C: materials and cross-checks ---------------------------------------
add("C",
    "Cloth ids (all guide-linked or directly probed during the audited Craft_Tailoring",
    "Cloth 4306, Mageweave Cloth 4338, Runecloth 14047, Netherweave Cloth 21877",
    "Frostweave Cloth 33470 (probe), Embersilk Cloth 53010, Windwool Cloth 72988,",
    "Sumptuous Fur 111557 (id from wowhead's reagent link on spell 172539), Shal'dorei",
    "Silk 124437 (guide link), Tidespray Linen 152576 (probe), Leystone Ore 123918 (id",
    "This step's own probes re-confirmed",
    "50; Outland 245; Northrend 200; Cataclysm 185; Pandaria 165 (guide full-route list",
    "main-route total 2250 includes the 1500 behind Hexweave Embroidery); Legion 330 silk",
    "shopping list 590 includes the robe, satin and embroidery steps).",
    "Anti-venom reagents: Small Venom Sac 1475 (direct probe of spell 7934), Large Venom",
    "Per craft: 1 cloth for the light bandages, 2 for every heavy variant (the wiki",
    "(275/55 and 55/55 both exact); Tidespray Linen Bandage 2 (200/100 exact); Anti-Venom",
    )

# --- M: trainer costs -----------------------------------------------------
add("M",
    "First Aid 1s, Journeyman 5s, Expert 10s, Artisan 2g50s, Master (BC) 10g, Grand",
    "Master 15g, Illustrious Grand Master 25g. Recipe learn prices as printed: Linen",
    "Bandage free (\"instantly learned when learning First Aid\"), Heavy Linen 1s,",
    "Netherweave 2g, Heavy",
    "training fee of 10 coppers\" - against the recipes table's Apprentice 1s: section 9",
    "\"Training cost: 10\" and",
    "its trainer box \"Profession Trainer: Battle for Azeroth Tailoring (1) / Cost: 10\"",
    "Classic-era bandage recipe",
    "trainer money = MoneyCost x reputation discount,",
    "FailReason::NotEnoughMoney, ModifyMoney deduction.",
    )

# --- 6: level needed ------------------------------------------------------
add("6",
    "First Aid learn itself: nothing - no spell, no character level, no skill (removed).",
    "for any rank; \"level 1 players can advance First Aid skill up to 225\"; Death",
    "knights began at First Aid 270; Manual: Heavy Frostweave Bandage \"requires a First",
    "Aid skill of 390 to learn or use\" - pre-8.0.1 rows only.",
    "Tidespray Linen Bandage item 158381 prints \"Requires Level 40\"",
    "\"individual types only limited by level requirements for use\".",
    "level 10\" pre-Shadowlands row on wowpedia's Profession page is a 9.0.1 change -",
    "Bandage trainer NPC levels (wowhead 267201 Taught by table): 60 / 50 / 50 / 10-60.",
    "prints \"Tailoring (40)\"; the number's exact meaning is not explained on the page:",
    )

# --- 7: TC core lines -----------------------------------------------------
add("7",
    "HandleTrainerListOpcode -> 112 SendTrainerList",
    "HandleTrainerBuySpellOpcode (GUID check at 137,",
    "Trainer.cpp 41 SendSpells (reputation discount 43,",
    "76 TeachSpell -> 79 CanTeachSpell",
    "106 ModifyMoney(-moneyCost); 172",
    "Spell.cpp 3869 TakePower() then 3872 TakeReagents() before",
    "ITEM_FLAG_NO_REAGENT_COST 0x10000000 (ItemTemplate.h 218), and",
    "Player::CanUseItem(ItemTemplate) at Player.cpp 11184 reading",
    "proto->GetRequiredSkill() at 11203-11208 (skill 0 -> EQUIP_ERR_PROFICIENCY_NEEDED,",
    "CanRollNeedForItem at 11245 / 11267, transmog-set and enchant checks at",
    "Player.cpp 5410 UpdateCraftSkill -> blocked by",
    "SPELL_ATTR1_NO_SKILL_INCREASE (5412-5413); reads the spell's SkillupSkillLineID",
    "CONFIG_SKILL_GAIN_CRAFTING (5433) and returns",
    "MECHANIC_DISCOVERY (5427) calls GetSkillDiscoverySpell + LearnSpell (5429-5430).",
    "SkillChance.Orange 100 / Yellow 75 / Green 25 / Grey 0,",
    "SkillGain.Crafting default 1. For bandages the SkillupSkillLineID is",
    "GetSkillRaceClassInfo(skillid, race, class) must exist (guard 2419-2421) and a",
    "SkillTiers row must exist (guard 2423-2425), else the effect returns; SetSkill is",
    "EffectTradeSkill's body is a NO-OP",
    "e) Create item: EffectCreateItem dispatch SpellEffects.cpp 116 -> EffectCreateItem",
    "1473 with SPELL_ATTR0_IS_TRADESKILL -> ItemContext::Trade_Skill at 1478 (further",
    "SKILL_TAILORING = 197 (SharedDefines.h 5911); the Tailoring",
    "sub-skills SKILL_KUL_TIRAN_TAILORING 2533 .. SKILL_CLASSIC_TAILORING 2540 live",
    "QUEST_TRSKILL_TAILORING = 10 (QuestDef.h 134); IsProfessionSkill =",
    "No GameObject focus and no focus",
    "almost anywhere, as long as you have the appropriate ingredients - cloth (for",
    "item 1251's Use is spell 746 (\"first-aid\",",
    "item 158381's Use is spell 267198 (\"first-aid\",",
    "anti-venom item 6452's Use is spell 7932",
    "any damage - direct, DoT, or even damage absorbed by a shield - cancels",
    "Recently Bandaged blocks re-use for 60 seconds (warcraft.wiki Bandage and",
    )

# --- 8: cannot-do items ---------------------------------------------------
add("8",
    "Train First Aid, gain one First Aid skill point, or reach any First Aid cap:",
    "Make skill 129 appear via relic spells: 160329 would early-return inside",
    "Follow any published \"First Aid 1-300 / 1-450 / 1-800\" guide on this server:",
    "Click profession-window buttons: crafts must be cast by spell id with the",
    "Talk to the trainers in section 2 at all: every bandage NPC, the four BfA",
    "Re-learn First Aid crafts automatically on a fresh character: Blizzard's own",
    "Craft anti-venoms under a First Aid assumption: on 8.3.7 they are Alchemy",
    "Earn the removed First Aid achievements or the Field Medic title:",
    "Reliably obtain the world-drop teachers: Manual: Strong Anti-Venom (rare world",
    "Use a bandage whenever it likes (if the companion uses them at all): spell",
    "Read complete trainer coverage from the wiki: First_Aid_trainers stops at",
    )

# --- 9: conflicts and unverified -----------------------------------------
add("9",
    "1) Removal vs residues: every current source says removed (section 1 chain) while",
    "2) Price of the old learn: wiki First_Aid prose \"a small training fee of 10 coppers\"",
    "3) Anti-Venom identity split: spell 7934 quick facts \"Skill: Classic Alchemy\" plus",
    "4) Linen Bandage identity split (= Craft_Tailoring conflict 15): quick facts \"Skill:",
    "5) Wiki recipes table provenance: its own note says \"The info in this list was",
    "6) Wiki trainers table ends at Pandaria: no Draenor, Legion or BfA rows at all, and",
    "7) \"First Aid in Draenor\" 160329: description \"Teaches you Draenor Master First Aid",
    "8) Route counts: the guides print zero First Aid counts (the line is gone); the",
    "9) Wiki skill table vs live skill links: the wiki First_Aid guide lists Antiseptic",
    "10) Two Olisarras: the wiki's Dalaran row [37.5, 36.7] is the Northrend-era npc",
    "11) Krenk Choplimb appears with npc 45540 in the Orgrimmar guide and with only a",
    "12) 267201 cost prints \"Training cost: 10\" in quick facts and \"Cost: 10\" inside the",
    "13) TC drift note: section 7 was re-read from master HEAD 209d6d51d1, the same HEAD",
    "14) Tidespray bandage heal print: item 158381 via spell 267198 reads \"Heals 4",
    "15) Anti-venom ids: 7934 from a direct probe, 7935 from the link inside wowhead",
    "Also unverified (not guessed): whether the 8.3.7 client DB2 ships skill 129 rows",
    )

# --- 10: sources ----------------------------------------------------------
add("10",
    "All pages fetched 2026-10-27; nothing fetched is stored in the repository.",
    "First_Aid (4; removal banner + patch 8.0.1 row, official overview, full skill",
    "First_Aid_trainers (4; full table read: The Maelstrom through Pandaria, all rows",
    "First_Aid_recipes (3; Learn/Yellow/Green/Gray colors, reagents, trainer prices,",
    "Bandage (1; Tailoring-since-BfA sentence, 60-second cooldown, channeled effect",
    "3275 Linen Bandage (Skill: Classic Tailoring, label \"Profession: First Aid (1)\",",
    "160329 First Aid in Draenor (added 6.0.1, 10 sec cast, \"Teaches you Draenor",
    "267201 Tidespray Linen Bandage (Training cost 10, Skill: Kul Tiran Tailoring,",
    "7934 Anti-Venom (Skill: Classic Alchemy, Training cost 4, box labels",
    "wowhead news 282901 \"Clarifications on First Aid Removal in Battle for Azeroth\"",
    "wow-professions news \"BFA Pre-Expansion Patch 8.0.1 - Profession Changes\" (1",
    "Craft_Tailoring.txt section 2 (bandage-trainer ids), sections 3.1-3.8 (guide",
    "audit 560/560 PASS this week.",
    "Craft_Cooking.txt section 7 (shared TC anchor pattern at the same HEAD).",
    "HEAD 209d6d51d1; anchors re-read this step: grep SKILL_FIRST_AID",
    "= 0 hits; the five enums (ItemTemplate.h 658, SharedDefines.h 5575/5670, QuestDef.h",
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
    if not lines[0].startswith("BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - FIRST AID"):
        problems.append("bad title")
    for i in range(1, 11):
        if not any(l.startswith(f"{i}. ") for l in lines):
            problems.append(f"missing section {i}")
    if "unverified" not in text:
        problems.append("no unverified marker")
    if "3.0 There is no First Aid route on 8.3.7" not in text:
        problems.append("missing route verdict line")
    return problems


def load():
    return PAYLOAD.read_bytes().decode("ascii")


def run_checks(text):
    return [(fam, n) for fam, n in CHECKS if n not in text]


MUTATIONS = [
    ("(2026-10-27); anything without a readable source says", "(2026-10-26); anything without a readable source says"),
    ("Bandage crafts printed = 315 (55 + 30 + 55 + 20 + 45 + 20 + 30 + 20 + 30 + 10 -",
     "Bandage crafts printed = 316 (55 + 30 + 55 + 20 + 45 + 20 + 30 + 20 + 30 + 10 -"),
    ("grep SKILL_FIRST_AID = 0 hits; the SkillLine", "grep SKILL_FIRST_AID = 1 hits; the SkillLine"),
    ("QuestDef.h:130          QUEST_TRSKILL_FIRSTAID = 6            (QuestTradeSkill)",
     "QuestDef.h:130          QUEST_TRSKILL_FIRSTAID = 7            (QuestTradeSkill)"),
    ("\"Skill: Kul Tiran Tailoring\"; both skill-up/Recipes tables link Tailoring",
     "\"Skill: Kul Tiran Tailrining\"; both skill-up/Recipes tables link Tailoring"),
    ("Thamner Pol, Kharanos, Dun Morogh [47.2, 52.6]", "Thamner Pol, Kharanos, Dun Morogh [47.3, 52.6]"),
    ("10-60, H, <Tailoring Trainer>).", "10-61, H, <Tailoring Trainer>)."),
    ("Mildred Fletcher npc 19184 (guide pin 66.6, 13.4, upstairs right)",
     "Mildred Fletcher npc 19184 (guide pin 66.7, 13.4, upstairs right)"),
    ("  - 80 - 130: 55 x Wool Bandage spell 3277 (55 Wool Cloth)",
     "  - 80 - 130: 56 x Wool Bandage spell 3277 (55 Wool Cloth)"),
    ("  - 2 - 50: 150 x Antiseptic Bandage spell 172539 (750 Sumptuous Fur; \"green for the",
     "  - 2 - 50: 150 x Antiseptic Bandage spell 172539 (751 Sumptuous Fur; \"green for the"),
    ("375 (Master, BC); 350 -> 450 (Grand Master, WotLK); 425 -> 525 (Illustrious Grand",
     "375 (Master, BC); 350 -> 450 (Grand Master, WotLK); 425 -> 526 (Illustrious Grand"),
    ("x3 spell 7934 at First Aid 80 from 1 Small Venom Sac; Strong Anti-Venom x3 at 130",
     "x3 spell 7934 at First Aid 81 from 1 Small Venom Sac; Strong Anti-Venom x3 at 130"),
    ("Sumptuous Fur 111557 (id from wowhead's reagent link on spell 172539), Shal'dorei",
     "Sumptuous Fur 111558 (id from wowhead's reagent link on spell 172539), Shal'dorei"),
    ("50; Outland 245; Northrend 200; Cataclysm 185; Pandaria 165 (guide full-route list",
     "50; Outland 245; Northrend 200; Cataclysm 185; Pandaria 166 (guide full-route list"),
    ("First Aid 1s, Journeyman 5s, Expert 10s, Artisan 2g50s, Master (BC) 10g, Grand",
     "First Aid 1s, Journeyman 6s, Expert 10s, Artisan 2g50s, Master (BC) 10g, Grand"),
    ("its trainer box \"Profession Trainer: Battle for Azeroth Tailoring (1) / Cost: 10\"",
     "its trainer box \"Profession Trainer: Battle for Azeroth Tailoring (1) / Cost: 11\""),
    ("Bandage trainer NPC levels (wowhead 267201 Taught by table): 60 / 50 / 50 / 10-60.",
     "Bandage trainer NPC levels (wowhead 267201 Taught by table): 60 / 51 / 50 / 10-60."),
    ("Tidespray Linen Bandage item 158381 prints \"Requires Level 40\"",
     "Tidespray Linen Bandage item 158381 prints \"Requires Level 41\""),
    ("Player.cpp 5410 UpdateCraftSkill -> blocked by", "Player.cpp 5411 UpdateCraftSkill -> blocked by"),
    ("SKILL_TAILORING = 197 (SharedDefines.h 5911); the Tailoring",
     "SKILL_TAILORING = 197 (SharedDefines.h 5912); the Tailoring"),
    ("Recently Bandaged blocks re-use for 60 seconds (warcraft.wiki Bandage and",
     "Recently Bandaged blocks re-use for 70 seconds (warcraft.wiki Bandage and"),
    ("Follow any published \"First Aid 1-300 / 1-450 / 1-800\" guide on this server:",
     "Follow any published \"First Aid 1-300 / 1-450 / 1-900\" guide on this server:"),
    ("Make skill 129 appear via relic spells: 160329 would early-return inside",
     "Make skill 129 appear via relic spells: 160330 would early-return inside"),
    ("3) Anti-Venom identity split: spell 7934 quick facts \"Skill: Classic Alchemy\" plus",
     "3) Anti-Venom identity split: spell 7935 quick facts \"Skill: Classic Alchemy\" plus"),
    ("6) Wiki trainers table ends at Pandaria: no Draenor, Legion or BfA rows at all, and",
     "6) Wiki trainers table ends at Draenor: no Legion or BfA rows at all, and"),
    ("First_Aid_trainers (4; full table read: The Maelstrom through Pandaria, all rows",
     "First_Aid_trainers (5; full table read: The Maelstrom through Pandaria, all rows"),
    ("= 0 hits; the five enums (ItemTemplate.h 658, SharedDefines.h 5575/5670, QuestDef.h",
     "= 0 hits; the six enums (ItemTemplate.h 658, SharedDefines.h 5575/5670, QuestDef.h"),
]


def self_test():
    original = load()
    total_pass = 0
    for rnd in (1, 2):
        results = []
        for i, (old, new) in enumerate(MUTATIONS, 1):
            if old not in original:
                results.append((i, False, "old literal missing"))
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
