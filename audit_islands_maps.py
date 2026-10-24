#!/usr/bin/env python3
"""Audit: Islands_Maps_COMPLETED.txt (Islands 1)."""

import re
import sys

sys.path.insert(0, ".")
from audit_common import (gh_content, gh_raw, source_stage, mutation_probe,
                          coord_trace)

DOC = "# Ai Research prompts/Islands/Islands_Maps_COMPLETED.txt"
TCDEV = "TCDEVEmu/AtalDazar_BFA"
TC = "TrinityCore/TrinityCore"
MTT = "MttAI-dev/MTT-WoW-BfA"
HAVEN = "HavenWoW/BFA-HavenCore"
ADDON = "dreamxiaodao/AddOns"
DICT = "Ironship/WordHunterWoW-Dictionary-DE"

FILES = {
    "isl_sql": (TCDEV, "sql/Ataldazar/world/2020_12_07_00_island.sql"),
    "un_charted": (TCDEV, "sql/Ataldazar/world/2020_11_22_01_Uncharted_Island.sql"),
    "mapdiff": (TCDEV, "sql/Ataldazar/hotfixes/2022_03_20_00_map_difficulty.sql"),
    "tc_safe": (TC, "sql/old/8.x/world/19071_2020_06_17/2019_10_26_01_world.sql"),
    "mtt_0507": (MTT, "sql/old/world/2020_05_07_01_world.sql"),
    "mtt_safe": (MTT, "sql/old/world/2020_05_15_04_world.sql"),
    "shared": (HAVEN, "src/server/game/Miscellaneous/SharedDefines.h"),
    "rares": (ADDON, "RareScanner/Tables/RareTables.lua"),
    "dict110": (DICT, "EntityData/Variants/retail/Data/npc/enUS_110.lua"),
    "dict112": (DICT, "EntityData/Variants/retail/Data/npc/enUS_112.lua"),
    "dict114": (DICT, "EntityData/Variants/retail/Data/npc/enUS_114.lua"),
}
RAW_FILES = {
    "go_tpl": (MTT, "sql/old/world/2020_05_19_02_TC_gameobject_template.sql"),
}
SNOW_SCRIPT = ("src/server/scripts/BattleforAzeroth/Island Expeditions/"
               "ScenarioSnowblossomVillage/scenario_snowblossom_village.cpp")

ISLES = {  # name -> map id (spec) ; entry = queue-teleport or None
    "Un'gol Ruins": (1813, None),
    "Havenswood": (1814, (-84.7982, -843.8871, 6.3429, 3.9626899)),
    "Jorundall": (1879, (14404.991, 11490.11, 6.3429, 4.09958)),
    "Verdant Wilds": (1882, (14917.806, 15177.087, 10.872437, 0)),
    "Whispering Reef": (1883, (-913.84894, 2159.6199, 28.34297, 0)),
    "The Rotting Mire": (1892, (9153.376, 9691.307, 6.3429, 1.5364347)),
    "The Dread Chain": (1893, (1424.8444, 457.19388, 6.432567, 4.33277)),
    "Molten Cay": (1897, None),
    "Skittering Hollow": (1898, None),
    "Snowblossom Village": (1907, (2234.67, -129.747, 6.3429, 2.34406)),
    "Crestfall": (2124, None),
}
LFG_NAME_MAP = {  # lfg name prefix -> map
    "Snowblossom Village": 1907, "Havenswood": 1814, "The Dread Chain": 1893,
    "The Rotting Mire": 1892, "Jorundall": 1879, "Verdant Wilds": 1882,
    "Whispering Reef": 1883,
}
ENTRY_NO_LFG = {1813, 1897, 1898, 2124}   # island.sql marks them TO DO
RARE_IDS = ["137579", "139218", "139411", "139415", "139416", "139418",
            "139681", "140992"]
RARE_NAMES = {
    "137579": "Unbound Azerite", "139218": "Life-Tender Olvarius",
    "139411": "Many-Fangs", "139415": "Slitherscale",
    "139416": "Volshas", "139418": "Stagnant One",
    "139681": "Bleakfin", "140992": "Corpseburster",
}
AZERITE_GO = ["273296", "289356", "289359", "289437", "279393", "290911",
              "290912", "290913"]
CHEST_GO = ["270913", "270914", "271647"]
EVENT_GO = ["281896", "299039", "282625", "282628"]
NAMELESS_GO = ["270945", "273297", "281597", "287445", "289318"]
SCENERY_GO = ["269984", "277463", "281470", "281471", "284424", "287451",
              "272643", "293703", "286962", "286963", "289320"]
GO_TYPE_NAME = {  # entry -> (name, type) claimed by the doc
    "273296": ("Azerite Shard", 10), "289356": ("Azerite Shard", 10),
    "289359": ("Azerite Chunk", 10), "289437": ("Azerite Crystal", 10),
    "279393": ("Azerite Growth", 5), "290911": ("Sack of Azerite", 10),
    "290912": ("Bag of Azerite", 10), "290913": ("Pouch of Azerite", 10),
    "270913": ("Old Chest", 10), "270914": ("Reinforced Chest", 10),
    "271647": ("Rotting Wooden Chest", 10),
    "281896": ("Azerite Detector", 5), "299039": ("Azerite Detector", 5),
    "282625": ("Shovel", 10), "282628": ("Sand Pile", 10),
}
UNVERIFIED_MIN = 12


def norm(s):
    return re.sub(r"\s+", " ", s)


