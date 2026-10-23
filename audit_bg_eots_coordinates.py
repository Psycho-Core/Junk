#!/usr/bin/env python3
"""Audit: Coordinates_Eye_of_the_Storm_COMPLETED.txt (BG coords step 3).

Stages:
  1. Static exact-literal checks (whitespace-normalised) + negatives.
  2. Mutation testing - every mutation must break a static check.
  3. Live source cross-check: HavenWoW BattlegroundEY.h/.cpp +
     Battleground.h, TrinityCore 8.x world dump, AzerothCore template.
  4. Derived recompute: all 33 dump rows in the document, every script
     coordinate float, all route legs/directs, flag runs, tower pairs,
     graveyard table, z-relief ranges, home-pair distances - coordinate
     trace + probes.
  5. Absence claims + injection probes + gh 404 control.
"""

import math
import re
import subprocess
import sys

sys.path.insert(0, ".")
from audit_common import gh_content, source_stage, mutation_probe, coord_trace

DOC = ("# Ai Research prompts/Battleground_Coordinates/"
       "Coordinates_Eye_of_the_Storm_COMPLETED.txt")
HAVEN = "HavenWoW/BFA-HavenCore"
TC = "TrinityCore/TrinityCore"
AC = "azerothcore/azerothcore-wotlk"

LC_FILES = {
    "eyh": "src/server/game/Battlegrounds/Zones/BattlegroundEY.h",
    "eyc": "src/server/game/Battlegrounds/Zones/BattlegroundEY.cpp",
    "bh": "src/server/game/Battlegrounds/Battleground.h",
}
TC_DUMP = "sql/old/8.x/world/19071_2020_06_17/2019_10_26_01_world.sql"
AC_TEMPLATE = "data/sql/base/db_world/battleground_template.sql"

# rows whose triples the document must contain (row-stage checks)
DOC_IDS = list(range(1103, 1134)) + [3772, 3773, 3951, 3952] + \
    [2841, 2843, 2847, 2849, 2851, 2853, 4000, 4001] + \
    [2855, 2879, 2885, 2891, 2893, 2903]
# full map-968 set for the diff recompute (33 rows)
R968 = [2841, 2843, 2847, 2849, 2851, 2853] + \
    list(range(2855, 2904, 2)) + [4000, 4001]
ALL_IDS = sorted(set(DOC_IDS) | set(R968))
# (map-968 row, map-566 counterpart) pairs
PAIRS968 = [(2841, 1104), (2843, 1103), (2847, 1106), (2849, 1107),
            (2851, 1105), (2853, 1108), (4001, 3772), (4000, 3773)] + \
           [(2855 + 2 * i, 1109 + i) for i in range(25)]

UNVERIFIED_MIN = 17


def norm(s):
    return re.sub(r"\s+", " ", s)


