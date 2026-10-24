#!/usr/bin/env python3
"""Audit: Vehicles_Isle_of_Conquest_COMPLETED.txt (Battleground_Vehicles 1)."""

import re
import sys

sys.path.insert(0, ".")
from audit_common import (gh_content, gh_raw, source_stage, mutation_probe,
                          coord_trace)

DOC = ("# Ai Research prompts/Battleground_Vehicles_completed/"
       "Vehicles_Isle_of_Conquest_COMPLETED.txt")
LC = "Titans-Project/LegionCore-Reforged"
AC = "azerothcore/azerothcore-wotlk"
B = "data/sql/base/db_world/"
FILES = {
    "ioc_h": "src/server/game/Battlegrounds/Zones/BattlegroundIsleOfConquest.h",
    "ioc_c": "src/server/game/Battlegrounds/Zones/BattlegroundIsleOfConquest.cpp",
    "zone": "src/server/scripts/Northrend/IsleOfConquest/isle_of_conquest.cpp",
}
RAW_FILES = {
    "ct": B + "creature_template.sql",
    "got": B + "gameobject_template.sql",
}
SMALL_FILES = {
    "cts": B + "creature_template_spell.sql",
    "vta": B + "vehicle_template_accessory.sql",
    "ssn": B + "spell_script_names.sql",
    "vdbc": B + "vehicle_dbc.sql",
    "vsdbc": B + "vehicleseat_dbc.sql",
}
GATE_IDS = [195699, 195698, 195700, 195494, 195496, 195495]
UNVERIFIED_MIN = 25


def norm(s):
    return re.sub(r"\s+", " ", s)


