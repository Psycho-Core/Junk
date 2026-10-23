#!/usr/bin/env python3
"""Mutation-tested audit for Arena_Ashamane_s_Fall_COMPLETED.txt (Step 8)."""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import (gh_content, source_stage, mutation_probe,
                          coord_trace)

DELIVERABLE = ("/home/user/Junk/# Ai Research prompts/Arenas_complete/"
               "Arena_Ashamane_s_Fall_COMPLETED.txt")

SQL_REPO = "TrinityCore/TrinityCore"
SQL_PATH = ("sql/old/8.x/world/19071_2020_06_17/"
            "2019_10_26_01_world.sql")
AF_REPO = "HavenWoW/BFA-HavenCore"
AF_PATH = ("src/server/game/Battlegrounds/Zones/BattlegroundAF.cpp")
AF_H_PATH = ("src/server/game/Battlegrounds/Zones/BattlegroundAF.h")
BG_H_PATH = "src/server/game/Battlegrounds/Battleground.h"
BG_PATH = "src/server/game/Battlegrounds/Battleground.cpp"
DM_REPO = "Ghostopheles/Datamine"
DM_PATH = "Datamine_Maps/Generated/Map_ValsharahArena.lua"
TPL_REPO = "zTerragor/vSLDB"
TPL_PATH = "sql/updates/world/2021_11_03_world_Battleground_Template.sql"

SOURCE_TOKENS = {
    "world_safe_locs (8.x)": [
        ("ws 5306", "1552,3542.7,5538.14,324.235,0.00848389"),
        ("ws 5307", "1552,3539.43,5472.07,325.436,88.5499"),
        ("ws 5308", "1552,3548.62,5601.11,325.227,268.325"),
    ],
    "battleground_template": [
        ("bg 816 row", "(816, 0, 5, 90, 120, 5307, 5308, 0, 1, '', "
                      "'Arena Ashamanes Fall')"),
    ],
    "BattlegroundAF.h": [
        ("door 250431", "BG_AF_OBJECT_TYPE_DOOR_1 = 250431"),
        ("door 250430", "BG_AF_OBJECT_TYPE_DOOR_2 = 250430"),
        ("buff 184663", "BG_AF_OBJECT_TYPE_BUFF_1 = 184663"),
        ("buff 184664", "BG_AF_OBJECT_TYPE_BUFF_2 = 184664"),
    ],
    "BattlegroundAF.cpp": [
        ("door 1 pos", "3548.0f, 5585.18f, 323.617f, 4.78249f"),
        ("door 2 pos", "3540.02f, 5487.5f, 323.943f, 1.59691f"),
        ("buff A pos", "3504.79f, 5499.64f, 325.824f, 0.822952f"),
        ("buff B pos", "3574.51f, 5576.24f, 326.795f, 4.08236f"),
        ("buff B rot", "0.0f, 0.70068f, -0.0f, 120"),
        ("worldstate", "0xE1A, 1"),
        ("triggers", "case 4536"),
        ("spawn", "SpawnBGObject(i, 60)"),
    ],
    "Battleground.cpp": [
        ("unused respawn param",
         "float rotation3, uint32 /*respawnTime*/, GOState goState)"),
        ("zeroed fallback", "!rotation0 && !rotation1 && !rotation2 && !rotation3"),
        ("quaternion", "QuaternionData rot(rotation0, rotation1, rotation2, rotation3)"),
    ],
    "Battleground.h": [
        ("respawn immediately", "RESPAWN_IMMEDIATELY             = 0"),
        ("signature", "float rotation3, uint32 respawnTime = 0"),
    ],
    "Map_ValsharahArena.lua": [
        ("map name", 'MapName = "Ashamane\'s Fall"'),
        ("map id", "MapID = 1552"),
        ("directory", "Directory = [[ValsharahArena]]"),
        ("instance type", "InstanceType = 4"),
        ("expansion", "ExpansionID = 6"),
        ("wdt", "WDTFileDataID: 1309335"),
    ],
}

