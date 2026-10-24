#!/usr/bin/env python3
"""Audit: Islands_Enemy_COMPLETED.txt (Islands 2)."""

import re
import subprocess
import sys

sys.path.insert(0, ".")
from audit_common import (gh_content, gh_raw, source_stage, mutation_probe,
                          coord_trace)

DOC = "# Ai Research prompts/Islands/Islands_Enemy_COMPLETED.txt"
DOC1 = "# Ai Research prompts/Islands/Islands_Maps_COMPLETED.txt"
TCDEV = "TCDEVEmu/AtalDazar_BFA"
WPP = "TrinityCore/WowPacketParser"
HAVEN = "HavenWoW/BFA-HavenCore"
TC = "TrinityCore/TrinityCore"
API = "Gethe/wow-ui-source"
DICT = "Ironship/WordHunterWoW-Dictionary-DE"
SCRIPTS_SUB = "src/server/scripts/BattleforAzeroth/Island%20Expeditions"
ISLES_DIR_FILES = [
    "UnchartedIsland", "ScenarioSnowblossomVillage",
    "ScenarioUngolRuins", "ScenarioVerdantWilds",
]

FILES = {
    "islpkt_h": (TCDEV, "src/server/game/Server/Packets/IslandPackets.h"),
    "islpkt_c": (TCDEV, "src/server/game/Server/Packets/IslandPackets.cpp"),
    "island_h": (TCDEV, "src/server/game/Handlers/IslandHandler.cpp"),
    "scen_h": (TCDEV, "src/server/game/Handlers/ScenarioHandler.cpp"),
    "inst_h": (TCDEV, "src/server/game/Instances/InstanceScript.h"),
    "inst_c": (TCDEV, "src/server/game/Instances/InstanceScript.cpp"),
    "sc_verd": (TCDEV, "src/server/scripts/BattleforAzeroth/"
                       "Island Expeditions/ScenarioVerdantWilds/"
                       "scenario_verdant_wilds.cpp"),
    "sc_snow": (TCDEV, "src/server/scripts/BattleforAzeroth/"
                       "Island Expeditions/ScenarioSnowblossomVillage/"
                       "scenario_snowblossom_village.cpp"),
    "sc_ungol": (TCDEV, "src/server/scripts/BattleforAzeroth/"
                        "Island Expeditions/ScenarioUngolRuins/"
                        "scenario_ungol_ruins.cpp"),
    "npcs": (TCDEV, "src/server/scripts/World/npcs_special.cpp"),
    "custom": (TCDEV, "src/server/scripts/Custom/custom_player_script.cpp"),
    "ispell": (TCDEV, "sql/Ataldazar/world/2020_12_25_01_island_spell.sql"),
    "isl_sql": (TCDEV, "sql/Ataldazar/world/2020_12_07_00_island.sql"),
    "mapdiff": (TCDEV, "sql/Ataldazar/hotfixes/2022_03_20_00_map_difficulty.sql"),
    "wpp": (WPP, "WowPacketParserModule.V8_0_1_27101/Parsers/IslandHandler.cs"),
    "shared": (HAVEN, "src/server/game/Miscellaneous/SharedDefines.h"),
    "apidoc": (API, "Interface/AddOns/Blizzard_APIDocumentationGenerated/"
                    "IslandsInfoDocumentation.lua"),
}
RAW_FILES = {}

# Advanced NPC teams (warcraft.wiki.gg), (team, [members]) per faction.
TEAMS_A = [
    ("Briona's Buccaneers",
     ["Briona the Bloodthirsty", "Varigg", "\"Stabby\" Lottie"]),
    ("Auric's Angels",
     ["Frostfencer Seraphi", "Squallshaper Bryson", "Squallshaper Auran"]),
    ("Light's Vengeance",
     ["Vindicator Baatul", "Anchorite Lanna", "Archmage Tamuura"]),
    ("Razak's Roughriders",
     ["Razak Ironsides", "Dizzy Dina", "Tally Zapnabber"]),
    ("Riftrunners",
     ["Riftblade Kelain", "Shadeweaver Zarra", "Duskrunner Lorinas"]),
    ("The Wolfpack",
     ["Gunnolf the Ferocious", "Fenrae the Cunning", "Raul the Tenacious"]),
    ("Dark Iron Demolishers",
     ["Airyn Swiftfeet", "Lady Tamakeen", "Brother Bruen"]),
    ("Thornspeakers",
     ["Thornguard Burton", "Thornspeaker Tavery", "Thornstalker Nydora"]),
]
TEAMS_H = [
    ("The Headhunters",
     ["Berserker Zar'ri", "Shadow Hunter Ju'loa", "Witch Doctor Unbugu"]),
    ("Warbraves",
     ["Spiritwalker Quura", "Mahna Flamewhisper", "Sunwalker Ordel"]),
    ("Greenbelly's Raiders",
     ["Captain Greenbelly", "Dorp", "Sneaky Pete"]),
    ("The Blazing Sunhawks",
     ["Phoenix Mage Rhydras", "Phoenix Mage Ryleia", "Sunbringer Firasi"]),
    ("The Highborne",
     ["Moonscythe Pelani", "Rune Scribe Lusaris", "Astralite Visara"]),
    ("Gazlowe's Greasemonkeys", ["Gazlowe", "Skaggit", "Lady Sena"]),
    ("Draenor's Blood",
     ["Nagtar Wolfsbane", "Ranah Saberclaw", "Charg \"The Boisterous\""]),
    ("Raptari",
     ["Guardian M'sheke", "Mooncaller Mozo'kas", "Wardruid Ko'chus"]),
]
ACTIVITY_ISLES = {  # lfg name prefix -> (core 4 ids, ids tagged 153)
    "Snowblossom Village": (["1983", "1988", "1989", "1990"], []),
    "Havenswood": (["1928", "1929", "1930", "1931"], ["2025", "2055"]),
    "Jorundall": (["1932", "1933", "1934", "1935"], ["2041", "2056"]),
    "Verdant Wilds": (["1724", "1743", "1746", "1763"], ["2058"]),
    "Whispering Reef": (["1735", "1740", "1749", "1908"], []),
    "The Rotting Mire": (["1723", "1744", "1745", "1764"], []),
    "The Dread Chain": (["1734", "1741", "1748", "1766"], []),
}
UNVERIFIED_MIN = 16
DICT_INITIAL = ["104", "107", "108", "110", "112", "114", "117", "118",
                "122", "123"]


def norm(s):
    return re.sub(r"\s+", " ", s)


