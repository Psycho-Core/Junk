#!/usr/bin/env python3
"""Audit: Vehicles_Strand_of_the_Ancients_COMPLETED.txt (Battleground_Vehicles 2)."""

import re
import sys

sys.path.insert(0, ".")
from audit_common import (gh_content, gh_raw, source_stage, mutation_probe,
                          coord_trace)

DOC = ("# Ai Research prompts/Battleground_Vehicles/"
       "Vehicles_Strand_of_the_Ancients_COMPLETED.txt")
LC = "Titans-Project/LegionCore-Reforged"
AC = "azerothcore/azerothcore-wotlk"
B = "data/sql/base/db_world/"
FILES = {
    "sota_h": "src/server/game/Battlegrounds/Zones/"
              "BattlegroundStrandOfTheAncients.h",
    "sota_c": "src/server/game/Battlegrounds/Zones/"
              "BattlegroundStrandOfTheAncients.cpp",
    "lc_godata": "src/server/game/Entities/GameObject/GameObjectData.h",
    "spell_generic": "src/server/scripts/Spells/spell_generic.cpp",
    "go_scripts": "src/server/scripts/World/go_scripts.cpp",
}
AC_FILES = {
    "ac_bg": "src/server/game/Battlegrounds/Zones/BattlegroundSA.cpp",
    "ac_godata": "src/server/game/Entities/GameObject/GameObjectData.h",
}
RAW_LC = {
    "lc_go": "src/server/game/Entities/GameObject/GameObject.cpp",
}
RAW_AC = {
    "ct": B + "creature_template.sql",
    "got": B + "gameobject_template.sql",
    "ctext": B + "creature_text.sql",
    "ac_go": "src/server/game/Entities/GameObject/GameObject.cpp",
}
SMALL_FILES = {
    "cts": B + "creature_template_spell.sql",
    "sls": B + "spell_linked_spell.sql",
    "ssn": B + "spell_script_names.sql",
    "vdbc": B + "vehicle_dbc.sql",
    "vsdbc": B + "vehicleseat_dbc.sql",
}
GATE_IDS = [190722, 190723, 190724, 190726, 190727, 192549]
UNVERIFIED_MIN = 25


def norm(s):
    return re.sub(r"\s+", " ", s)


