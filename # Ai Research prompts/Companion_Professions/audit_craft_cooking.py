#!/usr/bin/env python3
"""Audit Craft_Cooking.txt - STEP 134.

Families: S section, L learn map, T trainers, R routes, C cross/materials,
M costs, 6 level, 7 TC lines, 8 cannot-do, 9 conflicts, 10 sources, H hygiene.
Each check is a plain substring containment on the payload text; every needle
must appear on a single line (wrap-safe). Self-test mutates the payload and
requires >= 1 failing check per mutation.
"""
import sys
from pathlib import Path

PAYLOAD = Path(__file__).resolve().parent / "Craft_Cooking.txt"
CHECKS = []


def add(fam, *needles):
    for n in needles:
        CHECKS.append((fam, n))


# --- S: title, date, headings, totals -----------------------------------
add("S",
    "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - COOKING CRAFTING FOR A SERVER-SIDE COMPANION",
    "fetched this week (2026-10-27); anything without a readable source says \"unverified\"",
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
    "Format:  - A - B: N x Craft Name spell id (materials the guide prints). Counts are",
    "3.1 Classic 1-300 (guide: vanilla-cooking-leveling; learn at any cooking trainer",
    "3.2 Outland 1-75 (guide: outland-cooking-leveling; learn from Allison 49789",
    "3.3 Northrend 1-75 (guide: northrend-cooking-leveling; learn from Awilo",
    "3.4 Cataclysm 1-75 (guide: cataclysm-cooking-leveling; learn from Arugi 46709",
    "3.5 Pandaria 1-75 (guide: pandaria-cooking-leveling; learn from Sungshin",
    "3.6 Draenor 1-100 (guide: draenor-cooking-leveling; learn the item 111387",
    "3.7 Legion 1-100 (guide: legion-cooking-leveling; learn from Awilo 93536 (H)",
    "3.8 BfA 1-175 (guide: zandalari-kul-tiran-bfa-cooking-leveling-guide; learn",
    "Total exact-count casts printed by the guide = 310 (60 + 40 + 30 + 50 + 50 +",
    "Total exact-count casts printed by the guide = 130 (30 + 40 + 60).",
    "Total crafts printed by the guide = around 90-95 (\"around 30-35\" + \"make",
    "Total crafts printed by the guide = around 95-110 (15 + about 20-25 + about",
    "Total exact-count casts printed by the guide = 65 (40 + 20 + 5).",
    "Total crafts printed by the guide = 146 step counts (30 + 66 + 45 + 5) with",
    "Total crafts printed by the guide = 55 + around 70-90 (plus the unquantified",
    "Total exact-count casts printed by the guide = 194 (34 + 15 + 25 + 80 + 15 +",
    )