# ---------------------------------------------------------------- stage 1
STATIC_CHECKS = [
    ("heading completed", "=== EYE OF THE STORM COORDINATES - BFA 8.3.7 "
                          "(TRINITYCORE) - COMPLETED ==="),
    ("step numbering", "prompt 3 of 8 (Eye of the Storm, map 566)"),
    ("done line", "DONE - step 3 of 8 complete"),
    ("no-estimate policy", "nothing is estimated"),
    ("unverified policy", 'the entry says "unverified"'),
    # orientation
    ("no compass claim", "makes NO compass claims about Eye of the Storm"),
    ("images unreadable", "wiki map images could not be read"),
    ("z relief starts", "51-59 yd above the tower platforms"),
    ("z relief center", "30-37 yd below the towers"),
    ("pathing caveat", "NOT walkable-path measurements"),
    ("navmesh caveat", "no pathing/navmesh source for map 566 could be read"),
    ("band y1a", "y 1393.65 / 1402.36"),
    ("band y1b", "y 1729.68 /"),
    ("band x1", "x 2044.28 / 2048.83"),
    ("band x2", "x 2286.56 / 2284.48"),
    ("home a mt", "Mage Tower (275 yd) and Draenei Ruins"),
    ("home a dr", "(306 yd)"),
    ("home h be", "Blood Elf Tower (286 yd) and Fel Reaver Ruins (307 yd)"),
    # map id
    ("map line", "566 = Eye of the Storm"),
    ("instance row", '"566 ... NetherstormBG ... [[:Eye of the Storm]] ... '
                     'Battleground ...'),
    ("single map", "map 968 is the Rated Eye of the Storm"),
    ("rated instance row", "968 ... cata-inline ... Eye of the Storm|Rated "
                           "Eye of the Storm"),
    ("rated twins", "rated twins"),
    ("968 queue unver", "whether your server queues map 968 (and with which"),
    ("dup ff 3951", 'id 3951 "Forcefield Target 000" (566, 1808.21, '
                    '1539.49, 1267.41) o 360'),
    ("dup ff note", "second, coordinate-identical pair on map 566"),
    ("queue unver", "Which map id and template row your server's "
                    "battleground_template queues is unverified"),
    # starts
    ("start a id", 'Alliance, map 566: id 1103 "Netherstorm BG - Graveyard '
                   '(Alliance Start)"'),
    ("start a row", "(566, 2523.76, 1596.13, 1247.7)   o 180"),
    ("start h id", 'Horde, map 566: id 1104 "Netherstorm BG - Graveyard '
                   '(Horde Start)"'),
    ("start h row", "(566, 1803.02, 1539.97, 1249.19)  o 0"),
    ("double duty", "the same rows double as each"),
    ("ac row", "(7,8,15,61,80,1103,3.03123,1104,0.055761,10,1,'','Eye of "
               "The Storm"),
    ("ac a loc", "AllianceStartLoc = 1103 (AllianceStartO 3.03123 rad)"),
    ("ac h loc", "HordeStartLoc = 1104 (HordeStartO 0.055761 rad)"),
    ("ac script empty", "ScriptName is empty"),
    ("door a", "gameobject 184719 (Alliance door) (566, 2527.6, 1596.91, "
               "1246.0)"),
    ("door a o", "o -3.12414"),
    ("door h", "gameobject 184720 (Horde door) (566, 1803.21, 1539.49, "
               "1246.0)"),
    ("door h o", "o 3.14159"),
    ("door dist a", "Alliance start to 184719 = 4 yd"),
    ("door dist h", "Horde start to 184720 = 1 yd"),
    ("ff row 3772", 'id 3772 "Forcefield Target 000" (566, 1808.21, 1539.49,'
                    " 1267.41) o 360"),
    ("ff row 3773", 'id 3773 "Forcefield Target 001" (566, 2523.51, 1596.58,'
                    " 1269.27) o 180"),
    ("exploit h", "EY_EXPLOIT_TELEPORT_LOCATION_HORDE"),
    ("exploit a", "EY_EXPLOIT_TELEPORT_LOCATION_ALLIANCE"),
    ("ff dz h", "+18.2 yd in z"),
    ("ff dz a", "+21.6 yd in z"),
    ("bubble", "start inside a bubble for the first minute"),
    # map 968 rated set
    ("968 desc", '"Netherstorm BG 2.0" / "Netherstorm 2.0" - 33 rows: 6 '
                 "graveyards"),
    ("968 gy 2841", "id 2841 (968, 1807.06, 1539.16, 1247.85)  o 0"),
    ("968 gy 2843", "id 2843 (968, 2523.35, 1596.49, 1247.52)  o 180"),
    ("968 gy 2847", "id 2847 (968, 2012.4, 1455.41, 1172.2)  o 65"),
    ("968 gy 2849", "id 2849 (968, 2351.22, 1455.63, 1185.33)  o 270"),
    ("968 gy 2851", "id 2851 (968, 2013.06, 1677.24, 1182.13)  o 340"),
    ("968 gy 2853", "id 2853 (968, 2355.3, 1683.71, 1173.15)  o 225"),
    ("968 ff 4001", "id 4001 (968, 1808.21, 1539.49, 1267.41)  o 360"),
    ("968 ff 4000", "id 4000 (968, 2523.51, 1596.58, 1269.27)  o 180"),
    ("968 catchers", "ids 2855-2903 stepping by 2 (25 rows, 23 of them"),
    ("968 ex 2855", "id 2855 (968, 2626.9, 1457.85, 1225.54) o 180"),
    ("968 ex 2903", "id 2903 (968, 2117.21, 1807.68, 1171.55) o 180"),
    ("968 ident claim", "26 of the 33 rows are coordinate-identical to "
                        "their map-566 counterpart"),
    ("968 start delta", "differing from the section-2 rows by up to 4.04 yd"),
    ("968 001 claim", "five catcher rows differing by exactly 0.01 in a "
                      "single coordinate"),
    ("968 diff 2879", "id 2879 (968, 1796.22, 1341.52, 1188.57)  o 180 - "
                      "566 row 1121 x is 1796.21"),
    ("968 diff 2885", "id 2885 (968, 1692.78, 1672.57, 1225.53)  o 180 - "
                      "566 row 1124 y is 1672.56"),
    ("968 diff 2891", "id 2891 (968, 2213.18, 1469.54, 1175.01)  o 180 - "
                      "566 row 1127 x is 2213.19"),
    ("968 diff 2893", "id 2893 (968, 2226.6, 1692.81, 1161.85)  o 180 - "
                      "566 row 1128 z is 1161.84"),
    ("968 diff 2903", "id 2903 (968, 2117.21, 1807.68, 1171.55)  o 180 - "
                      "566 row 1133 z is 1171.56"),
    ("968 usage unver", "Usage of the map-968 set by your server: "
                        "unverified"),
    ("src 968 rows", "map-968 rows: 2841-2903"),
    ("src ff rows", "3772/3773 + 3951/3952"),
    ("src wiki968", "row 968 Rated Eye of the Storm"),
    ("unver 968 role", "The role of the map-968 Rated Eye of the Storm rows"),
    ("unver 3951", "what the duplicate rows 3951/3952 are for"),
    ("unver twins", "map-968 twins 2855-2903"),
    ("unver queued", "whether map 968 is queued at all"),
    # objectives
    ("no other objs", "No orbs, no mines and no mine cart depots exist"),
    ("fr spot", "(566, 2044.28, 1729.68, 1189.96) o -0.017453"),
    ("fr tr o", "BG_EY_TriggerPositions[0] o 0.017453"),
    ("fr cap", "(566, 2024.600708, 1742.819580, 1195.157715)  o 2.443461"),
    ("fr banners", "(566, 2057.46, 1735.07, 1187.91), (566, 2032.25, "
                   "1729.53, 1190.33),"),
    ("be spot", "(566, 2048.83, 1393.65, 1194.49) o 0.20944"),
    ("be cap", "(566, 2050.493164, 1372.235962, 1194.563477)  o 1.710423"),
    ("be banners", "(566, 2047.19, 1349.19, 1189.0), (566, 2074.32, "
                   "1385.78, 1194.72),"),
    ("dr spot", "(566, 2286.56, 1402.36, 1197.11) o 3.72381"),
    ("dr cap", "(566, 2301.010498, 1386.931641, 1197.183472)  o 1.570796"),
    ("dr banners", "(566, 2276.8, 1400.41, 1196.33), (566, 2305.78, "
                   "1404.56, 1199.38),"),
    ("mt spot", "(566, 2284.48, 1731.23, 1189.99) o 2.89725"),
    ("mt cap", "(566, 2282.121582, 1760.006958, 1189.707153)  o 1.919862"),
    ("mt banners", "(566, 2270.84, 1784.08, 1186.76), (566, 2269.13, "
                   "1737.7, 1186.66),"),
    ("tower flag go", "gameobject 184493"),
    ("world trigger", "WORLD_TRIGGER 12999"),
    ("banner entries", "184381 Alliance, 184380 Horde, 184382 Neutral"),
    ("cap go entries", "184081" ),
    ("cap entries 2", "184080"),
    ("cap entries 3", "184083"),
    ("cap entries 4", "184082"),
    ("at fr", "capture area trigger id 4514 (TR_FEL_REAVER_POINT)"),
    ("at be", "capture area trigger id 4476 (TR_BLOOD_ELF_POINT)"),
    ("at dr", "capture area trigger id 4518 (TR_DRAENEI_RUINS_POINT)"),
    ("at mt", "capture area trigger id 4516 (TR_MAGE_TOWER_POINT)"),
    ("cap rule", "BG_EY_POINT_MAX_CAPTURERS_COUNT = 5"),
    ("wiki stand", 'the more people standing in them the faster the '
                   'capture goes'),
    ("flag go", "gameobject 184141 (flagstand, shown at start)"),
    ("flag row", "(566, 2174.782227, 1569.054688, 1160.361938)  o "
                 "-1.448624"),
    ("flagdrop", "gameobject 184142 (flagdrop) is defined in the script but"
                 " never spawned"),
    ("pickup range", "click within 10 yd"),
    ("carry spell", "spell 34976"),
    ("drop spell", "spell 34991"),
    ("flag timer", "BG_EY_FLAG_RESPAWN_TIME = 8 * IN_MILLISECONDS"),
    ("flag seconds", "returns to its spawn after 8 seconds"),
    ("deliver rule", "Deliver it to any tower"),
    ("cap 1600", "win at 1600 points (BG_EY_MAX_TEAM_SCORE = 1600; wiki: "
                 "first to 1600)"),
    ("tick table", "BG_EY_TickPoints = {1, 2, 5, 10} per tick"),
    ("tick time", "BG_EY_FPOINTS_TICK_TIME = 2*IN_MILLISECONDS"),
    ("cadence conflict", "script 2 s vs wiki 1 s"),
    ("flag table", "BG_EY_FlagPoints = {75, 85, 100, 500} for 1/2/3/4 "
                   "towers"),
    # routes
    ("caveat 2", "NOT walkable-path measurements; actual walkability is "
                 "unverified"),
    ("hill quote", "Fights should take place near a tower, on the hill"),
    ("void quote", "falling into the void"),
    ("legs a mt", "legs: 4 yd, 278 yd   direct 275 yd"),
    ("legs a dr", "legs: 4 yd, 310 yd   direct 306 yd"),
    ("legs a fr", "legs: 4 yd, 501 yd   direct 498 yd"),
    ("legs a be", "legs: 4 yd, 520 yd  direct 516 yd"),
    ("legs a cf", "legs: 4 yd, 354 yd   direct 350 yd"),
    ("legs h be", "legs: 1 yd, 286 yd  direct 286 yd"),
    ("legs h fr", "legs: 1 yd, 307 yd  direct 307 yd"),
    ("legs h dr", "legs: 1 yd, 502 yd  direct 503 yd"),
    ("legs h mt", "legs: 1 yd, 518 yd  direct 518 yd"),
    ("legs h cf", "legs: 1 yd, 373 yd  direct 373 yd"),
    ("run mt", "Mage Tower 196 yd"),
    ("run dr", "Draenei Ruins 201 yd"),
    ("run fr", "Fel Reaver Ruins 207 yd"),
    ("run be", "Blood Elf Tower 216 yd"),
    ("pair be-dr", "Blood Elf-Draenei 238 yd"),
    ("pair fr-mt", "240 yd, Draenei-Mage 329 yd"),
    ("pair fb", "Fel Reaver-Blood Elf 336 yd"),
    ("pair fd", "Fel Reaver-Draenei 407 yd"),
    ("pair bm", "Blood Elf-Mage 412 yd"),
    # graveyards
    ("gy main rows", "Main graveyards (= the start rows, section 2)"),
    ("gy 1105", 'id 1105 "Netherstorm BG - Graveyard (Felreaver)"'),
    ("gy 1105 row", "(566, 2013.06, 1677.24, 1182.13)  o 340"),
    ("gy 1106 row", "(566, 2012.4, 1455.41, 1172.2)  o 65"),
    ("gy 1107", 'id 1107 "Netherstorm BG - Graveyard (Draenei Tower)"'),
    ("gy 1107 row", "(566, 2351.22, 1455.63, 1185.33)  o 270"),
    ("gy 1108 row", "(566, 2355.3, 1683.71, 1173.15)  o 225"),
    ("map fr", "Fel Reaver Ruins -> 1105, Blood Elf Tower -> 1106"),
    ("map dm", "Draenei Ruins -> 1107, Mage Tower -> 1108"),
    ("rule eligible", "YOUR team's main graveyard (always) plus each"),
    ("rule owned", "only while your team OWNS that tower"),
    ("rule state", "UNDER_CONTROL"),
    ("rule nearest", "nearest eligible graveyard in 3D"),
    ("tbl fr", "Fel Reaver Ruins: 1105 = 61 yd / 1103 = 498 yd / 1104 = "
               "307 yd"),
    ("tbl be", "Blood Elf Tower:  1106 = 72 yd / 1103 = 516 yd / 1104 = "
               "286 yd"),
    ("tbl dr", "Draenei Ruins:    1107 = 84 yd / 1103 = 306 yd / 1104 = "
               "503 yd"),
    ("tbl mt", "Mage Tower:       1108 = 85 yd / 1103 = 275 yd / 1104 = "
               "518 yd"),
    ("tbl cf", "central flag: 1103 = 350 yd, 1104 = 373 yd, tower GYs "
               "195-214 yd"),
    ("tbl cf detail", "1105 = 195, 1106 = 198, 1107 = 210, 1108 = 214 yd"),
    ("identity", "Each team's start IS its main graveyard row (0 yd)"),
    ("spirit mains", "3.124139 Alliance / 3.193953 Horde"),
    ("spirit entries", "creatures 13116 (Alliance) / 13117 (Horde)"),
    ("spirit on cap", "same facing 3.124139, script PointCaptured"),
    ("catcher note", "all 25, purpose unverified"),
    ("catcher 1109", "(566, 2626.9, 1457.85, 1225.54)  o 180"),
    ("catcher 1133", "(566, 2117.21, 1807.68, 1171.56)  o 180"),
    # buffs
    ("buff entries", "speed 179871, regeneration 179904, berserking 179905"),
    ("buff at map", "Fel Reaver buff trigger 4569, Blood Elf 4568, Draenei "
                    "4571"),
    ("buff at mt", "Mage 4570"),
    ("buff orient", "o 0.907571"),
    ("db2 note", "client DB2 AreaTrigger table"),
    ("buff coords unver", "exact buff coordinates are unverified"),
    ("random buff", "urand(0,2)"),
    ("hidden", "the other two stay hidden (RESPAWN_ONE_DAY)"),
    ("buff respawn", "BUFF_RESPAWN_TIME = 180 s (same object, same type)"),
    ("wiki no buff", "warcraft.wiki has no buff section"),
    ("achieve chill", "Take a Chill Pill"),
    ("berserker retail", "Berserker power-up"),
    ("speed parity", "Speed and regeneration retail parity: unverified"),
    ("spell mapping", "Which spell each gameobject"),
    ("no other buffs", "No other buff or power-up spawns are defined"),
    # sources
    ("dump file", "2019_10_26_01_world.sql"),
    ("not ey", "1101-1102 are NOT EY"),
    ("ey rows", 'map-566 rows: 1103-1133 ("Netherstorm BG") and'),
    ("no comment rows", 'no rows commented'),
    ("no comment rows 2", '"Eye of the Storm" (checked, none)'),
    ("ey files", "BattlegroundEY.h/.cpp"),
    ("ac source", "battleground_template.sql - Eye of The Storm row"),
    ("neg no buff section", "wiki page has no buff/power-up section"),
    ("neg no second map", "no second map id for EoTS in any readable"),
    ("neg flag3", "dropped-flag object 184142 never"),
    ("neg nav", "no pathing/navmesh source"),
    ("neg db2", "AreaTrigger DB2"),
    ("unverified header", "=== 8. EXPLICIT UNVERIFIED LIST ==="),
    ("unverified count", "unverified"),
]

