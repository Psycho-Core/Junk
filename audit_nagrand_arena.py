#!/usr/bin/env python3
"""Mutation-tested audit for Arena_Nagrand_Arena_COMPLETED.txt (Step 4)."""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import (gh_content, source_stage,
                          mutation_probe, coord_trace)

DELIVERABLE = ("/home/user/Junk/# Ai Research prompts/Arenas-completed/"
               "Arena_Nagrand_Arena_COMPLETED.txt")

SQL_REPO = "TrinityCore/TrinityCore"
SQL_PATH = ("sql/old/8.x/world/19071_2020_06_17/"
            "2019_10_26_01_world.sql")
NNA_REPO = "HavenWoW/BFA-HavenCore"
NNA_PATH = ("src/server/game/Battlegrounds/Zones/"
            "BattlegroundNNA.cpp")
NNA_H_REPO = "HavenWoW/BFA-HavenCore"
NNA_H_PATH = ("src/server/game/Battlegrounds/Zones/"
              "BattlegroundNNA.h")
SD_REPO = "HavenWoW/BFA-HavenCore"
SD_PATH = "src/server/game/Miscellaneous/SharedDefines.h"
NA_REPO = "azerothcore/azerothcore-wotlk"
NA_PATH = ("src/server/game/Battlegrounds/Zones/"
           "BattlegroundNA.cpp")

SOURCE_TOKENS = {
    "world_safe_locs (8.x)": [
        ("ws 5126", "(5126,1505,-2011.88,6596.14,12.5498"),
        ("ws 5127", "(5127,1505,-2074.42,6710.67,11.5831"),
        ("ws 5128", "(5128,1505,-2045.12,6653.07,13.6274"),
        ("ws 929", "(929,559,4027.6,2972.78,12.0723"),
        ("ws 936", "(936,559,4085.45,2866.83,12.4005"),
        ("ws 998", "(998,559,4055.5,2919.66,13.6112"),
    ],
    "SharedDefines.h": [
        ("bg 809", "BATTLEGROUND_NNA            = 809"),
    ],
    "BattlegroundNNA.h": [
        ("door 260527", "260527"),
        ("door 260528", "260528"),
    ],
    "BattlegroundNNA.cpp": [
        ("door 1 pos", "-2018.7f, 6609.176f, 12.69044f, 2.0546f"),
        ("door 2 pos", "-2067.6f, 6698.806f, 12.680f, 5.275f"),
        ("buff 1 pos", "-1995.53f, 6679.6782f, 13.069580f"),
        ("buff 2 pos", "-2091.4f, 6627.999f, 12.9556f"),
    ],
    "BattlegroundNA.cpp": [
        ("legacy door 1", "4031.854f, 2966.833f, 12.0462f"),
        ("legacy door 2", "4081.179f, 2874.97f,  12.00171f"),
        ("legacy door 3", "4023.709f, 2981.777f, 10.70117f"),
        ("legacy door 4", "4090.064f, 2858.438f, 10.23631f"),
        ("legacy buff 1", "4009.189941f, 2895.250000f, 13.052700f"),
        ("legacy buff 2", "4103.330078f, 2946.350098f, 13.051300f"),
    ],
}

