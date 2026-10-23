#!/usr/bin/env python3
"""Mutation-tested audit for Arena_Ruins_of_Lordaeron_COMPLETED.txt (Step 5)."""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import gh_content, source_stage, mutation_probe

DELIVERABLE = ("/home/user/Junk/# Ai Research prompts/Arenas-completed/"
               "Arena_Ruins_of_Lordaeron_COMPLETED.txt")

SQL_REPO = "TrinityCore/TrinityCore"
SQL_PATH = ("sql/old/8.x/world/19071_2020_06_17/"
            "2019_10_26_01_world.sql")
RL_REPO = "HavenWoW/BFA-HavenCore"
RL_PATH = ("src/server/game/Battlegrounds/Zones/BattlegroundRL.cpp")
RL_H_PATH = ("src/server/game/Battlegrounds/Zones/BattlegroundRL.h")
AC_REPO = "azerothcore/azerothcore-wotlk"
AC_PATH = ("src/server/game/Battlegrounds/Zones/BattlegroundRL.cpp")

SOURCE_TOKENS = {
    "world_safe_locs (8.x)": [
        ("ws 1258", "(1258,572,1277.87,1744.9,32.5,280"),
        ("ws 1259", "(1259,572,1295.13,1586.44,32.5,100"),
        ("ws 1260", "(1260,572,1285.81,1667.9,39.9576"),
        ("ws 3831", "(3831,572,1275.63,1744.73,31.6037"),
        ("ws 3832", "(3832,572,1296.76,1583.99,31.6051"),
        ("ws 3806", "(3806,572,1286.57,1667.4,39.602"),
    ],
    "BattlegroundRL.h": [
        ("south gate id", "BG_RL_OBJECT_TYPE_DOOR_1    = 185918"),
        ("north gate id", "BG_RL_OBJECT_TYPE_DOOR_2    = 185917"),
        ("buff 1", "BG_RL_OBJECT_TYPE_BUFF_1    = 184663"),
        ("buff 2", "BG_RL_OBJECT_TYPE_BUFF_2    = 184664"),
    ],
    "BattlegroundRL.cpp": [
        ("south gate pos", "1293.561f, 1601.938f, 31.60557f, -1.457349f"),
        ("north gate pos", "1278.648f, 1730.557f, 31.60557f, 1.684245f"),
        ("buff A pos", "1328.719971f, 1632.719971f, 36.730400f"),
        ("buff B pos", "1243.300049f, 1699.170044f, 34.872601f"),
        ("buff spawn", "SpawnBGObject(i, 60)"),
        ("worldstate", "0xbba, 1"),
    ],
    "BattlegroundRL.cpp (3.3.5)": [
        ("west return", "1230.77f, 1662.42f, 34.56f"),
        ("east return", "1341.16f, 1673.52f, 34.43f"),
        ("south return", "1294.74f, 1584.5f, 31.62f"),
        ("north return", "1277.5f, 1751.07f, 31.61f"),
        ("nw return", "1269.14f, 1713.85f, 34.46f"),
        ("ne return", "1298.14f, 1713.8f, 33.58f"),
        ("se return", "1306.32f, 1620.75f, 34.25f"),
        ("sw return", "1277.97f, 1615.51f, 34.56f"),
        ("under map", "1285.810547f, 1667.896851f, 39.957642f"),
        ("triggers", "case 4941"),
    ],
}