STATIC_CHECKS = [
    ("heading", "=== VEHICLES - ISLE OF CONQUEST - BFA 8.3.7 "
                "(TRINITYCORE) - COMPLETED ==="),
    ("numbering", "Prompt 1 of the Battleground_Vehicles set (Isle of "
                  "Conquest, map 628)"),
    ("done", "DONE - step 1 of the Battleground_Vehicles set complete"),
    ("no-estimate", "nothing is estimated"),
    ("unverified policy", 'says "unverified"'),
    ("no pathing", "no pathing source for map 628"),
    ("src A", "BattlegroundIsleOfConquest.cpp/.h (Zones)"),
    ("src A2", "isle_of_conquest.cpp (script"),
    ("src B", "AzerothCore world-db base SQL"),
    ("src C", "warcraft.wiki.gg: Isle of Conquest"),
    ("win general", "High Commander Halford Wyrmbane, creature 34924"),
    ("win agmar", "Overlord Agmar, creature 34922"),
    ("reinforce", "starts with 300 reinforcements"),
    ("gate rule", "At least 1 of the enemy keep's 3 gates"),
    ("capture channel", "channeled, interruptible"),
    ("plus15", "stacking +15% siege"),
    ("gate a1", 'id 195699 "Alliance Gate" Left   (628, 351.615, -762.75, '
                '48.9162)  o -1.5708'),
    ("gate a2", 'id 195698 "Alliance Gate" Right  (628, 351.024, '
                '-903.326, 48.9247)  o 1.5708'),
    ("gate a3", 'id 195700 "Alliance Gate" Front  (628, 413.479, -833.95, '
                '48.5238)  o 3.14159'),
    ("gate h1", 'id 195494 "Horde Gate" Front     (628, 1150.9, -762.606, '
                '47.5077)  o 3.14159'),
    ("gate h2", 'id 195496 "Horde Gate" Right     (628, 1217.9, -676.948, '
                '47.6341)  o 1.5708'),
    ("gate h3", 'id 195495 "Horde Gate" Left      (628, 1218.74, -851.155, '
                '48.2533)  o -1.5708'),
    ("tpl type", "type 33 (destructible), size 1, Data0=1, Data5=600000"),
    ("tpl displays", "22082/22078/22080"),
    ("tpl displays h", "22079/22081/22083"),
    ("tpl faction", "Data18 = 62\n   (Alliance rows) / 61 (Horde rows)"),
    ("health caveat", "gate-health slot of the type-33 row"),
    ("weapons list", "Demolisher Hurl Boulder and Ram"),
    ("weapons list2", "Glaive Throw (the Glaive's primary gate role per C)"),
    ("weapons list3", "Seaforium Bombs and Huge Seaforium Bombs"),
    ("no tower gate", "NOT listed as gate-damaging (C)"),
    ("no catapult gate", "catapults, players' normal attacks: not listed as "
                         "gate-damaging"),
    ("dg worldstate", "the gate's closed-worldstate goes 0 and open-state 1"),
    ("dg port a", "open gameobject 195223 at (628, 1283.05,"),
    ("dg port h", "open gameobject 195452 at (628, 273.033,"),
    ("dg banner", "keep banner loses its not-selectable flag"),
    ("dg honor", "GetBonusHonorFromKill(8)"),
    ("dg texts", "text ids 35409-35414"),
    ("door fx a", "gameobject 195703 \"Doodad_ND_Human_Gate_ClosedFX_"
                  "Door01\""),
    ("door fx h", "gameobject 195491 \"Doodad_ND_WinterOrc_Wall_GateFX_"
                  "Door01\""),
    ("door sniff", "this was not sniffed because I only had"),
    ("door pc1", "gameobject 195436 \"Doodad_HU_Portcullis01\" (628, "
                 "401.024, -780.724, 49.9482)"),
    ("door pc2", "gameobject 195437 \"Doodad_VR_Portcullis01\" (628, "
                 "1156.89,"),
    ("door odd", "gameobject 195451 \"Doodad_PortcullisActive01\" "
                 "(-832.595, 51.4109, -0.0261791)"),
    ("door odd unver", "position unverified"),
    ("door active2", "gameobject 195452 \"Doodad_PortcullisActive02\" "
                     "(628, 273.033,"),
    ("door horde", "gameobject 195223 \"Horde Keep Portcullis\" (628, "
                   "1283.05,"),
    ("banner h", "Horde banner gameobject 195393 (628, 1284.76, -705.668, "
                 "48.9163)"),
    ("banner a", "Alliance banner gameobject 195396 (628, 299.153,"),
    ("tele spells", "(H-OUT, spell 66549), 195313 (H-IN, spell 66548)"),
    ("tele a", "195315 (A-OUT,\n   66549), 195316 (A-IN, 66548)"),
    ("tower unver", "are not damageable\n   structures in any readable "
                    "source - unverified as damageable"),
    ("veh flag", "npcflag\n   16777216"),
    ("demo entry", "creature 34775 \"Demolisher\""),
    ("demo spawn1", "(628, 751.8281, -852.732666, 12.5250978)"),
    ("demo spawn4", "(628, 793.055542, -852.71875, 12.5671329)"),
    ("demo seats", "1 pilot (weapons + driving) + 2 passengers"),
    ("demo spell1", "spell 67440 \"Hurl Boulder\" - range: catapult-style"),
    ("demo range", "about 1 to 50 yd"),
    ("demo cd", "cooldown 3 s"),
    ("demo siege", "1,500 siege damage"),
    ("demo spell2", "spell 67441 \"Ram\""),
    ("demo ram7", "front within 7 yd"),
    ("demo ram cd", "cooldown 4 s"),
    ("siege entries", "creatures 34776 (Alliance) / 35069 (Horde)"),
    ("siege spawn", "(628, 773.680542, -884.092041, 16.8090363)"),
    ("siege flags", "UNIT_FLAG_NOT_SELECTABLE|CANNOT_SWIM|IMMUNE_TO_PC"),
    ("siege timer", "WORKSHOP_UPDATE_TIME = 180000 ms"),
    ("siege seats", "driver + main turret (seat 7) + 2 flame turrets (seats"),
    ("siege acc", "A 34778 flame x2 seats"),
    ("siege acc2", "34777 main seat 7; H 36356 x2 + 36355"),
    ("siege ram", "spell 67796 \"Ram\""),
    ("siege ram cd", "cooldown 1.5 s"),
    ("siege 67797", "spell 67797 - on the driver bar of both faction "
                    "templates"),
    ("siege rush", "64871 \"Steam Rush\" 70 yd"),
    ("siege cannon", "67461 \"Fire Cannon\" 10-70 yd"),
    ("siege blast", "66203 \"Steam Blast\" 10-yd"),
    ("siege napalm", "66186 \"Napalm\" cost 40"),
    ("siege flame", "67446 \"Flame Turret\" 15-yd"),
    ("cat entry", "creature 34793 \"Catapult\""),
    ("cat spawn1", "(628, 757.283, -341.7795, 12.2113762)"),
    ("cat spawn4", "(628, 810.7257, -342.083344, 12.1675768)"),
    ("cat seats", "total seat count unverified"),
    ("cat launch", "spell 66218 \"Launch\" - 40 yd"),
    ("cat script", "bound to script\n          spell_ioc_launch"),
    ("cat veil", "spell 66296 \"Shadow Veil\""),
    ("cat speed", "+50% movement speed and stealth for 20 s"),
    ("glaive entries", "creatures 34802 (Alliance) / 35273 (Horde)"),
    ("glaive spawn1", "(628, 779.3125, -342.972229, 12.2104874)"),
    ("glaive seats", "driver's seat only"),
    ("glaive spell", "spell 66456 \"Glaive Throw\""),
    ("glaive cd", "cooldown 1.5 s"),
    ("glaive siege", "4,500 siege in 5-yd radius"),
    ("glaive salvo", "spell 67195 \"Blade Salvo\" - channeled 10 s"),
    ("glaive salvo cd", "cooldown 30 s"),
    ("glaive horde", "spell 67034 (B) + 67195"),
    ("gun entries", "creatures 34929 (Alliance) / 34935 (Horde)"),
    ("gun count", "5 per ship on the port side"),
    ("gun grid", "GetCreatureListWithEntryInGrid(..., 150.0f)"),
    ("gun ships", 'gameobject 195121 "Alliance Gunship" / 195276 "Horde'),
    ("gun type", "type 15 transport"),
    ("gun disable", "emptied of riders and made not-selectable"),
    ("gun spell a", "Alliance spell 66518, Horde spell 66529"),
    ("gun spell name", '"Airship Cannon" - instant'),
    ("gun siege", "1,000 siege damage"),
    ("kc entry", 'creature 34944 "Keep Cannon"'),
    ("kc counts", "12 Alliance rows + 13 Horde rows"),
    ("kc dup", "one exact duplicate position"),
    ("kc rocket", 'spell 67452 "Rocket Blast" - 10-70 yd; instant; '
                  'cooldown 2 s'),
    ("kc inc", 'spell 66541 "Incendiary Rocket" - 10-70 yd; instant;'),
    ("kc inc cd", "cooldown 30 s"),
    ("kc inc dot", "15,500 Fire per second for 15 s"),
    ("kc turret script", "'npc_isle_of_conquest_turret'"),
    ("capt entries", "creatures 34960 (Alliance) / 35003 (Horde)"),
    ("capt a", "(628, 826.2205, -994.4028,\n       134.2812)"),
    ("capt rel", "(628, 10.89952, 4.880297, 20.49038)"),
    ("capt script", "'npc_ioc_gunship_captain'"),
    ("bomb entry", 'gameobject 195237 "Seaforium Bombs"'),
    ("bomb spell", "cast spell\n       66265"),
    ("bomb spawn1", "(628, 750.601, -864.597, 13.4754)"),
    ("bomb respawn", "Respawn 10 s, faction = workshop owner"),
    ("bomb rules", "detonates 10 s after planting"),
    ("huge entries", 'gameobject 195332 (Alliance keep stock) / 195333'),
    ("huge spell", "cast spell\n       66669"),
    ("huge a1", "(628, 297.3212, -851.321167, 48.91627)"),
    ("huge h4", "(628, 1273.849, -796.2778, 48.9364281)"),
    ("huge timer", "forced to 10 at setup (A SetRespawnTime(10))"),
    ("credits", "68365 demolisher"),
    ("seq demo", "immediately gets 4 demolishers + 2 seaforium"),
    ("seq siege", "siege engine becomes usable at\n   3 minutes"),
    ("seq front h", "Alliance front target: 628, 1150.9, -762.606,"),
    ("seq front a", "Horde front target: 628, 413.479, -833.95, 48.5238"),
    ("seq penin", "peninsula spots across\n   from the keeps"),
    ("solo phrase", "Solo-capable (mechanic needs only 1 player)"),
    ("duo phrase", "Needs 2+ players (by the mechanics)"),
    ("solo siege", "4 simultaneous seats"),
    ("neg verified", "VerifiedBuild 10314/12340"),
    ("neg scripts", "only isle_of_conquest.cpp - checked"),
    ("neg epgd", "EventPlayerDamagedGO"),
    ("neg empty", "in the BG script is empty"),
    ("neg dbc", "vehicle_dbc/vehicleseat_dbc tables in the AC"),
    ("neg dbc2", "are EMPTY (checked)"),
    ("neg wiki", "guns per tower, the Keep Cannon subpage says"),
    ("unver hdr", "7. EXPLICIT UNVERIFIED LIST"),
    ("unver gate", "retail gate HP"),
    ("unver catapult", "Catapult total seat count"),
    ("unver 67797", "67797 (siege driver slot 2) name"),
    ("unver path", "Gunship flight path"),
    ("unver order", "The gameplay order a \"good team\" runs"),
]

