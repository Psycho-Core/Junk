#!/usr/bin/env python3
"""Audit: Twink29_Prof_Jewelcrafting.txt (Twink29 Professions step 07).

Jewelcrafting for a level 29 battleground twink on a private BfA 8.3.7
(build 35662) server: wearable neck/rings, the gem answer (none), prospecting,
trainers, the sub-120 route, and class recommendations.

Verifiability this session: gh api is 403-blocked for external repos and
wowhead / wowpedia / warcraft.wiki.gg are out of outbound scope, so there is
no readable external source for item ids, spell ids, creature entries, map
ids or coordinates. Per the standing rule, every numeric claim in the
document is therefore reported unverified (the document self-marks them).
The audit verifies internal structure (8 sections, the route table, the
rank-spell line, the honesty markings) and reports coverage honestly instead
of inventing numbers. Every mutation literal below occurs exactly once in the
document, so each mutation breaks its corresponding static check.
"""

import re
import subprocess
import sys

sys.path.insert(0, ".")
from audit_common import coord_trace

DOC = "# Ai Research prompts/Twink29_Professions-completed/Twink29_Prof_Jewelcrafting.txt"


def _sh(args, cwd=None):
    res = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError("%s failed: %s" % (" ".join(args[:3]),
                                              (res.stderr or res.stdout).strip()))
    return res.stdout


def read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read().replace("\r\n", "\n")


def flat(text):
    """Collapse all whitespace runs so wrapped table rows match as one literal."""
    return re.sub(r"\s+", " ", text)


def source_notes():
    return [
        "    gh api: 403 for external repos this session (token scoped to Junk)",
        "    wowhead / wowpedia / warcraft.wiki.gg: out of outbound scope",
        "    => no readable source; every item id, spell id, creature entry,",
        "       map id and coordinate in the document is reported unverified",
        "    readable source: none -> all numeric claims unverified",
    ]


# ---------------------------------------------------------------- stage 1
STATIC_CHECKS = [
    ("heading", "TWINK29 - PROFESSIONS - STEP 07 - JEWELCRAFTING"),
    ("server context",
     "private Battle for Azeroth 8.3.7 build 35662, TrinityCore base."),
    ("skill line and cap", "skill line 755, capped at 225"),
    ("section 1", "1. THE FIRST THING THAT HAS TO BE SAID"),
    ("section 2", "2. WHAT A 29 CAN ACTUALLY WEAR"),
    ("section 3", "3. GEMS - THE THING THE PROMPT ASKS ABOUT, AND THE ANSWER IS NOT YET"),
    ("section 4", "4. PROSPECTING - THE ONLY ECONOMY ANGLE"),
    ("section 5", "5. TRAINERS"),
    ("section 6", "6. THE CHEAPEST ROUTE TO WHAT A 29 NEEDS"),
    ("section 7", "7. ALT - WHAT A 29 CANNOT DO"),
    ("section 8", "8. WHICH CLASSES SHOULD TAKE IT"),
    ("rank spells", "apprentice 25229 (cap 75), journeyman 25230 at skill 50, "
     "expert 28894 at skill 125, artisan 28895 at skill 200, master 28897 at skill 275"),
    ("pendant", "Pendant of the Agate Shield 20950"),
    ("pendant spell", "Spell 25610"),
    ("pendant design", "Design 20970"),
    ("twilight ring", "20828 Ring of Twilight Shadows"),
    ("twilight ring spell", "Spell 25318"),
    ("pearl ring", "Simple Pearl Ring 20820"),
    ("pearl ring spell", "Spell 25284"),
    ("woven copper ring", "21931 Woven Copper Ring"),
    ("heavy copper ring", "21932 Heavy Copper Ring"),
    ("woven spell", "Spell 26925"),
    ("heavy copper spell", "Spell 26926"),
    ("prospecting", "Spell 31252, Jewelcrafting 20"),
    ("stop points", "100 for Ring of Twilight Shadows, 120 for the Pendant"),
    ("bold blood garnet", "Bold Blood Garnet 23095"),
    ("garnet spell", "28905 at Jewelcrafting 305"),
    ("socket unverified", "no 29 item has a socket"),
    ("trainers unverified", "all three are unverified"),
    ("prospecting yields unverified", "the yields are unverified"),
    ("shopping copper", "160x Copper Bar 2840"),
    ("shopping bronze", "100x Bronze Bar 2841"),
    ("shopping stone", "200x Heavy Stone 2838"),
]

