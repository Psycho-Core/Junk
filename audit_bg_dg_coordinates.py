#!/usr/bin/env python3
"""Audit: Coordinates_Deepwind_Gorge_COMPLETED.txt (Battleground_Coordinates step 2).

Stages:
  1. Static exact-literal checks on the document (+ negative checks),
     whitespace-normalised because the document is line-wrapped.
  2. Mutation testing - every mutation must break at least one check.
  3. Source cross-check against GitHub corpora fetched live (LegionCore-
     Reforged Deepwind script + Battleground.h, TrinityCore 8.x world dump,
     AzerothCore battleground_template).
  4. Derived values recomputed from source bodies: all 8 world_safe_locs
     rows, door/cart/mine floats parsed from the script, all route legs,
     mine pairs, catch distances, the per-team graveyard rule results,
     coordinate trace - with reaction probes.
  5. Absence claims (no DG script in either BfA core, no Deepwind row in
     AzerothCore, no post-8.3 TC rows for map 2245) with injection probes
     and a gh 404 control.
"""

import base64
import math
import re
import subprocess
import sys

sys.path.insert(0, ".")
from audit_common import gh_content, source_stage, mutation_probe, coord_trace

DOC = ("# Ai Research prompts/Battleground_Coordinates/"
       "Coordinates_Deepwind_Gorge_COMPLETED.txt")
HAVEN = "HavenWoW/BFA-HavenCore"
BFA = "Titans-Project/BfaCore-Reforged"
LEGION = "Titans-Project/LegionCore-Reforged"
TC = "TrinityCore/TrinityCore"
AC = "azerothcore/azerothcore-wotlk"

LC_FILES = {
    "dgh": "src/server/game/Battlegrounds/Zones/BattlegroundDeepwindGorge.h",
    "dgc": "src/server/game/Battlegrounds/Zones/BattlegroundDeepwindGorge.cpp",
    "lbh": "src/server/game/Battlegrounds/Battleground.h",
}
TC_DUMP = "sql/old/8.x/world/19071_2020_06_17/2019_10_26_01_world.sql"
AC_TEMPLATE = "data/sql/base/db_world/battleground_template.sql"
DS_H = "src/server/game/Battlegrounds/Zones/BattlegroundDS.h"
ZONES = "src/server/game/Battlegrounds/Zones"

# post-8.3 TC update files that were checked for Deepwind/2245 rows
TC_ABSENCE = [
    "2020_02_17_00_world.sql", "2020_02_18_00_world.sql",
    "2020_02_29_00_world.sql", "2020_04_25_00_world.sql",
    "2020_05_02_00_world.sql", "2020_05_02_01_world.sql",
    "2020_05_02_02_world.sql", "2020_05_02_03_world.sql",
    "2020_05_22_00_world.sql", "2020_05_22_01_world.sql",
    "2020_02_19_00_world_creatures.sql",
    "2020_03_25_00_world_creatures.sql",
]
ROW_IDS = [4486, 4487, 4488, 4489, 4545, 4546, 4613, 4614]

UNVERIFIED_MIN = 25


def norm(s):
    return re.sub(r"\s+", " ", s)