STATIC_CHECKS = [
    ("heading", "=== ISLAND EXPEDITIONS - MAPS - BFA 8.3.7 (TRINITYCORE) "
                "- COMPLETED ==="),
    ("done", "DONE - step 1 of the Islands set complete"),
    ("src wiki", "warcraft.wiki.gg"),
    ("src tcdev", "TCDEVEmu/AtalDazar_BFA (8.3.7 server SQL,"),
    ("src safe", "TrinityCore sql/old/8.x world_safe_locs dump"),
    ("src mtt", "MTT-WoW-BfA SQL (cross-check, identical rows)"),
    ("src haven", "HavenWoW/BFA- HavenCore SharedDefines.h"),
    ("src rare", "RareScanner addon rare list"),
    ("rotation", "11 islands in the weekly rotation"),
    ("tot n", "Normal 6,000 Azerite."),
    ("tot h", "Heroic 9,000 Azerite."),
    ("tot m", "Mythic 12,000 Azerite."),
    ("tot p", "PvP 12,000 Azerite (same as Mythic; PvP win also gives "
              "Conquest)."),
    ("weekly", "Weekly quest total: 36,000 Azerite per week (was 40,000"),
    ("ratio", "6 Normal or 4 Heroic or 3 Mythic/PvP wins (Icy Veins)"),
    ("diff ids", "38 = Normal, 39 = Heroic, 40 = Mythic"),
    ("diff mp", "(MaxPlayers 3), 45 = PvP (MaxPlayers 6)"),
    ("diff src", "IDs 4096/4097/4098/4171, build 34963"),
    ("enum src", "LOOT_MODE_NORMAL/HEROIC/MYTHIC/PVP_ISLAND = 38/39/40/45"),
    ("d153", "Difficulty 153 appears in TCDEVEmu"),
    ("d153 enum", "153 = Teeming Island"),
    ("start wiki", "every island has at least 4 start locations"),
    ("start unv", "the exact\n   coordinates of the 4 retail start points "
                  "per island: unverified"),
    ("isle1", "Un'gol Ruins - map 1813."),
    ("isle2", "Havenswood - map 1814."),
    ("isle3", "Jorundall - map 1879."),
    ("isle4", "Verdant Wilds - map 1882, zone 9440"),
    ("isle5", "Whispering Reef - map 1883."),
    ("isle6", "Rotting Mire - map 1892"),
    ("isle7", "Dread Chain - map 1893"),
    ("isle8", "Molten Cay - map 1897."),
    ("isle9", "Skittering Hollow - map 1898."),
    ("isle10", "Snowblossom Village - map 1907."),
    ("isle11", "Crestfall - map 2124"),
    ("e hav", "(1814, -84.7982, -843.8871, 6.3429, o 3.9626899)"),
    ("e jor", "(1879, 14404.991, 11490.11, 6.3429, o 4.09958)"),
    ("e ver", "(1882, 14917.806, 15177.087, 10.872437, o 0)"),
    ("e reef", "(1883, -913.84894, 2159.6199, 28.34297, o 0)"),
    ("e mire", "(1892, 9153.376, 9691.307, 6.3429, o 1.5364347)"),
    ("e dread", "(1893, 1424.8444, 457.19388, 6.432567, o 4.33277)"),
    ("e snow", "(1907, 2234.67, -129.747, 6.3429, o 2.34406)"),
    ("s ungol", "(1813, 125.644, -470.398, 0, o 0)"),
    ("s hav", "(1814, -266.278, -1308.08, 43.1385, o 0)"),
    ("s jor", "(1879, 14198.8, 11071.3, 12.2526, o 0)"),
    ("s ver", "(1882, 14500.7, 15096.6, 0, o 0)"),
    ("s reef", "(1883, -898.649, 1668.74, 41.9155, o 0)"),
    ("s mire", "(1892, 8926.07, 9965.83, 0, o 0)"),
    ("s dread", "(1893, 1301.26, -352.104, 0.303792, o 0)"),
    ("s molten", "(1897, 1753.93, 1390.02, 260.916, o 0)"),
    ("s skit", "(1898, 8791.45, -5561.79, 0, o 0)"),
    ("s snow", "(1907, 1873.58, -213.153, 3.0708, o 0)"),
    ("s crest", "(2124, 1190.19, -165.148, -0.367364, o 0)"),
    ("lfg hav", "lfg dungeon ids: 1928 (38), 1929 (39), 1930 (40), 1931 (45),"),
    ("lfg jor", "lfg dungeon ids: 1932 (38), 1933 (39), 1934 (40), 1935 (45),"),
    ("lfg ver", "lfg dungeon ids: 1724 (38), 1743 (39), 1746 (40), 1763 (45),"),
    ("lfg reef", "lfg dungeon ids: 1735 (38), 1740 (39), 1749 (40), 1908 (45;"),
    ("lfg mire", "lfg dungeon ids: 1723 (38), 1744 (39), 1745 (40), 1764 (45)."),
    ("lfg dread", "lfg dungeon ids: 1734 (38), 1741 (39), 1748 (40), 1766 (45)."),
    ("lfg snow", "lfg dungeon ids: 1983 (38), 1988 (39), 1989 (40), 1990 (45)."),
    ("reef typo", 'source row has orientation typo "08"'),
    ("ilvl", "requiredItemLevel 0,\n     VerifiedBuild 28153"),
    ("todo ungol", "Entry: unverified (source marks it TO DO - no lfg rows)."),
    ("todo molten", "Entry: unverified (source marks it TO DO - no lfg rows; "
                    "comment"),
    ("todo crest", "1987, 1985, 1986, 1984, 2057"),
    ("inst1", "parent 1642, script scenario_ungol_ruins"),
    ("inst2", "parent 1642, script scenario_havenswood"),
    ("inst3", "parent 1642, script scenario_jorundall"),
    ("inst4", "parent 1642, script scenario_verdant_wilds"),
    ("inst5", "parent 1642, script scenario_whispering_reef"),
    ("inst6", "parent 1642, script scenario_the_rotting_mire"),
    ("inst7", "parent 1642, script scenario_the_dread_chain"),
    ("inst8", "parent 1642, script scenario_molten_cay"),
    ("inst9", "parent 1642, script scenario_skittering_hollow"),
    ("inst10", "parent 1642, script scenario_crestfall"),
    ("snow script", "scenario_snowblossom_village.cpp exists"),
    ("snow noinst", "instance_template row for 1907 not present"),
    ("spawndiff", "spawnDifficulties '38,39,40,45' on all"),
    ("spawndiff153", "plus 153 on maps 1814, 1879, 1882, 2124."),
    ("exit z", "(1642, -2048.53, 956.798, 7.05158, o 167.31)"),
    ("exit z name", "Islands - Port of\n     Zandalar Exit Loc"),
    ("exit b", "(1643, 936.776, -460.89, 8.38692, o 251.654)"),
    ("respawn wiki", "Chests and Azerite Nodes of all kinds"),
    ("respawn despawn", "despawn when the cast for gathering is finished"),
    ("respawn timer", "In-run respawn timer:\n     unverified"),
    ("spawn7200", "spawntimesecs 7200 and spawnDifficulties '38' as shipped"),
    ("verdant stats", "180 creature spawn rows / 75 distinct entries"),
    ("verdant go stats", "67 gameobject spawn rows / 34 distinct entries"),
    ("rare hdr", "75 distinct entries (8 of them"),
    ("rare1", '137579 "Unbound Azerite":      (1882, 15198.4, 14802.6, '
              '18.6424)'),
    ("rare2", '139218 "Life-Tender Olvarius": (1882, 14855.3, 14816.4, '
              '6.34723)'),
    ("rare3", '139411 "Many-Fangs":           (1882, 14912.7, 14627, 0)'),
    ("rare4", '139415 "Slitherscale":         (1882, 15191, 14686.7, 0)'),
    ("rare5", '139416 "Volshas":              (1882, 15157.8, 14644.9, '
              '-0.101324)'),
    ("rare6", '139418 "Stagnant One":         (1882, 14914.8, 14619.8, 0)'),
    ("rare7", '139681 "Bleakfin":             (1882, 15118, 14633.8, '
              '-0.0809143)'),
    ("rare8", '140992 "Corpseburster":        (1882, 14933.8, 14883.8, '
              '3.22263)'),
    ("rare all", "All 8 rows: spawntimesecs 7200, spawnDifficulties '38'."),
    ("az 273296", '273296 "Azerite Shard" (type 10), 9 rows:'),
    ("az 273296 c", "(1882, 15246.3, 14953.7, 39.9086)"),
    ("az 289356", '289356 "Azerite Shard" (type 10), 4 rows:'),
    ("az 289359", '(1882, 15166.8, 14724.3, 0.947647)'),
    ("az 289437", '289437 "Azerite Crystal" (type 10), 3 rows:'),
    ("az 279393", '279393 "Azerite Growth" (type 5), 3 rows:'),
    ("az 290911", '290911 "Sack of Azerite" (type 10), 5 rows:'),
    ("az 290911 c", "(1882, 14975.5, 14845.3, 6.78653)"),
    ("az 290912", '290912 "Bag of Azerite" (type 10), 3 rows:'),
    ("az 290913", '290913 "Pouch of Azerite" (type 10), 3 rows:'),
    ("az 290913 c", "(1882, 14979.7, 14851.6, 7.28653)"),
    ("chest1", '270913 "Old Chest":           (1882, 15318.6, 15016, '
               '44.0913)'),
    ("chest2", '270914 "Reinforced Chest", 3 rows:'),
    ("chest2 c", "(1882, 14856.7, 14842.5, 6.6265)"),
    ("chest3", '271647 "Rotting Wooden Chest": (1882, 15205.7, 14837, '
               '24.049)'),
    ("ev det1", '281896 "Azerite Detector" (type 5): (1882, 14794.8, '
                '14721.2, 6.09588)'),
    ("ev det2", '299039 "Azerite Detector" (type 5): (1882, 15200.5, 14614, '
                '6.48719)'),
    ("ev shov", '282625 "Shovel", 2 rows:'),
    ("ev shov c", "(1882, 14678.2, 14958.9, 2.84112)"),
    ("ev sand", '282628 "Sand Pile", 2 rows:'),
    ("ev sand c", "(1882, 14651.9, 15048.3, 1.07474)"),
    ("scenery", "269984 Sticky Starfish x2, 277463 Unripe Pumpkin x1"),
    ("scenery2", "281470 Orange Spineapple x1, 281471 Yellow Spineapple x4"),
    ("scenery3", "286962 Kul'Tiran Frigate (type 43) x1"),
    ("nameless hdr", "Entries with no name in any readable source"),
    ("nl 270945", "270945 (1882, 14934.8, 14784.2, 2.48005) o 3.98669"),
    ("nl 273297", "273297 (1882, 15250.5, 14944.3, 39.7836) o 5.13127"),
    ("nl 281597", "281597 (1882, 14954.5, 14914.2, 5.98949) o 3.35291"),
    ("nl 287445", "287445 (1882, 15332, 15000.5, 46.1907) o 3.43313"),
    ("nl 289318", "289318, 2 rows"),
    ("nl 289318 c", "289318, 2 rows: (1882, 14657, 15330.5, 0.967176)"),
    ("uncharted", "Uncharted Island - map 1955, zone 9778"),
    ("uncharted stats", "66 creature spawn rows + 15 gameobject"),
    ("pouch1955", '291080 "Pouch of Azerite" x4 rows'),
    ("crescent hdr", "Crescent Isle - map 1645 (8.0 prototype"),
    ("crescent1", "(1645, 3443.49, -144.335, 7.49805, o 16)"),
    ("crescent2", '(1645, 3485.54, -128.806, 0.887992, o 0) "Safe Loc"'),
    ("crescent3", "(1645, 3833.23, -220.333, 1.26485, o 179.846)"),
    ("crescent bots", "(1645, 3641.79, -245.13, 2.61367, o 0)"),
    ("proto 1780a", "(1780, 14344.9, 14823.3, 0.591667, o 0)"),
    ("proto 1780b", "(1780, 14833.4, 7141.44, 5.60289, o 223.651)"),
    ("alpha name", 'alpha name: "8.0 Islands - Forested - Prototype"'),
    ("sec6", "WHAT WAS NOT FOUND"),
    ("unv starts", "The 4 per-island retail start-point coordinates"),
    ("unv pools", "Azerite node, chest, event and rare spawn pools for the "
                  "10 islands"),
    ("unv respawn", "In-expedition node respawn timer"),
    ("unv names", "Names of 5 Verdant gameobject entries (270945, 273297, "
                  "281597,"),
]