# --- L: skill lines and learn map ---------------------------------------
add("L",
    "Base spell: Cooking 2550 - Training cost: 10, Difficulty: 111, Skill: Cooking",
    "Taught by (66).",
    "158765 (skill 1), 3102 (50), 3413 (125), 18260 (200), 33359 (275), 51296",
    "195128 (700).",
    "264632-264647, starting exactly",
    "264648 = \"Order Blast\", an 8.0.1 server-side",
    "there is NO internal gap. Eight main/wrapper pairs:",
    "main 264632 \"Classic Cooking\" (Learn Skill Classic Cooking skill=2548,",
    "cap 300) added 8.0.1, no Training-cost line, no Taught-by table rendered",
    "wrapper 264633 \"Cooking\" added 8.0.1 (the only wrapper not tagged 8.1.0 -",
    "Learn Spell 2550 + Learn Spell 264632 + Learn Skill Step",
    "(2548) Value 1; three effects, 100 yd range, See also (16).",
    "main 264634 \"Outland Cooking\" (skill=2547, cap 75, cost 10, 8.0.1, Taught",
    "by 7), wrapper 264635 (8.1.0): Learn Spell 264634 + Step 2547.",
    "main 264636 \"Northrend Cooking\" (skill=2546, cap 75, cost 10, 8.0.1, Taught",
    "by 5), wrapper 264637 (8.1.0): Learn 264636 + Step 2546.",
    "main 264638 \"Cataclysm Cooking\" (skill=2545, cap 75, cost 10, 8.0.1, Taught",
    "by 27), wrapper 264639 (8.1.0): Learn 264638 + Step 2545.",
    "main 264640 \"Pandaria Cooking\" (skill=2544, cap 75, cost 10, 8.0.1, Taught",
    "by 2), wrapper 264641 (8.1.0): Learn 264640 + Step 2544 (Related shows only",
    "main 264642 \"Draenor Cooking\" (skill=2543, cap 100) added 8.0.1, no",
    "wrapper 264643 (8.1.0): Learn 264642 + Step 2543 - Triggered by (1) spell",
    "main 264644 \"Legion Cooking\" (skill=2542, cap 100, cost 10, added 8.0.1,",
    "Taught by 2), wrapper 264645 (8.1.0): Learn 264644 + Step 2542 (Related",
    "main 264646 \"Kul Tiran Cooking\" (skill=2541, cap 175, cost 8, added 8.0.1,",
    "\"Alliance Specific Spell\", Taught by 4), wrapper 264647 (8.1.0):",
    "main 265817 \"Zandalari Cooking\" (cap 175, cost 8, added 8.1.0, \"Horde",
    "Cooking skill=2541) Value 1 - the Horde spell carries the Alliance label and",
    "wrapper 265818 added 8.0.1 (section 9 item 5): Learn 265817 + Step 2541.",
    "2548 Classic 1-300, 2547 Outland 1-75, 2546",
    "Northrend 1-75, 2545 Cataclysm 1-75, 2544 Pandaria 1-75, 2543 Draenor 1-100,",
    "2542 Legion 1-100, 2541 BfA (Kul Tiran/Zandalari) 1-175. Every main except the",
    "Classic one prints \"Requires Cooking (1)\" in quick facts - the base skill 185",
    "item 111387 \"The Joy of Draenor Cooking\" (Book, iLvl 40,",
    "Requires Level 10, source printed \"Drop\")",
    "160360 \"Introduction to",
    "Cooking in Draenor\" (added 6.0.1, Item Effect, 10 sec cast, \"Tradeskill recipe\"",
    "flag, text \"Teaches you Draenor Cooking and a number of recipes\")",
    "Teaches (2) (the second taught spell's id was not rendered:",
    "guide agrees: \"Visit your trainer ... and learn Legion Cooking\"",
    "\"Kul Tiran Cooking\" 264646 is the Alliance version and",
    "difference\". Trainers: T'sarah the Royal Chef (H) and \"Cap'n\" Byron Mehlsack (A).",
    "264632 nor 264633 has a Taught-by table",
    "How skill 2548 reaches a fresh",
    "31281 \"So You Want to Be a Chef...\" (make 5 Sliced Peaches",
    "31302 \"Ready for Greatness\"",
    "31479 Way of the Brew (deliver 5 Ginseng to Bobo Ironpaw 58717)",
    "31470 Way of the Wok (Anthea Ironpaw)",
    "skill in any Way\" - one Way to 75 is enough (section 3.5 uses the cheapest).",
    "base spell 2550 is Taught by 66 creatures",
    )

