#!/usr/bin/env python3
"""Mutation-tested audit for Arena_Black_Rook_Hold_Arena_COMPLETED.txt (9)."""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import (gh_content, source_stage, mutation_probe,
                          coord_trace)

DELIVERABLE = ("/home/user/Junk/# Ai Research prompts/Arenas_complete/"
               "Arena_Black_Rook_Hold_Arena_COMPLETED.txt")

SQL_REPO = "TrinityCore/TrinityCore"
SQL_PATH = ("sql/old/8.x/world/19071_2020_06_17/"
            "2019_10_26_01_world.sql")
BRH_REPO = "HavenWoW/BFA-HavenCore"
BRH_PATH = ("src/server/game/Battlegrounds/Zones/BattlegroundBRH.cpp")
BRH_H_PATH = ("src/server/game/Battlegrounds/Zones/BattlegroundBRH.h")
BG_H_PATH = "src/server/game/Battlegrounds/Battleground.h"
ARENA_PATH = "src/server/game/Battlegrounds/Arena.cpp"
DM_REPO = "Ghostopheles/Datamine"
DM_PATH = "Datamine_Maps/Generated/Map_BlackRookHoldArena.lua"
TPL_REPO = "zTerragor/vSLDB"
TPL_PATH = "sql/updates/world/2021_11_03_world_Battleground_Template.sql"

SOURCE_TOKENS = {
    "world_safe_locs (8.x)": [
        ("ws 5120", "1504,1419.42,1255.49,34.1073,0"),
        ("ws 5121", "1504,1372.13,1247.19,33.0047,358.226"),
        ("ws 5122", "1504,1472.7,1275.16,32.1104,210.632"),
        ("map 1170 row", "1170,4382.98,-433.246,380.712,179.087"),
    ],
    "battleground_template": [
        ("bg 808 row", "(808, 0, 5, 90, 120, 5121, 5122, 0, 1, '', "
                      "'Black Rook Hold Arena')"),
    ],
    "BattlegroundBRH.cpp": [
        ("door 245763", "BG_BRH_OBJECT_TYPE_DOOR_1 = 245763"),
        ("door 245766", "BG_BRH_OBJECT_TYPE_DOOR_2 = 245766"),
        ("door 245767", "BG_BRH_OBJECT_TYPE_DOOR_3 = 245767"),
        ("door 245768", "BG_BRH_OBJECT_TYPE_DOOR_4 = 245768"),
        ("door 245770", "BG_BRH_OBJECT_TYPE_DOOR_5 = 245770"),
        ("door 245781", "BG_BRH_OBJECT_TYPE_DOOR_6 = 245781"),
        ("door 245762", "BG_BRH_OBJECT_TYPE_DOOR_7 = 245762"),
        ("door 245765", "BG_BRH_OBJECT_TYPE_DOOR_8 = 245765"),
        ("door 245769", "BG_BRH_OBJECT_TYPE_DOOR_9 = 245769"),
        ("anvil 249825", "BG_BRH_OBJECT_TYPE_ANVIL = 249825, //Wtf?"),
        ("open loop", "i < BG_BRH_OBJECT_DOOR_7"),
        ("close loop", "i < BG_BRH_OBJECT_MAX"),
        ("buff spawn", "SpawnBGObject(i, ARENA_COUNTDOWN_MAX)"),
        ("door 1 pos", "1464.32f, 1254.87f, 33.24f, 0.84f"),
        ("door 9 pos", "1424.42f, 1208.04f, 33.27f, 4.73f"),
        ("anvil pos", "1185.11f, 1404.49f, 65.18f, 1.57f"),
        ("buff A pos", "1423.24f, 1287.08f, 32.84f, 4.75f"),
        ("buff B pos", "1461.35f, 1225.18f,  33.0f, 2.59f"),
        ("buff respawn arg", "BgBrhGoPositions[10][7], BUFF_RESPAWN_TIME"),
    ],
    "Battleground.h": [
        ("buff respawn", "BUFF_RESPAWN_TIME               = 180"),
        ("countdown", "ARENA_COUNTDOWN_MAX             = 60"),
    ],
    "Arena.cpp": [
        ("base worldstate fn", "void Arena::FillInitialWorldStates"),
        ("alive green", "ARENA_WORLD_STATE_ALIVE_PLAYERS_GREEN"),
    ],
    "Map_BlackRookHoldArena.lua": [
        ("map name", 'MapName = "Black Rook Hold Arena"'),
        ("map id", "MapID = 1504"),
        ("directory", "Directory = [[BlackrookHoldArena]]"),
        ("instance type", "InstanceType = 4"),
        ("expansion", "ExpansionID = 6"),
        ("wdt", "WDTFileDataID: 1244360"),
    ],
}

