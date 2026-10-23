#!/usr/bin/env python3
"""Mutation-tested audit for Arena_Mugambala_COMPLETED.txt (Step 11).

Eight independent stages:
  1. static claims inside the document
  2. mutation testing: every claim must fail when its value is altered
  3. source cross-check: every quoted value must exist upstream
  4. derived arithmetic recomputed from the source rows
  5. negative claims recomputed from the source data
  6. coordinate trace: no number may be invented
  7. door and orb positions parsed out of BattlegroundMB.cpp
  8. the implemented case: switch, zone file and doc claims

Unlike Step 10 this arena is implemented, so stage 8 asserts the
positive facts (case exists, BattlegroundMB is constructed) instead
of an absence.
"""

import math
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import (gh_content, source_stage, mutation_probe,
                          coord_trace)

DELIVERABLE = ("/home/user/Junk/# Ai Research prompts/Arenas-completed/"
               "Arena_Mugambala_COMPLETED.txt")

SQL_REPO = "TrinityCore/TrinityCore"
SQL_PATH = ("sql/old/8.x/world/19071_2020_06_17/"
            "2019_10_26_01_world.sql")
HP_REPO = "HavenWoW/BFA-HavenCore"
SD_PATH = "src/server/game/Miscellaneous/SharedDefines.h"
BGM_PATH = "src/server/game/Battlegrounds/BattlegroundMgr.cpp"
BG_H_PATH = "src/server/game/Battlegrounds/Battleground.h"
MB_H_PATH = "src/server/game/Battlegrounds/Zones/BattlegroundMB.h"
MB_CPP_PATH = "src/server/game/Battlegrounds/Zones/BattlegroundMB.cpp"
ZONES_PATH = "src/server/game/Battlegrounds/Zones"
DM_REPO = "Ghostopheles/Datamine"
DM_PATH = "Datamine_Maps/Generated/Map_ZandalariArena.lua"
TPL_REPO = "zTerragor/vSLDB"
TPL_PATH = "sql/updates/world/2021_11_03_world_Battleground_Template.sql"

START_IDS = (6616, 6617)
GO_ID = 6895
MAP_ROWS = (6616, 6617, 6895)

SOURCE_TOKENS = {
    "world_safe_locs (8.x)": [
        ("ws 6616", "6616,1911,-1935.1,1233.3,34.7009,132.874"),
        ("ws 6617", "6617,1911,-1934.25,1369.32,34.4306,226.605"),
        ("ws 6895", "6895,1911,-1938.79,1299.93,34.4306,0"),
        ("comment 6616",
         "Arena - Zandalar - Teleport Target - Team 1 (East)"),
        ("comment 6617",
         "Arena - Zandalar - Teleport Target - Team 2 (West)"),
        ("comment 6895", "Arena - Zandalar - Teleport Target - Game On"),
    ],
    "battleground_template": [
        ("bg 903 row", "(903, 0, 5, 90, 120, 6616, 6617, 0, 1, '', "
                        "'Arena Bfa Mugambala')"),
    ],
    "SharedDefines.h": [
        ("mugambala enum", "BATTLEGROUND_MUGAMBALA      = 903"),
        ("hook point enum", "BATTLEGROUND_HOOK_POINT     = 897"),
    ],
    "BattlegroundMgr.cpp": [
        ("mugambala case", "case BATTLEGROUND_MUGAMBALA:"),
        ("constructs MB class",
         "bg = new BattlegroundMB(*(BattlegroundMB*)bg_template);"),
        ("default branch", "default:"),
        ("null instance", "return nullptr;"),
    ],
    "BattlegroundMB.h": [
        ("door 1 entry", "BG_MB_OBJECT_TYPE_DOOR_1 = 250431, "
                         "// Esta es la puerta de la Horda"),
        ("door 2 entry", "BG_MB_OBJECT_TYPE_DOOR_2 = 250430, "
                         "// Esta es la puerta de la Alianza"),
        ("buff 1 entry", "BG_MB_OBJECT_TYPE_BUFF_1 = 184663, "
                         "// Buff Originales Arenas Mugambala"),
        ("buff 2 entry", "BG_MB_OBJECT_TYPE_BUFF_2 = 184664  "
                         "// Buff 2 Originales Arenas Mugambala"),
    ],
    "BattlegroundMB.cpp": [
        ("door 1 position",
         "AddObject(BG_MB_OBJECT_DOOR_1, BG_MB_OBJECT_TYPE_DOOR_1, "
         "-1947.074707f, 1355.202515f, 34.755638f, 3.816283f"),
        ("door 2 position",
         "AddObject(BG_MB_OBJECT_DOOR_2, BG_MB_OBJECT_TYPE_DOOR_2, "
         "-1961.725952f, 1354.591675f, 34.430664f, 4.683993f"),
        ("buff 1 position",
         "AddObject(BG_MB_OBJECT_BUFF_1, BG_MB_OBJECT_TYPE_BUFF_1, "
         "-1962.612305f, 1245.579956f, 34.431129f, 1.652806f"),
        ("buff 2 position",
         "AddObject(BG_MB_OBJECT_BUFF_2, BG_MB_OBJECT_TYPE_BUFF_2, "
         "-1962.612305f, 1245.579956f, 34.431129f, 1.652806f, "
         "0.0f, 0.70068f"),
        ("snifer comment", "Door is custom need snifer"),
        ("orb respawn", "SpawnBGObject(i, 60);"),
        ("door spawn", "SpawnBGObject(i, RESPAWN_IMMEDIATELY);"),
        ("trigger 4536", "case 4536:"),
        ("trigger 4537", "case 4537:"),
        ("worldstate", "packet.Worldstates.emplace_back(0xE1A, 1);"),
        ("generic trigger",
         "Battleground::HandleAreaTrigger(player, trigger, entered);"),
        ("door loop", "for (uint32 i = BG_MB_OBJECT_DOOR_1; "
                      "i <= BG_MB_OBJECT_DOOR_2; ++i)"),
        ("buff loop", "for (uint32 i = BG_MB_OBJECT_BUFF_1; "
                      "i <= BG_MB_OBJECT_BUFF_2; ++i)"),
    ],
    "Battleground.h": [
        ("addobject signature", "float rotation3, uint32 respawnTime = 0"),
    ],
    "Map_ZandalariArena.lua": [
        ("map name", 'MapName = "Mugambala"'),
        ("map id", "MapID = 1911"),
        ("directory", "Directory = [[ZandalariArena]]"),
        ("instance type", "InstanceType = 4"),
        ("expansion", "ExpansionID = 7"),
        ("wdt", "WDTFileDataID: 1890596"),
    ],
}