def _dict_token(name):
    if "\"" not in name:
        return name
    parts = [p.strip() for p in name.split("\"") if p.strip()]
    return max(parts, key=len)


STATIC_CHECKS = [
    ("heading", "=== ISLAND EXPEDITIONS - ENEMY TEAM - BFA 8.3.7 "
                "(TRINITYCORE) - COMPLETED ==="),
    ("done", "DONE - step 2 of the Islands set complete"),
    ("src wiki", "warcraft.wiki.gg \"Island Expedition\" (Advanced NPC"),
    ("src moudi", "worldofmoudi.com island expedition guide"),
    ("src rude", "superlativelyrude.com AI-teams guide"),
    ("src icy", "Icy Veins"),
    ("src tcdev", "TCDEVEmu/AtalDazar_BFA server source"),
    ("src wpp", "WowPacketParser V8_0_1_27101 IslandHandler.cs"),
    ("src api", "IslandsInfoDocumentation.lua"),
    ("xref", "cross-reference Islands_Maps (step 1)"),
    ("s1 size", "team of 3 Advanced NPC opponents from the opposite faction"),
    ("s1 pvp", "3 human players, not NPCs"),
    ("s1 mirror", "gnomes on one side and goblins on the other"),
    ("s1 hub a", "Tradewinds Market"),
    ("s1 hub h", "Dazar'alor"),
    ("s1 unv", "Creature entries for the 48 team members: unverified"),
    ("s2 race", "first side to the Azerite total wins"),
    ("s2 mimic", "mimic player behavior"),
    ("s2 node", "prioritize Azerite nodes"),
    ("s2 aggro", "if players focus on combat rather than"),
    ("s2 adapt", "influenced by several factors, including the number of "
                 "players in the expedition and the current Azerite"),
    ("s2 stage", "announced stages"),
    ("s2 noserver", "no enemy-team AI at all"),
    ("s2 unv", "Exact decision logic (switch lists, aggro radius"),
    ("s3 n", "Normal 6000, Heroic 9000, Mythic 12000, PvP 12000"),
    ("s3 dur", "about 15-20 minutes"),
    ("s3 math", "6000 / 15-20 min = 300-400"),
    ("s3 st2n", "stage 2 (clusters + elementals): Normal ~3000-4000 (33%)"),
    ("s3 st2h", "Heroic ~6000 (33%), Mythic ~12000 (50%)"),
    ("s3 st3", "stage 3 (boss/event chests): Normal 6000 (50%)"),
    ("s3 st3h", "Heroic 12000 (50%), Mythic 20000 (80%)"),
    ("s3 guide", "one guide only, unverified against client/server data"),
    ("s3 rate", "per-minute azerite income for the NPC team specifically:"),
    ("s3 flat", "adds a flat\n       +3 azerite to the killer's side"),
    ("s3 basexp", "int32 baseXP = 3; instance->GiveIslandAzeriteXpGain(...)"),
    ("s3 gate", "DIFFICULTY_NORMAL_ISLAND .. DIFFICULTY_PVP_ISLAND"),
    ("s3 tick", "each periodic tick adds\n       +1 stack, capped at 250 stacks"),
    ("s3 cap", "SetStackAmount(min(+1, 250))"),
    ("s3 payout", "pays out its\n       current stack count, then resets that "
                  "target to 1 stack"),
    ("s3 pvp", "Killing a PLAYER pays out the victim's stack count (max 250)"),
    ("s3 accum", "longer you are alive"),
    ("s3 ws", "updates world states 12930 (Alliance gain) and 13627 (Horde"),
    ("s3 win", "GetIslandCount()[0] >= 9000 or [1] >= 9000"),
    ("s3 win2", "This server wins at 9000 on"),
    ("s3 energy", "Spell 265703 \"Azerite Energy\" is defined but its cast is"),
    ("s3 tick unv", "aura period value not"),
    ("s4 e1", "285835 \"Activate Extractor\""),
    ("s4 e2", "280859 \"Collecting\""),
    ("s4 e3", "285811 \"Deploy Extractor\" - deploy an Azerite extractor"),
    ("s4 e4", "285630 \"Heart of Azeroth\" - use the Heart's power"),
    ("s4 mining", "Mining (no spell id on the page)"),
    ("s4 opening", "Opening (no spell id on the page)"),
    ("s4 unv", "per-team class spell kits"),
    ("s5 opp", "Opponents            3 NPCs      3 NPCs      3 NPCs      "
               "3 players"),
    ("s5 tot", "Azerite to win       6000        9000        12000       "
               "12000"),
    ("s5 id", "Difficulty id        38          39          40          45"),
    ("s5 mp", "MaxPlayers (DB)      3           3           3           6"),
    ("s5 hp", "Enemy health mod     base        +100%       +200%       "
              "n/a (players)"),
    ("s5 az", "Azerite gain mod     base        +50%        +100%       n/a"),
    ("s5 grp", "Group form           any 3       any 3       premade 3   "
               "3v3"),
    ("s5 enum", "DIFFICULTY_NORMAL_ISLAND = 38 / HEROIC = 39 / MYTHIC = 40"),
    ("s5 enum2", "PVP_ISLAND = 45 (and DIFFICULTY_TEEMING_ISLAND = 153)"),
    ("s5 teeming", "DIFFICULTY_TEEMING_ISLAND = 153"),
    ("s5 mods", "Azerite increased by 50% ... enemies have 100% more health"),
    ("s5 premade", "premade-3 for Mythic - Icy Veins"),
    ("s5 ilvl", "Mythic 315 (all guides agree); Heroic 295"),
    ("s5 ilvl2", "GameRevolution) vs 305 (Gamepur) - conflict between"),
    ("s5 conv", "which value was final in 8.3.7: unverified"),
    ("s5 conquest", "50 Conquest on a win (was 8)"),
    ("s6 start", "at least 4 start locations chosen per run"),
    ("s6 unv", "which start point the NPC team takes, and its "
               "patrol/path waypoints"),
    ("s6 four", "contains only four"),
    ("s6 folders", "UnchartedIsland, ScenarioSnowblossomVillage, "
                   "ScenarioUngolRuins, ScenarioVerdantWilds"),
    ("s6 empty", "OnCreatureCreate handlers are empty"),
    ("s6 todo", "//TO DO cast on pve NPC"),
    ("s6 stub", "the NPC side of the azerite system is stubbed out"),
    ("s6 zero", "return zero files - no upstream island AI to copy either"),
    ("s6 final", "Enemy spawn point and path point coordinates on a server "
                 "built from these sources: unverified"),
    ("s7 cmsg", "CMSG_ISLAND_QUEUE { PackedGuid128 QueueNPCGuid, "
                "int32 ActivityID }"),
    ("s7 cmsg2", "TCDEVEmu IslandOnQueue reads the\n       same two fields"),
    ("s7 mission", "SMSG_ISLANDS_MISSION_NPC / SMSG_ISLAND_OPEN_QUEUE_NPC"),
    ("s7 gain", "SMSG_ISLAND_AZERITE_GAIN / SMSG_ISLAND_AZERITE_XP_GAIN"),
    ("s7 gainf", "int32 Gain (XpGain), PackedGuid128 PlayerGuid"),
    ("s7 size", "payload\n         size 4 + 36 + 36 + 4"),
    ("s7 done", "SMSG_ISLAND_COMPLETE / SMSG_ISLAND_COMPLETED"),
    ("s7 donef", "uint32 GroupTeamSize, then PlayerModelDisplayInfo per "
                 "player"),
    ("s7 win", "int32 Winner (0 = Alliance, 1 = Horde)"),
    ("s7 commented", "display-info block itself is commented out"),
    ("s7 event", "ISLAND_AZERITE_GAIN payload = { amount, gainedByPlayer"),
    ("s7 faction", "factionIndex, gainedBy (WOWGUID), gainedFrom (WOWGUID)"),
    ("s7 opcode", "Numeric opcode values for build 35662: unverified"),
    ("s8 join", "sLFGMgr->JoinLfg(GetPlayer(), ROLE_DAMAGE, {ActivityID})"),
    ("s8 role", "hardcoded to the damage role"),
    ("s8 credit", "KilledMonsterCredit\n   139310 (Alliance) and 139309 (Horde)"),
    ("s8 act snow", "Snowblossom Village 1983/1988/1989/1990 (38/39/40/45)"),
    ("s8 act hav", "Havenswood 1928/1929/1930/1931 (+2025/2055 tagged 153)"),
    ("s8 act jor", "Jorundall 1932/1933/1934/1935 (+2041/2056 tagged 153)"),
    ("s8 act ver", "Verdant Wilds 1724/1743/1746/1763 (+2058 tagged 153)"),
    ("s8 act reef", "Whispering Reef 1735/1740/1749/1908"),
    ("s8 act mire", "Rotting Mire 1723/1744/1745/1764"),
    ("s8 act dread", "Dread Chain 1734/1741/1748/1766"),
    ("s8 act none", "no queue rows\n       in the readable SQL (step 1)"),
    ("s8 timer", "verdant 45 s + event at 45 s"),
    ("s8 timer2", "snowblossom 33 s + event at 33 s, ungol shows 45/45 but"),
    ("s8 residue", "EVENT_START_TIMER -> CastIslandAzeriteAura() (260738 on "
                   "all\n       players)"),
    ("s8 loop", "EVENT_GAME_START every 1 s"),
    ("s8 conv", "plays conversation 6514 (HORDE_ON_BEGIN)"),
    ("s8 conv2", "7498 (ON_50) and 7487 (ON_80) which are not"),
    ("s8 complete", "IslandComplete: remove 260738 from everyone, cast"),
    ("s8 winner", "IslandCompleted{MapID, Winner 0/1, DisplayInfos of the "
                  "winning"),
    ("s8 conv7504", "play conversation 7504 when the Horde wins"),
    ("s8 ws init", "14684=6000, 15893=17"),
    ("s8 reg verd", "InstanceScript for map 1882, ungol for\n       1813 "
                    "(RegisterInstanceScript)"),
    ("s8 reg snow", "InstanceMapScript(\"scenario_snowblossom_village\", "
                    "1907)"),
    ("s8 aura", "aura script spell_azerite_residue_260738"),
    ("s8 poi", "HandleQueryScenarioPOI"),
    ("s8 cover", "only 3 of the 11 rotation islands"),
    ("s8 nothandle", "enemy team spawning, stage 2/3 events"),
    ("s9 hdr", "UNVERIFIED LIST (consolidated)"),
    ("s9 entries", "Creature entries of the 48 Advanced NPC team members"),
    ("s9 path", "Enemy team start-point choice and patrol/path waypoints"),
    ("s9 rate", "Per-minute Azerite income of the retail NPC team"),
    ("s9 algo", "Exact AI targeting algorithm (priority weights, switch "
                "rules)"),
    ("s9 kits", "Per-team combat spell kits beyond the six wiki ability "
                "entries"),
    ("s9 stage", "Stage 2/3 trigger thresholds confirmed only by one guide"),
    ("s9 tick", "Residue aura tick period (stacks per minute) in the server "
                "data"),
    ("s9 ilvl", "Heroic queue item level (295 vs 305 guide conflict)"),
    ("s9 teem", "What Teeming (difficulty 153) changed in 8.3.7"),
    ("s9 opcode", "Numeric opcode values on build 35662"),
    ("s9 conv", "Conversations 7498/7487 trigger conditions"),
    ("s9 ws", "world states 16018/14253/13004/14065/14246/"),
    ("s9 four", "Queue activity ids for Crestfall, Molten Cay, Un'gol Ruins "
                "and"),
    ("s9 cover", "Server-side scenario handling for the 8 islands without "
                 "scripts"),
]
# team roster statics (16) + every member name (48)
for _team, _members in TEAMS_A + TEAMS_H:
    _lit = "%s - %s" % (_team, _members[0])
    STATIC_CHECKS.append(("team " + _team[:18], _lit))
    for _m in _members:
        STATIC_CHECKS.append(("member " + _m[:20], _m))
