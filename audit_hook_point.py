#!/usr/bin/env python3
"""Mutation-tested audit for Arena_Hook_Point_COMPLETED.txt (Step 10).

Six independent stages:
  1. static claims inside the document
  2. mutation testing: every claim must fail when its value is altered
  3. source cross-check: every quoted value must exist upstream
  4. derived arithmetic recomputed from the source rows
  5. negative claims recomputed from the source data
  6. coordinate trace: no number may be invented

Stage 7 covers the CreateBattleground switch and the Zones directory,
because this arena's whole story is the absence of a zone class.
"""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import (gh_content, source_stage, mutation_probe,
                          coord_trace, missing)

DELIVERABLE = ("/home/user/Junk/# Ai Research prompts/Arenas-completed/"
               "Arena_Hook_Point_COMPLETED.txt")

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

SWITCH_ORDER = ["AV", "WS", "AB", "NA", "BE", "EY", "RL", "SA", "DS", "RV",
                "IC", "TP", "BFG", "TTP", "TVA", "NNA", "AF", "BEG", "BRH",
                "MUGAMBALA", "RB", "AA"]
CASE_LIST = ("cases for AV, WS, AB, NA, BE, EY, RL, SA, DS, RV, IC, TP, "
             "BFG, TTP, TVA, NNA, AF, BEG, BRH and MUGAMBALA")

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
        ("mugambala enum", "BATTLEGROUND_MUGAMBALA      = 903"),
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