def flat(text):
    return re.sub(r"\s+", " ", text)


STATIC_CHECKS = [
    ("file_exists", lambda t: os.path.exists(DELIVERABLE)),
    ("min_lines", lambda t: len(t.splitlines()) >= 250),
    ("max_width_78", lambda t: all(len(l) <= 78 for l in t.splitlines())),
    ("title_completed",
     lambda t: t.splitlines()[0].endswith("- COMPLETED ===")),
    ("title_map_1911", lambda t: "MAP 1911" in t.splitlines()[0]),
    ("eight_sections", lambda t: all(
        "=== %d. " % n in t for n in range(1, 9))),

    ("map_1911", lambda t: "Arena map ID: 1911" in t),
    ("dir", lambda t: "Map.dbc directory: ZandalariArena\n" in t),
    ("instance_type_4", lambda t: "InstanceType: 4" in t),
    ("instance_list", lambda t: 'Client instance list: 1911 "Mugambala"'
                                in t),
    ("zone_9992", lambda t: 'AreaTable zone: 9992 "Mugambala"' in t),
    ("zone_src_note", lambda t: "not read from AreaTable" in t),
    ("expansion_field_7",
     lambda t: "ExpansionID field in the map row: 7" in t),
    ("wdt", lambda t: "1890596" in t),
    ("no_legacy", lambda t: "No legacy duplicate" in t),
    ("bg_903", lambda t: 'Battleground entry: 903 "Arena Bfa Mugambala"'
                         in t),
    ("team_slots", lambda t: "MinPlayersPerTeam 0, MaxPlayersPerTeam 5"
                             in t),
    ("lvl_90_120", lambda t: "MinLvl 90, MaxLvl 120" in t),
    ("start_locs", lambda t: "AllianceStartLoc 6616, HordeStartLoc 6617"
                             in t),
    ("start_max_dist_0", lambda t: "StartMaxDist 0" in t),
    ("weight_1", lambda t: "Weight 1" in t),
    ("location", lambda t: "Location: Zuldazar, Zandalar" in t),
    ("patch", lambda t: "patch 8.0.1 (2018-07-17)" in t),

    ("headline", lambda t: "this arena works" in t),
    ("impl_class", lambda t: "BattlegroundMB exists" in t),
    ("case_for_mb",
     lambda t: "has a case for BATTLEGROUND_MUGAMBALA" in flat(t)),
    ("spawned_claim",
     lambda t: "spawned by the server at the coordinates given"
               in flat(t)),
    ("not_wiki",
     lambda t: "not guessed from a wiki" in t),

    ("ws_6616", lambda t: "WorldSafeLoc 6616" in t),
    ("ws_6617", lambda t: "WorldSafeLoc 6617" in t),
    ("ws_6895", lambda t: "WorldSafeLoc 6895" in t),
    ("t1_x", lambda t: "X: -1935.1" in t),
    ("t1_y", lambda t: "Y: 1233.3" in t),
    ("t1_z", lambda t: "Z: 34.7009" in t),
    ("t1_facing", lambda t: "132.874 deg = 2.3191 rad" in t),
    ("t2_x", lambda t: "X: -1934.25" in t),
    ("t2_y", lambda t: "Y: 1369.32" in t),
    ("t2_z", lambda t: "Z: 34.4306" in t),
    ("t2_facing", lambda t: "226.605 deg = 3.9550 rad" in t),
    ("go_x", lambda t: "X: -1938.79" in t),
    ("go_y", lambda t: "Y: 1299.93" in t),
    ("go_z", lambda t: re.search(
        r"Game On target \(WorldSafeLoc 6895\):\n"
        r"  X: -1938\.79\n  Y: 1299\.93\n  Z: 34\.4306", t) is not None),
    ("go_facing", lambda t: "Facing: 0 deg = 0 rad" in t),
    ("comment_east",
     lambda t: "Arena - Zandalar - Teleport Target - Team 1 (East)"
               in t),
    ("comment_west",
     lambda t: "Arena - Zandalar - Teleport Target - Team 2 (West)"
               in t),
    ("comment_go",
     lambda t: "Arena - Zandalar - Teleport Target - Game On" in t),
    ("naming_note", lambda t: "labels rather than the\nworld axes"
                              in t or "labels follow the arena's own "
                                      "compass" in flat(t)),
    ("no_gy", lambda t: "No arena graveyard row exists on map 1911"
                        in t),
    ("three_rows", lambda t: "has exactly three rows" in t),
    ("dist", lambda t: "Distance start to start: 136.02 units" in t),
    ("mid", lambda t: "Midpoint of the two starts: about -1934.675, "
                      "1301.31" in flat(t)),
    ("half", lambda t: "Each start is 68.01 units from that midpoint"
                       in t),
    ("axis", lambda t: "Axis is 0.85 apart on X and 136.02 apart on Y"
                       in t),
    ("bearing",
     lambda t: "Bearing from Team 1 to Team 2 is 89.64 deg" in t),
    ("off1", lambda t: "43.23 deg off that bearing" in t),
    ("off2", lambda t: "43.04 deg off the reverse" in t),
    ("agree", lambda t: "agree to 0.19 deg" in t),
    ("go_offset", lambda t: "Game On target is 4.34 units from the "
                            "midpoint" in flat(t)),
    ("go_axis", lambda t: "4.12 along" in t and "1.38 along -Y" in t),

    ("door1_label", lambda t: "Horde door (object 250431" in t),
    ("door2_label", lambda t: "Alliance door (object 250430" in t),
    ("d1_x", lambda t: "X: -1947.074707" in t),
    ("d1_y", lambda t: "Y: 1355.202515" in t),
    ("d1_z", lambda t: "Z: 34.755638" in t),
    ("d1_rad", lambda t: "3.816283 rad = 218.66 deg" in t),
    ("d2_x", lambda t: "X: -1961.725952" in t),
    ("d2_y", lambda t: "Y: 1354.591675" in t),
    ("d2_z", lambda t: "Z: 34.430664" in t),
    ("d2_rad", lambda t: "4.683993 rad = 268.37 deg" in t),
    ("doors_apart", lambda t: "The two doors are 14.66 apart" in t),
    ("door_z_gap", lambda t: "differs by 0.325" in t),
    ("d1_start", lambda t: "Horde door is 19.07 from the" in t),
    ("d2_start", lambda t: "Alliance door is 124.18 from the Alliance "
                           "start" in flat(t)),
    ("snifer", lambda t: '"custom need snifer"' in t),
    ("gate_unverified",
     lambda t: "real gate coordinates are unverified" in t),
    ("spawn_close", lambda t: "StartingEventCloseDoors spawns both shut"
                              in t),
    ("spawn_open", lambda t: "StartingEventOpenDoors calls DoorOpen on "
                             "both" in flat(t)),

    ("pillar_count", lambda t: "Pillar count: 1 large one" in t),
    ("liq_none", lambda t: "No source describes a second" in t),
    ("pillar_unverified", lambda t: "Pillar position: unverified" in t),
    ("upper_unverified",
     lambda t: "Upper floor coordinates: unverified" in t),
    ("four_objects",
     lambda t: "spawns exactly four objects on this map" in t),
    ("terrain_note", lambda t: "the pillar is terrain" in t),
    ("blizz_quote", lambda t: "large pillar in the middle" in t),
    ("inven_quote", lambda t: "square structure in the centre" in t),
    ("namu_quote", lambda t: "large pillar on one side and high stairs"
                             in t),
    ("mod_quote", lambda t: "Three separate wide open areas" in t),

    ("z_t1", lambda t: re.search(r"Team 1 start:\s+34\.7009", t) is not None),
    ("z_t2", lambda t: re.search(r"Team 2 start:\s+34\.4306", t) is not None),
    ("z_go", lambda t: re.search(r"Game On target:\s+34\.4306", t) is not None),
    ("z_d2", lambda t: re.search(r"Alliance door:\s+34\.430664", t) is not None),
    ("z_orb", lambda t: re.search(r"Orb position:\s+34\.431129", t) is not None),
    ("z_d1", lambda t: re.search(r"Horde door:\s+34\.755638", t) is not None),
    ("z_spread6", lambda t: "Spread across the six: 0.33 units" in t),
    ("upper_unv2", lambda t: "Height of the upper floor: unverified"
                             in t),
    ("ramps_none", lambda t: "Ramps: none." in t),
    ("stairs_note", lambda t: "stairs are terrain" in flat(t)),

    ("role_melee", lambda t: "Melee DPS:" in t),
    ("role_ranged", lambda t: "Ranged DPS:" in t),
    ("role_healer", lambda t: "Healers:" in t),
    ("caution_roles", lambda t: "Read with caution" in t),
    ("no_coord_roles", lambda t: "not from coordinates" in flat(t)),
    ("start_gap_z", lambda t: "The two starts differ by 0.27 in Z" in t),

    ("buff_label", lambda t: "184663 and 184664 (BG_MB_OBJECT_BUFF_1, "
                             "_2)" in flat(t)),
    ("b_x", lambda t: "X: -1962.612305" in t),
    ("b_y", lambda t: "Y: 1245.579956" in t),
    ("b_z", lambda t: "Z: 34.431129" in t),
    ("b_rad", lambda t: "1.652806 rad = 94.70 deg" in t),
    ("same_point", lambda t: "both AddObject calls pass the same X, Y"
                             in flat(t)),
    ("orb_dist1", lambda t: "30.13 from the Team 1 start" in t),
    ("orb_dist2", lambda t: "126.95 from the Team 2 start" in flat(t)),
    ("respawn_60", lambda t: "Respawn: 60 s" in t),
    ("spawn60", lambda t: "SpawnBGObject(i, 60)" in t),
    ("not_respawn_time",
     lambda t: "is not a respawn time" in flat(t)),
    ("four_rotations",
     lambda t: "AddObject takes four rotations before the respawn time"
               in flat(t)),
    ("respawn0", lambda t: "created with respawn 0" in t),
    ("spell", lambda t: "34709" in t),
    ("spell_name", lambda t: "Shadow Sight" in t),
    ("spell_dmg", lambda t: "+5% damage taken" in t),
    ("spell_dur", lambda t: "15 s" in t),

    ("flow_wired", lambda t: "fully wired in this core" in t),
    ("flow_row", lambda t: "row 903 with Weight 1 selects it" in t),
    ("flow_construct", lambda t: "that constructs BattlegroundMB"
                                 in flat(t)),
    ("flow_doors",
     lambda t: "SpawnBGObject(i, 60) when the gates open" in flat(t)),
    ("flow_triggers", lambda t: "4536 and 4537" in t),
    ("flow_trigger_behaviour",
     lambda t: "deliberately do nothing" in t),
    ("flow_worldstate", lambda t: "worldstate 0xE1A to 1" in t),
    ("flow_inherited", lambda t: "come from Arena,\nnot from this file"
                                 in t),

    ("sources", lambda t: "Sources:" in t),
    ("unverified", lambda t: "Unverified:" in t),
    ("src_mb_h", lambda t: "BattlegroundMB.h" in t),
    ("src_mb_cpp", lambda t: "BattlegroundMB.cpp" in t),
    ("src_mgr", lambda t: "BattlegroundMgr.cpp" in t),
    ("src_datamine", lambda t: "Map_ZandalariArena.lua" in t),
    ("src_wowhead_zone", lambda t: "Wowhead zone 9992" in t),
    ("src_wowhead_spell", lambda t: "Wowhead spell 34709" in t),
    ("src_wowhead_obj",
     lambda t: "Wowhead object lookup" in t),
    ("src_blizz", lambda t: "Blizzard arena preview text" in t),
    ("src_inven", lambda t: "Inven preview" in t),
    ("src_namu", lambda t: "NamuWiki arena page" in t),
    ("unv_pillar", lambda t: "Pillar position and dimensions" in t),
    ("unv_upper",
     lambda t: "Upper floor height, extent and stair positions" in t),
    ("unv_gates",
     lambda t: "Retail gate positions (the zone file calls its doors "
               "custom)" in flat(t)),
    ("unv_orb",
     lambda t: "Second orb position (both orbs spawn at one point here)"
               in flat(t)),
    ("unv_gy", lambda t: "Graveyard location (no row on map 1911)" in t),
]

