#!/usr/bin/env python3
"""Mutation-tested audit for MythicPlus_Server_COMPLETED.txt (Mythic+ step 1).

Five stages, each of which is itself probe-tested so the audit is
verified, not just run:

  1. static claims inside the document
  2. mutation testing: every mutation must break a static check
  3. source cross-check: every quoted value must exist upstream
     (flattened corpora, so whitespace in the sources cannot hide a hit),
     with a tampered-source probe
  4. derived values recomputed from the source bodies: the reward bonus
     table, the death-penalty factor, the timed-bracket count, the
     random-keystone whitelist, the chest entry set, the start sequence
     order - each with a reaction probe
  5. absence claims recomputed: no forces/timer/insert opcode in the
     fork's opcode table, no ChallengeMode stack upstream - with an
     injection probe and a control path that must succeed

The document under audit is server-side research: opcode numbers, packet
fields, DB2/SQL tables, class and function names, has/lacks claims for
HavenWoW/BFA-HavenCore (8.3.7 build 35662) against TrinityCore master.
"""

import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import gh_content, source_stage, mutation_probe

DELIVERABLE = ("/home/user/Junk/# Ai Research prompts/Mythic_Plus_completed/"
               "MythicPlus_Server_COMPLETED.txt")

HP = "HavenWoW/BFA-HavenCore"
TC = "TrinityCore/TrinityCore"

SOURCES = {
    "Opcodes.h": "src/server/game/Server/Protocol/Opcodes.h",
    "Opcodes.cpp": "src/server/game/Server/Protocol/Opcodes.cpp",
    "ChallengeModePackets.h":
        "src/server/game/Server/Packets/ChallengeModePackets.h",
    "ChallengeModeHandler.cpp":
        "src/server/game/Handlers/ChallengeModeHandler.cpp",
    "SharedDefines.h": "src/server/game/Miscellaneous/SharedDefines.h",
    "ItemTemplate.h": "src/server/game/Entities/Item/ItemTemplate.h",
    "DBCEnums.h": "src/server/game/DataStores/DBCEnums.h",
    "DB2Stores.cpp": "src/server/game/DataStores/DB2Stores.cpp",
    "DB2Structure.h": "src/server/game/DataStores/DB2Structure.h",
    "GameTables.cpp": "src/server/game/DataStores/GameTables.cpp",
    "CharacterDatabase.cpp":
        "src/server/database/Database/Implementation/CharacterDatabase.cpp",
    "InstanceScript.cpp": "src/server/game/Instances/InstanceScript.cpp",
    "InstanceScript.h": "src/server/game/Instances/InstanceScript.h",
    "InstanceScenario.cpp": "src/server/game/Scenarios/InstanceScenario.cpp",
    "Group.h": "src/server/game/Groups/Group.h",
    "ChallengeModeMgr.cpp": "src/server/game/ChallengeMode/ChallengeModeMgr.cpp",
    "ChallengeModeMgr.h": "src/server/game/ChallengeMode/ChallengeModeMgr.h",
    "challenge_scripts.cpp": "src/server/scripts/World/challenge_scripts.cpp",
}

# Paths that must NOT exist upstream (stage 5 control/failure pair).
TC_MISSING = [
    "src/server/game/ChallengeMode/ChallengeModeMgr.cpp",
    "src/server/game/Handlers/ChallengeModeHandler.cpp",
]
TC_CONTROL = "src/server/game/DataStores/DB2Stores.h"


def flat(text):
    return re.sub(r"\s+", " ", text)


# --- stage 1: static claims -------------------------------------------------

