#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit for Companion_Professions step 5 (PART 14, STEP 127): Craft_Blacksmithing.txt.

Checks (statics):
  * structure: ten sections, the prompt's deliverable name, RESEARCH_MASTER
    STEP 127 lines, plain-text hygiene, the eight 3.x route blocks
  * skill lines 164/2477..2437 with caps, expansion learn spells and
    wrappers, Requires Blacksmithing (1), the 8.0.1 rank merge, the Draenor
    scroll chain and the Legion quest chain, the faction pairing
  * trainers: every creature entry quoted from the guides, spell pages and
    wiki tables, the two BfA /way coordinates, the twin-Alard warning,
    wiki coordinates for Outland/Northrend/Pandaria/Classic
  * routes: all recipe spell ids per expansion (as one derived set plus the
    named anchor recipes), craft markers, colour warnings quoted from guides,
    the Firmament Stone station and the Mark of Honor gates
  * materials: ore/bar/stone ids per expansion, the smelt spells from own
    Gather_Mining.txt, fluxes, Expulsom, the unverified hammer item id
  * costs: learn-spell Training cost 10/5 lines, recipe cost sample 10, the
    50-gold conflict, reputation discount functions and wiki numbers
  * level needed: ReqLevel/ReqSkillLine/ReqAbility, free primary profession
    point, the 5/10 wiki minimums, the 9.0.1 level-10 note, Legion quest 10,
    Draenor level 90
  * core rules: TakeReagents before HandleEffects, full-bag path,
    EffectCreateItem, UpdateCraftSkill and SkillChance maths, MECHANIC_
    DISCOVERY branch, GameObjectFocusCheck/RequiresSpellFocus anvil
    enforcement, trainer interaction flow
  * cannot-do: nine "- Cannot" bullets, interaction guard, full-bag loss,
    twin Alard trap, daily cooldown, Mark of Honor PvP
  * conflicts: 10-vs-50 gold, cost units, classic rank spells, Legion reward
    ids, BfA route divergence, difficulty strings not decoded, guide vintage
  * sources: eight guide slugs, TC files, wiki pages, own Gather_Mining and
    Craft_Alchemy files

Derived: learn-spell set, line-id set, creature-id set, full route spell-id
set, material id set, craft-count markers, station/anvil logic, ASCII/line
hygiene.

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
    "doc": "Craft_Blacksmithing.txt",
    "p5": "05_Blacksmithing.txt",
    "rm": os.path.join("..", "RESEARCH_MASTER.txt"),
}

# --- id sets (all must appear in the deliverable, word-boundary checked) ---
LEARN_IDS = [
    "2018", "3100", "195097", "201699",
    "264434", "264435", "264436", "264437", "264438", "264439",
    "264440", "264441", "264442", "264443", "264444", "264445",
    "264446", "264447", "264448", "265803",
]

LINE_IDS = ["164", "2477", "2476", "2475", "2474", "2473", "2472", "2454", "2437"]

TRAINER_IDS = [
    # bfa + nazjatar + mark vendors
    "133536", "127112", "154321", "153817", "142552", "142564",
    "154652", "154653",
    # classic / cata taught-by sample
    "1241", "514", "5511", "11178", "3355", "4596",
    # outland taught-by + route vendors
    "33631", "33609", "21209", "20124", "33675", "20125",
    "19662", "16583", "19373", "17904", "19331", "19321",
    # northrend taught-by + wiki rows
    "28694", "26988", "29924", "26981", "29505", "29506", "26904",
    # pandaria taught-by + vendors
    "64085", "64058", "65114", "65129",
    # draenor scroll + traders
    "87062", "87550", "90894", "91030",
    # legion trainer + rank sources + quest drops
    "92183", "92265", "92243", "107760", "75043", "74254",
    # classic plan vendors / dungeon drops
    "8176", "8161", "17975", "18497",
    # stormsteel reputation vendors
    "135447", "135446",
]

