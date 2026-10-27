#!/usr/bin/env python3
"""Audit Transmog_Code.txt - STEP 139 (task 17).

Families: S title/scope/sections, T tables+columns, M TransmogSource values,
C CanAddAppearance tests, B bind+lookup paths, P server grant paths,
D storage/hidden, X differences vs retail/master, L limits, R server-source
block, H hygiene (programmatic).
Substring containment on single lines (wrap-safe). Self-test mutates the
payload and requires >= 1 failing check per mutation; each literal must occur
exactly once in the payload.
"""
import sys
from pathlib import Path

PAYLOAD = Path(__file__).resolve().parent / "Transmog_Code.txt"
CHECKS = []


def add(fam, *needles):
    for n in needles:
        CHECKS.append((fam, n))


# --- S: title, scope, sections --------------------------------------------
add("S",
    "TRANSMOG COLLECTION - THE DATA AND THE SERVER CODE, 8.3.7 (BUILD 35662)",
    "Scope: the tables that decide whether an appearance can be collected, the",
    "8.3.7. Two sources are used and kept apart throughout:",
    "  the client   the DB2 tables of build 8.3.7.35662, read row by row;",
    "  the server   Titans-Project/BfaCore-Reforged, a TrinityCore-derived C++",
    "               server for 8.3.7.35662. It is a community core, not a Blizzard",
    "               or TrinityCore release; no official TrinityCore 8.3.7 branch",
    "               exists, so nothing here is quoted from TrinityCore master except",
    "               in the one section that compares the two.",
    "File and line numbers refer to that core at its archived HEAD.",
    "THE CHAIN OF TABLES",
    "THE TABLES, FIELD BY FIELD",
    "THE TRANSMOGSOURCE TYPE COLUMN",
    "WHAT MAKES AN APPEARANCE UNCOLLECTIBLE",
    "WHERE THE BIND IS TESTED",
    "EVERY SERVER PATH THAT GRANTS AN APPEARANCE",
    "TEMPORARY VERSUS PERMANENT, AND THE TWO CLOCKS",
    "HOW IT IS STORED AND SENT",
    "WHAT THE SERVER IGNORES",
    "DIFFERENCES FROM RETAIL AND FROM TRINITYCORE MASTER",
    "LIMITS OF THIS FILE",
    )

# --- T: tables, columns, row counts ---------------------------------------
add("T",
    "One collectible appearance is one row of ItemModifiedAppearance. Everything",
    "  ItemModifiedAppearance.ID                 the number the collection stores",
    "    .ItemAppearanceID  -> ItemAppearance     ItemDisplayInfoID, icon, display",
    "  ItemModifiedAppearance.ItemAppearanceID  <-  TransmogSetItem",
    "either fills the same wardrobe entry, while the collection bit for the other",
    "ItemModifiedAppearance - six columns, typed as the 8.3.7 core declares them:",
    "  uint32 ID",
    "  uint16 ItemAppearanceID",
    "  int8   TransmogSourceTypeEnum",
    "98,056 rows at build 35662. The column set matches the client table exactly -",
    "ItemAppearance - five columns:",
    "  uint8  DisplayType",
    "  int32  DefaultIconFileDataID",
    "ItemAppearance 153, for example, has DisplayType 2 (body or shirt),",
    "ItemDisplayInfoID 5661 and icon file data id 132759.",
    "Item, the small table, not ItemSparse - nine columns:",
    "  uint8  ClassID",
    "  int8   InventoryType",
    "  int32  IconFileDataID",
    "Only ClassID, SubclassID and InventoryType matter to collection: they pick the",
    "  OverallQualityID, Flags[4] (Flags2 and Flags3 are tested), AllowableClass,",
    "  AllowableRace, RequiredLevel, RequiredSkill, RequiredSkillRank, ItemLevel,",
    "  MinFactionID, MinReputation, RequiredHoliday, Bonding.",
    "ItemSearchName - read only for existence. If the item id has no row there, the",
    "TransmogSet - thirteen columns:",
    "  uint32 TrackingQuestID",
    "  uint16 ParentTransmogSetID",
    "  uint8  ExpansionID",
    "  int16  UiOrder",
    "TransmogSetItem - four columns:",
    "  uint32 ItemModifiedAppearanceID",
    "Sets are small. TransmogSet 13, \"Wild Combatant's Chain Armor\", has ClassMask 4,",
    "TrackingQuestID 42975, Flags 0x14, TransmogSetGroupID 12,",
    "TransmogSetItem with Flags 0x0, 0x1 and 0x3.",
    "QuestPackageItem - five columns, reached from the quest reward path:",
    "  uint16 PackageID",
    "  uint32 ItemQuantity",
    )

