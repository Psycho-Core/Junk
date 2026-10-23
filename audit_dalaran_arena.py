#!/usr/bin/env python3
"""Mutation-tested audit for Arena_Dalaran_Arena_COMPLETED.txt (Step 3)."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import (gh_content, source_stage,
                          mutation_probe, coord_trace)

SQL_REPO = "TrinityCore/TrinityCore"
SQL_PATH = ("sql/old/8.x/world/19071_2020_06_17/"
            "2019_10_26_01_world.sql")
DS_REPO = "HavenWoW/BFA-HavenCore"
DS_PATH = ("src/server/game/Battlegrounds/Zones/"
           "BattlegroundDS.cpp")
DS_H_PATH = ("src/server/game/Battlegrounds/Zones/"
             "BattlegroundDS.h")
AC_REPO = "azerothcore/azerothcore-wotlk"
AC_PATH = ("src/server/game/Battlegrounds/Zones/"
           "BattlegroundDS.cpp")

SOURCE_TOKENS = {
    "world_safe_locs (8.x)": [
        ("ws 1362", "(1362,617,1218.01,764.795,14.7297"),
        ("ws 1363", "(1363,617,1361.76,817.337,14.8449"),
        ("ws 1361", "(1361,617,1292.14,790.993,8.11463"),
    ],
    "BattlegroundDS.h": [
        ("door 192642", "192642"),
        ("door 192643", "192643"),
    ],
    "BattlegroundDS.cpp": [
        ("door 1 pos", "1350.95f, 817.2f, 20.8096f, 3.15f"),
        ("door 2 pos", "1232.65f, 764.913f, 20.0729f, 6.3f"),
        ("water pos", "1291.56f, 790.837f, 7.1f"),
        ("buff 1 pos", "1291.7f, 813.424f, 7.11472f"),
        ("buff 2 pos", "1291.7f, 768.911f, 7.11472f"),
        ("spout low", "1212.833f, 765.3871f, 16.09484f"),
        ("spout high", "1369.977f, 817.2882f, 16.08718f"),
    ],
}

DELIVERABLE = ("/home/user/Junk/# Ai Research prompts/Arenas_complete/"
               "Arena_Dalaran_Arena_COMPLETED.txt")

STATIC_CHECKS = [
    ("file_exists", lambda t: os.path.exists(DELIVERABLE)),
    ("non_empty", lambda t: len(t.strip()) > 0),
    ("min_lines", lambda t: len(t.splitlines()) >= 140),
    ("max_width_78", lambda t: all(len(l) <= 78 for l in t.splitlines())),
    ("title_completed", lambda t: "COMPLETED ===" in t.splitlines()[0]),

    ("sec_start", lambda t: "START POSITIONS" in t.upper()),
    ("sec_pipes", lambda t: "ENTRANCE PIPES" in t.upper()),
    ("sec_los", lambda t: "PILLARS AND LINE OF SIGHT" in t.upper()),
    ("sec_heights", lambda t: "HEIGHT LEVELS AND RAMPS" in t.upper()),
    ("sec_roles", lambda t: "FIRST POSITIONS BY ROLE" in t.upper()),
    ("sec_pickups", lambda t: "BUFF / HEALTH PICKUPS" in t.upper()),
    ("sec_notes", lambda t: "ADDITIONAL NOTES" in t.upper()),
    ("sec_sources", lambda t: "SOURCES:" in t.upper()),
    ("sec_unverified", lambda t: "UNVERIFIED:" in t.upper()),
    ("unverified_lists_crates", lambda t: "Crate pile coordinates" in t),
    ("unverified_lists_stairs", lambda t: "Staircase coordinates" in t),

    ("map_617", lambda t: "Map ID: 617" in t),
    ("bg_id_10", lambda t: "Battleground entry: 10" in t),
    ("dalaranarena_name", lambda t: "DalaranArena" in t),

    ("ws1362", lambda t: "WorldSafeLoc 1362" in t),
    ("ws1363", lambda t: "WorldSafeLoc 1363" in t),
    ("ws1361", lambda t: "WorldSafeLoc 1361" in t),
    ("ally_x", lambda t: "X: 1218.01" in t),
    ("ally_y", lambda t: "Y: 764.795" in t),
    ("ally_z", lambda t: "Z: 14.7297" in t),
    ("horde_x", lambda t: "1361.76" in t),
    ("horde_y", lambda t: "Y: 817.337" in t),
    ("horde_z", lambda t: "Z: 14.8449" in t),
    ("facing_team1", lambda t: "10.001 deg = 0.1746 rad" in t),
    ("facing_team2", lambda t: "190.001 deg = 3.3161 rad" in t),
    ("grave_x", lambda t: "X: 1292.14" in t),
    ("grave_y", lambda t: "790.993" in t),
    ("grave_z", lambda t: "Z: 8.11463" in t),
    ("grave_facing", lambda t: "279.001 deg = 4.8695 rad" in t),
    ("grave_name", lambda t: "Dalaran Arena - PvP Graveyard" in t),

    ("door_low", lambda t: "192643" in t and "1232.65" in t and "20.0729" in t),
    ("door_high", lambda t: "192642" in t and "1350.95" in t and "20.8096" in t),
    ("spout_low", lambda t: "1212.833" in t and "16.09484" in t),
    ("spout_high", lambda t: "1369.977" in t and "16.08718" in t),
    ("creature_28567", lambda t: "28567" in t),
    ("spell_flush", lambda t: "57405" in t),
    ("spell_flush_kb", lambda t: "61698" in t),
    ("spell_spout", lambda t: "58873" in t),

    ("water_collision", lambda t: "194395" in t and "1291.56" in t),
    ("water_visual", lambda t: "191877" in t),
    ("water_z", lambda t: "790.837" in t and "7.1" in t),
    ("two_crates", lambda t: "Count: 2" in t and "Crate piles" in t),
    ("crate_unverified", lambda t: "Coordinates: unverified" in t),

    ("floor_z", lambda t: "Z ~3.16" in t),
    ("platform_z", lambda t: "Z ~7.11" in t),
    ("drop_395", lambda t: "3.95" in t),
    ("four_stairs", lambda t: "Staircases: 4" in t),
    ("patch_530", lambda t: "5.3.0" in t),
    ("patch_320", lambda t: "3.2.0" in t),

    ("bound_south", lambda t: "1290.44, 744.96" in t),
    ("bound_north", lambda t: "1292.6, 837.07" in t),
    ("bound_west", lambda t: "1250.68, 790.86" in t),
    ("bound_east", lambda t: "1332.50, 790.9, 3.16" in t),
    ("size_x", lambda t: "81.8" in t),
    ("size_y", lambda t: "92.1" in t),

    ("ss_go_1", lambda t: "184663" in t),
    ("ss_go_2", lambda t: "184664" in t),
    ("ss_north", lambda t: "1291.7, 813.424, 7.11472" in t),
    ("ss_south", lambda t: "1291.7, 768.911, 7.11472" in t),
    ("ss_spell", lambda t: "34709" in t),
    ("ss_duration", lambda t: "15 s" in t),
    ("ss_damage", lambda t: "+5% damage taken" in t),
    ("ss_spawn_90", lambda t: "90 s after the gates open" in t),
    ("ss_respawn_120", lambda t: "120 s after being taken" in t),
    ("no_health_pickup", lambda t: "no health, mana, haste" in t.lower()),

    ("melee_section", lambda t: "Melee DPS:" in t),
    ("ranged_section", lambda t: "Ranged DPS:" in t),
    ("healer_section", lambda t: "Healers:" in t),
    ("mounts_allowed", lambda t: "allows mounts" in t or "mounts allowed" in t),

    ("demonic_circle", lambda t: "48018" in t),
    ("under_map", lambda t: "1299.046" in t and "9.338" in t),
    ("dampening", lambda t: "Dampening" in t),
    ("uninstanced_copy", lambda t: "map 571" in t),

    ("src_dbc", lambda t: "world_safe_locs" in t),
    ("src_template", lambda t: "battleground_template" in t),
    ("src_core", lambda t: "BattlegroundDS" in t),
    ("src_wiki", lambda t: "Warcraft Wiki" in t),
    ("src_wowhead", lambda t: "Wowhead" in t),
]

MUTATIONS = [
    ("map_id_wrong", lambda t: t.replace("Map ID: 617", "Map ID: 619")),
    ("bg_id_wrong", lambda t: t.replace("Battleground entry: 10", "Battleground entry: 11")),
    ("ws_1362_wrong", lambda t: t.replace("WorldSafeLoc 1362", "WorldSafeLoc 1364")),
    ("ws_1363_wrong", lambda t: t.replace("WorldSafeLoc 1363", "WorldSafeLoc 1365")),
    ("ws_1361_wrong", lambda t: t.replace("WorldSafeLoc 1361", "WorldSafeLoc 1360")),
    ("ally_x_wrong", lambda t: t.replace("X: 1218.01", "X: 1219.01")),
    ("ally_z_wrong", lambda t: t.replace("Z: 14.7297", "Z: 14.7397")),
    ("horde_x_wrong", lambda t: t.replace("1361.76", "1362.76")),
    ("horde_z_wrong", lambda t: t.replace("Z: 14.8449", "Z: 14.8459")),
    ("facing_wrong", lambda t: t.replace("10.001 deg = 0.1746 rad", "10.001 deg = 1.1746 rad")),
    ("grave_x_wrong", lambda t: t.replace("X: 1292.14", "X: 1293.14")),
    ("grave_z_wrong", lambda t: t.replace("Z: 8.11463", "Z: 9.11463")),
    ("door_id_swap", lambda t: t.replace("192643", "192644").replace("192642", "192645")),
    ("door_x_wrong", lambda t: t.replace("1232.65", "1233.65")),
    ("door_z_wrong", lambda t: t.replace("20.8096", "21.8096")),
    ("spout_wrong", lambda t: t.replace("1212.833", "1213.833")),
    ("creature_wrong", lambda t: t.replace("28567", "28568")),
    ("spell_flush_wrong", lambda t: t.replace("57405", "57406")),
    ("spell_spout_wrong", lambda t: t.replace("58873", "58874")),
    ("water_id_wrong", lambda t: t.replace("194395", "194396").replace("191877", "191878")),
    ("water_xy_wrong", lambda t: t.replace("1291.56", "1291.66")),
    ("crate_count_wrong", lambda t: t.replace("Count: 2", "Count: 3")),
    ("crate_verified_claim", lambda t: t.replace("Coordinates: unverified", "Coordinates: verified")),
    ("floor_z_wrong", lambda t: t.replace("Z ~3.16", "Z ~3.26")),
    ("platform_z_wrong", lambda t: t.replace("Z ~7.11", "Z ~7.21")),
    ("drop_wrong", lambda t: t.replace("3.95", "5.95")),
    ("stairs_count_wrong", lambda t: t.replace("Staircases: 4", "Staircases: 2")),
    ("bound_wrong", lambda t: t.replace("1250.68, 790.86", "1251.68, 790.86")),
    ("size_wrong", lambda t: t.replace("81.8", "84.8")),
    ("ss_go_wrong", lambda t: t.replace("184663", "184665").replace("184664", "184666")),
    ("ss_pos_wrong", lambda t: t.replace("813.424", "814.424")),
    ("ss_spell_wrong", lambda t: t.replace("34709", "34710")),
    ("ss_damage_wrong", lambda t: t.replace("+5% damage taken", "+10% damage taken")),
    ("ss_spawn_wrong", lambda t: t.replace("90 s after the gates open", "60 s after the gates open")),
    ("ss_respawn_wrong", lambda t: t.replace("120 s after being taken", "180 s after being taken")),
    ("pickup_claim_wrong", lambda t: t.replace("no health, mana, haste", "health, mana, haste")),
    ("unverified_flip", lambda t: t.replace("Unverified:", "Verified:")),
    ("unverified_crates_removed",
     lambda t: t.replace("- Crate pile coordinates (both piles)", "- Crate geometry")),
    ("stair_unverified_removed", lambda t: t.replace("- Staircase coordinates (all four)", "- Staircase geometry")),
    ("demonic_circle_wrong", lambda t: t.replace("48018", "48019")),
    ("under_map_wrong", lambda t: t.replace("1299.046", "1300.046")),
    ("source_removed", lambda t: t.replace("BattlegroundDS", "BattlegroundXX")),
    ("width_inflate", lambda t: t.replace("=== 1. START POSITIONS",
                                          "=== 1. START POSITIONS AND ALL OF THE VERY LONG EXTRA TEXT HERE")),
]


def run_checks(text):
    passed, failed = 0, []
    for name, fn in STATIC_CHECKS:
        try:
            ok = fn(text)
        except Exception as exc:  # pragma: no cover
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
    print("AUDIT: Arena_Dalaran_Arena_COMPLETED.txt (Step 3)")
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
        "BattlegroundDS.cpp": gh_content(DS_REPO, DS_PATH),
        "BattlegroundDS.h": gh_content(DS_REPO, DS_H_PATH),
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

    print("\n[4] No-invented-coordinates trace")
    corpora["BattlegroundDS.cpp (3.3.5)"] = gh_content(AC_REPO, AC_PATH)
    ok, lines, _ = coord_trace(original, corpora)
    for line in lines:
        print(line)
    if not ok:
        print("    INVENTED COORDINATES FOUND")
        return 1
    if coord_trace(original.replace("1332.50, 790.9, 3.16",
                                    "1337.50, 790.9, 3.16"), corpora)[0]:
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
