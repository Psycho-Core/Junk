#!/usr/bin/env python3
"""Mutation-tested audit for Arena_Tol_vir_Arena_COMPLETED.txt (Step 6)."""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import (gh_content, source_stage, mutation_probe,
                          coord_trace)

DELIVERABLE = ("/home/user/Junk/# Ai Research prompts/Arenas_complete/"
               "Arena_Tol_vir_Arena_COMPLETED.txt")

SQL_REPO = "TrinityCore/TrinityCore"
SQL_PATH = ("sql/old/8.x/world/19071_2020_06_17/"
            "2019_10_26_01_world.sql")
TVA_REPO = "HavenWoW/BFA-HavenCore"
TVA_PATH = ("src/server/game/Battlegrounds/Zones/BattlegroundTVA.cpp")
TVA_H_PATH = ("src/server/game/Battlegrounds/Zones/BattlegroundTVA.h")
DM_REPO = "Ghostopheles/Datamine"
DM_PATH = "Datamine_Maps/Generated/Map_TolVirArena.lua"
TPL_REPO = "zTerragor/vSLDB"
TPL_PATH = "sql/updates/world/2021_11_03_world_Battleground_Template.sql"

SOURCE_TOKENS = {
    "world_safe_locs (8.x)": [
        ("ws 4135", "980,-10716.7,429.295,24.4117,0"),
        ("ws 4136", "980,-10649.9,428.172,24.419,182.385"),
        ("ws 4137", "980,-10778.2,430.875,24.4117,0.332764"),
        ("ws 4138", "980,-10716.4,429.233,24.4117,0"),
    ],
    "BattlegroundTVA.h": [
        ("gate 213196", "BG_TV_OBJECT_TYPE_DOOR_1    = 213196"),
        ("gate 213197", "BG_TV_OBJECT_TYPE_DOOR_2    = 213197"),
        ("buff 184663", "BG_TV_OBJECT_TYPE_BUFF_1    = 184663"),
        ("buff 184664", "BG_TV_OBJECT_TYPE_BUFF_2    = 184664"),
    ],
    "BattlegroundTVA.cpp": [
        ("gate 1 pos", "-10654.3f, 428.3047f, 23.54276f, 3.141593f"),
        ("gate 2 pos", "-10774.61f, 431.2383f, 23.54276f, 0"),
        ("buff A pos", "-10717.63f, 383.8223f, 24.412825f"),
        ("buff B pos", "-10716.6f, 475.364f, 24.4131f"),
        ("worldstate", "0xE1A, 1"),
        ("triggers", "case 8451"),
        ("spawn", "SpawnBGObject(i, 60)"),
    ],
    "battleground_template": [
        ("bg 719 row", "(719, 0, 5, 90, 120, 4136, 4137, 10, 1, '', "
                       "'Tol\\'viron Arena')"),
        ("AV 150", "(1, 10, 40, 45, 120, 611, 610, 150"),
        ("WSG 75", "(2, 2, 10, 10, 120, 769, 770, 75"),
        ("AB 75", "(3, 2, 15, 10, 120, 890, 889, 75"),
        ("EotS 75", "(7, 2, 15, 35, 120, 1103, 1104, 75"),
        ("IoC 200", "(30, 10, 40, 71, 120, 1299, 1245, 200"),
        ("Kotmogu 50", "(699, 2, 10, 40, 120, 4534, 4535, 50"),
    ],
    "Map_TolVirArena.lua": [
        ("map name", 'MapName = "Tol\'Viron Arena"'),
        ("map id", "MapID = 980"),
        ("directory", "Directory = [[TolVirArena]]"),
        ("instance type", "InstanceType = 4"),
        ("expansion", "ExpansionID = 3"),
    ],
}