# --- M: TransmogSource values ---------------------------------------------
add("M",
    "TransmogSourceTypeEnum is one signed byte per row and is the first test in the",
    "  0  Unknown                       7 rows - 104339 (item 168279), 105561",
    "  1  Dungeon Journal Encounter    15,434 rows - 136 (item 872), 142 (888),",
    "  2  Quest                        - 7545 is item 19019",
    "  3  Vendor                       14,851 rows - 1253 (item 3426), 1254 (3427),",
    "  5  Hidden Until Collected       - 19 (item 38), 24 (45), 27 (49), 30 (53)",
    "  6  Can't Collect                86 rows - 9261 (item 23421), 15167 (32912),",
    "  9  Not Valid for Transmog       - 14 (item 17, \"Martin Fury\"), 15 to 18",
    "Only values 6 and 9 are refused by the server. Value 5 is accepted: the name",
    "Whether values 4, 7 and 8 also occur in this build was not checked.",
    )

# --- C: CanAddAppearance ---------------------------------------------------
add("C",
    "CollectionMgr::CanAddAppearance, CollectionMgr.cpp:694-775, is the whole test.",
    "  1  the ItemModifiedAppearance pointer is null - the item has no appearance",
    "  2  TransmogSourceTypeEnum is 6 or 9;",
    "  3  there is no ItemSearchName row for the item id;",
    "  4  there is no ItemTemplate (so no ItemSparse / Item row);",
    "  5  the owning session has no Player - a login-time edge case;",
    "  6  Player::CanUseItem(ItemTemplate) is not EQUIP_ERR_OK. This single call",
    "     BaseRequiredLevel, holiday, required reputation, an artifact row whose",
    "  7  Flags2 has ITEM_FLAG2_NO_SOURCE_FOR_ITEM_VISUAL, or quality is",
    "  8  class is ITEM_CLASS_WEAPON and either the player lacks the proficiency bit",
    "     (GetWeaponProficiency() & (1 << Subclass)) or the subclass is EXOTIC,",
    "  9  class is ITEM_CLASS_ARMOR and InventoryType is outside BODY, SHIELD,",
    "     CLOAK, TABARD, HOLDABLE, HEAD, SHOULDERS, CHEST, WAIST, LEGS, FEET,",
    "     ARMOR_MISCELLANEOUS;",
    " 10  class is ITEM_CLASS_ARMOR, the item is not a cloak, and",
    "     PlayerClassByArmorSubclass[Subclass] does not contain the player's class.",
    "     That table, at CollectionMgr.cpp:604-616, is: cloth priest mage warlock,",
    "     leather rogue monk druid demon hunter, mail hunter shaman, plate warrior",
    "     paladin death knight; miscellaneous and buckler are all classes, shield",
    "     warrior paladin shaman, libram paladin, idol druid, totem shaman, sigil",
    " 11  class is neither weapon nor armour - this is what stops necklaces, rings,",
    " 12  quality is below ITEM_QUALITY_UNCOMMON, unless the item has both",
    "     ITEM_FLAG2_IGNORE_QUALITY_FOR_ITEM_VISUAL_SOURCE and",
    "     ITEM_FLAG3_ACTS_AS_TRANSMOG_HIDDEN_VISUAL_OPTION. Both flags are required;",
    " 13  the bit for this ItemModifiedAppearance id is already set.",
    "Note what is not in that list: the item's own binding, level, or price. Binding",
    "is tested one level up, in AddItemAppearance(Item*), and not tested at all for",
    "ItemModifiedAppearance 14 for item 17 \"Martin Fury\" is refused by test 2 before",
    "shirt (Class 4, Subclass 4, InventoryType 4), and ItemSearchName 17 reads",
    "quality 0, item level 1, expansion 0. ItemModifiedAppearance 9261 for item",
    "23421 is refused by the same test from the other list, value 6.",
    )

