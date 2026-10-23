#!/usr/bin/env python3
"""Audit: Coordinates_Arathi_Basin_COMPLETED.txt (Battleground_Coordinates step 1).

Stages:
  1. Static exact-literal checks on the document (+ negative checks).
  2. Mutation testing - every mutation must break at least one check.
  3. Source cross-check against GitHub corpora fetched live (fork code,
     TrinityCore 8.x world_safe_locs dump, AzerothCore battleground_template,
     LegionCore-Reforged hotfix).
  4. Derived values recomputed from source bodies: all 24 world_safe_locs
     rows parsed and matched, route legs and node-node distances recomputed
     from fork coordinates + dump entrances, 2107-vs-529 graveyard deltas,
     coordinate trace, with reaction probes.
  5. Absence claims (script map-agnostic, no 2107 Entrance Target rows,
     retail buff parity unverified) with injection probes and a gh control.
"""

import base64
import math
import re
import subprocess
import sys

sys.path.insert(0, ".")
from audit_common import gh_content, source_stage, mutation_probe, coord_trace

DOC = ("# Ai Research prompts/Battleground_Coordinates/"
       "Coordinates_Arathi_Basin_COMPLETED.txt")
FORK = "HavenWoW/BFA-HavenCore"
TC = "TrinityCore/TrinityCore"
AC = "azerothcore/azerothcore-wotlk"
LC = "Titans-Project/LegionCore-Reforged"

FORK_FILES = {
    "abh": "src/server/game/Battlegrounds/Zones/BattlegroundAB.h",
    "abc": "src/server/game/Battlegrounds/Zones/BattlegroundAB.cpp",
    "bh": "src/server/game/Battlegrounds/Battleground.h",
    "bc": "src/server/game/Battlegrounds/Battleground.cpp",
    "om": "src/server/game/Globals/ObjectMgr.cpp",
    "uh": "src/server/game/Entities/Unit/Unit.h",
}
TC_DUMP = ("sql/old/8.x/world/19071_2020_06_17/2019_10_26_01_world.sql")
AC_TEMPLATE = "data/sql/base/db_world/battleground_template.sql"
LC_HOTFIX = "sql/old/hotfixes/2026_09_01_00_arathi_start_positions.sql"

ROW_IDS = [889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899,
           3705, 3706, 3981, 3982, 7055, 7056,
           7251, 7252, 7253, 7254, 7255, 7256, 7257]