STATIC_CHECKS = [
    ("file_exists", lambda t: os.path.exists(DELIVERABLE)),
    ("min_lines", lambda t: len(t.splitlines()) >= 200),
    ("max_width_78", lambda t: all(len(l) <= 78 for l in t.splitlines())),
    ("title_completed",
     lambda t: t.splitlines()[0].endswith("- COMPLETED ===")),
    ("title_map_1504", lambda t: "MAP 1504" in t.splitlines()[0]),

    ("map_1504", lambda t: "Arena map ID: 1504" in t),
    ("dir", lambda t: "Map.dbc directory: BlackrookHoldArena\n" in t),
    ("instance_type_4", lambda t: "InstanceType: 4" in t),
    ("zone_7816", lambda t: "AreaTable zone: 7816" in t),
    ("subzone", lambda t: "subzone Raven's Glory" in t),
    ("expansion_field_6", lambda t: "ExpansionID field in the map row: 6" in t),
    ("wdt", lambda t: "1244360" in t),
    ("no_legacy", lambda t: "No legacy duplicate" in t),
    ("bg_808", lambda t: 'Battleground entry: 808 "Black Rook Hold Arena"'
                         in t),
    ("max_players_5", lambda t: "MaxPlayersPerTeam 5" in t),
    ("lvl_90_120", lambda t: "MinLvl 90, MaxLvl 120" in t),
    ("start_max_dist_0", lambda t: "StartMaxDist 0" in t),
    ("weight_1", lambda t: "Weight 1" in t),
    ("patch_703", lambda t: "patch 7.0.3" in t),
    ("ninth", lambda t: "Ninth arena map counting" in t),
    ("location", lambda t: "Location: outside Black Rook Hold" in t),
    ("map_1170_caution", lambda t: "map 1170 also carries a row" in t),
    ("map_1170_xy", lambda t: "4382.98, -433.246" in t),

    ("ws_5121", lambda t: "WorldSafeLoc 5121" in t),
    ("ws_5122", lambda t: "WorldSafeLoc 5122" in t),
    ("ws_5120", lambda t: "WorldSafeLoc 5120" in t),
    ("t1_x", lambda t: "X: 1372.13" in t),
    ("t1_y", lambda t: "Y: 1247.19" in t),
    ("t1_z", lambda t: "Z: 33.0047" in t),
    ("t1_facing", lambda t: "358.226 deg = 6.2522 rad" in t),
    ("t2_x", lambda t: "X: 1472.7" in t),
    ("t2_y", lambda t: "Y: 1275.16" in t),
    ("t2_z", lambda t: "Z: 32.1104" in t),
    ("t2_facing", lambda t: "210.632 deg = 3.6762 rad" in t),
    ("gy_x", lambda t: "X: 1419.42" in t),
    ("gy_y", lambda t: "Y: 1255.49" in t),
    ("gy_z", lambda t: "Z: 34.1073" in t),
    ("no_gameon", lambda t: "There is no Game On row on map 1504" in t),
    ("dist_starts", lambda t: "104.39 units" in t),
    ("centre", lambda t: "about 1422.41, 1261.18" in t),
    ("half", lambda t: "52.19 units" in t),
    ("axis_x", lambda t: "100.57 apart on X, 27.97 apart on Y" in t),
    ("bearing", lambda t: "Bearing from Team 1 to Team 2 is 15.54 deg" in t),
    ("off1", lambda t: "17.32 deg off that bearing" in t),
    ("off2", lambda t: "15.09 deg off the reverse" in t),
    ("gy_to_centre", lambda t: "6.43 units" in t),
    ("gy_raised", lambda t: "0.84 above the highest door" in t),
    ("step_bound", lambda t: "the step is under 1.2 units" in t),

    ("nine_doors", lambda t: "nine door game objects" in t),
    ("door_table_ids", lambda t: all(x in t for x in
                                     ("245763", "245766", "245767", "245768",
                                      "245770", "245781", "245762", "245765",
                                      "245769"))),
    ("door1_xy", lambda t: "245763  1464.32  1254.87" in t),
    ("door9_xy", lambda t: "245769  1424.42  1208.04" in t),
    ("door_z_band", lambda t: "Z 33.21 to 33.27" in t),
    ("close_all", lambda t: "spawns every object from door 1" in t),
    ("open_six", lambda t: "only\n  doors 1 to 6 are ever opened" in t
                           or "only doors 1 to 6" in t),
    ("doors_unopened", lambda t: "245762, 245765 and 245769" in t),
    ("unopened_unverified", lambda t: "loop\n  off-by-three, is unverified"
                                      in t or "off-by-three" in t),

    ("one_pillar", lambda t: "Pillar count: 1" in t),
    ("liq_quote", lambda t: "statue in the centre of the map that\n   functions as a pillar" in t),
    ("platform_unverified", lambda t: "Platform position: unverified" in t),
    ("rooms", lambda t: "remain accessible after the gates" in t),
    ("pillar_pos_unverified", lambda t: "Pillar position: unverified" in t),

    ("two_levels", lambda t: "Two levels plus the entry rooms" in t),
    ("floor_band", lambda t: "Arena floor (door band):      33.21 to 33.27" in t),
    ("platform_z", lambda t: "34.1073" in t),
    ("stairs", lambda t: "stairs that surround\nmost of it" in t
                         or "stairs that surround most of it" in t),
    ("no_second_floor", lambda t: "No second floor" in t),

    ("role_melee", lambda t: "Melee DPS:" in t),
    ("role_ranged", lambda t: "Ranged DPS:" in t),
    ("role_healer", lambda t: "Healers:" in t),
    ("cover_middle", lambda t: "cover here\nis in the middle" in t
                               or "cover here is in the middle" in t),

    ("buff_a_id", lambda t: "Shadow Sight A (GO 184663)" in t),
    ("buff_b_id", lambda t: "Shadow Sight B (GO 184664)" in t),
    ("buff_a_x", lambda t: "X: 1423.24" in t),
    ("buff_a_y", lambda t: "Y: 1287.08" in t),
    ("buff_a_z", lambda t: "Z: 32.84" in t),
    ("buff_b_x", lambda t: "X: 1461.35" in t),
    ("buff_b_y", lambda t: "Y: 1225.18" in t),
    ("buff_b_z", lambda t: "Z: 33.0" in t),
    ("buff_a_orient", lambda t: "Orientation: 4.75 rad" in t),
    ("buff_b_orient", lambda t: "Orientation: 2.59 rad" in t),
    ("buff_dists", lambda t: "25.92 units" in t and "53.02 units" in t),
    ("buff_gap", lambda t: "72.69 units" in t),
    ("buff_asym", lambda t: "a measured\ndifference of 27.11 units" in t
                            or "27.10 units" in t),
    ("spawn_60", lambda t: "60 s after the gates open (ARENA_COUNTDOWN_MAX)" in t),
    ("respawn_180", lambda t: "180 s (BUFF_RESPAWN_TIME)" in t),
    ("spell", lambda t: "34709" in t),
    ("spell_dmg", lambda t: "+5% damage taken" in t),
    ("wiki_90s", lambda t: "wiki quotes 90 s" in t),
    ("no_health", lambda t: "No health, mana, haste" in t),
    ("twelve_objects", lambda t: "twelve objects: nine doors, one anvil" in t),
    ("anvil", lambda t: "entry 249825" in t),
    ("anvil_x", lambda t: "X: 1185.11" in t),
    ("anvil_y", lambda t: "Y: 1404.49" in t),
    ("anvil_z", lambda t: "Z: 65.18" in t),
    ("anvil_dist", lambda t: "277.22 units" in t),
    ("anvil_above", lambda t: "31.98 units" in t),

    ("no_0xe1a", lambda t: "does not send\nworldstate 0xE1A" in t
                           or "does not send worldstate 0xE1A" in t),
    ("no_oob", lambda t: "No out-of-bounds or under-map return points" in t),
    ("no_trigger_override", lambda t: "no area-trigger overrides" in t),
    ("anvil_comment", lambda t: "comment questioning" in t),
    ("door_warning", lambda t: "three door\nobjects stay shut" in t
                               or "three door objects stay shut" in t),

    ("sources", lambda t: "Sources:" in t),
    ("unverified", lambda t: "Unverified:" in t),
    ("src_brh", lambda t: "BattlegroundBRH.cpp" in t),
    ("src_datamine", lambda t: "Map_BlackRookHoldArena.lua" in t),
    ("src_wiki", lambda t: 'Warcraft Wiki "Black Rook Hold Arena"' in t),
    ("src_liquipedia", lambda t: 'Liquipedia "Black Rook Hold Arena"' in t),
]

