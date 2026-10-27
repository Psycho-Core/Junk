#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit for Companion_Professions step 2 (PART 14, STEP 124): Gather_Mining.txt.

Checks (statics):
  * structure: ten sections, the prompt's deliverable name, RESEARCH_MASTER
    STEP 124 lines, plain-text hygiene
  * skill lines 186/2572..2565 with caps and gather spells, learn spells
    265852/265854, trainers, technique example, the 150-vs-175 cap caveat
  * gather spell family: 2575 facts, the eight 2658xx expansion spells with
    potentials and patches, legacy ladder, Find Minerals 2580, quest spell
    291257, NPC variant 274129
  * cast time 3.2 s (2018-09-28 archive capture + current pages), glove
    enchants 153431/159466, stirrups 253112, mounted-flag history, pick
    disagreement
  * full ore threshold table (29 rows with item ids) from party_features
    4.5, modern ore item ids, Ghost Iron gap, mine-at-skill-1 rule
  * mob mining: 5 x level, no skill-ups, pick required, 491-critter filter
    samples, "Mined from NPC (622)"
  * skill-up rules incl. MiningSteps decay and smelting
  * respawn machinery + wiki rare-substitution pairs and seams
  * gameobject entries per expansion, complete BfA set with every per-zone
    id
  * best zones per skill range through BfA 1-175
  * ten "N. Cannot ..." items
  * forbidden leftovers: herbalism content, wrong cast times

Derived: item ids present in BOTH the deliverable and BfA_8.3.7_party
_features.txt, spell-family completeness, trainer-id completeness, ASCII
hygiene, BfA-cap consistency, all eight 4.x expansion headings.