# --- B: bind and lookup paths ---------------------------------------------
add("B",
    "CollectionMgr::AddItemAppearance(Item*), CollectionMgr.cpp:620, runs four steps",
    "  1  the item is not soulbound - stop;",
    "  3  the item carries ITEM_FIELD_FLAG_BOP_TRADEABLE or",
    "     ITEM_FIELD_FLAG_REFUNDABLE - remember a temporary appearance under the",
    "  4  otherwise set the permanent appearance.",
    "Item::GetItemModifiedAppearance (Item.cpp:2318) does nothing more than",
    "sDB2Manager.GetItemModifiedAppearance(GetEntry(), _bonusData.AppearanceModID).",
    "AppearanceModID comes from the item bonus ITEM_BONUS_APPEARANCE, and when an",
    "(Item.cpp:2788-2795). DB2Manager::GetItemModifiedAppearance (DB2Stores.cpp:2432)",
    "looks the pair up in a map keyed by ItemID | (ItemAppearanceModifierID << 24),",
    "core asserts ItemID <= 0xFFFFFF when it builds that map (DB2Stores.cpp:1167).",
    )

# --- P: server grant paths -------------------------------------------------
add("P",
    "OnItemAdded(Item*, Player*) - CollectionMgr.cpp:167. Two lines: heirloom",
    "  Player.cpp:12804    Player::StoreNewItem, the tail of every item creation",
    "  Player.cpp:24072    Player::_StoreOrEquipNewItem, the vendor purchase. The",
    "  Player.cpp:13234    Player::VisualizeItem - the bind-on-equip,",
    "  Player.cpp:19910    Player::_LoadInventory - every soulbound item in the",
    "  Player.cpp:20089    Player::_LoadVoidStorage - same idea for void storage,",
    "  Player.cpp:20681    Player::_LoadQuestStatusRewarded - every choice reward",
    "  Player.cpp:20684    same function - every fixed reward id.",
    "  Player.cpp:20690    same function - every QuestPackageItem whose",
    "  Player.cpp:30705    Player::UpdateShop, product type 4 (APPEARANCE):",
    "  SpellHandler.cpp:118  item use on a BIND_ON_USE, BIND_ON_ACQUIRE or",
    "  VoidStorageHandler.cpp:199  withdrawal from void storage: store, bind,",
    "  TransmogrificationHandler.cpp:282  the transmogrifier, and only for an",
    "  Item.cpp:1764       Item::SetNotRefundable, only when the caller left",
    "  Item.cpp:1819       Item::ClearSoulboundTradeable, only when allowedGUIDs is",
    "  SpellEffects.cpp:6420  SPELL_EFFECT_LEARN_TRANSMOG_SET (effect 255,",
    "                      SharedDefines.h:1340) -> CollectionMgr::AddTransmogSet",
    "                      (CollectionMgr.cpp:647), which walks TransmogSetItem for",
    "  Player.cpp:13342    Player::MoveItemFromInventory - trade, auction, guild",
    "  Player.cpp:29178    Player::HandleItemRefund - refund accepted, appearance",
    "Nothing grants an appearance on loot assignment, on mail receipt or on trade",
    )

