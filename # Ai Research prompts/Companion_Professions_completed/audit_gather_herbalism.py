#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit for Companion_Professions step 1 (PART 14, STEP 123): Gather_Herbalism.txt.

Checks (statics):
  * structure: the deliverable's ten sections, the prompt's deliverable name,
    the RESEARCH_MASTER STEP 123 lines, plain-text hygiene
  * skill lines and gather spells of 8.3.7 (2366 + the 2658xx family, child
    line ids, caps, learn spells 265833/265836, tracking 2383, legacy ranks)
  * cast time 2 s (2020-10-25 capture), 5 yd, mounted-flag disagreement,
    BfA quality-of-life items (stirrups 253112, barding 154166, Sky Golem,
    glove enchants 153430/159464) and the recorded 1.5 s conflict
  * skill-per-node tables for all eight expansions with their item ids,
    the post-6.0.2 "never blocks" rule, mob herbalism 5 x level
  * server skill-up rules (Lock.db2 check, +1275, bands, SkillChance conf,
    one-skill-up-per-GUID) and respawn mechanics (spawntimesecs, pools,
    Respawn.MinCheckIntervalMS / DynamicMode)
  * gameobject entries read from wowhead per expansion, complete for BfA,
    samples for the older expansions
  * best zones per skill range through BfA 1-175
  * the nine "no client cannot do" items
  * forbidden leftovers: wrong ids, wrong times, mining tracking on a
    herbalism page

Derived: item-id cross-check against BfA_8.3.7_party_features.txt, spell-family
and trainer-id completeness, ASCII hygiene, BfA cap consistency.