STATIC_CHECKS = [
    ("file_exists", lambda t: os.path.exists(DELIVERABLE)),
    ("min_lines", lambda t: len(t.splitlines()) >= 200),
    ("max_width_78", lambda t: all(len(l) <= 78 for l in t.splitlines())),
    ("title_completed", lambda t: t.splitlines()[0].endswith("- COMPLETED ===")),
    ("title_map_980", lambda t: "MAP 980" in t.splitlines()[0]),

    ("map_980", lambda t: "Arena map ID: 980" in t),
    ("dir_tolvirarena", lambda t: "TolVirArena" in t),
    ("instance_type_4", lambda t: "InstanceType: 4" in t),
    ("zone_6296", lambda t: "AreaTable zone: 6296" in t),
    ("expansion_field_3", lambda t: "ExpansionID field in the map row: 3" in t),
    ("expansion_caveat", lambda t: "not as a release claim" in t),
    ("bg_719", lambda t: 'Battleground entry: 719 "Tol\'viron Arena"' in t),
    ("max_players_5", lambda t: "MaxPlayersPerTeam 5" in t),
    ("lvl_90_120", lambda t: "MinLvl 90, MaxLvl 120" in t),
    ("start_max_dist", lambda t: "StartMaxDist 10" in t),
    ("added_504", lambda t: "patch 5.0.4" in t),
    ("sixth_arena", lambda t: "Sixth arena map" in t),
    ("uldum", lambda t: "Location: Uldum" in t),
    ("ruins_of_ammon", lambda t: "Ruins of Ammon" in t),

    ("ws_4136", lambda t: "WorldSafeLoc 4136" in t),
    ("ws_4137", lambda t: "WorldSafeLoc 4137" in t),
    ("ws_4135", lambda t: "WorldSafeLoc 4135" in t),
    ("ws_4138", lambda t: "WorldSafeLoc 4138" in t),
    ("ally_x", lambda t: "X: -10649.9" in t),
    ("ally_y", lambda t: "Y: 428.172" in t),
    ("ally_z", lambda t: "Z: 24.419" in t),
    ("ally_facing", lambda t: "182.385 deg = 3.1832 rad" in t),
    ("horde_x", lambda t: "X: -10778.2" in t),
    ("horde_y", lambda t: "Y: 430.875" in t),
    ("horde_z", lambda t: "Z: 24.4117" in t),
    ("horde_facing", lambda t: "0.332764 deg = 0.005808 rad" in t),
    ("gy_x", lambda t: "X: -10716.7" in t),
    ("gy_y", lambda t: "Y: 429.295" in t),
    ("go_x", lambda t: "X: -10716.4" in t),
    ("go_y", lambda t: "Y: 429.233" in t),
    ("dist_starts", lambda t: "128.3 units" in t),
    ("centre", lambda t: "-10714.05, 429.52" in t),
    ("start_to_centre", lambda t: "64.2 units" in t),
    ("axis_x", lambda t: "128.3 apart on X" in t),
    ("axis_y", lambda t: "2.7 apart on Y" in t),
    ("gy_to_centre", lambda t: "2.7 units from the centre" in t),
    ("go_to_centre", lambda t: "2.4 units from the centre" in t),

    ("gate_1_id", lambda t: "GO 213196" in t),
    ("gate_2_id", lambda t: "GO 213197" in t),
    ("gate_1_pos", lambda t: "-10654.3" in t and "428.3047" in t),
    ("gate_z", lambda t: "23.54276" in t),
    ("gate_1_orient", lambda t: "3.141593 rad" in t),
    ("gate_1_quat", lambda t: "0, 0, -1, 0" in t),
    ("gate_2_pos", lambda t: "-10774.61" in t and "431.2383" in t),
    ("gate_2_quat", lambda t: "0, 0, 0, 1" in t),
    ("gate_gap_start", lambda t: "4.4 units" in t and "3.6 units" in t),
    ("gate_gap", lambda t: "120.3 units" in t),
    ("triggers_8451", lambda t: "8451 and 8452" in t),
    ("gate_sill", lambda t: "0.876 units below" in t),

    ("pillars_four", lambda t: "Pillar count: 4" in t),
    ("pillars_unverified", lambda t: "Pillar positions: unverified" in t),
    ("no_los_objects", lambda t: "spawns no LoS object" in t),
    ("wiki_quote", lambda t: "direction of the pillars" in t),
    ("orb_axis", lambda t: "91.5 units apart along Y" in t),

    ("single_level", lambda t: "Single level" in t),
    ("z_ladder", lambda t: "Floor Z spans 23.54276 to 24.419" in t),
    ("spread", lambda t: "0.876 units" in t),
    ("flat_floor", lambda t: "0.0073 units" in t),

    ("role_melee", lambda t: "Melee DPS:" in t),
    ("role_ranged", lambda t: "Ranged DPS:" in t),
    ("role_healer", lambda t: "Healers:" in t),
    ("no_centre", lambda t: "Do not take the centre" in t),

    ("buff_a_id", lambda t: "Shadow Sight A (GO 184663)" in t),
    ("buff_b_id", lambda t: "Shadow Sight B (GO 184664)" in t),
    ("buff_a_pos", lambda t: "-10717.63" in t and "383.8223" in t),
    ("buff_a_z", lambda t: "24.412825" in t),
    ("buff_b_pos", lambda t: "-10716.6" in t and "475.364" in t),
    ("buff_b_z", lambda t: "24.4131" in t),
    ("buff_dists", lambda t: "45.8 units" in t and "45.9 units" in t),
    ("buff_a_orient", lambda t: "Orientation: 1.555 rad" in t),
    ("orb_z_level", lambda t: "to within 0.0003 units" in t),
    ("nagrand_orb_gap", lambda t: "orbs sit 108.9 apart" in t),
    ("buff_gap", lambda t: "91.5 units apart" in t),
    ("no_battlemaster_claim", lambda t: "BattlemasterList id" not in t),
    ("spawn_60", lambda t: "Spawn: 60 s after the gates open" in t),
    ("wiki_90s", lambda t: "wiki quotes 90 s" in t),
    ("orbs_opposite", lambda t: "opposite sides of the Arena" in t),
    ("respawn_120", lambda t: "Respawn after pickup: 120 s" in t),
    ("spell", lambda t: "34709" in t),
    ("spell_15s", lambda t: "15 s" in t),
    ("dmg_5", lambda t: "+5% damage taken" in t),
    ("no_health", lambda t: "No health, mana, haste" in t),
    ("four_objects", lambda t: "exactly four objects on this map" in t),
    ("no_fake_object_ids", lambda t: "179871" not in t and "179904" not in t),
    ("kotmogu_50", lambda t: "Kotmogu 50" in t),

    ("worldstate", lambda t: "Worldstate 0xE1A" in t),
    ("dampening_hotfix", lambda t: "2014-10-30" in t),
    ("no_oob", lambda t: "No out-of-bounds or under-map return points" in t),

    ("sources", lambda t: "Sources:" in t),
    ("unverified", lambda t: "Unverified:" in t),
    ("src_tva", lambda t: "BattlegroundTVA" in t),
    ("src_datamine", lambda t: "Map_TolVirArena.lua" in t),
    ("src_wiki", lambda t: 'Warcraft Wiki "Tol\'viron Arena"' in t),
]