# --- T: trainers and positions ------------------------------------------
add("T",
    "warcraft.wiki Cooking_trainers page (6 chunks; the table ENDS at Draenor - last",
    "row Guy Fireeye, Brokenspear Tavern, Warspear, NO coordinate - and the page sits",
    "KTC Train-a-Tron Deluxe, Town-In-A-Box/Sky Falls/Gallywix Docks, The Lost",
    "Gremlock Pilsnor, Kharanos, Dun Morogh [54.6, 50.6]",
    "Cook Ghilm, Gol'Bolar Quarry, Dun Morogh [75.6, 52.6]",
    "Tomas, Goldshire, Elwynn Forest [44.2, 66.0]",
    "Crystal Boughman, Lakeshire, Redridge Mountains [22.8, 40.6]",
    "Stephen Ryback, Old Town, Stormwind [77.2, 53.2]",
    "Daryl Riknussun, The Great Forge, Ironforge [60.1, 36.4]",
    "Mrs. Gant, Booty Bay, Cape of Stranglethorn [42.7, 72.7]",
    "The Chef, Brill, Tirisfal Glades [61.2, 52.6]",
    "Slagg, Hammerfall, Arathi Highlands [69.2, 34.4]",
    "Eunice Burch, The Trade Quarter, Undercity [62.8, 44.2]",
    "Zarrin, Dolanaar, Teldrassil [56.6, 53.6]",
    "Henry Stern, Razorfen Downs (NO coordinate)",
    "Dirge Quikcleave, Gadgetzan, Tanaris [52.6, 29.0]",
    "Aska Mistrunner, High Rise, Thunder Bluff [51.0, 53.0]",
    "Arugi, Borstan's Firepit/The Drag, Orgrimmar [56.2, 51.6]",
    "Marogg, The Drag, Orgrimmar [56.6, 62.6]",
    "Zamja, Valley of Spirits, Orgrimmar [57.5, 53.6]",
    "Gaston, Honor Hold, Hellfire Peninsula [54.0, 63.6]",
    "Allison, Thrallmar, Hellfire Peninsula [56.8, 37.4]",
    "Naka, Cenarion Refuge, Zangarmarsh [78.5, 63.0]",
    "Jack Trapper, Lower City, Shattrath City [63.5, 68.6]",
    "Kylene, Lower City, Shattrath City [75.5, 32.6] (Barmaid; wiki: \"Teaches",
    "Rollick MacKreel, Valiance Keep, Borean Tundra [57.8, 71.6]",
    "Katherine Lee, A Hero's Welcome, Dalaran [41.5, 64.6]",
    "Orn Tenderhoof, Warsong Hold, Borean Tundra [42.0, 54.2]",
    "Thomas Kolichio, Vengeance Landing, Howling Fjord [78.5, 29.4]",
    "Awilo Lon'gomba, Sunreaver's Sanctuary, Dalaran [70.0, 39.0]",
    "Chin, Dawn's Blossom, The Jade Forest [46.3, 45.2]",
    "Sungshin Ironpaw, Halfhill Market, Valley of the Four Winds [53.6, 51.2]",
    "Anthea Ironpaw [52.8, 51.8] (Way of the Wok), Kol Ironpaw [53.0, 51.4]",
    "Master Chang, Peak of Serenity, Kun-Lai Summit [50.6, 41.8]",
    "Guy Fireeye, Brokenspear Tavern, Warspear (NO coordinate; last wiki row).",
    "Awilo Lon'gomba npc 93536 (Legion Dalaran, H, NPC level 45) and",
    "Katherine Lee npc 93534 (Legion Dalaran, A, NPC level 10-45)",
    "Nomi npc 101846 runs the test kitchen next to them. Position:",
    "\"Cap'n\" Byron Mehlsack npc 136052, Boralus, level 60, A",
    "Ulooaka npc 154257, Nazjatar, level 50, A (guide: visible only",
    "T'sarah the Royal Chef npc 141549, Dazar'alor, level 60",
    "Howcha npc 141906, Dazar'alor, level 60",
    "154408, Nazjatar, level 50, H (intro quests gate visibility)",
    "Slagg npc 232031,",
    "Stacks npc 150632, Mechagon, level 60-90, Mechanical",
    "Derek Odds npc 31032 (A) and Misensi npc 31031 (H), Dalaran",
    "Shazdar npc 49737 (H, Orgrimmar) and Bario Matalli npc 49701",
    "Andrew Hilbert npc 3556 (H, Silverpine/The Sepulcher)",
    "Pusillin npc 14354 drops Recipe: Runn Tum Tuber Surprise 18267",
    "Cookie One-Eye npc 16585 (H) / Sid Limbardi npc 16826 (A)",
    "Xerintha Ravenoak npc 20916 (H, Blade's Edge, LIMITED supply - or quest",
    "npc 107379 (Azsuna, Wardens Revered - Recipe: Spiced Falcosaur Omelet",
    "Hanul Swiftgale npc 141936 (H) / Henrick Wyther npc 142095 (A)",
    "Collector Kojo npc 135793 (Tortollan Seekers",
    "Kabonka npc 340 (Stormwind)",
    )

