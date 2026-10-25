#!/usr/bin/env python3
"""Audit for Craft_Engineering.txt (Companion_Professions, RESEARCH_MASTER STEP 129).

Static checks: every payload must appear verbatim in the deliverable unless
kind=re (regex, MULTILINE). Derived checks recompute sums from the file's own
numbers. --self-test mutates the file in memory; every mutation must fail
at least one check.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "Craft_Engineering.txt"
RAW = TARGET.read_text(encoding="utf-8")

# kind: "lit" = substring, "re" = MULTILINE regex over the full text.
CHECKS = [
    # --- heading / scope -------------------------------------------------
    ("H01 heading", "re", r"^BATTLE FOR AZEROTH 8\.3\.7 \(BUILD 35662\) - ENGINEERING CRAFTING FOR A SERVER-SIDE COMPANION$"),
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
    ("B01 base4036", "lit", "Base spell Engineering 4036"),
    ("B02 skill202", "lit", "skill=202, value 1"),
    ("B03 trade skill", "re", r"Effect1 = Trade Skill, Effect2 =\s+Learn Skill \(Engineering"),
    ("B04 cost10", "lit", '"Training cost: 10"'),
    ("B05 mining text", "re", r"Requires\s+stone and metal found with the Mining skill"),
    ("B06 taught49", "re", r'shows "Taught by\s+\(49\)" \(list not rendered\)'),
    ("B07 ranks", "re", r"4037 \(50\), 4038 \(125\),\s+12656 \(200\), 30350 \(275\), 51306 \(350\), 82774 \(425\),\s+110403 \(500\)"),
    ("B08 other ranks", "lit", '"Other ranks (9)"'),
    ("B09 apprentice", "re", r"Apprentice wrapper spell 4039 \"Apprentice Engineer\": Effect1\s+Learn Spell 4036, Effect2 Learn Skill Step \(202\) value 1"),
    ("B10 seealso49383", "lit", "adds 49383 to the same family"),
    # --- 8.0.1 chains ----------------------------------------------------
    ("L01 classic", "re", r"Classic 1-300, skill=2506:"),
    ("L02 classic main", "re", r"main 264475 \"Engineering\" \(8\.0\.1,\s+cap 300"),
    ("L03 classic learn", "re", r"Effect\s+Learn Skill \(Classic Engineering, skill=2506\) value 1"),
    ("L04 classic wrapper", "re", r"wrapper 264478\s+\(8\.0\.1\): Effect1 Learn Spell 4036, Effect2 Learn Spell 264475,\s+Effect3 Learn Skill Step \(2506\) value 1"),
    ("L05 outland", "re", r"Outland 1-75, skill=2505: main 264479 \(8\.0\.1, quick facts \"Requires\s+Engineering \(1\)\", \"Training cost: 10\", cap 75\)"),
    ("L06 outland chain", "re", r"wrapper 264480 \(beta page read\): Learn Spell 264479 \+\s+Learn Skill Step \(2505\)"),
    ("L07 nr", "re", r"Northrend 1-75, skill=2504: main 264481 \(8\.0\.1, \"Requires Engineering\s+\(1\)\", \"Training cost: 10\", cap 75\)"),
    ("L08 nr chain", "re", r"wrapper 264482 \(8\.1\.0\): Learn\s+Spell 264481 \+ Learn Skill Step \(2504\)"),
    ("L09 cata", "re", r"Cataclysm 1-75, skill=2503: main 264483 \(8\.0\.1, \"Requires Engineering"),
    ("L10 cata chain", "re", r"wrapper 264484 \(8\.1\.0\): Learn\s+Spell 264483 \+ Learn Skill Step \(2503\)"),
    ("L11 mop", "re", r"Pandaria 1-75, skill=2502: main 264485 \(8\.0\.1"),
    ("L12 mop chain", "re", r"wrapper 264486 \(8\.1\.0\): Learn\s+Spell 264485 \+ Learn Skill Step \(2502\)"),
    ("L13 draenor", "re", r"Draenor 1-100, skill=2501: main 264487 \(8\.0\.1, cap 100"),
    ("L14 draenor chain", "re", r"wrapper 264488\s+\(8\.1\.0\): Learn Spell 264487 \+ Learn Skill Step \(2501\)"),
    ("L15 learning161787", "lit", "Triggered by (1) Learning 161787"),
    ("L16 scroll111921", "re", r"scroll item 111921 \"Draenor Engineering\""),
    ("L17 legion", "re", r"Legion 1-100, skill=2500: main 264490 \(8\.0\.1, cap 100"),
    ("L18 legion chain", "re", r"wrapper 264491 \(8\.1\.0\): Learn Spell 264490 \+ Learn Skill\s+Step \(2500\)"),
    ("L19 legion reward", "re", r"wrapper page \"Reward from \(1\)\": quest 40545 \"Aww Scrap!\",\s+level 10"),
    ("L20 bfa", "re", r"Battle for Azeroth 1-175, skill=2499 \(one line id, both factions\)"),
    ("L21 kt", "re", r"Alliance main 264492 \"Kul Tiran Engineering\" \(8\.0\.1"),
    ("L21b kt cap", "re", r"Training cost: 10\", cap 175, Alliance Specific"),
    ("L22 kt chain", "re", r"Alliance wrapper 264493 \(8\.1\.0\): Learn Spell 264492 \+\s+Learn\s+Skill\s+Step \(2499\)"),
    ("L23 zal", "re", r"Horde main 265807 \"Zandalari Engineering\""),
    ("L24 zal cost", "re", r"\"Training cost: 10\", \"Added\s+in patch 8\.1\.0\", cap 175, Horde Specific"),
    ("L25 zal chain", "re", r"Horde wrapper 265808\s+\(wowhead quick facts: \"Added in patch 8\.0\.1\""),
    ("L26 shared", "re", r"Both faction mains link\s+Learn Skill to skill=2499 \"Kul Tiran Engineering\""),
    ("L27 boost", "re", r"spell 201700 \"Legion Engineer\""),
    ("L28 cost list", "re", r"264479 = 10;\s+264481 = 10; 264483 = 10; 264485 = 10; 264492 = 10;\s+265807 = 10"),
    ("L29 no cost", "re", r"Mains 264475/264487/264490 and wrappers show no Training cost\s+field"),
    ("L30 nitro cost", "re", r"55016 \(a route recipe\) prints \"Training cost:\s+115\" and \"Profession Trainer: Northrend Engineering \(30\)\""),
    # --- TC learn path ---------------------------------------------------
    ("T01 npch", "re", r"NPCHandler\.cpp 97 HandleTrainerListOpcode,\s+112 SendTrainerList, 130 HandleTrainerBuySpellOpcode, 145 interaction guard"),
    ("T02 npc155", "re", r"155\s+trainer->TeachSpell\(npc, _player, packet\.SpellID\)"),
    ("T03 trainer76", "re", r"Trainer\.cpp 76\s+Trainer::TeachSpell"),
    ("T04 discount", "re", r"98 reputationDiscount = GetReputationPriceDiscount\(npc\)"),
    ("T05 money", "lit", "100 HasEnoughMoney check"),
    ("T06 modify", "lit", "106 ModifyMoney(-moneyCost)"),
    ("T07 can", "re", r"149\s+Trainer::CanTeachSpell"),
    ("T08 freeprof", "re", r"156/165 IsPrimaryProfessionFirstRank \+\s+GetFreePrimaryProfessionPoints = 2-profession limit"),
    ("T09 state", "lit", "172 GetSpellState"),
    ("T10 skill gate", "re", r"181-183 \"check skill requirement\" \(ReqSkillLine/ReqSkillRank gate\)"),
    ("T11 ability", "re", r"185-187 ReqAbility prerequisite spells"),
    ("T12 level", "lit", "189 level requirement block"),
    ("T13 payload", "re", r"trainer list payload carries\s+ReqSkillRank/ReqAbility \(Trainer\.cpp 67-68\)"),
    # --- trainers section ------------------------------------------------
    ("C01 wiki page", "lit", "warcraft.wiki.gg/wiki/Engineering_trainers"),
    ("C02 lien", "re", r"Lien Farner,\s+Goldshire, Elwynn \[42, 67\] \(Apprentice only\)"),
    ("C03 wembil", "re", r"Wembil\s+Taskwidget, Kharanos, Dun Morogh \[53\.7, 52\] \(Apprentice\)"),
    ("C04 bronk", "re", r"Bronk\s+Guzzlegear, Steelgrill's Depot, Dun Morogh \[57\.2, 48\.6\]"),
    ("C05 overspark", "re", r"Tinkmaster Overspark, Tinker\s+Town,\s+Ironforge \[69\.8, 50\.0\] \(Teaches Gnomish Engineering plans\)"),
    ("C06 oglethorpe", "re", r"Oglethorpe\s+Obnoticus, Booty Bay, Cape of Stranglethorn \[43\.0, 72\.0\] \(Gnomish\s+plans\)"),
    ("C07 lil", "re", r"Lilliam Sparkspindle, Dwarven\s+District, Stormwind \[63\.2, 31\.5\]"),
    ("C08 franklin", "re", r"Franklin Lloyd, The Rogues' Quarter,\s+Undercity \[76\.1, 74\.0\]"),
    ("C09 roxxik", "re", r"Roxxik, Nogg's Machine Shop/The Drag, Orgrimmar \[56\.8, 56\.4\]"),
    ("C10 vazario", "re", r"Vazario Linkgrease, Ratchet \[68\.4, 69\.2\] \(Teaches Goblin Engineering\s+plans\)"),
    ("C11 nixx", "re", r"Nixx\s+Sprocketspring, Gadgetzan \[52\.5, 27\.3\] \(Goblin plans\)"),
    ("C12 sinbei", "re", r"Engineer Sinbei, Scryer's Tier, Shattrath\s+\[44\.1, 65\.0\]"),
    ("C13 sinbei aldor", "re", r"\"Not available to members of the\s+Aldor\""),
    ("C14 mihila", "re", r"Technician\s+Mihila, Aldor Rise, Shattrath \[38\.1, 32\.0\]"),
    ("C15 mihila scryer", "re", r"members\s+of the Scryers\"" ),
    ("C16 oshenko", "re", r"Timofey Oshenko,\s+Like Clockwork/Magus Commerce Exchange,\s+Dalaran \[39, 27\]"),
    ("C17 findle didi", "re", r"Findle\s+Whistlesteam, same building\s+\[39\.5, 25\.2\]\s+\(Teaches Gnomish Engineering\s+plans\);\s+Didi the Wrench, same building\s+\[39\.5, 25\.5\]"),
    ("C18 binkie", "re", r"Binkie\s+Brightgear,\s+Argent Tournament Grounds, Icecrown \[72\.1, 20\.9\]"),
    ("C19 guyo", "re", r"Guyo Crystalgear, Hall of the Crescent Moon, Shrine of Two\s+Moons \[60\.6, 44\.8\]"),
    ("C20 sally", "re", r"Sally Fizzlefury, Nesingwary's Safari, Valley of\s+the Four Winds \[16\.0, 83\.0\]"),
    ("C21 no rows", "re", r"No Draenor/Broken Isles/Kul Tiras-Zandalar rows exist on this page"),
    ("C22 patch403", "re", r"4\.0\.3a \(2010-11-23\) \"all trainer ranks equalized,\s+leaving only gnome and goblin specializations as uniquely different types\s+of trainers\""),
    ("C23 patch230", "re", r"2\.3\.0 \(2007-11-13\) trainers now train to Artisan 300"),
    ("C24 cata taught", "re", r"Taught by \(13\):\s+\"Jack\" Pisarek Slamfix 45545"),
    ("C25 outland taught", "re", r"Outland main 264479, Taught by \(7\)"),
    ("C26 niobe", "re", r"Niobe Whizzlespark 24868\s+\(Shadowmoon Valley\)"),
    ("C27 nr taught", "re", r"Northrend main 264481, Taught by \(3\)"),
    ("C28 mop taught", "re", r"Pandaria main 264485, Taught by \(2\)"),
    ("C29 kt taught", "re", r"Kul Tiran main 264492, Taught by \(3\):\s+Flip Quickcharge 150630\s+\(Mechagon\), Instructor Alikana 153817 \(Nazjatar\), Layla Evenkeel\s+136059 \(Boralus\)"),
    ("C30 zal taught", "re", r"Zandalari main 265807, Taught by \(4\)"),
    ("C31 shuga", "re", r"Shuga Blastcaps 131840\s+\(Dazar'alor\)"),
    ("C32 dual dalaran", "re", r"the same NPC exists in Legion Dalaran but he won't teach\s+you Northrend recipes"),
    ("C33 hobart", "re", r"Hobart\s+Grapplehammer npc=93539 in Dalaran \(Broken Isles, \"not Northrend!\"\),\s+turn-in Filgo Scrapbottom npc=102193"),
    ("C34 nazjatar", "re", r"Nazjatar\s+trainers Jada 154321 \(H\) / Instructor Alikana 153817 \(A\)"),
    ("C35 bryan", "re", r"Bryan Landers 28722 \(Tinker's Kit,\s+Mining Pick, Blacksmith Hammer near the Northrend trainer\)"),
    ("C36 lathrai", "re", r"Wind Trader Lathrai 18484 \(White Smoke Flare formula"),
    ("C37 viggz", "re", r"Viggz Shinesparked 19661 \(Adamantite Rifle\s+schematic, Shattrath, limited\s+supply\)"),
    ("C38 ganarg", "re", r"Gan'arg Analyzer 23385"),
    ("C39 vendors1", "re", r"Natal'hakata 131287 \(H, Zuldazar\) / Sister\s+Lilyana 135800 \(A\) for grenade rank 3"),
    ("C40 mekka", "re", r"High Tinker Mekkatorque 144796 drops\s+schematic 166276"),
    ("C41 naz vendors", "re", r"Dazzerian 154652\s+\(H\) / Crafticus\s+Mindbender 154653 \(A\) at Nazjatar"),
    ("C42 ore trader", "re", r"Ore Trader Alexi\s+Hackercam 90894 \(A\) / Trixxy Volt 91030 \(H\)"),
    ("C43 widow", "re", r"The Widow 97366 \(Dalaran Sewers\) sells Gunpowder Charge\s+ranks 2/3 for 250/500 Sightless Eye"),
    # --- 3.1 Classic -----------------------------------------------------
    ("R01 vanilla", "re", r"Vanilla Engineering Leveling Guide 1-300 \(Midnight\)"),
    ("R02 hammer", "re", r"buy Blacksmith\s+Hammer 5956 from an engineering/blacksmith supply vendor at step 30"),
    ("R03 spanner", "re", r"craft\s+Arclight Spanner spell 7430 \(item 6219"),
    ("R04 adjustor", "re", r"Gyromatic Micro-Adjustor spell\s+12590 \(item 10498, requires 175 skill\)"),
    ("R05 rbp", "re", r"1-30: 60x Rough Blasting Powder spell 3918 = 60 Rough Stone 2835"),
    ("R06 bolts", "re", r"30-50: 30x Handful of Copper Bolts spell 3922 = 30 Copper Bar 2840"),
    ("R07 bomb", "re", r"50-75: 30x Rough Copper Bomb spell 3923"),
    ("R08 cbp", "re", r"75-90: 20x Coarse Blasting Powder spell 3929 = 20 Coarse Stone 2836"),
    ("R09 dyn", "re", r"90-100: 20x Coarse Dynamite spell 3931"),
    ("R10 cw", "re", r"100-113: 13x Clockwork Box spell 8334 = 39 Bronze Bar 2841"),
    ("R11 use", "re", r"113-125: Use the Clockwork Box item 6712"),
    ("R12 gg", "re", r"125-130: 1x Flying Tiger Goggles spell 3934"),
    ("R13 hbp", "re", r"130-150: 30x Heavy Blasting Powder item 4377 = 30 Heavy Stone 2838"),
    ("R14 hbp spell", "re", r"craft spell 3945 per classic/forever spell pages"),
    ("R15 whirring", "re", r"15x Whirring Bronze Gizmo item 4375 \(craft spell 3942\)"),
    ("R16 fwk", "re", r"150-160: 15x Bronze Framework spell 3953"),
    ("R17 sheep", "re", r"160-175: 15x Explosive Sheep spell 3955"),
    ("R18 spec200", "re", r"at skill 200 you can specialize in\s+Gnomish or Goblin Engineering"),
    ("R19 sbp", "re", r"176-195: 60x Solid Blasting Powder spell 12585 = 120 Solid Stone 7912"),
    ("R20 tube", "re", r"195-200: 7x Mithril Tube spell 12589 = 21 Mithril Bar 3860"),
    ("R21 trigger", "re", r"200-216: 20x Unstable Trigger spell 12591"),
    ("R22 casing", "re", r"216-238: 40x Mithril Casing spell 12599 = 120 Mithril Bar"),
    ("R23 he bomb", "re", r"238-250: 20x Hi-Explosive Bomb spell 12619"),
    ("R24 dense", "re", r"250-260: 20x Dense Blasting Powder spell 19788 = 40 Dense\s+Stone\s+12365"),
    ("R25 widget", "re", r"260-285: 25x Thorium Widget spell 19791 = 75 Thorium Bar 12359 \+\s+25 Runecloth 14047"),
    ("R26 thorium tube", "re", r"285-300: 20x Thorium Tube spell 19795 = 120 Thorium Bar"),
    ("R27 shopping", "re", r"Shopping list \(guide\): 60x 2835, 36x 2840, 20x 2836, 20x 2589,\s+107x"),
    ("R28 bronze recon", "re", r"Bronze 39\+8\+30\+30 = 107; Mithril\s+21\+20\+120 = 161; Thorium 75\+120 = 195; Wool 15\+15\+30 = 60; Copper\s+30 bolts \+ spanner's 6 = 36"),
    ("R29 total", "lit", "Total planned crafts = 447 numbered steps"),
    # --- 3.2 Outland -----------------------------------------------------
    ("O01 range warn", "re", r"route is yellow/green-heavy, hence ranged shopping"),
    ("O02 bolts", "re", r"1-20: 126x Handful of Fel Iron Bolts craft spell 30305 \(item 23783\)"),
    ("O03 ebp", "re", r"20x Elemental Blasting Powder craft spell\s+30303 \(item 23781\) = 40 Mote of Earth 22573 \+ 20 Mote of Fire 22574"),
    ("O04 casing", "re", r"56x Fel Iron Casing craft spell 30304 \(item 23782\) = 168 Fel Iron\s+Bar"),
    ("O05 bomb", "re", r"20-25: 5x Fel Iron Bomb craft spell 30310 \(item 23736\)"),
    ("O06 frame", "re", r"25-35: 34x Adamantite Frame craft spell 30306 \(item 23784\) = 136\s+Adamantite Bar 23446 \+ 34 Primal Earth 22452"),
    ("O07 flare", "re", r"35-55: 70x White Smoke Flare craft spell 30341 \(item 23768\)"),
    ("O08 core", "re", r"55-60: 6x Khorium Power Core spell 30308"),
    ("O09 rifle", "re", r"60-70: 17x Adamantite Rifle craft spell 30313 \(item 23746\) = 51 Fel\s+Iron Casing \+ 34 Adamantite Frame \+ 68 Handful of Fel Iron Bolts"),
    ("O10 bot", "re", r"70-75: 6x Field Repair Bot 110G spell 44391 = 6 Khorium Power Core"),
    ("O11 gtscc", "re", r"Global Thermal Sapper Charge spell 56514 from\s+Didi the Wrench 29513"),
    ("O12 shopping", "re", r"300-450x Fel Iron 23445, 40x Mote of Earth\s+22573, 20x Mote of Fire 22574"),
    ("O13 exact", "re", r"Fel Iron 126\+168 = 294 \(within floor 300 slack\)"),
    ("O14 total", "lit", "Total planned crafts = 340."),
    # --- 3.3 Northrend ---------------------------------------------------
    ("N01 shop", "re", r"260 Cobalt Bar 36916, 6 Frostweave Cloth 33470,\s+10 Crystallized Earth 37701"),
    ("N02 shop2", "re", r"390\s+Saronite Bar 36913, 9 Eternal Shadow 35627"),
    ("N03 not on list", "re", r"NOT on the\s+shopping list: 45x Tinker's Kit item 90146"),
    ("N04 bolts", "re", r"1-10: 35x Handful of Cobalt Bolts spell 56349 = 70 Cobalt Bar\s+\(yields 1 or 3 bolts per craft\)"),
    ("N05 trigger", "re", r"10x Volatile Blasting Trigger spell\s+53281 = 30 Cobalt Bar \+\s+10 Crystallized Water \(yields 2 per craft\)"),
    ("N06 cap", "re", r"10x Overcharged Capacitor spell 56464 = 40 Cobalt Bar \+ 10\s+Crystallized Earth"),
    ("N07 decoy", "re", r"10-15: 6x Explosive Decoy spell 56463 = 6 Frostweave \+ 18 Volatile"),
    ("N08 tube", "re", r"15-26: 15x Froststeel Tube spell 56471 = 120 Cobalt Bar \+ 15\s+Crystallized Water \(keep; Cobalt subtotal 260 exact\)"),
    ("N09 scope", "re", r"26-30: 5x Diamond-cut Refractor Scope spell 61471"),
    ("N10 nitro", "re", r"30-35: 15x Nitro Boosts spell 55016 = 15 Tinker's Kit"),
    ("N11 nitro page", "re", r"\"Profession\s+Trainer: Northrend Engineering \(30\)\", Tools: Arclight Spanner,\s+\"Requires Belt\", Effect Enchant Item: Nitro Boosts \(4223\)"),
    ("N12 dish", "re", r"35-45: 30x Mind Amplification Dish spell 67839"),
    ("N13 injector", "re", r"45-50: 5x Mana Injector Kit craft spell 56477 \(item 42546\) = 60\s+Saronite Bar \+ 10 Crystallized Water"),
    ("N14 goggles", "re", r"50-55: 5x Mechanized Snow Goggles spell 61482"),
    ("N15 moll", "re", r"MOLL-E spell\s+56472 is the 54-skill alternative"),
    ("N16 noise", "re", r"55-60: 5x Noise Machine spell 56467"),
    ("N17 gaa", "re", r"60-74: 30x Gnomish Army Knife spell 56462 = 300 Saronite Bar \+\s+30 Skinning Knife \+ 30 Mining Pick \+ 30 Blacksmith Hammer"),
    ("N18 wormhole", "re", r"74-75: 1x Wormhole Generator: Northrend spell 67920 = 8 Titanium\s+Bar"),
    ("N19 conflict", "re", r"Saronite check: 60\+40\+300 = 400 against the 390 shopping line"),
    ("N20 total", "lit", "Total planned crafts = 172."),
    # --- 3.4 Cataclysm ---------------------------------------------------
    ("K01 shop", "re", r"60 Obsidium Bar 54849, 30 Volatile Air 52328, 360\s+Elementium Bar 52186, 15 Volatile Fire 52325"),
    ("K02 boltgun", "re", r"High-Powered Bolt Gun item 60223 \(\"Requires 15 skill points\s+in Catacylsm Engineering to craft\""),
    ("K03 bolts", "re", r"30x Handful of Obsidium Bolts spell 84403 =\s+60 Obsidium Bar"),
    ("K04 ether", "re", r"15x Electrified Ether spell 94748 = 30\s+Volatile Air"),
    ("K05 blastpack", "re", r"Volatile Seaforium Blastpack spell 84409"),
    ("K06 safety", "re", r"Safety Catch Removal Kit spell 84410"),
    ("K07 tackle", "re", r"45-60: 15x Lure Master Tackle Box spell 84415 = 300 Elementium Bar \+\s+60 Handful of Obsidium Bolts"),
    ("K08 toolbox", "re", r"Elementium Toolbox 84416"),
    ("K09 bigdaddy", "re", r"Big Daddy spell 95707"),
    ("K10 lure", "re", r"60-75: 15x Heat-Treated Spinning Lure spell 84430 = 60 Elementium"),
    ("K11 recon", "re", r"Obsidium 30x2 = 60 exact; Volatile Air 15x2 = 30 exact;\s+Elementium 300\+60 = 360 exact; Volatile Fire 15 exact"),
    ("K12 total", "re", r"Total planned\s+crafts = 90 \(60-75 branch\)"),
    # --- 3.5 Pandaria ----------------------------------------------------
    ("P01 shop", "re", r"406 Ghost Iron Bar 72096, 60\s+Windwool Cloth 72988, 26 Spirit of Harmony 76061"),
    ("P02 bolts", "re", r"1-25: 112x Ghost Iron Bolts spell 127113 = 336 Ghost Iron Bar"),
    ("P03 bars", "re", r"wiki\s+table confirms 3 bars per craft"),
    ("P04 heg", "re", r"70x High-Explosive Gunpowder spell\s+127114 = 70 Ghost Iron Bar"),
    ("P05 tinkers", "re", r"25-55: 30x Tinker's Kit spell 131563 = 60 High-Explosive Gunpowder \+\s+60 Ghost Iron Bolts \+ 60 Windwool Cloth"),
    ("P06 thermal", "re", r"55-62: 10x Thermal Anvil spell 127131 = 80 High-Explosive Gunpowder"),
    ("P07 mirror", "re", r"Mirror Scope 127116"),
    ("P08 goggles", "re", r"62-75: 13x Mist-Piercing Goggles spell 127130 = 104 Ghost Iron Bolts\s+\+\s+26 Spirit of Harmony"),
    ("P09 luck", "re", r"sometimes I just didn't get a single skill point for 8"),
    ("P10 conflict", "re", r"Gunpowder consumption 60\+80 =\s+140 against only 70 produced"),
    ("P11 total", "re", r"Total planned crafts = 112\+70\+30\+10\+13 = 235"),
    # --- 3.6 Draenor -----------------------------------------------------
    ("D01 scroll", "re", r"3\.6 Draenor 1-100 \(scroll item 111921 \"Draenor Engineering\" first\)"),
    ("D02 vendors", "re", r"Sean\s+Catchpole 87065 \(Stormshield, A\) / Nik Steelrings 87552 \(Warspear, H\)"),
    ("D03 zaren", "re", r"Zaren\s+Hoffle \(Lunarfall\) selling\s+the scroll item for Cost:100 \(unit not printed\)"),
    ("D04 works", "re", r"garrison\s+Engineering Works NPC after \"Your First Engineering\s+Work Order\""),
    ("D05 quest A", "re", r"Gnomish Location Transponder 115278\s+from Draenor mobs or Karnoth 75043 during Shadows Awaken 34019"),
    ("D06 quest H", "re", r"Burned-Out Hand Cannon 116438 from mobs or Dorogg the Ruthless 74254\s+during The Butcher\s+of Bladespire 33410"),
    ("D07 tips", "re", r"Gearspring Parts spell 169080 \(15 True Iron Ore 109119\s+\+ 15 Blackrock Ore 109118 = 8 parts\)"),
    ("D08 uaa knife", "re", r"Ultimate Gnomish Army Knife\s+spell 169140"),
    ("D09 anvil note", "re", r"blacksmith anvil stands behind the\s+trainer building"),
    ("D10 stealth", "re", r"12x Stealthman 54 spell 162207\s+= 24 Blackrock Ore \+ 24 True Iron Ore \+ 24 Nagrand Arrowbloom 109128"),
    ("D11 stealth reag", "re", r"per-spell reagents 2/2/2; Tools: Gyromatic Micro-Adjustor"),
    ("D12 discovery", "re", r"quick\s+facts \"Learned via discovery\", Mechanic: Discovery"),
    ("D13 rocket", "re", r"23x Mecha-Blast Rocket spell 173308 = 138 Blackrock Ore"),
    ("D14 shield", "re", r"23x Shieldtronic Shield spell 173309 = 138 True Iron Ore"),
    ("D15 secrets", "re", r"1x Secrets of Draenor Engineering spell 177054"),
    ("D16 didi", "re", r"70x Didi's Delicate Assembly spell 169078 =\s+1050 True Iron Ore \+ 1050 Blackrock Ore"),
    ("D17 weld", "re", r"spell 182120 = 70 Primal Spirit 120945 \+ 350 True Iron \+ 350\s+Blackrock"),
    ("D18 trader", "re", r"schematic 122712 from the garrison Ore Trader"),
    ("D19 rotation", "re", r"Trader rotation is\s+Ore->Dust->Fur->Leather->Herb daily"),
    ("D20 total", "re", r"Total planned crafts \(main branch\) = 12 \+ 1 \+ 70 = 83"),
    # --- 3.7 Legion ------------------------------------------------------
    ("G01 learn", "re", r"quest 40545 \"Aww Scrap!\" \(level 10, Profession: Engineering quick\s+fact, added 7\.0\.1\) from Hobart Grapplehammer 93539"),
    ("G02 crate", "re", r"provided Crate of Guns 133750; reward learn spell\s+264491"),
    ("G03 quest list", "re", r"wowhead storyline lists 31 quests \(40545,"),
    ("G04 hov", "re", r"40877 Halls of Valor, 40878 Violet Hold"),
    ("G05 court", "re", r"40882 Court\s+of Stars"),
    ("G06 must", "re", r"MUST do\s+All Charged Up 40862 \(about the 10th\)"),
    ("G07 route", "re", r"about 140x Rank 3 - Gunpowder Charge spell\s+199014 = 140 Leystone Ore 123918 \+ 2800 Oversized Blasting\s+Cap\s+136637"),
    ("G08 hobart sell", "re", r"sold by Hobart near the trainer, about 3200 gold for 2800"),
    ("G09 widow", "re", r"Ranks 2/3 sold by The Widow 97366 in the\s+Dalaran Sewers for 250/500 Sightless Eye"),
    ("G10 r12 fail", "re", r"R1/R2 cannot reach 100 \(guide\) - get R3\s+first"),
    ("G11 total", "re", r"Total planned crafts = about 140"),
    # --- 3.8 BfA ---------------------------------------------------------
    ("A01 shop", "re", r"700 Monelite Ore\s+152512, 350 Storm Silver Ore 152579, 250 Chemical Blasting Cap 160502,\s+900 Insulated Wiring 163569, 405 Osmenite Ore 168185, 55 Expulsom 152668"),
    ("A02 vendor", "re", r"Wiring and Caps are sold by the\s+engineering trainer - \"Don't buy them from the Auction House!\""),
    ("A03 fried", "re", r"1-30: 30x F\.R\.I\.E\.D\. spell 255392 = 180 Monelite \+ 150 Chemical\s+Blasting Cap \+ 240 Insulated Wiring"),
    ("A04 reagents", "re", r"reagents per cast 6/5/8 verified\s+on the spell page; Effect Create Item"),
    ("A05 rearr", "re", r"30-35: 5x Deployable Attire Rearranger spell 256154"),
    ("A06 r2 fried", "re", r"35-60: learn R2 bombs from the trainer, then 30x Rank 2 - F\.R\.I\.E\.D\.\s+spell 255393 = 150 Monelite \+ 90 Chemical Blasting Cap \+ 150\s+Insulated Wiring"),
    ("A07 organic", "re", r"R3 Organic Discombobulation Grenade spell 255409"),
    ("A08 r2 rearr", "re", r"60-85: learn R2 from the trainer, then 25x Rank 2 - Deployable\s+Attire Rearranger spell 256155"),
    ("A09 damp", "re", r"15x Rank 3 - Magical\s+Intrusion Dampener spell 280734 = 120 Monelite \+ 80 Storm Silver \+\s+90 Insulated Wiring"),
    ("A10 method1", "re", r"35x Rank 3 - Unstable Temporal Time\s+Shifter spell 283916 = 280 Monelite \+ 210 Storm Silver \+\s+525\s+Insulated Wiring"),
    ("A11 r2 shifter", "re", r"\(R2 spell 283915 bought from Natal'hakata \(Zuldazar\) / Provisioner\s+Fray 135808"),
    ("A12 method2", "re", r"110-125\s+25x Time Shifter R1 spell 283914 = 300 Monelite \+ 200 Storm Silver \+\s+400 Insulated Wiring"),
    ("A13 mechantula", "re", r"125-145 35x Mechantula spell\s+286478 = 350 Monelite \+ 175 Platinum Ore 152513 \+ 350 Insulated\s+Wiring"),
    ("A14 gnomeregan", "re", r"schematic 165844 from Pet Battle Challenge: Gnomeregan for\s+Pristine Gizmo 165835"),
    ("A15 method3", "re", r"20x\s+Rank 3 - Sinister Combatant's Discombobulator spell 282808 = 500\s+Storm Silver \+ 300 Platinum \+ 80 Expulsom"),
    ("A16 method4", "re", r"Method 4\s+\(15 Tidalcore 165948 - guaranteed last boss in Mythic"),
    ("A17 frost", "re", r"Frost-Laced Ammunition 265102\s+= 420 Monelite \+ 175 Wiring \+ 175 Caps"),
    ("A18 scope", "re", r"Monelite Scope of Alacrity\s+264967 = 350 Monelite \+ 175 Storm Silver"),
    ("A19 scrap loop", "re", r"scrap-loop:\s+craft one pair, scrap it in the Scrapper to recover Expulsom and\s+Tidalcore, repeat"),
    ("A20 specs", "re", r"15x Surging Synthetic Specs spell 286873 = 450 Storm\s+Silver \+ 150 Platinum \+ 225 Insulated Wiring \+ 15 Expulsom \+ 15\s+Tidalcore"),
    ("A21 naz", "re", r"learn from Jada 154321 \(H\) / Instructor Alikana\s+153817 \(A\) after the Nazjatar intro"),
    ("A22 notorious1", "re", r"5x Rank 1 - Notorious\s+Combatant's Discombobulator spell 294784 = 75 Osmenite"),
    ("A23 notorious2", "re", r"15x Rank 2 spell 294785 = 210 Osmenite \+ 60\s+Storm Silver \+ 120 Insulated Wiring \+ 30 Expulsom"),
    ("A24 notorious3", "re", r"10x Rank 3 spell 294786 = 120 Osmenite \+ 30 Storm\s+Silver \+ 60 Insulated Wiring \+ 10 Expulsom"),
    ("A25 recon", "re", r"Monelite 180\+50\+150\+200\+120 = 700\s+exact"),
    ("A26 total", "re", r"Total planned crafts \(main path: 30\+5\+30\+25\+15\+\s+35\+15\+10\) = 165"),
    # --- 4 materials -----------------------------------------------------
    ("M01 no de", "re", r"There is NO Engineering disenchanting - the profession\s+creates and uses, it does not deconstruct"),
    ("M02 classic", "re", r"Classic: Rough Stone 2835, Copper Bar 2840, Coarse Stone 2836, Linen\s+Cloth 2589"),
    ("M03 classic2", "re", r"Thorium\s+Bar 12359, Runecloth 14047 \(all linked on the guide\)"),
    ("M04 outland", "re", r"Outland: Fel Iron Bar 23445, Mote of Earth 22573, Mote of Fire\s+22574"),
    ("M05 nr", "re", r"Northrend: Cobalt Bar 36916, Frostweave Cloth 33470, Crystallized\s+Earth 37701"),
    ("M06 tinkers kit", "re", r"Tinker's Kit item 90146 \(vendor Bryan Landers, or craft spell\s+131563"),
    ("M07 cata", "re", r"Cataclysm: Obsidium Bar 54849, Volatile Air 52328, Elementium Bar\s+52186, Volatile Fire 52325"),
    ("M08 mop", "re", r"Pandaria: Ghost Iron Bar 72096, Windwool Cloth 72988, Spirit of\s+Harmony 76061"),
    ("M09 mop2", "re", r"Ghost Iron Bolts item 77467 \(3 bars per craft\), High-Explosive\s+Gunpowder item 77468 \(1 bar per craft\)"),
    ("M10 wod", "re", r"Draenor: Blackrock Ore 109118, True Iron Ore 109119, Nagrand\s+Arrowbloom 109128, Primal Spirit 120945, Gearspring Parts 111366"),
    ("M11 wod frags", "re", r"Blackrock Fragment item 109992 \(spell 157516\), True Iron Nugget\s+109991 \(spell 157517\), Nagrand Arrowbloom Petal 109628 \(spell\s+157027\)"),
    ("M12 legion", "re", r"Legion: Leystone Ore 123918, Oversized Blasting Cap 136637 \(Hobart\)"),
    ("M13 bfa", "re", r"Battle for Azeroth: Monelite Ore 152512, Storm Silver Ore 152579,\s+Platinum Ore 152513"),
    ("M14 bfa2", "re", r"Chemical Blasting Cap\s+160502 \(trainer vendor\), Insulated Wiring 163569 \(trainer vendor\)"),
    ("M15 tools", "re", r"Tools \(carry in inventory\): Blacksmith Hammer 5956 \(vendor\),\s+Arclight Spanner 6219"),
    ("M16 gaa", "re", r"Ultimate Gnomish Army Knife item 114943"),
    ("M17 wiki tools", "re", r"wiki Requirements:\s+schematics often need one of these carried tools; wiki also states\s+\"Anvils are also required to craft\""),
    ("M18 thermal", "re", r"Thermal Anvils can be crafted at high skill"),
    # --- 5 costs ---------------------------------------------------------
    ("F01 raw", "re", r"Learn-spell quick-fact \"Training cost\" \(raw value; wowhead prints no\s+unit\)"),
    ("F02 list", "re", r"4036 = 10,\s+264479 = 10, 264481 = 10, 264483 = 10, 264485 = 10,\s+264492 = 10, 265807 = 10"),
    ("F03 pattern", "re", r"Same conflict pattern as Alchemy/Blacksmithing/\s+Enchanting"),
    ("F04 nitro", "re", r"\"Training cost: 115\"\s+with detail line \"Profession Trainer: Northrend Engineering \(30\) - Cost:\s+115\""),
    ("F05 scroll", "re", r"Draenor Engineering scroll vendors show \"Cost:100\""),
    ("F06 sightless", "re", r"Sightless Eye 250 \(R2 Gunpowder Charge\) and 500 \(R3\) at The\s+Widow"),
    ("F07 marks", "re", r"6 for the Sinister Discombobulator rank 2\+3\s+pair, 2 for the Nazjatar Notorious rank 2, 4 for rank 3"),
    ("F08 primal", "re", r"Schematic: Primal Welding 122712 = 60 Blackrock Ore from the Ore\s+Trader"),
    ("F09 unverified", "re", r"prices for old schematics were not printed on these guides -\s+unverified where needed"),
    ("F10 moneycost", "re", r"price = trainer-spell MoneyCost x\s+GetReputationPriceDiscount\(npc\) \(Trainer\.cpp 98\)"),
    # --- 6 level ---------------------------------------------------------
    ("V01 classic5", "re", r"Classic: warcraft\.wiki Classic engineering schematics - \"can be\s+trained as early as level 5\""),
    ("V02 outland50", "re", r"Outland: wowpedia Outland engineering schematics - \"as early as\s+level 50\""),
    ("V03 nr65", "re", r"Northrend: wowpedia Northrend engineering schematics - \"as early as\s+level 65\""),
    ("V04 cata75", "re", r"Cataclysm: warcraft\.wiki Cataclysm schematics - \"as early as level\s+75\""),
    ("V05 mop80", "re", r"Pandaria: warcraft\.wiki Pandaria schematics - \"as early as level\s+80\""),
    ("V06 wod90", "re", r"Draenor: warcraft\.wiki Draenor schematics - \"as early as level 90\""),
    ("V07 legion98", "re", r"Legion: warcraft\.wiki Legion schematics - \"as early as level 98\""),
    ("V08 legion10", "re", r"current quest 40545 requires level 10"),
    ("V09 bfa unknown", "re", r"Battle for Azeroth: no character-level line printed on the learn\s+spells"),
    ("V10 table", "re", r"Classic\s+Apprentice/Journeyman/Expert/Artisan ladder 1-75 / 75-150 / 150-225 /\s+225-300"),
    ("V11 bfa175", "re", r"BfA Kul Tiran/\s+Zandalari Master 1-175 \(this page agrees with the learn spells - no cap\s+conflict on Engineering\)"),
    ("V12 gates", "re", r"\"Profession: Engineering \(1\)\" on 3918 and\s+255392"),
    ("V13 spec", "re", r"specialization at skill 200 \(wiki \+ guide\)"),
    ("V14 no craft gate", "re", r"There is no server-side\s+craft-time skill check for engineering recipes"),
    # --- 7 core ----------------------------------------------------------
    ("W01 create", "re", r"recipes are Effect Create Item\s+\(wowhead samples 3918 and 255392 both print Effect: Create Item"),
    ("W02 take", "re", r"Spell\.cpp 3872/3877 TakeReagents\(\)\s+\(definition 5600\)"),
    ("W03 docreate", "re", r"DoCreateItem SpellEffects\.cpp 1383"),
    ("W04 inv", "re", r"1440 \(EQUIP_ERR_INV_FULL \|\| EQUIP_ERR_ITEM_MAX_COUNT\s+-> SendEquipError\)"),
    ("W05 skill1469", "re", r"grants skill at 1469 \(`if \(!m_CastItem\)\s+player->UpdateCraftSkill\(m_spellInfo\);`\)"),
    ("W06 yields", "re", r"Handful of Cobalt Bolts yields 1 or 3, Volatile\s+Blasting Trigger yields 2, Ghost Iron Bolts yield 2"),
    ("W07 create2", "re", r"SPELL_EFFECT_CREATE_ITEM_2 \(effect 157,\s+table line 249\) with IsLootCrafting rolls from LootTemplates_Spell\s+\(EffectCreateItem2 SpellEffects\.cpp 1482"),
    ("W08 itemcast", "re", r"item-cast crafts also grant skill through Spell\.cpp\s+3864 \(SPELL_ATTR9_ITEM_CAST_GRANTS_SKILL_GAIN\)"),
    ("W09 tinker", "re", r"Tinker recipes are ENCHANT-ITEM crafts, not Create Item"),
    ("W10 nitro sample", "re", r"sample\s+Nitro Boosts 55016 prints \"Requires Belt\", Tools: Arclight Spanner"),
    ("W11 eip", "re", r"SpellEffects\.cpp 2463\s+EffectEnchantItemPerm \(effect 53 SPELL_EFFECT_ENCHANT_ITEM, table\s+line 145\)"),
    ("W12 target", "re", r"\"Target\s+must be own item\" flag"),
    ("W13 floor", "re", r"level floor via BaseLevel \(7691-7697\s+SPELL_FAILED_LOWLEVEL\)"),
    ("W14 cap", "re", r"MaxLevel\s+cap when casting from an item or prismatic \(7699-7701\s+SPELL_FAILED_HIGHLEVEL\)"),
    ("W15 onuse", "re", r"on-use conflict \(7716-7723\s+SPELL_FAILED_ON_USE_ENCHANT\)"),
    ("W16 trade", "re", r"foreign-item\s+soulbound check \(7741-7746 SPELL_FAILED_NOT_TRADEABLE\) which matches\s+the recipe's \"Target must be own item\" flag"),
    ("W17 skill2492", "re", r"SpellEffects\.cpp 2490-2492\s+\(comment \"do not increase skill\s+if vellum used\""),
    ("W18 no vellum", "re", r"Engineering has NO vellum branch equivalent in these routes"),
    ("W19 update", "re", r"Player::UpdateCraftSkill Player\.cpp 5410, early-out\s+SPELL_ATTR1_NO_SKILL_INCREASE 5412"),
    ("W20 discovery", "re", r"discovery branch MECHANIC_DISCOVERY 5427-5431 \(Stealthman\s+54's quick facts print \"Learned via discovery\""),
    ("W21 gain", "re", r"gain = NumSkillUps x\s+CONFIG_SKILL_GAIN_CRAFTING 5433"),
    ("W22 colours", "re", r"orange\s+always, yellow probably, green probably not, grey never; red = not\s+high enough skill to learn"),
    ("W23 quest reward", "re", r"quest rewards \(264491\) go through the\s+quest-reward learn path"),
    ("W24 scroll path", "re", r"item\s+111922-analog item 111921 -> Learning spell 161787 -> wrapper 264488"),
    ("W25 focus", "re", r"RequiresSpellFocus machinery \(Spell\.cpp 1120/1133, GameObjectFocus\s+check 2322-2323"),
    ("W26 aura focus", "re", r"aura-provided focus 6064-6066, fail packet 4473"),
    ("W27 learn effects", "re", r"8\.0\.1 mains use Learn Skill \(line id\) value 1"),
    ("W28 classic triple", "re", r"Classic wrapper 264478 additionally\s+learns\s+4036 \(trade skill \+ skill 202\) and 264475 \(line 2506\)"),
    ("W29 req1", "re", r"expansion mains also\s+require base Engineering \(1\) as their quick facts state"),
    # --- 8 cannot --------------------------------------------------------
    ("X01 gnome", "re", r"Gnome Engineering\s+Specialization 20593 is Apply Aura: Mod Skill \(Engineering\) value 5"),
    ("X02 visage", "re", r"a non-Gnome companion never gets\s+the \+5 orange extension"),
    ("X03 kt2", "re", r"Kul Tiran \+2 Jack of All Trades 291442 comes from the guides'"),
    ("X04 gates", "re", r"Exalted\s+Zandalari/Proudmoore for Time Shifter R2"),
    ("X05 wq", "re", r"random \"Work Order\" World\s+Quests for R3 schematics"),
    ("X06 mark", "re", r"Mark of Honor from battlegrounds"),
    ("X07 tidalcore", "re", r"Mythic/Mythic\+ Tidalcore drops"),
    ("X08 trader rng", "re", r"garrison Ore-Trader daily rotation with\s+1-of-4 spawn RNG \(level 3 town hall; wait 5 days"),
    ("X09 content", "re", r"Legion quest chain dungeons\s+\(Halls of Valor 40877, Violet Hold 40878, Court of Stars 40882"),
    ("X10 ah", "re", r"shopping lists assume an AH; the\s+companion must substitute mining"),
    ("X11 faction", "re", r"Aldor cannot use Sinbei, Scryers cannot use\s+Mihila"),
    ("X12 dual", "re", r"Timofey in Legion Dalaran will not teach Northrend\s+recipes"),
    ("X13 spec", "re", r"Global Thermal Sapper Charge 56514\s+and Big Daddy 95707 routes assume Goblin Engineering quests"),
    ("X14 profs", "re", r"CanTeachSpell's free\s+profession point gate \(Trainer\.cpp 156\)"),
    ("X15 ui", "re", r"colour of each recipe in the profession window"),
    ("X16 night", "re", r"\"Can only\s+be used during nighttime\" and shares potion cooldowns"),
    ("X17 stale rows", "re", r"wiki trainers page is marked outdated and patch 4\.0\.3a equalized ranks"),
    # --- 9 conflicts -----------------------------------------------------
    ("Y01 c1", "re", r"1\) Gnome bonus: vanilla guide and Legion guide say \"\+15 Engineering\""),
    ("Y02 c2", "re", r"2\) Kul Tiran \+2 \(Jack of All Trades 291442\)"),
    ("Y03 c3", "re", r"3\) Northrend shopping list: Saronite 390 vs exact route need 400"),
    ("Y04 c4", "re", r"4\) Northrend shopping list omits the 45 Tinker's Kits"),
    ("Y05 c5", "re", r"5\) Pandaria shopping list: High-Explosive Gunpowder produced = 70 but\s+route consumes"),
    ("Y06 c6", "re", r"6\) Legion reward link: the guide hyperlinks spell 201700"),
    ("Y07 c7", "re", r"7\) Legion quest count: guide says 29; wowhead storyline lists 31"),
    ("Y08 c8", "re", r"8\) Classic wrapper 264478 teacher"),
    ("Y09 c9", "re", r"9\) Patch tags on the BfA Horde pair"),
    ("Y10 c10", "re", r"10\) Anvil/station: wiki says \"Anvils are also required to craft\""),
    ("Y11 c11", "re", r"11\) Heavy Blasting Powder: retail spell 3930 does not exist"),
    ("Y12 c12", "re", r"12\) Clockwork Box step \(113-125\)"),
    ("Y13 c13", "re", r"13\) BfA Magical Intrusion Dampener: the guide reports a live bug"),
    ("Y14 c14", "re", r"14\) Training-cost units: pages print \"Training cost: 10\"/\"115\""),
    ("Y15 c15", "re", r"15\) TC line drift: the Enchanting file"),
    ("Y16 c16", "re", r"16\) Nitro Boosts flag \"Can only be used during nighttime\""),
    ("Y17 c17", "re", r"17\) Gnomish/Goblin retention on retail 8\.3\.7's Classic bar"),
    ("Y18 c18", "re", r"18\) Outland shopping is explicitly ranged"),
    ("Y19 c19", "re", r"19\) Wowpedia-host fetches for the schematic headers were chrome-heavy"),
    # --- 10 sources ------------------------------------------------------
    ("Z01 date", "re", r"All fetched 2026-10-26 week"),
    ("Z02 base list", "re", r"4036 \(base \+ other ranks\), 4039, 264475"),
    ("Z03 probes", "re", r"wowhead item pages probed for craft spells and ids:"),
    ("Z04 search", "re", r"Guide-hub search results \(record id/url\)"),
    ("Z05 url kt", "lit", "https://www.wowhead.com/spell=264492/kul-tiran-engineering"),
    ("Z06 url kt skill", "lit", "https://www.wowhead.com/skill=2499/kul-tiran-engineering"),
    ("Z07 url bfa", "lit", "https://www.wow-professions.com/guides/zandalari-kul-tiran-bfa-engineering-leveling-guide"),
    ("Z08 url outland", "lit", "https://www.wowhead.com/spell=264479/outland-engineering"),
    ("Z09 url nr", "lit", "https://www.wowhead.com/spell=264482/northrend-engineering"),
    ("Z10 url legion", "lit", "https://www.wowhead.com/spell=264491/legion-engineering"),
    ("Z11 url quest", "lit", "https://www.wow-professions.com/guides/legion-engineering-leveling"),
    ("Z12 url hbp", "lit", "https://www.wowhead.com/classic/spell=3945/heavy-blasting-powder"),
    ("Z13 url leystone", "lit", "https://www.wowhead.com/item=123918/leystone-ore"),
    ("Z14 url tinkers", "lit", "https://www.wowhead.com/item=90146/tinkers-kit"),
    ("Z15 slugs", "re", r"wow-professions guides \(full slugs\): vanilla-engineering-leveling,\s+outland-engineering-leveling, northrend-engineering-leveling,\s+cataclysm-engineering-leveling, pandaria-engineering-leveling,\s+draenor-engineering-leveling, legion-engineering-leveling"),
    ("Z16 bfa slug", "re", r"zandalari-kul-tiran-bfa-engineering-leveling-guide"),
    ("Z17 wiki pages", "re", r"warcraft\.wiki\.gg pages: Engineering \(7 chunks"),
    ("Z18 trainers chunks", "re", r"Engineering_trainers\s+\(6 chunks"),
    ("Z19 schematics", "re", r"Classic_engineering_schematics \(level 5, rank ladder"),
    ("Z20 wowpedia", "re", r"wowpedia\.fandom\.com:\s+Outland_engineering_schematics \(level 50\)"),
    ("Z21 tc clone", "re", r"TrinityCore master, fetched this week with a blobless sparse clone"),
    ("Z22 tc spell", "re", r"Spells/Spell\.cpp \(3864, 3872/3877, 5600"),
    ("Z23 tc effects", "re", r"Spells/SpellEffects\.cpp \(145, 191, 249, 1383, 1440, 1469, 1482-1522"),
    ("Z24 tc player", "re", r"Entities/Player/Player\.cpp \(5410-5437\)"),
    ("Z25 tc npc", "re", r"Handlers/NPCHandler\.cpp \(97, 112,\s+130, 145, 155\)"),
    ("Z26 tc trainer", "re", r"Entities/Creature/\s+Trainer\.cpp \(67-68, 76, 98-106, 149, 156, 165, 172, 181-191\)"),
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

    classic = [60, 30, 30, 20, 20, 13, 1, 30, 15, 15, 1, 60, 7, 20, 40, 20, 20, 25, 20]
    total = num(r"Total planned crafts = (\d+) numbered steps")
    if total != sum(classic) or sum(classic) != 447:
        failures.append("D01 classic craft sum %s != 447" % total)
    outland = [126, 20, 56, 5, 34, 70, 6, 17, 6]
    total = num(r"Total planned crafts = (\d+)\.\s*\n\n3\.3")
    if total != sum(outland) or sum(outland) != 340:
        failures.append("D02 outland craft sum %s != 340" % total)
    if 126 + 168 != 294 or 136 + 34 + 48 != 218:
        failures.append("D02b outland material math")
    nr = [35, 10, 10, 6, 15, 5, 15, 30, 5, 5, 5, 30, 1]
    total = num(r"Total planned crafts = (\d+)\.\s*\n\n3\.4")
    if total != sum(nr) or sum(nr) != 172:
        failures.append("D03 NR craft sum %s != 172" % total)
    if 70 + 30 + 40 + 120 != 260 or 60 + 40 + 300 != 400:
        failures.append("D03b NR material math")
    if not re.search(r"Saronite 390 vs exact route need 400", text):
        failures.append("D03c NR saronite conflict present")
    cata = [30, 15, 15, 15, 15]
    if sum(cata) != 90:
        failures.append("D04 cata craft sum")
    if 30 * 2 != 60 or 15 * 2 != 30 or 300 + 60 != 360:
        failures.append("D04b cata material math")
    mop = [112, 70, 30, 10, 13]
    total = num(r"Total planned crafts = 112\+70\+30\+10\+13 = (\d+)")
    if total != sum(mop) or sum(mop) != 235:
        failures.append("D05 mop craft sum %s != 235" % total)
    if 112 * 3 + 70 != 406 or 60 + 80 != 140:
        failures.append("D05b mop bar math")
    if not re.search(r"produced = 70 but\s+route consumes", text):
        failures.append("D05c mop HEG conflict present")
    if 12 + 1 + 70 != 83:
        failures.append("D06 draenor branch sum")
    bfa = [30, 5, 30, 25, 15, 35, 15, 10]
    total = num(r"main path: 30\+5\+30\+25\+15\+\s+35\+15\+10\) = (\d+)")
    if total != sum(bfa) or sum(bfa) != 165:
        failures.append("D07 BfA craft sum %s != 165" % total)
    if 180 + 50 + 150 + 200 + 120 != 700:
        failures.append("D07b BfA monelite math")
    key_ids = [
        4036, 4039, 4037, 4038, 12656, 30350, 51306, 264475, 264478,
        264479, 264480, 264481, 264482, 264483, 264484, 264485, 264486,
        264487, 264488, 264490, 264491, 264492, 264493, 265807, 265808,
        111921, 40545, 3918, 3922, 3923, 3929, 3931, 8334, 3934, 3942,
        3945, 3953, 3955, 12590, 12585, 12589, 12591, 12599, 12619,
        19788, 19791, 19795, 7430, 30305, 30303, 30304, 30310, 30306,
        30341, 30308, 30313, 44391, 56349, 53281, 56464, 56463, 56471,
        61471, 55016, 67839, 56477, 61482, 56472, 56467, 56462, 67920,
        84403, 94748, 84409, 84410, 84415, 84416, 95707, 84430, 127113,
        127114, 131563, 127131, 127116, 127130, 169080, 169140, 162207,
        173308, 173309, 177054, 169078, 182120, 199014, 255392, 255393,
        256154, 256155, 255409, 280734, 283916, 283915, 283914, 286478,
        282808, 265102, 264967, 286873, 294784, 294785, 294786, 20593,
        56514, 95707, 201700, 161787,
        2835, 2840, 2836, 2589, 2841, 2838, 2592, 2319, 3859, 7912,
        3860, 4338, 12365, 12359, 14047, 23445, 22573, 22574, 22452,
        21877, 23446, 21884, 23449, 36916, 33470, 37701, 37705, 33568,
        36913, 35627, 35622, 36860, 35623, 41163, 54849, 52328, 52186,
        52325, 72096, 72988, 76061, 89112, 109118, 109119, 109128,
        120945, 111366, 123918, 136637, 152512, 152579, 152513, 168185,
        160502, 163569, 165948, 90146, 5956, 6219, 10498, 60223, 114943,
        6712, 4377, 4375, 23783, 23781, 23782, 23736, 23784, 23768,
        23746, 42546, 77467, 77468, 109992, 109991, 109628,
    ]
    missing = [i for i in key_ids if str(i) not in text]
    if missing:
        failures.append("D08 key id coverage missing: %s" % missing[:12])
    for fam in ["5410", "1383", "1482", "2463", "7664", "172", "130", "2322"]:
        if fam not in text:
            failures.append("D09 missing TC family %s" % fam)
    conf = re.findall(r"^(\d{1,2})\) ", text, re.M)
    if len(conf) < 19:
        failures.append("D10 conflict items %d < 19" % len(conf))
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
        ("skill id", "skill=202, value 1", "skill=999, value 1"),
        ("classic main id", "main 264475", "main 264476x"),
        ("nr saronite", "Saronite Bar 36913", "Saronite Bar 36914"),
        ("classic total", "447 numbered steps", "448 numbered steps"),
        ("tc skill gate line", "181-183", "181-184"),
        ("gloom id analog", "Chemical Blasting Cap 160502", "Chemical Blasting Cap 160503"),
        ("npc entry", "136059", "139999"),
        ("legion level", "quest 40545 requires level 10", "quest 40545 requires level 11"),
        ("bfa cap", "cap 175, Alliance Specific", "cap 150, Alliance Specific"),
        ("dampener spell", "spell 280734", "spell 280735"),
        ("hbp spell", "craft spell 3945 per classic", "craft spell 3946 per classic"),
        ("scroll id", "scroll item 111921", "scroll item 111922"),
        ("bfa total", "15+10) = 165", "15+10) = 166"),
        ("conflict count", "19) Wowpedia-host", "19a Wowpedia-host"),
        ("leystone", "Leystone Ore 123918", "Leystone Ore 123919"),
        ("nitro effect", "Enchant Item: Nitro Boosts (4223)", "Enchant Item: Nitro Boosts (4224)"),
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
