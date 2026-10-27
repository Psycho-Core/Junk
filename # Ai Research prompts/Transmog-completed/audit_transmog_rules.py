#!/usr/bin/env python3
"""Audit Transmog_Rules.txt - STEP 138 (task 16).

Families: S title/sections, Q four-question rule, A action rows, G gates,
U later-qualifies outcomes, C client notes, V server notes, R verified/
unverified/sources, H hygiene (programmatic).
Substring containment on single lines (wrap-safe). Self-test mutates the
payload and requires >= 1 failing check per mutation; each mutation literal
must occur exactly once in the payload.
"""
import sys
from pathlib import Path

PAYLOAD = Path(__file__).resolve().parent / "Transmog_Rules.txt"
CHECKS = []


def add(fam, *needles):
    for n in needles:
        CHECKS.append((fam, n))


# --- S: title, scope, section headers -------------------------------------
add("S",
    "TRANSMOG COLLECTION RULES - WORLD OF WARCRAFT 8.3.7 (BUILD 35662)",
    "Scope: when an appearance is added to a character's Appearances (wardrobe)",
    "collection. Applying an appearance to a piece of gear is a separate act; the gates",
    "Everything here is the 8.3.7 ruleset, not the 9.x or 10.x ruleset;",
    "THE ONE RULE THAT DECIDES EVERYTHING",
    "ACTION BY ACTION",
    "THE GATES, ONE BY ONE",
    "THE ITEM YOU CANNOT USE YET",
    "WHAT THE CLIENT SHOWS, AND WHAT THAT MEANS WHEN TESTING",
    "WHAT A SERVER HAS TO DO TO MATCH THIS",
    "WHAT IS VERIFIED AND WHAT IS NOT",
    "Sources read for this step:",
    )

# --- Q: the four-question rule --------------------------------------------
add("Q",
    "The wiki records a four-question test posted by a Blizzard developer. All four",
    "answers must be yes at the same moment, for the same character:",
    "  1  Can you equip the item right now?",
    "  2  Does equipping it keep your Armor Skills passive? In practice: is it your",
    "  3  Is it permanently soulbound to you?",
    "  4  Is it at least Uncommon quality?",
    "Yes to all four: the character learns the appearance. No to any one: it learns",
    "nothing, and in the 8.3.7 client it is not queued for later either.",
    "other side: every soulbound item is added automatically, and every quest reward",
    "  - the trigger is the bind, not the loot and not the equip;",
    "  - for an item that binds on equip, the trigger is therefore the equip.",
    )

# --- A: action by action ---------------------------------------------------
add("A",
    "BIND ON PICKUP, LOOTED",
    "  Learned at the moment the item enters the bags and binds. No equip needed.",
    "  bind-on-pickup plate chest binds it and learns nothing; a level 40 character",
    "BIND ON EQUIP, LOOTED",
    "  Not learned on loot. Learned on the first equip, which is the bind. An item",
    "  that stays in the bags, the bank or Void Storage is not learned.",
    "BIND ON PICKUP, WON ON A ROLL",
    "  8.3.7 has no need-or-greed roll for dungeon and raid loot: patch 8.0.1 removed",
    "  the loot-mode setting and personal loot is the only mode left. Most",
    "  assigned; a personal-loot drop that is bind-on-equip still waits for the equip.",
    "  the winner learns it when it binds, the losers never see it.",
    "BIND ON PICKUP, BOUGHT FROM A VENDOR",
    "  Learned at the purchase, because the purchase is the bind. This is the normal",
    "  case for PvP gear bought from a battleground vendor and for faction",
    "BIND ON EQUIP, BOUGHT FROM A VENDOR",
    "  Not learned at the purchase. Learned when the buyer equips it.",
    "QUEST REWARD, THE OPTION CHOSEN",
    "  Learned when the quest is handed in.",
    "QUEST REWARD, AN OPTION NOT CHOSEN",
    "  Learned as well. The wiki states that all quest rewards from a completed quest",
    "  are added even if the player did not choose that reward, and Blizzard support",
    "  quests. Two exceptions are documented: Azerite armour rewards and PvP weapon",
    "  rewards add only the item that was actually chosen.",
    "CRAFTED, RESULT BINDS ON PICKUP",
    "  Learned by the crafter at the moment the craft binds the item to them.",
    "CRAFTED, RESULT BINDS ON EQUIP",
    "  Not learned by the crafter. Learned by whoever equips it. Crafting an item for",
    "  another player teaches the crafter nothing, and selling it teaches the buyer",
    "MAIL",
    "  Receiving a bind-on-equip item in the mail does not teach it; a mailbox is not",
    "  normally be mailed by a player at all. Whether an item returned by the",
    "  Postmaster teaches its appearance on pickup is unverified.",
    "TRADE, AND THE AUCTION HOUSE",
    "  A bind-on-equip item received by trade or bought from the auction house is not",
    "  only if the seller equipped it first; selling a bind-on-equip item that was",
    "  never worn teaches nothing.",
    "EQUIP",
    "  The trigger for every bind-on-equip item. Equipping is also what re-runs",
    "  question 1 for an item that was bound earlier while the character could not",
    "REFUND AND TRADE WINDOWS",
    "  A vendor purchase can be refunded, and a drop can be traded to another",
    "rule text does not give the length and the two-hour figure is unverified here.",
    "  soulbound and that \"trading an item during the grace period timer will revoke",
    "  the appearance\". A Blizzard support answer quoted on the forums puts it the",
    "  Which of the two describes the 8.3.7 client exactly: unverified. Both agree on",
    "ENSEMBLE ITEMS",
    "  An ensemble is a usable item that teaches a list of appearances when used, and",
    "  ensembles exist in 8.3.7. The gating on a given ensemble (class, armour type,",
    "  faction) is item data and is unverified here; the appearance still has to pass",
    )

