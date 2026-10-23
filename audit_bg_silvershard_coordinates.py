#!/usr/bin/env python3
"""Audit: Coordinates_Silvershard_Mines_COMPLETED.txt (BG coords step 5)."""

import math
import re
import subprocess
import sys

sys.path.insert(0, ".")
from audit_common import gh_content, source_stage, mutation_probe, coord_trace

DOC = ("# Ai Research prompts/Battleground_Coordinates/"
       "Coordinates_Silvershard_Mines_COMPLETED.txt")
LC = "Titans-Project/LegionCore-Reforged"
HAVEN = "HavenWoW/BFA-HavenCore"
BFA = "Titans-Project/BfaCore-Reforged"
TC = "TrinityCore/TrinityCore"
AC = "azerothcore/azerothcore-wotlk"
FILES = {
    "smh": "src/server/game/Battlegrounds/Zones/BattlegroundSilvershardMines.h",
    "smc": "src/server/game/Battlegrounds/Zones/BattlegroundSilvershardMines.cpp",
}
TC_DUMP = "sql/old/8.x/world/19071_2020_06_17/2019_10_26_01_world.sql"
AC_TEMPLATE = "data/sql/base/db_world/battleground_template.sql"
DOC_IDS = [4061, 4062, 4072, 4073, 4074, 4075]
UNVERIFIED_MIN = 10


def norm(s):
    return re.sub(r"\s+", " ", s)