STATIC_CHECKS = [
    ("file_exists", lambda t: os.path.exists(DELIVERABLE)),
    ("min_lines", lambda t: len(t.splitlines()) >= 200),
    ("max_width_78", lambda t: all(len(l) <= 78 for l in t.splitlines())),
    ("title_completed",
     lambda t: t.splitlines()[0].endswith("- COMPLETED ===")),
    ("title_map_1825", lambda t: "MAP 1825" in t.splitlines()[0]),
    ("eight_sections", lambda t: all(
        "=== %d. " % n in t for n in range(1, 9))),

    ("map_1825", lambda t: "Arena map ID: 1825" in t),
    ("dir", lambda t: "Map.dbc directory: KulTirasArena\n" in t),
    ("instance_type_4", lambda t: "InstanceType: 4" in t),
    ("zone_9278", lambda t: 'AreaTable zone: 9278 "Kul Tiras Arena"' in t),
    ("zone_9279", lambda t: '9279\n  "Hook Point"' in t),
    ("zone_ambiguous",
     lambda t: "which\n  of the two the instance reports is unverified" in t),
    ("expansion_field_7", lambda t: "ExpansionID field in the map row: 7" in t),
    ("wdt", lambda t: "1712797" in t),
    ("no_legacy", lambda t: "No legacy duplicate" in t),
    ("bg_897", lambda t: 'Battleground entry: 897 "Hook Point"' in t),
    ("max_players_5", lambda t: "MaxPlayersPerTeam 5" in t),
    ("lvl_90_120", lambda t: "MinLvl 90, MaxLvl 120" in t),
    ("start_max_dist_0", lambda t: "StartMaxDist 0" in t),
    ("weight_1", lambda t: "Weight 1" in t),
    ("patch_801", lambda t: "patch 8.0.1" in t),
    ("location", lambda t: "Location: Ashvane Company Yards, Boralus" in t),

    ("headline", lambda t: "the map exists, the arena does not" in t),
    ("enum_declared", lambda t: "BATTLEGROUND_HOOK_POINT = 897" in t),
    ("func_named",
     lambda t: "CreateNewBattleground has cases for" in re.sub(r"\s+", " ", t)),
    ("func_no_old_name",
     lambda t: "BattlegroundMgr::CreateBattleground" not in t),
    ("no_case", lambda t: "no case for HOOK_POINT" in t),
    ("null_default", lambda t: "returns\n    nullptr" in t),
    ("no_zone_file", lambda t: "no Hook Point zone file" in t),
    ("case_list", lambda t: CASE_LIST in re.sub(r"\s+", " ", t)),

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
    ("comment_purple", lambda t: "Kul Tiras Arena - Purple Team - Start" in t),
    ("comment_gold", lambda t: "Kul Tiras Arena - Gold Team - Start" in t),
    ("comment_go",
     lambda t: "Arena - Kul Tiras - Teleport Target - Game On" in t),
    ("colour_naming", lambda t: "Purple Team" in t and "Gold Team" in t),
    ("no_gy", lambda t: "No arena graveyard row exists on map 1825" in t),
    ("three_rows", lambda t: "exactly three rows" in t),
    ("dist", lambda t: "113.71 units" in t),
    ("mid", lambda t: "about 1009.298, -327.776" in t),
    ("half", lambda t: "56.86 units" in t),
    ("axis", lambda t: "86.35 apart on X and 73.99 apart on Y" in t),
    ("bearing", lambda t: "Bearing from Purple to Gold is 139.41 deg" in t),
    ("off1", lambda t: "25.06 deg off that bearing" in t),
    ("off2", lambda t: "21.88 deg off the reverse" in t),
    ("go_offset", lambda t: "22.66 units from the midpoint" in t),

    ("gates_none", lambda t: "None. This core spawns no gates" in t),
    ("gates_unverified", lambda t: "gate\ncount, entries and coordinates are "
                                   "all unverified" in t
                                   or "count, entries and coordinates are all "
                                      "unverified" in t),
    ("pillars_two", lambda t: "Pillar count: 2" in t),
    ("liq_quote", lambda t: "two pillars in the middle area" in t),
    ("namu_quote", lambda t: "tall\n   and long wooden fence" in t),
    ("pillar_unverified", lambda t: "Pillar positions: unverified" in t),
    ("fence_unverified", lambda t: "Fence side: unverified" in t),
    ("two_sources_only",
     lambda t: "This section rests entirely on the two wiki pages" in t),

    ("one_level", lambda t: "One level as far as any readable source" in t),
    ("z_list_go", lambda t: "Game On target:    0.776609" in t),
    ("z_list_purple", lambda t: "Purple team start: 1.89676" in t),
    ("z_list_gold", lambda t: "Gold team start:   3.28703" in t),
    ("z_spread", lambda t: "Spread across all three: 2.51 units" in t),
    ("spawn_gap", lambda t: "differ\nby 1.39 units" in t),
    ("ramps", lambda t: "Ramps: unverified" in t),

    ("role_melee", lambda t: "Melee DPS:" in t),
    ("role_ranged", lambda t: "Ranged DPS:" in t),
    ("role_healer", lambda t: "Healers:" in t),
    ("caution_roles", lambda t: "Read with caution" in t),
    ("no_coord_roles",
     lambda t: "not\nfrom coordinates" in t or "not from coordinates" in t),

    ("buffs_none",
     lambda t: "None spawned. This core places no Shadow Sight" in t),
    ("buffs_unverified",
     lambda t: "count, object entries, positions and respawn are all "
               "unverified" in t),
    ("no_copy_warning",
     lambda t: "Do not copy the Tol'viron or Tiger's Peak" in t),
    ("spell", lambda t: "34709" in t),
    ("spell_name", lambda t: "Shadow Sight" in t),
    ("spell_dmg", lambda t: "+5% damage taken" in t),

    ("flow_fail", lambda t: "fails to produce an instance" in t),
    ("flow_inherited", lambda t: "inherited from Arena, not\nper-map" in t),
    ("flow_override",
     lambda t: "Nothing on this map overrides them" in t),

    ("sources", lambda t: "Sources:" in t),
    ("unverified", lambda t: "Unverified:" in t),
    ("src_mgr", lambda t: "BattlegroundMgr.cpp" in t),
    ("src_datamine", lambda t: "Map_KulTirasArena.lua" in t),
    ("src_wiki", lambda t: 'Warcraft Wiki "Hook Point (arena)"' in t),
    ("src_liquipedia", lambda t: 'Liquipedia "Hook Point"' in t),
    ("src_namu", lambda t: "NamuWiki arena page" in t),
    ("src_wowhead", lambda t: 'Wowhead zones 9278 "Kul Tiras Arena" '
                              'and 9279 "Hook Point"' in t),
    ("unv_graveyard", lambda t: "Graveyard location (no row on map 1825)" in t),
    ("unv_gates", lambda t: "Gate objects: count, entries, positions" in t),
    ("unv_orbs",
     lambda t: "Shadow Sight orbs: count, entries, positions, respawn" in t),
]

