#!/usr/bin/env python3
"""Mutation-tested audit for Arena_The_Tiger_s_Peak_COMPLETED.txt (Step 7)."""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import (gh_content, source_stage, mutation_probe,
                          coord_trace)

DELIVERABLE = ("/home/user/Junk/# Ai Research prompts/Arenas_complete/"
               "Arena_The_Tiger_s_Peak_COMPLETED.txt")

SQL_REPO = "TrinityCore/TrinityCore"
SQL_PATH = ("sql/old/8.x/world/19071_2020_06_17/"
            "2019_10_26_01_world.sql")
TTP_REPO = "HavenWoW/BFA-HavenCore"
TTP_PATH = ("src/server/game/Battlegrounds/Zones/BattlegroundTTP.cpp")
TTP_H_PATH = ("src/server/game/Battlegrounds/Zones/BattlegroundTTP.h")
DM_REPO = "Ghostopheles/Datamine"
DM_PATH = "Datamine_Maps/Generated/Map_ShadoPanArena.lua"
TPL_REPO = "zTerragor/vSLDB"
TPL_PATH = "sql/updates/world/2021_11_03_world_Battleground_Template.sql"
RL_PATH = "src/server/game/Battlegrounds/Zones/BattlegroundRL.cpp"
TVA_PATH = "src/server/game/Battlegrounds/Zones/BattlegroundTVA.cpp"

SOURCE_TOKENS = {
    "world_safe_locs (8.x)": [
        ("ws 4534", "1134,491.476,633.332,380.707,0.00848389"),
        ("ws 4535", "1134,642.367,633.406,380.705,180.283"),
        ("ws 4536", "1134,565.578,631.54,380.704,0.00848389"),
    ],
    "battleground_template": [
        ("bg 757 row", "(757, 0, 5, 90, 120, 4534, 4535, 0, 1, '', "
                      "'The Tiger\\'s Peak')"),
    ],
    "BattlegroundTTP.h": [
        ("door 212921", "BG_TTP_OBJECT_TYPE_DOOR_1    = 212921"),
        ("door 2 same", "BG_TTP_OBJECT_TYPE_DOOR_2    = 212921"),
        ("buff 184663", "BG_TTP_OBJECT_TYPE_BUFF_1    = 184663"),
        ("buff 184664", "BG_TTP_OBJECT_TYPE_BUFF_2    = 184664"),
    ],
    "BattlegroundTTP.cpp": [
        ("door 1 pos", "501.932f, 633.429f, 380.708f, 0.0262353f"),
        ("door 2 pos", "632.101f, 633.791f, 380.704f, 3.20989f"),
        ("buff A pos", "566.6805f, 602.2274f, 383.6813f, 3.316144f"),
        ("buff B pos", "566.6563f, 664.566f, 383.6809f, 2.460913f"),
        ("worldstate", "0xE1A, 1"),
        ("triggers", "case 4536"),
        ("spawn", "SpawnBGObject(i, 60)"),
    ],
    "BattlegroundRL.cpp": [
        ("RL door 1 quat", "-0.6658813f, 0.7460576f"),
    ],
    "BattlegroundTVA.cpp": [
        ("TV door 2 quat", "0, 0, 0, 0, 1.f, RESPAWN_IMMEDIATELY"),
    ],
    "Map_ShadoPanArena.lua": [
        ("map name", 'MapName = "The Tiger\'s Peak"'),
        ("map id", "MapID = 1134"),
        ("directory", "Directory = [[ShadoPanArena]]"),
        ("instance type", "InstanceType = 4"),
        ("expansion", "ExpansionID = 4"),
        ("wdt", "WDTFileDataID: 848418"),
    ],
}

