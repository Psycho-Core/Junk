#!/usr/bin/env python3
"""Audit: Coordinates_Warsong_Gulch_COMPLETED.txt (BG coords step 8)."""

import math
import re
import sys

sys.path.insert(0, ".")
from audit_common import gh_content, source_stage, mutation_probe, coord_trace

DOC = ("# Ai Research prompts/Battleground_Coordinates/"
       "Coordinates_Warsong_Gulch_COMPLETED.txt")
LC = "Titans-Project/LegionCore-Reforged"
TC = "TrinityCore/TrinityCore"
AC = "azerothcore/azerothcore-wotlk"
FILES = {
    "h": "src/server/game/Battlegrounds/Zones/BattlegroundWarsongGulch.h",
    "c": "src/server/game/Battlegrounds/Zones/BattlegroundWarsongGulch.cpp",
    "bh": "src/server/game/Battlegrounds/Battleground.h",
}
TC_DUMP = "sql/old/8.x/world/19071_2020_06_17/2019_10_26_01_world.sql"
AC_TEMPLATE = "data/sql/base/db_world/battleground_template.sql"
DOC_IDS = [769, 770, 771, 772, 3698, 3699, 3784, 3785, 7050, 7051, 7052, 7053]
UNVERIFIED_MIN = 14


def norm(s):
    return re.sub(r"\s+", " ", s)


