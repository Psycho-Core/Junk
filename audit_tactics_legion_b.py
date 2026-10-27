#!/usr/bin/env python3
"""Audit: Tactics_Legion_B.txt (Old Raids step 16 - Legion B).

Tomb of Sargeras + Antorus, the Burning Throne boss/trash tactics.

Verifiability this session: gh api is 403-blocked for external repos and
wowhead / wowpedia / warcraft.wiki.gg are out of outbound scope, and the
DBM / BigWigs raid modules are not reachable via the git fetch routes that
worked for Mythic+. No readable source exists for spell ids, creature
entries, map ids or coordinates, so per the standing rule everything
numeric in this document is reported unverified (the document self-marks
it). The audit therefore verifies internal structure (20 bosses across
two raids, the tactics fields per boss, raid/trash sections) and reports
coverage gaps honestly instead of inventing numbers.
"""

import re
import subprocess
import sys

sys.path.insert(0, ".")
from audit_common import coord_trace

DOC = "# Ai Research prompts/Old_Raids_completed/Tactics_Legion_B.txt"


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
    """Collapse all whitespace runs so wrapped header lines match as one literal."""
    return re.sub(r"\s+", " ", text)


def boss_blocks(text):
    """Split into (header, body) for the 20 numbered bosses."""
    heads = [m for m in re.finditer(
        r"^(1[0-9]|20|[1-9])\. ([A-Z][^\n]+)", text, re.M)]
    blocks = []
    for i, m in enumerate(heads):
        start = m.start()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        blocks.append((m.group(0), text[start:end]))
    return blocks


def source_notes():
    return [
        "    gh api: 403 for external repos this session (token scoped to Junk)",
        "    wowhead / wowpedia / warcraft.wiki.gg: out of outbound scope",
        "    DBM / BigWigs raid modules: not reachable via git fetch this session",
        "    => no readable source; every spell id, creature entry, map id and",
        "       coordinate in the document is reported unverified",
    ]


# ---------------------------------------------------------------- stage 1
STATIC_CHECKS = [
    ("heading", "Tactics: Legion B (Step 16)"),
    ("tomb section", "TOMB OF SARGERAS"),
    ("antorus section", "ANTORUS, THE BURNING THRONE"),
    ("trash section", "TRASH: pack breakdowns unverified for both raids."),
    ("honesty spell ids", "Spell ids unverified;"),
    ("honesty entries/maps/coords",
     "Creature entries, map ids, coordinates unverified unless stated."),
    ("step ref", "Step 16"),
]

NEGATIVE_CHECKS = []


def run_static(ftext):
    fails = []
    lines = []
    for name, lit in STATIC_CHECKS:
        hit = lit in ftext
        lines.append("    %-32s %s" % (name, "ok" if hit else "MISSING"))
        if not hit:
            fails.append(name)
    for name, lit in NEGATIVE_CHECKS:
        hit = lit not in ftext
        lines.append("    %-32s %s" % (name, "ok" if hit else "PRESENT!"))
        if not hit:
            fails.append(name)
    return fails, lines


# ---------------------------------------------------------------- stage 2
# Each mutation's OLD literal must byte-match a STATIC_CHECKS literal and
# occur exactly once in the document, so mutating it breaks that check.
MUTATIONS = [
    ("heading", "Tactics: Legion B (Step 16)", "Tactics: Legion B (Step 15)"),
    ("tomb section", "TOMB OF SARGERAS", "TOMB OF SARGERAX"),
    ("antorus section", "ANTORUS, THE BURNING THRONE",
     "ANTORUS, THE FROZEN THRONE"),
    ("trash section", "TRASH: pack breakdowns unverified for both raids.",
     "TRASH: pack breakdowns unverified for neither raid."),
    ("honesty spell ids", "Spell ids unverified;", "Spell ids verified;"),
    ("honesty entries/maps/coords",
     "Creature entries, map ids, coordinates unverified unless stated.",
     "Creature entries, map ids, coordinates unverified unless confirmed."),
    ("step ref", "Step 16", "Step 15"),
]


# ---------------------------------------------------------------- stage 3
def stage3():
    ok = True
    lines = []
    for ln in source_notes():
        lines.append(ln)
    lines.append("    readable source: none -> all numeric claims unverified")
    return ok, lines


# ---------------------------------------------------------------- stage 4
def run_derived(ftext, blocks):
    fails = []
    lines = []
    n_boss = len(blocks)
    lines.append("    bosses numbered 1..20: %d/20" % n_boss)
    if n_boss != 20:
        fails.append("boss count != 20")

    lines.append("    PHASES: field: %d/20 bosses" % ftext.count("PHASES:"))
    lines.append("    AI RULE: field: %d/20 bosses" % ftext.count("AI RULE:"))
    lines.append("    TANK: field: %d/20 bosses"
                 % ftext.count("TANK:"))
    lines.append("    ADD ORDER: field: %d/20 bosses"
                 % ftext.count("ADD ORDER:"))
    grp = sum(1 for _, b in blocks
              if ("GROUP:" in b or "GROUP RULE:" in b))
    lines.append("    GROUP / GROUP RULE: field: %d/20 bosses" % grp)

    full = 0
    incomplete = []
    for h, b in blocks:
        have = ("PHASES:" in b and "TANK:" in b and "ADD ORDER:" in b
                and "AI RULE:" in b
                and ("GROUP:" in b or "GROUP RULE:" in b))
        if have:
            full += 1
        else:
            missing = []
            for f in ("PHASES:", "TANK:", "ADD ORDER:", "AI RULE:"):
                if f not in b:
                    missing.append(f)
            if not ("GROUP:" in b or "GROUP RULE:" in b):
                missing.append("GROUP/GROUP RULE:")
            incomplete.append((h, missing))
    lines.append("    bosses with all five core fields: %d/20" % full)
    if incomplete:
        lines.append("    incomplete bosses:")
        for h, missing in incomplete:
            lines.append("      %s -> %s" % (h, ", ".join(missing)))
    return fails, lines


# ---------------------------------------------------------------- stage 5
def stage5(ftext):
    fails = []
    lines = []
    ok_c, c_lines, missing = coord_trace(ftext, {})
    lines += c_lines
    if missing:
        fails.append("coordinate trace")
        lines.append("    UNEXPECTED coordinate not traceable")
    else:
        lines.append("    no coordinate triples in document "
                     "(all coordinates unverified): ok")
    return fails, lines


# ---------------------------------------------------------------- main
def main():
    text = read(DOC)
    ftext = flat(text)
    blocks = boss_blocks(text)

    print("=" * 68)
    print("AUDIT: Tactics_Legion_B.txt (Old Raids step 16 - Legion B)")
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
    fails4, lines4 = run_derived(ftext, blocks)
    for ln in lines4:
        print(ln)

    print("\n[5] Coordinate trace")
    fails5, lines5 = stage5(ftext)
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
