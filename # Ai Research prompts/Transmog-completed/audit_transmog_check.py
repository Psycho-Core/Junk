#!/usr/bin/env python3
"""Audit Transmog_Check.txt - STEP 140 (task 18).

Families: S title/build/header, I item data (ids, class, subclass, quality,
flags), A appearance rows (ItemModifiedAppearance + ItemAppearance), V source
and verdict (Xavius, map, mail-wearer refusal), P grant path
(StoreNewItem -> OnItemAdded -> AddItemAppearance), C fifteen causes of a
refusal, U unverified items left as unverified, H hygiene (programmatic).
Substring containment on whitespace-normalised single lines (wrap-safe).
Self-test mutates the payload and requires >= 1 failing check per mutation;
each mutation literal must occur exactly once in the payload.
"""
import re
import sys
from pathlib import Path

PAYLOAD = Path(__file__).resolve().parent / "Transmog_Check.txt"
CHECKS = []


def add(fam, *needles):
    for n in needles:
        CHECKS.append((fam, n))


def flat(text):
    """Collapse all whitespace runs so wrapped table rows match as one literal."""
    return re.sub(r"\s+", " ", text)


# --- S: title, build, header ----------------------------------------------
add(
    "S",
    "THE FIRST SATYR'S SPOULDERS - WORKED COLLECTION CHECK",
    "Item 141006, build 8.3.7.35662",
    "Every number below was read out of the 8.3.7 tables or the 8.3.7 core",
    "the one web source is named where it is used",
)


# --- I: item data ----------------------------------------------------------
add(
    "I",
    "The First Satyr's Spaulders",
    "item id 141006",
    "class 4 - Armor",
    "subclass 2 - Leather",
    "inventory type 3 - Shoulder",
    "quality 4 - Epic",
    "item level 168",
    "required level 110",
    "binding 1 - Bind on Acquire",
    "allowable class 0xffffffff - every class",
    "allowable race 0xffffffff - every race",
    "expansion 6 - Legion",
    "ITEM_FLAG2_SHOW_BEFORE_DISCOVERED",
    "0x00400000",
    "IconFileDataID 0 in the Item table, 1045428 through ItemAppearance",
    "ItemSearchName 141006",
)


# --- A: appearance rows ----------------------------------------------------
add(
    "A",
    "ItemModifiedAppearance holds exactly two rows for item 141006",
    "IMA 93947 ItemID 141006 ItemAppearanceModifierID 1",
    "IMA 93948 ItemID 141006 ItemAppearanceModifierID 3",
    "ItemAppearanceID 31252",
    "ItemAppearance 31252 DisplayType 1 - Shoulder",
    "ItemDisplayInfoID 154217",
    "DefaultIconFileDataID 1045428",
    "There is no row with modifier 0",
    "modifier 0 resolves to nothing",
)


# --- V: source and verdict -------------------------------------------------
add(
    "V",
    "Xavius, entry 103769, title Nightmare Lord",
    "map id 1520",
    "The Emerald Nightmare",
    "0.27 percent",
    "119,688",
    "No. A hunter or a shaman at level 120 that loots this item should not have",
    "leather maps to rogue, monk, druid and demon hunter",
    "Hunter and shaman are not in that set",
    "the item is soulbound, the appearance is refused",
    "the primary-armour-type rule alone",
)


# --- P: grant path ---------------------------------------------------------
add(
    "P",
    "Player::StoreNewItem, which calls CollectionMgr::OnItemAdded",
    "OnItemAdded calls AddItemAppearance(Item)",
    "the account-wide bit for that IMA is set",
    "two hours of played time",
    "battlenet_item_appearances",
)


# --- C: causes of a refusal ------------------------------------------------
add(
    "C",
    "THE USUAL REASONS AN APPEARANCE DOES NOT COLLECT ON A TRINITYCORE-BASED 8.3.7 SERVER",
    "No ItemModifiedAppearance row for the pair (item id, appearance modifier)",
    "TransmogSourceTypeEnum is 6 or 9",
    "86 rows in this build are 6",
    "No ItemSearchName row",
    "No ItemSparse row",
    "The character cannot use the item at that moment",
    "ITEM_FLAG2_NO_SOURCE_FOR_ITEM_VISUAL",
    "cause 9 for any hunter or shaman",
    "cause 2 for anyone if the item is created without its appearance",
    "mail delivery goes through StoreItem, which does not grant",
    "vendor path passes false",
    "The database never saved",
)


# --- U: unverified ---------------------------------------------------------
add(
    "U",
    "Which raid difficulty each appearance modifier stands for",
    "bonus 9085",
    "Black Market Auction House",
    "Whether the 8.3.7 client displays the appearance as collected",
)