# --- G: gates --------------------------------------------------------------
add("G",
    "LEVEL",
    "  Must pass. Question 1 is read literally, so it includes the item's required",
    "  level: a character below it learns nothing at the bind. The 9.0.1 patch note",
    "  100. That removal is 9.0.1 only, so nothing taken from a modern guide may be",
    "  used for an 8.3.7 core: in 8.3.7 the level gate is live.",
    "CLASS",
    "  Must pass. An item restricted to another class cannot be equipped, so it is",
    "  never learned - this covers tier tokens, class quest rewards and class-locked",
    "ARMOUR TYPE",
    "  Must pass, and this is the strictest gate. The character learns only its",
    "    cloth    mage, priest, warlock",
    "    leather  druid, monk, rogue, demon hunter",
    "    mail     hunter, shaman",
    "    plate    warrior, paladin, death knight",
    "  So a warrior, who can wear cloth, leather, mail and plate, still learns plate",
    "  only, and a hunter learns mail only. Cloaks, shirts, tabards and other items",
    "  with no armour type are outside this gate.",
    "WEAPON PROFICIENCY",
    "  Must pass. A character learns a weapon appearance only if its class can equip",
    "  that weapon type; a mage never learns a bow, a priest never learns a sword.",
    "  polearms; bows, crossbows and guns) are a looser rule and apply only to",
    "FACTION",
    "  Must pass. An item that requires the other faction cannot be equipped, so it is",
    "  never learned. Patch 8.1.0 notes the matching rule from the other side: after",
    "  race change, an applied transmog that is no longer valid for the new race is",
    "RACE",
    "  Must pass. Heritage armour, racial quest rewards and race-locked items are",
    "PROFESSION",
    "  Must pass where the item requires a profession to equip - engineering goggles",
    "  are the standard case. A character without the profession cannot equip the",
    "  item and so learns nothing. Profession does not otherwise matter: any",
    "REPUTATION",
    "  Not checked by the collection itself. Reputation gates the vendor sale, and it",
    "  ItemSparse MinFactionID and MinReputation into exactly that). Patch 8.1.0",
    "  removed the reputation requirement from the other end: once an appearance is",
    "QUALITY",
    "  Must pass: Uncommon or better. Poor (grey) and Common (white) items could not",
    "  be collected in 8.3.7; patch 10.0.5 is what allowed most of them. Legendary is",
    "  a special case: before Legion most legendaries were not transmogrifiable at",
    "  all, and patch 8.3.0 made many legendary weapons transmogrifiable, with the",
    "  Warglaives of Azzinoth the stated exception (demon hunter only, through the",
    "  Black Temple Timewalking unlock). Which individual legendary items are",
    "  eligible in 8.3.7 is item data and is not checked here.",
    )

# --- U: the item you cannot use yet ---------------------------------------
add("U",
    "  BLOCKED BY LEVEL, ITEM STILL HELD",
    "when the character reaches the required level, equipping it then re-runs",
    "question 1 and the appearance is learned at that moment. No source read here",
    "    describes a level-up trigger of its own; every path listed on the wiki runs",
    "    through earning (binding) or equipping the item.",
    "  BLOCKED BY LEVEL, ITEM GONE",
    "    Same bind, but the item was sold, disenchanted or destroyed before the",
    "    character qualified. The appearance is lost for that character. There is no",
    "    retroactive grant in 8.3.7; the retroactive quest-reward pass is the 11.0.5",
    "  BLOCKED BY CLASS, ARMOUR TYPE, WEAPON PROFICIENCY, FACTION OR RACE",
    "    character on the same account that passes the gate, obtaining its own copy -",
    "    and a bind-on-pickup item has to be looted or received by that character",
    "  BLOCKED BY QUALITY",
    "    Poor and Common items are not collectable in 8.3.7 at any level and by any",
    "    class; this build does not offer it as a collectable appearance at all.",
    "Collections are account-wide, but the learning is done by the character that",
    "binds the item, and each character's ability to apply an appearance is judged",
    "does not let a mage wear it.",
    )