STATIC_CHECKS = [
    ("file_exists", lambda t: os.path.exists(DELIVERABLE)),
    ("min_lines", lambda t: len(t.splitlines()) >= 200),
    ("max_width_78", lambda t: all(len(l) <= 78 for l in t.splitlines())),
    ("title_completed",
     lambda t: t.splitlines()[0].endswith("- COMPLETED ===")),
    ("title_map_1134", lambda t: "MAP 1134" in t.splitlines()[0]),

    ("map_1134", lambda t: "Arena map ID: 1134" in t),
    ("dir", lambda t: "Map.dbc directory: ShadoPanArena" in t),
    ("instance_type_4", lambda t: "InstanceType: 4" in t),
    ("zone_6732", lambda t: "AreaTable zone: 6732" in t),
    ("expansion_field_4", lambda t: "ExpansionID field in the map row: 4" in t),
    ("wdt", lambda t: "848418" in t),
    ("no_legacy", lambda t: "No legacy duplicate" in t),
    ("legacy_ids", lambda t: "1505 vs 559" in t and "1672 vs 562" in t),
    ("bg_757", lambda t: 'Battleground entry: 757 "The Tiger\'s Peak"' in t),
    ("max_players_5", lambda t: "MaxPlayersPerTeam 5" in t),
    ("lvl_90_120", lambda t: "MinLvl 90, MaxLvl 120" in t),
    ("start_max_dist_0", lambda t: "StartMaxDist 0" in t),
    ("weight_1", lambda t: "Weight 1" in t),
    ("added_530", lambda t: "patch 5.3.0" in t),
    ("seventh", lambda t: "Seventh arena map" in t),
    ("shado_pan", lambda t: "Shado-Pan Monastery, atop Kun-Lai Summit" in t),
    ("retail_removal", lambda t: "2019-03-20" in t),
    ("retail_return", lambda t: "Dragonflight season 1" in t),
    ("pool_unverified", lambda t: "back in the pool during 8.3.7\n  is unverified"
                                  in t),

    ("ws_4534", lambda t: "WorldSafeLoc 4534" in t),
    ("ws_4535", lambda t: "WorldSafeLoc 4535" in t),
    ("ws_4536", lambda t: "WorldSafeLoc 4536" in t),
    ("t1_x", lambda t: "X: 491.476" in t),
    ("t1_y", lambda t: "Y: 633.332" in t),
    ("t1_z", lambda t: "Z: 380.707" in t),
    ("t1_facing", lambda t: "0.00848389 deg = 0.000148 rad" in t),
    ("t2_x", lambda t: "X: 642.367" in t),
    ("t2_y", lambda t: "Y: 633.406" in t),
    ("t2_z", lambda t: "Z: 380.705" in t),
    ("t2_facing", lambda t: "180.283 deg = 3.14653 rad" in t),
    ("go_x", lambda t: "X: 565.578" in t),
    ("go_y", lambda t: "Y: 631.54" in t),
    ("go_z", lambda t: "Z: 380.704" in t),
    ("no_gy_row", lambda t: "No arena graveyard row exists on map 1134" in t),
    ("dist_starts", lambda t: "150.89 units" in t),
    ("centre", lambda t: "about 566.921, 633.369" in t),
    ("start_to_centre", lambda t: "75.45 units" in t),
    ("axis_x", lambda t: "150.89 apart on X" in t),
    ("axis_y", lambda t: "0.07 apart on Y" in t),
    ("facing_not_opposite", lambda t: "180 deg plus 0.283" in t),
    ("go_to_centre", lambda t: "2.27 units" in t),

    ("door_entry", lambda t: "Both doors use the same game object entry" in t),
    ("door_entry_id", lambda t: "212921." in t),
    ("g1_x", lambda t: "X: 501.932" in t),
    ("g1_y", lambda t: "Y: 633.429" in t),
    ("g1_z", lambda t: "Z: 380.708" in t),
    ("g1_orient", lambda t: "Orientation: 0.0262353 rad" in t),
    ("g2_x", lambda t: "X: 632.101" in t),
    ("g2_y", lambda t: "Y: 633.791" in t),
    ("g2_orient", lambda t: "Orientation: 3.20989 rad" in t),
    ("quat_zero", lambda t: "Quaternion: 0, 0, 0, 0" in t),
    ("quat_contrast", lambda t: "Tol'viron team 2 uses 0, 0, 0, 1" in t
                                and "-0.6658813, 0.7460576" in t),
    ("gate_gap", lambda t: "130.17 units" in t),
    ("gate_start", lambda t: "10.46 units" in t and "10.27 units" in t),
    ("gate_level", lambda t: "within 0.001 units" in t),
    ("triggers", lambda t: "4536 and 4537" in t),
    ("trigger_caution", lambda t: "different tables" in t),

    ("two_statues", lambda t: "Statue count: 2" in t),
    ("two_platforms", lambda t: "Platform count: 2" in t),
    ("statues_unverified", lambda t: "Statue positions: unverified" in t),
    ("platforms_unverified", lambda t: "Platform centres: unverified" in t),
    ("liquipedia_quote", lambda t: "two statues that function as pillars"
                                   in t),
    ("mmoc_quote", lambda t: "the fence does not block line of\n   sight"
                             in t),
    ("engadget_quote", lambda t: "statues, facing each other" in t),
    ("four_objects", lambda t: "exactly four objects" in t),
    ("no_pit", lambda t: "No bridge" in t or "no bridge" in t),

    ("two_levels", lambda t: "Two levels." in t),
    ("floor_band", lambda t: "380.704 to 380.708" in t),
    ("platform_band", lambda t: "383.6809 to 383.6813" in t),
    ("orb_step", lambda t: "2.9733 above gate 1" in t and "2.9769" in t),
    ("stairs_outer", lambda t: "stairs on the outer side" in t),
    ("jump_down", lambda t: "too high to jump" in t),
    ("dh_jump", lambda t: "Demon Hunter can double jump" in t),

    ("role_melee", lambda t: "Melee DPS:" in t),
    ("role_ranged", lambda t: "Ranged DPS:" in t),
    ("role_healer", lambda t: "Healers:" in t),
    ("healer_safest", lambda t: "safest ground on the map" in t),
    ("knockback", lambda t: "blocks\n  knockbacks toward the arena" in t),

    ("buff_a_id", lambda t: "Shadow Sight A (GO 184663)" in t),
    ("buff_b_id", lambda t: "Shadow Sight B (GO 184664)" in t),
    ("buff_a_x", lambda t: "X: 566.6805" in t),
    ("buff_a_y", lambda t: "Y: 602.2274" in t),
    ("buff_a_z", lambda t: "Z: 383.6813" in t),
    ("buff_a_orient", lambda t: "Orientation: 3.316144 rad" in t),
    ("buff_b_x", lambda t: "X: 566.6563" in t),
    ("buff_b_y", lambda t: "Y: 664.566" in t),
    ("buff_b_z", lambda t: "Z: 383.6809" in t),
    ("buff_b_orient", lambda t: "Orientation: 2.460913 rad" in t),
    ("buff_dists", lambda t: "31.14 units" in t and "31.20 units" in t),
    ("buff_gap", lambda t: "62.34 units" in t),
    ("buff_x_gap", lambda t: "0.024 units apart on X" in t),
    ("buff_step", lambda t: "about 2.97 above the arena" in t),
    ("spawn_60", lambda t: "Spawn: 60 s after the gates open" in t),
    ("respawn_120", lambda t: "Respawn after pickup: 120 s" in t),
    ("spell", lambda t: "34709" in t),
    ("spell_dmg", lambda t: "+5% damage taken" in t),
    ("wiki_90s", lambda t: "wiki quotes 90 s" in t),
    ("no_health", lambda t: "No health, mana, haste" in t),

    ("worldstate", lambda t: "Worldstate 0xE1A" in t),
    ("no_oob", lambda t: "No out-of-bounds or under-map return points" in t),
    ("known_defects", lambda t: "blinking into the stair geometry" in t),

    ("sources", lambda t: "Sources:" in t),
    ("unverified", lambda t: "Unverified:" in t),
    ("src_ttp", lambda t: "BattlegroundTTP.cpp" in t),
    ("src_datamine", lambda t: "Map_ShadoPanArena.lua" in t),
    ("src_wiki", lambda t: 'Warcraft Wiki "Tiger\'s Peak"' in t),
    ("src_liquipedia", lambda t: 'Liquipedia "The Tiger\'s Peak"' in t),
    ("src_mod", lambda t: "Ministry of Defense arena guide" in t),
    ("src_forum", lambda t: 'Tiger\'s Peak Temporarily Closing' in t),
    ("no_second_floor", lambda t: "no second floor" in t),
]

