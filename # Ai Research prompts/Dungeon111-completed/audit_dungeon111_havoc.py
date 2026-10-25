#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit for the Dungeon111 set after the Demon Hunter Havoc rework.

Checks (statics):
  * structure: all 5 deliverables + 2 prompts + RESEARCH_MASTER STEP 050/051 lines
  * spec pins: Havoc (ChrSpecialization ID 577) everywhere the set states the spec
  * verified facts: Soul Rending 204909 = +10%/+10%, Metamorphosis 191427 (4 min,
    30 s form, +25% Haste/+20% Leech) + form 162264, Death Sweep 210152,
    Fel Barrage 258925, Havoc talent tree 7 rows x 3, Havoc PvP pool,
    DH2 Havoc items (178976, 144279, 158305, 159297, 127829/127830, 40817,
    T21 251767/251769), route = Havoc-only
  * forbidden leftovers: Vengeance-as-chosen-spec strings, dead spell ids,
    removed slot rows
  * derived: mastery gem math 50 / 20.28 * 1.8 == 4.44

Mutation self-test (--self-test): every "has" target is corrupted, every
"absent" string is inserted, every count is altered, and the derived number
is falsified; the audit must FAIL on each mutated document (baseline PASSes).
"""
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))


def load(rel):
    return io.open(os.path.join(BASE, rel), encoding="utf-8").read()


FILES = {
    "dh1": "Dungeon111_Demon_Hunter_1_Level_And_Spec.txt",
    "dh2": "Dungeon111_Demon_Hunter_2_Items.txt",
    "route": "Dungeon111_Route.txt",
    "dk1": "Dungeon111_Death_Knight_1_Level_And_Spec.txt",
    "dk2": "Dungeon111_Death_Knight_2_Items.txt",
    "p1": os.path.join("Demon_Hunter", "1_Level_And_Spec.txt"),
    "p2": os.path.join("Demon_Hunter", "2_Items_Enchants_Consumables.txt"),
    "rm": os.path.join("..", "RESEARCH_MASTER.txt"),
}

# ---------------------------------------------------------------- statics ---
# (id, file, kind, payload)
#   kind "has": payload substring must exist
#   kind "absent": payload substring must NOT exist
#   kind "count": (payload, n) exact count
#   kind "regex": (pattern, n) matches >= n
CHECKS = [
    # --- structure ---
    ("S01", "dh1", "has", "STEP 1: LEVEL, LOCKING AT 111, SPECIALIZATION, TALENTS, AND SPELLS"),
    ("S02", "dh1", "has", "1. CAN A DEMON HUNTER BE LEVEL 111 IN 8.3.7 AND HOW IT GETS THERE"),
    ("S03", "dh1", "has", "2. CHEAPEST WAY TO GET TO EXACTLY 111 AND KEEP IT THERE"),
    ("S04", "dh1", "has", "3. BEST SPECIALIZATION FOR DUNGEON BOOSTING AND WHY"),
    ("S05", "dh1", "has", "4. TALENTS AT LEVEL 111 (NORMAL AND PVP) WITH TALENT IDS AND SPELL IDS"),
    ("S06", "dh1", "has", "5. SPELLS THAT MATTER FOR DUNGEON BOOSTING (WITH SPELL IDS)"),
    ("S07", "dh2", "has", "STEP 2: ITEMS, DUNGEON SCALING (110-120), ENCHANTS, GEMS, CONSUMABLES, AND PROFESSIONS"),
    ("S08", "dh2", "has", "2. HOW ITEMS SCALE IN 110-120 DUNGEONS AT LEVEL 111"),
    ("S09", "dh2", "has", "3. ENCHANTS, GEMS, FLASKS, POTIONS, FOOD, AND OTHER CONSUMABLES (WITH IDS)"),
    ("S10", "dh2", "has", "4. PROFESSIONS THAT HELP AT LEVEL 111"),
    ("S11", "route", "has", "1. GROUP FORMATION, XP LOCK, QUEUEING, AND INSTANCE ENTRY RULES"),
    ("S12", "route", "has", "4. ORDERED FASTEST DUNGEON ROUTE FROM LEVEL 10 TO 120"),
    ("S13", "dk1", "has", "Blood (ChrSpecialization ID 250, Role: Tank"),
    ("S14", "dk2", "has", "STEP 2"),
    ("S15", "p1", "has", "WHAT TO DELIVER - ONE TEXT FILE, Dungeon111_Demon_Hunter_1_Level_And_Spec.txt"),
    ("S16", "p2", "has", "WHAT TO DELIVER - ONE TEXT FILE, Dungeon111_Demon_Hunter_2_Items.txt"),
    ("S17", "rm", "has", "--- STEP 050"),
    ("S18", "rm", "has", "--- STEP 051"),

    # --- spec pins ---
    ("P01", "p1", "has", "a level 111 Havoc Demon Hunter (the specification is Havoc, damage dealer, not a tank)"),
    ("P02", "p1", "has", "The Havoc specialization (ChrSpecialization ID 577) for dungeon boosting"),
    ("P03", "p2", "has", "a level 111 Havoc Demon Hunter (the specification is Havoc, damage dealer, not a tank)"),
    ("P04", "rm", "count", ("a level 111 Havoc Demon Hunter (the specification is Havoc, damage dealer, not a tank)", 2)),
    ("P05", "rm", "has", "The Havoc specialization (ChrSpecialization ID 577) for dungeon boosting"),
    ("P06", "dh1", "has", "- Havoc (ChrSpecialization ID 577, Role: Melee DPS, Resource: Fury [PowerType 17, max 100/120]"),
    ("P07", "dh1", "has", "Specialization choice switched to Havoc (ChrSpecialization ID 577) and Fel Secrets (Quest ID 40051)"),
    ("P08", "dh1", "has", "Why Vengeance (Spec ID 581) Was Not Selected:"),
    ("P09", "dh1", "absent", "Why Vengeance (Spec ID 581) Beats Havoc"),
    ("P10", "dh1", "absent", "switched to Vengeance (ChrSpecialization ID 581)"),
    ("P11", "dh2", "has", "(HAVOC DEMON HUNTER, SPEC ID 577)"),
    ("P12", "dh2", "absent", "(VENGEANCE DEMON HUNTER, SPEC ID 581)"),
    ("P13", "route", "has", "Recommended Level 111 Booster Spec: Havoc Demon Hunter (ChrSpecialization ID 577"),
    ("P14", "route", "absent", "Vengeance"),
    ("P15", "route", "absent", "or Vengeance Demon Hunter"),

    # --- DH1 verified facts ---
    ("F01", "dh1", "has", "Soul Rending (Havoc Talent ID 21863, Spell ID 204909): +10% passive Leech and +10% additional Leech while Metamorphosis is active in Patch 8.0.1-8.3.7"),
    ("F02", "dh1", "has", "Spell ID 204909: +10% passive Leech and +10% additional Leech in Metamorphosis (Patch 8.0.1-8.3.7 values)"),
    ("F03", "dh1", "has", "- Soul Rending: Spell ID 204909 (+10% passive Leech, +10% additional Leech in Metamorphosis in Patch 8.0.1-8.3.7)"),
    ("F04", "route", "has", "Soul Rending (Havoc Talent): Spell ID 204909 (+10% passive Leech, +10% additional Leech in Metamorphosis)"),
    ("F05", "dh1", "absent", "Spell ID 204909: +5%"),
    ("F06", "dh1", "absent", "+5% passive Leech and +25% additional Leech while in Metamorphosis"),
    ("F07", "dh1", "has", "Metamorphosis (Havoc, Ability Spell ID 191427, 40 yd, 4 min cooldown in Patch 8.3.7)"),
    ("F08", "dh1", "has", "30 sec demon form (Metamorphosis form Spell ID 162264) that grants +25% Haste and +20% Leech"),
    ("F09", "dh1", "has", "Death Sweep (Spell ID 210152, 35 Fury, 9 sec cooldown)"),
    ("F10", "route", "has", "Death Sweep (Metamorphosis): Spell ID 210152"),
    ("F11", "dh1", "has", "Spell ID 258925, 10 Fury, 1.5 min cooldown"),
    ("F12", "route", "has", "Fel Barrage (Talent): Spell ID 258925"),
    ("F13", "route", "absent", "Fel Barrage (Talent): Spell ID 211053;"),
    ("F14", "route", "has", "Ability Spell ID 191427 (40 yd, 4 min CD in 8.3.7"),
    ("F15", "route", "absent", "Vengeance DH Tank Cooldowns"),
    ("F16", "route", "absent", "Sigil of Misery"),
    ("F17", "dh1", "has", "Demonic (Havoc Talent ID 21900, Spell ID 213410)"),
    ("F18", "dh1", "has", "Havoc Demonic Wards (Spell ID 278386, added in Patch 8.0.1) is only -10% magic damage taken"),
    ("F19", "dh1", "has", "Leather Specialization (Havoc): Spell ID 178976 (+5% Agility while wearing Leather in all 8 armor slots)"),
    ("F20", "dh1", "has", "Mastery: Demonic Presence: Spell ID 185164 (in Patch 8.0.1-8.3.7: increases Chaos damage by 1.8% per Mastery point"),
    ("F21", "dh1", "has", "- Metamorphosis: Spell ID 191427 (demon form adds +20% Leech and +25% Haste for 30 sec in 8.3.7)"),
    ("F22", "dh1", "absent", "Metamorphosis (Spell ID 187827"),
    ("F23", "dh1", "absent", "Torment (Spell ID 185245"),
    ("F24", "dh1", "absent", "Soul Cleave (Spell ID 228477"),
    ("F25", "dh1", "absent", "Sigil of Flame (Spell ID 204596"),
    # preserved level/lock facts (sections 1-2 must stay intact)
    ("F26", "dh1", "has", "earn 537,730 XP to reach level 111"),
    ("F27", "dh1", "has", "StartDemonHunterPlayerLevel = 98"),
    ("F28", "dh1", "has", "Response 478 Havoc casts Spell ID 194939"),
    ("F29", "dh1", "has", "10 gold (100,000 copper) to lock XP"),

    # --- DH1 talent table ---
    ("T01", "dh1", "count", ("- Row 1 (Level 99):", 1)),
    ("T02", "dh1", "count", ("- Row 2 (Level 100):", 1)),
    ("T03", "dh1", "count", ("- Row 3 (Level 102):", 1)),
    ("T04", "dh1", "count", ("- Row 4 (Level 104):", 1)),
    ("T05", "dh1", "count", ("- Row 5 (Level 106):", 1)),
    ("T06", "dh1", "count", ("- Row 6 (Level 108):", 1)),
    ("T07", "dh1", "count", ("- Row 7 (Level 110):", 1)),
    ("T08", "dh1", "count", ("[SELECTED]", 9)),  # 7 PvE rows + 2 PvP picks
    ("T09", "dh1", "count", ("Talent ID: unverified", 26)),  # 19 in the 21-talent table (2 have real Talent IDs) + 7 in section 3
    ("T10", "dh1", "has", "[SELECTED] Blind Fury - Talent ID: unverified, Spell ID 203550"),
    ("T11", "dh1", "has", "[SELECTED] Immolation Aura - Talent ID: unverified, Spell ID 258920"),
    ("T12", "dh1", "has", "[SELECTED] Fel Barrage - Talent ID: unverified, Spell ID 258925"),
    ("T13", "dh1", "has", "[SELECTED] Soul Rending - Talent ID 21863, Spell ID 204909"),
    ("T14", "dh1", "has", "[SELECTED] First Blood - Talent ID: unverified, Spell ID 206416"),
    ("T15", "dh1", "has", "[SELECTED] Unleashed Power - Talent ID: unverified, Spell ID 206477"),
    ("T16", "dh1", "has", "[SELECTED] Demonic - Talent ID 21900, Spell ID 213410"),
    ("T17", "dh1", "has", "Alternative Col 3: Nemesis - Talent ID: unverified, Spell ID 206491"),
    ("T18", "dh1", "has", "Alternative Col 3: Dark Slash - Talent ID: unverified, Spell ID 258860"),
    ("T19", "dh1", "has", "Alternative Col 2: Cycle of Hatred - Talent ID: unverified, Spell ID 258887"),

    # --- DH1 PvP pool ---
    ("V01", "dh1", "has", "Havoc Spec ID 577 Pool - talents verified present in Patch 8.3.7"),
    ("V02", "dh1", "count", ("1) [SELECTED] Demonic Origins - Spell ID 235893", 1)),
    ("V03", "dh1", "count", ("2) [SELECTED] Solitude - Spell ID 211509", 1)),
    ("V04", "dh1", "has", "3) Mana Rift - Spell ID 235903"),
    ("V05", "dh1", "has", "4) Cover of Darkness - Spell ID 227635"),
    ("V06", "dh1", "has", "5) Reverse Magic - Spell ID 205604"),
    ("V07", "dh1", "has", "6) Detainment - Spell ID 205596"),
    ("V08", "dh1", "has", "7) Unending Hatred - Spell ID 213480"),
    ("V09", "dh1", "has", "8) Mana Break - Spell ID 203704"),
    ("V10", "dh1", "has", "9) Rain from Above - Spell ID 206803"),
    ("V11", "dh1", "has", "cooldown of Metamorphosis is reduced by 2 min, but the form now lasts 15 sec"),
    ("V12", "dh1", "has", "increases the mana cost of their spells by 30% for 10 sec (8.3 patch-note text)"),
    ("V13", "dh1", "absent", "Everlasting Hunt - PvpTalent ID 815, Spell ID 205626: Dealing damage increases movement speed by 15%"),
    ("V14", "dh1", "has", "Havoc's own PvpTalent.db2 row listing is unverified"),

    # --- DH2 facts ---
    ("I01", "dh2", "has", "Leather Specialization (Spell ID 178976: +5% Agility)"),
    ("I02", "dh2", "absent", "226359"),
    ("I03", "dh2", "absent", "217996"),
    ("I04", "dh2", "has", "SHOULDERS | Delusions of Grandeur | 144279 | 265 | 101"),
    ("I05", "dh2", "has", "WRIST | Sea Dog's Cuffs | 158305 | 217 | 111"),
    ("I06", "dh2", "has", "LEGS | Silver-Trimmed Breeches | 159297 | 217 | 111"),
    ("I07", "dh2", "has", "MAIN HAND | Twinblades of the Deceiver (Verus) | 127829"),
    ("I08", "dh2", "has", "OFF HAND | Twinblades of the Deceiver (Muramas) | 127830"),
    ("I09", "dh2", "has", "Quest ID 40817 Twinblades of the Deceiver Chosen"),
    ("I10", "dh2", "absent", "Aldrachi Warblades (Main Hand) |"),
    ("I11", "dh2", "absent", "Quest ID 41863"),
    ("I12", "dh2", "absent", "Oblivion's Embrace |"),
    ("I13", "dh2", "absent", "The Defiler's Lost Vambraces"),
    ("I14", "dh2", "has", "Havoc 2P Bonus (Spell ID 251767): Eye Beam damage increased by 40%"),
    ("I15", "dh2", "has", "4P Spell ID 251769: when Eye Beam finishes its full channel, Haste is increased by 25% for 8 sec"),
    ("I16", "dh2", "has", "Havoc Tier 21 2-Piece (Item Set ID 1329, Felreaper Vestments)"),
    ("I17", "dh2", "absent", "Vengeance 2P Bonus"),
    ("I18", "dh2", "has", "Priority Havoc Azerite traits: Eyes of Rage (Power Spell ID 278500), Furious Gaze (Power Spell ID 273232), Revolving Blades (Power Spell ID 279581)"),
    ("I19", "dh2", "has", "grants Row 5 talent First Blood Spell ID 206416 for free in Havoc spec"),
    ("I20", "dh2", "absent", "Fallout Spell ID 227174"),
    ("I21", "dh2", "has", "stacking additively with Soul Rending 204909"),
    ("I22", "dh2", "absent", "Frailty 247456"),
    ("I23", "dh2", "absent", "Mastery: Fel Blood Spell ID 203747"),
    ("I24", "dh2", "absent", "Riposte Spell ID 207197"),
    ("I25", "dh2", "absent", "Spirit Bomb"),
    ("I26", "dh2", "absent", "Infernal Strike"),
    ("I27", "dh2", "absent", "Demon Spikes"),
    ("I28", "dh2", "absent", "Gold-Tasseled Epaulets"),
    ("I29", "dh2", "has", "Haste-reduced cooldowns on Immolation Aura 258920, Eye Beam 198013, Metamorphosis 191427, Throw Glaive 185123"),
    ("I30", "dh2", "has", "111 -> 217"),
    ("I31", "dh2", "count", (r"^(HEAD|NECK|SHOULDERS|BACK|CHEST|WRIST|HANDS|WAIST|LEGS|FEET|FINGER 1|FINGER 2|TRINKET 1|TRINKET 2|MAIN HAND|OFF HAND) \| ", 48)),
    ("I32", "dh2", "has", "Works on both Twinblades of the Deceiver (127829 + 127830) and crafted/dungeon weapons."),
    ("I33", "dh2", "absent", "Fel Devastation"),
    ("I34", "dh2", "absent", "41863"),

    # --- cross-file consistency ---
    ("X01", "rm", "has", "The Havoc specialization (ChrSpecialization ID 577)"),
    ("X02", "route", "has", "Demonic Talent Spell ID 213410"),
    ("X03", "route", "has", "Eyes of Rage: Spell ID 278500"),
    ("X04", "route", "has", "Blind Fury Talent Spell ID 203550"),
    ("X05", "dh1", "has", "Dungeon111_Route.txt section 2"),
]

# windows after each occurrence of 204909 must not carry the old Vengeance values
SR_VALUE_FILES = ["dh1", "dh2", "route"]


def run_checks(docs, verbose=False):
    """Return (passed, failed) lists of check ids."""
    passed, failed = [], []
    for cid, fkey, kind, payload in CHECKS:
        text = docs[fkey]
        ok = False
        if kind == "has":
            ok = payload in text
        elif kind == "absent":
            ok = payload not in text
        elif kind == "count":
            pat, n = payload
            if cid == "I31":
                ok = len(re.findall(pat, text, re.M)) == n
            else:
                ok = text.count(pat) == n
        elif kind == "regex":
            pat, n = payload
            ok = len(re.findall(pat, text)) >= n
        (passed if ok else failed).append(cid)
    # Soul Rending value-window check
    sr_ok = True
    for fkey in SR_VALUE_FILES:
        text = docs[fkey]
        for m in re.finditer(r"204909", text):
            window = text[m.end():m.end() + 150]
            if "+5%" in window or "25% additional" in window:
                sr_ok = False
    (passed if sr_ok else failed).append("X06-sr-values")
    # derived mastery-gem math
    m = re.search(r"\+4\.44% Chaos damage at 111: 50 / 20\.28 rating-per-point \* 1\.8% per point", docs["dh2"])
    derived_ok = bool(m) and abs(round(50 / 20.28 * 1.8, 2) - 4.44) < 1e-9 and "+4.44% Chaos damage" in docs["dh2"]
    (passed if derived_ok else failed).append("X07-mastery-math")
    if verbose:
        for cid in passed:
            print("PASS", cid)
        for cid in failed:
            print("FAIL", cid)
    return passed, failed


def load_all():
    return dict((k, load(v)) for k, v in FILES.items())


def mutation_tests():
    """For every check, corrupt the document so the check must fail."""
    base = load_all()
    base_pass, base_fail = run_checks(base)
    if base_fail:
        print("BASELINE FAIL:", ", ".join(base_fail))
        return False
    total = 0
    detected = 0
    misses = []

    def mutate_and_expect_fail(fkey, new_docs, label):
        nonlocal total, detected
        total += 1
        passed, failed = run_checks(new_docs)
        if failed:
            detected += 1
        else:
            misses.append(label + " -> still PASS (" + ",".join(base_pass[:3]) + "...)")

    for cid, fkey, kind, payload in CHECKS:
        docs = dict(base)
        if kind == "has":
            old = payload
            # corrupt a distinctive slice so every has-check has a probe
            probe = old[: min(40, len(old))]
            new = docs[fkey].replace(old, "XXMUTATEDXX " + old[len(probe):], 1)
            if new == docs[fkey]:
                # payload too short/odd: append a poisoned duplicate context
                new = docs[fkey] + "\nXXMUTATEDXX " + old
            docs[fkey] = new
            mutate_and_expect_fail(fkey, docs, cid + ":has:" + old[:30])
        elif kind == "absent":
            docs[fkey] = docs[fkey] + "\n" + payload
            mutate_and_expect_fail(fkey, docs, cid + ":absent:" + payload[:30])
        elif kind == "count":
            pat, n = payload
            if cid == "I31":
                docs[fkey] = docs[fkey].replace("HEAD | ", "HEADXX | ", 1)
            else:
                docs[fkey] = docs[fkey].replace(pat, pat + " " + pat, 1)
            mutate_and_expect_fail(fkey, docs, cid + ":count:" + str(pat)[:30])

    # special probes: Soul Rending value window
    docs = dict(base)
    docs["dh1"] = docs["dh1"].replace(
        "Soul Rending (Havoc Talent ID 21863, Spell ID 204909): +10% passive Leech",
        "Soul Rending (Havoc Talent ID 21863, Spell ID 204909): +5% passive Leech", 1)
    mutate_and_expect_fail("dh1", docs, "X06:204909 gets +5%")
    # derived math
    docs = dict(base)
    docs["dh2"] = docs["dh2"].replace("+4.44% Chaos damage", "+4.94% Chaos damage", 1)
    mutate_and_expect_fail("dh2", docs, "X07:mastery number falsified")

    print("Static checks      : %d/%d PASS" % (len(base_pass), len(base_pass) + len(base_fail)))
    print("Mutation probes    : %d/%d detected" % (detected, total))
    for m in misses:
        print("  UNDETECTED:", m)
    return not misses and not base_fail


def main():
    docs = load_all()
    if "--self-test" in sys.argv:
        ok = mutation_tests()
        # stability: second full run must match
        ok2 = mutation_tests()
        print("SELF-TEST:", "PASS" if (ok and ok2) else "FAIL")
        sys.exit(0 if (ok and ok2) else 1)
    passed, failed = run_checks(docs, verbose="-v" in sys.argv)
    print("Dungeon111 Havoc audit: %d PASS, %d FAIL" % (len(passed), len(failed)))
    if failed:
        print("FAILED:", ", ".join(failed))
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