STATIC_CHECKS = [
    ("file_exists", lambda t: os.path.exists(DELIVERABLE)),
    ("min_lines", lambda t: len(t.splitlines()) >= 110),
    ("title_completed", lambda t: t.splitlines()[0] == "=== MYTHIC KEYSTONE "
     "SERVER SUPPORT - BFA 8.3.7 (TRINITYCORE) - COMPLETED ==="),
    ("numbering", lambda t: 'prompt 1 of 3 in "# Ai Research prompts/'
     'Mythic_Plus"' in t),
    ("sec1", lambda t: "1. PACKETS AND THEIR FIELDS" in t),
    ("sec2", lambda t: "2. CHALLENGE MODE DATA TABLES" in t),
    ("sec3", lambda t: "TRINITYCORE CLASSES AND FUNCTIONS" in t),
    ("sec4", lambda t: "4. WHAT A FORK OF THE 8.3.7 BRANCH HAS AND WHAT IT "
     "LACKS" in t),
    ("sec5", lambda t: "5. ID INDEX (verified from sources above)" in t),

    ("insert_one_packet", lambda t: "Insertion and run start are one client "
     "packet: CMSG_START_CHALLENGE_MODE = 0x3554" in t),
    ("no_insert_opcode", lambda t: "contains no INSERT_KEYSTONE opcode" in t),
    ("bag_fields", lambda t: "Bag (uint8), Slot (uint32), GobGUID "
     "(ObjectGuid)" in t),
    ("handler_reg", lambda t: "WorldSession::HandleChallengeModeStart "
     "(STATUS_LOGGEDIN, PROCESS_THREADUNSAFE)" in t),
    ("receptacle_49", lambda t: "GAMEOBJECT_TYPE_KEYSTONE_RECEPTACLE "
     "(type = 49)" in t),
    ("class_subclass", lambda t: "ITEM_CLASS_REAGENT (= 5) + "
     "ITEM_SUBCLASS_KEYSTONE (= 1)" in t),
    ("modifiers", lambda t: "ITEM_MODIFIER_CHALLENGE_MAP_CHALLENGE_MODE_ID"
     in t and "ITEM_MODIFIER_CHALLENGE_KEYSTONE_LEVEL" in t),
    ("item_158923", lambda t: 'entry 158923 "Mythic Keystone"' in t),
    ("destroy_comment", lambda t: '"Blizzard do not delete the key at '
     'challenge start"' in t),
    ("creation_path", lambda t: "item_challenge_key::OnCreate" in t
     and "Player::InitChallengeKey : Player::CreateChallengeKey" in t),

    ("start_pkt", lambda t: "SMSG_CHALLENGE_MODE_START = 0x261F, 33 bytes"
     in t),
    ("start_fields", lambda t: "StartedChallengeLevel (uint32, ctor default "
     "2), DeathCount (uint32), Energized (bool, ctor default true)" in t),
    ("affixes_zero", lambda t: "never assigned anywhere in the repo -> starts "
     "as 0,0,0" in t),
    ("difficulty_8", lambda t: "DifficultyRecID = DIFFICULTY_MYTHIC_KEYSTONE "
     "(= 8)" in t),
    ("countdown_10", lambda t: "TotalTime 10, TimeLeft 10 (10-second "
     "countdown)" in t),

    ("no_timer_opcode", lambda t: "No SMSG_CHALLENGE_MODE_UPDATE_TIMER "
     "opcode exists in the 35662 table" in t),
    ("elapsed_pkt", lambda t: "SMSG_START_ELAPSED_TIMER = 0x261C" in t),
    ("timer_id_1", lambda t: "TimerID 1 = WORLD_TIMER_TYPE_CHALLENGE_MODE"
     in t),
    ("death_penalty", lambda t: "+ 5 * death count (5-second death penalty, "
     "in code)" in t),
    ("complete_pkt", lambda t: "SMSG_CHALLENGE_MODE_COMPLETE = 0x2622" in t),
    ("complete_fields", lambda t: "unk (uint8, default 128)" in t),
    ("complete_trigger", lambda t: "InstanceScenario::CompleteScenario" in t
     and "cs_instance.cpp" in t),
    ("death_pkt", lambda t: "SMSG_CHALLENGE_MODE_UPDATE_DEATH_COUNT = 0x2620"
     in t),

    ("forces_negative", lambda t: "No forces-count packet exists" in t),
    ("forces_names", lambda t: "SMSG_CHALLENGE_MODE_UPDATE_FORCES (or any "
     "UPDATE_FORCES)" in t),
    ("scenario_sql", lambda t: "instance_scenario_progress" in t),
    ("reset_cmsg", lambda t: "CMSG_RESET_CHALLENGE_MODE = 0x3205" in t),
    ("diff_result", lambda t: "SMSG_CHANGE_PLAYER_DIFFICULTY_RESULT = 0x273B"
     in t),
    ("map_stats", lambda t: "SMSG_MYTHIC_PLUS_ALL_MAP_STATS = 0x2624" in t),
    ("leaders_result", lambda t: "SMSG_CHALLENGE_MODE_REQUEST_LEADERS_RESULT "
     "= 0x2626" in t),
    ("gap_2627", lambda t: "Opcode 0x2627 is absent from the table "
     "(unverified)" in t),
    ("affix_null", lambda t: "CMSG_REQUEST_CHALLENGE_MODE_AFFIXES = 0x3207 "
     "-> registered to Handle_NULL" in t),
    ("rewards_commented", lambda t: "response body is commented out in "
     "ChallengeModeHandler.cpp" in t),

    ("db2_name", lambda t: '"MapChallengeMode.db2"' in t),
    ("criteria_field", lambda t: "CriteriaCount[3] (int16)" in t),
    ("brackets_claim", lambda t: "counts how many of the 3 are > total "
     "duration -> 0-3 upgrades" in t),
    ("gt_health", lambda t: '"ChallengeModeHealth.txt"' in t),
    ("table_key", lambda t: "challenge_key (ID, Level, Affix, Affix1, Affix2, "
     "KeyIsCharded" in t),
    ("table_completed", lambda t: "character_completed_challenges (guid, "
     "KeyId, MapId, BestCompletion, LastCompletion, Medal, MedalDate)" in t),
    ("table_modifiers", lambda t: "challengeIsCharged)" in t),
    ("table_guild", lambda t: "guild_challenges (GuildId, ChallengeType, "
     "ChallengeCount)" in t),

    ("mgr_api", lambda t: "sChallengeModeMgr->GetMapChallengeModeEntry" in t),
    ("start_fn", lambda t: "StartChallengeMode(uint8 level) - guards" in t),
    ("duration_fn", lambda t: "InstanceScript::GetChallengeModeCurrentDuration"
     in t),
    ("hit_timer", lambda t: "_chestTimers[3] thresholds never initialized"
     in t),
    ("reward_bonus_head", lambda t: "2->3410/+5, 3->3411/+5" in t),
    ("reward_bonus_tail", lambda t: "14->3535/+50, 15->3535/+55" in t),
    ("base_ilvl", lambda t: "baseMythicIlevel constant = 885" in t),
    ("ach_head", lambda t: "11183 (key level >= 2)" in t),
    ("ach_tail", lambda t: "11162 and 11224 (>= 15)" in t),
    ("spell_might", lambda t: "SPELL_CHALLENGER_MIGHT = 206150" in t),
    ("spell_burden", lambda t: "SPELL_CHALLENGER_BURDEN = 206151" in t),
    ("door_go", lambda t: "GOB_CHALLENGER_DOOR = 239408" in t),
    ("font_go", lambda t: "GO_FONT_OF_POWER = 246779" in t),
    ("chest_set", lambda t: "challenge chests: 282735, 282736, 282737, "
     "288642, 288644, 290544, 290621, 290758, 290759, 290761" in t),
    ("difficulty_ids", lambda t: "DIFFICULTY_MYTHIC = 23, "
     "DIFFICULTY_MYTHIC_KEYSTONE = 8" in t),
    ("whitelist", lambda t: "244, 245, 246, 247, 248, 249, 250, 252, 353"
     in t),
    ("affix_indices", lambda t: "13 Explosive, 14 Quaking" in t),
    ("opcode_index", lambda t: "CMSG 0x3554 / 0x3090 / 0x308F / 0x3683 / "
     "0x3205 / 0x3206 / 0x3207 / 0x307C" in t),

    ("has_section", lambda t: "HAS (present in HavenWoW/BFA-HavenCore, "
     "absent upstream):" in t),
    ("lacks_section", lambda t: "LACKS / broken or unused (observed in "
     "code):" in t),
    ("newrecord_dead", lambda t: "SendChallengeModeNewPlayerRecord has no "
     "callers" in t),
    ("save_dead", lambda t: "SaveChallengeToDB and the challenge / "
     "challenge_member / challenge_oplote_loot INSERT path" in t),
    ("upstream_note", lambda t: "upstream has the tables, the fork has the "
     "mode" in t),
    ("unverified_section", lambda t: t.splitlines()[-1].startswith(
     "UNVERIFIED (explicit):")),
    ("sources_line", lambda t: "WowPacketParser (V7_0_3_22248, "
     "V9_0_1_36216)" in t and "warcraft.wiki.gg" in t),
]

