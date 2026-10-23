#!/usr/bin/env python3
"""Audit: Coordinates_Seething_Shore_COMPLETED.txt (BG coords step 4).

Stages:
  1. Static exact-literal checks (whitespace-normalised) + negatives.
  2. Mutation testing - every mutation must break a static check.
  3. Live source cross-check: LegionCore BattlegroundSeethingShore.h/.cpp,
     TrinityCore 8.x world dump, AzerothCore template (negative).
  4. Derived recompute: dump rows, script positions/offsets/timers, all
     route legs, node ring, GY neighbours, bands, airship distances -
     coordinate trace + probes.
  5. Absence claims + injection probes + gh 404 control.
"""

import math
import re
import subprocess
import sys

sys.path.insert(0, ".")
from audit_common import gh_content, source_stage, mutation_probe, coord_trace

DOC = ("# Ai Research prompts/Battleground_Coordinates/"
       "Coordinates_Seething_Shore_COMPLETED.txt")
LC = "Titans-Project/LegionCore-Reforged"
HAVEN = "HavenWoW/BFA-HavenCore"
BFA = "Titans-Project/BfaCore-Reforged"
TC = "TrinityCore/TrinityCore"
AC = "azerothcore/azerothcore-wotlk"

FILES = {
    "ssc": "src/server/game/Battlegrounds/Zones/BattlegroundSeethingShore.cpp",
    "ssh": "src/server/game/Battlegrounds/Zones/BattlegroundSeethingShore.h",
}
TC_DUMP = "sql/old/8.x/world/19071_2020_06_17/2019_10_26_01_world.sql"
AC_TEMPLATE = "data/sql/base/db_world/battleground_template.sql"

DOC_IDS = [6167, 6168, 6197, 6198, 6337, 6380]
UNVERIFIED_MIN = 15


def norm(s):
    return re.sub(r"\s+", " ", s)


