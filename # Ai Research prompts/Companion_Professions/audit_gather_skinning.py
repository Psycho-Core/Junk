#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit for Companion_Professions step 3 (PART 14, STEP 125): Gather_Skinning.txt.

Checks (statics):
  * structure: ten sections, the prompt's deliverable name, RESEARCH_MASTER
    STEP 125 lines, plain-text hygiene
  * skill lines 393/2564..2557 with caps and expansion learn spells, the
    faction pairing caveat, legacy rank ladder, cap caveats (150 vs 175,
    Draenor/Legion 100 vs 150), trainers for every expansion, Flayer, no
    tracking spell
  * gather spell: 8613 Skin Mob facts and flags, rank variants, no
    per-expansion on-corpse spell
  * cast time 1.5 s three ways, the four 1.5->0.5 items, mounted flag left
    unverified, knife item 7005 history (+10 vs +4 unverified)
  * skinnable types, the full 12-row level->required-skill band table with
    worked examples, non-monotonic warning, 2020-article divergence,
    GetProfessionSkillForExp, both standing unverified cautions, colour
    words, leather/hide/scale tables with item ids, BfA five materials,
    SkinLootID server verdict, volatiles, Core Leather 310, count rule
  * skill-up rules: SkillChance table, elite x2, SkinningSteps decay, cap
    refusal, 2011 hotfix, 3.1.0 no-fail, 8.0.1 split, vanilla stall
  * corpse lifecycle: no gameobjects, loot-empty, tap, despawn warnings,
    observed respawn rates, instance resets, world-DB-only intervals
  * creature entries per expansion with the guides' NPC ids and the one
    /way coordinate, #skinning anchors, bulk-filter id unverified
  * best zones per skill range through BfA 1-175
  * ten "N. Cannot ..." items
  * forbidden leftovers: wrong cast times, mining/herbalism content

Derived: item ids present in BOTH the deliverable and BfA_8.3.7_party
_features.txt, spell completeness, trainer and creature id completeness,
ASCII hygiene, BfA-cap consistency, the three 4.x subheadings, the band
examples, the eight guide slugs.

