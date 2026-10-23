#!/usr/bin/env python3
"""Mutation-tested audit for Arena_Blade_s_Edge_Arena_COMPLETED.txt (Step 2)."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import (gh_content, gh_gist, source_stage,
                          mutation_probe, coord_trace)

SQL_REPO = "TrinityCore/TrinityCore"
SQL_PATH = ("sql/old/8.x/world/19071_2020_06_17/"
            "2019_10_26_01_world.sql")
BEG_REPO = "HavenWoW/BFA-HavenCore"
BEG_PATH = ("src/server/game/Battlegrounds/Zones/"
            "BattlegroundBEG.cpp")
SD_REPO = "HavenWoW/BFA-HavenCore"
SD_PATH = "src/server/game/Miscellaneous/SharedDefines.h"

# (label, literal that must appear in the named upstream file)
SOURCE_TOKENS = {
    "world_safe_locs (8.x)": [
        ("ws 5816 x", "(5816,1672,2770.86,6061.61,-3.10842"),
        ("ws 5817", "(5817,1672,2803.76,5945.78,-3.09356"),
        ("ws 5804", "(5804,1672,2788.93,6003.73,4.94187"),
        ("ws 939", "(939,562,6292.66,288.579,4.95929"),
        ("ws 940", "(940,562,6184.98,236.011,4.97687"),
        ("ws 971", "(971,562,6236.97,262.649,2.73055"),
    ],
    "SharedDefines.h": [
        ("bg 844", "BATTLEGROUND_BEG            = 844"),
    ],
    "gist 4772221": [
        ("se pillar pt 1", "6236.567836f, 258.049106f, 11.500018f"),
        ("se pillar pt 2", "6235.567836f, 258.049106f, 11.500018f"),
        ("se pillar pt 3", "6230.818836f, 252.049106f, 11.500018f"),
        ("nw pillar pt 1", "6246.324219f, 271.570000f, 11.300000f"),
        ("nw pillar pt 2", "6242.942484f, 267.210030f, 11.280000f"),
        ("nw pillar pt 3", "6241.539484f, 265.441030f, 11.280000f"),
        ("map gate", "GetMapId() == 562"),
    ],
    "BattlegroundBEG.cpp": [
        ("door 265571", "265571"),
        ("door 265569", "265569"),
        ("door 1 pos", "2776.371f, 6055.702f, -3.733995f"),
        ("door 2 pos", "2797.014f, 5953.527f, -4.099238f"),
        ("buff 1 pos", "2815.306f, 5972.267f, -4.452f"),
        ("buff 2 pos", "2761.437f, 6038.106f, -3.49f"),
    ],
}

DELIVERABLE = ("/home/user/Junk/# Ai Research prompts/Arenas_complete/"
               "Arena_Blade_s_Edge_Arena_COMPLETED.txt")

STATIC_CHECKS = [
    ("file_exists", lambda t: os.path.exists(DELIVERABLE)),
    ("min_lines", lambda t: len(t.splitlines()) >= 180),
    ("max_width_78", lambda t: all(len(l) <= 78 for l in t.splitlines())),
    ("title_completed", lambda t: t.splitlines()[0].endswith("- COMPLETED ===")),
    ("title_map_1672", lambda t: "MAP 1672" in t.splitlines()[0]),

    ("map_1672", lambda t: "8.3.7 arena map ID: 1672" in t),
    ("dir_bladesedgearena2b", lambda t: "bladesedgearena2b" in t),
    ("instance_type_4", lambda t: "InstanceType: 4" in t),
    ("expansion_6", lambda t: "Expansion of this map row: 6" in t),
    ("bg_844", lambda t: 'Battleground entry used in 8.3.7: 844' in t),
    ("max_players_5", lambda t: "MaxPlayersPerTeam 5" in t),
    ("legacy_562", lambda t: "562 (directory bladesedgearena)" in t),

    ("ws_5816", lambda t: "WorldSafeLoc 5816" in t),
    ("ws_5817", lambda t: "WorldSafeLoc 5817" in t),
    ("ws_5804", lambda t: "WorldSafeLoc 5804" in t),
    ("ally_x", lambda t: "X: 2770.86" in t),
    ("ally_y", lambda t: "Y: 6061.61" in t),
    ("ally_z", lambda t: "Z: -3.10842" in t),
    ("horde_x", lambda t: "X: 2803.76" in t),
    ("horde_y", lambda t: "Y: 5945.78" in t),
    ("horde_z", lambda t: "Z: -3.09356" in t),
    ("ally_facing", lambda t: "311.741 deg = 5.4410 rad" in t),
    ("horde_facing", lambda t: "131.682 deg = 2.2983 rad" in t),
    ("gy_coords", lambda t: "2788.93" in t and "6003.73" in t),
    ("gy_z", lambda t: "4.94187" in t),
    ("gy_facing", lambda t: "322.842 deg = 5.6346 rad" in t),
    ("dist_starts", lambda t: "120.4 units" in t),
    ("centre", lambda t: "2787.31, 6003.69" in t),
    ("start_to_centre", lambda t: "60.2 units" in t),
    ("gy_above", lambda t: "8.0 units above" in t),

    ("door_265571", lambda t: "265571" in t),
    ("door_265569", lambda t: "265569" in t),
    ("door1_coords", lambda t: "2776.371" in t and "6055.702" in t),
    ("door1_z", lambda t: "-3.733995" in t),
    ("door2_coords", lambda t: "2797.014" in t and "5953.527" in t),
    ("door2_z", lambda t: "-4.099238" in t),
    ("door_gap", lambda t: "8.1 units" in t and "10.3 units" in t),
    ("triggers", lambda t: "4536 and 4537" in t),

    ("pillars_unverified", lambda t: "Pillar centre coordinates" in t),
    ("bridge_model", lambda t: "bridge" in t.lower()),
    ("pit", lambda t: "pit" in t.lower()),
    ("no_go_pillars", lambda t: "world model geometry, not game objects" in t),

    ("z_range", lambda t: "-4.5 to -3.0" in t),
    ("ramp_unverified", lambda t: "ramp count" in t.lower()),

    ("role_melee", lambda t: "Melee DPS:" in t),
    ("role_ranged", lambda t: "Ranged DPS:" in t),
    ("role_healer", lambda t: "Healers:" in t),

    ("buff_go_1", lambda t: "Shadow Sight A (GO 184663)" in t),
    ("buff_go_2", lambda t: "Shadow Sight B (GO 184664)" in t),
    ("buff1_coords", lambda t: "2815.306" in t and "5972.267" in t),
    ("buff1_z", lambda t: "-4.452" in t),
    ("buff2_coords", lambda t: "2761.437" in t and "6038.106" in t),
    ("buff2_z", lambda t: "-3.49" in t),
    ("buff_dist", lambda t: "42.1 units" in t and "43.1 units" in t),
    ("spawn_60", lambda t: "ARENA_COUNTDOWN_MAX = 60" in t),
    ("spell_34709", lambda t: "34709" in t),
    ("spell_15s", lambda t: "15 s" in t),
    ("dmg_5", lambda t: "+5% damage taken" in t),
    ("no_health_pickup", lambda t: "No health, mana, haste" in t),

    ("legacy_939", lambda t: "WorldSafeLoc 939" in t and "6292.66" in t),
    ("legacy_940", lambda t: "WorldSafeLoc 940" in t and "6184.98" in t),
    ("legacy_971", lambda t: "WorldSafeLoc 971" in t and "6236.97" in t),
    ("legacy_rope", lambda t: "6236.567836, 258.049106, 11.500018" in t),
    ("legacy_rope2", lambda t: "6230.818836, 252.049106, 11.500018" in t),
    ("legacy_rope3", lambda t: "6242.942484, 267.210030, 11.280000" in t),
    ("legacy_bridge_z", lambda t: "11.3-11.5" in t),
    ("legacy_warning", lambda t: "Do not use these numbers on map 1672" in t),

    ("sources", lambda t: "Sources:" in t),
    ("unverified", lambda t: "Unverified:" in t),
    ("src_haven", lambda t: "BattlegroundBEG" in t),
    ("src_datamine", lambda t: "Map_bladesedgearena2b.lua" in t),
    ("src_deg2rad", lambda t: "DegToRad" in t),
]

MUTATIONS = [
    ("map_id", lambda t: t.replace("8.3.7 arena map ID: 1672",
                                   "8.3.7 arena map ID: 1673")),
    ("map_dir", lambda t: t.replace("bladesedgearena2b", "bladesedgearena")),
    ("bg_entry", lambda t: t.replace("entry used in 8.3.7: 844",
                                     "entry used in 8.3.7: 845")),
    ("max_players", lambda t: t.replace("MaxPlayersPerTeam 5",
                                        "MaxPlayersPerTeam 10")),
    ("ws_alliance", lambda t: t.replace("WorldSafeLoc 5816",
                                        "WorldSafeLoc 5818")),
    ("ws_horde", lambda t: t.replace("WorldSafeLoc 5817",
                                     "WorldSafeLoc 5819")),
    ("ws_gy", lambda t: t.replace("WorldSafeLoc 5804",
                                  "WorldSafeLoc 5805")),
    ("ally_x", lambda t: t.replace("X: 2770.86", "X: 2771.86")),
    ("ally_y", lambda t: t.replace("Y: 6061.61", "Y: 6062.61")),
    ("ally_z", lambda t: t.replace("Z: -3.10842", "Z: -2.10842")),
    ("horde_x", lambda t: t.replace("X: 2803.76", "X: 2804.76")),
    ("horde_z", lambda t: t.replace("Z: -3.09356", "Z: -4.09356")),
    ("ally_facing", lambda t: t.replace("311.741 deg = 5.4410 rad",
                                        "311.741 deg = 1.4410 rad")),
    ("horde_facing", lambda t: t.replace("131.682 deg = 2.2983 rad",
                                         "131.682 deg = 4.2983 rad")),
    ("gy_coords", lambda t: t.replace("2788.93", "2789.93")),
    ("gy_z", lambda t: t.replace("4.94187", "5.94187")),
    ("dist", lambda t: t.replace("120.4 units", "130.4 units")),
    ("centre", lambda t: t.replace("2787.31, 6003.69", "2787.41, 6003.69")),
    ("start_to_centre", lambda t: t.replace("60.2 units", "66.2 units")),
    ("door1_id", lambda t: t.replace("265571", "265572")),
    ("door2_id", lambda t: t.replace("265569", "265570")),
    ("door1_x", lambda t: t.replace("2776.371", "2777.371")),
    ("door1_z", lambda t: t.replace("-3.733995", "-3.833995")),
    ("door2_y", lambda t: t.replace("5953.527", "5954.527")),
    ("door2_z", lambda t: t.replace("-4.099238", "-4.199238")),
    ("door_gap", lambda t: t.replace("8.1 units", "9.1 units")),
    ("triggers", lambda t: t.replace("4536 and 4537", "4538 and 4539")),
    ("pillar_verified_claim", lambda t: t.replace(
        "- Pillar centre coordinates", "- Pillar offsets")),
    ("z_range", lambda t: t.replace("-4.5 to -3.0", "-5.5 to -3.0")),
    ("buff1_go", lambda t: t.replace("GO 184663", "GO 184665")),
    ("buff2_go", lambda t: t.replace("GO 184664", "GO 184666")),
    ("buff1_x", lambda t: t.replace("2815.306", "2816.306")),
    ("buff1_z", lambda t: t.replace("-4.452", "-4.552")),
    ("buff2_y", lambda t: t.replace("6038.106", "6039.106")),
    ("buff_dist", lambda t: t.replace("42.1 units", "32.1 units")),
    ("countdown", lambda t: t.replace("ARENA_COUNTDOWN_MAX = 60",
                                      "ARENA_COUNTDOWN_MAX = 90")),
    ("spell", lambda t: t.replace("34709", "34710")),
    ("spell_dmg", lambda t: t.replace("+5% damage taken",
                                      "+10% damage taken")),
    ("pickup_claim", lambda t: t.replace("No health, mana, haste",
                                         "Health, mana, haste")),
    ("legacy_939", lambda t: t.replace("6292.66", "6293.66")),
    ("legacy_940", lambda t: t.replace("6184.98", "6185.98")),
    ("legacy_971", lambda t: t.replace("6236.97", "6237.97")),
    ("legacy_rope", lambda t: t.replace("6230.818836, 252.049106, 11.500018",
                                        "6230.818836, 253.049106, 11.500018")),
    ("legacy_bridge", lambda t: t.replace("11.3-11.5", "12.3-12.5")),
    ("legacy_warning_removed", lambda t: t.replace(
        "Do not use these numbers on map 1672", "Reference data")),
    ("unverified_removed", lambda t: t.replace("Unverified:", "Also verified:")),
    ("source_removed", lambda t: t.replace("DegToRad", "conversion")),
    ("width_inflate", lambda t: t.replace(
        "=== 2. GATES (map 1672) ===",
        "=== 2. GATES (map 1672) AND A GREAT DEAL OF ADDITIONAL TEXT THAT MAKES THIS LINE WAY TOO LONG ===")),
]


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
    print("AUDIT: Arena_Blade_s_Edge_Arena_COMPLETED.txt (Step 2)")
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
        "BattlegroundBEG.cpp": gh_content(BEG_REPO, BEG_PATH),
        "SharedDefines.h": gh_content(SD_REPO, SD_PATH),
        "gist 4772221": gh_gist("4772221", "gistfile1.diff"),
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
                text = text.replace(lit, lit[:-1] + ("9" if not lit.endswith("9")
                                                     else "8"))
        return text

    undetected = mutation_probe(corpora, SOURCE_TOKENS, break_literals)
    if undetected:
        print("    cross-check did not react to tampered source: %s"
              % undetected)
        return 1
    print("    cross-check reacts to tampered source (verified)")

    print("\n[4] No-invented-coordinates trace")
    ok, lines, _ = coord_trace(original, corpora)
    for line in lines:
        print(line)
    if not ok:
        print("    INVENTED COORDINATES FOUND")
        return 1
    if coord_trace(original.replace("6236.567836, 258.049106, 11.500018",
                                    "6237.567836, 258.049106, 11.500018"),
                   corpora)[0]:
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