NEGATIVE_CHECKS = [
    ("no estimated coordinate", "estimated coordinate"),
    ("no navmesh confirmed", "navmesh confirmed"),
    ("no direct inspection", "verified by direct inspection"),
    ("no todo", "TODO"),
    ("no fixme", "FIXME"),
]


def run_static(text):
    flat = norm(text)
    lines, fails = [], []
    n = flat.count("unverified")
    hit = n >= UNVERIFIED_MIN
    lines.append("    %-24s %s (%d >= %d)" % ("unverified count",
                 "ok" if hit else "FAIL", n, UNVERIFIED_MIN))
    if not hit:
        fails.append("unverified count")
    for name, lit in STATIC_CHECKS:
        ok = norm(lit) in flat
        lines.append("    %-24s %s" % (name, "ok" if ok else "MISSING"))
        if not ok:
            fails.append(name)
    for name, lit in NEGATIVE_CHECKS:
        ok = norm(lit) not in flat
        lines.append("    %-24s %s" % (name, "ok" if ok else "PRESENT!"))
        if not ok:
            fails.append(name)
    return fails, lines


MUTATIONS = [
    ("heading", "- COMPLETED ===\n\nPrompt", "- DRAFT ===\n\nPrompt"),
    ("numbering", "Prompt 1 of the Battleground_Vehicles set",
     "Prompt 9 of the Battleground_Vehicles set"),
    ("done", "DONE - step 1 of the Battleground_Vehicles set complete",
     "DONE - step 1 of the Battleground_Vehicles set is done"),
    ("reinforce", "starts with 300 reinforcements",
     "starts with 301 reinforcements"),
    ("gate rule", "At least 1 of the enemy keep's 3 gates",
     "At least 2 of the enemy keep's 3 gates"),
    ("plus15", "+15% siege", "+16% siege"),
    ("gate a1", "(628, 351.615, -762.75, 48.9162)",
     "(628, 351.615, -762.75, 48.9163)"),
    ("gate h3", "(628, 1218.74, -851.155, 48.2533)",
     "(628, 1218.74, -851.155, 48.2534)"),
    ("gate entry a1", "id 195699 \"Alliance Gate\" Left",
     "id 195701 \"Alliance Gate\" Left"),
    ("tpl health", "Data5=600000", "Data5=600001"),
    ("tpl display", "22082/22078/22080", "22083/22078/22080"),
    ("dg honor", "GetBonusHonorFromKill(8)", "GetBonusHonorFromKill(9)"),
    ("dg texts", "35409-35414", "35409-35415"),
    ("door port", "open gameobject 195223", "open gameobject 195224"),
    ("door pc1", "(628, 401.024,\n      -780.724, 49.9482)",
     "(628, 401.024,\n      -780.724, 49.9483)"),
    ("door odd", "(-832.595,\n      51.4109, -0.0261791)",
     "(-832.595,\n      51.4109, -0.0261792)"),
    ("banner h", "195393 (628, 1284.76, -705.668, 48.9163)",
     "195393 (628, 1284.76, -705.668, 48.9164)"),
    ("tele spell", "195314\n   (H-OUT, spell 66549)", "195314\n   (H-OUT, "
     "spell 66550)"),
    ("demo spawn", "(628, 751.8281, -852.732666, 12.5250978)",
     "(628, 751.8281, -852.732666, 12.5250979)"),
    ("demo seats", "1 pilot (weapons + driving) + 2 passengers",
     "1 pilot (weapons + driving) + 3 passengers"),
    ("demo spell", "spell 67440 \"Hurl Boulder\"", "spell 67442 \"Hurl "
     "Boulder\""),
    ("demo cd", "cooldown 3 s", "cooldown 4 s"),
    ("demo ram range", "front within 7 yd", "front within 8 yd"),
    ("siege spawn", "(628, 773.680542,\n       -884.092041, 16.8090363)",
     "(628, 773.680542,\n       -884.092041, 16.8090364)"),
    ("siege timer", "WORKSHOP_UPDATE_TIME = 180000 ms",
     "WORKSHOP_UPDATE_TIME = 180001 ms"),
    ("siege seats", "main turret (seat 7)", "main turret (seat 6)"),
    ("siege acc", "34778 flame x2 seats", "34779 flame x2 seats"),
    ("siege ram cd", "cooldown 1.5 s", "cooldown 1.6 s"),
    ("siege rush", "64871 \"Steam Rush\" 70 yd", "64871 \"Steam Rush\" 71 yd"),
    ("siege cannon", "67461 \"Fire Cannon\" 10-70 yd",
     "67461 \"Fire Cannon\" 10-71 yd"),
    ("cat spawn", "(628, 757.283, -341.7795, 12.2113762)",
     "(628, 757.283, -341.7795, 12.2113763)"),
    ("cat launch", "spell 66218 \"Launch\" - 40 yd",
     "spell 66218 \"Launch\" - 41 yd"),
    ("cat veil", "+50% movement speed and stealth for 20 s",
     "+51% movement speed and stealth for 20 s"),
    ("glaive spawn", "(628, 779.3125, -342.972229, 12.2104874)",
     "(628, 779.3125, -342.972229, 12.2104875)"),
    ("glaive cd", "cooldown 1.5 s", "cooldown 1.7 s"),
    ("glaive salvo cd", "cooldown 30 s", "cooldown 31 s"),
    ("glaive horde", "spell 67034 (B) + 67195", "spell 67035 (B) + 67195"),
    ("gun count", "5 per ship on the port side", "6 per ship on the port "
     "side"),
    ("gun grid", "150.0f", "151.0f"),
    ("gun spell", "Alliance spell 66518, Horde spell 66529",
     "Alliance spell 66519, Horde spell 66529"),
    ("gun cd", "cooldown 1.5 s", "cooldown 1.9 s"),
    ("kc rows", "12 Alliance rows + 13 Horde rows", "12 Alliance rows + "
     "14 Horde rows"),
    ("kc rocket cd", "instant; cooldown 2 s", "instant; cooldown 3 s"),
    ("kc inc cd", "cooldown 30 s", "cooldown 29 s"),
    ("capt rel", "(628, 10.89952, 4.880297, 20.49038)",
     "(628, 10.89952, 4.880297, 20.49039)"),
    ("bomb respawn", "Respawn 10 s, faction = workshop owner",
     "Respawn 11 s, faction = workshop owner"),
    ("bomb detonate", "detonates 10 s after planting",
     "detonates 11 s after planting"),
    ("huge spell", "66669", "66670"),
    ("huge a1", "(628, 297.3212, -851.321167, 48.91627)",
     "(628, 297.3212, -851.321167, 48.91628)"),
    ("huge timer", "SetRespawnTime(10)", "SetRespawnTime(11)"),
    ("solo seats", "4\n   simultaneous seats", "5\n   simultaneous seats"),
]


