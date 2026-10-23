#!/usr/bin/env python3
"""Audit: Coordinates_Temple_of_Kotmogu_COMPLETED.txt (BG coords step 6)."""

import math
import re
import subprocess
import sys

sys.path.insert(0, ".")
from audit_common import gh_content, source_stage, mutation_probe, coord_trace

DOC = ("# Ai Research prompts/Battleground_Coordinates/"
       "Coordinates_Temple_of_Kotmogu_COMPLETED.txt")
LC = "Titans-Project/LegionCore-Reforged"
HAVEN = "HavenWoW/BFA-HavenCore"
BFA = "Titans-Project/BfaCore-Reforged"
TC = "TrinityCore/TrinityCore"
AC = "azerothcore/azerothcore-wotlk"
FILES = {
    "kth": "src/server/game/Battlegrounds/Zones/BattlegroundKotmoguTemplate.h",
    "ktc": "src/server/game/Battlegrounds/Zones/BattlegroundKotmoguTemplate.cpp",
}
TC_DUMP = "sql/old/8.x/world/19071_2020_06_17/2019_10_26_01_world.sql"
AC_TEMPLATE = "data/sql/base/db_world/battleground_template.sql"
DOC_IDS = [3552, 3553, 3554, 4057, 4058, 4059, 4060]
UNVERIFIED_MIN = 15


def norm(s):
    return re.sub(r"\s+", " ", s)