NEGATIVE_CHECKS = [
    ("no estimated coordinate", "estimated coordinate"),
    ("no navmesh confirmed", "navmesh confirmed"),
    ("no pathing confirmed", "pathing confirmed"),
    ("no todo", "TODO"),
    ("no fixme", "FIXME"),
    ("no direct inspection", "verified by direct inspection"),
]


def run_static(text):
    flat = norm(text)
    ok_lines, fails = [], []
    for name, lit in STATIC_CHECKS:
        if name == "unverified count":
            n = flat.count("unverified")
            hit = n >= UNVERIFIED_MIN
            ok_lines.append("    %-28s %s (%d >= %d)"
                            % (name, "ok" if hit else "FAIL", n,
                               UNVERIFIED_MIN))
            if not hit:
                fails.append(name)
            continue
        hit = norm(lit) in flat
        ok_lines.append("    %-28s %s" % (name, "ok" if hit else "MISSING"))
        if not hit:
            fails.append(name)
    for name, lit in NEGATIVE_CHECKS:
        hit = norm(lit) not in flat
        ok_lines.append("    %-28s %s" % (name, "ok" if hit else "PRESENT!"))
        if not hit:
            fails.append(name)
    return fails, ok_lines


# ---------------------------------------------------------------- stage 2
MUTATIONS = [
    ("heading", "- COMPLETED ===\nBattleground", "- DRAFT ===\nBattleground"),
    ("step number", "prompt 3 of 8", "prompt 3 of 7"),
    ("done line", "DONE - step 3 of 8 complete", "DONE - step 3 of 9 complete"),
    ("compass claim", "makes NO compass claims about Eye of the Storm",
     "makes NO compass claims about Eye of the Basin"),
    ("band y", "y 1393.65 / 1402.36", "y 1393.66 / 1402.36"),
    ("home a", "Mage Tower (275 yd) and Draenei Ruins",
     "Mage Tower (276 yd) and Draenei Ruins"),
    ("map id line", "566 = Eye of the Storm", "567 = Eye of the Storm"),
    ("start a", "(566, 2523.76, 1596.13, 1247.7)",
     "(566, 2523.76, 1596.13, 1247.8)"),
    ("start h", "(566, 1803.02, 1539.97, 1249.19)",
     "(566, 1803.02, 1539.98, 1249.19)"),
    ("start id", "id 1103 \"Netherstorm BG - Graveyard (Alliance Start)\"",
     "id 1104 \"Netherstorm BG - Graveyard (Alliance Start)\""),
    ("ac row", "1103,3.03123,1104,0.055761", "1103,3.04123,1104,0.055761"),
    ("ac a o", "AllianceStartO 3.03123", "AllianceStartO 3.04123"),
    ("door a pos", "(566, 2527.6, 1596.91, 1246.0)",
     "(566, 2527.6, 1596.91, 1246.1)"),
    ("door a o", "o -3.12414", "o -3.12415"),
    ("door h pos", "(566, 1803.21, 1539.49, 1246.0)",
     "(566, 1803.21, 1539.50, 1246.0)"),
    ("door dist a", "Alliance start to 184719 = 4 yd",
     "Alliance start to 184719 = 5 yd"),
    ("door dist h", "Horde start to 184720 = 1 yd",
     "Horde start to 184720 = 2 yd"),
    ("ff 3772", "(566, 1808.21, 1539.49, 1267.41)",
     "(566, 1808.21, 1539.49, 1267.42)"),
    ("ff dz", "+18.2 yd in z", "+19.2 yd in z"),
    ("fr spot", "(566, 2044.28, 1729.68, 1189.96)",
     "(566, 2044.28, 1729.68, 1189.97)"),
    ("fr o", "o -0.017453", "o -0.017454"),
    ("fr cap", "(566, 2024.600708, 1742.819580, 1195.157715)",
     "(566, 2024.600708, 1742.819580, 1195.157716)"),
    ("be spot", "(566, 2048.83, 1393.65, 1194.49)",
     "(566, 2048.83, 1393.66, 1194.49)"),
    ("dr cap", "(566, 2301.010498, 1386.931641, 1197.183472)",
     "(566, 2301.010498, 1386.931641, 1197.183473)"),
    ("mt cap", "(566, 2282.121582, 1760.006958, 1189.707153)",
     "(566, 2282.121582, 1760.006958, 1189.707154)"),
    ("mt banner", "(566, 2270.84, 1784.08, 1186.76)",
     "(566, 2270.84, 1784.08, 1186.77)"),
    ("center flag", "(566, 2174.782227, 1569.054688, 1160.361938)",
     "(566, 2174.782227, 1569.054688, 1160.361939)"),
    ("flag go", "gameobject 184141 (flagstand, shown at start)",
     "gameobject 184140 (flagstand, shown at start)"),
    ("flagdrop", "but never spawned", "but always spawned"),
    ("pickup", "click within 10 yd", "click within 11 yd"),
    ("carry spell", "spell 34976", "spell 34977"),
    ("drop spell", "spell 34991", "spell 34992"),
    ("flag timer", "BG_EY_FLAG_RESPAWN_TIME = 8 * IN_MILLISECONDS",
     "BG_EY_FLAG_RESPAWN_TIME = 9 * IN_MILLISECONDS"),
    ("flag seconds", "spawn after 8 seconds", "spawn after 9 seconds"),
    ("max score", "BG_EY_MAX_TEAM_SCORE = 1600", "BG_EY_MAX_TEAM_SCORE = 1601"),
    ("wiki cap", "wiki: first to 1600", "wiki: first to 1700"),
    ("tick table", "{1, 2, 5, 10}", "{1, 2, 5, 11}"),
    ("tick time", "BG_EY_FPOINTS_TICK_TIME = 2*IN_MILLISECONDS",
     "BG_EY_FPOINTS_TICK_TIME = 3*IN_MILLISECONDS"),
    ("flag table", "{75, 85, 100, 500}", "{75, 85, 100, 501}"),
    ("cap5", "BG_EY_POINT_MAX_CAPTURERS_COUNT = 5",
     "BG_EY_POINT_MAX_CAPTURERS_COUNT = 6"),
    ("legs a mt", "legs: 4 yd, 278 yd", "legs: 4 yd, 279 yd"),
    ("direct a mt", "direct 275 yd", "direct 276 yd"),
    ("legs h be", "legs: 1 yd, 286 yd", "legs: 1 yd, 287 yd"),
    ("direct h mt", "direct 518 yd", "direct 519 yd"),
    ("run mt", "Mage Tower 196 yd", "Mage Tower 197 yd"),
    ("pair be dr", "Blood Elf-Draenei 238 yd", "Blood Elf-Draenei 239 yd"),
    ("pair dm", "Draenei-Mage 329 yd", "Draenei-Mage 330 yd"),
    ("pair fd", "Fel Reaver-Draenei 407 yd", "Fel Reaver-Draenei 408 yd"),
    ("gy 1105 row", "(566, 2013.06, 1677.24, 1182.13)",
     "(566, 2013.06, 1677.25, 1182.13)"),
    ("gy 1108 row", "(566, 2355.3, 1683.71, 1173.15)",
     "(566, 2355.3, 1683.72, 1173.15)"),
    ("tbl fr", "1105 = 61 yd / 1103 = 498 yd", "1105 = 62 yd / 1103 = 498 yd"),
    ("tbl mt", "1108 = 85 yd / 1103 = 275 yd", "1108 = 86 yd / 1103 = 275 yd"),
    ("tbl cf", "central flag: 1103 = 350 yd, 1104 = 373 yd",
     "central flag: 1103 = 351 yd, 1104 = 373 yd"),
    ("spirit o", "3.124139 Alliance / 3.193953 Horde",
     "3.124140 Alliance / 3.193953 Horde"),
    ("spirit entry", "creatures 13116 (Alliance) / 13117 (Horde)",
     "creatures 13116 (Alliance) / 13118 (Horde)"),
    ("catcher 1109", "(566, 2626.9, 1457.85, 1225.54)",
     "(566, 2626.9, 1457.85, 1225.55)"),
    ("catcher 1133", "(566, 2117.21, 1807.68, 1171.56)",
     "(566, 2117.21, 1807.68, 1171.57)"),
    ("buff entries", "speed 179871, regeneration 179904, berserking 179905",
     "speed 179871, regeneration 179904, berserking 179906"),
    ("buff at", "Draenei 4571", "Draenei 4572"),
    ("buff o", "o 0.907571", "o 0.907572"),
    ("urand", "urand(0,2)", "urand(0,3)"),
    ("buff respawn", "BUFF_RESPAWN_TIME = 180 s", "BUFF_RESPAWN_TIME = 181 s"),
    ("at be", "capture area trigger id 4476", "capture area trigger id 4477"),
    ("identity", "graveyard row (0 yd)", "graveyard row (1 yd)"),
    ("z range a", "51-59 yd above", "52-59 yd above"),
    ("z range c", "30-37 yd below", "30-38 yd below"),
    ("rated swap", "map 968 is the Rated Eye", "map 969 is the Rated Eye"),
    ("rated title", "Rated Eye of the Storm", "Rated Eye of the Basin"),
    ("968 row 2841", "(968, 1807.06, 1539.16, 1247.85)",
     "(968, 1807.06, 1539.16, 1247.86)"),
    ("968 row 4001", "(968, 1808.21, 1539.49, 1267.41)",
     "(968, 1808.21, 1539.49, 1267.42)"),
    ("dup ff id", "id 3951", "id 3950"),
    ("ident count", "26 of the 33 rows are", "27 of the 33 rows are"),
    ("start delta", "up to 4.04 yd", "up to 4.05 yd"),
    ("diff value", "566 row 1121 x is 1796.21", "566 row 1121 x is 1796.20"),
    ("968 catcher range", "ids 2855-2903 stepping by 2",
     "ids 2855-2905 stepping by 2"),
    ("diff count words", "five catcher rows differing by exactly 0.01",
     "six catcher rows differing by exactly 0.01"),
]