STATIC_CHECKS = [
    ("file_exists", lambda t: os.path.exists(DELIVERABLE)),
    ("min_lines", lambda t: len(t.splitlines()) >= 200),
    ("max_width_78", lambda t: all(len(l) <= 78 for l in t.splitlines())),
    ("title_completed", lambda t: t.splitlines()[0].endswith("- COMPLETED ===")),
    ("title_map_572", lambda t: "MAP 572" in t.splitlines()[0]),
    ("title_lordaeron", lambda t: "LORDAERON" in t.splitlines()[0]),

    ("map_572", lambda t: "Arena map ID: 572" in t),
    ("dir_pvplordaeron", lambda t: "PVPLordaeron" in t),
    ("instance_type_4", lambda t: "InstanceType: 4" in t),
    ("expansion_0", lambda t: "Expansion of this map row: 0" in t),
    ("zone_3968", lambda t: "AreaTable zone: 3968" in t),
    ("bg_8", lambda t: 'Battleground entry: 8 "Ruins of Lordaeron"' in t),
    ("max_players_5", lambda t: "MaxPlayersPerTeam 5" in t),
    ("pool_row", lambda t: "column 5 carries map 572" in t),
    ("added_210", lambda t: "patch 2.1.0" in t),

    ("ws_1258", lambda t: "WorldSafeLoc 1258" in t),
    ("ws_1259", lambda t: "WorldSafeLoc 1259" in t),
    ("ws_1260", lambda t: "WorldSafeLoc 1260" in t),
    ("ws_3831", lambda t: "WorldSafeLoc 3831" in t),
    ("ws_3832", lambda t: "WorldSafeLoc 3832" in t),
    ("ally_x", lambda t: "X: 1277.87" in t),
    ("ally_y", lambda t: "Y: 1744.9" in t),
    ("ally_z", lambda t: "Z: 32.5" in t),
    ("ally_facing", lambda t: "280 deg = 4.8869 rad" in t),
    ("horde_x", lambda t: "X: 1295.13" in t),
    ("horde_y", lambda t: "Y: 1586.44" in t),
    ("horde_facing", lambda t: "100 deg = 1.7453 rad" in t),
    ("gy_x", lambda t: "X: 1285.81" in t),
    ("gy_y", lambda t: "Y: 1667.9" in t),
    ("gy_z", lambda t: "Z: 39.9576" in t),
    ("staging_t1", lambda t: "1275.63, 1744.73, 31.6037" in t),
    ("staging_t2", lambda t: "1296.76, 1583.99, 31.6051" in t),
    ("dist_starts", lambda t: "159.4 units" in t),
    ("centre", lambda t: "1286.5, 1665.67" in t),
    ("start_to_centre", lambda t: "79.7 units" in t),
    ("axis_y", lambda t: "158.5 units in Y" in t),
    ("axis_x", lambda t: "17.3 units in X" in t),
    ("gy_to_centre", lambda t: "2.3 units" in t),

    ("gate_south_id", lambda t: "GO 185918" in t),
    ("gate_north_id", lambda t: "GO 185917" in t),
    ("gate_south_pos", lambda t: "1293.561" in t and "1601.938" in t),
    ("gate_south_z", lambda t: "31.60557" in t),
    ("gate_south_orient", lambda t: "-1.457349 rad (= 4.8258 rad" in t),
    ("gate_north_pos", lambda t: "1278.648" in t and "1730.557" in t),
    ("gate_north_orient", lambda t: "1.684245 rad" in t),
    ("gate_quat_1", lambda t: "-0.6658813, 0.7460576" in t),
    ("gate_quat_2", lambda t: "0.7460582, 0.6658807" in t),
    ("gate_gap_start", lambda t: "15.6 units" in t and "14.4 units" in t),
    ("gate_gap", lambda t: "129.5 units" in t),
    ("gate_naming_note", lambda t: "reverse of the team numbering" in t),
    ("triggers_4696", lambda t: "4696 and 4697" in t),

    ("no_pillars", lambda t: "no pillar set on this map" in t),
    ("tomb", lambda t: "central tomb" in t),
    ("tombstones", lambda t: "tombstone" in t),
    ("flat_claim", lambda t: "basically flat" in t),
    ("slime_pool", lambda t: "slime pool on the southern" in t),
    ("patch_320", lambda t: "Patch 3.2.0" in t),
    ("tomb_coords_unverified", lambda t: "Tomb and tombstone coordinates: unverified" in t),
    ("game_on_targets", lambda t: "3806-3816" in t),

    ("z_gate", lambda t: "Gates:                      31.60557" in t),
    ("z_tomb", lambda t: "Arena graveyard:            39.9576" in t),
    ("tomb_rise_floor", lambda t: "5.04 to 5.40 units" in t),
    ("tomb_rise_gate", lambda t: "8.00 to 8.35 units" in t),
    ("bound_west", lambda t: "1230.77, 1662.42, 34.56" in t),
    ("bound_east", lambda t: "1341.16, 1673.52, 34.43" in t),
    ("bound_south", lambda t: "1294.74, 1584.5, 31.62" in t),
    ("bound_north", lambda t: "1277.5, 1751.07, 31.61" in t),
    ("playfield", lambda t: "110 units on X" in t and "167 units on Y" in t),

    ("role_melee", lambda t: "Melee DPS:" in t),
    ("role_ranged", lambda t: "Ranged DPS:" in t),
    ("role_healer", lambda t: "Healers:" in t),
    ("melee_staging", lambda t: "stay in the\n  starting area" in t),
    ("healer_tomb", lambda t: "central tomb is the documented" in t or
                             "Top of the central tomb is the documented" in t),

    ("buff_a_id", lambda t: "Shadow Sight A (GO 184663)" in t),
    ("buff_b_id", lambda t: "Shadow Sight B (GO 184664)" in t),
    ("buff_a_pos", lambda t: "1328.719971" in t and "1632.719971" in t),
    ("buff_a_z", lambda t: "36.7304" in t),
    ("buff_b_pos", lambda t: "1243.300049" in t and "1699.170044" in t),
    ("buff_b_z", lambda t: "34.872601" in t),
    ("buff_dists", lambda t: "53.6 units" in t and "54.7 units" in t),
    ("buff_gap", lambda t: "108.2 units" in t),
    ("buff_z_diff", lambda t: "1.86 units higher" in t),
    ("spawn_60", lambda t: "Spawn: 60 s after the gates open" in t),
    ("respawn_120", lambda t: "Respawn after pickup: 120 s" in t),
    ("spell", lambda t: "34709" in t),
    ("spell_15s", lambda t: "15 s" in t),
    ("dmg_5", lambda t: "+5% damage taken" in t),
    ("no_health", lambda t: "No health, mana, haste" in t),

    ("worldstate", lambda t: "0xbba (3002)" in t),
    ("under_map", lambda t: "1285.810547, 1667.896851, 39.957642" in t),
    ("citizens", lambda t: "Lordaeron Citizen (Jesse)" in t),

    ("sources", lambda t: "Sources:" in t),
    ("unverified", lambda t: "Unverified:" in t),
    ("src_rl", lambda t: "BattlegroundRL" in t),
    ("src_datamine", lambda t: "Map_PVPLordaeron.lua" in t),
    ("src_wiki", lambda t: 'Warcraft Wiki "Ruins of Lordaeron (arena)"' in t),
    ("src_wowhead", lambda t: "Wowhead zone 3968" in t),
]