# ---------------------------------------------------------------- stage 1
STATIC_CHECKS = [
    ("heading", "=== SEETHING SHORE COORDINATES - BFA 8.3.7 (TRINITYCORE) "
                "- COMPLETED ==="),
    ("step numbering", "prompt 4 of 8 (Seething Shore, map 1803)"),
    ("done line", "DONE - step 4 of 8 complete"),
    ("no-estimate", "nothing is estimated"),
    ("unverified policy", 'the entry says "unverified"'),
    # section 0
    ("no compass", "makes NO compass claims"),
    ("band", "x 1113.924 - 1461.358, y 2570.769 - 2920.885, z 2.665191 - "
             "38.53647"),
    ("airship range", "2660-3106"),
    ("airship nearest", "nearest is the Horde airship row to Graveyard 6198 "
                        "at 2660 yd"),
    ("pathing caveat", "NOT walkable-path measurements: no pathing/navmesh "
                       "source for map"),
    ("raw pattern a", "6167 x 1396.54 vs 6168 x 1309.19"),
    ("raw pattern b", "6197 x 1478.41 vs 6198 x 1378.3"),
    # section 1
    ("map line", "1803 = Seething Shore"),
    ("instance row", '"1803 ... legion-inline ... [[Seething Shore]]"'),
    ("no second id", "No second map id for this battleground appears"),
    ("haven/bfa no script", "Neither HavenWoW/BFA-HavenCore nor "
                            "Titans-Project/BfaCore-Reforged ships"),
    ("script name", "BattlegroundSeethingShore.cpp/.h"),
    ("queue unver", "which id/template your server queues is unverified"),
    # section 2
    ("no start rows", "There are NO fixed start rows in the readable dump"),
    ("teleport calc", "gunship->CalculatePassengerPosition(x, y, z)"),
    ("teleport offsets", "z + 25.0 for Alliance / z + 40.0 for Horde"),
    ("dynamic starts", "starts are DYNAMIC transport positions, not "
                       "world_safe rows"),
    ("ship entries", "Alliance gunship gameobject 278407, Horde gunship "
                     "gameobject 279254"),
    ("transport const", "(1803, 1399.684, 2766.317, 3.485144)"),
    ("transport paths unver", "Transport movement paths: unverified"),
    ("boarding", "AddPlayer casts RocketParachute spell 262359"),
    ("prep collision", "281224 (Alliance) / 281226 (Horde)"),
    ("prep unused", "defined in the script enum but never referenced"),
    # section 3
    ("no flags", "No flags, no orbs and no mine cart depots exist in "
                 "Seething Shore"),
    ("wiki three", "Three nodes are active at any given time"),
    ("wiki 1500", "first team to collect 1,500 Azerite claims victory"),
    ("controller", "creature 125269 at (1803, 1399.684, 2766.317,"),
    ("controller z", "3.485144) - same coordinates as the transport "
                     "constants"),
    ("fissure entry", "creature entry 125253"),
    ("node 1", "(1803, 1113.924, 2886.993, 38.53647)"),
    ("node 2", "(1803, 1126.649, 2781.239, 31.00365)"),
    ("node 3", "(1803, 1243.155, 2721.465, 11.96428)"),
    ("node 4", "(1803, 1257.406, 2882.731, 27.66519)"),
    ("node 5", "(1803, 1259.161, 2571.423, 8.653152)"),
    ("node 6", "(1803, 1339.556, 2785.681, 2.665191)"),
    ("node 7", "(1803, 1346.759, 2920.885, 33.31765)"),
    ("node 8", "(1803, 1361.733, 2643.267, 4.608177)"),
    ("node 9", "(1803, 1390.245, 2570.769, 7.360876)"),
    ("node 10", "(1803, 1441.059, 2700.151, 9.876933)"),
    ("node 11", "(1803, 1454.085, 2598.380, 15.35741)"),
    ("node 12", "(1803, 1461.358, 2823.238, 31.80409)"),
    ("activation", "a 30-second timer activates a random non-active"),
    ("cap three", "_activeAzerriteFissureCounter >= 3"),
    ("cap matching", 'wiki\'s "three nodes'),
    ("start queue", "three activations are queued"),
    ("queue spacing", "500 ms apart"),
    ("tick refill words", "lowers the refill timer to 10 seconds"),
    ("tick refill", "_spawnTimerDelay = 10 * IN_MILLISECONDS"),
    ("go spell a", "gameobject 281307 via spell 262749, gameobject 272471 "
                   "via spell 248674"),
    ("capture 10yd", "click within 10 yd"),
    ("capture 10yd2", "fissure creature within 10 yd"),
    ("plus100", "teamScores += 100"),
    ("plus100 words", "+100 azerite"),
    ("honor30", "30 honor"),
    ("animkit", "anim kit 2560"),
    ("fx a", "spells 262508 (Alliance) / 262512 (Horde)"),
    ("spell activate", "ActivateAzerite 248688"),
    ("spell geyser", "AzeriteGeyser 248668"),
    ("spell knock", "AzeriteKnockBack 262385"),
    ("spell quake", "EarthquakeCameraShake 248719"),
    ("vignette", "VignetteDummy creature 129344"),
    ("cap 1500", "Scores::MaxTeamScore = 1500"),
    ("near victory", "Scores::NearVictory = 1200"),
    ("nv words", "more than 1200"),
    ("world states", "world states 13844/13845 (team totals),"),
    ("world states 2", "13846 (max), 13855/13856"),
    # section 4
    ("starts limitation", "Start-to-objective routes cannot be given as "
                          "fixed point lists"),
    ("parachute unver", "parachute landing spots"),
    ("ring intro", "Ordered node ring (all twelve nodes in ascending y then "
                   "x order"),
    ("gy intro", "Island landmark rows to their nearest node (recomputed)"),
    ("sep intro", "Landmark separations (recomputed)"),
    ("cd 6", "-> node 6: 63 yd"), ("cd 10", "-> node 10: 78 yd"),
    ("cd 12", "-> node 12: 84 yd"), ("cd 8", "-> node 8: 129 yd"),
    ("cd 3", "-> node 3: 163 yd"), ("cd 7", "-> node 7: 163 yd"),
    ("cd 11", "-> node 11: 177 yd"), ("cd 4", "-> node 4: 184 yd"),
    ("cd 9", "-> node 9: 196 yd"), ("cd 5", "-> node 5: 240 yd"),
    ("cd 2", "-> node 2: 273 yd"), ("cd 1", "-> node 1: 310 yd"),
    ("ring 9-5", "9-5: 131 yd"), ("ring 5-11", "5-11: 197 yd"),
    ("ring 11-8", "11-8: 103 yd"), ("ring 8-10", "8-10: 98 yd"),
    ("ring 10-3", "10-3: 199 yd"), ("ring 3-2", "3-2: 131 yd"),
    ("ring 2-6", "2-6: 213 yd"), ("ring 6-12", "6-12: 127 yd"),
    ("ring 12-4", "12-4: 212 yd"), ("ring 4-1", "4-1: 144 yd"),
    ("ring 1-7", "1-7: 235 yd"),
    ("gyn 6167", "Graveyard 6167 -> node 8: 45 yd (next node 10: 53 yd)"),
    ("gyn 6168", "Graveyard 6168 -> node 6: 35 yd (next node 4: 95 yd)"),
    ("gyn 6197", "Graveyard 6197 -> node 9: 261 yd (next node 11: 274 yd)"),
    ("gyn 6198", "Graveyard 6198 -> node 9: 304 yd (next node 5: 327 yd)"),
    ("sep 6167-6197", "6167-6197: 356 yd"),
    ("sep 6168-6198", "6168-6198: 540 yd"),
    ("sep 6167-6168", "6167-6168: 157 yd"),
    ("sep 6197-6198", "6197-6198: 116 yd"),
    ("subregions", "Bonfire, Crash Site, Overlook, Plunge, Ridge, Ruins, "
                   "Shipwreck, Tar Pits, Temple, Tide Pools, Tower"),
    ("subregion unver", "mapping each name to a node coordinate: unverified"),
    # section 5
    ("gy 6167", 'id 6167 "Azerite BG - Graveyard, Alliance"'),
    ("gy 6167 row", "(1803, 1396.54, 2672.31, 296.226)  o 121.005"),
    ("gy 6168", 'id 6168 "Azerite BG - Graveyard, Horde"'),
    ("gy 6168 row", "(1803, 1309.19, 2803.19, 274.448)  o 279.855"),
    ("gy 6197", 'id 6197 "Azerite BG - Graveyard 2, Alliance"'),
    ("gy 6197 row", "(1803, 1478.41, 2325.35, 160.883)  o 175.68"),
    ("gy 6198", 'id 6198 "Azerite BG - Graveyard 2, Horde"'),
    ("gy 6198 row", "(1803, 1378.3, 2267.13, 89.5317)  o 154.53"),
    ("gy 6337", 'id 6337 "Azerite BG - Graveyard Airship, Alliance"'),
    ("gy 6337 row", "(1803, -29.8623, 0.520232, 20.5534)  o 0"),
    ("gy 6380", 'id 6380 "Azerite BG - Graveyard Airship, Horde"'),
    ("gy 6380 row", "(1803, 0.875362, -8.07249, 34.1691)  o 89.5371"),
    ("no point gy", "no point-owned"),
    ("dynamic gy", "DYNAMIC safe"),
    ("gy offset", "same +25 (Alliance) / +40 (Horde) z offset"),
    ("respawn ship", "every death respawns aboard the gunship"),
    ("relocate", "RelocateDeadPlayers teleports ghosts there as well"),
    ("res spells", "RocketParachute 262359 and RocketParachite2 250917"),
    ("res uncharted", "casts UnchartedTerritory 262086"),
    ("helper claim", "GetTeamWorldSafeLocks (returning 6337/6380) is "
                     "defined but never called"),
    ("rows unreferenced", "rows 6167-6198 appear nowhere in the script"),
    # section 6
    ("box entry", "creature entry 133532"),
    ("box init", "urand(180, 300) seconds"),
    ("box reroll", "re-rolled to urand(180, 300) seconds"),
    ("box window", "between 3 and 5 minutes after the match"),
    ("box geo a", "40 yd below the team's own gunship"),
    ("box geo b", "65 yd toward the enemy gunship"),
    ("box fixed unver", "fixed coordinates are unverified"),
    ("box buff unver", "What buff the box grants: unverified"),
    ("wiki sky", "additional power-ups"),
    ("no other buffs", "No other buff or power-up spawns are defined"),
    # section 7/8
    ("src path", "BattlegroundSeethingShore.h/.cpp"),
    ("src dump rows", "rows 6167, 6168, 6197, 6198,"),
    ("src exactly6", "the only map-1803 rows in the dump, checked: "
                     "exactly 6"),
    ("src no seething comment", 'no rows commented "Seething Shore"'),
    ("src no transport rows", "no transport path rows for 278407/279254"),
    ("src wiki", "warcraft.wiki.gg: Seething Shore"),
    ("negatives header", "Negative results recorded"),
    ("unverified header", "=== 8. EXPLICIT UNVERIFIED LIST ==="),
    ("unverified count", "unverified"),
]

