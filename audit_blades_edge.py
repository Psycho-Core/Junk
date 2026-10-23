#!/usr/bin/env python3
"""
Mutation-tested audit for Arena_Blade_s_Edge_Arena_COMPLETED.txt (Step 2).
Verifies static content correctness and that audit detects injected mutations.
"""

import sys
import re
import os

DELIVERABLE = "/home/user/Junk/# Ai Research prompts/Arenas_complete/Arena_Blade_s_Edge_Arena_COMPLETED.txt"

# ============================================================
# STATIC CHECKS (must all pass on the real deliverable)
# ============================================================

STATIC_CHECKS = [
    # --- File existence & basic structure ---
    ("file_exists", lambda t: os.path.exists(DELIVERABLE)),
    ("non_empty", lambda t: len(t.strip()) > 0),
    ("line_count", lambda t: len(t.splitlines()) >= 140),
    ("max_line_width_78", lambda t: all(len(l) <= 78 for l in t.splitlines())),

    # --- Section headers present ---
    ("has_map_id_header", lambda t: "MAP 562" in t and "1672" in t),
    ("has_start_positions", lambda t: "START POSITIONS" in t.upper()),
    ("has_pillars_section", lambda t: "PILLARS" in t.upper() and "LINE OF SIGHT" in t.upper()),
    ("has_height_levels", lambda t: "HEIGHT LEVELS" in t.upper() and "RAMPS" in t.upper()),
    ("has_role_positions", lambda t: "FIRST POSITIONS BY ROLE" in t.upper()),
    ("has_pickups_section", lambda t: "BUFF" in t.upper() and "HEALTH PICKUPS" in t.upper()),
    ("has_additional_notes", lambda t: "ADDITIONAL NOTES" in t.upper()),
    ("has_sources", lambda t: "SOURCES:" in t.upper()),
    ("has_unverified", lambda t: "UNVERIFIED" in t.upper()),
    ("unverified_section", lambda t: "UNVERIFIED:" in t.upper()),

    # --- Map IDs ---
    ("map_id_562", lambda t: "562" in t),
    ("instance_id_1672", lambda t: "1672" in t),

    # --- Start positions (WorldSafeLocs 939, 940, 971) ---
    ("ws_939_alliance", lambda t: "939" in t and "ALLIANCE" in t.upper() and "TEAM 1" in t.upper()),
    ("ws_940_horde", lambda t: "940" in t and "HORDE" in t.upper() and "TEAM 2" in t.upper()),
    ("ws_971_graveyard", lambda t: "971" in t and "GRAVEYARD" in t.upper()),
    ("alliance_coords_6292", lambda t: "6292.66" in t),
    ("horde_coords_6184", lambda t: "6184.98" in t),
    ("graveyard_coords_6238", lambda t: "6238.93" in t),
    ("alliance_orient_0", lambda t: "0.0" in t and "NORTH" in t.upper()),
    ("horde_orient_pi", lambda t: "3.14159" in t and "SOUTH" in t.upper()),

    # --- Pillars ---
    ("two_main_pillars", lambda t: "TWO MAIN PILLARS" in t.upper() or "TWO PILLARS" in t.upper()),
    ("pillar_count_two", lambda t: "TWO" in t.upper() and "PILLAR" in t.upper()),
    ("se_pillar_coords", lambda t: "6236" in t and "258" in t),
    ("nw_pillar_coords", lambda t: "6241" in t and "265" in t),
    ("bridge_level_z_11_5", lambda t: "11.5" in t and "BRIDGE LEVEL" in t.upper()),
    ("bridge_z_exact", lambda t: "Z: ~11.3 - 11.5" in t or "Z ~11.3 - 11.5" in t),
    ("rope_walkways", lambda t: "ROPE WALK" in t.upper()),
    ("walkable_on_retail", lambda t: "WALKABLE" in t.upper()),
    ("center_pit_pillars_unverified", lambda t: "CENTER PIT" in t.upper() and "UNVERIFIED" in t.upper()),

    # --- Height levels & ramps ---
    ("ground_z_5", lambda t: "Z: ~4.9" in t or "Z ~5" in t or "GROUND" in t.upper()),
    ("bridge_z_11_5", lambda t: "Z: ~11.3" in t or "Z ~11.5" in t),
    ("bridge_z_exact_2", lambda t: "~11.3 - 11.5" in t),
    ("height_diff_6_5", lambda t: "6.5" in t and "HEIGHT" in t.upper()),
    ("height_diff_exact", lambda t: "~6.5" in t),
    ("six_ramps", lambda t: "6" in t and "RAMPS" in t.upper()),
    ("six_ramps_exact", lambda t: "6 RAMPS" in t.upper() or "6 TOTAL" in t.upper()),
    ("corner_ramps", lambda t: "CORNER" in t.upper() and "RAMPS" in t.upper()),
    ("center_ramps", lambda t: "CENTER" in t.upper() and "RAMPS" in t.upper()),
    ("ramp_positions_unverified", lambda t: "RAMP POSITIONS" in t.upper() and "UNVERIFIED" in t.upper()),

    # --- Role positions ---
    ("melee_rush_ramps", lambda t: "MELEE" in t.upper() and "RUSH" in t.upper()),
    ("ranged_bridge", lambda t: "RANGED" in t.upper() and "BRIDGE" in t.upper()),
    ("healers_follow_melee", lambda t: "FOLLOW MELEE" in t.upper() and "RAMP" in t.upper()),
    ("healers_bridge_pillar", lambda t: "HEALER" in t.upper() and "BRIDGE" in t.upper()),
    ("bridge_control_strategy", lambda t: "CONTROL OF THE BRIDGE" in t.upper()),

    # --- Pickups ---
    ("no_powerup_pickups", lambda t: "NOT HAVE" in t.upper() and "POWER-UP" in t.upper()),
    ("no_healing_haste_orbs", lambda t: "HEALING" in t.upper() and "HASTE" in t.upper()),
    ("arena_preparation_buff", lambda t: "PREPARATION" in t.upper() and "ZONE-IN" in t.upper()),
    ("glade_arena_contrast", lambda t: "GLADE ARENA" in t.upper()),

    # --- Sources ---
    ("source_worldsafelocs", lambda t: "WORLDSAFELOCS" in t.upper()),
    ("source_map_dbc", lambda t: "MAP.DBC" in t.upper()),
    ("source_battleground_template", lambda t: "BATTLEGROUND_TEMPLATE" in t.upper()),
    ("source_mmaps", lambda t: "MMAPS" in t.upper() or "MAPBUILDER" in t.upper()),
    ("source_liquipedia", lambda t: "LIQUIPEDIA" in t.upper()),
    ("source_wowpedia", lambda t: "WOWPEDIA" in t.upper()),
    ("source_gist", lambda t: "SAQIRMDEV" in t.upper() or "GIST" in t.upper()),
    ("source_worldsafelocs_exact", lambda t: "WorldSafeLocs.dbc" in t and "939" in t and "940" in t and "971" in t),
]