NEGATIVE_CHECKS = [
    ("no estimated coordinate", "estimated coordinate"),
    ("no navmesh confirmed", "navmesh confirmed"),
    ("no direct inspection", "verified by direct inspection"),
    ("no todo", "TODO"),
    ("no fixme", "FIXME"),
    ("no damageers", "damageers"),
    ("no placeholder", "placeholder"),
]


def run_static(text):
    flat = norm(text)
    lines, fails = [], []
    n = flat.count("unverified")
    hit = n >= UNVERIFIED_MIN
    lines.append("    %-24s %s (%d >= %d)" % ("unverified count",
                 "ok" if hit else "FAIL", n, UNVERIFIED_MIN))
    if not hit:
        fails.append("unverified count")
    for name, lit in STATIC_CHECKS:
        ok = norm(lit) in flat
        lines.append("    %-24s %s" % (name, "ok" if ok else "MISSING"))
        if not ok:
            fails.append(name)
    for name, lit in NEGATIVE_CHECKS:
        ok = norm(lit) not in flat
        lines.append("    %-24s %s" % (name, "ok" if ok else "PRESENT!"))
        if not ok:
            fails.append(name)
    return fails, lines


MUTATIONS = [
    ("heading", "- COMPLETED ===\n\nContext", "- DRAFT ===\n\nContext"),
    ("done", "DONE - step 1 of the Islands set complete",
     "DONE - step 1 of the Islands set is complete"),
    ("tot n", "Normal 6,000 Azerite.", "Normal 6,100 Azerite."),
    ("tot h", "Heroic 9,000 Azerite.", "Heroic 9,100 Azerite."),
    ("tot m", "Mythic 12,000 Azerite.", "Mythic 12,100 Azerite."),
    ("tot p", "PvP 12,000 Azerite (same as Mythic",
     "PvP 12,500 Azerite (same as Mythic"),
    ("weekly", "36,000 Azerite per week (was 40,000",
     "37,000 Azerite per week (was 40,000"),
    ("ratio", "6 Normal or 4 Heroic or", "6 Normal or 5 Heroic or"),
    ("diff ids", "38 = Normal, 39 = Heroic, 40 = Mythic",
     "38 = Normal, 39 = Heroic, 41 = Mythic"),
    ("maxp", "(MaxPlayers 3), 45 = PvP (MaxPlayers 6)",
     "(MaxPlayers 4), 45 = PvP (MaxPlayers 6)"),
    ("mapdiff ids", "IDs 4096/4097/4098/4171, build 34963",
     "IDs 4096/4097/4098/4172, build 34963"),
    ("d153", "153 = Teeming Island", "153 = Tempting Island"),
    ("rotation", "11 islands in the weekly rotation",
     "12 islands in the weekly rotation"),
    ("starts4", "at least 4 start locations", "at least 5 start locations"),
    ("map hav", "Havenswood - map 1814.", "Havenswood - map 1815."),
    ("map crest", "Crestfall - map 2124", "Crestfall - map 2125"),
    ("map snow", "Snowblossom Village - map 1907.",
     "Snowblossom Village - map 1908."),
    ("map ver", "Verdant Wilds - map 1882, zone 9440",
     "Verdant Wilds - map 1882, zone 9441"),
    ("entry hav", "-84.7982, -843.8871, 6.3429, o 3.9626899",
     "-84.7982, -843.8871, 6.3430, o 3.9626899"),
    ("entry ver", "14917.806, 15177.087, 10.872437, o 0",
     "14917.806, 15177.087, 10.872438, o 0"),
    ("entry snow", "2234.67, -129.747, 6.3429, o 2.34406",
     "2234.67, -129.747, 6.3429, o 2.34407"),
    ("safe ungol", "(1813, 125.644, -470.398, 0, o 0)",
     "(1813, 125.645, -470.398, 0, o 0)"),
    ("safe mire", "8926.07, 9965.83, 0, o 0", "8926.08, 9965.83, 0, o 0"),
    ("safe reef", "-898.649, 1668.74, 41.9155, o 0",
     "-898.650, 1668.74, 41.9155, o 0"),
    ("safe crest", "1190.19, -165.148, -0.367364, o 0",
     "1190.19, -165.148, -0.367365, o 0"),
    ("lfg hav", "1928 (38), 1929 (39), 1930 (40), 1931 (45),",
     "1928 (38), 1929 (39), 1930 (40), 1932 (45),"),
    ("lfg snow", "1983 (38), 1988 (39), 1989 (40), 1990 (45).",
     "1983 (38), 1988 (39), 1989 (40), 1991 (45)."),
    ("inst ver", "script scenario_verdant_wilds",
     "script scenario_verdant_wild"),
    ("spawndiff", "'38,39,40,45' on all", "'38,39,40,46' on all"),
    ("spawndiff153", "plus 153 on maps 1814, 1879, 1882, 2124.",
     "plus 153 on maps 1814, 1879, 1882, 2125."),
    ("exit z", "-2048.53, 956.798, 7.05158, o 167.31",
     "-2048.53, 956.798, 7.05158, o 167.32"),
    ("exit b", "936.776, -460.89, 8.38692, o 251.654",
     "936.776, -460.89, 8.38692, o 251.655"),
    ("spawn7200", "spawntimesecs 7200", "spawntimesecs 7201"),
    ("counts cr", "180 creature spawn rows / 75 distinct entries",
     "180 creature spawn rows / 76 distinct entries"),
    ("counts go", "34 distinct entries", "35 distinct entries"),
    ("rare hdr", "75 distinct entries (8 of them",
     "75 distinct entries (9 of them"),
    ("rare1", "15198.4, 14802.6, 18.6424", "15198.4, 14802.6, 18.6425"),
    ("rare2 name", '"Life-Tender Olvarius"', '"Life-Tender Olvaria"'),
    ("rare4", "15191, 14686.7, 0)", "15191, 14688, 0)"),
    ("rare5", "15157.8, 14644.9, -0.101324", "15157.8, 14644.9, -0.101325"),
    ("rare8", "14933.8, 14883.8, 3.22263", "14933.8, 14883.8, 3.22264"),
    ("az count 9", '"Azerite Shard" (type 10), 9 rows:',
     '"Azerite Shard" (type 10), 10 rows:'),
    ("az coord", "15246.3, 14953.7, 39.9086", "15246.3, 14953.7, 39.9087"),
    ("sack count", '"Sack of Azerite" (type 10), 5 rows:',
     '"Sack of Azerite" (type 10), 6 rows:'),
    ("pouch count", '"Pouch of Azerite" (type 10), 3 rows:',
     '"Pouch of Azerite" (type 10), 2 rows:'),
    ("chest count", '"Reinforced Chest", 3 rows:',
     '"Reinforced Chest", 4 rows:'),
    ("det coord", "14794.8, 14721.2, 6.09588", "14794.8, 14721.2, 6.09589"),
    ("shovel coord", "14678.2, 14958.9, 2.84112",
     "14678.2, 14958.9, 2.84113"),
    ("old chest", "15318.6, 15016, 44.0913", "15318.6, 15016, 44.0914"),
    ("nl 270945", "2.48005) o 3.98669", "2.48005) o 3.98670"),
    ("nl 289318", "14657, 15330.5, 0.967176", "14657, 15330.5, 0.967177"),
    ("scenery count", "269984 Sticky Starfish x2",
     "269984 Sticky Starfish x3"),
    ("uncharted stats", "66 creature spawn rows + 15 gameobject",
     "67 creature spawn rows + 15 gameobject"),
    ("pouch 1955", '291080 "Pouch of Azerite" x4 rows',
     '291080 "Pouch of Azerite" x5 rows'),
    ("crescent1", "3443.49, -144.335, 7.49805, o 16",
     "3443.49, -144.335, 7.49805, o 17"),
    ("crescent3", "3833.23, -220.333, 1.26485, o 179.846",
     "3833.23, -220.333, 1.26485, o 179.847"),
    ("proto a", "14344.9, 14823.3, 0.591667, o 0",
     "14344.9, 14823.3, 0.591668, o 0"),
    ("proto b", "14833.4, 7141.44, 5.60289, o 223.651",
     "14833.4, 7141.44, 5.60289, o 223.652"),
    ("alpha", "8.0 Islands - Forested - Prototype",
     "8.0 Islands - Forest - Prototype"),
    ("snow noinst", "instance_template row for 1907 not present",
     "instance_template row for 1907 present"),
    ("unv drop", "Entry: unverified (source TO DO; comment lists dungeon ids",
     "Entry: source TO DO; comment lists dungeon ids"),
    ("unv names", "Names of 5 Verdant gameobject entries",
     "Names of 6 Verdant gameobject entries"),
    ("ilvl", "requiredItemLevel 0,", "requiredItemLevel 1,"),
]