NEGATIVE_CHECKS = [
    ("no estimated coordinate", "estimated coordinate"),
    ("no navmesh confirmed", "navmesh confirmed"),
    ("no pathing confirmed", "pathing confirmed"),
    ("no todo", "TODO"),
    ("no fixme", "FIXME"),
    ("no direct inspection", "verified by direct inspection"),
]


def run_static(text):
    flat = norm(text)
    lines, fails = [], []
    for name, lit in STATIC_CHECKS:
        if name == "unverified count":
            n = flat.count("unverified")
            hit = n >= UNVERIFIED_MIN
            lines.append("    %-26s %s (%d >= %d)"
                         % (name, "ok" if hit else "FAIL", n,
                            UNVERIFIED_MIN))
            if not hit:
                fails.append(name)
            continue
        hit = norm(lit) in flat
        lines.append("    %-26s %s" % (name, "ok" if hit else "MISSING"))
        if not hit:
            fails.append(name)
    for name, lit in NEGATIVE_CHECKS:
        hit = norm(lit) not in flat
        lines.append("    %-26s %s" % (name, "ok" if hit else "PRESENT!"))
        if not hit:
            fails.append(name)
    return fails, lines


# ---------------------------------------------------------------- stage 2
MUTATIONS = [
    ("heading", "- COMPLETED ===\nBattleground", "- DRAFT ===\nBattleground"),
    ("numbering", "prompt 4 of 8", "prompt 4 of 7"),
    ("done", "DONE - step 4 of 8 complete", "DONE - step 4 of 9 complete"),
    ("compass", "makes NO compass claims", "makes YES compass claims"),
    ("band x", "x 1113.924 - 1461.358", "x 1113.925 - 1461.358"),
    ("band z", "z 2.665191 - 38.53647", "z 2.665192 - 38.53647"),
    ("airship range", "2660-3106", "2660-3107"),
    ("airship nearest", "Graveyard 6198 at 2660 yd", "Graveyard 6198 at "
     "2661 yd"),
    ("map id", "1803 = Seething Shore", "1804 = Seething Shore"),
    ("instance patch", "legion-inline", "legion-inlinex"),
    ("dynamic start", "DYNAMIC transport positions", "STATIC transport "
     "positions"),
    ("ship a", "gameobject 278407", "gameobject 278408"),
    ("ship h", "gameobject 279254", "gameobject 279255"),
    ("teleport a", "z + 25.0 for Alliance", "z + 26.0 for Alliance"),
    ("transport const", "(1803, 1399.684, 2766.317, 3.485144)",
     "(1803, 1399.684, 2766.317, 3.485145)"),
    ("parachute spell", "RocketParachute spell 262359",
     "RocketParachute spell 262360"),
    ("prep 281224", "281224", "281225"),
    ("fissure entry", "creature entry 125253", "creature entry 125254"),
    ("controller entry", "creature 125269", "creature 125270"),
    ("node 1 triple", "(1803, 1113.924, 2886.993, 38.53647)",
     "(1803, 1113.924, 2886.993, 38.53648)"),
    ("node 6 triple", "(1803, 1339.556, 2785.681, 2.665191)",
     "(1803, 1339.556, 2785.681, 2.665192)"),
    ("node 9 triple", "(1803, 1390.245, 2570.769, 7.360876)",
     "(1803, 1390.245, 2570.769, 7.360877)"),
    ("node 12 triple", "(1803, 1461.358, 2823.238, 31.80409)",
     "(1803, 1461.358, 2823.238, 31.80410)"),
    ("activation", "a 30-second timer", "a 31-second timer"),
    ("cap3", "_activeAzerriteFissureCounter >= 3",
     "_activeAzerriteFissureCounter >= 4"),
    ("go a", "gameobject 281307", "gameobject 281308"),
    ("spell node", "via spell 262749", "via spell 262750"),
    ("plus100", "teamScores += 100", "teamScores += 101"),
    ("honor", "30 honor", "31 honor"),
    ("animkit", "anim kit 2560", "anim kit 2561"),
    ("capture range", "click within 10 yd", "click within 11 yd"),
    ("fx", "262508 (Alliance) / 262512", "262509 (Alliance) / 262512"),
    ("maxscore", "Scores::MaxTeamScore = 1500", "Scores::MaxTeamScore = "
     "1501"),
    ("nearvictory", "Scores::NearVictory = 1200", "Scores::NearVictory = "
     "1201"),
    ("ws", "13844/13845", "13844/13846"),
    ("ctrl dist a", "-> node 6: 63 yd", "-> node 6: 64 yd"),
    ("ctrl dist b", "-> node 1: 310 yd", "-> node 1: 311 yd"),
    ("ring a", "9-5: 131 yd", "9-5: 132 yd"),
    ("ring b", "1-7: 235 yd", "1-7: 236 yd"),
    ("ring c", "10-3: 199 yd", "10-3: 200 yd"),
    ("gy neigh a", "Graveyard 6167 -> node 8: 45 yd",
     "Graveyard 6167 -> node 8: 46 yd"),
    ("gy neigh b", "Graveyard 6198 -> node 9: 304 yd",
     "Graveyard 6198 -> node 9: 305 yd"),
    ("sep a", "6167-6197: 356 yd", "6167-6197: 357 yd"),
    ("sep b", "6197-6198: 116 yd", "6197-6198: 117 yd"),
    ("gy 6167 triple", "(1803, 1396.54, 2672.31, 296.226)",
     "(1803, 1396.54, 2672.31, 296.227)"),
    ("gy 6168 o", "o 279.855", "o 279.856"),
    ("gy 6380 triple", "(1803, 0.875362, -8.07249, 34.1691)",
     "(1803, 0.875362, -8.07249, 34.1692)"),
    ("no point owned", "no point-owned", "many point-owned"),
    ("never called", "defined but never called", "defined and often called"),
    ("rows nowhere", "rows 6167-6198 appear nowhere in the",
     "rows 6167-6198 appear everywhere in the"),
    ("respawn ship", "every death respawns aboard the gunship",
     "every death respawns on the island"),
    ("box entry", "creature entry 133532", "creature entry 133533"),
    ("box urand", "urand(180, 300) seconds", "urand(181, 300) seconds"),
    ("box window", "between 3 and 5 minutes", "between 3 and 6 minutes"),
    ("box drop", "40 yd below the team's own gunship",
     "41 yd below the team's own gunship"),
    ("box drift", "65 yd toward the enemy gunship",
     "66 yd toward the enemy gunship"),
    ("res spell", "RocketParachite2 250917", "RocketParachite2 250918"),
    ("exactly 6", "checked: exactly 6", "checked: exactly 7"),
    ("wiki cap", "1,500 Azerite", "1,400 Azerite"),
    ("tick refill", "_spawnTimerDelay = 10 * IN_MILLISECONDS",
     "_spawnTimerDelay = 11 * IN_MILLISECONDS"),
]