STATIC_CHECKS = [
    ("file_exists", lambda t: os.path.exists(DELIVERABLE)),
    ("min_lines", lambda t: len(t.splitlines()) >= 200),
    ("max_width_78", lambda t: all(len(l) <= 78 for l in t.splitlines())),
    ("title_completed",
     lambda t: t.splitlines()[0].endswith("- COMPLETED ===")),
    ("title_map_1552", lambda t: "MAP 1552" in t.splitlines()[0]),

    ("map_1552", lambda t: "Arena map ID: 1552" in t),
    ("dir", lambda t: "Map.dbc directory: ValsharahArena" in t),
    ("instance_type_4", lambda t: "InstanceType: 4" in t),
    ("zone_8008", lambda t: "AreaTable zone: 8008" in t),
    ("zone_outer", lambda t: "outer Val'sharah zone is 8164" in t),
    ("expansion_field_6", lambda t: "ExpansionID field in the map row: 6" in t),
    ("wdt", lambda t: "1309335" in t),
    ("no_legacy", lambda t: "No legacy duplicate" in t),
    ("bg_816", lambda t: 'Battleground entry: 816 "Arena Ashamanes Fall"'
                         in t),
    ("max_players_5", lambda t: "MaxPlayersPerTeam 5" in t),
    ("lvl_90_120", lambda t: "MinLvl 90, MaxLvl 120" in t),
    ("start_max_dist_0", lambda t: "StartMaxDist 0" in t),
    ("weight_1", lambda t: "Weight 1" in t),
    ("patch_703", lambda t: "patch 7.0.3" in t),
    ("eighth", lambda t: "Eighth arena map, counting" in t),
    ("go_facing", lambda t: "Facing: 0.00848389 deg = 0.000148 rad" in t),
    ("location", lambda t: "Location: Val'sharah" in t),

    ("ws_5307", lambda t: "WorldSafeLoc 5307" in t),
    ("ws_5308", lambda t: "WorldSafeLoc 5308" in t),
    ("ws_5306", lambda t: "WorldSafeLoc 5306" in t),
    ("t1_x", lambda t: "X: 3539.43" in t),
    ("t1_y", lambda t: "Y: 5472.07" in t),
    ("t1_z", lambda t: "Z: 325.436" in t),
    ("t1_facing", lambda t: "88.5499 deg = 1.5455 rad" in t),
    ("t2_x", lambda t: "X: 3548.62" in t),
    ("t2_y", lambda t: "Y: 5601.11" in t),
    ("t2_z", lambda t: "Z: 325.227" in t),
    ("t2_facing", lambda t: "268.325 deg = 4.6832 rad" in t),
    ("go_x", lambda t: "X: 3542.7" in t),
    ("go_y", lambda t: "Y: 5538.14" in t),
    ("go_z", lambda t: "Z: 324.235" in t),
    ("no_gy_row", lambda t: "No arena graveyard row exists on map 1552" in t),
    ("dist_starts", lambda t: "129.37 units" in t),
    ("centre", lambda t: "about 3544.02, 5536.59" in t),
    ("half", lambda t: "64.68 units" in t),
    ("axis_y", lambda t: "129.04 apart on Y" in t),
    ("axis_x", lambda t: "129.04 apart on Y, 9.19 apart on X" in t),
    ("skew", lambda t: "4.07 degrees off a clean Y line" in t),
    ("facing_gap", lambda t: "180 degrees apart to within 0.22" in t),
    ("go_to_centre", lambda t: "2.04 units" in t),

    ("door_ids", lambda t: "GO 250430" in t and "GO 250431" in t),
    ("g1_x", lambda t: "X: 3540.02" in t),
    ("g1_y", lambda t: "Y: 5487.5" in t),
    ("g1_z", lambda t: "Z: 323.943" in t),
    ("g1_orient", lambda t: "Orientation: 1.59691 rad" in t),
    ("g2_x", lambda t: "X: 3548.0" in t),
    ("g2_y", lambda t: "Y: 5585.18" in t),
    ("g2_z", lambda t: "Z: 323.617" in t),
    ("g2_orient", lambda t: "Orientation: 4.78249 rad" in t),
    ("rot_zero", lambda t: t.count("Rotation passed to the core: 0.0, 0.0, 0.0") == 2),
    ("gate_gap", lambda t: "98.01 units" in t),
    ("gate_start", lambda t: "15.44 units" in t and "15.94 units" in t),
    ("gate_far", lambda t: "113.4 to 113.9 units" in t),
    ("gate_narrower", lambda t: "98.01 against\n129.37" in t),
    ("gate_below", lambda t: "1.493 and 1.610" in t),
    ("pivot_unverified", lambda t: "pivot sits is unverified" in t),
    ("triggers", lambda t: "4536 and 4537" in t),

    ("pillars_three", lambda t: "Pillar count: 3" in t),
    ("liq_quote", lambda t: "two square\n   pillars and a rectangular pillar" in t),
    ("mod_quote", lambda t: "closer than the Tol'viron Pillars" in t),
    ("namu_quote", lambda t: "thick bushes on the outside" in t),
    ("pillar_disagree", lambda t: "not fully agree on placement" in t),
    ("pillars_unverified", lambda t: "Pillar positions, size and shape: unverified" in t),
    ("one_rect", lambda t: "Only one of the three is rectangular" in t),
    ("four_objects", lambda t: "exactly four\n  objects" in t or "exactly four objects" in t),

    ("one_level", lambda t: "One main level." in t),
    ("z_spread", lambda t: "3.178 units" in t),
    ("spawn_z_gap", lambda t: "0.209 units" in t),
    ("no_ramp", lambda t: "Ramps: unverified" in t),
    ("orb_rise", lambda t: "1.359" in t and "0.388" in t),

    ("role_melee", lambda t: "Melee DPS:" in t),
    ("role_ranged", lambda t: "Ranged DPS:" in t),
    ("role_healer", lambda t: "Healers:" in t),
    ("gate_narrow_claim", lambda t: "31.36 units narrower" in t),

    ("buff_a_id", lambda t: "Shadow Sight A (GO 184663)" in t),
    ("buff_b_id", lambda t: "Shadow Sight B (GO 184664)" in t),
    ("buff_a_x", lambda t: "X: 3504.79" in t),
    ("buff_a_y", lambda t: "Y: 5499.64" in t),
    ("buff_a_z", lambda t: "Z: 325.824" in t),
    ("buff_a_orient", lambda t: "Orientation: 0.822952 rad" in t),
    ("buff_b_x", lambda t: "X: 3574.51" in t),
    ("buff_b_y", lambda t: "Y: 5576.24" in t),
    ("buff_b_z", lambda t: "Z: 326.795" in t),
    ("buff_b_orient", lambda t: "Orientation: 4.08236 rad" in t),
    ("buff_dists", lambda t: "53.90 units" in t and "50.01 units" in t),
    ("buff_gap", lambda t: "103.58 units" in t),
    ("buff_asym", lambda t: "a difference of 3.88 units" in t),
    ("spawn_60", lambda t: "Spawn: 60 s after the gates open" in t),
    ("spell", lambda t: "34709" in t),
    ("spell_dmg", lambda t: "+5% damage taken" in t),
    ("wiki_90s", lambda t: "wiki quotes 90 s" in t),
    ("respawn_unverified", lambda t: "Respawn after pickup: unverified" in t),
    ("no_health", lambda t: "No health, mana, haste" in t),

    ("worldstate", lambda t: "Worldstate 0xE1A" in t),
    ("no_oob", lambda t: "No out-of-bounds or under-map return points" in t),
    ("defect_misaligned", lambda t: "misaligned by\none" in t),
    ("defect_quat", lambda t: "0, 0, 0, 120" in t),
    ("defect_fallback", lambda t: "zeroed-rotation\n    fallback" in t),
    ("defect_cosmetic", lambda t: "cosmetic on the orbs" in t),

    ("sources", lambda t: "Sources:" in t),
    ("unverified", lambda t: "Unverified:" in t),
    ("src_af", lambda t: "BattlegroundAF.cpp" in t),
    ("src_datamine", lambda t: "Map_ValsharahArena.lua" in t),
    ("src_wiki", lambda t: 'Warcraft Wiki "Ashamane\'s Fall"' in t),
    ("src_liquipedia", lambda t: 'Liquipedia "Ashamane\'s Fall"' in t),
    ("src_mod", lambda t: "Ministry of Defense arena guide" in t),
    ("src_namu", lambda t: "NamuWiki arena page" in t),
]