MUTATIONS = [
    ("map_id", lambda t: t.replace("Arena map ID: 1504",
                                   "Arena map ID: 1505")),
    ("directory", lambda t: t.replace("BlackrookHoldArena",
                                      "BlackrookHoldArena2")),
    ("zone", lambda t: t.replace("AreaTable zone: 7816",
                                 "AreaTable zone: 7817")),
    ("expansion_field", lambda t: t.replace("map row: 6", "map row: 4")),
    ("wdt", lambda t: t.replace("1244360", "1244361")),
    ("bg_entry", lambda t: t.replace('Battleground entry: 808',
                                     'Battleground entry: 809')),
    ("max_players", lambda t: t.replace("MaxPlayersPerTeam 5",
                                        "MaxPlayersPerTeam 10")),
    ("levels", lambda t: t.replace("MinLvl 90, MaxLvl 120",
                                   "MinLvl 10, MaxLvl 120")),
    ("start_max_dist", lambda t: t.replace("StartMaxDist 0",
                                           "StartMaxDist 10")),
    ("weight", lambda t: t.replace("Weight 1", "Weight 0")),
    ("patch", lambda t: t.replace("patch 7.0.3", "patch 7.0.4")),
    ("ninth", lambda t: t.replace("Ninth arena map", "Tenth arena map")),
    ("ws_ally", lambda t: t.replace("WorldSafeLoc 5121",
                                    "WorldSafeLoc 5131")),
    ("ws_horde", lambda t: t.replace("WorldSafeLoc 5122",
                                     "WorldSafeLoc 5132")),
    ("ws_gy", lambda t: t.replace("WorldSafeLoc 5120",
                                  "WorldSafeLoc 5130")),
    ("t1_x", lambda t: t.replace("X: 1372.13", "X: 1373.13")),
    ("t1_y", lambda t: t.replace("Y: 1247.19", "Y: 1248.19")),
    ("t1_z", lambda t: t.replace("Z: 33.0047", "Z: 34.0047")),
    ("t1_facing", lambda t: t.replace("358.226 deg = 6.2522 rad",
                                      "358.226 deg = 5.2522 rad")),
    ("t2_x", lambda t: t.replace("X: 1472.7", "X: 1473.7")),
    ("t2_y", lambda t: t.replace("Y: 1275.16", "Y: 1276.16")),
    ("t2_z", lambda t: t.replace("Z: 32.1104", "Z: 33.1104")),
    ("t2_facing", lambda t: t.replace("210.632 deg = 3.6762 rad",
                                      "210.632 deg = 2.6762 rad")),
    ("gy_x", lambda t: t.replace("X: 1419.42", "X: 1420.42")),
    ("gy_y", lambda t: t.replace("Y: 1255.49", "Y: 1256.49")),
    ("gy_z", lambda t: t.replace("Z: 34.1073", "Z: 35.1073")),
    ("gameon_claim", lambda t: t.replace("There is no Game On row on map 1504",
                                         "There is one Game On row on 1504")),
    ("dist", lambda t: t.replace("104.39 units", "114.39 units")),
    ("centre", lambda t: t.replace("about 1422.41, 1261.18",
                                   "about 1422.51, 1261.18")),
    ("half", lambda t: t.replace("52.19 units", "62.19 units")),
    ("axis", lambda t: t.replace("100.57 apart on X", "110.57 apart on X")),
    ("bearing", lambda t: t.replace("is 15.54 deg", "is 16.54 deg")),
    ("off1", lambda t: t.replace("17.32 deg off", "18.32 deg off")),
    ("off2", lambda t: t.replace("15.09 deg off", "16.09 deg off")),
    ("gy_centre", lambda t: t.replace("6.43 units", "7.43 units")),
    ("gy_raised", lambda t: t.replace("0.84 above the highest door",
                                      "1.84 above the highest door")),
    ("step_bound", lambda t: t.replace("the step is under 1.2 units",
                                       "the step is under 2.2 units")),
    ("door_count", lambda t: t.replace("nine door game objects",
                                       "ten door game objects")),
    ("door1_id", lambda t: t.replace("245763  1464.32",
                                     "245764  1464.32")),
    ("door9_id", lambda t: t.replace("245769  1424.42",
                                     "245778  1424.42")),
    ("door1_xy", lambda t: t.replace("245763  1464.32  1254.87",
                                     "245763  1465.32  1254.87")),
    ("door9_xy", lambda t: t.replace("245769  1424.42  1208.04",
                                     "245769  1425.42  1208.04")),
    ("door_z_band", lambda t: t.replace("Z 33.21 to 33.27",
                                        "Z 33.21 to 34.27")),
    ("open_six", lambda t: t.replace("doors 1 to 6 are ever opened",
                                     "doors 1 to 9 are ever opened")),
    ("unopened_ids", lambda t: t.replace("245762, 245765 and 245769",
                                         "245762, 245765 and 245768")),
    ("pillar_count", lambda t: t.replace("Pillar count: 1",
                                         "Pillar count: 3")),
    ("pillar_pos", lambda t: t.replace("Pillar position: unverified",
                                       "Pillar position: verified")),
    ("rooms_claim", lambda t: t.replace("remain accessible after the gates",
                                        "close after the gates")),
    ("levels_claim", lambda t: t.replace("Two levels plus the entry rooms",
                                         "Three levels plus the entry rooms")),
    ("floor_band", lambda t: t.replace("33.21 to 33.27\n", "33.21 to 34.27\n", 1)),
    ("stairs_claim", lambda t: t.replace("stairs that surround\nmost of it",
                                         "stairs that skip the\nplatform")),
    ("second_floor", lambda t: t.replace("No second floor",
                                         "One second floor")),
    ("buff_a_id", lambda t: t.replace("GO 184663", "GO 184665")),
    ("buff_b_id", lambda t: t.replace("GO 184664", "GO 184666")),
    ("buff_a_x", lambda t: t.replace("X: 1423.24", "X: 1424.24")),
    ("buff_a_y", lambda t: t.replace("Y: 1287.08", "Y: 1288.08")),
    ("buff_a_z", lambda t: t.replace("Z: 32.84", "Z: 33.84")),
    ("buff_b_x", lambda t: t.replace("X: 1461.35", "X: 1462.35")),
    ("buff_b_y", lambda t: t.replace("Y: 1225.18", "Y: 1226.18")),
    ("buff_b_z", lambda t: t.replace("Z: 33.0", "Z: 34.0")),
    ("buff_a_orient", lambda t: t.replace("Orientation: 4.75 rad",
                                          "Orientation: 5.75 rad")),
    ("buff_b_orient", lambda t: t.replace("Orientation: 2.59 rad",
                                          "Orientation: 3.59 rad")),
    ("buff_dist", lambda t: t.replace("25.92 units", "26.92 units")),
    ("buff_gap", lambda t: t.replace("72.69 units", "73.69 units")),
    ("buff_asym", lambda t: t.replace("27.11 units", "28.11 units")),
    ("spawn", lambda t: t.replace("60 s after the gates open",
                                  "90 s after the gates open")),
    ("respawn", lambda t: t.replace("180 s (BUFF_RESPAWN_TIME)",
                                    "240 s (BUFF_RESPAWN_TIME)")),
    ("spell", lambda t: t.replace("34709", "34708")),
    ("spell_dmg", lambda t: t.replace("+5% damage taken",
                                      "+10% damage taken")),
    ("pickup_claim", lambda t: t.replace("No health, mana, haste",
                                         "Health, mana, haste")),
    ("object_count", lambda t: t.replace("twelve objects: nine doors",
                                         "eleven objects: nine doors")),
    ("anvil_id", lambda t: t.replace("entry 249825", "entry 249826")),
    ("anvil_x", lambda t: t.replace("X: 1185.11", "X: 1186.11")),
    ("anvil_dist", lambda t: t.replace("277.22 units", "278.22 units")),
    ("anvil_above", lambda t: t.replace("31.98 units", "32.98 units")),
    ("worldstate_claim", lambda t: t.replace("does not send\nworldstate 0xE1A",
                                             "does send\nworldstate 0xE1A")),
    ("oob_claim", lambda t: t.replace(
        "No out-of-bounds or under-map return points",
        "Three out-of-bounds or under-map return points")),
    ("door_warning", lambda t: t.replace("three door\nobjects stay shut",
                                        "two door\nobjects stay shut")),
    ("width_inflate", lambda t: t.replace(
        "=== 2. GATES AND THE NINE DOOR OBJECTS ===",
        "=== 2. GATES AND THE NINE DOOR OBJECTS AND A GREAT DEAL OF EXTRA TEXT THAT MAKES THIS LINE TOO LONG ===")),
]