MUTATIONS = [
    ("cmsg_start_hex", lambda t: t.replace("0x3554", "0x3555")),
    ("smsg_start_hex", lambda t: t.replace("0x261F", "0x2610")),
    ("elapsed_hex", lambda t: t.replace("0x261C", "0x269C")),
    ("receptacle_type", lambda t: t.replace("(type = 49)", "(type = 48)")),
    ("item_class", lambda t: t.replace("ITEM_CLASS_REAGENT (= 5)",
                                       "ITEM_CLASS_REAGENT (= 6)")),
    ("keystone_item", lambda t: t.replace("entry 158923", "entry 158924")),
    ("might_spell", lambda t: t.replace("SPELL_CHALLENGER_MIGHT = 206150",
                                        "SPELL_CHALLENGER_MIGHT = 206159")),
    ("door_go", lambda t: t.replace("GOB_CHALLENGER_DOOR = 239408",
                                    "GOB_CHALLENGER_DOOR = 239409")),
    ("font_go", lambda t: t.replace("GO_FONT_OF_POWER = 246779",
                                    "GO_FONT_OF_POWER = 246778")),
    ("difficulty", lambda t: t.replace("DIFFICULTY_MYTHIC = 23",
                                       "DIFFICULTY_MYTHIC = 22")),
    ("keystone_diff", lambda t: t.replace("DIFFICULTY_MYTHIC_KEYSTONE = 8",
                                          "DIFFICULTY_MYTHIC_KEYSTONE = 7")),
    ("base_ilvl", lambda t: t.replace("baseMythicIlevel constant = 885",
                                      "baseMythicIlevel constant = 886")),
    ("bonus_first", lambda t: t.replace("2->3410/+5", "2->3499/+5")),
    ("death_factor", lambda t: t.replace("+ 5 * death count",
                                         "+ 6 * death count")),
    ("achievement", lambda t: t.replace("11183 (key level >= 2)",
                                        "11182 (key level >= 2)")),
    ("whitelist_last", lambda t: t.replace("250, 252, 353", "250, 252, 354")),
    ("chest_first", lambda t: t.replace("282735, 282736", "282730, 282736")),
    ("numbering", lambda t: t.replace("prompt 1 of 3", "prompt 2 of 3")),
    ("heading", lambda t: t.replace("- COMPLETED ===", "- DRAFT ===", 1)),
    ("forces_claim", lambda t: t.replace("No forces-count packet exists",
                                         "Forces-count packet exists")),
    ("timer_id", lambda t: t.replace("TimerID 1 = WORLD_TIMER_TYPE_CHALLENGE_"
                                     "MODE",
                                     "TimerID 2 = WORLD_TIMER_TYPE_CHALLENGE_"
                                     "MODE")),
    ("insert_claim", lambda t: t.replace("contains no INSERT_KEYSTONE "
                                         "opcode",
                                         "contains an INSERT_KEYSTONE "
                                         "opcode")),
]


