#!/usr/bin/env python3
"""Mutation-tested audit for Arena_Kul_Tiras_Arena_COMPLETED.txt (Step 12).

Eight independent stages:
  1. static claims inside the document
  2. mutation testing: every claim must fail when its value is altered
  3. source cross-check: every quoted value must exist upstream
  4. derived arithmetic recomputed from the source rows
  5. negative claims recomputed from the source data
  6. coordinate trace: no number may be invented
  7. alias identity: the map is Hook Point under another name
  8. the Zones directory: no zone file under any spelling

Step 12's whole subject is naming, so stage 7 exists to prove the
alias claims (one template row, MapName "Hook Point", world safe
location comments saying "Kul Tiras Arena") against the sources
rather than trusting the document's wording.
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
               "Arena_Kul_Tiras_Arena_COMPLETED.txt")

SQL_REPO = "TrinityCore/TrinityCore"
SQL_PATH = ("sql/old/8.x/world/19071_2020_06_17/"
            "2019_10_26_01_world.sql")
HP_REPO = "HavenWoW/BFA-HavenCore"
SD_PATH = "src/server/game/Miscellaneous/SharedDefines.h"
BGM_PATH = "src/server/game/Battlegrounds/BattlegroundMgr.cpp"
ZONES_PATH = "src/server/game/Battlegrounds/Zones"
DM_REPO = "Ghostopheles/Datamine"
DM_PATH = "Datamine_Maps/Generated/Map_KulTirasArena.lua"
TPL_REPO = "zTerragor/vSLDB"
TPL_PATH = "sql/updates/world/2021_11_03_world_Battleground_Template.sql"

START_IDS = (6276, 6277)
GO_ID = 6896
MAP_ROWS = (6276, 6277, 6896)

SOURCE_TOKENS = {
    "world_safe_locs (8.x)": [
        ("ws 6276", "6276,1825,1052.47,-364.773,1.89676,114.343"),
        ("ws 6277", "6277,1825,966.125,-290.78,3.28703,297.523"),
        ("ws 6896", "6896,1825,1031.07,-334.044,0.776609,131.268"),
        ("comment 6276", "Kul Tiras Arena - Purple Team - Start"),
        ("comment 6277", "Kul Tiras Arena - Gold Team - Start"),
        ("comment 6896", "Arena - Kul Tiras - Teleport Target - Game On"),
    ],
    "battleground_template": [
        ("bg 897 row", "(897, 0, 5, 90, 120, 6276, 6277, 0, 1, '', "
                        "'Hook Point')"),
    ],
    "SharedDefines.h": [
        ("hook point enum", "BATTLEGROUND_HOOK_POINT     = 897"),
        ("kul tiras continent map", "MAP_KUL_TIRAS               = 1643"),
    ],
    "BattlegroundMgr.cpp": [
        ("default branch", "default:"),
        ("null instance", "return nullptr;"),
    ],
    "Map_KulTirasArena.lua": [
        ("map name", 'MapName = "Hook Point"'),
        ("map id", "MapID = 1825"),
        ("directory", "Directory = [[KulTirasArena]]"),
        ("instance type", "InstanceType = 4"),
        ("expansion", "ExpansionID = 7"),
        ("wdt", "WDTFileDataID: 1712797"),
    ],
}


def flat(text):
    return re.sub(r"\s+", " ", text)


STATIC_CHECKS = [
    ("file_exists", lambda t: os.path.exists(DELIVERABLE)),
    ("min_lines", lambda t: len(t.splitlines()) >= 260),
    ("max_width_78", lambda t: all(len(l) <= 78 for l in t.splitlines())),
    ("title_completed",
     lambda t: t.splitlines()[0].endswith("- COMPLETED ===")),
    ("title_map_1825", lambda t: "MAP 1825" in t.splitlines()[0]),
    ("eight_sections", lambda t: all(
        "=== %d. " % n in t for n in range(1, 9))),

    ("exists_yes", lambda t: "In the 8.3.7 client: yes, map 1825." in t),
    ("dir", lambda t: "Map.dbc directory: KulTirasArena\n" in t),
    ("mapdbc_name", lambda t: 'Map.dbc name: "Hook Point"' in t),
    ("instance_type_4", lambda t: "InstanceType: 4" in t),
    ("zone_9278",
     lambda t: 'AreaTable zone: 9278 "Kul Tiras Arena" per Wowhead'
               in t),
    ("zone_9279",
     lambda t: '9279 "Hook Point" is also an arena zone' in flat(t)),
    ("zone_ambiguous", lambda t: "which of the two\n  the instance "
                                 "reports is unverified" in t
                         or "the instance reports is unverified"
                            in flat(t)),
    ("expansion_field_7",
     lambda t: "ExpansionID field in the map row: 7" in t),
    ("wdt", lambda t: "1712797" in t),
    ("no_legacy", lambda t: "No legacy duplicate" in t),
    ("bg_897", lambda t: 'Battleground entry: 897 "Hook Point"' in t),
    ("team_slots", lambda t: "MinPlayersPerTeam 0, MaxPlayersPerTeam 5"
                             in t),
    ("lvl_90_120", lambda t: "MinLvl 90, MaxLvl 120" in t),
    ("start_locs", lambda t: "AllianceStartLoc 6276, HordeStartLoc 6277"
                             in t),
    ("start_max_dist_0", lambda t: "StartMaxDist 0" in t),
    ("weight_1", lambda t: "Weight 1" in t),
    ("location", lambda t: "Location: Ashvane Company Yards, Boralus"
                           in t),
    ("patch", lambda t: "patch 8.0.1 (2018-07-17)" in t),

    ("read_first", lambda t: "READ THIS FIRST - this arena and step 10's "
                             "Hook Point are the" in t),
    ("alias_same_map", lambda t: "same map under different names" in flat(t)),
    ("alias_single_entry", lambda t: "Map.dbc has a single entry" in t),
    ("alias_mapname_says",
     lambda t: 'its MapName field says "Hook Point"' in flat(t)),
    ("alias_single_row",
     lambda t: "battleground_template has a single row for it, id 897"
               in flat(t)),
    ("alias_no_other_row",
     lambda t: "no row mentioning Tiras or Hook exists other than that "
               "one" in flat(t)),
    ("alias_commented",
     lambda t: "world safe locations on map 1825 are commented" in t),
    ("alias_comment_quote",
     lambda t: '"Kul Tiras Arena - Purple Team - Start"' in t),
    ("alias_two_zones",
     lambda t: "two arena zones added in 8.0.1: 9278" in flat(t)),
    ("alias_enum_claim",
     lambda t: "BATTLEGROUND_HOOK_POINT = 897" in flat(t)),
    ("alias_no_enum",
     lambda t: "no Kul Tiras arena enum" in flat(t)),
    ("alias_continent",
     lambda t: "MAP_KUL_TIRAS = 1643 is the\n    continent" in t
                         or "MAP_KUL_TIRAS = 1643 is the continent"
                            in flat(t)),
    ("alias_ref_step10",
     lambda t: "Arena_Hook_Point_COMPLETED.txt" in t),
    ("alias_one_map",
     lambda t: "map with one queue entry and three names" in t),
    ("alias_no_repeat",
     lambda t: "Nothing below repeats a different map" in flat(t)),
    ("alias_reverified",
     lambda t: "verified again against the source dump for this file"
               in flat(t)),

    ("cannot_create", lambda t: "cannot create the arena at all" in t),
    ("declared",
     lambda t: "BATTLEGROUND_HOOK_POINT = 897 is declared" in flat(t)),
    ("no_case", lambda t: "has no HOOK_POINT" in t),
    ("null_default", lambda t: '"default: return nullptr;"' in flat(t)),
    ("no_zone_file",
     lambda t: "there is no zone file in "
               "src/server/game/Battlegrounds/Zones" in flat(t)),
    ("any_spelling", lambda t: "under any spelling" in t),
    ("nothing_spawned", lambda t: "nothing is spawned here" in flat(t)),

    ("ws_6276", lambda t: "WorldSafeLoc 6276" in t),
    ("ws_6277", lambda t: "WorldSafeLoc 6277" in t),
    ("ws_6896", lambda t: "WorldSafeLoc 6896" in t),
    ("t1_x", lambda t: "X: 1052.47" in t),
    ("t1_y", lambda t: "Y: -364.773" in t),
    ("t1_z", lambda t: "Z: 1.89676" in t),
    ("t1_facing", lambda t: "114.343 deg = 1.9957 rad" in t),
    ("t2_x", lambda t: "X: 966.125" in t),
    ("t2_y", lambda t: "Y: -290.78" in t),
    ("t2_z", lambda t: "Z: 3.28703" in t),
    ("t2_facing", lambda t: "297.523 deg = 5.1928 rad" in t),
    ("go_x", lambda t: "X: 1031.07" in t),
    ("go_y", lambda t: "Y: -334.044" in t),
    ("go_z", lambda t: "Z: 0.776609" in t),
    ("go_facing", lambda t: "131.268 deg = 2.2911 rad" in t),
    ("comment_purple",
     lambda t: '"Kul Tiras Arena - Purple Team - Start"' in t),
    ("comment_gold",
     lambda t: '"Kul Tiras Arena - Gold Team - Start"' in t),
    ("comment_go",
     lambda t: '"Arena - Kul Tiras - Teleport Target - Game On"' in t),
    ("comments_name", lambda t: 'both say "Kul Tiras Arena"' in t),
    ("gameon_drops",
     lambda t: "The Game On comment drops the word Arena and says"
               in flat(t)),
    ("colour_naming", lambda t: "Purple team" in t and "Gold team" in t),
    ("no_gy", lambda t: "No arena graveyard row exists on map 1825"
                        in t),
    ("three_rows", lambda t: "has exactly three rows" in t),
    ("dist", lambda t: "Distance start to start: 113.71 units" in t),
    ("mid", lambda t: "Midpoint of the two starts: about 1009.298, "
                      "-327.776" in flat(t)),
    ("half", lambda t: "Each start is 56.86 units from that midpoint"
                       in t),
    ("axis", lambda t: "Axis is 86.35 apart on X and 73.99 apart on Y"
                       in t),
    ("bearing",
     lambda t: "Bearing from Purple to Gold is 139.41 deg" in t),
    ("off1", lambda t: "25.06 deg off that bearing" in t),
    ("off2", lambda t: "21.88 deg off the reverse" in t),
    ("inward", lambda t: "Both teams face inward, both off-axis" in t),
    ("go_offset", lambda t: "Game On target is 22.66 units from the "
                            "midpoint" in flat(t)),

    ("gates_none",
     lambda t: "None. This core spawns no gates on map 1825" in t),
    ("gates_unverified",
     lambda t: "Gate count, entries and coordinates are unverified."
               in t),
    ("zone_class_needed",
     lambda t: "a zone class registered for BATTLEGROUND_HOOK_POINT"
               in flat(t)),

    ("pillar_disagree",
     lambda t: "Sources disagree on how many pillars this map has."
               in t),
    ("quote_liquipedia",
     lambda t: "two pillars in the middle area" in t),
    ("quote_namu",
     lambda t: "tall and long wooden fence on one side" in flat(t)),
    ("quote_inven",
     lambda t: "structures in the centre of the arena that act as "
               "pillars" in flat(t)),
    ("quote_blizzard",
     lambda t: "four pillars for players to dance around" in t),
    ("shark", lambda t: "shark hanging from it" in t),
    ("xpoff", lambda t: "quoted by xpoff" in t),
    ("count_two_claim",
     lambda t: "Liquipedia and Inven say two pillars in the middle"
               in flat(t)),
    ("namu_no_count",
     lambda t: "NamuWiki describes slanted pillars without giving a "
               "count" in flat(t)),
    ("fence_all_three",
     lambda t: "All three describe a fence on one side" in flat(t)),
    ("blizzard_unique",
     lambda t: "claims four big pillars plus two small, which no "
               "later page repeats" in flat(t)),
    ("count_conflict",
     lambda t: "Pillar count is therefore conflicting between" in t),
    ("majority_reading",
     lambda t: "the majority reading is two LoS pillars in the" in t),
    ("pillar_unverified",
     lambda t: "Pillar positions: unverified." in t),
    ("pillar_size_unv",
     lambda t: "Pillar size and slant: unverified." in t),
    ("fence_unverified",
     lambda t: 'Fence side: unverified beyond "one side"' in t),
    ("nothing_spawns",
     lambda t: "Nothing spawns here in server data" in flat(t)),
    ("prose_only", lambda t: "this section is prose only" in flat(t)),
    ("asym_backed", lambda t: "25.06 and 21.88 degrees" in t),

    ("one_level",
     lambda t: "One level as far as any readable source goes" in t),
    ("no_ramp_claim",
     lambda t: "No source describes a ramp or a second floor on this "
               "map" in flat(t)),
    ("z_list_go", lambda t: re.search(r"Game On target:\s+0\.776609",
                                      t) is not None),
    ("z_list_purple", lambda t: re.search(r"Purple team start:\s+1\.89676",
                                          t) is not None),
    ("z_list_gold", lambda t: re.search(r"Gold team start:\s+3\.28703",
                                        t) is not None),
    ("z_spread", lambda t: "Spread across all three: 2.51 units" in t),
    ("spawn_gap", lambda t: "spawn floors differ by 1.39 units"
                            in flat(t)),
    ("ramps", lambda t: "Ramps: unverified." in t),

    ("role_melee", lambda t: "Melee DPS:" in t),
    ("role_ranged", lambda t: "Ranged DPS:" in t),
    ("role_healer", lambda t: "Healers:" in t),
    ("caution_roles", lambda t: "Read with caution" in t),
    ("no_coord_roles", lambda t: "not from coordinates" in flat(t)),
    ("race_pillars", lambda t: "Race for the middle pillars" in t),
    ("max_range",
     lambda t: "max-range\n  casting across the middle works" in t
                         or "max-range casting across the middle works"
                            in flat(t)),
    ("healer_edge", lambda t: "Play the edge of the fenced side" in t),
    ("half_dist_role",
     lambda t: "Both teams are 56.86 from the midpoint" in flat(t)),
    ("diagonal",
     lambda t: "The start line is diagonal (86.35 by 73.99)" in t),
    ("go_role", lambda t: "Game On is 22.66 off the midpoint" in t),

    ("buffs_none",
     lambda t: "None spawned. This core places no Shadow Sight orbs "
               "on map 1825" in flat(t)),
    ("buffs_no_class",
     lambda t: "because no zone class exists for battleground 897"
               in t),
    ("buffs_unverified",
     lambda t: "count, object entries, positions and respawn are all "
               "unverified" in flat(t)),
    ("no_copy_warning",
     lambda t: "Do not copy coordinates from Tol'viron" in t),
    ("spell", lambda t: "34709" in t),
    ("spell_name", lambda t: "Shadow Sight" in t),
    ("spell_dmg", lambda t: "+5% damage taken" in t),
    ("spell_dur", lambda t: "15 s" in t),

    ("flow_head",
     lambda t: "The queue selects this map and then fails:" in t),
    ("flow_row",
     lambda t: 'battleground_template row 897 "Hook Point", Weight 1'
               in t),
    ("flow_no_case",
     lambda t: "CreateNewBattleground has no HOOK_POINT case and "
               "returns" in flat(t)),
    ("flow_null_branch",
     lambda t: "nullptr from the default branch" in flat(t)),
    ("flow_no_instance",
     lambda t: "a queue pop produces no instance" in flat(t)),
    ("name_map_id",
     lambda t: "map id to teleports and waypoints: 1825" in t),
    ("name_bg_id", lambda t: "battleground id: 897" in t),
    ("name_maplist",
     lambda t: "name in the client's map list: Hook Point" in t),
    ("name_comments",
     lambda t: "name in world safe location comments: Kul Tiras Arena"
               in t),
    ("name_zone_unv",
     lambda t: "zone id on the instance: 9278 or 9279, unverified"
               in t),
    ("page_hook",
     lambda t: "Liquipedia, NamuWiki and the wiki all page this arena "
               "as Hook Point" in flat(t)),
    ("wowhead_pages",
     lambda t: "Wowhead keeps both zone pages" in flat(t)),
    ("flow_inherited",
     lambda t: "inherited from Arena, not per-map" in flat(t)),

    ("sources", lambda t: "Sources:" in t),
    ("unverified", lambda t: "Unverified:" in t),
    ("src_sql_comments",
     lambda t: "comments naming Kul Tiras Arena" in t),
    ("src_sd", lambda t: "SharedDefines.h: BATTLEGROUND_HOOK_POINT" in t),
    ("src_continent",
     lambda t: "MAP_KUL_TIRAS = 1643 (continent)" in flat(t)),
    ("src_datamine", lambda t: "Map_KulTirasArena.lua" in t),
    ("src_wowhead", lambda t: "Wowhead zones 9278" in t),
    ("src_wiki", lambda t: 'Warcraft Wiki "Hook Point (arena)"' in t),
    ("src_liquipedia", lambda t: 'Liquipedia "Hook Point"' in t),
    ("src_namu", lambda t: "NamuWiki arena page" in t),
    ("src_inven", lambda t: "Inven preview, June 2018" in t),
    ("src_blizz",
     lambda t: "Blizzard arena preview text, August 2018 (via xpoff)"
               in t),
    ("unv_zone",
     lambda t: "Which zone id (9278 or 9279) the instance reports"
               in t),
    ("unv_gates",
     lambda t: "Gate objects: count, entries, positions (no zone "
               "file)" in flat(t)),
    ("unv_orbs",
     lambda t: "Shadow Sight orbs: count, entries, positions, respawn"
               in t),
    ("unv_pillar_count",
     lambda t: "Pillar count (sources conflict: 2 versus 4 plus 2)"
               in t),
    ("unv_pillar_pos", lambda t: "Pillar positions, size and slant"
                                 in t),
    ("unv_fence", lambda t: "Which side carries the wooden fence" in t),
    ("unv_ramp", lambda t: "Any ramp or second level" in t),
    ("unv_gy", lambda t: "Graveyard location (no row on map 1825)"
                         in t),
]

MUTATIONS = [
    ("map_id", lambda t: t.replace("In the 8.3.7 client: yes, map 1825.",
                                   "In the 8.3.7 client: yes, map 1826.")),
    ("directory", lambda t: t.replace("Map.dbc directory: KulTirasArena",
                                      "Map.dbc directory: KulTirasArena2")),
    ("mapdbc_name", lambda t: t.replace('Map.dbc name: "Hook Point"',
                                        'Map.dbc name: "Kul Tiras Pit"')),
    ("zone", lambda t: t.replace('AreaTable zone: 9278',
                                 'AreaTable zone: 9288')),
    ("zone_other", lambda t: t.replace('9279 "Hook',
                                       '9219 "Hook')),
    ("expansion_field", lambda t: t.replace(
        "ExpansionID field in the map row: 7",
        "ExpansionID field in the map row: 6")),
    ("wdt", lambda t: t.replace("1712797", "1712798")),
    ("bg_entry", lambda t: t.replace("Battleground entry: 897",
                                     "Battleground entry: 898")),
    ("team_slots", lambda t: t.replace("MaxPlayersPerTeam 5",
                                       "MaxPlayersPerTeam 10")),
    ("levels", lambda t: t.replace("MinLvl 90, MaxLvl 120",
                                   "MinLvl 10, MaxLvl 120")),
    ("start_locs", lambda t: t.replace(
        "AllianceStartLoc 6276, HordeStartLoc 6277",
        "AllianceStartLoc 6277, HordeStartLoc 6276")),
    ("start_max_dist", lambda t: t.replace("StartMaxDist 0",
                                           "StartMaxDist 10")),
    ("weight", lambda t: t.replace("Weight 1", "Weight 0")),
    ("location", lambda t: t.replace("Ashvane Company Yards",
                                     "Ashvane Company Docks")),
    ("patch", lambda t: t.replace("patch 8.0.1 (2018-07-17)",
                                  "patch 8.0.2 (2018-07-17)")),

    ("alias_exists", lambda t: t.replace(
        "In the 8.3.7 client: yes, map 1825.",
        "In the 8.3.7 client: no, no such map.")),
    ("alias_same_map", lambda t: t.replace(
        "same map under different names",
        "different maps under different names")),
    ("alias_single_entry", lambda t: t.replace(
        "Map.dbc has a single entry", "Map.dbc has two entries")),
    ("alias_mapname", lambda t: t.replace(
        'its MapName field says "Hook Point"',
        'its MapName field says something else')),
    ("alias_single_row", lambda t: t.replace(
        "battleground_template has a single row for it",
        "battleground_template has two rows for it")),
    ("alias_no_other_row", lambda t: t.replace(
        "no row mentioning Tiras or Hook exists",
        "rows mentioning Tiras or Hook exist")),
    ("alias_commented", lambda t: t.replace(
        "world safe locations on map 1825 are commented",
        "world safe locations on map 1825 are unlabelled")),
    ("alias_comment_quote", lambda t: t.replace(
        '"Kul Tiras Arena - Purple Team - Start"',
        '"Kul Tiras Arena - Purple Team - Begin"')),
    ("alias_two_zones", lambda t: t.replace(
        "two arena zones added in 8.0.1: 9278",
        "one arena zone added in 8.0.1: 9278")),
    ("alias_no_enum", lambda t: t.replace(
        "no Kul Tiras arena enum", "a Kul Tiras arena enum")),
    ("alias_continent", lambda t: t.replace(
        "MAP_KUL_TIRAS = 1643 is the", "MAP_KUL_TIRAS = 1642 is the")),
    ("alias_ref_step10", lambda t: t.replace(
        "Arena_Hook_Point_COMPLETED.txt",
        "Arena_Hook_Point2_COMPLETED.txt")),
    ("alias_one_map", lambda t: t.replace(
        "map with one queue entry and three names",
        "map with two queue entries and three names")),

    ("cannot_create", lambda t: t.replace(
        "cannot create the arena at all", "creates the arena at once")),
    ("no_case", lambda t: t.replace("has no HOOK_POINT",
                                    "has a HOOK_POINT")),
    ("null_default", lambda t: t.replace(
        '"default: return nullptr;"', '"default: return a handler;"')),
    ("no_zone_file", lambda t: t.replace(
        "there is no zone file in", "there is a zone file in")),
    ("nothing_spawned", lambda t: t.replace(
        "nothing is spawned", "everything is spawned")),

    ("ws_ally", lambda t: t.replace("WorldSafeLoc 6276",
                                    "WorldSafeLoc 6286")),
    ("ws_horde", lambda t: t.replace("WorldSafeLoc 6277",
                                     "WorldSafeLoc 6287")),
    ("ws_go", lambda t: t.replace("WorldSafeLoc 6896",
                                  "WorldSafeLoc 6906")),
    ("t1_x", lambda t: t.replace("X: 1052.47", "X: 1053.47")),
    ("t1_y", lambda t: t.replace("Y: -364.773", "Y: -365.773")),
    ("t1_z", lambda t: t.replace("Z: 1.89676", "Z: 2.89676")),
    ("t1_facing", lambda t: t.replace("114.343 deg = 1.9957 rad",
                                      "114.343 deg = 2.9957 rad")),
    ("t2_x", lambda t: t.replace("X: 966.125", "X: 967.125")),
    ("t2_y", lambda t: t.replace("Y: -290.78", "Y: -291.78")),
    ("t2_z", lambda t: t.replace("Z: 3.28703", "Z: 4.28703")),
    ("t2_facing", lambda t: t.replace("297.523 deg = 5.1928 rad",
                                      "297.523 deg = 4.1928 rad")),
    ("go_x", lambda t: t.replace("X: 1031.07", "X: 1032.07")),
    ("go_y", lambda t: t.replace("Y: -334.044", "Y: -335.044")),
    ("go_z", lambda t: t.replace("Z: 0.776609", "Z: 1.776609")),
    ("go_facing", lambda t: t.replace("131.268 deg = 2.2911 rad",
                                      "131.268 deg = 3.2911 rad")),
    ("comment_gold", lambda t: t.replace(
        '"Kul Tiras Arena - Gold Team - Start"',
        '"Kul Tiras Arena - Red Team - Start"')),
    ("comments_name", lambda t: t.replace('both say "Kul Tiras Arena"',
                                          'both say "Boralus Arena"')),
    ("gy_claim", lambda t: t.replace(
        "No arena graveyard row exists",
        "An arena graveyard row exists")),
    ("three_rows", lambda t: t.replace("has exactly three rows",
                                       "has exactly four rows")),
    ("dist", lambda t: t.replace("113.71 units", "123.71 units")),
    ("mid", lambda t: t.replace("about 1009.298, -327.776",
                                "about 1009.398, -327.776")),
    ("half", lambda t: t.replace("56.86 units", "66.86 units")),
    ("axis", lambda t: t.replace("86.35 apart on X", "96.35 apart on X")),
    ("bearing", lambda t: t.replace("is 139.41 deg", "is 149.41 deg")),
    ("off1", lambda t: t.replace("25.06 deg off", "26.06 deg off")),
    ("off2", lambda t: t.replace("21.88 deg off", "22.88 deg off")),
    ("go_offset", lambda t: t.replace("22.66 units from the midpoint",
                                      "23.66 units from the midpoint")),

    ("gate_claim", lambda t: t.replace(
        "None. This core spawns no gates on map 1825",
        "Two. This core spawns gates on map 1825")),
    ("gates_unverified", lambda t: t.replace(
        "Gate count, entries and coordinates are unverified.",
        "Gate count, entries and coordinates are verified.")),

    ("pillar_disagree", lambda t: t.replace(
        "Sources disagree on how many pillars this map has.",
        "Sources agree on how many pillars this map has.")),
    ("quote_liquipedia", lambda t: t.replace(
        "two pillars in the middle area", "six pillars in the corner")),
    ("quote_blizzard", lambda t: t.replace(
        "four pillars for players to dance around",
        "one pillar for players to dance around")),
    ("shark", lambda t: t.replace("shark hanging from it",
                                  "anchor hanging from it")),
    ("count_conflict", lambda t: t.replace(
        "Pillar count is therefore conflicting between",
        "Pillar count is therefore agreed between")),
    ("majority_reading", lambda t: t.replace(
        "the majority reading is two LoS pillars in the",
        "the only reading is six LoS pillars in the")),
    ("pillar_unverified", lambda t: t.replace(
        "Pillar positions: unverified.", "Pillar positions: verified.")),
    ("fence_unverified", lambda t: t.replace(
        'Fence side: unverified beyond "one side"',
        'Fence side: verified on the north side')),
    ("prose_only", lambda t: t.replace(
        "section is prose only", "section is data driven")),

    ("one_level", lambda t: t.replace(
        "One level as far as any readable source goes",
        "Two levels as far as any readable source goes")),
    ("z_spread", lambda t: t.replace("Spread across all three: 2.51 "
                                     "units", "Spread across all three: "
                                     "3.51 units")),
    ("spawn_gap", lambda t: t.replace(
        "spawn floors differ\nby 1.39 units",
        "spawn floors differ\nby 2.39 units")),
    ("ramps", lambda t: t.replace("Ramps: unverified.", "Ramps: verified.")),

    ("caution_roles", lambda t: t.replace("Read with caution",
                                          "Read without caution")),
    ("no_coord_roles", lambda t: t.replace("not from coordinates",
                                           "directly from coordinates")),
    ("race_pillars", lambda t: t.replace("Race for the middle pillars",
                                         "Race for the open ends")),
    ("diagonal", lambda t: t.replace("diagonal (86.35 by 73.99)",
                                     "diagonal (96.35 by 73.99)")),

    ("buff_claim", lambda t: t.replace(
        "None spawned. This core places no Shadow Sight orbs",
        "Two spawned. This core places Shadow Sight orbs")),
    ("buffs_no_class", lambda t: t.replace(
        "because no zone class exists for battleground 897",
        "because a zone class exists for battleground 897")),
    ("spell", lambda t: t.replace("34709", "34710")),
    ("spell_dmg", lambda t: t.replace("+5% damage taken",
                                      "+6% damage taken")),

    ("flow_head", lambda t: t.replace(
        "The queue selects this map and then fails:",
        "The queue selects this map and then succeeds:")),
    ("flow_row", lambda t: t.replace('battleground_template row 897',
                                     'battleground_template row 898')),
    ("flow_no_case", lambda t: t.replace(
        "has no HOOK_POINT case and returns",
        "has a HOOK_POINT case and returns")),
    ("flow_no_instance", lambda t: t.replace(
        "a queue pop produces no instance",
        "a queue pop produces a live instance")),
    ("name_map_id", lambda t: t.replace(
        "map id to teleports and waypoints: 1825",
        "map id to teleports and waypoints: 1826")),
    ("name_bg_id", lambda t: t.replace("battleground id: 897",
                                       "battleground id: 898")),
    ("name_maplist", lambda t: t.replace(
        "name in the client's map list: Hook Point",
        "name in the client's map list: Kul Tiras Arena")),
    ("name_zone_unv", lambda t: t.replace(
        "zone id on the instance: 9278 or 9279, unverified",
        "zone id on the instance: 9278, verified")),

    ("width_inflate", lambda t: t.replace(
        "=== 6. BUFF PICKUPS ===",
        "=== 6. BUFF PICKUPS AND A GREAT DEAL OF ADDITIONAL TEXT "
        "THAT MAKES THIS LINE FAR TOO LONG ===")),
]

FUNC_MARK = "BattlegroundMgr::CreateNewBattleground"
SWITCH_MARK = "switch (bgTypeId)"


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


DOC_BLOCK = (r"%s \(WorldSafeLoc %d[^)]*\):\n"
             r"  X: (-?\d+\.\d+)\n"
             r"  Y: (-?\d+\.\d+)\n"
             r"  Z: (-?\d+\.\d+)\n"
             r"  Facing: (-?\d+\.\d+) deg = (-?\d+\.\d+) rad")


def parse_sql_rows(sql):
    """id -> {x, y, z, facing, comment} for rows on map 1825."""
    rows = {}
    pattern = (r"\((\d+),1825,(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.\d+),"
               r"(-?\d+\.\d+),'([^']*)'\)")
    for m in re.finditer(pattern, sql):
        rows[int(m.group(1))] = {
            "x": float(m.group(2)), "y": float(m.group(3)),
            "z": float(m.group(4)), "f": float(m.group(5)),
            "comment": m.group(6)}
    return rows


def parse_doc_rows(text):
    blocks = {}
    for wid, label in ((6276, "Purple team"), (6277, "Gold team"),
                       (6896, "Game On target")):
        m = re.search(DOC_BLOCK % (re.escape(label), wid), text)
        if m:
            blocks[wid] = {
                "x": float(m.group(1)), "y": float(m.group(2)),
                "z": float(m.group(3)), "f": float(m.group(4)),
                "rad": m.group(5)}
    return blocks


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
        rad = round(math.radians(d["f"]), len(d["rad"].split(".")[1]))
        if abs(rad - float(d["rad"])) > 1e-9:
            ok = fail("%s: %s deg should be %.4f rad, doc says %s"
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

    a, b, go = src[6276], src[6277], src[GO_ID]
    cx, cy = (a["x"] + b["x"]) / 2.0, (a["y"] + b["y"]) / 2.0
    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])

    checks = [
        ("start to start", dist((a["x"], a["y"]), (b["x"], b["y"])),
         r"Distance start to start: (\d+\.\d+)"),
        ("start to midpoint", dist((a["x"], a["y"]), (cx, cy)),
         r"Each start is (\d+\.\d+) units"),
        ("axis X", abs(a["x"] - b["x"]), r"(\d+\.\d+) apart on X"),
        ("axis Y", abs(a["y"] - b["y"]), r"apart on X and (\d+\.\d+) "
                                         r"apart on Y"),
        ("gameon to midpoint", dist((go["x"], go["y"]), (cx, cy)),
         r"Game On target is (\d+\.\d+) units"),
    ]
    for label, value, pattern in checks:
        got = round(value, 2)
        want = grab(pattern)
        mark = "ok " if abs(got - want) <= 0.01 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %8.2f  recomputed %8.2f  %s"
                     % (label, want, got, mark))

    m = re.search(r"Midpoint of the two starts: about (-?\d+\.\d+), "
                  r"(-?\d+\.\d+)", text)
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
    want_b = grab(r"Bearing from Purple to Gold is (\d+\.\d+) deg")
    mark = "ok " if abs(bearing - want_b) <= 0.01 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.2f  recomputed %8.2f  %s"
                 % ("bearing P->G", want_b, bearing, mark))

    for label, face, pattern, ref in (
            ("P off bearing", a["f"],
             r"([\d.]+) deg off that bearing", bearing),
            ("G off bearing", b["f"],
             r"([\d.]+) deg off the reverse", (bearing + 180) % 360)):
        want = grab(pattern)
        diff = abs(face - ref)
        diff = min(diff, 360 - diff)
        mark = "ok " if abs(diff - want) <= 0.01 else "BAD"
        if mark == "BAD":
            ok = False
        lines.append("    %-20s doc %8.2f  recomputed %8.2f  %s"
                     % (label, want, diff, mark))

    want_spread = grab(r"Spread across all three: (\d+\.\d+) units")
    got_spread = round(max(a["z"], b["z"], go["z"])
                       - min(a["z"], b["z"], go["z"]), 2)
    mark = "ok " if abs(got_spread - want_spread) <= 0.01 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.2f  recomputed %8.2f  %s"
                 % ("Z spread", want_spread, got_spread, mark))

    want_gap = grab(r"differ\nby (\d+\.\d+) units")
    got_gap = round(max(a["z"], b["z"]) - min(a["z"], b["z"]), 2)
    mark = "ok " if abs(got_gap - want_gap) <= 0.01 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-20s doc %8.2f  recomputed %8.2f  %s"
                 % ("spawn Z gap", want_gap, got_gap, mark))

    return ok, lines


def absence_stage(text, corpora):
    """Recompute the document's negative claims from the source data."""
    ftext = flat(text)
    sql = corpora["world_safe_locs (8.x)"]
    mgr = corpora["BattlegroundMgr.cpp"]
    lines, ok = [], True

    rows = parse_sql_rows(sql)
    mark = "ok " if set(rows) == set(MAP_ROWS) else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s expect %s  found %s  %s"
                 % ("ids on map 1825", sorted(MAP_ROWS), sorted(rows),
                    mark))

    gy_words = ("graveyard", "corpse", "gy")
    has_gy = any(w in r["comment"].lower() for r in rows.values()
                 for w in gy_words)
    claims_none = "No arena graveyard row exists on map 1825" in ftext
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

    body = switch_body(mgr)
    labels = re.findall(r"case BATTLEGROUND_(\w+):", body)
    hook = "HOOK_POINT" in labels
    claims = "has no HOOK_POINT" in ftext
    mark = "ok " if (not hook) and claims else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %-14s doc claims no case  %s"
                 % ("CreateNewBattleground case",
                    "found HOOK_POINT" if hook else "none", mark))

    nulls = "return nullptr;" in body
    claims_null = '"default: return nullptr;"' in ftext
    mark = "ok " if nulls and claims_null else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %-14s doc quotes it  %s"
                 % ("default branch returns null",
                    "yes" if nulls else "no", mark))

    return ok, lines