MUTATIONS = [
    ("map_id", lambda t: t.replace("Arena map ID: 1911",
                                   "Arena map ID: 1912")),
    ("directory", lambda t: t.replace("ZandalariArena",
                                      "ZandalariArena2")),
    ("zone", lambda t: t.replace('AreaTable zone: 9992',
                                 'AreaTable zone: 9993')),
    ("expansion_field", lambda t: t.replace(
        "ExpansionID field in the map row: 7",
        "ExpansionID field in the map row: 6")),
    ("wdt", lambda t: t.replace("1890596", "1890597")),
    ("bg_entry", lambda t: t.replace("Battleground entry: 903",
                                     "Battleground entry: 904")),
    ("team_slots", lambda t: t.replace("MaxPlayersPerTeam 5",
                                       "MaxPlayersPerTeam 10")),
    ("levels", lambda t: t.replace("MinLvl 90, MaxLvl 120",
                                   "MinLvl 10, MaxLvl 120")),
    ("start_locs", lambda t: t.replace(
        "AllianceStartLoc 6616, HordeStartLoc 6617",
        "AllianceStartLoc 6617, HordeStartLoc 6616")),
    ("start_max_dist", lambda t: t.replace("StartMaxDist 0",
                                           "StartMaxDist 10")),
    ("weight", lambda t: t.replace("Weight 1", "Weight 0")),
    ("patch", lambda t: t.replace("patch 8.0.1 (2018-07-17)",
                                  "patch 8.0.2 (2018-07-17)")),
    ("location", lambda t: t.replace("Zuldazar, Zandalar",
                                     "Zuldazar, Kalimdor")),
    ("headline", lambda t: t.replace("this arena works",
                                     "this arena does not exist")),
    ("impl_class", lambda t: t.replace("BattlegroundMB exists",
                                       "BattlegroundMB is missing")),
    ("case_for_mb", lambda t: t.replace(
        "has a case for BATTLEGROUND_MUGAMBALA",
        "has no case for BATTLEGROUND_MUGAMBALA")),
    ("construct", lambda t: t.replace("that constructs BattlegroundMB",
                                      "that does not construct "
                                      "BattlegroundMB")),
    ("ws_ally", lambda t: t.replace("WorldSafeLoc 6616",
                                    "WorldSafeLoc 6626")),
    ("ws_horde", lambda t: t.replace("WorldSafeLoc 6617",
                                     "WorldSafeLoc 6627")),
    ("ws_go", lambda t: t.replace("WorldSafeLoc 6895",
                                  "WorldSafeLoc 6905")),
    ("t1_x", lambda t: t.replace("X: -1935.1", "X: -1936.1")),
    ("t1_y", lambda t: t.replace("Y: 1233.3", "Y: 1234.3")),
    ("t1_z", lambda t: t.replace("Z: 34.7009", "Z: 35.7009")),
    ("t1_facing", lambda t: t.replace("132.874 deg = 2.3191 rad",
                                      "132.874 deg = 3.3191 rad")),
    ("t2_x", lambda t: t.replace("X: -1934.25", "X: -1935.25")),
    ("t2_y", lambda t: t.replace("Y: 1369.32", "Y: 1370.32")),
    ("t2_z", lambda t: t.replace("Z: 34.4306", "Z: 35.4306")),
    ("t2_facing", lambda t: t.replace("226.605 deg = 3.9550 rad",
                                      "226.605 deg = 4.9550 rad")),
    ("go_x", lambda t: t.replace("X: -1938.79", "X: -1939.79")),
    ("go_y", lambda t: t.replace("Y: 1299.93", "Y: 1300.93")),
    ("go_z", lambda t: t.replace("Z: 34.4306", "Z: 35.4306")),
    ("go_facing", lambda t: t.replace("Facing: 0 deg = 0 rad",
                                      "Facing: 0 deg = 1 rad")),
    ("comment_east", lambda t: t.replace("Team 1 (East)",
                                         "Team 1 (West)")),
    ("comment_go", lambda t: t.replace("Teleport Target - Game On",
                                       "Teleport Target - Game Over")),
    ("gy_claim", lambda t: t.replace(
        "No arena graveyard row exists",
        "An arena graveyard row exists")),
    ("three_rows", lambda t: t.replace("has exactly three rows",
                                       "has exactly four rows")),
    ("dist", lambda t: t.replace("136.02 units", "146.02 units")),
    ("mid", lambda t: t.replace("about -1934.675, 1301.31",
                                "about -1934.775, 1301.31")),
    ("half", lambda t: t.replace("68.01 units", "78.01 units")),
    ("axis", lambda t: t.replace("0.85 apart on X", "1.85 apart on X")),
    ("bearing", lambda t: t.replace("is 89.64 deg", "is 99.64 deg")),
    ("off1", lambda t: t.replace("43.23 deg off", "44.23 deg off")),
    ("off2", lambda t: t.replace("43.04 deg off", "44.04 deg off")),
    ("agree", lambda t: t.replace("agree to 0.19 deg",
                                  "agree to 0.29 deg")),
    ("go_offset", lambda t: t.replace("4.34 units from the midpoint",
                                      "5.34 units from the midpoint")),
    ("go_axis", lambda t: t.replace("4.12 along", "5.12 along")),
    ("d1_x", lambda t: t.replace("X: -1947.074707", "X: -1948.074707")),
    ("d1_rad", lambda t: t.replace("3.816283 rad = 218.66 deg",
                                   "3.816283 rad = 219.66 deg")),
    ("d2_y", lambda t: t.replace("Y: 1354.591675", "Y: 1355.591675")),
    ("d2_rad", lambda t: t.replace("4.683993 rad = 268.37 deg",
                                   "4.683993 rad = 269.37 deg")),
    ("doors_apart", lambda t: t.replace("are 14.66 apart",
                                        "are 24.66 apart")),
    ("door_z_gap", lambda t: t.replace("differs by 0.325",
                                       "differs by 0.425")),
    ("d1_start", lambda t: t.replace("Horde door is 19.07 from the",
                                     "Horde door is 29.07 from the")),
    ("d2_start", lambda t: t.replace("Alliance door is 124.18",
                                     "Alliance door is 134.18")),
    ("snifer", lambda t: t.replace('"custom need snifer"',
                                   '"custom need sniffer"')),
    ("gate_unverified", lambda t: t.replace(
        "real gate coordinates are unverified",
        "real gate coordinates are verified")),
    ("pillar_count", lambda t: t.replace("Pillar count: 1 large one",
                                         "Pillar count: 2 large ones")),
    ("pillar_unverified", lambda t: t.replace(
        "Pillar position: unverified", "Pillar position: verified")),
    ("upper_unverified", lambda t: t.replace(
        "Upper floor coordinates: unverified",
        "Upper floor coordinates: verified")),
    ("four_objects", lambda t: t.replace(
        "spawns exactly four objects on this map",
        "spawns exactly six objects on this map")),
    ("z_spread6", lambda t: t.replace("Spread across the six: 0.33 units",
                                      "Spread across the six: 0.43 units")),
    ("upper_unv2", lambda t: t.replace(
        "Height of the upper floor: unverified",
        "Height of the upper floor: verified")),
    ("ramps", lambda t: t.replace("Ramps: none.", "Ramps: two.")),
    ("caution_roles", lambda t: t.replace("Read with caution",
                                          "Read without caution")),
    ("no_coord_roles", lambda t: t.replace("not from coordinates",
                                           "directly from coordinates")),
    ("start_gap_z", lambda t: t.replace("differ by 0.27 in Z",
                                        "differ by 0.37 in Z")),
    ("buff_ids", lambda t: t.replace("184663 and 184664",
                                     "184663 and 184665")),
    ("b_x", lambda t: t.replace("X: -1962.612305", "X: -1963.612305")),
    ("b_rad", lambda t: t.replace("1.652806 rad = 94.70 deg",
                                  "1.652806 rad = 95.70 deg")),
    ("same_point", lambda t: t.replace(
        "both AddObject calls pass the same X, Y",
        "both AddObject calls pass different X, Y")),
    ("orb_dist1", lambda t: t.replace("30.13 from the Team 1 start",
                                      "40.13 from the Team 1 start")),
    ("orb_dist2", lambda t: t.replace("126.95 from the",
                                      "136.95 from the")),
    ("respawn_60", lambda t: t.replace("Respawn: 60 s", "Respawn: 120 s")),
    ("spawn60", lambda t: t.replace("SpawnBGObject(i, 60)",
                                    "SpawnBGObject(i, 61)")),
    ("not_respawn_time", lambda t: t.replace(
        "is not a respawn time", "is a respawn time")),
    ("respawn0", lambda t: t.replace("created with respawn 0",
                                     "created with respawn 120")),
    ("spell", lambda t: t.replace("34709", "34710")),
    ("spell_dmg", lambda t: t.replace("+5% damage taken",
                                      "+6% damage taken")),
    ("flow_wired", lambda t: t.replace("fully wired in this core",
                                       "not wired in this core")),
    ("flow_triggers", lambda t: t.replace("4536 and 4537",
                                          "4536 and 4538")),
    ("flow_worldstate", lambda t: t.replace("worldstate 0xE1A to 1",
                                            "worldstate 0xE1A to 2")),
    ("width_inflate", lambda t: t.replace(
        "=== 4. HEIGHT LEVELS AND RAMPS ===",
        "=== 4. HEIGHT LEVELS, RAMPS AND A GREAT DEAL OF ADDITIONAL "
        "TEXT THAT MAKES THIS LINE FAR TOO LONG ===")),
]