NEGATIVE_CHECKS = []


def run_static(ftext):
    fails = []
    lines = []
    for name, lit in STATIC_CHECKS:
        hit = lit in ftext
        lines.append("    %-30s %s" % (name, "ok" if hit else "MISSING"))
        if not hit:
            fails.append(name)
    for name, lit in NEGATIVE_CHECKS:
        hit = lit not in ftext
        lines.append("    %-30s %s" % (name, "ok" if hit else "PRESENT!"))
        if not hit:
            fails.append(name)
    return fails, lines


# ---------------------------------------------------------------- stage 2
# Each OLD literal must byte-match a STATIC_CHECKS literal and occur exactly
# once in the document, so mutating it breaks that check.
MUTATIONS = [
    ("heading", "TWINK29 - PROFESSIONS - STEP 07 - JEWELCRAFTING",
     "TWINK29 - PROFESSIONS - STEP 06 - JEWELCRAFTING"),
    ("server build", "private Battle for Azeroth 8.3.7 build 35662, TrinityCore base.",
     "private Battle for Azeroth 8.3.7 build 35663, TrinityCore base."),
    ("skill cap", "skill line 755, capped at 225", "skill line 755, capped at 226"),
    ("rank master", "master 28897 at skill 275", "master 28897 at skill 276"),
    ("pendant id", "Pendant of the Agate Shield 20950",
     "Pendant of the Agate Shield 20951"),
    ("pendant spell", "Spell 25610", "Spell 25611"),
    ("design id", "Design 20970", "Design 20971"),
    ("twilight ring id", "20828 Ring of Twilight Shadows", "20829 Ring of Twilight Shadows"),
    ("twilight spell", "Spell 25318", "Spell 25319"),
    ("pearl ring id", "Simple Pearl Ring 20820", "Simple Pearl Ring 20821"),
    ("pearl spell", "Spell 25284", "Spell 25285"),
    ("woven ring id", "21931 Woven Copper Ring", "21933 Woven Copper Ring"),
    ("heavy copper ring id", "21932 Heavy Copper Ring", "21933 Heavy Copper Ring"),
    ("prospecting spell", "Spell 31252, Jewelcrafting 20", "Spell 31253, Jewelcrafting 20"),
    ("stop points", "100 for Ring of Twilight Shadows, 120 for the Pendant",
     "101 for Ring of Twilight Shadows, 121 for the Pendant"),
    ("bold blood garnet", "Bold Blood Garnet 23095", "Bold Blood Garnet 23096"),
    ("socket unverified", "no 29 item has a socket", "no 30 item has a socket"),
    ("trainers unverified", "all three are unverified", "all three are verified"),
    ("prospecting yields unverified", "the yields are unverified",
     "the yields are verified"),
    ("section 8", "8. WHICH CLASSES SHOULD TAKE IT",
     "9. WHICH CLASSES SHOULD TAKE IT"),
]


# ---------------------------------------------------------------- stage 3
def stage3():
    ok = True
    lines = []
    for ln in source_notes():
        lines.append(ln)
    return ok, lines