def alias_stage(text, corpora, tpl):
    """The alias claims: one map, one row, Hook Point name upstream."""
    ftext = flat(text)
    sql = corpora["world_safe_locs (8.x)"]
    sd = corpora["SharedDefines.h"]
    dm = corpora["Map_KulTirasArena.lua"]
    lines, ok = [], True

    def check(label, cond):
        nonlocal ok
        mark = "ok " if cond else "BAD"
        if not cond:
            ok = False
        lines.append("    %-34s %s" % (label, mark))
        return cond

    rows = [ln for ln in tpl.splitlines()
            if re.search(r"tiras|hook", ln, re.I)]
    check("template: exactly one Tiras/Hook row",
          len(rows) == 1 and "897" in rows[0]
          and "'Hook Point'" in rows[0])
    check("doc claims that single row",
          "battleground_template has a single row for it, id 897"
          in ftext)

    check('datamine MapName is "Hook Point"',
          'MapName = "Hook Point"' in dm)
    check("doc quotes that MapName",
          'its MapName field says "Hook Point"' in ftext)
    check("datamine directory is KulTirasArena",
          "Directory = [[KulTirasArena]]" in dm)
    check("doc quotes that directory",
          "Map.dbc has a single entry, directory KulTirasArena"
          in ftext)

    rows1825 = parse_sql_rows(sql)
    start_comments = [rows1825[w]["comment"] for w in (6276, 6277)
                      if w in rows1825]
    carry = len(start_comments) == 2 and all(
        "Kul Tiras Arena" in c for c in start_comments)
    check("both start comments carry Kul Tiras Arena", carry)
    check("doc says both comments carry it",
          'both say "Kul Tiras Arena"' in ftext)

    enum_ok = "BATTLEGROUND_HOOK_POINT     = 897" in sd
    check("SharedDefines declares HOOK_POINT 897", enum_ok)
    no_kul = re.search(r"BATTLEGROUND_\w*TIRAS", sd, re.I) is None
    check("no battleground enum named Kul Tiras", no_kul)
    check("doc claims no such enum", "no Kul Tiras arena enum" in ftext)
    cont = "MAP_KUL_TIRAS               = 1643" in sd
    check("MAP_KUL_TIRAS = 1643 present", cont)
    check("doc says 1643 is the continent",
          "MAP_KUL_TIRAS = 1643 is the" in ftext)

    return ok, lines