FUNC_MARK = "BattlegroundMgr::CreateNewBattleground"
SWITCH_MARK = "switch (bgTypeId)"
CONSTRUCT = "bg = new BattlegroundMB(*(BattlegroundMB*)bg_template);"


def switch_body(mgr):
    """Text of the CreateNewBattleground switch, or "" if not found."""
    fn = mgr.find(FUNC_MARK)
    if fn < 0:
        return ""
    start = mgr.find(SWITCH_MARK, fn)
    if start < 0:
        return ""
    end = mgr.find("return nullptr;", start)
    if end < 0:
        return ""
    return mgr[start:end + len("return nullptr;")]


NUM = r"(-?\d+(?:\.\d+)?)"


def parse_sql_rows(sql):
    """id -> {x, y, z, facing, comment} for rows on map 1911."""
    rows = {}
    pattern = (r"\((\d+),1911," + NUM + r"," + NUM + r"," + NUM + r","
               + NUM + r",'([^']*)'\)")
    for m in re.finditer(pattern, sql):
        rows[int(m.group(1))] = {
            "x": float(m.group(2)), "y": float(m.group(3)),
            "z": float(m.group(4)), "f": float(m.group(5)),
            "comment": m.group(6)}
    return rows


DOC_BLOCK = (r"%s \(WorldSafeLoc %d[^)]*\):\n"
             r"  X: " + NUM + r"\n"
             r"  Y: " + NUM + r"\n"
             r"  Z: " + NUM + r"\n"
             r"  Facing: " + NUM + r" deg = (\d+(?:\.\d+)?) rad")