# ---------------------------------------------------------------- stage 3
def stage3(corpora):
    token_map = {
        "ssc": [
            ("controller pos", "Position const ControllerPos = { "
                               "1399.684f, 2766.317f, 3.485144f };"),
            ("node 1 pos", "{ 1113.924f, 2886.993f, 38.53647f }"),
            ("node 4 pos", "{ 1257.406f, 2882.731f, 27.66519f }"),
            ("node 8 pos", "{ 1361.733f, 2643.267f, 4.608177f }"),
            ("node 12 pos", "{ 1461.358f, 2823.238f, 31.80409f }"),
            ("transport pos", "HordeTransportPos = { 1399.684f"),
            ("go azerite", "Azerite = 281307"),
            ("go azerite2", "Azerite2 = 272471"),
            ("go horde ship", "HordeTransport = 279254"),
            ("go ally ship", "AllianceTransport = 278407"),
            ("go collision h", "HordeAirshipPrepCollision = 281226"),
            ("go collision a", "AllianceAirshipPrepCollision = 281224"),
            ("cr controller", "Controller = 125269"),
            ("cr fissure", "AzeriteFissure = 125253"),
            ("cr vignette", "VignetteDummy = 129344"),
            ("cr box", "BuffBox         = 133532"),
            ("sp activate", "ActivateAzerite = 248688"),
            ("sp summon a", "SummonAzeriteCaptureNode = 262749"),
            ("sp summon b", "SummonAzeriteCaptureNode2 = 248674"),
            ("sp knock", "AzeriteKnockBack = 262385"),
            ("sp quake", "EarthquakeCameraShake = 248719"),
            ("sp geyser", "AzeriteGeyser = 248668"),
            ("sp fx a", "AzeriteCapturedAllianceCosmeticFX = 262508"),
            ("sp fx h", "AzeriteCapturedHordeCosmeticFX = 262512"),
            ("sp chute", "RocketParachute = 262359"),
            ("sp uncharted", "UnchartedTerritory = 262086"),
            ("sp chute2", "RocketParachite2 = 250917"),
            ("score near", "NearVictory = 1200"),
            ("score max", "MaxTeamScore = 1500"),
            ("ws a", "AllianceTotalScore = 13844"),
            ("ws max", "MaxScores = 13846"),
            ("cap3 src", "_activeAzerriteFissureCounter >= 3"),
            ("tick30", "_spawnTimerDelay = 30 * IN_MILLISECONDS"),
            ("teleport off", "TEAM_ALLIANCE ? 25.0f : 40.0f"),
            ("box reroll src", "m_boxesTimers[i] = urand(180, 300) * 1000"),
            ("box geo z", "ship->GetPositionZ() - 40.0f"),
            ("box geo xy", "SimplePosXYRelocationByAngle(pos, 65.0f"),
            ("capture add", "teamScores += 100;"),
            ("capture honor", "RewardHonorToTeam(30,"),
            ("capture anim", "SetAnimKitId(2560, true)"),
            ("capture range", "IsWithinDistInMap(object, 10)"),
            ("gy helper", "GetTeamWorldSafeLocks"),
            ("gy ret a", "return 6337;"),
            ("gy ret h", "return 6380;"),
            ("gy dynamic", "CalculatePassengerPosition"),
            ("chute cast", "CastSpell(player, Spells::RocketParachute)"),
            ("create transport", "CreateTransport(GameObjects::HordeTransport"),
            ("setup fissure", "AddCreature(Creatures::AzeriteFissure"),
        ],
        "ssh": [
            ("header guard", "#define __BATTLEGROUNDSS_H"),
            ("box init", "m_boxesTimers{ urand(180, 300)*1000"),
            ("counter decl", "_activeAzerriteFissureCounter{0}"),
        ],
        "wsl": [
            ("row 6167", "(6167,1803,1396.54,2672.31,296.226,121.005,"
                         "'Azerite BG - Graveyard, Alliance'),"),
            ("row 6168", "(6168,1803,1309.19,2803.19,274.448,279.855,"
                         "'Azerite BG - Graveyard, Horde'),"),
            ("row 6197", "(6197,1803,1478.41,2325.35,160.883,175.68,"
                         "'Azerite BG - Graveyard 2, Alliance'),"),
            ("row 6198", "(6198,1803,1378.3,2267.13,89.5317,154.53,"
                         "'Azerite BG - Graveyard 2, Horde'),"),
            ("row 6337", "(6337,1803,-29.8623,0.520232,20.5534,0,"
                         "'Azerite BG - Graveyard Airship, Alliance'),"),
            ("row 6380", "(6380,1803,0.875362,-8.07249,34.1691,89.5371,"
                         "'Azerite BG - Graveyard Airship, Horde'),"),
        ],
    }
    corpora_map = {k: corpora[k] for k in token_map}
    return source_stage(corpora_map, token_map)