STATIC_CHECKS = [
    ("heading", "=== WARSONG GULCH COORDINATES - BFA 8.3.7 (TRINITYCORE) - "
                "COMPLETED ==="),
    ("numbering", "Prompt 8 of 8 (Warsong Gulch, maps 489 and 2106)"),
    ("done", "DONE - step 8 of 8 complete"),
    ("no-estimate", "nothing is estimated"),
    ("unverified policy", 'the line says "unverified"'),
    ("no compass", "makes NO compass claims"),
    ("pathing caveat", "no pathing/navmesh source for map 489 or 2106 is"),
    ("maps", "489 = Warsong Gulch (classic), 2106 = Warsong Gulch variant"),
    ("no map literal", 'no "489" or "2106" literal at all'),
    ("no 2106 refs", "zero references to the map-2106 rows\n   7050-7053"),
    ("exactly12", "exactly 12 rows for maps 489 and 2106"),
    ("row split", "8 on 489, 4 on 2106"),
    ("ac row", "battleground_template row (2,...,769,3.14159,770,"
               "0.151581,75,..."),
    ("ac startloc", "StartLoc 769/770 (the same\n   FLAGROOM ids the "
                    "LegionCore script uses)"),
    ("ac 75", "value 75 in the\n   MaxTeamScore column (raw value 75; its "
              "retail meaning is\n   unverified)"),
    ("row 769", 'id 769  (489, 1523.81, 1481.76, 352.008)  o 180'),
    ("row 770", 'id 770  (489, 933.331, 1433.72, 345.536)  o 0'),
    ("row 771", 'id 771  (489, 1406.65, 1564.74, 328.326)  o 203.635'),
    ("row 772", 'id 772  (489, 1061.6, 1377.09, 328.558)  o 337'),
    ("row 3698", 'id 3698 (489, 1018.47, 1297.47, 342.959)  o 360'),
    ("row 3699", 'id 3699 (489, 1018.47, 1297.47, 342.959)  o 360'),
    ("row 3784", 'id 3784 (489, 1528.2, 1481.45, 351.992)  o 180'),
    ("row 3785", 'id 3785 (489, 930.716, 1435.44, 345.536)  o 360'),
    ("row 7050", 'id 7050 (2106, 933.66, 1434.7, 345.536)  o 0'),
    ("row 7051", 'id 7051 (2106, 1523.81, 1481.76, 352.008)  o 180'),
    ("row 7052", 'id 7052 (2106, 1407.48, 1561.21, 328.351)  o 196.435'),
    ("row 7053", 'id 7053 (2106, 1058.21, 1375.86, 328.597)  o 7.15001'),
    ("row 7051 note", "same xyz as id 769"),
    ("script uses 769-772", "it uses 769-772 only"),
    ("start a", "Alliance start (489, 1523.81, 1481.76, 352.008)"),
    ("start h", "Horde start    (489, 933.331, 1433.72, 345.536)"),
    ("ten doors", "Ten gate doors spawn in SetupBattleground"),
    ("door a1", "Alliance door 1 gameobject 179918 (489, 1503.335, "
                "1493.466, 352.1888)"),
    ("door a2", "(489, 1492.478, 1457.912, 342.9689)"),
    ("door a3", "(489, 1468.503, 1494.357, 351.8618)"),
    ("door a4", "(489, 1471.555, 1458.778, 362.6332)"),
    ("door a5", "Alliance door 5 gameobject 180322 (489, 1492.347, "
                "1458.34, 342.3712)"),
    ("door a6", "Alliance door 6 gameobject 180322 (489, 1503.466, "
                "1493.367, 351.7352)"),
    ("door h1", "Horde door 1 gameobject 179916 (489, 949.1663, 1423.772, "
                "345.6241)"),
    ("door h2", "Horde door 2 gameobject 179917 (489, 953.0507, 1459.842, "
                "340.6526)"),
    ("door h3", "Horde door 3 gameobject 180322 (489, 949.9523, 1422.751, "
                "344.9273)"),
    ("door h4", "Horde door 4 gameobject 180322 (489, 950.7952, 1459.583, "
                "342.1523)"),
    ("reclose", "doors A5, A6, H3, H4 are then re-closed for the match"),
    ("rot a", "o values are 3.115414 (A1-A4), -0.03490669 (A5,"),
    ("quat h1", "(-0.01673368, -0.004956111, -0.2839723, 0.9586737)"),
    ("timer15", "GameTime + Minutes(15)"),
    ("no orbs", "no orbs, carts, mines or nodes exist in this"),
    ("flag a", "Alliance flag gameobject 227741 (489, 1540.423, 1481.325, "
               "351.8284)"),
    ("flag a o", "o 3.089233"),
    ("flag h", "Horde flag gameobject 227740 (489, 916.0226, 1434.405, "
               "345.413)"),
    ("flag h o", "o 0.01745329"),
    ("ground a", "Alliance ground (dropped) flag gameobject 227745"),
    ("ground h", "Horde ground (dropped) flag gameobject 227744"),
    ("ground dyn", "CARRIER'S DROP POSITION"),
    ("timers", "BG_WS_FLAG_RESPAWN_TIME = 10000 ms, BG_WS_FLAG_DROP_TIME = "
               "10000 ms"),
    ("respawn param", "BG_WS_FLAG_RESPAWN_TIME / 1000 = 10 s"),
    ("max 3", "BG_WS_MAX_TEAM_SCORE = 3 (GetMaxScore() returns 3)"),
    ("max brawl", "BG_WS_MAX_TEAM_SCORE_BRAWL = 10"),
    ("2106 flag unver", "The map-2106 flag positions are unverified as "
                        "separate values"),
    ("routes hdr", "ROUTES - STRAIGHT-LINE LEGS THROUGH SCRIPTED OBJECTS"),
    ("route caveat", "NOT walkable-path measurements"),
    ("route a", "legs: 17 yd    direct 17 yd"),
    ("route b", "legs: 23 yd (start to Alliance door 6), 590 yd"),
    ("route b direct", "direct 610 yd"),
    ("route d", "legs: 19 yd (start to Horde door 1), 594 yd"),
    ("route d direct", "direct 609 yd"),
    ("cross", "Flag-to-flag cross distance (recomputed): 626 yd"),
    ("ctx a1", "Alliance Rez (771) to Alliance flag: 158 yd"),
    ("ctx h1", "Horde Rez (772) to Horde flag: 156 yd"),
    ("ctx a2", "Alliance Rez to Horde flag: 508 yd"),
    ("ctx h2", "Horde Rez to Alliance flag: 490 yd"),
    ("ctx e1", "Alliance Enter to Alliance Rez: 144 yd"),
    ("ctx e2", "Horde Enter to Horde Rez: 140 yd"),
    ("ctx pair e", "Enter pair (769-770): 592 yd"),
    ("ctx pair r", "Rez pair (771-772): 393 yd"),
    ("gy hdr", "GRAVEYARDS - WHICH ONE BELONGS TO WHICH POINT"),
    ("gy enum a", "ALLIANCE = 769, WS_GRAVEYARD_FLAGROOM_HORDE = 770"),
    ("gy enum b", "WS_GRAVEYARD_MAIN_ALLIANCE = 771, WS_GRAVEYARD_MAIN_HORDE "
                  "= 772"),
    ("rule waiting", "your team's FLAGROOM row = the Enter Loc behind your "
                     "base doors (Alliance 769, Horde 770)"),
    ("rule main", "your team's MAIN row = the Rez"),
    ("rule main2", "(Alliance 771, Horde 772)"),
    ("no neutral", "No neutral/midfield graveyard exists"),
    ("gy per point", "dying anywhere in the match sends you to your own "
                     "base's Rez row"),
    ("ant cheat", "are teleport"),
    ("spirit hdr", "Spirit guides: SetupBattleground spawns exactly two"),
    ("spirit add", "AddSpiritGuide(WS_SPIRIT_MAIN_ALLIANCE, 771's loc)"),
    ("spirit add2", "AddSpiritGuide(WS_SPIRIT_MAIN_HORDE, 772's loc)"),
    ("spirit entries", "13116 (Alliance) / 13117 (Horde)"),
    ("no spirit flagroom", "No spirit guide is spawned at the FLAGROOM rows"),
    ("buff hdr", "BUFF SPAWNS (SetupBattleground"),
    ("buff entries", "speed 179871, regeneration 179904,\n   berserking "
                     "179905"),
    ("buff respawn", "BUFF_RESPAWN_TIME from\n   Battleground.h = 180 s"),
    ("buff sp1", "Speed gameobject 179871 (489, 1449.93, 1470.71, "
                 "342.6346)"),
    ("buff sp1 o", "o -1.64061"),
    ("buff sp2", "(489, 1005.171, 1447.946, 335.9032)"),
    ("buff rg1", "Regeneration gameobject 179904 (489, 1317.506, 1550.851, "
                 "313.2344)"),
    ("buff rg2", "(489, 1110.451, 1353.656, 316.5181)"),
    ("buff bz1", "Berserking gameobject 179905 (489, 1320.09, 1378.79, "
                 "314.7532)"),
    ("buff bz2", "(489, 1139.688, 1560.288, 306.8432)"),
    ("band", "x 1005.171 - 1449.93,\n    y 1353.656 - 1560.288"),
    ("buff 2106 unver", "Buff positions on a map-2106 instance: unverified"),
    ("buff retail unver", "Retail parity of these six spawns is unverified"),
    ("brawl hdr", "BRAWL VARIANTS (same script"),
    ("brawl allsix a", "Alliance 227741 (489, 1357.948,"),
    ("brawl allsix h", "Horde 227740 (489, 1119.123,"),
    ("brawl allsix z", "(489, 1357.948,\n    1462.004, 325.2907)"),
    ("brawl extra", "extra flag objects at (489, 1529.36, 1474.93, "
                    "351.987) o 2.65"),
    ("brawl post a", "Alliance postaments gameobject\n    269358"),
    ("brawl post h", "Horde postaments\n    gameobject 227038"),
    ("brawl buffs", "five brawl\n    buffs gameobject 268652"),
    ("brawl spells", "238485, 239223, 239224,\n    239227, apply-get 239221"),
    ("brawl 10s", "respawn parameter\n    BG_WS_FLAG_RESPAWN_TIME / 1000 = "
                  "10 s"),
    ("brawl max", "Scramble max score = 10"),
    ("src dump", "2019_10_26_01_world.sql: exactly 12 rows"),
    ("src script", "BattlegroundWarsongGulch.cpp\n    and .h (Zones)"),
    ("src bh", "Battleground.h base-class ids"),
    ("neg literal", "The script\n   contains no"),
    ("neg 7050", "(the script references only 769-772)"),
    ("unver hdr", "10. EXPLICIT UNVERIFIED LIST"),
    ("unver queue", "Whether your server queues map 489 or 2106"),
    ("unver door", "Which door a walking player actually uses to leave "
                   "each base"),
    ("unver choke", "Named chokepoints, ramps, tunnels and stairs per "
                    "route"),
]

