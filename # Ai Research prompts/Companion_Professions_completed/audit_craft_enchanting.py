#!/usr/bin/env python3
"""Audit for Craft_Enchanting.txt (Companion_Professions, RESEARCH_MASTER STEP 128).

Static checks: every payload must appear verbatim in the deliverable unless
kind=re (regex, MULTILINE). Derived checks recompute sums from the file's own
numbers. --self-test mutates the file in memory; every mutation must fail
at least one check.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "Craft_Enchanting.txt"
RAW = TARGET.read_text(encoding="utf-8")

# kind: "lit" = substring, "re" = MULTILINE regex over the full text.
CHECKS = [
    # --- heading / scope -------------------------------------------------
    ("H01 heading", "re", r"^BATTLE FOR AZEROTH 8\.3\.7 \(BUILD 35662\) - ENCHANTING CRAFTING FOR A SERVER-SIDE COMPANION$"),
    ("H02 underline", "re", r"^={20,}$"),
    ("H03 scope unverified", "lit", 'says "unverified" instead of a guess'),
    ("H04 section 1", "lit", "1. THE SKILL LINES AND HOW A COMPANION LEARNS THEM"),
    ("H05 section 2", "lit", "2. TRAINERS AND THEIR POSITIONS"),
    ("H06 section 3", "lit", "3. CHEAPEST ROUTE 1 TO THE CAP OF EACH LINE"),
    ("H07 section 4", "lit", "4. MATERIALS AND WHERE EACH COMES FROM"),
    ("H08 section 5", "lit", "5. TRAINER COSTS"),
    ("H09 section 6", "lit", "6. LEVEL NEEDED"),
    ("H10 section 7", "lit", "7. WHAT THE CORE MUST DO FOR A CRAFT TO SUCCEED"),
    ("H11 section 8", "lit", "8. WHAT A SERVER-SIDE CHARACTER (NO CLIENT) CANNOT DO"),
    ("H12 section 9", "lit", "9. CONFLICTS AND UNVERIFIED INDEX"),
    ("H13 section 10", "lit", "10. SOURCES"),
    ("H14 subroutes", "re", r"3\.1 Classic 1-300[\s\S]+?3\.8 Battle for Azeroth 1-175"),
    # --- base spell / ranks ---------------------------------------------
    ("B01 base 7411", "lit", "Base spell Enchanting 7411"),
    ("B02 skill333", "lit", "skill=333, value 1"),
    ("B03 trade skill", "lit", "Effect1 = Trade Skill, Effect2 =\nLearn Skill (Enchanting"),
    ("B04 cost10", "lit", '"Training cost:\n10"'),
    ("B05 base text", "re", r"Requires Dusts and\s+Essences found by disenchanting magic items"),
    ("B06 taught47", "lit", '"Taught by (47)" list was not\nrendered'),
    ("B07 rank7412", "re", r"7412 \(50\), 7413 \(125\),"),
    ("B08 rank13920", "re", r"13920 \(200\), 28029 \(275\), 51313 \(350\), 74258 \(425\),\s+110400 \(500\)"),
    ("B09 other ranks", "lit", '"Other ranks (9)"'),
    ("B10 journeyman150", "lit", "maximum potential skill of 150"),
    # --- 8.0.1 learn chains --------------------------------------------
    ("L01 classic2494", "re", r"Classic 1-300, skill=2494:"),
    ("L02 wrap457", "re", r"wrapper 264457 \"Enchanting\" \(added 8\.0\.1"),
    ("L03 457 effects", "re", r"Effect1 Learn Spell 7411,\s+Effect2 Learn Spell 264455,\s+Effect3 Learn Skill Step \(2494\) value 1"),
    ("L04 main455", "re", r"Main 264455 \(8\.0\.1,\s+cap 300\): Effect Learn Skill \(Classic Enchanting,\s+skill=2494\) value 1"),
    ("L05 outland", "re", r"Outland 1-75, skill=2493: main 264460"),
    ("L06 outland chain", "re", r"wrapper 264461 \(8\.1\.0\): Learn Spell 264460 \+\s+Learn Skill Step \(2493\)"),
    ("L07 nr", "re", r"Northrend 1-75, skill=2492: main 264462"),
    ("L08 nr chain", "re", r"wrapper 264463 \(8\.1\.0\): Learn Spell 264462 \+\s+Learn Skill Step \(2492\)"),
    ("L09 cata", "re", r"Cataclysm 1-75, skill=2491: main 264464"),
    ("L10 cata req", "lit", '"Requires Enchanting (1)", "Training cost: 10"'),
    ("L11 cata chain", "re", r"wrapper 264466 \(8\.1\.0, note main\+2 because 264465 is an\s+unrelated spell \"Barrel Aged\"\): Learn Spell 264464 \+\s+Learn Skill Step\s+\(2491\)"),
    ("L12 cata taught9", "re", r"\"Taught by \(9\)\" for 264464"),
    ("L13 cata teachers", "re", r"Alanna Raveneye 3606[\s\S]{0,500}Xylinnia Starshine 7949 \(Feralas\)"),
    ("L14 mop", "re", r"Pandaria 1-75, skill=2489: main 264467 \(cap 75"),
    ("L15 mop chain", "re", r"wrapper 264468 \(8\.1\.0\): Learn Spell 264467 \+\s+Learn Skill Step \(2489\)"),
    ("L16 draenor", "re", r"Draenor 1-100, skill=2488: main 264469 \(8\.0\.1, cap 100\)"),
    ("L17 draenor chain", "re", r"wrapper 264470 \(8\.1\.0\): Learn Spell 264469 \+\s+Learn Skill Step \(2488\)"),
    ("L18 trigger161788", "lit", "Triggered by (1) Learning\n    161788"),
    ("L19 scroll111922", "re", r"scroll item 111922 \"Draenor Enchanting\""),
    ("L20 legion", "re", r"Legion 1-100, skill=2487: main 264471 \(8\.0\.1, cap 100\)"),
    ("L21 legion chain", "re", r"wrapper 264472 \(8\.1\.0\): Learn Spell 264471 \+\s+Learn Skill Step \(2487\)"),
    ("L22 legion reward", "re", r"\"Reward from \(1\)\": quest 39874"),
    ("L23 bfa", "re", r"Battle for Azeroth 1-175, skill=2486 \(one line id, both factions\)"),
    ("L24 kt", "re", r"Alliance 264473 \"Kul Tiran Enchanting\" \(8\.0\.1"),
    ("L25 kt cap", "re", r"cap 175, Alliance Specific Spell,\s+Taught by \(2\): Emily Fairweather 136041 Boralus, Instructor Okanu 153811\s+Nazjatar"),
    ("L26 zal", "re", r"Horde 265805 \"Zandalari Enchanting\" \(added 8\.1\.0"),
    ("L27 zal taught", "re", r"Taught by \(2\): Enchantress Quinni 122702 Dazar'alor, Narv 154393\s+Nazjatar"),
    ("L28 shared2486", "re", r"Both spells' Learn Skill links point at skill=2486"),
    ("L29 no wrapper bfa", "re", r"There is no separate 8\.1\.0 wrapper for BfA"),
    ("L30 boost spell", "lit", 'Spell 201698 "Legion Enchanter"'),
    ("L31 cost raw", "re", r"7411 = 10,\s+264464 = 10, 264473 = 10, 265805 = 10"),
    ("L32 no cost others", "re", r"mains/wrappers for Classic/Outland/\s+Northrend/Pandaria/Draenor/Legion show no Training cost"),
    # --- TC learn path ---------------------------------------------------
    ("T01 npch97", "re", r"NPCHandler\.cpp 97 HandleTrainerListOpcode,\s+112 SendTrainerList, 130 HandleTrainerBuySpellOpcode, 145 interaction guard"),
    ("T02 npc155", "re", r"155\s+trainer->TeachSpell\(npc, _player, packet\.SpellID\)"),
    ("T03 trainer76", "re", r"Trainer\.cpp 76\s+Trainer::TeachSpell"),
    ("T04 discount98", "re", r"98 reputationDiscount = GetReputationPriceDiscount\(npc\)"),
    ("T05 money100", "lit", "100 HasEnoughMoney check"),
    ("T06 modify106", "lit", "106 ModifyMoney(-moneyCost)"),
    ("T07 can149", "re", r"149\s+Trainer::CanTeachSpell"),
    ("T08 freeprof", "re", r"156/165 IsPrimaryProfessionFirstRank \+\s+GetFreePrimaryProfessionPoints = 2-profession limit"),
    ("T09 getstate", "lit", "172 GetSpellState"),
    ("T10 reqskill", "re", r"182 \"if \(trainerSpell->ReqSkillLine && player->GetBaseSkillValue\(\s+trainerSpell->ReqSkillLine\) < trainerSpell->ReqSkillRank\) return\s+SpellState::Unavailable\""),
    ("T11 ability", "re", r"185-186 ReqAbility\s+prerequisite spells"),
    ("T12 levelgate", "lit", "189 level requirement block"),
    ("T13 payload", "re", r"Trainer list payload carries\s+ReqSkillRank/ReqAbility to the client \(Trainer\.cpp 67-68\)"),
    ("T14 skill gate range", "re", r"GetSpellState ReqSkillLine/ReqSkillRank\s+\(Trainer\.cpp 181-183\)"),
    # --- trainers section ------------------------------------------------
    ("C01 wiki page", "lit", "warcraft.wiki.gg/wiki/Enchanting_trainers"),
    ("C02 wembil", "re", r"Wembil Taskwidget, Kharanos, Dun Morogh \[53\.7, 52\.2\]"),
    ("C03 lien", "re", r"Lien Farner, Goldshire, Elwynn \[42, 67\]"),
    ("C04 kitta", "re", r"Kitta Firewind, Tower of Azora, Elwynn \[64\.9, 70\.6\]"),
    ("C05 lucan", "re", r"Lucan Cordell, The Canals, Stormwind \[53, 74\.3\]"),
    ("C06 gimble", "re", r"Gimble Thistlefuzz, The\s+Great Forge, Ironforge \[60, 45\.4\]"),
    ("C07 annora", "re", r"Annora, Uldaman, Badlands \(no coords,\s+\"Will only appear when room is cleared\"\)"),
    ("C08 sedana", "re", r"Sedana, Court of the Sun, Silvermoon \[70, 24\]"),
    ("C09 godan", "re", r"Godan, Godan's Runeworks/The\s+Drag, Orgrimmar \[53\.4, 49\.5\]"),
    ("C10 johan", "re", r"Johan Barnes, Honor Hold, Hellfire \[53\.7, 66\.1\]"),
    ("C11 felannia", "re", r"Felannia, Thrallmar, Hellfire \[52\.3, 36\.1\]"),
    ("C12 andiala", "re", r"Enchantress Andiala,\s+Scryer's Tier, Shattrath \[55\.5, 74\.5\]"),
    ("C13 zurii", "re", r"Zurii, Aldor Rise, Shattrath \[36\.4, 44\.0\]"),
    ("C14 asarnan", "re", r"Asarnan, The Stormspire, Netherstorm \[44\.2, 33\.7\]"),
    ("C15 nalthanis", "re", r"Enchanter Nalthanis, Simply Enchanting/Magus Commerce\s+Exchange, Dalaran \[39\.1, 40\.5\]"),
    ("C16 lai", "re", r"Lai the Spellpaw, Dawn's Blossom, Jade Forest \[46\.8, 42\.9\]"),
    ("C17 bil", "re", r"Bil Sparktonic, Stormshield, Ashran"),
    ("C18 emily wiki", "re", r"Emily Fairweather, Tradewinds Market, Boralus \(Alliance, no\s+coords"),
    ("C19 quinni wiki", "re", r"Enchantress Quinni, Great Seal, Dazar'alor"),
    ("C20 dual dalaran", "re", r"the two Dalaran copies share the layout"),
    ("C21 patch403", "re", r"4\.0\.3a \(2010-11-23\) \"All trainer ranks were\s+removed, allowing any trainer to teach any skill level\""),
    ("C22 patch230", "re", r"2\.3\.0 \(2007-11-13\)\s+enchanting trainers train to Artisan 300"),
    ("C23 cata guide text", "re", r"Visit any trainer in the main\s+cities of old Azeroth"),
    ("C24 nalthanis28693", "re", r"Enchanter Nalthanis\s+npc=28693 at Dalaran \(Northrend\)"),
    ("C25 legion trainer", "re", r"trainer Enchanter Nalthanis\s+npc=93531, quest giver Ildine Sorrowspear npc=93530"),
    ("C26 quest npc list", "re", r"Jace Darkweaver 90317 \(Azsuna\)[\s\S]{0,400}Tigrid the\s+Charmer 98367 \(Stormheim\)"),
    ("C27 outland guides", "re", r"Johan Barnes npc=18773 \(A,\s+Honor Hold\) or Felannia npc=18753 \(H, Thrallmar\)"),
    ("C28 quinni guide", "re", r"Enchantress Quinni\n+\(Terrace of Crafters, Dazar'alor\) and Emily Fairweather \(Tradewinds Market,\s+Boralus\)"),
    ("C29 nazjatar", "re", r"Instructor Okanu 153811 \(A\) and Narv 154393 \(H\)"),
    ("C30 madame ruby", "re", r"Madame Ruby npc=19663 \(Shattrath, limited-supply"),
    ("C31 vanessa", "re", r"Vanessa Sellers npc=32514 \(Northrend Dalaran, 4 Dream\s+Shards each"),
    ("C32 ildine vendors", "re", r"Ildine Sorrowspear 93530 \(Legion: Formula: Ley Shatter 140634"),
    ("C33 toraan", "re", r"Toraan the Revered\s+127151 \(Formula: Chaos Shatter 152658, Argussian Reach - Friendly\)"),
    ("C34 kojo", "re", r"Collector Kojo 134345 \(Tortollan Seekers - Revered:\s+162298/162301\)"),
    ("C35 leedan", "re", r"Leedan Gustaf 142564 \(A\) / Ozgrom Ragefang 142552 \(H\) \(Mark of\s+Honor wand"),
    ("C36 scroll vendors", "re", r"Bil Sparktonic 85914 \(Stormshield\)\s+/ Hane'ke 86027 \(Warspear\) sell scroll 111922"),
    # --- 3.1 Classic route ------------------------------------------------
    ("R01 vanilla guide", "re", r"Vanilla Enchanting Leveling Guide 1-300 \(Midnight\)"),
    ("R02 vellum note", "re", r"Enchanting Vellum 38682 if you can't put it on your own\s+armor because it's too high level"),
    ("R03 rod", "re", r"1-2: 1x Runed Copper Rod item 6218 = 1x Copper Rod 6217"),
    ("R04 minor health", "re", r"2-90: 105x Enchant Bracer: Minor Health spell 7418 = 105x Strange\s+Dust"),
    ("R05 minor sta", "re", r"90-100: 10x Enchant Bracer - Minor Stamina spell 7457 = 30x Strange"),
    ("R06 wand", "re", r"100-110: 10x Greater Magic Wand item 11288 = 10x Simple Wood 4470 \+\s+10x Greater Magic Essence 10939"),
    ("R07 13378", "re", r"110-130: 20x Minor Stamina spell 13378 = 20x Lesser Eternal Essence\s+16202 \+ 40x Light Illusion Dust 16204"),
    ("R08 13501", "re", r"130-160: 33x Enchant Bracer - Lesser Stamina spell 13501 = 66x Light"),
    ("R09 13640", "re", r"160-180: 20x Greater Health spell 13640 = 60x Light Illusion Dust"),
    ("R10 13661", "re", r"180-220: 55x Enchant Bracer: Strength spell 13661 = 55x Light"),
    ("R11 13858", "re", r"220-245: 28x Superior Health spell 13858 = 56x Rich Illusion Dust\s+156930"),
    ("R12 13935", "re", r"245-255: 10x Enchant Boots - Agility spell 13935 = 20x Greater Eternal"),
    ("R13 13939", "re", r"255-260: 5x Enchant Bracer - Greater Strength spell 13939 = 10x Greater"),
    ("R14 20008", "re", r"260-275: 15x Enchant Bracer - Greater Intellect spell 20008 = 45x"),
    ("R15 20012", "re", r"275-290: 15x Greater Agility spell 20012 = 45x Greater Eternal"),
    ("R16 20028", "re", r"290-300: 10x Major Mana spell 20028 = 50x Rich Illusion Dust"),
    ("R17 classic shopping", "re", r"Shopping list \(guide\): 1x 10938, 134x 10940, 10x 10939, 10x 4470,\s+20x 16202"),
    ("R18 classic total", "lit", "Total planned crafts = 337 + rod"),
    # --- 3.2 Outland -----------------------------------------------------
    ("O01 shop", "re", r"630x Arcane Dust 22445, 15x Nightmare Vine 22792,\s+20x Lesser Planar Essence 22447, 25x Greater Planar Essence 22446, 5x Large\s+Prismatic Shard 22449, 12x Void Crystal 22450"),
    ("O02 lesser assault", "re", r"1-10: 9x Lesser Assault spell 34002 = 54x Arcane Dust"),
    ("O03 brawn", "re", r"10-16: 6x Brawn spell 27899 = 36x Arcane Dust"),
    ("O04 armor27961", "re", r"16-30: 16x Major Armor spell 27961 = 128x Arcane Dust"),
    ("O05 34009", "re", r"30-35: 5x Major Stamina spell 34009 = 75x Arcane Dust"),
    ("O06 44383", "re", r"35-40: 5x Armor spell 44383 = 5x Large Prismatic Shard \+ 20x Lesser"),
    ("O07 oil", "re", r"40-50: 15x Superior Wizard Oil item 22522 = 45x Arcane Dust \+ 15x\s+Nightmare Vine \+ 15x Crystal Vial 3371"),
    ("O08 major str", "re", r"50-69: 25x Major Strength spell 33995 = 300x Arcane Dust \+ 25x Greater"),
    ("O09 void sphere", "re", r"69-70: 1x Void Sphere spell 28028 = 2x Void Crystal"),
    ("O10 cooldown", "re", r"Void Sphere every 2 days \(10 days for 5 points"),
    ("O11 alt formulas", "re", r"Formula 22556 Major Agility[\s\S]{0,500}Formula 22555 Major Spellpower \(Blade's Edge\s+mobs\)"),
    ("O12 total", "lit", "Total planned crafts = 82 (excluding the 5-recipe 70-75 alternative)"),
    # --- 3.3 Northrend ---------------------------------------------------
    ("N01 shop", "re", r"310x Infinite Dust 34054, 45x Greater Cosmic Essence\s+34055 \(\+30x more GCE or 60x more Infinite Dust\), 8x Dream Shard 34052,\s+30x Abyss Crystal 34057"),
    ("N02 gatherer", "re", r"1-15: 14x Enchant Gloves: Gatherer spell 44506 = 15x Greater"),
    ("N03 shatter", "re", r"15-30: 20x Abyssal Shatter spell 69412 = 20x Abyss Crystal"),
    ("N04 haste", "re", r"30-40: 10x Enchant Gloves - Haste spell 44484 = 120x Infinite Dust"),
    ("N05 precision", "re", r"40-45: 5x Enchant Gloves - Precision spell 44488 = 20x Greater"),
    ("N06 chest", "re", r"45-55: 10x Enchant Chest: Greater Versatility spell 44509 = 40x Infinite\s+Dust \+ 40x Lesser Cosmic Essence 34056"),
    ("N07 crusher", "re", r"55-60: 5x Enchant Gloves: Crusher spell 60668 = 75x Infinite Dust"),
    ("N08 mighty", "re", r"60-65: 5x Enchant Cloak - Mighty Stamina spell 47672 = 75x Infinite"),
    ("N09 conv", "re", r"conversion spells 44122/44123 verified on the items"),
    ("N10 branch", "re", r"10x Enchant Cloak - Wisdom\s+spell 47899 = 60x Greater Cosmic Essence \+ 10x Abyss Crystal, or 10x\s+Shadow Armor spell 44631 = 120x Infinite Dust \+ 10x Abyss Crystal"),
    ("N11 item37349", "re", r"Formula: Enchant Cloak - Shadow Armor item 37349"),
    ("N12 total", "re", r"Total planned crafts = 79 either branch"),
    # --- 3.4 Cataclysm ---------------------------------------------------
    ("K01 shop", "re", r"591x Hypnotic Dust 52555, 5x Lesser Celestial\s+Essence 52718, 106x Greater Celestial Essence 52719"),
    ("K02 boots", "re", r"1-5: 4x Enchant Boots - Earthen Vitality spell 74189 = 8x Hypnotic"),
    ("K03 cloak", "re", r"5-10: 6x Enchant Cloak - Lesser Power spell 74192 = 18x Hypnotic"),
    ("K04 gloves", "re", r"10-15: 5x Enchant Gloves - Haste spell 74198 = 20x Hypnotic Dust \+\s+5x Lesser Celestial"),
    ("K05 intellect", "re", r"15-25: 10x Enchant Cloak - Intellect spell 74202 = 60x Hypnotic"),
    ("K06 strength", "re", r"25-30: 5x Enchant Gloves - Exceptional Strength spell 74212 = 15x\s+Hypnotic Dust \+ 10x Greater Celestial"),
    ("K07 agility", "re", r"30-35: 5x Enchant Boots - Major Agility spell 74213 = 20x Hypnotic\s+Dust \+ 10x Greater Celestial"),
    ("K08 ghaste", "re", r"35-40: 5x Enchant Gloves - Greater Haste spell 74220 = 25x Hypnotic"),
    ("K09 shield", "re", r"40-45: 5x Enchant Shield - Mastery spell 74226 = 60x Hypnotic Dust"),
    ("K10 bracer", "re", r"45-55: 10x Enchant Bracer - Precision spell 74232 = 120x Hypnotic"),
    ("K11 superior", "re", r"55-60: 5x Superior Intellect spell 74235 = 30x Hypnotic Dust \+ 20x"),
    ("K12 vers", "re", r"60-65: 5x Exceptional Versatility spell 74237 = 45x Hypnotic Dust \+\s+15x Greater Celestial"),
    ("K13 mastery", "re", r"65-75: 17x Enchant Boots - Mastery spell 74238 = 170x Hypnotic Dust \+\s+51x Greater Celestial"),
    ("K14 total", "re", r"material sums reconcile exactly with the shopping\s+list \(591/5/106\)"),
    # --- 3.5 Pandaria ----------------------------------------------------
    ("P01 shop", "re", r"208x Spirit Dust 74249, 76x Mysterious Essence 74250"),
    ("P02 chest", "re", r"1-40: 44x Enchant Chest - Mighty Versatility spell 104393 = 176x"),
    ("P03 boots", "re", r"40-55: 16x Enchant Boots - Greater Haste spell 104407 = 32x Spirit\s+Dust \+ 16x Mysterious"),
    ("P04 gloves", "re", r"55-75: 20x Enchant Gloves - Superior Mastery spell 104420 = 60x"),
    ("P05 alt", "re", r"Greater Protection 104401 if Ethereal Shard 74247"),
    ("P06 total", "re", r"sums reconcile \(208/76\)"),
    # --- 3.6 Draenor -----------------------------------------------------
    ("D01 scroll learn", "re", r"scroll item 111922 \"Draenor Enchanting\" also teaches a few basic\s+recipes"),
    ("D02 vendors", "re", r"Bil Sparktonic 85914 Stormshield \(A\) or Hane'ke 86027 Warspear \(H\)"),
    ("D03 study", "re", r"Enchanter's Study\s+garrison building vendor NPC after quest \"Your First Enchanting Work\s+Order\""),
    ("D04 bracer", "re", r"Enchanted Highmaul\s+Bracer 115350 from Draenor mobs or Karnoth 75043 during Shadows Awaken\s+quest 34019 \(A\) / Dorogg the Ruthless 74254 during The Butcher of\s+Bladespire quest 33410 \(H\)"),
    ("D05 dust", "re", r"1-100: 180x Enchanted Dust spell 162948 = 180x Draenic Dust 109693"),
    ("D06 mark", "re", r"Mark of the Shattered Hand spell 159236 with Temporal\s+Crystal 113588"),
    ("D07 total", "lit", "Total planned crafts = 180 (+ a few Marks at the end)"),
    # --- 3.7 Legion ------------------------------------------------------
    ("G01 learn quest", "re", r"quest 39874 \"Some Enchanted Evening\", requires level 10, from\s+Enchanter Nalthanis 93531"),
    ("G02 chain mats", "re", r"54x Arkhana 124440, 15x Leylight Shard\s+124441, 5x Enchanting Vellum 38682"),
    ("G03 quest list", "re", r"guide lists all 29 quests: 39874,"),
    ("G04 raven", "re", r"Enchanted Raven Sigil\s+137221 from Black Rook Hold mobs"),
    ("G05 instances", "re", r"clear Neltharion's\s+Lair, The Stonecore and Scholomance"),
    ("G06 de route", "re", r"19 easy skill points by Disenchanting any\s+item from the Broken Isles"),
    ("G07 lfr", "re", r"Archmage Timear 111246 in Dalaran\s+queues the Raid Finder wings"),
    ("G08 chaos", "re", r"50\s+Chaos Crystal 124442"),
    ("G09 chaos shatter", "re", r"Chaos Shatter spell 252106 = 1x Chaos Crystal 124442 -> 2x Leylight\s+Shard 124441"),
    ("G10 ley", "re", r"Ley Shatter spell 224199 = 1x Leylight Shard -> 3x\s+Arkhana 124440"),
    ("G11 formulas", "re", r"Formula: Ley Shatter 140634 sold by Ildine; Formula:\s+Chaos Shatter 152658 sold by Toraan the Revered 127151"),
    ("G12 55 shatter", "re", r"25-70: 55x Chaos Shatter = 55x Chaos Crystal"),
    ("G13 words", "re", r"55x Rank 3 Word of Critical Strike 191009 / Word\s+of Haste 191010 / Word of Mastery 191011 / Word of Versatility 191012"),
    ("G14 uniting", "re", r"Uniting the\s+Isles quest 43341 from Archmage Khadgar 90417 \(level 45"),
    ("G15 bindings", "re", r"70-100: make 30 of ONE of: R3 Binding of Critical Strike 191013 /"),
    ("G16 binding cost", "re", r"120x Chaos Crystal \+ 1050x Arkhana \(4x crystal \+ 35x Arkhana per\s+craft\)"),
    ("G17 r3 sources", "re", r"128600/128602/128603 from First Arcanist Thalyssra\s+97140 \(The Nightfallen - Exalted\), 128601 from Sylvia Hartshorn"),
    ("G18 total", "re", r"Planned crafts: 55 shatters \+ 30 bindings = 85, plus 19 disenchant points"),
    # --- 3.8 BfA ---------------------------------------------------------
    ("A01 shop", "re", r"734x Umbra Shard 152876, 3850x\s+Gloom Dust 152875, 222x Veiled Crystal 152877"),
    ("A02 expulsom", "re", r"87x Expulsom 152668, 12x Mark of Honor\s+137642"),
    ("A03 gloves", "re", r"1-30: 40x any glove enchant that costs 5x Gloom Dust = 200x Gloom\s+Dust"),
    ("A04 seal", "re", r"30-35: 7x any \"Seal of\.\.\.\" ring enchant = 84x Gloom Dust"),
    ("A05 r2 ring", "re", r"35-60: learn the R2 ring enchants from the trainer, then 50x \"Rank 2\s+ring enchant\" = 500x Gloom Dust"),
    ("A06 kojo", "re", r"formula\s+162298/162301 from Collector Kojo 134345"),
    ("A07 wand", "re", r"60-75: 30x Enchanter's Umbral Wand spell 265106 = 30x Star Wood\s+11291 \(bought from the Enchanting Trainer\) \+ 600x Gloom Dust \+ 30x\s+Umbra Shard"),
    ("A08 coastal", "re", r"75-85: 20x Coastal Surge spell 255103 = 100x Umbra Shard \+ 400x Gloom\s+Dust \+ 20x Veiled Crystal"),
    ("A09 deadly", "re", r"85-95: 17x Deadly Navigation spell 268907 = 136x Umbra Shard \+ 340x\s+Gloom Dust \+ 17x Veiled Crystal"),
    ("A10 r2 coastal", "re", r"95-120: learn R2 weapon enchants from the trainer, then 40x Rank 2\s+Coastal Surge spell 255104 = 160x Umbra Shard \+ 720x Gloom Dust \+\s+40x Veiled Crystal"),
    ("A11 scepter", "re", r"Sorcerous Scepter 269715 x10 \(10 Star Wood, 120 Umbra, 30\s+Expulsom\)"),
    ("A12 r3 formulas", "re", r"Coastal Surge 162315 \(Work Order\s+quests 52355 A/52360 H\), Torrent of Elements 162319 \(52356 A/52361 H\)"),
    ("A13 pact", "re", r"120-125: 7x R2 \"Pact of\.\.\.\" ring enchant = 28x Umbra Shard \+ 90x Gloom\s+Dust \+ 35x Veiled Crystal"),
    ("A14 quick", "re", r"125-150: 25x Quick Navigation spell 268895 = 150x Umbra Shard \+ 450x\s+Gloom Dust \+ 25x Veiled Crystal"),
    ("A15 tiki", "re", r"Enchanted Tiki Mask 285644\s+x25 = 500x Gloom Dust \+ 50x Umbra Shard \(formula 165696 drops from\s+King Rastakhan 145616"),
    ("A16 150-155", "re", r"Horde: visit Narv 154393 in Nazjatar"),
    ("A17 accord", "re", r"5x Accord of Critical Strike 298009 =\s+25x Veiled Crystal \+ 20x Umbra Shard \+ 90x Gloom Dust"),
    ("A18 notorious", "re", r"Dazzerian 154652 \(H\) / Crafticus Mindbender\s+154653 \(A\) at Nazjatar and craft R2 294782 x15"),
    ("A19 force", "re", r"155-165: 10x Force Multiplier 298440 = 60x Umbra Shard \+ 250x Gloom\s+Dust \+ 30x Veiled Crystal"),
    ("A20 r2 force", "re", r"165-175: learn the R2 recipes from the trainer, then 10x Rank 2 Force\s+Multiplier 298439 = 50x Umbra Shard \+ 220x Gloom Dust \+ 30x Veiled"),
    ("A21 r3 notch", "re", r"R3 formula 169540 for 4x Mark of\s+Honor"),
    ("A22 war campaign", "re", r"Uniting Kul Tiras\s+quest 51918 \(A\) / Uniting Zandalar 51916"),
    ("A23 total", "re", r"Total planned crafts \(main path, no wands\): 40\+7\+50\+30\+20\+17\+40\+7\+25\+5\+\s+10\+10 = 261"),
    # --- 4 materials -----------------------------------------------------
    ("M01 wiki disenchant", "re", r"wiki/Enchanting section\n+\"Disenchanting\""),
    ("M02 legendary", "re", r"Legendary\s+items cannot be disenchanted"),
    ("M03 table", "re", r"Dust - mostly uncommon armor, less often uncommon\s+weapons"),
    ("M04 shard", "re", r"Shard - usually rare\s+items, rarely uncommon \(3 lesser -> 1 greater, NOT\s+back\)"),
    ("M05 crystal", "re", r"Crystal - always\s+epic, rarely rare"),
    ("M06 spell13262", "re", r"Disenchant spell 13262\s+\"is a spell that you learn when you acquire Enchanting from your profession\s+trainer\""),
    ("M07 scaling", "re", r"you can no longer sort enchanting results just based\s+on item level"),
    ("M08 735", "re", r"wiki patch 7\.3\.5: materials\s+\"now based on the item's\s+expansion level instead of item level\""),
    ("M09 classic ids", "re", r"Strange Dust 10940, Lesser Magic Essence 10938, Greater Magic\s+Essence 10939, Light Illusion Dust 16204, Lesser Eternal Essence 16202"),
    ("M10 shards classic", "re", r"Small Brilliant Shard 14343, Rich Illusion Dust 156930, Greater Eternal\s+Essence 16203, Large Brilliant Shard 14344"),
    ("M11 outland ids", "re", r"Arcane Dust 22445, Lesser Planar Essence 22447, Greater Planar\s+Essence 22446"),
    ("M12 prismatic", "re", r"Small Prismatic Shard 22448, Large Prismatic Shard 22449, Void Crystal\s+22450"),
    ("M13 nv", "re", r"Nightmare Vine 22792 \(herb - Herbalism 365"),
    ("M14 vial", "re", r"Crystal Vial 3371\s+\(vendor, cost field 1-4 on wowhead\)"),
    ("M15 nr ids", "re", r"Infinite Dust 34054, Lesser Cosmic Essence 34056, Greater\s+Cosmic Essence 34055"),
    ("M16 dream", "re", r"Small Dream Shard 34053 \(Use: 3 -> 1 Dream Shard,\s+spell 61755\), Dream Shard 34052, Abyss Crystal 34057"),
    ("M17 cata ids", "re", r"Hypnotic Dust 52555, Lesser Celestial Essence 52718,\s+Greater Celestial Essence 52719, Small Heavenly Shard 52720, Heavenly\s+Shard 52721, Maelstrom Crystal 52722"),
    ("M18 cata conv", "re", r"greater item \"Turn three lesser celestial essences into\s+a greater one\" \(spell 74186\), lesser item \"Turn a greater celestial\s+essence into three lesser ones\" \(spell 74187\)"),
    ("M19 mop ids", "re", r"Spirit Dust 74249, Mysterious Essence 74250, Small Ethereal\s+Shard 74252, Ethereal Shard 74247, Sha Crystal 74248"),
    ("M20 mop conv", "re", r"Mysterious Diffusion spell 118237 \(Enchanting 535\),\s+Ethereal Shatter spell 118238 \(Enchanting 585\)"),
    ("M21 wod ids", "re", r"Draenic Dust 109693, Small Luminous Shard 115502, Luminous\s+Shard 111245, Fractured Temporal Crystal 115504, Temporal Crystal\s+113588"),
    ("M22 legion ids", "re", r"Arkhana 124440, Leylight Shard 124441, Chaos Crystal 124442\."),
    ("M23 bfa ids", "re", r"Gloom Dust 152875, Umbra Shard 152876, Veiled\s+Crystal 152877; Expulsom 152668"),
    ("M24 vellum", "re", r"Enchanting Vellum 38682 \(Inscription-crafted"),
    ("M25 starwood", "re", r"Star Wood 11291 \(Enchanting\s+trainer vendor, BfA wand reagent\)"),
    ("M26 shatters", "re", r"Void Shatter 45765 \(Outland Enchanting 60, 2x Large Prismatic Shard"),
    ("M27 abyssal", "re", r"Abyssal Shatter 69412 \(NR route, Abyss Crystal ->\s+shards\)"),
    ("M28 veil shatter", "re", r"Veiled Shatter 290361, Umbra\s+Shatter 290360"),
    # --- 5 costs ---------------------------------------------------------
    ("F01 raw fields", "re", r"Learn-spell quick-fact \"Training cost\" \(raw value; wowhead prints no unit"),
    ("F02 list", "re", r"7411 = 10,\s+264464 = 10, 264473 = 10, 265805 = 10"),
    ("F03 no cost", "re", r"264455, 264457, 264460, 264461, 264462, 264463, 264466, 264467,\s+264468, 264469, 264470, 264471, 264472 show no Training cost"),
    ("F04 conflict pattern", "re", r"Same conflict pattern as Blacksmithing/Alchemy"),
    ("F05 10c wiki", "re", r"warcraft\.wiki's classic row for professions prints \"10 c\""),
    ("F06 moneycost", "re", r"price = trainer-spell MoneyCost x\n+GetReputationPriceDiscount\(npc\) \(Trainer\.cpp 98\)"),
    ("F07 150", "re", r"Coastal Surge 255103\n+\"Training cost: 150\" and detail line \"Trainer: Enchantress Quinni - Zone:\s+Zuldazar - Cost: 150\""),
    ("F08 4ds", "re", r"Vanessa Sellers charges 4 Dream Shards per\s+formula"),
    ("F09 annora gold", "re", r"11\.79 Gold to learn everything\s+from Annora"),
    ("F10 marks", "re", r"6x buys R2\+R3 wand recipes from Leedan/Ozgrom \(guide wording\),\s+2x buys the R2 Nazjatar wand recipe, 4x buys R3 formula 169540"),
    ("F11 25g", "re", r"trainer-formula table\s+on wowpedia prints \"Battle for Azeroth\s+trainer\s+25 g\""),
    ("F12 unverified", "re", r"Where a price is not quoted above, treat it as\s+unverified rather than\s+assuming"),
    # --- 6 level ---------------------------------------------------------
    ("V01 lvl5", "re", r"can be trained as early as level\s+5"),
    ("V02 58 outland", "re", r"Outland: warcraft\.wiki Outland formulas page - \"as early as level 58\""),
    ("V03 58 nr", "re", r"Northrend: warcraft\.wiki Northrend formulas page - \"as early as level\s+58\""),
    ("V04 unknowns", "re", r"Cataclysm/Pandaria/Draenor: no character-level line was read"),
    ("V05 legion10", "re", r"current quest 39874 requires level 10"),
    ("V06 legion98", "re", r"\"trained as early as level 98\" \(original\s+7\.0 gate\)"),
    ("V07 bfa unknown", "re", r"Battle for Azeroth: no character-level line printed"),
    ("V08 broken tpl", "re", r"trained as early as level\s+TBC\" - the template failed"),
    ("V09 caps table", "re", r"Classic ranks 1-75/75-150/150-225/225-300"),
    ("V10 82 note", "re", r"8\.2\.0\)\"\) - use 175 for 8\.3\.7"),
    ("V11 prof gates", "re", r"\"Profession: Enchanting\s+\(1\)\" on 7418; \"Profession: Battle for Azeroth Enchanting \(40\)\" on Coastal\s+Surge 255103"),
    ("V12 skill columns", "re", r"7418 quick fact \"Skill: Classic Enchanting\""),
    ("V12b kul tiran col", "re", r"\"Skill: Kul Tiran Enchanting\""),
    ("V13 no craft gate", "re", r"There is no server-side craft-time skill check for enchant recipes"),
    # --- 7 core ----------------------------------------------------------
    ("W01 eip", "re", r"SpellEffects\.cpp 2463\s+EffectEnchantItemPerm \(registered for effect 53 SPELL_EFFECT_ENCHANT_ITEM\s+at table line 145\)"),
    ("W02 vellum", "re", r"if the target IsVellum \(2476\)"),
    ("W03 docreate", "re", r"creates the scroll via DoCreateItem\s+\(effectInfo->ItemType, Trade_Skill context\)"),
    ("W04 miscvalue", "re", r"enchant_id = effectInfo->MiscValue, looks up\s+SpellItemEnchantmentEntry \(2494-2498\)"),
    ("W05 take", "re", r"Spell\.cpp 3871/3876 TakeReagents\(\)\s+\(definition 5599\)"),
    ("W06 invfull", "re", r"report inventory full \(1440\s+EQUIP_ERR_INV_FULL \|\| EQUIP_ERR_ITEM_MAX_COUNT ->\s+SendEquipError"),
    ("W07 cast time", "re", r"Recipes print 2-second cast \(7418, 255103\) and tools \"Runed Enchanting\s+Rod\""),
    ("W08 504", "re", r"wiki patch 5\.0\.4: \"All enchantments\s+now only require Runed Copper Rod\""),
    ("W09 vellum owner", "re", r"7668-7670 \"cannot enchant vellum for other player\" ->\s+SPELL_FAILED_NOT_TRADEABLE"),
    ("W10 exploit", "re", r"vellum is blocked \(7671-7674, ITEM_FLAG_NO_REAGENT_COST\s+->\s+SPELL_FAILED_TOTEM_CATEGORY\)"),
    ("W11 notfound", "re", r"Item target required \(7687 SPELL_FAILED_ITEM_NOT_FOUND\)"),
    ("W12 baselevel", "re", r"target's\s+required level \(or item level if none\) must reach the spell's\s+BaseLevel \(7691-7697 -> SPELL_FAILED_LOWLEVEL\)"),
    ("W13 maxlevel", "re", r"target item level above the spell's MaxLevel ->\s+SPELL_FAILED_HIGHLEVEL \(7699-7701\)"),
    ("W14 caps printed", "re", r"\"Cannot be applied to items higher than level 120\" \(7418, cata\s+scrolls 52750-52753, BfA 255103 all print a level-120 cap"),
    ("W15 136", "re", r"\"items higher than level 136\" on wowpedia's Spellpower page"),
    ("W16 onuse", "re", r"SPELL_FAILED_ON_USE_ENCHANT \(7716-7723\)"),
    ("W17 trade", "re", r"soulbound enchant flag ->\s+SPELL_FAILED_NOT_TRADEABLE \(7741-7746\)"),
    ("W18 temp", "re", r"Temporary enchants repeat the level floor/cap \(7754-7777\)"),
    ("W19 skill guard", "re", r"SpellEffects\.cpp 2490-2492\s+\(\"// do not increase skill if vellum used\" comment sits above"),
    ("W20 updatecraft", "re", r"`if \(!m_CastItem\) player->UpdateCraftSkill\(m_spellInfo\);`"),
    ("W21 vellum noskill", "re", r"the vellum branch at 2476-2486 makes no UpdateCraftSkill call at all"),
    ("W22 player body", "re", r"UpdateCraftSkill: Player\.cpp 5410, early-out SPELL_ATTR1_NO_SKILL_\s+INCREASE 5412"),
    ("W23 discovery", "re", r"discovery branch\s+MECHANIC_DISCOVERY 5427-5431"),
    ("W24 gain", "re", r"gain = NumSkillUps x\s+CONFIG_SKILL_GAIN_CRAFTING 5433"),
    ("W25 sites", "re", r"DoCreateItem success 1469, EffectCreateItem2 loot\s+crafting 1499, disenchant 3533, and Spell\.cpp 3864"),
    ("W26 colors", "re", r"orange always, yellow probably,\s+green probably not, grey never"),
    ("W27 de handler", "re", r"handler table SpellEffects\.cpp 191 = EffectDisEnchant for effect 99\s+SPELL_EFFECT_DISENCHANT"),
    ("W28 de body", "re", r"body 3525-3538: skill via UpdateCraftSkill\s+3533"),
    ("W29 loot", "re", r"FillLoot on the item's\s+GetDisenchantLootId\(\) with LootTemplates_Disenchant \(LOOT_DISENCHANTING\)"),
    ("W30 de gate", "re", r"GetDisenchantSkillRequired\(\) must be present \(7797\) and\s+<= GetSkillValue\(SKILL_ENCHANTING\) \(7800 -> SPELL_FAILED_CANT_BE_\s+SALVAGED_SKILL at 7801\)"),
    ("W31 learn effects", "re", r"8\.0\.1 mains use Learn Skill \(line id\)\s+value 1 with cap in the text"),
    ("W32 classic triple", "re", r"Classic wrapper 264457 additionally\s+learns 7411 \(trade skill \+ skill 333\) and 264455 \(line 2494\)"),
    # --- 8 cannot --------------------------------------------------------
    ("X01 be", "re", r"Arcane Affinity 28877 is a\s+racial Apply Aura: Mod Skill \(Enchanting\) value 5"),
    ("X02 visage", "re", r"Dracthyr Visage \(races 75/76\)"),
    ("X03 reps", "re", r"Tortollan\s+Revered \(Kojo formulas\), Nightfallen/Dreamweavers Exalted \(R3\s+Bindings\)"),
    ("X04 wq", "re", r"World Quest\s+rotation \(BfA R3 work orders; Legion WQs every 2-3 days"),
    ("X05 cd", "re", r"Void Sphere's 2-day\s+cooldown route"),
    ("X06 places", "re", r"Annora is inside Uldaman"),
    ("X07 instances", "re", r"the Legion chain needs Darkheart Thicket, Halls of Valor"),
    ("X08 lfr", "re", r"Raid Finder farming needs the queue NPC path \(Archmage Timear\)"),
    ("X09 ah", "re", r"server-side character has no AH/mail UI"),
    ("X10 vellum noskill", "re", r"the TC vellum path grants no skill\s+point \(section 7d\)"),
    ("X11 foreign", "re", r"soulbound-flag enchants on foreign items\s+fail \(Spell\.cpp 7746\)"),
    ("X12 profs", "re", r"CanTeachSpell's free primary\s+profession point gate \(Trainer\.cpp 156\)"),
    ("X13 ui", "re", r"rank-star hover sources, red/yellow/\s+green recipe colours in the window"),
    ("X14 stale", "re", r"while the patch note says ranks were removed -\s+use the patch note"),
    # --- 9 conflicts -----------------------------------------------------
    ("Y01 c1", "re", r"1\) BfA cap: warcraft\.wiki training table says 1-150; both learn spells and\s+both leveling guides say 175"),
    ("Y02 c2", "re", r"2\) wow-professions' BfA overview page says \"maximum of 176 skill points\""),
    ("Y03 c3", "re", r"3\) Blood Elf bonus: wiki perks section says \"\+10\"; spell 28877 effect\s+value 5"),
    ("Y04 c4", "re", r"4\) Vellum skill: wiki Trading section says"),
    ("Y05 c5", "re", r"5\) Cosmic conversion counts"),
    ("Y06 c6", "re", r"6\) Outland guide crosslink"),
    ("Y07 c7", "re", r"7\) Northrend guide's Wisdom formula link points at item 44488"),
    ("Y08 c8", "re", r"8\) Legion chain ownership"),
    ("Y09 c9", "re", r"9\) Legion gating levels: 10 \(current wowhead\), 98 \(wowpedia original\)"),
    ("Y10 c10", "re", r"10\) Classic apprentice level"),
    ("Y11 c11", "re", r"11\) Training-cost units"),
    ("Y12 c12", "re", r"12\) BfA trainer coordinates"),
    ("Y13 c13", "re", r"13\) Who teaches Classic wrapper 264457 now"),
    ("Y14 c14", "re", r"14\) Wowpedia BfA formulas header prints \"trained as early as level TBC\""),
    ("Y15 c15", "re", r"15\) wowpedia says Northrend enchanting \"as early as level 58\""),
    ("Y16 c16", "re", r"16\) Draenor wrapper 264470 \"Triggered by \(1\) Learning 161788\""),
    ("Y17 c17", "re", r"17\) Enchanted Tiki Mask \"100% drop\""),
    ("Y18 c18", "re", r"18\) Outland guide's Superior Wizard Oil step"),
    ("Y19 c19", "re", r"19\) Cataclysm guide's yellow-warning steps"),
    # --- 10 sources ------------------------------------------------------
    ("Z01 date", "re", r"All fetched 2026-10-26 week"),
    ("Z02 spells list", "re", r"7411 \(base \+ other ranks 158716/195096/7412/7413/\s+13920/28029/51313/74258/110400\)"),
    ("Z03 probes", "re", r"wowhead item pages probed for ids:"),
    ("Z04 search ids", "re", r"Guide-hub search results \(record id/url\)"),
    ("Z05 url classic skill", "lit", "https://www.wowhead.com/skill=2494/classic-enchanting"),
    ("Z06 url vanilla", "lit", "https://www.wow-professions.com/guides/vanilla-enchanting-leveling"),
    ("Z07 url bfa guide", "lit", "https://www.wow-professions.com/guides/zandalari-kul-tiran-bfa-enchanting-leveling-guide"),
    ("Z08 url outland spell", "lit", "https://www.wowhead.com/spell=264460/outland-enchanting"),
    ("Z09 url nr spell", "lit", "https://www.wowhead.com/spell=264462/northrend-enchanting"),
    ("Z10 url legion spell", "lit", "https://www.wowhead.com/spell=264471/legion-enchanting"),
    ("Z11 url quest", "lit", "https://www.wowhead.com/quest=39874/some-enchanted-evening"),
    ("Z12 url nv", "lit", "https://www.wowhead.com/item=22792/nightmare-vine"),
    ("Z13 url cata conv", "lit", "https://www.wowhead.com/spell=74187/lesser-celestial-essence"),
    ("Z13b url cata conv2", "lit", "https://www.wowhead.com/cata/spell=74186/greater-celestial-essence"),
    ("Z14 guides slugs", "re", r"wow-professions guides \(full slugs\): vanilla-enchanting-leveling;\s+outland-enchanting-leveling; northrend-enchanting-leveling;\s+cataclysm-enchanting-leveling; pandaria-enchanting-leveling;\s+draenor-enchanting-leveling; legion-enchanting-leveling;"),
    ("Z15 de guide", "lit", "wow-disenchanting-guide"),
    ("Z16 wiki pages", "re", r"warcraft\.wiki\.gg pages: Enchanting \(training table, requirements, perks"),
    ("Z17 trainers chunks", "re", r"Enchanting_trainers \(5 chunks, all\s+coords above \+ 4\.0\.3a/2\.3\.0 patches\)"),
    ("Z18 wowpedia", "re", r"wowpedia\.fandom\.com: Classic_enchanting_formulas \(level 5, 300 cap\)"),
    ("Z19 tc files", "re", r"TrinityCore master, fetched this week with the GitHub contents API and a\s+blobless sparse clone"),
    ("Z20 tc spell", "re", r"Spells/Spell\.cpp\s+\(3864, 3871/3876, 5599, 7664-7678, 7691-7701, 7716-7763, 7784-7804\)"),
    ("Z21 tc effects", "re", r"Spells/SpellEffects\.cpp \(145, 191, 1440, 1469, 1499, 2463-2527, 3525-3538\)"),
    ("Z22 tc player", "re", r"Entities/Player/Player\.cpp \(5410-5437\)"),
    ("Z23 tc npc", "re", r"Handlers/NPCHandler\.cpp \(97, 112,\s+130, 145, 155\)"),
    ("Z24 tc trainer", "re", r"Entities/Creature/Trainer\.cpp \(67-68, 76, 98-106, 149,\s+156, 165, 172, 181-191\)"),
]

SECTION_HEADS = [
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


def run_checks(text):
    failures = []
    for name, kind, payload in CHECKS:
        if kind == "lit":
            ok = payload in text
        elif kind == "re":
            ok = re.search(payload, text, re.M) is not None
        else:
            raise ValueError((name, kind))
        if not ok:
            failures.append(name)
    order = []
    for idx, ln in enumerate(text.split("\n"), 1):
        if ln in SECTION_HEADS:
            order.append((ln, idx))
    if [h for h, _ in order] != SECTION_HEADS:
        failures.append("ORDER section headings sequential")
    elif order[0][1] != 8:
        failures.append("ORDER section 1 on line 8 (was %s)" % order[0][1])
    return failures


def derived_checks(text):
    failures = []

    def num(pattern, group=1, default=None):
        m = re.search(pattern, text, re.M)
        return int(m.group(group)) if m else default

    classic = [1, 105, 10, 10, 20, 33, 20, 55, 28, 10, 5, 15, 15, 10]
    total = num(r"Total planned crafts = (\d+) \+ rod")
    if total != sum(classic) or sum(classic) != 337:
        failures.append("D01 classic craft sum %s != %s" % (total, sum(classic)))
    outland = [9, 6, 16, 5, 5, 15, 25, 1]
    total = num(r"Total planned crafts = (\d+) \(excluding the 5-recipe")
    if total != sum(outland) or sum(outland) != 82:
        failures.append("D02 outland craft sum %s != %s" % (total, sum(outland)))
    nr = [14, 20, 10, 5, 10, 5, 5, 10]
    total = num(r"Total planned crafts = (\d+) either branch")
    if total != sum(nr) or sum(nr) != 79:
        failures.append("D03 northrend craft sum %s != %s" % (total, sum(nr)))
    cata = [4, 6, 5, 10, 5, 5, 5, 5, 10, 5, 5, 5, 17]
    if sum(cata) != 87:
        failures.append("D04 cata craft sum math")
    if not re.search(r"shopping\s+list \(591/5/106\)", text):
        failures.append("D04b cata reconciliation marker")
    hd = [8, 18, 20, 60, 15, 20, 25, 60, 120, 30, 45, 170]
    lce = [5]
    gce = [10, 10, 20, 15, 51]
    if (sum(hd), sum(lce), sum(gce)) != (591, 5, 106):
        failures.append("D05 cata material math")
    mop_crafts = [44, 16, 20]
    if sum(mop_crafts) != 80 or not re.search(r"sums reconcile \(208/76\)", text):
        failures.append("D06 mop reconciliation marker")
    sd = [176, 32]
    me = [16, 60]
    if (sum(sd), sum(me)) != (208, 76):
        failures.append("D07 mop material math")
    bfa = [40, 7, 50, 30, 20, 17, 40, 7, 25, 5, 10, 10]
    total = num(r"40\+7\+50\+30\+20\+17\+40\+7\+25\+5\+\s+10\+10 = (\d+)")
    if total != sum(bfa) or sum(bfa) != 261:
        failures.append("D08 bfa craft sum %s != 261" % total)
    if not re.search(r"55 shatters \+ 30 bindings = 85", text):
        failures.append("D09 legion planned sum")
    key_ids = [
        7411, 7412, 7413, 13920, 28029, 264455, 264457, 264460, 264461,
        264462, 264463, 264464, 264466, 264467, 264468, 264469, 264470,
        264471, 264472, 264473, 265805, 111922, 39874, 7418, 7457, 11288,
        13378, 13501, 13640, 13661, 13858, 13935, 13939, 20008, 20012,
        20028, 34002, 27899, 27961, 34009, 44383, 22522, 33995, 28028,
        44506, 69412, 44484, 44488, 44509, 60668, 47672, 47899, 44631,
        74189, 74192, 74198, 74202, 74212, 74213, 74220, 74226, 74232,
        74235, 74237, 74238, 104393, 104407, 104420, 162948, 159236,
        252106, 224199, 191009, 191013, 255103, 255104, 268907, 265106,
        269715, 269719, 268895, 285644, 298009, 294781, 294782, 298440,
        298439, 294783, 333, 2494, 2493, 2492, 2491, 2489, 2488, 2487,
        2486, 10940, 10938, 10939, 4470, 16202, 16204, 16203, 156930,
        14343, 14344, 22445, 22447, 22446, 22448, 22449, 22450, 22792,
        3371, 34054, 34056, 34055, 34053, 34052, 34057, 52555, 52718,
        52719, 74249, 74250, 74247, 109693, 113588, 124440, 124441,
        124442, 152875, 152876, 152877, 38682, 6217, 6218, 11291,
    ]
    missing = [i for i in key_ids if str(i) not in text]
    if missing:
        failures.append("D10 key id coverage missing: %s" % missing[:12])
    for fam in ["5410", "3525", "2463", "7664", "172", "130"]:
        if fam not in text:
            failures.append("D11 missing TC family %s" % fam)
    conf = re.findall(r"^(\d{1,2})\) ", text, re.M)
    if len(conf) < 19:
        failures.append("D12 conflict items %d < 19" % len(conf))
    return failures


def preflight():
    misses = [
        n for n, k, p in CHECKS
        if (p not in RAW if k == "lit" else not re.search(p, RAW, re.M))
    ]
    if misses:
        print("PREFLIGHT %d payload misses:" % len(misses))
        for m in misses:
            print("  -", m)
        return False
    return True


def self_test():
    mutations = []
    for label, old, new in [
        ("skill id", "skill=333", "skill=999"),
        ("outland main id", "264460", "264461x"),
        ("cata dust count", "591x Hypnotic Dust", "592x Hypnotic Dust"),
        ("classic total", "Total planned crafts = 337 + rod", "Total planned crafts = 338 + rod"),
        ("tc skill gate line", "181-183", "181-184"),
        ("gloom dust id", "Gloom Dust 152875", "Gloom Dust 152876"),
        ("npc entry", "Emily Fairweather 136041", "Emily Fairweather 999999"),
        ("legion level", "requires level 10, from", "requires level 11, from"),
        ("bfa cap", "cap 175, Alliance Specific", "cap 150, Alliance Specific"),
        ("crusher spell", "spell 60668", "spell 60669"),
        ("de fail line", "SALVAGED_SKILL at 7801", "SALVAGED_SKILL at 7802"),
        ("draenor scroll", "scroll item 111922", "scroll item 111923"),
        ("outland total", "Total planned crafts = 82", "Total planned crafts = 83"),
        ("conflict count", "19) Cataclysm guide", "19a Cataclysm guide"),
    ]:
        mutations.append((label, RAW.replace(old, new)))
    results = []
    for label, mutated in mutations:
        fails = run_checks(mutated) + derived_checks(mutated)
        results.append((label, fails))
    bad = [(l, f) for l, f in results if not f]
    for l, f in results:
        status = "caught by %d" % len(f) if f else "SURVIVED"
        print("  self-test %-22s %s" % (l, status))
    return not bad


def main(argv):
    if "--self-test" in argv:
        print("Running self-test (mutation testing)...")
        ok = self_test()
        print("SELF-TEST %s" % ("PASS" if ok else "FAIL"))
        return 0 if ok else 1

    if not TARGET.exists():
        print("MISSING", TARGET)
        return 2

    fails = run_checks(RAW) + derived_checks(RAW)
    total = len(CHECKS)
    if fails:
        print("FAIL %d checks failed (of %d static):" % (len(fails), total))
        for f in fails:
            print("  -", f)
        return 1
    bad_ascii = [(i, ch) for i, ch in enumerate(RAW) if ord(ch) > 127]
    if bad_ascii:
        print("HYGIENE FAIL: non-ASCII chars:", bad_ascii[:5])
        return 1
    long_lines = [n for n, ln in enumerate(RAW.split("\n"), 1) if len(ln) > 100]
    if long_lines:
        print("HYGIENE FAIL: lines > 100 chars:", long_lines[:10])
        return 1
    print("RESULT: %d PASS, %d FAIL (0)" % (total, len(fails)))
    print("HYGIENE: ASCII only, max line <= 100")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