STATIC_CHECKS = [
    ("heading", "=== VEHICLES - STRAND OF THE ANCIENTS - BFA 8.3.7 "
                "(TRINITYCORE) - COMPLETED ==="),
    ("numbering", "Prompt 2 of the Battleground_Vehicles set (Strand of "
                  "the Ancients, map 607)"),
    ("done", "DONE - step 2 of the Battleground_Vehicles set complete"),
    ("src LC", "LegionCore-Reforged"),
    ("src AC", "AzerothCore (AC) db_world base SQL"),
    ("src wiki", "warcraft.wiki.gg \"Strand of the Ancients\""),
    ("src spells", "wowhead spell pages"),
    ("src acbg", "AC BattlegroundSA.cpp"),
    ("removed", "removed in patch 8.0.1"),
    ("round len", "BG_SA_ROUNDLENGTH = 600 * IN_MILLISECONDS"),
    ("warmup", "BG_SA_WARMUPLENGTH = 120 * 1000"),
    ("boat start", "BG_SA_BOAT_START = 60 * 1000"),
    ("r2 timer", "second-round warmup 60 s"),
    ("texts", "broadcast texts 29448 (one minute) and 29449"),
    ("coin", "urand(0,1) ? ALLIANCE : HORDE"),
    ("att start", "(607, 2682.936, -830.368, 30.0) o 2.895"),
    ("att start2", "(607, 2577.003, 980.261, 30.0) o 0.807"),
    ("landing", "(607, 1600.381, -106.263, 8.8745) o 3.78"),
    ("def start", "(607, 1209.7, -65.16, 70.1) o 0.0"),
    ("relic", "(607, 836.5, -108.8, 120.219) o 0.0"),
    ("relic cond", "Ancient Gate (192549), Yellow Moon (190727)"),
    ("relic cond2", "Green Emerald OR Blue Sapphire"),
    ("relic team", "the clicker is on the attacking team"),
    ("struct d0", "Data0 ="),
    ("struct d5", "intactNumHits, Data5 = damagedNumHits, Data9 = "
                  "DamagedEvent,"),
    ("struct d14", "Data14 = DestroyedEvent; AC GameObject.cpp: starting "
                   "health ="),
    ("health rule", "Data0 + Data5, DAMAGED state when health <= Data5, "
                    "DESTROYED"),
    ("gate owner", "faction-set to the DEFENDERS each setup"),
    ("gate g label", "Gate 1 - Green Emerald: gameobject 190722"),
    ("gate g pos", "(607, 1411.57, 108.163, 28.692) o 5.441"),
    ("gate g hp", "health 2000 + 9000 = 11000; DamagedEvent 19041, "
                  "DestroyedEvent 19046"),
    ("gate g row", "(190722,33,7906,'Gate of the Green Emerald',"),
    ("gate g row2", "'','','',1,2000,0,0,0,1,9000,1,0,0,19041,1,1,0,0,19046"),
    ("gate b label", "Gate 2 - Blue Sapphire: gameobject 190724"),
    ("gate b pos", "(607, 1431.3413, -219.437, 30.893) o 0.9736"),
    ("gate b hp", "health 2000 + 9000 = 11000; events 19040 / 19045"),
    ("gate b row", "(190724,33,7906,'Gate of the Blue Sapphire',"),
    ("gate p label", "Gate 3 - Purple Amethyst: gameobject 190723"),
    ("gate p pos", "(607, 1214.681, 81.21, 53.413) o 5.745"),
    ("gate p hp", "health 4000 + 9000 = 13000; events 19043 / 19048"),
    ("gate p row", "(190723,33,7906,'Gate of the Purple Amethyst',"),
    ("gate r label", "Gate 4 - Red Sun: gameobject 190726"),
    ("gate r pos", "(607, 1227.667, -212.555, 55.372) o 0.5023"),
    ("gate r hp", "health 4000 + 9000 = 13000; events 19042 / 19047"),
    ("gate r row", "(190726,33,7906,'Gate of the Red Sun',"),
    ("gate y label", "Gate 5 - Yellow Moon: gameobject 190727"),
    ("gate y pos", "(607, 1055.452, -108.1, 82.134) o 0.034"),
    ("gate y hp", "health 5000 + 9000 = 14000; events 19044 / 19049"),
    ("gate y row", "(190727,33,7906,'Gate of the Yellow Moon',"),
    ("gate a label", "Gate 6 - Chamber of Ancient Relics"),
    ("gate a pos", "(607, 878.555, -108.2, 117.845) o 0.0"),
    ("gate a hp", "health 5000 + 5000 = 10000 (the lowest total of the six"),
    ("gate a events", "events 19836 / 19837"),
    ("gate a row", "(192549,33,8165,'Chamber of Ancient Relics',"),
    ("wiki rule", "The gates can only be brought down through"),
    ("blast dmg", "siege damage 4500 in a 10-yard radius"),
    ("hurl dmg", "Hurl Boulder 52338 (see 3a): 1000"),
    ("ram dmg", "Ram 60206 (see 3a): 1500 siege"),
    ("no player dmg", "a gate hook for them) - unverified"),
    ("no tower dmg", "NOT gate-damaging weapons: Antipersonnel Cannon "
                     "rockets"),
    ("texts list", "under attack 1 Blue, 2 Green, 3 Red,"),
    ("trigger rows", "(607, 1453.49, -250.453, 30.896) o 4.2883"),
    ("ws values", "1 = OK, 2 = DAMAGED, 3 = DESTROYED"),
    ("dg sigil", "DelObject(gateId + 9)"),
    ("dg sigil g", "(607, 1414.054, 106.72, 41.442) o 5.441"),
    ("dg sigil y", "(607, 1060.63, -107.8, 94.7) o 0.034"),
    ("dg sigil p", "(607, 1217.8, 79.532, 66.58) o 5.745"),
    ("dg honor", "GetBonusHonorFromKill(1)"),
    ("dg pair", "the FIRST gate of a pair"),
    ("unlock outer", "(x < 1371 and z < 35 and y > 100) or (x < 1382 and "
                     "z < 35 and y < -100)"),
    ("unlock mid", "Red or Purple destroyed -> rows with 68 < z < 73"),
    ("unlock yellow", "Yellow destroyed -> rows with 78 < z < 87"),
    ("flag unlock", "West (LEFT) and East (RIGHT) capturable flags"),
    ("central unlock", "the South (CENTRAL) flag additionally needs Red OR "
                       "Purple destroyed"),
    ("relic select", "loses GO_FLAG_NOT_SELECTABLE (see 1)"),
    ("no towers", "No towers exist on Strand of the Ancients"),
    ("portal row", "(192819,22,8244,'Defender\\'s Portal'"),
    ("portal spell", "spell Data0 = 54640"),
    ("portal p1", "(607, 1468.380005, -225.798996, 30.896200) o 0.0 (blue)"),
    ("portal y", "(607, 1065.260010, -89.79501, 81.073402) o 0.0 (yellow)"),
    ("portal r", "(607, 1255.569946, -233.548996, 56.43699) o 0.0 (red)"),
    ("portal wiki", "attackers cannot use them"),
    ("no wall obj", "no separate wall objects are damageable"),
    ("demo entry", "creature 28781 (both factions"),
    ("demo flag", "npcflag 16777216 (VEHICLE), type 9, faction 168"),
    ("demo hm", "HealthModifier 14.8148, VehicleId 158"),
    ("demo spawn1", "(607, 1611.597656, -117.270073, 8.719355)"),
    ("demo o1", "o 2.513274"),
    ("demo spawn2", "(607, 1618.047729, 61.424641, 7.248210) o 3.979351"),
    ("demo spawn3", "(607, 1371.055786, -317.071136, 35.007359)"),
    ("demo spawn4", "(607, 1353.139893, 223.745438, 35.265411) o 4.343684"),
    ("demo respawn param", "respawntime = 600"),
    ("demo faction", "dem->setFaction(BgFactions[Attackers])"),
    ("demo warmup", "DemolisherStartState"),
    ("demo seats wiki", "up to 3 passengers as well as a driver"),
    ("demo seats guide", "1 driver and 2 passengers"),
    ("demo cts", "(28781,1,60206,12340)"),
    ("hurl spell", "spell 52338 \"Hurl Boulder\" - range: unlimited"),
    ("hurl cd", "cooldown 2 s (wiki and wowclassicdb)"),
    ("hurl siege", "1000 siege damage, 10 yd radius"),
    ("ram spell", "spell 60206 \"Ram\" - range 15 yd (Shorter), instant"),
    ("ram cd", "cooldown 4 s, GCD 1.5 s (wowhead)"),
    ("ram siege", "1500 siege damage to buildings (wowhead effect #3)"),
    ("no repair", "Repair: no repair mechanic exists in the sources for SOTA"),
    ("respawn 30", "DemoliserRespawnList[i] = now + 30000"),
    ("respawn place", "Relocate()s the unit back to ITS slot row"),
    ("cannon entry", "Antipersonnel Cannon (wall turret) - creature 27894"),
    ("cannon flag", "npcflag 16777216 (VEHICLE), type 9, faction 614"),
    ("cannon hm", "Modifier 8.64198, VehicleId 160 (DBC, unreadable)"),
    ("cannon pair g", "(607, 1436.429, 110.05, 41.407) o 5.4"),
    ("cannon pair b", "(607, 1422.115, -196.433, 42.1825)"),
    ("cannon pair p", "(607, 1236.213, 92.287, 64.965) o 5.751"),
    ("cannon pair r", "(607, 1232.345, -187.517, 66.945) o 0.45"),
    ("cannon pair y", "(607, 1068.693, -86.951, 93.81) o 0.02"),
    ("cannon spell", "spell 49872 \"Rocket"),
    ("cannon range", "range 10-70 yd, instant, cooldown 2 s, missile radius"),
    ("cannon wiki", "60,000 HP at level 80"),
    ("cannon not gate", "it does NOT damage gates"),
    ("cannon bomb", "Bombs can't be destroyed by Turrets"),
    ("bomb row", "(190753,22,8582,'Seaforium Bomb'"),
    ("bomb spell", "spell Data0 = 52415, Data1 charges = 1,"),
    ("bomb mount", "Data3 allowMounted = 1 (pick up while mounted = wiki)"),
    ("carry", "\"Carrying Seaforium\" (wowhead: interact range 5 yd"),
    ("sls add", "(52415, 52418, 'Carrying Seaforium - Add')"),
    ("sls rm", "(52410, -52418, 'Carrying Seaforium - Remove')"),
    ("place spell", "spell 52410 \"Place Seaforium"),
    ("place time", "2 s cast (wiki and wowhead), self range"),
    ("charge row", "(190752,6,8582,'Massive Seaforium Charge'"),
    ("charge fields", "Data3 spellId = 52408, Data4 type = 2"),
    ("charge script", "'go_massive_seaforium_charge'"),
    ("trap comment", "bomb casts on spawn"),
    ("arm ac", "if (goInfo->trap.type == 2) m_cooldownTime ="),
    ("arm hardcode", "now + 10 s // Hardcoded tooltip value"),
    ("arm lc", "LC GameObject.cpp the same (+10 with the same comment)"),
    ("bomb away", "Type 2 - Bomb (will go away after casting its"),
    ("blast spell", "Spell 52408 \"Seaforium Blast\" (wowhead): instant"),
    ("blast effects", "effect 1 Fire damage in a 10 yd radius + effect 2 "
                      "siege damage 4500"),
    ("disarm wiki", "2 s channel, interruptible like a capture point"),
    ("disarm core", "OnGossipHello -> SetLootState(GO_JUST_DEACTIVATED)"),
    ("piles 68", "Pile spawns: 68 objects of entry 190753"),
    ("pile resp", "RESPAWN_ONE_DAY respawn"),
    ("pile unselect", "spawned GO_FLAG_NOT_SELECTABLE"),
    ("pile A", "Pile A - north dock pile (selectable at round start, 11 rows)"),
    ("pile B", "Pile B - south dock pile (selectable at round start, 11 rows)"),
    ("pile C", "Pile C - north factory, west cluster (unlocks with Green or"),
    ("pile D", "Pile D - north factory, east cluster (7 rows; the literal"),
    ("pile E", "Pile E - south factory, west cluster (unlocks with Green or"),
    ("pile F", "Pile F - south factory, east cluster (5 rows; 2 never pass"),
    ("pile G", "Pile G - inner-wall terrace near the south (central)"),
    ("pile H", "Pile H - west of the relic chamber"),
    ("pile A row", "(607, 1592.49, 47.5969, 7.52271)  o 4.63218"),
    ("never 1", "(607, 1371.41, 194.028, 31.5107)   o 0.753095   NEVER"),
    ("never 2", "(607, 1382.75, -286.354, 32.4099)  o 1.00442    NEVER"),
    ("never f", "2 never pass"),
    ("lc arming", "LC GameObject.cpp the same (+10 with the same comment)"),
    ("ship a1", "'The Graceful Maiden'"),
    ("ship h1", "'The Coffin Carrier'"),
    ("ship a2", "'The Frostbreaker'"),
    ("ship h2", "'The Blightbringer'"),
    ("ship missing", "absent from the AC dump"),
    ("ship off", "z offset -3.750"),
    ("ship move", "SetMoving(true)"),
    ("aura 12438", "spell 12438 before the ships move"),
    ("aura 68377", "RemovePlayer strips 68377"),
    ("kanrethad", "(607, 841.921, -134.194, 196.838) o 6.23082"),
    ("sales1", "(607, 1348.644165, -298.786469, 31.080130) o 1.710423"),
    ("sales2", "(607, 1358.191040, 195.527786, 31.018187) o 4.171337"),
    ("text1", "vehicle emporium is open for business!"),
    ("text2", "vehicle shop is open for business!"),
    ("gy entries", "1350 beach (attackers' fixed respawn)"),
    ("gy list", "1349 defender last-resort, 1347 East capturable,"),
    ("gy guard", "defenders can never re-capture"),
    ("flag w", "(607, 1309.192017, 9.416233, 30.893402) o 1.518436"),
    ("flag e", "(607, 1338.859253, -153.327316, 30.895077)"),
    ("flag s", "(607, 1215.108032, -65.715767, 70.084267)"),
    ("banners a", "Alliance 191310 (central), 191308 (left),"),
    ("banners h", "Horde 191309/191307/191305"),
    ("gy dbc", "client DBC and are not in readable SQL - unverified"),
    ("seq header", "4. SEQUENCE A GOOD TEAM FOLLOWS"),
    ("seq land", "land at (607, 1600.381, -106.263, 8.8745);"),
    ("seq drive b", "toward Blue gate front"),
    ("seq drive g", "toward Green gate front (607, 1411.57,"),
    ("seq fire", "keep moving while defenders aim"),
    ("seq pile H", "pile H does not open until Yellow itself is down"),
    ("seq flags", "channel West flag (607, 1309.192017, 9.416233, "
                  "30.893402) and/or"),
    ("seq red", "(607, 1227.667, -212.555, 55.372) and Purple front"),
    ("seq def pre", "man the Green + Blue turret pairs immediately"),
    ("seq def beach", "priority is killing the beach demolishers before "
                      "they reach the wall"),
    ("seq portal", "fallback through the Defender's Portals behind each "
                   "gate"),
    ("seq last gy", "the last resort yard 1349"),
    ("seq round2", "everything is rebuilt (gates full, piles re-flagged"),
    ("solo hdr", "Solo-capable (mechanic needs only 1 player)"),
    ("duo hdr", "Needs two or more (mechanic or hard tactics)"),
    ("solo drive", "Drive a demolisher: driver alone has both weapons"),
    ("solo plant", "Plant: the carrier's button is spell 52410"),
    ("duo disarm", "Keep a planted charge alive"),
    ("duo split", "The \"right\" split for bots beyond the above: unverified"),
    ("neg era", "VerifiedBuild 12340"),
    ("neg only2", "spawns exactly two creature types as machines"),
    ("neg wide", "No catapults, siege engines, glaive throwers, gunships"),
    ("neg dbc", "vehicle_dbc.sql and vehicleseat_dbc.sql contain no data "
                "rows"),
    ("neg folder", "LC ships no dedicated SOTA script folder"),
    ("neg scripts", "spell_sa_place_seaforium"),
    ("neg gen", "spell_gen_seaforium_blast"),
    ("neg gos", "go_massive_seaforium_charge"),
    ("neg links", "casts 226090 Horde / 226094 Alliance on hit"),
    ("neg credit", "achievement credit 60937"),
    ("neg never", "The five seaforium rows listed NEVER in 3c stay locked all"),
    ("neg fire", "Seaforium Blast also carries a 10 yd Fire damage effect"),
    ("unver hdr", "7. UNVERIFIED LIST (consolidated)"),
    ("unver gy", "Graveyard spirit positions for entries 1346-1350 (DBC only)"),
    ("unver disarm", "Seaforium disarm spell id and how the 2 s retail "
                     "channel"),
    ("unver aura", "Names of spells 12438 and 68377"),
    ("unver ships", "Ship templates 208000 / 208001"),
    ("unver ram", "Which retail patch removed the demolisher Ram 60206"),
    ("unver links", "LC spell ids 226090/226094"),
]