MUTATIONS = [
    ("map_id", lambda t: t.replace("Arena map ID: 1825",
                                   "Arena map ID: 1826")),
    ("directory", lambda t: t.replace("KulTirasArena", "KulTirasArena2")),
    ("zone", lambda t: t.replace('AreaTable zone: 9278 "Kul Tiras Arena"',
                                 'AreaTable zone: 9288 "Kul Tiras Arena"')),
    ("zone_other", lambda t: t.replace('9279\n  "Hook Point"',
                                       '9271\n  "Hook Point"')),
    ("zone_confidence", lambda t: t.replace(
        "which\n  of the two the instance reports is unverified",
        "which\n  of the two the instance reports is 9278")),
    ("expansion_field", lambda t: t.replace("map row: 7", "map row: 6")),
    ("wdt", lambda t: t.replace("1712797", "1712798")),
    ("bg_entry", lambda t: t.replace('Battleground entry: 897',
                                     'Battleground entry: 898')),
    ("max_players", lambda t: t.replace("MaxPlayersPerTeam 5",
                                        "MaxPlayersPerTeam 10")),
    ("levels", lambda t: t.replace("MinLvl 90, MaxLvl 120",
                                   "MinLvl 10, MaxLvl 120")),
    ("start_max_dist", lambda t: t.replace("StartMaxDist 0",
                                           "StartMaxDist 10")),
    ("weight", lambda t: t.replace("Weight 1", "Weight 0")),
    ("patch", lambda t: t.replace("patch 8.0.1", "patch 8.0.2")),
    ("location", lambda t: t.replace("Ashvane Company Yards",
                                     "Ashvane Company Docks")),
    ("enum_value", lambda t: t.replace("BATTLEGROUND_HOOK_POINT = 897",
                                       "BATTLEGROUND_HOOK_POINT = 898")),
    ("func_name", lambda t: t.replace("CreateNewBattleground",
                                      "CreateBattleground")),
    ("case_claim", lambda t: t.replace("no case for HOOK_POINT",
                                       "a case for HOOK_POINT")),
    ("null_claim", lambda t: t.replace("returns\n    nullptr",
                                       "returns\n    a handler")),
    ("zone_file_claim", lambda t: t.replace("no Hook Point zone file",
                                            "one Hook Point zone file")),
    ("case_list_drop", lambda t: t.replace("BRH and MUGAMBALA",
                                           "BRH and MB")),
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
    ("comment_purple", lambda t: t.replace("Purple Team - Start",
                                           "Purple Team - Begin")),
    ("gy_claim", lambda t: t.replace("No arena graveyard row exists",
                                     "An arena graveyard row exists")),
    ("three_rows", lambda t: t.replace("exactly three rows",
                                       "exactly four rows")),
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
    ("gate_claim", lambda t: t.replace("None. This core spawns no gates",
                                       "Two. This core spawns gates")),
    ("pillar_count", lambda t: t.replace("Pillar count: 2",
                                         "Pillar count: 3")),
    ("pillar_unverified", lambda t: t.replace("Pillar positions: unverified",
                                              "Pillar positions: verified")),
    ("fence_claim", lambda t: t.replace("Fence side: unverified",
                                        "Fence side: the north side")),
    ("level_claim", lambda t: t.replace("One level as far as any readable",
                                        "Two levels as far as any readable")),
    ("z_spread", lambda t: t.replace("Spread across all three: 2.51 units",
                                     "Spread across all three: 3.51 units")),
    ("spawn_gap", lambda t: t.replace("differ\nby 1.39 units",
                                      "differ\nby 2.39 units")),
    ("ramps", lambda t: t.replace("Ramps: unverified", "Ramps: verified")),
    ("buff_claim", lambda t: t.replace(
        "None spawned. This core places no Shadow Sight",
        "Orbs spawned. This core places two Shadow Sight")),
    ("spell", lambda t: t.replace("34709", "34708")),
    ("spell_dmg", lambda t: t.replace("+5% damage taken",
                                      "+10% damage taken")),
    ("flow_claim", lambda t: t.replace("fails to produce an instance",
                                       "produces an instance")),
    ("flow_override", lambda t: t.replace("Nothing on this map overrides them",
                                          "Something on this map overrides them")),
    ("width_inflate", lambda t: t.replace(
        "=== 2. GATES ===",
        "=== 2. GATES AND A GREAT DEAL OF ADDITIONAL TEXT THAT MAKES THIS "
        "LINE FAR TOO LONG ===")),
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


def case_labels(body):
    return re.findall(r"case BATTLEGROUND_(\w+):", body)


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


DOC_BLOCK = (r"%s \(WorldSafeLoc %d[^)]*\):\n"
             r"  X: (-?\d+\.\d+)\n"
             r"  Y: (-?\d+\.\d+)\n"
             r"  Z: (-?\d+\.\d+)\n"
             r"  Facing: (-?\d+\.\d+) deg = (-?\d+\.\d+) rad")


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
    """Recompute every derived claim from the source rows, not the doc."""
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
        ("axis Y", abs(a["y"] - b["y"]), r"(\d+\.\d+) apart on Y"),
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
    flat = re.sub(r"\s+", " ", text)
    sql = corpora["world_safe_locs (8.x)"]
    mgr = corpora["BattlegroundMgr.cpp"]
    sd = corpora["SharedDefines.h"]
    lines, ok = [], True

    rows = parse_sql_rows(sql)
    mark = "ok " if set(rows) == set(MAP_ROWS) else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s expect %s  found %s  %s"
                 % ("ids on map 1825", sorted(MAP_ROWS), sorted(rows), mark))

    gy_words = ("graveyard", "corpse", "gy")
    has_gy = any(w in r["comment"].lower() for r in rows.values()
                 for w in gy_words)
    claims_none = "No arena graveyard row exists on map 1825" in flat
    mark = "ok " if claims_none and not has_gy else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s rows with a graveyard comment: %-5s %s"
                 % ("no graveyard row", str(has_gy), mark))

    wants_three = "The map has exactly three rows" in flat
    mark = "ok " if wants_three and len(rows) == 3 else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s claim 3  found %d  %s"
                 % ("row count", len(rows), mark))

    body = switch_body(mgr)
    labels = case_labels(body)
    hook = "HOOK_POINT" in labels
    wants_none = "no case for HOOK_POINT" in flat
    mark = "ok " if hook != wants_none and not hook else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %-14s %s"
                 % ("CreateBattleground case",
                    "found " + ("HOOK_POINT" if hook else "none"), mark))

    declared = "BATTLEGROUND_HOOK_POINT     = 897" in sd
    mark = "ok " if declared else "BAD"
    if not declared:
        ok = False
    lines.append("    %-30s %-14s %s"
                 % ("enum declared in header", "value 897", mark))

    gated = "no case for HOOK_POINT, so the" in flat
    mark = "ok " if gated else "BAD"
    if not gated:
        ok = False
    lines.append("    %-30s %-14s %s"
                 % ("document explains the fallthrough", "stated", mark))

    nulls = "return nullptr;" in body
    mark = "ok " if nulls and "default:" in body else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %-14s %s"
                 % ("default branch returns null", "yes" if nulls else "no",
                    mark))

    return ok, lines