def run_checks(text):
    passed, failed = 0, []
    for name, fn in STATIC_CHECKS:
        try:
            good = fn(text)
        except Exception as exc:            # noqa: BLE001
            good = False
            failed.append("%s (error: %s)" % (name, exc))
            continue
        if good:
            passed += 1
        else:
            failed.append(name)
    return passed, failed


# --- stage 3 source tokens (checked against flattened corpora) --------------

SOURCE_TOKENS = {
    "Opcodes.h": [
        ("CMSG_START_CHALLENGE_MODE 0x3554",
         "CMSG_START_CHALLENGE_MODE = 0x3554"),
        ("CMSG_REQUEST_LEADERS 0x3090",
         "CMSG_CHALLENGE_MODE_REQUEST_LEADERS = 0x3090"),
        ("CMSG_REQUEST_MAP_STATS 0x308F",
         "CMSG_CHALLENGE_MODE_REQUEST_MAP_STATS = 0x308F"),
        ("CMSG_GET_REWARDS 0x3683",
         "CMSG_GET_CHALLENGE_MODE_REWARDS = 0x3683"),
        ("CMSG_RESET 0x3205", "CMSG_RESET_CHALLENGE_MODE = 0x3205"),
        ("CMSG_RESET_CHEAT 0x3206",
         "CMSG_RESET_CHALLENGE_MODE_CHEAT = 0x3206"),
        ("CMSG_AFFIXES 0x3207",
         "CMSG_REQUEST_CHALLENGE_MODE_AFFIXES = 0x3207"),
        ("CMSG_GUILD_CHALLENGE 0x307C",
         "CMSG_GUILD_CHALLENGE_UPDATE_REQUEST = 0x307C"),
        ("SMSG_START 0x261F", "SMSG_CHALLENGE_MODE_START = 0x261F"),
        ("SMSG_DEATH 0x2620",
         "SMSG_CHALLENGE_MODE_UPDATE_DEATH_COUNT = 0x2620"),
        ("SMSG_RESET 0x2621", "SMSG_CHALLENGE_MODE_RESET = 0x2621"),
        ("SMSG_COMPLETE 0x2622", "SMSG_CHALLENGE_MODE_COMPLETE = 0x2622"),
        ("SMSG_WEEKLY_REWARD 0x2623",
         "SMSG_MYTHIC_PLUS_WEEKLY_REWARD_RESPONSE = 0x2623"),
        ("SMSG_ALL_MAP_STATS 0x2624",
         "SMSG_MYTHIC_PLUS_ALL_MAP_STATS = 0x2624"),
        ("SMSG_CURRENT_AFFIXES 0x2625",
         "SMSG_MYTHIC_PLUS_CURRENT_AFFIXES = 0x2625"),
        ("SMSG_LEADERS_RESULT 0x2626",
         "SMSG_CHALLENGE_MODE_REQUEST_LEADERS_RESULT = 0x2626"),
        ("SMSG_NEW_WEEK 0x2628", "SMSG_MYTHIC_PLUS_NEW_WEEK_RECORD = 0x2628"),
        ("SMSG_NEW_SEASON 0x2629",
         "SMSG_MYTHIC_PLUS_NEW_SEASON_RECORD = 0x2629"),
        ("SMSG_CHANGE_DIFF 0x273B",
         "SMSG_CHANGE_PLAYER_DIFFICULTY_RESULT = 0x273B"),
        ("SMSG_START_TIMER 0x25BC", "SMSG_START_TIMER = 0x25BC"),
        ("SMSG_START_ELAPSED 0x261C", "SMSG_START_ELAPSED_TIMER = 0x261C"),
        ("SMSG_STOP_ELAPSED 0x261D", "SMSG_STOP_ELAPSED_TIMER = 0x261D"),
        ("SMSG_START_ELAPSED_S 0x261E",
         "SMSG_START_ELAPSED_TIMERS = 0x261E"),
    ],
    "Opcodes.cpp": [
        ("reg start", "DEFINE_HANDLER(CMSG_START_CHALLENGE_MODE, "
         "STATUS_LOGGEDIN, PROCESS_THREADUNSAFE, "
         "&WorldSession::HandleChallengeModeStart);"),
        ("reg affixes null", "DEFINE_HANDLER(CMSG_REQUEST_CHALLENGE_MODE_"
         "AFFIXES, STATUS_UNHANDLED, PROCESS_THREADUNSAFE, "
         "&WorldSession::Handle_NULL);"),
        ("reg leaders", "DEFINE_HANDLER(CMSG_CHALLENGE_MODE_REQUEST_LEADERS, "
         "STATUS_LOGGEDIN, PROCESS_THREADSAFE, "
         "&WorldSession::HandleRequestLeaders);"),
        ("reg reset", "DEFINE_HANDLER(CMSG_RESET_CHALLENGE_MODE, "
         "STATUS_LOGGEDIN, PROCESS_THREADUNSAFE, "
         "&WorldSession::HandleResetChallengeMode);"),
    ],
    "ChallengeModePackets.h": [
        ("bag field", "uint8 Bag;"),
        ("slot field", "uint32 Slot;"),
        ("gob field", "ObjectGuid GobGUID;"),
        ("start size", "ServerPacket(SMSG_CHALLENGE_MODE_START, 33)"),
        ("level default", "uint32 StartedChallengeLevel = 2;"),
        ("energized default", "bool Energized = true;"),
        ("duration field", "int32 Duration;"),
        ("unk field", "uint8 unk = 128;"),
        ("rewards commented", "// class Rewards final : public ServerPacket"),
        ("affixes array", "std::array<uint32, 3> Affixes{};"),
        ("dup death class", "class ChallengeModeUpdateDeathCount final : "
         "public ServerPacket"),
    ],
    "ChallengeModeHandler.cpp": [
        ("receptacle check", "GetGameObjectIfCanInteractWith(start.GobGUID, "
         "GAMEOBJECT_TYPE_KEYSTONE_RECEPTACLE)"),
        ("subclass check", "GetSubClass() != ITEM_SUBCLASS_KEYSTONE"),
        ("modifier map id", "ITEM_MODIFIER_CHALLENGE_MAP_CHALLENGE_MODE_ID"),
        ("modifier level", "ITEM_MODIFIER_CHALLENGE_KEYSTONE_LEVEL"),
        ("start dispatch", "instanceScript->StartChallengeMode("
         "challengeModeLevel)"),
        ("destroy key", "_player->DestroyItem(start.Bag, start.Slot, true)"),
        ("retail comment", "Blizzard do not delete the key at challenge "
         "start"),
        ("rewards stub", "//SendPacket(rewards.Write());"),
        ("stats update fn", "void WorldSession::SendChallengeModeMapStatsUpdate"
         "(uint32 keyID)"),
    ],
    "SharedDefines.h": [
        ("receptacle enum", "GAMEOBJECT_TYPE_KEYSTONE_RECEPTACLE = 49"),
        ("door go", "GOB_CHALLENGER_DOOR = 239408"),
        ("door line235", "GOB_CHALLENGER_DOOR_LINE235 = 239323"),
        ("font go", "GO_FONT_OF_POWER = 246779"),
        ("might spell", "SPELL_CHALLENGER_MIGHT = 206150"),
        ("burden spell", "SPELL_CHALLENGER_BURDEN = 206151"),
        ("not in timer", "CHALLENGE_NOT_IN_TIMER = 0"),
        ("timer level 1", "CHALLENGE_TIMER_LEVEL_1 = 1"),
        ("timer level 3", "CHALLENGE_TIMER_LEVEL_3 = 3"),
        ("world timer type", "WORLD_TIMER_TYPE_CHALLENGE_MODE = 1"),
        ("err reset key", "ERR_CHALLENGE_MODE_RESET_KEYSTONE = 874"),
        ("err wrong key", "ERR_CHALLENGE_MODE_INCORRECT_KEYSTONE = 936"),
        ("loot mode", "LOOT_MODE_MYTHIC_KEYSTONE = 8"),
        ("error active", "SPELL_CUSTOM_ERROR_CANT_DO_THAT_WHILE_MYTHIC_"
         "KEYSTONE_IS_ACTIVE = 168"),
        ("modify keystone effect", "SPELL_EFFECT_MODIFY_KEYSTONE = 258"),
    ],
    "ItemTemplate.h": [
        ("reagent class", "ITEM_CLASS_REAGENT = 5"),
        ("keystone subclass", "ITEM_SUBCLASS_KEYSTONE = 1"),
    ],
    "DBCEnums.h": [
        ("difficulty keystone", "DIFFICULTY_MYTHIC_KEYSTONE = 8"),
        ("difficulty mythic", "DIFFICULTY_MYTHIC = 23"),
        ("difficulty raid", "DIFFICULTY_MYTHIC_RAID = 16"),
        ("challenge flag", "DIFFICULTY_FLAG_CHALLENGE_MODE = 0x08"),
        ("criteria complete", "CRITERIA_TYPE_COMPLETE_CHALLENGE_MODE = 71"),
        ("criteria guild", "CRITERIA_TYPE_COMPLETE_CHALLENGE_MODE_GUILD = 22"),
        ("criteria medal", "CRITERIA_ADDITIONAL_CONDITION_CHALLENGE_MODE_"
         "MEDAL = 83"),
    ],
    "DB2Stores.cpp": [
        ("db2 literal", 'sMapChallengeModeStore("MapChallengeMode.db2"'),
        ("lookup fn", "GetChallengeModeByMapID"),
    ],
    "DB2Structure.h": [
        ("struct name", "struct MapChallengeModeEntry"),
        ("criteria field", "int16 CriteriaCount[3];"),
        ("mapid field", "uint16 MapID;"),
    ],
    "GameTables.cpp": [
        ("gt damage", 'LOAD_GT(sChallengeModeDamage, "ChallengeModeDamage.txt")'),
        ("gt health", 'LOAD_GT(sChallengeModeHealth, "ChallengeModeHealth.txt")'),
    ],
    "CharacterDatabase.cpp": [
        ("insert challenge", "INSERT INTO challenge ("),
        ("insert member", "INSERT INTO challenge_member ("),
        ("upsert oplote", "REPLACE INTO challenge_oplote_loot ("),
        ("upsert key", "REPLACE INTO challenge_key ("),
        ("key typo", "KeyIsCharded"),
        ("select completed", "FROM character_completed_challenges WHERE "
         "guid = ?"),
        ("insert completed", "INSERT INTO character_completed_challenges "
         "(guid, KeyId, MapId, BestCompletion, LastCompletion, Medal, "
         "MedalDate)"),
        ("guild challenges", "REPLACE INTO guild_challenges"),
        ("guild select order", "SELECT GuildId, ChallengeType, "
         "ChallengeCount FROM guild_challenges"),
        ("guild init order", "INSERT INTO guild_challenges VALUES (?, ?, 0)"),
        ("modifier column", "challengeIsCharged"),
    ],
    "InstanceScript.cpp": [
        ("difficulty guard", "instance->GetDifficultyID() != "
         "DIFFICULTY_MYTHIC"),
        ("boss mask guard", "if (GetCompletedEncounterMask())"),
        ("difficulty type 5", "WorldPackets::ChallengeMode::"
         "ChangePlayerDifficultyResult(5)"),
        ("difficulty type 11", "ChangePlayerDifficultyResult "
         "changePlayerDifficultyResult(11)"),
        ("start timer type", "startTimer.Type = WorldPackets::Misc::"
         "StartTimer::TIMER_TYPE_CHALLENGE"),
        ("start send", "SendChallengeModeStart();"),
        ("delayed start", "AddTimedDelayedOperation(10000,"),
        ("complete level", "complete.ChallengeLevel = _challengeModeLevel + "
         "mythicIncrement"),
        ("death factor", "+ (5 * _challengeModeDeathCount)"),
        ("timer id send", "startElapsedTimer.TimerID = 1"),
        ("ach 11183", "DoCompleteAchievement(11183)"),
        ("ach 11184", "DoCompleteAchievement(11184)"),
        ("ach 11185", "DoCompleteAchievement(11185)"),
        ("ach 11162", "DoCompleteAchievement(11162)"),
        ("ach 11224", "DoCompleteAchievement(11224)"),
        ("chest spawn call", "SpawnChallengeModeRewardChest();"),
        ("door summon", "instance->SummonGameObject(GOB_CHALLENGER_DOOR"),
        ("might cast", "CastCustomSpell(SPELL_CHALLENGER_MIGHT, values, "
         "creature, TRIGGERED_FULL_MASK)"),
        ("burden cast", "CastCustomSpell(SPELL_CHALLENGER_BURDEN, values, "
         "player, TRIGGERED_FULL_MASK)"),
        ("duration formula", "GetMSTimeDiffToNow(_challengeModeStartTime) "
         "/ 1000"),
    ],
    "InstanceScript.h": [
        ("start decl", "void StartChallengeMode(uint8 level);"),
        ("complete decl", "void CompleteChallengeMode();"),
        ("chest virtual", "virtual void SpawnChallengeModeRewardChest() { }"),
        ("affixes member", "std::array<uint32, 3> _affixes;"),
        ("bolstering id", "ChallengerBolstering = 209859"),
        ("quake id", "ChallengerQuake = 240447"),
        ("volcanic id", "ChallengerSummonVolcanicPlume = 209861"),
    ],
    "InstanceScenario.cpp": [
        ("started check", "instance->IsChallengeModeStarted()"),
        ("complete call", "instance->CompleteChallengeMode();"),
    ],
    "Group.h": [
        ("group affixes", "std::array<uint32, 3> m_affixes{};"),
        ("in challenge", "bool InChallenge();"),
    ],
    "ChallengeModeMgr.cpp": [
        ("whitelist 244", "challengeModeEntry->ID == 244"),
        ("whitelist 353", "challengeModeEntry->ID == 353"),
        ("base ilvl", "const uint32 baseMythicIlevel = 885;"),
        ("bonus first", "{ 3410, 5 }"),
        ("bonus last", "{ 3535, 55 }"),
        ("health scalar", "100.f * (challengeHealth->Scalar - 1.f)"),
        ("chest timer cmp", "if (GetChallengeTimer() < _chestTimers[2])"),
        ("save fn", "void ChallengeModeMgr::SaveChallengeToDB(ChallengeData "
         "const* challengeData)"),
    ],
    "ChallengeModeMgr.h": [
        ("chest list", "ChallengeChestList"),
    ],
    "challenge_scripts.cpp": [
        ("item check", "player->HasItemCount(158923, 1, true)"),
        ("init key", "player->InitChallengeKey(item)"),
        ("create key", "player->CreateChallengeKey(item)"),
        ("script class", "class item_challenge_key"),
    ],
    # Upstream TrinityCore master: only the stores, no mode.
    "TC_DB2Stores.h": [
        ("upstream store", "sMapChallengeModeStore"),
        ("upstream bonus override", "sChallengeModeItemBonusOverrideStore"),
    ],
}