# ---------------------------------------------------------------- stage 1
STATIC_CHECKS = [
    ("heading completed", "=== ARATHI BASIN COORDINATES - BFA 8.3.7 "
                          "(TRINITYCORE) - COMPLETED ==="),
    ("step numbering", "prompt 1 of 8"),
    ("done line", "DONE - step 1 of 8 complete"),
    ("direction convention", "+y runs toward the top (north) edge"),
    ("no-walkable claim", "NOT walkable-path measurements"),
    # map ids
    ("map 529", "529   Arathi Basin (classic map)"),
    ("map 2107", "2107  Arathi Basin, BfA version"),
    ("wiki mapid row", "Battle for Azeroth - Arathi Basin - 2107"),
    ("2107 delta claim", "within about 6 yd"),
    ("bs pair example", "(1016.59, 955.185, -42.8287) vs 2107 "
                        "(1016.93, 956.981, -42.8305)"),
    ("winter out of scope", "Arathi Basin (Winter Brawl)"),
    ("comp stomp out of scope", "AI Test Map 8B"),
    ("map-agnostic claim", "is unverified - the server database is not in "
                           "the repository"),
    # starts
    ("ally start id", 'Alliance, map 529:  id 890  "Arathi Basin - '
                      'Alliance Entrance"'),
    ("ally start row", "(529, 1313.9, 1310.74, -9.01043)   facing 220.05"),
    ("horde start row", "(529, 684.014, 681.22, -12.9159)   facing 46.1249"),
    ("2107 ally row", "(2107, 1315.21, 1305.74, -11.697)  facing 219.275"),
    ("2107 ids", "id 7056"),
    ("2107 horde id", "id 7055"),
    ("ac ally starto", "AllianceStartO = 3.91571"),
    ("ac horde starto", "HordeStartO = 0.813671"),
    ("legion precedent", "WorldSafeLocs 889/890"),
    ("lc file", '"arathi_start_positions"'),
    ("lc move 889", "(529, 695.3, 691.9, -11.6, LocO 0.87)"),
    ("lc move 890", "(529, 1301.8, 1301.6, -7.7, LocO 3.92)"),
    ("lc build", "VerifiedBuild 26972"),
    ("variant unverified", "Which of the two variants your world_safe_locs "
                           "table serves is unverified"),
    ("base rooms", "around world_safe 890"),
    ("horde base room", "around world_safe 889"),
    # doors
    ("ally gate id", "gameobject 180255"),
    ("ally gate pos", "(529, 1284.597, 1281.167, -15.97792)"),
    ("ally gate o", "o 0.7068594"),
    ("ally gate rot", "rotation 0.012957, -0.060288, 0.344959, 0.93659"),
    ("horde gate id", "gameobject 180256"),
    ("horde gate pos", "(529, 708.0903, 708.4479, -17.8342)"),
    ("horde gate o", "o -2.391099"),
    ("horde gate rot", "rotation 0.050291, 0.015127, 0.929217, -0.365784"),
    ("gate dist a", "about 42 yd (straight-line)"),
    ("gate dist h", "about 36 yd from the Horde entrance"),
    # area triggers / exploit / exits
    ("start at ally", '6634 "Alliance Start"'),
    ("start at horde", '6635 "Horde Start"'),
    ("exploit loc", "world_safe_locs 3705"),
    ("exploit a", "(529, 1313.9, 1310.74, -9.01043) facing 140"),
    ("exploit h", "facing 314"),
    ("duplicate rows", "3981/3982"),
    ("exit ally", '892 "Alliance Exit" (0, -1215.59, -2531.75, 21.6734) '
                  'facing 178.65'),
    ("exit horde", '891 "Horde Exit" (0, -831.881, -3518.52, 72.4831) '
                   'facing 166.85'),
    ("no items", "Arathi Basin mechanics use no items"),
    # nodes
    ("five nodes", "no orb and no mine cart depot in Arathi Basin"),
    ("stables banner", "227420"),
    ("bs banner", "227522"),
    ("farm banner", "227536"),
    ("lm banner", "227544"),
    ("gm banner", "227538"),
    ("stables pos", "(529, 1166.785, 1200.132, -56.70859)"),
    ("bs pos", "(529, 977.0156, 1046.616, -44.80923)"),
    ("farm pos", "(529, 806.1821, 874.2723, -55.99371)"),
    ("lm pos", "(529, 856.1419, 1148.902, 11.18469)"),
    ("gm pos", "(529, 1146.923, 848.1782, -110.917)"),
    ("click range", "clicks the banner within 10 yd"),
    ("unk triggers", "4020, 4021, 4674"),
    ("world trigger", "WORLD_TRIGGER creature 12999"),
    ("honor spell", "spell 68652"),
    ("faction split", "faction 84 (Alliance) or 83 (Horde)"),
    ("visuals", "42975 neutral"),
    ("visual occupied", "42980 Alliance-occupied"),
    ("z lm", "z +11.18"),
    # routes
    ("route a stables", "door 180255 (1284.597, 1281.167, -15.97792) -> "
                        "banner 227420 (1166.785, 1200.132, -56.70859)"),
    ("route a bs", "banner 227522 (977.0156, 1046.616, -44.80923)"),
    ("route a lm", "banner 227544 (856.1419, 1148.902, 11.18469)"),
    ("route a gm", "banner 227538 (1146.923, 848.1782, -110.917)"),
    ("route a farm", "banner 227536 (806.1821, 874.2723, -55.99371)"),
    ("route h gate", "door 180256 (708.0903, 708.4479, -17.8342)"),
    ("legs a stables", "legs: 42 yd, 143 yd"),
    ("legs a bs", "legs: 42 yd, 387 yd"),
    ("legs a lm", "legs: 42 yd, 448 yd"),
    ("legs a gm", "legs: 42 yd, 454 yd"),
    ("legs a farm", "legs: 42 yd, 628 yd"),
    ("legs h farm", "legs: 36 yd, 193 yd"),
    ("legs h gm", "legs: 36 yd, 461 yd"),
    ("legs h bs", "legs: 36 yd, 432 yd"),
    ("legs h lm", "legs: 36 yd, 465 yd"),
    ("legs h stables", "legs: 36 yd, 672 yd"),
    ("direct a stables", "direct 184 yd"),
    ("direct a bs", "direct 428 yd"),
    ("direct a lm", "direct 486 yd"),
    ("direct a gm", "direct 492 yd"),
    ("direct a farm", "direct 670 yd"),
    ("direct h farm", "direct 228 yd"),
    ("direct h gm", "direct 492 yd"),
    ("direct h bs", "direct 468 yd"),
    ("direct h lm", "direct 498 yd"),
    ("direct h stables", "direct 709 yd"),
    ("nn st-bs", "Stables-Blacksmith 244 yd"),
    ("nn st-lm", "Stables-Lumber Mill 315 yd"),
    ("nn st-gm", "Stables-Gold Mine 353 yd"),
    ("nn st-farm", "Stables-Farm 486 yd"),
    ("nn bs-lm", "Blacksmith-Lumber Mill 158 yd"),
    ("nn bs-gm", "Blacksmith-Gold Mine 261 yd"),
    ("nn bs-farm", "Blacksmith-Farm 243 yd"),
    ("nn lm-farm", "Lumber Mill-Farm 279 yd"),
    ("nn lm-gm", "Lumber Mill-Gold Mine 418 yd"),
    ("nn farm-gm", "Farm-Gold Mine 342 yd"),
    # graveyards
    ("gy 895 row", "895 (1201.87, 1163.13, -56.286) f 106.65"),
    ("gy 7252 row", "7252 (1201.54, 1166.4, -56.205) f 160.45"),
    ("gy 894 row", "894 (1016.59, 955.185, -42.8287) f 96.75"),
    ("gy 7257 row", "7257 (1016.93, 956.981, -42.8305) f 96.75"),
    ("gy 893 row", "893 (834.726, 784.979, -57.0819) f 97.65"),
    ("gy 7256 row", "7256 (835.172, 789.642, -55.9021) f 97.65"),
    ("gy 897 row", "897 (772.756, 1213.11, 15.7974) f 289.35"),
    ("gy 7254 row", "7254 (773.495, 1208.02, 15.7973) f 323.978"),
    ("gy 896 row", "896 (1211.52, 781.557, -82.7095) f 145.35"),
    ("gy 7253 row", "7253 (1212.31, 784.983, -82.9087) f 145.35"),
    ("gy 898 row", "898 (1355.2, 1274.19, -9.3585) f 157.05"),
    ("gy 7251 row", "7251 (1353.22, 1272.2, -11.2072) f 119.941"),
    ("gy 899 row", "899 (711.536, 648.83, -10.0401) f 74.0853"),
    ("gy 7255 row", "7255 (708.266, 644.445, -12.5542) f 74.0853"),
    ("respawn rule", "OWNED node closest to your corpse"),
    ("hardcoded ids", "hardcodes ids 898 (Alliance) / 899 (Horde)"),
    ("relocate rule", "RelocateDeadPlayers -> GetClosestGraveYard"),
    ("spirit st", "(1200.03, 1171.09, -56.47) 5.15"),
    ("spirit bs", "(1017.43, 960.61, -42.95) 4.88"),
    ("spirit farm", "(833.00, 793.00, -57.25) 5.27"),
    ("spirit lm", "(775.17, 1206.40, 15.79) 1.90"),
    ("spirit gm", "(1207.48, 787.00, -83.36) 5.51"),
    ("spirit ally base", "(1354.05, 1275.48, -11.30) 4.77"),
    ("spirit horde base", "(714.61, 646.15, -10.87) 4.34"),
    ("spirit entries", "13116 (Alliance), 13117 (Horde)"),
    ("spirit spell", "spell 22011"),
    ("spirit visual", "visual 3060"),
    # buffs
    ("buff respawn", "respawns in 180 seconds"),
    ("buff respawn const", "BUFF_RESPAWN_TIME = 180 s"),
    ("buff hidden const", "86400 s (RESPAWN_ONE_DAY)"),
    ("buff entries", "179871 Speed, 179904 Regeneration, 179905 Berserking"),
    ("buff st", "(1185.71, 1185.24, -56.36) 2.56"),
    ("buff bs", "(990.75, 1008.18, -42.60) 2.43"),
    ("buff farm", "(817.66, 843.34, -56.54) 3.01"),
    ("buff lm", "(807.46, 1189.16, 11.92) 5.44"),
    ("buff gm", "(1146.62, 816.94, -98.49) 6.14"),
    ("buff trap", "type in script: TRAP"),
    ("buff spell speed", "spell 23451 (Speed)"),
    ("buff spell resto", "23493 (Restoration)"),
    ("buff spell berserk", "23505 (Berserking)"),
    ("buff retail unverified", "Retail 8.3.7 parity of AB buffs is "
                               "unverified"),
    # sources
    ("tc dump path", "2019_10_26_01_world.sql"),
    ("ac path", "data/sql/base/db_world/battleground_template.sql"),
    ("lc path", "arathi_start_positions.sql"),
    ("map image source", "wowclassicdatabase.com"),
    ("cmangos source", "cmangos/issues #2290"),
    ("wowhead negative", "returns page-not-found"),
    ("unverified list", "=== 8. EXPLICIT UNVERIFIED LIST ==="),
    ("pathing unverified item", "no pathing/navmesh source could be read"),
    ("waypoint unverified", "Ramps and tunnels inside the instance: "
                            "unverified"),
    ("unverified count", "unverified"),  # threshold handled below
]

