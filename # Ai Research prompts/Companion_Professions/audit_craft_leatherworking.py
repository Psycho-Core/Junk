#!/usr/bin/env python3
"""Audit for Craft_Leatherworking.txt (BfA 8.3.7 build 35662).

Verifies section structure, the full 8.0.1 learn block (mains/wrappers,
sub-skills, caps, gaps), all 52 wiki trainer rows plus wowhead/guide
sources, every routed step with spell ids, the eight per-line craft
totals (recomputed from the printed addends), materials/costs/level,
fresh TrinityCore file:line anchors, the 19-item conflict index, source
manifest, ASCII/line-length hygiene, and absence of sibling-file
(Jewelcrafting/Inscription) ids.

Usage:
  python3 audit_craft_leatherworking.py            # run all checks
  python3 audit_craft_leatherworking.py --self-test  # 20 mutations
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "Craft_Leatherworking.txt"

CHECKS = []


def chk(desc, cond):
    CHECKS.append((desc, bool(cond)))


def load():
    return TARGET.read_text(encoding="utf-8")


def norm(t):
    return re.sub(r"\s+", " ", t)


def section_checks(t):
    n = norm(t)
    chk("line1 header", t.splitlines()[0] ==
        "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - LEATHERWORKING CRAFTING FOR A SERVER-SIDE COMPANION")
    chk("header underline", t.splitlines()[1].startswith("=") and
        len(t.splitlines()[1]) >= len(t.splitlines()[0]))
    chk("scope paragraph", 'anything without a readable source says "unverified"' in n)
    heads = [
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
    ]
    pos = -1
    for h in heads:
        i = t.find(h)
        chk(f"section header present: {h[:40]}", i >= 0)
        chk(f"section header in order: {h[:40]}", i > pos)
        pos = i
    for sub in ["3.1 Classic 1-300", "3.2 Outland 1-75", "3.3 Northrend 1-75",
                "3.4 Cataclysm 1-75", "3.5 Pandaria 1-75", "3.6 Draenor 1-100",
                "3.7 Legion 1-100", "3.8 BfA 1-175"]:
        chk(f"route {sub}", sub in t)
    for lit in ["8.3.7 (BUILD 35662)", "TrinityCore-based 8.3.7",
                "section 9 item 3", "Craft counts are exactly the counts"]:
        chk(f"scope literal: {lit[:38]}", lit in n)


def learn_map_checks(t):
    n = norm(t)
    lits = [
        "Base spell: Leatherworking 2108",
        "Training cost: 10, Difficulty: 111, Effect #1 Trade Skill",
        "Learn Skill (Leatherworking, skill=165) Value 1",
        "Requires leather scraps and hides gathered with the Skinning skill",
        "Other ranks (9), Taught by (50), Triggered by (1)",
        "158752 (skill 1), 195119 (skill 1), 3104 (50), 3811 (125), 10662 (200)",
        "32549 (275), 51302 (350), 81199 (425), 110423 (500)",
        "264577-264593 with three verified non-Leatherworking gaps",
        '264576 "Foul Winds"',
        '264587 "Head Slam"',
        '264594 "Spell #264594 doesn\'t exist" = end of block',
        "plus the Horde pair 265813/265814",
        "main 264577 \"Leatherworking\" (Learn Skill Classic Leatherworking skill=2532, cap 300)",
        "no Training-cost line, no Taught-by table rendered",
        "wrapper 264578 \"Leatherworking\" added 8.0.1 (the only wrapper not tagged 8.1.0",
        "Learn Spell 2108 + Learn Spell 264577 + Learn Skill Step (2532) Value 1",
        "main 264579 \"Outland Leatherworking\" (skill=2531, cap 75, cost 10, 8.0.1, Taught by 3)",
        "wrapper 264580 (8.1.0): Learn Spell 264579 + Step 2531",
        "main 264581 \"Northrend Leatherworking\" (skill=2530, cap 75, cost 10, 8.0.1, Taught by 4)",
        "wrapper 264582 (8.1.0): Learn 264581 + Step 2530",
        "main 264583 \"Cataclysm Leatherworking\" (skill=2529, cap 75, cost 10, 8.0.1, Taught by 13)",
        "wrapper 264584 (8.1.0): Learn 264583 + Step 2529",
        "main 264585 \"Pandaria Leatherworking\" (skill=2528, cap 75, cost 10, 8.0.1, Taught by 1)",
        "wrapper 264586 (8.1.0): Learn 264585 + Step 2528",
        "main 264588 \"Draenor Leatherworking\" (skill=2527, cap 100) added 8.0.1",
        "wrapper 264589 (8.1.0): Learn 264588 + Step 2527 - Triggered by (1) spell 169925",
        "main 264590 \"Legion Leatherworking\" (skill=2526, cap 100) added 8.0.1",
        "wrapper 264591 (8.1.0): Learn 264590 + Step 2526 - Reward from (1) quest 39958 \"Skin Deep\"",
        "main 264592 \"Kul Tiran Leatherworking\" (skill=2525, cap 175, cost 10, added 8.0.1",
        '"Alliance Specific Spell", Taught by 2',
        "wrapper 264593 (8.1.0): Learn 264592 + Step 2525",
        "main 265813 \"Zandalari Leatherworking\" (cap 175, cost 10, added 8.1.0",
        '"Horde Specific Spell", Taught by 2',
        "Effect says Learn Skill (Kul Tiran Leatherworking skill=2525) Value 1",
        "BOTH factions share sub-skill 2525 (section 9 item 4)",
        "wrapper 265814 (8.1.0): Learn 265813 + Step 2525 Value 1",
        "2532 Classic 1-300, 2531 Outland 1-75, 2530 Northrend 1-75",
        "2529 Cataclysm 1-75, 2528 Pandaria 1-75",
        "2527 Draenor 1-100, 2526 Legion 1-100",
        "2525 BfA (Kul Tiran/Zandalari) 1-175",
        "item 115358 \"Draenor Leatherworking\" (iLvl 15, Binds/Unique, Consumable, added 6.0.1",
        "Cost: 95-100 - currency unit not rendered: unverified",
        'Teaches you Draenor Leatherworking and a number of recipes" -> spell 169925',
        "Requires Level 10 AND Requires Leatherworking (1)",
        "Teaches (8): Secrets of Draenor Leatherworking 176089",
        "Journeying Robes 171261, Traveling Tunic 171264",
        "Traveling Helm 171263, Traveling Leggings 171265",
        "Journeying Helm 171260, Journeying Slacks 171262, Burnished Leather 171391",
        "Spell 169925 (6.0.1, Item Effect) -> triggers wrapper 264589",
        "Leara Moonsilk npc 87057 (Stormshield) / Garm Gladestride npc 87549 (Warspear)",
        "Dirty Note item 114877 from Karnoth npc 75043 during Shadows Awaken quest 34019",
        "Tattered Frostwolf Shroud item 116173 from Dorogg the Ruthless npc 74254",
        "The Butcher of Bladespire quest 33410",
        "trainer Namha Moonwater npc 93523 (Dalaran) -> quest 39958 \"Skin Deep\"",
        "(Level 10, Requires level 10)",
        "The quest reward is Legion Leatherworker 201705",
        'wrapper 264591 as "Reward from" that quest (section 9 item 15)',
        "Spell 201705 (added 7.0.1): Effect #1 Learn Spell 195119",
        "Effect #2 Learn Skill Step (165) Value 10",
        "behind 42 Leatherworking profession quests",
        "level 45 after Suramar quest \"Masquerade\" 42079",
        "\"Demon Flesh\" 40211 rewarding Recipe: Gravenscale Armbands item 140644",
        "Recipe: Dreadleather Bindings item 140636",
        "Uniting the Isles 43341 (Archmage Khadgar npc 90417",
        "need Leatherworking 25",
        "Apprentice/Journeyman/Expert/Artisan at 1-75/75-150/150-225/225-300",
        'the BfA row shows "1 - 150" while every 8.3.7 source says the BfA cap is 175',
    ]
    for lit in lits:
        chk(f"learn: {lit[:54]}", norm(lit) in n)
    for m in ["264577", "264579", "264581", "264583", "264585", "264588",
              "264590", "264592", "265813"]:
        chk(f"main id present: {m}", m in t)
    for w in ["264578", "264580", "264582", "264584", "264586", "264589",
              "264591", "264593", "265814"]:
        chk(f"wrapper id present: {w}", w in t)
    for s in ["2532", "2531", "2530", "2529", "2528", "2527", "2526", "2525"]:
        chk(f"sub-skill id {s}", s in t)


def trainer_checks(t):
    n = norm(t)
    rows = [
        "KTC Train-a-Tron Deluxe, Town-In-A-Box/Sky Falls/Gallywix Docks",
        "Teaches only up to Journeyman level",
        "Whittler Dewei, The Singing Pools",
        "Elder Oakpaw, Mandori Village",
        "Wembil Taskwidget, Kharanos, Dun Morogh [53.7, 52]",
        "Lien Farner, Goldshire, Elwynn Forest [42, 67]",
        "Adele Fielder, Goldshire, Elwynn Forest [46.4, 62.1]",
        "Jack \"All-Trades\" Derrington",
        "Drakk Stonehand, Wildhammer Keep, Aerie Peak, The Hinterlands [13, 43]",
        "Fimble Finespindle, Finespindle's Leather Goods, The Great Forge, Ironforge [40, 33]",
        "Simon Tanner, Protective Hide, Old Town, Stormwind [71, 62]",
        "Therisa Sallow, Calston Estate, Tirisfal Glades [44.5, 53]",
        "Nedric Sallow, Brill, Tirisfal Glades [61, 51]",
        "Shelene Rhobart, southeast of Brill, Tirisfal Glades [67, 60]",
        "Saren, Falconwing Square, Eversong Woods [49, 47]",
        "Sathein, west of the Silvermoon entrance, Eversong Woods [54, 51]",
        "Brumn Winterhoof, west of Boulder'gor, Arathi Highlands [28, 44]",
        "Brawn, Grom'gol Base Camp, Northern Stranglethorn [37.8, 50.4]",
        "Se'Jib, south of Mizjah Ruins, Northern Stranglethorn [45.2, 58.6]",
        "Lynalis, Walk of Elders, Silvermoon City [85, 81]",
        "Arthur Moore, Rogues' Quarter, Undercity [74, 56]",
        "Iranis Shadebloom, Dolanaar, Teldrassil [56, 52.2]",
        "Nadyia Maneweaver, northwest of Ban'ethil Hollow, Teldrassil [41, 49]",
        "Valn, Azure Watch, Azuremyst Isle [48.5, 52.2]",
        "Moordo, Stillpine Hold, Azuremyst Isle [44.8, 23.8]",
        "Aayndia Floralwind, Astranaar, Ashenvale [35, 52]",
        "Eustace Tanwell, Theramore, Dustwallow Marsh [66.4, 45.2]",
        "Telonis, Craftsmen's Terrace, Darnassus [64, 21]",
        "Akham, Leatherworking & Skinning, Trader's Tier, The Exodar [67, 74]",
        "KTC Train-a-Tron Deluxe, Bilgewater Harbor, Azshara [57, 50.5]",
        "Runda, Razor Hill, Durotar [53, 42]",
        "Lalum Darkmane, Bloodhoof Village, Mulgore [46.5, 57.5]",
        "Chaw Stronghide, Bloodhoof Village, Mulgore [47, 60]",
        "Narv Hidecrafter, Ghost Walker Post, Desolace [55, 56]",
        "Hahrana Ironhide, Leatherworking & Skinning, Camp Mojache, Feralas [74, 43]",
        "Karolek, Kodohide Leatherworkers, the Drag, Orgrimmar [62, 45]",
        "Una, Middle rise, Thunder Bluff [43, 44]",
        "Brumman, Honor Hold, Hellfire Peninsula [56, 63]",
        "Barim Spilthoof, Thrallmar, Hellfire Peninsula [56, 37]",
        "Grikka, Mok'Nathal Village, Blade's Edge Mountains [73, 62]",
        "Darmari, Lower City, Shattrath City [67, 68]",
        "Daenril, Scryer's Tier, Shattrath City [41.8, 63.8]",
        "Not available to members of the Aldor",
        "Korim, Aldor Rise, Shattrath City [37.6, 28.6]",
        "Not available to members of the Scryers",
        "Rosemary Bovard, Valiance Keep, Borean Tundra [57, 70]",
        "Bernadette Dexter, Valgarde, Howling Fjord [60, 63]",
        "Gunter Hansen, Vengeance Landing, Howling Fjord [78, 30]",
        "Awan Iceborn, Taunka'le Village, Borean Tundra [77, 38]",
        "Andellion + Diane Cannings + Manfred Staller + Namha Moonwater",
        "Legendary Leathers, Magus Commerce Exchange, Dalaran [36, 29]",
        "Kul'de, Argent Tournament Grounds, Icecrown [71, 20]",
        "Clean Pelt, The Grummle Bazaar, Kun-Lai Summit [64.6, 60.9]",
        "Master Cannon, Peak of Serenity, Kun-Lai Summit [50.6, 42.0]",
        "Cassandra Brennor, Tradewinds Market, Boralus (no coordinate)",
        "Xanjo, Terrace of Crafters, Dazar'alor (no coordinate)",
    ]
    for r in rows:
        chk(f"wiki row: {r[:52]}", norm(r) in n)
    chk("52 rows count", "warcraft.wiki Leatherworking_trainers (52 rows, page includes the BfA pair" in n)
    for land in ["The Maelstrom (Cataclysm):", "The Wandering Isle (Mists of Pandaria):",
                 "Eastern Kingdoms:", "Kalimdor:", "Outland:", "Northrend:",
                 "Pandaria:", "Kul Tiras / Zandalar (Battle for Azeroth):"]:
        chk(f"group {land}", land in t)
    chk("page includes BfA pair", "page includes the BfA pair" in n)
    wow = [
        "Brumman npc 18771 (Hellfire, level 30, AH)",
        "Darmari npc 19187 (Shattrath, level 30, AH)",
        'npc 33612 "Leatherworking" (Shattrath, level 30, Uncategorized)',
        "Andellion npc 29508, Diane Cannings npc 28700, Manfred Staller npc 29507, Namha Moonwater npc 29509",
        "Aayndia Floralwind 3967, Adele Fielder 1632, Chaw Stronghide 3069",
        "Drakk Stonehand 11097 (A), Eustace Tanwell 53436 (A)",
        "Fimble Finespindle 5127 (A), Hahrana Ironhide 11098 (H, 30)",
        "Karolek 3365 (H, 14-90), Lynalis 16688, Shelene Rhobart 3549",
        "Simon Tanner 5564 (A, 9-90), Telonis npc 151287 (Stormwind, level 60)",
        "Telonis npc 4212 (Darnassus, level 80)",
        "Clean Pelt npc 65121 (Kun-Lai, level 20-35)",
        "Cassandra Brennor npc 136063 (Boralus, level 60, A)",
        "Instructor Alikana npc 153817 (Nazjatar, level 50, A)",
        "Jada npc 154321 (Nazjatar, level 50, H)",
        "Xanjo npc 122698 (Dazar'alor, level 10-60, H)",
    ]
    for wv in wow:
        chk(f"wowhead taught-by: {wv[:52]}", norm(wv) in n)
    guide = [
        "Darmari npc 19187 (learn Outland Leatherworking, Shattrath)",
        "Almaador npc 21432 (Sha'tar Honored)",
        "Alurmi npc 21643 (inside Caverns of Time, Keepers of Time Honored)",
        "Diane Cannings npc 28700 (Dalaran Northrend trainer",
        "Braeg Stoutbeard npc 32515",
        "Tamar npc 3366 (Horde, Orgrimmar) / Jillian Tanner npc 5565 (Alliance, Stormwind)",
        "Krogo Darkhide npc 64054 (Horde, Shrine of Two Moons)",
        "Tanner Pang npc 64094 (Alliance, Shrine of Seven Stars)",
        "Jake the Fox npc 91024 (Alliance) / Zeezu npc 91033 (Horde)",
        "Stalriss Dawnrunner npc 98969 (Suramar, rank-1 recipe seller after the quests)",
        "Ranid Glowergold npc 93521 (Dalaran, rank 2)",
        "Strap Bucklebolt npc 107760 (Dalaran Sewers, rank 2/3 for Sightless Eye)",
        "Shade of Xavius npc 101403 (Darkheart Thicket)",
        "Dargrul npc 107704 (Neltharion's Lair)",
        "Advisor Vandros npc 98208 (The Arcway)",
        "Advisor Melandrus npc 104218 (Court of Stars)",
        "Aman de Child npc 141609 (Amber Tanning Oil",
        "Dazzerian npc 154652 (H) / Crafticus Mindbender npc 154653 (A) at Nazjatar",
        "need Leatherworking 160 / 170",
        "Khadgar npc 90417 (Uniting the Isles 43341)",
    ]
    for g in guide:
        chk(f"guide source: {g[:52]}", norm(g) in n)


def route_checks(t):
    n = norm(t)
    steps = [
        # 3.1
        "19 x Light Leather spell 2881 (57 Ruined Leather Scraps; 3 scraps per craft)",
        "10 x Light Armor Kit spell 2152 (10 Light Leather)",
        "20 x Handstitched Leather Cloak spell 9058 (40 Light Leather, 20 Coarse Thread)",
        "5 x Handstitched Leather Belt spell 3753 (30 Light Leather, 5 Coarse Thread)",
        "30 x Embossed Leather Gloves spell 3756 (90 Light Leather, 60 Coarse Thread)",
        "15 x Fine Leather Belt spell 3763 (90 Light Leather, 30 Coarse Thread",
        "15 x Cured Medium Hide spell 3817 (15 Medium Hide, 15 Salt; keep them)",
        "16 x Dark Leather Boots spell 2167 (64 Medium Leather, 32 Fine Thread, 16 Gray Dye)",
        "15 x Dark Leather Belt spell 3766 (15 Fine Leather Belt, 15 Cured Medium Hide, 30 Fine Thread, 15 Gray Dye",
        'guide prints "Gray Die"',
        "5 x Hillman's Leather Gloves spell 3764 (70 Medium Leather, 20 Fine Thread)",
        "5 x Heavy Leather spell 20649 (25 Medium Leather)",
        "20 x Cured Heavy Hide spell 3818 (20 Heavy Hide, 60 Salt; keep them)",
        "20 x Heavy Armor Kit spell 3780 (100 Heavy Leather, 20 Fine Thread",
        "10 x Barbaric Shoulders spell 7151 (80 Heavy Leather, 10 Cured Heavy Hide, 20 Fine Thread)",
        "10 x Guardian Gloves spell 7156 (40 Heavy Leather, 10 Cured Heavy Hide, 10 Silken Thread)",
        "5 x Thick Armor Kit spell 10487 (25 Thick Leather, 5 Silken Thread)",
        "35 x Nightscape Headband spell 10507 (175 Thick Leather, 70 Silken Thread)",
        "15 x Nightscape Pants spell 10548 (210 Thick Leather, 60 Silken Thread)",
        "18 x Rugged Armor Kit spell 19058 (90 Rugged Leather)",
        "25 x Wicked Leather Bracers spell 19052 (200 Rugged Leather, 25 Black Dye, 25 Rune Thread",
        "10 x Wicked Leather Headband spell 19071 (120 Rugged Leather, 10 Black Dye, 10 Rune Thread)",
        # 3.2
        "5 x Comfortable Insoles spell 32482 (10 Knothide Leather",
        "Knothide Leather Scraps 25649 -> Knothide Leather is spell 32454",
        "25 x Knothide Armor Kit item 25650 (100 Knothide Leather; yellow; guide links the item, craft spell id unverified)",
        "246 x Heavy Knothide Leather spell 32455 (1230 Knothide Leather",
        "20 x Thick Draenic Vest spell 32473 (60 Heavy Knothide Leather, 60 Rune Thread 14341",
        "Scaled Draenic Boots item 25659",
        "30 x Heavy Knothide Armor Kit item 34330 (90 Heavy Knothide Leather",
        "8 x Drums of Battle spell 35543 (48 Heavy Knothide Leather, 32 Thick Clefthoof Leather",
        "8 x Drums of Panic spell 35538 (48 Heavy Knothide Leather, 32 Fel Hide",
        "guide's observed range 7-15 crafts",
        # 3.3
        "5 x Borean Armor Kit spell 50962 (20 Borean Leather 33568",
        "leather is spell 64661 for skinners - \"free 5 skill points\"",
        "5 x Arctic Boots spell 50948 (40 Borean Leather)",
        "5 x Arctic Gloves spell 50947 (50 Borean Leather)",
        "300 x Heavy Borean Leather spell 50936 (1800 Borean Leather",
        "Arctic Belt 50949 / Arctic Wristguards 51571",
        "6 x Nerubian Bracers spell 60622 (72 Borean Leather",
        "13 x Dark Frostscale Leggings spell 60601 (52 Heavy Borean Leather, 65 Crystallized Water 37705)",
        "13 x Dark Iceborne Leggings spell 60611 (52 Heavy Borean Leather, 65 Crystallized Shadow 37703)",
        "5 x Overcast Bracers item 43264 (40 Heavy Borean Leather, 5 Eternal Water 35622",
        "Pattern 44524 from Braeg Stoutbeard 32515",
        "13 x Overcast Handwraps spell 60721 (130 Heavy Borean Leather, 13 Eternal Water",
        "Pattern 44525 from Braeg 32515",
        "5 x Frosthide Leg Armor spell 50965 (10 Arctic Fur 44128, 10 Nerubian Chitin 38558, 5 Frozen Orb 43102)",
        "5 x Icescale Leg Armor spell 50967 (10 Arctic Fur, 10 Icy Dragonscale 38557, 5 Frozen Orb)",
        "10 x Trollwoven Girdle spell 60759 (100 Heavy Borean Leather, 50 Eternal Shadow 35627, 50 Eternal Fire 36860, 10 Frozen Orb",
        "Pattern 44551 from Braeg for 2 Arctic Fur",
        "Revenant's Treads 60757 / Windripper Boots 62176",
        # 3.4
        "6 x Savage Armor Kit spell 78379 (30 Savage Leather 52976)",
        "5 x Tsunami Boots spell 78410 (35 Savage Leather, 5 Eternium Thread",
        "10 x Savage Cloak spell 78380 (70 Savage Leather, 10 Eternium Thread)",
        "5 x Darkbrand Boots spell 78407 (50 Savage Leather, 5 Eternium Thread)",
        "10 x Darkbrand Shoulders spell 78411 (120 Savage Leather, 10 Eternium Thread)",
        "240 x Heavy Savage Leather spell 78436 (1200 Savage Leather)",
        "5 x Darkbrand Chestguard spell 78428 (60 Savage Leather, 5 Eternium Thread",
        "12 x Darkbrand Helm spell 78424 (60 Heavy Savage Leather",
        "3 x Vicious Hide Cloak spell 99535 (3 Pristine Hide 52980, 12 Volatile Fire 52325)",
        "3 x Vicious Fur Cloak spell 99536 (3 Pristine Hide, 12 Volatile Earth",
        "5 x Vicious Leather Bracers spell 78446 (50 Heavy Savage Leather, 50 Volatile Fire",
        "Pattern 67046 from the same supply vendors",
        "5 x Vicious Leather Boots spell 78454 (50 Heavy Savage Leather, 50 Volatile Fire; pattern from the same vendors)",
        "5 x Vicious Leather Helm spell 78469 (50 Heavy Savage Leather, 50 Volatile Water 52326",
        # 3.5
        "10 x Sha Armor Kit spell 124628 (40 Mist-Touched Leather 72120",
        "conversion Sha-Touched Leather 72162 -> Mist-Touched spell 124627",
        "22 x Misthide Bracers spell 124576 (110 Mist-Touched Leather",
        "6 x Misthide Gloves spell 124574 (48 Mist-Touched Leather)",
        "15 x Misthide Chestguard spell 124573 (150 Mist-Touched Leather)",
        "24 x Contender's Leather Bracers spell 124608 (288 Mist-Touched Leather",
        "Pattern 86250 from Krogo Darkhide 64054 (H) / Tanner Pang 64094 (A) for 1 Spirit of Harmony 76061 = 10 Motes of Harmony 89112",
        # 3.6
        "55 x Drums of Fury spell 178208 (275 Raw Beast Hide 110609",
        "recipe item 120258",
        "Secrets of Draenor Leatherworking spell 176089 crafted first - 1-day cooldown",
        "45 x Leather Refurbishing Kit spell 171266 (1350 Raw Beast Hide",
        "recipe item 116325",
        "ALTERNATIVE 55 - 100 (guide-printed): 45 x Spiritual Leathercraft spell 182121 (45 Primal Spirit 120945 + 450 Raw Beast Hide",
        "recipe item 122715 from the random garrison leather trader",
        "for 60 Raw Beast Hide; Primal Spirit sold by the trader for 5 Raw Beast Hide each = 225 extra Raw Beast Hide",
        "total 735 instead of 1350",
        # 3.7
        "90 x Rank 3 Warhide Bindings spell 194711 (810 Stonehide Leather - id unverified",
        '"this is just an aproximate number"',
        "you can also make it up to 80 if you are feeling lucky",
        "90 x Rank 3 Battlebound Grips 194754 with 1080 Stormscale",
        "25 x Rank 3 Gravenscale Girdle spell 194768 (300 Stormscale, 50 Blood of Sargeras 124124)",
        "25 x Rank 3 Dreadleather Belt spell 194728 (300 Stonehide Leather, 50 Blood of Sargeras)",
        "250/500 Sightless Eye currency 1149",
        "750 in about 25 minutes",
        "25 x Dreadleather Bindings 194727 (2750 Stonehide)",
        "25 x Gravenscale Armbands 194767 (2750 Stormscale)",
        "25 x Dreadleather Gloves 194732 (2875 Stonehide)",
        "25 x Gravenscale Grips 194772 (2750 Stormscale)",
        # 3.8
        "25 x Shimmerscale Armguards spell 256757 (150 Shimmerscale 153050, 100 Blood-Stained Bone 154164)",
        "25 x Coarse Leather Armguards spell 256756 (150 Coarse Leather 152541, 100 Blood-Stained Bone",
        "Shimmerscale Pauldrons spell 256759 (200 Shimmerscale",
        "25 x Coarse Leather Pauldrons spell 256754 (200 Coarse Leather, 150 Blood-Stained Bone)",
        "50 x Hardened Tempest Hide spell 272278 (50 Tempest Hide 154722, 50 Amber Tanning Oil 160059",
        "Aman de Child 141609, Alliance from the trainer",
        "15 x Coarse Leather Barding spell 256790 (375 Coarse Leather",
        "Shimmerscale Diving Helmet 256793",
        "45 x Rank 2 Coarse Leather Barding spell 286019 (900 Coarse Leather",
        "Rank 3 recipe item 166313",
        "30 x Drums of the Maelstrom spell 256791 (750 Coarse Leather, 300 Blood-Stained Bone)",
        "40 x Dredged Leather Bladder spell 301405 (400 Dredged Leather 168649, 200 Nylon Thread - id unverified)",
        "Jada 154321 (H) / Instructor Alikana 153817 (A) after the first few intro quests",
        "6 x Notorious Combatant's Mail Armguards 294823 with 6 Mark of Honor 137642 + Expulsom 152668",
        "Dazzerian 154652 (H) / Crafticus Mindbender 154653 (A), need Leatherworking 160 / 170",
    ]
    for s in steps:
        chk(f"route: {s[:54]}", norm(s) in n)


def totals_checks(t):
    n = norm(t)
    found = re.findall(
        r"Total (?:exact-count casts|crafts) printed by the guide = (\d+) \(([^)]*)\)",
        n)
    chk("8 route totals present", len(found) == 8)
    expected = ["323", "342", "367", "311", "77", "100", "140", "230"]
    vals = [v for v, _ in found]
    for e in expected:
        chk(f"total {e} exists", e in vals)
    for num_s, body in found:
        head = body.split(";")[0].split(".")[0]
        addends = [int(x) for x in re.findall(r"\d+", head)]
        chk(f"total {num_s} from {addends}", sum(addends) == int(num_s))
    # shopping cross-checks printed in section 4
    for cross in [
        "Light 10+40+30+90+90 = 260 (exact)",
        "Medium 64+70+25 = 159 vs list 160",
        "Heavy 100+80+40 = 220 (exact)",
        "Thick 25+175+210 = 410 (exact)",
        "Rugged 90+200+120 = 410 (exact)",
        "consumed 60+90+48+48 = 246 exactly",
        "direct crafts 20+40+50+1800+72 = 1982 exact",
        "consumes 52+40+130+100 = 322 while the 300-craft step yields 300",
        "30+35+70+50+120+1200+60 = 1565 exact",
        "Volatile Fire 12+50+50 = 112 exact",
        "printed crafts consume 40+110+48+150+288 = 636 vs list 640",
        "Coarse 375+900+750 = 2025 exact",
        "Shimmerscale 150+200 = 350 exact",
        "Blood-Stained 100+150+300 = 550 exact",
        "Dredged 400 exact",
    ]:
        chk(f"cross-check: {cross[:52]}", norm(cross) in n)


def materials_costs_level_checks(t):
    n = norm(t)
    mats = [
        "Rune Thread 14341 (vendor, same shops)",
        "Knothide Leather Scraps 25649 (Skinning)",
        "Borean Leather Scraps 33567 -> leather conversion spell 64661",
        "Crystallized Water 37705 OR 65 Crystallized Shadow 37703",
        "18 Eternal Water 35622, 15 Frozen Orb 43102",
        "50 Eternal Shadow 35627, 50 Eternal Fire 36860",
        "Pristine Hide 52980 (vendor Tamar 3366 / Jillian Tanner 5565 for 10 Heavy Savage Leather 56516 each",
        "wiki notes Heavy Savage Leather is also sold by supply vendors",
        "Spirit of Harmony 76061 (= 10 Motes of Harmony 89112",
        "Raw Beast Hide 110609 (skin/AH), Primal Spirit 120945",
        "Blood of Sargeras 124124 (binds when picked up",
        "Sightless Eye currency 1149",
        "rank-3 recipe items 137924 (world drop), 137892 (Withered Army Training 43943 chest), 137897 (Vandros 98208), 137929 (Melandrus 104218)",
        "2025 Coarse Leather 152541, 350 Shimmerscale 153050",
        "50 Tempest Hide 154722, 550 Blood-Stained Bone 154164, 400 Dredged Leather 168649",
        "Nylon Thread (id unverified - section 10 probe miss)",
        "Amber Tanning Oil 160059 (Aman de Child 141609 / trainer)",
        "Mark of Honor 137642 (PvP), Expulsom 152668 (Scrapper)",
        "Calcified Bone 154165, Mistscale 153051, Hardened Tempest Hide 152542",
        "Spirit of the Bested 168138, Long Regal Sinew 168139",
        "(Skinning)/AH",
        "threads, dyes, and salt from Leatherworking Supply vendors near your trainer",
    ]
    for m in mats:
        chk(f"material: {m[:54]}", norm(m) in n)
    costs = [
        "Base spell 2108: \"Training cost: 10\"",
        "mains with the same line: 264579, 264581, 264583, 264585, 264592, 265813",
        "WITHOUT a training-cost line",
        "Currency unit is not rendered on the pages - unverified",
        "trainer money = MoneyCost x reputation discount",
        "FailReason::NotEnoughMoney",
        "Drums of Battle pattern - Sha'tar Honored (no gold printed)",
        "Drums of Panic pattern - Keepers of Time Honored (no gold printed)",
        "Trollwoven Girdle pattern 44551 - 2 Arctic Fur",
        "Contender's Leather Bracers pattern 86250 - 1 Spirit of Harmony",
        "60 Raw Beast Hide, Primal Spirit 5 each",
        "rank 2 - 250 Sightless Eye, rank 3 - 500 Sightless Eye",
        "alternate step - 6 Mark of Honor + Expulsom",
        "Arctic Fur from Braeg - 10 Heavy Borean Leather",
        "Pristine Hide - 10 Heavy Savage Leather",
        "quest 39958 shows \"Money 1,400\" with no unit: unverified",
        "item 115358 quick facts show \"Cost: 95-100\" with no unit: unverified",
    ]
    for c in costs:
        chk(f"cost: {c[:54]}", norm(c) in n)
    level = [
        "Profession learn itself: no character level on spell 2108 or the mains",
        "\"Leatherworking does not require special tools or locations to craft\"",
        "Scroll 115358: \"Requires Level 10\" AND \"Requires Leatherworking (1)\"",
        "quest 39958 \"Skin Deep\" is Level 10, requires level 10",
        "to start the 42 quests \"at 50\"",
        "the last chain needs level 45",
        "Uniting the Isles 43341 needs friendly with every Legion faction",
        "profession World Quests need Leatherworking 25",
        "level 60 (Cassandra 136063) and 10-60 (Xanjo 122698)",
        "Nazjatar recipe trainers show level 50 (Jada/Alikana)",
        "rank-2/3 buying needs Leatherworking 160 / 170",
        "Tools of the Trade questline needs character level 120 AND Battle for Azeroth Leatherworking 150",
        "\"requires level 111\"",
        "Master (Outland), Grand Master (Northrend)",
        "Illustrious Grand Master (Cataclysm), Zen Master (Pandaria)",
        "Draenor Master (1-100), Legion Master (1-100)",
        "Kul Tiran/Zandalari Master (row says 1 - 150 - section 9 item 1)",
        "Cut 'Em Out! (H) / Fair Trade (A)",
    ]
    for v in level:
        chk(f"level: {v[:54]}", norm(v) in n)


def tc_checks(t):
    n = norm(t)
    anchors = [
        "HEAD 209d6d51d1",
        "same HEAD as the Companion_Professions audit clones",
        "NPCHandler.cpp 97 HandleTrainerListOpcode -> 112 SendTrainerList",
        "talks to trainer->SendSpells at 127",
        "NPCHandler.cpp 130 HandleTrainerBuySpellOpcode (GUID check at 137)",
        "Trainer.cpp 41 SendSpells (condition filtering at 58)",
        "76 TeachSpell -> 79 CanTeachSpell (CanTeachSpell definition 149)",
        "98 reputationDiscount x MoneyCost (99)",
        "100 HasEnoughMoney -> 102 SendTeachFailure NotEnoughMoney",
        "106 ModifyMoney(-moneyCost)",
        "Trainer.cpp 172 GetSpellState, 212 SendTeachFailure",
        "teaches the mains (264577, 264579, 264581, 264583, 264585, 264592/265813)",
        "Spell.cpp 3869 TakePower() then 3872 TakeReagents()",
        "definition TakeReagents at Spell.cpp 5600",
        "ITEM_FLAG_NO_REAGENT_COST 0x10000000 (ItemTemplate.h 218)",
        "There is NO server-side skill gate on recipe casts",
        "reqSkillValue appears only in the lock path",
        "Spell.cpp 6373 -> CanOpenLock 8648, lock table value 8688, fail 8702",
        "Player.cpp 5410 UpdateCraftSkill",
        "SPELL_ATTR1_NO_SKILL_INCREASE (5412)",
        "reads the spell's skill line at 5421-5422 (SkillupSkillLineID)",
        "CONFIG_SKILL_GAIN_CRAFTING (5433)",
        "SkillGainChance (5435)",
        "World.cpp 784-787 SkillChance.Orange 100 / Yellow 75 / Green 25 / Grey 0",
        "World.cpp 790 SkillGain.Crafting default 1",
        "SpellEffects.cpp 128 (LEARN_SPELL) and 210 (effect 118 SKILL)",
        "EffectSkill 4668",
        "SkillTiers lookup 4689",
        "SetSkill 4699",
        "EffectLearnSpell 2129 (TriggerSpell learn at 2170)",
        "wrappers 264578-264593 and 265814",
        "SpellEffects.cpp 116",
        "EffectCreateItem 1473",
        "SPELL_ATTR0_IS_TRADESKILL -> ItemContext::Trade_Skill at 1478",
        "ATTR0_IS_TRADESKILL selections at 1492/1522/2484",
        "DoCreateItem 1383",
        "EffectCreateItem2 dispatch 249 / definition 1482 (call sites 1499/2492/3533)",
        "SKILL_LEATHERWORKING = 165 (SharedDefines.h 5901)",
        "QUEST_SORT_LEATHERWORKING -> SKILL_LEATHERWORKING (SharedDefines.h 6366)",
        "QUEST_TRSKILL_LEATHERWORKING = 8 (QuestDef.h 132)",
        "Spell.cpp 3863-3865 (ATTR9_ITEM_CAST_GRANTS_SKILL_GAIN",
        "the WoD scroll cast of 169925 via item 115358",
        "ordinary QUEST_TRSKILL_LEATHERWORKING (8) quests",
        "PROSPECTING 127 at SpellEffects.cpp 219 / EffectProspecting 4614",
        "MILLING 158 at 250 / EffectMilling 4641",
        "no leatherworking-specific spell effect in the core",
    ]
    for a in anchors:
        chk(f"TC: {a[:54]}", norm(a) in n)


def cannot_do_checks(t):
    n = norm(t)
    items = [
        "Click profession-window buttons",
        "cast by spell id with the recipe already in the spellbook",
        "Talk to trainers, vendors and NPCs at all",
        "walk up to a guard and ask",
        "Complete quests: Skin Deep 39958",
        "the 42 Legion profession quests",
        "Tools of the Trade questline (level 120 + BfA skill 150)",
        "Get lucky with the garrison leather trader",
        "random daily spawn among 4 NPCs at a level-3 town hall",
        "not guaranteed ... even on the day it is supposed to spawn",
        "Hold reputation the recipes need",
        "Sha'tar Honored (Drums of Battle), Keepers of Time Honored (Drums of Panic)",
        "Daenril not for Aldor, Korim not for Scryers",
        "only sell to Revered (overview)",
        "Run dungeons/raids/world content for rank 3",
        "Blood of Sargeras 124124 only drops from content and cannot be bought",
        "Earn currencies by playing",
        "Sightless Eye 1149",
        "Mark of Honor 137642 (PvP)",
        "Interact with world objects as a player would",
        "Mallet of Thunderous Skins 293076",
        "Scrap-o-Matic 1000 / Shred-Master Mk1",
    ]
    for i in items:
        chk(f"cannot-do: {i[:52]}", i in n)


def conflicts_checks(t):
    n = norm(t)
    sec9 = t.split("9. CONFLICTS AND UNVERIFIED INDEX")[1].split("10. SOURCES")[0]
    nums = [int(m) for m in re.findall(r"^(\d+)\)", sec9, flags=re.M)]
    chk("conflicts numbered 1..19", nums == list(range(1, 20)))
    items = [
        'wiki training table prints "1 - 150"',
        '"maximum potential skill of 175"',
        "Adopted: 175 (page is flagged outdated)",
        "264592 (Alliance) added 8.0.1 while 265813 (Horde) added 8.1.0",
        "Adopted: A main is 8.0.1, H main is 8.1.0",
        "every wrapper 264580-264593 and 265814 is tagged 8.1.0",
        "whose quick facts print 8.0.1",
        "same first-wrapper exception the Jewelcrafting/Inscription blocks show",
        "Adopted: 264578 = 8.0.1, the rest = 8.1.0",
        'spell 265813 is named "Zandalari Leatherworking"',
        "Effect reads Learn Skill (Kul Tiran Leatherworking) skill=2525",
        "label is wrong on the Horde spell (mirrors the Jewelcrafting file's item 10)",
        '264576 is "Foul Winds"',
        '264587 is "Head Slam" (Temple of Sethraliss ability)',
        '264594 answers "Spell #264594 doesn\'t exist"',
        "block = 264577-264593 with two verified non-LW gaps",
        "Two Dalaran eras, same names",
        "same NPC in Legion Dalaran will not teach Northrend Leatherworking",
        "Namha Moonwater npc 93523",
        "Namha Moonwater npc 29509",
        "the wiki's single four-name Dalaran row does not distinguish the eras",
        "Outland taught-by mismatch",
        '"Uncategorized" creature literally named "Leatherworking" (npc 33612, Shattrath)',
        "Taught-by 3 vs wiki 6",
        "Cataclysm taught-by mismatch",
        "TWO Telonis NPCs (151287 Stormwind level 60 and 4212 Darnassus level 80)",
        "keep all 13 wowhead entries",
        "Classic main has no trainer table",
        '264577\'s page renders no "Taught by" section',
        "main 264577's own teacher list is unverified",
        "Wrapper effect shape",
        "THREE effects (Learn 2108 + Learn 264577 + Step 2532)",
        "every other wrapper has two",
        "Cost lines",
        "mains 264577, 264588 and 264590 show NO \"Training cost: 10\"",
        "the other three record \"no training-cost line\"",
        "Northrend 60-65 reads as a choice",
        "route total 367; both spell ids kept",
        "Northrend heavy-leather arithmetic",
        "steps consume 52+40+130+100 = 322 (+22)",
        "the +22 bridge is unverified",
        "Pandaria shopping list",
        "the guide itself says \"approximate materials\"",
        "Legion quest 39958 rewards",
        "Adopted: the quest grants BOTH the perk spell and the wrapper",
        "Draenor leather trader dates",
        "treat the trader as a random daily spawn only",
        "Historic rows kept for context",
        "4.0.3a (specializations removed, ranks equalized)",
        "4.0.1 removed specializations (Elemental/Tribal/Dragonscale)",
        "6.0.2 removed Fur Lining/Leg Reinforcements (needed 400 skill)",
        "8.0.1 split the skill bars",
        "TC drift statement",
        "re-read from master HEAD 209d6d51d1",
        "the shared craft and trainer anchors are unchanged",
        "Guide vintage label",
        '"vanilla-leatherworking-leveling" page is branded "(Midnight)"',
        '"NOT a WoW Classic guide"',
        "Adopted: as printed",
        "Also unverified (not guessed):",
        "probe item 152576 = Tidespray Linen, a miss",
        "Stonehide Leather / Stormscale ids",
        '"learn on craft" discovery handling',
    ]
    for i in items:
        chk(f"conflict: {i[:54]}", norm(i) in n)


def sources_checks(t):
    n = norm(t)
    src = [
        "fetched 2026-10-26 week",
        "nothing fetched is stored in the repository",
        "2108 (base Leatherworking: cost 10, difficulty 111, 9 other ranks, Taught by 50)",
        "MISS for block start - it is \"Foul Winds\"",
        "264577, 264578, 264579, 264580, 264581, 264582, 264583, 264584, 264585, 264586",
        '"Head Slam" - non-LW gap',
        "264588, 264589, 264590, 264591, 264592, 264593",
        "264594 (does not exist - end of block)",
        "265813 (Horde main), 265814 (Horde wrapper)",
        "115358 (WoD scroll -> Teaches spell 169925, 8 taught recipes)",
        '201705 (Legion Leatherworker: Learn 195119 + Step 165 value 10)',
        'quest 39958 "Skin Deep" (Level 10 / Requires 10, wrapper 264591 reward link)',
        "skill=165 hub (Skill ID 165, pattern-group counts)",
        "spells/professions/leatherworking (1922-result recipe list; not used for ids)",
        "MISS for Nylon Thread - it is Tidespray Linen",
        "Leatherworking (8 chunks; read 0-3, 5-6",
        "leather-conversion rules, limited/daily conversions, specializations, historic benefits, patch rows",
        "Leatherworking_trainers (6 chunks, 52 rows through Kul Tiras/Zandalar + patch rows)",
        "vanilla-leatherworking-leveling (2 chunks; guide content complete in 0)",
        "outland-leatherworking-leveling (1)",
        "northrend-leatherworking-leveling (2; content complete in 0)",
        "cataclysm-leatherworking-leveling (1)",
        "pandaria-leatherworking-leveling (1)",
        "draenor-leatherworking-leveling (2; content complete in 0)",
        "legion-leatherworking-leveling (2)",
        "zandalari-kul-tiran-bfa-leatherworking-leveling-guide (2)",
        "bfa-leatherworking overview (5 chunks; read 0-2",
        "blobless sparse clone of master (src/server/game + src/server/scripts), HEAD 209d6d51d1",
        "SpellEffects.cpp 116/128/210/219/249/250/1383",
        "Spell.cpp 3863-3865/3869/3872/5600/6373",
        "Player.cpp 5410/5412/5421-5422/5433/5435",
        "World.cpp 629-630/784-787",
        "NPCHandler.cpp 97/112/127/130/137",
        "Trainer.cpp 41/58/76/79/98-100/102/106/149",
        "SharedDefines.h 5901/6366",
        "QuestDef.h 132, ItemTemplate.h 218, Loot.h 115",
    ]
    for s in src:
        chk(f"source: {s[:54]}", norm(s) in n)


def hygiene_and_guard_checks(t):
    try:
        t.encode("ascii")
        chk("ascii", True)
    except UnicodeEncodeError:
        chk("ascii", False)
    over = [i + 1 for i, l in enumerate(t.splitlines()) if len(l) > 100]
    chk("no line > 100 cols", not over)
    chk("no trailing whitespace", not any(l != l.rstrip() for l in t.splitlines()))
    chk("no tabs", "\t" not in t)
    chk("no TODO/FIXME", "TODO" not in t and "FIXME" not in t)
    chk("unverified marker present", t.count("unverified") >= 20)
    chk("no CRLF", "\r" not in t)
    chk("no leftover Felix typo", "Felix" not in t)
    forbidden = ["25229", "25230", "158750", "195116", "264507", "264508",
                 "264509", "264510", "265809", "265810", "265811", "265812",
                 "45357", "51005", "201700", "201703", "201704", "169926",
                 "115359", "40523", "31252", "264494", "264495", "264496",
                 "264497", "264498", "264499", "264500", "264501", "264502",
                 "264503", "264504", "264505", "264506", "161789", "111923"]
    for f in forbidden:
        chk(f"no sibling id {f}", f not in t)
    chk("755/773 not used as skills", not re.search(r"\b755\b", t) and
        not re.search(r"\b773\b", t))
    chk("shared quest 43341 allowed", "43341" in t)


def run_all(t):
    CHECKS.clear()
    section_checks(t)
    learn_map_checks(t)
    trainer_checks(t)
    route_checks(t)
    totals_checks(t)
    materials_costs_level_checks(t)
    tc_checks(t)
    cannot_do_checks(t)
    conflicts_checks(t)
    sources_checks(t)
    hygiene_and_guard_checks(t)
    return CHECKS


MUTATIONS = [
    ("base id 2108 -> 2109", "Base spell: Leatherworking 2108",
     "Base spell: Leatherworking 2109"),
    ("Classic sub-skill 2532 -> 2533", "Classic Leatherworking skill=2532",
     "Classic Leatherworking skill=2533"),
    ("total 323 -> 324", "guide = 323 (19 + 10", "guide = 324 (19 + 10"),
    ("total 367 -> 368", "guide = 367 (5 + 5", "guide = 368 (5 + 5"),
    ("total 230 -> 231", "guide = 230 (25 + 25", "guide = 231 (25 + 25"),
    ("skill id 165 -> 166", "SKILL_LEATHERWORKING = 165 (SharedDefines.h 5901)",
     "SKILL_LEATHERWORKING = 166 (SharedDefines.h 5901)"),
    ("QuestDef line 132 -> 133", "QUEST_TRSKILL_LEATHERWORKING = 8 (QuestDef.h 132)",
     "QUEST_TRSKILL_LEATHERWORKING = 8 (QuestDef.h 133)"),
    ("NotEnoughMoney renamed", "SendTeachFailure NotEnoughMoney",
     "SendTeachFailure NotEnoughGold"),
    ("orange weight 100 -> 99", "SkillChance.Orange 100 /",
     "SkillChance.Orange 99 /"),
    ("wiki row count 52 -> 51", "Leatherworking_trainers (52 rows, page includes the BfA pair",
     "Leatherworking_trainers (51 rows, page includes the BfA pair"),
    ("BfA cap 1-175 -> 1-150", "(Kul Tiran/Zandalari) 1-175",
     "(Kul Tiran/Zandalari) 1-150"),
    ("trainer coord drift", "Dun Morogh [53.7, 52]", "Dun Morogh [53.7, 53]"),
    ("block-end probe 264594 -> 264595",
     "264594 answers \"Spell #264594 doesn't exist\"",
     "264595 answers \"Spell #264594 doesn't exist\""),
    ("total 77 -> 78", "guide = 77 (10 + 22", "guide = 78 (10 + 22"),
    ("Nylon Thread unverified -> id",
     "200 Nylon Thread - id unverified); learn the recipe at Nazjatar",
     "200 Nylon Thread 152576); learn the recipe at Nazjatar"),
    ("non-ascii injection", "CHEAPEST ROUTE", "CHEAPESTé ROUTE"),
    ("line longer than 100 cols",
     "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - LEATHERWORKING CRAFTING FOR A SERVER-SIDE COMPANION",
     "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - LEATHERWORKING CRAFTING FOR A SERVER-SIDE COMPANION PAD PAD PAD"),
    ("renumber conflict 17)", "17) Historic rows kept for context",
     "18) Historic rows kept for context"),
    ("Warhide count 810 -> 800", "(810 Stonehide Leather",
     "(800 Stonehide Leather"),
    ("scope build 8.3.7 -> 8.4.0",
     "TrinityCore-based 8.3.7 server", "TrinityCore-based 8.4.0 server"),
]


def self_test():
    base = load()
    print(f"Self-test: {len(MUTATIONS)} mutations against pristine file")
    pristine = run_all(base)
    p_pass = sum(1 for _, ok in pristine if ok)
    print(f"Pristine: {p_pass}/{len(pristine)} pass")
    if p_pass != len(pristine):
        for d, ok in pristine:
            if not ok:
                print(f"  PRISTINE FAIL: {d}")
        print("SELF-TEST ABORT: pristine not green")
        return 1
    failures = 0
    for label, old, new in MUTATIONS:
        if old not in base:
            print(f"  {label}: TARGET NOT FOUND (bad mutation)")
            failures += 1
            continue
        mutated = base.replace(old, new, 1)
        if mutated == base:
            print(f"  {label}: NO-OP (bad mutation)")
            failures += 1
            continue
        res = run_all(mutated)
        caught = [d for d, ok in res if not ok]
        if caught:
            print(f"  {label}: caught by {len(caught)} check(s) -> {caught[0][:70]}")
        else:
            print(f"  {label}: NOT CAUGHT")
            failures += 1
    if failures:
        print(f"SELF-TEST FAIL ({failures}/{len(MUTATIONS)} missed or invalid)")
        return 1
    print(f"SELF-TEST PASS ({len(MUTATIONS)}/{len(MUTATIONS)} mutations caught)")
    return 0


def main():
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    t = load()
    res = run_all(t)
    passed = sum(1 for _, ok in res if ok)
    failed = [(d, ok) for d, ok in res if not ok]
    for d, _ in failed:
        print(f"FAIL: {d}")
    print(f"CHECKS: {passed}/{len(res)} pass, {len(failed)} fail")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