Mutation self-test (--self-test): every target is falsified at ALL of its
occurrences (double-occurrence payloads from step 1's audit taught us that),
regexes are blinded, derived checks are falsified; baseline must PASS first.
"""
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))


def load(rel):
    return io.open(os.path.join(BASE, rel), encoding="utf-8").read()


FILES = {
    "doc": "Gather_Mining.txt",
    "p2": "02_Mining.txt",
    "rm": os.path.join("..", "RESEARCH_MASTER.txt"),
    "pf": os.path.join("..", "BfA_8.3.7_party_features.txt"),
}

CHECKS = [
    # --- structure ---
    ("S01", "doc", "has", "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - MINING GATHERING FOR A SERVER-SIDE COMPANION"),
    ("S02", "doc", "has", "1. THE SKILL LINES AND HOW A COMPANION LEARNS THEM"),
    ("S03", "doc", "has", "2. THE SPELL IDS THAT GATHER"),
    ("S04", "doc", "has", "3. HOW LONG A GATHER TAKES"),
    ("S05", "doc", "has", "4. SKILL NEEDED PER NODE (AND PER CREATURE)"),
    ("S06", "doc", "has", "5. HOW THE SKILL RISES (SERVER RULES)"),
    ("S07", "doc", "has", "6. HOW NODES RESPAWN"),
    ("S08", "doc", "has", "7. NODE GAMEOBJECT ENTRIES BY ZONE, PER EXPANSION"),
    ("S09", "doc", "has", "8. BEST ZONES FOR EACH SKILL RANGE (THROUGH THE BFA RANGE)"),
    ("S10", "doc", "has", "9. WHAT A SERVER-SIDE CHARACTER (NO CLIENT) CANNOT DO"),
    ("S11", "doc", "has", "10. SOURCES AND UNVERIFIED INDEX"),
    ("S12", "doc", "absent", "\t"),
    ("S13", "doc", "regex", (r"^\s{1,2}\d+\. Cannot ", 10)),
    ("S14", "doc", "has", "Unverified, collected:"),
    ("S15", "doc", "regex", (r"unverified", 20)),
    ("S16", "p2", "has", "WHAT TO DELIVER - ONE TEXT FILE, Gather_Mining.txt"),
    ("S17", "p2", "has", "Do only this step"),
    ("S18", "rm", "has", "--- STEP 124"),
    ("S19", "rm", "has", "Deliver ONE text file named: Gather_Mining.txt"),
    ("S20", "rm", "has", "PROFESSIONS FOR THE COMPANION BOTS (15 steps)"),

    # --- skill lines / learning ---
    ("L01", "doc", "regex", (r"2572\s+Classic Mining\s+300\s+265837 \(8\.0\.1\)", 1)),
    ("L02", "doc", "regex", (r"2571\s+Outland Mining\s+75\s+265839 \(8\.0\.1\)", 1)),
    ("L03", "doc", "regex", (r"2570\s+Northrend Mining\s+75\s+265841 \(8\.1\.0\)", 1)),
    ("L04", "doc", "regex", (r"2569\s+Cataclysm Mining\s+75\s+265843 \(8\.1\.0\)", 1)),
    ("L05", "doc", "regex", (r"2568\s+Pandaria Mining\s+75\s+265845 \(8\.1\.0\)", 1)),
    ("L06", "doc", "regex", (r"2567\s+Draenor Mining\s+100\s+265847 \(8\.0\.1\)", 1)),
    ("L07", "doc", "regex", (r"2566\s+Legion Mining\s+100\s+265849 \(8\.1\.0\)", 1)),
    ("L08", "doc", "has", "2565     Kul Tiran / Zandalari Mining    175   265851 Alliance (8.0.1)"),
    ("L09", "doc", "has", "265853 Horde (8.1.0)"),
    ("L10", "doc", "has", "2575 (the classic spell, learn value 1)"),
    ("L11", "doc", "has", "Kul Tiran Mining 265852 (Alliance) and Zandalari Mining"),
    ("L12", "doc", "has", "265854 (Horde)"),
    ("L13", "doc", "has", "Myra Cabot creature 136091"),
    ("L14", "doc", "has", "Secott the Goldsmith creature 122694"),
    ("L15", "doc", "has", "Instructor Ulooaka 154257 (Alliance)"),
    ("L16", "doc", "has", "Rolm 154408"),
    ("L17", "doc", "has", "item 111349"),
    ("L18", "doc", "has", "Hurnak Grimmord 18779"),
    ("L19", "doc", "has", "Krugosh 18747"),
    ("L20", "doc", "has", "Hanlir 33640 or Fono 33682"),
    ("L21", "doc", "has", "Jedidiah Handers 28698"),
    ("L22", "doc", "has", "Brunna Ironaxe 26976"),
    ("L23", "doc", "has", "Jonathan Lewis 26962"),
    ("L24", "doc", "has", "Rockseeker Guo 67024"),
    ("L25", "doc", "regex", (r"Stonebreaker\s+Ruian 66979", 1)),
    ("L26", "doc", "has", "Smeltmaster Ashpaw 65092"),
    ("L27", "doc", "has", "Krunn 3175"),
    ("L28", "doc", "has", "Gelman Stonehand 5513"),
    ("L29", "doc", "has", "Mining Technique: Osmenite"),
    ("L30", "doc", "has", "spell 299543"),
    ("L31", "doc", "regex", (r"potential 175|potential mining skill of 175", 2)),
    ("L32", "doc", "has", "unverified between 150 and 175"),
    ("L33", "doc", "absent", "265831"),
    ("L34", "doc", "absent", "2549"),

    # --- gather spells ---
    ("P01", "doc", "has", "2575   Mining - 5 yd range (Interact), 3.2 sec cast, GCD 0, no cost."),
    ("P02", "doc", "has", "Effect 1 Open Object (Mining) value 1275"),
    ("P03", "doc", "has", "Learn Skill Mining 186 value 1"),
    ("P04", "doc", "has", "web.archive capture of 2018-09-28 (8.0.1 live)"),
    ("P05", "doc", "has", "265837 Classic (2572), potential 300, 8.0.1"),
    ("P06", "doc", "has", "265839 Outland (2571), potential 75, 8.0.1"),
    ("P07", "doc", "has", "265841 Northrend (2570), potential 75, 8.1.0"),
    ("P08", "doc", "has", "265843 Cataclysm (2569), potential 75, 8.1.0"),
    ("P09", "doc", "has", "265845 Pandaria (2568), potential 75, 8.1.0"),
    ("P10", "doc", "has", "265847 Draenor (2567), potential 100, 8.0.1"),
    ("P11", "doc", "has", "265849 Legion (2566), potential 100, 8.1.0"),
    ("P12", "doc", "has", "265851 Kul Tiran (2565), potential 175, 8.0.1"),
    ("P13", "doc", "has", "265853 Horde side of 2565, potential 175, 8.1.0"),
    ("P14", "doc", "has", "Outland Mining 265840, Northrend"),
    ("P15", "doc", "has", "2576 (50), 3564 (125),"),
    ("P16", "doc", "has", "29354 (275), 50310 (350), 74517 (425), 102161 (500)"),
    ("P17", "doc", "has", "base variants 158754 and 195122"),
    ("P18", "doc", "has", "Find Minerals tracking: spell 2580"),
    ("P19", "doc", "has", "309835 and 366260"),
    ("P20", "doc", "has", "Brinestone Pickaxe item 167012"),
    ("P21", "doc", "has", "quest 56883"),
    ("P22", "doc", "has", "Spell 274129 \"Mining\""),
    ("P23", "doc", "has", "Open Object value 100"),
    ("P24", "doc", "absent", "Find Herbs"),
    ("P25", "doc", "absent", "Herb Gathering"),
    ("P26", "doc", "absent", "Open Object value 1274"),

    # --- time / items ---
    ("T01", "doc", "has", "Base cast time: 3.2 seconds."),
    ("T02", "doc", "has", "dated 2018-09-28 (live 8.0.1 era) says \"3.2 sec cast\""),
    ("T03", "doc", "regex", (r"3\.2 sec", 4)),
    ("T04", "doc", "has", "Kul Tiran Mining item 153431"),
    ("T05", "doc", "has", "Gloves - Zandalari Mining item 159466"),
    ("T06", "doc", "has", "Monel-Hardened Stirrups spell 253112"),
    ("T07", "doc", "has", "Hoofplates spell 253110"),
    ("T08", "doc", "regex", (r"Coarse Leather\s+Barding item 154166", 1)),
    ("T09", "doc", "has", "shows NO \"Can be used while mounted\" flag"),
    ("T10", "doc", "has", "baseline mounted mining on 8.3.7 is"),
    ("T11", "doc", "has", "Requires a Mining Pick."),
    ("T12", "doc", "has", "265851/265853 drop that sentence"),
    ("T13", "doc", "absent", "cast time: 2 seconds"),
    ("T14", "doc", "absent", "down from 1.5 seconds"),

    # --- ore threshold table ---
    ("B01", "doc", "regex", (r"Copper Vein\s+Classic\s+1\s+25\s+50\s+100\s+2770", 1)),
    ("B02", "doc", "regex", (r"Tin Vein\s+Classic\s+50\s+75\s+100\s+150\s+2771", 1)),
    ("B03", "doc", "regex", (r"Silver Vein\s+Classic\s+65\s+85\s+110\s+160\s+2775", 1)),
    ("B04", "doc", "regex", (r"Iron Vein\s+Classic\s+100\s+125\s+150\s+200\s+2772", 1)),
    ("B05", "doc", "regex", (r"Gold Vein\s+Classic\s+115\s+130\s+165\s+215\s+2776", 1)),
    ("B06", "doc", "regex", (r"Mithril Deposit\s+Classic\s+150\s+175\s+200\s+250\s+3858", 1)),
    ("B07", "doc", "regex", (r"Truesilver Deposit\s+Classic\s+165\s+165\s+\?\s+\?\s+7911", 1)),
    ("B08", "doc", "regex", (r"Dark Iron Vein\s+Classic\s+165\s+165\s+\?\s+\?\s+11370", 1)),
    ("B09", "doc", "regex", (r"Small Thorium Vein\s+Classic\s+200\s+225\s+250\s+300\s+10620", 1)),
    ("B10", "doc", "regex", (r"Rich Thorium Vein\s+Classic\s+215\s+240\s+265\s+315\s+10620", 1)),
    ("B11", "doc", "regex", (r"Fel Iron Vein\s+TBC\s+275\s+325\s+350\s+400\s+23424", 1)),
    ("B12", "doc", "regex", (r"Adamantite Vein\s+TBC\s+325\s+350\s+375\s+425\s+23425", 1)),
    ("B13", "doc", "regex", (r"Rich Adamantite Vein\s+TBC\s+350\s+375\s+400\s+450\s+23425", 1)),
    ("B14", "doc", "regex", (r"Nethercite Deposit\s+TBC\s+350\s+375\s+390\s+400\s+32464", 1)),
    ("B15", "doc", "regex", (r"Cobalt Deposit\s+WotLK\s+350\s+375\s+400\s+425\s+36909", 1)),
    ("B16", "doc", "regex", (r"Khorium Vein\s+TBC\s+375\s+400\s+425\s+-\s+23426", 1)),
    ("B17", "doc", "regex", (r"Ancient Gem Vein\s+TBC\s+375\s+-\s+-\s+-\s+-", 1)),
    ("B18", "doc", "regex", (r"Rich Cobalt Deposit\s+WotLK\s+375\s+400\s+425\s+450\s+36909", 1)),
    ("B19", "doc", "regex", (r"Saronite Deposit\s+WotLK\s+400\s+425\s+450\s+500\s+36912", 1)),
    ("B20", "doc", "regex", (r"Rich Saronite Deposit\s+WotLK\s+425\s+450\s+500\s+525\s+36912", 1)),
    ("B21", "doc", "regex", (r"Obsidium Deposit\s+Cata\s+425\s+450\s+475\s+-\s+53038", 1)),
    ("B22", "doc", "regex", (r"Rich Obsidium Deposit\s+Cata\s+450\s+475\s+500\s+-\s+53038", 1)),
    ("B23", "doc", "regex", (r"Pure Saronite Deposit\s+WotLK\s+450\s+-\s+-\s+-\s+36912", 1)),
    ("B24", "doc", "regex", (r"Titanium Deposit\s+WotLK\s+450\s+-\s+-\s+-\s+36910", 1)),
    ("B25", "doc", "regex", (r"Elementium Vein\s+Cata\s+475\s+500\s+525\s+-\s+52185", 1)),
    ("B26", "doc", "regex", (r"Rich Elementium Vein\s+Cata\s+500\s+525\s+-\s+-\s+52185", 1)),
    ("B27", "doc", "regex", (r"Pyrite Deposit\s+Cata\s+525\s+-\s+-\s+-\s+52183", 1)),
    ("B28", "doc", "regex", (r"Rich Pyrite Deposit\s+Cata\s+525\s+-\s+-\s+-\s+52183", 1)),
    ("B29", "doc", "regex", (r"Kyparite Deposit\s+MoP\s+550\s+-\s+-\s+-\s+72093", 1)),
    ("B30", "doc", "regex", (r"Rich Kyparite Deposit\s+MoP\s+575\s+-\s+-\s+-\s+72093", 1)),
    ("B31", "doc", "regex", (r"Trillium Vein\s+MoP\s+600\s+-\s+-\s+-\s+72094", 1)),
    ("B32", "doc", "regex", (r"Rich Trillium Vein\s+MoP\s+600\s+-\s+-\s+-\s+72103", 1)),
    ("B33", "doc", "has", "Blackrock Ore 109118, True Iron Ore 109119"),
    ("B34", "doc", "has", "Leystone Ore 123918, Felslate 123919, Empyrium 151564"),
    ("B35", "doc", "has", "Monelite Ore 152512, Storm Silver Ore 152579,"),
    ("B36", "doc", "has", "Platinum Ore 152513, Osmenite Ore 168185"),
    ("B37", "doc", "has", "Ghost Iron Deposit"),
    ("B38", "doc", "regex", (r"Ghost Iron Deposit\s+\(the MoP opener ore the guides use\) has NO row", 1)),
    ("B39", "doc", "has", "every node can"),
    ("B40", "doc", "regex", (r"In 8\.3\.7\s+the red band never blocks", 1)),
    ("B41", "doc", "has", "You will get much fewer ores if you start"),
    ("B42", "doc", "has", "rank 1 of the expansion skill"),

    # --- creature side ---
    ("M01", "doc", "has", "5 x the creature's level"),
    ("M02", "doc", "has", "level 70"),
    ("M03", "doc", "has", "mining cannot be leveled in this fashion"),
    ("M04", "doc", "has", "A mining pick is"),
    ("M05", "doc", "has", "all level 60+"),
    ("M06", "doc", "has", "TBC mobs do not drop WotLK ore"),
    ("M07", "doc", "has", "returns 491 creatures"),
    ("M08", "doc", "has", "Morcrush 18690"),
    ("M09", "doc", "has", "Rockweed Shambler 150583 Nazjatar"),
    ("M10", "doc", "has", "\"Mined from NPC (622)\""),
    ("M11", "doc", "has", "against today's 954"),
    ("M12", "doc", "absent", "gives skill-ups"),

    # --- skill-up rules ---
    ("R01", "doc", "has", "SPELL_FAILED_LOW_CASTLEVEL"),
    ("R02", "doc", "regex", (r"effect\s+value \(\+1275\)", 1)),
    ("R03", "doc", "regex", (r"yellow = red \+ 30, green = yellow \+ 30,\s+grey = green \+ 30", 1)),
    ("R04", "doc", "has", "trivial-skill low/high fields"),
    ("R05", "doc", "has", "SkillChance.Orange = 100"),
    ("R06", "doc", "has", "SkillChance.Yellow = 75"),
    ("R07", "doc", "has", "SkillChance.Green = 25"),
    ("R08", "doc", "has", "SkillChance.Grey = 0"),
    ("R09", "doc", "has", "SkillGain.Gathering = 1 point per success"),
    ("R10", "doc", "has", "Mining DOES have chance decay"),
    ("R11", "doc", "has", "SkillChance.MiningSteps"),
    ("R12", "doc", "has", "halving it once per steps skill"),
    ("R13", "doc", "has", "SkillChance.MiningSteps = 0"),
    ("R14", "doc", "has", "Smelting also gives Mining skill points"),
    ("R15", "doc", "absent", "SkillChance.Orange = 50"),
    ("R16", "doc", "regex", (r"cannot\s+infer profession skill from gathered node count", 1)),
    ("R17", "doc", "has", "skill-up per character per node GUID until the node respawns"),
    ("R18", "doc", "absent", "SkillChance.Grey = 5"),
    ("R19", "doc", "absent", "SkillGain.Gathering = 2"),
    ("R20", "doc", "absent", "Herbalism has NO chance decay"),

    # --- respawn ---
    ("N01", "doc", "has", "GO_ACTIVATED (lootable)"),
    ("N02", "doc", "has", "GO_JUST_DEACTIVATED"),
    ("N03", "doc", "has", "m_respawnTime = now + delay"),
    ("N04", "doc", "has", "gameobject.spawntimesecs"),
    ("N05", "doc", "has", "default before load is 300 s"),
    ("N06", "doc", "has", "Respawn.MinCheckIntervalMS = 5000"),
    ("N07", "doc", "has", "Respawn.DynamicMode = 0"),
    ("N08", "doc", "has", "PoolMgr::UpdatePool"),
    ("N09", "doc", "has", "pool_members"),
    ("N10", "doc", "has", "pool_template"),
    ("N11", "doc", "has", "Tin to Silver, Iron to Gold, Mithril to Truesilver"),
    ("N12", "doc", "has", "Fel Iron and"),
    ("N13", "doc", "has", "Saronite to Titanium, Elementium to Pyrite, Ghost"),
    ("N14", "doc", "has", "Seams (introduced in"),
    ("N15", "doc", "has", "respawn as a"),
    ("N16", "doc", "has", "the respawn rate should be fast enough on the yellow path"),
    ("N17", "doc", "has", "no spawn rows, coordinates or respawn times"),
    ("N18", "doc", "absent", "Respawn.DynamicMode = 1"),
    ("N19", "doc", "absent", "spawntimesecs is always 60"),

    # --- gameobject entries ---
    ("G01", "doc", "has", "objects 1731 (Darkshore, Azshara, Tirisfal Glades, ...)"),
    ("G02", "doc", "has", "and 181248 (Ghostlands)"),
    ("G03", "doc", "has", "objects 1732 (Hillsbrad"),
    ("G04", "doc", "has", "and 181249 (Ghostlands)"),
    ("G05", "doc", "has", "Fel Iron Deposit object 181555"),
    ("G06", "doc", "has", "objects 189978 (Zul'Drak, Howling Fjord, Borean"),
    ("G07", "doc", "has", "Rich 189979"),
    ("G08", "doc", "has", "object 202738 (Deepholm, Twilight Highlands,"),
    ("G09", "doc", "has", "Rich Elementium Vein -> 202741"),
    ("G10", "doc", "has", "objects 209312 (Dread Wastes, Townlong Steppes,"),
    ("G11", "doc", "has", "Rich 209329"),
    ("G12", "doc", "has", "215414/215416"),
    ("G13", "doc", "has", "Blackrock Deposit 228563"),
    ("G14", "doc", "has", "Rich 228564"),
    ("G15", "doc", "has", "243313 / 243312"),
    ("G16", "doc", "has", "232542 /"),
    ("G17", "doc", "has", "237359 / 237360"),
    ("G18", "doc", "has", "Leystone Deposit 241726"),
    ("G19", "doc", "has", "Leystone Seam 253280"),
    ("G20", "doc", "has", "Rich 245324"),
    ("G21", "doc", "has", "Felslate Deposit 241743"),
    ("G22", "doc", "has", "Felslate Seam 255344"),
    ("G23", "doc", "has", "Rich Felslate 245325"),
    ("G24", "doc", "has", "Timewarped\" copies (5172xx)"),
    ("G25", "doc", "has", "Deposit 276616"),
    ("G26", "doc", "has", "Seam 276619"),
    ("G27", "doc", "has", "Rich 276621"),
    ("G28", "doc", "has", "Rough 297467 Tiragarde / 297621 Vol'dun"),
    ("G29", "doc", "has", "Hardened 297468 Stormsong / 297624 Zuldazar"),
    ("G30", "doc", "has", "Luminous 297466 Drustvar / 297618 Nazmir"),
    ("G31", "doc", "has", "Deposit 276617, Seam 276620, Rich 276622"),
    ("G32", "doc", "has", "Coarse 297470 Tiragarde / 297622 Vol'dun"),
    ("G33", "doc", "has", "Dense 297471 Stormsong / 297625 Zuldazar"),
    ("G34", "doc", "has", "Gleaming 297469 Drustvar / 297619 Nazmir"),
    ("G35", "doc", "has", "Deposit 276618, Rich 276623"),
    ("G36", "doc", "has", "Smooth 297473 Tiragarde / 297623 Vol'dun"),
    ("G37", "doc", "has", "Burnished 297472 Drustvar / 297620 Nazmir"),
    ("G38", "doc", "has", "Ductile 297474 Stormsong / 297626 Zuldazar"),
    ("G39", "doc", "has", "Deposit 325875, Seam 325874, Rich 325873"),
    ("G40", "doc", "has", "316430 (Boralus) / 316746"),
    ("G41", "doc", "absent", "object 1618"),
    ("G42", "doc", "absent", "326598"),
    ("G43", "doc", "absent", "276237"),

    # --- zones per skill range ---
    ("Z01", "doc", "has", "1-50 Copper - Durotar, Darkshore (Zidormi creature 141489"),
    ("Z02", "doc", "has", "50-100 Tin/Silver - Ashenvale"),
    ("Z03", "doc", "has", "100-150 Iron/Gold"),
    ("Z04", "doc", "has", "150-200 Mithril/Truesilver"),
    ("Z05", "doc", "has", "200-275"),
    ("Z06", "doc", "has", "Un'Goro Crater, Winterspring"),
    ("Z07", "doc", "has", "Small Thorium"),
    ("Z08", "doc", "has", "Darkmoon Faire quest"),
    ("Z09", "doc", "has", "29518 from Rinling creature 14841 gives +2 Mining"),
    ("Z10", "doc", "has", "1-75 Nagrand and Netherstorm"),
    ("Z11", "doc", "has", "Fel Iron stops ~40"),
    ("Z12", "doc", "has", "Icecrown or Sholazar Basin (Saronite), or"),
    ("Z13", "doc", "has", "Smelt Cobalt spell"),
    ("Z14", "doc", "has", "49252"),
    ("Z15", "doc", "has", "Smelt Saronite"),
    ("Z16", "doc", "has", "49258"),
    ("Z17", "doc", "has", "Twilight Highlands (best) or Uldum (Elementium)"),
    ("Z18", "doc", "has", "1-55 Valley of the Four Winds or Jade Forest (Ghost Iron)"),
    ("Z19", "doc", "has", "55-75 Townlong Steppes or Dread Wastes (Kyparite)"),
    ("Z20", "doc", "has", "any of Frostfire Ridge, Talador, Shadowmoon Valley"),
    ("Z21", "doc", "has", "1-85 Suramar - Rich nodes then Seam nodes"),
    ("Z22", "doc", "has", "Suramar 40.4, 29.4"),
    ("Z23", "doc", "has", "Uniting the Isles 43341"),
    ("Z24", "doc", "has", "Archmage Khadgar creature"),
    ("Z25", "doc", "has", "90417"),
    ("Z26", "doc", "has", "1-150 any BfA zone"),
    ("Z27", "doc", "has", "Nazmir, Drustvar,"),
    ("Z28", "doc", "has", "Zuldazar, Stormsong Valley (Monelite)"),
    ("Z29", "doc", "has", "150-175 Nazjatar Osmenite"),
    ("Z30", "doc", "has", "Highmountain Tauren get +15 Mining skill"),
    ("Z31", "doc", "absent", "1-175 in Elwynn"),
    ("Z32", "doc", "absent", "Val'sharah for 1-75"),

    # --- cannot-do ---
    ("W01", "doc", "has", "Cannot see nodes"),
    ("W02", "doc", "has", "Cannot use Find Minerals 2580 for anything"),
    ("W03", "doc", "has", "Cannot receive input-driven casts"),
    ("W04", "doc", "has", "Cannot watch the cast bar or the loot window"),
    ("W05", "doc", "has", "Cannot re-farm one vein for skill-ups"),
    ("W06", "doc", "has", "Cannot decide the pick question from the sources"),
    ("W07", "doc", "has", "Cannot mine corpses unless the fork implements it"),
    ("W08", "doc", "has", "Cannot trust mounted mining on 8.3.7"),
    ("W09", "doc", "has", "Cannot infer skill from node counts"),
    ("W10", "doc", "has", "Cannot exceed the cap"),
]

# ---------------------------------------------------------------- derived ---
ITEM_IDS_BOTH = ["2770", "2771", "23424", "36909", "52185", "72093",
                 "109118", "123918", "152512", "168185", "152579", "152513"]
SPELL_FAMILY = ["2575", "265837", "265839", "265841", "265843", "265845",
                "265847", "265849", "265851", "265853", "265852", "265854"]
TRAINER_IDS = ["136091", "122694", "154257", "154408", "18779", "18747",
               "33640", "33682", "28698", "26999", "26912", "26976", "26962",
               "67024", "66979", "65092", "141489", "90417"]


def run_checks(docs, verbose=False):
    passed, failed = [], []

    def mark(cid, ok):
        (passed if ok else failed).append(cid)

    for cid, fkey, kind, payload in CHECKS:
        text = docs[fkey]
        ok = False
        if kind == "has":
            ok = payload in text
        elif kind == "absent":
            ok = payload not in text
        elif kind == "count":
            pat, n = payload
            ok = text.count(pat) == n
        elif kind == "regex":
            pat, n = payload
            ok = len(re.findall(pat, text, re.M)) >= n
        mark(cid, ok)

    # X01 item ids in the deliverable AND in the repo's recorded tables
    ok = all(i in docs["doc"] and i in docs["pf"] for i in ITEM_IDS_BOTH)
    mark("X01-itemids-pf", ok)
    # X02 full spell family
    mark("X02-spell-family", all(s in docs["doc"] for s in SPELL_FAMILY))
    # X03 trainer/quest creature ids
    mark("X03-trainer-ids", all(t in docs["doc"] for t in TRAINER_IDS))
    # X04 plain-text hygiene
    ok = (all(ord(c) < 128 for c in docs["doc"])
          and "\t" not in docs["doc"]
          and max(len(l) for l in docs["doc"].splitlines()) <= 140)
    mark("X04-ascii-lines", ok)
    # X05 BfA cap consistency: spell rows say 175 and the caveat keeps 150/175
    ok = bool(re.search(r"2565\s+Kul Tiran / Zandalari Mining\s+175", docs["doc"])) \
        and "unverified between 150 and 175" in docs["doc"] \
        and "BfA 1-175" in docs["doc"]
    mark("X05-bfa-cap", ok)
    # X06 all eight section 4.x expansion headings (word-boundary safe)
    ok = all(re.search(re.escape(h) + r"(?![A-Za-z])", docs["doc"])
             for h in ["4.1 Vein and deposit thresholds",
                       "4.2 Modern ores the recorded threshold table does not tabulate (item ids)",
                       "4.3 Creature side (mob mining / ore skinning)"])
    mark("X06-section4-headings", ok)
    # X07 the two standing "?" rows stay marked
    ok = len(re.findall(r"Truesilver Deposit\s+Classic\s+165\s+165\s+\?", docs["doc"])) == 1 \
        and "green/grey values are the standing unverified pair" in docs["doc"]
    mark("X07-unknown-rows", ok)

    if verbose:
        for cid in passed:
            print("PASS", cid)
        for cid in failed:
            print("FAIL", cid)
    return passed, failed


def load_all():
    return dict((k, load(v)) for k, v in FILES.items())


def mutation_tests():
    base = load_all()
    base_pass, base_fail = run_checks(base)
    if base_fail:
        print("BASELINE FAIL:", ", ".join(base_fail))
        return False
    total = 0
    detected = 0
    misses = []

    def expect_fail(new_docs, label):
        nonlocal total, detected
        total += 1
        passed, failed = run_checks(new_docs)
        if failed:
            detected += 1
        else:
            misses.append(label + " -> still PASS")

    for cid, fkey, kind, payload in CHECKS:
        docs = dict(base)
        if kind == "has":
            old = payload
            probe = old[: min(40, len(old))]
            blinded = "XXMUTATEDXX " + old[len(probe):]
            new = docs[fkey].replace(old, blinded)   # ALL occurrences
            if new == docs[fkey]:
                new = docs[fkey] + "\nXXMUTATEDXX " + old
            docs[fkey] = new
            expect_fail(docs, cid + ":has:" + old[:30])
        elif kind == "absent":
            docs[fkey] = docs[fkey] + "\n" + payload
            expect_fail(docs, cid + ":absent:" + payload[:30])
        elif kind == "count":
            pat, n = payload
            docs[fkey] = docs[fkey].replace(pat, pat + " " + pat, 1)
            expect_fail(docs, cid + ":count:" + str(pat)[:30])
        elif kind == "regex":
            pat, n = payload
            blinded = re.sub(pat, "XXMUTATEDXX", docs[fkey], flags=re.M)
            if blinded == docs[fkey]:
                blinded = docs[fkey] + "\nXXMUTATEDXX " + pat
            docs[fkey] = blinded
            expect_fail(docs, cid + ":regex:" + pat[:30])

    # derived probes
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("152579", "152519", 1)
    expect_fail(docs, "X01:item id falsified against party_features")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("265854", "265850", 1)
    expect_fail(docs, "X02:spell family broken")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("33640", "33641", 1)
    expect_fail(docs, "X03:trainer id falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"] + "\narrow \u2192 here"
    expect_fail(docs, "X04:non-ascii injected")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("unverified between 150 and 175",
                                      "verified as 150", 1)
    expect_fail(docs, "X05:cap caveat falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("4.3 Creature side (mob mining / ore skinning)",
                                      "4.3 Creature sides (mob mining / ore skinning)", 1)
    expect_fail(docs, "X06:heading corrupted")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace(
        "green/grey values are the standing unverified pair",
        "green/grey values were solved this week", 1)
    expect_fail(docs, "X07:unknown-row caveat removed")

    print("Static checks      : %d/%d PASS" % (len(base_pass), len(base_pass) + len(base_fail)))
    print("Mutation probes    : %d/%d detected" % (detected, total))
    for m in misses:
        print("  UNDETECTED:", m)
    return not misses and not base_fail


def main():
    docs = load_all()
    if "--self-test" in sys.argv:
        ok = mutation_tests()
        ok2 = mutation_tests()
        print("SELF-TEST:", "PASS" if (ok and ok2) else "FAIL")
        sys.exit(0 if (ok and ok2) else 1)
    passed, failed = run_checks(docs, verbose="-v" in sys.argv)
    print("Gather_Mining audit: %d PASS, %d FAIL" % (len(passed), len(failed)))
    if failed:
        print("FAILED:", ", ".join(failed))
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