# --- C: client notes -------------------------------------------------------
add("C",
    "visible \"appearance learned\" message when it is added, while Rare and above",
    "always do. A missing toast on a green item is therefore not evidence that the",
    "collection failed. Check the Appearances tab, not the chat line.",
    "the character has not collected yet is highlighted in its tooltip. Whether the",
    "unverified, so the Appearances tab, not the tooltip colour, is the safe test.",
    )

# --- V: server notes -------------------------------------------------------
add("V",
    "Four things have to be true in the server's own data, not only in the client:",
    "  - the item must actually bind in the server's item handling, at the same",
    "    operation that grants the appearance; a core that grants on loot but binds",
    "    on equip (or the reverse) will drift from the client;",
    "  - the server has to evaluate the same four checks before inserting the",
    "    appearance, because the client will not fix a wrong insert and the collection",
    "  - the check is made against the character that binds the item, and the",
    "    appearance then belongs to the whole account, so the insert has to be",
    "    account-scoped while the decision is character-scoped;",
    "  - a refund or a trade inside the window must remove the appearance again if it",
    "    was inserted early.",
    "The exact table and function on this TrinityCore-based 8.3.7 core are the subject",
    "of the next step and are unverified here. No code is given in this file.",
    )

# --- R: verified / unverified / sources -----------------------------------
add("R",
    "Verified, read this run:",
    "  - the four-question test, its wording, and the \"permanently soulbound / trading",
    "    during the grace period revokes\" clause: the Appearances page as it stood on",
    "    2018-12-11, which still prints the test; the live page has replaced it with a",
    "  - primary-armour-type-only collection and the \"same primary armour type ...",
    "  - uncommon-or-better, and that 10.0.5 is what changed it: the Appearances",
    "  - personal loot as the only loot mode from 8.0.1: the Loot page patch list;",
    "  - the 9.0.1 removal of the old-expansion level gate, with the Legion-100",
    "  - 8.3.0 legendaries, and the Warglaives exception: the 8.3.0 patch note and",
    "  - reputation no longer gating the appearance once acquired: the 8.1.0 patch",
    "  - the green-versus-rare toast behaviour and the Azerite/PvP quest-reward",
    "Unverified, and left as unverified:",
    "  - whether a refundable or tradable item is granted at once and revoked on",
    "  - the exact level figure that gated each old expansion in the 8.3.7 client,",
    "  - whether an item returned by the Postmaster teaches its appearance on pickup;",
    "  - the gating on individual ensemble items;",
    "  - which individual legendary items are eligible in 8.3.7;",
    "  - the server-side table and function, which is the next step.",
    "  warcraft.wiki.gg Appearances, revision of 2018-12-11 (8.1-era text, four-question",
    "  warcraft.wiki.gg Transmogrification,",
    "  revision of 2020-01-13 (8.3-era text); warcraft.wiki.gg Patch 8.1.0;",
    "  wowpedia Patch 9.0.1 (undocumented changes); wowpedia Loot (8.0.1 note);",
    "  wowpedia Patch 8.3.0; Blizzard support articles 15823 and 177415 as quoted;",
    "  the EU forum post quoting the support article's full criteria list.",
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
    want = "TRANSMOG COLLECTION RULES - WORLD OF WARCRAFT 8.3.7 (BUILD 35662)"
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
    ("TRANSMOG COLLECTION RULES - WORLD OF WARCRAFT 8.3.7 (BUILD 35662)",
     "TRANSMOG COLLECTION RULES - WORLD OF WARCRAFT 8.3.7 (BUILD 35663)"),
    # Q
    ("  4  Is it at least Uncommon quality?", "  4  Is it at least Rare quality?"),
    # A
    ("Learned on the first equip, which is the bind.", "Learned on the second equip, which is the bind."),
    ("patch 8.0.1 removed", "patch 8.0.2 removed"),
    # G
    ("  Must pass: Uncommon or better. Poor (grey) and Common (white) items could not",
     "  Must pass: Rare or better. Poor (grey) and Common (white) items could not"),
    ("    plate    warrior, paladin, death knight", "    plate    warrior, paladin"),
    ("  used for an 8.3.7 core: in 8.3.7 the level gate is live.",
     "  used for an 8.3.7 core: in 8.3.7 the level gate is off."),
    # U
    ("  BLOCKED BY LEVEL, ITEM GONE", "  BLOCKED BY LEVEL, ITEM SOLD"),
    ("retroactive quest-reward pass is the 11.0.5", "retroactive quest-reward pass is the 11.0.6"),
    # C
    ("Check the Appearances tab, not the chat line.", "Check the chat line, not the Appearances tab."),
    # V
    ("account-scoped while the decision is character-scoped;",
     "account-scoped while the decision is account-scoped;"),
    # R
    ("revision of 2018-12-11 (8.1-era text, four-question",
     "revision of 2018-12-12 (8.1-era text, four-question"),
    ("Unverified, and left as unverified:", "Verified, and left as verified:"),
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