NEGATIVE_CHECKS = [
    ("no estimated coordinate", "estimated coordinate"),
    ("no navmesh confirmed", "navmesh confirmed"),
    ("no direct inspection", "verified by direct inspection"),
    ("no todo", "TODO"),
    ("no fixme", "FIXME"),
    ("no 1500 claim", "1500 points"),
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
    n17 = flat.count("legs: 17 yd direct 17 yd")
    lines.append("    %-24s %s (%d >= 2)" % ("route 17 x2",
                 "ok" if n17 >= 2 else "FAIL", n17))
    if n17 < 2:
        fails.append("route 17 x2")
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
    ("heading", "- COMPLETED ===", "- DRAFT ==="),
    ("numbering", "Prompt 8 of 8", "Prompt 8 of 9"),
    ("done", "DONE - step 8 of 8 complete", "DONE - step 8 of 9 complete"),
    ("compass", "makes NO compass claims", "makes YES compass claims"),
    ("map literal", 'no "489" or "2106" literal at all',
     'no "4890" or "2106" literal at all'),
    ("exactly12", "exactly 12 rows for maps 489 and 2106",
     "exactly 13 rows for maps 489 and 2106"),
    ("row split", "8 on 489, 4 on 2106", "8 on 489, 5 on 2106"),
    ("row 769", "(489, 1523.81, 1481.76, 352.008)  o 180",
     "(489, 1523.81, 1481.76, 352.009)  o 180"),
    ("row 772", "(489, 1061.6, 1377.09, 328.558)",
     "(489, 1061.6, 1377.09, 328.559)"),
    ("row 7052", "(2106, 1407.48, 1561.21, 328.351)",
     "(2106, 1407.48, 1561.21, 328.352)"),
    ("row 7053 o", "o 7.15001", "o 7.15002"),
    ("ac row", "769,3.14159,770,0.151581,75", "769,3.14159,770,0.151581,76"),
    ("start a", "Alliance start (489, 1523.81, 1481.76, 352.008)",
     "Alliance start (489, 1523.81, 1481.76, 352.007)"),
    ("start h", "Horde start    (489, 933.331, 1433.72, 345.536)",
     "Horde start    (489, 933.331, 1433.72, 345.537)"),
    ("door a1", "(489, 1503.335, 1493.466, 352.1888)",
     "(489, 1503.335, 1493.466, 352.1889)"),
    ("door a1 entry", "door 1 gameobject 179918", "door 1 gameobject 179919"),
    ("door a5 entry", "door 5 gameobject 180322", "door 5 gameobject 180323"),
    ("door h1 pos", "(489, 949.1663, 1423.772, 345.6241)",
     "(489, 949.1663, 1423.772, 345.6242)"),
    ("door h2 entry", "door 2 gameobject 179917", "door 2 gameobject 179918"),
    ("reclose", "doors A5, A6, H3, H4 are then re-closed",
     "doors A5, A6, H3, H4 are then never re-closed"),
    ("timer15", "GameTime + Minutes(15)", "GameTime + Minutes(16)"),
    ("flag a entry", "Alliance flag gameobject 227741",
     "Alliance flag gameobject 227742"),
    ("flag a pos", "(489, 1540.423, 1481.325, 351.8284)",
     "(489, 1540.423, 1481.325, 351.8285)"),
    ("flag h pos", "(489, 916.0226, 1434.405, 345.413)",
     "(489, 916.0226, 1434.405, 345.414)"),
    ("ground entries", "dropped) flag gameobject 227745",
     "dropped) flag gameobject 227746"),
    ("timer r", "BG_WS_FLAG_RESPAWN_TIME = 10000",
     "BG_WS_FLAG_RESPAWN_TIME = 10001"),
    ("timer d", "BG_WS_FLAG_DROP_TIME = 10000",
     "BG_WS_FLAG_DROP_TIME = 10001"),
    ("max 3", "BG_WS_MAX_TEAM_SCORE = 3", "BG_WS_MAX_TEAM_SCORE = 4"),
    ("brawl max", "BG_WS_MAX_TEAM_SCORE_BRAWL = 10",
     "BG_WS_MAX_TEAM_SCORE_BRAWL = 11"),
    ("route 17", "legs: 17 yd    direct 17 yd", "legs: 18 yd    direct 17 yd"),
    ("route b leg1", "legs: 23 yd (start to Alliance door 6)",
     "legs: 24 yd (start to Alliance door 6)"),
    ("route b leg2", "590 yd (door 6 to Horde", "591 yd (door 6 to Horde"),
    ("route b direct", "direct 610 yd", "direct 611 yd"),
    ("route d leg1", "legs: 19 yd (start to Horde door 1)",
     "legs: 20 yd (start to Horde door 1)"),
    ("route d leg2", "594 yd (door 1 to Alliance", "595 yd (door 1 to "
     "Alliance"),
    ("route d direct", "direct 609 yd", "direct 608 yd"),
    ("cross", "recomputed): 626 yd", "recomputed): 627 yd"),
    ("ctx a1", "Alliance flag: 158 yd", "Alliance flag: 159 yd"),
    ("ctx h2", "to Alliance flag: 490 yd", "to Alliance flag: 491 yd"),
    ("ctx pair r", "Rez pair (771-772): 393 yd", "Rez pair (771-772): 394 yd"),
    ("gy enum", "ALLIANCE = 769, WS_GRAVEYARD_FLAGROOM_HORDE = 770",
     "ALLIANCE = 771, WS_GRAVEYARD_FLAGROOM_HORDE = 770"),
    ("rule waiting", "(Alliance 769, Horde 770)", "(Alliance 771, Horde 770)"),
    ("rule main", "(Alliance 771, Horde 772)", "(Alliance 772, Horde 771)"),
    ("spirit add", "AddSpiritGuide(WS_SPIRIT_MAIN_ALLIANCE, 771's loc)",
     "AddSpiritGuide(WS_SPIRIT_MAIN_ALLIANCE, 769's loc)"),
    ("spirit entries", "13117 (Horde)", "13118 (Horde)"),
    ("buff entry sp", "Speed gameobject 179871 (489, 1449.93",
     "Speed gameobject 179872 (489, 1449.93"),
    ("buff sp1 pos", "(489, 1449.93, 1470.71, 342.6346)",
     "(489, 1449.93, 1470.71, 342.6347)"),
    ("buff bz2 pos", "(489, 1139.688, 1560.288, 306.8432)",
     "(489, 1139.688, 1560.288, 306.8433)"),
    ("buff respawn", "Battleground.h = 180 s", "Battleground.h = 181 s"),
    ("band", "x 1005.171 - 1449.93", "x 1005.172 - 1449.93"),
    ("brawl allsix", "(489, 1357.948,\n    1462.004, 325.2907)",
     "(489, 1357.948,\n    1462.004, 325.2908)"),
    ("brawl post", "postaments gameobject\n    269358",
     "postaments gameobject\n    269359"),
    ("brawl buff entry", "buffs gameobject 268652", "buffs gameobject 268653"),
    ("brawl spells", "238485, 239223, 239224", "238485, 239223, 239225"),
]