MUTATIONS = [
    ("map_id", lambda t: t.replace("Arena map ID: 980", "Arena map ID: 981")),
    ("map_dir", lambda t: t.replace("TolVirArena", "TolVironArena")),
    ("zone", lambda t: t.replace("AreaTable zone: 6296",
                                 "AreaTable zone: 6297")),
    ("expansion_field", lambda t: t.replace("map row: 3", "map row: 4")),
    ("bg_entry", lambda t: t.replace("Battleground entry: 719",
                                     "Battleground entry: 720")),
    ("max_players", lambda t: t.replace("MaxPlayersPerTeam 5",
                                        "MaxPlayersPerTeam 10")),
    ("levels", lambda t: t.replace("MinLvl 90, MaxLvl 120",
                                   "MinLvl 10, MaxLvl 120")),
    ("start_max_dist", lambda t: t.replace("StartMaxDist 10",
                                           "StartMaxDist 0")),
    ("patch", lambda t: t.replace("patch 5.0.4", "patch 5.0.5")),
    ("ws_ally", lambda t: t.replace("WorldSafeLoc 4136",
                                    "WorldSafeLoc 4146")),
    ("ws_horde", lambda t: t.replace("WorldSafeLoc 4137",
                                     "WorldSafeLoc 4147")),
    ("ws_gy", lambda t: t.replace("WorldSafeLoc 4135",
                                  "WorldSafeLoc 4145")),
    ("ws_go", lambda t: t.replace("WorldSafeLoc 4138",
                                  "WorldSafeLoc 4148")),
    ("ally_x", lambda t: t.replace("X: -10649.9", "X: -10648.9")),
    ("ally_y", lambda t: t.replace("Y: 428.172", "Y: 429.172")),
    ("ally_z", lambda t: t.replace("Z: 24.419", "Z: 25.419")),
    ("ally_facing", lambda t: t.replace("182.385 deg = 3.1832 rad",
                                        "182.385 deg = 1.1832 rad")),
    ("horde_x", lambda t: t.replace("X: -10778.2", "X: -10777.2")),
    ("horde_y", lambda t: t.replace("Y: 430.875", "Y: 431.875")),
    ("horde_facing", lambda t: t.replace("0.332764 deg = 0.005808 rad",
                                         "0.332764 deg = 1.005808 rad")),
    ("gy_x", lambda t: t.replace("X: -10716.7", "X: -10715.7")),
    ("gy_y", lambda t: t.replace("Y: 429.295", "Y: 430.295")),
    ("go_x", lambda t: t.replace("X: -10716.4", "X: -10715.4")),
    ("go_y", lambda t: t.replace("Y: 429.233", "Y: 430.233")),
    ("dist", lambda t: t.replace("128.3 units", "138.3 units")),
    ("centre", lambda t: t.replace("-10714.05, 429.52",
                                   "-10714.15, 429.52")),
    ("start_to_centre", lambda t: t.replace("64.2 units", "74.2 units")),
    ("axis_x", lambda t: t.replace("128.3 apart on X", "138.3 apart on X")),
    ("axis_y", lambda t: t.replace("2.7 apart on Y", "3.7 apart on Y")),
    ("gate_1_id", lambda t: t.replace("GO 213196", "GO 213198")),
    ("gate_2_id", lambda t: t.replace("GO 213197", "GO 213199")),
    ("gate_1_x", lambda t: t.replace("-10654.3", "-10655.3")),
    ("gate_1_y", lambda t: t.replace("428.3047", "429.3047")),
    ("gate_z", lambda t: t.replace("23.54276", "24.54276")),
    ("gate_1_orient", lambda t: t.replace("3.141593 rad", "1.141593 rad")),
    ("gate_2_x", lambda t: t.replace("-10774.61", "-10773.61")),
    ("gate_2_y", lambda t: t.replace("431.2383", "432.2383")),
    ("gate_gap_start", lambda t: t.replace("4.4 units", "5.4 units")),
    ("gate_gap", lambda t: t.replace("120.3 units", "130.3 units")),
    ("triggers", lambda t: t.replace("8451 and 8452", "8453 and 8454")),
    ("gate_sill", lambda t: t.replace("0.876 units below",
                                      "1.876 units below")),
    ("pillar_count", lambda t: t.replace("Pillar count: 4",
                                         "Pillar count: 6")),
    ("pillar_verified", lambda t: t.replace("Pillar positions: unverified",
                                            "Pillar positions: verified")),
    ("los_claim", lambda t: t.replace("spawns no LoS object",
                                      "spawns one LoS object")),
    ("orb_axis", lambda t: t.replace("91.5 units apart along Y",
                                     "81.5 units apart along Y")),
    ("level_claim", lambda t: t.replace("Single level", "Two levels")),
    ("spread", lambda t: t.replace("0.876 units", "1.876 units")),
    ("flat_floor", lambda t: t.replace("0.0073 units", "0.0173 units")),
    ("buff_a_id", lambda t: t.replace("GO 184663", "GO 184665")),
    ("buff_b_id", lambda t: t.replace("GO 184664", "GO 184666")),
    ("buff_a_x", lambda t: t.replace("-10717.63", "-10716.63")),
    ("buff_a_y", lambda t: t.replace("383.8223", "384.8223")),
    ("buff_a_z", lambda t: t.replace("24.412825", "25.412825")),
    ("buff_b_x", lambda t: t.replace("-10716.6", "-10715.6")),
    ("buff_b_y", lambda t: t.replace("475.364", "476.364")),
    ("buff_b_z", lambda t: t.replace("24.4131", "25.4131")),
    ("buff_dist", lambda t: t.replace("45.8 units", "55.8 units")),
    ("buff_a_orient", lambda t: t.replace("Orientation: 1.555 rad",
                                          "Orientation: 2.555 rad")),
    ("orb_z_level", lambda t: t.replace("to within 0.0003 units",
                                        "to within 0.0030 units")),
    ("nagrand_orb_gap", lambda t: t.replace("orbs sit 108.9 apart",
                                            "orbs sit 109.9 apart")),
    ("buff_gap", lambda t: t.replace("91.5 units apart", "101.5 units apart")),
    ("spawn", lambda t: t.replace("Spawn: 60 s after the gates open",
                                  "Spawn: 90 s after the gates open")),
    ("wiki_delay", lambda t: t.replace("wiki quotes 90 s",
                                       "wiki quotes 120 s")),
    ("battlemaster_reintroduced", lambda t: t.replace(
        "AreaTable zone: 6296",
        "AreaTable zone: 6296\n  BattlemasterList id 6 carries map 980")),
    ("respawn", lambda t: t.replace("Respawn after pickup: 120 s",
                                    "Respawn after pickup: 180 s")),
    ("spell", lambda t: t.replace("34709", "34710")),
    ("spell_dmg", lambda t: t.replace("+5% damage taken",
                                      "+10% damage taken")),
    ("pickup_claim", lambda t: t.replace("No health, mana, haste",
                                         "Health, mana, haste")),
    ("object_count", lambda t: t.replace(
        "The core spawns exactly four objects",
        "The core spawns exactly five objects")),
    ("worldstate", lambda t: t.replace("Worldstate 0xE1A",
                                       "Worldstate 0xE1B")),
    ("dampening_date", lambda t: t.replace("2014-10-30", "2014-10-31")),
    ("unverified_removed", lambda t: t.replace("Unverified:", "Also verified:")),
    ("source_removed", lambda t: t.replace("Map_TolVirArena.lua",
                                           "Map_Other.lua")),
    ("width_inflate", lambda t: t.replace(
        "=== 2. GATES ===",
        "=== 2. GATES AND A GREAT DEAL OF ADDITIONAL TEXT THAT MAKES THIS LINE FAR TOO LONG ===")),
]