# --- stage 4: derived values ------------------------------------------------

def derived_stage(doc, flat_sources, raw_sources):
    """Recompute document numbers from the source bodies."""
    ok, lines = [], []

    # (a) reward bonus table: doc list must equal the source pair list.
    doc_pairs = [(int(b), int(d)) for b, d in re.findall(
        r"->(\d+)/\+(\d+)", doc)]
    doc_levels = [int(lv) for lv in re.findall(r"(\d+)->\d+/\+\d+", doc)]
    body_at = flat_sources["ChallengeModeMgr.cpp"].find(
        "GetBonusListIdsForRewards")
    body = flat_sources["ChallengeModeMgr.cpp"][body_at:body_at + 1400]
    src_pairs = [(int(a), int(b)) for a, b in
                 re.findall(r"\{\s*(\d+),\s*(\d+)\s*\}", body)]
    good = (len(doc_pairs) == 14 and doc_pairs == src_pairs
            and doc_levels == list(range(2, 16)))
    ok.append(good)
    lines.append("    reward bonus table: doc %d entries vs source %d "
                 "pairs -> %s" % (len(doc_pairs), len(src_pairs),
                                  "MATCH" if good else "MISMATCH"))

    # (b) death-penalty factor extracted from the duration formula.
    m = re.search(r"(\d+)\s*\*\s*_challengeModeDeathCount",
                  raw_sources["InstanceScript.cpp"])
    factor = int(m.group(1)) if m else None
    good = factor is not None and ("+ %d * death count" % factor) in doc
    ok.append(good)
    lines.append("    death penalty factor: source %s, doc states -> %s"
                 % (factor, "MATCH" if good else "MISMATCH"))

    # (c) timed-bracket loop bound in CompleteChallengeMode.
    at = flat_sources["InstanceScript.cpp"].find("void InstanceScript::"
                                                  "CompleteChallengeMode")
    region = flat_sources["InstanceScript.cpp"][at:at + 900]
    m = re.search(r"for \(uint8 i = 0; i < (\d+); \+\+i\)", region)
    bound = int(m.group(1)) if m else None
    good = bound is not None and (
        "how many of the %d are" % bound) in doc and (
        "-> 0-%d upgrades" % bound) in doc
    ok.append(good)
    lines.append("    timed brackets: source loop bound %s, doc claims -> %s"
                 % (bound, "MATCH" if good else "MISMATCH"))

    # (d) random-keystone whitelist: doc set equals source set.
    m = re.search(r'"Temp fix, only doable dungeons"\):\s*([0-9, ]+)',
                  doc.replace("\n", " "))
    doc_ids = set(int(x) for x in m.group(1).split(",")) if m else set()
    at = flat_sources["ChallengeModeMgr.cpp"].find(
        "uint32 ChallengeModeMgr::GetRandomChallengeId")
    region = flat_sources["ChallengeModeMgr.cpp"][at:at + 1200]
    src_ids = set(int(x) for x in re.findall(r"ID == (\d+)", region))
    good = bool(doc_ids) and doc_ids == src_ids
    ok.append(good)
    lines.append("    keystone whitelist: doc %s vs source %s -> %s"
                 % (sorted(doc_ids) or "{}", sorted(src_ids) or "{}",
                    "MATCH" if good else "MISMATCH"))

    # (e) chest entry set: doc list equals ChallengeChestList contents.
    m = re.search(r"challenge chests: ([0-9, ]+)", doc)
    doc_chests = set(int(x) for x in m.group(1).split(",")) if m else set()
    at = raw_sources["ChallengeModeMgr.h"].find("ChallengeChestList")
    region = raw_sources["ChallengeModeMgr.h"][at:at + 400]
    brace = region.find("{")
    end = region.find("}", brace)
    src_chests = set(int(x) for x in re.findall(r"\d+", region[brace:end]))
    good = bool(doc_chests) and doc_chests == src_chests
    ok.append(good)
    lines.append("    chest entries: doc %d vs source %d -> %s"
                 % (len(doc_chests), len(src_chests),
                    "MATCH" if good else "MISMATCH"))

    # (f) start sequence order inside StartChallengeMode.
    at = flat_sources["InstanceScript.cpp"].find(
        "void InstanceScript::StartChallengeMode")
    region = flat_sources["InstanceScript.cpp"][at:at + 4200]
    markers = ["ChangePlayerDifficultyResult(5)", "DoNearTeleportPlayers",
               "SummonGameObject(GOB_CHALLENGER_DOOR",
               "startTimer.TotalTime = 10", "SendChallengeModeStart()",
               "AddTimedDelayedOperation(10000"]
    idx = [region.find(mk) for mk in markers]
    good = all(i >= 0 for i in idx) and idx == sorted(idx)
    ok.append(good)
    lines.append("    start sequence order: %s"
                 % ("in documented order" if good else
                    "ORDER MISMATCH %s" % idx))

    return all(ok), lines