def parse_wsl(wsl):
    rows = {}
    for line in wsl.splitlines():
        m = re.match(r"\((\d+),(489|2106),([^,]+),([^,]+),([^,]+),([^,]+),(.*)\)",
                     line.strip())
        if not m:
            continue
        rid = int(m.group(1))
        if rid in DOC_IDS:
            rows[rid] = {"map": m.group(2), "x": m.group(3),
                         "y": m.group(4), "z": m.group(5),
                         "facing": m.group(6)}
    return rows


def parse_script(h, c):
    out = {}

    def last3(pat, s):
        m = re.search(pat, s)
        return tuple(v.strip().rstrip("f") for v in m.groups())

    out["flag_a"] = last3(
        r"BG_OBJECT_A_FLAG_WS_ENTRY, ([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f", c)
    out["flag_h"] = last3(
        r"BG_OBJECT_H_FLAG_WS_ENTRY, ([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f", c)
    m = re.search(
        r"BrawlAllSix\)\s*\{(.*?)BrawlBattlegroundWarsongScramble",
        c, re.S)
    blk = m.group(1)
    ma = re.search(r"BG_OBJECT_A_FLAG_WS_ENTRY, ([-\d.]+)f, ([-\d.]+)f, "
                   r"([-\d.]+)f", blk)
    mh = re.search(r"BG_OBJECT_H_FLAG_WS_ENTRY, ([-\d.]+)f, ([-\d.]+)f, "
                   r"([-\d.]+)f", blk)
    out["allsix_a"] = tuple(v.rstrip("f") for v in ma.groups())
    out["allsix_h"] = tuple(v.rstrip("f") for v in mh.groups())
    out["doors"] = re.findall(
        r"AddObject\(BG_WS_OBJECT_DOOR_[AH]_\d, BG_OBJECT_DOOR_[AH]_\d_"
        r"WS_ENTRY, ([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f", c)
    out["buffs"] = re.findall(
        r"(BG_OBJECTID_\w+_ENTRY), ([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f, "
        r"[-\d.]+f, 0, 0, [-\d.]+f, [-\d.]+f, BUFF_RESPAWN_TIME", c)
    m = re.search(r"BG_WS_FLAG_RESPAWN_TIME\s+=\s*(\d+)", h)
    out["timer_r"] = m.group(1)
    m = re.search(r"BG_WS_FLAG_DROP_TIME\s+=\s*(\d+)", h)
    out["timer_d"] = m.group(1)
    m = re.search(r"BG_WS_MAX_TEAM_SCORE\s+=\s*(\d+)", h)
    out["max"] = m.group(1)
    m = re.search(r"BG_WS_MAX_TEAM_SCORE_BRAWL\s+=\s*(\d+)", h)
    out["max_brawl"] = m.group(1)
    m = re.search(r"BUFF_RESPAWN_TIME\s*=\s*(\d+)",
                  parse_script.BH if parse_script.BH else "")
    out["buff_respawn"] = m.group(1) if m else None
    return out