def parse_doc_rows(text):
    blocks = {}
    for wid, label in ((6616, "Team 1"), (6617, "Team 2"),
                       (6895, "Game On target")):
        m = re.search(DOC_BLOCK % (re.escape(label), wid), text)
        if m:
            blocks[wid] = {
                "x": float(m.group(1)), "y": float(m.group(2)),
                "z": float(m.group(3)), "f": float(m.group(4)),
                "rad": m.group(5)}
    return blocks


def parse_doc_header_block(text, header):
    """Labeled X/Y/Z block after `header:` (doors, orb)."""
    m = re.search(re.escape(header) + r":\n"
                  r"  X: " + NUM + r"\n"
                  r"  Y: " + NUM + r"\n"
                  r"  Z: " + NUM + r"\n"
                  r"  Orientation: (\d+\.\d+) rad = (\d+\.\d+) deg",
                  text)
    if not m:
        return None
    return {"x": float(m.group(1)), "y": float(m.group(2)),
            "z": float(m.group(3)), "rad": m.group(4),
            "deg": float(m.group(5))}


def parse_cpp_objects(cpp):
    """Macro -> (x, y, z, orientation) parsed out of the AddObject calls."""
    out = {}
    for macro in ("DOOR_1", "DOOR_2", "BUFF_1", "BUFF_2"):
        m = re.search(
            r"AddObject\(BG_MB_OBJECT_%s, BG_MB_OBJECT_TYPE_%s, "
            r"(-?\d+\.\d+)f, (-?\d+\.\d+)f, (-?\d+\.\d+)f, "
            r"(\d+\.\d+)f" % (macro, macro), cpp)
        if m:
            out[macro] = (float(m.group(1)), float(m.group(2)),
                          float(m.group(3)), float(m.group(4)))
    return out


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