NEGATIVE_CHECKS = [
    ("no estimated coordinate", "estimated coordinate"),
    ("no navmesh confirmed", "navmesh confirmed"),
    ("no direct inspection", "verified by direct inspection"),
    ("no todo", "TODO"),
    ("no fixme", "FIXME"),
    ("no damageers", "damageers"),
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
    ("numbering", "Prompt 2 of the Battleground_Vehicles set",
     "Prompt 7 of the Battleground_Vehicles set"),
    ("done", "DONE - step 2 of the Battleground_Vehicles set complete",
     "DONE - step 2 of the Battleground_Vehicles set is done"),
    ("round len", "600 * IN_MILLISECONDS", "601 * IN_MILLISECONDS"),
    ("boat start", "BG_SA_BOAT_START = 60 * 1000",
     "BG_SA_BOAT_START = 61 * 1000"),
    ("texts", "29448 (one minute) and 29449",
     "29447 (one minute) and 29449"),
    ("coin", "urand(0,1) ? ALLIANCE : HORDE",
     "urand(0,2) ? ALLIANCE : HORDE"),
    ("landing", "(607, 1600.381, -106.263, 8.8745) o 3.78",
     "(607, 1600.381, -106.263, 8.8745) o 3.79"),
    ("def start", "(607, 1209.7, -65.16, 70.1) o 0.0",
     "(607, 1209.7, -65.16, 70.2) o 0.0"),
    ("relic", "(607, 836.5, -108.8, 120.219)",
     "(607, 836.5, -108.8, 120.220)"),
    ("gate g pos", "(607, 1411.57, 108.163, 28.692) o 5.441",
     "(607, 1411.57, 108.163, 28.693) o 5.441"),
    ("gate g hp", "2000 + 9000 =\n       11000; DamagedEvent 19041",
     "2000 + 9000 =\n       11001; DamagedEvent 19041"),
    ("gate b hp", "events 19040 / 19045", "events 19040 / 19046"),
    ("gate p pos", "(607, 1214.681, 81.21, 53.413)",
     "(607, 1214.681, 81.22, 53.413)"),
    ("gate y hp", "5000 + 9000 = 14000", "5000 + 9000 = 14001"),
    ("gate a hp", "the lowest total of the six", "the highest total of the six"),
    ("gate a ev", "events 19836 / 19837", "events 19836 / 19838"),
    ("gate g row", "1,2000,0,0,0,1,9000,1,0,0,19041,1,1,0,0,19046",
     "1,2000,0,0,0,1,9000,1,0,0,19041,1,1,0,0,19047"),
    ("hurl dmg", "1000\n         siege damage, 10 yd radius",
     "1001\n         siege damage, 10 yd radius"),
    ("ram dmg", "1500 siege\n         damage to buildings",
     "1501 siege\n         damage to buildings"),
    ("honor", "GetBonusHonorFromKill(1)", "GetBonusHonorFromKill(2)"),
    ("sigil g", "(607, 1414.054, 106.72, 41.442)",
     "(607, 1414.054, 106.72, 41.443)"),
    ("unlock outer", "z < 35 and y > 100)",
     "z < 35 and y > 101)"),
    ("unlock mid", "68 < z < 73", "68 < z < 74"),
    ("unlock yellow", "78 < z < 87", "78 < z < 88"),
    ("flag w", "(607, 1309.192017, 9.416233, 30.893402)",
     "(607, 1309.192017, 9.416233, 30.893403)"),
    ("portal spell", "54640", "54641"),
    ("portal pos", "(607, 1468.380005, -225.798996, 30.896200)",
     "(607, 1468.380005, -225.798996, 30.896201)"),
    ("demo row", "creature 28781 (both factions",
     "creature 28782 (both factions"),
    ("demo hm", "HealthModifier 14.8148, VehicleId 158",
     "HealthModifier 14.8149, VehicleId 158"),
    ("demo o1", "o 2.513274", "o 2.513275"),
    ("demo spawn3", "(607, 1371.055786, -317.071136,\n         35.007359)",
     "(607, 1371.055786, -317.071136,\n         35.007360)"),
    ("respawn param", "respawntime = 600", "respawntime = 601"),
    ("demo seats wiki", "up to 3\n       passengers as well as a driver",
     "up to 4\n       passengers as well as a driver"),
    ("demo seats guide", 'guide: "1\n       driver and 2 passengers',
     'guide: "1\n       driver and 3 passengers'),
    ("hurl spell", "spell 52338 \"Hurl Boulder\"", "spell 52339 \"Hurl Boulder\""),
    ("hurl cd", "cooldown 2 s (wiki and\n         wowclassicdb",
     "cooldown 3 s (wiki and\n         wowclassicdb"),
    ("ram spell", "spell 60206 \"Ram\"", "spell 60207 \"Ram\""),
    ("ram cd", "cooldown 4 s, GCD 1.5 s (wowhead)",
     "cooldown 5 s, GCD 1.5 s (wowhead)"),
    ("respawn30", "now + 30000", "now + 30001"),
    ("cannon row", "Antipersonnel Cannon (wall turret) - creature 27894",
     "Antipersonnel Cannon (wall turret) - creature 27895"),
    ("cannon hm", "Modifier 8.64198, VehicleId 160",
     "Modifier 8.64199, VehicleId 160"),
    ("cannon pos", "(607, 1436.429, 110.05, 41.407)",
     "(607, 1436.429, 110.06, 41.407)"),
    ("cannon hp", "turret has 60,000\n       HP at level 80",
     "turret has 61,000\n       HP at level 80"),
    ("bomb row", "(190753,22,8582,'Seaforium Bomb'",
     "(190753,22,8582,'Seaforium Bombs'"),
    ("bomb spell", "spell Data0 = 52415, Data1 charges = 1,",
     "spell Data0 = 52416, Data1 charges = 1,"),
    ("bomb mount", "Data3 allowMounted = 1", "Data3 allowMounted = 0"),
    ("place spell", "spell 52410 \"Place Seaforium",
     "spell 52411 \"Place Seaforium"),
    ("charge row", "(190752,6,8582,'Massive Seaforium Charge'",
     "(190752,6,8582,'Massive Seaforium Charges'"),
    ("charge fields", "Data3 spellId = 52408, Data4 type = 2",
     "Data3 spellId = 52409, Data4 type = 2"),
    ("arm hardcode", "now + 10 s // Hardcoded tooltip value",
     "now + 11 s // Hardcoded tooltip value"),
    ("blast effects", "damage 4500 in a 10 yd radius",
     "damage 4501 in a 10 yd radius"),
    ("pile A row", "(607, 1592.49, 47.5969, 7.52271)",
     "(607, 1592.49, 47.5969, 7.52272)"),
    ("never row", "(607, 1371.41, 194.028, 31.5107)",
     "(607, 1371.41, 194.028, 31.5108)"),
    ("pile counts", "selectable at round start, 11 rows",
     "selectable at round start, 12 rows"),
    ("ship row", "'The Coffin Carrier'", "'The Coffin Carriers'"),
    ("ship off", "z offset -3.750", "z offset -3.751"),
    ("sales text", "vehicle emporium is open for business!",
     "vehicle emporiums is open for business!"),
    ("gy list", "1347 East capturable", "1348 East capturable"),
    ("flag s", "1215.108032", "1215.108033"),
    ("sls add", "(52415, 52418, 'Carrying", "(52415, 52419, 'Carrying"),
    ("sls rm", "(52410, -52418, 'Carrying", "(52410, -52417, 'Carrying"),
    ("neg only2", "spawns exactly\n     two creature types as machines",
     "spawns exactly\n     three creature types as machines"),
    ("neg folder", "LC ships no dedicated SOTA script folder",
     "LC ships a dedicated SOTA script folder"),
    ("no towers", "No towers exist on Strand of the Ancients",
     "Towers exist on Strand of the Ancients"),
]