parse_script.BH = ""


def rd(x):
    return int(x + 0.5)


def stage3(corpora):
    parse_script.BH = corpora.get("bh") or ""
    token_map = {
        "h": [
            ("max", "BG_WS_MAX_TEAM_SCORE                    = 3"),
            ("max brawl", "BG_WS_MAX_TEAM_SCORE_BRAWL              = 10"),
            ("timer r", "BG_WS_FLAG_RESPAWN_TIME                 = 10000"),
            ("timer d", "BG_WS_FLAG_DROP_TIME                    = 10000"),
            ("door a1", "BG_OBJECT_DOOR_A_1_WS_ENTRY          = 179918"),
            ("door a5", "BG_OBJECT_DOOR_A_5_WS_ENTRY          = 180322"),
            ("door h1", "BG_OBJECT_DOOR_H_1_WS_ENTRY          = 179916"),
            ("flag a", "BG_OBJECT_A_FLAG_WS_ENTRY            = 227741"),
            ("flag h", "BG_OBJECT_H_FLAG_WS_ENTRY            = 227740"),
            ("ground a", "BG_OBJECT_A_FLAG_GROUND_WS_ENTRY     = 227745"),
            ("ground h", "BG_OBJECT_H_FLAG_GROUND_WS_ENTRY     = 227744"),
            ("brawl buff", "BG_BRAWL_BUFF_ENTRY                  = 268652"),
            ("post a", "BG_BRAWL_A_POSTAMENT                 = 269358"),
            ("post h", "BG_BRAWL_H_POSTAMENT                 = 227038"),
            ("gy a", "WS_GRAVEYARD_FLAGROOM_ALLIANCE = 769"),
            ("gy h", "WS_GRAVEYARD_FLAGROOM_HORDE    = 770"),
            ("gy ma", "WS_GRAVEYARD_MAIN_ALLIANCE     = 771"),
            ("gy mh", "WS_GRAVEYARD_MAIN_HORDE        = 772"),
            ("maxscore fn", "GetMaxScore() const override { return 3; }"),
            ("brawl spell", "SPELL_BG_WS_BRAWL_BUFF_1                  = "
                            "238485"),
            ("brawl pos", "BG_OBJECT_A_FLAG_WS_ENTRY ,{ 1529.36f"),
        ],
        "c": [
            ("buff sp1", "BG_OBJECTID_SPEEDBUFF_ENTRY, 1449.93f, 1470.71f, "
                         "342.6346f"),
            ("buff sp2", "BG_OBJECTID_SPEEDBUFF_ENTRY, 1005.171f, 1447.946f, "
                         "335.9032f"),
            ("buff rg1", "BG_OBJECTID_REGENBUFF_ENTRY, 1317.506f, 1550.851f, "
                         "313.2344f"),
            ("buff rg2", "BG_OBJECTID_REGENBUFF_ENTRY, 1110.451f, 1353.656f, "
                         "316.5181f"),
            ("buff bz1", "BG_OBJECTID_BERSERKERBUFF_ENTRY, 1320.09f, "
                         "1378.79f, 314.7532f"),
            ("buff bz2", "BG_OBJECTID_BERSERKERBUFF_ENTRY, 1139.688f, "
                         "1560.288f, 306.8432f"),
            ("door a1", "BG_OBJECT_DOOR_A_1_WS_ENTRY, 1503.335f, 1493.466f, "
                        "352.1888f"),
            ("door h4", "BG_OBJECT_DOOR_H_4_WS_ENTRY, 950.7952f, 1459.583f, "
                        "342.1523f"),
            ("flag a", "BG_OBJECT_A_FLAG_WS_ENTRY, 1540.423f, 1481.325f, "
                       "351.8284f"),
            ("flag h", "BG_OBJECT_H_FLAG_WS_ENTRY, 916.0226f, 1434.405f, "
                       "345.413f"),
            ("allsix a", "BrawlAllSix)\n    {\n        if (!AddObject("
                         "BG_WS_OBJECT_A_FLAG, BG_OBJECT_A_FLAG_WS_ENTRY, "
                         "1357.948f"),
            ("timer param", "BG_WS_FLAG_RESPAWN_TIME / 1000"),
            ("gy fn", "graveyardsInProgress[2] = { WS_GRAVEYARD_MAIN_"
                      "ALLIANCE, WS_GRAVEYARD_MAIN_HORDE }"),
            ("gy fn2", "graveyards[2] = { WS_GRAVEYARD_FLAGROOM_ALLIANCE, "
                       "WS_GRAVEYARD_FLAGROOM_HORDE }"),
            ("spirit a", "AddSpiritGuide(WS_SPIRIT_MAIN_ALLIANCE, sg->Loc, "
                         "TEAM_ALLIANCE)"),
            ("spirit h", "AddSpiritGuide(WS_SPIRIT_MAIN_HORDE, sg->Loc, "
                         "TEAM_HORDE)"),
            ("timer15", "std::chrono::duration_cast<Seconds>(Minutes(15))"),
            ("capture", "m_TeamScores[team]++"),
            ("reclose", "SpawnBGObject(BG_WS_OBJECT_DOOR_A_5, "
                        "RESPAWN_ONE_DAY)"),
        ],
        "bh": [
            ("buff respawn", "BUFF_RESPAWN_TIME"),
            ("spirit a", "13116"),
            ("spirit h", "13117"),
            ("buff entries", "179871"),
        ],
        "wsl": [("row %d" % i, "(%d,%s,%s,%s,%s,%s," % (i, r["map"],
                r["x"], r["y"], r["z"], r["facing"]))
                for i, r in parse_wsl(corpora["wsl"]).items()],
        "act": [("ac row", "(2,5,10,10,80,769,3.14159,770,0.151581,75,1")],
    }
    corpora_map = {k: corpora.get(k, "") for k in token_map}
    return source_stage(corpora_map, token_map)