STATIC_CHECKS = [
    ("heading", "=== SILVERSHARD MINES COORDINATES - BFA 8.3.7 "
                "(TRINITYCORE) - COMPLETED ==="),
    ("numbering", "prompt 5 of 8 (Silvershard Mines, map 727)"),
    ("done", "DONE - step 5 of 8 complete"),
    ("no-estimate", "nothing is estimated"),
    ("unverified policy", 'the entry says "unverified"'),
    ("no compass", "makes NO coordinate-compass claims"),
    ("band", "x 564.8048 - 896.7936, y 25.29027 - 502.3111, "
             "z 298.2867 - 364.1431"),
    ("raw pattern", "851.575 vs 630.17"),
    ("pathing caveat", "NOT walkable-path measurements: no pathing/navmesh "
                       "source for map 727"),
    ("rail caveat", "minecart rail waypoints are not in any readable source"),
    ("map line", "727 = Silvershard Mines"),
    ("no second id", "No second map id appears in any readable source"),
    ("cores no script", "Neither HavenWoW/BFA-HavenCore nor "
                        "Titans-Project/BfaCore-Reforged ships"),
    ("script name", "BattlegroundSilvershardMines.cpp/.h"),
    ("queue unver", "which id/template your server queues is unverified"),
    ("start h id", 'id 4061 "STV Diamond Mine - BG - Start - Horde (Start)"'),
    ("start h row", "(727, 630.17, 230.174, 328.838)  o 310.329"),
    ("start a id", 'id 4062 "STV Diamond Mine - BG - Start - Alliance (Start)"'),
    ("start a row", "(727, 851.575, 135.141, 328.838)  o 125.768"),
    ("double duty", "the SAME two rows are each faction's only graveyard"),
    ("door 1", "gameobject 212939 (Alliance door 1) (727, 852.02, 158.21, "
               "328.76)"),
    ("door 1 o", "o 0.15"),
    ("door 2", "gameobject 212940 (Alliance door 2) (727, 830.09, 143.92, "
               "328.50)"),
    ("door 3", "gameobject 212941 (Horde door 1) (727, 652.17, 228.49, "
               "328.91)"),
    ("door 4", "gameobject 212942 (Horde door 2) (727, 636.50, 208.12, "
               "328.64)"),
    ("door dists a", "Alliance start to 212939 = 23 yd"),
    ("door dists a2", "to 212940 = 23 yd"),
    ("door dists h", "Horde start to 212941 = 22 yd"),
    ("door dists h2", "to 212942 = 23 yd"),
    ("raised area", 'raised starting area'),
    ("no flags", "No flags, no orbs and no capture nodes exist here"),
    ("depot diamond row", "(727, 894.528, 30.7066, 363.927)  o 115.242"),
    ("depot diamond go", "gameobject 212082 (THE_DESPOSITS_OF_DIAMONDS)"),
    ("depot diamond pos", "(727, 896.7936, 25.29027, 364.1431)  o "
                          "3.539994"),
    ("depot wf row", "(727, 571.024, 336.894, 346.593)  o 2.6878"),
    ("depot wf go", "gameobject 212080 (RESERVOIR)"),
    ("depot wf pos", "(727, 564.8048, 337.0873, 347.1427)  o 1.571254"),
    ("depot lava row", "(727, 620.889, 79.6562, 298.326)  o 9.01141"),
    ("depot lava go", "gameobject 212081 (THE_DESPOSITION_OF_LAVA)"),
    ("depot lava pos", "(727, 615.5099, 79.41812, 298.2867)  o 1.654058"),
    ("depot troll row", "(727, 783.064, 495.927, 359.336)  o 314.661"),
    ("depot troll go", "gameobject 212083 (BACKLOG_TROLLS)"),
    ("depot troll pos", "(727, 777.7377, 502.3111, 359.4537)  o 0.719448"),
    ("depot ids", "row id 4074"),
    ("wiki three", "three diamond drop-off points"),
    ("discrepancy", "discrepancy is recorded as-is"),
    ("cart npc", "NPC creature entry 60140"),
    ("cart 1", "(727, 744.542053, 183.545883, 319.658203)  o 4.356342"),
    ("cart 2", "(727, 739.400330, 203.598511, 319.603333)  o 2.308198"),
    ("cart 3", "(727, 760.184509, 198.844742, 319.446655)  o 0.351249"),
    ("cart spell n", "spell 125695 (NORTH capture point)"),
    ("cart spell s", "spell 125696 (SOUTH capture point)"),
    ("cart spell e", "spell 125620 (EAST capture point)"),
    ("max carts", "Maximum three carts active"),
    ("first cart", "first cart 10 s after start"),
    ("waypoint unver", "Cart rail waypoints: unverified"),
    ("not blizzlike", "not blizzlike"),
    ("switch npc", "Two track switches (script NPC entry 60283"),
    ("switch east", "East switch (727, 715.585388, 101.272034, 319.994690) "
                    "o 4.647377"),
    ("switch north", "North switch (727, 847.481689, 308.032562, "
                     "346.573242)  o 0.587086"),
    ("switch opened", "BG_SSM_TRACK_SWITCH_OPENED spell 120228"),
    ("switch closed", "BG_SSM_TRACK_SWITCH_CLOSED spell 120229"),
    ("switch cd", "cooldown 3000 ms"),
    ("switch rule", "need no cart control to flip"),
    ("defend aura", "128646"),
    ("control visuals", "116086 (Alliance) / 116085 (Horde)"),
    ("trickle", "3 carts = 5 points, 2 carts = 3 points, 1 cart = 2 points"),
    ("trickle timer", "every 2 seconds"),
    ("arrival", "PointsPerMineCart"),
    ("arrival val", "scores 150 points"),
    ("cap script", "SSM_MAX_TEAM_POINTS = 1500"),
    ("cap wiki", "first to 1600"),
    ("cap unver", "which your server uses: unverified"),
    ("legs caveat", "NOT walkable-path measurements; actual walkability is "
                    "unverified"),
    ("a diamond", "legs: 23 yd, 140 yd   direct 119 yd"),
    ("a waterfall", "legs: 23 yd, 338 yd   direct 351 yd"),
    ("a lava", "legs: 23 yd, 249 yd   direct 243 yd"),
    ("a troll", "legs: 23 yd, 352 yd   direct 375 yd"),
    ("a east", "legs: 23 yd, 148 yd   direct 140 yd"),
    ("a north", "legs: 23 yd, 150 yd   direct 173 yd"),
    ("h diamond", "legs: 22 yd, 318 yd   direct 336 yd"),
    ("h waterfall", "legs: 22 yd, 139 yd   direct 125 yd"),
    ("h lava", "legs: 22 yd, 154 yd   direct 151 yd"),
    ("h troll", "legs: 22 yd, 301 yd   direct 310 yd"),
    ("h east", "legs: 22 yd, 142 yd   direct 155 yd"),
    ("h north", "legs: 22 yd, 211 yd   direct 231 yd"),
    ("pair dw", "Diamond-Waterfall 455 yd"),
    ("pair dl", "Diamond-Lava 286 yd"),
    ("pair dt", "Diamond-Troll 492 yd"),
    ("pair wl", "Waterfall-Lava 263 yd"),
    ("pair wt", "Waterfall-Troll 270 yd"),
    ("pair lt", "Lava-Troll 453 yd"),
    ("track sets", "East to"),
    ("track sets unver", "mapping each set to specific coordinates: "
                         "unverified"),
    ("gy rows", "Two rows only - each faction's start row doubles as its "
                "graveyard"),
    ("gy enum a", "SSM_GRAVEYARD_MAIN_ALLIANCE = 4062"),
    ("gy enum h", "SSM_GRAVEYARD_MAIN_HORDE = 4061"),
    ("gy rule", "always the player's own team's main row"),
    ("gy wiki", "only a single graveyard for each faction"),
    ("no point gy", "Which graveyard belongs to which point: none"),
    ("spirits", "spirit creatures 13116 (Alliance)"),
    ("spirits h", "13117 (Horde)"),
    ("gy dist", "Start-to-own-graveyard distance: 0 yd"),
    ("buff 1", "(727, 749.444153, 64.338188, 369.535797)  o 6.058259"),
    ("buff 2", "(727, 789.979431, 281.883575, 355.389984)  o 0.652173"),
    ("buff 3", "(727, 539.873596, 396.386749, 345.722412)  o 3.994188"),
    ("buff 4", "(727, 614.202698, 120.924660, 294.430908)  o 4.241807"),
    ("buff entry b", "gameobject entry 179905"),
    ("buff entry r", "gameobject entry 179904"),
    ("buff respawn", "BUFF_RESPAWN_TIME = 180 s"),
    ("greed", "Greed is Good"),
    ("src dump", "rows 4061, 4062 (starts = graveyards) and 4072-4075"),
    ("src exactly6", "the only map-727 rows in the dump (checked: "
                     "exactly 6)"),
    ("src no comment", 'no rows commented "Silvershard" (none)'),
    ("src wiki", "warcraft.wiki.gg: Silvershard Mines"),
    ("neg waypoint", "no rail waypoint data in any readable source"),
    ("neg ac", "AzerothCore's battleground_template has no Silvershard row"),
    ("neg header", "Negative results recorded"),
    ("unver header", "=== 8. EXPLICIT UNVERIFIED LIST ==="),
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
    lines, fails = [], []
    for name, lit in STATIC_CHECKS:
        if name == "unverified count":
            n = flat.count("unverified")
            hit = n >= UNVERIFIED_MIN
            lines.append("    %-24s %s (%d >= %d)"
                         % (name, "ok" if hit else "FAIL", n,
                            UNVERIFIED_MIN))
            if not hit:
                fails.append(name)
            continue
        hit = norm(lit) in flat
        lines.append("    %-24s %s" % (name, "ok" if hit else "MISSING"))
        if not hit:
            fails.append(name)
    for name, lit in NEGATIVE_CHECKS:
        hit = norm(lit) not in flat
        lines.append("    %-24s %s" % (name, "ok" if hit else "PRESENT!"))
        if not hit:
            fails.append(name)
    return fails, lines


MUTATIONS = [
    ("heading", "- COMPLETED ===\nBattleground", "- DRAFT ===\nBattleground"),
    ("numbering", "prompt 5 of 8", "prompt 5 of 7"),
    ("done", "DONE - step 5 of 8 complete", "DONE - step 5 of 9 complete"),
    ("compass", "makes NO coordinate-compass claims",
     "makes YES coordinate-compass claims"),
    ("band", "x 564.8048 - 896.7936", "x 564.8049 - 896.7936"),
    ("raw pattern", "851.575 vs 630.17", "851.576 vs 630.17"),
    ("map id", "727 = Silvershard Mines", "728 = Silvershard Mines"),
    ("start h", "(727, 630.17, 230.174, 328.838)",
     "(727, 630.17, 230.174, 328.839)"),
    ("start a", "(727, 851.575, 135.141, 328.838)",
     "(727, 851.575, 135.142, 328.838)"),
    ("start h o", "o 310.329", "o 310.330"),
    ("door 1 pos", "(727, 852.02, 158.21, 328.76)",
     "(727, 852.02, 158.22, 328.76)"),
    ("door 1 entry", "gameobject 212939", "gameobject 212943"),
    ("door 4 pos", "(727, 636.50, 208.12, 328.64)",
     "(727, 636.50, 208.13, 328.64)"),
    ("door dist a", "Alliance start to 212939 = 23 yd",
     "Alliance start to 212939 = 24 yd"),
    ("door dist h", "Horde start to 212941 = 22 yd",
     "Horde start to 212941 = 23 yd"),
    ("depot diamond row", "(727, 894.528, 30.7066, 363.927)",
     "(727, 894.528, 30.7066, 363.928)"),
    ("depot diamond go", "gameobject 212082", "gameobject 212084"),
    ("depot diamond pos", "(727, 896.7936, 25.29027, 364.1431)",
     "(727, 896.7936, 25.29027, 364.1432)"),
    ("depot wf row", "(727, 571.024, 336.894, 346.593)",
     "(727, 571.025, 336.894, 346.593)"),
    ("depot wf go", "gameobject 212080", "gameobject 212084"),
    ("depot lava pos", "(727, 615.5099, 79.41812, 298.2867)",
     "(727, 615.5099, 79.41813, 298.2867)"),
    ("depot troll row", "(727, 783.064, 495.927, 359.336)",
     "(727, 783.064, 495.928, 359.336)"),
    ("cart npc", "NPC creature entry 60140", "NPC creature entry 60141"),
    ("cart 1 pos", "(727, 744.542053, 183.545883, 319.658203)",
     "(727, 744.542053, 183.545883, 319.658204)"),
    ("cart 2 pos", "(727, 739.400330, 203.598511, 319.603333)",
     "(727, 739.400330, 203.598511, 319.603334)"),
    ("cart spell n", "spell 125695", "spell 125694"),
    ("cart spell e", "spell 125620", "spell 125621"),
    ("first cart", "first cart 10 s after start", "first cart 11 s after "
     "start"),
    ("switch east pos", "(727, 715.585388, 101.272034, 319.994690)",
     "(727, 715.585388, 101.272034, 319.994691)"),
    ("switch north pos", "(727, 847.481689, 308.032562, 346.573242)",
     "(727, 847.481689, 308.032562, 346.573243)"),
    ("switch npc", "60283", "60284"),
    ("switch opened", "spell 120228", "spell 120227"),
    ("switch cd", "cooldown 3000 ms", "cooldown 3001 ms"),
    ("trickle", "3 carts = 5 points, 2 carts = 3 points, 1 cart = 2 points",
     "3 carts = 5 points, 2 carts = 3 points, 1 cart = 4 points"),
    ("trickle timer", "every 2", "every 3"),
    ("arrival val", "150 points (script PointsPerMineCart)",
     "151 points (script PointsPerMineCart)"),
    ("cap script", "SSM_MAX_TEAM_POINTS = 1500",
     "SSM_MAX_TEAM_POINTS = 1501"),
    ("cap wiki", "first to 1600", "first to 1700"),
    ("a diamond", "legs: 23 yd, 140 yd", "legs: 23 yd, 141 yd"),
    ("a diamond direct", "direct 119 yd", "direct 120 yd"),
    ("h north", "legs: 22 yd, 211 yd", "legs: 22 yd, 212 yd"),
    ("a east direct", "direct 140 yd", "direct 141 yd"),
    ("pair dw", "Diamond-Waterfall 455 yd", "Diamond-Waterfall 456 yd"),
    ("pair lt", "Lava-Troll 453 yd", "Lava-Troll 454 yd"),
    ("pair wt", "Waterfall-Troll 270 yd", "Waterfall-Troll 271 yd"),
    ("gy enum a", "SSM_GRAVEYARD_MAIN_ALLIANCE = 4062",
     "SSM_GRAVEYARD_MAIN_ALLIANCE = 4063"),
    ("gy dist", "Start-to-own-graveyard distance: 0 yd",
     "Start-to-own-graveyard distance: 5 yd"),
    ("buff 1 pos", "(727, 749.444153, 64.338188, 369.535797)",
     "(727, 749.444153, 64.338188, 369.535798)"),
    ("buff 3 pos", "(727, 539.873596, 396.386749, 345.722412)",
     "(727, 539.873596, 396.386749, 345.722413)"),
    ("buff entry b", "gameobject entry 179905", "gameobject entry 179906"),
    ("buff respawn", "BUFF_RESPAWN_TIME = 180 s", "BUFF_RESPAWN_TIME = 181 s"),
    ("greed", "Greed is Good", "Greed is Better"),
    ("exactly 6", "checked: exactly 6", "checked: exactly 7"),
    ("not blizzlike", "not blizzlike", "fully blizzlike"),
    ("no comment", '"Silvershard" (none)', '"Silvershard" (dozens)'),
    ("waypoint neg", "waypoint data in any readable source",
     "waypoint data fully present in readable sources"),
]


def stage3(corpora):
    token_map = {
        "smh": [
            ("depot go diamond", "= 212082"),
            ("depot go waterfall", "= 212080"),
            ("depot go lava", "= 212081"),
            ("depot go troll", "= 212083"),
            ("door 1 entry", "= 212939"), ("door 2 entry", "= 212940"),
            ("door 3 entry", "= 212941"), ("door 4 entry", "= 212942"),
            ("gy a", "SSM_GRAVEYARD_MAIN_ALLIANCE     = 4062"),
            ("gy h", "SSM_GRAVEYARD_MAIN_HORDE        = 4061"),
            ("max points", "SSM_MAX_TEAM_POINTS                 = 1500"),
            ("switch npc", "NPC_TRACK_SWITCH            = 60283"),
            ("cart npc", "NPC_MINE_CART               = 60140"),
            ("spell north", "= 125695"), ("spell south", "= 125696"),
            ("spell east", "= 125620"), ("defend aura", "= 128646"),
            ("opened", "= 120228"), ("closed", "= 120229"),
            ("visual a", "= 116086"), ("visual h", "= 116085"),
            ("per cart", "= 150"),
            ("buff east row", "{749.444153f, 64.338188f, 369.535797f, "
                              "6.058259f}"),
            ("buff water row", "{539.873596f, 396.386749f, 345.722412f, "
                               "3.994188f}"),
            ("buff lava row", "{614.202698f, 120.924660f, 294.430908f, "
                              "4.241807f}"),
            ("depot pos diamond", "{896.7936f, 25.29027f, 364.1431f, "
                                  "3.539994f"),
            ("depot pos troll", "{777.7377f, 502.3111f, 359.4537f, "
                                "0.719448f"),
            ("door pos a1", "{852.02f, 158.21f, 328.76f, 0.15f}"),
            ("door pos h1", "{652.17f, 228.49f, 328.91f, 0.16f}"),
            ("switch pos e", "{715.585388f, 101.272034f, 319.994690f, "
                             "4.647377f}"),
            ("switch pos n", "{847.481689f, 308.032562f, 346.573242f, "
                             "0.587086f}"),
            ("cart count", "BG_SSM_MINE_CARTS_MAX"),
        ],
        "smc": [
            ("cart spawn 1", "744.542053f, 183.545883f, 319.658203f, "
                             "4.356342f"),
            ("cart spawn 2", "739.400330f, 203.598511f, 319.603333f, "
                             "2.308198f"),
            ("cart spawn 3", "760.184509f, 198.844742f, 319.446655f, "
                             "0.351249f"),
            ("setup depot a", "OBJECT_BG_SSM_THE_DESPOSITS_OF_DIAMONDS, "
                              "BgSSMDepotPos[0]"),
            ("setup door", "AddObject(BG_SSM_OBJECT_DOOR_A_1, "
                           "OBJECT_BG_SSM_DOOR1"),
            ("gy fn", "BattlegroundSilvershardMines::GetClosestGraveYard"),
            ("per cart fn", "PointsPerMineCart);"),
            ("trickle add", "AddPoints(TEAM_ALLIANCE, 5);"),
            ("addpoints timer", "_mineCartAddPointsTimer = 2000"),
            ("switch timer", "_trackSwitchClickTimer[SSM_EAST_TRACK_SWITCH] = 3000"),
            ("spawn timer", "_mineCartSpawnTimer = 10 * IN_MILLISECONDS"),
            ("speed", "SetSpeed(MOVE_WALK, 1.2f)"),
            ("buff bers entry", "BG_SSM_OBJECT_BERSERKING_BUFF_EAST, "
                                "BG_OBJECTID_BERSERKERBUFF_ENTRY"),
            ("buff regen entry", "BG_SSM_OBJECT_RESTORATION_BUFF_WATERFALL, "
                                 "BG_OBJECTID_REGENBUFF_ENTRY"),
            ("spirit a", "AddSpiritGuide(SSM_SPIRIT_ALLIANCE"),
            ("spirit h", "AddSpiritGuide(SSM_SPIRIT_HORDE"),
            ("switch spawn", "AddCreature(NPC_TRACK_SWITCH, "
                             "SSM_TRACK_SWITCH_EAST"),
        ],
        "wsl": [
            ("row 4061", "(4061,727,630.17,230.174,328.838,310.329,"
                         "'STV Diamond Mine - BG - Start - Horde "
                         "(Start)'),"),
            ("row 4062", "(4062,727,851.575,135.141,328.838,125.768,"
                         "'STV Diamond Mine - BG - Start - Alliance "
                         "(Start)'),"),
            ("row 4072", "(4072,727,571.024,336.894,346.593,2.6878,"
                         "'STV Diamond Mine - BG - Depot - Waterfall'),"),
            ("row 4073", "(4073,727,620.889,79.6562,298.326,9.01141,"
                         "'STV Diamond Mine - BG - Depot - Lava'),"),
            ("row 4074", "(4074,727,894.528,30.7066,363.927,115.242,"
                         "'STV Diamond Mine - BG - Depot - Diamond'),"),
            ("row 4075", "(4075,727,783.064,495.927,359.336,314.661,"
                         "'STV Diamond Mine - BG - Depot - Troll'),"),
        ],
    }
    corpora_map = {k: corpora[k] for k in token_map}
    return source_stage(corpora_map, token_map)


def parse_wsl_rows(wsl):
    rows = {}
    for line in wsl.splitlines():
        m = re.match(r"\((\d+),(\d+),([^,]+),([^,]+),([^,]+),([^,]+),(.*)\)",
                     line.strip())
        if not m:
            continue
        rid = int(m.group(1))
        if rid in DOC_IDS:
            rows[rid] = {"map": m.group(2), "x": m.group(3),
                         "y": m.group(4), "z": m.group(5),
                         "facing": m.group(6)}
    return rows


def rd(x):
    return int(x + 0.5)


def parse_arrays(smh, smc):
    out = {}
    m = re.search(r"BgSSMDepotPos\[\]\[8\] =\s*\{(.*?)\n\};", smh, re.S)
    out["depot"] = [tuple(v.strip().rstrip("f") for v in
                          re.findall(r"[-\d.]+f",
                                     row)[:4])
                    for row in re.findall(r"\{(.*?)\}", m.group(1), re.S)]
    m = re.search(r"BgSSMDoorPos\[4\]\[4\] =\s*\{(.*?)\n\};", smh, re.S)
    out["door"] = [tuple(v.strip().rstrip("f") for v in
                         re.findall(r"[-\d.]+f", row))
                   for row in re.findall(r"\{(.*?)\}", m.group(1), re.S)]
    m = re.search(r"BgSSMBuffPos\[4\]\[4\] =\s*\{(.*?)\n\};", smh, re.S)
    out["buff"] = [tuple(v.strip().rstrip("f") for v in
                         re.findall(r"[-\d.]+f", row))
                   for row in re.findall(r"\{(.*?)\}", m.group(1), re.S)]
    m = re.search(r"BgSSMTrackPos\[2\]\[4\] =\s*\{(.*?)\n\};", smh, re.S)
    out["track"] = [tuple(v.strip().rstrip("f") for v in
                          re.findall(r"[-\d.]+f", row))
                    for row in re.findall(r"\{(.*?)\}", m.group(1), re.S)]
    out["cart"] = re.findall(
        r"Position\(([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f\)", smc)
    return out


def stage4(text, corpora, probe=False):
    if probe:
        text = text.replace("(727, 851.575, 135.141, 328.838)",
                            "(727, 852.575, 135.141, 328.838)", 1)
    flat = norm(text)
    lines, fails = [], []

    rows = parse_wsl_rows(corpora["wsl"])
    hit = 0
    for rid in DOC_IDS:
        r = rows.get(rid)
        if not r:
            fails.append("row %d not in dump" % rid)
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

    arr = parse_arrays(corpora["smh"], corpora["smc"])
    cok = 0
    want_list = []
    for i, d in enumerate(arr["depot"]):
        want_list.append("(727, %s, %s, %s)" % d[:3])
    for d in arr["door"]:
        want_list.append("(727, %s, %s, %s)" % d[:3])
    for b in arr["buff"]:
        want_list.append("(727, %s, %s, %s)" % b[:3])
    for t in arr["track"]:
        want_list.append("(727, %s, %s, %s)" % t[:3])
    for c in arr["cart"]:
        want_list.append("(727, %s, %s, %s)" % c[:3])
    missing = [w for w in want_list if w not in flat]
    cok = len(want_list) - len(missing)
    if missing:
        fails.append("script triples missing: %s" % missing[:4])
    lines.append("    script coordinate triples matched: %d/%d"
                 % (cok, len(want_list)))

    # scalars from sources
    checks = []
    scal = {
        "cap": re.search(r"SSM_MAX_TEAM_POINTS\s*=\s*(\d+)",
                         corpora["smh"]).group(1),
        "percart": re.search(r"PointsPerMineCart\s*=\s*(\d+)",
                             corpora["smh"]).group(1),
        "timer": re.search(r"_mineCartAddPointsTimer = (\d+)",
                           corpora["smc"]).group(1),
        "cd": re.search(r"_trackSwitchClickTimer\[SSM_EAST_TRACK_SWITCH\] = "
                        r"(\d+)", corpora["smc"]).group(1),
        "spawn": re.search(r"_mineCartSpawnTimer = (\d+) \* IN_MILLISECONDS",
                           corpora["smc"]).group(1),
        "speed": re.search(r"SetSpeed\(MOVE_WALK, ([\d.]+)f\)",
                           corpora["smc"]).group(1),
    }
    checks += [
        ("cap", "SSM_MAX_TEAM_POINTS = %s" % scal["cap"]),
        ("arrival", "scores %s points" % scal["percart"]),
        ("trickle timer", "every %d seconds"
         % (int(scal["timer"]) // 1000)),
        ("switch cd", "cooldown %s ms" % scal["cd"]),
        ("first cart", "first cart %s s after start" % scal["spawn"]),
        ("speed", "cart walk speed %s" % scal["speed"]),
    ]
    sok = 0
    for name, want in checks:
        ok = want in flat
        sok += ok
        if not ok:
            fails.append("%s (%s)" % (name, want))
    lines.append("    script-derived scalars: %d/%d match doc"
                 % (sok, len(checks)))

    # distances
    A = (float(rows[4062]["x"]), float(rows[4062]["y"]))
    H = (float(rows[4061]["x"]), float(rows[4061]["y"]))
    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
    dA = (float(arr["door"][0][0]), float(arr["door"][0][1]))
    dH = (float(arr["door"][2][0]), float(arr["door"][2][1]))
    dep = arr["depot"]
    trk = arr["track"]
    names = ["Diamond", "Waterfall", "Lava", "Troll"]
    dok = 0
    for i, nm in enumerate(names):
        p = (float(dep[i][0]), float(dep[i][1]))
        for start, door, tag in ((A, dA, "a"), (H, dH, "h")):
            l1, l2, dirc = rd(dist(start, door)), rd(dist(door, p)), \
                rd(dist(start, p))
            ok = ("legs: %d yd, %d yd" % (l1, l2)) in flat and \
                 ("direct %d yd" % dirc) in flat
            dok += ok
            if not ok:
                fails.append("route %s->%s" % (tag, nm))
    lines.append("    depot routes: %d/8 match recompute" % dok)

    sok2 = 0
    for i, nm in enumerate(("East", "North")):
        p = (float(trk[i][0]), float(trk[i][1]))
        for start, door, tag in ((A, dA, "a"), (H, dH, "h")):
            l1, l2, dirc = rd(dist(start, door)), rd(dist(door, p)), \
                rd(dist(start, p))
            ok = ("legs: %d yd, %d yd" % (l1, l2)) in flat and \
                 ("direct %d yd" % dirc) in flat
            sok2 += ok
            if not ok:
                fails.append("route %s->sw %s" % (tag, nm))
    lines.append("    switch routes: %d/4 match recompute" % sok2)

    dok2 = 0
    for i in range(4):
        for j in range(i + 1, 4):
            p = (float(dep[i][0]), float(dep[i][1]))
            q = (float(dep[j][0]), float(dep[j][1]))
            want = "%s-%s %d yd" % (names[i], names[j], rd(dist(p, q)))
            ok = want in flat
            dok2 += ok
            if not ok:
                fails.append("pair %s" % want)
    lines.append("    depot pairs: %d/6 match recompute" % dok2)

    dd = [("Alliance start to 212939 = %d yd" % rd(dist(A, dA))),
          ("to 212940 = %d yd" % rd(dist(A, (float(arr["door"][1][0]),
                                             float(arr["door"][1][1]))))),
          ("Horde start to 212941 = %d yd" % rd(dist(H, dH))),
          ("to 212942 = %d yd" % rd(dist(H, (float(arr["door"][3][0]),
                                             float(arr["door"][3][1])))))]
    dok3 = sum(1 for w in dd if w in flat)
    if dok3 != 4:
        fails.append("door dists %s" % dok3)
    lines.append("    door distances: %d/4" % dok3)

    xs = [float(d[0]) for d in dep]
    ys = [float(d[1]) for d in dep]
    zs = [float(d[2]) for d in dep]
    want = "x %s - %s, y %s - %s, z %s - %s" % (
        str(min(xs)), str(max(xs)), str(min(ys)), str(max(ys)),
        str(min(zs)), str(max(zs)))
    ok = want in flat
    if not ok:
        fails.append("band (%s)" % want)
    lines.append("    depot band: %s" % ("ok" if ok else "MISMATCH " + want))

    # raw A>H x pattern from rows
    want = "%s vs %s" % (rows[4062]["x"], rows[4061]["x"])
    ok = want in flat
    if not ok:
        fails.append("raw pattern (%s)" % want)
    lines.append("    raw x pattern: %s" % ("ok" if ok else "MISMATCH"))

    ok_c, c_lines, missing_c = coord_trace(text, corpora)
    lines.extend(c_lines)
    if not ok_c:
        fails.append("coordinate trace: %s" % missing_c[:6])
    probe_txt = text.replace("(727, 630.17, 230.174, 328.838)",
                             "(727, 631.17, 230.174, 328.838)", 1)
    ok2, _, _ = coord_trace(probe_txt, corpora)
    probe_ok = (probe_txt != text) and not ok2
    lines.append("    coordinate probe reacts: %s"
                 % ("yes" if probe_ok else "no"))
    if not probe_ok:
        fails.append("coordinate probe")
    return fails, lines


def stage5(text, corpora):
    lines, fails = [], []
    m727 = []
    for line in corpora["wsl"].splitlines():
        m = re.match(r"\((\d+),(\d+),", line.strip())
        if m and m.group(2) == "727":
            m727.append(int(m.group(1)))
    ok = sorted(m727) == sorted(DOC_IDS)
    if not ok:
        fails.append("map-727 rows = %s" % sorted(m727))
    lines.append("    dump map-727 rows: %d, ids match: %s"
                 % (len(m727), "yes" if ok else "NO"))
    n_s = len(re.findall(r"(?i)silvershard", corpora["wsl"]))
    ok = n_s == 0
    if not ok:
        fails.append("dump has %d silvershard rows" % n_s)
    lines.append("    dump 'Silvershard'-commented rows: %d (need 0)" % n_s)
    n_ac = len(re.findall(r"(?i)silvershard|,727,", corpora["act"]))
    ok = n_ac == 0
    if not ok:
        fails.append("AC has %d matches" % n_ac)
    lines.append("    AzerothCore Silvershard/727 rows: %d (need 0)" % n_ac)

    # no rail waypoint movement calls in the script
    n_mp = len(re.findall(r"MovePoint|MoveSmooth|MoveSingleAnim", corpora["smc"]))
    ok = n_mp == 0
    if not ok:
        fails.append("script has %d movement calls" % n_mp)
    lines.append("    script rail MovePoint-style calls: %d (need 0)" % n_mp)

    for repo in (HAVEN, BFA):
        res = subprocess.run(
            ["gh", "api", "repos/%s/contents/src/server/game/"
             "Battlegrounds/Zones" % repo, "--jq", ".[].name"],
            capture_output=True, text=True)
        names = [n for n in res.stdout.split() if n]
        bad = [n for n in names if re.search(r"(?i)silvershard", n)]
        sanity = "BattlegroundAB.cpp" in names
        okc = res.returncode == 0 and sanity and not bad
        lines.append("    %-32s %d files, no Silvershard script: %s"
                     % (repo, len(names), "yes" if okc else "NO"))
        if not okc:
            fails.append("zones listing %s" % repo)

    inj1 = text + "\nnavmesh confirmed under inspection.\n"
    f1, _ = run_static(inj1)
    r1 = "no navmesh confirmed" in f1
    lines.append("    injection probe (navmesh confirmed):  %s"
                 % ("detected" if r1 else "NOT DETECTED"))
    if not r1:
        fails.append("navmesh probe")
    inj2 = text + "\nverified by direct inspection.\n"
    f2, _ = run_static(inj2)
    r2 = "no direct inspection" in f2
    lines.append("    injection probe (direct inspection):  %s"
                 % ("detected" if r2 else "NOT DETECTED"))
    if not r2:
        fails.append("direct-inspection probe")
    stripped = text.replace("unverified", "verified")
    f3, _ = run_static(stripped)
    r3 = "unverified count" in f3
    lines.append("    injection probe (unverified stripped):%s"
                 % (" detected" if r3 else " NOT DETECTED"))
    if not r3:
        fails.append("unverified probe")
    res = subprocess.run(
        ["gh", "api", "-X", "GET",
         "repos/Titans-Project/LegionCore-Reforged/contents/src/server/"
         "game/DoesNotExist.cpp"],
        capture_output=True, text=True)
    absent = res.returncode != 0
    lines.append("    control: bogus LegionCore path 404:      %s"
                 % ("yes" if absent else "NO"))
    if not absent:
        fails.append("gh 404 control")
    lines.append("    control: live corpora loaded:            %d"
                 % len(corpora))
    return fails, lines


def main():
    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()
    print("=" * 68)
    print("AUDIT: Coordinates_Silvershard_Mines_COMPLETED.txt (BG step 5)")
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
    corpora = {k: gh_content(LC, p) for k, p in FILES.items()}
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
        {"smc": [("cart1 float", "744.542053f")]},
        lambda t: t.replace("744.542053f", "744.543053f"))
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