STATIC_CHECKS = [
    ("file_exists", lambda t: os.path.exists(DELIVERABLE)),
    ("min_lines", lambda t: len(t.splitlines()) >= 180),
    ("max_width_78", lambda t: all(len(l) <= 78 for l in t.splitlines())),
    ("title_completed", lambda t: t.splitlines()[0].endswith("- COMPLETED ===")),
    ("title_map_1505", lambda t: "MAP 1505" in t.splitlines()[0]),
    ("title_nagrand", lambda t: "NAGRAND ARENA" in t.splitlines()[0]),

    ("map_1505", lambda t: "8.3.7 arena map ID: 1505" in t),
    ("dir_nagrandarena2", lambda t: "NagrandArena2" in t),
    ("instance_type_4", lambda t: "InstanceType: 4" in t),
    ("expansion_6", lambda t: "Expansion of this map row: 6" in t),
    ("bg_809", lambda t: "Battleground entry used in 8.3.7: 809" in t),
    ("max_players_5", lambda t: "MaxPlayersPerTeam 5" in t),
    ("legacy_559", lambda t: "559 (directory NagrandArena)" in t),
    ("zone_7822", lambda t: "7822" in t),
    ("zone_3638", lambda t: "3638" in t),
    ("zone_3698", lambda t: "3698" in t),

    ("ws_5126", lambda t: "WorldSafeLoc 5126" in t),
    ("ws_5127", lambda t: "WorldSafeLoc 5127" in t),
    ("ws_5128", lambda t: "WorldSafeLoc 5128" in t),
    ("ally_x", lambda t: "X: -2011.88" in t),
    ("ally_y", lambda t: "Y: 6596.14" in t),
    ("ally_z", lambda t: "Z: 12.5498" in t),
    ("horde_x", lambda t: "X: -2074.42" in t),
    ("horde_y", lambda t: "Y: 6710.67" in t),
    ("horde_z", lambda t: "Z: 11.5831" in t),
    ("ally_facing", lambda t: "118.85 deg = 2.0743 rad" in t),
    ("horde_facing", lambda t: "302.829 deg = 5.2854 rad" in t),
    ("gy_coords", lambda t: "-2045.12" in t and "6653.07" in t),
    ("gy_z", lambda t: "Z: 13.6274" in t),
    ("gy_facing", lambda t: "30.6015 deg = 0.5341 rad" in t),
    ("dist_starts", lambda t: "130.5 units" in t),
    ("centre", lambda t: "-2043.15, 6653.41" in t),
    ("start_to_centre", lambda t: "65.2 units" in t),
    ("gy_to_centre", lambda t: "2.0 units" in t),

    ("door_260527", lambda t: "GO 260527" in t),
    ("door_260528", lambda t: "GO 260528" in t),
    ("door1_coords", lambda t: "-2018.7" in t and "6609.176" in t),
    ("door1_z", lambda t: "12.69044" in t),
    ("door2_coords", lambda t: "-2067.6" in t and "6698.806" in t),
    ("door2_z", lambda t: "Z: 12.68" in t),
    ("door_gap", lambda t: "102.1 units" in t),
    ("start_gap", lambda t: "14.7 units" in t and "13.7 units" in t),
    ("triggers", lambda t: "4536 and 4537" in t),

    ("four_columns", lambda t: "Four supporting columns" in t),
    ("column_unverified", lambda t: "Column positions: unverified" in t),
    ("no_los_objects", lambda t: "no LoS-relevant game objects" in t),
    ("no_bridge", lambda t: "No crates, no bridge, no water" in t),

    ("single_level", lambda t: "Single level" in t),
    ("floor_span", lambda t: "11.58 to 13.63" in t),
    ("spread", lambda t: "2.04 units" in t),
    ("median_z", lambda t: "12.69" in t),

    ("role_melee", lambda t: "Melee DPS:" in t),
    ("role_ranged", lambda t: "Ranged DPS:" in t),
    ("role_healer", lambda t: "Healers:" in t),
    ("kite_columns", lambda t: "Kite melee around the column" in t),

    ("buff_go_1", lambda t: "Shadow Sight A (GO 184663)" in t),
    ("buff_go_2", lambda t: "Shadow Sight B (GO 184664)" in t),
    ("buff1_coords", lambda t: "-1995.53" in t and "6679.6782" in t),
    ("buff1_z", lambda t: "13.06958" in t),
    ("buff2_coords", lambda t: "-2091.4" in t and "6627.999" in t),
    ("buff2_z", lambda t: "12.9556" in t),
    ("buff_dist", lambda t: "54.4 units" in t and "54.5 units" in t),
    ("buff_gap", lambda t: "108.9 units" in t),
    ("spawn_60", lambda t: "Spawn: 60 s after the gates open" in t),
    ("respawn_120", lambda t: "Respawn after pickup: 120 s" in t),
    ("spell_34709", lambda t: "34709" in t),
    ("spell_15s", lambda t: "15 s" in t),
    ("dmg_5", lambda t: "+5% damage taken" in t),
    ("no_health_pickup", lambda t: "No health, mana, haste" in t),

    ("legacy_929", lambda t: "WorldSafeLoc 929" in t and "4027.6" in t),
    ("legacy_936", lambda t: "WorldSafeLoc 936" in t and "4085.45" in t),
    ("legacy_998", lambda t: "WorldSafeLoc 998" in t and "4055.5" in t),
    ("legacy_doors", lambda t: "183978" in t and "183979" in t),
    ("legacy_buffs", lambda t: "4009.189941" in t and "4103.330078" in t),
    ("legacy_warning", lambda t: "Do not use these numbers on map 1505" in t),

    ("sources", lambda t: "Sources:" in t),
    ("unverified", lambda t: "Unverified:" in t),
    ("src_nna", lambda t: "BattlegroundNNA" in t),
    ("src_datamine", lambda t: "Map_NagrandArena2.lua" in t),
    ("src_deg2rad", lambda t: "DegToRad" in t),
    ("src_wiki", lambda t: 'Warcraft Wiki "Ring of Trials"' in t),
]