def stage3(corpora):
    token_map = {
        "sota_h": [
            ("gate enum g", "GO_GATE_OF_THE_GREEN_EMERALD"),
            ("gate enum y", "GO_GATE_OF_THE_YELLOW_MOON"),
            ("gate enum b", "GO_GATE_OF_THE_BLUE_SAPPHIRE"),
            ("gate enum r", "GO_GATE_OF_THE_RED_SUN"),
            ("gate enum p", "GO_GATE_OF_THE_PURPLE_AMETHYST"),
            ("gate enum a", "GO_CHAMBER_OF_ANCIENT_RELICS"),
            ("max gates", "MAX_GATES 6"),
            ("ancient ev", "BG_SA_EVENT_ANCIENT_GATE_DESTROYED"),
            ("round len", "600 * IN_MILLISECONDS"),
            ("npc cannon", "NPC_ANTI_PERSONNAL_CANNON"),
            ("npc demo", "NPC_DEMOLISHER_SA"),
            ("gate row g", "1411.57f, 108.163f, 28.692f"),
            ("gate row b", "1431.3413f, -219.437f, 30.893f"),
            ("gate row y", "1055.452f, -108.1f, 82.134f"),
            ("gate row a", "878.555f, -108.2f, 117.845f"),
            ("cannon row1", "1436.429f, 110.05f, 41.407f"),
            ("cannon row10", "1215.11f, 57.772f, 64.739f"),
            ("demo row1", "1611.597656f, -117.270073f, 8.719355f"),
            ("demo row4", "1353.139893f, 223.745438f, 35.265411f"),
            ("bomb count", "BG_SA_MAXOBJ = BG_SA_BOMB+68"),
            ("boat enum", "BG_SA_BOAT_ONE_H"),
            ("gy array", "BG_SA_GYEntries[BG_SA_MAX_GY]"),
            ("gy beach", "1350,"),
            ("text west", "TEXT_WEST_GRAVEYARD_CAPTURED_A"),
            ("text titan", "BG_SA_TEXT_ALLIANCE_CAPTURED_TITAN_PORTAL"),
        ],
        "sota_c": [
            ("destroy fn", "BattlegroundStrandOfTheAncients::DestroyGate"),
            ("honor", "GetBonusHonorFromKill(1)"),
            ("respawn30", "DemoliserRespawnList[i] = GameTime::GetGameTimeMS"
                          "() + 30000"),
            ("sigil del", "DelObject(i + 9)"),
            ("unlock x", "GetPositionX() < 1371.0f"),
            ("unlock z mid", "GetPositionZ() < 73.0f && GetBGObject(i)->"
                             "GetPositionZ() > 68.0f"),
            ("unlock z yellow", "GetPositionZ() < 87.0f && GetBGObject(i)->"
                                "GetPositionZ() > 78.0f"),
            ("unlock z start", "GetPositionZ() < 22.0f"),
            ("gun faction", "gun->setFaction(BgFactions[Attackers ? "
                            "TEAM_ALLIANCE : TEAM_HORDE])"),
            ("demo faction", "dem->setFaction(BgFactions[Attackers])"),
            ("relic select", "GetBGObject(BG_SA_TITAN_RELIC)->RemoveFlag("
                             "GAMEOBJECT_FIELD_FLAGS, GO_FLAG_NOT_SELECTABLE)"),
            ("relic cond", "GateStatus[BG_SA_ANCIENT_GATE] == "
                           "BG_SA_GATE_DESTROYED"),
            ("landing", "player->TeleportTo(607, 1600.381f, -106.263f, "
                        "8.8745f, 3.78f, 0)"),
            ("def start", "{ 1209.7f, -65.16f, 70.1f, 0.0f }"),
            ("boat pick", "boatid = Attackers ? BG_SA_BOAT_ONE_H : "
                          "BG_SA_BOAT_ONE_A"),
            ("spawn demo4", "AddCreature(BG_SA_NpcEntries[BG_SA_DEMOLISHER_4]"),
            ("spawn demo3", "AddCreature(BG_SA_NpcEntries[BG_SA_DEMOLISHER_3]"),
            ("text south", "TEXT_SOUTH_GRAVEYARD_CAPTURED_A"),
            ("recapture", "if (GraveyardStatus[i] == Attackers)"),
            ("flag west", "CaptureGraveyard(BG_SA_LEFT_CAPTURABLE_GY"),
            ("epgd nonempty", "getGateIdFromDamagedOrDestroyEventId(eventType)"),
        ],
        "lc_godata": [
            ("d struct", "GAMEOBJECT_TYPE_DESTRUCTIBLE_BUILDING"),
            ("d health", "uint32 HealthRec;"),
            ("d dmg evt", "uint32 DamagedEvent;"),
            ("d des evt", "uint32 DestroyedEvent;"),
            ("d rebuild", "uint32 RebuildingTime;"),
        ],
        "lc_go": [
            ("trap bomb", "trap.charges == 2"),
            ("hardcode", "Hardcoded tooltip value"),
            ("bomb away", "will go away after casting"),
        ],
        "spell_generic": [
            ("place script", "spell_sa_place_seaforium_charge"),
            ("h spell", "226090"),
            ("a spell", "226094"),
            ("blast script", "spell_gen_seaforium_blast"),
            ("credit", "SPELL_PLANT_CHARGES_CREDIT_ACHIEVEMENT = 60937"),
        ],
        "go_scripts": [
            ("charge script", "go_massive_seaforium_charge"),
            ("deactivate", "SetLootState(GO_JUST_DEACTIVATED)"),
        ],
        "ac_bg": [
            ("ac update", "BattlegroundSA::UpdateDemolisherSpawns"),
            ("ac respawn30", "DemoliserRespawnList[i] = GameTime::"
                             "GetGameTimeMS().count() + 30000"),
            ("ac visible", "Demolisher->SetVisible(true);"),
            ("ac relocate", "Demolisher->Relocate(BG_SA_NpcSpawnlocs"),
        ],
        "ac_godata": [
            ("ac intact", "uint32 intactNumHits;"),
            ("ac damaged", "uint32 damagedNumHits;"),
            ("ac bomb", "bomb casts on spawn"),
        ],
        "ac_go": [
            ("ac init hp", "m_goValue.Building.Health = goinfo->building."
                           "intactNumHits + goinfo->building.damagedNumHits"),
            ("ac dmg state", "m_goValue.Building.Health <= GetGOInfo()->"
                             "building.damagedNumHits"),
            ("ac arm", "+ 10 * IN_MILLISECONDS; // Hardcoded tooltip value"),
            ("go cond", "trap.type == 2"),
        ],
        "got": [
            ("row g", "(190722,33,7906,'Gate of the Green Emerald','','','',"
                      "1,2000,0,0,0,1,9000,1,0,0,19041,1,1,0,0,19046,0,0,0,"
                      "43,0,0,0,21630,0,'','',12340)"),
            ("row b", "(190724,33,7906,'Gate of the Blue Sapphire','','','',"
                      "1,2000,0,0,0,1,9000,1,0,0,19040,1,1,0,0,19045,0,0,0,"
                      "43,0,0,0,21630,0,'','',12340)"),
            ("row p", "(190723,33,7906,'Gate of the Purple Amethyst','','','',"
                      "1,4000,0,0,0,1,9000,1,0,0,19043,1,1,0,0,19048,0,0,0,"
                      "43,0,0,0,21630,0,'','',12340)"),
            ("row r", "(190726,33,7906,'Gate of the Red Sun','','','',"
                      "1,4000,0,0,0,1,9000,1,0,0,19042,1,1,0,0,19047,0,0,0,"
                      "43,0,0,0,21630,0,'','',12340)"),
            ("row y", "(190727,33,7906,'Gate of the Yellow Moon','','','',"
                      "1,5000,0,0,0,1,9000,1,0,0,19044,1,1,0,0,19049,0,0,0,"
                      "43,0,0,0,21630,0,'','',12340)"),
            ("row a", "(192549,33,8165,'Chamber of Ancient Relics','','','',"
                      "1,5000,0,0,0,1,5000,1,0,0,19836,1,1,0,0,19837,0,0,0,"
                      "38,0,0,0,21630,0,'','',12340)"),
            ("row bomb", "(190753,22,8582,'Seaforium Bomb','','','',2,52415,1,"
                         "0,1,1,"),
            ("row charge", "(190752,6,8582,'Massive Seaforium Charge','','','',"
                           "2,1819,0,0,52408,2,"),
            ("row portal", "'Defender\\'s Portal','','','',1,54640,0,0,1,1,"),
            ("ship maiden", "(193182,11,8409,'The Graceful Maiden'"),
            ("ship blight", "(193183,11,8410,'The Blightbringer'"),
            ("ship coffin", "(193184,11,8410,'The Coffin Carrier'"),
            ("ship frost", "(193185,11,8409,'The Frostbreaker'"),
        ],
        "cts": [
            ("bar demo", "(28781,0,52338,12340)"),
            ("bar demo2", "(28781,1,60206,12340)"),
            ("bar cannon", "(27894,0,49872,12340)"),
        ],
        "ct": [
            ("row cannon", "(27894,32795,0,0,0,0,'Antipersonnel Cannon'"),
            ("row demo", "(28781,32796,0,0,0,0,'Battleground Demolisher'"),
            ("ai name", "'NullCreatureAI'"),
        ],
        "sls": [
            ("sls rm", "(52410,-52418,0,'Carrying Seaforium - Remove')"),
            ("sls add", "(52415,52418,0,'Carrying Seaforium - Add')"),
        ],
        "ssn": [
            ("blast bind", "(52408,'spell_gen_seaforium_blast')"),
        ],
        "ctext": [
            ("text spark", "Sparklight\\'s vehicle emporium is open for "
                           "business!"),
            ("text rig", "Rigspark\\'s vehicle shop is open for business!"),
            ("text id1", "(29260,1,0,"),
            ("text id2", "(29262,1,0,"),
        ],
    }
    corpora_map = {k: corpora.get(k, "") for k in token_map}
    return source_stage(corpora_map, token_map)