def derived_stage(text):
    def grab(pattern):
        m = re.search(pattern, text)
        if not m:
            raise RuntimeError("pattern not found: %s" % pattern)
        return float(m.group(1))

    t1x = grab(r"X: (-10649\.9)")
    t2x = grab(r"X: (-10778\.2)")
    t1y, t2y = 428.172, 430.875
    gx, gy = -10716.7, 429.295
    gox, goy = -10716.4, 429.233
    d1 = (-10654.3, 428.3047)
    d2 = (-10774.61, 431.2383)
    b1 = (-10717.63, 383.8223)
    b2 = (-10716.6, 475.364)

    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
    cx, cy = (t1x + t2x) / 2.0, (t1y + t2y) / 2.0

    checks = [
        ("start to start", dist((t1x, t1y), (t2x, t2y)),
         r"Distance start to start: (\d+\.\d+)"),
        ("start to centre", dist((t1x, t1y), (cx, cy)),
         r"Each start is (\d+\.\d+) units"),
        ("axis X", abs(t1x - t2x), r"(\d+\.\d+) apart on X"),
        ("axis Y", abs(t1y - t2y), r"(\d+\.\d+) apart on Y"),
        ("graveyard to centre", dist((gx, gy), (cx, cy)),
         r"Graveyard is (\d+\.\d+) units"),
        ("gameon to centre", dist((gox, goy), (cx, cy)),
         r"Game On target is (\d+\.\d+) units"),
        ("gate to gate", dist(d1, d2), r"Distance between the two gates: (\d+\.\d+)"),
        ("gate1 to start", dist(d1, (t1x, t1y)),
         r"Alliance start stands (\d+\.\d+) units"),
        ("gate2 to start", dist(d2, (t2x, t2y)),
         r"Horde start stands (\d+\.\d+) units"),
        ("orb A to centre", dist(b1, (cx, cy)),
         r"About (\d+\.\d+) units from the arena centre\n"),
        ("orb B to centre", dist(b2, (cx, cy)),
         r"About 45\.8 units from the arena centre[\s\S]*?About (\d+\.\d+) units"),
        ("orb to orb", dist(b1, b2),
         r"orbs are (\d+\.\d+) units apart and sit"),
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

    for deg_s in ("182.385", "0.332764"):
        m = re.search(re.escape(deg_s) + r" deg = ([\d.]+) rad", text)
        if not m:
            raise RuntimeError("radian claim missing for %s" % deg_s)
        want = float(m.group(1))
        places = len(m.group(1).split(".")[1])
        got = round(math.radians(float(deg_s)), places)
        mark = "ok " if abs(got - want) <= 1e-9 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %9.6f rad  recomputed %9.6f  %s"
                     % (deg_s + " deg", want, got, mark))

    # gate sill drop and floor flatness, both parsed from the document
    m = re.search(r"gates sit ([\d.]+) units below", text)
    if not m:
        raise RuntimeError("sill claim missing")
    want = float(m.group(1))
    got = round(24.419 - 23.54276, 3)
    mark = "ok " if abs(got - want) <= 0.001 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %9.3f      recomputed %9.3f  %s"
                 % ("gate sill drop", want, got, mark))

    m = re.search(r"flat to within ([\d.]+) units", text)
    if not m:
        raise RuntimeError("floor flatness claim missing")
    want = float(m.group(1))
    got = round(24.419 - 24.4117, 4)
    mark = "ok " if abs(got - want) <= 0.0002 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %9.4f      recomputed %9.4f  %s"
                 % ("floor flatness", want, got, mark))

    m = re.search(r"the arena floor to within (\d+\.\d+) units", text)
    if not m:
        raise RuntimeError("orb Z level claim missing")
    want = float(m.group(1))
    got = round(24.4131 - 24.412825, 4)
    mark = "ok " if abs(got - want) <= 0.00005 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %9.4f      recomputed %9.4f  %s"
                 % ("orb Z level", want, got, mark))

    m = re.search(r"Floor Z spans (\d+\.\d+) to (\d+\.\d+)", text)
    if not m:
        raise RuntimeError("floor span claim missing")
    span = round(float(m.group(2)) - float(m.group(1)), 3)
    m2 = re.search(r"That is a spread of (\d+\.\d+) units", text)
    want = float(m2.group(1))
    mark = "ok " if abs(span - want) <= 0.001 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %9.3f      recomputed %9.3f  %s"
                 % ("floor Z spread", want, span, mark))

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
    print("AUDIT: Arena_Tol_vir_Arena_COMPLETED.txt (Step 6)")
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
        "BattlegroundTVA.h": gh_content(TVA_REPO, TVA_H_PATH),
        "BattlegroundTVA.cpp": gh_content(TVA_REPO, TVA_PATH),
        "Map_TolVirArena.lua": gh_content(DM_REPO, DM_PATH),
        "battleground_template": gh_content(TPL_REPO, TPL_PATH),
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

    probes = {
        "distance changed": original.replace("128.3 units", "138.3 units"),
        "radians changed": original.replace("3.1832 rad", "1.1832 rad"),
        "sill changed": original.replace("0.876 units below",
                                         "1.876 units below"),
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

    print("\n[5] No-invented-coordinates trace")
    ok, lines, _ = coord_trace(original, corpora)
    for line in lines:
        print(line)
    if not ok:
        print("    INVENTED COORDINATES FOUND")
        return 1
    probe = original.replace("X: -10649.9", "X: -10639.9")
    if probe == original or coord_trace(probe, corpora)[0]:
        print("    trace did not react to an invented coordinate")
        return 1
    print("    trace reacts to an invented coordinate (verified)")

    print("\n" + "=" * 62)
    print("AUDIT RESULT: PASS")
    print("  static checks: %d/%d" % (passed, len(STATIC_CHECKS)))
    print("  mutations: %d/%d" % (detected, len(MUTATIONS)))
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