Mutation self-test (--self-test): every target is falsified at ALL of its
occurrences, regexes are blinded, derived checks are falsified (doc side
and party_features side); baseline must PASS first.
"""
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))


def load(rel):
    return io.open(os.path.join(BASE, rel), encoding="utf-8").read()


FILES = {
    "doc": "Gather_Skinning.txt",
    "p2": "03_Skinning.txt",
    "rm": os.path.join("..", "RESEARCH_MASTER.txt"),
    "pf": os.path.join("..", "BfA_8.3.7_party_features.txt"),
}

CHECKS = [
    # --- structure ---
    ("S01", "doc", "has", "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - SKINNING GATHERING FOR A SERVER-SIDE COMPANION"),
    ("S02", "doc", "has", "1. THE SKILL LINES AND HOW A COMPANION LEARNS THEM"),
    ("S03", "doc", "has", "2. THE SPELL IDS THAT GATHER"),
    ("S04", "doc", "has", "3. HOW LONG A GATHER TAKES"),
    ("S05", "doc", "has", "4. SKILL NEEDED PER CREATURE (AND WHAT DROPS)"),
    ("S06", "doc", "has", "5. HOW THE SKILL RISES (SERVER RULES)"),
    ("S07", "doc", "has", "6. HOW CORPSES \"RESPAWN\""),
    ("S08", "doc", "has", "7. CREATURE ENTRIES BY ZONE, PER EXPANSION"),
    ("S09", "doc", "has", "8. BEST ZONES FOR EACH SKILL RANGE (THROUGH THE BFA RANGE)"),
    ("S10", "doc", "has", "9. WHAT A SERVER-SIDE CHARACTER (NO CLIENT) CANNOT DO"),
    ("S11", "doc", "has", "10. SOURCES AND UNVERIFIED INDEX"),
    ("S12", "doc", "absent", "\t"),
    ("S13", "doc", "regex", (r"^\s{1,2}\d+\. Cannot ", 10)),
    ("S14", "doc", "has", "Unverified, collected:"),
    ("S15", "doc", "regex", (r"unverified", 20)),
    ("S16", "p2", "has", "WHAT TO DELIVER - ONE TEXT FILE, Gather_Skinning.txt"),
    ("S17", "p2", "has", "Do only this step"),
    ("S18", "rm", "has", "--- STEP 125"),
    ("S19", "rm", "has", "Deliver ONE text file named: Gather_Skinning.txt"),
    ("S20", "rm", "has", "PROFESSIONS FOR THE COMPANION BOTS (15 steps)"),

    # --- skill lines / learning ---
    ("L01", "doc", "regex", (r"2564\s+Classic Skinning\s+300\s+265855 \(8\.0\.1\)", 1)),
    ("L02", "doc", "regex", (r"2563\s+Outland Skinning\s+75\s+265857 \(8\.0\.1\)", 1)),
    ("L03", "doc", "regex", (r"2562\s+Northrend Skinning\s+75\s+265859 \(8\.1\.0\)", 1)),
    ("L04", "doc", "regex", (r"2561\s+Cataclysm Skinning\s+75\s+265861 \(8\.1\.0\)", 1)),
    ("L05", "doc", "regex", (r"2560\s+Pandaria Skinning\s+75\s+265863 \(8\.1\.0\)", 1)),
    ("L06", "doc", "regex", (r"2559\s+Draenor Skinning\s+100\s+265865 \(8\.0\.1\)", 1)),
    ("L07", "doc", "regex", (r"2558\s+Legion Skinning\s+100\s+265867 \(8\.1\.0\)", 1)),
    ("L08", "doc", "regex", (r"2557\s+Kul Tiran / Zandalari Skinning\s+175\s+265869 Alliance \(8\.0\.1\)", 1)),
    ("L09", "doc", "has", "265871 Horde (8.1.0)"),
    ("L10", "doc", "regex", (r"393\s+Skinning \(base\)\s+-\s+8613", 1)),
    ("L11", "doc", "regex", (r"How 265870/265872 pair\s+with 265869/265871 is unverified", 1)),
    ("L12", "doc", "has", "unverified between 150 and 175"),
    ("L13", "doc", "has", "BfA 1-175"),
    ("L14", "doc", "has", "shows 1-150 for both - those bar caps are unverified too"),
    ("L15", "doc", "has", "8617 Journeyman [50]"),
    ("L16", "doc", "has", "102216 [500]"),
    ("L17", "doc", "has", "158756 and 195125 with"),
    ("L18", "doc", "has", "Training cost: 10"),
    ("L19", "doc", "has", "taught by 45 trainers"),
    ("L20", "doc", "has", "Rana the Cutta creature 122699"),
    ("L21", "doc", "has", "Camilla Darksky creature 136061"),
    ("L22", "doc", "has", "Instructor Ulooaka 154257"),
    ("L23", "doc", "has", "Mr. Pleeb creature 123500"),
    ("L24", "doc", "has", "Rolm 154408"),
    ("L25", "doc", "regex", (r"265865 shows no\s+\"Taught by\" list", 1)),
    ("L26", "doc", "has", "\"A Guide to Skinning in Draenor\""),
    ("L27", "doc", "has", "40131 or Stormscale Sample 40141"),
    ("L28", "doc", "has", "rewards Legion Skinner spell 201707"),
    ("L29", "doc", "has", "Derik Marks"),
    ("L30", "doc", "has", "Moorutu 18755"),
    ("L31", "doc", "has", "Tyn 16692"),
    ("L32", "doc", "has", "12 old-world trainers"),
    ("L33", "doc", "regex", (r"265855 \(Classic\) shows no\s+\"Taught\s+by\" list", 1)),
    ("L34", "doc", "has", "Flayer"),
    ("L35", "doc", "has", "\"+5 to their skill\""),
    ("L36", "doc", "has", "Find Herbs is 2383, Find Minerals 2580"),
    ("L37", "doc", "has", "Skinning has no equivalent"),
    ("L38", "doc", "has", "ContentTuning expansion id"),

    # --- gather spell ---
    ("G01", "doc", "has", "The single on-corpse cast at every expansion: 8613"),
    ("G02", "doc", "has", "Skin Mob, value 1"),
    ("G03", "doc", "has", "Learn Skill Skinning 393"),
    ("G04", "doc", "has", "Range 5 yards (Interact)"),
    ("G05", "doc", "has", "NO per-expansion on-corpse spells"),
    ("G06", "doc", "has", "pre-8.0 rank"),
    ("G07", "doc", "has", "\"Other ranks\" of 8613"),
    ("G08", "doc", "has", "Generates no threat"),
    ("G09", "doc", "has", "Suppress Caster Procs"),
    ("G10", "doc", "has", "Do Not Display Range"),
    ("G11", "doc", "regex", (r"Don't close loot window", 2)),
    ("G12", "doc", "has", "right-click the corpse (2019"),

    # --- time / tools ---
    ("T01", "doc", "has", "Base cast time: 1.5 seconds, range 5 yards, cost none, GCD 0"),
    ("T02", "doc", "has", "1.5 sec cast"),
    ("T03", "doc", "has", "Cast time 1.5 seconds"),
    ("T04", "doc", "has", "skinning time down from 1.5 seconds to 0.5"),
    ("T05", "doc", "has", "reduces your skinning time from 1.5 seconds to 0.5"),
    ("T06", "doc", "has", "Enchant Gloves - Kul Tiran Skinning item 153434"),
    ("T07", "doc", "has", "Enchant Gloves - Zandalari Skinning item 159467"),
    ("T08", "doc", "has", "Enchant Gloves - Legion Skinning item 128560"),
    ("T09", "doc", "has", "Darkmoon Firewater item 124671"),
    ("T10", "doc", "has", "baseline mounted skinning"),
    ("T11", "doc", "has", "item 7005"),
    ("T12", "doc", "has", "Requires Skinning (1)"),
    ("T13", "doc", "has", "durability added 4.0.3a"),
    ("T14", "doc", "regex", (r"No longer\s+required to skin", 1)),
    ("T15", "doc", "has", "+10 Skinning while equipped"),
    ("T16", "doc", "has", "+4 Skinning Skill"),
    ("T17", "doc", "has", "BfA-era bonus was +10 or +4 is unverified"),
    ("T18", "doc", "has", "Gnomish Army Knife"),
    ("T19", "doc", "has", "profession-tool"),

    # --- who / required skill / drops ---
    ("K01", "doc", "has", "4.1 Who is skinnable"),
    ("K02", "doc", "has", "beasts, dragonkin, silithids, some nerubians, demon"),
    ("K03", "doc", "has", "very rarely, humanoids"),
    ("K04", "doc", "has", "most birds"),
    ("K05", "doc", "has", "looted empty before it can be"),
    ("K06", "doc", "has", "Critters stopped being skinnable in patch 3.2.0"),
    ("K07", "doc", "has", "dragonkin or insectoid foes"),
    ("K08", "doc", "has", "do not need to have killed it yourself"),
    ("B01", "doc", "regex", (r"1-10\s+1\s+1 -> 1, 10 -> 1", 1)),
    ("B02", "doc", "regex", (r"11-19\s+\(level - 10\) x 10\s+11 -> 10, 19 -> 90", 1)),
    ("B03", "doc", "regex", (r"20-73\s+level x 5\s+20 -> 100, 60 -> 300, 73 -> 365", 1)),
    ("B04", "doc", "regex", (r"74-79\s+level x 10 - 365\s+74 -> 375, 79 -> 425", 1)),
    ("B05", "doc", "regex", (r"80-84\s+level x 5 \+ 35\s+80 -> 435, 84 -> 455", 1)),
    ("B06", "doc", "regex", (r"85-87\s+level x 15 - 805\s+85 -> 470, 87 -> 500", 1)),
    ("B07", "doc", "regex", (r"88-92\s+\(level - 62\) x 20\s+88 -> 520, 92 -> 600", 1)),
    ("B08", "doc", "regex", (r"93-104\s+level x 5 \+ 175\s+93 -> 640, 104 -> 695", 1)),
    ("B09", "doc", "regex", (r"105-107\s+level x 15 - 905\s+105 -> 670, 107 -> 700", 1)),
    ("B10", "doc", "regex", (r"108-112\s+\(level - 72\) x 20\s+108 -> 720, 112 -> 800", 1)),
    ("B11", "doc", "regex", (r"113-122\s+\(level - 32\) x 10\s+113 -> 810, 120 -> 880", 1)),
    ("B12", "doc", "regex", (r"123 and up\s+900\s+flat cap", 1)),
    ("K09", "doc", "has", "(level 104 needs 695"),
    ("K10", "doc", "has", "(470 at level 84, 530 at"),
    ("K11", "doc", "has", "computes and is treated as authoritative"),
    ("K12", "doc", "has", "GetProfessionSkillForExp"),
    ("K13", "doc", "has", "level 120 corpse"),
    ("K14", "doc", "has", "EffectSkinning does not refuse"),
    ("K15", "doc", "has", "refusal is client-side"),
    ("K16", "doc", "regex", (r"fork enforces\s+it server-side is unverified", 1)),
    ("K17", "doc", "has", "scale is unverified"),
    ("K18", "doc", "has", "skin any mobs with"),
    ("K19", "doc", "has", "type of leather you get is determined by the"),
    ("K20", "doc", "has", "red = not high enough skill to skin"),
    ("K21", "doc", "has", "grey = never"),
    ("K22", "doc", "regex", (r"Stonehide Leather\s+124113\s+100\+ Broken Isles", 1)),
    ("K23", "doc", "regex", (r"Ruined Leather Scraps\s+2934\s+5-17", 1)),
    ("K24", "doc", "regex", (r"Rugged Leather\s+8170\s+45-60", 1)),
    ("K25", "doc", "has", "usually need curing"),
    ("K26", "doc", "has", "dragonkin speciality rather than a level band"),
    ("K27", "doc", "has", "Coarse Leather 152541"),
    ("K28", "doc", "has", "Shimmerscale 153050"),
    ("K29", "doc", "has", "154722 (quality 2, hide), Mistscale 153051 (quality 2, scale)"),
    ("K30", "doc", "has", "154165 (quality 2, bone)"),
    ("K31", "doc", "has", "skinning_loot_template keyed by creature entry"),
    ("K32", "doc", "has", "none of it is in client DB2 build 35662"),
    ("K33", "doc", "has", "Bloated Stomach container"),
    ("K34", "doc", "has", "about 20% each of five"),
    ("K35", "doc", "has", "1-4 Volatile Air"),
    ("K36", "doc", "has", "Requires 310 Skinning"),
    ("K37", "doc", "has", "same number of leathers at expansion skill 1 as at 75"),

    # --- skill rise ---
    ("U01", "doc", "has", "Player::UpdateGatherSkill"),
    ("U02", "doc", "regex", (r"Orange\s+red \+ 0\s+100%\s+SkillChance\.Orange = 100", 1)),
    ("U03", "doc", "regex", (r"Yellow\s+red \+ 30\s+75%\s+SkillChance\.Yellow = 75", 1)),
    ("U04", "doc", "regex", (r"Green\s+red \+ 60\s+25%\s+SkillChance\.Green = 25", 1)),
    ("U05", "doc", "regex", (r"Grey\s+red \+ 90\s+0%\s+SkillChance\.Grey = 0", 1)),
    ("U06", "doc", "has", "green = yellow + 30, grey = green + 30"),
    ("U07", "doc", "has", "SkillGain.Gathering = 1"),
    ("U08", "doc", "has", "multiplier is 2 for elites and 1"),
    ("U09", "doc", "has", "SkillChance.SkinningSteps"),
    ("U10", "doc", "has", "halving it once per steps skill points"),
    ("U11", "doc", "has", "refuses to raise a skill once it"),
    ("U12", "doc", "has", "Hotfix 2011-06-01"),
    ("U13", "doc", "has", "no longer continue"),
    ("U14", "doc", "has", "no longer fail when Mining"),
    ("U15", "doc", "has", "separate skill bar"),
    ("U16", "doc", "has", "250 or 285"),
    ("U17", "doc", "has", "Level 40 seems to be required"),

    # --- respawn ---
    ("R01", "doc", "has", "no gameobjects at all"),
    ("R02", "doc", "has", "\"tapped\""),
    ("R03", "doc", "has", "corpses might start"),
    ("R04", "doc", "has", "corpses will start despawning"),
    ("R05", "doc", "has", "One skin per corpse"),
    ("R06", "doc", "has", "extremely quickly"),
    ("R07", "doc", "has", "probably around 30 seconds"),
    ("R08", "doc", "has", "spawn \"instantly\" one or two"),
    ("R09", "doc", "has", "always at least one pack up"),
    ("R10", "doc", "has", "Reset all instances"),
    ("R11", "doc", "has", "the reset locks"),
    ("R12", "doc", "has", "world database rows"),
    ("R13", "doc", "has", "no spawn rows"),
    ("R14", "doc", "has", "exact intervals unverified"),

    # --- creature entries by zone ---
    ("C01", "doc", "has", "Skinning has no gameobject nodes"),
    ("C02", "doc", "has", "creature_template"),
    ("C03", "doc", "has", "#skinning"),
    ("C04", "doc", "has", "npc=79034#skinning"),
    ("C05", "doc", "has", "herbalism's filter is cr=15"),
    ("C06", "doc", "has", "mining's is cr=16, skinning's id is unverified"),
    ("C07", "doc", "has", "verified-on-wowhead, unverified-on-your-8.3.7-core"),
    ("C08", "doc", "has", "Not skinnable"),
    ("C09", "doc", "has", "guide gives no"),
    ("C10", "doc", "has", "creature ids here: unverified"),
    ("C11", "doc", "has", "gorilla ids unverified"),
    ("C12", "doc", "has", "The per-entry DROP table is"),
    ("C13", "doc", "has", "78.7, 72.2"),
    ("C14", "doc", "regex", (r"Armored Battleboar 36696", 1)),
    ("C15", "doc", "regex", (r"Ebon Slavehunter 42043 skinnable", 1)),
    ("C16", "doc", "has", "Tamed Clefthoof 79034"),
    ("C17", "doc", "has", "Scavenging Boar 133822"),
    ("C18", "doc", "has", "Young Bloodgazer 115675"),

    # --- best zones ---
    ("Z01", "doc", "regex", (r"Vanilla \(Classic bar\) 1-300:", 1)),
    ("Z02", "doc", "regex", (r"Outland 1-75:", 1)),
    ("Z03", "doc", "regex", (r"Northrend 1-75:", 1)),
    ("Z04", "doc", "regex", (r"Cataclysm 1-75:", 1)),
    ("Z05", "doc", "regex", (r"Pandaria 1-75:", 1)),
    ("Z06", "doc", "regex", (r"Draenor 1-100:", 1)),
    ("Z07", "doc", "regex", (r"Legion 1-100:", 1)),
    ("Z08", "doc", "regex", (r"Battle for Azeroth 1-175:", 1)),
    ("Z09", "doc", "has", "15-20"),
    ("Z10", "doc", "has", "you will reach 75 in"),
    ("Z11", "doc", "has", "10-15 minutes"),
    ("Z12", "doc", "has", "about 4 minutes per clear"),
    ("Z13", "doc", "has", "two clears \"around 10"),
    ("Z14", "doc", "has", "two clears about 10 minutes"),
    ("Z15", "doc", "has", "Legacy Raid size 25 man"),
    ("Z16", "doc", "has", "always at least 4-5"),
    ("Z17", "doc", "has", "cap caveats in section 1"),
    ("Z18", "doc", "has", "Worgen Flayer +5"),
    ("Z19", "doc", "has", "every cast to 0.5 seconds"),

    # --- cannot do ---
    ("N01", "doc", "has", "knife-shaped cursor"),
    ("N02", "doc", "has", "no CMSG"),
    ("N03", "doc", "has", "5-yard interact range"),
    ("N04", "doc", "has", "read the corpse's loot itself first"),
    ("N05", "doc", "has", "skinning_loot_template output"),
    ("N06", "doc", "has", "one skin empties it"),
    ("N07", "doc", "has", "is tapped (section 6)"),
    ("N08", "doc", "has", "world-DB only (section 6)"),
    ("N09", "doc", "has", "+10 at 5.0.4 vs +4"),
    ("N10", "doc", "has", "elite x2 multiplier"),
    ("N11", "doc", "has", "must read the skill line directly"),

    # --- sources ---
    ("V01", "doc", "has", "Sources read 2026-10-25 unless noted:"),
    ("V02", "doc", "has", "265869, 265871 (each: potential"),
    ("V03", "doc", "has", "name=Skinning"),
    ("V04", "doc", "has", "spells=11.393"),
    ("V05", "doc", "has", "warcraft.wiki.gg Skinning"),
    ("V06", "doc", "has", "Skinning_Knife (item 7005 history)"),
    ("V07", "doc", "has", "20190830101450"),
    ("V08", "doc", "has", "sections 4.1, 4.2, 4.3, 4.6, 4.7 and 5"),
    ("V09", "doc", "regex", (r"pairing of\s+guide spells 265870/265872", 1)),
    ("V10", "doc", "has", "110-120"),
    ("V11", "doc", "regex", (r"bulk wowhead \"skinnable NPC\"\s+filter id", 1)),
    ("V12", "doc", "has", "158756 and 195125"),
    ("V13", "doc", "has", "205243"),
    ("V14", "doc", "has", "255065, 267486"),
    ("V15", "doc", "has", "vanilla-bar point-stall"),
    ("V16", "doc", "has", "no 2018-era capture of 8613 read"),
]

# leather/hide/scale/BfA ids that must appear in the deliverable AND in the
# recorded party_features 4.3 tables
ITEM_IDS_BOTH = [
    "2934", "2318", "2319", "4234", "4304", "8170", "25649", "21887",
    "33567", "33568", "52977", "52976", "72162", "72120", "124113",
    "783", "4232", "4235", "8169", "8171", "25707", "52980", "72163",
    "110610",
    "7286", "7392", "8165", "15415", "15412", "15416", "15414", "15410",
    "12607", "20381", "29548", "38557",
    "152541", "153050", "154722", "153051", "154165",
]

SPELL_FAMILY = [
    "8613", "8617", "8618", "10768", "32678", "50305", "74522", "102216",
    "158756", "195125",
    "265855", "265857", "265859", "265861", "265863", "265865", "265867",
    "265869", "265871", "265870", "265872",
    "201707", "2383", "2580", "40131", "40141",
]

TRAINER_IDS = [
    "122699", "136061", "154257", "123500", "154408",
    "27000", "26986", "26913", "26963", "28696",
    "18755", "18777", "19180", "16692", "33618",
    "6291", "6292", "6306", "53437", "8144", "1292", "7089", "6287",
    "6289", "44782", "7088", "6290",
]

CREATURE_IDS = [
    "36696", "42043", "42041", "34898",
    "20671", "20773", "20610", "20777", "20634", "17131",
    "28098", "28096", "39751", "39747",
    "46508", "46507", "46153", "46970", "46162", "46158",
    "59139", "56256",
    "79034", "76597", "80782", "84341",
    "115675", "115666", "111206", "98808",
    "133822", "130953",
    "111351", "7005", "124671", "153434", "159467", "128560",
]

GUIDE_SLUGS = [
    "vanilla", "outland", "northrend", "cataclysm",
    "pandaria", "draenor", "legion", "zandalari-kul-tiran-bfa",
]


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
    # X02 spell family / gather ids complete
    mark("X02-spell-family", all(s in docs["doc"] for s in SPELL_FAMILY))
    # X03 trainer creature ids
    mark("X03-trainer-ids", all(t in docs["doc"] for t in TRAINER_IDS))
    # X04 plain-text hygiene
    ok = (all(ord(c) < 128 for c in docs["doc"])
          and "\t" not in docs["doc"]
          and max(len(l) for l in docs["doc"].splitlines()) <= 140)
    mark("X04-ascii-lines", ok)
    # X05 BfA cap consistency: spell rows say 175 and the caveat keeps 150/175
    ok = bool(re.search(r"2557\s+Kul Tiran / Zandalari Skinning\s+175", docs["doc"])) \
        and "unverified between 150 and 175" in docs["doc"] \
        and "BfA 1-175" in docs["doc"]
    mark("X05-bfa-cap", ok)
    # X06 the three section 4.x subheadings (word-boundary safe)
    ok = all(re.search(re.escape(h) + r"(?![A-Za-z])", docs["doc"])
             for h in ["4.1 Who is skinnable",
                       "4.2 Required skill as a function of creature level",
                       "4.3 What a corpse drops"])
    mark("X06-section4-headings", ok)
    # X07 the non-monotonic warning keeps both worked examples
    ok = "104 -> 695" in docs["doc"] and "105 -> 670" in docs["doc"] \
        and "not monotonic" in docs["doc"]
    mark("X07-band-examples", ok)
    # X08 all eight guide slugs in the sources
    mark("X08-guide-slugs", all(g in docs["doc"] for g in GUIDE_SLUGS))
    # X09 skinnable creature id set
    mark("X09-creature-ids", all(c in docs["doc"] for c in CREATURE_IDS))

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
    docs["doc"] = docs["doc"].replace("152541", "152514", 1)
    expect_fail(docs, "X01:doc item id falsified against party_features")
    docs = dict(base)
    docs["pf"] = docs["pf"].replace("153050", "153500", 1)
    expect_fail(docs, "X01:party_features id falsified against doc")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("265867", "265866", 1)
    expect_fail(docs, "X02:spell family broken")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("136061", "136062", 1)
    expect_fail(docs, "X03:trainer id falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("79034", "79035", 1)
    expect_fail(docs, "X09:creature id falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"] + "\narrow \u2192 here"
    expect_fail(docs, "X04:non-ascii injected")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("unverified between 150 and 175",
                                      "verified as 150", 1)
    expect_fail(docs, "X05:cap caveat falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("4.3 What a corpse drops",
                                      "4.3 What a corpse drop", 1)
    expect_fail(docs, "X06:heading corrupted")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("105 -> 670", "105 -> 675", 1)
    expect_fail(docs, "X07:band example falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("zandalari-kul-tiran-bfa",
                                      "zandalari-kul-tiran-old")
    expect_fail(docs, "X08:guide slug removed")

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
    print("Gather_Skinning audit: %d PASS, %d FAIL" % (len(passed), len(failed)))
    if failed:
        print("FAILED:", ", ".join(failed))
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