def stage4(text, corpora, probe=False):
    if probe:
        text = text.replace("(489, 1523.81, 1481.76, 352.008)",
                            "(489, 1524.81, 1481.76, 352.008)")
    flat = norm(text)
    lines, fails = [], []
    parse_script.BH = corpora.get("bh") or ""

    rows = parse_wsl(corpora["wsl"])
    hit = 0
    for rid in DOC_IDS:
        r = rows.get(rid)
        if not r:
            fails.append("row %d missing in dump" % rid)
            continue
        triple = "(%s, %s, %s, %s)" % (r["map"], r["x"], r["y"], r["z"])
        context = triple in flat or ("id %d" % rid) in flat
        facing_ok = re.search(r"(?<![0-9.])o %s(?![0-9.])"
                              % re.escape(r["facing"]), flat)
        ok = triple in flat and context and bool(facing_ok)
        hit += ok
        if not ok:
            fails.append("row %d mismatch" % rid)
    lines.append("    world_safe rows matched: %d/%d" % (hit, len(DOC_IDS)))

    s = parse_script(corpora["h"], corpora["c"])
    want = ["(489, %s, %s, %s)" % t[:3] for t in (s["flag_a"], s["flag_h"],
                                                   s["allsix_a"],
                                                   s["allsix_h"])]
    want += ["(489, %s, %s, %s)" % t[:3] for t in s["doors"]]
    want += ["(489, %s, %s, %s)" % t[1:4] for t in s["buffs"]]
    missing = [w for w in want if w not in flat]
    lines.append("    script coordinate triples matched: %d/%d"
                 % (len(want) - len(missing), len(want)))
    if missing:
        fails.append("script triples missing: %s" % missing[:5])

    checks = [
        ("timer r", "BG_WS_FLAG_RESPAWN_TIME = %s ms" % s["timer_r"]),
        ("timer d", "BG_WS_FLAG_DROP_TIME = %s ms" % s["timer_d"]),
        ("max", "BG_WS_MAX_TEAM_SCORE = %s" % s["max"]),
        ("brawl max", "BG_WS_MAX_TEAM_SCORE_BRAWL = %s" % s["max_brawl"]),
        ("respawn param", "BG_WS_FLAG_RESPAWN_TIME / 1000 = %s s"
         % rd(int(s["timer_r"]) / 1000.0)),
    ]
    if s["buff_respawn"]:
        checks.append(("buff respawn", "Battleground.h = %s s"
                       % s["buff_respawn"]))
    sok = 0
    for name, want in checks:
        ok = want in flat
        sok += ok
        if not ok:
            fails.append("%s (%s)" % (name, want.replace("\n", " ")))
    lines.append("    script-derived scalars: %d/%d match doc"
                 % (sok, len(checks)))

    P = {k: (float(r["x"]), float(r["y"])) for k, r in rows.items()}
    P["A_flag"] = tuple(float(v) for v in s["flag_a"])
    P["H_flag"] = tuple(float(v) for v in s["flag_h"])
    P["A_doors"] = [tuple(float(v) for v in t[:2]) for t in s["doors"][:6]]
    P["H_doors"] = [tuple(float(v) for v in t[:2]) for t in s["doors"][6:]]
    dist = lambda a, b: math.hypot(a[0] - b[0], a[1] - b[1])

    ok_a = rd(dist(P[769], P["A_flag"]))
    ok_h = rd(dist(P[770], P["H_flag"]))
    nA = min(range(6), key=lambda i: dist(P[769], P["A_doors"][i]))
    nH = min(range(4), key=lambda i: dist(P[770], P["H_doors"][i]))
    dA = [rd(dist(P[769], d)) for d in P["A_doors"]]
    dH = [rd(dist(P[770], d)) for d in P["H_doors"]]
    legsB = (dA[nA], rd(dist(P["A_doors"][nA], P["H_flag"])))
    legsD = (dH[nH], rd(dist(P["H_doors"][nH], P["A_flag"])))
    dirB = rd(dist(P[769], P["H_flag"]))
    dirD = rd(dist(P[770], P["A_flag"]))
    cross = rd(dist(P["A_flag"], P["H_flag"]))
    route_checks = [
        ("own flag A", flat.count("legs: %d yd direct %d yd"
                                  % (ok_a, ok_a)) >= 2),
        ("route B", ("legs: %d yd (start to Alliance door %d), %d yd"
                     % (legsB[0], nA + 1, legsB[1])) in flat),
        ("route B direct", "direct %d yd" % dirB in flat),
        ("route D", ("legs: %d yd (start to Horde door %d), %d yd"
                     % (legsD[0], nH + 1, legsD[1])) in flat),
        ("route D direct", "direct %d yd" % dirD in flat),
        ("cross", "Flag-to-flag cross distance (recomputed): %d yd"
         % cross in flat),
    ]
    rok = 0
    for name, ok in route_checks:
        rok += ok
        if not ok:
            fails.append("route %s" % name)
    lines.append("    routes: %d/%d match recompute (own %d/%d, nearest "
                 "doors A%d/H%d)" % (rok, len(route_checks), ok_a, ok_h,
                                     nA + 1, nH + 1))

    pairs = [
        ("Alliance Rez (771) to Alliance flag: %d yd"
         % rd(dist(P[771], P["A_flag"])), "a1"),
        ("Horde Rez (772) to Horde flag: %d yd"
         % rd(dist(P[772], P["H_flag"])), "h1"),
        ("Alliance Rez to Horde flag: %d yd"
         % rd(dist(P[771], P["H_flag"])), "a2"),
        ("Horde Rez to Alliance flag: %d yd"
         % rd(dist(P[772], P["A_flag"])), "h2"),
        ("Alliance Enter to Alliance Rez: %d yd"
         % rd(dist(P[769], P[771])), "e1"),
        ("Horde Enter to Horde Rez: %d yd"
         % rd(dist(P[770], P[772])), "e2"),
        ("Enter pair (769-770): %d yd" % rd(dist(P[769], P[770])), "pe"),
        ("Rez pair (771-772): %d yd" % rd(dist(P[771], P[772])), "pr"),
    ]
    cok = 0
    for want, tag in pairs:
        ok = want in flat
        cok += ok
        if not ok:
            fails.append("ctx %s (%s)" % (tag, want))
    lines.append("    GY-context distances: %d/8 match recompute" % cok)

    xs = [float(t[1]) for t in s["buffs"]]
    ys = [float(t[2]) for t in s["buffs"]]
    want = "x %s - %s" % (str(min(xs)), str(max(xs)))
    ok = want in flat
    if not ok:
        fails.append("band x (%s)" % want)
    lines.append("    buff band x: %s" % ("ok" if ok else "MISMATCH"))

    ok_c, c_lines, missing_c = coord_trace(text, corpora)
    lines.extend(c_lines)
    if not ok_c:
        fails.append("coord trace: %s" % missing_c[:6])
    probe_txt = text.replace("(489, 1061.6, 1377.09, 328.558)",
                             "(489, 1062.6, 1377.09, 328.558)")
    ok2, _, _ = coord_trace(probe_txt, corpora)
    probe_ok = (probe_txt != text) and not ok2
    lines.append("    coordinate probe reacts: %s"
                 % ("yes" if probe_ok else "no"))
    if not probe_ok:
        fails.append("coord probe")
    return fails, lines