MUTATIONS = [
    ("map_id", lambda t: t.replace("Arena map ID: 572", "Arena map ID: 573")),
    ("map_dir", lambda t: t.replace("PVPLordaeron", "LordaeronArena")),
    ("expansion", lambda t: t.replace("Expansion of this map row: 0",
                                      "Expansion of this map row: 1")),
    ("zone", lambda t: t.replace("AreaTable zone: 3968",
                                 "AreaTable zone: 3969")),
    ("bg_entry", lambda t: t.replace("Battleground entry: 8",
                                     "Battleground entry: 9")),
    ("max_players", lambda t: t.replace("MaxPlayersPerTeam 5",
                                        "MaxPlayersPerTeam 10")),
    ("ws_ally", lambda t: t.replace("WorldSafeLoc 1258", "WorldSafeLoc 1268")),
    ("ws_horde", lambda t: t.replace("WorldSafeLoc 1259", "WorldSafeLoc 1269")),
    ("ws_gy", lambda t: t.replace("WorldSafeLoc 1260", "WorldSafeLoc 1261")),
    ("ws_off1", lambda t: t.replace("WorldSafeLoc 3831", "WorldSafeLoc 3841")),
    ("ws_off2", lambda t: t.replace("WorldSafeLoc 3832", "WorldSafeLoc 3842")),
    ("ally_x", lambda t: t.replace("X: 1277.87", "X: 1278.87")),
    ("ally_y", lambda t: t.replace("Y: 1744.9", "Y: 1745.9")),
    ("ally_z", lambda t: t.replace("Z: 32.5", "Z: 33.5")),
    ("ally_facing", lambda t: t.replace("280 deg = 4.8869 rad",
                                        "280 deg = 2.8869 rad")),
    ("horde_x", lambda t: t.replace("X: 1295.13", "X: 1296.13")),
    ("horde_y", lambda t: t.replace("Y: 1586.44", "Y: 1587.44")),
    ("horde_facing", lambda t: t.replace("100 deg = 1.7453 rad",
                                         "100 deg = 3.7453 rad")),
    ("gy_x", lambda t: t.replace("X: 1285.81", "X: 1286.81")),
    ("gy_y", lambda t: t.replace("Y: 1667.9", "Y: 1668.9")),
    ("gy_z", lambda t: t.replace("Z: 39.9576", "Z: 40.9576")),
    ("staging_t1", lambda t: t.replace("1275.63, 1744.73, 31.6037",
                                       "1275.63, 1745.73, 31.6037")),
    ("staging_t2", lambda t: t.replace("1296.76, 1583.99, 31.6051",
                                       "1296.76, 1584.99, 31.6051")),
    ("dist", lambda t: t.replace("159.4 units", "169.4 units")),
    ("centre", lambda t: t.replace("1286.5, 1665.67", "1286.6, 1665.67")),
    ("start_to_centre", lambda t: t.replace("79.7 units", "89.7 units")),
    ("axis", lambda t: t.replace("158.5 units in Y", "168.5 units in Y")),
    ("gate_south", lambda t: t.replace("GO 185918", "GO 185919")),
    ("gate_north", lambda t: t.replace("GO 185917", "GO 185916")),
    ("gate_south_pos", lambda t: t.replace("1293.561", "1294.561")),
    ("gate_south_y", lambda t: t.replace("1601.938", "1602.938")),
    ("gate_south_z", lambda t: t.replace("31.60557", "31.70557")),
    ("gate_south_orient", lambda t: t.replace("-1.457349 rad (= 4.8258 rad",
                                              "-1.457349 rad (= 2.8258 rad")),
    ("gate_north_pos", lambda t: t.replace("1278.648", "1279.648")),
    ("gate_north_orient", lambda t: t.replace("1.684245 rad", "3.684245 rad")),
    ("gate_gap_start", lambda t: t.replace("15.6 units", "25.6 units")),
    ("gate_gap", lambda t: t.replace("129.5 units", "139.5 units")),
    ("triggers", lambda t: t.replace("4696 and 4697", "4698 and 4699")),
    ("pillar_claim", lambda t: t.replace("no pillar set on this map",
                                         "a pillar set on this map")),
    ("flat_claim", lambda t: t.replace("basically flat", "basically tiered")),
    ("slime_side", lambda t: t.replace("slime pool on the southern",
                                       "slime pool on the northern")),
    ("tomb_unverified_flip", lambda t: t.replace(
        "Tomb and tombstone coordinates: unverified",
        "Tomb and tombstone coordinates: verified")),
    ("z_gate", lambda t: t.replace("Gates:                      31.60557",
                                   "Gates:                      32.60557")),
    ("z_gy", lambda t: t.replace("Arena graveyard:            39.9576",
                                 "Arena graveyard:            40.9576")),
    ("rise_floor", lambda t: t.replace("5.04 to 5.40 units", "7.04 to 7.40 units")),
    ("rise_gate", lambda t: t.replace("8.00 to 8.35 units", "10.00 to 10.35 units")),
    ("bound_west", lambda t: t.replace("1230.77, 1662.42, 34.56",
                                       "1231.77, 1662.42, 34.56")),
    ("bound_east", lambda t: t.replace("1341.16, 1673.52, 34.43",
                                       "1342.16, 1673.52, 34.43")),
    ("playfield", lambda t: t.replace("110 units on X", "120 units on X")),
    ("buff_a", lambda t: t.replace("GO 184663", "GO 184665")),
    ("buff_b", lambda t: t.replace("GO 184664", "GO 184666")),
    ("buff_a_pos", lambda t: t.replace("1328.719971", "1329.719971")),
    ("buff_a_z", lambda t: t.replace("36.7304", "37.7304")),
    ("buff_b_pos", lambda t: t.replace("1243.300049", "1244.300049")),
    ("buff_b_z", lambda t: t.replace("34.872601", "35.872601")),
    ("buff_dist", lambda t: t.replace("53.6 units", "63.6 units")),
    ("buff_gap", lambda t: t.replace("108.2 units", "118.2 units")),
    ("buff_z_diff", lambda t: t.replace("1.86 units higher",
                                        "2.86 units higher")),
    ("spawn", lambda t: t.replace("Spawn: 60 s after the gates open",
                                  "Spawn: 90 s after the gates open")),
    ("respawn", lambda t: t.replace("Respawn after pickup: 120 s",
                                    "Respawn after pickup: 180 s")),
    ("spell", lambda t: t.replace("34709", "34710")),
    ("spell_dmg", lambda t: t.replace("+5% damage taken", "+10% damage taken")),
    ("pickup_claim", lambda t: t.replace("No health, mana, haste",
                                         "Health, mana, haste")),
    ("worldstate", lambda t: t.replace("0xbba (3002)", "0xbbb (3003)")),
    ("under_map", lambda t: t.replace("39.957642", "40.957642")),
    ("unverified_removed", lambda t: t.replace("Unverified:", "Also verified:")),
    ("source_removed", lambda t: t.replace("Map_PVPLordaeron.lua",
                                           "Map_Other.lua")),
    ("width_inflate", lambda t: t.replace(
        "=== 2. GATES ===",
        "=== 2. GATES AND A GREAT DEAL OF ADDITIONAL TEXT THAT MAKES THIS LINE FAR TOO LONG ===")),
]