def stage3(corpora):
    token_map = {
        "ioc_h": [
            ("gate enums", "GO_ALLIANCE_GATE_1 = 195699"),
            ("gate enums h", "GO_HORDE_GATE_1 = 195494"),
            ("door enums", "GO_DOODAD_HU_PORTCULLIS01 = 195436"),
            ("door enums2", "GO_HORDE_KEEP_PORTCULLIS = 195223"),
            ("tele comment", "GO_TELEPORTER_1 = 195314, // 195314 H-OUT "
                             "66549"),
            ("timer", "WORKSHOP_UPDATE_TIME = 180000"),
            ("timer2", "DOCKS_UPDATE_TIME = 180000"),
            ("npc demo", "NPC_DEMOLISHER                      = 34775"),
            ("npc siege", "NPC_SIEGE_ENGINE_A                  = 34776"),
            ("npc catapult", "NPC_CATAPULT                        = 34793"),
            ("npc kc", "NPC_KEEP_CANNON                     = 34944"),
            ("gate row a", "351.615f, -762.75f, 48.9162f"),
            ("gate row h", "1218.74f, -851.155f, 48.2533f"),
            ("workshop row", "751.8281f, -852.732666f, 12.5250978f"),
            ("siege row", "773.680542f, -884.092041f, 16.8090363f"),
            ("docks row", "779.3125f, -342.972229f, 12.2104874f"),
            ("catapult row", "757.283f, -341.7795f, 12.2113762f"),
            ("bomb row", "750.601f, -864.597f, 13.4754f"),
            ("captains", "BG_IC_HangarCaptains[4]"),
            ("huge a row", "297.3212f, -851.321167f, 48.91627f"),
            ("huge h row", "1273.849f, -796.2778f, 48.9364281f"),
        ],
        "ioc_c": [
            ("destroy fn", "BattlegroundIsleOfConquest::DestroyGate"),
            ("honor", "RewardHonorToTeam(GetBonusHonorFromKill(8)"),
            ("text front", "BG_IC_TEXT_FRONT_GATE_HORDE_DESTROYED"),
            ("respawn bombs", "seaforiumBombs->SetRespawnTime(10)"),
            ("grid", "GetCreatureListWithEntryInGrid(cannons, "
                     "NPC_ALLIANCE_GUNSHIP_CANNON, 150.0f)"),
            ("siege timer reset", "siegeEngineWorkshopTimer = "
                                  "WORKSHOP_UPDATE_TIME"),
            ("spawn demo", "AddCreature(NPC_DEMOLISHER, type, "
                           "nodePoint->faction,"),
            ("spawn siege", "AddCreature((nodePoint->faction == "
                            "TEAM_ALLIANCE ? NPC_SIEGE_ENGINE_A : "
                            "NPC_SIEGE_ENGINE_H), siegeType"),
            ("transport", "CreateTransport(GO_HORDE_GUNSHIP"),
            ("door open", "DoorOpen((player->GetBGTeamId() == "
                          "TEAM_ALLIANCE ? BG_IC_GO_HORDE_KEEP_PORTCULLIS"),
            ("epgd", "EventPlayerDamagedGO(Player* /*player*/, "
                     "GameObject* /*go*/, uint32 /*eventType*/)"),
        ],
        "zone": [
            ("garage", "npc_four_car_garage"),
            ("credit demo", "SPELL_DRIVING_CREDIT_DEMOLISHER"),
            ("boss spells", "SPELL_MORTAL_STRIKE     = 58460"),
            ("boss spells2", "SPELL_CRUSHING_LEAP     = 68506"),
            ("boss spells3", "SPELL_DAGGER_THROW      = 67280"),
            ("boss spells4", "SPELL_RAGE              = 66776"),
        ],
        "cts": [
            ("demo bar", "(34775,0,67440,10314)"),
            ("demo bar2", "(34775,1,67441,10314)"),
            ("siege bar", "(34776,0,67796,10314)"),
            ("siege bar2", "(34776,1,67797,10314)"),
            ("siege h bar", "(35069,1,67797,10314)"),
            ("cat bar", "(34793,0,66218,10314)"),
            ("cat bar2", "(34793,1,66296,10314)"),
            ("glaive bar", "(34802,0,66456,10314)"),
            ("glaive bar2", "(34802,1,67195,10314)"),
            ("glaive h bar", "(35273,0,67034,10314)"),
            ("gun a bar", "(34929,0,66518,10314)"),
            ("gun h bar", "(34935,0,66529,10314)"),
            ("kc bar", "(34944,0,67452,10314)"),
            ("kc bar2", "(34944,1,66541,10314)"),
        ],
        "ct": [
            ("demo row", "(34775,35415,0,0,0,0,'Demolisher'"),
            ("siege row", "(34776,35431,0,0,0,0,'Siege Engine'"),
            ("cat row", "(34793,35413,0,0,0,0,'Catapult'"),
            ("glaive row", "(34802,35419,0,0,0,0,'Glaive Thrower'"),
            ("kc row", "(34944,35429,0,0,0,0,'Keep Cannon'"),
            ("turret script", "'npc_isle_of_conquest_turret',10314)"),
            ("capt script", "'npc_ioc_gunship_captain'"),
            ("vehicle npcflag", "vehichleCursor"),
        ],
        "got": [
            ("gate h row", "600000,0,0,0,0,0,0,0,0,22079,0,0,0,61,"),
            ("gate a row", "600000,0,0,0,0,0,0,0,0,22082,0,0,0,62,"),
            ("bomb row", "(195237,10,8976,'Seaforium Bombs'"),
            ("bomb spell", ",0,0,0,0,0,0,0,0,66265,"),
            ("huge row", "(195332,10,8976,'Huge Seaforium Bombs'"),
            ("huge spell", "1,0,1,0,0,0,0,66669,"),
            ("ship a", "(195121,15,9002,'Alliance Gunship'"),
            ("ship h", "(195276,15,9001,'Horde Gunship'"),
            ("gate names", "'Horde Gate','','','',1,1,0,0,0,0,600000"),
        ],
        "vta": [
            ("acc a1", "(34776,34778,1,1,"),
            ("acc a2", "(34776,34778,2,1,"),
            ("acc a7", "(34776,34777,7,1,"),
            ("acc h1", "(35069,36356,1,1,"),
            ("acc h7", "(35069,36355,7,1,"),
        ],
        "ssn": [
            ("launch", "(66218,'spell_ioc_launch')"),
        ],
    }
    corpora_map = {k: corpora.get(k, "") for k in token_map}
    return source_stage(corpora_map, token_map)