# ---------------------------------------------------------------- stage 4
def parse_wsl_rows(wsl):
    rows = {}
    for line in wsl.splitlines():
        m = re.match(r"\((\d+),(\d+),([^,]+),([^,]+),([^,]+),([^,]+),(.*)\)",
                     line.strip())
        if not m:
            continue
        rid = int(m.group(1))
        if rid in DOC_IDS:
            rows[rid] = {"map": m.group(2), "x": m.group(3),
                         "y": m.group(4), "z": m.group(5),
                         "facing": m.group(6)}
    return rows


def parse_script(ssc):
    out = {}
    m = re.search(r"AzeriteFissurePositions\[\] =\s*\{(.*?)\};", ssc, re.S)
    out["nodes_raw"] = re.findall(
        r"\{\s*([-\d.]+)f,\s*([-\d.]+)f,\s*([-\d.]+)f\s*\}", m.group(1))
    out["nodes"] = [(float(a), float(b), float(c))
                    for a, b, c in out["nodes_raw"]]
    m = re.search(r"ControllerPos = \{\s*([-\d.]+)f,\s*([-\d.]+)f,\s*"
                  r"([-\d.]+)f", ssc)
    out["ctrl"] = tuple(float(m.group(i)) for i in (1, 2, 3))
    m = re.search(r"TEAM_ALLIANCE \? ([\d.]+)f : ([\d.]+)f", ssc)
    out["tp_off"] = (m.group(1), m.group(2))
    m = re.search(r"GetPositionZ\(\) - ([\d.]+)f", ssc)
    out["box_z"] = m.group(1)
    m = re.search(r"SimplePosXYRelocationByAngle\(pos, ([\d.]+)f", ssc)
    out["box_xy"] = m.group(1)
    m = re.search(r"NearVictory = (\d+)", ssc)
    out["near"] = m.group(1)
    m = re.search(r"MaxTeamScore = (\d+)", ssc)
    out["max"] = m.group(1)
    m = re.search(r"_activeAzerriteFissureCounter >= (\d+)", ssc)
    out["cap3"] = m.group(1)
    # Reset() seeds the per-match initial cadence; the ctor default (90)
    # is overwritten before play. A later assignment (10) is the refill
    # timer and is checked separately below.
    idx = ssc.find("BattlegroundSeethingShore::Reset()")
    block = ssc[idx:idx + 900] if idx >= 0 else ""
    m = re.search(r"_spawnTimerDelay = (\d+) \* IN_MILLISECONDS", block)
    out["tick"] = m.group(1) if m else "NONE"
    all_ticks = re.findall(r"_spawnTimerDelay = (\d+) \* IN_MILLISECONDS",
                           ssc)
    out["tick_refill"] = "10" if "10" in all_ticks else "NONE"
    m = re.search(r"teamScores \+= (\d+)", ssc)
    out["plus"] = m.group(1)
    m = re.search(r"RewardHonorToTeam\((\d+),", ssc)
    out["honor"] = m.group(1)
    m = re.search(r"SetAnimKitId\((\d+),", ssc)
    out["anim"] = m.group(1)
    m = re.search(r"IsWithinDistInMap\(object, (\d+)\)", ssc)
    out["range"] = m.group(1)
    return out


def rd(x):
    return int(x + 0.5)