def switch_stage(text, mgr):
    """The case list quoted in the doc must be the real switch order."""
    flat = re.sub(r"\s+", " ", text)
    body = switch_body(mgr)
    labels = case_labels(body)

    lines, ok = [], True
    mark = "ok " if labels == SWITCH_ORDER else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %s" % ("switch order", mark))
    if mark == "BAD":
        lines.append("      doc expects %s" % SWITCH_ORDER)
        lines.append("      source has   %s" % labels)

    quoted = CASE_LIST in flat
    mark = "ok " if quoted else "BAD"
    if not quoted:
        ok = False
    lines.append("    %-30s %s" % ("doc quotes that list", mark))

    mark = "ok " if "HOOK_POINT" not in labels else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %s" % ("no HOOK_POINT case", mark))

    return ok, lines


def zones_stage(names):
    """No Hook Point zone file, under any plausible spelling."""
    lines, ok = [], True
    hits = [n for n in names
            if re.search(r"hook|hp|kultiras|kul_tiras", n, re.I)]
    mark = "ok " if not hits else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %d files, matches %s  %s"
                 % ("Zones directory", len(names), hits or "none", mark))

    cpp = sorted(n[:-4] for n in names if n.endswith(".cpp"))
    alias = {"MUGAMBALA": "MB"}          # BattlegroundMB.cpp serves 903
    expected = ["ArenaAll"] + ["Battleground" + alias.get(n, n)
                               for n in SWITCH_ORDER
                               if n not in ("RB", "AA")]
    mark = "ok " if cpp == sorted(expected) else "BAD"
    if mark == "BAD":
        ok = False
    lines.append("    %-30s %d files  %s"
                 % ("one class per switch case", len(cpp), mark))
    if mark == "BAD":
        lines.append("      expected %s" % sorted(expected))
        lines.append("      found    %s" % cpp)
    return ok, lines


def main():
    if not os.path.exists(DELIVERABLE):
        print("MISSING DELIVERABLE: %s" % DELIVERABLE)
        return 1
    with open(DELIVERABLE) as fh:
        original = fh.read()

    print("=" * 66)
    print("AUDIT: Arena_Hook_Point_COMPLETED.txt (Step 10)")
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
        "coordinate changed": original.replace("X: 1052.47", "X: 1022.47"),
        "distance changed": original.replace("113.71 units", "123.71 units"),
        "radians changed": original.replace("1.9957 rad", "2.9957 rad"),
        "bearing changed": original.replace("is 139.41 deg", "is 149.41 deg"),
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
    probe_corpora["BattlegroundMgr.cpp"] = corpora[
        "BattlegroundMgr.cpp"].replace(
            "case BATTLEGROUND_MUGAMBALA:",
            "case BATTLEGROUND_HOOK_POINT:\n            bg = nullptr;\n"
            "            break;\n        case BATTLEGROUND_MUGAMBALA:")
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

    print("\n[7] The missing zone class, checked against the tree")
    ok, lines = switch_stage(original, corpora["BattlegroundMgr.cpp"])
    for line in lines:
        print(line)
    if not ok:
        print("    SWITCH DOES NOT MATCH THE DOCUMENT")
        return 1
    import subprocess
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