# ---------------------------------------------------------------- stage 1
STATIC_CHECKS = [
    ("heading completed", "=== DEEPWIND GORGE COORDINATES - BFA 8.3.7 "
                          "(TRINITYCORE) - COMPLETED ==="),
    ("step numbering", "prompt 2 of 8 (Deepwind Gorge, maps 1105 + 2245)"),
    ("done line", "DONE - step 2 of 8 complete"),
    ("no-estimate policy", "nothing is estimated"),
    ("unverified policy", 'the entry says "unverified"'),
    # orientation
    ("north proof rule", "smaller y = north, larger y = south"),
    ("north proof allies", "4546 y=195.135 vs 4488 y=242.712"),
    ("north proof horde", "4489 y=758.708 vs 4545 y=802.188"),
    ("mine order proof", "Pandaren, Central, and Goblin"),
    ("mine order y", "y=431.1771 / 499.059 / 574.368"),
    ("no east/west claim", "makes NO east/west claims about map 1105"),
    ("pathing caveat", "NOT walkable-path measurements"),
    ("navmesh caveat", "no pathing/navmesh source for these maps could be read"),
    # maps
    ("1105 original", '1105 = Deepwind Gorge, original ("Gold Rush") '
                      'battleground, added 5.3.0'),
    ("1105 removed", "removed from retail in patch 8.3.0"),
    ("gold rush comments", 'comments starting "Gold Rush BG"'),
    ("goldrush map file", "WorldMap-GoldRush.jpg"),
    ("2245 redesign", "2245 = Deepwind Gorge, redesigned battleground, "
                      "added patch 8.3.0"),
    ("2245 instance row", "2245 ... [[Deepwind Gorge]] ... Battleground "
                          "... 8.3.x"),
    ("inspired by ab", "inspired by Arathi Basin"),
    ("five points", "Market, Farm, Ruins, Shrine, Quarry"),
    ("cap claim 1500", "first to 1,500 points"),
    ("zone 6665", "zone 6665 (original, added 5.5.0 label on MoP Classic)"),
    ("zone 10886", 'zone 10886 (added patch 8.3.0) both name "Deepwind Gorge"'),
    ("ac negative", "AzerothCore's base battleground_template has no Deepwind "
                    "row (checked, none)"),
    ("tc 2245 negative", "contain no map-2245 rows at all"),
    ("no script claim", "BfaCore-Reforged contains a Deepwind Gorge "
                        "battleground script (Zones directory listing "
                        "checked)"),
    # starts
    ("horde start id", 'Horde,     map 1105: id 4486 "Gold Rush BG - Horde '
                       'Start Location"'),
    ("horde start row", "(1105, -60.1632, 830.599, 135.379)   o 230.07"),
    ("ally start id", 'Alliance,  map 1105: id 4487 "Gold Rush BG - Alliance '
                      'Start Location"'),
    ("ally start row", "(1105, -275.198, 174.618, 136.185)   o 37.8039"),
    ("start sides", "Alliance starts on the north edge of the map, Horde on "
                    "the south edge"),
    ("door 220159", "gameobject 220159 (1105, -263.455, 218.163, 132.43)  "
                    "o 4.72984"),
    ("door 220160", "gameobject 220160 (1105, -213.712, 201.043, 132.488)  "
                    "o 3.9619"),
    ("door 220161", "gameobject 220161 (1105, -69.8785, 781.837, 132.43)  "
                    "o 1.58825"),
    ("door 220366", "gameobject 220366 (1105, -119.621, 798.957, 132.488)  "
                    "o 0.820303"),
    ("cart go a", "gameobject 220164 (1105, -241.741, 208.611, 133.747)  "
                  "o 0.84278"),
    ("cart go h", "gameobject 220166 (1105, -91.6163, 791.361, 133.747)  "
                  "o 4.02356"),
    ("respawn immediate", "RESPAWN_IMMEDIATELY at match setup"),
    ("cart npcs", 'creature 71071 "Alliance Mine Cart", creature 71073 '
                  '"Horde Mine Cart"'),
    ("2245 start unver", "Map 2245 starts/base positions: unverified"),
    ("2245 ally side", "Alliance sits on the east side (bases Farm northeast, "
                       "Shrine southeast)"),
    ("2245 horde side", "Horde on the west side (Quarry northwest, Ruins "
                        "southwest)"),
    ("2245 market", "Market is the middle base"),
    ("2245 strategy", "sends Alliance sitters to Farm and Shrine, Horde "
                      "sitters to Quarry and Ruins, everyone else to Market"),
    ("template unver", "Which world_safe ids your server's battleground_template "
                       "uses for starts is unverified"),
    # objectives
    ("no orbs", "No orbs exist in Deepwind Gorge"),
    ("flag entry", "creature entry 53194"),
    ("flag enum", "BG_DG_ENTRY_FLAG"),
    ("interact spell", "interact spell 97388"),
    ("pan mine row", "(1105, 68.39236, 431.1771, 111.4928)  o 1.229"),
    ("mid mine row", "(1105, -167.5035, 499.059, 92.62903)  o 1.249549"),
    ("gob mine row", "(1105, -397.7726, 574.368, 111.0529)  o 1.437866"),
    ("capture auras", "neutral 98554, contested Alliance 98543 / Horde 98545, "
                      "captured Alliance 98519 / Horde 98527"),
    ("7s channel", "7-second uninterrupted channel"),
    ("gold steal", "removes 200 gold from the loser"),
    ("gold score", "scores 200"),
    ("cart auras", "cart auras Alliance 141551 / Horde 141555"),
    ("chains aura", "chains aura 141553"),
    ("spawn spells", "141554 (Alliance) / 141550 (Horde"),
    ("carrier auras", "141210 on Alliance carriers, 140876 on Horde carriers"),
    ("cart ats", "9013 (Alliance cart point), 9012 (Horde cart point)"),
    ("catch id 4613", 'id 4613 "Gold Rush BG - Pandaren Mine Catch"'),
    ("catch 4613 row", "(1105, 104.08, 423.483, 112.371)  o 161.378"),
    ("catch id 4614", 'id 4614 "Gold Rush BG - Goblin Mine Catch"'),
    ("catch 4614 row", "(1105, -438.592, 582.325, 111.57)  o 0"),
    ("catch purpose", "purpose unverified - the row id is not referenced "
                      "anywhere in the readable script"),
    ("2245 points row", "Market (middle), Farm (northeast), Ruins (southwest), "
                        "Quarry (northwest), Shrine (southeast)"),
    ("2245 capture", "right-click the white flag, 6-second assault channel"),
    ("2245 no assault", "cannot assault while taking damage"),
    ("2245 cap", "first to 1,500 wins"),
    ("2245 flag entries unver", "White flag gameobject/creature entries and "
                                "coordinates: unverified"),
    # routes
    ("quarry text", "dislodged rock"),
    ("bridges text", "makeshift wooden bridges"),
    ("mine interiors", "the mines have interiors"),
    ("legs a pan", "legs: 45 yd, 394 yd"),
    ("legs a gob", "legs: 45 yd, 381 yd"),
    ("legs h gob", "legs: 50 yd, 388 yd"),
    ("direct h steal", "direct 648 yd"),
    ("pair pan-cen", "Pandaren-Central 245 yd"),
    ("pair pan-gob", "Pandaren-Goblin 488 yd"),
    # graveyards
    ("gy 4546 row", "(1105, -113.682, 195.135, 137.454)  o 134.932"),
    ("gy 4488 row", "(1105, -331.54, 242.712, 132.569)   o 0"),
    ("gy 4489 row", "(1105, -0.00868056, 758.708, 132.569) o 189.014"),
    ("gy 4545 row", "(1105, -222.743, 802.188, 137.451)  o 313.287"),
    ("gy 4546 id", "Alliance Cemetery (North), id 4546"),
    ("gy 4488 id", "Alliance Cemetery (South), id 4488"),
    ("gy 4489 id", "Horde Cemetery (North), id 4489"),
    ("gy 4545 id", "Horde Cemetery (South), id 4545"),
    ("spirit entries", "13116 (Alliance) and 13117 (Horde)"),
    ("spirit enum", "BG_CREATURE_ENTRY_A/H_SPIRITGUIDE"),
    ("wowhead spirit", "Horde Spirit Guide 13117"),
    ("not point based", "do NOT belong to individual points"),
    ("rule a", "whichever of YOUR OWN two cemeteries is closer to the corpse"),
    ("rule b quote", "Dying on the northern half of the map results in "
                     "re-spawning at your faction's southern graveyard (and "
                     "vice versa)"),
    ("rule conflict", "OPPOSITE answer for deaths at the northern (Pandaren) "
                      "mine"),
    ("gy central a static", "4488 (304 vs 309 yd)"),
    ("gy central h static", "4545 (308 vs 309 yd"),
    ("start gy static", "163 yd (North) / 88 yd"),
    ("pair sep static", "223 yd (Alliance) / 227 yd (Horde)"),
    ("2245 gy legend", "legend marks graveyards (black dots)"),
    ("2245 res quote", 'resurrecting at Farm'),
    ("2245 gy linked", "base-linked graveyards"),
    # buffs
    ("buff bersk spawn", "2x Berserking buff spawns"),
    ("buff bersk loc", "just north-east of the Central Mine, one just "
                       "south-west of the Central Mine"),
    ("buff bersk spell", "spell 24378"),
    ("buff rest spawn", "2x Restoration buff spawns"),
    ("buff rest loc", "one at the Pandaren Mine, one at the Goblin Mine"),
    ("buff rest spell", "spell 132958"),
    ("buff effects a", "+30% damage done, +10% damage taken, 1 minute"),
    ("buff effects b", "cancelled by damage"),
    ("haste spots", "inside the Market building; on top of the Shrine "
                    "structure"),
    ("haste value", "+30% Haste"),
    ("leaf farm", "at Farm, east of the flag under the shrine"),
    ("leaf ruins", "at Ruins, south of the flag on the wall"),
    ("bersk ledge", "overlooking Market"),
    ("bersk quarry", "at Quarry underneath the wooden ledge"),
    ("brew achievement", "achievement 14187"),
    ("brew object", "object 343707"),
    ("brew patch", "added patch 9.0.1"),
    ("brew location", "location of this object is unknown"),
    ("brew spell", "spell 318352"),
    # rules/notes
    ("cap 1600 mop", "cap 1600 in the MoP era"),
    ("ach 8333", '8333 "1600 to 0"'),
    ("emulator cap", "Legion-era emulator uses a 1500 cap"),
    ("cap 2245", "the cap is 1500 for map 2245"),
    ("15v15", "15v15"),
    ("10v10", "10v10"),
    ("no bullet carts", "No orbs, no bullet-carts"),
    # sources
    ("dump file", "2019_10_26_01_world.sql"),
    ("dump rows", "rows 4486, 4487, 4488, 4489, 4545, 4546, 4613, 4614"),
    ("lc files", "BattlegroundDeepwindGorge.h/.cpp"),
    ("lc rule fn", "LegionCore GetClosestGraveYard"),
    ("mop guide", "guide/deepwind-gorge-battleground-strategy"),
    ("rbg guide", "guide/deepwind-gorge-rated-battlegrounds-rbg-guide"),
    ("npc pages", "npc=71071 Alliance Mine Cart, npc=71073 Horde Mine Cart"),
    ("negatives header", "Negative results recorded"),
    ("unverified header", "=== 9. EXPLICIT UNVERIFIED LIST ==="),
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
    ok_lines, fails = [], []
    for name, lit in STATIC_CHECKS:
        if name == "unverified count":
            n = flat.count("unverified")
            hit = n >= UNVERIFIED_MIN
            ok_lines.append("    %-28s %s (%d >= %d)"
                            % (name, "ok" if hit else "FAIL", n,
                               UNVERIFIED_MIN))
            if not hit:
                fails.append(name)
            continue
        hit = norm(lit) in flat
        ok_lines.append("    %-28s %s" % (name, "ok" if hit else "MISSING"))
        if not hit:
            fails.append(name)
    for name, lit in NEGATIVE_CHECKS:
        hit = norm(lit) not in flat
        ok_lines.append("    %-28s %s" % (name, "ok" if hit else "PRESENT!"))
        if not hit:
            fails.append(name)
    return fails, ok_lines


# ---------------------------------------------------------------- stage 2
MUTATIONS = [
    ("heading", "- COMPLETED ===\nBattleground", "- DRAFT ===\nBattleground"),
    ("step number", "prompt 2 of 8", "prompt 2 of 7"),
    ("done line", "DONE - step 2 of 8 complete", "DONE - step 2 of 9 complete"),
    ("north rule", "smaller y = north, larger y = south",
     "smaller y = south, larger y = north"),
    ("north proof", "4546 y=195.135 vs 4488 y=242.712",
     "4546 y=195.136 vs 4488 y=242.712"),
    ("mine order", "y=431.1771 / 499.059 / 574.368",
     "y=431.1771 / 499.060 / 574.368"),
    ("map id note", "maps 1105 + 2245", "maps 1105 + 2246"),
    ("start row h", "(1105, -60.1632, 830.599, 135.379)",
     "(1105, -60.1632, 830.599, 135.380)"),
    ("start row a", "(1105, -275.198, 174.618, 136.185)",
     "(1105, -275.198, 174.619, 136.185)"),
    ("start id", "id 4487", "id 4490"),
    ("door float", "-263.455, 218.163", "-263.456, 218.163"),
    ("door facing", "o 4.72984", "o 4.72985"),
    ("door h", "-69.8785, 781.837", "-69.8786, 781.837"),
    ("cart float", "-241.741, 208.611", "-241.742, 208.611"),
    ("cart go o", "o 0.84278", "o 0.84279"),
    ("door id", "gameobject 220366", "gameobject 220367"),
    ("flag entry", "53194", "53195"),
    ("interact spell", "97388", "97389"),
    ("flag pan", "(1105, 68.39236, 431.1771, 111.4928)",
     "(1105, 68.39236, 431.1771, 111.4929)"),
    ("flag mid", "(1105, -167.5035, 499.059, 92.62903)",
     "(1105, -167.5035, 499.059, 92.62904)"),
    ("flag gob", "(1105, -397.7726, 574.368, 111.0529)",
     "(1105, -397.7726, 574.369, 111.0529)"),
    ("aura neutral", "neutral 98554", "neutral 98555"),
    ("aura contested", "98543 / Horde 98545", "98544 / Horde 98545"),
    ("cart aura", "141551 / Horde 141555", "141551 / Horde 141556"),
    ("carrier aura", "141210 on Alliance", "141211 on Alliance"),
    ("cart at", "9013", "9014"),
    ("catch row", "(1105, 104.08, 423.483, 112.371)",
     "(1105, 104.08, 423.484, 112.371)"),
    ("catch id", "id 4613", "id 4615"),
    ("route a pan", "legs: 45 yd, 394 yd", "legs: 45 yd, 395 yd"),
    ("route a gob", "legs: 45 yd, 381 yd", "legs: 45 yd, 382 yd"),
    ("route h gob", "legs: 50 yd, 388 yd", "legs: 50 yd, 389 yd"),
    ("route direct", "direct 648 yd", "direct 649 yd"),
    ("mine pair 1", "Pandaren-Central 245 yd", "Pandaren-Central 246 yd"),
    ("mine pair 2", "Pandaren-Goblin 488 yd", "Pandaren-Goblin 489 yd"),
    ("gy row n", "(1105, -113.682, 195.135, 137.454)",
     "(1105, -113.682, 195.136, 137.454)"),
    ("gy row hn", "(1105, -0.00868056, 758.708, 132.569)",
     "(1105, -0.00868056, 758.709, 132.569)"),
    ("spirit entry", "13116 (Alliance) and 13117 (Horde)",
     "13116 (Alliance) and 13118 (Horde)"),
    ("central gy a", "4488 (304 vs 309 yd)", "4488 (305 vs 309 yd)"),
    ("central gy h", "4545 (308 vs 309 yd", "4545 (307 vs 309 yd"),
    ("start gy dist", "163 yd (North) / 88 yd", "164 yd (North) / 88 yd"),
    ("pair separation", "223 yd (Alliance) / 227 yd (Horde)",
     "224 yd (Alliance) / 227 yd (Horde)"),
    ("buff spell b", "spell 24378", "spell 24379"),
    ("buff spell r", "spell 132958", "spell 132959"),
    ("cap 1500", "first to 1,500 points", "first to 1,600 points"),
    ("cap wins", "first to 1,500 wins", "first to 1,600 wins"),
    ("five points order", "Market, Farm, Ruins, Shrine, Quarry",
     "Market, Farm, Ruins, Quarry, Shrine"),
    ("ally bases", "Farm northeast, Shrine southeast",
     "Farm southeast, Shrine northeast"),
    ("cart npc", '71071 "Alliance', '71072 "Alliance'),
    ("capture time", "6-second", "5-second"),
    ("channel time", "7-second uninterrupted channel",
     "8-second uninterrupted channel"),
    ("mop cap", "cap 1600 in the", "cap 1700 in the"),
    ("current cap", "the cap is 1500 for map 2245",
     "the cap is 1501 for map 2245"),
]


# ---------------------------------------------------------------- stage 3
def stage3(corpora):
    token_map = {
        "dgh": [
            ("max score", "#define BG_DG_MAX_TEAM_SCORE 1500"),
            ("flag entry", "= 53194"),
            ("door 1", "= 220159"), ("door 2", "= 220160"),
            ("door 3", "= 220161"), ("door 4", "= 220366"),
            ("cart go a", "= 220164"), ("cart go h", "= 220166"),
            ("loc a bot", "BG_DG_LOC_SPIRIT_ALLIANCE_BOT = 4488"),
            ("loc h bot", "BG_DG_LOC_SPIRIT_HORDE_BOT    = 4545"),
            ("loc a top", "BG_DG_LOC_SPIRIT_ALLIANCE_TOP = 4546"),
            ("loc h top", "BG_DG_LOC_SPIRIT_HORDE_TOP    = 4489"),
            ("aura neutral", "= 98554"), ("aura h contest", "= 98545"),
            ("aura a contest", "= 98543"), ("aura h cap", "= 98527"),
            ("aura a cap", "= 98519"),
            ("cart aura h", "= 141555"), ("cart aura a", "= 141551"),
            ("chains", "= 141553"),
            ("capture", "= 97388"),
            ("spawn a", "= 141554"), ("spawn h", "= 141550"),
            ("flag aura h", "= 141210"), ("flag aura a", "= 140876"),
            ("ws goblin", "DG_GOBLIN_MINE_ALLIANCE_ASSAULT"),
            ("ws pandaren", "DG_PANDAREN_MINE_CAPTURED_BY_TEAM"),
        ],
        "dgc": [
            ("door 1 pos", "-263.455f, 218.163f, 132.43f, 4.72984f"),
            ("door 2 pos", "-213.712f, 201.043f, 132.488f, 3.9619f"),
            ("door 3 pos", "-69.8785f, 781.837f, 132.43f, 1.58825f"),
            ("door 4 pos", "-119.621f, 798.957f, 132.488f, 0.820303f"),
            ("cart pos a", "-241.741f, 208.611f, 133.747f, 0.84278f"),
            ("cart pos h", "-91.6163f, 791.361f, 133.747f, 4.02356f"),
            ("flag pos mid", "-167.5035f, 499.059f, 92.62903f, 1.249549f"),
            ("flag pos pan", "68.39236f, 431.1771f, 111.4928f, 1.229f"),
            ("flag pos gob", "-397.7726f, 574.368f, 111.0529f, 1.437866f"),
            ("gy rule a", "BG_DG_LOC_SPIRIT_ALLIANCE_BOT, "
                          "BG_DG_LOC_SPIRIT_HORDE_TOP"),
            ("gy rule h", "BG_DG_LOC_SPIRIT_ALLIANCE_TOP, "
                          "BG_DG_LOC_SPIRIT_HORDE_BOT"),
            ("at cart a", "IsInAreaTriggerRadius(9013)"),
            ("at cart h", "IsInAreaTriggerRadius(9012)"),
            ("cart npcs", "{71073, 71071}"),
            ("gold 200", "ModGold(GetTeamId(), -200)"),
            ("interact", "UNIT_FIELD_INTERACT_SPELL_ID, "
                         "BG_DG_CAPTURE_SPELL"),
            ("gy fn", "BattlegroundDeepwindGorge::GetClosestGraveYard"),
            ("add flags", "AddCreature(BG_DG_ENTRY_FLAG"),
            ("aura apply", "AddAura(BG_DG_AURA_NEUTRAL, m_point)"),
            ("setup doors", "SetupBattleground()"),
        ],
        "lbh": [
            ("spirit a", "= 13116"), ("spirit h", "= 13117"),
        ],
        "wsl": [
            ("row 4486", "(4486,1105,-60.1632,830.599,135.379,230.07,"
                         "'Gold Rush BG - Horde Start Location'),"),
            ("row 4487", "(4487,1105,-275.198,174.618,136.185,37.8039,"
                         "'Gold Rush BG - Alliance Start Location'),"),
            ("row 4488", "(4488,1105,-331.54,242.712,132.569,0,"
                         "'Gold Rush BG - Alliance Cemetery (South)'),"),
            ("row 4489", "(4489,1105,-0.00868056,758.708,132.569,189.014,"
                         "'Gold Rush BG - Horde Cemetery (North)'),"),
            ("row 4545", "(4545,1105,-222.743,802.188,137.451,313.287,"
                         "'Gold Rush BG - Horde Cemetery (South)'),"),
            ("row 4546", "(4546,1105,-113.682,195.135,137.454,134.932,"
                         "'Gold Rush BG - Alliance Cemetery (North)'),"),
            ("row 4613", "(4613,1105,104.08,423.483,112.371,161.378,"
                         "'Gold Rush BG - Pandaren Mine Catch'),"),
            ("row 4614", "(4614,1105,-438.592,582.325,111.57,0,"
                         "'Gold Rush BG - Goblin Mine Catch'),"),
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
                         "facing": m.group(6)}
    return rows


def parse_script_coords(cgc):
    """Parse doors/carts (AddObject) and mine flags (AddCreature) floats."""
    out = {}
    for m in re.finditer(
            r"AddObject\((BG_DG_DOOR_\d), (BG_DG_ENTRY_DOOR_\d), "
            r"([^)]+)\)", cgc):
        vals = [v.strip().rstrip("f") for v in m.group(3).split(",")[:4]]
        out[m.group(2)] = tuple(vals)
    for key, entry in (("BG_DG_CART_ALLIANCE", "BG_DG_ENTRY_CART_ALLIANCE"),
                       ("BG_DG_CART_HORDE", "BG_DG_ENTRY_CART_HORDE")):
        m = re.search(r"AddObject\(%s, %s, ([^)]+)\)"
                      % (key, re.escape(entry)), cgc)
        if m:
            vals = [v.strip().rstrip("f") for v in m.group(1).split(",")[:4]]
            out[entry] = tuple(vals)
    for m in re.finditer(
            r"AddCreature\(BG_DG_ENTRY_FLAG, BG_DG_UNIT_FLAG_(\w+), "
            r"TEAM_NEUTRAL, ([^)]+)\)", cgc):
        vals = [v.strip().rstrip("f") for v in m.group(2).split(",")[:4]]
        out["FLAG_" + m.group(1)] = tuple(vals)
    return out


def rd(x):
    return int(x + 0.5)


def stage4(text, corpora, probe=False):
    if probe:
        text = text.replace("(1105, -113.682, 195.135, 137.454)",
                            "(1105, -113.682, 195.136, 137.454)", 1)
    flat = norm(text)
    lines, fails = [], []

    # 4a. the eight dump rows vs the document
    rows = parse_wsl_rows(corpora["wsl"])
    hit = 0
    for rid in ROW_IDS:
        r = rows.get(rid)
        if not r:
            fails.append("row %d missing from dump" % rid)
            lines.append("    row %-5d NOT IN DUMP" % rid)
            continue
        triple = "(%s, %s, %s, %s)" % (r["map"], r["x"], r["y"], r["z"])
        context = triple in flat or ("id %d" % rid) in flat
        facing_ok = re.search(r"(?<![0-9.])o %s(?![0-9.])"
                              % re.escape(r["facing"]), flat)
        ok = triple in flat and context and bool(facing_ok)
        hit += ok
        if not ok:
            fails.append("row %d doc mismatch" % rid)
        lines.append("    row %-5d %-48s %s"
                     % (rid, triple, "ok" if ok else "DOC MISMATCH"))
    lines.append("    world_safe rows matched: %d/%d" % (hit, len(ROW_IDS)))

    # 4b. script floats parsed from the cpp vs the document
    coords = parse_script_coords(corpora["dgc"])
    expect_keys = ["BG_DG_ENTRY_DOOR_1", "BG_DG_ENTRY_DOOR_2",
                   "BG_DG_ENTRY_DOOR_3", "BG_DG_ENTRY_DOOR_4",
                   "BG_DG_ENTRY_CART_ALLIANCE", "BG_DG_ENTRY_CART_HORDE",
                   "FLAG_MID", "FLAG_TOP", "FLAG_BOT"]
    c_ok = 0
    for k in expect_keys:
        v = coords.get(k)
        if not v:
            fails.append("script float %s unparsed" % k)
            lines.append("    script %-24s PARSE FAIL" % k)
            continue
        triple = "(1105, %s, %s, %s)" % (v[0], v[1], v[2])
        ok = triple in flat
        c_ok += ok
        if not ok:
            fails.append("script float %s doc mismatch" % k)
        lines.append("    script %-24s %-48s %s"
                     % (k, triple, "ok" if ok else "DOC MISMATCH"))
    lines.append("    script coordinate triples matched: %d/%d"
                 % (c_ok, len(expect_keys)))

    # 4c. route legs / directs / door summary / catch distances
    A = (float(rows[4487]["x"]), float(rows[4487]["y"]))
    H = (float(rows[4486]["x"]), float(rows[4486]["y"]))
    dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])

    def pt(key):
        v = coords[key]
        return (float(v[0]), float(v[1]))

    d1, d2 = pt("BG_DG_ENTRY_DOOR_1"), pt("BG_DG_ENTRY_DOOR_2")
    d3, d4 = pt("BG_DG_ENTRY_DOOR_3"), pt("BG_DG_ENTRY_DOOR_4")
    ca, ch = pt("BG_DG_ENTRY_CART_ALLIANCE"), pt("BG_DG_ENTRY_CART_HORDE")
    pan, mid, gob = pt("FLAG_TOP"), pt("FLAG_MID"), pt("FLAG_BOT")

    routes = [
        ("A->Pandaren", A, d1, pan), ("A->Central", A, d1, mid),
        ("A->Goblin", A, d1, gob), ("A->Horde cart", A, d1, ch),
        ("H->Pandaren", H, d3, pan), ("H->Central", H, d3, mid),
        ("H->Goblin", H, d3, gob), ("H->Alliance cart", H, d3, ca),
    ]
    ok_routes = 0
    for name, s, door, node in routes:
        l1, l2, direct = rd(dist(s, door)), rd(dist(door, node)), \
            rd(dist(s, node))
        want = ["legs: %d yd, %d yd" % (l1, l2), "direct %d yd" % direct]
        ok = all(w in flat for w in want)
        ok_routes += ok
        if not ok:
            fails.append("route %s (%s)" % (name, want))
        lines.append("    %-17s legs %3d + %3d, direct %3d   %s"
                     % (name, l1, l2, direct, "ok" if ok else "MISMATCH"))
    lines.append("    route legs+direct: %d/%d match recompute"
                 % (ok_routes, len(routes)))

    summary = [
        "Alliance start to 220159 = %d yd" % rd(dist(A, d1)),
        "to 220160 = %d yd" % rd(dist(A, d2)),
        "to own cart = %d yd" % rd(dist(A, ca)),
        "Horde start to 220161 = %d yd" % rd(dist(H, d3)),
        "to 220366 = %d yd" % rd(dist(H, d4)),
        "to own cart = %d yd" % rd(dist(H, ch)),
    ]
    # the doc repeats "to own cart = NN yd" for both teams; check both values
    a_cart, h_cart = rd(dist(A, ca)), rd(dist(H, ch))
    sum_ok = 0
    for s in summary:
        if s == "to own cart = %d yd" % a_cart and \
                ("to own cart = %d yd" % a_cart) in flat:
            sum_ok += 1
            continue
        if s == "to own cart = %d yd" % h_cart and \
                ("to own cart = %d yd" % h_cart) in flat:
            sum_ok += 1
            continue
        if s in flat:
            sum_ok += 1
        else:
            fails.append("door summary: %s" % s)
    lines.append("    door/cart summary strings: %d/%d"
                 % (sum_ok, len(summary)))

    pairs = [("Pandaren-Central", pan, mid), ("Central-Goblin", mid, gob),
             ("Pandaren-Goblin", pan, gob)]
    ok_pairs = 0
    for label, p, q in pairs:
        want = "%s %d yd" % (label, rd(dist(p, q)))
        ok = want in flat
        ok_pairs += ok
        if not ok:
            fails.append("mine pair %s" % label)
    lines.append("    mine pair distances: %d/%d match recompute"
                 % (ok_pairs, len(pairs)))

    c4613 = (float(rows[4613]["x"]), float(rows[4613]["y"]))
    c4614 = (float(rows[4614]["x"]), float(rows[4614]["y"]))
    catch = [("Pandaren", rd(dist(c4613, pan))), ("Goblin", rd(dist(c4614, gob)))]
    ok_catch = 0
    for label, n in catch:
        want = "(%d yd from %s flag)" % (n, label)
        ok = want in flat
        ok_catch += ok
        if not ok:
            fails.append("catch %s" % label)
    lines.append("    mine catch distances: %d/%d match recompute"
                 % (ok_catch, len(catch)))

    # 4d. graveyard rule recomputation (LegionCore algorithm)
    pair_a = (4546, 4488)   # (North, South) Alliance
    pair_h = (4489, 4545)   # (North, South) Horde

    def gy_res(rid):
        r = rows[rid]
        return (float(r["x"]), float(r["y"]))

    def closest2(corpse, default, alt):
        ddef = dist(corpse, gy_res(default))
        dalt = dist(corpse, gy_res(alt))
        if dalt < ddef:
            return alt, rd(dalt), rd(ddef)
        return default, rd(ddef), rd(dalt)

    res = {}
    for label, pos in (("Pandaren", pan), ("Central", mid), ("Goblin", gob)):
        a_id, a_c, a_f = closest2(pos, 4488, 4546)
        h_id, h_c, h_f = closest2(pos, 4489, 4545)
        res[label] = (a_id, a_c, a_f, h_id, h_c, h_f)

    checks = [
        ("gy pandaren", "Pandaren Mine -> Alliance %d / Horde %d"
         % (res["Pandaren"][0], res["Pandaren"][3])),
        ("gy goblin", "Goblin Mine -> Alliance %d / Horde %d"
         % (res["Goblin"][0], res["Goblin"][3])),
        ("gy central a", "Central Mine -> Alliance %d (%d vs %d yd"
         % (res["Central"][0], res["Central"][1], res["Central"][2])),
        ("gy central h", "Horde %d (%d vs %d yd"
         % (res["Central"][3], res["Central"][4], res["Central"][5])),
    ]
    margins = sorted([abs(res["Central"][1] - res["Central"][2]),
                      abs(res["Central"][4] - res["Central"][5])])
    checks.append(("gy margin", "%d-%d yd" % (margins[0], margins[1])))
    ok_gy = 0
    for name, want in checks:
        ok = want in flat
        ok_gy += ok
        if not ok:
            fails.append("%s (%s)" % (name, want))
        lines.append("    %-22s %-46s %s"
                     % (name, want, "ok" if ok else "MISMATCH"))
    lines.append("    graveyard rule checks: %d/%d"
                 % (ok_gy, len(checks)))

    aN = rd(dist(A, gy_res(4546)))
    aS = rd(dist(A, gy_res(4488)))
    hN = rd(dist(H, gy_res(4489)))
    hS = rd(dist(H, gy_res(4545)))
    want = ("Alliance start to own cemeteries = %d yd (North) / %d yd "
            "(South); Horde start = %d yd (North) / %d yd (South)"
            % (aN, aS, hN, hS))
    ok = want in flat
    if not ok:
        fails.append("start->GY distances")
    lines.append("    start->own-GY distances            %s"
                 % ("ok" if ok else "MISMATCH: " + want))

    sep_a = rd(dist(gy_res(4546), gy_res(4488)))
    sep_h = rd(dist(gy_res(4489), gy_res(4545)))
    want = ("separation is %d yd (Alliance) / %d yd (Horde)"
            % (sep_a, sep_h))
    ok = want in flat
    if not ok:
        fails.append("GY pair separation")
    lines.append("    GY pair separation                 %s"
                 % ("ok" if ok else "MISMATCH: " + want))

    # 4e. coordinate trace + probe
    ok_c, c_lines, missing_c = coord_trace(text, corpora)
    lines.extend(c_lines)
    if not ok_c:
        fails.append("coordinate trace: %s" % missing_c[:6])
    probe_txt = text.replace("(1105, -60.1632, 830.599, 135.379)",
                             "(1105, -60.1632, 830.599, 135.380)", 1)
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

    # neither BfA core ships a Deepwind script (Zones listing via gh)
    for repo in (HAVEN, BFA):
        res = subprocess.run(
            ["gh", "api", "repos/%s/contents/%s" % (repo, ZONES),
             "--jq", ".[].name"],
            capture_output=True, text=True)
        names = [n for n in res.stdout.split() if n]
        bad = [n for n in names if re.search(r"(?i)deepwind|battlegrounddg",
                                             n)]
        sanity = "BattlegroundAB.cpp" in names
        ok = res.returncode == 0 and sanity and not bad
        if not ok:
            fails.append("zones listing %s (%s)" % (repo, bad))
        lines.append("    %-32s %d files, no Deepwind script: %s"
                     % (repo, len(names), "yes" if ok else "NO"))
    # BattlegroundDS.h content (make sure DS != Deepwind)
    ds = gh_content(HAVEN, DS_H)
    ds_ok = bool(ds) and not re.search(r"(?i)deepwind|gorge|1105", ds)
    if not ds_ok:
        fails.append("BattlegroundDS.h contains Deepwind markers")
    lines.append("    BattlegroundDS.h has no Deepwind markers: %s"
                 % ("yes" if ds_ok else "NO"))

    # AzerothCore template: no Deepwind row
    act_ok = not re.search(r"(?i)deepwind|gold rush", corpora["act"])
    if not act_ok:
        fails.append("AC template has a Deepwind row")
    lines.append("    AzerothCore template Deepwind-negative: %s"
                 % ("yes" if act_ok else "NO"))

    # post-8.3 TC updates: no Deepwind / Gold Rush / map 2245 rows
    clean = 0
    for fn in TC_ABSENCE:
        t = gh_content(TC, "sql/old/8.x/world/19071_2020_06_17/" + fn)
        if t is None:
            fails.append("absence file unreadable: %s" % fn)
            continue
        if not re.search(r"(?i)deepwind|gold rush|,2245,", t):
            clean += 1
        else:
            fails.append("absence file has hits: %s" % fn)
    lines.append("    post-8.3 TC files clean of DG/2245:   %d/%d"
                 % (clean, len(TC_ABSENCE)))

    # document-claim injection probes
    inj1 = text + "\nnavmesh confirmed under inspection.\n"
    f1, _ = run_static(inj1)
    r1 = "no navmesh confirmed" in f1
    lines.append("    injection probe (navmesh confirmed):  %s"
                 % ("detected" if r1 else "NOT DETECTED"))
    if not r1:
        fails.append("navmesh injection probe")

    inj2 = text + "\nverified by direct inspection.\n"
    f2, _ = run_static(inj2)
    r2 = "no direct inspection" in f2
    lines.append("    injection probe (direct inspection):  %s"
                 % ("detected" if r2 else "NOT DETECTED"))
    if not r2:
        fails.append("direct-inspection injection probe")

    stripped = text.replace("unverified", "verified")
    f3, _ = run_static(stripped)
    r3 = "unverified count" in f3
    lines.append("    injection probe (unverified stripped):%s"
                 % (" detected" if r3 else " NOT DETECTED"))
    if not r3:
        fails.append("unverified count probe")

    # gh 404 control
    res = subprocess.run(
        ["gh", "api", "-X", "GET",
         "repos/%s/contents/src/server/game/DoesNotExist.cpp" % LEGION],
        capture_output=True, text=True)
    absent = res.returncode != 0
    lines.append("    control: bogus LegionCore path 404:  %s"
                 % ("yes" if absent else "NO"))
    if not absent:
        fails.append("gh 404 control")
    lines.append("    control: live corpora loaded:        %d"
                 % len(corpora))
    return fails, lines


# ---------------------------------------------------------------- main
def main():
    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()

    print("=" * 68)
    print("AUDIT: Coordinates_Deepwind_Gorge_COMPLETED.txt (BG coords step 2)")
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
    corpora = {k: gh_content(LEGION, p) for k, p in LC_FILES.items()}
    corpora["wsl"] = gh_content(TC, TC_DUMP)
    corpora["act"] = gh_content(AC, AC_TEMPLATE)
    missing = [k for k, v in corpora.items() if v is None]
    if missing:
        print("    CORPUS FETCH FAILED: %s" % missing)
        return 1
    ok3, lines3 = stage3(corpora)
    for ln in lines3:
        print(ln)
    print("    (wiki/wowhead literals are guarded by stages 1-2 only - "
          "not reachable from gh)")
    if not ok3:
        print("    SOURCE CROSS-CHECK FAILED")
    probe_undetected = mutation_probe(
        corpora,
        {"dgc": [("central flag float", "-167.5035f")]},
        lambda t: t.replace("-167.5035f", "-167.5045f"))
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
    print("    row check reacts to doc tamper:      %s"
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