def stage4(text, corpora, probe=False):
    if probe:
        text = text.replace("(1803, 1396.54, 2672.31, 296.226)",
                            "(1803, 1396.54, 2672.31, 296.227)", 1)
    flat = norm(text)
    lines, fails = [], []

    # 4a. six dump rows
    rows = parse_wsl_rows(corpora["wsl"])
    hit = 0
    for rid in DOC_IDS:
        r = rows.get(rid)
        if not r:
            fails.append("row %d not in dump" % rid)
            continue
        triple = "(%s, %s, %s, %s)" % (r["map"], r["x"], r["y"], r["z"])
        context = triple in flat or ("id %d" % rid) in flat
        facing_ok = re.search(r"(?<![0-9.])o %s(?![0-9.])"
                              % re.escape(r["facing"]), flat)
        ok = triple in flat and context and bool(facing_ok)
        hit += ok
        if not ok:
            fails.append("row %d doc mismatch" % rid)
    lines.append("    world_safe rows matched: %d/%d" % (hit, len(DOC_IDS)))

    # 4b. script-derived values vs document
    s = parse_script(corpora["ssc"])
    cok = 0
    ct = "(1803, %s, %s, %s)" % tuple(("%g" % v).rstrip("0").rstrip(".")
                                      if False else str(v) for v in s["ctrl"])
    # controller triple as written in the doc uses the raw dump-style text
    ctrl_txt = "(1803, 1399.684, 2766.317, 3.485144)"
    want_items = [
        ("controller", ctrl_txt if ctrl_txt.split(", ")[1:] ==
         [str(s["ctrl"][0]), str(s["ctrl"][1]), str(s["ctrl"][2])] and
         ctrl_txt in flat else None),
    ]
    if ctrl_txt in flat and s["ctrl"] == (1399.684, 2766.317, 3.485144):
        cok += 1
    else:
        fails.append("controller triple (%s)" % (s["ctrl"],))
    node_ok = 0
    for (rx, ry, rz) in s["nodes_raw"]:
        triple = "(1803, %s, %s, %s)" % (rx, ry, rz)
        ok = triple in flat
        node_ok += ok
        if not ok:
            fails.append("node triple %s" % triple)
    lines.append("    controller %d/1, node triples %d/%d"
                 % (cok, node_ok, len(s["nodes"])))
    if node_ok != 12:
        fails.append("node count %d" % node_ok)

    checks = [
        ("teleport offsets", "z + %s for Alliance / z + %s for Horde"
         % s["tp_off"]),
        ("box z", "%s yd below the team's own gunship"
         % s["box_z"].rstrip("0").rstrip(".")),
        ("box xy", "%s yd toward the enemy gunship"
         % s["box_xy"].rstrip("0").rstrip(".")),
        ("near victory", "Scores::NearVictory = %s" % s["near"]),
        ("max score", "Scores::MaxTeamScore = %s" % s["max"]),
        ("cap three", "_activeAzerriteFissureCounter >= %s" % s["cap3"]),
        ("tick", "a %s-second timer" % s["tick"]),
        ("tick refill", "_spawnTimerDelay = %s * IN_MILLISECONDS"
         % s["tick_refill"]),
        ("plus100", "teamScores += %s" % s["plus"]),
        ("plus words", "+%s azerite" % s["plus"]),
        ("honor", "%s honor" % s["honor"]),
        ("anim", "anim kit %s" % s["anim"]),
        ("range", "click within %s yd" % s["range"]),
        ("near words", "more than %s" % s["near"]),
    ]
    sok = 0
    for name, want in checks:
        ok = want in flat
        sok += ok
        if not ok:
            fails.append("%s (%s)" % (name, want))
    lines.append("    script-derived scalars: %d/%d match doc"
                 % (sok, len(checks)))

    # box timer window from the header urand bounds
    m = re.search(r"m_boxesTimers\{\s*urand\((\d+),\s*(\d+)\)", corpora["ssh"])
    lo, hi = m.group(1), m.group(2)
    want = "urand(%s, %s) seconds" % (lo, hi)
    ok = want in flat
    if not ok:
        fails.append("box timer window (%s)" % want)
    # minutes window
    mins = (int(lo) + 59) // 60, (int(hi) + 59) // 60
    want = "between %d and %d minutes after the match" % (mins[0], mins[1])
    ok = want in flat
    if not ok:
        fails.append("box minutes (%s)" % want)
    lines.append("    box timers: %s / %s" %
                 ("urand(%s, %s)" % (lo, hi), "ok" if ok else "MISMATCH"))

    # 4c. distances
    nodes = s["nodes"]
    ctrl = (s["ctrl"][0], s["ctrl"][1])
    dok = 0
    for i, (x, y, z) in enumerate(nodes, start=1):
        want = "-> node %d: %d yd" % (i, rd(math.hypot(x - ctrl[0],
                                                       y - ctrl[1])))
        ok = want in flat
        dok += ok
        if not ok:
            fails.append("ctrl->node %d" % i)
    lines.append("    controller->nodes: %d/12" % dok)

    order = sorted(range(len(nodes)),
                   key=lambda i: (nodes[i][1], nodes[i][0]))
    rok = 0
    legs = []
    for k in range(len(order) - 1):
        a, b = order[k], order[k + 1]
        n = rd(math.hypot(nodes[a][0] - nodes[b][0],
                          nodes[a][1] - nodes[b][1]))
        legs.append((a + 1, b + 1, n))
        want = "%d-%d: %d yd" % (a + 1, b + 1, n)
        ok = want in flat
        rok += ok
        if not ok:
            fails.append("ring %s" % want)
    lines.append("    node ring legs: %d/11" % rok)

    gyn = {6167: 6167, 6168: 6168, 6197: 6197, 6198: 6198}
    gok = 0
    for rid in (6167, 6168, 6197, 6198):
        gx, gy = float(rows[rid]["x"]), float(rows[rid]["y"])
        ds = sorted((rd(math.hypot(gx - nx, gy - ny)), i + 1)
                    for i, (nx, ny, nz) in enumerate(nodes))
        want = "Graveyard %d -> node %d: %d yd (next node %d: %d yd)" \
            % (rid, ds[0][1], ds[0][0], ds[1][1], ds[1][0])
        ok = want in flat
        gok += ok
        if not ok:
            fails.append("gy->node %s" % want)
    lines.append("    GY->nearest node: %d/4" % gok)

    pairs = [(6167, 6197), (6168, 6198), (6167, 6168), (6197, 6198)]
    pok = 0
    for a, b in pairs:
        ax, ay = float(rows[a]["x"]), float(rows[a]["y"])
        bx, by = float(rows[b]["x"]), float(rows[b]["y"])
        want = "%d-%d: %d yd" % (a, b, rd(math.hypot(ax - bx, ay - by)))
        ok = want in flat
        pok += ok
        if not ok:
            fails.append("gy pair %s" % want)
    lines.append("    GY pairs: %d/4" % pok)

    # 4d. bands
    xs = [n[0] for n in nodes]
    ys = [n[1] for n in nodes]
    zs = [n[2] for n in nodes]
    want = "x %s - %s, y %s - %s, z %s - %s" % (
        str(min(xs)), str(max(xs)), str(min(ys)), str(max(ys)),
        str(min(zs)), str(max(zs)))
    ok = want in flat
    if not ok:
        fails.append("bands (%s)" % want)
    lines.append("    node bands: %s" % ("ok" if ok else "MISMATCH: " + want))

    # airship distances
    aair = (float(rows[6337]["x"]), float(rows[6337]["y"]))
    hair = (float(rows[6380]["x"]), float(rows[6380]["y"]))
    ds = []
    for tname, tpos in (("Alliance", aair), ("Horde", hair)):
        for rid in (6167, 6168, 6197, 6198):
            gx, gy = float(rows[rid]["x"]), float(rows[rid]["y"])
            ds.append((rd(math.hypot(tpos[0] - gx, tpos[1] - gy)),
                       tname, rid))
    lo_d, lo_team, lo_rid = min(ds)
    hi_d = max(d for d, _, _ in ds)
    ok = ("%d-%d" % (lo_d, hi_d)) in flat
    if not ok:
        fails.append("airship range (%d-%d)" % (lo_d, hi_d))
    want = ("nearest is the %s airship row to Graveyard %d at %d yd"
            % (lo_team, lo_rid, lo_d))
    ok = want in flat
    if not ok:
        fails.append("airship nearest (%s)" % want)
    lines.append("    airship distances: %d-%d yd, nearest %s/%d"
                 % (lo_d, hi_d, lo_team, lo_rid))

    # raw x pattern
    want_a = "6167 x %s vs 6168 x %s" % (rows[6167]["x"], rows[6168]["x"])
    want_b = "6197 x %s vs 6198 x %s" % (rows[6197]["x"], rows[6198]["x"])
    ok = want_a in flat and want_b in flat
    if not ok:
        fails.append("raw x pattern")
    lines.append("    raw x pattern A>H: %s" % ("ok" if ok else "MISMATCH"))

    # 4e. coord trace + probes
    ok_c, c_lines, missing_c = coord_trace(text, corpora)
    lines.extend(c_lines)
    if not ok_c:
        fails.append("coordinate trace: %s" % missing_c[:6])
    probe_txt = text.replace("(1803, 1113.924, 2886.993, 38.53647)",
                             "(1803, 1114.924, 2886.993, 38.53647)", 1)
    ok2, _, _ = coord_trace(probe_txt, corpora)
    probe_ok = (probe_txt != text) and not ok2
    lines.append("    coordinate probe reacts: %s"
                 % ("yes" if probe_ok else "no"))
    if not probe_ok:
        fails.append("coordinate probe")
    return fails, lines


