#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit for Companion_Professions step 4 (PART 14, STEP 126): Craft_Alchemy.txt.

Checks (statics):
  * structure: ten sections, the prompt's deliverable name, RESEARCH_MASTER
    STEP 126 lines, plain-text hygiene, the eight 3.x route blocks
  * skill lines 171/2485..2478 with caps, expansion learn spells and patches,
    Requires Alchemy (1), the Draenor treatise chain, the faction pairing
  * trainers: every creature entry quoted from the guides and spell pages,
    the two BfA /way coordinates, the twin-Linzy warning, classic trainer set
  * routes: all recipe spell ids per expansion (as one derived set plus the
    named anchor recipes), craft markers, colour warnings quoted from guides
  * materials: Crystal Vial everywhere with the seven-era evidence line,
    herb ids per expansion, the Sand Shifter unverified flag, recipe items
  * costs: learn-spell Training cost 10 lines, recipe cost samples 7750/130/
    9/5, the 50-gold conflict, reputation discount functions
  * level needed: ReqLevel/ReqSkillLine/ReqAbility, free primary profession
    point, Legion 10/45, BfA flask 115, no Journeyman/Expert rank spells
  * core rules: TakeReagents before HandleEffects, full-bag path,
    EffectCreateItem, UpdateCraftSkill and SkillChance maths, MECHANIC_
    DISCOVERY branch, focus checks, trainer interaction flow
  * cannot-do: seven "- Cannot" bullets, interaction guard, full-bag loss,
    twin Linzy trap, cooldowns
  * conflicts: Draenor 75 vs 100, BfA 150 vs 175, 10 vs 50 gold, +5 vs +15,
    rank labels, difficulty strings not decoded
  * sources: eight guide slugs, TC files, wiki, own Gather_Herbalism file

Derived: learn-spell set, line-id set, creature-id set, full route spell-id
set, herb/item id set, craft-count markers, vial logic, ASCII/line hygiene.