def derived_stage(text, sql):
    """Recompute every derived claim of section 1 from the source rows."""
    src = parse_sql_rows(sql)
    docs = parse_doc_rows(text)
    lines, ok = [], True

    def fail(msg):
        lines.append("    BAD  " + msg)
        return False

    for wid in MAP_ROWS:
        label = "WorldSafeLoc %d" % wid
        if wid not in docs:
            ok = fail("%s: coordinate block not found in doc" % label)
            continue
        if wid not in src:
            ok = fail("%s: row not found in source" % label)
            continue
        d, s = docs[wid], src[wid]
        same = all(abs(d[k] - s[k]) < 1e-9 for k in ("x", "y", "z", "f"))
        if not same:
            ok = fail("%s: doc %s != source %s"
                      % (label, [d[k] for k in ("x", "y", "z", "f")],
                         [s[k] for k in ("x", "y", "z", "f")]))
        else:
            lines.append("    %-16s doc matches source row (x, y, z, facing)"
                         % label)
        digits = len(d["rad"].split(".")[1]) if "." in d["rad"] else 0
        rad = round(math.radians(d["f"]), digits)
        if abs(rad - float(d["rad"])) > 1e-9:
            ok = fail("%s: %s deg should be %s rad, doc says %s"
                      % (label, d["f"], rad, d["rad"]))
        else:
            lines.append("    %-16s %.3f deg -> %s rad  ok"
                         % (label, d["f"], d["rad"]))

    if not ok:
        return ok, lines

    def grab(pattern):
        m = re.search(pattern, text)
        if not m:
            raise RuntimeError("pattern not found: %s" % pattern)
        return float(m.group(1))

    a, b, go = src[6616], src[6617], src[GO_ID]
    cx, cy = (a["x"] + b["x"]) / 2.0, (a["y"] + b["y"]) / 2.0
    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])

    checks = [
        ("start to start", dist((a["x"], a["y"]), (b["x"], b["y"])),
         r"Distance start to start: (\d+\.\d+)"),
        ("start to midpoint", dist((a["x"], a["y"]), (cx, cy)),
         r"Each start is (\d+\.\d+) units"),
        ("axis X", abs(a["x"] - b["x"]), r"Axis is (\d+\.\d+) apart on X"),
        ("axis Y", abs(a["y"] - b["y"]), r"apart on X and (\d+\.\d+) "
                                         r"apart on Y"),
        ("gameon to midpoint", dist((go["x"], go["y"]), (cx, cy)),
         r"Game On target is (\d+\.\d+) units"),
        ("gameon along -X", abs(cx - go["x"]),
         r"units from the midpoint: (\d+\.\d+) along"),
        ("gameon along -Y", abs(cy - go["y"]),
         r"along\n  -X and (\d+\.\d+) along -Y"),
    ]
    for label, value, pattern in checks:
        got = round(value, 2)
        want = grab(pattern)
        mark = "ok " if abs(got - want) <= 0.01 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %8.2f  recomputed %8.2f  %s"
                     % (label, want, got, mark))

    m = re.search(r"Midpoint of the two starts: about " + NUM + r", "
                  + NUM, text)
    if not m:
        raise RuntimeError("midpoint claim missing")
    for label, want, got in (("midpoint X", float(m.group(1)), cx),
                             ("midpoint Y", float(m.group(2)), cy)):
        mark = "ok " if abs(got - want) <= 0.01 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %9.3f     recomputed %9.3f  %s"
                     % (label, want, got, mark))

    bearing = math.degrees(math.atan2(b["y"] - a["y"],
                                      b["x"] - a["x"])) % 360
    want_b = grab(r"Bearing from Team 1 to Team 2 is (\d+\.\d+) deg")
    mark = "ok " if abs(bearing - want_b) <= 0.01 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.2f  recomputed %8.2f  %s"
                 % ("bearing T1->T2", want_b, bearing, mark))

    offs = []
    for label, face, pattern, ref in (
            ("T1 off bearing", a["f"],
             r"which is (\d+\.\d+) deg off that bearing", bearing),
            ("T2 off bearing", b["f"],
             r"which is (\d+\.\d+) deg off the reverse",
             (bearing + 180) % 360)):
        want = grab(pattern)
        diff = abs(face - ref)
        diff = min(diff, 360 - diff)
        mark = "ok " if abs(diff - want) <= 0.01 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %8.2f  recomputed %8.2f  %s"
                     % (label, want, diff, mark))
        offs.append(want)

    want_agree = grab(r"agree to (\d+\.\d+) deg")
    got_agree = round(abs(offs[0] - offs[1]), 2)
    mark = "ok " if abs(got_agree - want_agree) <= 0.01 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.2f  recomputed %8.2f  %s"
                 % ("offsets agree to", want_agree, got_agree, mark))

    want_gap = grab(r"The two starts differ by (\d+\.\d+) in Z")
    got_gap = round(max(a["z"], b["z"]) - min(a["z"], b["z"]), 2)
    mark = "ok " if abs(got_gap - want_gap) <= 0.01 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.2f  recomputed %8.2f  %s"
                 % ("start Z gap", want_gap, got_gap, mark))

    return ok, lines


def absence_stage(text, corpora):
    """Recompute the document's negative claims from the source data."""
    ftext = flat(text)
    sql = corpora["world_safe_locs (8.x)"]
    cpp = corpora["BattlegroundMB.cpp"]
    lines, ok = [], True

    rows = parse_sql_rows(sql)
    mark = "ok " if set(rows) == set(MAP_ROWS) else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s expect %s  found %s  %s"
                 % ("ids on map 1911", sorted(MAP_ROWS), sorted(rows),
                    mark))

    gy_words = ("graveyard", "corpse", " gy")
    has_gy = any(w in r["comment"].lower() for r in rows.values()
                 for w in gy_words)
    claims_none = "No arena graveyard row exists on map 1911" in ftext
    mark = "ok " if claims_none and not has_gy else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s rows with a graveyard comment: %-5s %s"
                 % ("no graveyard row", str(has_gy), mark))

    wants_three = "has exactly three rows" in ftext
    mark = "ok " if wants_three and len(rows) == 3 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s claim 3  found %d  %s"
                 % ("row count", len(rows), mark))

    triggers = [t for t in ("case 4536:", "case 4537:") if t in cpp]
    generic = "Battleground::HandleAreaTrigger" in cpp
    claims = ("4536 and 4537 are listed in HandleAreaTrigger"
              in ftext and "deliberately do nothing" in ftext)
    mark = "ok " if claims and len(triggers) == 2 and generic else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s listed %d  generic fallthrough %s  %s"
                 % ("area triggers 4536/4537", len(triggers),
                    str(generic), mark))

    objects = cpp.count("AddObject(BG_MB_OBJECT_")
    claims_four = "spawns exactly four objects on this map" in ftext
    claims_split = "two doors and two orbs" in ftext
    mark = "ok " if claims_four and claims_split and objects == 4 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s AddObject calls %d  doc says four  %s"
                 % ("spawned object count", objects, mark))

    ws = "packet.Worldstates.emplace_back(0xE1A, 1);" in cpp
    claims_ws = "worldstate 0xE1A to 1" in ftext
    mark = "ok " if ws and claims_ws else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s source %s  doc %s  %s"
                 % ("worldstate 0xE1A = 1", str(ws), str(claims_ws),
                    mark))

    return ok, lines