# --- D: storage and hidden -------------------------------------------------
add("D",
    "AddTemporaryAppearance (CollectionMgr.cpp:813) keys an unordered_set of item",
    "Player::AddConditionalTransmog. The wardrobe shows the appearance while the",
    "temporary, and IsSetCompleted (CollectionMgr.cpp:663) only counts a piece when",
    "The permanent grant (CollectionMgr.cpp:777) does four things: grows the bitset",
    "and then updates criteria - CRITERIA_TYPE_APPEARANCE_UNLOCKED_BY_SLOT for the",
    "CRITERIA_TYPE_TRANSMOG_SET_UNLOCKED for each set the appearance belongs to,",
    "Both clocks are two hours of played time, not real time:",
    "  refund       Item::UpdatePlayedTime (Item.cpp:1767) accumulates wall-clock",
    "               passes 2*HOUR; Item::IsRefundExpired is the same comparison.",
    "               The flag itself is ITEM_FIELD_FLAG_REFUNDABLE, set at purchase",
    "  tradeable    Item::CheckSoulboundTradeExpire (Item.cpp:1827) compares",
    "               CreatePlayedTime + 2*HOUR against the owner's total played time",
    "CollectionMgr::LoadAccountItemAppearances (CollectionMgr.cpp:507) builds a",
    "CollectionMgr::SaveAccountItemAppearances (CollectionMgr.cpp:560) writes it",
    "  table battlenet_item_appearances, columns battlenetAccountId, blobIndex,",
    "Favourites live in",
    "ActivePlayerData::ConditionalTransmog for the temporary ones. With 98,056 rows",
    "options, CollectionMgr.cpp:535-557:",
    "  134110 hidden helm      134111 hidden cloak     134112 hidden shoulder",
    "  168659 hidden chest     142503 hidden shirt     142504 hidden tabard",
    "  168665 hidden bracers   158329 hidden gloves    143539 hidden belt",
    "  168664 hidden boots",
    )

# --- X: differences --------------------------------------------------------
add("X",
    "Five differences matter to a project that has to run 8.3.7:",
    "The Flags column. Build 35662 has no Flags column in ItemModifiedAppearance.",
    "TrinityCore master has one, int32, last in the struct. Any export written for",
    "CanAddAppearance got shorter. The master version (CollectionMgr.cpp:680) keeps",
    "the Player null check, CanUseItem, the weapon proficiency bit, the",
    "PlayerClassByArmorSubclass test and the quality floor. A private server built on",
    "Criteria changed. 8.3.7 fires CRITERIA_TYPE_APPEARANCE_UNLOCKED_BY_SLOT and",
    "master's rules would collect items the 8.3.7 client expects to refuse.",
    "Master fires",
    "CriteriaType::LearnAnyTransmog on every grant and LearnAnyTransmogInSlot with",
    "The lookup moved. 8.3.7 resolves (itemId, modId) through",
    "DB2Manager::GetItemModifiedAppearance against a packed map. Master routes it",
    "through a separate Transmog/TransmogMgr module.",
    "ItemAppearance gained a PlayerConditionID field after 8.3.7 and its DisplayType",
    "width or signedness of several of them: TrackingQuestID, TransmogSetGroupID,",
    "ParentTransmogSetID, ExpansionID and UiOrder are int32 in master.",
    "The temporary mechanism is the same in both: bind-on-pickup tradeable and",
    "refundable items produce a conditional appearance and the 2*HOUR played-time",
    "refund window is unchanged from 8.3.7 to master.",
    )

# --- L: limits -------------------------------------------------------------
add("L",
    "The server quoted here is a community core. Where it and the client disagree the",
    "client wins, because the client decides what the wardrobe accepts; the core only",
    "decides what it tells the client. Nothing in this file was checked against a",
    "Blizzard server, and no claim is made about how the 8.3.7 client itself chooses",
    "to filter a row whose TransmogSourceTypeEnum is 5.",
    "Counts for enum values 2, 5, 9 and for values 4, 7, 8 were not read.",
    )


def hygiene_failures(text):
    out = []
    if any(b > 127 for b in text.encode("utf-8")):
        out.append("non-ASCII byte present")
    lines = text.split("\n")
    if not text.endswith("\n"):
        out.append("missing final newline")
    if "\t" in text:
        out.append("tab character present")
    for i, ln in enumerate(lines, 1):
        if ln != ln.rstrip():
            out.append(f"trailing whitespace on line {i}")
            break
    long_lines = [i for i, ln in enumerate(lines, 1) if len(ln) > 100]
    if long_lines:
        out.append(f"line(s) over 100 columns: {long_lines[:5]}")
    want = "TRANSMOG COLLECTION - THE DATA AND THE SERVER CODE, 8.3.7 (BUILD 35662)"
    if lines[0] != want:
        out.append("title line mismatch")
    if not (len(lines) > 1 and set(lines[1]) == {"="} and len(lines[1]) == 78):
        out.append("title underline mismatch (Part 15 convention: 78 '=')")
    return out