def absence_stage(text, corpora):
    """Recompute negative and count claims from the source data."""
    sql = corpora["world_safe_locs (8.x)"]
    brh = corpora["BattlegroundBRH.cpp"]
    flat = re.sub(r"\s+", " ", text)
    lines, ok = [], True

    rows = [ln for ln in sql.splitlines() if re.search(r"\(\d+,1504,", ln)]
    want_rows = 3 if "There is no Game On row on map 1504" in flat else 4
    mark = "ok " if len(rows) == want_rows else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-32s claim %d  found %d  %s"
                 % ("rows on map 1504", want_rows, len(rows), mark))

    opens = re.search(r"for \(uint32 i = BG_BRH_OBJECT_DOOR_1; "
                      r"i < BG_BRH_OBJECT_DOOR_(\d+); \+\+i\)\s*\n\s*DoorOpen",
                      brh)
    want_open = 6 if "doors 1 to 6 are ever opened" in flat else 9
    got_open = int(opens.group(1)) - 1 if opens else -1
    mark = "ok " if got_open == want_open else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-32s claim %d  found %d  %s"
                 % ("doors opened by the loop", want_open, got_open, mark))

    doors = len(re.findall(r"BG_BRH_OBJECT_TYPE_DOOR_\d+ = \d+", brh))
    want_doors = 9 if "nine door game objects" in flat else 10
    mark = "ok " if doors == want_doors else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-32s claim %d  found %d  %s"
                 % ("door entries in zone", want_doors, doors, mark))

    objs = brh.count("AddObject(")
    want_objs = 12 if "twelve objects" in flat else 11
    mark = "ok " if objs == want_objs else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-32s claim %d  found %d  %s"
                 % ("AddObject calls in zone", want_objs, objs, mark))

    has_trig = "HandleAreaTrigger" in brh
    wants_trig_none = "there are no area-trigger overrides" in flat
    mark = "ok " if has_trig != wants_trig_none else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-32s %-22s %s"
                 % ("zone overrides area triggers",
                    "no expected" if wants_trig_none else "yes expected", mark))

    has_ws = "BRH::FillInitialWorldStates" in brh
    wants_none = "does not send worldstate 0xE1A" in flat
    mark = "ok " if has_ws != wants_none else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-32s %-22s %s"
                 % ("zone overrides worldstates",
                    "no expected" if wants_none else "yes expected", mark))

    return ok, lines