ROUTE_IDS = [
    # classic
    "2660", "2665", "3326", "2666", "19666", "2668", "3328", "3337",
    "2672", "19667", "9918", "9928", "9937", "9931", "9964", "9961",
    "16641", "16644", "16649", "16652", "16653",
    # outland
    "34607", "29547", "29552", "29548", "32284", "29568", "29728",
    "34608", "29608", "29610", "29616", "29619", "29649",
    # northrend
    "55835", "55204", "55301", "55303",
    # cataclysm
    "76178", "76262", "76264", "76265", "76438", "76266", "76267",
    "76441", "76261", "76442", "76458", "76467", "76459", "76468",
    # pandaria
    "122633", "122579", "122577", "122636", "122576",
    # draenor
    "176090", "173355", "171699", "182116",
    # legion
    "184442", "182983", "182945",
    # bfa
    "253183", "253165", "253180", "253174", "253162", "269064",
    "269451", "269424", "269444", "253190", "253186",
    "294763", "294764", "294765", "286015", "286016", "283238",
    "253158",
]

MATERIAL_IDS = [
    # classic stones/bars/dyes
    "2835", "2836", "2838", "7912", "12365", "2840", "2841", "2842",
    "3575", "3859", "3857", "3860", "12359", "2605", "4338", "8170",
    "7910",
    # outland
    "23424", "23427", "23425", "23445", "23446", "23447", "23448",
    "23573", "21877", "22445", "22449", "21884", "21885", "21886",
    "22452", "30810", "29739", "30809", "29740",
    # northrend
    "36916", "36913", "41163", "37700", "35623", "35624", "49252",
    "49258",
    # cataclysm
    "54849", "52186", "53039", "52327", "52325", "52326", "74537",
    # pandaria
    "72096", "76061", "89112",
    # draenor
    "109118", "109119", "120945",
    # legion
    "123918", "123919", "124124",
    # bfa
    "152512", "152579", "152513", "168185", "152668", "160298",
    "18567", "137642",
    # misc
    "1149", "72093",
]

GUIDE_SLUGS = [
    "vanilla-blacksmithing-leveling",
    "outland-blacksmithing-leveling",
    "northrend-blacksmithing-leveling",
    "cataclysm-blacksmithing-leveling",
    "pandaria-blacksmithing-leveling",
    "draenor-blacksmithing-leveling",
    "legion-blacksmithing-leveling",
    "zandalari-kul-tiran-bfa-blacksmithing-leveling-guide",
]