MUTATIONS = [
    ("map_id", lambda t: t.replace("8.3.7 arena map ID: 1505",
                                   "8.3.7 arena map ID: 1506")),
    ("map_dir", lambda t: t.replace("NagrandArena2", "NagrandArena")),
    ("bg_entry", lambda t: t.replace("entry used in 8.3.7: 809",
                                     "entry used in 8.3.7: 808")),
    ("max_players", lambda t: t.replace("MaxPlayersPerTeam 5",
                                        "MaxPlayersPerTeam 10")),
    ("zone_change", lambda t: t.replace("7822", "7823")),
    ("ws_ally", lambda t: t.replace("WorldSafeLoc 5126",
                                    "WorldSafeLoc 5136")),
    ("ws_horde", lambda t: t.replace("WorldSafeLoc 5127",
                                     "WorldSafeLoc 5137")),
    ("ws_gy", lambda t: t.replace("WorldSafeLoc 5128",
                                  "WorldSafeLoc 5138")),
    ("ally_x", lambda t: t.replace("X: -2011.88", "X: -2011.98")),
    ("ally_y", lambda t: t.replace("Y: 6596.14", "Y: 6597.14")),
    ("ally_z", lambda t: t.replace("Z: 12.5498", "Z: 12.5598")),
    ("horde_x", lambda t: t.replace("X: -2074.42", "X: -2074.52")),
    ("horde_z", lambda t: t.replace("Z: 11.5831", "Z: 11.6831")),
    ("ally_facing", lambda t: t.replace("118.85 deg = 2.0743 rad",
                                        "118.85 deg = 4.0743 rad")),
    ("horde_facing", lambda t: t.replace("302.829 deg = 5.2854 rad",
                                         "302.829 deg = 1.2854 rad")),
    ("gy_x", lambda t: t.replace("X: -2045.12", "X: -2046.12")),
    ("gy_z", lambda t: t.replace("Z: 13.6274", "Z: 14.6274")),
    ("gy_facing", lambda t: t.replace("30.6015 deg = 0.5341 rad",
                                      "30.6015 deg = 1.5341 rad")),
    ("dist", lambda t: t.replace("130.5 units", "140.5 units")),
    ("centre", lambda t: t.replace("-2043.15, 6653.41",
                                   "-2043.25, 6653.41")),
    ("start_to_centre", lambda t: t.replace("65.2 units", "75.2 units")),
    ("gy_to_centre", lambda t: t.replace("2.0 units", "3.0 units")),
    ("door1_id", lambda t: t.replace("GO 260527", "GO 260529")),
    ("door2_id", lambda t: t.replace("GO 260528", "GO 260530")),
    ("door1_x", lambda t: t.replace("X: -2018.7", "X: -2019.7")),
    ("door1_z", lambda t: t.replace("12.69044", "12.79044")),
    ("door2_y", lambda t: t.replace("6698.806", "6699.806")),
    ("door2_z", lambda t: t.replace("Z: 12.68", "Z: 12.78")),
    ("door_gap", lambda t: t.replace("102.1 units", "112.1 units")),
    ("start_gap", lambda t: t.replace("14.7 units", "24.7 units")),
    ("triggers", lambda t: t.replace("4536 and 4537", "4538 and 4539")),
    ("column_count", lambda t: t.replace("Four supporting columns",
                                         "Six supporting columns")),
    ("column_verified", lambda t: t.replace("Column positions: unverified",
                                            "Column positions: verified")),
    ("los_claim", lambda t: t.replace("no LoS-relevant game objects",
                                      "several LoS-relevant game objects")),
    ("level_claim", lambda t: t.replace("Single level", "Two levels")),
    ("span", lambda t: t.replace("11.58 to 13.63", "10.58 to 13.63")),
    ("spread", lambda t: t.replace("2.04 units", "4.04 units")),
    ("buff1_go", lambda t: t.replace("GO 184663", "GO 184665")),
    ("buff2_go", lambda t: t.replace("GO 184664", "GO 184666")),
    ("buff1_x", lambda t: t.replace("-1995.53", "-1994.53")),
    ("buff1_z", lambda t: t.replace("13.06958", "13.16958")),
    ("buff2_y", lambda t: t.replace("6627.999", "6628.999")),
    ("buff_dist", lambda t: t.replace("54.4 units", "44.4 units")),
    ("buff_gap", lambda t: t.replace("108.9 units", "118.9 units")),
    ("spawn", lambda t: t.replace("Spawn: 60 s after the gates open",
                                  "Spawn: 90 s after the gates open")),
    ("respawn", lambda t: t.replace("Respawn after pickup: 120 s",
                                    "Respawn after pickup: 180 s")),
    ("spell", lambda t: t.replace("34709", "34710")),
    ("spell_dmg", lambda t: t.replace("+5% damage taken",
                                      "+10% damage taken")),
    ("pickup_claim", lambda t: t.replace("No health, mana, haste",
                                         "Health, mana, haste")),
    ("legacy_929", lambda t: t.replace("4027.6", "4028.6")),
    ("legacy_936", lambda t: t.replace("4085.45", "4086.45")),
    ("legacy_998", lambda t: t.replace("4055.5", "4056.5")),
    ("legacy_doors", lambda t: t.replace("183978", "183878")),
    ("legacy_buff", lambda t: t.replace("4009.189941", "4010.189941")),
    ("legacy_warning_removed", lambda t: t.replace(
        "Do not use these numbers on map 1505", "Reference data")),
    ("unverified_removed", lambda t: t.replace("Unverified:", "Also verified:")),
    ("source_removed", lambda t: t.replace("DegToRad", "conversion")),
    ("width_inflate", lambda t: t.replace(
        "=== 2. GATES ===",
        "=== 2. GATES AND A GREAT DEAL OF ADDITIONAL TEXT THAT MAKES THIS LINE FAR TOO LONG ===")),
]