def object_stage(text, corpora):
    """Door and orb positions: doc blocks versus BattlegroundMB.cpp."""
    cpp = corpora["BattlegroundMB.cpp"]
    sql = corpora["world_safe_locs (8.x)"]
    src = parse_sql_rows(sql)
    objs = parse_cpp_objects(cpp)
    lines, ok = [], True

    def fail(msg):
        lines.append("    BAD  " + msg)
        return False

    pairs = [
        ("Horde door (object 250431, BG_MB_OBJECT_DOOR_1)", "DOOR_1"),
        ("Alliance door (object 250430, BG_MB_OBJECT_DOOR_2)", "DOOR_2"),
        ("Buff objects 184663 and 184664 (BG_MB_OBJECT_BUFF_1, _2)",
         "BUFF_1"),
    ]
    for header, macro in pairs:
        block = parse_doc_header_block(text, header)
        if block is None:
            ok = fail("%s: block not found in doc" % macro)
            continue
        if macro not in objs:
            ok = fail("%s: AddObject call not found in source" % macro)
            continue
        sx, sy, sz, so = objs[macro]
        same = all(abs(block[k] - v) < 1e-9
                   for k, v in (("x", sx), ("y", sy), ("z", sz)))
        if not same:
            ok = fail("%s: doc (%s, %s, %s) != source (%s, %s, %s)"
                      % (macro, block["x"], block["y"], block["z"],
                         sx, sy, sz))
        else:
            lines.append("    %-8s doc block matches AddObject x, y, z"
                         % macro)
        want_deg = round(math.degrees(so), 2)
        if abs(want_deg - block["deg"]) > 0.01:
            ok = fail("%s: orientation %s rad = %.2f deg, doc says %s"
                      % (macro, block["rad"], want_deg, block["deg"]))
        else:
            lines.append("    %-8s %s rad = %.2f deg  ok"
                         % (macro, block["rad"], want_deg))
        if abs(float(block["rad"]) - so) > 1e-9:
            ok = fail("%s: doc rad %s != source rad %s"
                      % (macro, block["rad"], so))

    if "BUFF_1" in objs and "BUFF_2" in objs:
        same = objs["BUFF_1"][:3] == objs["BUFF_2"][:3]
        claims = "both AddObject calls pass the same X, Y" in flat(text)
        mark = "ok " if same and claims else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-30s source %s  doc %s  %s"
                     % ("both orbs at one point", str(same),
                        str(claims), mark))
    else:
        ok = fail("buff AddObject calls not found")

    def grab(pattern):
        m = re.search(pattern, text)
        if not m:
            raise RuntimeError("pattern not found: %s" % pattern)
        return float(m.group(1))

    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
    try:
        if "DOOR_1" in objs and "DOOR_2" in objs:
            d1, d2 = objs["DOOR_1"], objs["DOOR_2"]
            checks = [
                ("doors apart", dist(d1[:2], d2[:2]),
                 r"The two doors are (\d+\.\d+) apart"),
                ("door Z spread", abs(d1[2] - d2[2]),
                 r"their Z\ndiffers by (\d+\.\d+)"),
                ("Horde door to T2", dist(d1[:2], (src[6617]["x"],
                                                   src[6617]["y"])),
                 r"Horde door is (\d+\.\d+) from the"),
                ("Alliance door to T1", dist(d2[:2], (src[6616]["x"],
                                                      src[6616]["y"])),
                 r"Alliance door is (\d+\.\d+) from the Alliance start"),
            ]
            if "BUFF_1" in objs:
                checks += [
                    ("orb to T1", dist(objs["BUFF_1"][:2],
                                       (src[6616]["x"], src[6616]["y"])),
                     r"of each other, (\d+\.\d+) from the Team 1 start"),
                    ("orb to T2", dist(objs["BUFF_1"][:2],
                                       (src[6617]["x"], src[6617]["y"])),
                     r"and (\d+\.\d+) from the\nTeam 2 start"),
                ]
            zs = [src[w]["z"] for w in MAP_ROWS] + [d1[2], d2[2]]
            if "BUFF_1" in objs:
                zs.append(objs["BUFF_1"][2])
            checks.append(("Z spread of six",
                           max(zs) - min(zs),
                           r"Spread across the six: (\d+\.\d+) units"))
            for label, value, pattern in checks:
                got = round(value, 3 if label == "door Z spread" else 2)
                want = grab(pattern)
                mark = "ok " if abs(got - want) <= 0.011 else "BAD"
                if mark == "BAD":
                    ok = False
                lines.append("    %-20s doc %8.3f  recomputed %8.3f  %s"
                             % (label, want, got, mark))
    except RuntimeError as exc:
        ok = fail(str(exc))

    return ok, lines


def impl_stage(text, mgr, names):
    """This arena is implemented: case present, class constructed."""
    ftext = flat(text)
    lines, ok = [], True
    body = switch_body(mgr)
    labels = re.findall(r"case BATTLEGROUND_(\w+):", body)

    mark = "ok " if "MUGAMBALA" in labels else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %s" % ("MUGAMBALA case in switch", mark))

    mark = "ok " if CONSTRUCT in body else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %s" % ("constructs BattlegroundMB", mark))

    claims_case = ("has a case for BATTLEGROUND_MUGAMBALA" in ftext)
    mark = "ok " if claims_case else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %s" % ("doc claims that case", mark))

    claims_ctor = "that constructs BattlegroundMB" in ftext
    mark = "ok " if claims_ctor else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %s" % ("doc claims the construction", mark))

    has_cpp = "BattlegroundMB.cpp" in names
    has_h = "BattlegroundMB.h" in names
    mark = "ok " if has_cpp and has_h else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s cpp %s  h %s  %s"
                 % ("zone files present", str(has_cpp), str(has_h), mark))

    names_ok = "BattlegroundMB.cpp" in ftext and "BattlegroundMB.h" in ftext
    mark = "ok " if names_ok else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %s" % ("doc names both files", mark))

    nulls = "return nullptr;" in body
    mark = "ok " if nulls else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %s" % ("switch still ends in nullptr", mark))

    return ok, lines