# ---------------------------------------------------------------- stage 3
def stage3(corpora):
    token_map = {
        "eyh": [
            ("max score", "BG_EY_MAX_TEAM_SCORE"),
            ("score value", "= 1600"),
            ("flag timer h", "= (8*IN_MILLISECONDS)"),
            ("tick time h", "= (2*IN_MILLISECONDS)"),
            ("cap5 h", "BG_EY_POINT_MAX_CAPTURERS_COUNT     = 5"),
            ("doors", "BG_OBJECT_A_DOOR_EY_ENTRY           = 184719"),
            ("door h enum", "BG_OBJECT_H_DOOR_EY_ENTRY           = 184720"),
            ("flag1", "= 184493"), ("flag2", "= 184141"),
            ("flag3", "= 184142"),
            ("banners", "BG_OBJECT_A_BANNER_EY_ENTRY         = 184381"),
            ("banner h", "BG_OBJECT_H_BANNER_EY_ENTRY         = 184380"),
            ("banner n", "BG_OBJECT_N_BANNER_EY_ENTRY         = 184382"),
            ("cap be", "= 184080"), ("cap fr", "= 184081"),
            ("cap hu", "= 184082"), ("cap dr", "= 184083"),
            ("at be pt", "TR_BLOOD_ELF_POINT        = 4476"),
            ("at fr pt", "TR_FEL_REAVER_POINT       = 4514"),
            ("at mt pt", "TR_MAGE_TOWER_POINT       = 4516"),
            ("at dr pt", "TR_DRAENEI_RUINS_POINT    = 4518"),
            ("at be buff", "TR_BLOOD_ELF_BUFF         = 4568"),
            ("at fr buff", "TR_FEL_REAVER_BUFF        = 4569"),
            ("at mt buff", "TR_MAGE_TOWER_BUFF        = 4570"),
            ("at dr buff", "TR_DRAENEI_RUINS_BUFF     = 4571"),
            ("gy a", "EY_GRAVEYARD_MAIN_ALLIANCE     = 1103"),
            ("gy h", "EY_GRAVEYARD_MAIN_HORDE        = 1104"),
            ("gy fr", "EY_GRAVEYARD_FEL_REAVER       = 1105"),
            ("gy be", "EY_GRAVEYARD_BLOOD_ELF         = 1106"),
            ("gy dr", "EY_GRAVEYARD_DRAENEI_RUINS     = 1107"),
            ("gy mt", "EY_GRAVEYARD_MAGE_TOWER        = 1108"),
            ("carry spell", "BG_EY_NETHERSTORM_FLAG_SPELL        = 34976"),
            ("drop spell", "= 34991"),
            ("exploit a", "EY_EXPLOIT_TELEPORT_LOCATION_ALLIANCE = 3773"),
            ("exploit h", "EY_EXPLOIT_TELEPORT_LOCATION_HORDE = 3772"),
            ("tick table h", "BG_EY_TickPoints[EY_POINTS_MAX] = {1, 2, 5, 10}"),
            ("flag table h", "BG_EY_FlagPoints[EY_POINTS_MAX] = {75, 85, 100, 500}"),
            ("trigger pos fr", "{2044.28f, 1729.68f, 1189.96f, 0.017453f}"),
            ("trigger pos be", "{2048.83f, 1393.65f, 1194.49f, 0.20944f}"),
            ("trigger pos dr", "{2286.56f, 1402.36f, 1197.11f, 3.72381f}"),
            ("trigger pos mt", "{2284.48f, 1731.23f, 1189.99f, 2.89725f}"),
            ("struct fr gy", "BG_EY_TEXT_HORDE_TAKEN_FEL_REAVER_RUINS, "
                             "EY_GRAVEYARD_FEL_REAVER)"),
            ("struct mt gy", "BG_EY_TEXT_HORDE_TAKEN_MAGE_TOWER, "
                             "EY_GRAVEYARD_MAGE_TOWER)"),
        ],
        "eyc": [
            ("door a pos", "2527.6f, 1596.91f, 1246.0f, -3.12414f"),
            ("door h pos", "1803.21f, 1539.49f, 1246.0f, 3.14159f"),
            ("fr banner c", "2057.46f, 1735.07f, 1187.91f, -0.925024f"),
            ("be banner c", "2047.19f, 1349.19f, 1189.0f, -1.62316f"),
            ("dr banner c", "2276.8f, 1400.41f, 1196.33f, 2.44346f"),
            ("mt banner c", "2270.84f, 1784.08f, 1186.76f, 2.42601f"),
            ("fr flag", "2044.28f, 1729.68f, 1189.96f, -0.017453f"),
            ("be flag", "2048.83f, 1393.65f, 1194.49f, 0.20944f"),
            ("dr flag", "2286.56f, 1402.36f, 1197.11f, 3.72381f"),
            ("mt flag", "2284.48f, 1731.23f, 1189.99f, 2.89725f"),
            ("fr cap", "2024.600708f, 1742.819580f, 1195.157715f"),
            ("be cap", "2050.493164f, 1372.235962f, 1194.563477f"),
            ("dr cap", "2301.010498f, 1386.931641f, 1197.183472f"),
            ("mt cap", "2282.121582f, 1760.006958f, 1189.707153f"),
            ("center flag", "2174.782227f, 1569.054688f, 1160.361938f"),
            ("gy fn", "BattlegroundEY::GetClosestGraveYard"),
            ("spirit main a", "AddSpiritGuide(EY_SPIRIT_MAIN_ALLIANCE"),
            ("spirit main h", "AddSpiritGuide(EY_SPIRIT_MAIN_HORDE"),
            ("spirit on cap", "GetWorldSafeLoc(m_CapturingPointTypes[Point]"
                              ".GraveYardId)"),
            ("world trigger", "AddCreature(WORLD_TRIGGER"),
            ("buff spawn", "Buff_Entries[0], at->Pos.X, at->Pos.Y, "
                           "at->Pos.Z, 0.907571f"),
            ("random buff", "uint8 buff = urand(0, 2)"),
            ("pickup range", "IsWithinDistInMap(target_obj, 10)"),
            ("flag timer set", "m_FlagsTimer = BG_EY_FLAG_RESPAWN_TIME"),
            ("tick add", "AddPoints(ALLIANCE, BG_EY_TickPoints["),
            ("flag points", "BG_EY_FlagPoints[m_TeamPointsCount[team_id] - 1]"),
            ("at cases", "case TR_BLOOD_ELF_POINT:"),
            ("capture cap", "BG_EY_POINT_MAX_CAPTURERS_COUNT"),
            ("exploit fn", "BattlegroundEY::GetExploitTeleportLocation"),
        ],
        "bh": [
            ("speed buff", "BG_OBJECTID_SPEEDBUFF_ENTRY     = 179871"),
            ("regen buff", "BG_OBJECTID_REGENBUFF_ENTRY     = 179904"),
            ("zerker buff", "BG_OBJECTID_BERSERKERBUFF_ENTRY = 179905"),
            ("buff table", "uint32 const Buff_Entries[3]"),
            ("buff respawn", "BUFF_RESPAWN_TIME               = 180"),
            ("spirit a", "= 13116"), ("spirit h", "= 13117"),
        ],
        "wsl": [
            ("row 1103", "(1103,566,2523.76,1596.13,1247.7,180,"
                         "'Netherstorm BG - Graveyard (Alliance Start)'),"),
            ("row 1104", "(1104,566,1803.02,1539.97,1249.19,0,"
                         "'Netherstorm BG - Graveyard (Horde Start)'),"),
            ("row 1105", "(1105,566,2013.06,1677.24,1182.13,340,"
                         "'Netherstorm BG - Graveyard (Felreaver)'),"),
            ("row 1106", "(1106,566,2012.4,1455.41,1172.2,65,"
                         "'Netherstorm BG - Graveyard (BE Tower)'),"),
            ("row 1107", "(1107,566,2351.22,1455.63,1185.33,270,"
                         "'Netherstorm BG - Graveyard (Draenei Tower)'),"),
            ("row 1108", "(1108,566,2355.3,1683.71,1173.15,225,"
                         "'Netherstorm BG - Graveyard (Human Tower)'),"),
            ("row 1109", "(1109,566,2626.9,1457.85,1225.54,180,"
                         "'Netherstorm BG - Corpse Catcher 000'),"),
            ("row 1133", "(1133,566,2117.21,1807.68,1171.56,180,"
                         "'Netherstorm BG - Corpse Catcher 024'),"),
            ("row 3772", "(3772,566,1808.21,1539.49,1267.41,360,"
                         "'Forcefield Target 000'),"),
            ("row 3773", "(3773,566,2523.51,1596.58,1269.27,180,"
                         "'Forcefield Target 001'),"),
            ("row 3951", "(3951,566,1808.21,1539.49,1267.41,360,"
                         "'Forcefield Target 000'),"),
            ("row 2841", "(2841,968,1807.06,1539.16,1247.85,0,"
                         "'Netherstorm BG 2.0 - Graveyard (Horde Start)'),"),
            ("row 2853", "(2853,968,2355.3,1683.71,1173.15,225,"
                         "'Netherstorm BG 2.0 - Graveyard (Human Tower)'),"),
            ("row 4001", "(4001,968,1808.21,1539.49,1267.41,360,"
                         "'Netherstorm 2.0 - Forcefield Target 000'),"),
            ("row 2903", "(2903,968,2117.21,1807.68,1171.55,180,"
                         "'Netherstorm BG 2.0 - Corpse Catcher 024 "
                         "(copy)'),"),
        ],
        "act": [
            ("ey template row", "(7,8,15,61,80,1103,3.03123,1104,0.055761,"
                                "10,1,'','Eye of The Storm (battleground)'),"),
        ],
    }
    corpora_map = {k: corpora[k] for k in token_map}
    return source_stage(corpora_map, token_map)


