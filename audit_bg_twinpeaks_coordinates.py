#!/usr/bin/env python3
"""Audit: Coordinates_Twin_Peaks_COMPLETED.txt (BG coords step 7)."""

import math
import re
import subprocess
import sys

sys.path.insert(0, ".")
from audit_common import gh_content, source_stage, mutation_probe, coord_trace

DOC = ("# Ai Research prompts/Battleground_Coordinates/"
       "Coordinates_Twin_Peaks_COMPLETED.txt")
LC = "Titans-Project/LegionCore-Reforged"
HAVEN = "HavenWoW/BFA-HavenCore"
BFA = "Titans-Project/BfaCore-Reforged"
TC = "TrinityCore/TrinityCore"
AC = "azerothcore/azerothcore-wotlk"
FILES = {
    "tph": "src/server/game/Battlegrounds/Zones/BattlegroundTwinPeaks.h",
    "tpc": "src/server/game/Battlegrounds/Zones/BattlegroundTwinPeaks.cpp",
}
TC_DUMP = "sql/old/8.x/world/19071_2020_06_17/2019_10_26_01_world.sql"
AC_TEMPLATE = "data/sql/base/db_world/battleground_template.sql"
HAVEN_TP = "src/server/game/Battlegrounds/Zones/BattlegroundTP.cpp"
DOC_IDS = [1726, 1727, 1728, 1729, 1749, 1750,
           3944, 3945, 3946, 3947, 3948, 3949, 4283, 4284, 4341, 4342]
UNVERIFIED_MIN = 14


def norm(s):
    return re.sub(r"\s+", " ", s)