# --- R: routes ------------------------------------------------------------
add("R",
    "60 x Spice Bread spell 37836 (60 Simple Flour 30817, 60 Mild",
    "40 x Smoked Bear Meat spell 8607 (40 Bear Meat - id unverified",
    "about 30 x Boiled Clams spell 6499 (30 Clam Meat - id",
    "then Crab Cake spell 2544 (1 Crawler",
    "50 x Curiously Tasty Omelet spell 3376 (50 Raptor Egg - id",
    "50 x Roast Raptor spell 15855 (50 Raptor Flesh - id",
    "25 x Monster Omelet spell 15933 (25 Giant Egg - id",
    "40 x Juicy Bear Burger spell 46688 (40 Bear Flank - id",
    "15 x Smoked Desert Dumplings spell 24801 (15 Sandworm Meat",
    "20424 from Dredge Strikers 11740 / Dredge Crushers 11741 in Silithus",
    "talk to Rhonormu",
    "Runn Tum Tuber Surprise spell (id unverified; recipe",
    "Pilgrim's Bounty event food",
    "30 x Ravager Dog spell 33284 (30 Ravager Flesh 27674",
    "Buzzard Bites (craft spell id unverified - the guide links food item 27651)",
    "40 x Talbuk Steak spell 33289 (40 Talbuk Venison 27682",
    "Roasted Clefthoof spell 33287 (40 Clefthoof Meat 27678",
    "40 x Warp Burger spell 33288 (40 Warped Flesh 27681",
    "60 x Crunchy Serpent spell 38868 (60 Serpent Flesh 31671)",
    "60 x Mok'Nathal Shortribs spell 38867 (60 Raptor Ribs 31670)",
    "around 30-35 meats/fish cooked with the recipes the trainer",
    "Kungaloosh spell 53056 (quest 13571 via Washed-Up Mage 32516",
    "Spiced Mammoth Treats 57440, Tracker Snacks 57443, Blackened Worg Steak",
    "Firecracker Salmon 45568, Imperial Manta Steak",
    "Spicy Fried Herring 57433",
    "each also costs 1",
    "Northern Spices 43007 per craft) bought for 3 Epicurean's Award (currency",
    "15 x Darkbrew Lager (craft spell id unverified - the guide links",
    "30 Skin of Dwarven Stout 2596, 15 Jug of Bourbon",
    "Lightly Fried Lurker 65412 (Striped Lurker",
    "Pickled Guppy 65417 (Highland",
    "Baked Rockfish 65426 (Algaefin",
    "Blood Shrimp 62791 from Abyssal Clam 52340 dropped by most Vashj'ir mobs.",
    "Way of the Brew learn: quest 31479 - deliver 5 Ginseng 74845 to Bobo",
    "40 x Ginseng Tea spell 124052 (40 Ginseng 74845)",
    "20 x Jade Witch Brew spell 124053 (100 Jade Squash 74847,",
    "5 x Banquet of the Brew spell 125602 (5 100 Year Soy Sauce",
    "Grill spells 104298/104299/125141, Oven 104310/104311/125600,",
    "the book can drop from any humanoid mob at Draenor... after 20-30 kills",
    "30 x Grilled Saberfish spell 161002 (150 Crescent Saberfish",
    "Flesh 109137 - probe: 5 per craft; output \"Recipe for 4 servings",
    "Fat Sleeper Cakes 160981 + Braised",
    "Skulker Chowder 160983 +",
    "Sturgeon Stew 160979 + Pan-Seared Talbuk",
    "Blackrock Barbecue",
    "Feast of the Waters spell 173979",
    "Feast of Blood spell 173978",
    "Nomi 101846 offers quest 40988",
    "each work order takes 5 ingredients",
    "and 4 HOURS, may teach a recipe, often yields Badly Burnt Food 133913",
    "55 x Rank 2 Salt and Pepper Shank spell 201524 (275 Lean Shank",
    "124117, 110 Flaked Sea Salt 133588, 110 Dalapeno Pepper 133589 - guide's",
    "Azshari Salad 201555, Crispy Bacon 201685,",
    "Magister 201554",
    "cook around 70-90\" of ONE rank 2 recipe (rank 1 greys at 80,",
    "Spiced Falcosaur Omelet item 142331 from Marin Bladewing 107379 at Azsuna",
    "34 x Mon'Dazi spell 259442 (340 Wild Flour 160399, 170 Foosaka",
    "15 x Rank 2 - Kul Tiramisu spell 259412 (150 Wild Flour, 75",
    "25 x ONE of: Seasoned Loins spell 259433 (250 Stringy Loins",
    "Honey-Glazed Haunches 259414 (250 Meaty Haunch",
    "Sailor's Pie 259439 (250 Briny Flesh",
    "Seasoned Loins rank 2 spell 259434 (800 Stringy Loins,",
    "Sailor's Pie rank 2 spell 259440 (800 Briny",
    "15 x Rank 1 - Abyssal-Fried Rissole spell 297084 (120 Moist",
    "25 x Rank 2 - Abyssal-Fried Rissole spell 297085 (200 Moist",
    "rank 3 recipe items (optional): 162286 and 162295 from World",
    "Instructor Ulooaka 154257 at Nazjatar - \"finish the first few intro quest",
    "Quests \"Work Order: ...\", 162293 from Collector Kojo 135793",
    "last 10 points, so you might have to make more\"; the guide headline says",
    )