STATIC_CHECKS = [
    ("heading", "=== TEMPLE OF KOTMOGU COORDINATES - BFA 8.3.7 "
                "(TRINITYCORE) - COMPLETED ==="),
    ("numbering", "prompt 6 of 8 (Temple of Kotmogu, map 998)"),
    ("done", "DONE - step 6 of 8 complete"),
    ("no-estimate", "nothing is estimated"),
    ("unverified policy", 'the entry says "unverified"'),
    ("no compass", "makes NO compass claims"),
    ("band", "x 1716.78 - 1850.29, y 1249.93 - 1416.77"),
    ("pathing caveat", "NOT walkable-path measurements: no pathing/navmesh "
                       "source for map 998"),
    ("map line", "998 = Temple of Kotmogu"),
    ("vop tag", '"Valley of Power - BG" - the internal name'),
    ("scenario note", "row 4288"),
    ("scenario map", "map 1035"),
    ("queue unver", "which id/template your server queues is unverified"),
    ("cores no script", "Neither HavenWoW/BFA-HavenCore nor "
                        "Titans-Project/BfaCore-Reforged ships"),
    ("script name", "BattlegroundKotmoguTemplate.cpp/.h"),
    ("start a id", 'id 4059 "Valley of Power - BG - Start - Alliance'),
    ("start a row", "(998, 1784.27, 1077.63, 28.8781)  o 91.6923"),
    ("start h id", 'id 4060 "Valley of Power - BG - Start - Horde'),
    ("start h row", "(998, 1780.42, 1598.72, 33.7822)  o 270.726"),
    ("door entry", "gameobject entry 213172"),
    ("door a row", "(998, 1783.84, 1100.66, 20.60)  o 1.625020"),
    ("door h row", "(998, 1780.15, 1570.22, 24.59)  o 4.711630"),
    ("door dists", "Alliance start to its door = 23 yd, Horde start to its "
                   "door = 29 yd"),
    ("gates quote", "outside its gates on opposed sides"),
    ("no flags", "No flags, carts or capture nodes"),
    ("orb green", "gameobject 212091 (998, 1716.78, 1416.64, 13.5709)"),
    ("orb green s", "o 1.57239 - pickup spell 121176, holder aura 121220"),
    ("orb purple", "gameobject 212092 (998, 1850.26, 1416.77, 13.5709)"),
    ("orb purple s", "pickup spell 121175, holder aura 121219"),
    ("orb orange", "gameobject 212093 (998, 1850.29, 1250.31, 13.5708)"),
    ("orb orange s", "pickup spell 121177, holder aura 121221"),
    ("orb blue", "gameobject 212094 (998, 1716.83, 1249.93, 13.5706)"),
    ("orb blue s", "pickup spell 121164, holder aura 121217"),
    ("world trigger", "WORLD_TRIGGER aura creature"),
    ("brawl orb a", "(998, 1716.747, 1333.411, 13.18124)"),
    ("brawl orb b", "(998, 1849.882, 1333.389, 13.32879)"),
    ("brawl unver", "brawl mode on your server: unverified"),
    ("tick table", "BG_KT_TickPoints = {3, 4, 5}"),
    ("zones", "KT_ZONE_OUT, KT_ZONE_IN, KT_ZONE_MIDDLE"),
    ("zone quote", "the farther you are from the heart of the temple, the "
                   "fewer points"),
    ("tick cadence unver", "tick cadence: unverified"),
    ("cap", "BG_KT_MAX_TEAM_SCORE = 1500"),
    ("kill bonus", "killing blows"),
    ("kill unver", "that mechanism was not traced in the script "
                   "(unverified)"),
    ("holder effects", "deals and receives increased damage, reduced "
                       "healing"),
    ("hotmogu", "HOTMOGU 237738"),
    ("insignia", "131527 (Alliance) / 131528 (Horde)"),
    ("a orange", "legs: 23 yd, 164 yd   direct 185 yd"),
    ("a green", "legs: 23 yd, 323 yd   direct 346 yd"),
    ("h green", "legs: 29 yd, 166 yd   direct 193 yd"),
    ("h purple", "legs: 29 yd, 169 yd   direct 195 yd"),
    ("h orange", "legs: 29 yd, 328 yd   direct 355 yd"),
    ("h blue", "legs: 29 yd, 326 yd   direct 355 yd"),
    ("pair gp", "Green-Purple 133 yd"),
    ("pair go", "Green-Orange 213 yd"),
    ("pair ob", "Orange-Blue 133 yd"),
    ("pair pb", "Purple-Blue 214 yd"),
    ("center quote", "central scoring area, an outer plaza"),
    ("gy rows", "Five dump rows exist (map 998"),
    ("gy 3552", "(998, 1889.37, 1156.54, 15.0766)  o 140.912"),
    ("gy 3553", "(998, 1675.8, 1522.34, 16.7631)  o 310.714"),
    ("gy 3554", "(998, 838.373, 1266.11, 5.21376)  o 317.523"),
    ("gy 4057", "(998, 1680.98, 1147.54, 18.3058)  o 43.1923"),
    ("gy 4058", "(998, 1892.88, 1521.14, 15.7067)  o 224.058"),
    ("gy rule in", "IN_PROGRESS: Alliance always 3552, Horde always 3553"),
    ("gy rule wait", "Alliance 4058, Horde 4057"),
    ("gy no choice", "no nearest-choice"),
    ("no point gy", "which graveyard belongs to which point: none"),
    ("3554 unused", "NOT referenced by the readable script"),
    ("spirit a", "(998, 1892.61, 1151.69, 14.7160)"),
    ("spirit h", "(998, 1672.40, 1524.10, 16.7387)"),
    ("spirit enum", "BG_KT_SpiritPositions"),
    ("spirit entries", "13116 (Alliance) / 13117 (Horde)"),
    ("spirit differ", "differ from the respawn rows above"),
    ("buff entry", "BG_OBJECTID_BERSERKERBUFF_ENTRY = 179905"),
    ("buff 1", "(998, 1856.635, 1333.741, 10.555)  o 3.150048"),
    ("buff 2", "(998, 1710.284, 1333.345, 10.554)  o 0.116051"),
    ("buff param", "BUFF_RESPAWN_TIME (180 s) as their spawn's respawn "
                   "parameter"),
    ("buff parity", "retail parity of these two spawns is unverified"),
    ("no other buffs", "No other buff or power-up spawns are defined"),
    ("src dump", "world_safe_locs rows 3552, 3553, 3554,"),
    ("src exactly7", "the only map-998 rows (checked: exactly 7)"),
    ("src wiki", "warcraft.wiki.gg: Temple of Kotmogu"),
    ("neg rows", "row 3554 unreferenced by the script"),
    ("neg buff wiki", "wiki has no buff section"),
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
            lines.append("    %-22s %s (%d >= %d)"
                         % (name, "ok" if hit else "FAIL", n,
                            UNVERIFIED_MIN))
            if not hit:
                fails.append(name)
            continue
        hit = norm(lit) in flat
        lines.append("    %-22s %s" % (name, "ok" if hit else "MISSING"))
        if not hit:
            fails.append(name)
    for name, lit in NEGATIVE_CHECKS:
        hit = norm(lit) not in flat
        lines.append("    %-22s %s" % (name, "ok" if hit else "PRESENT!"))
        if not hit:
            fails.append(name)
    return fails, lines


MUTATIONS = [
    ("heading", "- COMPLETED ===\nBattleground", "- DRAFT ===\nBattleground"),
    ("numbering", "prompt 6 of 8", "prompt 6 of 7"),
    ("done", "DONE - step 6 of 8 complete", "DONE - step 6 of 9 complete"),
    ("compass", "makes NO compass claims", "makes YES compass claims"),
    ("band", "x 1716.78 - 1850.29", "x 1716.79 - 1850.29"),
    ("map id", "998 = Temple of Kotmogu", "997 = Temple of Kotmogu"),
    ("scenario", "map 1035", "map 1036"),
    ("start a", "(998, 1784.27, 1077.63, 28.8781)",
     "(998, 1784.27, 1077.63, 28.8782)"),
    ("start h", "(998, 1780.42, 1598.72, 33.7822)",
     "(998, 1780.42, 1598.72, 33.7823)"),
    ("start h o", "o 270.726", "o 270.727"),
    ("door entry", "gameobject entry 213172", "gameobject entry 213173"),
    ("door a", "(998, 1783.84, 1100.66, 20.60)",
     "(998, 1783.84, 1100.66, 20.61)"),
    ("door h", "(998, 1780.15, 1570.22, 24.59)",
     "(998, 1780.15, 1570.22, 24.60)"),
    ("door dist", "= 23 yd", "= 24 yd"),
    ("orb green", "gameobject 212091", "gameobject 212095"),
    ("orb green pos", "(998, 1716.78, 1416.64, 13.5709)",
     "(998, 1716.78, 1416.64, 13.5710)"),
    ("orb green spell", "pickup spell 121176", "pickup spell 121170"),
    ("orb purple pos", "(998, 1850.26, 1416.77, 13.5709)",
     "(998, 1850.26, 1416.77, 13.5710)"),
    ("orb orange spell", "holder aura 121221", "holder aura 121222"),
    ("orb blue pos", "(998, 1716.83, 1249.93, 13.5706)",
     "(998, 1716.83, 1249.93, 13.5707)"),
    ("orb blue spell", "pickup spell 121164", "pickup spell 121165"),
    ("brawl a", "(998, 1716.747, 1333.411, 13.18124)",
     "(998, 1716.747, 1333.411, 13.18125)"),
    ("ticks", "BG_KT_TickPoints = {3, 4, 5}", "BG_KT_TickPoints = {3, 4, 6}"),
    ("cap", "BG_KT_MAX_TEAM_SCORE = 1500", "BG_KT_MAX_TEAM_SCORE = 1501"),
    ("hotmogu", "HOTMOGU 237738", "HOTMOGU 237739"),
    ("insignia", "131527 (Alliance) / 131528", "131527 (Alliance) / 131529"),
    ("a orange", "legs: 23 yd, 164 yd", "legs: 23 yd, 165 yd"),
    ("a orange direct", "direct 185 yd", "direct 186 yd"),
    ("h green", "legs: 29 yd, 166 yd", "legs: 29 yd, 167 yd"),
    ("h orange direct", "direct 355 yd", "direct 356 yd"),
    ("pair gp", "Green-Purple 133 yd", "Green-Purple 134 yd"),
    ("pair ob", "Orange-Blue 133 yd", "Orange-Blue 134 yd"),
    ("pair go", "Green-Orange", "Green-Orangex"),
    ("gy 3552", "(998, 1889.37, 1156.54, 15.0766)",
     "(998, 1889.37, 1156.54, 15.0767)"),
    ("gy 3554", "(998, 838.373, 1266.11, 5.21376)",
     "(998, 838.373, 1266.11, 5.21377)"),
    ("gy 4058 o", "o 224.058", "o 224.059"),
    ("gy rule", "always 3552, Horde always 3553",
     "always 3553, Horde always 3552"),
    ("gy rule wait", "Alliance 4058, Horde 4057", "Alliance 4057, Horde 4058"),
    ("spirit a", "(998, 1892.61, 1151.69, 14.7160)",
     "(998, 1892.61, 1151.69, 14.7161)"),
    ("spirit h", "(998, 1672.40, 1524.10, 16.7387)",
     "(998, 1672.40, 1524.10, 16.7388)"),
    ("spirit entries", "13116 (Alliance) / 13117 (Horde)",
     "13116 (Alliance) / 13118 (Horde)"),
    ("buff entry", "BERSERKERBUFF_ENTRY = 179905", "BERSERKERBUFF_ENTRY = "
     "179906"),
    ("buff 1", "(998, 1856.635, 1333.741, 10.555)",
     "(998, 1856.635, 1333.741, 10.556)"),
    ("buff 2", "(998, 1710.284, 1333.345, 10.554)",
     "(998, 1710.284, 1333.345, 10.555)"),
    ("buff respawn", "BUFF_RESPAWN_TIME (180 s)", "BUFF_RESPAWN_TIME (181 s)"),
    ("no buff wiki", "retail parity of these two spawns is unverified",
     "retail parity of these two spawns is fully proven"),
    ("exactly7", "checked: exactly 7", "checked: exactly 8"),
    ("3554 claim", "NOT referenced by the readable script",
     "frequently referenced by the readable script"),
    ("gates", "outside its gates on opposed sides",
     "inside its gates on opposed sides"),
]


def stage3(corpora):
    token_map = {
        "kth": [
            ("cap", "#define BG_KT_MAX_TEAM_SCORE        1500"),
            ("ticks", "uint32 const BG_KT_TickPoints[3] = { 3, 4, 5 };"),
            ("door entry", "BG_KT_OBJECT_DOOR_ENTRY     = 213172"),
            ("orb 1", "= 212091"), ("orb 2", "= 212092"),
            ("orb 3", "= 212093"), ("orb 4", "= 212094"),
            ("pick green", "= 121176"), ("pick purple", "= 121175"),
            ("pick orange", "= 121177"), ("pick blue", "= 121164"),
            ("aura green", "= 121220"), ("aura purple", "= 121219"),
            ("aura orange", "= 121221"), ("aura blue", "= 121217"),
            ("insignia a", "= 131527"), ("insignia h", "= 131528"),
            ("hotmogu", "= 237738"),
            ("gy a1", "KT_GRAVEYARD_RECTANGLEA1    = 3552"),
            ("gy a2", "KT_GRAVEYARD_RECTANGLEA2    = 4058"),
            ("gy h1", "KT_GRAVEYARD_RECTANGLEH1    = 3553"),
            ("gy h2", "KT_GRAVEYARD_RECTANGLEH2    = 4057"),
            ("door pos a", "{1783.84f, 1100.66f, 20.60f, 1.625020f}"),
            ("door pos h", "{1780.15f, 1570.22f, 24.59f, 4.711630f}"),
            ("orb pos green", "{1716.78f, 1416.64f, 13.5709f, 1.57239f}"),
            ("orb pos purple", "{1850.26f, 1416.77f, 13.5709f, 1.56061f}"),
            ("orb pos orange", "{1850.29f, 1250.31f, 13.5708f, 4.70848f}"),
            ("orb pos blue", "{1716.83f, 1249.93f, 13.5706f, 4.71397f}"),
            ("spirit pos a", "{1892.61f, 1151.69f, 14.7160f, 2.523528f}"),
            ("spirit pos h", "{1672.40f, 1524.10f, 16.7387f, 6.032206f}"),
        ],
        "ktc": [
            ("setup door", "AddObject(BG_KT_OBJECT_A_DOOR, "
                           "BG_KT_OBJECT_DOOR_ENTRY"),
            ("buff 1 src", "BG_OBJECTID_BERSERKERBUFF_ENTRY, 1856.635f, "
                           "1333.741f, 10.555f"),
            ("buff 2 src", "BG_OBJECTID_BERSERKERBUFF_ENTRY, 1710.284f, "
                           "1333.345f, 10.554f"),
            ("buff respawn param", "10.555f, 3.150048f, 0, 0, 0.5591929f, "
                                   "0.8290376f, BUFF_RESPAWN_TIME)"),
            ("spirit a spawn", "AddSpiritGuide(BG_KT_CREATURE_SPIRIT_1"),
            ("spirit h spawn", "AddSpiritGuide(BG_KT_CREATURE_SPIRIT_2"),
            ("orb spawn", "AddObject(BG_KT_OBJECT_ORB_GREEN + i, "
                          "BG_KT_OBJECT_ORB_1_ENTRY + i"),
            ("brawl orb a", "1716.747f, 1333.411f, 13.18124f"),
            ("brawl orb b", "1849.882f, 1333.389f, 13.32879f"),
            ("gy fn", "BattlegroundKotmoguTemplate::GetClosestGraveYard"),
            ("gy ternary", "GetStatus() == STATUS_IN_PROGRESS ? "
                           "KT_GRAVEYARD_RECTANGLEA1 : KT_GRAVEYARD_RECTANGLEA2"),
            ("gy ternary h", "? KT_GRAVEYARD_RECTANGLEH1 : "
                             "KT_GRAVEYARD_RECTANGLEH2"),
            ("zone tick", "m_TeamScores[teamID] += BG_KT_TickPoints[playerZone]"),
            ("clamp", "m_TeamScores[teamID] = BG_KT_MAX_TEAM_SCORE"),
            ("zone out", "KT_ZONE_OUT"),
            ("zone mid", "return KT_ZONE_MIDDLE"),
        ],
        "wsl": [
            ("row 3552", "(3552,998,1889.37,1156.54,15.0766,140.912,"
                         "'Valley of Power - BG - Graveyard - Alliance "
                         "(Rectangle)'),"),
            ("row 3553", "(3553,998,1675.8,1522.34,16.7631,310.714,"
                         "'Valley of Power - BG - Graveyard - Horde "
                         "(Rectangle)'),"),
            ("row 3554", "(3554,998,838.373,1266.11,5.21376,317.523,"
                         "'Valley of Power - BG - Graveyard - Alliance "
                         "(Circle)'),"),
            ("row 4057", "(4057,998,1680.98,1147.54,18.3058,43.1923,"
                         "'Valley of Power - BG - Graveyard - Horde "
                         "(Rectangle) 2'),"),
            ("row 4058", "(4058,998,1892.88,1521.14,15.7067,224.058,"
                         "'Valley of Power - BG - Graveyard - Alliance "
                         "(Rectangle) 2'),"),
            ("row 4059", "(4059,998,1784.27,1077.63,28.8781,91.6923,"
                         "'Valley of Power - BG - Start - Alliance "
                         "(Rectangle) Start'),"),
            ("row 4060", "(4060,998,1780.42,1598.72,33.7822,270.726,"
                         "'Valley of Power - BG - Start - Horde "
                         "(Rectangle) Start'),"),
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


def parse_arrays(kth, ktc):
    out = {}

    def rows_of(block):
        return [tuple(v.strip().rstrip("f") for v in
                      re.findall(r"[-\d.]+f", r))
                for r in re.findall(r"\{(.*?)\}", block, re.S)]

    m = re.search(r"BG_KT_DoorPositions\[MAX_TEAMS\]\[4\] =\s*\{(.*?)\n\};",
                  kth, re.S)
    out["door"] = rows_of(m.group(1))
    m = re.search(r"BG_KT_OrbPositions\[MAX_ORBS\]\[4\] =\s*\{(.*?)\n\};",
                  kth, re.S)
    out["orb"] = rows_of(m.group(1))
    m = re.search(r"BG_KT_SpiritPositions\[MAX_ORBS\] =\s*\{(.*?)\n\};",
                  kth, re.S)
    out["spirit"] = rows_of(m.group(1))
    m = re.search(r"BG_KT_TickPoints\[3\] = \{([^}]*)\}", kth)
    out["ticks"] = [v.strip() for v in m.group(1).split(",")]
    m = re.search(r"#define BG_KT_MAX_TEAM_SCORE\s+(\d+)", kth)
    out["cap"] = m.group(1)
    m = re.search(r"BERSERKBUFF_1, BG_OBJECTID_BERSERKERBUFF_ENTRY, "
                  r"([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f", ktc)
    out["buff1"] = tuple(m.group(i) for i in (1, 2, 3, 4))
    m = re.search(r"BERSERKBUFF_2, BG_OBJECTID_BERSERKERBUFF_ENTRY, "
                  r"([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f", ktc)
    out["buff2"] = tuple(m.group(i) for i in (1, 2, 3, 4))
    m = re.search(r"1716\.747f, 1333\.411f, ([-\d.]+)f", ktc)
    out["brawl_a_z"] = m.group(1)
    return out


def stage4(text, corpora, probe=False):
    if probe:
        text = text.replace("(998, 1889.37, 1156.54, 15.0766)",
                            "(998, 1889.37, 1156.54, 15.0767)", 1)
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

    arr = parse_arrays(corpora["kth"], corpora["ktc"])
    want_list = ["(998, %s, %s, %s)" % t[:3] for t in arr["door"]]
    want_list += ["(998, %s, %s, %s)" % t[:3] for t in arr["orb"]]
    want_list += ["(998, %s, %s, %s)" % t[:3] for t in arr["spirit"]]
    want_list += ["(998, %s, %s, %s)" % t[:3] for t in (arr["buff1"],
                                                        arr["buff2"])]
    missing = [w for w in want_list if w not in flat]
    lines.append("    script coordinate triples matched: %d/%d"
                 % (len(want_list) - len(missing), len(want_list)))
    if missing:
        fails.append("script triples missing: %s" % missing)

    checks = [
        ("cap", "BG_KT_MAX_TEAM_SCORE = %s" % arr["cap"]),
        ("ticks", "BG_KT_TickPoints = {%s}" % ", ".join(arr["ticks"])),
    ]
    sok = 0
    for name, want in checks:
        ok = want in flat
        sok += ok
        if not ok:
            fails.append("%s (%s)" % (name, want))
    lines.append("    script-derived scalars: %d/%d match doc"
                 % (sok, len(checks)))

    A = (float(rows[4059]["x"]), float(rows[4059]["y"]))
    H = (float(rows[4060]["x"]), float(rows[4060]["y"]))
    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
    dA = (float(arr["door"][0][0]), float(arr["door"][0][1]))
    dH = (float(arr["door"][1][0]), float(arr["door"][1][1]))
    names = ["Green", "Purple", "Orange", "Blue"]
    dok = 0
    for i, nm in enumerate(names):
        p = (float(arr["orb"][i][0]), float(arr["orb"][i][1]))
        for start, door, tag in ((A, dA, "a"), (H, dH, "h")):
            l1, l2, dirc = rd(dist(start, door)), rd(dist(door, p)), \
                rd(dist(start, p))
            ok = ("legs: %d yd, %d yd" % (l1, l2)) in flat and \
                 ("direct %d yd" % dirc) in flat
            dok += ok
            if not ok:
                fails.append("route %s->%s" % (tag, nm))
    lines.append("    orb routes: %d/8 match recompute" % dok)

    dok2 = 0
    for i in range(4):
        for j in range(i + 1, 4):
            p = (float(arr["orb"][i][0]), float(arr["orb"][i][1]))
            q = (float(arr["orb"][j][0]), float(arr["orb"][j][1]))
            want = "%s-%s %d yd" % (names[i], names[j], rd(dist(p, q)))
            ok = want in flat
            dok2 += ok
            if not ok:
                fails.append("pair %s" % want)
    lines.append("    orb pairs: %d/6 match recompute" % dok2)

    da = rd(dist(A, dA))
    dh = rd(dist(H, dH))
    ok = ("Alliance start to its door = %d yd" % da) in flat and \
         ("Horde start to its door = %d yd" % dh) in flat
    if not ok:
        fails.append("door distances")
    lines.append("    door distances: A %d yd, H %d yd" % (da, dh))

    xs = [float(o[0]) for o in arr["orb"]]
    ys = [float(o[1]) for o in arr["orb"]]
    want = "x %s - %s, y %s - %s" % (str(min(xs)), str(max(xs)),
                                     str(min(ys)), str(max(ys)))
    ok = want in flat
    if not ok:
        fails.append("band (%s)" % want)
    lines.append("    orb band: %s" % ("ok" if ok else "MISMATCH " + want))

    ok_c, c_lines, missing_c = coord_trace(text, corpora)
    lines.extend(c_lines)
    if not ok_c:
        fails.append("coordinate trace: %s" % missing_c[:6])
    probe_txt = text.replace("(998, 1784.27, 1077.63, 28.8781)",
                             "(998, 1785.27, 1077.63, 28.8781)", 1)
    ok2, _, _ = coord_trace(probe_txt, corpora)
    probe_ok = (probe_txt != text) and not ok2
    lines.append("    coordinate probe reacts: %s"
                 % ("yes" if probe_ok else "no"))
    if not probe_ok:
        fails.append("coordinate probe")
    return fails, lines


def stage5(text, corpora):
    lines, fails = [], []
    m998 = []
    for line in corpora["wsl"].splitlines():
        m = re.match(r"\((\d+),(\d+),", line.strip())
        if m and m.group(2) == "998":
            m998.append(int(m.group(1)))
    ok = sorted(m998) == sorted(DOC_IDS)
    if not ok:
        fails.append("map-998 rows = %s" % sorted(m998))
    lines.append("    dump map-998 rows: %d, ids match: %s"
                 % (len(m998), "yes" if ok else "NO"))
    n_ac = len(re.findall(r"(?i)kotmogu|,998,", corpora["act"]))
    ok = n_ac == 0
    if not ok:
        fails.append("AC has %d matches" % n_ac)
    lines.append("    AzerothCore Kotmogu/998 rows: %d (need 0)" % n_ac)

    n_3554 = len(re.findall(r"3554", corpora["ktc"] + corpora["kth"]))
    ok = n_3554 == 0
    if not ok:
        fails.append("3554 referenced %d times" % n_3554)
    lines.append("    row 3554 in script: %d (need 0)" % n_3554)

    for repo in (HAVEN, BFA):
        res = subprocess.run(
            ["gh", "api", "repos/%s/contents/src/server/game/"
             "Battlegrounds/Zones" % repo, "--jq", ".[].name"],
            capture_output=True, text=True)
        names = [n for n in res.stdout.split() if n]
        bad = [n for n in names if re.search(r"(?i)kotmogu", n)]
        sanity = "BattlegroundAB.cpp" in names
        okc = res.returncode == 0 and sanity and not bad
        lines.append("    %-32s %d files, no Kotmogu script: %s"
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
    print("AUDIT: Coordinates_Temple_of_Kotmogu_COMPLETED.txt (BG step 6)")
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
        {"kth": [("green orb float", "1716.78f")]},
        lambda t: t.replace("1716.78f", "1716.79f"))
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