def _rows_h(ioc_h):
    """Gate + vehicle + bomb rows parsed as raw strings from the header."""
    out = {}
    for m in re.finditer(
            r"\{BG_IC_GO_(ALLIANCE|HORDE)_GATE_(\d),\s*GO_\w+_GATE_\d,\s*"
            r"([-\d.f]+),\s*([-\d.f]+),\s*([-\d.f]+),\s*([-\d.f]+)\}",
            ioc_h):
        out["gate %s%s" % (m.group(1), m.group(2))] = tuple(
            v.rstrip("f") for v in m.group(3, 4, 5, 6))
    for m in re.finditer(
            r"\{(\d+\.\d+f),\s*(-\d+\.\d+f),\s*(\d+\.\d+f),\s*"
            r"(-?\d+\.\d+f)\},\s*// (Demolisher|Siege Engine|"
            r"Glaive Throwers|Catapults)", ioc_h):
        key = "veh %s %s" % (m.group(5),
                             "0" if "0" not in out else len(
                                 [k for k in out
                                  if k.startswith("veh %s" % m.group(5))]))
        out[key] = tuple(v.rstrip("f") for v in m.group(1, 2, 3, 4))
    for m in re.finditer(
            r"\{(\d+\.\d+f),\s*(-\d+\.\d+f),\s*(\d+\.\d+f),\s*"
            r"(-?\d+\.\d+f)\},\s*// Demolisher", ioc_h):
        pass
    kc = re.findall(r"TEAM_ALLIANCE, (\d+\.\d+f), (-?\d+\.\d+f), "
                    r"(\d+\.\d+f), (-?\d+\.\d+f)\}, // \d+", ioc_h)
    kch = re.findall(r"TEAM_HORDE, (\d+\.\d+f), (-?\d+\.\d+f), "
                     r"(\d+\.\d+f), (-?\d+\.\d+f)\}, // \d+", ioc_h)
    out["kc_a"] = [tuple(v.rstrip("f") for v in t) for t in kc]
    out["kc_h"] = [tuple(v.rstrip("f") for v in t) for t in kch]
    return out