# --- C: cross-checks and materials --------------------------------------
add("C",
    "Origins below are the guide's own words or a probe result",
    "form came from a fresh wowhead spell/item page, ids in \"(link)\"",
    "Simple Flour 30817 (link, vendor), Mild Spices 2678 (link, vendor) -",
    "Sandworm Meat 20424 (link, farm Silithus",
    "Runn Tum Tuber 18255 (link, farm",
    "Ravager Flesh 27674 (link, farm), Buzzard Meat 27671 (link, farm)",
    "Venison 27682 (link, farm), Clefthoof Meat 27678 (link, farm)",
    "Serpent Flesh 31671 (link, farm), Raptor Ribs",
    "Northern Spices 43007 (link; 10 bought per Epicurean's Award 81 (link)",
    "Skin of Dwarven Stout 2596 (probe: cost 96-120 each, sold by 50 vendors),",
    "Ginseng 74845 x40, Jade Squash",
    "Sauce 74853 x5 (all links; \"You can buy Ginseng from Sungshin Ironpaw\"",
    "Crescent Saberfish Flesh 109137 (probe on 161002; fished fish -> flesh),",
    "other Draenor meat/fish id above (Fat Sleeper Flesh, Raw Riverbeast Meat,",
    "Dalapeno Pepper 133589 (probe) - both vendor reagents, Falcosaur",
    "Slice of Bacon 133680, Fatty Bearsteak 124118",
    "Wild Flour 160399, Choral Honey 160398, Powdered Sugar 160712,",
    "Aromatic Fish Oil 160711 (link; made from fish - the probe of 259442",
    "168302 + Mauve Stinger 168646 (links), Moist Fillet 168645 (link).",
    "Stringy Loins 154897, Meaty Haunch 154898, Briny Flesh 152631",
    "meats: Stringy Loins 154897",
    "100 Aromatic Fish Oil, 1050",
    "Cross-checks (re-derived from the printed steps):",
    "BfA meats: 250 + 800 = 1050 exact (Seasoned Loins path through both",
    "Moist Fillet: 120 + 200 = 320 exact",
    "68 + 30 = 98 <= shopping 100 (2 spare)",
    "Wild Flour steps: 340 + 150 + 75",
    "Foosaka 170 + 75 + 125 + 400 + 45 + 75 = 890 - both are",
    "55 crafts x 5/2/2 = 275 / 110 / 110 exact (guide totals)",
    "30 crafts x 5 = 150 Crescent Saberfish Flesh exact",
    "Classic: 60 + 60 exact for Spice Bread; Cata Darkbrew 30 + 15 exact for",
    "Midnight Salmon 162515",
    "Frenzied Fangtooth 152545, Lane Snapper 152546,",
    "Witchberries 74846 x350",
    )

# --- M: trainer costs ----------------------------------------------------
add("M",
    "Base spell 2550: \"Training cost: 10\"; mains with the same line: 264634,",
    "264636, 264638, 264640, 264644. BfA mains 264646 and 265817 print",
    "\"Training cost: 8\". Mains WITHOUT a training-cost line on their wowhead",
    "page: 264632 (Classic) and 264642 (Draenor, learned from the book); no",
    "Currency unit is not rendered on the pages -",
    "trainer money = MoneyCost x reputation",
    "\"Training cost:",
    "10\" and its box \"Profession Trainer: Classic Cooking (1) / Cost: 10\" (two",
    "each from Derek Odds/Misensi; Cataclysm recipes: \"One recipe usually costs",
    "Northern Spices: 10 for",
    "no gold prices are printed anywhere in",
    "Pandaria Way",
    "quests cost ingredient deliveries, not gold",
    )

# --- 6: level needed ------------------------------------------------------
add("6",
    "no character level printed on spell 2550 or on",
    "\"Req. 10\" printed in spell 160360's Used-by-Item row",
    "Mon'Dazi item \"Requires Level 45\", Rank 2 Salt and Pepper Shank item",
    "\"Requires Level 40\", Grilled Saberfish item",
    "\"Requires Level 35\".",
    "BfA: Byron 60, T'sarah 60, Howcha 60, Ulooaka 50,",
    "Rolm 50, Slagg 80, Stacks 60-90; Legion: Awilo 45, Katherine 10-45; MoP:",
    "Legion needs quests 40988/40989 + 40990 (learn 6 recipes)",
    "Uniting Kul Tiras 51918 /",
    "Character levels for these were not printed: unverified",
    "a Cata-classic daily guide (warcrafttavern, search",
    "Outland dailies need level 70 and Northrend dailies level 71",
    "Salt and",
    "Pepper Shank rank 1 \"Cooking (20)\", Mon'Dazi rank 2 \"(50)\"",
    "TC has no located gameplay check that blocks a cast below",
    )