# --- H: hygiene ------------------------------------------------------------
TITLE = "THE FIRST SATYR'S SPOULDERS - WORKED COLLECTION CHECK"


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
            out.append("trailing whitespace on line %d" % i)
            break
    long_lines = [i for i, ln in enumerate(lines, 1) if len(ln) > 100]
    if long_lines:
        out.append("line(s) over 100 columns: %s" % long_lines[:5])
    if lines[0] != TITLE:
        out.append("title line mismatch")
    if not (len(lines) > 1 and set(lines[1]) == {"="} and len(lines[1]) == 78):
        out.append("title underline mismatch (78 '=')")
    return out


def run_checks(text):
    flat_text = flat(text)
    return [(fam, n) for fam, n in CHECKS if n not in flat_text]


def report(text):
    failures = run_checks(text)
    h = hygiene_failures(text)
    by_fam = {}
    for fam, _ in CHECKS:
        by_fam[fam] = by_fam.get(fam, 0) + 1
    total = len(CHECKS)
    for fam in sorted(by_fam):
        nf = sum(1 for f, _ in failures if f == fam)
        print("family %s: %d/%d %s" % (fam, by_fam[fam] - nf, by_fam[fam],
                                      "PASS" if nf == 0 else "FAIL %d" % nf))
    print("checks: %d/%d %s" % (total - len(failures), total,
                              "PASS" if not failures else "FAIL"))
    if h:
        for m in h:
            print("hygiene FAIL: %s" % m)
    else:
        print("hygiene PASS")
    for fam, needle in failures:
        print("  MISS [%s] %s" % (fam, needle[:90]))
    return not failures and not h


MUTATIONS = [
    ("S", "Item 141006, build 8.3.7.35662", "Item 141006, build 8.3.7.35663"),
    ("I", "subclass 2 - Leather", "subclass 2 - Mail"),
    ("I", "quality 4 - Epic", "quality 3 - Rare"),
    ("I", "binding 1 - Bind on Acquire", "binding 2 - Bind on Equip"),
    ("I", "ITEM_FLAG2_SHOW_BEFORE_DISCOVERED", "ITEM_FLAG2_NO_SOURCE_FOR_ITEM_VISUAL"),
    ("A", "IMA 93947 ItemID 141006 ItemAppearanceModifierID 1",
     "IMA 93947 ItemID 141006 ItemAppearanceModifierID 2"),
    ("A", "IMA 93948 ItemID 141006 ItemAppearanceModifierID 3",
     "IMA 93948 ItemID 141006 ItemAppearanceModifierID 4"),
    ("A", "There is no row with modifier 0", "There is a row with modifier 0"),
    ("V", "Xavius, entry 103769, title Nightmare Lord",
     "Xavius, entry 103770, title Nightmare Lord"),
    ("V", "No. A hunter or a shaman at level 120 that loots this item should not have",
     "Yes. A hunter or a shaman at level 120 that loots this item should have"),
    ("V", "leather maps to rogue, monk, druid and demon hunter",
     "leather maps to hunter, shaman, warrior, paladin"),
    ("P", "Player::StoreNewItem, which calls CollectionMgr::OnItemAdded",
     "Player::StoreItem, which calls CollectionMgr::OnItemAdded"),
    ("P", "battlenet_item_appearances", "battlenet_item_illusions"),
    ("C", "TransmogSourceTypeEnum is 6 or 9", "TransmogSourceTypeEnum is 5 or 7"),
    ("C", "cause 9 for any hunter or shaman", "cause 9 for any plate wearer"),
    ("C", "cause 2 for anyone if the item is created without its appearance",
     "cause 2 for anyone if the item is created with its appearance"),
    ("C", "mail delivery goes through StoreItem, which does not grant",
     "mail delivery goes through StoreNewItem, which grants"),
    ("U", "bonus 9085", "bonus 9086"),
]


def self_test():
    original = flat(PAYLOAD.read_text(encoding="utf-8"))
    total_pass = 0
    for rnd in (1, 2):
        npass = 0
        bad = []
        for i, (fam, old, new) in enumerate(MUTATIONS, 1):
            count = original.count(old)
            if count != 1:
                bad.append((i, fam, "literal occurs %dx" % count))
                continue
            mutated = original.replace(old, new, 1)
            if run_checks(mutated):
                npass += 1
                total_pass += 1
            else:
                bad.append((i, fam, "no check failed"))
        print("self-test round %d: %d/%d %s" % (rnd, npass, len(MUTATIONS),
                                              "PASS" if not bad else "FAIL"))
        for i, fam, why in bad:
            print("  mutation %d (%s): %s" % (i, fam, why))
    print("self-test total: %d/%d" % (total_pass, len(MUTATIONS) * 2))
    return total_pass == len(MUTATIONS) * 2


if __name__ == "__main__":
    text = PAYLOAD.read_text(encoding="utf-8")
    ok = report(text)
    if "--self-test" in sys.argv:
        st = self_test()
        sys.exit(0 if (ok and st) else 1)
    sys.exit(0 if ok else 1)