CHECKS = [
    # --- structure ---
    ("S01", "doc", "has", "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - BLACKSMITHING CRAFTING FOR A SERVER-SIDE COMPANION"),
    ("S02", "doc", "has", "1. THE SKILL LINES AND HOW A COMPANION LEARNS THEM"),
    ("S03", "doc", "has", "2. TRAINERS AND THEIR POSITIONS"),
    ("S04", "doc", "has", "3. CHEAPEST ROUTE 1 TO THE CAP OF EACH LINE"),
    ("S05", "doc", "has", "4. MATERIALS AND WHERE EACH COMES FROM"),
    ("S06", "doc", "has", "5. TRAINER COSTS"),
    ("S07", "doc", "has", "6. LEVEL NEEDED"),
    ("S08", "doc", "has", "7. WHAT THE CORE MUST DO FOR A CRAFT TO SUCCEED"),
    ("S09", "doc", "has", "8. WHAT A SERVER-SIDE CHARACTER (NO CLIENT) CANNOT DO"),
    ("S10", "doc", "has", "9. CONFLICTS AND UNVERIFIED INDEX"),
    ("S11", "doc", "has", "10. SOURCES"),
    ("S12", "doc", "absent", "\t"),
    ("S13", "doc", "regex", (r"^- Cannot ", 7)),
    ("S14", "doc", "regex", (r"unverified", 20)),
    ("S15", "doc", "regex", (r"^3\.[1-8] ", 8)),
    ("S16", "p5", "has", "WHAT TO DELIVER - ONE TEXT FILE, Craft_Blacksmithing.txt"),
    ("S17", "p5", "has", "Do only this step"),
    ("S18", "rm", "has", "--- STEP 127"),
    ("S19", "rm", "has", "Deliver ONE text file named: Craft_Blacksmithing.txt"),
    ("S20", "rm", "has", "PROFESSIONS FOR THE COMPANION BOTS (15 steps)"),

    # --- skill lines and learn spells ---
    ("L01", "doc", "regex", (r"2477\s+Classic Blacksmithing", 1)),
    ("L02", "doc", "regex", (r"2476\s+Outland Blacksmithing", 1)),
    ("L03", "doc", "regex", (r"2475\s+Northrend Blacksmithing", 1)),
    ("L04", "doc", "regex", (r"2474\s+Cataclysm Blacksmithing", 1)),
    ("L05", "doc", "regex", (r"2473\s+Pandaria Blacksmithing", 1)),
    ("L06", "doc", "regex", (r"2472\s+Draenor Blacksmithing", 1)),
    ("L07", "doc", "regex", (r"2454\s+Legion Blacksmithing", 1)),
    ("L08", "doc", "regex", (r"2437\s+Kul Tiran / Zandalari", 1)),
    ("L09", "doc", "regex", (r"164\s+Blacksmithing \(base\)", 1)),
    ("L10", "doc", "has", "264435 (8.0.1)"),
    ("L11", "doc", "has", "264448 Alliance (8.0.1)"),
    ("L12", "doc", "has", "265803 Horde (8.1.0)"),
    ("L13", "doc", "has", "wrapper 264437"),
    ("L14", "doc", "has", "wrapper 264439"),
    ("L15", "doc", "has", "Requires Blacksmithing (1)"),
    ("L16", "doc", "has", "maximum potential skill of"),
    ("L17", "doc", "has", "Learn Skill Step"),
    ("L18", "doc", "has", "scroll item 115356"),
    ("L19", "doc", "has", "Triggered by (1)"),
    ("L20", "doc", "has", "Strange New Ores 38499"),
    ("L21", "doc", "has", "201699"),
    ("L22", "doc", "has", "195097"),
    ("L23", "doc", "has", "Other ranks (9)"),
    ("L24", "doc", "has", "now just \"Classic\""),
    ("L25", "doc", "has", "264444 (8.0.1)"),
    ("L26", "doc", "has", "Tribal Knowledge 38533"),
    ("L27", "doc", "has", "Haephest's Satchel"),
    ("L28", "doc", "has", "Fractured Forge Hammer"),
    ("L29", "doc", "has", "264445"),
    ("L30", "doc", "regex", (r"9\.0\.1\s+\(2020-10-13\)", 1)),

    # --- trainers and positions ---
    ("T01", "doc", "has", "Grix \"Ironfists\" Barlow creature 133536"),
    ("T02", "doc", "has", "/way 73.4 8.4"),
    ("T03", "doc", "has", "Tradewinds Market"),
    ("T04", "doc", "has", "Forgemaster Zak'aal creature 127112"),
    ("T05", "doc", "has", "/way 43.6 38.6"),
    ("T06", "doc", "has", "Terrace of Crafters"),
    ("T07", "doc", "has", "Jada creature 154321"),
    ("T08", "doc", "has", "Instructor Alikana creature 153817"),
    ("T09", "doc", "has", "won't teach you Northrend recipes"),
    ("T10", "doc", "has", "TWO Alard Schmieds"),
    ("T11", "doc", "has", "creature 92183"),
    ("T12", "doc", "has", "creature 28694"),
    ("T13", "doc", "has", "[45.5, 28.0]"),
    ("T14", "doc", "has", "[69.2, 44.8]"),
    ("T15", "doc", "has", "[52.4, 50.0]"),
    ("T16", "doc", "has", "[48.4, 36.9]"),
    ("T17", "doc", "has", "[21.6, 72.2]"),
    ("T18", "doc", "has", "Zula Slagfury creature 20125"),
    ("T19", "doc", "has", "Len the Hammer creature 65114"),
    ("T20", "doc", "has", "Zen Master Lao creature 65129"),
    ("T21", "doc", "has", "Royce Bigbeard creature 87062"),
    ("T22", "doc", "has", "Nonn Threeratchet creature 87550"),
    ("T23", "doc", "has", "Ozgrom Ragefang creature 142552"),
    ("T24", "doc", "has", "Leedan Gustaf creature 142564"),
    ("T25", "doc", "has", "Tognus Flintfire creature 1241"),
    ("T26", "doc", "regex", (r"Quartermaster\s+Enuril\s+creature 19331", 1)),
    ("T27", "doc", "has", "Urael creature 92265"),
    ("T28", "doc", "has", "Muirn Ironhorn creature 92243"),
    ("T29", "doc", "regex", (r"Strap Bucklebolt\s+creature 107760", 1)),
    ("T30", "doc", "has", "Aaron Hollman creature 19662"),
    ("T31", "doc", "has", "limited supply"),
    ("T32", "doc", "has", "30-60 minute"),
    ("T33", "doc", "has", "15-60 min"),
    ("T34", "doc", "regex", (r"/way \d", 2)),
    ("T35", "doc", "has", "Boralus (zone 8568)"),
    ("T36", "doc", "regex", (r"zone\s+8670", 1)),
    ("T37", "doc", "has", "zone 4395"),
    ("T38", "doc", "has", "wowhead 10052"),
    ("T39", "doc", "has", "no Draenor\nsection"),
    ("T40", "doc", "has", "no Broken Isles section"),

    # --- routes: named anchors per expansion ---
    ("R01", "doc", "has", "3.1 Classic 1-300"),
    ("R02", "doc", "has", "3.2 Outland 1-75"),
    ("R03", "doc", "has", "3.3 Northrend 1-75"),
    ("R04", "doc", "has", "3.4 Cataclysm 1-75"),
    ("R05", "doc", "has", "3.5 Pandaria 1-75"),
    ("R06", "doc", "has", "3.6 Draenor 1-100"),
    ("R07", "doc", "has", "3.7 Legion 1-100"),
    ("R08", "doc", "has", "3.8 Battle for Azeroth 1-175"),
    ("R09", "doc", "has", "Rough Sharpening Stone"),
    ("R10", "doc", "has", "Felsteel Gloves"),
    ("R11", "doc", "has", "Daunting Legplates"),
    ("R12", "doc", "has", "Hardened Obsidium Breastplate"),
    ("R13", "doc", "has", "Contender's Revenant Bracers"),
    ("R14", "doc", "has", "Truesteel Reshaper"),
    ("R15", "doc", "has", "Demonsteel Waistguard"),
    ("R16", "doc", "has", "Monel-Hardened Armguards"),
    ("R17", "doc", "has", "Notorious Combatant's Plate Armguards"),
    ("R18", "doc", "has", "Firmament Stone"),
    ("R19", "doc", "has", "Mark of Honor"),
    ("R20", "doc", "has", "Shopping list totals"),
    ("R21", "doc", "has", "Yellow for the last 5 points"),
    ("R22", "doc", "has", "green last 3 points"),
    ("R23", "doc", "has", "yellow at 10"),
    ("R24", "doc", "has", "extras"),
    ("R25", "doc", "has", "Rank 2/3"),
    ("R26", "doc", "has", "Hoofplates"),
    ("R27", "doc", "has", "Tools of the Trade"),
    ("R28", "doc", "has", "Khaz'gorian Smithing Hammer"),
    ("R29", "doc", "has", "three ways"),
    ("R30", "doc", "has", "Revered"),

    # --- materials ---
    ("M01", "doc", "has", "Coal 3857"),
    ("M02", "doc", "has", "Green Dye 2605"),
    ("M03", "doc", "has", "Smelt Cobalt spell 49252"),
    ("M04", "doc", "has", "49258"),
    ("M05", "doc", "has", "lines 189-192"),
    ("M06", "doc", "has", "Blacksmith Hammer"),
    ("M07", "doc", "has", "its item id was not read"),
    ("M08", "doc", "regex", (r"(?i)auction house", 2)),
    ("M09", "doc", "regex", (r"Gather_Mining\.txt", 2)),
    ("M10", "doc", "has", "Blood of Sargeras 124124"),
    ("M11", "doc", "has", "Durable Flux 160298"),
    ("M12", "doc", "has", "Elemental Flux 18567"),
    ("M13", "doc", "has", "Expulsom 152668"),
    ("M14", "doc", "has", "smelting is Mining"),
    ("M15", "doc", "has", "Mark of Sargeras 30809"),
    ("M16", "doc", "has", "Kyparite 72093"),

    # --- costs ---
    ("C01", "doc", "regex", (r"Training cost: 10", 2)),
    ("C02", "doc", "has", "Training cost: 5"),
    ("C03", "doc", "regex", (r"50 gold", 2)),
    ("C04", "doc", "has", "MoneyCost"),
    ("C05", "doc", "has", "GetReputationPriceDiscount"),
    ("C06", "doc", "has", "NotEnoughMoney"),
    ("C07", "doc", "has", "SendTeachFailure"),
    ("C08", "doc", "has", "Cost: 10"),
    ("C09", "doc", "has", "2s50c"),
    ("C10", "doc", "has", "9 copper"),
    ("C11", "doc", "has", "currency unit is not printed"),

    # --- level needed ---
    ("G01", "doc", "has", "ReqSkillLine"),
    ("G02", "doc", "regex", (r"ReqLevel", 2)),
    ("G03", "doc", "has", "ReqAbility"),
    ("G04", "doc", "regex", (r"free\s+primary profession point", 1)),
    ("G05", "doc", "has", "two primary professions"),
    ("G06", "doc", "has", "min level 5"),
    ("G07", "doc", "has", "min level 10"),
    ("G08", "doc", "has", "Level 10, Requires 10"),
    ("G09", "doc", "has", "Requires Level 90"),
    ("G10", "doc", "regex", (r"9\.0\.1", 2)),
    ("G11", "doc", "regex", (r"no character\s+level", 1)),
    ("G12", "doc", "has", "level 45"),
    ("G13", "doc", "has", "per-spell ReqLevel"),
    ("G14", "doc", "has", "GetBaseSkillValue"),

    # --- core: what the server must do ---
    ("K01", "doc", "has", "TakeReagents"),
    ("K02", "doc", "has", "DestroyItemCount"),
    ("K03", "doc", "regex", (r"before\s+HandleEffects", 1)),
    ("K04", "doc", "has", "EQUIP_ERR_INV_FULL"),
    ("K05", "doc", "has", "EQUIP_ERR_ITEM_MAX_COUNT"),
    ("K06", "doc", "has", "SPELL_EFFECT_CREATE_ITEM"),
    ("K07", "doc", "has", "ItemContext::Trade_Skill"),
    ("K08", "doc", "has", "UpdateCraftSkill"),
    ("K09", "doc", "has", "SkillupSkillLineID"),
    ("K10", "doc", "has", "NumSkillUps x CONFIG_SKILL_GAIN_CRAFTING"),
    ("K11", "doc", "has", "SkillGainChance"),
    ("K12", "doc", "has", "TrivialSkillLineRankHigh"),
    ("K13", "doc", "has", "UpdateSkillPro"),
    ("K14", "doc", "has", "MECHANIC_DISCOVERY"),
    ("K15", "doc", "has", "GetSkillDiscoverySpell"),
    ("K16", "doc", "has", "Alchemy Discoveries here"),
    ("K17", "doc", "has", "GameObjectFocusCheck"),
    ("K18", "doc", "has", "RequiresSpellFocus"),
    ("K19", "doc", "has", "SPELL_FAILED_MIN_SKILL"),
    ("K20", "doc", "has", "CMSG_TRAINER_BUY_SPELL"),
    ("K21", "doc", "has", "PlayerInteractionType::Trainer"),
    ("K22", "doc", "has", "TeachSpell"),
    ("K23", "doc", "has", "CanTeachSpell"),
    ("K24", "doc", "has", "IsInteractingWith"),
    ("K25", "doc", "has", "StartInteraction"),
    ("K26", "doc", "has", "HandleTrainerBuySpellOpcode"),
    ("K27", "doc", "regex", (r"Cast time: 2 seconds", 1)),
    ("K28", "doc", "has", "Mechanic n/a"),
    ("K29", "doc", "regex", (r"Rough Sharpening Stone,\s+for example", 1)),
    ("K30", "doc", "regex", (r"created\s+anywhere", 1)),
    ("K31", "doc", "has", "Requires Anvil"),
    ("K32", "doc", "has", "blacksmith hammer and anvil"),
    ("K33", "doc", "has", "ITEM_SUBCLASS_PROFESSION_BLACKSMITHING"),
    ("K34", "doc", "has", "FindGameObjectFocus"),
    ("K35", "doc", "has", "line 5410"),
    ("K36", "doc", "has", "line 5599"),
    ("K37", "doc", "has", "line 2321"),
    ("K38", "doc", "has", "line 130"),

    # --- cannot do ---
    ("N01", "doc", "has", "Cannot see the profession window"),
    ("N02", "doc", "has", "Cannot learn a spell \"by opening the trainer\""),
    ("N03", "doc", "has", "Cannot run quests the normal way"),
    ("N04", "doc", "has", "Cannot reliably farm reputation- or dungeon-gated recipes"),
    ("N05", "doc", "has", "Cannot predict randomness"),
    ("N06", "doc", "has", "Cannot buy out of the shopping list"),
    ("N07", "doc", "has", "Cannot bypass"),
    ("N08", "doc", "has", "Cannot get Mark of Honor without PvP"),
    ("N09", "doc", "has", "Cannot craft \"anywhere\""),
    ("N10", "doc", "has", "full bag and silently lose reagents"),
    ("N11", "doc", "has", "dungeon automation"),
    ("N12", "doc", "has", "vendor-purchase packets"),
    ("N13", "doc", "has", "Wrong twin"),
    ("N14", "doc", "has", "interaction guard"),

    # --- conflicts and unverified ---
    ("U01", "doc", "has", "sources disagree"),
    ("U02", "doc", "has", "BfA route divergence"),
    ("U03", "doc", "has", "current-retail pages"),
    ("U04", "doc", "has", "quoted raw"),
    ("U05", "doc", "has", "NOT decoded"),
    ("U06", "doc", "has", "post-dates 8.3.7"),
    ("U07", "doc", "has", "still offers them"),
    ("U08", "doc", "has", "your server grants"),
    ("U09", "doc", "regex", (r"whether ANY blacksmithing spell carries it is\s+unverified", 1)),
    ("U10", "doc", "has", "the per-line 8.3.7 values were not read"),

    # --- sources ---
    ("V01", "doc", "has", "6278"),
    ("V02", "doc", "has", "warcraft.wiki.gg"),
    ("V03", "doc", "has", "wowpedia"),
    ("V04", "doc", "has", "SpellEffects.cpp"),
    ("V05", "doc", "has", "NPCHandler.cpp"),
    ("V06", "doc", "has", "Trainer.cpp"),
    ("V07", "doc", "has", "Gather_Mining.txt"),
    ("V08", "doc", "has", "Craft_Alchemy.txt"),
    ("V09", "doc", "has", "gh api"),
    ("V10", "doc", "has", "wowhead.com/spell=264438"),
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
    mark("X05-material-ids", all_ids(MATERIAL_IDS))
    # X06 plain-text hygiene
    ok = (all(ord(c) < 128 for c in docs["doc"])
          and "\t" not in docs["doc"]
          and max(len(l) for l in docs["doc"].splitlines()) <= 140)
    mark("X06-ascii-lines", ok)
    # X07 BfA cap consistency: table row 175 (row wraps - use \s+) + prose
    ok = bool(re.search(r"2437\s+Kul Tiran / Zandalari\s+Blacksmithing\s+175",
                        docs["doc"])) and "skill of 175" in docs["doc"]
    mark("X07-bfa-cap", ok)
    # X08 craft markers
    mark("X08-craft-counts", len(re.findall(r"\d+ crafts", docs["doc"])) >= 40)
    # X09 anvil/station/anywhere logic held together
    ok = ("Requires Anvil" in docs["doc"]
          and "Firmament Stone" in docs["doc"]
          and re.search(r"created\s+anywhere", docs["doc"])
          and "blacksmith hammer and anvil" in docs["doc"])
    mark("X09-anvil-station", ok)
    # X10 guide slugs (each checked as a literal, mutated globally)
    mark("X10-guide-slugs", all(g in docs["doc"] for g in GUIDE_SLUGS))
    # X11 core symbols
    core = ["TakeReagents", "UpdateCraftSkill", "MECHANIC_DISCOVERY",
            "GetSkillDiscoverySpell", "CMSG_TRAINER_BUY_SPELL",
            "PlayerInteractionType::Trainer", "SPELL_FAILED_MIN_SKILL",
            "GameObjectFocusCheck", "RequiresSpellFocus"]
    mark("X11-core-symbols", all(s in docs["doc"] for s in core))
    # X12 named vendors: faction trainers + scroll + mark vendors
    pairs = ["133536", "127112", "154321", "87062", "87550", "142552",
             "142564"]
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
    docs["doc"] = docs["doc"].replace("264435", "998877")
    expect_fail(docs, "X01:learn spell falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("2475", "997766")
    expect_fail(docs, "X02:line id falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("133536", "996655")
    expect_fail(docs, "X03:trainer id falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("253183", "399311")
    expect_fail(docs, "X04:route spell id falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("152512", "159512")
    expect_fail(docs, "X05:material id falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"] + "\narrow \u2192 here"
    expect_fail(docs, "X06:non-ascii injected")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("skill of 175", "skill of 174")
    expect_fail(docs, "X07:cap caveat falsified")
    docs = dict(base)
    docs["doc"] = re.sub(r"\d+ crafts", "NN shapes", docs["doc"])
    expect_fail(docs, "X08:craft markers falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("Requires Anvil", "Requires Pedestal")
    expect_fail(docs, "X09:anvil rule falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("legion-blacksmithing-leveling",
                                      "legion-blacksmithing-level-up")
    expect_fail(docs, "X10:guide slug removed")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("Alchemy Discoveries here",
                                      "Alchemy findings here")
    expect_fail(docs, "X11:core symbol falsified")
    docs = dict(base)
    docs["doc"] = docs["doc"].replace("Firmament Stone", "Firmament Slab")
    expect_fail(docs, "X09b:station falsified")
    docs = dict(base)
    docs["p5"] = docs["p5"].replace("Craft_Blacksmithing.txt",
                                    "Craft_Blacksmitting.txt")
    expect_fail(docs, "S16:prompt deliverable name falsified")
    docs = dict(base)
    docs["rm"] = docs["rm"].replace("Craft_Blacksmithing.txt",
                                    "Craft_Blacksmitting.txt")
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
    print("Craft_Blacksmithing audit: %d PASS, %d FAIL" % (len(passed), len(failed)))
    if failed:
        print("FAILED:", ", ".join(failed))
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