MUTATIONS = [
    ("map_id", lambda t: t.replace("Arena map ID: 1134", "Arena map ID: 1135")),
    ("directory", lambda t: t.replace("ShadoPanArena", "ShadoPanArena2")),
    ("zone", lambda t: t.replace("AreaTable zone: 6732",
                                 "AreaTable zone: 6733")),
    ("expansion_field", lambda t: t.replace("map row: 4", "map row: 3")),
    ("wdt", lambda t: t.replace("848418", "848419")),
    ("bg_entry", lambda t: t.replace('Battleground entry: 757',
                                     'Battleground entry: 758')),
    ("max_players", lambda t: t.replace("MaxPlayersPerTeam 5",
                                        "MaxPlayersPerTeam 10")),
    ("levels", lambda t: t.replace("MinLvl 90, MaxLvl 120",
                                   "MinLvl 10, MaxLvl 120")),
    ("start_max_dist", lambda t: t.replace("StartMaxDist 0",
                                           "StartMaxDist 10")),
    ("weight", lambda t: t.replace("Weight 1", "Weight 0")),
    ("patch", lambda t: t.replace("patch 5.3.0", "patch 5.3.1")),
    ("removal_date", lambda t: t.replace("2019-03-20", "2019-03-21")),
    ("legacy_claim", lambda t: t.replace("No legacy duplicate",
                                         "One legacy duplicate")),
    ("legacy_ids", lambda t: t.replace("1505 vs 559", "1505 vs 557")),
    ("ws_ally", lambda t: t.replace("WorldSafeLoc 4534",
                                    "WorldSafeLoc 4544")),
    ("ws_horde", lambda t: t.replace("WorldSafeLoc 4535",
                                     "WorldSafeLoc 4545")),
    ("ws_go", lambda t: t.replace("WorldSafeLoc 4536",
                                  "WorldSafeLoc 4546")),
    ("t1_x", lambda t: t.replace("X: 491.476", "X: 492.476")),
    ("t1_y", lambda t: t.replace("Y: 633.332", "Y: 634.332")),
    ("t1_z", lambda t: t.replace("Z: 380.707", "Z: 381.707")),
    ("t1_facing", lambda t: t.replace("0.00848389 deg = 0.000148 rad",
                                      "0.00848389 deg = 0.001148 rad")),
    ("t2_x", lambda t: t.replace("X: 642.367", "X: 643.367")),
    ("t2_y", lambda t: t.replace("Y: 633.406", "Y: 634.406")),
    ("t2_z", lambda t: t.replace("Z: 380.705", "Z: 381.705")),
    ("t2_facing", lambda t: t.replace("180.283 deg = 3.14653 rad",
                                      "180.283 deg = 1.14653 rad")),
    ("go_x", lambda t: t.replace("X: 565.578", "X: 566.578")),
    ("go_z", lambda t: t.replace("Z: 380.704", "Z: 381.704")),
    ("gy_claim", lambda t: t.replace("No arena graveyard row exists",
                                     "An arena graveyard row exists")),
    ("dist", lambda t: t.replace("150.89 units", "160.89 units")),
    ("centre", lambda t: t.replace("about 566.921, 633.369",
                                   "about 566.931, 633.369")),
    ("start_to_centre", lambda t: t.replace("75.45 units", "85.45 units")),
    ("axis_x", lambda t: t.replace("150.89 apart on X", "160.89 apart on X")),
    ("axis_y", lambda t: t.replace("0.07 apart on Y", "1.07 apart on Y")),
    ("facing_claim", lambda t: t.replace("180 deg plus 0.283",
                                         "180 deg plus 0.000")),
    ("door_entry_id", lambda t: t.replace("entry, 212921", "entry, 212922")),
    ("g1_x", lambda t: t.replace("X: 501.932", "X: 502.932")),
    ("g1_y", lambda t: t.replace("Y: 633.429", "Y: 634.429")),
    ("g1_z", lambda t: t.replace("Z: 380.708", "Z: 381.708")),
    ("g1_orient", lambda t: t.replace("Orientation: 0.0262353 rad",
                                      "Orientation: 1.0262353 rad")),
    ("g2_x", lambda t: t.replace("X: 632.101", "X: 633.101")),
    ("g2_y", lambda t: t.replace("Y: 633.791", "Y: 634.791")),
    ("g2_orient", lambda t: t.replace("Orientation: 3.20989 rad",
                                      "Orientation: 1.20989 rad")),
    ("quat", lambda t: t.replace("Quaternion: 0, 0, 0, 0",
                                 "Quaternion: 0, 0, -1, 0")),
    ("quat_contrast", lambda t: t.replace("Tol'viron team 2 uses 0, 0, 0, 1",
                                          "Tol'viron team 2 uses 0, 0, 0, 0")),
    ("gate_gap", lambda t: t.replace("130.17 units", "140.17 units")),
    ("gate_start", lambda t: t.replace("10.46 units", "11.46 units")),
    ("gate_level", lambda t: t.replace("within 0.001 units",
                                       "within 1.001 units")),
    ("triggers", lambda t: t.replace("4536 and 4537", "4538 and 4539")),
    ("statue_count", lambda t: t.replace("Statue count: 2",
                                         "Statue count: 4")),
    ("platform_count", lambda t: t.replace("Platform count: 2",
                                           "Platform count: 3")),
    ("statues_verified", lambda t: t.replace("Statue positions: unverified",
                                             "Statue positions: verified")),
    ("objects", lambda t: t.replace("exactly four objects",
                                    "exactly five objects")),
    ("levels_claim", lambda t: t.replace("Two levels.", "Three levels.")),
    ("floor_band", lambda t: t.replace("380.704 to 380.708",
                                       "380.704 to 381.708")),
    ("platform_band", lambda t: t.replace("383.6809 to 383.6813",
                                          "383.6809 to 384.6813")),
    ("orb_step", lambda t: t.replace("2.9733 above gate 1",
                                     "3.9733 above gate 1")),
    ("dh_jump", lambda t: t.replace("Demon Hunter can double jump",
                                    "Warrior can double jump")),
    ("second_floor", lambda t: t.replace("no second floor",
                                         "a second floor")),
    ("buff_a_id", lambda t: t.replace("GO 184663", "GO 184665")),
    ("buff_b_id", lambda t: t.replace("GO 184664", "GO 184666")),
    ("buff_a_x", lambda t: t.replace("X: 566.6805", "X: 567.6805")),
    ("buff_a_y", lambda t: t.replace("Y: 602.2274", "Y: 603.2274")),
    ("buff_a_z", lambda t: t.replace("Z: 383.6813", "Z: 384.6813")),
    ("buff_a_orient", lambda t: t.replace("Orientation: 3.316144 rad",
                                          "Orientation: 2.316144 rad")),
    ("buff_b_x", lambda t: t.replace("X: 566.6563", "X: 567.6563")),
    ("buff_b_y", lambda t: t.replace("Y: 664.566", "Y: 665.566")),
    ("buff_b_z", lambda t: t.replace("Z: 383.6809", "Z: 384.6809")),
    ("buff_b_orient", lambda t: t.replace("Orientation: 2.460913 rad",
                                          "Orientation: 3.460913 rad")),
    ("buff_dist", lambda t: t.replace("31.14 units", "41.14 units")),
    ("buff_gap", lambda t: t.replace("62.34 units", "72.34 units")),
    ("buff_x_gap", lambda t: t.replace("0.024 units apart on X",
                                       "0.024 units apart on Y")),
    ("buff_step", lambda t: t.replace("about 2.97 above the arena",
                                      "about 3.97 above the arena")),
    ("spawn", lambda t: t.replace("Spawn: 60 s after the gates open",
                                  "Spawn: 90 s after the gates open")),
    ("respawn", lambda t: t.replace("Respawn after pickup: 120 s",
                                    "Respawn after pickup: 180 s")),
    ("spell", lambda t: t.replace("34709", "34708")),
    ("spell_dmg", lambda t: t.replace("+5% damage taken",
                                      "+10% damage taken")),
    ("wiki_delay", lambda t: t.replace("wiki quotes 90 s",
                                       "wiki quotes 120 s")),
    ("pickup_claim", lambda t: t.replace("No health, mana, haste",
                                         "Health, mana, haste")),
    ("worldstate", lambda t: t.replace("Worldstate 0xE1A",
                                       "Worldstate 0xE1B")),
    ("width_inflate", lambda t: t.replace(
        "=== 2. GATES ===",
        "=== 2. GATES AND A GREAT DEAL OF ADDITIONAL TEXT THAT MAKES THIS LINE FAR TOO LONG ===")),
]