def _split_island_blocks(text):
    """Return {map_id: block_text} for the per-island sections."""
    blocks = {}
    starts = list(re.finditer(r"\n   ([^\n]+?) - map (\d{4})", text))
    for i, m in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        blocks[m.group(2)] = text[m.start():end]
    return blocks


def stage3(corpora):
    token_map = {
        "isl_sql": [
            ("lfg snow row", "(1983, 'Snowblossom Village 38', 2234.67, "
                             "-129.747, 6.3429, 2.34406, 0, 28153),"),
            ("lfg hav row", "(1928, 'Havenswood 38', -84.7982, -843.8871, "
                            "6.3429, 3.9626899, 0, 28153),"),
            ("lfg dread row", "(1734, 'The Dread Chain 38', 1424.8444, "
                              "457.19388, 6.432567, 4.33277, 0, 28153),"),
            ("lfg mire row", "(1723, 'The Rotting Mire 38', 9153.376, "
                             "9691.307, 6.3429, 1.5364347, 0, 28153),"),
            ("lfg jor row", "(1932, 'Jorundall 38', 14404.991, 11490.11, "
                            "6.3429, 4.09958, 0, 28153),"),
            ("lfg ver row", "(1724, 'Verdant Wilds 38', 14917.806, 15177.087, "
                            "10.872437, 0, 0, 28153),"),
            ("lfg reef row", "(1735, 'Whispering Reef 38', -913.84894, "
                             "2159.6199, 28.34297, 0, 0, 28153),"),
            ("lfg reef pvp", "(1908, 'Whispering Reef 45',"),
            ("lfg jor 153", "(2041, 'Jorundall 153 pvp',"),
            ("todo crest", "TO DO"),
            ("todo names", "Crestfall 2124"),
            ("spawn153 hav", "spawnDifficulties`='38,39,40,45,153' WHERE "
                             "`map`=1814"),
            ("spawn153 crest", "spawnDifficulties`='38,39,40,45,153' WHERE "
                               "`map`=2124"),
            ("inst hav", "(1814, 1642, 'scenario_havenswood', 1, 1),"),
            ("inst crest", "(2124, 1642, 'scenario_crestfall', 1, 1),"),
            ("island.sql deletes", "DELETE FROM `instance_template` WHERE "
                                   "`map` IN (1814,1892,1893,1879,2124,1897,"
                                   "1813,1882,1898,1883);"),
        ],
        "un_charted": [
            ("cr header", "INSERT INTO `creature` (`guid`, `id`, `map`"),
            ("sample verdant", "(282102549, 135182, 1882, 9440, 9440, '38'"),
            ("rare1 row", ", 15198.4, 14802.6, 18.6424, 4.44993,"),
            ("rare2 row", ", 14855.3, 14816.4, 6.34723, 2.22222,"),
            ("rare3 row", ", 14912.7, 14627, 0, 1.572,"),
            ("rare8 row", ", 14933.8, 14883.8, 3.22263, 2.75301,"),
            ("shard row", ", 15246.3, 14953.7, 39.9086, 2.88116,"),
            ("sack row", ", 14975.5, 14845.3, 6.78653, 5.28633,"),
            ("chest row", ", 15318.6, 15016, 44.0913, 2.36365,"),
            ("detector row", ", 14794.8, 14721.2, 6.09588, 1.28894,"),
            ("go header", "INSERT INTO `gameobject` (`guid`, `id`, `map`"),
            ("uncharted zone", ", 1955, 9778,"),
        ],
        "mapdiff": [
            ("diff38", "(4096, '', 38, 0, 0, 3, 0, 0, 0, 0, 1882, 34963),"),
            ("diff39", "(4097, '', 39, 0, 0, 3, 0, 0, 0, 0, 1882, 34963),"),
            ("diff40", "(4098, '', 40, 0, 0, 3, 0, 0, 0, 0, 1882, 34963),"),
            ("diff45", "(4171, '', 45, 0, 0, 6, 0, 0, 0, 0, 1882, 34963)"),
        ],
        "tc_safe": [
            ("safe ungol", "(6401,1813,125.644,-470.398,0,0,'Un\\'gol "
                           "Ruins'),"),
            ("safe hav", "(6969,1814,-266.278,-1308.08,43.1385,0,"
                         "'Havenswood'),"),
            ("safe jor", "(6971,1879,14198.8,11071.3,12.2526,0,'Jorundall'),"),
            ("safe ver", "(6566,1882,14500.7,15096.6,0,0,'Verdant Wilds'),"),
            ("safe reef", "(6576,1883,-898.649,1668.74,41.9155,0,"
                          "'The Whispering Reef'),"),
            ("safe mire", "(6565,1892,8926.07,9965.83,0,0,'The Rotting "
                          "Mire'),"),
            ("safe dread", "(6570,1893,1301.26,-352.104,0.303792,0,"
                           "'The Dread Chain'),"),
            ("safe molten", "(6581,1897,1753.93,1390.02,260.916,0,"
                            "'The Molten Cay'),"),
            ("safe skit", "(6567,1898,8791.45,-5561.79,0,0,'Skittering "
                          "Hollow'),"),
            ("safe snow", "(7219,1907,1873.58,-213.153,3.0708,0,"
                          "'Snowblossom Village'),"),
            ("safe crest", "(7220,2124,1190.19,-165.148,-0.367364,0,"
                           "'Crestfall'),"),
            ("crescent a1", "(6030,1645,3443.49,-144.335,7.49805,16,"
                            "'Islands - Crescent Isle - Alliance - Setup 1'),"),
            ("crescent h3", "(6173,1645,3483.39,-129.571,0.763218,7.52344,"
                            "'Islands - Crescent Isle - Horde - Setup 3'),"),
            ("crescent safe", "(6096,1645,3485.54,-128.806,0.887992,0,"
                              "'Islands - Crescent Isle - Safe Loc'),"),
            ("crescent bots", "(6387,1645,3641.79,-245.13,2.61367,0,"
                              "'8.0 Islands - Crescent Isle - Bots '),"),
            ("tropical", "(6381,1780,14344.9,14823.3,0.591667,0,"
                         "'Islands - Tropical Isle - Horde - Setup 1'),"),
            ("gilnean", "(6382,1780,14833.4,7141.44,5.60289,223.651,"
                        "'Islands - Gilnean Isle - Horde - Setup 1'),"),
            ("exit z", "(7035,1642,-2048.53,956.798,7.05158,167.31,"
                       "'Islands - Port of Zandalar Exit Loc'),"),
            ("exit b", "(7036,1643,936.776,-460.89,8.38692,251.654,"
                       "'Islands - Boralus Harbor Exit Loc'),"),
        ],
        "mtt_0507": [
            ("crystal name", "(289437, 10, 47692, 'Azerite Crystal'"),
            ("pouch name", "(290913, 10, 49910, 'Pouch of Azerite'"),
            ("pouch 1955", "(291080, 10, 49910, 'Pouch of Azerite'"),
            ("re-spawn", "DELETE FROM `gameobject` WHERE `id` IN (291080, "
                         "290913);"),
        ],
        "mtt_safe": [
            ("dread cross", "('6570','1893','1301.26','-352.104',"
                            "'0.303792','0','The Dread Chain'),"),
            ("molten cross", "('6581','1897','1753.93','1390.02',"
                             "'260.916','0','The Molten Cay'),"),
            ("skit cross", "('6567','1898','8791.45','-5561.79','0','0',"
                           "'Skittering Hollow'),"),
        ],
        "shared": [
            ("enum n", "LOOT_MODE_NORMAL_ISLAND"),
            ("enum h", "LOOT_MODE_HEROIC_ISLAND"),
            ("enum m", "LOOT_MODE_MYTHIC_ISLAND"),
            ("enum p", "LOOT_MODE_PVP_ISLAND"),
            ("enum t", "LOOT_MODE_TEEMING_ISLAND"),
        ],
        "rares": [(i, "%s, --%s" % (i, RARE_NAMES[i])) for i in RARE_IDS],
        "dict110": [("137579", 'entries[137579] = { ["name"] = "Unbound '
                               'Azerite" }')],
        "dict112": [(i, 'entries[%s] = { ["name"] = "%s" }'
                        % (i, RARE_NAMES[i]))
                    for i in ["139218", "139411", "139415", "139416",
                              "139418", "139681"]],
        "dict114": [("140992", 'entries[140992] = { ["name"] = "Corpseburster"'
                               ' }')],
        "go_tpl": [
            (e, "values('%s','%d'," % (e, GO_TYPE_NAME[e][1]))
            for e in list(GO_TYPE_NAME)
            if e not in ("289437", "290913")  # named in mtt_0507 only
        ] + [
            ("shard name", "'Azerite Shard',"),
            ("chunk name", "'Azerite Chunk',"),
            ("growth name", "'Azerite Growth',"),
            ("sack name", "'Sack of Azerite',"),
            ("bag name", "'Bag of Azerite',"),
            ("oldchest name", "'Old Chest',"),
            ("reinforced name", "'Reinforced Chest',"),
            ("rotting name", "'Rotting Wooden Chest',"),
            ("detector name", "'Azerite Detector',"),
            ("shovel name", "'Shovel',"),
            ("sand name", "'Sand Pile',"),
            ("starfish name", "'Sticky Starfish',"),
            ("pumpkin name", "'Unripe Pumpkin',"),
            ("spineapple o", "'Orange Spineapple',"),
            ("spineapple y", "'Yellow Spineapple',"),
            ("flower name", "'Giant Flower',"),
            ("carn name", "'Carnivorous Plant',"),
            ("pillar name", "'Pillar of the Watchers',"),
            ("boomerang name", "'Crude Boomerang',"),
            ("frigate name", "'Kul\\'Tiran Frigate','"),
            ("paku name", "'Breath of Pa\\'ku','"),
            ("collision name", "'Collision',"),
        ],
    }
    return source_stage(corpora, token_map)