# ============================================================
# MUTATIONS (each should be detected by at least one check)
# ============================================================

MUTATIONS = [
    ("map_id_wrong", lambda t: t.replace("562", "563")),
    ("instance_id_wrong", lambda t: t.replace("1672", "1673")),
    ("ws_939_changed", lambda t: t.replace("939", "938")),
    ("ws_940_changed", lambda t: t.replace("940", "941")),
    ("ws_971_changed", lambda t: t.replace("971", "972")),
    ("alliance_x_wrong", lambda t: t.replace("6292.66", "6293.66")),
    ("horde_x_wrong", lambda t: t.replace("6184.98", "6185.98")),
    ("graveyard_x_wrong", lambda t: t.replace("6238.93", "6239.93")),
    ("alliance_orient_wrong", lambda t: t.replace("0.0 (North)", "1.57 (East)")),
    ("horde_orient_wrong", lambda t: t.replace("3.14159 (South/Pi)", "0.0 (North)")),
    ("pillar_count_wrong", lambda t: t.replace("Two main pillars", "Three main pillars").replace("Two pillars", "Three pillars").replace("two main pillars", "three main pillars")),
    ("bridge_z_wrong", lambda t: t.replace("Z: ~11.3 - 11.5", "Z: ~12.0 - 12.5").replace("~11.3 - 11.5", "~12.0 - 12.5")),
    ("height_diff_wrong", lambda t: t.replace("~6.5 units", "~10.0 units").replace("~6.5", "~10.0")),
    ("ramp_count_wrong", lambda t: t.replace("6 ramps", "4 ramps").replace("6 RAMPS", "4 RAMPS").replace("6 TOTAL", "4 TOTAL").replace("(6 total", "(4 total").replace("(6 TOTAL", "(4 TOTAL")),
    ("has_pickups", lambda t: t.replace("does NOT have arena power-up pickups", "HAS arena power-up pickups")),
    ("glade_removed", lambda t: t.replace("Glade Arena", "Some Other Arena")),
    ("melee_stays_ground", lambda t: t.replace("Rush up nearest ramp", "Stay on ground level")),
    ("healer_stays_ground_only", lambda t: t.replace("Follow melee up ramp", "Stay on ground level")),
    ("source_removed", lambda t: t.replace("TrinityCore WorldSafeLocs.dbc", "").replace("WorldSafeLocs.dbc", "")),
    ("unverified_removed", lambda t: t.replace("Unverified:", "Verified:").replace("UNVERIFIED:", "VERIFIED:")),
]

def run_static_checks(text, label=""):
    """Run all static checks on text. Returns (passed_count, failed_list)."""
    passed = 0
    failed = []
    for name, check in STATIC_CHECKS:
        try:
            if check(text):
                passed += 1
            else:
                failed.append(name)
        except Exception as e:
            failed.append(f"{name} (error: {e})")
    return passed, failed

def test_mutations(original_text):
    """Apply each mutation and verify at least one check fails."""
    detected = 0
    undetected = []
    for name, mut_fn in MUTATIONS:
        mutated = mut_fn(original_text)
        passed, failed = run_static_checks(mutated)
        if failed:
            detected += 1
        else:
            undetected.append(name)
    return detected, undetected

def main():
    # Load deliverable
    with open(DELIVERABLE, "r") as f:
        original = f.read()

    print("=" * 60)
    print("MUTATION-TESTED AUDIT: Arena_Blade_s_Edge_Arena_COMPLETED.txt (Step 2)")
    print("=" * 60)

    # 1. Static checks on real deliverable
    print("\n[1] Static checks on real deliverable...")
    passed, failed = run_static_checks(original)
    print(f"    Passed: {passed}/{len(STATIC_CHECKS)}")
    if failed:
        print(f"    FAILED checks: {failed}")
        return 1
    print("    ALL STATIC CHECKS PASSED")

    # 2. Mutation testing
    print("\n[2] Mutation testing...")
    detected, undetected = test_mutations(original)
    print(f"    Mutations detected: {detected}/{len(MUTATIONS)}")
    if undetected:
        print(f"    UNDETECTED mutations: {undetected}")
        return 1
    print("    ALL MUTATIONS DETECTED")

    # 3. Summary
    print("\n" + "=" * 60)
    print("AUDIT RESULT: PASS")
    print(f"  Static checks: {passed}/{len(STATIC_CHECKS)}")
    print(f"  Mutations detected: {detected}/{len(MUTATIONS)}")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())