# ---------------------------------------------------------------- stage 4
def parse_wsl_rows(wsl):
    rows = {}
    for line in wsl.splitlines():
        m = re.match(r"\((\d+),(\d+),([^,]+),([^,]+),([^,]+),([^,]+),(.*)\)",
                     line.strip())
        if not m:
            continue
        rid = int(m.group(1))
        if rid in ALL_IDS:
            rows[rid] = {"map": m.group(2), "x": m.group(3),
                         "y": m.group(4), "z": m.group(5),
                         "facing": m.group(6)}
    return rows


def parse_script_coords(cyc):
    """Distinct (x, y, z) triples from every AddObject call + trigger pos."""
    out = {}
    for m in re.finditer(r"AddObject\(\w+,\s*\w+,\s*([^)]+)\)", cyc):
        vals = [v.strip().rstrip("f") for v in m.group(1).split(",")[:3]]
        out[tuple(vals)] = True
    return list(out)


def rd(x):
    return int(x + 0.5)


def stage4(text, corpora, probe=False):
    if probe:
        text = text.replace("(566, 2626.9, 1457.85, 1225.54)",
                            "(566, 2626.9, 1457.85, 1225.55)", 1)
    flat = norm(text)
    lines, fails = [], []

    # 4a. all 49 document rows vs document
    rows = parse_wsl_rows(corpora["wsl"])
    hit = 0
    for rid in DOC_IDS:
        r = rows.get(rid)
        if not r:
            fails.append("row %d missing from dump" % rid)
            lines.append("    row %-5d NOT IN DUMP" % rid)
            continue
        triple = "(%s, %s, %s, %s)" % (r["map"], r["x"], r["y"], r["z"])
        context = triple in flat or ("id %d" % rid) in flat
        facing_ok = re.search(r"(?<![0-9.])o %s(?![0-9.])"
                              % re.escape(r["facing"]), flat)
        ok = triple in flat and context and bool(facing_ok)
        hit += ok
        if not ok:
            fails.append("row %d doc mismatch" % rid)
    lines.append("    world_safe rows matched: %d/%d" % (hit, len(DOC_IDS)))

    # 4b. every AddObject coordinate triple in the cpp vs document
    coords = parse_script_coords(corpora["eyc"])
    c_ok = 0
    for (x, y, z) in coords:
        triple = "(566, %s, %s, %s)" % (x, y, z)
        ok = triple in flat
        c_ok += ok
        if not ok:
            fails.append("script triple %s" % triple)
    lines.append("    script coordinate triples matched: %d/%d"
                 % (c_ok, len(coords)))

    # 4c. routes / flag runs / pairs
    A = (float(rows[1103]["x"]), float(rows[1103]["y"]))
    H = (float(rows[1104]["x"]), float(rows[1104]["y"]))
    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])

    def find_object(cyc, enum_name, want_z=False):
        m = re.search(r"AddObject\(%s,\s*\w+,\s*([^)]+)\)" % enum_name, cyc)
        vals = [v.strip().rstrip("f") for v in m.group(1).split(",")[:3]]
        if want_z:
            return (float(vals[0]), float(vals[1]), float(vals[2]))
        return (float(vals[0]), float(vals[1]))

    cyc = corpora["eyc"]
    dA = find_object(cyc, "BG_EY_OBJECT_DOOR_A")
    dH = find_object(cyc, "BG_EY_OBJECT_DOOR_H")
    FR = find_object(cyc, "BG_EY_OBJECT_FLAG_FEL_REAVER")
    BE = find_object(cyc, "BG_EY_OBJECT_FLAG_BLOOD_ELF")
    DR = find_object(cyc, "BG_EY_OBJECT_FLAG_DRAENEI_RUINS")
    MT = find_object(cyc, "BG_EY_OBJECT_FLAG_MAGE_TOWER")
    CF = find_object(cyc, "BG_EY_OBJECT_FLAG_NETHERSTORM")

    routes = [
        ("A->Mage", A, dA, MT, "legs: 4 yd, 278 yd   direct 275 yd"),
        ("A->Draenei", A, dA, DR, None),
        ("A->FelReaver", A, dA, FR, None),
        ("A->BloodElf", A, dA, BE, None),
        ("A->center", A, dA, CF, None),
        ("H->BloodElf", H, dH, BE, None),
        ("H->FelReaver", H, dH, FR, None),
        ("H->Draenei", H, dH, DR, None),
        ("H->Mage", H, dH, MT, None),
        ("H->center", H, dH, CF, None),
    ]
    ok_routes = 0
    for name, s, door, node, _ in routes:
        l1, l2, direct = rd(dist(s, door)), rd(dist(door, node)), \
            rd(dist(s, node))
        want = ["legs: %d yd, %d yd" % (l1, l2), "direct %d yd" % direct]
        ok = all(w in flat for w in want)
        ok_routes += ok
        if not ok:
            fails.append("route %s (%s)" % (name, want))
    lines.append("    route legs+direct: %d/%d match recompute"
                 % (ok_routes, len(routes)))

    runs = [("Mage Tower", MT), ("Draenei Ruins", DR),
            ("Fel Reaver Ruins", FR), ("Blood Elf Tower", BE)]
    ok_runs = 0
    for label, node in runs:
        want = "%s %d yd" % (label, rd(dist(CF, node)))
        ok = want in flat
        ok_runs += ok
        if not ok:
            fails.append("flag run %s" % label)
    lines.append("    flag runs center->towers: %d/%d match recompute"
                 % (ok_runs, len(runs)))

    pairs = [("Blood Elf-Draenei", BE, DR), ("Fel Reaver-Mage", FR, MT),
             ("Draenei-Mage", DR, MT), ("Fel Reaver-Blood Elf", FR, BE),
             ("Fel Reaver-Draenei", FR, DR), ("Blood Elf-Mage", BE, MT)]
    ok_pairs = 0
    for label, p, q in pairs:
        want = "%s %d yd" % (label, rd(dist(p, q)))
        ok = want in flat
        ok_pairs += ok
        if not ok:
            fails.append("pair %s" % label)
    lines.append("    tower pairs: %d/%d match recompute"
                 % (ok_pairs, len(pairs)))

    # 4d. z-relief ranges, exploit dz, door distances, home pairs
    zA = float(rows[1103]["z"])
    zH = float(rows[1104]["z"])
    tower_z = [find_object(cyc, e, want_z=True)[2] for e in
               ("BG_EY_OBJECT_FLAG_FEL_REAVER", "BG_EY_OBJECT_FLAG_BLOOD_ELF",
                "BG_EY_OBJECT_FLAG_DRAENEI_RUINS",
                "BG_EY_OBJECT_FLAG_MAGE_TOWER")]
    cz = find_object(cyc, "BG_EY_OBJECT_FLAG_NETHERSTORM", want_z=True)[2]
    start_lo = rd(min(zA, zH) - max(tower_z))
    start_hi = rd(max(zA, zH) - min(tower_z))
    want = "%d-%d yd above the tower platforms" % (start_lo, start_hi)
    ok = want in flat
    if not ok:
        fails.append("z relief start (%s)" % want)
    cen_lo = rd(min(tower_z) - cz)
    cen_hi = rd(max(tower_z) - cz)
    want2 = "%d-%d yd below the towers" % (cen_lo, cen_hi)
    ok2 = want2 in flat
    if not ok2:
        fails.append("z relief center (%s)" % want2)
    lines.append("    z relief: starts %d-%d above, center %d-%d below "
                 "towers: %s" % (start_lo, start_hi, cen_lo, cen_hi,
                                 "ok" if (ok and ok2) else "MISMATCH"))

    dz_h = round(float(rows[3772]["z"]) - zH, 1)
    dz_a = round(float(rows[3773]["z"]) - zA, 1)
    want_h = "+%.1f yd in z" % dz_h
    want_a = "+%.1f yd in z" % dz_a
    ok = want_h in flat and want_a in flat
    if not ok:
        fails.append("exploit dz (%s / %s)" % (want_h, want_a))
    lines.append("    exploit dz: %s / %s" % (want_h, want_a))

    da = rd(dist(A, dA))
    dh = rd(dist(H, dH))
    ok = ("Alliance start to 184719 = %d yd" % da) in flat and \
         ("Horde start to 184720 = %d yd" % dh) in flat
    if not ok:
        fails.append("door distances")
    lines.append("    door distances: A %d yd, H %d yd" % (da, dh))

    a_d = {label: rd(dist(A, node)) for label, node in
           (("Mage Tower", MT), ("Draenei Ruins", DR),
            ("Fel Reaver Ruins", FR), ("Blood Elf Tower", BE))}
    h_d = dict(a_d)  # recomputed below with H
    h_d = {label: rd(dist(H, node)) for label, node in
           (("Mage Tower", MT), ("Draenei Ruins", DR),
            ("Fel Reaver Ruins", FR), ("Blood Elf Tower", BE))}
    a_near = sorted(a_d.items(), key=lambda kv: kv[1])[:2]
    h_near = sorted(h_d.items(), key=lambda kv: kv[1])[:2]
    ok = all("(%d yd)" % v in flat for _, v in a_near + h_near)
    if not ok:
        fails.append("home pair distances %s %s" % (a_near, h_near))
    lines.append("    home pairs: A %s / H %s"
                 % (["%s %d" % kv for kv in a_near],
                    ["%s %d" % kv for kv in h_near]))

    # 4e. graveyard table
    gy_rows = {"Fel Reaver Ruins": 1105, "Blood Elf Tower": 1106,
               "Draenei Ruins": 1107, "Mage Tower": 1108}
    tower_pos = {"Fel Reaver Ruins": FR, "Blood Elf Tower": BE,
                 "Draenei Ruins": DR, "Mage Tower": MT}
    ok_gy = 0
    for label, gy in gy_rows.items():
        g = (float(rows[gy]["x"]), float(rows[gy]["y"]))
        d1 = rd(dist(tower_pos[label], g))
        d2 = rd(dist(tower_pos[label], A))
        d3 = rd(dist(tower_pos[label], H))
        want = "%s: %d = %d yd / 1103 = %d yd / 1104 = %d yd" \
            % (label, gy, d1, d2, d3)
        ok = want in flat
        ok_gy += ok
        if not ok:
            fails.append("GY table %s (%s)" % (label, want))
    # center line
    c1 = rd(dist(CF, A))
    c2 = rd(dist(CF, H))
    gds = sorted(rd(dist(CF, (float(rows[g]["x"]), float(rows[g]["y"]))))
                 for g in (1105, 1106, 1107, 1108))
    want = ("central flag: 1103 = %d yd, 1104 = %d yd, tower GYs %d-%d yd"
            % (c1, c2, gds[0], gds[-1]))
    ok = want in flat
    ok_gy += ok
    if not ok:
        fails.append("GY center line (%s)" % want)
    lines.append("    GY distance table: %d/5 match recompute" % ok_gy)

    # 4f2. map-968 vs map-566 diff claims
    ident, diff_ids, max_start_delta = 0, [], 0.0
    for a, b in PAIRS968:
        A, B = rows.get(a), rows.get(b)
        if not A or not B:
            fails.append("diff pair missing %d/%d" % (a, b))
            continue
        same = (A["x"], A["y"], A["z"]) == (B["x"], B["y"], B["z"])
        if same:
            ident += 1
        else:
            diff_ids.append(a)
        if b in (1103, 1104):
            for k in ("x", "y", "z"):
                max_start_delta = max(max_start_delta,
                                      abs(float(A[k]) - float(B[k])))
    want = "26 of the 33 rows are coordinate-identical to their map-566 " \
        "counterpart"
    ok = ident == 26 and want in flat
    if not ok:
        fails.append("968 identical count (%d)" % ident)
    want = "differing from the section-2 rows by up to %.2f yd" \
        % max_start_delta
    ok = want in flat
    if not ok:
        fails.append("968 start delta (%s)" % want)
    ok_d = 0
    for a, b, axis in ((2879, 1121, "x"), (2885, 1124, "y"),
                       (2891, 1127, "x"), (2893, 1128, "z"),
                       (2903, 1133, "z")):
        A, B = rows.get(a), rows.get(b)
        delta = round(abs(float(A[axis]) - float(B[axis])), 2)
        want = "566 row %d %s is %s" % (b, axis, B[axis])
        ok = delta == 0.01 and want in flat
        ok_d += ok
        if not ok:
            fails.append("968 diff row %d (%s, delta %s)" % (a, want, delta))
    lines.append("    968 vs 566: identical %d/33, start delta %.2f yd, "
                 "0.01-diff rows %d/5: %s"
                 % (ident, max_start_delta, ok_d,
                    "ok" if (ident == 26 and ok_d == 5) else "MISMATCH"))

    # 4f. GY mapping from the ey.h struct init
    m = re.findall(r"BattlegroundEYCapturingPointStruct\(.*?,\s*"
                   r"(EY_GRAVEYARD_\w+)\)", corpora["eyh"])
    id_of = {"EY_GRAVEYARD_FEL_REAVER": 1105, "EY_GRAVEYARD_BLOOD_ELF": 1106,
             "EY_GRAVEYARD_DRAENEI_RUINS": 1107,
             "EY_GRAVEYARD_MAGE_TOWER": 1108}
    label_of = {"EY_GRAVEYARD_FEL_REAVER": "Fel Reaver Ruins",
                "EY_GRAVEYARD_BLOOD_ELF": "Blood Elf Tower",
                "EY_GRAVEYARD_DRAENEI_RUINS": "Draenei Ruins",
                "EY_GRAVEYARD_MAGE_TOWER": "Mage Tower"}
    ok_map = 0
    for sym in m[:4]:
        want = "%s -> %d" % (label_of[sym], id_of[sym])
        ok = want in flat
        ok_map += ok
        if not ok:
            fails.append("GY mapping %s" % want)
    lines.append("    GY point mapping: %d/4 from struct init" % ok_map)

    # 4g. coord trace + probes
    ok_c, c_lines, missing_c = coord_trace(text, corpora)
    lines.extend(c_lines)
    if not ok_c:
        fails.append("coordinate trace: %s" % missing_c[:6])
    probe_txt = text.replace("(566, 2523.76, 1596.13, 1247.7)",
                             "(566, 2523.76, 1596.13, 1247.8)", 1)
    ok2, _, _ = coord_trace(probe_txt, corpora)
    probe_ok = (probe_txt != text) and not ok2
    lines.append("    coordinate probe reacts: %s"
                 % ("yes" if probe_ok else "no"))
    if not probe_ok:
        fails.append("coordinate probe")

    return fails, lines