# ---------------------------------------------------------------- stage 5
def stage5(text, corpora):
    lines, fails = [], []

    # dump: exactly the six map-1803 rows; no Seething comments;
    # no transport-path rows for the gunships
    m1803 = []
    for line in corpora["wsl"].splitlines():
        m = re.match(r"\((\d+),(\d+),", line.strip())
        if m and m.group(2) == "1803":
            m1803.append(int(m.group(1)))
    ok = sorted(m1803) == sorted(DOC_IDS)
    if not ok:
        fails.append("map-1803 rows = %s" % sorted(m1803))
    lines.append("    dump map-1803 rows: %d, ids match: %s"
                 % (len(m1803), "yes" if ok else "NO"))
    n_se = len(re.findall(r"(?i)seething", corpora["wsl"]))
    ok = n_se == 0
    if not ok:
        fails.append("dump has %d 'seething' rows" % n_se)
    lines.append("    dump 'Seething Shore'-commented rows: %d (need 0)"
                 % n_se)
    n_tp = len(re.findall(r",278407,|,279254,", corpora["wsl"]))
    ok = n_tp == 0
    if not ok:
        fails.append("dump transport rows = %d" % n_tp)
    lines.append("    dump gunship transport-path rows: %d (need 0)" % n_tp)

    # AzerothCore template: no Seething/Azerite row
    n_ac = len(re.findall(r"(?i)seething|azerite", corpora["act"]))
    ok = n_ac == 0
    if not ok:
        fails.append("AC template has %d Seething rows" % n_ac)
    lines.append("    AzerothCore Seething rows: %d (need 0)" % n_ac)

    # script-side absence claims
    ssc, ssh = corpora["ssc"], corpora["ssh"]
    checks = [
        ("row ids unreferenced",
         len(re.findall(r"6167|6168|6197|6198", ssc + ssh)) == 0),
        ("6337 once", len(re.findall(r"6337", ssc)) == 1),
        ("6380 once", len(re.findall(r"6380", ssc)) == 1),
        ("helper once (never called)",
         len(re.findall(r"GetTeamWorldSafeLocks", ssc)) == 1),
        ("281224 once (enum only)",
         len(re.findall(r"281224", ssc)) == 1),
        ("281226 once (enum only)",
         len(re.findall(r"281226", ssc)) == 1),
    ]
    for name, okc in checks:
        lines.append("    %-30s %s" % (name, "ok" if okc else "FAIL"))
        if not okc:
            fails.append(name)

    # Zones listings: no Seething script in either BfA core
    for repo in (HAVEN, BFA):
        res = subprocess.run(
            ["gh", "api", "repos/%s/contents/src/server/game/"
             "Battlegrounds/Zones" % repo, "--jq", ".[].name"],
            capture_output=True, text=True)
        names = [n for n in res.stdout.split() if n]
        bad = [n for n in names
               if re.search(r"(?i)seething|BattlegroundSS", n)]
        sanity = "BattlegroundAB.cpp" in names
        okc = res.returncode == 0 and sanity and not bad
        lines.append("    %-32s %d files, no Seething script: %s"
                     % (repo, len(names), "yes" if okc else "NO"))
        if not okc:
            fails.append("zones listing %s" % repo)

    # injection probes
    inj1 = text + "\nnavmesh confirmed under inspection.\n"
    f1, _ = run_static(inj1)
    r1 = "no navmesh confirmed" in f1
    lines.append("    injection probe (navmesh confirmed):  %s"
                 % ("detected" if r1 else "NOT DETECTED"))
    if not r1:
        fails.append("navmesh probe")
    inj2 = text + "\nverified by direct inspection.\n"
    f2, _ = run_static(inj2)
    r2 = "no direct inspection" in f2
    lines.append("    injection probe (direct inspection):  %s"
                 % ("detected" if r2 else "NOT DETECTED"))
    if not r2:
        fails.append("direct-inspection probe")
    stripped = text.replace("unverified", "verified")
    f3, _ = run_static(stripped)
    r3 = "unverified count" in f3
    lines.append("    injection probe (unverified stripped):%s"
                 % (" detected" if r3 else " NOT DETECTED"))
    if not r3:
        fails.append("unverified probe")

    # gh 404 control
    res = subprocess.run(
        ["gh", "api", "-X", "GET",
         "repos/Titans-Project/LegionCore-Reforged/contents/src/server/"
         "game/DoesNotExist.cpp"],
        capture_output=True, text=True)
    absent = res.returncode != 0
    lines.append("    control: bogus LegionCore path 404:      %s"
                 % ("yes" if absent else "NO"))
    if not absent:
        fails.append("gh 404 control")
    lines.append("    control: live corpora loaded:            %d"
                 % len(corpora))
    return fails, lines