def stage4(text, corpora, probe=False):
    if probe:
        text = text.replace("(628, 351.615, -762.75, 48.9162)",
                            "(628, 352.615, -762.75, 48.9162)")
    flat = norm(text)
    lines, fails = [], []
    ioc_h, ioc_c = corpora["ioc_h"], corpora["ioc_c"]

    # gate rows raw-compare
    gots = re.findall(
        r"\{BG_IC_GO_((?:ALLIANCE|HORDE)_GATE_\d), GO_\w+_GATE_\d, "
        r"([-\d.f]+), ([-\d.f]+), ([-\d.f]+), ([-\d.f]+)\}",
        ioc_h)
    ghit = 0
    for name, x, y, z, o in gots:
        want = "(628, %s, %s, %s)" % (x.rstrip("f"), y.rstrip("f"),
                                      z.rstrip("f"))
        ok = want in flat
        ghit += ok
        if not ok:
            fails.append("gate row %s %s" % (name, want))
    lines.append("    gate rows matched: %d/%d" % (ghit, len(gots)))

    # keep cannon rows: sets of raw triples per faction
    kc_pat = (r"BG_IC_NPC_KEEP_CANNON_\d+, NPC_KEEP_CANNON, TEAM_%s, "
              r"(\d+\.\d+f), (-?\d+\.\d+f), (\d+\.\d+f), "
              r"[-\d.f]+\}, // \d+")
    kc_a = re.findall(kc_pat % "ALLIANCE", ioc_h)
    kc_h = re.findall(kc_pat % "HORDE", ioc_h)
    doc_kc = re.findall(r"^\s+(\d+\.\d+|4\d+\.\d+|1\d+\.\d+), "
                        r"(-?\d+\.\d+), (\d+\.\d+)  o ", text, re.M)
    def have(rows):
        n = 0
        for x, y, z in rows:
            want = "%s, %s, %s" % (x.rstrip("f"), y.rstrip("f"),
                                   z.rstrip("f"))
            if want in flat:
                n += 1
        return n
    ha, hh = have(kc_a), have(kc_h)
    lines.append("    keep-cannon rows matched: A %d/%d, H %d/%d"
                 % (ha, len(kc_a), hh, len(kc_h)))
    if ha != len(kc_a) or hh != len(kc_h):
        fails.append("keep-cannon rows")

    # template claims from gameobject_template
    gate_tpl = {}
    for line in corpora["got"].splitlines():
        m = re.match(r"\((\d+),33,", line)
        if m and int(m.group(1)) in GATE_IDS:
            row = line.rstrip(",;")
            gate_tpl[int(m.group(1))] = row
    tok = 0
    for gid, row in gate_tpl.items():
        m = re.search(r"600000,0,0,0,0,0,0,0,0,(\d+),0,0,0,(\d+),", row)
        if not m:
            fails.append("tpl parse %d" % gid)
            continue
        disp, fac = m.group(1), m.group(2)
        ok = ("Data5=600000" in flat and disp in flat and fac in flat)
        tok += bool(ok)
        if not ok:
            fails.append("tpl %d (%s/%s)" % (gid, disp, fac))
    lines.append("    gate template claims: %d/%d match doc"
                 % (tok, len(gate_tpl)))

    # creature_template_spell map vs doc claims
    want_bars = [
        (34775, 0, 67440), (34775, 1, 67441), (34776, 0, 67796),
        (34776, 1, 67797), (35069, 1, 67797), (34793, 0, 66218),
        (34793, 1, 66296), (34802, 0, 66456), (34802, 1, 67195),
        (35273, 0, 67034), (34929, 0, 66518), (34935, 0, 66529),
        (34944, 0, 67452), (34944, 1, 66541),
    ]
    bar_ok = 0
    for entry, idx, spell in want_bars:
        row = "(%d,%d,%d," % (entry, idx, spell)
        in_src = row in corpora["cts"]
        in_doc = ("spell %d" % spell) in flat
        ok = in_src and in_doc
        bar_ok += ok
        if not ok:
            fails.append("bar %s (src=%s doc=%s)"
                         % (row, in_src, in_doc))
    lines.append("    action-bar spells: %d/%d in template AND doc"
                 % (bar_ok, len(want_bars)))

    # accessory seats
    acc = {"34776": {"1": "34778", "2": "34778", "7": "34777"},
           "35069": {"1": "36356", "2": "36356", "7": "36355"}}
    aok = 0
    for veh, seats in acc.items():
        for seat, npc in seats.items():
            row = "(%s,%s,%s,1," % (veh, npc, seat)
            ok = row in corpora["vta"]
            aok += ok
            if not ok:
                fails.append("accessory %s" % row)
    doc_seats = ("seats 1, 2" in flat and "seat 7" in flat
                 and "34777/34778/36355/36356" in flat)
    lines.append("    siege accessory rows: %d/%d; doc seat claims: %s"
                 % (aok, 6, "yes" if doc_seats else "NO"))
    if not doc_seats:
        fails.append("doc seat claims")

    ok_c, c_lines, missing_c = coord_trace(text, corpora)
    for ln in c_lines:
        if "NOT IN" in ln or "triples traced" in ln:
            lines.append(ln)
    if not ok_c:
        fails.append("coordinate trace: %s" % missing_c[:6])
    probe_txt = text.replace("(628, 750.601, -864.597, 13.4754)",
                             "(628, 751.601, -864.597, 13.4754)")
    ok2, _, _ = coord_trace(probe_txt, corpora)
    probe_ok = (probe_txt != text) and not ok2
    lines.append("    coordinate probe reacts: %s"
                 % ("yes" if probe_ok else "no"))
    if not probe_ok:
        fails.append("coord probe")
    reacts = probe  # doc-tamper path: gate row edited above
    if probe:
        hit_fail = any("gate row" in str(f) for f in fails)
        lines.append("    row check reacts to doc tamper: %s"
                     % ("yes" if hit_fail else "no"))
        if not hit_fail:
            fails.append("row probe")
    return fails, lines