def _parse_spawns(text):
    """(creature_rows, gameobject_rows) dicts for the spawn file."""
    import csv
    import io

    def rows_for(table):
        out = []
        pat = re.compile(
            r"INSERT INTO `%s` \(([^)]*)\)\s*VALUES\s*(.*?);\s*"
            r"(?:INSERT|DELETE|$)" % table, re.S | re.I)
        for m in pat.finditer(text):
            cols = [c.strip().strip("`") for c in m.group(1).split(",")]
            for row in csv.reader(io.StringIO(m.group(2)), quotechar="'",
                                  escapechar="\\"):
                row = [x.strip() for x in row]
                if len(row) == len(cols):
                    out.append(dict(zip(cols, row)))
        return out

    return rows_for("creature"), rows_for("gameobject")


def stage4(text, corpora, probe=False):
    fails, lines = [], []

    def bad(msg):
        fails.append(msg)

    # -- island blocks: entry/safe/unverified placement
    blocks = _split_island_blocks(text)
    if len(blocks) < 11:
        bad("island blocks %d" % len(blocks))
    lines.append("    island sections parsed:                  %d"
                 % len(blocks))
    for name, (m, entry) in ISLES.items():
        blk = blocks.get(str(m))
        if blk is None:
            bad("missing block map %d" % m)
            continue
        if entry is None:
            if "Entry: unverified" not in blk:
                bad("map %d should be Entry: unverified" % m)
        else:
            x, y, z, o = entry
            lit = norm("(%d, %s, %s, %s, o %s)" % (m, _s(x), _s(y), _s(z),
                                                   _s(o)))
            if lit not in norm(blk):
                bad("entry coord map %d" % m)
    lines.append("    entry/unverified placement per island: %s"
                 % ("ok" if not [f for f in fails
                                 if f.startswith(("entry", "missing block",
                                                  "map "))]
                    else "FAIL"))

    # -- island.sql derived: lfg rows, instances, spawnDifficulties
    isl = corpora["isl_sql"]
    lfg_rows = re.findall(
        r"\((\d+), '([^']+?) (\d+)', (-?[\d.]+), (-?[\d.]+), (-?[\d.]+), "
        r"(-?[\d.]+), (-?\d+), (\d+)\)", isl)
    flat = norm(text)
    seen_isles = set()
    for did, nm, diff, x, y, z, o, ilvl, build in lfg_rows:
        if nm not in LFG_NAME_MAP:
            bad("unexpected lfg name %r" % nm)
            continue
        seen_isles.add(nm)
        m = LFG_NAME_MAP[nm]
        blk = blocks.get(str(m), "")
        if did not in blk:
            bad("lfg id %s missing from map %d block" % (did, m))
        if diff != "38":
            continue  # doc quotes the primary (Normal) row only
        lit = "(%d, %s, %s, %s, o %s)" % (m, x, y, z, o)
        if norm(lit) not in flat:
            bad("lfg entry %s %s" % (nm, lit))
    if seen_isles != set(LFG_NAME_MAP):
        bad("lfg islands diff %s" % (set(LFG_NAME_MAP) ^ seen_isles))
    lines.append("    lfg queue rows -> doc coords:           %d/7 islands"
                 % len(seen_isles))
    inst = re.findall(r"\((\d{4}), 1642, '([a-z_]+)', 1, 1\)", isl)
    inst_ok = True
    for m, script in inst:
        if norm("parent 1642, script %s" % script) not in flat:
            bad("instance script %s" % script)
            inst_ok = False
    if len(inst) != 10:
        bad("instance rows %d" % len(inst))
    if re.search(r"\(1907, 1642,", isl):
        bad("1907 instance row present in source but doc says absent")
    lines.append("    instance_template rows -> doc:          %d (%s)"
                 % (len(inst), "ok" if inst_ok else "FAIL"))

    # -- world_safe_locs derived
    safe = corpora["tc_safe"]
    safe_rows = re.findall(
        r"\((\d+),(\d+),(-?[\d.]+),(-?[\d.]+),(-?[\d.]+),(-?[\d.]+),"
        r"'((?:[^'\\]|\\.)*)'\)", safe)
    want_maps = {m for m, _ in ISLES.values()}
    found = {}
    extra = []
    for _gid, m, x, y, z, o, nm in safe_rows:
        m = int(m)
        if m in want_maps:
            found[m] = (x, y, z, o, nm)
        elif m in (1645, 1780, 1642, 1643) and "Islands -" in nm.replace(
                "\\", "") or (m == 1645 and "Crescent Isle" in nm):
            extra.append((m, x, y, z, o, nm))
    miss = [m for m in want_maps if m not in found]
    if miss:
        bad("safe locs missing for maps %s" % sorted(miss))
    for m, (x, y, z, o, nm) in found.items():
        lit = "(%d, %s, %s, %s, o %s)" % (m, x, y, z, o)
        if norm(lit) not in flat:
            bad("safe loc %s" % lit)
    cres = [r for r in extra if r[0] == 1645 and "Crescent Isle" in r[5]]
    if len(cres) < 8:
        bad("crescent rows %d" % len(cres))
    for m, x, y, z, o, nm in cres + [r for r in extra if r[0] == 1780]:
        lit = "(%d, %s, %s, %s, o %s)" % (m, x, y, z, o)
        if norm(lit) not in flat:
            bad("proto safe %s" % lit)
    exits = [r for r in extra if r[0] in (1642, 1643)]
    if len(exits) != 2:
        bad("exit locs %d" % len(exits))
    for m, x, y, z, o, nm in exits:
        lit = "(%d, %s, %s, %s, o %s)" % (m, x, y, z, o)
        if norm(lit) not in flat:
            bad("exit loc %s" % lit)
    lines.append("    world_safe_locs -> doc:                 11 islands + "
                 "%d crescent + 2 exits" % len(cres))

    # -- Verdant spawns derived
    cr_rows, go_rows = _parse_spawns(corpora["un_charted"])
    c1882 = [r for r in cr_rows if r["map"] == "1882"]
    g1882 = [r for r in go_rows if r["map"] == "1882"]
    c1955 = [r for r in cr_rows if r["map"] == "1955"]
    g1955 = [r for r in go_rows if r["map"] == "1955"]
    stats = (len(c1882), len(set(r["id"] for r in c1882)),
             len(g1882), len(set(r["id"] for r in g1882)))
    if stats != (180, 75, 67, 34):
        bad("verdant stats %s" % (stats,))
    if (len(c1955), len(g1955)) != (66, 15):
        bad("uncharted stats %s" % ((len(c1955), len(g1955)),))
    if set(r["spawntimesecs"] for r in c1882 + g1882) != {"7200"}:
        bad("spawn seconds set")
    if set(r["spawnDifficulties"] for r in c1882 + g1882) != {"'38'"}:
        bad("spawnDiff set")
    lines.append("    Verdant spawn stats (cr/cr-id/go/go-id): %d/%d/%d/%d"
                 % stats)
    lines.append("    Uncharted (1955) cr/go rows:            %d/%d"
                 % (len(c1955), len(g1955)))

    # rare ids: RareScanner set intersect spawns
    raresrc = set(re.findall(r"^\s*(\d{6,7}), --", corpora["rares"], re.M))
    spawn_ids = set(r["id"] for r in c1882)
    derived_rares = sorted(raresrc & spawn_ids)
    rsec = text.split("Rares (entry, name, coordinates):", 1)[-1].split(
        "Azerite node / azerite loot objects", 1)[0]
    doc_rares = sorted(set(re.findall(
        r'^\s+(\d{6}) "([^"]+)":\s+\(1882,', rsec, re.M)))
    if derived_rares != RARE_IDS:
        bad("derived rares %s" % derived_rares)
    if [d[0] for d in doc_rares] != RARE_IDS:
        bad("doc rares %s" % [d[0] for d in doc_rares])
    for rid, rname in doc_rares:
        if RARE_NAMES.get(rid) != rname:
            bad("rare name %s" % rid)
        rows = [r for r in c1882 if r["id"] == rid]
        if len(rows) != 1:
            bad("rare %s rows %d" % (rid, len(rows)))
            continue
        r = rows[0]
        lit = "(1882, %s, %s, %s)" % (r["position_x"], r["position_y"],
                                      r["position_z"])
        if norm(lit) not in flat:
            bad("rare coord %s" % lit)
    lines.append("    RareScanner intersection spawn rares:    %d/8, all "
                 "coords in doc" % len(derived_rares))

    # azerite/chest/event/nameless full row presence
    def rows_present(ids, label):
        n, miss_n = 0, 0
        for i in ids:
            for r in [r for r in g1882 if r["id"] == i]:
                lit = "(1882, %s, %s, %s)" % (r["position_x"],
                                              r["position_y"],
                                              r["position_z"])
                n += 1
                if norm(lit) not in flat:
                    miss_n += 1
                    bad("%s coord %s %s" % (label, i, lit))
        lines.append("    %-28s %d/%d row coords in doc"
                     % (label + ":", n - miss_n, n))
        return n

    rows_present(AZERITE_GO, "azerite GO rows")
    rows_present(CHEST_GO, "chest GO rows")
    rows_present(EVENT_GO, "event GO rows")
    rows_present(NAMELESS_GO, "nameless GO rows")

    # row counts claimed in doc vs derived
    from collections import Counter
    cnt = Counter(r["id"] for r in g1882)
    for i in AZERITE_GO:
        m = re.search(r'%s "([^"]+)" \(type (\d+)\), (\d+) rows?' % i, text)
        if not m:
            bad("count line %s" % i)
            continue
        if int(m.group(3)) != cnt[i]:
            bad("count claim %s %d != %d" % (i, int(m.group(3)), cnt[i]))
        if int(m.group(2)) != GO_TYPE_NAME[i][1]:
            bad("type claim %s" % i)
    m = re.search(r'270914 "([^"]+)", (\d+) rows', text)
    if not m or int(m.group(2)) != cnt["270914"]:
        bad("count claim 270914")
    # single-row chests / detectors / shovels
    for i in ("270913", "271647", "281896", "299039"):
        if cnt[i] != 1:
            bad("single row %s has %d" % (i, cnt[i]))
    for i in ("282625", "282628"):
        m = re.search(r'%s "([^"]+)", (\d+) rows' % i, text)
        if not m or int(m.group(2)) != cnt[i]:
            bad("count claim %s" % i)
    # scenery counts
    for i in SCENERY_GO:
        m = re.search(r"\b%s [^,]*? x(\d+)" % i, text)
        if not m:
            bad("scenery line %s" % i)
            continue
        if int(m.group(1)) != cnt[i]:
            bad("scenery count %s %s != %d" % (i, m.group(1), cnt[i]))
    lines.append("    GO row-count claims vs derived counts: checked")

    # names via mtt_0507 + go_tpl
    if "(289437, 10, 47692, 'Azerite Crystal'" not in corpora["mtt_0507"]:
        bad("crystal template row")
    for lit in ('289437 "Azerite Crystal" (type 10)',
                '290913 "Pouch of Azerite" (type 10)'):
        if norm(lit) not in flat:
            bad("name claim %s" % lit)
    # map_difficulty derived
    md = re.findall(r"\((\d+), '[^']*', (\d+), 0, 0, (\d+), 0, 0, 0, 0, "
                    r"1882, 34963\)", corpora["mapdiff"])
    md_map = {d: p for _i, d, p in md}
    if md_map != {"38": "3", "39": "3", "40": "3", "45": "6"}:
        bad("map_difficulty %s" % md_map)
    if norm("(MaxPlayers 3), 45 = PvP (MaxPlayers 6)") not in flat:
        bad("maxplayers claim")
    lines.append("    map_difficulty 38/39/40/45 players:     %s"
                 % "/".join(md_map.get(k, "?") for k in ("38", "39", "40",
                                                         "45")))

    # snow script existence
    import subprocess
    res = subprocess.run(
        ["gh", "api", "repos/%s/contents/%s" % (TCDEV,
                                                SNOW_SCRIPT.replace(" ", "%20"))],
        capture_output=True, text=True)
    if res.returncode != 0:
        bad("snow script missing")
    if norm("scenario_snowblossom_village.cpp exists") not in flat:
        bad("snow script claim in doc")
    lines.append("    snowblossom script exists (API):        %s"
                 % ("yes" if res.returncode == 0 else "NO"))

    # totals: internal arithmetic (network-restricted sources)
    tot = {"n": 6000, "h": 9000, "m": 12000, "p": 12000}
    checks = [
        ("Normal 6,000 Azerite." in text, "tot n"),
        ("Heroic 9,000 Azerite." in text, "tot h"),
        ("Mythic 12,000 Azerite." in text, "tot m"),
        ("PvP 12,000 Azerite (same as Mythic" in text, "tot p"),
        (tot["n"] * 6 == 36000 and tot["h"] * 4 == 36000
         and tot["m"] * 3 == 36000, "weekly math"),
        ("36,000 Azerite per week" in text, "weekly claim"),
    ]
    for ok, label in checks:
        if not ok:
            bad("totals %s" % label)
    lines.append("    azerite totals internal consistency:    ok "
                 "(web sources not reachable from sandbox)")

    # coord trace over all corpora
    ok_t, lines_t, missing_t = coord_trace(text, corpora)
    lines.append("    %s" % lines_t[-1].strip())
    if not ok_t:
        bad("coord trace %s" % (missing_t[:3],))
    return fails, lines


