#!/usr/bin/env python3
"""Audit all 17 Positions_*.txt deliverables (BfA_Positions_Completed).

Families: T titles, M map/instance, B boss/encounter evidence, C coordinate
evidence, S file structure, G unverified contract, X source citations,
H hygiene (programmatic, per file).
CHECKS entries are (family, filename, needle); every needle must appear in
the named file on a single line (wrap-safe). Self-test mutates one file per
mutation and requires >= 1 failing check; each mutation literal must occur
exactly once in that file.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = [
    "Positions_Atal_Dazar.txt",
    "Positions_Battle_of_Dazar_alor.txt",
    "Positions_Crucible_of_Storms.txt",
    "Positions_Freehold.txt",
    "Positions_Kings_Rest.txt",
    "Positions_Ny_alotha_the_Waking_City.txt",
    "Positions_Operation_Mechagon_Junkyard.txt",
    "Positions_Operation_Mechagon_Workshop.txt",
    "Positions_Shrine_of_the_Storm.txt",
    "Positions_Siege_of_Boralus.txt",
    "Positions_Temple_of_Sethraliss.txt",
    "Positions_The_Eternal_Palace.txt",
    "Positions_The_MOTHERLODE.txt",
    "Positions_The_Underrot.txt",
    "Positions_Tol_Dagor.txt",
    "Positions_Uldir.txt",
    "Positions_Waycrest_Manor.txt",
]
CHECKS = []


def add(fam, fname, *needles):
    for n in needles:
        CHECKS.append((fam, fname, n))


# --- T: titles -------------------------------------------------------------
add("T", "Positions_Atal_Dazar.txt", "POSITIONS AND NUMBERS - ATAL'DAZAR")
add("T", "Positions_Battle_of_Dazar_alor.txt", "POSITIONS AND NUMBERS - BATTLE OF DAZAR'ALOR")
add("T", "Positions_Crucible_of_Storms.txt", "POSITIONS AND NUMBERS - CRUCIBLE OF STORMS")
add("T", "Positions_Freehold.txt", "FREEHOLD - POSITIONS AND NUMBERS, BATTLE FOR AZEROTH 8.3.7 BUILD 35662")
add("T", "Positions_Kings_Rest.txt", "KINGS' REST - POSITIONS AND NUMBERS, BATTLE FOR AZEROTH 8.3.7 BUILD 35662")
add("T", "Positions_Ny_alotha_the_Waking_City.txt", "POSITIONS AND NUMBERS - NY'ALOTHA, THE WAKING CITY")
add("T", "Positions_Operation_Mechagon_Junkyard.txt", "=== OPERATION MECHAGON JUNKYARD - MAP 2097 ===")
add("T", "Positions_Operation_Mechagon_Workshop.txt", "=== OPERATION MECHAGON WORKSHOP - MAP 2097 ===")
add("T", "Positions_Shrine_of_the_Storm.txt", "SHRINE OF THE STORM - POSITIONS AND NUMBERS, BFA 8.3.7 BUILD 35662")
add("T", "Positions_Siege_of_Boralus.txt", "SIEGE OF BORALUS - POSITIONS AND NUMBERS, BFA 8.3.7 BUILD 35662")
add("T", "Positions_Temple_of_Sethraliss.txt", "TEMPLE OF SETHRALISS - POSITIONS AND NUMBERS, BFA 8.3.7 BUILD 35662")
add("T", "Positions_The_Eternal_Palace.txt", "POSITIONS AND NUMBERS - THE ETERNAL PALACE")
add("T", "Positions_The_MOTHERLODE.txt", "THE MOTHERLODE!! - POSITIONS AND NUMBERS, BFA 8.3.7 BUILD 35662")
add("T", "Positions_The_Underrot.txt", "THE UNDERROT - POSITIONS AND NUMBERS, BFA 8.3.7 BUILD 35662")
add("T", "Positions_Tol_Dagor.txt", "TOL DAGOR - POSITIONS AND NUMBERS, BFA 8.3.7 BUILD 35662")
add("T", "Positions_Uldir.txt", "POSITIONS AND NUMBERS - ULDIR")
add("T", "Positions_Waycrest_Manor.txt", "=== WAYCREST MANOR - MAP 1862 ===")

# --- M: map / instance -----------------------------------------------------
add("M", "Positions_Atal_Dazar.txt", "Map      : 1763   Client: 8.3.7 build 35662")
add("M", "Positions_Battle_of_Dazar_alor.txt", "Map      : 2070   Client: 8.3.7 build 35662")
add("M", "Positions_Crucible_of_Storms.txt", "Map      : 2096   Client: 8.3.7 build 35662")
add("M", "Positions_Freehold.txt", "Map id 1754. Four encounters: Skycap'n Kragg, Council o' Captains, Ring of")
add("M", "Positions_Kings_Rest.txt", "Map id 1762. Four encounters: The Golden Serpent, Mchimba the Embalmer, The")
add("M", "Positions_Ny_alotha_the_Waking_City.txt", "Map      : 2217   Client: 8.3.7 build 35662")
add("M", "Positions_Operation_Mechagon_Junkyard.txt", "Instance script: RegisterInstanceScript(instance_operation_mechagon, 2097)")
add("M", "Positions_Operation_Mechagon_Workshop.txt", "Instance script: RegisterInstanceScript(instance_operation_mechagon, 2097)")
add("M", "Positions_Shrine_of_the_Storm.txt", "Map id 1864. Four encounters: Aqu'sirr, the Tidesage Council (Brother")
add("M", "Positions_Siege_of_Boralus.txt", "Map id 1822. Five encounters: Chopper Redhook, Sergeant Bainbridge,")
add("M", "Positions_Temple_of_Sethraliss.txt", "Map id 1877. Four encounters, five boss creatures: Adderis and")
add("M", "Positions_The_Eternal_Palace.txt", "Map      : 2164   Client: 8.3.7 build 35662")
add("M", "Positions_The_MOTHERLODE.txt", "Map id 1594. Four encounters: Coin-Operated Crowd Pummeler 129214,")
add("M", "Positions_The_Underrot.txt", "Map id 1841. Four boss encounters: Elder Leaxa 131318, Cragmaw the")
add("M", "Positions_Tol_Dagor.txt", "Map id 1771. Four boss encounters: The Sand Queen 127479, Jes Howlis")
add("M", "Positions_Uldir.txt", "Map      : 1861   Area: 9389   Client: 8.3.7 build 35662")
add("M", "Positions_Waycrest_Manor.txt", "Instance script: RegisterInstanceScript(instance_waycrest_manor, 1862)")

# --- B: boss / encounter evidence -----------------------------------------
add("B", "Positions_Atal_Dazar.txt", "4. BOSS 1 - PRIESTESS ALUN'ZA")
add("B", "Positions_Battle_of_Dazar_alor.txt", "4. BOSS 1 - CHAMPION OF THE LIGHT")
add("B", "Positions_Crucible_of_Storms.txt", "4. BOSS 1 - THE RESTLESS CABAL")
add("B", "Positions_Freehold.txt", "4. BOSS 1 - SKYCAP'N KRAGG  (entry 126832, MDT hp 5,379,459, level 122)")
add("B", "Positions_Kings_Rest.txt", "4. BOSS 1 - THE GOLDEN SERPENT  (entry 135322, MDT hp 5,379,459, level 122)")
add("B", "Positions_Ny_alotha_the_Waking_City.txt", "4. BOSS 1 - WRATHION, THE BLACK EMPEROR")
add("B", "Positions_Operation_Mechagon_Junkyard.txt", "3. Junkyard bosses (Gobbamak, Gunker, Trixie/Naeno) have no MDT anchor")
add("B", "Positions_Operation_Mechagon_Workshop.txt", "6. Tussle Tonks: two bosses share encounter, DBM tracks both GUIDs. Platinum")
add("B", "Positions_Shrine_of_the_Storm.txt", "4. BOSS 1 - AQU'SIRR  (entry 134056, MDT hp 6,147,954, level 122)")
add("B", "Positions_Siege_of_Boralus.txt", "4. BOSS 1 - CHOPPER REDHOOK  (128650, MDT hp 2,819,992, level 122)")
add("B", "Positions_Temple_of_Sethraliss.txt", "4. BOSS 1 - ADDERIS 133379 AND ASPIX 133944")
add("B", "Positions_The_Eternal_Palace.txt", "4. BOSS 1 - ABYSSAL COMMANDER SIVARA")
add("B", "Positions_The_MOTHERLODE.txt", "4. BOSS 1 - COIN-OPERATED CROWD PUMMELER 129214")
add("B", "Positions_The_Underrot.txt", "4. BOSS 1 - ELDER LEAXA 131318")
add("B", "Positions_Tol_Dagor.txt", "4. BOSS 1 - THE SAND QUEEN 127479")
add("B", "Positions_Uldir.txt", "4. BOSS 1 - TALOC")
add("B", "Positions_Waycrest_Manor.txt", "5. Heartsbane Triad: three sisters share ENCOUNTER_ID 2116 but have separate")

# --- C: coordinate evidence ------------------------------------------------
add("C", "Positions_Atal_Dazar.txt", "Entry pad      game_tele 1873  (-848.182129, 2073.235596, 725.144592)")
add("C", "Positions_Battle_of_Dazar_alor.txt", "(-417.682, 1191.241, 320.289) o 3.113")
add("C", "Positions_Crucible_of_Storms.txt", "The Restless Cabal arena centre  (3631.75, -1729.25,   85.65)")
add("C", "Positions_Freehold.txt", "(-1583.321777, -1005.083862, 73.821770)  o 2.468250")
add("C", "Positions_Kings_Rest.txt", "(-1016.96, 2699.47, 809.916) o 3.86648")
add("C", "Positions_Ny_alotha_the_Waking_City.txt", "arena centre        (-1756.909, -43.431, -1477.872) o 6.2706")
add("C", "Positions_Operation_Mechagon_Junkyard.txt", "Bot positions: (626.62,-348.21,0.42), (595.42,-325.17,1.02),")
add("C", "Positions_Operation_Mechagon_Workshop.txt", "Script spawn: (632.534, -43.874, 92.058, 5.39) sub4 (flying)")
add("C", "Positions_Shrine_of_the_Storm.txt", "are (4167.202, -1238.528, 186.894) o 4.730950, on map 1864 [DB]")
add("C", "Positions_Siege_of_Boralus.txt", "Home: (620.000, -245.000, 12.580) o 1.000, map 1822 [SRV]")
add("C", "Positions_Temple_of_Sethraliss.txt", "centre is exact: (3344.53, 3148.79, 88.43), commented //45y")
add("C", "Positions_The_Eternal_Palace.txt", "arena centre                (298.54, 153.91, 1449.97)   script \"//40y\"")
add("C", "Positions_The_MOTHERLODE.txt", "arena centre is (1215.50, -3325.10, 57.33), commented //40y, and")
add("C", "Positions_The_Underrot.txt", "centerPlatform - Leaxa's (868.98, 1230.07, 56.30) and Zancha's")
add("C", "Positions_Tol_Dagor.txt", "that carry x, y and z (3.1), the only z values in the")
add("C", "Positions_Uldir.txt", "(-334.4931, -276.9445, 1120.836) o 2.291085")
add("C", "Positions_Waycrest_Manor.txt", "Soulbound Goliath Burning Brush position hardcoded (-409,-261,234, o=3).")

# --- S: structure ----------------------------------------------------------
add("S", "Positions_Atal_Dazar.txt", "0. HOW TO READ THIS FILE")
add("S", "Positions_Battle_of_Dazar_alor.txt", "0. HOW TO READ THIS FILE")
add("S", "Positions_Crucible_of_Storms.txt", "0. HOW TO READ THIS FILE")
add("S", "Positions_Freehold.txt", "0. HOW TO READ THIS FILE")
add("S", "Positions_Kings_Rest.txt", "0. HOW TO READ THIS FILE")
add("S", "Positions_Ny_alotha_the_Waking_City.txt", "0. HOW TO READ THIS FILE")
add("S", "Positions_Shrine_of_the_Storm.txt", "0. HOW TO READ THIS FILE")
add("S", "Positions_The_Eternal_Palace.txt", "0. HOW TO READ THIS FILE")
add("S", "Positions_Uldir.txt", "0. HOW TO READ THIS FILE")
add("S", "Positions_Tol_Dagor.txt", "0. READ THIS FIRST - WHAT THIS FILE CAN AND CANNOT GIVE")
add("S", "Positions_Uldir.txt", "1. SOURCES AND THEIR LIMITS")
add("S", "Positions_Freehold.txt", "1. SOURCES AND THEIR LIMITS")
add("S", "Positions_Tol_Dagor.txt", "1. SOURCES AND THEIR LIMITS")
add("S", "Positions_Operation_Mechagon_Junkyard.txt", "1. No creature spawn table (world coordinates with z) exists in any readable")
add("S", "Positions_Operation_Mechagon_Workshop.txt", "1. No creature spawn table (world coordinates with z) exists in any readable")
add("S", "Positions_Waycrest_Manor.txt", "1. No creature spawn table (world coordinates with z) exists in any readable")

# --- G: unverified contract ------------------------------------------------
add("G", "Positions_Atal_Dazar.txt", "11. WHAT IS NOT IN THIS FILE, AND WHY")
add("G", "Positions_Battle_of_Dazar_alor.txt", "13. WHAT IS STILL UNVERIFIED, AND WHAT WOULD RESOLVE IT")
add("G", "Positions_Crucible_of_Storms.txt", "7. WHAT IS STILL UNVERIFIED, AND WHAT WOULD RESOLVE IT")
add("G", "Positions_Freehold.txt", "11. WHAT IS NOT IN THIS FILE, AND WHY")
add("G", "Positions_Kings_Rest.txt", "11. WHAT IS NOT IN THIS FILE, AND WHY")
add("G", "Positions_Ny_alotha_the_Waking_City.txt", "17. WHAT IS STILL UNVERIFIED, AND WHAT WOULD RESOLVE IT")
add("G", "Positions_Shrine_of_the_Storm.txt", "11. WHAT IS NOT IN THIS FILE, AND WHY")
add("G", "Positions_Siege_of_Boralus.txt", "12. WHAT IS NOT IN THIS FILE, AND WHY")
add("G", "Positions_Temple_of_Sethraliss.txt", "11. WHAT IS NOT IN THIS FILE, AND WHY")
add("G", "Positions_The_Eternal_Palace.txt", "13. WHAT IS STILL UNVERIFIED, AND WHAT WOULD RESOLVE IT")
add("G", "Positions_The_MOTHERLODE.txt", "11. WHAT IS NOT IN THIS FILE, AND WHY")
add("G", "Positions_The_Underrot.txt", "11. WHAT IS NOT IN THIS FILE, AND WHY")
add("G", "Positions_Tol_Dagor.txt", "\"unverified\".")
add("G", "Positions_Uldir.txt", "12. WHAT IS STILL UNVERIFIED, AND WHAT WOULD RESOLVE IT")
add("G", "Positions_Operation_Mechagon_Junkyard.txt", "All boss spawn positions, tank positions, safe spots: z = unverified (no")
add("G", "Positions_Operation_Mechagon_Workshop.txt", "z = unverified (MDT has no z)")
add("G", "Positions_Waycrest_Manor.txt", "=== 5. SAFE SPOTS / POSITIONING (z = unverified unless noted) ===")

# --- X: source citations ---------------------------------------------------
add("X", "Positions_Uldir.txt", "world/2020_08_13_00_uldir.sql, VerifiedBuild 28153")
add("X", "Positions_Operation_Mechagon_Junkyard.txt", "Psycho-Core/Psycho-Core-8.3.7_Scripts scripts/KulTiras/Operation Mechagon/")
add("X", "Positions_Operation_Mechagon_Workshop.txt", "LetsTimeIt/DungeonTools BattleForAzeroth/MechagonCity.lua (MDT)")
add("X", "Positions_Waycrest_Manor.txt", "LetsTimeIt/DungeonTools BattleForAzeroth/WaycrestManor.lua (MDT)")
add("X", "Positions_Tol_Dagor.txt", "[SRV]  a line in the 8.3.7 script: tol_dagor.h,")


def hygiene_failures():
    out = []
    for name in FILES:
        t = (HERE / name).read_text(encoding="utf-8")
        lines = t.split("\n")
        if any(b > 127 for b in t.encode("utf-8")):
            out.append(f"{name}: non-ASCII byte")
        if "\t" in t:
            out.append(f"{name}: tab")
        if not t.endswith("\n"):
            out.append(f"{name}: no final newline")
        tw = [i for i, ln in enumerate(lines, 1) if ln != ln.rstrip()]
        if tw:
            out.append(f"{name}: trailing whitespace line {tw[0]}")
        lg = [i for i, ln in enumerate(lines, 1) if len(ln) > 100]
        if lg:
            out.append(f"{name}: >100 cols line {lg[0]}")
    return out


def load(name):
    return (HERE / name).read_text(encoding="utf-8")


def run_checks(texts):
    return [(fam, fn, n) for fam, fn, n in CHECKS if n not in texts[fn]]


def report():
    texts = {n: load(n) for n in FILES}
    failures = run_checks(texts)
    h = hygiene_failures()
    by_fam = {}
    for fam, _, _ in CHECKS:
        by_fam[fam] = by_fam.get(fam, 0) + 1
    total = len(CHECKS)
    for fam in sorted(by_fam):
        nf = sum(1 for f, _, _ in failures if f == fam)
        print(f"family {fam}: {by_fam[fam] - nf}/{by_fam[fam]} {'PASS' if nf == 0 else f'FAIL {nf}'}")
    print(f"checks: {total - len(failures)}/{total} {'PASS' if not failures else 'FAIL'}")
    if h:
        for m in h:
            print(f"hygiene FAIL: {m}")
    else:
        print("hygiene PASS (17 files)")
    for fam, fn, n in failures:
        print(f"  MISS [{fam}] {fn}: {n[:70]}")
    return not failures and not h


MUTATIONS = [
    ("Positions_Uldir.txt", "POSITIONS AND NUMBERS - ULDIR", "POSITIONS AND NUMBERZ - ULDIR"),
    ("Positions_Waycrest_Manor.txt", "=== WAYCREST MANOR - MAP 1862 ===", "=== WAYCREST MANOR - MAP 1863 ==="),
    ("Positions_Freehold.txt", "Map id 1754.", "Map id 1755."),
    ("Positions_Atal_Dazar.txt", "Map      : 1763   Client: 8.3.7 build 35662", "Map      : 1764   Client: 8.3.7 build 35662"),
    ("Positions_Uldir.txt", "4. BOSS 1 - TALOC", "4. BOSS 1 - TALOQ"),
    ("Positions_Tol_Dagor.txt", "4. BOSS 1 - THE SAND QUEEN 127479", "4. BOSS 1 - THE SAND QUEEN 127478"),
    ("Positions_Battle_of_Dazar_alor.txt", "(-417.682, 1191.241, 320.289) o 3.113", "(-417.682, 1191.241, 320.290) o 3.113"),
    ("Positions_Uldir.txt", "(-334.4931, -276.9445, 1120.836) o 2.291085", "(-334.4931, -276.9445, 1120.837) o 2.291085"),
    ("Positions_Tol_Dagor.txt", "0. READ THIS FIRST - WHAT THIS FILE CAN AND CANNOT GIVE",
     "0. READ THIS FIRST - WHAT THIS FILE CAN AND COULD NOT GIVE"),
    ("Positions_Uldir.txt", "1. SOURCES AND THEIR LIMITS", "2. SOURCES AND THEIR LIMITS"),
    ("Positions_Operation_Mechagon_Junkyard.txt", "safe spots: z = unverified (no", "safe spots: z = verified (no"),
    ("Positions_Waycrest_Manor.txt", "(z = unverified unless noted)", "(z = verified unless noted)"),
    ("Positions_Uldir.txt", "world/2020_08_13_00_uldir.sql", "world/2020_08_14_00_uldir.sql"),
    ("Positions_Waycrest_Manor.txt", "BattleForAzeroth/WaycrestManor.lua", "BattleForAzeroth/Waycrest.lua"),
]


def self_test():
    originals = {n: load(n) for n in FILES}
    total_pass = 0
    for rnd in (1, 2):
        npass = 0
        bad = []
        for i, (fn, old, new) in enumerate(MUTATIONS, 1):
            count = originals[fn].count(old)
            if count != 1:
                bad.append((i, f"literal occurs {count}x in {fn}"))
                continue
            texts = dict(originals)
            texts[fn] = originals[fn].replace(old, new, 1)
            if run_checks(texts):
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
    ok = report()
    if "--self-test" in sys.argv:
        st = self_test()
        sys.exit(0 if (ok and st) else 1)
    sys.exit(0 if ok else 1)