# ---------------------------------------------------------------- stage 4
def run_derived(ftext):
    fails = []
    lines = []
    # route table: six rows, checked via distinctive flattened substrings
    route_rows = [
        "Delicate Copper Wire 25255",
        "Bronze Setting 25278",
        "Simple Pearl Ring 20820",
        "Ring of Twilight Shadows 25318",
        "Heavy Stone Statue 32807",
    ]
    found = 0
    for row in route_rows:
        if row in ftext:
            found += 1
        else:
            fails.append("route row missing: %s" % row)
    lines.append("    route table rows present: %d/5" % found)
    # shopping list
    shop = ["160x Copper Bar 2840", "100x Bronze Bar 2841", "200x Heavy Stone 2838"]
    shop_found = sum(1 for s in shop if s in ftext)
    lines.append("    shopping list rows present: %d/3" % shop_found)
    if shop_found != 3:
        fails.append("shopping list incomplete")
    # section count
    n_sec = sum(1 for i in range(1, 9)
                if ("%d. " % i) in ftext or ("%d.  " % i) in ftext)
    lines.append("    numbered sections present: %d/8" % n_sec)
    if n_sec != 8:
        fails.append("section count != 8")
    # unverified markings (honesty)
    unv = ftext.count("unverified")
    lines.append("    'unverified' markings: %d" % unv)
    if unv < 5:
        fails.append("too few unverified markings")
    return fails, lines


# ---------------------------------------------------------------- stage 5
def stage5(text, ftext):
    fails = []
    lines = []
    ok_c, c_lines, missing = coord_trace(text, {})
    lines += c_lines
    if missing:
        fails.append("coordinate trace")
        lines.append("    UNEXPECTED coordinate triple not traceable")
    else:
        lines.append("    no (x,y,z) coordinate triples in document "
                     "(coords cited are unverified pairs): ok")
    # plain-text hygiene on the original document
    ascii_ok = all(ord(c) < 128 for c in text)
    tab_ok = "\t" not in text
    nl_ok = text.endswith("\n")
    maxcol = max((len(l) for l in text.split("\n")), default=0)
    lines.append("    ASCII: %s, no tabs: %s, final newline: %s, max col: %d"
                 % (ascii_ok, tab_ok, nl_ok, maxcol))
    if not (ascii_ok and tab_ok and nl_ok and maxcol <= 120):
        fails.append("plain-text hygiene")
    return fails, lines


# ---------------------------------------------------------------- main
def main():
    text = read(DOC)
    ftext = flat(text)

    print("=" * 68)
    print("AUDIT: Twink29_Prof_Jewelcrafting.txt (Twink29 Professions step 07)")
    print("=" * 68)

    fails1, lines1 = run_static(ftext)
    total1 = len(STATIC_CHECKS) + len(NEGATIVE_CHECKS)
    print("\n[1] Static checks: %d/%d passed" % (total1 - len(fails1), total1))
    if fails1:
        print("    FAILED: %s" % ", ".join(fails1))
    for ln in lines1:
        print(ln)

    print("\n[2] Mutation testing (%d mutations)" % len(MUTATIONS))
    undetected = []
    for name, old, new in MUTATIONS:
        cnt = ftext.count(old)
        if cnt != 1:
            undetected.append("%s (count=%d)" % (name, cnt))
            continue
        mutated = ftext.replace(old, new, 1)
        f_s, _ = run_static(mutated)
        if not f_s:
            undetected.append(name)
    print("    detected %d/%d" % (len(MUTATIONS) - len(undetected),
                                  len(MUTATIONS)))
    if undetected:
        print("    UNDETECTED: %s" % ", ".join(undetected))

    print("\n[3] Source cross-check (no readable source this session)")
    ok3, lines3 = stage3()
    for ln in lines3:
        print(ln)

    print("\n[4] Derived structure recomputed from document")
    fails4, lines4 = run_derived(ftext)
    for ln in lines4:
        print(ln)

    print("\n[5] Coordinate trace and plain-text hygiene")
    fails5, lines5 = stage5(text, ftext)
    for ln in lines5:
        print(ln)

    all_fails = (fails1 + undetected + ([] if ok3 else ["source"])
                 + fails4 + fails5)
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