MUTATIONS = [
    ("map_id", lambda t: t.replace("Arena map ID: 1552", "Arena map ID: 1553")),
    ("directory", lambda t: t.replace("ValsharahArena", "ValsharahArena2")),
    ("zone", lambda t: t.replace("AreaTable zone: 8008",
                                 "AreaTable zone: 8009")),
    ("outer_zone", lambda t: t.replace("zone is 8164", "zone is 8165")),
    ("expansion_field", lambda t: t.replace("map row: 6", "map row: 7")),
    ("wdt", lambda t: t.replace("1309335", "1309336")),
    ("bg_entry", lambda t: t.replace('Battleground entry: 816',
                                     'Battleground entry: 817')),
    ("max_players", lambda t: t.replace("MaxPlayersPerTeam 5",
                                        "MaxPlayersPerTeam 10")),
    ("levels", lambda t: t.replace("MinLvl 90, MaxLvl 120",
                                   "MinLvl 10, MaxLvl 120")),
    ("start_max_dist", lambda t: t.replace("StartMaxDist 0",
                                           "StartMaxDist 10")),
    ("weight", lambda t: t.replace("Weight 1", "Weight 0")),
    ("patch", lambda t: t.replace("patch 7.0.3", "patch 7.0.4")),
    ("eighth", lambda t: t.replace("Eighth arena map", "Ninth arena map")),
    ("go_facing", lambda t: t.replace("0.00848389 deg = 0.000148 rad",
                                      "0.00848389 deg = 0.001148 rad")),
    ("ws_ally", lambda t: t.replace("WorldSafeLoc 5307",
                                    "WorldSafeLoc 5317")),
    ("ws_horde", lambda t: t.replace("WorldSafeLoc 5308",
                                     "WorldSafeLoc 5318")),
    ("ws_go", lambda t: t.replace("WorldSafeLoc 5306",
                                  "WorldSafeLoc 5316")),
    ("t1_x", lambda t: t.replace("X: 3539.43", "X: 3540.43")),
    ("t1_y", lambda t: t.replace("Y: 5472.07", "Y: 5473.07")),
    ("t1_z", lambda t: t.replace("Z: 325.436", "Z: 326.436")),
    ("t1_facing", lambda t: t.replace("88.5499 deg = 1.5455 rad",
                                      "88.5499 deg = 2.5455 rad")),
    ("t2_x", lambda t: t.replace("X: 3548.62", "X: 3549.62")),
    ("t2_y", lambda t: t.replace("Y: 5601.11", "Y: 5602.11")),
    ("t2_z", lambda t: t.replace("Z: 325.227", "Z: 326.227")),
    ("t2_facing", lambda t: t.replace("268.325 deg = 4.6832 rad",
                                      "268.325 deg = 3.6832 rad")),
    ("go_x", lambda t: t.replace("X: 3542.7", "X: 3543.7")),
    ("go_y", lambda t: t.replace("Y: 5538.14", "Y: 5539.14")),
    ("go_z", lambda t: t.replace("Z: 324.235", "Z: 325.235")),
    ("gy_claim", lambda t: t.replace("No arena graveyard row exists",
                                     "An arena graveyard row exists")),
    ("dist", lambda t: t.replace("129.37 units", "139.37 units")),
    ("centre", lambda t: t.replace("about 3544.02, 5536.59",
                                   "about 3544.12, 5536.59")),
    ("half", lambda t: t.replace("64.68 units", "74.68 units")),
    ("axis_y", lambda t: t.replace("129.04 apart on Y", "130.04 apart on Y")),
    ("axis_x", lambda t: t.replace("on Y, 9.19 apart on X",
                                    "on Y, 19.19 apart on X")),
    ("skew", lambda t: t.replace("4.07 degrees", "5.07 degrees")),
    ("facing_gap", lambda t: t.replace("within 0.22", "within 0.42")),
    ("door_ids", lambda t: t.replace("GO 250430", "GO 250432")),
    ("g1_x", lambda t: t.replace("X: 3540.02", "X: 3541.02")),
    ("g1_y", lambda t: t.replace("Y: 5487.5", "Y: 5488.5")),
    ("g1_z", lambda t: t.replace("Z: 323.943", "Z: 324.943")),
    ("g1_orient", lambda t: t.replace("Orientation: 1.59691 rad",
                                      "Orientation: 2.59691 rad")),
    ("g2_x", lambda t: t.replace("X: 3548.0", "X: 3549.0")),
    ("g2_y", lambda t: t.replace("Y: 5585.18", "Y: 5586.18")),
    ("g2_z", lambda t: t.replace("Z: 323.617", "Z: 324.617")),
    ("g2_orient", lambda t: t.replace("Orientation: 4.78249 rad",
                                      "Orientation: 3.78249 rad")),
    ("rot_zero", lambda t: t.replace("Rotation passed to the core: 0.0, 0.0, 0.0",
                                     "Rotation passed to the core: 0.0, 0.0, 1.0", 1)),
    ("gate_gap", lambda t: t.replace("98.01 units", "99.01 units")),
    ("gate_start", lambda t: t.replace("15.44 units", "16.44 units")),
    ("gate_far", lambda t: t.replace("113.4 to 113.9 units",
                                     "114.4 to 113.9 units")),
    ("gate_narrower", lambda t: t.replace("98.01 against\n129.37",
                                          "99.01 against\n129.37")),
    ("gate_below", lambda t: t.replace("1.493 and 1.610",
                                       "1.493 and 1.710")),
    ("triggers", lambda t: t.replace("4536 and 4537", "4538 and 4539")),
    ("pillar_count", lambda t: t.replace("Pillar count: 3",
                                         "Pillar count: 4")),
    ("pillars_verified", lambda t: t.replace(
        "Pillar positions, size and shape: unverified",
        "Pillar positions, size and shape: verified")),
    ("rectangle_claim", lambda t: t.replace("one of the three is rectangular",
                                            "all three are rectangular")),
    ("objects", lambda t: t.replace("exactly four", "exactly five")),
    ("levels_claim", lambda t: t.replace("One main level.", "Two main levels.")),
    ("z_spread", lambda t: t.replace("3.178 units", "4.178 units")),
    ("spawn_z_gap", lambda t: t.replace("0.209 units", "0.309 units")),
    ("ramp_claim", lambda t: t.replace("Ramps: unverified", "Ramps: verified")),
    ("orb_rise", lambda t: t.replace("1.359", "1.459")),
    ("gate_narrow_claim", lambda t: t.replace("31.36 units narrower",
                                              "32.36 units narrower")),
    ("buff_a_id", lambda t: t.replace("GO 184663", "GO 184665")),
    ("buff_b_id", lambda t: t.replace("GO 184664", "GO 184666")),
    ("buff_a_x", lambda t: t.replace("X: 3504.79", "X: 3505.79")),
    ("buff_a_y", lambda t: t.replace("Y: 5499.64", "Y: 5500.64")),
    ("buff_a_z", lambda t: t.replace("Z: 325.824", "Z: 326.824")),
    ("buff_a_orient", lambda t: t.replace("Orientation: 0.822952 rad",
                                          "Orientation: 1.822952 rad")),
    ("buff_b_x", lambda t: t.replace("X: 3574.51", "X: 3575.51")),
    ("buff_b_y", lambda t: t.replace("Y: 5576.24", "Y: 5577.24")),
    ("buff_b_z", lambda t: t.replace("Z: 326.795", "Z: 327.795")),
    ("buff_b_orient", lambda t: t.replace("Orientation: 4.08236 rad",
                                          "Orientation: 3.08236 rad")),
    ("buff_dist", lambda t: t.replace("53.90 units", "54.90 units")),
    ("buff_gap", lambda t: t.replace("103.58 units", "104.58 units")),
    ("buff_asym", lambda t: t.replace("a difference of 3.88 units",
                                      "a difference of 4.89 units")),
    ("spawn", lambda t: t.replace("Spawn: 60 s after the gates open",
                                  "Spawn: 90 s after the gates open")),
    ("spell", lambda t: t.replace("34709", "34708")),
    ("spell_dmg", lambda t: t.replace("+5% damage taken",
                                      "+10% damage taken")),
    ("wiki_delay", lambda t: t.replace("wiki quotes 90 s",
                                       "wiki quotes 120 s")),
    ("respawn_claim", lambda t: t.replace("Respawn after pickup: unverified",
                                          "Respawn after pickup: 120 s")),
    ("pickup_claim", lambda t: t.replace("No health, mana, haste",
                                         "Health, mana, haste")),
    ("worldstate", lambda t: t.replace("Worldstate 0xE1A",
                                       "Worldstate 0xE1B")),
    ("quat_claim", lambda t: t.replace("0, 0, 0, 120", "0, 0, 0, 60")),
    ("fallback_claim", lambda t: t.replace("zeroed-rotation",
                                           "null-rotation")),
    ("width_inflate", lambda t: t.replace(
        "=== 2. GATES ===",
        "=== 2. GATES AND A GREAT DEAL OF ADDITIONAL TEXT THAT MAKES THIS LINE FAR TOO LONG ===")),
]