# ---------------------------------------------------------------- stage 5
def stage5(text, corpora):
    lines, fails = [], []

    # dump: no rows commented "Eye of the Storm"; all Netherstorm BG rows
    # are map 566
    n_eye = len(re.findall(r"(?i)eye of the storm", corpora["wsl"]))
    ok = n_eye == 0
    if not ok:
        fails.append("dump has %d 'Eye of the Storm' rows" % n_eye)
    lines.append("    dump 'Eye of the Storm'-commented rows: %d (need 0)"
                 % n_eye)

    bad = 0
    c566 = c968gy = c968ff = cff = 0
    for line in corpora["wsl"].splitlines():
        s = line.strip()
        if not s.startswith("("):
            continue
        m = re.match(r"\((\d+),(\d+),.*'([^']*)'", s)
        if not m:
            continue
        mp, comment = m.group(2), m.group(3)
        if "Forcefield Target" in comment:
            cff += 1
        if comment.startswith("Netherstorm BG - "):
            if mp == "566":
                c566 += 1
            else:
                bad += 1
        elif comment.startswith("Netherstorm BG 2.0 - "):
            if mp == "968":
                c968gy += 1
            else:
                bad += 1
        elif comment.startswith("Netherstorm 2.0 - "):
            if mp == "968":
                c968ff += 1
            else:
                bad += 1
        elif comment.startswith("Netherstorm BG"):
            # any other "Netherstorm BG*" comment = unknown variant
            bad += 1
        # other "Netherstorm ..." comments are Outland zone rows (map 530)
    ok = (c566 == 31 and c968gy == 31 and c968ff == 2 and cff == 6
          and bad == 0)
    if not ok:
        fails.append("EY dump row sets 566=%d 968gy=%d 968ff=%d ff=%d "
                     "bad=%d" % (c566, c968gy, c968ff, cff, bad))
    lines.append("    EY dump row sets: map566=%d, map968 GY=%d, "
                 "map968 FF=%d, forcefield total=%d: %s"
                 % (c566, c968gy, c968ff, cff, "ok" if ok else "BAD"))

    # AzerothCore: exactly one Eye of The Storm template row
    n_ac = len(re.findall(r"(?i)eye of the storm", corpora["act"]))
    ok = n_ac == 1
    if not ok:
        fails.append("AC template has %d Eye rows" % n_ac)
    lines.append("    AzerothCore Eye template rows: %d (need 1)" % n_ac)

    # document-claim injection probes
    inj1 = text + "\nnavmesh confirmed under inspection.\n"
    f1, _ = run_static(inj1)
    r1 = "no navmesh confirmed" in f1
    lines.append("    injection probe (navmesh confirmed):  %s"
                 % ("detected" if r1 else "NOT DETECTED"))
    if not r1:
        fails.append("navmesh injection probe")

    inj2 = text + "\nverified by direct inspection.\n"
    f2, _ = run_static(inj2)
    r2 = "no direct inspection" in f2
    lines.append("    injection probe (direct inspection):  %s"
                 % ("detected" if r2 else "NOT DETECTED"))
    if not r2:
        fails.append("direct-inspection injection probe")

    stripped = text.replace("unverified", "verified")
    f3, _ = run_static(stripped)
    r3 = "unverified count" in f3
    lines.append("    injection probe (unverified stripped):%s"
                 % (" detected" if r3 else " NOT DETECTED"))
    if not r3:
        fails.append("unverified count probe")

    # gh 404 control
    res = subprocess.run(
        ["gh", "api", "-X", "GET",
         "repos/HavenWoW/BFA-HavenCore/contents/src/server/game/"
         "DoesNotExist.cpp"],
        capture_output=True, text=True)
    absent = res.returncode != 0
    lines.append("    control: bogus Haven path 404:          %s"
                 % ("yes" if absent else "NO"))
    if not absent:
        fails.append("gh 404 control")
    lines.append("    control: live corpora loaded:           %d"
                 % len(corpora))
    return fails, lines