def absence_stage(text, corpora):
    """Recompute the document's negative and count claims from the data."""
    sql = corpora["world_safe_locs (8.x)"]
    ttp = corpora["BattlegroundTTP.cpp"]
    lines, ok = [], True

    rows = [ln for ln in sql.splitlines() if re.search(r"\(\d+,1134,", ln)]
    want_rows = 3 if "No arena graveyard row exists on map 1134" in text else 4
    mark = "ok " if len(rows) == want_rows else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-32s claim %d  found %d  %s"
                 % ("graveyard rows on 1134", want_rows, len(rows), mark))

    gy = [ln for ln in rows if "Graveyard" in ln]
    wants_none = "No arena graveyard row exists on map 1134" in text
    mark = "ok " if (not gy) == wants_none else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-32s %-22s %s"
                 % ("any graveyard comment", "none expected" if wants_none
                    else "at least one expected", mark))

    objs = ttp.count("AddObject(")
    want_objs = 4 if "exactly four objects" in text else 5
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

    t1x = grab(r"X: (491\.476)")
    t2x = grab(r"X: (642\.367)")
    t1y, t2y = 633.332, 633.406
    gox, goy = 565.578, 631.54
    d1 = (501.932, 633.429)
    d2 = (632.101, 633.791)
    b1 = (566.6805, 602.2274)
    b2 = (566.6563, 664.566)

    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
    cx, cy = (t1x + t2x) / 2.0, (t1y + t2y) / 2.0

    checks = [
        ("start to start", dist((t1x, t1y), (t2x, t2y)),
         r"Distance start to start: (\d+\.\d+)"),
        ("start to centre", dist((t1x, t1y), (cx, cy)),
         r"Each start is (\d+\.\d+) units"),
        ("axis X", abs(t1x - t2x), r"(\d+\.\d+) apart on X"),
        ("axis Y", abs(t1y - t2y), r"(\d+\.\d+) apart on Y"),
        ("gameon to centre", dist((gox, goy), (cx, cy)),
         r"Game On target is (\d+\.\d+) units"),
        ("gate to gate", dist(d1, d2),
         r"Distance between the two gates: (\d+\.\d+)"),
        ("gate1 to start", dist(d1, (t1x, t1y)),
         r"Team 1 start stands (\d+\.\d+) units"),
        ("gate2 to start", dist(d2, (t2x, t2y)),
         r"Team 2 start stands (\d+\.\d+) units"),
        ("orb A to centre", dist(b1, (cx, cy)),
         r"About (\d+\.\d+) units from the arena centre\n\nShadow Sight B"),
        ("orb B to centre", dist(b2, (cx, cy)),
         r"About 31\.14 units from the arena centre[\s\S]*?About (\d+\.\d+) units"),
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
        lines.append("    %-20s doc %7.2f  recomputed %7.2f  %s"
                     % (label, want, got, mark))

    for deg_s in ("0.00848389", "180.283"):
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

    m = re.search(r"([\d.]+) above gate 1's\n(?:[\d.]+) and ([\d.]+) above gate 2's",
                  text)
    if not m:
        raise RuntimeError("orb step claims missing")
    for label, want_s, got in (
            ("orb A over gate 1", m.group(1), round(383.6813 - 380.708, 4)),
            ("orb B over gate 2", m.group(2), round(383.6809 - 380.704, 4))):
        want = float(want_s)
        mark = "ok " if abs(got - want) <= 0.0001 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %9.4f      recomputed %9.4f  %s"
                     % (label, want, got, mark))

    m = re.search(r"Arena centre: about (-?\d+\.\d+), (-?\d+\.\d+)", text)
    if not m:
        raise RuntimeError("centre claim missing")
    want_x, want_y = float(m.group(1)), float(m.group(2))
    for label, want, got in (("centre X", want_x, cx), ("centre Y", want_y, cy)):
        mark = "ok " if abs(got - want) <= 0.01 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %9.3f      recomputed %9.3f  %s"
                     % (label, want, got, mark))

    m = re.search(r"Only (\d+\.\d+) units apart on X", text)
    if m:
        want = float(m.group(1))
        got = round(abs(b1[0] - b2[0]), 3)
        mark = "ok " if abs(got - want) <= 0.001 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %9.3f      recomputed %9.3f  %s"
                     % ("orb X gap", want, got, mark))

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
    print("AUDIT: Arena_The_Tiger_s_Peak_COMPLETED.txt (Step 7)")
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
        "BattlegroundTTP.h": gh_content(TTP_REPO, TTP_H_PATH),
        "BattlegroundTTP.cpp": gh_content(TTP_REPO, TTP_PATH),
        "BattlegroundRL.cpp": gh_content(TTP_REPO, RL_PATH),
        "BattlegroundTVA.cpp": gh_content(TTP_REPO, TVA_PATH),
        "Map_ShadoPanArena.lua": gh_content(DM_REPO, DM_PATH),
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
        "distance changed": original.replace("150.89 units", "160.89 units"),
        "radians changed": original.replace("3.14653 rad", "1.14653 rad"),
        "orb step changed": original.replace("2.9733 above gate 1",
                                             "3.9733 above gate 1"),
        "centre changed": original.replace("about 566.921, 633.369",
                                           "about 566.961, 633.369"),
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
        "(4534,1134,",
        "(4544,1134,0,0,0,0,'Arena - Shado-Pan - Graveyard'),\n(4534,1134,")
    probe_corpora = dict(corpora)
    probe_corpora["world_safe_locs (8.x)"] = sql_broken
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
    probe = original.replace("X: 491.476", "X: 461.476")
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