# --- 7: TC core ------------------------------------------------------------
add("7",
    "HEAD 209d6d51d1 - the same HEAD the Tailoring and",
    "Leatherworking files' section 7 were re-read from",
    "NPCHandler.cpp 97 HandleTrainerListOpcode -> 112",
    "HandleTrainerBuySpellOpcode (GUID check at 137, TeachSpell call at 155)",
    "Trainer.cpp 41 SendSpells (reputation discount 43, MoneyCost x discount",
    "76 TeachSpell -> 79 CanTeachSpell (definition",
    "106 ModifyMoney(-moneyCost); 172",
    "Spell.cpp 3869 TakePower() then 3872 TakeReagents()",
    "ITEM_FLAG_NO_REAGENT_COST 0x10000000 (ItemTemplate.h 218)",
    "DB2LoadInfo.h 3301), the auction-bot price filters, and quest turn-in",
    "GetSkillValue(skill) < qInfo->GetRequiredSkillValue()) - cooking recipe",
    "Player.cpp 5410 UpdateCraftSkill -> blocked by",
    "SPELL_ATTR1_NO_SKILL_INCREASE (5412-5413)",
    "5422 (SkillupSkillLineID)",
    "CONFIG_SKILL_GAIN_CRAFTING (5433)",
    "SkillGainChance (definition 5399, call",
    "MECHANIC_DISCOVERY",
    "GetSkillDiscoverySpell + LearnSpell (5429-5430)",
    "World.cpp 784-787",
    "128 (LEARN_SPELL",
    "136 (SKILL_STEP 44 -> EffectLearnSkill 2405, SetSkill at 2433)",
    "139 (TRADE_SKILL 47 -> EffectTradeSkill 2451)",
    "EffectTradeSkill's body is a NO-OP",
    "the mains' Effect #1 \"Trade Skill\" does nothing",
    "EffectCreateItem dispatch 116",
    "EffectCreateItem 1473 with SPELL_ATTR0_IS_TRADESKILL",
    "DoCreateItem 1383; EffectCreateItem2 dispatch 249",
    "(SPELL_EFFECT_CREATE_ITEM_2 = 157) -> definition 1482",
    "RequiresSpellFocus is checked in Spell.cpp - GameObjectFocusCheck call",
    "at 2322 (definition GridNotifiers.h 940-956",
    "SPELL_AURA_PROVIDE_SPELL_FOCUS at 6066 -> failure",
    "SPELL_FAILED_REQUIRES_SPELL_FOCUS 6072",
    "SpellFocusObject id at 4469-4473",
    "spellFocusType fields (225, 236-238, 731)",
    "SKILL_COOKING = 185 (SharedDefines.h 5907)",
    "SKILL_KUL_TIRAN_COOKING 2541 .. SKILL_CLASSIC_COOKING 2548",
    "(SharedDefines.h 6123-6130)",
    "QUEST_SORT_COOKING = 304 (5669)",
    "returns SKILL_COOKING (6369)",
    "QUEST_TRSKILL_COOKING = 3 (QuestDef.h",
    "QUEST_INFO_COOKING_WORLD_QUEST = 131",
    "TRADESKILL_COOKING = 3 (ScriptedGossip.h 38)",
    "TRADESKILL_FIRSTAID = 6 (41)",
    "TRADESKILL_FISHING = 12 (47)",
    "TRADESKILL_ARCHAEOLOGY = 16 (51)",
    "IsProfessionSkill",
    "SKILL_APPRENTICE_COOKING = 981 (6027)",
    "ATTR9_ITEM_CAST_GRANTS_SKILL_GAIN",
    "Object.cpp 1811",
    "aura 67556",
    "PROFESSION_SLOT_COOKING_TOOL = 25",
    "ITEM_SUBCLASS_PROFESSION_COOKING = 4",
    "ITEM_SUBCLASS_COOKING_RECIPE = 5",
    "BAG_FAMILY_MASK_COOKING_SUPP",
    "item-cast 111387 -> EffectLearnSpell 2129 learns",
    "9349/9361/9356,",
    "Player.cpp 15405 skill gate where a quest sets one",
    "Create Tradeskill Item (161002).",
    )