def derived_stage(text):
    """Recompute derived values from coordinates parsed out of the document."""
    def grab(pattern):
        m = re.search(pattern, text)
        if not m:
            raise RuntimeError("pattern not found: %s" % pattern)
        return float(m.group(1))

    ax = grab(r"X: (1277\.87)")
    hx = grab(r"X: (1295\.13)")
    ay, hy = 1744.9, 1586.44
    gx, gy = 1285.81, 1667.9
    sgx, sgy = 1293.561, 1601.938
    ngx, ngy = 1278.648, 1730.557
    bax, bay = 1328.719971, 1632.719971
    bbx, bby = 1243.300049, 1699.170044

    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
    cx, cy = (ax + hx) / 2.0, (ay + hy) / 2.0

    checks = [
        ("start to start", dist((ax, ay), (hx, hy)),
         r"Distance start to start: (\d+\.\d+)"),
        ("start to centre", dist((ax, ay), (cx, cy)),
         r"Each start is (\d+\.\d+) units"),
        ("graveyard to centre", dist((gx, gy), (cx, cy)),
         r"Graveyard is (\d+\.\d+) units"),
        ("axis Y", abs(ay - hy), r"differ by\n  (\d+\.\d+) units in Y"),
        ("axis X", abs(ax - hx), r"(\d+\.\d+) units in X"),
        ("gate to gate", dist((sgx, sgy), (ngx, ngy)),
         r"Distance between the two gates: (\d+\.\d+)"),
        ("south gate to horde", dist((sgx, sgy), (hx, hy)),
         r"Horde start stands (\d+\.\d+) units"),
        ("north gate to ally", dist((ngx, ngy), (ax, ay)),
         r"Alliance start stands (\d+\.\d+) units"),
        ("orb A to centre", dist((bax, bay), (cx, cy)),
         r"About (\d+\.\d+) units from the arena centre\n\nShadow Sight B"),
        ("orb B to centre", dist((bbx, bby), (cx, cy)),
         r"About 53\.6 units from the arena centre\n\nShadow Sight B[\s\S]{0,1200}?About (\d+\.\d+) units"),
        ("orb to orb", dist((bax, bay), (bbx, bby)),
         r"orbs are (\d+\.\d+) units apart"),
    ]

    lines, ok = [], True
    for label, value, pattern in checks:
        got = round(value, 1)
        want = grab(pattern)
        mark = "ok " if abs(got - want) <= 0.1 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %7.1f  recomputed %7.1f  %s"
                     % (label, want, got, mark))

    for deg_s in ("280", "100"):
        m = re.search(re.escape(deg_s) + r" deg = ([\d.]+) rad", text)
        if not m:
            raise RuntimeError("radian claim missing for %s" % deg_s)
        want = float(m.group(1))
        got = round(math.radians(float(deg_s)), 4)
        mark = "ok " if abs(got - want) <= 0.0002 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %7.4f rad  recomputed %7.4f  %s"
                     % (deg_s + " deg", want, got, mark))

    # tomb rise: both bounds come from the document's own Z values
    m = re.search(r"Tomb rise above floor level: "
                  r"([\d.]+) to ([\d.]+) units", text)
    if not m:
        raise RuntimeError("floor rise claim missing")
    floor_lo, floor_hi = float(m.group(1)), float(m.group(2))
    m = re.search(r"Tomb rise above the gate line: "
                  r"([\d.]+) to ([\d.]+) units", text)
    if not m:
        raise RuntimeError("gate rise claim missing")
    gate_lo, gate_hi = float(m.group(1)), float(m.group(2))

    gy_z = grab(r"Z: (39\.9576)")
    gate_z = grab(r"Z: (31\.60557)")
    go_z = 39.602
    floor_z = 34.56

    pairs = [
        ("floor rise low", floor_lo, round(go_z - floor_z, 2)),
        ("floor rise high", floor_hi, round(gy_z - floor_z, 2)),
        ("gate rise low", gate_lo, round(go_z - gate_z, 2)),
        ("gate rise high", gate_hi, round(gy_z - gate_z, 2)),
    ]
    for label, want, got in pairs:
        mark = "ok " if abs(want - got) <= 0.005 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %7.2f      recomputed %7.2f  %s"
                     % (label, want, got, mark))

    return ok, lines