# ---------------------------------------------------------------- main
def main():
    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()

    print("=" * 68)
    print("AUDIT: Coordinates_Seething_Shore_COMPLETED.txt (BG step 4)")
    print("=" * 68)

    fails1, lines1 = run_static(text)
    total1 = len(STATIC_CHECKS) + len(NEGATIVE_CHECKS)
    print("\n[1] Static checks: %d/%d passed" % (total1 - len(fails1), total1))
    if fails1:
        print("    FAILED: %s" % ", ".join(fails1))
        for ln in lines1:
            if "MISSING" in ln or "PRESENT" in ln or "FAIL" in ln:
                print(ln)
    else:
        print("    all static checks passed")

    print("\n[2] Mutation testing (%d mutations)" % len(MUTATIONS))
    undetected = []
    for name, old, new in MUTATIONS:
        mutated = text.replace(old, new)
        if mutated == text:
            undetected.append(name + " (no-op)")
            continue
        f, _ = run_static(mutated)
        if not f:
            undetected.append(name)
    print("    detected %d/%d"
          % (len(MUTATIONS) - len(undetected), len(MUTATIONS)))
    if undetected:
        print("    UNDETECTED: %s" % ", ".join(undetected))

    print("\n[3] Source cross-check (upstream files fetched live)")
    corpora = {k: gh_content(LC, p) for k, p in FILES.items()}
    corpora["wsl"] = gh_content(TC, TC_DUMP)
    corpora["act"] = gh_content(AC, AC_TEMPLATE)
    missing = [k for k, v in corpora.items() if v is None]
    if missing:
        print("    CORPUS FETCH FAILED: %s" % missing)
        return 1
    ok3, lines3 = stage3(corpora)
    for ln in lines3:
        print(ln)
    if not ok3:
        print("    SOURCE CROSS-CHECK FAILED")
    probe_undetected = mutation_probe(
        corpora,
        {"ssc": [("node1 float", "1113.924f")]},
        lambda t: t.replace("1113.924f", "1113.925f"))
    print("    reaction to tampered source (verified): %s"
          % ("yes" if probe_undetected == [] else "NO"))
    if probe_undetected != []:
        ok3 = False

    print("\n[4] Derived values recomputed from source bodies")
    fails4, lines4 = stage4(text, corpora)
    for ln in lines4:
        print(ln)
    probe_fails, _ = stage4(text, corpora, probe=True)
    reacts = any("doc mismatch" in f for f in probe_fails)
    print("    row check reacts to doc tamper:          %s"
          % ("yes" if reacts else "NO"))
    if not reacts:
        fails4.append("row probe")
    if fails4:
        print("    DERIVED STAGE FAILED: %s"
              % ", ".join(str(f) for f in fails4))

    print("\n[5] Absence claims")
    fails5, lines5 = stage5(text, corpora)
    for ln in lines5:
        print(ln)
    if fails5:
        print("    ABSENCE STAGE FAILED: %s" % ", ".join(fails5))

    all_fails = fails1 + undetected + ([] if ok3 else ["source"]) + \
        fails4 + fails5
    print("\n" + "=" * 68)
    if not all_fails:
        print("AUDIT RESULT: PASS")
        print("  static checks: %d/%d" % (total1, total1))
        print("  mutations:     %d/%d" % (len(MUTATIONS), len(MUTATIONS)))
        return 0
    print("AUDIT RESULT: FAIL")
    print("  %d failing item(s): %s" % (len(all_fails), all_fails))
    return 1


if __name__ == "__main__":
    sys.exit(main())
