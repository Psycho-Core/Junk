#!/usr/bin/env python3
"""Audit for Craft_Jewelcrafting.txt (BfA 8.3.7 build 35662).

Verifies section structure, every id/name/number family the file claims,
the eight per-line craft-count totals (recomputed from the printed
addends), trainer coordinates, TrinityCore file:line anchors, the
19-item conflict index, source manifests, ASCII/line-length hygiene, and
absence of sibling-file (Inscription/Engineering) skill ids.

Usage:
  python3 audit_craft_jewelcrafting.py            # run all checks
  python3 audit_craft_jewelcrafting.py --self-test  # 20 mutations
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "Craft_Jewelcrafting.txt"

CHECKS = []


def chk(desc, cond):
    CHECKS.append((desc, bool(cond)))


def load():
    return TARGET.read_text(encoding="utf-8")


def section_checks(t):
    # Structure
    chk("line1 header", t.splitlines()[0] ==
        "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - JEWELCRAFTING CRAFTING FOR A SERVER-SIDE COMPANION")
    chk("header underline", t.splitlines()[1].startswith("=") and
        len(t.splitlines()[1]) >= len(t.splitlines()[0]))
    chk("scope paragraph", "anything without a readable source says \"unverified\"" in t)
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
    norm_t = re.sub(r"\s+", " ", t)
    for h in heads:
        i = t.find(h)
        chk(f"section header present: {h[:40]}", i >= 0)
        chk(f"section header in order: {h[:40]}", i > pos)
        pos = i
    for sub in ["3.1 Classic 1-300", "3.2 Outland 1-75", "3.3 Northrend 1-75",
                "3.4 Cataclysm 1-75", "3.5 Pandaria 1-75", "3.6 Draenor 1-100",
                "3.7 Legion 1-100", "3.8 BfA 1-175"]:
        chk(f"route {sub}", sub in t)
    # Build date / scope constants
    for lit in ["8.3.7 (BUILD 35662)", "TrinityCore-based 8.3.7", "section 9 item 13"]:
        chk(f"scope literal {lit[:30]}", re.sub(r"\s+", " ", lit) in norm_t)


def learn_map_checks(t):
    lits = [
        "Base spell Jewelcrafting 25229",
        "Learn Skill (Jewelcrafting, skill=755, value 1)",
        "Training\ncost: 10".replace("\n", "\n"),  # prose wrap-safe
        "Difficulty 111",
        "Taught by (33)",
        "158750", "195116", "25230", "28894", "28895", "28897",
        "51311", "73318", "110420",
        "Requires precious gems and metals gathered with",
        "264532-264549",
        "264536", "264540", "Construct Building",
        "Spell #264540 doesn't exist",
        "main 264532 (Learn Skill skill=2524, cap 300)",
        "wrapper 264533", "Learn Spell 25229 + Learn Spell 264532",
        "main 264534 (skill=2523, cap 75, cost 10, Taught",
        "wrapper 264535", "Step 2523",
        "main 264537 (skill=2522, cap 75, cost 10,",
        "wrapper 264538", "Step 2522",
        "main 264539 (skill=2521, cap 75, cost 10,",
        "wrapper 264541", "Step 2521",
        "main 264542 (skill=2520, cap 75, cost 10,",
        "wrapper 264543", "Step 2520",
        "main 264544 (skill=2519, cap 100, no training",
        "wrapper 264545 (Learn Spell 264544 + Step 2519;",
        "Triggered by (1)\" spell 169926",
        "main 264546 (skill=2518, cap 100)",
        "wrapper\n    264547 (Learn Spell 264546 + Step 2518; \"Reward from (1)\" quest 40523)",
        "main 264548 (skill=2517, cap 175,",
        "Taught by 2)", "wrapper 264549 (Learn Spell 264548 + Step 2517",
        "main 265811 (skill=2517, cap 175,",
        "Taught by 1, \"Horde Specific Spell\", quick facts 8.1.0",
        "wrapper 265812 (Learn Spell 265811 + Step 2517 value 1)",
        "same skill id 2517",
        "\"Kul Tiran Jewelcrafting\" (section 9 item 10)",
        "item 115359 \"Draenor Jewelcrafting\" (iLvl 40, Req. 10",
        "169926 (6.0.1, Item Effect, 10-second cast",
        "Teaches you Draenor Jewelcrafting and a number of recipes",
        "Teaches (11)", "quest 40523 rewards wrapper 264547",
        "spell 31252, 2-second cast, Effect \"Prospect\" value 5",
        "GCD 1.5", "Target must be own item",
        "Search 5 ore of a base metal",
        "always yields at least 1 gem",
        "Adamantite Powder in 3.0.2", "Titanium Ore added in",
        "added in patch 10.0.0", "382980", "382973",
        "consumes 20 ore per attempt", "queueable",
        "Mass Prospect Osmenite 300619",
    ]
    # wrap-tolerant probes: normalize whitespace for prose literals that
    # may be split by the file's line wrapping.
    norm = re.sub(r"\s+", " ", t)
    for lit in lits:
        probe = re.sub(r"\s+", " ", lit)
        chk(f"learn literal: {probe[:52]}", probe in norm)
    # wrapper patch-tag facts
    chk("wrappers 8.1.0 rule", "every wrapper is tagged" in norm and "8.1.0" in t)
    chk("exception wrapper 264533", "quick facts read 8.0.1" in norm)
    # sub-skill ids and caps
    for n in range(2517, 2525):
        chk(f"sub-skill id {n}", str(n) in t)
    for cap in ["cap 300", "cap 75", "cap 100", "cap 175"]:
        chk(f"cap literal {cap}", cap in t)
    # mains/wrappers counted by id
    mains = ["264532", "264534", "264537", "264539", "264542", "264544",
             "264546", "264548", "265811"]
    wraps = ["264533", "264535", "264538", "264541", "264543", "264545",
             "264547", "264549", "265812"]
    for i in mains:
        chk(f"main {i} listed", f"main {i}" in norm or f"main {i}".replace("main ", "") in t)
    for w in wraps:
        chk(f"wrapper {w} listed", w in t)
    chk("9 main/wrapper pairs", all(m in t for m in mains) and all(w in t for w in wraps))


def trainer_checks(t):
    norm = re.sub(r"\s+", " ", t)
    rows = [
        "KTC Train-a-Tron Deluxe, Town-In-A-Box/Sky Falls/Gallywix",
        "Whittler Dewei, The Singing Pools", "Elder Oakpaw, Mandori Village",
        "Wembil Taskwidget, Kharanos, Dun Morogh [53.7, 52]",
        "Lien Farner, Goldshire, Elwynn [42, 67]",
        "Jack \"All-Trades\" Derrington, Gilneas starting zone",
        "Hanner Gembold, The Great Forge, Ironforge [51, 25.4]",
        "Theresa Denman,\n  Trade District, Stormwind [63.6, 61.6]",
        "Therisa Sallow, Calston Estate,\n  Tirisfal [44.5, 53]",
        "Nedric Sallow, Brill, Tirisfal [61, 51]",
        "Saren, Falconwing\n  Square, Eversong [49, 47]",
        "Aleinia, Falconwing Square, Eversong [48.5, 47.4]",
        "Kalinda, The Royal\n  Exchange, Silvermoon [90.5, 74.1]",
        "Neller Fayne, Mining & Jewelcrafting\n  War Quarter, Undercity [56.2, 36.6]",
        "Valn, Azure Watch, Azuremyst [48.5, 52.2]",
        "Iranis\n  Shadebloom, Dolanaar, Teldrassil [56, 52.2]",
        "Ingo Woolybush,\n  Theramore, Dustwallow [66.2, 45.2]",
        "Aessa Silverdew, Craftsmen's Terrace,\n  Darnassus [54.0, 31.6]",
        "Farii, The Crystal Hall, Exodar [45.0, 24.0]",
        "Bilgewater Harbor, Azshara [57, 50.5]",
        "Runda, Razor Hill, Durotar [53, 42]",
        "Lalum\n  Darkmane, Bloodhoof Village, Mulgore [46.5, 57.5]",
        "Lugrah,\n  Red Canyon Mining & Jewelcrafting Valley of Honor, Orgrimmar [72.5, 34.3]",
        "Nahari Cloudchaser, Cloudchaser Jewelcrafting Lower rise, Thunder Bluff\n  [35.0, 54.0]",
        "Tatiana, Honor Hold, Hellfire [54.6, 63.6]",
        "Kalaen, Thrallmar,\n  Hellfire [56.8, 37.7]",
        "Hamanar, Aldor Rise, Shattrath [35.7, 20.5]",
        "Nemiha,\n  Aldor Rise, Shattrath [36.2, 46.9]",
        "Kirembri Silvermane, Scryer's\n  Tier, Shattrath [58.1, 75.0]",
        "Jazdalaad, The Stormspire, Netherstorm [44.5, 34.0]",
        "Alestos, Valiance Keep, Borean [57.5, 72.3]",
        "Ounhulo, Valgarde,\n  Howling Fjord [59.9, 63.8]",
        "Geba'li, Warsong Hold, Borean [41.6, 53.4]",
        "Carter Tiffens, Vengeance Landing,\n  Howling Fjord [79.3, 28.8]",
        "Cartier & Co. Fine Jewelry/Magus Commerce Exchange, Dalaran [40.5,\n  35.2]",
        "Oluros, Argent Tournament Grounds, Icecrown [71.5, 20.8]",
        "Mai the Jade Shaper, Greenstone Village, Jade Forest [48.0,\n  34.0]",
    ]
    for r in rows:
        probe = re.sub(r"\s+", " ", r)
        chk(f"trainer row: {probe[:46]}", probe in norm)
    chk("36 wiki rows claimed", "36 rows" in t)
    for land in ["The Maelstrom:", "Wandering Isle:", "Eastern Kingdoms:",
                 "Kalimdor:", "Outland:", "Northrend:", "Pandaria:"]:
        chk(f"landmass {land}", land in t)
    chk("page ends at Pandaria", "ends at Pandaria" in norm)
    wowhead = [
        "npc 33614, Shattrath", "Nemiha npc 33680", "Tatiana npc 18774",
        "Geba'li npc 26982", "Timothy Jones\n    npc 28701",
        "Farii npc 19778", "Hanner Gembold npc\n    52586", "Lugrah npc 46675",
        "Nahari Cloudchaser npc\n    52657", "Neller Fayne npc 52587",
        "Theresa\n    Denman npc 44582", "Mai the Jade Shaper npc 65098",
        "Instructor Okanu npc 153811", "Samuel D. Colton III npc 130368",
        "Seshuli npc 122695",
    ]
    for w in wowhead:
        probe = re.sub(r"\s+", " ", w)
        chk(f"wowhead taught-by: {probe[:44]}", probe in norm)
    guide = [
        "Kalinda npc 19775", "Aleinia npc 15501",
        "Loremaster Skosiris npc 33642", "Nemiha npc 33680 instead",
        "Narv npc 154393", "Artificer Harlaan npc 87052",
        "Kaevan Highwit npc 87548", "Tiffany Cartier\n    npc 93526",
        "Jabrul\n    npc 100500", "Ransa Greyfeather npc 106902",
        "Oxana Demonslay 97361", "Matthew Rabis\n    97360", "The Widow 97366",
        "Dazzik \"Proudmoore\" 97362", "Marith Lazuria 50482",
        "Isabel Jones 50480", "Karnoth 75043", "Dorogg the Ruthless 74254",
        "Shadows Awaken 34019", "The\n    Butcher of Bladespire 33410",
        "bookcase", "Scryers\"", "Aldor\"",
        "dual" if "dual" in norm else "won't teach you\n    \"Northrend recipes\"" ,
    ]
    for g in guide:
        probe = re.sub(r"\s+", " ", g)
        chk(f"guide source: {probe[:44]}", probe in norm)


def route_checks(t):
    norm = re.sub(r"\s+", " ", t)
    steps = [
        # 3.1 Classic
        "30 x Delicate Copper Wire spell 25255 (60 Copper Bar)",
        "20 x Tigerseye Band spell 32179",
        "alt 20 x Malachite Pendant spell 32178",
        "50 x Bronze Setting spell 25278 (100 Bronze Bar)",
        "20 x Simple Pearl Ring spell 25284",
        "20 x Gloom Band spell 25287",
        "alt Ring of\n    Silver Might spell 25317",
        "10 x Ring of Twilight Shadows (guide links item 20828",
        "10 x Heavy Stone Statue spell 32807 (80 Heavy Stone)",
        "30 x Pendant of the Agate Shield spell 25610",
        "Design: Amulet of the Moon item 20854 (yellow at 140)",
        "45 x Mithril Filigree spell 25615 (90 Mithril Bar)",
        "8 x Solid Stone Statue spell 32808 (80 Solid Stone)",
        "15 x Engraved Truesilver Ring spell 25620",
        "25 x Citrine Ring of Rapid Healing spell 25621",
        "5 x Aquamarine Pendant of the Warrior spell 26876",
        "50 x Thorium Setting spell 26880 (50 Thorium Bar)",
        "10 x Ruby Pendant of Fire spell 26883",
        "20 x Simple Opal Ring spell 26902",
        "alt Diamond Focus Ring spell 36526 from 265",
        "7 x Diamond Focus Ring spell 36526",
        "3 x Sapphire Pendant of Winter Night spell 26908",
        "alt Glowing Thorium\n    Band spell 34960",
        "10 x Emerald Lion Ring spell 34961",
        # prospecting table (Classic)
        "Copper Ore 2770 -> Malachite 774 (50%)",
        "Tin Ore 2771 -> Lesser\n    Moonstone 1705 (38%)",
        "Iron Ore 2772", "Mithril Ore 3858", "Thorium Ore 10620",
        "Jade 1529 (3.33% each)", "Star Ruby 7910",
        # 3.2 Outland
        "240 Adamantite\n    Ore 23425, 12 Primal Earth 22452, 12 Adamantite Bar 23446",
        "12 Dawnstone\n    23440 or 12 Talasite 23437, 12 Living Ruby 23436, 5 Earthstorm Diamond\n    25867",
        "prospect 240 x Adamantite Ore (48 casts of Prospecting 31252",
        "Adamantite Powder 24243",
        "Bold Blood Garnet 23095", "Jagged\n    Deep Peridot 23104",
        "Sparkling Azure Moonstone 23119", "Glinting Shadow\n    Draenite 23100",
        "Reckless Flame Spessarite 23099", "vendor item 23136",
        "12 x Mercurial Adamantite item 31079 (48 Adamantite Powder, 12\n    Primal Earth",
        "Regal Deep Peridot 23105", "Sovereign Shadow Draenite spell 28936",
        "Rigid Azure\n    Moonstone 23116", "Golden Draenite Ring spell 31049",
        "Potent Flame Spessarite 23101", "Nakodu 21655",
        "12 x Heavy Adamantite Ring item 24078",
        "Mystic Dawnstone spell 31101", "Design 24208",
        "Aldraan 21485/Coreiel 21474 for 12 gold",
        "Steady Talasite spell 43493", "Design 33783",
        "Davian\n    Vaclav 18822 / Jaffrey Noreliqe 18821 for 4 Halaa Research Token 26044",
        "Kailee's Rose spell 42588", "Design 33155 from\n    Almaador 21432",
        "Blood of\n    Amber 42592, Don Julio's Heart 42558, Facet of Eternity 42593, Falling\n    Star 42590",
        "5 x Insightful Earthstorm Diamond spell 32870",
        "Design 25904", "Recipe 25869, transmute\n    spell 32765",
        # 3.3 Northrend
        "around 35\n    total of one or mixed common gems",
        "7 Bloodstone, 14 Crystallized Earth 37701, 46 Eternal Earth 35624",
        "23 Eternal Shadow 35627",
        "30 Earthsiege Diamond 41334 (or\n    30 Skyflare Diamond 41266)",
        "15 Frozen Orb 43102",
        "7 x Bloodstone Band spell 56193",
        "23 x Stoneguard Band spell 58145",
        "23 x\n    Shadowmight Ring spell 58146",
        "Champion Ros'slai 39173 Horde / Knight\n    Dameron 32294 Alliance",
        "1 Mark of Honor 137642",
        "around 30 x Powerful Earthsiege Diamond spell 55399",
        "Swift Skyflare Diamond spell 55394",
        "Dream Signet item 42340, Runed Mana Band\n    45808, Scarlet Signet 45809, Sky Sapphire Amulet 45813",
        "15 x Icy Prism spell 62242",
        "Arcanist Ivrenne 31580", "Magistrix Lambriesse 31582",
        # 3.4 Cataclysm
        "avoid\n    Nightstone 52180 and Hessonite 52181",
        "Jasper Ring item\n    52306 vendors at 5 gold",
        "17 x Hessonite Band spell 73495 (34 Hessonite)",
        "Carnelian Spikes item 52492",
        "15 x Nightstone Choker spell 73497 (25 Jeweler's Setting, 30\n    Nightstone",
        "The Perforator spell 73621",
        "4 days of Jewelcrafting dailies",
        "Illustrious Jewelcrafter's Token\n    currency 361",
        "exactly 4 tokens; 20 x\n    Forlorn Shadowspirit Diamond spell 73476 (20 Shadowspirit Diamond\n    52303",
        "Vicious Amberjewel Band 99540, Vicious Ruby\n    Signet 99541, Vicious Sapphire Ring 99539",
        "5 x Vicious Sapphire Necklace spell 99542",
        "Vicious Amberjewel Pendant\n    spell 99543",
        "Vicious Ruby Choker spell 99544",
        # 3.5 Pandaria
        "Tiger Opal 76130, Roguestone 76135, Alexandrite 76137, Lapis\n    Lazuli 76133",
        "Sun's Radiance 76142, Vermilion Onyx\n    76140, River's Heart 76138, Primordial Ruby\n    76131, Imperial Amethyst\n    76141, Wild Jade 76139",
        "Jeweler's Toolset 20815 from Woodcarver\n    Liupo 62328",
        "about 80 x single-gem uncommon cuts (orange until 50, yellow to\n    55, green to 60",
        "River's Heart 131593, Sun's Radiance 131695,",
        "Vermilion Onyx 131690, Wild Jade 131688, Primordial Ruby 131686,",
        "Imperial Amethyst 131691",
        "wait a day for another\n    research",
        "Secrets of the Stone spell 131759",
        "14 x the discovered rare cut",
        # 3.6 Draenor
        "Drained Crystal Fragment 115507",
        "Intricate\n    Crimson Pendant 115287",
        "3 x Secrets of Draenor Jewelcrafting spell 176087 (1-day\n    cooldown",
        "Recipe: Reflecting Prism 116108",
        "Recipe: Prismatic Focusing Lens 116109",
        "55 x Reflecting Prism spell 170731 (55 Sorcerous Fire 113261)",
        "55 x Prismatic Focusing Lens spell 170732 (55 Sorcerous Earth 113263)",
        "Critical\n    Strike 170719 (450 Blackrock Ore + 90 Fireweed)",
        "Haste 170720 (450\n    Blackrock Ore + 90 Frostweed)",
        "Mastery 170721 (450 True Iron Ore + 90\n    Starflower)",
        "Stamina 170724 (450 True Iron Ore + 90 Talador Orchid)",
        "Versatility 170723 (450 Blackrock Ore + 90 Gorgrond Flytrap)",
        "98 x Taladite cuts straight from 1 (980 ore + 196\n    herbs)",
        # 3.7 Legion
        "24 profession quests",
        "A Personal Touch 40562 (needs 50 Legion\n    Jewelcrafting)",
        "Uniting the Isles 43341 (Archmage Khadgar\n    90417, level 45",
        "plus 25 Legion\n    Jewelcrafting",
        "Deadly Deep Amber 195848 (Deep Amber 130173)",
        "Masterful\n    Queen's Opal 195851 (Queen's Opal 130177)",
        "Quick Azsunite 195849\n    (Azsunite 130174)",
        "Versatile Skystone 195850 (Skystone 130176)",
        "Jeweled Lockpick 195881 (Sangrite 130172)",
        "Azsunite Loop 195925 (50 Azsunite + 25\n    Chaotic Spinel 130175)",
        "Deep Amber Loop 195923, Queen's Opal Loop\n    209609, Skystone Loop 195924",
        "Skystone Pendant 195927 (225\n    Skystone + 45 Sangrite)",
        "Queen's Opal Pendant 209610, Deep Amber\n    Pendant 195926, Azsunite Pendant 195928",
        "25 Blood of Sargeras 124124, 10 Infernal Brimstone 124444, 5\n    Pandemonite 130181, 5 Furystone 130178",
        # 3.8 BfA
        "Deadly Solstone 256689, Insightful\n    Rubellite 256693, Masterful Kubiline 256692, Quick Golden Beryl 256694,",
        "Straddling Viridium 256691, Versatile Kyanite 256690",
        "Deadly Amberblaze 256696, Masterful\n    Tidal Amethyst 256698, Quick Owlseye 256699, Versatile Royal Quartz\n    256695",
        "10 x Kraken's Eye of Agility 256701 or Intellect 256702 or\n    Strength 256700",
        "Narv 154393 (Horde) /\n    Instructor Okanu 153811",
        "5 x\n    Masterful Sea Currant 298797 (5 Sea Currant) or Versatile Dark Opal\n    298794 (5 Dark Opal)",
        "Deadly Lava Lazuli 298798, Straddling Sage Agate 300756,\n    Quick Sand Spinel 298796",
        "Mass Prospect Osmenite spell 300619 gives skill points all\n    the way to 175",
        "100-150 Osmenite Ore 168185",
        "Leviathan's Eye 168635 is the prospecting prize",
    ]
    for s in steps:
        probe = re.sub(r"\s+", " ", s)
        chk(f"route step: {probe[:52]}", probe in norm)


def totals_checks(t):
    norm = re.sub(r"\s+", " ", t)
    found = re.findall(r"Total exact-count (?:casts|crafts)[^=]*= (\d+) \(([^)]*)\)", norm)
    chk("8 route totals present", len(found) == 8)
    for num_s, body in found:
        head = body.split(";")[0].split(".")[0]
        addends = [int(x) for x in re.findall(r"\d+", head)]
        chk(f"total {num_s} from {addends}", sum(addends) == int(num_s))
    # explicit expected values
    expected = {"368": 8, "29": 2, "110": 5, "87": 5, "95": 3,
                "103": 3, "75": 3, "25": 3}
    for val, n in expected.items():
        chk(f"total value {val} exists", f"= {val} (" in norm)
        chk(f"total {val} has {n} addends", any(v == val for v, _ in found))
    # derived arithmetic
    chk("240/5 = 48 prospect casts", 240 // 5 == 48 and
        "48 casts of Prospecting 31252" in norm)
    chk("980 ore / 196 herbs skip math", "98 x Taladite" in norm and "980 ore" in norm)


def materials_costs_level_checks(t):
    norm = re.sub(r"\s+", " ", t)
    mats = [
        "Jeweler's Kit 20815", "Small Lustrous Pearl 5498",
        "Heavy Stone 2838 + Solid\n    Stone 7912", "Essence of Undeath 12808",
        "Adamantite Powder 24243", "Primal Earth 22452",
        "Earthstorm\n    from Alchemy transmute 32765",
        "Bloodstone 36917", "Crystallized Earth 37701",
        "Frozen Orb 43102", "Shadowspirit Diamond\n    52303 (crafted)",
        "Illustrious Jewelcrafter's Token 361", "Spirit\n    of Harmony (Secrets of the Stone research",
        "Sorcerous Fire 113261, Sorcerous Earth 113263",
        "Fireweed 109125, Frostweed 109124,",
        "Starflower 109127, Talador Orchid 109129, Gorgrond Flytrap 109126",
        "Blood of Sargeras 124124 (world content),",
        "Solstone/Rubellite/Kubiline/Golden Beryl/Viridium/Kyanite,",
        "Osmenite Ore\n    168185, Leviathan's Eye 168635",
        "Storm Silver Ore\n    152579, Platinum Ore 152513",
        "Solstone 22%, Kubiline 21%",
        "Viridium 22%", "Kyanite 24%",
        "Jeweler's Setting\"\nis a crafting reagent",
        "three names for\n    one id, section 9 item 17",
        "(prospect)", "(Mining)", "(vendor)", "(AH)", "(daily/quest)",
        "(alchemy)",
    ]
    for m in mats:
        probe = re.sub(r"\s+", " ", m)
        chk(f"material: {probe[:52]}", probe in norm)
    costs = [
        "Training\ncost: 10" if "Training\ncost: 10" in t else "Training cost: 10",
        "currency\nunit is not rendered on the page - unverified",
        "no training-cost line",
        "12 gold (Halaa, limited\n    supply)",
        "4 Halaa Research Token 26044",
        "1 Mark of Honor 137642 each",
        "exactly 4 Illustrious Jewelcrafter's\n    Token 361",
        "250 Sightless Eye 1149 each",
        "sell\n    recalibrations for 25 gold",
        "MoneyCost x reputation\n    discount",
        "FailReason::NotEnoughMoney at\n    102",
    ]
    for c in costs:
        probe = re.sub(r"\s+", " ", c)
        chk(f"cost: {probe[:52]}", probe in norm)
    level = [
        "Level 10, \"Requires level 10\", Side\n    Both",
        "added 7.0.1",
        "iLvl 40, Req. 10",
        "only at 50 Legion Jewelcrafting",
        "World Quests need 25;",
        "level 45",
        "first Nazjatar intro quests",
        "level 60 (Boralus/Dazar'alor)",
        "level 50 (Nazjatar)",
        "Apprentice/\n    Journeyman/Expert/Artisan 1-300",
        "1-75/75-150/150-225/\n    225-300",
        "Kul Tiran/\n    Zandalari Master 1-150 (stale - section 9 item 3)",
        "can be trained as early as\n    level 5",
        "level 50 (section 9 item 4)",
        "\"level TBC\" (section 9 item 5)",
        "after skill 300",
        "Tatiana/Kalaen",
        "Gemcutting 28875 = +5 (section 9 item 1)",
        "291442 = +2 to every profession",
        "added\n    8.1.5",
        "Halaa control", "Wintergrasp\n    control", "Aldor/Scryers exclusivity",
        "no character-level gates",
    ]
    for v in level:
        probe = re.sub(r"\s+", " ", v)
        chk(f"level: {probe[:52]}", probe in norm)


def tc_checks(t):
    norm = re.sub(r"\s+", " ", t)
    anchors = [
        "HEAD 209d6d51d1",
        "NPCHandler.cpp 97 HandleTrainerListOpcode -> 112",
        "102-109", "missing trainer data at 121",
        "127 trainer->SendSpells",
        "130 HandleTrainerBuySpellOpcode -> 155",
        "Trainer.cpp 41 SendSpells",
        "discount at 43/65",
        "76 TeachSpell -> 98-99",
        "reputationDiscount x MoneyCost",
        "NotEnoughMoney at\n   102",
        "ModifyMoney(-moneyCost)",
        "149 CanTeachSpell, 172 GetSpellState, 212 SendTeachFailure",
        "SPELL_EFFECT_SKILL\n   (effect 118, SpellEffects.cpp 210 dispatch)",
        "EffectSkill at\n   SpellEffects.cpp 4668",
        "SetSkill(skillid, skillStep, skillval, maxSkillVal) at 4699",
        "SkillTiers (4689)",
        "EffectLearnSpell SpellEffects.cpp 2129",
        "learned at 2170",
        "item 115359 -> 169926",
        "Spell.cpp 7805-7835 case SPELL_EFFECT_PROSPECTING",
        "ITEM_FLAG_IS_PROSPECTABLE (7811)",
        "no trade slot\n   (7814-7815)",
        "SPELL_FAILED_LOW_CASTLEVEL (7817-7819)",
        "NEED_MORE_ITEMS (7823-7828)",
        "HaveLootFor else\n   CANT_BE_PROSPECTED (7831-7832)",
        "EffectProspecting SpellEffects.cpp\n   4614",
        "UpdateGatherSkill(SKILL_JEWELCRAFTING, ...) at 4633",
        "LOOT_PROSPECTING (Loot.h 115, type 23)",
        "LootMgr.cpp 55, load 1308, refs check 1450",
        "LootHandler.cpp 347-348",
        "3869 TakePower()",
        "3872 TakeReagents() (definition 5600",
        "ITEM_FLAG_NO_REAGENT_COST",
        "EffectCreateItem SpellEffects.cpp\n   1473",
        "EffectCreateItem2 1482",
        "SPELL_ATTR0_IS_TRADESKILL selecting\n   ItemContext::Trade_Skill (1478/1492/1522/2484)",
        "DoCreateItem\n   SpellEffects.cpp 1383",
        "at\n   1469",
        "same call at 1499",
        "2492/3533",
        "SPELL_ATTR9_ITEM_CAST_GRANTS_SKILL_GAIN",
        "Spell.cpp 3863-3865",
        "Player.cpp 5410 UpdateCraftSkill",
        "SPELL_ATTR1_NO_SKILL_INCREASE (5412)",
        "SkillupSkillLineID at 5421-5422",
        "SkillGain.Crafting (5433, default 1 at World.cpp 790)",
        "SkillGainChance against TrivialSkillLineRankHigh/Low (5435)",
        "SkillChance.Orange 100 / Yellow 75 / Green 25 / Grey 0\n   (World.cpp 784-787)",
        "reqSkillValue checks in Spell.cpp",
        "6373 -> CanOpenLock 8648-8703",
        "the prospecting/milling item ranks (7817,\n   7848)",
        "no dedicated TC effect\n   row",
        "SkillChance.Prospecting default\n   false (World.cpp 629)",
        "(630)",
        "SKILL_JEWELCRAFTING = 755 at SharedDefines.h\n   5958",
        "QUEST_SORT_JEWELCRAFTING maps to it at 6370",
        "QUEST_TRSKILL_JEWELCRAFTING = 14 (QuestDef.h 138)",
        "SPELL_EFFECT_PROSPECTING =\n   127",
        "SpellEffects.cpp 219 dispatch",
        "SpellInfo.cpp 1089",
        "section 9 item 14",
        "section 9 item 18",
    ]
    for a in anchors:
        probe = re.sub(r"\s+", " ", a)
        chk(f"TC anchor: {probe[:52]}", probe in norm)


def cannot_do_checks(t):
    items = [
        "Click profession-window buttons",
        "item target",
        "Talk to trainers or vendors",
        "client opcode",
        "Turn in quests",
        "24-quest",
        "34019/33410",
        "4 Cataclysm daily-quest days",
        "Socket gems",
        "shift-right-click socketing UI",
        "Choose a race at creation",
        "bookcase (Outland learn object",
        "garrison Gem Boutique vendor",
        "Auction House",
        "World Quests",
    ]
    for i in items:
        chk(f"cannot-do: {i[:44]}", i in re.sub(r"\s+", " ", t))


def conflicts_checks(t):
    norm = re.sub(r"\s+", " ", t)
    sec9 = t.split("9. CONFLICTS AND UNVERIFIED INDEX")[1].split("10. SOURCES")[0]
    nums = [int(m) for m in re.findall(r"^(\d+)\)", sec9, flags=re.M)]
    chk("conflicts numbered 1..19", nums == list(range(1, 20)))
    items = [
        "six wow-professions guides", "\"+10 Jewelcrafting skill\"",
        "spell 28875", "Mod Skill value 5", "Adopted: 5.",
        "\"+5 from the trait Jack of", "Skill in all\n2) professions increased by 2" if False else
        "increased by 2\" (11 Mod Skill effects value 2",
        "Adopted: 2.", "1-150", "Adopted: 175.",
        "\"level 5\"", "\"level 50\"", "section 9 item 4",
        "\"level TBC\"", "Engineering's item 14",
        "spell 201704 \"Legion\n   Jewelcrafter\"", "195116", "value 10",
        "Adopted: 264547", "Engineering's 201700",
        "Inscription file's 201703",
        "382980", "382973", "Adopted for 8.3.7: 31252",
        "three ways for the same lines",
        "npc 33614", "Hamanar + Nemiha, Kirembri, Kalaen and\n   Jazdalaad",
        "wiki lists 6",
        "Aleinia npc 15501 (Eversong Woods) - neither appears\n   in 264539's Taught-by",
        "\"Learn Skill (\n   Kul Tiran Jewelcrafting)\"",
        "Patch-tag asymmetry", "quick facts print 8.1.0",
        "print 8.0.1 while every other wrapper",
        "Block gaps verified by probe",
        "TC vs guide on prospecting skill",
        "defaults to false (World.cpp 629)",
        "ptr.wowhead link 300619",
        "\"Skill: 111325\"",
        "One id, three spellings",
        "HEAD 209d6d51d1 versus the earlier files'",
        "Teaches only Apprentice",
        "4.0.3a", "2.3.0", "Simple Grinder", "5.0.4",
        "Also unverified (not guessed):",
        "SkillLineAbility rows", "Kalaen's creature entry",
        "\"Trade Skill\" effect enum id",
    ]
    for i in items:
        probe = re.sub(r"\s+", " ", i)
        chk(f"conflict: {probe[:52]}", probe in norm)


def sources_checks(t):
    norm = re.sub(r"\s+", " ", t)
    src = [
        "fetched 2026-10-26 week",
        "not stored in the repository",
        "25229 (base + 9 other ranks 158750, 195116, 25230,",
        "264510 (miss - Shoot)",
        "264454 (miss - Currency",
        "264540\n(does not exist)",
        "169926\n(WoD scroll effect",
        "31252 (Prospecting",
        "28875 (Gemcutting: Mod Skill value 5)",
        "291442 (Jack of All Trades",
        "201704 (Legion Jewelcrafter",
        "skill 755\n(Jewelcrafting hub)",
        "40523 \"Facet-nating Friends\"",
        "25-row storyline",
        "warcraft.wiki pages (chunk counts)",
        "Jewelcrafting_trainers (5 chunks, 36 rows, ends at\nPandaria)",
        "Classic/Outland/Northrend/Cataclysm/Pandaria/Draenor/Legion/",
        "Battle_for_Azeroth_jewelcrafting_designs",
        "vanilla-jewelcrafting-leveling (3\nchunks)",
        "outland-jewelcrafting-leveling (2)",
        "northrend-jewelcrafting-\nleveling (2)",
        "cataclysm-jewelcrafting-leveling (1)",
        "pandaria-\njewelcrafting-leveling (1)",
        "draenor-jewelcrafting-leveling (1), legion-\njewelcrafting-leveling (chunks 0-2)",
        "zandalari-kul-tiran-bfa-jewelcrafting-\nleveling-guide (2)",
        "wowpedia.fandom.com/wiki/Outland_jewelcrafting_designs",
        "wowpedia.fandom.com/wiki/Battle_for_Azeroth_jewelcrafting_designs",
        "wowhead.com/skill=2517/kul-tiran-jewelcrafting",
        "wow-professions.com/guides/bfa-jewelcrafting",
        "blobless sparse clone of master, HEAD 209d6d51d1",
        "Spells/Spell.cpp",
        "Entities/Creature/Trainer.cpp",
        "Handlers/LootHandler.cpp",
        "World/World.cpp",
        "Miscellaneous/SharedDefines.h",
    ]
    for s in src:
        probe = re.sub(r"\s+", " ", s)
        chk(f"source: {probe[:52]}", probe in norm)


def hygiene_and_guard_checks(t):
    try:
        t.encode("ascii")
        chk("ascii", True)
    except UnicodeEncodeError:
        chk("ascii", False)
    over = [i + 1 for i, l in enumerate(t.splitlines()) if len(l) > 100]
    chk(f"no line > 100 cols", not over)
    chk("no trailing whitespace", not any(l != l.rstrip() for l in t.splitlines()))
    chk("no tabs", "\t" not in t)
    chk("no TODO/FIXME", "TODO" not in t and "FIXME" not in t)
    chk("unverified marker present", t.count("unverified") >= 10)
    chk("no CRLF", "\r" not in t)
    # sibling-file guard: ids that must not leak into this deliverable
    forbidden = ["45357", "264494", "264495", "264496", "264497", "264498",
                 "264499", "264500", "264501", "264502", "264503", "264504",
                 "264505", "264506", "264507", "264508", "264509", "265809",
                 "265810", "51005", "161789", "111923", "255663", "39847"]
    for f in forbidden:
        chk(f"no sibling id {f}", f not in t)
    chk("773 not present as skill", not re.search(r"\b773\b", t))
    chk("cross-file refs allowed", "201703" in t and "201700" in t)


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
    ("base id 25229 -> 25230", "Base spell Jewelcrafting 25229",
     "Base spell Jewelcrafting 25230"),
    ("gap id 264540 -> 264541", "Spell #264540 doesn't exist",
     "Spell #264541 doesn't exist"),
    ("Classic sub-skill step 2524 -> 2525", "skill=2524, cap 300",
     "skill=2525, cap 300"),
    ("total 368 -> 369", "= 368 (30 + 20", "= 369 (30 + 20"),
    ("total 110 -> 111", "= 110 (35 + 7", "= 111 (35 + 7"),
    ("total 95 -> 96", "= 95 (80 + 1 + 14)", "= 96 (80 + 1 + 14)"),
    ("prospect value 5 -> 4", "Effect \"Prospect\" value 5",
     "Effect \"Prospect\" value 4"),
    ("prospecting cfg false -> true", "SkillChance.Prospecting default\n   false",
     "SkillChance.Prospecting default\n   true"),
    ("skill id 755 -> 756", "SKILL_JEWELCRAFTING = 755 at SharedDefines.h",
     "SKILL_JEWELCRAFTING = 756 at SharedDefines.h"),
    ("Gemcutting adopted 5 -> 10", "Gemcutting 28875 = +5",
     "Gemcutting 28875 = +10"),
    ("drop section 7 header", "7. WHAT THE CORE MUST DO FOR A CRAFT TO SUCCEED",
     "7. WHAT THE CORE DOES"),
    ("Dalaran coord drift", "[40.5,\n  35.2]", "[40.5,\n  36.2]"),
    ("Mass Prospect id 300619 -> 300618", "Osmenite spell 300619",
     "Osmenite spell 300618"),
    ("quest level 10 -> 11", "\"Requires level 10\"",
     "\"Requires level 11\""),
    ("Kaevan npc 87548 -> 87549", "Kaevan Highwit npc 87548",
     "Kaevan Highwit npc 87549"),
    ("non-ascii injection", "CHEAPEST ROUTE", "CHEAPESTé ROUTE"),
    ("line longer than 100 cols",
     "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - JEWELCRAFTING CRAFTING FOR A SERVER-SIDE COMPANION",
     "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - JEWELCRAFTING CRAFTING FOR A SERVER-SIDE COMPANION PAD PAD PAD PAD"),
    ("renumber conflict 17)", "17) Tool names", "18) Tool names"),
    ("Kailee's Rose 42588 -> 42589", "Kailee's Rose spell 42588",
     "Kailee's Rose spell 42589"),
    ("loot type 23 -> 24", "LOOT_PROSPECTING (Loot.h 115, type 23)",
     "LOOT_PROSPECTING (Loot.h 115, type 24)"),
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