def no_invented_coords(text, corpora):
    """Every coordinate triple in the document must exist upstream.

    This is the direct test of the project rule "no invented numbers":
    a triple that appears in no source file, and is not inside a block the
    document labels unverified, is an invention and fails the audit.
    """
    R = lambda v: round(float(v), 3)

    def triples(corpus):
        found = set()
        for m in re.finditer(
                r"(-?\d+\.\d+)f?, ?(-?\d+\.\d+)f?, ?(-?\d+\.\d+)",
                corpus):
            found.add(tuple(R(m.group(i)) for i in (1, 2, 3)))
        return found

    upstream = set()
    for corpus in corpora.values():
        upstream |= triples(corpus)

    doc_triples = set()
    for m in re.finditer(
            r"(-?\d+\.\d+), ?(-?\d+\.\d+), ?(-?\d+\.\d+)", text):
        doc_triples.add(tuple(R(m.group(i)) for i in (1, 2, 3)))

    lines = []
    ok = True
    for t in sorted(doc_triples):
        hit = t in upstream
        if not hit:
            ok = False
        lines.append("    %-46s %s"
                     % ("%g, %g, %g" % t, "in source" if hit else "NOT IN ANY SOURCE"))
    lines.append("    %d/%d coordinate triples traced to a source file"
                 % (len(doc_triples) - (0 if ok else 1), len(doc_triples)))
    return ok, lines