STATIC_CHECKS.append(("stabb", "\"Stabby\" Lottie (dwarven/gnomish pirates)"))
STATIC_CHECKS.append(("charg", "Charg \"The Boisterous\" (mag'har orcs)"))

NEGATIVE_CHECKS = [
    ("no estimated coordinate", "estimated coordinate"),
    ("no navmesh confirmed", "navmesh confirmed"),
    ("no direct inspection", "verified by direct inspection"),
    ("no todo", "TODO"),
    ("no fixme", "FIXME"),
    ("no damageers", "damageers"),
    ("no placeholder", "placeholder"),
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
    ("heading", "- COMPLETED ===\n\nSources", "- DRAFT ===\n\nSources"),
    ("done", "DONE - step 2 of the Islands set complete",
     "DONE - step 2 of the Islands set finished"),
    ("s1 size", "Advanced NPC opponents from the opposite faction, racing "
                 "to the",
     "Advanced NPC opponents from the allied faction, racing to the"),
    ("s1 pvp", "3 human players, not NPCs", "4 human players, not NPCs"),
    ("team briona", "Briona's Buccaneers - Briona the Bloodthirsty",
     "Briona's Buccaneers - Briona the Bloodthirst"),
    ("member varigg", "Varigg,", "Varig,"),
    ("team wolfpack", "The Wolfpack - Gunnolf the Ferocious",
     "The Wolfpack - Gunnolf the Ferocia"),
    ("team raptari", "Raptari - Guardian M'sheke",
     "Raptari - Guardian M'sheka"),
    ("team sunhawks", "The Blazing Sunhawks - Phoenix Mage Rhydras",
     "The Blazing Sunhawks - Phoenix Mage Rhydra"),
    ("s2 node", "prioritize Azerite nodes", "prioritize Azerite chests"),
    ("s2 aggro", "if players focus on combat rather than",
     "if players focus on gathering rather than"),
    ("s3 n", "Normal 6000, Heroic 9000, Mythic 12000, PvP 12000",
     "Normal 6100, Heroic 9000, Mythic 12000, PvP 12000"),
    ("s3 math", "6000 / 15-20 min = 300-400", "6000 / 15-20 min = 300-500"),
    ("st2n", "~3000-4000 (33%)", "~3000-4100 (33%)"),
    ("st3m", "Mythic 20000 (80%)", "Mythic 20100 (80%)"),
    ("basexp", "int32 baseXP = 3;", "int32 baseXP = 4;"),
    ("cap", "SetStackAmount(min(+1, 250))", "SetStackAmount(min(+1, 251))"),
    ("payout", "resets that target to 1 stack", "resets that target to 2 stack"),
    ("pvp250", "victim's stack count (max 250)", "victim's stack count "
                                                 "(max 251)"),
    ("ws", "world states 12930 (Alliance gain) and 13627 (Horde",
     "world states 12931 (Alliance gain) and 13627 (Horde"),
    ("win", "GetIslandCount()[0] >= 9000 or [1] >= 9000",
     "GetIslandCount()[0] >= 9001 or [1] >= 9001"),
    ("win2", "This server wins at 9000 on", "This server wins at 9001 on"),
    ("energy", "Spell 265703 \"Azerite Energy\"", "Spell 265704 \"Azerite "
                                                  "Energy\""),
    ("e1", "285835 \"Activate Extractor\"", "285836 \"Activate Extractor\""),
    ("e2", "280859 \"Collecting\"", "280860 \"Collecting\""),
    ("e3", "285811 \"Deploy Extractor\"", "285812 \"Deploy Extractor\""),
    ("e4", "285630 \"Heart of Azeroth\"", "285631 \"Heart of Azeroth\""),
    ("s5 tot", "6000        9000        12000       12000",
     "6000        9000        12000       13000"),
    ("s5 id", "38          39          40          45",
     "38          39          40          46"),
    ("s5 mp", "3           3           3           6",
     "3           3           3           7"),
    ("s5 hp", "+100%       +200%       n/a (players)",
     "+100%       +201%       n/a (players)"),
    ("s5 az", "+50%        +100%       n/a", "+50%        +101%       n/a"),
    ("s5 grp", "premade 3   3v3", "premade 4   3v3"),
    ("s5 enum", "MYTHIC = 40", "MYTHIC = 41"),
    ("s5 teem", "DIFFICULTY_TEEMING_ISLAND = 153",
     "DIFFICULTY_TEEMING_ISLAND = 154"),
    ("s5 ilvl", "Mythic 315 (all guides agree)", "Mythic 316 (all guides "
                                                 "agree)"),
    ("s5 conv", "50 Conquest on a win (was 8)", "50 Conquest on a win "
                                                "(was 9)"),
    ("s6 folders", "ScenarioUngolRuins, ScenarioVerdantWilds",
     "ScenarioUngolRuins, ScenarioVerdantWild"),
    ("s6 todo", "//TO DO cast on pve NPC", "//TO DONE cast on pve NPC"),
    ("s6 zero", "return zero files - no upstream island AI",
     "return one file - no upstream island AI"),
    ("s7 cmsg", "CMSG_ISLAND_QUEUE { PackedGuid128 QueueNPCGuid, "
                "int32 ActivityID }",
     "CMSG_ISLAND_QUEUE { PackedGuid128 QueueNPCGuid, int32 ActivityId }"),
    ("s7 size", "size 4 + 36 + 36 + 4", "size 4 + 36 + 36 + 5"),
    ("s7 win", "int32 Winner (0 = Alliance, 1 = Horde)",
     "int32 Winner (1 = Alliance, 0 = Horde)"),
    ("s7 event", "payload = { amount", "payload = { counts"),
    ("s8 join", "JoinLfg(GetPlayer(), ROLE_DAMAGE, {ActivityID})",
     "JoinLfg(GetPlayer(), ROLE_HEAL, {ActivityID})"),
    ("s8 credit", "139310 (Alliance) and 139309 (Horde)",
     "139311 (Alliance) and 139309 (Horde)"),
    ("s8 act snow", "Snowblossom Village 1983/1988/1989/1990",
     "Snowblossom Village 1983/1988/1989/1991"),
    ("s8 act ver", "Verdant Wilds 1724/1743/1746/1763",
     "Verdant Wilds 1724/1743/1746/1764"),
    ("s8 timer", "verdant 45 s + event at 45 s", "verdant 46 s + event at "
                                                 "46 s"),
    ("s8 timer2", "snowblossom 33 s + event at 33 s",
     "snowblossom 34 s + event at 34 s"),
    ("s8 conv", "plays conversation 6514 (HORDE_ON_BEGIN)",
     "plays conversation 6515 (HORDE_ON_BEGIN)"),
    ("s8 conv7504", "play conversation 7504 when the Horde wins",
     "play conversation 7505 when the Horde wins"),
    ("s8 complete", "IslandComplete: remove 260738 from everyone",
     "IslandComplete: remove 260739 from everyone"),
    ("s8 reg verd", "InstanceScript for map 1882", "InstanceScript for map "
                                                   "1883"),
    ("s8 reg snow", "InstanceMapScript(\"scenario_snowblossom_village\", "
                    "1907)",
     "InstanceMapScript(\"scenario_snowblossom_village\", 1908)"),
    ("s8 cover", "only 3 of the 11 rotation islands",
     "only 4 of the 11 rotation islands"),
    ("s9 four", "Queue activity ids for Crestfall, Molten Cay",
     "Queue activity ids for Crestfall, Molton Cay"),
    ("unv drop", "Enemy team start-point choice and patrol/path waypoints",
     "Enemy team start-point choice"),
    ("unv drop2", "Exact AI targeting algorithm (priority weights, switch "
                  "rules)",
     "AI targeting algorithm (priority weights, switch rules)"),
]