Mutation self-test (--self-test): every target is falsified at ALL of its
occurrences, regexes are blinded, derived sets get their own falsifications;
baseline must PASS first.
"""
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))


def load(rel):
    return io.open(os.path.join(BASE, rel), encoding="utf-8").read()


FILES = {
    "doc": "Craft_Alchemy.txt",
    "p4": "04_Alchemy.txt",
    "rm": os.path.join("..", "RESEARCH_MASTER.txt"),
}

# --- id sets (all must appear in the deliverable, word-boundary checked) ---
LEARN_IDS = [
    "2259", "264211", "264212", "264213", "264220", "264243",
    "264245", "264247", "264248", "264250", "264255", "265787",
]

LINE_IDS = ["171", "2478", "2479", "2480", "2481", "2482", "2483", "2484", "2485"]

TRAINER_IDS = [
    # classic capitals
    "3347", "4611", "3009", "16642", "5499", "5177", "4160", "16723",
    # outland
    "33630", "33674", "19052", "18802", "16588", "33608",
    # northrend / legion twins / vendors
    "28703", "92456", "92458", "92457",
    # pandaria / draenor
    "65186", "56777", "87048", "87542",
    # bfa + nazjatar
    "122703", "132228", "154393", "153811",
    # reputation vendors (bfa rank 3)
    "131287", "135800", "135459", "135808", "135804", "135815",
    "135447", "135446",
    # vendor / quest / drop npcs
    "19837", "18005", "19042", "75043", "74254",
    "96028", "104218", "98208", "91007", "96759", "95676", "95888",
    "97140", "110321",
    # legion quest anchors
    "39325", "39346", "201697",
]

ROUTE_IDS = [
    # classic
    "2330", "2337", "3171", "3447", "3173", "7181", "3452", "11449",
    "11450", "11457", "11465", "11478", "17555", "17556", "17572",
    # outland
    "33732", "33740", "33738", "28545", "45061", "28551", "28555",
    "28562", "22907", "22911",
    # northrend
    "53839", "53900", "54218", "53840", "53905", "53837", "57427",
    "57425", "53902", "60350", "60396", "60405", "40199",
    # cataclysm
    "93935", "80477", "80481", "80484", "80486", "80487", "80488",
    "80491", "80494", "80496", "80498", "80723", "80250", "80721",
    "80248", "80246", "80247",
    # pandaria
    "114752", "114775",
    # draenor
    "175880", "118700", "156577", "156580", "156578", "156579",
    "156582", "156561", "156563", "156568", "156564", "156585",
    "109137", "109558", "156614", "112566", "34019", "33410",
    # legion
    "188301", "188297", "188304", "188299", "188300", "188335",
    "188326", "188329", "188332", "188337", "188338", "188339",
    "188340", "188341", "188342", "188343", "188344", "188345",
    "188346", "188347", "188348", "229217", "124124", "127834",
    "127926", "127927", "127928", "127929", "127930", "127931",
    "127932", "127933", "142121",
    # bfa
    "252382", "252385", "252391", "252394", "252400", "252397",
    "252383", "252386", "252384", "252387", "252389", "252390",
    "252335", "252345", "252339", "252342", "279169", "279166",
    "279163", "279160", "279167", "279161", "279164", "279170",
    "252352", "252349", "252358", "252355", "252353", "252359",
    "252356", "252350", "301310", "301311", "251832",
    # shared intermediates
    "118", "152494", "152495",
]

HERB_IDS = [
    # classic
    "2447", "765", "2450", "785", "2453", "3820", "3357", "3356",
    "3821", "3355", "8838", "3358", "8839", "8846", "13466", "13463",
    "13464", "13465", "13467", "3371",
    # outland
    "22785", "22786", "22787", "22791", "22792",
    # northrend
    "36907", "36904", "36901", "36903", "36906", "36905", "36908",
    "37704", "36932", "36929", "36860", "36917", "36923", "35623",
    # cataclysm
    "52983", "52985", "52986", "52329", "52987", "52988", "52179",
    "52178", "52180",
    # pandaria
    "72234", "72235", "72237", "79010", "79011", "72238",
    # draenor
    "109124", "109125", "109126", "109127", "109128", "109129",
    # legion
    "124101", "124102", "124103", "124104", "124105", "124106",
    "128304",
    # bfa
    "152505", "152506", "152507", "152508", "152509", "152510",
    "152511", "168487", "1718",
]

GUIDE_SLUGS = [
    "vanilla-", "outland-", "northrend-", "cataclysm-",
    "pandaria-", "draenor-", "legion-alchemy-leveling",
    "zandalari-kul-tiran-bfa",
]

CHECKS = [
    # --- structure ---
    ("S01", "doc", "has", "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - ALCHEMY CRAFTING FOR A SERVER-SIDE COMPANION"),
    ("S02", "doc", "has", "1. THE SKILL LINES AND HOW A COMPANION LEARNS THEM"),
    ("S03", "doc", "has", "2. TRAINERS AND THEIR POSITIONS"),
    ("S04", "doc", "has", "3. THE CHEAPEST ROUTE FROM 1 TO THE CAP OF EACH LINE"),
    ("S05", "doc", "has", "4. MATERIALS AND WHERE EACH COMES FROM"),
    ("S06", "doc", "has", "5. TRAINER COSTS"),
    ("S07", "doc", "has", "6. LEVEL NEEDED"),
    ("S08", "doc", "has", "7. WHAT THE CORE MUST DO FOR A CRAFT TO SUCCEED"),
    ("S09", "doc", "has", "8. WHAT A SERVER-SIDE CHARACTER (NO CLIENT) CANNOT DO"),
    ("S10", "doc", "has", "9. CONFLICTS AND UNVERIFIED INDEX"),
    ("S11", "doc", "has", "10. SOURCES AND UNVERIFIED INDEX"),
    ("S12", "doc", "absent", "\t"),
    ("S13", "doc", "regex", (r"^- Cannot ", 7)),
    ("S14", "doc", "regex", (r"unverified", 20)),
    ("S15", "doc", "regex", (r"^3\.[1-8] ", 8)),
    ("S16", "p4", "has", "WHAT TO DELIVER - ONE TEXT FILE, Craft_Alchemy.txt"),
    ("S17", "p4", "has", "Do only this step"),
    ("S18", "rm", "has", "--- STEP 126"),
    ("S19", "rm", "has", "Deliver ONE text file named: Craft_Alchemy.txt"),
    ("S20", "rm", "has", "PROFESSIONS FOR THE COMPANION BOTS (15 steps)"),

    # --- skill lines and learn spells ---
    ("L01", "doc", "has", "Classic Alchemy step"),
    ("L02", "doc", "has", "2484     Outland Alchemy"),
    ("L03", "doc", "has", "2483     Northrend Alchemy"),
    ("L04", "doc", "has", "2482     Cataclysm Alchemy"),
    ("L05", "doc", "has", "2481     Pandaria Alchemy"),
    ("L06", "doc", "has", "2480     Draenor Alchemy"),
    ("L07", "doc", "has", "2479     Legion Alchemy"),
    ("L08", "doc", "has", "2478     Kul Tiran / Zandalari Alchemy"),
    ("L09", "doc", "has", "171      Alchemy (base)"),
    ("L10", "doc", "has", "264212 (8.1.0)"),
    ("L11", "doc", "has", "264255 Alliance (8.0.1)"),
    ("L12", "doc", "has", "265787 Horde (8.1.0)"),
    ("L13", "doc", "has", "264248 (8.1.0, wrapper"),
    ("L14", "doc", "has", "264247 added 8.0.1"),
    ("L15", "doc", "has", "Requires Alchemy (1)"),
    ("L16", "doc", "has", "maximum potential skill of"),
    ("L17", "doc", "has", "Learn Skill Step"),
    ("L18", "doc", "has", "Treatise on the Alchemy of Draenor"),
    ("L19", "doc", "has", "Triggered by"),
    ("L20", "doc", "has", "Legion Alchemist 201697"),
    ("L21", "doc", "has", "Get Your Mix On 39325"),
    ("L22", "doc", "has", "Testing the Calibration 39346"),
    ("L23", "doc", "has", "Mixology"),

    # --- trainers and positions ---
    ("T01", "doc", "has", "Clever Kumali creature 122703"),
    ("T02", "doc", "has", "/way 42.2 38.0"),
    ("T03", "doc", "has", "Terrace of Crafters"),
    ("T04", "doc", "has", "Elric Whalgrene creature 132228"),
    ("T05", "doc", "has", "/way 74.2 6.6"),
    ("T06", "doc", "has", "Tradewinds Market"),
    ("T07", "doc", "has", "Narv creature 154393"),
    ("T08", "doc", "has", "Okanu creature 153811"),
    ("T09", "doc", "regex", (r"map id\s+1718", 1)),
    ("T10", "doc", "has", "does not teach Northrend"),
    ("T11", "doc", "has", "TWO Linzy Blackbolts exist"),
    ("T12", "doc", "has", "Boralus (zone 8568)"),
    ("T13", "doc", "has", "Dazar'alor (wowhead zone 8670)"),
    ("T14", "doc", "has", "zone 4395"),
    ("T15", "doc", "has", "zone 7502"),
    ("T16", "doc", "has", "zone 6138"),
    ("T17", "doc", "regex", (r"zone\s+5785", 1)),
    ("T18", "doc", "has", "Yelmak 3347 (Orgrimmar)"),
    ("T19", "doc", "has", "Camberon 16642 (Silvermoon City)"),
    ("T20", "doc", "has", "Patricia Egan 92457"),
    ("T21", "doc", "has", "limited supply"),
    ("T22", "doc", "has", "18-20 min"),
    ("T23", "doc", "regex", (r"^\s+- (Horde|Alliance): ", 2)),

    # --- routes: named anchors per expansion ---
    ("R01", "doc", "has", "3.1 Classic 1-300"),
    ("R02", "doc", "has", "3.2 Outland 1-75"),
    ("R03", "doc", "has", "3.3 Northrend 1-75"),
    ("R04", "doc", "has", "3.4 Cataclysm 1-75"),
    ("R05", "doc", "has", "3.5 Pandaria 1-75 (DISCOVERY-BASED"),
    ("R06", "doc", "has", "3.6 Draenor 1-100"),
    ("R07", "doc", "has", "3.7 Legion 1-100"),
    ("R08", "doc", "has", "3.8 Battle for Azeroth 1-175"),
    ("R09", "doc", "has", "Purification Potion"),
    ("R10", "doc", "has", "Major Dreamless Sleep Potion"),
    ("R11", "doc", "has", "Flask of Stoneblood"),
    ("R12", "doc", "has", "Transmute: Amberjewel"),
    ("R13", "doc", "has", "Master Healing Potion"),
    ("R14", "doc", "has", "Draenic Mana Potion"),
    ("R15", "doc", "has", "Flask of the Whispered Pact"),
    ("R16", "doc", "has", "Abyssal Healing Potion"),
    ("R17", "doc", "has", "Coastal Rejuvenation Potion"),
    ("R18", "doc", "regex", (r"Battle Potion of\s+Strength", 1)),
    ("R19", "doc", "regex", (r"Flask of the\s+Vast Horizon", 1)),
    ("R20", "doc", "has", "Elixir of Mighty Agility"),
    ("R21", "doc", "has", "Mythical Healing Potion"),
    ("R23", "doc", "regex", (r"chance to learn\s+additional recipes", 1)),
    ("R24", "doc", "has", "Philosopher's Stone"),
    ("R25", "doc", "has", "Rank 3"),
    ("R26", "doc", "has", "reputation vendors"),
    ("R27", "doc", "has", "Shopping list"),
    ("R28", "doc", "has", "Green for the last"),
    ("R29", "doc", "has", "expect extras"),

    # --- materials ---
    ("M01", "doc", "has", "Crystal Vial 3371"),
    ("M02", "doc", "has", "vanilla 2330, Outland 28555, Northrend 53837, Cataclysm 80494,"),
    ("M03", "doc", "has", "never include vials"),
    ("M04", "doc", "has", "Alchemy Supplies"),
    ("M05", "doc", "has", "Stormsong Valley, Drustvar"),
    ("M06", "doc", "has", "Vol'dun, Nazmir"),
    ("M07", "doc", "has", "Val'sharah/Dreamleaf"),
    ("M08", "doc", "has", "Klaxxi'vess"),
    ("M09", "doc", "regex", (r"Sand Shifter \(BfA\s+Demitri's - item id unverified", 1)),
    ("M10", "doc", "has", "Pygmy Suckerfish 40199"),
    ("M11", "doc", "has", "Crescent Saberfish Flesh 109137"),
    ("M12", "doc", "has", "Auction House dependency"),
    ("M13", "doc", "regex", (r"Gather_Herbalism\.txt", 4)),
    ("M14", "doc", "has", "Blood of Sargeras 124124"),
    ("M15", "doc", "has", "Volatile Life 52329"),

    # --- costs ---
    ("C01", "doc", "regex", (r"Training cost: 10", 2)),
    ("C02", "doc", "has", "Training cost 7750"),
    ("C03", "doc", "has", "Training cost 130"),
    ("C04", "doc", "regex", (r"Cost: 130", 2)),
    ("C05", "doc", "has", "Cost: 9"),
    ("C06", "doc", "has", "Cost: 5"),
    ("C07", "doc", "regex", (r"50 gold", 2)),
    ("C08", "doc", "has", "MoneyCost"),
    ("C09", "doc", "has", "GetReputationPriceDiscount"),
    ("C10", "doc", "has", "NotEnoughMoney"),

    # --- level needed ---
    ("G01", "doc", "has", "ReqSkillLine"),
    ("G02", "doc", "regex", (r"ReqLevel", 2)),
    ("G03", "doc", "has", "ReqAbility"),
    ("G04", "doc", "regex", (r"FREE\s+primary profession point", 1)),
    ("G05", "doc", "has", "only two primary professions"),
    ("G06", "doc", "has", "CHARACTER LEVEL 115"),
    ("G07", "doc", "regex", (r"requires level 10", 1)),
    ("G08", "doc", "has", "level 45"),
    ("G09", "doc", "has", "Journeyman/Expert"),
    ("G10", "doc", "has", "unverified-negative"),
    ("G11", "doc", "has", "level shown on the spell pages"),

    # --- core: what the server must do ---
    ("K01", "doc", "has", "TakeReagents"),
    ("K02", "doc", "has", "DestroyItemCount"),
    ("K03", "doc", "has", "before HandleEffects"),
    ("K04", "doc", "has", "EQUIP_ERR_INV_FULL"),
    ("K05", "doc", "has", "SPELL_EFFECT_CREATE_ITEM"),
    ("K06", "doc", "has", "Trade_Skill"),
    ("K07", "doc", "has", "UpdateCraftSkill"),
    ("K08", "doc", "has", "SPELL_ATTR1_NO_SKILL_INCREASE"),
    ("K09", "doc", "has", "SkillupSkillLineID"),
    ("K10", "doc", "has", "NumSkillUps"),
    ("K11", "doc", "has", "CONFIG_SKILL_GAIN_CRAFTING"),
    ("K12", "doc", "has", "SkillGainChance"),
    ("K13", "doc", "has", "TrivialSkillLineRankHigh"),
    ("K14", "doc", "has", "UpdateSkillPro"),
    ("K15", "doc", "has", "MECHANIC_DISCOVERY"),
    ("K16", "doc", "has", "GetSkillDiscoverySpell"),
    ("K17", "doc", "has", "Alchemy Discoveries here"),
    ("K18", "doc", "has", "GameObjectFocusCheck"),
    ("K19", "doc", "has", "SPELL_AURA_PROVIDE_SPELL_FOCUS"),
    ("K20", "doc", "has", "SPELL_FAILED_MIN_SKILL"),
    ("K21", "doc", "has", "CMSG_TRAINER_BUY_SPELL"),
    ("K22", "doc", "has", "PlayerInteractionType::Trainer"),
    ("K23", "doc", "has", "TeachSpell"),
    ("K24", "doc", "has", "IsCastable"),
    ("K25", "doc", "has", "CanTeachSpell passes"),
    ("K26", "doc", "has", "LearnSpell directly"),
    ("K27", "doc", "regex", (r"2 seconds", 1)),
    ("K28", "doc", "has", "Mechanic: Discovery"),
    ("K29", "doc", "regex", (r"No longer requires the Dalaran Alchemy\s+Station", 1)),
    ("K30", "doc", "has", "created anywhere"),
    ("K31", "doc", "has", "daily at midnight"),
    ("K32", "doc", "has", "IsInteractingWith"),
    ("K33", "doc", "has", "UNIT_NPC_FLAG_TRAINER"),

    # --- cannot do ---
    ("N01", "doc", "has", "Cannot see the profession window"),
    ("N02", "doc", "has", "Cannot learn a spell \"by opening the trainer\""),
    ("N03", "doc", "has", "Cannot run quests the normal way"),
    ("N04", "doc", "has", "Cannot reliably farm reputation- or dungeon-gated recipes"),
    ("N05", "doc", "has", "Cannot predict randomness"),
    ("N06", "doc", "has", "Cannot buy out of the shopping list"),
    ("N07", "doc", "has", "Cannot bypass cooldowns"),
    ("N08", "doc", "has", "full bag and silently lose reagents"),
    ("N09", "doc", "has", "dungeon automation"),
    ("N10", "doc", "has", "vendor-purchase packets"),

    # --- conflicts and unverified ---
    ("U01", "doc", "regex", (r"1-175", 2)),
    ("U02", "doc", "regex", (r"1-150", 2)),
    ("U03", "doc", "has", "150-vs-175"),
    ("U04", "doc", "has", "5 vs 15"),
    ("U05", "doc", "has", "NOT decoded"),
    ("U06", "doc", "has", "labels are inconsistent"),
    ("U07", "doc", "has", "middle id by id order"),
    ("U08", "doc", "has", "currency unit is not"),
    ("U09", "doc", "regex", (r"unverified\s+for this one spell", 1)),
    ("U10", "doc", "has", "unverified-negative"),

    # --- sources ---
    ("V01", "doc", "has", "zandalari-kul-tiran-bfa-alchemy-leveling-guide"),
    ("V02", "doc", "has", "wow-professions.com"),
    ("V03", "doc", "has", "warcraft.wiki.gg/wiki/Alchemy"),
    ("V04", "doc", "has", "SpellEffects"),
    ("V05", "doc", "has", "NPCHandler.cpp"),
    ("V06", "doc", "has", "Trainer.cpp"),
    ("V07", "doc", "has", "6139"),
    ("V08", "doc", "has", "spells=11.171"),
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

    # derived sets: word-boundary id presence
    def all_ids(ids):
        return all(re.search(r"\b%s\b" % re.escape(i), docs["doc"]) for i in ids)

    mark("X01-learn-ids", all_ids(LEARN_IDS))
    mark("X02-line-ids", all_ids(LINE_IDS))
    mark("X03-trainer-ids", all_ids(TRAINER_IDS))
    mark("X04-route-ids", all_ids(ROUTE_IDS))
    mark("X05-herb-ids", all_ids(HERB_IDS))
    # X06 plain-text hygiene
    ok = (all(ord(c) < 128 for c in docs["doc"])
          and "\t" not in docs["doc"]
          and max(len(l) for l in docs["doc"].splitlines()) <= 140)
    mark("X06-ascii-lines", ok)
    # X07 BfA cap consistency: table row 175 + both prose caps
    ok = bool(re.search(r"2478\s+Kul Tiran / Zandalari Alchemy\s+175",
                        docs["doc"])) \
        and "1-175" in docs["doc"] and "1-150" in docs["doc"] \
        and "150-vs-175" in docs["doc"]
    mark("X07-bfa-cap", ok)
    # X08 craft markers
    mark("X08-craft-counts", len(re.findall(r"\d+ crafts", docs["doc"])) >= 40)
    # X09 vial logic held together
    ok = ("Crystal Vial 3371" in docs["doc"]
          and "never include vials" in docs["doc"]
          and "vanilla 2330, Outland 28555" in docs["doc"])
    mark("X09-vial-logic", ok)
    # X10 guide slugs (prefix-extension safe: each is checked as a literal
    # and mutated globally)
    mark("X10-guide-slugs", all(g in docs["doc"] for g in GUIDE_SLUGS))
    # X11 core symbols
    core = ["TakeReagents", "UpdateCraftSkill", "MECHANIC_DISCOVERY",
            "GetSkillDiscoverySpell", "CMSG_TRAINER_BUY_SPELL",
            "PlayerInteractionType::Trainer", "SPELL_FAILED_MIN_SKILL",
            "GameObjectFocusCheck"]
    mark("X11-core-symbols", all(s in docs["doc"] for s in core))
    # X12 creature-id completeness against guides' named set (subset already
    # in X03); here: bfa + nazjatar + reputation vendors all with names
    pairs = ["122703", "132228", "154393", "153811", "131287", "135800"]
    mark("X12-named-vendors", all(
        re.search(r"\b%s\b" % p, docs["doc"]) for p in pairs))

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

    # derived probes (each falsified at ALL occurrences, non-superstring)
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("264212", "998877")
    expect_fail(docs, "X01:learn spell falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("2483", "997766")
    expect_fail(docs, "X02:line id falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("122703", "996655")
    expect_fail(docs, "X03:trainer id falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("301311", "399311")
    expect_fail(docs, "X04:route spell id falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("152509", "159509")
    expect_fail(docs, "X05:herb id falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"] + "\narrow \u2192 here"
    expect_fail(docs, "X06:non-ascii injected")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("150-vs-175", "150-vs-999")
    expect_fail(docs, "X07:cap caveat falsified")
    docs = dict(base)
    docs["doc"] = re.sub(r"\d+ crafts", "NN shapes", docs["doc"])
    expect_fail(docs, "X08:craft markers falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("never include vials",
                                      "often include vials")
    expect_fail(docs, "X09:vial rule falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("zandalari-kul-tiran-bfa",
                                      "zandalari-kul-tiran-old")
    expect_fail(docs, "X10:guide slug removed")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("Alchemy Discoveries here",
                                      "Alchemy findings here")
    expect_fail(docs, "X11:core symbol falsified")
    docs = dict(base)
    docs["p4"] = docs["p4"].replace("Craft_Alchemy.txt", "Craft_Alcemy.txt")
    expect_fail(docs, "S16:prompt deliverable name falsified")
    docs = dict(base)
    docs["rm"] = docs["rm"].replace("Craft_Alchemy.txt", "Craft_Alcemy.txt")
    expect_fail(docs, "S19:master deliverable name falsified")

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
    print("Craft_Alchemy audit: %d PASS, %d FAIL" % (len(passed), len(failed)))
    if failed:
        print("FAILED:", ", ".join(failed))
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