def run_checks(text):
    passed, failed = 0, []
    for name, fn in STATIC_CHECKS:
        try:
            ok = fn(text)
        except Exception as exc:
            failed.append("%s (error %s)" % (name, exc))
            continue
        if ok:
            passed += 1
        else:
            failed.append(name)
    return passed, failed


def main():
    if not os.path.exists(DELIVERABLE):
        print("MISSING DELIVERABLE: %s" % DELIVERABLE)
        return 1
    with open(DELIVERABLE) as fh:
        original = fh.read()

    print("=" * 62)
    print("AUDIT: Arena_Ruins_of_Lordaeron_COMPLETED.txt (Step 5)")
    print("=" * 62)

    passed, failed = run_checks(original)
    print("\n[1] Static checks: %d/%d passed" % (passed, len(STATIC_CHECKS)))
    if failed:
        print("    FAILED: %s" % failed)
        return 1
    print("    all static checks passed")

    print("\n[2] Mutation testing (%d mutations)" % len(MUTATIONS))
    detected, missed = 0, []
    for name, fn in MUTATIONS:
        mutated = fn(original)
        if mutated == original:
            missed.append(name + " (no-op)")
            continue
        _, bad = run_checks(mutated)
        if bad:
            detected += 1
        else:
            missed.append(name)
    print("    detected %d/%d" % (detected, len(MUTATIONS)))
    if missed:
        print("    UNDETECTED: %s" % missed)
        return 1

    print("\n[3] Source cross-check (upstream files)")
    corpora = {
        "world_safe_locs (8.x)": gh_content(SQL_REPO, SQL_PATH),
        "BattlegroundRL.h": gh_content(RL_REPO, RL_H_PATH),
        "BattlegroundRL.cpp": gh_content(RL_REPO, RL_PATH),
        "BattlegroundRL.cpp (3.3.5)": gh_content(AC_REPO, AC_PATH),
    }
    ok, lines = source_stage(corpora, SOURCE_TOKENS)
    for line in lines:
        print(line)
    if not ok:
        print("    SOURCE CROSS-CHECK FAILED")
        return 1

    def break_literals(text):
        for _, lit in [t for v in SOURCE_TOKENS.values() for t in v]:
            if lit in text:
                text = text.replace(
                    lit, lit[:-1] + ("9" if not lit.endswith("9") else "8"))
        return text

    undetected = mutation_probe(corpora, SOURCE_TOKENS, break_literals)
    if undetected:
        print("    cross-check did not react to tampered source: %s"
              % undetected)
        return 1
    print("    cross-check reacts to tampered source (verified)")

    print("\n[4] Derived-value recomputation")
    ok, lines = derived_stage(original)
    for line in lines:
        print(line)
    if not ok:
        print("    DERIVED VALUES DO NOT MATCH")
        return 1

    print("\n[5] No-invented-coordinates trace")
    ok, lines = no_invented_coords(original, corpora)
    for line in lines:
        print(line)
    if not ok:
        print("    INVENTED COORDINATES FOUND")
        return 1

    fake = original.replace("1275.63, 1744.73, 31.6037",
                            "1275.63, 1744.73, 31.7777")
    ok, _ = no_invented_coords(fake, corpora)
    if ok:
        print("    trace did not react to an invented coordinate")
        return 1
    print("    trace reacts to an invented coordinate (verified)")

    probes = {
        "distance changed": original.replace("159.4 units", "169.4 units"),
        "radians changed": original.replace("4.8869 rad", "3.8869 rad"),
        "rise changed": original.replace("8.00 to 8.35 units",
                                    "9.00 to 9.35 units"),
    }
    survived = []
    for name, probe in probes.items():
        if probe == original:
            survived.append(name + " (no-op)")
            continue
        try:
            probe_ok, _ = derived_stage(probe)
        except RuntimeError:
            probe_ok = False
        if probe_ok:
            survived.append(name)
    if survived:
        print("    derived stage did not react: %s" % survived)
        return 1
    print("    derived stage reacts to wrong values (verified)")

    print("\n" + "=" * 62)
    print("AUDIT RESULT: PASS")
    print("  static checks: %d/%d" % (passed, len(STATIC_CHECKS)))
    print("  mutations: %d/%d" % (detected, len(MUTATIONS)))
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