def _gh(repo, path):
    r = subprocess.run(["gh", "api", "repos/%s/contents/%s" % (repo, path)],
                       capture_output=True, text=True)
    return r.returncode == 0


_TC_SEARCH_CACHE = {}


def _tc_search(q):
    """Total hits for a code search query, cached and retried with backoff."""
    import time
    if q in _TC_SEARCH_CACHE:
        return _TC_SEARCH_CACHE[q]
    got = None
    for attempt in range(3):
        r = subprocess.run(
            ["gh", "api", "search/code?q=%s+repo:%s" % (q, TC),
             "--jq", ".total_count"], capture_output=True, text=True)
        out = r.stdout.strip()
        if out.isdigit():
            got = int(out)
            break
        time.sleep(8 + 4 * attempt)
    _TC_SEARCH_CACHE[q] = got
    return got


def stage3(corpora):
    token_map = {
        "islpkt_h": [
            ("class queue", "class IslandOnQueue final : public ClientPacket"),
            ("cmsg", "ClientPacket(CMSG_ISLAND_QUEUE"),
            ("fields", "ObjectGuid QueueNPCGuid;"),
            ("activity", "int32 ActivityID = 0;"),
            ("open npc", "ServerPacket(SMSG_ISLAND_OPEN_QUEUE_NPC, 36)"),
            ("gain pkt", "ServerPacket(SMSG_ISLAND_AZERITE_XP_GAIN, "
                         "4 + 36 + 36 + 4)"),
            ("gain fields", "int32 XpGain = 0;"),
            ("done pkt", "ServerPacket(SMSG_ISLAND_COMPLETED)"),
            ("map winner", "int32 MapID = 0;"),
            ("winner", "int32 Winner = 0;"),
            ("display", "std::vector<WorldPackets::Inspect::"
                        "PlayerModelDisplayInfo> DisplayInfos;"),
        ],
        "islpkt_c": [
            ("write gain", "_worldPacket << XpGain;"),
            ("write src", "_worldPacket << SourceID;"),
            ("write map", "_worldPacket << MapID;"),
            ("write win", "_worldPacket << Winner;"),
            ("read guid", "_worldPacket >> QueueNPCGuid;"),
            ("read act", "_worldPacket >> ActivityID;"),
        ],
        "island_h": [
            ("handler", "void WorldSession::HandleIslandQueue"),
            ("join", "sLFGMgr->JoinLfg(GetPlayer(), ROLE_DAMAGE, "
                     "newDungeons);"),
            ("insert", "newDungeons.insert(islandQueue.ActivityID);"),
            ("credit a", "KilledMonsterCredit(139310);"),
            ("credit h", "KilledMonsterCredit(139309);"),
        ],
        "scen_h": [
            ("poi", "void WorldSession::HandleQueryScenarioPOI"),
            ("scenmgr", "sScenarioMgr->GetScenarioPOIs"),
        ],
        "inst_h": [
            ("ws h", "WORLDSTATE_HORDE_GAIN = 13627,"),
            ("ws a", "WORLDSTATE_ALLIANCE_GAIN = 12930,"),
            ("sp res", "SPELL_AZERITE_RESIDUE = 260738,"),
            ("sp en", "SPELL_AZERITE_ENERGY = 265703,"),
            ("sp done", "SPELL_ISLAND_COMPLETE = 245618,"),
            ("sp comment", "// island - complete"),
            ("getcount", "GetIslandCount() const"),
            ("cast", "void CastIslandAzeriteAura();"),
            ("give", "void GiveIslandAzeriteXpGain("),
            ("complete", "void IslandComplete(bool winnerIsAlliance);"),
            ("array", "std::array<uint32, 2> _islandCount;"),
        ],
        "inst_c": [
            ("cast body", "DoCastSpellOnPlayers(SPELL_AZERITE_RESIDUE)"),
            ("todo", "//TO DO cast on pve NPC"),
            ("xpgain", "xpgain.XpGain = xp;"),
            ("add", "_islandCount[0] = _islandCount[0] + xp;"),
            ("ws update", "DoUpdateWorldState(WORLDSTATE_ALLIANCE_GAIN, "
                          "_islandCount[0])"),
            ("rm residue", "DoRemoveAurasDueToSpellOnPlayers("
                           "SPELL_AZERITE_RESIDUE)"),
            ("cast done", "DoCastSpellOnPlayers(SPELL_ISLAND_COMPLETE)"),
            ("winner tern", "package.Winner = winnerIsAlliance ? 0 : 1;"),
            ("conv7504", "player->PlayConversation(7504);"),
            ("send", "instance->SendToPlayers(package.Write());"),
        ],
        "sc_verd": [
            ("t45", "startTimer.TotalTime = 45;"),
            ("sched45", "events.ScheduleEvent(EVENT_START_TIMER, "
                        "45 * IN_MILLISECONDS);"),
            ("win a", "if (GetIslandCount()[0] >= 9000)"),
            ("win h", "else if(GetIslandCount()[1] >= 9000)"),
            ("conv begin", "HORDE_ON_BEGIN = 6514,"),
            ("conv 50", "HORDE_ON_50 = 7498,"),
            ("conv 80", "HORDE_ON_80 = 7487,"),
            ("conv done", "HORDE_ON_COMPLETE = 7504,"),
            ("reg", "RegisterInstanceScript(scenario_verdant_wilds, 1882)"),
            ("play", "DoPlayConversation(HORDE_ON_BEGIN);"),
            ("loop", "events.ScheduleEvent(EVENT_GAME_START, "
                     "1 * IN_MILLISECONDS);"),
        ],
        "sc_snow": [
            ("t33", "startTimer.TotalTime = 33;"),
            ("sched33", "events.ScheduleEvent(EVENT_START_TIMER, "
                        "33 * IN_MILLISECONDS);"),
            ("mapscript", "InstanceMapScript(\"scenario_snowblossom_village\", "
                          "1907)"),
            ("win", "GetIslandCount()[0] >= 9000"),
        ],
        "sc_ungol": [
            ("t45", "startTimer.TotalTime = 45;"),
            ("sched33", "events.ScheduleEvent(EVENT_START_TIMER, "
                        "33 * IN_MILLISECONDS);"),
            ("reg", "RegisterInstanceScript(scenario_ungol_ruins, 1813)"),
            ("stack", "std::min((aura->GetStackAmount() + 1), 250)"),
            ("aura reg", "RegisterAuraScript(spell_azerite_residue_260738)"),
        ],
        "npcs": [
            ("base", "int32 baseXP = 3;"),
            ("gate", "GetMap()->GetDifficultyID() >= "
                     "DIFFICULTY_NORMAL_ISLAND"),
            ("gate2", "<= DIFFICULTY_PVP_ISLAND"),
            ("class", "class ps_island_get_xp"),
            ("give", "GiveIslandAzeriteXpGain(killer, killed->GetGUID(), "
                     "baseXP)"),
        ],
        "custom": [
            ("pvpkill", "void OnPVPKill(Player* killer, Player* killed)"),
            ("crekill", "void OnCreatureKill(Player* killer, Creature* killed)"),
            ("reset", "aura->SetStackAmount(1);"),
            ("give count", "GiveIslandAzeriteXpGain(killer, killed->GetGUID(), "
                           "count)"),
            ("class", "class ps_spell_azerite_residue"),
        ],
        "ispell": [
            ("row", "(260738, 'spell_azerite_residue_260738')"),
        ],
        "isl_sql": [
            ("snow", "(1983, 'Snowblossom Village 38',"),
            ("hav", "(1928, 'Havenswood 38',"),
            ("jor", "(1932, 'Jorundall 38',"),
            ("ver", "(1724, 'Verdant Wilds 38',"),
            ("reef", "(1735, 'Whispering Reef 38',"),
            ("mire", "(1723, 'The Rotting Mire 38',"),
            ("dread", "(1734, 'The Dread Chain 38',"),
            ("hav153", "(2025, 'Havenswood 153 pvp',"),
            ("jor153", "(2041, 'Jorundall 153 pvp',"),
            ("ver153", "(2058, 'Verdant Wilds 153',"),
        ],
        "mapdiff": [
            ("d38", "(4096, '', 38, 0, 0, 3, 0, 0, 0, 0, 1882, 34963)"),
            ("d45", "(4171, '', 45, 0, 0, 6, 0, 0, 0, 0, 1882, 34963)"),
        ],
        "wpp": [
            ("p gain", "[Parser(Opcode.SMSG_ISLAND_AZERITE_GAIN)]"),
            ("f gain", 'packet.ReadInt32("Gain")'),
            ("f pguid", 'packet.ReadPackedGuid128("PlayerGuid")'),
            ("f sguid", 'packet.ReadPackedGuid128("SourceGuid")'),
            ("f sid", 'packet.ReadInt32("SourceID")'),
            ("p done", "[Parser(Opcode.SMSG_ISLAND_COMPLETE)]"),
            ("f map", 'packet.ReadInt32("MapID")'),
            ("f win", 'packet.ReadInt32("Winner")'),
            ("f gts", 'packet.ReadUInt32("GroupTeamSize")'),
            ("p mission", "[Parser(Opcode.SMSG_ISLANDS_MISSION_NPC)]"),
            ("f npc", 'packet.ReadPackedGuid128("QueueNPCGuid")'),
            ("p cmsg", "[Parser(Opcode.CMSG_ISLAND_QUEUE)]"),
            ("f act", 'packet.ReadInt32("ActivityID")'),
        ],
        "shared": [
            ("l n", "LOOT_MODE_NORMAL_ISLAND"),
            ("l p", "LOOT_MODE_PVP_ISLAND"),
            ("l t", "LOOT_MODE_TEEMING_ISLAND"),
        ],
        "apidoc": [
            ("ev name", 'Name = "IslandAzeriteGain"'),
            ("ev lit", 'LiteralName = "ISLAND_AZERITE_GAIN"'),
            ("amount", '{ Name = "amount"'),
            ("faction", '{ Name = "factionIndex"'),
            ("from", '{ Name = "gainedFrom"'),
        ],
    }
    # dynamic dictionary tokens for the 48 roster names
    dict_corpus = {}
    for n in DICT_INITIAL:
        dict_corpus["dict" + n] = gh_content(
            DICT, "EntityData/Variants/retail/Data/npc/enUS_%s.lua" % n)
    roster = []
    for _t, members in TEAMS_A + TEAMS_H:
        roster.extend(members)
    unresolved = []
    placed_names = set()
    for name in roster:
        tok = _dict_token(name)
        placed = False
        for key, text in dict_corpus.items():
            if tok in text:
                token_map.setdefault(key, []).append((name, tok))
                placed_names.add(name)
                placed = True
                break
        if not placed:
            unresolved.append(name)
    # runtime search for unresolved names
    still = []
    for name in unresolved:
        tok = _dict_token(name)
        r = subprocess.run(
            ["gh", "api", "search/code?q=%s+repo:%s"
             % (name.replace('"', '').replace(" ", "+").replace("'", "%27"),
                DICT), "--jq", ".items[]? | select(.path|test(\"npc/enUS\")) "
             "| .path"],
            capture_output=True, text=True)
        paths = [p for p in r.stdout.split()
                 if p.endswith(".lua") and "/" in p and "{" not in p]
        placed = False
        for p in paths[:3]:
            key = "dyn_" + p.rsplit("/", 1)[-1]
            if key not in dict_corpus:
                try:
                    dict_corpus[key] = gh_content(DICT, p)
                except RuntimeError:
                    continue
            if tok in dict_corpus[key]:
                token_map.setdefault(key, []).append((name, tok))
                placed = True
                break
        if not placed:
            still.append(name)
        else:
            placed_names.add(name)
    corpora.update(dict_corpus)
    dict_keys = [k for k in dict_corpus if dict_corpus[k]]
    ok, lines = source_stage(corpora, token_map)
    found = len(placed_names)
    lines.append("    %-28s %d/%d roster names found in NPC dictionary"
                 % ("roster cross-check:", found, len(roster)))
    if still:
        lines.append("    wiki-only roster names (no dictionary row): %s"
                     % ", ".join(still))
    if len(dict_keys) < 3:
        ok = False
        lines.append("    dictionary fetch problem")
    # absence: no lfg rows for the four islands without queue data
    lfg_names = set(re.findall(r"\((\d+), '([^']+?) \d+(?: pvp)?',",
                               corpora["isl_sql"]))
    names = {nm for _i, nm in lfg_names}
    for want in ACTIVITY_ISLES:
        if want not in names:
            ok = False
            lines.append("    lfg name missing: %s" % want)
    extra = names - set(ACTIVITY_ISLES)
    if extra:
        ok = False
        lines.append("    unexpected lfg names: %s" % sorted(extra))
    lines.append("    %-28s %d lfg islands only (4 without rows)"
                 % ("activity id set:", len(names)))
    return ok, lines