def absence_stage(text, corpora):
    """Verify the document's negative and count claims against the data.

    An audit that only checks what the document says cannot catch a
    wrong absence claim; these have to be recomputed from the corpus.
    """
    sql = corpora["world_safe_locs (8.x)"]
    afc = corpora["BattlegroundAF.cpp"]
    lines, ok = [], True

    rows = [ln for ln in sql.splitlines() if re.search(r"\(\d+,1552,", ln)]
    want_rows = 3 if "No arena graveyard row exists on map 1552" in text else 4
    mark = "ok " if len(rows) == want_rows else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-32s claim %d  found %d  %s"
                 % ("graveyard rows on 1552", want_rows, len(rows), mark))

    gy = [ln for ln in rows if "Graveyard" in ln]
    wants_none = "No arena graveyard row exists on map 1552" in text
    mark = "ok " if (not gy) == wants_none else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-32s %-22s %s"
                 % ("any graveyard comment", "none expected" if wants_none
                    else "at least one expected", mark))

    objs = afc.count("AddObject(")
    want_objs = 4 if "exactly four" in text else 5
    mark = "ok " if objs == want_objs else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-32s claim %d  found %d  %s"
                 % ("AddObject calls in zone", want_objs, objs, mark))

    return ok, lines


def derived_stage(text):
    def grab(pattern):
        m = re.search(pattern, text)
        if not m:
            raise RuntimeError("pattern not found: %s" % pattern)
        return float(m.group(1))

    t1x = grab(r"X: (3539\.43)")
    t2x = grab(r"X: (3548\.62)")
    t1y, t2y = 5472.07, 5601.11
    gox, goy = 3542.7, 5538.14
    d1 = (3548.0, 5585.18)
    d2 = (3540.02, 5487.5)
    b1 = (3504.79, 5499.64)
    b2 = (3574.51, 5576.24)

    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
    cx, cy = (t1x + t2x) / 2.0, (t1y + t2y) / 2.0

    checks = [
        ("start to start", dist((t1x, t1y), (t2x, t2y)),
         r"Distance start to start: (\d+\.\d+)"),
        ("start to centre", dist((t1x, t1y), (cx, cy)),
         r"Each start is (\d+\.\d+) units"),
        ("axis Y", abs(t1y - t2y), r"(\d+\.\d+) apart on Y"),
        ("axis X", abs(t1x - t2x), r"(\d+\.\d+) apart on X"),
        ("gameon to centre", dist((gox, goy), (cx, cy)),
         r"Game On target is (\d+\.\d+) units"),
        ("gate to gate", dist(d1, d2),
         r"Distance between the two gates: (\d+\.\d+)"),
        ("gate1 to start", dist(d1, (t2x, t2y)),
         r"Team 2 start stands (\d+\.\d+) units"),
        ("gate2 to start", dist(d2, (t1x, t1y)),
         r"Team 1 start stands (\d+\.\d+) units"),
        ("orb A to centre", dist(b1, (cx, cy)),
         r"About (\d+\.\d+) units from the arena centre\n\nShadow Sight B"),
        ("orb B to centre", dist(b2, (cx, cy)),
         r"About 53\.90 units from the arena centre[\s\S]*?About (\d+\.\d+) units"),
        ("orb to orb", dist(b1, b2),
         r"orbs are (\d+\.\d+) units apart"),
    ]

    lines, ok = [], True
    for label, value, pattern in checks:
        got = round(value, 2)
        want = grab(pattern)
        mark = "ok " if abs(got - want) <= 0.01 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %8.2f  recomputed %8.2f  %s"
                     % (label, want, got, mark))

    for deg_s in ("88.5499", "268.325", "0.00848389"):
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

    m = re.search(r"Arena centre: about (-?\d+\.\d+), (-?\d+\.\d+)", text)
    if not m:
        raise RuntimeError("centre claim missing")
    for label, want, got in (("centre X", float(m.group(1)), cx),
                             ("centre Y", float(m.group(2)), cy)):
        mark = "ok " if abs(got - want) <= 0.01 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %9.2f      recomputed %9.2f  %s"
                     % (label, want, got, mark))

    # axis skew in degrees, from the two parsed start X values
    got_skew = round(math.degrees(math.atan2(abs(t1x - t2x),
                                             abs(t1y - t2y))), 2)
    want_skew = grab(r"(\d+\.\d+) degrees off a clean Y line")
    mark = "ok " if abs(got_skew - want_skew) <= 0.01 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.2f      recomputed %8.2f  %s"
                 % ("axis skew", want_skew, got_skew, mark))

    # full Z spread across the seven stated Z values
    zs = [323.617, 324.235, 323.943, 325.227, 325.436, 325.824, 326.795]
    want_spread = grab(r"Full spread across all seven points: (\d+\.\d+)")
    got_spread = round(max(zs) - min(zs), 3)
    mark = "ok " if abs(got_spread - want_spread) <= 0.001 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.3f      recomputed %8.3f  %s"
                 % ("Z spread", want_spread, got_spread, mark))

    want_gap = grab(r"two spawn floors differ by (\d+\.\d+)")
    got_gap = round(325.436 - 325.227, 3)
    mark = "ok " if abs(got_gap - want_gap) <= 0.001 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.3f      recomputed %8.3f  %s"
                 % ("spawn Z gap", want_gap, got_gap, mark))

    want_narrow = grab(r"(\d+\.\d+) units narrower than the spawn line")
    got_narrow = round(dist((t1x, t1y), (t2x, t2y)) - dist(d1, d2), 2)
    mark = "ok " if abs(got_narrow - want_narrow) <= 0.01 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.2f      recomputed %8.2f  %s"
                 % ("gate narrowing", want_narrow, got_narrow, mark))

    want_asym = grab(r"a difference of (\d+\.\d+) units")
    got_asym = round(abs(dist(b1, (cx, cy)) - dist(b2, (cx, cy))), 2)
    mark = "ok " if abs(got_asym - want_asym) <= 0.01 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.2f      recomputed %8.2f  %s"
                 % ("orb asymmetry", want_asym, got_asym, mark))

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
    print("AUDIT: Arena_Ashamane_s_Fall_COMPLETED.txt (Step 8)")
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
        "battleground_template": gh_content(TPL_REPO, TPL_PATH),
        "BattlegroundAF.h": gh_content(AF_REPO, AF_H_PATH),
        "BattlegroundAF.cpp": gh_content(AF_REPO, AF_PATH),
        "Battleground.cpp": gh_content(AF_REPO, BG_PATH),
        "Battleground.h": gh_content(AF_REPO, BG_H_PATH),
        "Map_ValsharahArena.lua": gh_content(DM_REPO, DM_PATH),
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
        "distance changed": original.replace("129.37 units", "139.37 units"),
        "radians changed": original.replace("1.5455 rad", "2.5455 rad"),
        "skew changed": original.replace("4.07 degrees", "5.07 degrees"),
        "spread changed": original.replace("3.178 units", "4.178 units"),
        "centre changed": original.replace("about 3544.02, 5536.59",
                                           "about 3544.12, 5536.59"),
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

    print("\n[5] Absence and count claims checked against the data")
    ok, lines = absence_stage(original, corpora)
    for line in lines:
        print(line)
    if not ok:
        print("    ABSENCE CLAIMS DO NOT MATCH THE DATA")
        return 1

    sql_broken = corpora["world_safe_locs (8.x)"].replace(
        "(5306,1552,",
        "(5316,1552,0,0,0,0,'Arena - Val\\'sharah - Graveyard'),\n(5306,1552,")
    afc_broken = corpora["BattlegroundAF.cpp"].replace("AddObject(", "NoObject(")
    probe_corpora = dict(corpora)
    probe_corpora["world_safe_locs (8.x)"] = sql_broken
    probe_corpora["BattlegroundAF.cpp"] = afc_broken
    if absence_stage(original, probe_corpora)[0]:
        print("    absence stage did not react to changed data")
        return 1
    print("    absence stage reacts to changed data (verified)")

    print("\n[6] No-invented-coordinates trace")
    ok, lines, _ = coord_trace(original, corpora)
    for line in lines:
        print(line)
    if not ok:
        print("    INVENTED COORDINATES FOUND")
        return 1
    probe = original.replace("X: 3539.43", "X: 3509.43")
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