def derived_stage(text):
    def grab(pattern):
        m = re.search(pattern, text)
        if not m:
            raise RuntimeError("pattern not found: %s" % pattern)
        return float(m.group(1))

    t1x = grab(r"X: (1372\.13)")
    t2x = grab(r"X: (1472\.7)")
    t1y, t2y = 1247.19, 1275.16
    gy = (1419.42, 1255.49)
    b1 = (1423.24, 1287.08)
    b2 = (1461.35, 1225.18)
    anvil = (1185.11, 1404.49)

    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
    cx, cy = (t1x + t2x) / 2.0, (t1y + t2y) / 2.0

    checks = [
        ("start to start", dist((t1x, t1y), (t2x, t2y)),
         r"Distance start to start: (\d+\.\d+)"),
        ("start to centre", dist((t1x, t1y), (cx, cy)),
         r"Each start is (\d+\.\d+) units"),
        ("axis X", abs(t1x - t2x), r"(\d+\.\d+) apart on X"),
        ("axis Y", abs(t1y - t2y), r"(\d+\.\d+) apart on Y"),
        ("graveyard to centre", dist(gy, (cx, cy)),
         r"Graveyard is (\d+\.\d+) units"),
        ("orb A to centre", dist(b1, (cx, cy)),
         r"About (\d+\.\d+) units from the start midpoint\n\nShadow Sight B"),
        ("orb B to centre", dist(b2, (cx, cy)),
         r"About 25\.92 units from the start midpoint[\s\S]*?About (\d+\.\d+) units"),
        ("orb to orb", dist(b1, b2),
         r"orbs are (\d+\.\d+) units apart"),
        ("anvil to centre", dist(anvil, (cx, cy)),
         r"That is (\d+\.\d+) units from the arena midpoint"),
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

    for deg_s in ("358.226", "210.632"):
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

    m = re.search(r"Midpoint of the two starts: about (-?\d+\.\d+), "
                  r"(-?\d+\.\d+)", text)
    if not m:
        raise RuntimeError("midpoint claim missing")
    for label, want, got in (("midpoint X", float(m.group(1)), cx),
                             ("midpoint Y", float(m.group(2)), cy)):
        mark = "ok " if abs(got - want) <= 0.01 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %9.2f      recomputed %9.2f  %s"
                     % (label, want, got, mark))

    bearing = math.degrees(math.atan2(t2y - t1y, t2x - t1x)) % 360
    want_b = grab(r"Bearing from Team 1 to Team 2 is (\d+\.\d+) deg")
    mark = "ok " if abs(bearing - want_b) <= 0.01 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.2f      recomputed %8.2f  %s"
                 % ("bearing 1->2", want_b, bearing, mark))

    for label, face, pattern in (
            ("T1 off bearing", 358.226, r"([\d.]+) deg off that bearing"),
            ("T2 off bearing", 210.632, r"([\d.]+) deg off the reverse")):
        want = grab(pattern)
        ref = bearing if label.startswith("T1") else (bearing + 180) % 360
        diff = abs(face - ref)
        diff = min(diff, 360 - diff)
        mark = "ok " if abs(diff - want) <= 0.01 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %8.2f      recomputed %8.2f  %s"
                     % (label, want, diff, mark))

    want_raise = grab(r"([\d.]+) above the highest door")
    got_raise = round(34.1073 - 33.27, 2)
    mark = "ok " if abs(got_raise - want_raise) <= 0.01 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.2f      recomputed %8.2f  %s"
                 % ("platform raise", want_raise, got_raise, mark))

    want_hi = grab(r"([\d.]+) above the\n  Team 1 start")
    got_hi = round(34.1073 - 33.0047, 2)
    mark = "ok " if abs(got_hi - want_hi) <= 0.01 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.2f      recomputed %8.2f  %s"
                 % ("raise over T1", want_hi, got_hi, mark))

    want_asym = grab(r"a measured\ndifference of ([\d.]+) units")
    got_asym = round(abs(dist(b1, (cx, cy)) - dist(b2, (cx, cy))), 2)
    mark = "ok " if abs(got_asym - want_asym) <= 0.01 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.2f      recomputed %8.2f  %s"
                 % ("orb asymmetry", want_asym, got_asym, mark))

    return ok, lines