def stage4(text, corpora, probe=False):
    fails, lines = [], []

    def bad(msg):
        fails.append(msg)

    flat = norm(text)

    # enums re-derivation from InstanceScript.h
    inst_h = corpora["inst_h"]
    ws_a = re.search(r"WORLDSTATE_ALLIANCE_GAIN = (\d+)", inst_h)
    ws_h = re.search(r"WORLDSTATE_HORDE_GAIN = (\d+)", inst_h)
    sp = dict(re.findall(r"(SPELL_[A-Z_]+) = (\d+)", inst_h))
    if not ws_a or int(ws_a.group(1)) != 12930:
        bad("ws_a parse")
    if not ws_h or int(ws_h.group(1)) != 13627:
        bad("ws_h parse")
    for lit in ("12930 (Alliance gain)", "13627 (Horde",
                "260738", "265703", "245618"):
        if lit not in text:
            bad("enum claim %s" % lit)
    if sp.get("SPELL_ISLAND_COMPLETE") != "245618":
        bad("spell parse")
    lines.append("    worldstates 12930/13627 + spells 260738/265703/245618"
                 " -> doc: ok")

    # timers + win thresholds across the three scenario scripts
    verd, snow, ungol = (corpora["sc_verd"], corpora["sc_snow"],
                         corpora["sc_ungol"])
    checks = [
        ("TotalTime = 45" in verd and "event at 45 s" in text, "verdant 45"),
        ("TotalTime = 33" in snow and "event at 33 s" in text, "snow 33"),
        ("TotalTime = 45" in ungol and "45/45 but" in text,
         "ungol display mismatch"),
        ("ScheduleEvent(EVENT_START_TIMER, 33 * IN_MILLISECONDS)" in ungol
         and "start event at 33 s (code as written)" in text,
         "ungol schedule 33"),
    ]
    for ok, label in checks:
        if not ok:
            bad(label)
    n9000 = sum(s.count("GetIslandCount()[0] >= 9000") for s in
                (verd, snow, ungol))
    if n9000 < 3:
        bad("9000 checks in sources: %d" % n9000)
    if "wins at 9000 on" not in text or ">= 9000 or [1] >= 9000" not in text:
        bad("9000 doc claims")
    lines.append("    9000 win checks in scripts:             %d/3, doc ok"
                 % n9000)

    # baseXP / stack payout
    if "int32 baseXP = 3;" not in corpora["npcs"]:
        bad("baseXP source")
    if "int32 baseXP = 3; instance->GiveIslandAzeriteXpGain" not in flat:
        bad("baseXP doc")
    if "std::min((aura->GetStackAmount() + 1), 250)" not in ungol:
        bad("stack cap source")
    if "SetStackAmount(min(+1, 250))" not in text:
        bad("stack cap doc")
    if corpora["custom"].count("GiveIslandAzeriteXpGain(killer") != 2:
        bad("payout call count")
    lines.append("    azerite math (+3/kill, cap 250, 2 payouts): source+doc ok")

    # activity ids re-derived
    rows = re.findall(r"\((\d+), '([^']+?) (\d+)(?: pvp)?',",
                      corpora["isl_sql"])
    grouped = {}
    for did, nm, diff in rows:
        grouped.setdefault(nm, []).append((int(diff), did))
    for nm, (core, tag153) in ACTIVITY_ISLES.items():
        got_core = sorted(d for d, _i in grouped.get(nm, []) if d != 153)
        got_153 = sorted(d for d, _i in grouped.get(nm, []) if d == 153)
        if got_core != [38, 39, 40, 45]:
            bad("core diffs %s %s" % (nm, got_core))
        ids = [i for d, i in sorted(grouped.get(nm, [])) if d != 153]
        if ids != core:
            bad("core ids %s %s != %s" % (nm, ids, core))
        if "/".join(core) not in text:
            bad("doc activity %s" % nm)
        if tag153:
            if [i for d, i in sorted(grouped[nm]) if d == 153] != tag153:
                bad("153 ids %s" % nm)
            frag = "(+%s tagged 153)" % "/".join(tag153)
            if frag not in text:
                bad("doc 153 %s" % nm)
    lines.append("    activity ids re-derived from lfg rows:   7 islands -> doc")

    # MaxPlayers re-derived
    md = re.findall(r"\((\d+), '[^']*', (\d+), 0, 0, (\d+), 0, 0, 0, 0, "
                    r"1882, 34963\)", corpora["mapdiff"])
    md_map = {d: p for _i, d, p in md}
    if md_map != {"38": "3", "39": "3", "40": "3", "45": "6"}:
        bad("mapdiff %s" % md_map)
    if "MaxPlayers (DB)      3           3           3           6" not in \
            text.replace("\n", " "):
        # raw spacing line may wrap; use norm form
        if norm("MaxPlayers (DB) 3 3 3 6") not in flat:
            bad("maxplayers doc")
    lines.append("    map_difficulty players 3/3/3/6 -> doc:   ok")

    # island script folder listing (exactly four scenario folders)
    r = subprocess.run(
        ["gh", "api", "-X", "GET",
         "repos/%s/contents/src/server/scripts/BattleforAzeroth/"
         "Island%%20Expeditions" % TCDEV, "--jq", ".[].name"],
        capture_output=True, text=True)
    got = sorted(x for x in r.stdout.split() if x)
    if got != sorted(ISLES_DIR_FILES):
        bad("folder listing %s" % got)
    for f in ISLES_DIR_FILES:
        if f not in text:
            bad("folder name %s" % f)
    lines.append("    Island Expeditions script folders:       %d == 4, all "
                 "in doc" % len(got))

    # OnCreatureCreate handlers empty (no enemy team spawn)
    empties = 0
    for key in ("sc_verd", "sc_snow", "sc_ungol"):
        m = re.search(r"void OnCreatureCreate\(Creature\* creature\)[^{]*"
                      r"\{(.*?)\n    \}", corpora[key], re.S)
        if m and "GetEntry" not in m.group(1) and "switch" not in m.group(1):
            empties += 1
        elif m and re.search(r"default:\s*break;", m.group(1)) and \
                not re.search(r"case ", m.group(1)):
            empties += 1
    if empties < 2:
        bad("OnCreatureCreate empties %d" % empties)
    if "OnCreatureCreate handlers are empty" not in text:
        bad("empty handler doc")
    lines.append("    empty OnCreatureCreate handlers found:   %d (doc ok)"
                 % empties)

    # upstream TC absence via code search (cached: search API throttles)
    total = 0
    for q in ("IslandExpedition", "%22Island+Expedition%22"):
        got = _tc_search(q)
        if got is None:
            bad("tc search failed")
        else:
            total += got
    if total != 0:
        bad("TC upstream search total %d" % total)
    if "return zero files" not in text:
        bad("zero files doc")
    lines.append("    TC upstream island code search hits:     %d (doc: zero)"
                 % total)

    # queue handler body claims
    ih = corpora["island_h"]
    for lit in ("ROLE_DAMAGE", "KilledMonsterCredit(139310)",
                "KilledMonsterCredit(139309)", "islandQueue.ActivityID"):
        if lit not in ih:
            bad("handler source %s" % lit)
    for lit in ("ROLE_DAMAGE, {ActivityID}", "139310 (Alliance)",
                "139309 (Horde)"):
        if norm(lit) not in flat:
            bad("handler doc %s" % lit)

    # winner mapping + display infos
    ic = corpora["inst_c"]
    if "package.Winner = winnerIsAlliance ? 0 : 1;" not in ic:
        bad("winner tern source")
    if "Winner (0 = Alliance, 1 = Horde)" not in text:
        bad("winner doc")
    if "player->PlayConversation(7504);" not in ic:
        bad("conv7504 source")
    if "conversation 7504 when the Horde wins" not in text:
        bad("conv7504 doc")

    # packet payload size
    if "SMSG_ISLAND_AZERITE_XP_GAIN, 4 + 36 + 36 + 4" not in \
            corpora["islpkt_h"]:
        bad("payload source")
    if "4 + 36 + 36 + 4" not in text:
        bad("payload doc")

    # cross-deliverable consistency with step 1
    try:
        with open(DOC1, encoding="utf-8") as fh:
            doc1 = fh.read()
    except OSError:
        doc1 = ""
        bad("step1 doc unreadable")
    for lit in ("Normal 6,000 Azerite.", "38 = Normal, 39 = Heroic, "
                "40 = Mythic", "45 = PvP (MaxPlayers 6)"):
        if norm(lit) not in norm(doc1):
            bad("step1 missing %s" % lit)
    for lit in ("Normal 6000, Heroic 9000, Mythic 12000, PvP 12000",
                "38          39          40          45"):
        if norm(lit) not in flat:
            bad("step2 missing %s" % lit)
    if not (("6,000" in doc1 or "6000" in doc1) and "6000" in text):
        bad("totals cross-doc")
    lines.append("    step1/step2 totals + difficulty ids cross-doc: ok")

    # coord trace (doc has no map coordinates)
    ok_t, lines_t, missing_t = coord_trace(text, corpora)
    lines.append("    %s" % lines_t[-1].strip())
    if not ok_t:
        bad("coord trace %s" % (missing_t[:3],))
    return fails, lines