# --- 8: cannot do ---------------------------------------------------------
add("8",
    "1. Click profession-window buttons: crafts must be cast by spell id with",
    "2. Talk to trainers, vendors and NPCs at all: trainer lists/buys are",
    "3. Stand near a fire: every probed recipe requires the Cooking Fire focus",
    "fails SPELL_FAILED_REQUIRES_SPELL_FOCUS - the",
    "4. Complete quests: the Pandaria intro (31281 Sliced Peaches, 31302 Rice",
    "5. Wait on real-time gates: Legion work orders take 4 hours each",
    "minimum 3 / maximum 5 award payout",
    "6. Get lucky: Draenor discovery",
    "limited-supply vendor stock",
    "7. Hold reputation: Tortollan Seekers Revered",
    "8. Run world content for inputs: Falcosaur Eggs 142336",
    "9. Progress the BfA world: World Quest rank 3 recipes rotate",
    "10. See the wiki-only era trainers",
    "Odds 31032, Misensi 31031, Shazdar 49737,",
    "the dailies givers (Katherine 28705, Awilo 29631, Marogg",
    "I'll Huff 40047, Nature vs Nurture 40045 -> Murlocs 40102",
    "Amateur Hour",
    "Bottled Up 38407 -> Infiltrating",
    "Uniting Zandalar 51916 (first War Campaign steps) for World Quests",
    "fishing itself (every fish line in 3.3-3.8 - Fishing is a",
    "the auction house for",
    )

# --- 9: conflicts ---------------------------------------------------------
add("9",
    "Numbered conflicts (all resolved by adoption below):",
    "1) The wiki Cooking_trainers table ends at Draenor (last row Guy Fireeye,",
    "2) Northrend trainer sets disagree: the wiki lists 7 (adds Thomas Kolichio",
    "3) Outland taught-by three ways: wowhead's 264634 table lists 7",
    "4) Skill label bug: spell 265817 is named \"Zandalari Cooking\"",
    "5) Patch tags cross over between factions: A main 264646 = 8.0.1 but H main",
    "6) Wrapper patch tags: every wrapper 264635-264647 is tagged 8.1.0 except",
    "7) Classic main has no trainer table: 264632 and 264633 render no \"Taught",
    "8) Cost lines: mains 264632 and 264642 show NO \"Training cost\"",
    "9) Guide copy-paste: the Cataclysm guide's intro says",
    "10) BfA guide internal tension: step 75-140 headlines",
    "11) Rank-table skill display: recipe rank tables print",
    "12) Food \"Requires Level\" lines: Mon'Dazi (45), Rank 2 S&P Shank (40),",
    "13) Draenor recipe provenance: Grilled Saberfish 161002's quick facts say",
    "14) Two Dalaran eras, same trainer names: Katherine Lee 28705 and Awilo",
    "15) Vintage/anachronism labels: the vanilla guide page is branded",
    "16) NPC name collision \"Slagg\"",
    "17) Kylene's double role: she appears in 264634's Taught-by",
    "18) Block boundaries: the Tailoring file ends at 264631",
    "19) \"Requires meat from beasts and fire\" (mains/base tooltips) vs the",
    "20) TC drift statement: this file's section 7 anchors were re-read from",
    "21) Daily-quest level gates: a Cata-classic guide (warcrafttavern, search",
    "Adopted: the Taught-by 5 own the learn map",
    "Adopted: one sub-skill 2541; the label is",
    "Adopted: base 2550's Taught-by 66 handles the \"learn Cooking\"",
    "book/spell 160360 teaches the first recipe + the skill",
    "Adopted: fire = focus check;",
    "Also unverified (not guessed): Jug of Bourbon's item id",
    "ALL Cataclysm craft spell ids (the guide links recipe items and outputs,",
    "spell 160360's second taught spell",
    "gameobject entries provide the Cooking Fire focus",
    "grant path of Classic Cooking 2548 on a fresh character",
    "work-order/Nomi state machine details beyond the guide's text",
    )