def main():
    if not os.path.exists(DELIVERABLE):
        print("MISSING DELIVERABLE: %s" % DELIVERABLE)
        return 1
    with open(DELIVERABLE) as fh:
        original = fh.read()

    print("=" * 66)
    print("AUDIT: Arena_Mugambala_COMPLETED.txt (Step 11)")
    print("=" * 66)

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
        "SharedDefines.h": gh_content(HP_REPO, SD_PATH),
        "BattlegroundMgr.cpp": gh_content(HP_REPO, BGM_PATH),
        "Battleground.h": gh_content(HP_REPO, BG_H_PATH),
        "BattlegroundMB.h": gh_content(HP_REPO, MB_H_PATH),
        "BattlegroundMB.cpp": gh_content(HP_REPO, MB_CPP_PATH),
        "Map_ZandalariArena.lua": gh_content(DM_REPO, DM_PATH),
    }
    ok, lines = source_stage(corpora, SOURCE_TOKENS)
    for line in lines:
        print(line)
    if not ok:
        print("    SOURCE CROSS-CHECK FAILED")
        return 1

    def break_literals(text_):
        for _, lit in [t for v in SOURCE_TOKENS.values() for t in v]:
            if lit in text_:
                text_ = text_.replace(
                    lit, lit[:-1] + ("9" if not lit.endswith("9") else "8"))
        return text_

    undetected = mutation_probe(corpora, SOURCE_TOKENS, break_literals)
    if undetected:
        print("    cross-check did not react to tampered source: %s"
              % undetected)
        return 1
    print("    cross-check reacts to tampered source (verified)")

    print("\n[4] Derived values recomputed from the source rows")
    ok, lines = derived_stage(original, corpora["world_safe_locs (8.x)"])
    for line in lines:
        print(line)
    if not ok:
        print("    DERIVED VALUES DO NOT MATCH")
        return 1

    probes = {
        "coordinate changed": original.replace("X: -1935.1",
                                               "X: -1931.5"),
        "distance changed": original.replace("136.02 units",
                                             "146.02 units"),
        "radians changed": original.replace("2.3191 rad", "3.3191 rad"),
        "bearing changed": original.replace("is 89.64 deg",
                                            "is 99.64 deg"),
        "agreement changed": original.replace("agree to 0.19 deg",
                                              "agree to 1.19 deg"),
        "midpoint changed": original.replace("about -1934.675, 1301.31",
                                             "about -1934.775, 1301.31"),
    }
    survived = []
    for name, probe in probes.items():
        if probe == original:
            survived.append(name + " (no-op)")
            continue
        try:
            probe_ok, _ = derived_stage(probe,
                                        corpora["world_safe_locs (8.x)"])
        except RuntimeError:
            probe_ok = False
        if probe_ok:
            survived.append(name)
    if survived:
        print("    derived stage did not react: %s" % survived)
        return 1
    print("    derived stage reacts to wrong values (verified)")

    print("\n[5] Negative claims recomputed from the source")
    ok, lines = absence_stage(original, corpora)
    for line in lines:
        print(line)
    if not ok:
        print("    NEGATIVE CLAIMS DO NOT MATCH THE DATA")
        return 1
    probe_corpora = dict(corpora)
    probe_corpora["world_safe_locs (8.x)"] = corpora[
        "world_safe_locs (8.x)"] + (
        "\n(9999,1911,-1900.0,1300.0,34.5,0,"
        "'Arena - Zandalar - Graveyard'),")
    if absence_stage(original, probe_corpora)[0]:
        print("    absence stage did not react to a graveyard row")
        return 1
    print("    absence stage reacts to a graveyard row (verified)")
    probe_corpora = dict(corpora)
    probe_corpora["BattlegroundMB.cpp"] = corpora[
        "BattlegroundMB.cpp"].replace("case 4536:", "case 45360:")
    if absence_stage(original, probe_corpora)[0]:
        print("    absence stage did not react to a lost trigger")
        return 1
    print("    absence stage reacts to a lost trigger (verified)")
    probe_corpora = dict(corpora)
    probe_corpora["BattlegroundMB.cpp"] = corpora[
        "BattlegroundMB.cpp"].replace(
            "|| !AddObject(BG_MB_OBJECT_BUFF_2", "|| false && ")
    if absence_stage(original, probe_corpora)[0]:
        print("    absence stage did not react to a dropped object")
        return 1
    print("    absence stage reacts to a dropped object (verified)")

    print("\n[6] No-invented-coordinates trace")
    ok, lines, _ = coord_trace(original, corpora)
    for line in lines:
        print(line)
    if not ok:
        print("    INVENTED COORDINATES FOUND")
        return 1
    probe = original.replace("X: -1935.1", "X: -1931.5")
    if probe == original or coord_trace(probe, corpora)[0]:
        print("    trace did not react to an invented coordinate")
        return 1
    print("    trace reacts to an invented coordinate (verified)")

    print("\n[7] Door and orb positions parsed from the zone file")
    ok, lines = object_stage(original, corpora)
    for line in lines:
        print(line)
    if not ok:
        print("    OBJECT POSITIONS DO NOT MATCH THE ZONE FILE")
        return 1
    probe_corpora = dict(corpora)
    probe_corpora["BattlegroundMB.cpp"] = corpora[
        "BattlegroundMB.cpp"].replace("-1947.074707f", "-1941.074707f")
    if object_stage(original, probe_corpora)[0]:
        print("    object stage did not react to a moved door")
        return 1
    print("    object stage reacts to a moved door (verified)")

    print("\n[8] The implemented case, checked against the tree")
    out = subprocess.run(
        ["gh", "api", "repos/%s/contents/%s" % (HP_REPO, ZONES_PATH),
         "--jq", ".[].name"], capture_output=True, text=True)
    if out.returncode != 0:
        print("    directory listing failed: %s" % out.stderr.strip())
        return 1
    names = [n for n in out.stdout.split("\n") if n]
    ok, lines = impl_stage(original, corpora["BattlegroundMgr.cpp"], names)
    for line in lines:
        print(line)
    if not ok:
        print("    IMPLEMENTATION CLAIMS DO NOT MATCH")
        return 1
    mgr_probe = corpora["BattlegroundMgr.cpp"].replace(CONSTRUCT, " ;")
    if impl_stage(original, mgr_probe, names)[0]:
        print("    impl stage did not react to a missing construction")
        return 1
    print("    impl stage reacts to a missing construction (verified)")
    names_probe = [n for n in names if n != "BattlegroundMB.cpp"]
    if impl_stage(original, corpora["BattlegroundMgr.cpp"],
                  names_probe)[0]:
        print("    impl stage did not react to a missing zone file")
        return 1
    print("    impl stage reacts to a missing zone file (verified)")

    print("\n" + "=" * 66)
    print("AUDIT RESULT: PASS")
    print("  static checks: %d/%d" % (passed, len(STATIC_CHECKS)))
    print("  mutations:     %d/%d" % (detected, len(MUTATIONS)))
    print("=" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())