def stage5(text, corpora):
    lines, fails = [], []
    # AC vehicle dbc tables must be empty (doc's negative)
    for key, label in (("vdbc", "vehicle_dbc"),
                       ("vsdbc", "vehicleseat_dbc")):
        n = len(re.findall(r"^\(", corpora[key], re.M))
        ok = n == 0
        if not ok:
            fails.append("%s has %d data rows" % (label, n))
        lines.append("    %s data rows: %d (need 0)" % (label, n))
    # LC folder holds only isle_of_conquest.cpp
    import subprocess
    res = subprocess.run(
        ["gh", "api", "repos/%s/contents/src/server/scripts/Northrend/"
         "IsleOfConquest" % LC, "--jq", ".[].name"],
        capture_output=True, text=True)
    names = [x for x in res.stdout.split() if x]
    ok = names == ["isle_of_conquest.cpp"]
    if not ok:
        fails.append("IsleOfConquest folder = %s" % names)
    lines.append("    LC IsleOfConquest folder files: %s (need only "
                 "isle_of_conquest.cpp)" % names)
    # EventPlayerDamagedGO is empty
    m = re.search(r"EventPlayerDamagedGO\(Player\*[^{]*\{([^}]*)\}",
                  corpora["ioc_c"])
    ok = m is not None and m.group(1).strip() == ""
    if not ok:
        fails.append("EventPlayerDamagedGO not empty/absent")
    lines.append("    EventPlayerDamagedGO body empty: %s"
                 % ("yes" if ok else "NO"))
    # sanity: templates present
    ok = ("(34775," in corpora["ct"] and "(195494,33," in corpora["got"]
          and "(66218,'spell_ioc_launch')" in corpora["ssn"])
    if not ok:
        fails.append("template sanity")
    lines.append("    AC rows present (34775/195494/66218): %s"
                 % ("yes" if ok else "NO"))
    probes = [("navmesh confirmed", "no navmesh confirmed"),
              ("verified by direct inspection", "no direct inspection")]
    for extra, key in probes:
        f, _ = run_static(text + "\n%s.\n" % extra)
        r = key in f
        lines.append("    injection probe (%s):%s"
                     % (extra[:26], " detected" if r else " NOT DETECTED"))
        if not r:
            fails.append("probe %s" % key)
    stripped = text.replace("unverified", "verified")
    f, _ = run_static(stripped)
    r = "unverified count" in f
    lines.append("    injection probe (unverified stripped):%s"
                 % (" detected" if r else " NOT DETECTED"))
    if not r:
        fails.append("unverified probe")
    res = subprocess.run(
        ["gh", "api", "-X", "GET",
         "repos/azerothcore/azerothcore-wotlk/contents/data/sql/"
         "DoesNotExist.sql"],
        capture_output=True, text=True)
    absent = res.returncode != 0
    lines.append("    control: bogus AC path 404:                  %s"
                 % ("yes" if absent else "NO"))
    if not absent:
        fails.append("404 control")
    return fails, lines