def _ac_ct_columns(ct_sql):
    m = re.search(r"CREATE TABLE `creature_template`\s*\((.*?)\)\s*ENGINE",
                  ct_sql, re.S)
    cols = []
    for line in m.group(1).splitlines():
        mm = re.match(r"\s*`([^`]+)`", line)
        if mm:
            cols.append(mm.group(1))
    return cols


def _parse_csv_row(line):
    vals, cur, inq, i = [], "", False, 0
    while i < len(line):
        c = line[i]
        if inq:
            if c == "'" and i + 1 < len(line) and line[i + 1] == "'":
                cur += "''"
                i += 2
                continue
            if c == "'":
                inq = False
            else:
                cur += c
        else:
            if c == "'":
                inq = True
            elif c == ",":
                vals.append(cur.strip())
                cur = ""
                i += 1
                continue
            else:
                cur += c
        i += 1
    vals.append(cur.strip())
    return vals


def stage4(text, corpora, probe=False):
    if probe:
        text = text.replace("(607, 1411.57, 108.163, 28.692)",
                            "(607, 1411.67, 108.163, 28.692)")
    flat = norm(text)
    lines, fails = [], []
    sota_h, sota_c = corpora["sota_h"], corpora["sota_c"]

    # gate rows from gameobject_template: hp parts + events + claims
    got_rows = {}
    for line in corpora["got"].splitlines():
        m = re.match(r"\((\d+),33,", line)
        if m and int(m.group(1)) in GATE_IDS:
            got_rows[int(m.group(1))] = line.rstrip(",;")
    tok = 0
    for gid in GATE_IDS:
        row = got_rows.get(gid)
        if not row:
            fails.append("tpl missing %d" % gid)
            continue
        m = re.search(r"'([^']+)','','','',1,(\d+),0,0,0,1,(\d+),1,0,0,"
                      r"(\d+),1,1,0,0,(\d+),", row)
        if not m:
            fails.append("tpl parse %d" % gid)
            continue
        name, intact, damg, devt, revt = (m.group(1), int(m.group(2)),
                                          int(m.group(3)), int(m.group(4)),
                                          int(m.group(5)))
        hp_claim = "%d + %d = %d" % (intact, damg, intact + damg)
        ev_flat = ("DamagedEvent %d, DestroyedEvent %d" % (devt, revt))
        ev_flat2 = ("events %d / %d" % (devt, revt))
        ok = (name in flat and hp_claim in flat and
              (ev_flat in flat or ev_flat2 in flat))
        tok += bool(ok)
        if not ok:
            fails.append("gate claim %d %s" % (gid, hp_claim))
    lines.append("    gate template claims: %d/%d match doc"
                 % (tok, len(GATE_IDS)))

    # gate spawn positions from the header (BG_SA_ObjSpawnlocs[0..5])
    m = re.search(r"BG_SA_ObjSpawnlocs\[BG_SA_MAXOBJ\]\[4\] =\s*\{(.*?)\n\};",
                  sota_h, re.S)
    spawn_rows = re.findall(
        r"\{\s*([-\d.f]+),\s*([-\d.f]+),\s*([-\d.f]+),\s*([-\d.f]+)\s*\}",
        m.group(1))
    phit = 0
    for i in range(6):
        x, y, z, o = (v.rstrip("f") for v in spawn_rows[i])
        want = "(607, %s, %s, %s)" % (x, y, z)
        ok = want in flat
        phit += ok
        if not ok:
            fails.append("gate spawn %d %s" % (i, want))
    lines.append("    gate spawn rows matched: %d/6" % phit)

    # cannon rows NpcSpawnlocs[0..9]
    m = re.search(r"BG_SA_NpcSpawnlocs\[BG_SA_MAXNPC \+ BG_SA_DEMOLISHER_"
                  r"AMOUNT\]\[4\] =\s*\{(.*?)\n\};", sota_h, re.S)
    npc_rows = re.findall(
        r"\{\s*([-\d.f]+),\s*([-\d.f]+),\s*([-\d.f]+),\s*([-\d.f]+)\s*\}",
        m.group(1))
    chit = 0
    for i in range(10):
        x, y, z, o = (v.rstrip("f") for v in npc_rows[i])
        want = "(607, %s, %s, %s)" % (x, y, z)
        ok = want in flat
        chit += ok
        if not ok:
            fails.append("cannon spawn %d %s" % (i, want))
    lines.append("    cannon rows matched: %d/10" % chit)

    # demolisher rows 15..18
    dhit = 0
    for i in (15, 16, 17, 18):
        x, y, z, o = (v.rstrip("f") for v in npc_rows[i])
        want = "(607, %s, %s, %s)" % (x, y, z)
        ok = want in flat
        dhit += ok
        if not ok:
            fails.append("demo spawn %d %s" % (i, want))
    lines.append("    demolisher rows matched: %d/4" % dhit)

    # 68 bomb rows + NEVER classification
    m = re.search(r"// Bombs\n(.*?)\n\};", sota_h, re.S)
    bombs = re.findall(
        r"\{\s*([-\d.f]+),\s*([-\d.f]+),\s*([-\d.f]+),\s*([-\d.f]+)\s*\}",
        m.group(1))
    bhit = 0
    never_src = set()
    for idx, (x, y, z, o) in enumerate(bombs):
        xf, yf, zf = (x.rstrip("f"), y.rstrip("f"), z.rstrip("f"))
        want = "(607, %s, %s, %s)" % (xf, yf, zf)
        ok = want in flat
        bhit += ok
        if not ok:
            fails.append("bomb row %d %s" % (idx, want))
        X, Y, Z = float(xf), float(yf), float(zf)
        start = Z < 22.0
        outer = ((X < 1371 and Z < 35 and Y > 100) or
                 (X < 1382 and Z < 35 and Y < -100))
        mid = 68 < Z < 73
        yellow = 78 < Z < 87
        if not (start or outer or mid or yellow):
            never_src.add((xf, yf, zf))
    lines.append("    bomb rows matched: %d/68" % bhit)
    if bhit != 68:
        fails.append("bomb rows")
    doc_never = set()
    for m2 in re.finditer(
            r"\(607, (-?[\d.]+), (-?[\d.]+), (-?[\d.]+)\)\s+o [-\d.]+\s+"
            r"NEVER", text):
        doc_never.add(m2.groups())
    ok_never = doc_never == never_src and len(doc_never) == 5
    lines.append("    NEVER rows: doc %d vs computed %d - %s"
                 % (len(doc_never), len(never_src),
                    "match" if ok_never else "MISMATCH"))
    if not ok_never:
        fails.append("NEVER rows")

    # action bars vs doc
    bars = [(28781, 0, 52338), (28781, 1, 60206), (27894, 0, 49872)]
    bar_ok = 0
    for entry, idx, spell in bars:
        row = "(%d,%d,%d," % (entry, idx, spell)
        in_src = row in corpora["cts"]
        in_doc = ("spell %d" % spell) in flat
        ok = in_src and in_doc
        bar_ok += ok
        if not ok:
            fails.append("bar %s (src=%s doc=%s)" % (row, in_src, in_doc))
    lines.append("    action-bar spells: %d/%d in template AND doc"
                 % (bar_ok, len(bars)))

    # creature_template decode for 27894 / 28781
    cols = _ac_ct_columns(corpora["ct"])
    claims = {
        27894: {"npcflag": "16777216", "type": "9", "faction": "614",
                "HealthModifier": "8.64198", "VehicleId": "160",
                "AIName": "NullCreatureAI", "ScriptName": ""},
        28781: {"npcflag": "16777216", "type": "9", "faction": "168",
                "HealthModifier": "14.8148", "VehicleId": "158",
                "AIName": "NullCreatureAI", "ScriptName": ""},
    }
    ct_ok = 0
    for entry, want in claims.items():
        row = [l for l in corpora["ct"].splitlines()
               if l.startswith("(%d," % entry)]
        if not row:
            fails.append("ct row %d" % entry)
            continue
        vals = _parse_csv_row(row[0].rstrip(",;"))
        d = dict(zip(cols, vals))
        bad = [k for k, v in want.items() if d.get(k) != v]
        doc_bits = ["npcflag 16777216", "type 9",
                    "faction %s" % want["faction"],
                    "HealthModifier %s" % want["HealthModifier"],
                    "VehicleId %s" % want["VehicleId"],
                    "'NullCreatureAI'"]
        missing_doc = [b for b in doc_bits if b not in flat]
        if not bad and not missing_doc:
            ct_ok += 1
        else:
            fails.append("ct %d bad=%s doc=%s" % (entry, bad, missing_doc))
    lines.append("    creature_template decode: %d/2 match doc claims"
                 % ct_ok)

    ok_c, c_lines, missing_c = coord_trace(text, corpora)
    for ln in c_lines:
        if "NOT IN" in ln or "triples traced" in ln:
            lines.append(ln)
    if not ok_c:
        fails.append("coordinate trace: %s" % [str(t) for t in missing_c[:6]])
    probe_txt = text.replace("(607, 1592.49, 47.5969, 7.52271)",
                             "(607, 1592.49, 47.5969, 7.62271)")
    ok2, _, _ = coord_trace(probe_txt, corpora)
    probe_ok = (probe_txt != text) and not ok2
    lines.append("    coordinate probe reacts: %s"
                 % ("yes" if probe_ok else "no"))
    if not probe_ok:
        fails.append("coord probe")
    if probe:
        hit_fail = any("gate spawn" in str(f) for f in fails)
        lines.append("    row check reacts to doc tamper: %s"
                     % ("yes" if hit_fail else "no"))
        if not hit_fail:
            fails.append("row probe")
    return fails, lines