def _s(v):
    """Format a source number exactly as written."""
    if isinstance(v, str):
        return v
    if float(v) == int(v):
        return str(int(v))
    return repr(v)


def stage5(text, corpora):
    lines, fails = [], []
    # injection probes
    probes = [("TODO", "no todo"),
              ("verified by direct inspection", "no direct inspection"),
              ("estimated coordinate", "no estimated coordinate")]
    for extra, key in probes:
        f, _ = run_static(text + "\n%s.\n" % extra)
        r = key in f
        lines.append("    injection probe (%s):%s"
                     % (extra[:28], " detected" if r else " NOT DETECTED"))
        if not r:
            fails.append("probe %s" % key)
    stripped = text.replace("unverified", "verified")
    f, _ = run_static(stripped)
    r = "unverified count" in f
    lines.append("    injection probe (unverified stripped):%s"
                 % (" detected" if r else " NOT DETECTED"))
    if not r:
        fails.append("unverified probe")
    # 404 control
    import subprocess
    res = subprocess.run(
        ["gh", "api", "-X", "GET",
         "repos/TCDEVEmu/AtalDazar_BFA/contents/DoesNotExist.sql"],
        capture_output=True, text=True)
    absent = res.returncode != 0
    lines.append("    control: bogus repo path 404:                  %s"
                 % ("yes" if absent else "NO"))
    if not absent:
        fails.append("404 control")
    return fails, lines