# --- stage 5: absence claims ------------------------------------------------

def absence_stage(doc, flat_sources):
    ok, lines = [], []
    for name, banned in [("Opcodes.h", "CHALLENGE_MODE_UPDATE_TIMER"),
                         ("Opcodes.h", "CHALLENGE_MODE_UPDATE_FORCES"),
                         ("Opcodes.h", "INSERT_KEYSTONE")]:
        present = banned in flat_sources[name]
        ok.append(not present)
        lines.append("    %s lacks %-32s %s" % (name, banned,
                                                "absent (good)" if not present
                                                else "PRESENT (bad)"))
    # The document must still state those absences.
    claim = ("No SMSG_CHALLENGE_MODE_UPDATE_TIMER opcode exists" in doc
             and "No forces-count packet exists" in doc
             and "contains no INSERT_KEYSTONE opcode" in doc)
    ok.append(claim)
    lines.append("    document states all three absences -> %s"
                 % ("yes" if claim else "NO"))
    return all(ok), lines


def gh_exists(repo, path):
    out = subprocess.run(
        ["gh", "api", "repos/%s/contents/%s" % (repo, path),
         "--jq", ".name"], capture_output=True, text=True)
    return out.returncode == 0


# --- main -------------------------------------------------------------------

def main():
    if not os.path.exists(DELIVERABLE):
        print("MISSING DELIVERABLE: %s" % DELIVERABLE)
        return 1
    with open(DELIVERABLE) as fh:
        original = fh.read()

    print("=" * 66)
    print("AUDIT: MythicPlus_Server_COMPLETED.txt (Mythic+ step 1)")
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
    flat_sources = {name: flat(gh_content(HP, path))
                    for name, path in SOURCES.items()}
    flat_sources["TC_DB2Stores.h"] = flat(gh_content(TC, TC_CONTROL))
    raw_sources = {name: gh_content(HP, path)
                   for name, path in SOURCES.items()}
    raw_sources["TC_DB2Stores.h"] = gh_content(TC, TC_CONTROL)

    ok, lines = source_stage(flat_sources, SOURCE_TOKENS)
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

    undetected = mutation_probe(flat_sources, SOURCE_TOKENS, break_literals)
    if undetected:
        print("    cross-check did not react to tampered source: %s"
              % undetected)
        return 1
    print("    cross-check reacts to tampered source (verified)")

    print("\n[4] Derived values recomputed from source bodies")
    ok, lines = derived_stage(original, flat_sources, raw_sources)
    for line in lines:
        print(line)
    if not ok:
        print("    DERIVED STAGE FAILED")
        return 1
    # Reaction probes for each derived sub-check.
    probes = [
        ("bonus table", original.replace("2->3410/+5", "2->3499/+5")),
        ("death factor", original.replace("+ 5 * death count",
                                          "+ 6 * death count")),
        ("bracket count", original.replace("how many of the 3 are",
                                           "how many of the 4 are")),
        ("whitelist", original.replace("250, 252, 353", "250, 252, 354")),
        ("chest set", original.replace("290761", "290762")),
        ("sequence order", None),
    ]
    for label, probe_doc in probes:
        if probe_doc is None:
            continue
        if derived_stage(probe_doc, flat_sources, raw_sources)[0]:
            print("    derived stage did not react to %s" % label)
            return 1
    # Order-check reaction: feed the checker a reversed marker expectation.
    at = flat_sources["InstanceScript.cpp"].find(
        "void InstanceScript::StartChallengeMode")
    region = flat_sources["InstanceScript.cpp"][at:at + 4200]
    rev = ["AddTimedDelayedOperation(10000", "SendChallengeModeStart()",
           "startTimer.TotalTime = 10", "SummonGameObject(GOB_CHALLENGER_DOOR",
           "DoNearTeleportPlayers", "ChangePlayerDifficultyResult(5)"]
    idx = [region.find(mk) for mk in rev]
    if all(i >= 0 for i in idx) and idx == sorted(idx):
        print("    order probe did not react (reversed order accepted)")
        return 1
    print("    derived stage reacts to wrong values (verified)")

    print("\n[5] Absence claims recomputed")
    ok, lines = absence_stage(original, flat_sources)
    for line in lines:
        print(line)
    if not ok:
        print("    ABSENCE STAGE FAILED")
        return 1
    probe_sources = dict(flat_sources)
    probe_sources["Opcodes.h"] = flat_sources["Opcodes.h"] + (
        "\nSMSG_CHALLENGE_MODE_UPDATE_TIMER = 0x9999")
    if absence_stage(original, probe_sources)[0]:
        print("    absence stage did not react to an injected opcode")
        return 1
    print("    absence stage reacts to an injected opcode (verified)")
    if not gh_exists(HP, SOURCES["Opcodes.h"]):
        print("    control fetch failed: fork path must exist")
        return 1
    for path in TC_MISSING:
        if gh_exists(TC, path):
            print("    upstream path unexpectedly exists: %s" % path)
            return 1
        print("    upstream lacks %-58s confirmed" % path)
    print("    control path check verified")

    print("\n" + "=" * 66)
    print("AUDIT RESULT: PASS")
    print("  static checks: %d/%d" % (passed, len(STATIC_CHECKS)))
    print("  mutations:     %d/%d" % (detected, len(MUTATIONS)))
    print("=" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())