# --- 10: sources ----------------------------------------------------------
add("10",
    "All pages fetched 2026-10-27; nothing fetched is stored in the repository.",
    "2550 (base Cooking: cost 10, difficulty 111, skill 185, 9 other ranks",
    "Taught by 66)",
    "264648 (\"Order Blast\" - verified non-Cooking end boundary)",
    "160360 (Introduction to Cooking in Draenor: Item Effect, 10 sec, Trigger",
    "(Spice Bread: skill Classic Cooking, cost 10, Create Item, Taught by 30,",
    "259442 (Mon'Dazi rank 1: skill Kul Tiran",
    "201524 (Salt and Pepper Shank rank 2: skill Legion Cooking",
    "(Grilled Saberfish: skill Draenor Cooking",
    "2596 (Skin of Dwarven Stout: cost 96-120, 50 vendors)",
    "93534 (Katherine Lee Legion: Teaches 10",
    "136052 (\"Cap'n\" Byron Mehlsack: Teaches 31",
    "Cooking_trainers (6 chunks; full table read",
    "vanilla-cooking-leveling (2, \"(Midnight)\" branded)",
    "zandalari-kul-tiran-bfa-cooking-leveling-guide (2)",
    "warcrafttavern Cata-classic",
    "HEAD 209d6d51d1; anchors re-read:",
    "2451-2461 (EffectTradeSkill no-op)",
    "grep SKILL_COOKING = 9 hits",
    "gameplay gate found (only DB2LoadInfo.h 3301",
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
    if not lines[0].startswith("BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - COOKING"):
        problems.append("bad title")
    for i in range(1, 11):
        if not any(l.startswith(f"{i}. ") for l in lines):
            problems.append(f"missing section {i}")
    if "unverified" not in text:
        problems.append("no unverified marker")
    if "Format:  - A - B: N x Craft Name spell id" not in text:
        problems.append("missing route format line")
    return problems


def load():
    return PAYLOAD.read_bytes().decode("ascii")


def run_checks(text):
    return [(fam, n) for fam, n in CHECKS if n not in text]


MUTATIONS = [
    ("fetched this week (2026-10-27)", "fetched this week (2026-10-26)"),
    ("Taught by (66).", "Taught by (67)."),
    ("Learn Skill Classic Cooking skill=2548,", "Learn Skill Classic Cooking skill=2549,"),
    ("wrapper 265818 added 8.0.1 (section 9 item 5)", "wrapper 265818 added 8.1.0 (section 9 item 5)"),
    ("Zandalari Cooking\" (cap 175, cost 8, added 8.1.0", "Zandalari Cooking\" (cap 175, cost 9, added 8.1.0"),
    ("(skill=2547, cap 75, cost 10, 8.0.1, Taught", "(skill=2547, cap 75, cost 9, 8.0.1, Taught"),
    ("Sungshin Ironpaw, Halfhill Market, Valley of the Four Winds [53.6, 51.2]",
     "Sungshin Ironpaw, Halfhill Market, Valley of the Four Winds [53.6, 51.3]"),
    ("Stephen Ryback, Old Town, Stormwind [77.2, 53.2]",
     "Stephen Ryback, Old Town, Stormwind [77.2, 53.3]"),
    ("Byron Mehlsack npc 136052, Boralus, level 60, A", "Byron Mehlsack npc 136052, Boralus, level 61, A"),
    ("60 x Spice Bread spell 37836 (60 Simple Flour 30817", "60 x Spice Bread spell 37836 (60 Simple Flour 30818"),
    ("casts printed by the guide = 310 (60 + 40 + 30 + 50 + 50 +",
     "casts printed by the guide = 311 (60 + 40 + 30 + 50 + 50 +"),
    ("casts printed by the guide = 194 (34 + 15 + 25 + 80 + 15 +",
     "casts printed by the guide = 195 (34 + 15 + 25 + 80 + 15 +"),
    ("BfA meats: 250 + 800 = 1050 exact", "BfA meats: 250 + 800 = 1051 exact"),
    ("30 crafts x 5 = 150 Crescent Saberfish Flesh exact", "30 crafts x 5 = 151 Crescent Saberfish Flesh exact"),
    ("\"Training cost: 8\". Mains WITHOUT", "\"Training cost: 9\". Mains WITHOUT"),
    ("SKILL_COOKING = 185 (SharedDefines.h 5907)", "SKILL_COOKING = 185 (SharedDefines.h 5908)"),
    ("at 2322 (definition GridNotifiers.h 940-956", "at 2322 (definition GridNotifiers.h 941-956"),
    ("Legion work orders take 4 hours each", "Legion work orders take 5 hours each"),
    ("Shank rank 1 \"Cooking (20)\", Mon'Dazi rank 2 \"(50)\"",
     "Shank rank 1 \"Cooking (21)\", Mon'Dazi rank 2 \"(50)\""),
    ("1) The wiki Cooking_trainers table ends at Draenor (last row Guy Fireeye,",
     "1) The wiki Cooking_trainers table ends at Pandaria (last row Guy Fireeye,"),
    ("264648 (\"Order Blast\" - verified non-Cooking end boundary)",
     "264648 (\"Order Bost\" - verified non-Cooking end boundary)"),
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