NEGATIVE_CHECKS = [
    ("no retail-confirmed buffs", "retail parity confirmed"),
    ("no pathing-confirmed claim", "pathing confirmed"),
    ("no todo", "TODO"),
    ("no fixme", "FIXME"),
    ("no estimated coords", "estimated coordinate"),
]

UNVERIFIED_MIN = 17


def run_static(text):
    ok_lines, fails = [], []
    for name, lit in STATIC_CHECKS:
        if name == "unverified count":
            n = text.count("unverified")
            hit = n >= UNVERIFIED_MIN
            ok_lines.append("    %-28s %s (%d >= %d)"
                            % (name, "ok" if hit else "FAIL", n,
                               UNVERIFIED_MIN))
            if not hit:
                fails.append(name)
            continue
        hit = lit in text
        ok_lines.append("    %-28s %s" % (name, "ok" if hit else "MISSING"))
        if not hit:
            fails.append(name)
    for name, lit in NEGATIVE_CHECKS:
        hit = lit not in text
        ok_lines.append("    %-28s %s" % (name, "ok" if hit else "PRESENT!"))
        if not hit:
            fails.append(name)
    return fails, ok_lines


# ---------------------------------------------------------------- stage 2
MUTATIONS = [
    ("heading", "=== ARATHI BASIN COORDINATES - BFA 8.3.7 "
                "(TRINITYCORE) - COMPLETED ===",
     "=== ARATHI BASIN COORDINATES - BFA 8.3.7 (TRINITYCORE) - DRAFT ==="),
    ("step number", "prompt 1 of 8", "prompt 1 of 7"),
    ("direction", "+y runs toward the top (north) edge",
     "+y runs toward the bottom (north) edge"),
    ("map id 2107", "2107  Arathi Basin, BfA version",
     "2108  Arathi Basin, BfA version"),
    ("delta claim", "within about 6 yd", "within about 60 yd"),
    ("ally start id", 'Alliance, map 529:  id 890',
     'Alliance, map 529:  id 891'),
    ("ally facing", "facing 220.05", "facing 220.06"),
    ("2107 ally row", "(2107, 1315.21, 1305.74, -11.697)",
     "(2107, 1315.21, 1305.74, -11.698)"),
    ("ac orientation", "AllianceStartO = 3.91571", "AllianceStartO = 3.91572"),
    ("ac horde orientation", "HordeStartO = 0.813671", "HordeStartO = 0.151581"),
    ("lc moved start", "(529, 695.3, 691.9, -11.6, LocO 0.87)",
     "(529, 696.3, 691.9, -11.6, LocO 0.87)"),
    ("lc build", "VerifiedBuild 26972", "VerifiedBuild 26973"),
    ("ally gate id", "gameobject 180255", "gameobject 180257"),
    ("ally gate pos", "(529, 1284.597, 1281.167, -15.97792)",
     "(529, 1284.597, 1281.167, -15.97793)"),
    ("gate distance", "about 42 yd (straight-line)",
     "about 44 yd (straight-line)"),
    ("exploit id", "world_safe_locs 3705", "world_safe_locs 3707"),
    ("exit row", "(0, -1215.59, -2531.75, 21.6734)",
     "(0, -1215.59, -2531.75, 21.6735)"),
    ("stables banner", "227420", "227421"),
    ("node pos", "(529, 1166.785, 1200.132, -56.70859)",
     "(529, 1166.785, 1200.132, -56.70858)"),
    ("click range", "clicks the banner within 10 yd",
     "clicks the banner within 15 yd"),
    ("world trigger", "WORLD_TRIGGER creature 12999",
     "WORLD_TRIGGER creature 12998"),
    ("honor spell", "spell 68652", "spell 68653"),
    ("banner visual", "42980 Alliance-occupied", "42981 Alliance-occupied"),
    ("route leg a", "legs: 42 yd, 143 yd", "legs: 42 yd, 144 yd"),
    ("route leg h", "legs: 36 yd, 672 yd", "legs: 36 yd, 673 yd"),
    ("route direct", "direct 184 yd", "direct 185 yd"),
    ("node-node 1", "Stables-Blacksmith 244 yd", "Stables-Blacksmith 245 yd"),
    ("node-node 2", "Farm-Gold Mine 342 yd", "Farm-Gold Mine 343 yd"),
    ("gy 529 row", "895 (1201.87, 1163.13, -56.286) f 106.65",
     "895 (1201.88, 1163.13, -56.286) f 106.65"),
    ("gy 2107 row", "7257 (1016.93, 956.981, -42.8305)",
     "7257 (1016.93, 956.982, -42.8305)"),
    ("hardcoded gy ids", "hardcodes ids 898 (Alliance) / 899 (Horde)",
     "hardcodes ids 897 (Alliance) / 899 (Horde)"),
    ("spirit entry", "13116 (Alliance), 13117 (Horde)",
     "13115 (Alliance), 13117 (Horde)"),
    ("spirit pos", "(1200.03, 1171.09, -56.47) 5.15",
     "(1200.04, 1171.09, -56.47) 5.15"),
    ("buff respawn", "respawns in 180 seconds", "respawns in 120 seconds"),
    ("buff entries", "179871 Speed, 179904 Regeneration, 179905 Berserking",
     "179872 Speed, 179904 Regeneration, 179905 Berserking"),
    ("buff pos", "(1185.71, 1185.24, -56.36) 2.56",
     "(1185.72, 1185.24, -56.36) 2.56"),
    ("retail parity", "Retail 8.3.7 parity of AB buffs is unverified",
     "Retail 8.3.7 parity of AB buffs is confirmed"),
    ("tc source", "2019_10_26_01_world.sql", "2019_10_26_02_world.sql"),
    ("wiki mapid", "Battle for Azeroth - Arathi Basin - 2107",
     "Battle for Azeroth - Arathi Basin - 2108"),
    ("map-agnostic unverified", "is unverified - the server database is not "
                                "in the repository",
     "is verified - the server database is in the repository"),
]