STATIC_CHECKS = [
    ("heading", "=== TWIN PEAKS COORDINATES - BFA 8.3.7 (TRINITYCORE) - "
                "COMPLETED ==="),
    ("numbering", "prompt 7 of 8 (Twin Peaks, map 726)"),
    ("done", "DONE - step 7 of 8 complete"),
    ("no-estimate", "nothing is estimated"),
    ("unverified policy", 'the entry says "unverified"'),
    ("no compass", "makes NO compass claims"),
    ("flag offset", "x 2117.637 (Alliance side) and x 1578.337 (Horde side)"),
    ("pathing caveat", "NOT walkable-path measurements: no pathing/navmesh "
                       "source for map 726"),
    ("map line", "726 = Twin Peaks"),
    ("sixteen rows", "all sixteen map-726 dump rows below"),
    ("exactly16", "checked: exactly 16 map-726 rows"),
    ("wiki ctf", "first to three captures"),
    ("wiki wsg", "identical to those for Warsong Gulch"),
    ("queue unver", "which id/template your server queues is unverified"),
    ("cores ship tp", "and Titans-Project/BfaCore-Reforged DO ship"),
    ("haven twin static", "verified to be a Twin Peaks script with its "
                          "own object entries"),
    ("cores ship tp2", "BattlegroundTP.cpp (both Zones directory listings "
                       "checked"),
    ("haven flagver", "it does NOT use the 227741/227740 flag "
                      "entries of the LegionCore file"),
    ("ttp arena", "BattlegroundTTP files are arenas"),
    ("script name", "BattlegroundTwinPeaks .cpp/.h is the script source"),
    ("waiting spawns", "the entrance rows, which the script names FLAGROOM "
                       "indices"),
    ("start a id", 'id 1726 "Twin Peaks - Alliance Entrance"'),
    ("start a row", "(726, 2142.6, 175.918, 43.6513)  o 150"),
    ("start h id", 'id 1727 "Twin Peaks - Horde Entrance"'),
    ("start h row", "(726, 1549.54, 346.955, 1.28533)  o 0"),
    ("template unver", "StartLoc ids your server uses: unverified"),
    ("six doors", "Start gates - six doors"),
    ("door a1", "Alliance door 1 gameobject 206653 (726, 2135.525, "
                "218.926, 43.60946)"),
    ("door a2", "(726, 2156.0, 219.2059, 43.6256)  o 2.609261"),
    ("door a3", "(726, 2118.088, 154.6754, 43.57089)  o 2.609261"),
    ("door h1", "Horde door 1 gameobject 208205 (726, 1556.656, "
                "314.7127, 1.589001)"),
    ("door h2", "(726, 1574.605, 321.2421, 1.58989)  o 6.178466"),
    ("door h3", "(726, 1558.088, 372.7654, 1.723727)  o 6.178466"),
    ("door entries h", "208206"),
    ("subregions", "Wildhammer Stronghold (Alliance) and Dragonmaw Forge "
                   "(Horde)"),
    ("no orbs", "No orbs, carts or capture nodes exist in Twin Peaks"),
    ("score 3", "GetMaxScore() returns 3"),
    ("wiki 3 caps", "the first faction to capture three flags is "
                    "victorious"),
    ("flag a", "Alliance flag gameobject 227741 (726, 2117.637, 191.6823, "
               "44.05199)"),
    ("flag a o", "o 6.021387"),
    ("flag h", "Horde flag gameobject 227740 (726, 1578.337, 344.0451, "
               "2.418409)"),
    ("flag h o", "o 2.792518"),
    ("respawn param", "respawn parameter BG_TP_FLAG_RESPAWN_TIME / 1000"),
    ("ground flags", "Alliance ground flag gameobject 227745, Horde ground "
                     "flag gameobject 227744"),
    ("ground unver", "positions unverified"),
    ("timer 23000", "BG_TP_FLAG_RESPAWN_TIME = 23000 ms"),
    ("timer 10000", "BG_TP_FLAG_DROP_TIME = 10000 ms"),
    ("route a steal", "legs: 32 yd, 572 yd   direct 589 yd"),
    ("route a defend", "legs: 32 yd, 37 yd    direct 30 yd"),
    ("route h steal", "legs: 27 yd, 588 yd  direct 589 yd"),
    ("route h defend", "legs: 27 yd, 35 yd   direct 29 yd"),
    ("nearest a", "door 3 (32 yd, nearest of its three)"),
    ("nearest h", "door 3 (27 yd, nearest of its three)"),
    ("cross", "Flag-to-flag cross distance (recomputed): 560 yd"),
    ("ctx ab", "graveyard 149 yd"),
    ("ctx ac", "graveyard 345 yd"),
    ("ctx hb", "graveyard 132 yd"),
    ("ctx hc", "graveyard 301 yd"),
    ("ctx asc", "to Alliance center graveyard 374 yd"),
    ("ctx hsc", "to Horde center graveyard 326 yd"),
    ("sep base", "base graveyard pair separation 619 yd"),
    ("sep center", "graveyard pair separation 285 yd"),
    ("route caveat", "NOT walkable-path measurements; walkability "
                     "unverified"),
    ("choke unver", "named chokepoint list per route: unverified"),
    ("gy 1726", '(726, 2142.6, 175.918, 43.6513)  o 150   "Alliance Entrance"'),
    ("gy 1728", '(726, 1561.16, 212.76, 13.8615)  o 0      "Horde Graveyard (Base)"'),
    ("gy 1729", '(726, 2168.1, 332.038, 34.6959)  o 180    "Alliance Graveyard (Base)"'),
    ("gy 1749", '(726, 1877.15, 439.111, -4.00017)  o 240  "Alliance Graveyard (Center)"'),
    ("gy 1750", '(726, 1816.87, 160.083, 1.80644)  o 60    "Horde Graveyard (Center)"'),
    ("gy array", "BG_TP_GraveyardIds = {1726, 1727, 1729, 1728, 1749, 1750}"),
    ("rule waiting", "your team's ENTRANCE row (Alliance 1726, Horde 1727)"),
    ("rule cmp", "compare the corpse's distance to the ENEMY entrance row vs "
                 "the enemy CENTER row"),
    ("rule base", "respawn at your team's BASE graveyard (Alliance 1729, "
                  "Horde 1728"),
    ("rule center", "otherwise respawn at your team's CENTER graveyard "
                    "(Alliance 1749, Horde 1750)"),
    ("no points", "Which graveyard belongs to which point: no points exist"),
    ("spirit rows", "the setup loop covers the START and MIDDLE indices "
                    "only"),
    ("spirit entries", "13116 (Alliance) / 13117 (Horde)"),
    ("sploit ids a", "ids 3944, 3945, 3946 all"),
    ("sploit triple a", "(726, 2138.85, 178.863, 43.7)  o 148"),
    ("sploit ids h", "ids 3947, 3948, 3949 all"),
    ("sploit triple h", "(726, 1555.94, 346.375, 1.76868)  o 356"),
    ("anti 4283", 'id 4283'),
    ("anti 4283 row", "(726, 1819.45, 189.984, -18.8967)  o 60"),
    ("anti 4284", 'id 4284'),
    ("anti 4341", 'id 4341'),
    ("anti 4341 row", "(726, 2156.57, 319.844, 23.1756)  o 206.749"),
    ("anti 4342", 'id 4342'),
    ("unused claim", "none referenced by the readable script"),
    ("six buffs", "Six buffs (script SetupBattleground"),
    ("buff speed a", "Speed gameobject 179871 (726, 1544.55, 303.852, "
                     "0.692371)  o 6.265733"),
    ("sniff 1", "id 179899 in sniff"),
    ("buff speed b", "(726, 2175.866, 226.6215, 43.76288)  o 2.600535"),
    ("buff regen a", "Regeneration gameobject 179904 (726, 1754.163, "
                     "242.125, -14.13157)"),
    ("sniff 2", "id 179906 in sniff"),
    ("buff regen b", "(726, 1951.18, 383.795, -10.5257)  o 4.06662"),
    ("buff zerker a", "Berserking gameobject 179905 (726, 1932.832, "
                      "226.7917, -17.05979)"),
    ("sniff 3", "id 179907 in sniff"),
    ("buff zerker b", "(726, 1737.566, 435.8455, -8.086342)  o 5.515242"),
    ("buff band", "x 1544.55 - 2175.866, y 226.6215 - 435.8455"),
    ("buff respawn", "BUFF_RESPAWN_TIME = 180 s"),
    ("no buff wiki", "retail parity of these six spawns is unverified"),
    ("sniff caveat", "per-map object ids on retail - 179899/179906/179907"),
    ("src dump", "the sixteen map-726 rows listed above"),
    ("src wiki", "warcraft.wiki.gg: Twin Peaks"),
    ("neg tp diff", "the cores' BattlegroundTP.cpp differs from the "
                    "LegionCore file cited above"),
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
    ("numbering", "prompt 7 of 8", "prompt 7 of 9"),
    ("done", "DONE - step 7 of 8 complete", "DONE - step 7 of 10 complete"),
    ("compass", "makes NO compass claims", "makes YES compass claims"),
    ("map id", "726 = Twin Peaks", "727 = Twin Peaks"),
    ("exactly16", "exactly 16 map-726 rows", "exactly 17 map-726 rows"),
    ("start a", "(726, 2142.6, 175.918, 43.6513)",
     "(726, 2142.6, 175.918, 43.6514)"),
    ("start h o", "1.28533)  o 0", "1.28533)  o 1"),
    ("door a1 pos", "(726, 2135.525, 218.926, 43.60946)",
     "(726, 2135.525, 218.926, 43.60947)"),
    ("door a1 entry", "gameobject 206653", "gameobject 206656"),
    ("door h3 pos", "(726, 1558.088, 372.7654, 1.723727)",
     "(726, 1558.088, 372.7654, 1.723728)"),
    ("score3", "GetMaxScore() returns 3", "GetMaxScore() returns 4"),
    ("flag a", "gameobject 227741", "gameobject 227742"),
    ("flag a pos", "(726, 2117.637, 191.6823, 44.05199)",
     "(726, 2117.637, 191.6823, 44.05200)"),
    ("flag h pos", "(726, 1578.337, 344.0451, 2.418409)",
     "(726, 1578.337, 344.0451, 2.418410)"),
    ("ground flag", "gameobject 227745", "gameobject 227746"),
    ("timer 23000", "= 23000 ms", "= 23001 ms"),
    ("timer 10000", "= 10000 ms", "= 10001 ms"),
    ("route a steal", "legs: 32 yd, 572 yd", "legs: 32 yd, 573 yd"),
    ("route a direct", "direct 589 yd", "direct 590 yd"),
    ("route h defend", "legs: 27 yd, 35 yd", "legs: 27 yd, 36 yd"),
    ("nearest a", "(32 yd, nearest of its three)", "(33 yd, nearest of its "
     "three)"),
    ("cross", "recomputed): 560 yd", "recomputed): 561 yd"),
    ("ctx ab", "graveyard 149 yd", "graveyard 150 yd"),
    ("ctx hc", "graveyard 301 yd", "graveyard 302 yd"),
    ("sep base", "separation 619 yd", "separation 620 yd"),
    ("sep center", "separation 285 yd", "separation 286 yd"),
    ("gy row 1728", "(726, 1561.16, 212.76, 13.8615)",
     "(726, 1561.16, 212.76, 13.8616)"),
    ("gy row 1749", "(726, 1877.15, 439.111, -4.00017)",
     "(726, 1877.15, 439.111, -4.00018)"),
    ("gy array", "{1726, 1727, 1729, 1728, 1749, 1750}",
     "{1726, 1727, 1729, 1728, 1749, 1751}"),
    ("rule waiting", "(Alliance 1726, Horde", "(Alliance 1727, Horde"),
    ("rule base", "(Alliance 1729, Horde", "(Alliance 1728, Horde"),
    ("rule center", "Alliance 1749, Horde 1750", "Alliance 1750, Horde 1749"),
    ("spirit entries", "13117 (Horde)", "13118 (Horde)"),
    ("sploit a", "ids 3944, 3945, 3946 all", "ids 3944, 3945, 3947 all"),
    ("sploit triple a", "(726, 2138.85, 178.863, 43.7)",
     "(726, 2138.85, 178.863, 43.8)"),
    ("sploit triple h", "(726, 1555.94, 346.375, 1.76868)",
     "(726, 1555.94, 346.375, 1.76869)"),
    ("anti 4283 row", "(726, 1819.45, 189.984, -18.8967)",
     "(726, 1819.45, 189.984, -18.8968)"),
    ("anti 4341 row", "(726, 2156.57, 319.844, 23.1756)",
     "(726, 2156.57, 319.844, 23.1757)"),
    ("unused claim", "none referenced by the readable script",
     "all referenced by the readable script"),
    ("buff speed a", "(726, 1544.55, 303.852, 0.692371)",
     "(726, 1544.55, 303.852, 0.692372)"),
    ("buff zerker b", "(726, 1737.566, 435.8455, -8.086342)",
     "(726, 1737.566, 435.8455, -8.086343)"),
    ("buff band", "x 1544.55 - 2175.866", "x 1544.56 - 2175.866"),
    ("buff entry speed", "Speed gameobject 179871", "Speed gameobject 179872"),
    ("buff entry zerker", "Berserking gameobject 179905",
     "Berserking gameobject 179906"),
    ("buff respawn", "BUFF_RESPAWN_TIME = 180 s", "BUFF_RESPAWN_TIME = 181 s"),
    ("sniff", "id 179899 in sniff", "id 179900 in sniff"),
    ("no buff wiki", "these six spawns is unverified",
     "these six spawns is proven"),
    ("core claim", "it does NOT use the 227741/227740 flag",
     "it DOES use the 227741/227740 flag"),
    ("haven twin", "verified to be a Twin Peaks script with",
     "verified to be a Warsong Gulch script with"),
]