def door_table_stage(text, corpora):
    """Verify every row of the document's door table against the source."""
    brh = corpora["BattlegroundBRH.cpp"]
    positions = []
    for m in re.finditer(r"\{\s*(-?[\d.]+)f,\s*(-?[\d.]+)f,\s*(-?[\d.]+)f,"
                         r"\s*(-?[\d.]+)f,\s*(-?[\d.]+)f,\s*(-?[\d.]+)f,"
                         r"\s*(-?[\d.]+)f,\s*(-?[\d.]+)f\s*\}", brh):
        positions.append(tuple(float(m.group(i)) for i in (1, 2, 3, 4)))
    entries = [int(e) for e in re.findall(
        r"BG_BRH_OBJECT_TYPE_DOOR_\d+ = (\d+)", brh)]

    rows = []
    for line in text.splitlines():
        m = re.match(r"\s{2}(\d)\s+(\d{6})\s+(-?[\d.]+)\s+(-?[\d.]+)\s+"
                     r"(-?[\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$", line)
        if m:
            rows.append((int(m.group(1)), int(m.group(2)), float(m.group(3)),
                         float(m.group(4)), float(m.group(5)), float(m.group(6)),
                         float(m.group(7))))

    t1x = float(re.search(r"X: (1372\.13)", text).group(1))
    t2x = float(re.search(r"X: (1472\.7)", text).group(1))
    cx, cy = (t1x + t2x) / 2.0, (1247.19 + 1275.16) / 2.0

    lines, ok = [], True
    if len(rows) != 9:
        return False, ["    door table rows: found %d, want 9" % len(rows)]
    if len(positions) < 9 or len(entries) < 9:
        return False, ["    source array/entries short: %d/%d"
                       % (len(positions), len(entries))]

    for idx, entry, x, y, z, o, radius in rows:
        px, py, pz, po = positions[idx - 1]
        good = (abs(px - x) < 1e-6 and abs(py - y) < 1e-6
                and abs(pz - z) < 1e-6 and abs(po - o) < 1e-6)
        entry_ok = (entry == entries[idx - 1])
        want_r = round(math.hypot(x - cx, y - cy), 1)
        radius_ok = abs(want_r - radius) <= 0.05
        if not (good and entry_ok and radius_ok):
            ok = False
        lines.append("    door %d  entry %s  xyz/o %s  radius %s"
                     % (idx, "ok" if entry_ok else "BAD",
                        "ok" if good else "BAD",
                        "ok" if radius_ok else "BAD"))
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
    print("AUDIT: Arena_Black_Rook_Hold_Arena_COMPLETED.txt (Step 9)")
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
        "BattlegroundBRH.cpp": gh_content(BRH_REPO, BRH_PATH),
        "Battleground.h": gh_content(BRH_REPO, BG_H_PATH),
        "Arena.cpp": gh_content(BRH_REPO, ARENA_PATH),
        "Map_BlackRookHoldArena.lua": gh_content(DM_REPO, DM_PATH),
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
        "distance changed": original.replace("104.39 units", "114.39 units"),
        "radians changed": original.replace("6.2522 rad", "5.2522 rad"),
        "bearing changed": original.replace("is 15.54 deg", "is 16.54 deg"),
        "raise changed": original.replace("0.84 above the highest door",
                                          "1.84 above the highest door"),
        "centre changed": original.replace("about 1422.41, 1261.18",
                                           "about 1422.51, 1261.18"),
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
        "(5120,1504,",
        "(5130,1504,0,0,0,0,'Blackrook Hold Arena - Game On'),\n(5120,1504,")
    brh_broken = corpora["BattlegroundBRH.cpp"].replace(
        "i < BG_BRH_OBJECT_DOOR_7", "i < BG_BRH_OBJECT_DOOR_9")
    probe_corpora = dict(corpora)
    probe_corpora["world_safe_locs (8.x)"] = sql_broken
    probe_corpora["BattlegroundBRH.cpp"] = brh_broken
    if absence_stage(original, probe_corpora)[0]:
        print("    absence stage did not react to changed data")
        return 1
    print("    absence stage reacts to changed data (verified)")

    print("\n[6] Door table verified row by row against the source")
    ok, lines = door_table_stage(original, corpora)
    for line in lines:
        print(line)
    if not ok:
        print("    DOOR TABLE DOES NOT MATCH THE SOURCE")
        return 1
    probe = original.replace("  3      245767  1384.61  1232.35  33.27  2.86         47.5",
                             "  3      245767  1384.61  1232.35  33.27  2.86         57.5")
    if probe == original or door_table_stage(probe, corpora)[0]:
        print("    door table stage did not react to a changed radius")
        return 1
    print("    door table stage reacts to a wrong row (verified)")

    print("\n[7] No-invented-coordinates trace")
    ok, lines, _ = coord_trace(original, corpora)
    for line in lines:
        print(line)
    if not ok:
        print("    INVENTED COORDINATES FOUND")
        return 1
    probe = original.replace("X: 1372.13", "X: 1342.13")
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