def stage5(text, corpora):
    lines, fails = [], []
    maps = {}
    for line in corpora["wsl"].splitlines():
        m = re.match(r"\((\d+),(489|2106),", line.strip())
        if m:
            maps.setdefault(m.group(2), []).append(int(m.group(1)))
    ok = (sorted(maps.get("489", [])) == [769, 770, 771, 772, 3698, 3699,
                                          3784, 3785]
          and sorted(maps.get("2106", [])) == [7050, 7051, 7052, 7053])
    if not ok:
        fails.append("dump maps = %s" % maps)
    lines.append("    dump rows: 489=%d, 2106=%d, ids match: %s"
                 % (len(maps.get("489", [])), len(maps.get("2106", [])),
                    "yes" if ok else "NO"))

    script = corpora["h"] + corpora["c"]
    n_lit = len(re.findall(r"\b(?:489|2106)\b", script))
    ok = n_lit == 0
    if not ok:
        fails.append("script has %d 489/2106 literals" % n_lit)
    lines.append("    script 489/2106 literals: %d (need 0)" % n_lit)

    n_2106rows = len(re.findall(r"7050|7051|7052|7053", script))
    n_other = len(re.findall(r"3698|3699|3784|3785", script))
    ok = n_2106rows == 0 and n_other == 0
    if not ok:
        fails.append("script references dump rows: %d/%d"
                     % (n_2106rows, n_other))
    lines.append("    script refs 7050-7053: %d, 3698-3785: %d (need 0/0)"
                 % (n_2106rows, n_other))

    ok = ("769,3.14159,770,0.151581,75,1" in corpora["act"]
          and "Warsong Gulch (battleground)" in corpora["act"])
    if not ok:
        fails.append("AC row2 mismatch")
    lines.append("    AC row 2 StartLoc 769/770 + 75: %s"
                 % ("yes" if ok else "NO"))

    bh = corpora.get("bh") or ""
    m = re.search(r"BUFF_RESPAWN_TIME\s*=\s*(\d+)", bh)
    ok = m is not None and "13116" in bh and "13117" in bh and \
        "179871" in bh
    if not ok:
        fails.append("Battleground.h tokens (%s)"
                     % (m.group(1) if m else "no BUFF_RESPAWN_TIME"))
    lines.append("    Battleground.h: BUFF_RESPAWN_TIME=%s, spirits/"
                 "buff id present: %s"
                 % (m.group(1) if m else "?", "yes" if ok else "NO"))

    probes = [
        ("navmesh confirmed", "no navmesh confirmed"),
        ("verified by direct inspection", "no direct inspection"),
    ]
    for extra, key in probes:
        f, _ = run_static(text + "\n%s.\n" % extra)
        r = key in f
        lines.append("    injection probe (%s):%s"
                     % (extra[:24], " detected" if r else " NOT DETECTED"))
        if not r:
            fails.append("probe %s" % key)
    stripped = text.replace("unverified", "verified")
    f, _ = run_static(stripped)
    r = "unverified count" in f
    lines.append("    injection probe (unverified stripped):%s"
                 % (" detected" if r else " NOT DETECTED"))
    if not r:
        fails.append("unverified probe")
    import subprocess
    res = subprocess.run(
        ["gh", "api", "-X", "GET",
         "repos/TrinityCore/TrinityCore/contents/sql/DoesNotExist.sql"],
        capture_output=True, text=True)
    absent = res.returncode != 0
    lines.append("    control: bogus dump path 404:                %s"
                 % ("yes" if absent else "NO"))
    if not absent:
        fails.append("404 control")
    return fails, lines


def main():
    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()
    print("=" * 68)
    print("AUDIT: Coordinates_Warsong_Gulch_COMPLETED.txt (BG step 8)")
    print("=" * 68)

    fails1, lines1 = run_static(text)
    total1 = len(STATIC_CHECKS) + len(NEGATIVE_CHECKS) + 2
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
        corpora, {"h": [("flag entry", "= 227741")]},
        lambda t: t.replace("= 227741", "= 227743"))
    print("    reaction to tampered source (verified): %s"
          % ("yes" if probe_undetected == [] else "NO"))
    if probe_undetected != []:
        ok3 = False

    print("\n[4] Derived values recomputed from source bodies")
    fails4, lines4 = stage4(text, corpora)
    for ln in lines4:
        print(ln)
    probe_fails, _ = stage4(text, corpora, probe=True)
    reacts = any("mismatch" in str(f) for f in probe_fails)
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