def zones_stage(names):
    """No zone file for this battleground, under any plausible spelling."""
    lines, ok = [], True
    hits = [n for n in names
            if re.search(r"hook|hp|kultiras|kul_tiras", n, re.I)]
    mark = "ok " if not hits else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %d files, matches %s  %s"
                 % ("Zones directory", len(names), hits or "none", mark))
    return ok, lines


def main():
    if not os.path.exists(DELIVERABLE):
        print("MISSING DELIVERABLE: %s" % DELIVERABLE)
        return 1
    with open(DELIVERABLE) as fh:
        original = fh.read()

    print("=" * 66)
    print("AUDIT: Arena_Kul_Tiras_Arena_COMPLETED.txt (Step 12)")
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
        "Map_KulTirasArena.lua": gh_content(DM_REPO, DM_PATH),
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
        "coordinate changed": original.replace("X: 1052.47",
                                               "X: 1022.47"),
        "distance changed": original.replace("113.71 units",
                                             "123.71 units"),
        "radians changed": original.replace("1.9957 rad", "2.9957 rad"),
        "bearing changed": original.replace("is 139.41 deg",
                                            "is 149.41 deg"),
        "spread changed": original.replace("all three: 2.51 units",
                                           "all three: 3.51 units"),
        "midpoint changed": original.replace("about 1009.298, -327.776",
                                             "about 1009.398, -327.776"),
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
        "\n(9999,1825,1000.0,-300.0,1.5,0.0,"
        "'Kul Tiras Arena - Graveyard'),")
    if absence_stage(original, probe_corpora)[0]:
        print("    absence stage did not react to a graveyard row")
        return 1
    print("    absence stage reacts to a graveyard row (verified)")
    probe_corpora = dict(corpora)
    probe_corpora["BattlegroundMgr.cpp"] = corpora[
        "BattlegroundMgr.cpp"].replace(
            "case BATTLEGROUND_MUGAMBALA:",
            "case BATTLEGROUND_HOOK_POINT:\n            bg = nullptr;\n"
            "            break;\n        case BATTLEGROUND_MUGAMBALA:", 1)
    if absence_stage(original, probe_corpora)[0]:
        print("    absence stage did not react to a HOOK_POINT case")
        return 1
    print("    absence stage reacts to a HOOK_POINT case (verified)")

    print("\n[6] No-invented-coordinates trace")
    ok, lines, _ = coord_trace(original, corpora)
    for line in lines:
        print(line)
    if not ok:
        print("    INVENTED COORDINATES FOUND")
        return 1
    probe = original.replace("X: 1052.47", "X: 1022.47")
    if probe == original or coord_trace(probe, corpora)[0]:
        print("    trace did not react to an invented coordinate")
        return 1
    print("    trace reacts to an invented coordinate (verified)")

    print("\n[7] Alias identity: one map under two names")
    ok, lines = alias_stage(original, corpora,
                            corpora["battleground_template"])
    for line in lines:
        print(line)
    if not ok:
        print("    ALIAS CLAIMS DO NOT MATCH THE SOURCES")
        return 1
    probe_tpl = corpora["battleground_template"] + (
        "\n(999, 0, 5, 90, 120, 6276, 6277, 0, 1, '', "
        "'Kul Tiras Arena'),")
    if alias_stage(original, corpora, probe_tpl)[0]:
        print("    alias stage did not react to a second template row")
        return 1
    print("    alias stage reacts to a second template row (verified)")
    probe_corpora = dict(corpora)
    probe_corpora["Map_KulTirasArena.lua"] = corpora[
        "Map_KulTirasArena.lua"].replace('MapName = "Hook Point"',
                                         'MapName = "Kul Tiras Arena"')
    if alias_stage(original, probe_corpora,
                   corpora["battleground_template"])[0]:
        print("    alias stage did not react to a changed MapName")
        return 1
    print("    alias stage reacts to a changed MapName (verified)")
    probe_corpora = dict(corpora)
    probe_corpora["SharedDefines.h"] = corpora[
        "SharedDefines.h"].replace(
            "BATTLEGROUND_HOOK_POINT     = 897",
            "BATTLEGROUND_KUL_TIRAS      = 897,\n"
            "    BATTLEGROUND_HOOK_POINT     = 897")
    if alias_stage(original, probe_corpora,
                   corpora["battleground_template"])[0]:
        print("    alias stage did not react to a Kul Tiras enum")
        return 1
    print("    alias stage reacts to a Kul Tiras enum (verified)")

    print("\n[8] The missing zone file, checked against the tree")
    out = subprocess.run(
        ["gh", "api", "repos/%s/contents/%s" % (HP_REPO, ZONES_PATH),
         "--jq", ".[].name"], capture_output=True, text=True)
    if out.returncode != 0:
        print("    directory listing failed: %s" % out.stderr.strip())
        return 1
    names = [n for n in out.stdout.split("\n") if n]
    ok, lines = zones_stage(names)
    for line in lines:
        print(line)
    if not ok:
        print("    ZONES DIRECTORY DOES NOT MATCH")
        return 1
    if zones_stage(["BattlegroundHP.cpp"] + names)[0]:
        print("    zones stage did not react to a Hook Point file")
        return 1
    print("    zones stage reacts to a Hook Point file (verified)")

    print("\n" + "=" * 66)
    print("AUDIT RESULT: PASS")
    print("  static checks: %d/%d" % (passed, len(STATIC_CHECKS)))
    print("  mutations:     %d/%d" % (detected, len(MUTATIONS)))
    print("=" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())