def stage5(text, corpora):
    lines, fails = [], []
    probes = [("TODO", "no todo"),
              ("verified by direct inspection", "no direct inspection"),
              ("estimated coordinate", "no estimated coordinate")]
    for extra, key in probes:
        f, _ = run_static(text + "\n%s.\n" % extra)
        r = key in f
        lines.append("    injection probe (%s):%s"
                     % (extra[:28], " detected" if r else " NOT DETECTED"))
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
         "repos/TCDEVEmu/AtalDazar_BFA/contents/DoesNotExist.sql"],
        capture_output=True, text=True)
    absent = res.returncode != 0
    lines.append("    control: bogus repo path 404:                  %s"
                 % ("yes" if absent else "NO"))
    if not absent:
        fails.append("404 control")
    fake = text + "\nInjected 123.456, 789.012, 345.678 triple line.\n"
    ok_t, _lines_t, missing_t = coord_trace(fake, corpora)
    reacted = not ok_t and len(missing_t) >= 1
    lines.append("    coord trace probe (fake triple):               %s"
                 % ("detected" if reacted else "NOT DETECTED"))
    if not reacted:
        fails.append("coord probe")
    return fails, lines


def main():
    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()
    print("=" * 68)
    print("AUDIT: Islands_Enemy_COMPLETED.txt (Islands 2)")
    print("=" * 68)

    fails1, lines1 = run_static(text)
    total1 = len(STATIC_CHECKS) + len(NEGATIVE_CHECKS) + 1
    print("\n[1] Static checks: %d/%d passed" % (total1 - len(fails1),
                                                 total1))
    if fails1:
        print("    FAILED: %s" % ", ".join(fails1))
        for ln in lines1:
            if "MISSING" in ln or "PRESENT" in ln:
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
    corpora = {}
    for key, (repo, path) in FILES.items():
        corpora[key] = gh_content(repo, path)
    for key, (repo, path) in RAW_FILES.items():
        corpora[key] = gh_raw(repo, path)
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
        corpora,
        {"npcs": [("baseXP in source", "int32 baseXP = 3;")]},
        lambda t: t.replace("int32 baseXP = 3;", "int32 baseXP = 4;"))
    print("    reaction to tampered source (verified): %s"
          % ("yes" if probe_undetected == [] else "NO"))
    if probe_undetected != []:
        ok3 = False

    print("\n[4] Derived values recomputed from source bodies")
    fails4, lines4 = stage4(text, corpora)
    for ln in lines4:
        print(ln)
    if fails4:
        print("    DERIVED STAGE FAILED: %s" % ", ".join(str(f) for f in
                                                         fails4))
    doc_probes = [
        ("worldstate", "world states 12930 (Alliance gain)",
         "world states 12931 (Alliance gain)"),
        ("activity id", "Snowblossom Village 1983/1988/1989/1990",
         "Snowblossom Village 1983/1988/1989/1992"),
        ("timer", "verdant 45 s + event at 45 s",
         "verdant 47 s + event at 47 s"),
        ("win check", "wins at 9000 on", "wins at 9002 on"),
    ]
    baseline = set(fails4)
    for label, old, new in doc_probes:
        mutated = text.replace(old, new)
        if mutated == text:
            print("    doc probe (%s):     no-op!" % label)
            fails4.append("probe no-op " + label)
            continue
        pf, _ = stage4(mutated, corpora, probe=True)
        reacted = any(f not in baseline for f in pf)
        print("    doc probe (%s):     %s" % (
            label, "reacts" if reacted else "NOT DETECTED"))
        if not reacted:
            fails4.append("probe " + label)

    print("\n[5] Absence / injection")
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