def run_checks(text):
    return [(fam, n) for fam, n in CHECKS if n not in text]


def report(text):
    failures = run_checks(text)
    h = hygiene_failures(text)
    by_fam = {}
    for fam, _ in CHECKS:
        by_fam[fam] = by_fam.get(fam, 0) + 1
    total = len(CHECKS)
    for fam in sorted(by_fam):
        nf = sum(1 for f, _ in failures if f == fam)
        print(f"family {fam}: {by_fam[fam] - nf}/{by_fam[fam]} {'PASS' if nf == 0 else f'FAIL {nf}'}")
    print(f"checks: {total - len(failures)}/{total} {'PASS' if not failures else 'FAIL'}")
    if h:
        for m in h:
            print(f"hygiene FAIL: {m}")
    else:
        print("hygiene PASS")
    for fam, needle in failures:
        print(f"  MISS [{fam}] {needle[:90]}")
    return not failures and not h


MUTATIONS = [
    # S
    ("THE CHAIN OF TABLES", "THE CHAINS OF TABLES"),
    # T
    ("98,056 rows at build 35662.", "98,057 rows at build 35662."),
    ("TransmogSet - thirteen columns:", "TransmogSet - twelve columns:"),
    # M
    ("  6  Can't Collect                86 rows", "  6  Can't Collect                87 rows"),
    # C
    (" 13  the bit for this ItemModifiedAppearance id is already set.",
     " 13  the bit for this ItemModifiedAppearance id is never set."),
    ("That table, at CollectionMgr.cpp:604-616, is:", "That table, at CollectionMgr.cpp:605-616, is:"),
    # B
    ("CollectionMgr.cpp:694-775, is the whole test.", "CollectionMgr.cpp:694-776, is the whole test."),
    ("(Item.cpp:2318) does nothing more than", "(Item.cpp:2319) does nothing more than"),
    # P
    ("Player.cpp:30705    Player::UpdateShop", "Player.cpp:30706    Player::UpdateShop"),
    ("SpellEffects.cpp:6420  SPELL_EFFECT_LEARN_TRANSMOG_SET (effect 255,",
     "SpellEffects.cpp:6421  SPELL_EFFECT_LEARN_TRANSMOG_SET (effect 255,"),
    # D
    ("Both clocks are two hours of played time, not real time:",
     "Both clocks are one hour of played time, not real time:"),
    ("  168664 hidden boots", "  168663 hidden boots"),
    # X
    ("TrinityCore master has one, int32, last in the struct.",
     "TrinityCore master has one, int16, last in the struct."),
    # L
    ("Counts for enum values 2, 5, 9 and for values 4, 7, 8 were not read.",
     "Counts for enum values 2, 5, 9 and for values 4, 7, 8 were all read."),
]


def self_test():
    original = PAYLOAD.read_text(encoding="utf-8")
    total_pass = 0
    for rnd in (1, 2):
        npass = 0
        bad = []
        for i, (old, new) in enumerate(MUTATIONS, 1):
            count = original.count(old)
            if count != 1:
                bad.append((i, f"literal occurs {count}x"))
                continue
            mutated = original.replace(old, new, 1)
            if run_checks(mutated):
                npass += 1
                total_pass += 1
            else:
                bad.append((i, "no check failed"))
        print(f"self-test round {rnd}: {npass}/{len(MUTATIONS)} {'PASS' if not bad else 'FAIL'}")
        for i, why in bad:
            print(f"  mutation {i}: {why}")
    print(f"self-test total: {total_pass}/{len(MUTATIONS) * 2}")
    return total_pass == len(MUTATIONS) * 2


if __name__ == "__main__":
    text = PAYLOAD.read_text(encoding="utf-8")
    ok = report(text)
    if "--self-test" in sys.argv:
        st = self_test()
        sys.exit(0 if (ok and st) else 1)
    sys.exit(0 if ok else 1)