def main():
    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()
    print("=" * 68)
    print("AUDIT: Islands_Maps_COMPLETED.txt (Islands 1)")
    print("=" * 68)

    fails1, lines1 = run_static(text)
    total1 = len(STATIC_CHECKS) + len(NEGATIVE_CHECKS) + 1
    print("\n[1] Static checks: %d/%d passed" % (total1 - len(fails1),
                                                 total1))
    if fails1:
        print("    FAILED: %s" % ", ".join(fails1))
        for ln in lines1:
            if "MISSING" in ln or "PRESENT" in ln:
                print(ln)
    else:
        print("    all static checks passed")

    print("\n[2] Mutation testing (%d mutations)" % len(MUTATIONS))
    undetected = []
    for name, old, new in MUTATIONS:
        mutated = text.replace(old, new)
        if mutated == text:
            undetected.append(name + " (no-op)")
            continue
        f, _ = run_static(mutated)
        if not f:
            undetected.append(name)
    print("    detected %d/%d"
          % (len(MUTATIONS) - len(undetected), len(MUTATIONS)))
    if undetected:
        print("    UNDETECTED: %s" % ", ".join(undetected))

    print("\n[3] Source cross-check (upstream files fetched live)")
    corpora = {}
    for key, (repo, path) in FILES.items():
        corpora[key] = gh_content(repo, path)
    for key, (repo, path) in RAW_FILES.items():
        corpora[key] = gh_raw(repo, path)
    missing = [k for k, v in corpora.items() if not v]
    if missing:
        print("    CORPUS FETCH FAILED: %s" % missing)
        return 1
    ok3, lines3 = stage3(corpora)
    for ln in lines3:
        print(ln)
    if not ok3:
        print("    SOURCE CROSS-CHECK FAILED")
    probe_undetected = mutation_probe(
        corpora,
        {"un_charted": [("rare1 row in source",
                         ", 15198.4, 14802.6, 18.6424, 4.44993,")]},
        lambda t: t.replace(", 15198.4, 14802.6, 18.6424, 4.44993,",
                            ", 15198.4, 14802.6, 18.6425, 4.44993,"))
    print("    reaction to tampered source (verified): %s"
          % ("yes" if probe_undetected == [] else "NO"))
    if probe_undetected != []:
        ok3 = False

    print("\n[4] Derived values recomputed from source bodies")
    fails4, lines4 = stage4(text, corpora)
    for ln in lines4:
        print(ln)
    if fails4:
        print("    DERIVED STAGE FAILED: %s" % ", ".join(str(f) for f in
                                                         fails4))
    # coordinate probes: doc tamper must be caught by derived compares
    doc_probes = [
        ("rare coord", "15198.4, 14802.6, 18.6424",
         "15198.4, 14802.6, 18.6425"),
        ("entry coord", "14917.806, 15177.087, 10.872437",
         "14917.806, 15177.087, 10.872438"),
        ("safe coord", "14500.7, 15096.6, 0, o 0",
         "14500.7, 15096.7, 0, o 0"),
        ("go row coord", "15246.3, 14953.7, 39.9086",
         "15246.3, 14953.7, 39.9087"),
    ]
    for label, old, new in doc_probes:
        mutated = text.replace(old, new)
        if mutated == text:
            print("    doc probe (%s):     no-op!" % label)
            fails4.append("probe no-op " + label)
            continue
        pf, _ = stage4(mutated, corpora, probe=True)
        reacted = bool(pf)
        print("    doc probe (%s):     %s" % (
            label, "reacts" if reacted else "NOT DETECTED"))
        if not reacted:
            fails4.append("probe " + label)

    print("\n[5] Absence / injection")
    fails5, lines5 = stage5(text, corpora)
    for ln in lines5:
        print(ln)
    if fails5:
        print("    ABSENCE STAGE FAILED: %s" % ", ".join(fails5))

    all_fails = fails1 + undetected + ([] if ok3 else ["source"]) + \
        fails4 + fails5
    print("\n" + "=" * 68)
    if not all_fails:
        print("AUDIT RESULT: PASS")
        print("  static checks: %d/%d" % (total1, total1))
        print("  mutations:     %d/%d" % (len(MUTATIONS), len(MUTATIONS)))
        return 0
    print("AUDIT RESULT: FAIL")
    print("  %d failing item(s): %s" % (len(all_fails), all_fails))
    return 1


if __name__ == "__main__":
    sys.exit(main())