# ---------------------------------------------------------------- main
def main():
    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()

    print("=" * 68)
    print("AUDIT: Coordinates_Eye_of_the_Storm_COMPLETED.txt (BG step 3)")
    print("=" * 68)

    fails1, lines1 = run_static(text)
    total1 = len(STATIC_CHECKS) + len(NEGATIVE_CHECKS)
    print("\n[1] Static checks: %d/%d passed" % (total1 - len(fails1), total1))
    if fails1:
        print("    FAILED: %s" % ", ".join(fails1))
        for ln in lines1:
            if "MISSING" in ln or "PRESENT" in ln or "FAIL" in ln:
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
    corpora = {k: gh_content(HAVEN, p) for k, p in LC_FILES.items()}
    corpora["wsl"] = gh_content(TC, TC_DUMP)
    corpora["act"] = gh_content(AC, AC_TEMPLATE)
    missing = [k for k, v in corpora.items() if v is None]
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
        {"eyc": [("center flag float", "2174.782227f")]},
        lambda t: t.replace("2174.782227f", "2174.783227f"))
    print("    reaction to tampered source (verified): %s"
          % ("yes" if probe_undetected == [] else "NO"))
    if probe_undetected != []:
        ok3 = False

    print("\n[4] Derived values recomputed from source bodies")
    fails4, lines4 = stage4(text, corpora)
    for ln in lines4:
        print(ln)
    probe_fails, _ = stage4(text, corpora, probe=True)
    reacts = any("doc mismatch" in f for f in probe_fails)
    print("    row check reacts to doc tamper:          %s"
          % ("yes" if reacts else "NO"))
    if not reacts:
        fails4.append("row probe")
    if fails4:
        print("    DERIVED STAGE FAILED: %s"
              % ", ".join(str(f) for f in fails4))

    print("\n[5] Absence claims")
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