Mutation self-test (--self-test): every "has" target is corrupted, every
"absent" string is inserted, every count is altered, every regex is blinded,
and each derived check is falsified; the audit must FAIL on each mutated
document (baseline PASSes).
"""
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))


def load(rel):
    return io.open(os.path.join(BASE, rel), encoding="utf-8").read()


FILES = {
    "doc": "Gather_Herbalism.txt",
    "p1": "01_Herbalism.txt",
    "rm": os.path.join("..", "RESEARCH_MASTER.txt"),
    "pf": os.path.join("..", "BfA_8.3.7_party_features.txt"),
}

# ---------------------------------------------------------------- statics ---
# (id, file, kind, payload)
#   kind "has": payload substring must exist
#   kind "absent": payload substring must NOT exist
#   kind "count": (payload, n) exact count
#   kind "regex": (pattern, n) matches >= n
CHECKS = [
    # --- structure ---
    ("S01", "doc", "has", "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - HERBALISM GATHERING FOR A SERVER-SIDE COMPANION"),
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
    ("S13", "doc", "regex", (r"^  \d+\. Cannot ", 9)),
    ("S14", "doc", "has", "Unverified, collected:"),
    ("S15", "doc", "regex", (r"unverified", 15)),
    ("S16", "p1", "has", "WHAT TO DELIVER - ONE TEXT FILE, Gather_Herbalism.txt"),
    ("S17", "p1", "has", "Do only this step"),
    ("S18", "rm", "has", "--- STEP 123"),
    ("S19", "rm", "has", "Deliver ONE text file named: Gather_Herbalism.txt"),
    ("S20", "rm", "has", "PROFESSIONS FOR THE COMPANION BOTS (15 steps)"),

    # --- skill lines / learning ---
    ("L01", "doc", "regex", (r"2556\s+Classic Herbalism\s+300\s+265819 \(8\.0\.1\)", 1)),
    ("L02", "doc", "regex", (r"2555\s+Outland Herbalism\s+75\s+265821 \(8\.0\.1\)", 1)),
    ("L03", "doc", "regex", (r"2554\s+Northrend Herbalism\s+75\s+265823 \(8\.1\.0\)", 1)),
    ("L04", "doc", "regex", (r"2553\s+Cataclysm Herbalism\s+75\s+265825 \(8\.1\.0\)", 1)),
    ("L05", "doc", "regex", (r"2552\s+Pandaria Herbalism\s+75\s+265827 \(8\.1\.0\)", 1)),
    ("L06", "doc", "regex", (r"2551\s+Draenor Herbalism\s+100\s+265829 \(8\.0\.1\)", 1)),
    ("L07", "doc", "regex", (r"2550\s+Legion Herbalism\s+100\s+265834 \(8\.1\.0\)", 1)),
    ("L08", "doc", "has", "2549     Kul Tiran / Zandalari Herbalism 175   265831 Alliance (8.0.1)"),
    ("L09", "doc", "has", "265835 Horde (8.1.0)"),
    ("L10", "doc", "has", "2366 (the classic spell, learn value 1)"),
    ("L11", "doc", "has", "Kul Tiran Herbalism 265833 (Alliance), Zandalari Herbalism"),
    ("L12", "doc", "has", "265836 (Horde)"),
    ("L13", "doc", "has", "Declan Senal creature 136096"),
    ("L14", "doc", "has", "Jahden Fla"),
    ("L15", "doc", "has", "creature 122704"),
    ("L16", "doc", "has", "Instructor Ulooaka 154257"),
    ("L17", "doc", "has", "Rolm 154408"),
    ("L18", "doc", "has", "item 111350"),
    ("L19", "doc", "has", "Kirea Moondancer 26994"),
    ("L20", "doc", "has", "Rorelien 18776"),
    ("L21", "doc", "has", "Grower Miao 66980"),
    ("L22", "doc", "has", "Herbalism Technique:"),
    ("L23", "doc", "has", "spell 252440"),
    ("L24", "doc", "absent", "265820"),
    ("L25", "doc", "absent", "265832"),

    # --- gather spells ---
    ("P01", "doc", "has", "2366   Herb Gathering - 5 yd range (Interact), 2 sec cast, GCD 0, no cost."),
    ("P02", "doc", "has", "Open Object (Herbalism) value 1275"),
    ("P03", "doc", "regex", (r"Learn Skill\s+Herbalism 182 value 1", 1)),
    ("P04", "doc", "has", "265819, 265821, 265823, 265825, 265827, 265829, 265831, 265834, 265835"),
    ("P05", "doc", "has", "2383   Find Herbs"),
    ("P06", "doc", "has", "2368 (50), 3570 (125), 11993 (200), 28695 (275), 50300 (350)"),
    ("P07", "doc", "has", "74519 (425), 110413 (500)"),
    ("P08", "doc", "has", "/web/20201025165308/"),
    ("P09", "doc", "absent", "Find Minerals"),
    ("P10", "doc", "absent", "4 sec cast"),
    ("P11", "doc", "absent", "Open Object value 1274"),

    # --- time / items ---
    ("T01", "doc", "has", "Base cast time: 2 seconds"),
    ("T02", "doc", "has", "Global cooldown: 0"),
    ("T03", "doc", "has", "Monel-Hardened Stirrups spell 253112"),
    ("T04", "doc", "regex", (r"Coarse Leather\s+Barding item 154166", 1)),
    ("T05", "doc", "has", "Sky Golem item 95416"),
    ("T06", "doc", "has", "Enchant Gloves - Kul Tiran Herbalism item 153430, Enchant"),
    ("T07", "doc", "has", "Gloves - Zandalari Herbalism item 159464"),
    ("T13", "doc", "has", "Enchant Gloves - Kul Tiran Herbalism item 153430"),
    ("T08", "doc", "has", "down from 1.5 seconds"),
    ("T09", "doc", "regex", (r"spell pages are the\s+primary source and they say 2 seconds", 1)),
    ("T10", "doc", "regex", (r"flag \"Can be\s+used while mounted\"", 1)),
    ("T11", "doc", "has", "treat baseline mounted gathering on 8.3.7 as"),
    ("T12", "doc", "absent", "cast time: 1.5 seconds"),

    # --- skill-per-node tables, classic + samples ---
    ("B01", "doc", "regex", (r"Peacebloom\s+1\s+25\s+50\s+100\s+2447", 1)),
    ("B02", "doc", "regex", (r"Silverleaf\s+1\s+25\s+50\s+100\s+765", 1)),
    ("B03", "doc", "regex", (r"Earthroot\s+1\s+40\s+75\s+115\s+2449", 1)),
    ("B04", "doc", "regex", (r"Mageroyal\s+1\s+75\s+100\s+150\s+785", 1)),
    ("B05", "doc", "regex", (r"Briarthorn\s+1\s+95\s+120\s+170\s+2450", 1)),
    ("B06", "doc", "regex", (r"Black Lotus\s+1\s+\?\s+\?\s+300\s+13468", 1)),
    ("B07", "doc", "regex", (r"Dreamfoil\s+1\s+295\s+\?\s+300\s+13463", 1)),
    ("B08", "doc", "regex", (r"Blacker Lotus\s+\?\s+\?\s+\?\s+\?\s+-", 1)),
    ("B09", "doc", "has", "Felweed 22785, Dreaming Glory 22786"),
    ("B10", "doc", "has", "Netherdust Bush 32468"),
    ("B11", "doc", "has", "Goldclover 36901, Fire Leaf 39970"),
    ("B12", "doc", "has", "Frost Lotus 36908"),
    ("B13", "doc", "has", "Cinderbloom 52983, Azshara's Veil 52985"),
    ("B14", "doc", "has", "Twilight Jasmine 52987"),
    ("B15", "doc", "has", "Green Tea Leaf 72234, Rain Poppy 72237"),
    ("B16", "doc", "has", "Golden Lotus 72238"),
    ("B17", "doc", "has", "Frostweed 109124, Starflower 109127"),
    ("B18", "doc", "has", "Nagrand Arrowbloom 109128"),
    ("B19", "doc", "has", "Aethril 124101, Dreamleaf 124102"),
    ("B20", "doc", "has", "Yseralline 128304"),

    # --- BfA table ---
    ("C01", "doc", "regex", (r"Akunda's Bite\s+1\s+\?\s+\?\s+150\s+152507", 1)),
    ("C02", "doc", "regex", (r"Riverbud\s+1\s+\?\s+\?\s+150\s+152505", 1)),
    ("C03", "doc", "regex", (r"Sea Stalk\s+1\s+\?\s+\?\s+150\s+152511", 1)),
    ("C04", "doc", "regex", (r"Siren's Pollen\s+1\s+\?\s+\?\s+150\s+152509", 1)),
    ("C05", "doc", "regex", (r"Star Moss\s+1\s+\?\s+\?\s+150\s+152506", 1)),
    ("C06", "doc", "regex", (r"Winter's Kiss\s+1\s+\?\s+\?\s+150\s+152508", 1)),
    ("C07", "doc", "regex", (r"Anchor Weed\s+1\s+\?\s+\?\s+150\s+152510", 1)),
    ("C08", "doc", "regex", (r"Zin'anthid\s+1\s+\?\s+\?\s+175\s+168487", 1)),
    ("C09", "doc", "has", "every row orange at 1"),
    ("C10", "doc", "has", "ten fragments combine into one herb"),
    ("C11", "doc", "has", "petals/stems/leaves/"),

    # --- creatures ---
    ("M01", "doc", "has", "5 x the creature's level"),
    ("M02", "doc", "has", "and this gives NO skill-ups"),
    ("M03", "doc", "has", "22 creatures in Outland"),
    ("M04", "doc", "has", "Hungarfen 17770 The Underbog"),
    ("M05", "doc", "has", "Blackmoss the Fetid 3535"),
    ("M06", "doc", "has", "Whiplash 129803 Stormsong Valley"),
    ("M07", "doc", "has", "Carnivorous Lasher 149653"),
    ("M08", "doc", "has", "571 creatures spanning every era"),
    ("M09", "doc", "regex", (r"\"Gathered from NPC\s+\(809\)\"", 1)),
    ("M10", "doc", "absent", "gives skill-ups"),

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
    ("R10", "doc", "has", "Herbalism has NO chance decay with skill"),
    ("R11", "doc", "has", "SkillChance.MiningSteps/SkinningSteps"),
    ("R12", "doc", "has", "both = 0 in the conf"),
    ("R13", "doc", "has", "Allow one skill-up until respawned"),
    ("R14", "doc", "has", "per-GUID skill-up list"),
    ("R15", "doc", "absent", "SkillChance.Grey = 5"),
    ("R16", "doc", "absent", "SkillGain.Gathering = 2"),
    ("R17", "doc", "absent", "SkillChance.Orange = 50"),

    # --- respawn ---
    ("N01", "doc", "has", "GO_ACTIVATED (lootable)"),
    ("N02", "doc", "has", "GO_JUST_DEACTIVATED (GameObject.cpp"),
    ("N03", "doc", "has", "m_respawnTime = now + delay"),
    ("N04", "doc", "has", "gameobject.spawntimesecs"),
    ("N05", "doc", "has", "default before load is 300 s"),
    ("N06", "doc", "has", "Respawn.MinCheckIntervalMS = 5000"),
    ("N07", "doc", "has", "Respawn.DynamicMode = 0"),
    ("N08", "doc", "has", "PoolMgr::UpdatePool"),
    ("N09", "doc", "has", "pool_members"),
    ("N10", "doc", "has", "pool_template limits (maxobjects)"),
    ("N11", "doc", "has", "no spawn rows, coordinates or respawn times"),
    ("N12", "doc", "has", "linked respawns"),
    ("N13", "doc", "absent", "Respawn.DynamicMode = 1"),
    ("N14", "doc", "absent", "spawntimesecs is always 60"),

    # --- gameobject entries ---
    ("G01", "doc", "has", "object 1618 Herb"),
    ("G02", "doc", "has", "object 1617 Herb"),
    ("G03", "doc", "has", "object 1619 Herb"),
    ("G04", "doc", "has", "object 181270 Herb"),
    ("G05", "doc", "has", "object 189973 Herb"),
    ("G06", "doc", "has", "object 202747 Herb"),
    ("G07", "doc", "has", "objects 209349 Herb"),
    ("G08", "doc", "has", "221542 Herb (Timeless Isle)"),
    ("G09", "doc", "has", "233117 (Frostwall, Frostfire Ridge)"),
    ("G10", "doc", "has", "228571 (Spires of Arak, Shadowmoon Valley, Lunarfall, ...)"),
    ("G11", "doc", "has", "235376"),
    ("G12", "doc", "has", "237398 (Ashran)"),
    ("G13", "doc", "has", "object 244774 Herb"),
    ("G14", "doc", "has", "Aqueous 247865"),
    ("G15", "doc", "has", "Iridescent 248020"),
    ("G16", "doc", "has", "276237 (Vol'dun, Nazmir, ...)"),
    ("G17", "doc", "has", "276234 (Tiragarde Sound, Stormsong Valley, Drustvar, ...)"),
    ("G18", "doc", "has", "281870 (Nazmir, Zuldazar, Dazar'alor, ...)"),
    ("G19", "doc", "has", "297606 Tiragarde, 297607 Stormsong,"),
    ("G20", "doc", "has", "297060 Drustvar, 297608 Nazmir, 297061 Zuldazar, 297609 Vol'dun"),
    ("G21", "doc", "has", "276240 (Tiragarde Sound, Stormsong Valley, Drustvar, ...)"),
    ("G22", "doc", "has", "281872 (Nazmir, Zuldazar, Vol'dun, ...)"),
    ("G23", "doc", "has", "297610 Tiragarde, 297611 Stormsong, 297062 Drustvar,"),
    ("G24", "doc", "has", "297612 Nazmir, 297064 Zuldazar, 297613 Vol'dun"),
    ("G25", "doc", "has", "Siren's Sting 276239 (Tiragarde Sound, Drustvar, Stormsong"),
    ("G26", "doc", "has", "281869 (Nazmir, Zuldazar, Vol'dun, ...)"),
    ("G27", "doc", "has", "276236 and 281079 (Tiragarde Sound, Drustvar, Stormsong"),
    ("G28", "doc", "has", "281867 and 281868 (Vol'dun, Nazmir, Zuldazar, ...)"),
    ("G29", "doc", "has", "276238 (Drustvar, Tiragarde Sound, Stormsong Valley)"),
    ("G30", "doc", "has", "276242 (Nazmir, Vol'dun, Tiragarde Sound, ...)"),
    ("G31", "doc", "has", "294125 (Drustvar, Tiragarde Sound, Stormsong Valley)"),
    ("G32", "doc", "has", "297065 Tiragarde, 297614 Stormsong, 297066 Drustvar,"),
    ("G33", "doc", "has", "297615 Zuldazar, 297616 Vol'dun, 297617 Nazmir"),
    ("G34", "doc", "has", "326598 (Nazjatar)"),
    ("G35", "doc", "has", "map id 1718"),
    ("G36", "doc", "has", "the name link"),
    ("G37", "doc", "absent", "object 1620 Herb"),
    ("G38", "doc", "absent", "326597"),
    ("G39", "doc", "absent", "276235 ("),

    # --- zones per skill range ---
    ("Z01", "doc", "has", "1-70 starter zones (Tirisfal Glades, Elwynn Forest"),
    ("Z02", "doc", "has", "70-115 Hillsbrad Foothills or Darkshore"),
    ("Z03", "doc", "has", "115-185 Western Plaguelands"),
    ("Z04", "doc", "has", "185-255 Thousand Needles or Eastern Plaguelands (Sungrass)"),
    ("Z05", "doc", "has", "255-300 Swamp of Sorrows and Felwood"),
    ("Z06", "doc", "has", "1-50 Nagrand, Blade's Edge Mountains, Terokkar"),
    ("Z07", "doc", "has", "50-75 Netherstorm (Netherbloom)"),
    ("Z08", "doc", "has", "50-75 Storm Peaks (Icethorn, Lichbloom)"),
    ("Z09", "doc", "has", "Uldum (Whiptail) or Twilight Highlands (Twilight Jasmine)"),
    ("Z10", "doc", "has", "Zidormi creature 162419"),
    ("Z11", "doc", "has", "1-45 Valley of the Four Winds (Silkweed)"),
    ("Z12", "doc", "has", "45-75 Kun-Lai Summit (Snow Lily)"),
    ("Z13", "doc", "has", "any of Nagrand, Talador, Frostfire Ridge, Shadowmoon Valley"),
    ("Z14", "doc", "has", "1-85 any Broken Isles zone"),
    ("Z15", "doc", "has", "Fel-Encrusted Herb Clusters at Broken Shore"),
    ("Z16", "doc", "has", "1-150 Drustvar (Winter's Kiss routes 1-2) and Vol'dun"),
    ("Z17", "doc", "has", "150-175 Nazjatar Zin'anthid (grey at 175)"),
    ("Z18", "doc", "has", "gains slow at ~150"),
    ("Z19", "doc", "absent", "1-175 in Elwynn"),

    # --- cannot-do section ---
    ("W01", "doc", "has", "Cannot see nodes"),
    ("W02", "doc", "has", "Cannot use Find Herbs 2383 for anything"),
    ("W03", "doc", "has", "Cannot receive input-driven casts"),
    ("W04", "doc", "has", "Cannot watch the cast bar"),
    ("W05", "doc", "has", "Cannot loot through a window"),
    ("W06", "doc", "has", "Cannot re-farm one node for skill-ups"),
    ("W07", "doc", "has", "Cannot skin herb corpses unless the fork implements it"),
    ("W08", "doc", "has", "Cannot trust mounted-gather flags blindly"),
    ("W09", "doc", "has", "Cannot exceed the cap or beat the grey band"),
]

# ---------------------------------------------------------------- derived ---
ITEM_IDS_BOTH = ["2447", "765", "2449", "785", "3356", "8831", "13468",
                 "22785", "36901", "52983", "72234", "109124", "124101",
                 "152507", "152510", "168487"]
SPELL_FAMILY = ["2366", "265819", "265821", "265823", "265825", "265827",
                "265829", "265831", "265834", "265835", "265833", "265836"]
TRAINER_IDS = ["136096", "122704", "154257", "154408", "18776", "18748",
               "33639", "33678", "26994", "26974", "26910", "26958", "28704",
               "66980", "65877", "67025", "162419"]


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

    # X01 item ids appear in the deliverable AND in the repo's recorded tables
    ok = all(i in docs["doc"] and i in docs["pf"] for i in ITEM_IDS_BOTH)
    mark("X01-itemids-pf", ok)
    # X02 full spell family on the page
    mark("X02-spell-family", all(s in docs["doc"] for s in SPELL_FAMILY))
    # X03 trainer/quest creature ids all recorded
    mark("X03-trainer-ids", all(t in docs["doc"] for t in TRAINER_IDS))
    # X04 plain-text hygiene: ASCII only, no tabs, no runaway lines
    ok = (all(ord(c) < 128 for c in docs["doc"])
          and "\t" not in docs["doc"]
          and max(len(l) for l in docs["doc"].splitlines()) <= 140)
    mark("X04-ascii-lines", ok)
    # X05 BfA cap consistency: line 2549 caps at 175 and Zin'anthid greys at 175
    ok = bool(re.search(r"2549\s+Kul Tiran / Zandalari Herbalism\s+175", docs["doc"])) \
        and bool(re.search(r"Zin'anthid\s+1\s+\?\s+\?\s+175", docs["doc"])) \
        and "(grey at 175)" in docs["doc"]
    mark("X05-bfa-cap", ok)
    # X06 every expansion section 4 heading present (word-boundary safe:
    #    a corrupted "4.7 Legions" must NOT satisfy the "4.7 Legion" heading)
    ok = all(re.search(re.escape(h) + r"(?![A-Za-z])", docs["doc"])
             for h in [
                 "4.1 Classic", "4.2 The Burning Crusade",
                 "4.3 Wrath of the Lich King", "4.4 Cataclysm",
                 "4.5 Mists of Pandaria", "4.6 Warlords of Draenor",
                 "4.7 Legion", "4.8 Battle for Azeroth"])
    mark("X06-expansion-headings", ok)

    if verbose:
        for cid in passed:
            print("PASS", cid)
        for cid in failed:
            print("FAIL", cid)
    return passed, failed


def load_all():
    return dict((k, load(v)) for k, v in FILES.items())


def mutation_tests():
    """For every check, corrupt the document so the check must fail."""
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
            new = docs[fkey].replace(old, blinded)
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
    docs["doc"] = docs["doc"].replace("3356", "3350", 1)
    expect_fail(docs, "X01:item id falsified against party_features")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("265836", "265830", 1)
    expect_fail(docs, "X02:spell family broken")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("33678", "33670", 1)
    expect_fail(docs, "X03:trainer id falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"] + "\narrow \u2192 here"
    expect_fail(docs, "X04:non-ascii injected")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("(grey at 175)", "(grey at 150)", 1)
    expect_fail(docs, "X05:BfA cap falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("4.7 Legion", "4.7 Legions", 1)
    expect_fail(docs, "X06:expansion heading removed")

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
    print("Gather_Herbalism audit: %d PASS, %d FAIL" % (len(passed), len(failed)))
    if failed:
        print("FAILED:", ", ".join(failed))
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