def stage3(corpora):
    token_map = {
        "tph": [
            ("timer resp", "BG_TP_FLAG_RESPAWN_TIME                 = 23000"),
            ("timer drop", "BG_TP_FLAG_DROP_TIME                    = 10000"),
            ("door a1", "= 206653"), ("door a2", "= 206654"),
            ("door a3", "= 206655"),
            ("door h1", "= 208205"), ("door h2", "= 208206"),
            ("door h3", "= 208207"),
            ("flag a", "= 227741"), ("flag h", "= 227740"),
            ("ground a", "= 227745"), ("ground h", "= 227744"),
            ("gy array", "uint32 const BG_TP_GraveyardIds[TP_MAX_GRAVEYARDS] "
                         "= { 1726, 1727, 1729, 1728, 1749, 1750 };"),
            ("maxscore", "GetMaxScore() const override { return 3; }"),
            ("gy enum", "TP_GRAVEYARD_FLAGROOM_ALLIANCE          = 0"),
        ],
        "tpc": [
            ("flag spawn a", "BG_OBJECT_A_FLAG_TP_ENTRY, 2117.637f, "
                             "191.6823f, 44.05199f, 6.021387f"),
            ("flag spawn h", "BG_OBJECT_H_FLAG_TP_ENTRY, 1578.337f, "
                             "344.0451f, 2.418409f, 2.792518f"),
            ("flag respawn param", "BG_TP_FLAG_RESPAWN_TIME / 1000"),
            ("buff speed", "BG_OBJECTID_SPEEDBUFF_ENTRY, 1544.55f, "
                           "303.852f, 0.692371f"),
            ("buff regen", "BG_OBJECTID_REGENBUFF_ENTRY, 1754.163f, "
                           "242.125f, -14.13157f"),
            ("buff zerker", "BG_OBJECTID_BERSERKERBUFF_ENTRY, 1932.832f, "
                           "226.7917f, -17.05979f"),
            ("door spawn", "AddObject(BG_TP_OBJECT_DOOR_A_1, "
                           "BG_OBJECT_DOOR_A_1_TP_ENTRY, 2135.525f"),
            ("gy fn", "BattlegroundTwinPeaks::GetClosestGraveYard"),
            ("gy waiting", "LookupEntry(BG_TP_GraveyardIds["
                           "TP_GRAVEYARD_FLAGROOM_ALLIANCE + team])"),
            ("gy cmp", "grave_enemy_middle"),
            ("capture", "m_TeamScores[team]++"),
            ("spirit loop", "i = TP_GRAVEYARD_START_ALLIANCE; i < "
                            "TP_MAX_GRAVEYARDS"),
            ("sniff comment", "id 179899 in sniff"),
        ],
        "wsl": [
            ("row 1726", "(1726,726,2142.6,175.918,43.6513,150,"
                         "'Twin Peaks - Alliance Entrance'),"),
            ("row 1727", "(1727,726,1549.54,346.955,1.28533,0,"
                         "'Twin Peaks - Horde Entrance'),"),
            ("row 1728", "(1728,726,1561.16,212.76,13.8615,0,"
                         "'Twin Peaks - Horde Graveyard (Base)'),"),
            ("row 1729", "(1729,726,2168.1,332.038,34.6959,180,"
                         "'Twin Peaks - Alliance Graveyard (Base)'),"),
            ("row 1749", "(1749,726,1877.15,439.111,-4.00017,240,"
                         "'Twin Peaks - Alliance Graveyard (Center)'),"),
            ("row 1750", "(1750,726,1816.87,160.083,1.80644,60,"
                         "'Twin Peaks - Horde Graveyard (Center)'),"),
            ("row 3944", "(3944,726,2138.85,178.863,43.7,148,"
                         "'Twin Peaks - Alliance Sploit Teleport Trigger "
                         "Target'),"),
            ("row 3947", "(3947,726,1555.94,346.375,1.76868,356,"
                         "'Twin Peaks - Horde Sploit Teleport Trigger "
                         "Target'),"),
            ("row 4283", "(4283,726,1819.45,189.984,-18.8967,60,"
                         "'Twin Peaks - Horde Graveyard (Center) Anti "
                         "Exploit'),"),
            ("row 4284", "(4284,726,1871.68,425.066,-16.3683,240,"
                         "'Twin Peaks - Alliance Graveyard (Center) Anti "
                         "Exploit'),"),
            ("row 4341", "(4341,726,2156.57,319.844,23.1756,206.749,"
                         "'Twin Peaks - Alliance Graveyard (Base) Anti "
                         "Exploit'),"),
            ("row 4342", "(4342,726,1578.69,209.264,0.766625,358.629,"
                         "'Twin Peaks - Horde Graveyard (Base) Anti "
                         "Exploit'),"),
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


def parse_script(tph, tpc):
    out = {}

    def rows_of(block):
        return [tuple(v.strip().rstrip("f") for v in
                      re.findall(r"[-\d.]+f", r))
                for r in re.findall(r"\{(.*?)\}", block, re.S)]

    out["flag_a"] = re.search(
        r"BG_OBJECT_A_FLAG_TP_ENTRY, ([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f, "
        r"([-\d.]+)f", tpc).groups()
    out["flag_h"] = re.search(
        r"BG_OBJECT_H_FLAG_TP_ENTRY, ([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f, "
        r"([-\d.]+)f", tpc).groups()
    out["doors"] = re.findall(
        r"AddObject\(BG_TP_OBJECT_DOOR_[AH]_\d, BG_OBJECT_DOOR_[AH]_\d_"
        r"TP_ENTRY, ([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f", tpc)
    out["buffs"] = [tuple(m) for m in re.findall(
        r"ENTRY, ([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f, ([-\d.]+)f,\s*0, 0, "
        r"[-\d.]+f, [-\d.]+f, BUFF_RESPAWN_TIME\)", tpc)]
    m = re.search(r"BG_TP_GraveyardIds\[TP_MAX_GRAVEYARDS\] = \{([^}]*)\}",
                  tph)
    out["gy_ids"] = [v.strip() for v in m.group(1).split(",")]
    m = re.search(r"BG_TP_FLAG_RESPAWN_TIME\s+=\s*(\d+)", tph)
    out["timer_r"] = m.group(1)
    m = re.search(r"BG_TP_FLAG_DROP_TIME\s+=\s*(\d+)", tph)
    out["timer_d"] = m.group(1)
    m = re.search(r"GetMaxScore\(\) const override \{ return (\d+); \}", tph)
    out["maxscore"] = m.group(1)
    return out


def stage4(text, corpora, probe=False):
    if probe:
        text = text.replace("(726, 2142.6, 175.918, 43.6513)",
                            "(726, 2143.6, 175.918, 43.6513)")
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

    s = parse_script(corpora["tph"], corpora["tpc"])
    want_list = ["(726, %s, %s, %s)" % t[:3] for t in (s["flag_a"],
                                                       s["flag_h"])]
    want_list += ["(726, %s, %s, %s)" % t[:3] for t in s["doors"]]
    want_list += ["(726, %s, %s, %s)" % t[:3] for t in s["buffs"]]
    missing = [w for w in want_list if w not in flat]
    lines.append("    script coordinate triples matched: %d/%d"
                 % (len(want_list) - len(missing), len(want_list)))
    if missing:
        fails.append("script triples missing: %s" % missing)

    checks = [
        ("timers", "BG_TP_FLAG_RESPAWN_TIME = %s ms" % s["timer_r"]),
        ("drop timer", "BG_TP_FLAG_DROP_TIME = %s ms" % s["timer_d"]),
        ("maxscore", "GetMaxScore() returns %s" % s["maxscore"]),
        ("gy array", "BG_TP_GraveyardIds = {%s}" % ", ".join(s["gy_ids"])),
    ]
    sok = 0
    for name, want in checks:
        ok = want in flat
        sok += ok
        if not ok:
            fails.append("%s (%s)" % (name, want))
    lines.append("    script-derived scalars: %d/%d match doc"
                 % (sok, len(checks)))

    A = (float(rows[1726]["x"]), float(rows[1726]["y"]))
    H = (float(rows[1727]["x"]), float(rows[1727]["y"]))
    fa = (float(s["flag_a"][0]), float(s["flag_a"][1]))
    fh = (float(s["flag_h"][0]), float(s["flag_h"][1]))
    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
    dA = [tuple(float(v) for v in t[:2]) for t in s["doors"][:3]]
    dH = [tuple(float(v) for v in t[:2]) for t in s["doors"][3:]]
    nA = min(range(3), key=lambda i: dist(A, dA[i]))
    nH = min(range(3), key=lambda i: dist(H, dH[i]))
    da = [rd(dist(A, d)) for d in dA]
    dh = [rd(dist(H, d)) for d in dH]
    ok = ("to doors 1/2/3 = %d / %d / %d yd" % tuple(da)) in flat and \
         ("to doors 1/2/3 = %d / %d / %d yd" % tuple(dh)) in flat
    if not ok:
        fails.append("door distances %s %s" % (da, dh))
    lines.append("    door distances: A %s / H %s" % (da, dh))

    routes = [("A->Hflag", A, dA[nA], fh), ("A->Aflag", A, dA[nA], fa),
              ("H->Aflag", H, dH[nH], fa), ("H->Hflag", H, dH[nH], fh)]
    rok = 0
    for name, st, door, tgt in routes:
        l1, l2, dirc = rd(dist(st, door)), rd(dist(door, tgt)), \
            rd(dist(st, tgt))
        ok = ("legs: %d yd, %d yd" % (l1, l2)) in flat and \
             ("direct %d yd" % dirc) in flat
        rok += ok
        if not ok:
            fails.append("route %s" % name)
    lines.append("    flag routes: %d/4 match recompute (nearest doors "
                 "A%d+1/H%d+1)" % (rok, nA, nH))

    cross = rd(dist(fa, fh))
    ok = ("Flag-to-flag cross distance (recomputed): %d yd" % cross) in flat
    if not ok:
        fails.append("cross %d" % cross)
    ctx = [
        ("graveyard %d yd" % rd(dist(fa, rows[1729]["x"] and
                                     (float(rows[1729]["x"]),
                                      float(rows[1729]["y"]))))),
    ] if False else []
    # GY context distances
    pairs = [
        ("graveyard %d yd" % rd(dist(fa, (float(rows[1729]["x"]),
                                          float(rows[1729]["y"])))), "ab"),
        ("graveyard %d yd" % rd(dist(fa, (float(rows[1749]["x"]),
                                          float(rows[1749]["y"])))), "ac"),
        ("graveyard %d yd" % rd(dist(fh, (float(rows[1728]["x"]),
                                          float(rows[1728]["y"])))), "hb"),
        ("graveyard %d yd" % rd(dist(fh, (float(rows[1750]["x"]),
                                          float(rows[1750]["y"])))), "hc"),
        ("to Alliance center graveyard %d yd" % rd(
            dist(A, (float(rows[1749]["x"]), float(rows[1749]["y"])))), "asc"),
        ("to Horde center graveyard %d yd" % rd(
            dist(H, (float(rows[1750]["x"]), float(rows[1750]["y"])))), "hsc"),
        ("base graveyard pair separation %d yd" % rd(
            dist((float(rows[1729]["x"]), float(rows[1729]["y"])),
                 (float(rows[1728]["x"]), float(rows[1728]["y"])))), "sepb"),
        ("graveyard pair separation %d yd" % rd(
            dist((float(rows[1749]["x"]), float(rows[1749]["y"])),
                 (float(rows[1750]["x"]), float(rows[1750]["y"])))), "sepc"),
    ]
    cok = 0
    for want, tag in pairs:
        ok = want in flat
        cok += ok
        if not ok:
            fails.append("ctx %s (%s)" % (tag, want))
    lines.append("    GY-context distances: %d/8 match recompute" % cok)

    xs = [float(b[0]) for b in s["buffs"]]
    ys = [float(b[1]) for b in s["buffs"]]
    want = "x %s - %s, y %s - %s" % (str(min(xs)), str(max(xs)),
                                     str(min(ys)), str(max(ys)))
    ok = want in flat
    if not ok:
        fails.append("buff band (%s)" % want)
    lines.append("    buff band: %s" % ("ok" if ok else "MISMATCH " + want))
    lines.append("    cross distance: %d yd" % cross)
    if not ok:
        pass

    ok_c, c_lines, missing_c = coord_trace(text, corpora)
    lines.extend(c_lines)
    if not ok_c:
        fails.append("coordinate trace: %s" % missing_c[:6])
    probe_txt = text.replace("(726, 1561.16, 212.76, 13.8615)",
                             "(726, 1562.16, 212.76, 13.8615)")
    ok2, _, _ = coord_trace(probe_txt, corpora)
    probe_ok = (probe_txt != text) and not ok2
    lines.append("    coordinate probe reacts: %s"
                 % ("yes" if probe_ok else "no"))
    if not probe_ok:
        fails.append("coordinate probe")
    return fails, lines


def stage5(text, corpora):
    lines, fails = [], []
    m726 = []
    for line in corpora["wsl"].splitlines():
        m = re.match(r"\((\d+),(\d+),", line.strip())
        if m and m.group(2) == "726":
            m726.append(int(m.group(1)))
    ok = sorted(m726) == sorted(DOC_IDS)
    if not ok:
        fails.append("map-726 rows = %s" % sorted(m726))
    lines.append("    dump map-726 rows: %d, ids match: %s"
                 % (len(m726), "yes" if ok else "NO"))

    n_ac = len(re.findall(r"(?i)twin|,726,", corpora["act"]))
    ok = n_ac == 0
    if not ok:
        fails.append("AC has %d matches" % n_ac)
    lines.append("    AzerothCore Twin/726 rows: %d (need 0)" % n_ac)

    n_unused = len(re.findall(r"3944|3947|4283|4284|4341|4342",
                              corpora["tph"] + corpora["tpc"]))
    ok = n_unused == 0
    if not ok:
        fails.append("sploit/anti ids referenced %d times" % n_unused)
    lines.append("    sploit/anti ids in LegionCore script: %d (need 0)"
                 % n_unused)

    # corrected claim: both BfA cores DO ship BattlegroundTP.cpp
    for repo in (HAVEN, BFA):
        res = subprocess.run(
            ["gh", "api", "repos/%s/contents/src/server/game/"
             "Battlegrounds/Zones" % repo, "--jq", ".[].name"],
            capture_output=True, text=True)
        names = [n for n in res.stdout.split() if n]
        has_tp = "BattlegroundTP.cpp" in names
        has_ttp = "BattlegroundTTP.cpp" in names
        sanity = "BattlegroundAB.cpp" in names
        okc = res.returncode == 0 and sanity and has_tp and has_ttp
        lines.append("    %-32s %d files, ships BattlegroundTP.cpp: %s"
                     % (repo, len(names), "yes" if okc else "NO"))
        if not okc:
            fails.append("zones listing %s" % repo)
    haven_tp = gh_content(HAVEN, HAVEN_TP)
    ok = (haven_tp is not None and "Twin" in haven_tp
          and "227741" not in haven_tp and "227740" not in haven_tp)
    if not ok:
        fails.append("Haven BattlegroundTP.cpp truth mismatch "
                     "(needs Twin refs, no 227741/227740)")
    lines.append("    Haven BattlegroundTP.cpp: Twin refs: %s, "
                 "227741/227740 absent: %s"
                 % ("yes" if (haven_tp and "Twin" in haven_tp) else "NO",
                    "yes" if (haven_tp and "227741" not in haven_tp
                              and "227740" not in haven_tp) else "NO"))

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
    print("AUDIT: Coordinates_Twin_Peaks_COMPLETED.txt (BG step 7)")
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
        {"tph": [("flag entry", "= 227741")]},
        lambda t: t.replace("= 227741", "= 227742"))
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