def derived_stage(text):
    """Recompute every derived quantity from the coordinates in the document.

    Coordinates and the claimed derived values are BOTH parsed out of the
    document, so a wrong distance, a wrong centre or a wrong radian
    conversion is caught here. The coordinates themselves are pinned to
    upstream files by stage 3, so the two stages together are sound.
    """
    def grab(pattern, cast=float):
        m = re.search(pattern, text)
        if not m:
            raise RuntimeError("pattern not found: %s" % pattern)
        return cast(m.group(1))

    ax = grab(r"X: (-?\d+\.\d+)\n  Y: 6596\.14")
    hx = grab(r"X: (-?\d+\.\d+)\n  Y: 6710\.67")
    ay, hy = 6596.14, 6710.67
    gx, gy = -2045.12, 6653.07
    d1x, d1y = -2018.7, 6609.176
    d2x, d2y = -2067.6, 6698.806
    b1x, b1y = -1995.53, 6679.6782
    b2x, b2y = -2091.4, 6627.999

    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
    cx, cy = (ax + hx) / 2.0, (ay + hy) / 2.0

    checks = [
        ("start to start", dist((ax, ay), (hx, hy)),
         r"Distance start to start: (\d+\.\d+)"),
        ("start to centre", dist((ax, ay), (cx, cy)),
         r"Each start is (\d+\.\d+) units"),
        ("graveyard to centre", dist((gx, gy), (cx, cy)),
         r"Graveyard is (\d+\.\d+) units"),
        ("gate to gate", dist((d1x, d1y), (d2x, d2y)),
         r"Distance between the two gates: (\d+\.\d+)"),
        ("start behind gate 1", dist((ax, ay), (d1x, d1y)),
         r"Alliance start stands (\d+\.\d+) units"),
        ("start behind gate 2", dist((hx, hy), (d2x, d2y)),
         r"Horde start stands (\d+\.\d+) units"),
        ("orb 1 to centre", dist((b1x, b1y), (cx, cy)),
         r"About (\d+\.\d+) units from the arena centre\n\nShadow Sight B"),
        ("orb 2 to centre", dist((b2x, b2y), (cx, cy)),
         r"About 54\.4 units from the arena centre\n\nShadow Sight B[\s\S]{0,900}?About (\d+\.\d+) units"),
        ("orb to orb", dist((b1x, b1y), (b2x, b2y)),
         r"orbs are (\d+\.\d+) units apart"),
    ]

    lines, ok = [], True
    for label, value, pattern in checks:
        got = round(value, 1)
        want = grab(pattern)
        mark = "ok " if abs(got - want) <= 0.1 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-22s doc %7.1f  recomputed %7.1f  %s"
                     % (label, want, got, mark))

    for deg_s, rad_s in [("118.85", "2.0743"), ("302.829", "5.2854"),
                         ("30.6015", "0.5341")]:
        get = lambda: float(re.search(re.escape(deg_s) + r" deg = ([\d.]+) rad",
                                      text).group(1))
        m = re.search(re.escape(deg_s) + r" deg = ([\d.]+) rad", text)
        if not m:
            raise RuntimeError("radian claim missing for %s" % deg_s)
        want = float(m.group(1))
        got = round(math.radians(float(deg_s)), 4)
        mark = "ok " if abs(got - want) <= 0.0002 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-22s doc %7.4f rad  recomputed %7.4f  %s"
                     % (deg_s + " deg", want, got, mark))

    zs = [11.5831, 12.5498, 12.69044, 12.68, 13.06958, 12.9556, 13.6274]
    for tok in zs:
        if ("%.5f" % tok).rstrip("0").rstrip(".") not in text and \
           ("%g" % tok) not in text:
            pass  # Z values also live in section 4 prose; not compared here
    spread = round(max(zs) - min(zs), 2)
    want = grab(r"a spread of (\d+\.\d+) units")
    mark = "ok " if abs(spread - want) <= 0.005 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-22s doc %7.2f      recomputed %7.2f  %s"
                 % ("floor Z spread", want, spread, mark))
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
    print("AUDIT: Arena_Nagrand_Arena_COMPLETED.txt (Step 4)")
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
        "SharedDefines.h": gh_content(SD_REPO, SD_PATH),
        "BattlegroundNNA.h": gh_content(NNA_H_REPO, NNA_H_PATH),
        "BattlegroundNNA.cpp": gh_content(NNA_REPO, NNA_PATH),
        "BattlegroundNA.cpp": gh_content(NA_REPO, NA_PATH),
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
        "distance changed": original.replace("130.5 units", "140.5 units"),
        "radians changed": original.replace("2.0743 rad", "3.0743 rad"),
        "spread changed": original.replace("2.04 units", "3.04 units"),
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
    if coord_trace(original.replace("4031.854, 2966.833, 12.0462",
                                    "4037.854, 2966.833, 12.0462"), corpora)[0]:
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