def stage5(text, corpora):
    lines, fails = [], []
    for key, label in (("vdbc", "vehicle_dbc"),
                       ("vsdbc", "vehicleseat_dbc")):
        n = len(re.findall(r"^\(", corpora[key], re.M))
        ok = n == 0
        if not ok:
            fails.append("%s has %d data rows" % (label, n))
        lines.append("    %s data rows: %d (need 0)" % (label, n))
    import subprocess
    absent_all = True
    for sub in ("EasternKingdoms/StrandOfTheAncients",
                "Northrend/StrandOfTheAncients"):
        res = subprocess.run(
            ["gh", "api", "repos/%s/contents/src/server/scripts/%s"
             % (LC, sub)], capture_output=True, text=True)
        if res.returncode == 0:
            absent_all = False
            fails.append("LC scripts/%s exists" % sub)
    lines.append("    LC SOTA script folders absent: %s"
                 % ("yes" if absent_all else "NO"))
    m = re.search(r"EventPlayerDamagedGO\(Player\*[^{]*\{(.*?)\n\}",
                  corpora["sota_c"], re.S)
    ok = m is not None and "getGateIdFromDamagedOrDestroyEventId" in m.group(1)
    if not ok:
        fails.append("EventPlayerDamagedGO empty/absent")
    lines.append("    EventPlayerDamagedGO handles gate events: %s"
                 % ("yes" if ok else "NO"))
    ok = ("(27894," in corpora["ct"] and "(190753," in corpora["got"]
          and "(52408,'spell_gen_seaforium_blast')" in corpora["ssn"]
          and "(28781,0,52338," in corpora["cts"])
    if not ok:
        fails.append("template sanity")
    lines.append("    AC rows present (27894/190753/52408/28781): %s"
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
    print("AUDIT: Vehicles_Strand_of_the_Ancients_COMPLETED.txt (Vehicles 2)")
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
    for k, p in AC_FILES.items():
        corpora[k] = gh_content(AC, p)
    for k, p in RAW_LC.items():
        corpora[k] = gh_raw(LC, p)
    for k, p in RAW_AC.items():
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
        corpora, {"cts": [("bar demo", "(28781,0,52338,12340)")]},
        lambda t: t.replace("(28781,0,52338,12340)",
                            "(28781,0,52339,12340)"))
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