def main():
    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()
    print("=" * 68)
    print("AUDIT: Vehicles_Isle_of_Conquest_COMPLETED.txt (Vehicles 1)")
    print("=" * 68)

    fails1, lines1 = run_static(text)
    total1 = len(STATIC_CHECKS) + len(NEGATIVE_CHECKS) + 1
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
    for k, p in RAW_FILES.items():
        corpora[k] = gh_raw(AC, p)
    for k, p in SMALL_FILES.items():
        corpora[k] = gh_content(AC, p)
    missing = [k for k, v in corpora.items() if not v]
    if missing:
        print("    CORPUS FETCH FAILED: %s" % missing)
        return 1
    ok3, lines3 = stage3(corpora)
    for ln in lines3:
        print(ln)
    if not ok3:
        print("    SOURCE CROSS-CHECK FAILED")
    probe_undetected = mutation_probe(
        corpora, {"cts": [("demo bar", "(34775,0,67440,10314)")]},
        lambda t: t.replace("(34775,0,67440,10314)",
                            "(34775,0,67441,10314)"))
    print("    reaction to tampered source (verified): %s"
          % ("yes" if probe_undetected == [] else "NO"))
    if probe_undetected != []:
        ok3 = False

    print("\n[4] Derived values recomputed from source bodies")
    fails4, lines4 = stage4(text, corpora)
    for ln in lines4:
        print(ln)
    probe_fails, probe_lines = stage4(text, corpora, probe=True)
    for ln in probe_lines:
        if "reacts" in ln:
            print(ln)
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
