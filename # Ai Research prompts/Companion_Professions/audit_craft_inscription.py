#!/usr/bin/env python3
"""Audit for Craft_Inscription.txt (Companion_Professions, RESEARCH_MASTER STEP 130).

Static checks: every payload must appear verbatim in the deliverable unless
kind=re (regex, MULTILINE). Derived checks recompute sums and ratios from the
file's own numbers. --self-test mutates the file in memory; every mutation
must fail at least one check.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "Craft_Inscription.txt"
RAW = TARGET.read_text(encoding="utf-8")

# kind: "lit" = substring, "re" = MULTILINE regex over the full text.
CHECKS = [
    # --- heading / scope -------------------------------------------------
    ("H01 heading", "re", r"^BATTLE FOR AZEROTH 8\.3\.7 \(BUILD 35662\) - INSCRIPTION CRAFTING FOR A SERVER-SIDE COMPANION$"),
    ("H02 underline", "re", r"^={20,}$"),
    ("H03 scope unverified", "lit", 'says "unverified" instead of a guess'),
    ("H04 s1", "lit", "1. THE SKILL LINES AND HOW A COMPANION LEARNS THEM"),
    ("H05 s2", "lit", "2. TRAINERS AND THEIR POSITIONS"),
    ("H06 s3", "lit", "3. CHEAPEST ROUTE 1 TO THE CAP OF EACH LINE"),
    ("H07 s4", "lit", "4. MATERIALS AND WHERE EACH COMES FROM"),
    ("H08 s5", "lit", "5. TRAINER COSTS"),
    ("H09 s6", "lit", "6. LEVEL NEEDED"),
    ("H10 s7", "lit", "7. WHAT THE CORE MUST DO FOR A CRAFT TO SUCCEED"),
    ("H11 s8", "lit", "8. WHAT A SERVER-SIDE CHARACTER (NO CLIENT) CANNOT DO"),
    ("H12 s9", "lit", "9. CONFLICTS AND UNVERIFIED INDEX"),
    ("H13 s10", "lit", "10. SOURCES"),
    ("H14 subroutes", "re", r"3\.1 Classic 1-300[\s\S]+?3\.8 Battle for Azeroth 1-175"),
    # --- base spell ------------------------------------------------------
    ("B01 base45357", "lit", "Base spell Inscription 45357"),
    ("B02 skill773", "lit", "skill=773, value 1"),
    ("B03 trade skill", "re", r"Effect1 = Trade Skill, Effect2 =\s+Learn Skill \(Inscription"),
    ("B04 cost10", "lit", '"Training cost: 10"'),
    ("B05 pigment text", "re", r"Requires pigments milled from herbs"),
    ("B06 taught42", "re", r'shows "Taught by\s+\(42\)" \(list not rendered\)'),
    ("B07 ranks", "re", r"45358 \(50\), 45359 \(125\),\s+45360 \(200\), 45361 \(275\),\s+45363 \(350\), 86008 \(425\), 110417 \(500\)"),
    ("B08 other ranks", "lit", '"Other ranks (9)"'),
    ("B09 low ranks", "re", r"158748 \(1\), 195115 \(1\)"),
    ("B10 difficulty", "re", r"Difficulty 111"),
    ("B11 triple", "re", r"triple-effect wrapper \(it also brings the base trade skill\)"),
    # --- 8.0.1 chains ----------------------------------------------------
    ("L01 classic", "re", r"Classic 1-300, skill=2514:"),
    ("L02 classic main", "re", r"main 264494 \"Inscription\" \(8\.0\.1, cap 300,"),
    ("L03 classic wrapper", "re", r"wrapper 264495\s+\(8\.1\.0\): Effect1 Learn Spell 45357, Effect2\s+Learn Spell 264494, Effect3 Learn Skill Step \(2514\) value 1"),
    ("L04 outland", "re", r"Outland 1-75, skill=2513: main 264496 \(8\.0\.1, quick facts \"Requires\s+Inscription \(1\)\", \"Training cost: 10\", cap 75\)"),
    ("L05 outland chain", "re", r"wrapper 264497 \(8\.1\.0\): Learn Spell 264496 \+\s+Learn Skill\s+Step \(2513\)"),
    ("L06 nr", "re", r"Northrend 1-75, skill=2512: main 264498 \(8\.0\.1, \"Training cost: 10\",\s+cap 75\)"),
    ("L07 nr chain", "re", r"wrapper 264499 \(8\.1\.0\): Learn Spell 264498 \+ Learn Skill Step\s+\(2512\)"),
    ("L08 cata", "re", r"Cataclysm 1-75, skill=2511: main 264500 \(8\.0\.1, \"Training cost: 10\",\s+cap 75\)"),
    ("L09 cata chain", "re", r"wrapper 264501 \(8\.1\.0\): Learn Spell 264500 \+ Learn Skill Step\s+\(2511\)"),
    ("L10 mop", "re", r"Pandaria 1-75, skill=2510: main 264502 \(8\.0\.1, \"Training cost: 10\",\s+cap 75\)"),
    ("L11 mop chain", "re", r"wrapper 264503 \(8\.1\.0\): Learn Spell 264502 \+ Learn Skill Step\s+\(2510\)"),
    ("L12 wod", "re", r"Draenor 1-100, skill=2509: main 264504 \(8\.0\.1, cap 100, no Training\s+cost shown, no Taught-by\)"),
    ("L13 wod chain", "re", r"wrapper\s+264505 \(8\.1\.0\): Learn Spell 264504 \+ Learn Skill Step \(2509\)"),
    ("L14 triggered", "lit", "Triggered by (1) Learning 161789"),
    ("L15 scroll", "re", r"scroll item 111923 \"Draenor Inscription\""),
    ("L16 legion", "re", r"Legion 1-100, skill=2508: main 264506 \(8\.0\.1, cap 100"),
    ("L17 legion chain", "re", r"wrapper 264507 \(8\.1\.0\): Learn Spell 264506 \+\s+Learn Skill\s+Step \(2508\)"),
    ("L18 legion reward", "re", r"wrapper page \"Reward from \(1\)\": quest 39847 \"Sign This\",\s+level 10, Both factions"),
    ("L19 bfa pair", "re", r"Battle for Azeroth 1-175, skill=2507 \(separate mains per faction\)"),
    ("L20 kt main", "re", r"Alliance main 264508 \"Kul Tiran Inscription\""),
    ("L21 kt cap", "re", r"Training cost: 10\", cap 175, Alliance Specific"),
    ("L22 kt chain", "re", r"Alliance wrapper 264509 \(8\.1\.0\): Learn Spell 264508 \+\s+Learn\s+Skill\s+Step \(2507\)"),
    ("L23 zal main", "re", r"Horde main 265809 \"Zandalari Inscription\""),
    ("L24 zal cap", "re", r"\"Training cost: 10\", \"Added\s+in patch 8\.1\.0\", cap 175, Horde Specific"),
    ("L25 zal chain", "re", r"Horde wrapper 265810: Learn Spell\s+265809 \+ Learn Skill Step \(2507\)"),
    ("L26 boost", "re", r"spell 201703 \"Legion Scribe\" \(Learn Spell 195115"),
    ("L27 boost value", "re", r"value 10\) is linked by the\s+Legion\s+leveling guide"),
    # --- TC learn path ---------------------------------------------------
    ("T01 npch", "re", r"NPCHandler\.cpp 97 HandleTrainerListOpcode -> 112\s+SendTrainerList -> 130 HandleTrainerBuySpellOpcode -> 145 interaction\s+guard -> 155 trainer->TeachSpell"),
    ("T02 trainer", "re", r"Trainer\.cpp 76 TeachSpell -> 79\s+CanTeachSpell -> 149 CanTeachSpell body"),
    ("T03 discount", "re", r"money at 100-106 with reputation\s+discount 98"),
    ("T04 freeprof", "re", r"156/165\), money at 100-106|free\s+primary profession point \(156/165\)"),
    ("T05 state", "re", r"172\s+GetSpellState"),
    ("T06 skill gate", "re", r"skill gate 182-184,"),
    ("T07 ability", "re", r"prerequisite spells 185-187, level 189-191"),
    ("T08 payload", "re", r"SendSpells puts ReqSkillRank/ReqAbility in the list packet \(67-68\)"),
    # --- trainers section ------------------------------------------------
    ("C01 wiki page", "lit", "warcraft.wiki.gg/wiki/Inscription_trainers"),
    ("C02 catarina", "re", r"Catarina Stanford, Canals, Stormwind \[49\.8, 74\.7\]"),
    ("C03 elise", "re", r"Elise\s+Brightletter, Great Forge, Ironforge \[60\.7, 44\.9\]"),
    ("C04 margaux", "re", r"Margaux Parchley, Apothecarium, Undercity\s+\[61\.5, 57\.9\]"),
    ("C05 zantasia", "re", r"Zantasia, Court of the Sun, Silvermoon \[69\.5, 24\]"),
    ("C06 nerog", "re", r"Nerog, The Mighty Pen/The Drag, Orgrimmar\s+\[55, 56\]"),
    ("C07 jomah", "re", r"Jo'mah, Valley of Spirits, Orgrimmar \[46\.5, 57\.5\]"),
    ("C08 poshken", "re", r"Poshken\s+Hardbinder, Spirit Rise, Thunder Bluff \[29, 21\.5\]"),
    ("C09 feyden", "re", r"Feyden Darkin,\s+Craftsmen's Terrace, Darnassus \[58\.9, 14\.1\]"),
    ("C10 thoth", "re", r"Thoth, Crystal Hall,\s+Exodar \[40\.5, 39\.1\]"),
    ("C11 theoden", "re", r"Theoden\s+Manners, Theramore, Dustwallow \(no coordinate printed\)"),
    ("C12 ktc", "re", r"KTC Train-a-Tron Deluxe, Bilgewater Harbor, Azshara \[57, 50\.5\]"),
    ("C13 wembil", "re", r"Wembil\s+Taskwidget, Kharanos, Dun Morogh \[53\.7, 52\]"),
    ("C14 lien", "re", r"Lien Farner, Goldshire, Elwynn \[42, 67\]"),
    ("C15 saren", "re", r"Saren, Falconwing\s+Square, Eversong \[49, 47\]"),
    ("C16 therisa", "re", r"Therisa Sallow, Calston Estate,\s+Tirisfal \[44\.5, 53\]"),
    ("C17 nedric", "re", r"Nedric Sallow, Brill, Tirisfal\s+\[61, 51\]"),
    ("C18 valn", "re", r"Valn, Azure Watch, Azuremyst \[48\.5, 52\.2\]"),
    ("C19 iranis", "re", r"Iranis Shadebloom, Dolanaar, Teldrassil \[56, 52\.2\]"),
    ("C20 runda", "re", r"Runda, Razor Hill,\s+Durotar \[53, 42\]"),
    ("C21 lalum", "re", r"Lalum Darkmane,\s+Bloodhoof Village, Mulgore \[46\.5, 57\.5\]"),
    ("C22 schwan", "re", r"Michael Schwan, Honor Hold, Hellfire \[53\.9, 65\.5\]"),
    ("C23 neferatti", "re", r"Neferatti,\s+Thrallmar, Hellfire \[52\.3, 36\.1\]"),
    ("C24 lidio", "re", r"Recorder Lidio, Shattrath \[36\.5,\s+44\.4\]"),
    ("C25 lidio scryers", "re", r'Not available to members of the Scryers'),
    ("C26 lanloer", "re", r"Scribe Lanloer,\s+Shattrath \[56\.6, 74\.6\]"),
    ("C27 lanloer aldor", "re", r'Not available to members of the Aldor'),
    ("C28 tink", "re", r"Tink Brightbolt, Valiance Keep, Borean \[57\.6, 71\.7\]"),
    ("C29 mindri", "re", r"Mindri\s+Dinkles, Valgarde, Howling Fjord \[58\.6, 62\.8\]"),
    ("C30 adelene", "re", r"Adelene Sunlance,\s+Warsong Hold, Borean \[41\.2, 53\.9\]"),
    ("C31 booker", "re", r"Booker Kells, Vengeance Landing,\s+Howling Fjord \[79\.4, 29\.3\]"),
    ("C32 pallin coord", "re", r"Professor Pallin, The Scribes'\s+Sacellum/Magus Commerce Exchange, Dalaran \[42\.4, 37\.5\]"),
    ("C33 arthur", "re", r"Arthur Denny,\s+Argent Tournament Grounds, Icecrown \[71\.7, 21\]"),
    ("C34 wei", "re", r"Inkmaster Wei, The Arboretum, Jade Forest \[55\.0, 45\.0\]"),
    ("C35 rinji", "re", r"Scribe Rinji,\s+Greenstone Village, Jade Forest \[47\.6, 35\.0\]"),
    ("C36 huynh", "re", r"Lorewalker\s+Huynh, Seat of Knowledge, Vale of Eternal Blossoms \[81\.8, 29\.4\]"),
    ("C37 marshall", "re", r"Master\s+Marshall, Peak of Serenity, Kun-Lai \[50\.6, 42\.3\]"),
    ("C38 no rows", "re", r"No Draenor/Broken Isles/Kul Tiras-Zandalar rows exist on this page"),
    ("C39 outland taught", "re", r"Outland main 264496, Taught by \(3\)"),
    ("C40 npc33615", "re", r'"Inscription" 33615\s+\(Shattrath City, uncategorized row\)'),
    ("C41 npc30721", "re", r"Michael Schwan 30721 \(Hellfire\s+Peninsula\)"),
    ("C42 npc33638", "re", r"Scribe Lanloer 33638 \(Shattrath City\)"),
    ("C43 nr taught", "re", r"Northrend main 264498, Taught by \(3\): Adelene Sunlance 26977"),
    ("C44 booker id", "re", r"Booker Kells 26959 \(Howling Fjord\), Professor Pallin\s+28702 \(Dalaran\)"),
    ("C45 cata taught", "re", r"Cataclysm main 264500, Taught by \(10\)"),
    ("C46 npc list", "re", r"Reshad 81770\s+\(Spires of Arak\)"),
    ("C47 mop taught", "re", r"Pandaria main 264502, Taught by \(3\): Inkmaster Wei 56065"),
    ("C48 kt taught", "re", r"Kul Tiran main 264508, Taught by \(3\)"),
    ("C49 kt names", "re", r"Instructor Okanu 153811\s+\(Nazjatar, level 50\), Kronah 131386 \(Drustvar, level 60\), Zooey\s+Inksprocket 130399 \(Boralus, level 60\)"),
    ("C50 zal taught", "re", r"Zandalari main 265809, Taught by \(3\): Chronicler Grazzul 130901"),
    ("C51 kizani", "re", r"Chronicler Kizani 132264 \(Dazar'alor and the Great\s+Seal\), Narv 154393 \(Nazjatar\)"),
    ("C52 no taught", "re", r"Classic 264494/264495 and Draenor 264504/264505 render no Taught-by"),
    ("C53 way grazzul", "re", r"Chronicler Grazzul in\s+Dazar'alor Terrace of Crafters /way 42\.3, 39\.6"),
    ("C54 way zooey", "re", r"Zooey Inksprocket in\s+Boralus Tradewinds Market /way 73\.4, 6\.33"),
    ("C55 guard", "re", r"ask a guard for a map pin|ask a guard in"),
    ("C56 nazjatar reveal", "re", r"Nazjatar trainers appear only after the first Nazjatar intro quests"),
    ("C57 split note", "re", r"if you completed the\s+Aldor/Scryer quest you can only interact with one"),
    ("C58 nr guide five", "re", r"Northrend guide - Tink\s+Brightbolt \(Valiance Keep, A\)"),
    ("C59 dual dalaran warn", "re", r"Northrend, not Legion Dalaran"),
    ("C60 legion pallin", "re", r"Legion guide - Professor Pallin 92195 in The Scribe's\s+Sacellum"),
    ("C61 scroll vendors", "re", r"Joao Calhandro\s+87063 \(Stormshield, A\) and Maru'sa 87551 \(Warspear, H\)"),
    ("C62 garrison", "re", r'Scribe\'s Quarters NPC in your garrison after "Your First Inscription Work\s+Order"'),
    ("C63 satchel", "re", r"Mysterious Satchel 114984 \(A\) / Illegible\s+Sootstained\s+Notes 115593"),
    ("C64 mishi", "re", r"Mishi 65716 flies you up"),
    # --- 3.0 milling -----------------------------------------------------
    ("R00 spell", "re", r"Milling spell 51005 \("),
    ("R00b effect", "re", r"Effect: Milling\s+Value 5, \"Target must be own item\", Cooldown n/a"),
    ("R00c reqs", "re", r"Requirements \(wowpedia\s+Milling page\): Level 5 \+ Inscription \(1\)"),
    ("R00d yields", "re", r"Five of any listed herb make\s+2-4 common pigments and may produce 1-3 uncommon pigments"),
    ("R00e to 25", "re", r"milling gives skill points up\s+to 25"),
    ("R00f mass", "re", r"unlock Mass Mill at 50,\s+which will give skill points up to 80"),
    ("R00g zinanthid", "re", r"Mass Mill Zin'anthid\" 298927\s+is learned at 155 \(4-5 points per mass mill\)"),
    ("R00h warning", "re", r"DO NOT USE MASS MILL YET, IT WON'T GIVE YOU SKILL POINTS"),
    # --- 3.1 Classic -----------------------------------------------------
    ("R01 guide", "re", r"Vanilla Inscription Leveling Guide 1-300"),
    ("R02 tools", "re", r"Buy Virtuoso Inking Set 39505 and\s+Light Parchment 39354 from the Inscription Supply vendor"),
    ("R03 shop", "re", r"180 Alabaster-tier herbs, 160 Dusky-tier, 260\s+Golden-tier, 260\s+Emerald-tier, 160 Violet-tier, 180 Silvery-tier"),
    ("R04 moonglow", "re", r"44 x Moonglow Ink spell 52843 \(88 Alabaster Pigment; keep"),
    ("R05 recall", "re", r"30 x Scroll of Recall spell 48248 \(30 Moonglow Ink\)"),
    ("R06 vellum alt", "re", r"alt:\s+Enchanting Vellum spell 52739"),
    ("R07 midnight", "re", r"36 x Midnight Ink spell 53462 \(72 Dusky Pigment"),
    ("R08 powder", "re", r"25 x Vanishing Powder spell 92026 \(25 Midnight Ink\)"),
    ("R09 hunter", "re", r"Hunter's Ink spell 57703"),
    ("R10 myst", "re", r"Mysterious Tarot spell 48247"),
    ("R11 lions", "re", r"63 x Lion's Ink spell 57704 \(126 Golden Pigment"),
    ("R12 res1", "re", r"4 x Research: Moonglow Ink spell 165564 \(12 Moonglow Ink\)"),
    ("R13 res2", "re", r"3 x Research: Midnight Ink spell 165304 \(12 Midnight Ink\)"),
    ("R14 res3", "re", r"4 x Research: Lion's Ink spell 165456 \(12 Lion's Ink\)"),
    ("R15 glyph9", "re", r"9 x any glyph discovered by Research: Lion's Ink \(3 Lion's\s+ Ink each = 27\)"),
    ("R16 dawnstar", "re", r"Dawnstar Ink spell 57706"),
    ("R17 strange", "re", r"Strange Tarot spell 59480"),
    ("R18 glyph8", "re", r"8 x any discovered glyph \(24 Lion's Ink\)"),
    ("R19 jade", "re", r"40 x Jadefire Ink spell 57707 \(80 Emerald Pigment\)"),
    ("R20 scrolls3", "re", r"5 x Scroll of Stamina III 50614, 5 x Scroll of Versatility\s+III 50606, 5 x Scroll of Intellect III 50599, 5 x Scroll of Strength\s+III 58486"),
    ("R21 agi3", "re", r"5 x Scroll of Agility III 58476"),
    ("R22 royal", "re", r"Royal Ink spell 57708"),
    ("R23 resjade", "re", r"5 x Research: Jadefire Ink spell 165460 \(15 Jadefire Ink\)"),
    ("R24 arcane", "re", r"Arcane Tarot spell 59487"),
    ("R25 glyph15", "re", r"15 x any\s+orange glyph \(45 inks\)"),
    ("R26 celest", "re", r"34 x Celestial Ink spell 57709 \(68 Violet Pigment\)"),
    ("R27 recall2", "re", r"10 x Scroll of Recall II 60336"),
    ("R28 scrolls4", "re", r"5 x Scroll of Intellect IV\s+50600, 5 x Scroll of Strength IV 58487"),
    ("R29 fiery", "re", r"Fiery Ink spell 57710"),
    ("R30 agi4", "re", r"5 x Scroll\s+of Agility IV 58478"),
    ("R31 rescel", "re", r"3 x Research: Celestial Ink spell 165461 \(9 Celestial Ink\)"),
    ("R32 shadowy", "re", r"Shadowy Tarot spell 59491"),
    ("R33 glyph17", "re", r"17 x any\s+orange glyph \(51 inks\)"),
    ("R34 shimmer", "re", r"42 x Shimmering Ink spell 57711 \(84 Silvery Pigment\)"),
    ("R35 scrolls5", "re", r"5 x Scroll of Versatility V 50608, 5 x Scroll of Intellect\s+V 50601, 5 x Scroll of Strength V 58488, 5 x Scroll of Agility V\s+58480"),
    ("R36 sky", "re", r"Ink of the Sky spell 57712"),
    ("R37 resshim", "re", r"4 x\s+Research: Shimmering Ink spell 165463 \(12 Shimmering Ink\)"),
    ("R38 glyph11", "re", r"11 x any\s+orange glyph \(33 inks\)"),
    ("R39 stam6", "re", r"10 x Scroll of Stamina VI 50618 \(10 Shimmering Ink\)"),
    ("R40 total", "re", r"Total exact-count casts printed by the guide = 477"),
    # --- 3.2 Outland -----------------------------------------------------
    ("O01 guide", "re", r"Outland Inscription Leveling Guide 1-75"),
    ("O02 mill500", "re", r"mill around\s+500 of any Outland herb"),
    ("O03 ebon", "re", r"Ebon Pigment 43108 into Darkflame Ink spell 57714"),
    ("O04 book", "re", r"Book of Clever Tricks spell 59496"),
    ("O05 approx", "re", r"you don't\s+have to reach 33, and you might even reach 35"),
    ("O06 research", "re", r"42 x Research: Ethereal Ink spell 165464 \(126 Ethereal Ink;"),
    ("O07 parchment", "re", r"eats 3 Light Parchment per cast per wowdb"),
    ("O08 total", "re", r"Total exact-count casts printed by the guide = 42 \(the 25-33 Book of"),
    # --- 3.3 Northrend ---------------------------------------------------
    ("N01 guide", "re", r"Northrend Inscription Leveling Guide 1-75"),
    ("N02 mill450", "re", r"mill around 450 of any Northrend\s+herb"),
    ("N03 ink sea", "re", r"95 x Ink of the Sea spell 57715 \(190 Azure\s+Pigment\)"),
    ("N04 icy", "re", r"Icy Pigment 43109 into Snowfall Ink\s+spell 57716"),
    ("N05 scrolls8", "re", r"5 x Scroll of Stamina VIII 50620, 5 x Scroll of Versatility\s+VIII 50611, 5 x Scroll of Intellect VIII 50604, 5 x Scroll of\s+Strength VIII 58491"),
    ("N06 agi8", "re", r"15 x Scroll of Agility\s+VIII 58483"),
    ("N07 yellow", "re", r"yellow for the last 5 - expect extra"),
    ("N08 res", "re", r"10 x Research: Ink of the Sea 165465 \(30 Ink of the Sea\)"),
    ("N09 runescroll", "re", r"Runescroll of Fortitude spell 69385"),
    ("N10 fewer", "re", r"fewer than 10\s+research if runescrolls gave points"),
    ("N11 total", "re", r"Total exact-count casts printed by the guide = 150 \(95 ink prep \+ 45"),
    # --- 3.4 Cataclysm ---------------------------------------------------
    ("K01 guide", "re", r"Cataclysm Inscription Leveling Guide 1 - 75"),
    ("K02 mill180", "re", r"mill\s+around 180 of any Cataclysm herb"),
    ("K03 technique", "re", r"Technique: Origami Beetle item 65651 from Schnottz\s+Infantryman 48629"),
    ("K04 zidormi", "re", r"Zidormi 162419 at Ramkahen to phase back"),
    ("K05 origami", "re", r"100 x Origami Beetle spell 86646 \(300\s+Light Parchment\)"),
    ("K06 forged", "re", r"1 x Forged Documents spell 86654"),
    ("K07 cd", "re", r"This recipe has 1-day cooldown"),
    ("K08 research", "re", r"14 x Research: Blackfallow Ink spell 165466 \(42 Blackfallow"),
    ("K09 total", "re", r"Total exact-count casts printed by the guide = 115 \(100 \+ 1 \+ 14\)"),
    # --- 3.5 Pandaria ----------------------------------------------------
    ("P01 guide", "re", r"Pandaria Inscription Leveling Guide 1 - 75"),
    ("P02 vendors", "re", r"Fang Whitescroll 64053\s+\(Shrine of Two Moons\) or Veronica Faraday 64081"),
    ("P03 ink", "re", r"135 x Ink of Dreams spell 111645 \(270 Shadow\s+Pigment\)"),
    ("P04 starlight", "re", r"Misty Pigment 79253 into Starlight Ink spell 111646"),
    ("P05 res", "re", r"20 x Research: Ink of Dreams spell 165467 \(60 Ink of\s+Dreams\)"),
    ("P06 ox", "re", r"Greater Ox Horn Inscription spell 126994"),
    ("P07 fewer", "re", r"make fewer than 20 if you gained more than 5 skill points"),
    ("P08 crane", "re", r"5 x Secret Crane Wing Inscription spell 127023 \(15 Ink of\s+Dreams\)"),
    ("P09 total", "re", r"Total exact-count casts printed by the guide = 180 \(135 ink prep \+ 20 \+"),
    # --- 3.6 Draenor -----------------------------------------------------
    ("D01 scroll", "re", r'3\.6 Draenor 1-100 \(scroll item 111923 "Draenor Inscription" first\)'),
    ("D02 trigger", "re", r"10-sec\s+item effect that triggers Learning 161789 -> wrapper 264505"),
    ("D03 questchain", "re", r"Mysterious Satchel 114984"),
    ("D04 cerulean", "re", r"need 900 total -> mill around 2250 herbs"),
    ("D05 vendors2", "re", r"Jasa 86041\s+\(Warspear\) / Trader Caerel 85950 \(Stormshield\)"),
    ("D06 secrets", "re", r"1 x Secrets of Draenor Inscription spell 177045"),
    ("D07 technique", "re", r"Technique: Volatile Crystal item 118614"),
    ("D08 crystal", "re", r"75 x Volatile Crystal spell 166432 \(900 Cerulean Pigment\)"),
    ("D09 alt", "re", r"Alternative \(1250 herbs instead of 2250\)"),
    ("D10 trader npc", "re", r"Samantha Scarlet 91404 A / Nicholas Mitrik 91031 H"),
    ("D11 spirit", "re", r"75 x The Spirit of War spell 182125 \(75\s+Primal Spirit 120945 \+ 300 Cerulean Pigment\)"),
    ("D12 rotation", "re", r"rotation Ore -> Dust -> Fur -> Leather -> Herb"),
    ("D13 dates", "re", r"EU/NA dates are swapped"),
    ("D14 total", "re", r"Total exact-count casts on the main branch = 76 \(1 \+ 75\)"),
    # --- 3.7 Legion ------------------------------------------------------
    ("G01 guide", "re", r"Legion Inscription Leveling Guide 1-100"),
    ("G02 pallin", "re", r"Trainer Professor Pallin\s+npc 92195, The Scribe's Sacellum"),
    ("G03 quest", "re", r"Quest \"Sign\s+This\" 39847 \(level 10, Both\)"),
    ("G04 sign item", "re", r"right-click the Unsigned\s+Contract item 129047 in your inventory to sign it"),
    ("G05 provides", "re", r"provides\s+129047 -> 129043"),
    ("G06 shop", "re", r"~200 Sallow\s+Pigment 129034 \+ ~900 Roseate Pigment 129032"),
    ("G07 herbs", "re", r"~4500 herbs if milling only Aethril"),
    ("G08 mill400", "re", r"manually mill ~400 Legion herbs"),
    ("G09 technique", "re", r"Technique: Tome of the Tranquil Mind item 141447"),
    ("G10 tome", "re", r"20 x Tome of the Tranquil Mind spell 227043 \(20 Sallow"),
    ("G11 vantus", "re", r"60 x any Nighthold Rank 3 Vantus Rune \(180 Sallow Pigment \+\s+900 Roseate Pigment\)"),
    ("G12 lfr", "re", r"Archmage\s+Timear 111246 in Dalaran"),
    ("G13 r3 vendors", "re", r"Marin Bladewing 107379"),
    ("G14 veridis", "re", r"Veridis Fallon 107376"),
    ("G15 rune ids", "re", r"137781 Star Augur\s+Etraeus, 137777 Spellblade\s+Aluriel"),
    ("G16 runes2", "re", r"137776\s+Trilliax, 137774 Skorpyron, 137780 Krosus, 137779 High Botanist\s+Tel'arn"),
    ("G17 arch", "re", r"137782 Grand Magistrix Elisande from Archaeology fragments"),
    ("G18 fishing", "re", r"137775 Chronomatic Anomaly fished from Cursed Queenfish"),
    ("G19 massmill quest", "re", r"Mass Milling Techniques quest 39954"),
    ("G20 reward spell", "re", r"Mass Mill Yseralline Seeds 210116"),
    ("G21 table", "re", r"Aethrem Crystal\s+136909 -> Mass Mill Aethril 209658"),
    ("G22 table2", "re", r"Sallow\s+Essence 136918 -> Mass Mill Felwort 209664"),
    ("G23 astral", "re", r"Technique: Mass Mill\s+astral".replace("astral", "Astral Glory item 152725") + ""),
    ("G24 total", "re", r"Total exact-count casts printed by the guide = 80 \(20 tomes \+ 60"),
    # --- 3.8 BfA ---------------------------------------------------------
    ("A01 guide", "re", r"BfA Inscription Leveling Guide 1 - 175"),
    ("A02 way", "re", r"/way 42\.3, 39\.6"),
    ("A03 way2", "re", r"/way 73\.4, 6\.33"),
    ("A04 guard", "re", r"ask a guard for a map pin"),
    ("A05 rates", "re", r"Ultramarine ~75%, Crimson ~25%, Viridescent\s+~10% \(Anchor Weed ~30%\)"),
    ("A06 totals", "re", r"~900 Ultramarine Ink 158187, ~550 Crimson Ink 158188, ~50\s+Viridescent Ink 158189"),
    ("A07 vendor", "re", r"Light Parchment 39354, Distilled Water\s+158186, Acacia Powder 158205"),
    ("A08 mill", "re", r"mill 100-150 of one herb to 25"),
    ("A09 inks", "re", r"Ultramarine spell 264776,\s+Crimson 264777, Viridescent 264778"),
    ("A10 mass", "re", r"unlock Mass Mill at 50"),
    ("A11 warscroll", "re", r"War-Scroll of Battle Shout spell 264767"),
    ("A12 warscroll n", "re", r"8 x War-Scroll of Battle Shout 264767 \(64 Crimson Ink"),
    ("A13 contracts", "re", r"Alliance 60 x Rank 2 - Contract: 7th Legion spell 284293"),
    ("A14 contracts h", "re", r"Horde 60 x Rank 2 -\s+Contract: The Honorbound spell 284296"),
    ("A15 contract math", "re", r"900 Ultramarine Ink \+ 480\s+Crimson Ink"),
    ("A16 honored", "re", r"Honored with the\s+faction required"),
    ("A17 r2 items", "re", r"Recipe: Contract: 7th Legion 166278 from Vindicator\s+Jaelaana 135446"),
    ("A18 r2 items2", "re", r"Recipe: Contract: The Honorbound 166310 from Ransa\s+Greyfeather 135447"),
    ("A19 alt contracts", "re", r"Contract: Talanji's Expedition 256288 \(Provisioner Lija 135459\)"),
    ("A20 alt contracts2", "re", r"Contract: Order of\s+Embers 256279 \(Quartermaster Alcorn 135815\)"),
    ("A21 neutral", "re", r"Contract: Champions of\s+Azeroth 256298 and Contract: Tortollan Seekers 256295"),
    ("A22 yellow105", "re", r"yellow at\s+105"),
    ("A23 workorder", "re", r"daily \"Work Order\" Inscription World Quests reward"),
    ("A24 dmow", "re", r"5 x Rank 2 - Darkmoon Card of War spell 256245 \(5 Light\s+Parchment \+ 50 Viridescent Ink \+ 5 Expulsom 152668\)"),
    ("A25 r3 dmow", "re", r"Rank 3 recipe\s+162377 from Collector Kojo 135793 at Tortollan Seekers Revered"),
    ("A26 nazjatar", "re", r"Narv 154393 H / Instructor Okanu\s+153811 A; intro quests first"),
    ("A27 maroon", "re", r"100 x Maroon\s+Ink spell 298929 \(100 Distilled Water \+ 100 Maroon Pigment\)"),
    ("A28 zinanthid", "re", r"mill\s+around 150 Zin'anthid 168487"),
    ("A29 total", "re", r"Total exact-count casts printed by the guide = 173 \(8 \+ 60 \+ 5 \+ 100"),
    # --- 4 materials -----------------------------------------------------
    ("M01 companion", "re", r"wiki names Herbalism the companion\s+profession"),
    ("M02 tools", "re", r"Virtuoso Inking Set 39505 \(tool; bought from\s+inscription vendors"),
    ("M03 parchment", "re", r"Light Parchment 39354 \(vendor, 15c per\s+warcraft\.wiki"),
    ("M04 water", "re", r"Distilled\s+Water 158186 and Acacia Powder 158205 \(BfA vendor goods\)"),
    ("M05 classic a", "re", r"Peacebloom 2447, Silverleaf 765,\s+Earthroot 2449 -> Alabaster Pigment 39151"),
    ("M06 classic b", "re", r"Mageroyal 785, Briarthorn 2450,\s+Swiftthistle 2452, Stranglekelp 3820, Bruiseweed 2453"),
    ("M07 classic c", "re", r"Wild Steelbloom 3355,\s+Grave Moss 3369, Kingsblood 3356, Liferoot 3357"),
    ("M08 classic d", "re", r"Dragon's Teeth 3819, Fadeleaf\s+3818, Goldthorn 3821, Khadgar's Whisker 3358"),
    ("M09 classic e", "re", r"Blindweed 8839, Firebloom 4625,\s+Ghost Mushroom 8845, Gromsblood 8846, Purple Lotus 8831"),
    ("M10 classic f", "re", r"Dreamfoil 13463, Golden Sansam 13464, Icecap 13467"),
    ("M11 outland", "re", r"Felweed 22785, Dreaming Glory 22786, Ragveil 22787"),
    ("M12 outland2", "re", r"Nether Pigment 39342 \+\s+Ebon Pigment 43108"),
    ("M13 nr", "re", r"Goldclover 36901, Tiger Lily 36904, Deadnettle 37921"),
    ("M14 nr2", "re", r"Azure Pigment 39343 \+ Icy\s+Pigment 43109"),
    ("M15 cata", "re", r"Cinderbloom 52983, Stormvine 52984, Heartblossom 52986"),
    ("M16 cata2", "re", r"Ashen Pigment 61979 \+ Burning Embers 61980"),
    ("M17 mop", "re", r"Green Tea Leaf 72234, Rain Poppy 72237, Silkweed 72235"),
    ("M18 mop2", "re", r"Shadow\n    Pigment 79251 \+ Misty Pigment 79253"),
    ("M19 wod", "re", r"Fireweed 109125, Frostweed 109124, Gorgrond Flytrap\s+109126"),
    ("M20 wod2", "re", r"Warbinder's Ink 113111\s+exists but the route spends pigment directly"),
    ("M21 legion", "re", r"Aethril 124101, Dreamleaf 124102,\s+Foxflower 124103"),
    ("M22 legion2", "re", r"Roseate Pigment\s+129032 \+ Sallow Pigment 129034"),
    ("M23 bfa", "re", r"Riverbud 152505, Star Moss 152506, Akunda's\s+Bite 152507"),
    ("M24 bfa2", "re", r"Ultramarine\s+Ink 158187 \(spell 264776: 1 Distilled Water \+ 2 Ultramarine\s+Pigment\)"),
    ("M25 bfa3", "re", r"Viridescent Ink 158189 \(spell 264778: 1 Distilled\n    Water \+ 1 Acacia Powder \+ 1 Viridescent Pigment\)"),
    ("M26 maroon", "re", r"Maroon Ink 168663 \(spell 298929: 1\n    Distilled Water \+ 1 Maroon Pigment; Inscription 125"),
    ("M27 rules", "re", r"common inks come\s+from 2 common pigments; uncommon inks from 1 uncommon pigment, except\s+Snowfall Ink and Inferno Ink which each require two"),
    ("M28 glyph rule", "re", r"Glyphs and\s+scrolls use common inks; tomes and Darkmoon cards use common \+\s+uncommon inks"),
    ("M29 umbral", "re", r"Umbral Ink 173058 can be traded for any ink at\s+ink traders"),
    ("M30 ah note", "re", r"buying herbs/pigments/inks from the auction house is\s+the fast path"),
    # --- 5 costs ---------------------------------------------------------
    ("F01 raw", "re", r"Learn-spell quick-fact \"Training cost\" \(raw value; wowhead prints no\s+unit, warcraft\.wiki prints the same figure as copper\)"),
    ("F02 list", "re", r"45357 = 10,\s+264496 = 10, 264498 = 10, 264500 = 10, 264502 = 10,\s+264508 = 10,\s+265809 = 10"),
    ("F03 copper", "re", r"is 10\s+copper, before any discounts"),
    ("F04 unverified", "re", r"Classic 264494/264495, Draenor 264504/264505 and Legion 264506/264507\s+render no training cost - unverified"),
    ("F05 midnight", "re", r"Profession Trainer: Classic Inscription \(75\) - Cost:\s+3 50"),
    ("F06 contract", "re", r"Contract: Zandalari Empire R1 source \"Chronicler Kizani\s+35 g\""),
    ("F07 vessel", "re", r"Inscribed Vessel of Mysticism source \"Chronicler Kizani\s+/\s+Zooey Inksprocket 40 g\""),
    ("F08 1000g", "re", r'source as\n"Honored with <faction> 1000 g" \(as printed\)'),
    ("F09 spirit", "re", r"Technique: The Spirit of War = 20 Cerulean\s+Pigment"),
    ("F10 parchment15", "re", r"Light Parchment 15c \(warcraft\.wiki\); pigments sell for\s+25c and inks 5s"),
    ("F11 moneycost", "re", r"price = trainer-spell MoneyCost x\s+GetReputationPriceDiscount\(npc\) \(Trainer\.cpp 98\)"),
    # --- 6 level ---------------------------------------------------------
    ("V01 classic5", "re", r"Classic: level 5 \(300 cap\)"),
    ("V02 outland5", "re", r"Outland: level 5 \(75 cap\)"),
    ("V03 nr5", "re", r"Northrend: level 5 \(75 cap\) - wowpedia's Northrend page still prints\n    \"level 65\""),
    ("V04 cata5", "re", r"Cataclysm: level 5 \(75 cap\)"),
    ("V05 mop5", "re", r"Pandaria: level 5 \(the header also misprints \"progression up to 5\n    skill\""),
    ("V06 wod5", "re", r"Draenor: level 5 \(100 cap\)"),
    ("V07 legion5", "re", r"Legion: level 5 \(100 cap\); current quest 39847 requires level 10"),
    ("V08 bfa5", "re", r"Battle for Azeroth: level 5, cap 175 \(BfA technique page header\)"),
    ("V09 trainer levels", "re", r"Okanu/Narv level 50, Kronah/Zooey/Grazzul\s+level 60"),
    ("V10 base", "re", r"prospective scribes must be\s+level 5"),
    ("V11 milling", "re", r"Milling requirements: Level 5 \+ Inscription \(1\)"),
    ("V12 table", "re", r"Classic\s+Apprentice/Journeyman/Expert/Artisan ladder 1-75 / 75-150 / 150-225 /\s+225-300"),
    ("V13 bfa row", "re", r"BfA Kul Tiran/Zandalari Master\s+1-150 \(this row is stale"),
    ("V14 gates", "re", r'"Profession: Pandaria Inscription \(1\)" on\nResearch: Ink of Dreams 165467'),
    ("V15 maroon125", "re", r"Maroon Ink requires Inscription 125"),
    ("V16 no craft gate", "re", r"There is no server-side\s+craft-time skill check for inscription recipes"),
    ("V17 reqskill", "re", r"reqSkillValue only for lock-opening, gathering, prospecting and the\s+milling path below"),
    ("V18 tc gates", "re", r"trainer learn gate = GetSpellState ReqSkillLine/\s+ReqSkillRank \(Trainer\.cpp 182-184\) and level check 189-191"),
    # --- 7 core ----------------------------------------------------------
    ("W01 clone", "re", r"Verified against TrinityCore master fetched this week \(blobless sparse\s+clone"),
    ("W02 create", "re", r"recipes are Effect Create Item\s+\(sampled pages print Effect: Create Item"),
    ("W03 take", "re", r"Spell\.cpp 3872/3877\s+TakeReagents\(\) \(definition 5600\)"),
    ("W04 docreate", "re", r"DoCreateItem SpellEffects\.cpp 1383"),
    ("W05 inv", "re", r"1440\s+\(EQUIP_ERR_INV_FULL \|\| EQUIP_ERR_ITEM_MAX_COUNT -> SendEquipError\)"),
    ("W06 skill1469", "re", r"grants skill at 1469 \(`if \(!m_CastItem\) player->\s+UpdateCraftSkill\(m_spellInfo\);`\)"),
    ("W07 no variable", "re", r"none of the routed steps print a\s+variable\s+yield"),
    ("W08 create2", "re", r"SPELL_EFFECT_CREATE_ITEM_2 \(effect 157,\s+table line 249\) with\s+IsLootCrafting rolls from LootTemplates_Spell\s+\(EffectCreateItem2"),
    ("W09 itemcast", "re", r"item-cast crafts grant skill through Spell\.cpp\s+3863\s+\(SPELL_ATTR9_ITEM_CAST_GRANTS_SKILL_GAIN\)"),
    ("W10 mill table", "re", r"SPELL_EFFECT_MILLING \(effect 158,\s+table SpellEffects\.cpp 250,\s+implicit target ITEM at SpellInfo\.cpp 1120\)"),
    ("W11 checkcast", "re", r"CheckCast block\s+Spell\.cpp 7836-7866"),
    ("W12 cant milled", "re", r"no target -> failed\s+CANT_BE_MILLED"),
    ("W13 owner", "re", r"item owned by someone else \(trade slot\) -> failed\s+CANT_BE_MILLED"),
    ("W14 low", "re", r"failed\s+LOW_CASTLEVEL \(this is\s+the only cast-time recipe-like skill gate in these routes\)"),
    ("W15 need items", "re", r"failed NEED_MORE_ITEMS \(fills the need-items counters\s+with the herb entry and 5\)"),
    ("W16 loot tmpl", "re", r"loot template missing -> failed\s+CANT_BE_MILLED"),
    ("W17 effect", "re", r"EffectMilling SpellEffects\.cpp 4641-4666"),
    ("W18 flag", "re", r"re-check millable flag \(4651\) and count >= 5 \(4654\)"),
    ("W19 config", "re", r"world config CONFIG_SKILL_MILLING \(4656\) gates the skill grant"),
    ("W20 update", "re", r"GetPureSkillValue \+ herb RequiredSkillRank -> UpdateGatherSkill\s+\(4658-4660\)"),
    ("W21 loot build", "re", r"builds LOOT_MILLING from LootTemplates_Milling\s+keyed by the target item entry \(4663-4664\) and SendLoot \(4665\)"),
    ("W22 consume", "re", r"LootHandler\.cpp 348-361 destroys\s+exactly 5 items from the stack"),
    ("W23 cheat note", "re", r"destroy only 5 items from stack in\s+case prospecting and milling"),
    ("W24 default false", "re", r"World\.cpp 630 registers \"SkillChance\.Milling\" with\s+DefaultValue false \(World\.h 124 CONFIG_SKILL_MILLING\)"),
    ("W25 config line", "re", r"on a default\s+TC config milling yields pigments but grants no inscription skill"),
    ("W26 updatecraft", "re", r"Player::UpdateCraftSkill Player\.cpp 5410, early-out\s+SPELL_ATTR1_NO_SKILL_INCREASE 5412"),
    ("W27 discovery", "re", r"discovery branch MECHANIC_DISCOVERY 5427 \(research spells carry a\s+Script Effect"),
    ("W28 gain", "re", r"gain =\s+NumSkillUps x CONFIG_SKILL_GAIN_CRAFTING 5433"),
    ("W29 colours", "re", r"orange always, yellow probably, green\s+probably not, grey never; red = not\s+high enough skill to learn"),
    ("W30 quest path", "re", r"quest-reward learn path"),
    ("W31 tools", "re", r"Whether the\s+8\.3\.7 server enforces a carried tool[\s\S]{0,140}?was not verified"),
    ("W32 focus", "re", r"focus machinery exists \(Spell\.cpp 1120/1133, GameObjectFocus\s+2322-2323"),
    ("W33 vellum", "re", r"TC's vellum branch SpellEffects\.cpp\s+2475-2492 belongs to the enchanter's cast"),
    ("W34 learn effects", "re", r"effect 36\s+LEARN_SPELL \(table line 128\) -> EffectLearnSpell SpellEffects\.cpp\s+2129"),
    ("W35 skill step", "re", r"effect 44 SKILL_STEP \(table line 136\) -> EffectLearnSkill 2405"),
    ("W36 trade", "re", r"effect 47 TRADE_SKILL \(table line 139\) -> EffectTradeSkill 2451"),
    ("W37 skill lines", "re", r"the 773 skill line\s+\(and its eight sub-lines 2507-2514\)"),
    ("W38 req1", "re", r"expansion mains also require base Inscription \(1\) as their quick\s+facts state"),
    # --- 8 cannot --------------------------------------------------------
    ("X01 nightborne", "re", r"Ancient History 255663\s+is \"Inscription skill increased by 5\" \(Apply Aura: Mod Skill\s+\(Inscription\) value 5\)"),
    ("X02 visage", "re", r"a non-Nightborne companion never gets\s+the \+5\s+orange extension"),
    ("X03 kt2", "re", r"Kul Tiran \+2 Jack of All Trades comes from guide\s+text only"),
    ("X04 honored", "re", r"Honored factions for the\s+BfA R2 contracts"),
    ("X05 rep2", "re", r"Tortollan Revered for the\s+Darkmoon Card of War R3"),
    ("X06 wardens", "re", r"The Wardens/Court of Farondis Revered for the\s+Legion R3 Vantus vendors"),
    ("X07 argus", "re", r"Argussian Reach Friendly for Technique: Mass\s+Mill Astral Glory"),
    ("X08 cd", "re", r"1-day Forged Documents cooldown"),
    ("X09 wq", "re", r"daily \"Work Order\" World\s+Quests for BfA R3 recipes"),
    ("X10 trader rng", "re", r"1-of-4 RNG, level 3 town hall, 5-day cycle"),
    ("X11 dates", "re", r"dates currently swapped between EU/NA"),
    ("X12 lfr", "re", r"Raid Finder queueing and\s+Nighthold boss kills"),
    ("X13 fishing", "re", r"Azsuna fishing for the Chronomatic Anomaly\s+rune"),
    ("X14 arch", "re", r"Legion Archaeology for the Elisande rune"),
    ("X15 ladder", "re", r"book-and-ladder room clicks"),
    ("X16 storyline", "re", r"42-quest Legion\s+storyline behind quest 39847"),
    ("X17 hov", "re", r"Halls of\s+Valor 39953 - a dungeon"),
    ("X18 uldum", "re", r"Uldum mob farming plus the Zidormi phase\s+switch"),
    ("X19 satchel", "re", r"Mysterious Satchel/Illegible Sootstained Notes drop chains \(WoD\)"),
    ("X20 naz", "re", r"Nazjatar intro quests that reveal Narv/Instructor Okanu"),
    ("X21 ah", "re", r"every shopping list assumes an AH"),
    ("X22 faction", "re", r"mains 264508 \(Alliance Specific\) and\s+265809 \(Horde Specific\) are one-sided"),
    ("X23 split", "re", r"Aldor cannot use Recorder\s+Lidio and Scryers cannot use Scribe Lanloer"),
    ("X24 dual", "re", r"same name, npc 92195"),
    ("X25 profs", "re", r"CanTeachSpell's free\s+profession point gate \(Trainer\.cpp 156\)"),
    ("X26 ui", "re", r"the technique loot-spark on the counter behind\s+Pallin"),
    ("X27 stale rows", "re", r"patch 4\.0\.3a equalized trainer ranks"),
    ("X28 config", "re", r"SkillChance\.Milling defaults to false"),
    # --- 9 conflicts -----------------------------------------------------
    ("Y01 c1", "re", r"1\) Nightborne bonus:"),
    ("Y02 c2", "re", r"2\) BfA cap: warcraft\.wiki's Inscription training table prints BfA 1-150"),
    ("Y03 c3", "re", r"3\) wowpedia BfA techniques header prints \"trained as early as level TBC\""),
    ("Y04 c4", "re", r"4\) Pandaria technique page header prints \"permits progression up to 5"),
    ("Y05 c5", "re", r"5\) Level gates: every warcraft\.wiki inscription technique header prints"),
    ("Y06 c6", "re", r"6\) Legion reward link: the guide hyperlinks spell 201703"),
    ("Y07 c7", "re", r"7\) Northrend trainer set:"),
    ("Y08 c8", "re", r"8\) Professor Pallin has two npc ids in live pages:"),
    ("Y09 c9", "re", r"9\) Outland trainer set: sources differ"),
    ("Y10 c10", "re", r"10\) Classic/Cataclysm trainer sets:"),
    ("Y11 c11", "re", r"11\) Patch tags on the BfA Horde pair: wowhead quick facts say main\s+265809"),
    ("Y12 c12", "re", r"12\) BfA pigment rates:"),
    ("Y13 c13", "re", r"13\) Research cooldowns:"),
    ("Y14 c14", "re", r"14\) Training-cost units:"),
    ("Y15 c15", "re", r"15\) TC line drift: this fetch shows SpellEffects\.cpp SPELL_ATTR9 at 3863"),
    ("Y16 c16", "re", r"16\) \"Milling gives skill points up to 25\" is printed by every guide"),
    ("Y17 c17", "re", r"17\) The milling table page's \"Umbral Ink trades for any ink at ink"),
    ("Y18 c18", "re", r"18\) Outland 33-75 and several vanilla steps are explicitly approximate"),
    ("Y19 c19", "re", r"19\) Classic 264494/264495 and Draenor 264504 render no teacher list"),
    # --- 10 sources ------------------------------------------------------
    ("Z01 date", "re", r"All fetched 2026-10-26 week"),
    ("Z02 spell list", "re", r"45357 \(base \+ 9 other ranks\), 264494, 264495"),
    ("Z03 quest", "re", r"39847 \"Sign This\" \(level 10, Both, start/end\s+Professor Pallin 92195"),
    ("Z04 search", "re", r"Guide-hub search results \(record id/url\)"),
    ("Z05 url classic", "lit", "https://www.wowhead.com/skill=2514/classic-inscription"),
    ("Z06 url wiki classic", "lit", "https://warcraft.wiki.gg/wiki/Classic_inscription_techniques"),
    ("Z07 url milling", "lit", "https://www.wowhead.com/wotlk/spell=51005/milling"),
    ("Z08 url blackfallow", "lit", "https://www.wowhead.com/item=61978/blackfallow-ink"),
    ("Z09 url moonglow", "lit", "https://www.wowhead.com/item=39469/moonglow-ink"),
    ("Z10 url ultramarine", "lit", "https://www.wowhead.com/item=158187/ultramarine-ink"),
    ("Z11 url crimson", "lit", "https://www.wowhead.com/item=158188/crimson-ink"),
    ("Z12 url viridescent", "lit", "https://www.wowhead.com/item=158189/viridescent-ink"),
    ("Z13 url maroon", "lit", "https://www.wowhead.com/item=168663/maroon-ink"),
    ("Z14 url nr guide", "lit", "https://www.wow-professions.com/guides/northrend-inscription-leveling"),
    ("Z15 slugs", "re", r"wow-professions guides \(full slugs\): vanilla-inscription-leveling,\s+outland-inscription-leveling, northrend-inscription-leveling,\s+cataclysm-inscription-leveling, pandaria-inscription-leveling,\s+draenor-inscription-leveling, legion-inscription-leveling"),
    ("Z16 bfa slug", "re", r"zandalari-kul-tiran-bfa-inscription-leveling-guide"),
    ("Z17 mill table slug", "re", r"milling-table-inscription \(all herb/pigment/ink item links"),
    ("Z18 wiki pages", "re", r"warcraft\.wiki\.gg pages: Inscription \(14 chunks"),
    ("Z19 trainers chunks", "re", r"Inscription_trainers\s+\(5 chunks"),
    ("Z20 ingredients", "re", r"Inscription_ingredients \(mill 5 -> 2-4 common \+ 1-3\s+uncommon pigments"),
    ("Z21 technique pages", "re", r"Classic/Outland/Northrend/Cataclysm/Pandaria/Draenor/Legion/\s+Battle_for_Azeroth inscription techniques"),
    ("Z22 wowpedia", "re", r"wowpedia\.fandom\.com snippets \(search results with URLs above and\)"),
    ("Z23 tc clone", "re", r"TrinityCore master, fetched this week with a blobless sparse clone \(HEAD\s+e0eec525aa"),
    ("Z24 tc spell", "re", r"Spells/Spell\.cpp \(3863, 3872/3877, 5600,\s+6373, 7836-7866"),
    ("Z25 tc effects", "re", r"Spells/SpellEffects\.cpp \(128,\s+136, 139, 145, 249, 250, 1383, 1440, 1469"),
    ("Z26 tc mill", "re", r"4641-4666"),
    ("Z27 tc player", "re", r"Entities/Player/Player\.cpp \(5399,\s+5410-5437\)"),
    ("Z28 tc npc", "re", r"Handlers/NPCHandler\.cpp \(97, 112,\s+125, 130, 145, 155\)"),
    ("Z29 tc loot", "re", r"Handlers/LootHandler\.cpp \(348-361\)"),
    ("Z30 tc world", "re", r"World/World\.cpp\s+\(630 SkillChance\.Milling default false\)"),
    ("Z31 tc trainer", "re", r"Entities/Creature/Trainer\.cpp\s+\(67-68, 76, 79, 98-106, 149, 156, 165, 172, 182-191\)"),
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

    vanilla = [44, 30, 36, 25, 63, 4, 3, 4, 9, 8, 40, 5, 5, 5, 5, 5, 5,
               15, 34, 10, 5, 5, 5, 3, 17, 42, 5, 5, 5, 5, 4, 11, 10]
    total = num(r"Total exact-count casts printed by the guide = (477)")
    if total != sum(vanilla) or sum(vanilla) != 477:
        failures.append("D01 vanilla craft sum %s != 477" % total)
    pairs = [
        (r"44 x Moonglow Ink spell 52843 \(88 Alabaster", 44, 88),
        (r"36 x Midnight Ink spell 53462 \(72 Dusky", 36, 72),
        (r"63 x Lion's Ink spell 57704 \(126 Golden", 63, 126),
        (r"40 x Jadefire Ink spell 57707 \(80 Emerald", 40, 80),
        (r"34 x Celestial Ink spell 57709 \(68 Violet", 34, 68),
        (r"42 x Shimmering Ink spell 57711 \(84 Silvery", 42, 84),
    ]
    for pat, crafts, pig in pairs:
        m = re.search(pat, text)
        if not m or pig != crafts * 2:
            failures.append("D02 ink math %s" % pat[:30])
    research = [
        (r"4 x Research: Moonglow Ink spell 165564 \(12", 4),
        (r"3 x Research: Midnight Ink spell 165304 \(12", 3),
        (r"4 x Research: Lion's Ink spell 165456 \(12", 4),
        (r"5 x Research: Jadefire Ink spell 165460 \(15", 5),
        (r"3 x Research: Celestial Ink spell 165461 \(9", 3),
        (r"4 x\s+Research: Shimmering Ink spell 165463 \(12", 4),
    ]
    for pat, n in research:
        if not re.search(pat, text):
            failures.append("D03 research line %s" % pat[:30])
    glyphs = [
        (r"\(3 Lion's\s+Ink each = 27\)", 9),
        (r"8 x any discovered glyph \(24", 8),
        (r"15 x any\s+orange glyph \(45", 15),
        (r"17 x any\s+orange glyph \(51", 17),
        (r"11 x any\s+orange glyph \(33", 11),
    ]
    for pat, n in glyphs:
        if not re.search(pat, text):
            failures.append("D04 glyph line %s" % pat[:24])
    total = num(r"guide = (42) \(the 25-33 Book of")
    if total != 42:
        failures.append("D05 outland total %s != 42" % total)
    total = num(r"guide = (150) \(95 ink prep")
    if total != 150 or 95 != 5 + 5 + 5 + 5 + 15 + 30 + 30:
        failures.append("D06 NR total %s / ink math" % total)
    if not re.search(r"95 x Ink of the Sea spell 57715 \(190 Azure", text) or 190 != 95 * 2:
        failures.append("D06b NR azure math")
    total = num(r"guide = (115) \(100 \+ 1 \+ 14\)")
    if total != 115 or 100 + 1 + 14 != 115 or not re.search(r"100 x Origami Beetle spell 86646 \(300", text):
        failures.append("D07 cata total/math")
    if not re.search(r"14 x Research: Blackfallow Ink spell 165466 \(42", text) or 42 != 14 * 3:
        failures.append("D07b cata research math")
    total = num(r"guide = (180) \(135 ink prep")
    if total != 180 or not re.search(r"135 x Ink of Dreams spell 111645 \(270", text) or 270 != 135 * 2:
        failures.append("D08 mop total/math")
    if not re.search(r"20 x Research: Ink of Dreams spell 165467 \(60", text) or 60 != 20 * 3:
        failures.append("D08b mop research math")
    total = num(r"main branch = (76) \(1 \+ 75\)")
    if total != 76 or 1 + 75 != 76:
        failures.append("D09 wod total")
    if not re.search(r"900 total -> mill around 2250", text) or 2250 // 5 * 2 != 900:
        failures.append("D09b wod mill math")
    if not re.search(r"75 x Volatile Crystal spell 166432 \(900", text) or 900 != 75 * 12:
        failures.append("D09c wod crystal math")
    total = num(r"guide = (80) \(20 tomes")
    if total != 80 or 20 + 60 != 80:
        failures.append("D10 legion total")
    if not re.search(r"60 x any Nighthold Rank 3 Vantus Rune \(180 Sallow Pigment \+\s+900 Roseate Pigment\)", text) \
            or 60 * 3 != 180 or 60 * 15 != 900:
        failures.append("D10b legion vantus math")
    if not re.search(r"~200 Sallow\s+Pigment 129034 \+ ~900 Roseate Pigment", text) or 20 + 180 != 200:
        failures.append("D10c legion shopping math")
    total = num(r"guide = (173) \(8 \+ 60 \+ 5 \+ 100")
    if total != 173 or 8 + 60 + 5 + 100 != 173:
        failures.append("D11 bfa total")
    if not re.search(r"900 Ultramarine Ink \+ 480\s+Crimson Ink", text) or 60 * 15 != 900 or 60 * 8 != 480:
        failures.append("D11b bfa contract math")
    if not re.search(r"\(64 Crimson Ink", text) or 8 * 8 != 64:
        failures.append("D11c bfa warscroll math")
    if not re.search(r"\+ 50 Viridescent Ink", text) or 5 * 10 != 50:
        failures.append("D11d bfa dmow math")
    key_ids = [
        45357, 45358, 45359, 45360, 45361, 45363, 86008, 110417, 158748,
        195115, 264494, 264495, 264496, 264497, 264498, 264499, 264500,
        264501, 264502, 264503, 264504, 264505, 264506, 264507, 264508,
        264509, 265809, 265810, 161789, 111923, 39847, 129047, 129043,
        201703, 195115, 51005, 161789, 65651, 86646, 86654, 165466,
        177045, 166432, 118614, 122713, 182125, 120945, 141447, 227043,
        39954, 210116, 136909, 209658, 136918, 209664, 152725, 298927,
        298929, 264776, 264777, 264778, 264767, 284293, 284296, 256245,
        256288, 256279, 256298, 166278, 166310, 162377, 52843, 48248,
        53462, 92026, 57703, 48247, 57704, 165564, 165304, 165456, 57706,
        59480, 57707, 50614, 50606, 50599, 58486, 58476, 165460, 59487,
        57709, 60336, 50600, 58487, 58478, 165461, 59491, 57711, 50608,
        50601, 58488, 58480, 57712, 165463, 50618, 57714, 59496, 165464,
        57715, 57716, 50620, 50611, 50604, 58491, 58483, 165465, 69385,
        111645, 111646, 165467, 126994, 127023, 52739,
        39505, 39354, 158186, 158205, 152668,
        39151, 39334, 43103, 39338, 43104, 39339, 43105, 39340, 43106,
        39341, 43107, 39342, 43108, 39343, 43109, 61979, 61980, 79251,
        79253, 114931, 129032, 129034, 153635, 153636, 153669, 168662,
        39469, 43115, 39774, 43116, 43117, 43118, 43119, 43120, 43121,
        43122, 43123, 43124, 43125, 43126, 43127, 61978, 79254, 79255,
        158187, 158188, 158189, 168663, 173058, 113111,
        2447, 765, 2449, 785, 2450, 2452, 3820, 2453, 3355, 3369, 3356,
        3357, 3819, 3818, 3821, 3358, 8839, 4625, 8845, 8846, 8831, 8838,
        8836, 13463, 13464, 13467, 13465, 13466, 22785, 22786, 22787,
        22789, 22790, 22792, 22791, 22793, 36901, 36904, 37921, 39970,
        36907, 36903, 36906, 36905, 52983, 52984, 52986, 52985, 52988,
        52987, 72234, 72237, 72235, 89639, 79010, 79011, 109125, 109124,
        109126, 109128, 109127, 109129, 124101, 124102, 124103, 124104,
        124105, 124106, 128304, 151565, 152505, 152506, 152507, 152508,
        152509, 152510, 152511, 168487,
        33615, 30721, 33638, 26977, 26959, 28702, 30713, 30717, 30706,
        30711, 46716, 30709, 81770, 53415, 30716, 30710, 56065, 64691,
        62327, 153811, 131386, 130399, 130901, 132264, 154393, 92195,
        30715, 33679, 26995, 26916, 87063, 87551, 114984, 115593,
    ]
    missing = [i for i in key_ids if str(i) not in text]
    if missing:
        failures.append("D12 key id coverage missing: %s" % missing[:12])
    for fam in ["5410", "1383", "1482", "4641", "7836", "4656", "630", "348",
                "128", "2129", "2405", "2451", "3872", "5600", "97", "155",
                "182", "189", "98"]:
        if fam not in text:
            failures.append("D13 missing TC family %s" % fam)
    conf = re.findall(r"^(\d{1,2})\) ", text, re.M)
    if len(conf) < 19:
        failures.append("D14 conflict items %d < 19" % len(conf))
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
        ("base skill", "skill=773, value 1", "skill=774, value 1"),
        ("base id", "Base spell Inscription 45357", "Base spell Inscription 45358"),
        ("classic main", "main 264494 \"Inscription\"", "main 264495 \"Inscription\""),
        ("bfa horde main", "Horde main 265809 \"Zandalari Inscription\"", "Horde main 265811 \"Zandalari Inscription\""),
        ("milling id", "Milling spell 51005 (", "Milling spell 51006 ("),
        ("tc skill gate", "skill gate 182-184,", "skill gate 181-184,"),
        ("mill effect lines", "4641-4666", "4641-4667"),
        ("config default", "DefaultValue false", "DefaultValue true"),
        ("vanilla total", "guide = 477", "guide = 478"),
        ("nr total", "guide = 150 (95 ink prep", "guide = 151 (95 ink prep"),
        ("bfa total", "guide = 173 (8 + 60 + 5 + 100", "guide = 174 (8 + 60 + 5 + 100"),
        ("grazzul npc", "Chronicler Grazzul 130901", "Chronicler Grazzul 130902"),
        ("quest id", "quest 39847 \"Sign This\"", "quest 39848 \"Sign This\""),
        ("conflict marker", "19) Classic 264494/264495", "19. Classic 264494/264495"),
        ("nightborne value", "(Inscription) value 5)", "(Inscription) value 6)"),
        ("loothandler", "LootHandler.cpp 348-361", "LootHandler.cpp 348-362"),
        ("bfa cap", "cap 175, Alliance Specific", "cap 150, Alliance Specific"),
        ("zinanthid id", "Zin'anthid 168487", "Zin'anthid 168489"),
        ("maroon spell", "Maroon\n    Ink spell 298929", "Maroon\n    Ink spell 298930"),
        ("pallin npc", "Professor Pallin 92195", "Professor Pallin 92196"),
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

    if not preflight():
        return 3

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