# ---------------------------------------------------------------- stage 3
def stage3(corpora):
    token_map = {
        "abh": [
            ("stables banner", "= 227420"),
            ("bs banner", "= 227522"),
            ("farm banner", "= 227536"),
            ("lm banner", "= 227544"),
            ("gm banner", "= 227538"),
            ("ally gate", "= 180255"),
            ("horde gate", "= 180256"),
            ("node stables", "1166.785f, 1200.132f, -56.70859f"),
            ("node bs", "977.0156f, 1046.616f, -44.80923f"),
            ("node farm", "806.1821f, 874.2723f, -55.99371f"),
            ("node lm", "856.1419f, 1148.902f, 11.18469f"),
            ("node gm", "1146.923f, 848.1782f, -110.917f"),
            ("door a", "1284.597f, 1281.167f, -15.97792f"),
            ("door h", "708.0903f, 708.4479f, -17.8342f"),
            ("gy id array", "{895, 894, 893, 897, 896, 898, 899}"),
            ("buff st", "1185.71f, 1185.24f"),
            ("buff bs", "990.75f, 1008.18f"),
            ("buff farm", "817.66f, 843.34f"),
            ("buff lm", "807.46f, 1189.16f"),
            ("buff gm", "1146.62f, 816.94f"),
            ("spirit st", "1200.03f, 1171.09f"),
            ("spirit bs", "1017.43f, 960.61f"),
            ("spirit farm", "833.00f, 793.00f"),
            ("spirit lm", "775.17f, 1206.40f"),
            ("spirit gm", "1207.48f, 787.00f"),
            ("spirit ally", "1354.05f, 1275.48f"),
            ("spirit horde", "714.61f, 646.15f"),
            ("exploit ally", "AB_EXPLOIT_TELEPORT_LOCATION_ALLIANCE = 3705"),
            ("exploit horde", "AB_EXPLOIT_TELEPORT_LOCATION_HORDE    = 3706"),
            ("visual neutral", "= 42975"),
            ("visual occ", "= 42980"),
            ("spirit enum a", "BG_AB_SPIRIT_ALIANCE        = 5"),
        ],
        "abc": [
            ("closest gy fn", "GetClosestGraveYard(Player* player)"),
            ("base fallback", "BG_AB_GraveyardIds[teamIndex+5]"),
            ("click range", "IsWithinDistInMap(obj, 10)"),
            ("trigger spawn", "AddCreature(WORLD_TRIGGER"),
            ("random buff", "urand(0, 2)"),
            ("exploit fn", "GetExploitTeleportLocation"),
            ("relocate call", "RelocateDeadPlayers(BgCreatures[node])"),
            ("spirit guide call", "BG_AB_SpiritGuidePos[node]"),
            ("start guides", "_NodeOccupied(BG_AB_SPIRIT_ALIANCE, ALLIANCE)"),
            ("honor aura", "SPELL_HONORABLE_DEFENDER_25Y"),
            ("quest reward", "SPELL_AB_QUEST_REWARD_5_BASES"),
            ("start at 6634", "case 6634"),
            ("start at 6635", "case 6635"),
            ("exit at 3948", "case 3948"),
            ("exit at 3949", "case 3949"),
            ("node at st", "case 3866"),
            ("node at bs", "case 3870"),
            ("node at farm", "case 3867"),
            ("node at lm", "case 3868"),
            ("node at gm", "case 3869"),
            ("unk at 4020", "case 4020"),
            ("unk at 4021", "case 4021"),
            ("unk at 4674", "case 4674"),
        ],
        "bh": [
            ("spirit entry a", "BG_CREATURE_ENTRY_A_SPIRITGUIDE"),
            ("spirit entry a id", "= 13116"),
            ("spirit entry h id", "= 13117"),
            ("buff speed", "= 179871"),
            ("buff regen", "= 179904"),
            ("buff berserk", "= 179905"),
            ("respawn one day", "RESPAWN_ONE_DAY"),
            ("respawn day val", "= 86400"),
            ("buff respawn name", "BUFF_RESPAWN_TIME"),
            ("honor spell def", "= 68652"),
            ("spirit channel", "= 22011"),
            ("spirit visual", "= 3060"),
        ],
        "bc": [
            ("add spirit guide", "Battleground::AddSpiritGuide"),
            ("entry select", "BG_CREATURE_ENTRY_H_SPIRITGUIDE"),
            ("trigger buff fn", "HandleTriggerBuff"),
            ("buff respawn call", "SpawnBGObject(index, BUFF_RESPAWN_TIME)"),
            ("buff reroll", "Randomly select new buff"),
            ("relocate body", "TeleportTo(closestGrave->Loc)"),
            ("relocate comment", "closest own node's graveyard"),
        ],
        "om": [("worldsafe query", "FROM world_safe_locs")],
        "uh": [("world trigger define", "#define WORLD_TRIGGER   12999")],
        "wsl": [
            ("uprez entrance", "Arathi Basin (Uprez) - Horde Entrance"),
            ("new graveyard", "Arathi Basin (New) - Graveyard, A-Base"),
            ("entrance target", "Arathi Basin - Entrance Target - Alliance"),
            ("horde exit", "'Arathi Basin - Horde Exit'"),
            ("winter", "Arathi Basin (Winter Brawl) - Alliance Entrance"),
            ("ai test", "AI Test Map 8B - Arathi Basin - Horde Entrance"),
        ],
        "act": [("ab template row",
                 "(3,8,15,20,80,890,3.91571,889,0.813671,75,1,'',"
                 "'Arathi Basin (battleground)'),")],
        "lc": [
            ("move 889", "(889, '', 695.3, 691.9, -11.6, 0.87, 529, 26972)"),
            ("move 890", "(890, '', 1301.8, 1301.6, -7.7, 3.92, 529, 26972)"),
            ("azerite comment", "battleground_template points both the "
                                "original battleground and Azerite Rush"),
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
        if rid in ROW_IDS:
            rows[rid] = {"map": m.group(2), "x": m.group(3),
                         "y": m.group(4), "z": m.group(5),
                         "facing": m.group(6), "comment": m.group(7)}
    return rows


def _f(block_decl, text):
    m = re.search(block_decl, text, re.S)
    return m.group(1) if m else ""


def parse_fork_coords(abh):
    doors_raw = _f(r"BG_AB_DoorPositions\[2\]\[8\] =\s*\{(.*?)\n\};", abh)
    doors = []
    for row in re.findall(r"\{([^}]+)\}", doors_raw):
        nums = [float(v.replace("f", "").strip())
                for v in row.split(",")[:4]]
        doors.append(tuple(nums))
    nodes_raw = _f(
        r"BG_AB_NodePositions\[BG_AB_DYNAMIC_NODES_COUNT\]\[4\] =\s*"
        r"\{(.*?)\n\};", abh)
    nodes = []
    for row in re.findall(r"\{([^}]+)\}", nodes_raw):
        nums = [float(v.replace("f", "").strip())
                for v in row.split(",")[:4]]
        nodes.append(tuple(nums))
    return doors, nodes


def rd(x):
    """Round half up (not banker's) to whole yards."""
    return int(x + 0.5)


def stage4(text, corpora, probe=False):
    lines, fails = [], []
    doc = text
    if probe:
        doc = doc.replace("1201.87, 1163.13", "1201.87, 1163.14", 1) \
            if "1201.87, 1163.13" in text else \
            doc.replace("legs: 42 yd, 143 yd", "legs: 42 yd, 144 yd", 1)

    # 4a. all 24 world_safe_locs rows vs document
    rows = parse_wsl_rows(corpora["wsl"])
    hit = 0
    for rid in ROW_IDS:
        r = rows.get(rid)
        if not r:
            fails.append("row %d missing from dump" % rid)
            lines.append("    row %-5d NOT IN DUMP" % rid)
            continue
        triple = "(%s, %s, %s, %s)" % (r["map"], r["x"], r["y"], r["z"])
        xyz = "(%s, %s, %s)" % (r["x"], r["y"], r["z"])
        context = triple in doc or ("%d %s" % (rid, xyz)) in doc
        coords_ok = xyz in doc or triple in doc
        facing_ok = re.search(r"\b(?:f|facing) %s\b" % re.escape(r["facing"]),
                              doc)
        ok = coords_ok and context and bool(facing_ok)
        if ok:
            hit += 1
        else:
            fails.append("row %d doc mismatch" % rid)
        lines.append("    row %-5d %-46s %s"
                     % (rid, triple, "ok" if ok else "DOC MISMATCH"))
    lines.append("    world_safe rows matched: %d/%d" % (hit, len(ROW_IDS)))

    # 4b. route legs + direct distances recomputed from sources
    rows_all = parse_wsl_rows(corpora["wsl"])
    ax, ay = float(rows_all[890]["x"]), float(rows_all[890]["y"])
    hx, hy = float(rows_all[889]["x"]), float(rows_all[889]["y"])
    doors, nodes = parse_fork_coords(corpora["abh"])
    if len(doors) != 2 or len(nodes) != 5:
        fails.append("fork coordinate parse (doors=%d nodes=%d)"
                     % (len(doors), len(nodes)))
        lines.append("    fork coordinate parse FAILED")
        return fails, lines
    st, bs, fm, lm, gm = [(n[0], n[1]) for n in nodes]
    A, H = (ax, ay), (hx, hy)
    gA, gH = (doors[0][0], doors[0][1]), (doors[1][0], doors[1][1])
    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
    routes = [
        ("A->Stables", A, gA, st), ("A->Blacksmith", A, gA, bs),
        ("A->LumberMill", A, gA, lm), ("A->GoldMine", A, gA, gm),
        ("A->Farm", A, gA, fm),
        ("H->Farm", H, gH, fm), ("H->GoldMine", H, gH, gm),
        ("H->Blacksmith", H, gH, bs), ("H->LumberMill", H, gH, lm),
        ("H->Stables", H, gH, st),
    ]
    ok_routes = 0
    for name, s, g, n in routes:
        leg1, leg2, direct = rd(dist(s, g)), rd(dist(g, n)), rd(dist(s, n))
        want = ["legs: %d yd, %d yd" % (leg1, leg2),
                "direct %d yd" % direct]
        ok = all(w in doc for w in want)
        ok_routes += ok
        if not ok:
            fails.append("route %s (%s)" % (name, want))
        lines.append("    %-16s legs %3d + %3d, direct %3d   %s"
                     % (name, leg1, leg2, direct, "ok" if ok else "MISMATCH"))
    lines.append("    route legs+direct: %d/%d match recompute"
                 % (ok_routes, len(routes)))

    # 4c. node-to-node distances
    pairs = [("Stables-Blacksmith", st, bs), ("Stables-Lumber Mill", st, lm),
             ("Stables-Gold Mine", st, gm), ("Stables-Farm", st, fm),
             ("Blacksmith-Lumber Mill", bs, lm),
             ("Blacksmith-Gold Mine", bs, gm),
             ("Blacksmith-Farm", bs, fm), ("Lumber Mill-Farm", lm, fm),
             ("Lumber Mill-Gold Mine", lm, gm), ("Farm-Gold Mine", fm, gm)]
    ok_nn = 0
    for label, p, q in pairs:
        want = "%s %d yd" % (label, rd(dist(p, q)))
        ok = want in doc
        ok_nn += ok
        if not ok:
            fails.append("node-node %s" % label)
    lines.append("    node-node distances: %d/%d match recompute"
                 % (ok_nn, len(pairs)))

    # 4d. 2107-vs-529 graveyard delta claim
    pairs_id = [(895, 7252), (894, 7257), (893, 7256), (897, 7254),
                (896, 7253), (898, 7251), (899, 7255)]
    deltas = []
    for a, b in pairs_id:
        ra, rb = rows[a], rows[b]
        d3 = math.sqrt(sum((float(ra[k]) - float(rb[k])) ** 2
                           for k in ("x", "y", "z")))
        deltas.append(d3)
    mx = rd(max(deltas))
    delta_ok = (mx == 6 and "within about 6 yd" in doc)
    if not delta_ok:
        fails.append("2107 delta (max=%s)" % mx)
    lines.append("    2107-vs-529 max graveyard delta: %d yd (doc says 6)  %s"
                 % (mx, "ok" if delta_ok else "MISMATCH"))

    # 4e. coordinate trace over every corpus
    ok_c, c_lines, missing_c = coord_trace(doc, corpora)
    lines.extend(c_lines)
    if not ok_c:
        fails.append("coordinate trace: %s" % missing_c[:6])
    probe_txt = doc.replace("1313.9, 1310.74, -9.01043",
                            "1313.9, 9310.74, -9.01043", 1)
    ok2, _, _ = coord_trace(probe_txt, corpora)
    probe_ok = (probe_txt != doc) and not ok2
    lines.append("    coordinate probe reacts: %s"
                 % ("yes" if probe_ok else "no"))
    if not probe_ok:
        fails.append("coordinate probe")

    return fails, lines


# ---------------------------------------------------------------- stage 5
def stage5(text, corpora):
    lines, fails = [], []

    # script map-agnostic: no 2107 token in the AB script files
    for key in ("abh", "abc"):
        if "2107" in corpora[key]:
            fails.append("2107 found in %s" % key)
    lines.append("    AB script contains no 2107 (map-agnostic): %s"
                 % ("yes" if all("2107" not in corpora[k]
                                for k in ("abh", "abc")) else "NO"))
    if "is unverified - the server database is not in the repository" \
            not in text:
        fails.append("map-agnostic unverified statement missing")
    lines.append("    document marks queued map id unverified: ok")

    # dump: every Entrance Target row is map 529, none on 2107
    rows = parse_wsl_rows(corpora["wsl"])
    et = {rid: r for rid, r in rows.items() if "Entrance Target" in r["comment"]}
    et_ids = set(et)
    et_ok = et_ids == {3705, 3706, 3981, 3982} and \
        all(r["map"] == "529" for r in et.values())
    if not et_ok:
        fails.append("entrance target rows: %s" % sorted(et_ids))
    lines.append("    Entrance Target rows exist only for 529 "
                 "(3705/3706/3981/3982): %s" % ("yes" if et_ok else "NO"))
    if "Map 2107 has no Entrance Target rows in the dump" not in text:
        fails.append("2107 entrance-target absence claim missing")

    # retail buff parity must stay unverified; injection must be caught
    if "Retail 8.3.7 parity of AB buffs is unverified" not in text:
        fails.append("retail buff parity unverified claim missing")
    injected = text + "\nretail parity confirmed by direct reading.\n"
    f_inj, _ = run_static(injected)
    reacts = "no retail-confirmed buffs" in f_inj
    lines.append("    injection probe (retail parity confirmed): %s"
                 % ("detected" if reacts else "NOT DETECTED"))
    if not reacts:
        fails.append("retail injection probe")

    # unverified-count probe
    stripped = text.replace("unverified", "verified")
    f_cnt, _ = run_static(stripped)
    reacts2 = "unverified count" in f_cnt
    lines.append("    injection probe (all unverified markers stripped): %s"
                 % ("detected" if reacts2 else "NOT DETECTED"))
    if not reacts2:
        fails.append("unverified count probe")

    # gh control: a bogus fork path must 404
    res = subprocess.run(
        ["gh", "api", "-X", "GET",
         "repos/%s/contents/src/server/game/Battlegrounds/Zones/"
         "DoesNotExist.cpp" % FORK],
        capture_output=True, text=True)
    absent = res.returncode != 0
    lines.append("    control: bogus fork path 404: %s"
                 % ("yes" if absent else "NO"))
    if not absent:
        fails.append("gh 404 control")
    lines.append("    control: real fork files fetched live: "
                 "%d corpora loaded" % len(corpora))

    return fails, lines


# ---------------------------------------------------------------- main
def main():
    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()

    print("=" * 68)
    print("AUDIT: Coordinates_Arathi_Basin_COMPLETED.txt (BG coords step 1)")
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
    corpora = {k: gh_content(FORK, p) for k, p in FORK_FILES.items()}
    corpora["wsl"] = gh_content(TC, TC_DUMP)
    corpora["act"] = gh_content(AC, AC_TEMPLATE)
    corpora["lc"] = gh_content(LC, LC_HOTFIX)
    ok3, lines3 = stage3(corpora)
    for ln in lines3:
        print(ln)
    print("    (warcraft.wiki / wowhead / image literals are guarded by "
          "stages 1-2 only - not reachable from gh)")
    if not ok3:
        print("    SOURCE CROSS-CHECK FAILED")
    probe_undetected = mutation_probe(
        corpora,
        {"abh": [("stables banner", "= 227420")]},
        lambda t: t.replace("= 227420", "= 227421"))
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
    print("    row check reacts to doc tamper: %s"
          % ("yes" if reacts else "NO"))
    if not reacts:
        fails4.append("row probe")
    if fails4:
        print("    DERIVED STAGE FAILED: %s" % ", ".join(str(f) for f in fails4))

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
