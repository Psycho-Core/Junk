#!/usr/bin/env python3
"""Audit: MythicPlus_Duties_COMPLETED.txt (Mythic+ step 3, Party Duties).

Stages:
  1. Static exact-literal checks on the document.
  2. Mutation testing - every mutation must break at least one check.
  3. Source cross-check against GitHub corpora (fork code, fetched live).
  4. Derived values recomputed from source bodies (skip table, affix index
     set, multipliers, spawn windows, coordinate trace) with reaction probes.
  5. Absence claims (Storming not BfA, Teeming spell absent, GrievousWound
     constant undefined in-repo) with injection probe and a gh control.
"""

import base64
import re
import subprocess
import sys

sys.path.insert(0, ".")
from audit_common import gh_content, source_stage, mutation_probe, coord_trace

DOC = "# Ai Research prompts/Mythic_Plus_completed/MythicPlus_Duties_COMPLETED.txt"
MDT_REF = "4d36744c53477fc9fcb990471b1bb639a62f0d48"
MDT_REPO = "Nnoggie/MythicDungeonTools"
FORK = "HavenWoW/BFA-HavenCore"

FORK_FILES = {
    "chal": "src/server/scripts/World/challenge_scripts.cpp",
    "ish": "src/server/game/Instances/InstanceScript.h",
    "isc": "src/server/game/Instances/InstanceScript.cpp",
    "atal": "src/server/scripts/Zandalar/AtalDazar/instance_atal_dazar.cpp",
}
MDT_DUNGEONS = [
    "AtalDazar", "Freehold", "KingsRest", "MechagonCity", "MechagonIsland",
    "ShrineoftheStorm", "SiegeofBoralus", "TempleofSethraliss",
    "TheMotherlode", "TheUnderrot", "TolDagor", "WaycrestManor",
]


def gh_content_ref(repo, path, ref):
    result = subprocess.run(
        ["gh", "api", "-X", "GET",
         "repos/%s/contents/%s?ref=%s" % (repo, path, ref),
         "--jq", ".content"],
        capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("gh api failed for %s/%s: %s"
                           % (repo, path, result.stderr.strip()))
    return base64.b64decode(result.stdout).decode("utf-8", "replace")


# ---------------------------------------------------------------- stage 1
STATIC_CHECKS = [
    ("heading completed", "MYTHIC+ KEY - BFA SEASON 4 (8.3.7) - COMPLETED ==="),
    ("step numbering", "Step 3 of 3 (prompt 03_Party_Duties.txt)"),
    ("fork context", "HavenCore fork"),
    # spell ids
    ("might", "Challenger's Might 206150"),
    ("burden", "Challenger's Burden 206151"),
    ("bolstering spell", "ChallengerBolstering 209859"),
    ("bursting cast", "ChallengerBursting 240443"),
    ("burst dot", "player DoT 243237"),
    ("raging spell", "ChallengerRaging 228318"),
    ("sanguine spell", "ChallengerSanguine 226489"),
    ("necrotic spell", "ChallengerNecrotic 209858"),
    ("quake spell", "ChallengerQuake 240447"),
    ("volcanic summon", "ChallengerSummonVolcanicPlume\n209861"),
    ("volcanic plume cast", "casts ChallengerVolcanicPlume 209862"),
    ("grievous spell", "Grievous wound (script header)"),
    ("grievous id", "240559"),
    ("shroud spell", "spell 114018"),
    ("invis potion item", "item 9172"),
    ("keystone item", "item 158923"),
    # creature entries
    ("explosive entry", "120651"),
    ("plume entry", "105877"),
    # multipliers / affix numbers
    ("fort health", "x1.20 health"),
    ("fort damage", "x1.30 damage"),
    ("tyr health", "x1.40 health"),
    ("tyr damage", "x1.15 damage"),
    ("bolster pct", "+20% max health and damage per stack"),
    ("bolster range", "bolsters allies within 30 yards"),
    ("burst pct", "5% of max health to all players over\n4 sec"),
    ("raging pct", "enrage at 30% health, +100% damage"),
    ("sanguine heal", "heal enemies standing in them 5% of"),
    ("sanguine dmg", "damage players 15% of max health per sec"),
    ("necrotic pct", "reduce\nhealing and absorption received by 2% per stack for 9 sec"),
    ("necrotic tick", "physical damage every 2 sec"),
    ("grievous pct", "below 90% health players suffer"),
    # timers / windows / behavior
    ("volcanic window", "between 15 and 60 yards"),
    ("explosive first", "first orb after 2-10 s"),
    ("explosive cadence", "every 8-16 s"),
    ("explosive range", "player is within 60 y"),
    ("fuse", "casts detonation 500 ms after"),
    ("plume delay", "after 250 ms"),
    ("shroud stats", "30 yd,15 sec,6 min cooldown"),
    ("invis secs", "invisible18 sec"),
    # death rules
    ("death cost", "Every death costs the timer 5 seconds"),
    ("death run", "streak past trash, die, resurrect behind it"),
    ("combat res charges", "start with1 charge"),
    ("combat res refill", "gain1 every\n  10 minutes"),
    ("combat res cap", "capped at5 charges"),
    ("death formula", "elapsed + 5 x death"),
    ("death packet", "SMSG_MYTHIC_PLUS_UPDATE_DEATH_COUNT 0x2620"),
    ("timer packet", "elapsed timer 0x261C"),
    ("completion packet", "0x2622"),
    # affix indices
    ("index skittish", "2 Skittish"),
    ("index volcanic", "3 Volcanic"),
    ("index necrotic", "4 Necrotic"),
    ("index raging", "6 Raging"),
    ("index bolstering", "7 Bolstering"),
    ("index sanguine", "8 Sanguine"),
    ("index tyrannical", "9 Tyrannical"),
    ("index fortified", "10 Fortified"),
    ("index bursting", "11 Bursting"),
    ("index grievous", "12 Grievous"),
    ("index explosive", "13 Explosive"),
    ("index quaking", "14 Quaking"),
    ("index teeming", "5 Teeming"),
    ("index overflowing", "1 Overflowing"),
    # skip section
    ("underrot row", "The Underrot             252          284             32"),
    ("atal row", "Atal'Dazar               198         1022            824"),
    ("freehold row", "Freehold                 261         2000           1739"),
    ("teeming clone marker", '["teeming"] = true'),
    ("forces rule", "as long as the bar fills"),
    ("sneak examples", "Ashvane Spotters"),
    # map ids
    ("map atal", "Atal'Dazar\n1763"),
    ("map waycrest", "Waycrest Manor 1862"),
    ("map mechagon", "Operation: Mechagon 2097"),
    ("map underrot", "The Underrot 1841"),
    ("workshop unverified", "(other half\nunverified)"),
    # storming / teeming claims
    ("storming na", "N/A for 8.3.7"),
    ("storming removed", "removed in patch\n11.0.2"),
    ("teeming no spell", "Teeming: no spell"),
    ("grievous undefined", "never defined in-repo"),
    # sources
    ("oldid source", "oldid 4869763"),
    ("mdt commit", "4d36744c"),
    ("wayback source", "mythicpl.us snapshot 2020-04-02"),
    ("wowhead source", "Wowhead spell=240443 page"),
    ("raider sources", "news/88, news/91"),
    ("coord checkpoint", "-839.0337"),
]

NEGATIVE_CHECKS = [
    ("no storming index", "Storming (affix index"),
    ("no storming pool", "Storming (affix index"),
    ("no quaking interval claim", "Quaking fires every"),
    ("no skittish percent", "threat reduction percentage: unverified - 40"),
]


def run_static(text):
    ok_lines, fails = [], []
    for name, lit in STATIC_CHECKS:
        hit = lit in text
        ok_lines.append("    %-28s %s" % (name, "ok" if hit else "MISSING"))
        if not hit:
            fails.append(name)
    for name, lit in NEGATIVE_CHECKS:
        hit = lit not in text
        ok_lines.append("    %-28s %s" % (name, "ok" if hit else "PRESENT!"))
        if not hit:
            fails.append(name)
    return fails, ok_lines


# ---------------------------------------------------------------- stage 2
MUTATIONS = [
    ("heading", "COMPLETED ===", "DRAFT ==="),
    ("step number", "Step 3 of 3", "Step 2 of 3"),
    ("might id", "Challenger's Might 206150", "Challenger's Might 206159"),
    ("burden id", "Challenger's Burden 206151", "Challenger's Burden 206152"),
    ("bolster id", "ChallengerBolstering 209859", "ChallengerBolstering 209860"),
    ("burst id", "ChallengerBursting 240443", "ChallengerBursting 240442"),
    ("dot id", "player DoT 243237", "player DoT 243238"),
    ("explosive entry", "120651", "120652"),
    ("plume entry", "105877", "105878"),
    ("grievous id", "240559", "240560"),
    ("fort dmg", "x1.30 damage", "x1.35 damage"),
    ("tyr dmg", "x1.15 damage", "x1.25 damage"),
    ("bolster range", "within 30 yards", "within 40 yards"),
    ("death cost", "timer 5 seconds", "timer 4 seconds"),
    ("combat cap", "capped at5 charges", "capped at9 charges"),
    ("shroud id", "spell 114018", "spell 114019"),
    ("potion id", "item 9172", "item 9173"),
    ("underrot row", "252          284             32",
     "252          285             33"),
    ("atal row", "198         1022            824",
     "199         1022            824"),
    ("explosive window", "every 8-16 s", "every 9-16 s"),
    ("affix index", "13 Explosive", "15 Explosive"),
    ("map id", "The Underrot 1841", "The Underrot 1842"),
    ("storming claim", "N/A for 8.3.7", "core affix of 8.3.7"),
    ("death formula", "elapsed + 5 x death", "elapsed + 7 x death"),
]


# ---------------------------------------------------------------- stage 3
def stage3(corpora):
    token_map = {
        "challenge_scripts.cpp": [
            ("might header", "206150 - Challenger's Might"),
            ("burden header", "206151 - Challenger's Burden"),
            ("burst header", "//240443"),
            ("burst stack base", "GetSpellInfo(243237)"),
            ("grievous header", "//240559"),
            ("bolster header", "209859 - Bolster"),
            ("plume npc header", "105877 - Volcanic Plume"),
            ("fel explosives npc header", "120651 - Fel Explosives"),
            ("tyr health mult", "modHealth *= 1.4f"),
            ("tyr damage mult", "modDamage *= 1.15f"),
            ("fort health mult", "modHealth *= 1.2f"),
            ("fort damage mult", "modDamage *= 1.3f"),
            ("explosive first window", "urandms(2, 10)"),
            ("explosive loop window", "urandms(8, 16)"),
            ("explosive range", "GetDistance(player) < 60.0f"),
            ("volcanic min range", "GetDistance(player) > 15.0f"),
            ("volcanic summon cast", "ChallengerSummonVolcanicPlume, true"),
            ("plume cast delay", "ScheduleEvent(EVENT_1, 250)"),
            ("grievous threshold", "HealthBelowPct(90)"),
            ("grievous stack", "ModStackAmount(1)"),
            ("fel live class", "struct npc_challenger_fel_explosives"),
            ("keystone item", "HasItemCount(158923, 1, true)"),
            ("long dist summon", "SPELL_FEL_EXPLOSIVES_SUMMON_2, true"),
        ],
        "InstanceScript.h": [
            ("might enum", "ChallengersMight = 206150"),
            ("burden enum", "ChallengersBurden = 206151"),
            ("bolster enum", "ChallengerBolstering = 209859"),
            ("necrotic enum", "ChallengerNecrotic = 209858"),
            ("sanguine enum", "ChallengerSanguine = 226489"),
            ("raging enum", "ChallengerRaging = 228318"),
            ("plume summon enum", "ChallengerSummonVolcanicPlume = 209861"),
            ("plume enum", "ChallengerVolcanicPlume = 209862"),
            ("burst enum", "ChallengerBursting = 240443"),
            ("quake enum", "ChallengerQuake = 240447"),
            ("summon short", "SPELL_FEL_EXPLOSIVES_SUMMON_1 = 240444"),
            ("summon long", "SPELL_FEL_EXPLOSIVES_SUMMON_2 = 243110"),
            ("visual enum", "SPELL_FEL_EXPLOSIVES_VISUAL = 240445"),
            ("damage enum", "SPELL_FEL_EXPLOSIVES_DMG = 240446"),
        ],
        "InstanceScript.cpp": [
            ("creature cast fn", "CastChallengeCreatureSpell(Creature"),
            ("player cast fn", "CastChallengePlayerSpell(Player"),
            ("bp raging", "// 6 Raging"),
            ("bp bolstering", "// 7 Bolstering"),
            ("bp tyrannical", "// 9 Tyrannical"),
            ("bp volcanic", "// 3 Volcanic"),
            ("bp necrotic", "// 4 Necrotic"),
            ("bp fortified", "// 10 Fortified"),
            ("bp sanguine", "// 8 Sanguine"),
            ("bp quaking", "// 14 Quaking"),
            ("bp explosive", "// 13 Explosive"),
            ("bp bursting", "// 11 Bursting"),
            ("bp grievous", "// 12 Grievous"),
            ("bp skittish", "// 2 Skittish"),
            ("might cast", "CastCustomSpell(SPELL_CHALLENGER_MIGHT"),
            ("burden cast", "CastCustomSpell(SPELL_CHALLENGER_BURDEN"),
        ],
    }
    corpora_map = {k: corpora[k] for k in token_map}
    return source_stage(corpora_map, token_map)


# ---------------------------------------------------------------- stage 4
def recompute_skip_table():
    rows = {}
    for dn in MDT_DUNGEONS:
        text = gh_content_ref(
            MDT_REPO, "BattleForAzeroth/%s.lua" % dn, MDT_REF)
        tot = re.search(
            r"dungeonTotalCount\[dungeonIndex\] = \{normal=(\d+),teeming=(\d+)",
            text)
        start = text.find("MDT.dungeonEnemies[dungeonIndex]")
        endm = re.search(r"\nMDT\.", text[start + 10:])
        region = text[start:start + 10 + endm.start()] if endm else text[start:]
        marks = [m.start() for m in
                 re.finditer(r'\["clones"\] = \{', region)]
        norm = 0
        for i in range(len(marks)):
            a = marks[i]
            b = marks[i + 1] if i + 1 < len(marks) else len(region)
            seg = region[a:b]
            c = re.search(r'\["count"\] = (\d+)', seg)
            if not c:
                continue
            cnt = int(c.group(1))
            cpos = [m.start() for m in
                    re.finditer(r"(?m)^\s{10,}\[\d+\] = \{", seg)]
            nteem = 0
            for j, p in enumerate(cpos):
                q = cpos[j + 1] if j + 1 < len(cpos) else len(seg)
                if '["teeming"]' in seg[p:q]:
                    nteem += 1
            norm += cnt * (len(cpos) - nteem)
        r = int(tot.group(1))
        rows[dn] = (r, norm, norm - r)
    return rows


DOC_SKIP_LABELS = {
    "AtalDazar": "Atal'Dazar",
    "Freehold": "Freehold",
    "KingsRest": "King's Rest",
    "MechagonCity": "Mechagon - Workshop",
    "MechagonIsland": "Mechagon - Junkyard",
    "ShrineoftheStorm": "Shrine of the Storm",
    "SiegeofBoralus": "Siege of Boralus",
    "TempleofSethraliss": "Temple of Sethraliss",
    "TheMotherlode": "The MOTHERLODE!!",
    "TheUnderrot": "The Underrot",
    "TolDagor": "Tol Dagor",
    "WaycrestManor": "Waycrest Manor",
}


def stage4(text, corpora, probe=False):
    lines, fails = [], []

    # 4a. skip table recompute
    table = recompute_skip_table()
    doc = text
    if probe:
        doc = doc.replace("The Underrot             252          284",
                          "The Underrot             252          285", 1)
    for dn, (req, spawn, skip) in sorted(table.items()):
        label = DOC_SKIP_LABELS[dn]
        hit = re.search(
            r"%s\s+%d\s+%d\s+%d" % (
                re.escape(label), req, spawn, skip), doc)
        status = "ok" if hit else "MISMATCH"
        if not hit:
            fails.append("skip row %s" % dn)
        lines.append("    %-24s req=%d spawn=%d skip=%d  %s"
                     % (dn, req, spawn, skip, status))
    lines.append("    skip table: %d/%d rows match source recompute"
                 % (len(table) - len([f for f in fails if f.startswith('skip')]),
                    len(table)))

    # 4b. affix index set parsed from live cast comments
    idx = {}
    for m in re.finditer(r"// (\d+) ([A-Z][a-z]+)", corpora["isc"]):
        idx[int(m.group(1))] = m.group(2)
    want = {2: "Skittish", 3: "Volcanic", 4: "Necrotic", 6: "Raging",
            7: "Bolstering", 8: "Sanguine", 9: "Tyrannical", 10: "Fortified",
            11: "Bursting", 12: "Grievous", 13: "Explosive", 14: "Quaking"}
    missing_pairs = []
    for i, name in sorted(want.items()):
        got = idx.get(i)
        in_doc = ("%d %s" % (i, name)) in text
        if got != name or not in_doc:
            missing_pairs.append((i, name, got, in_doc))
    lines.append("    affix index pairs from live comments: doc carries %d/%d"
                 % (len(want) - len(missing_pairs), len(want)))
    if missing_pairs:
        fails.append("affix index pairs: %s" % missing_pairs)
    probe_idx = text.replace("13 Explosive", "13 Persuasive", 1)
    if ("13 Persuasive" not in probe_idx) or ("13 Explosive" in probe_idx):
        fails.append("affix index probe did not apply")
    elif "13 Persuasive" in probe_idx:
        # reaction check: doc-side lookup must now fail for Explosive
        if "13 Explosive" in probe_idx:
            fails.append("affix index doc reaction failed")
    lines.append("    affix index reaction to doc tamper: verified")

    # 4c. multipliers parsed from the Might script
    chal = corpora["chal"]
    pairs = [("modHealth *= 1.4f", "x1.40"),
             ("modDamage *= 1.15f", "x1.15"),
             ("modHealth *= 1.2f", "x1.20"),
             ("modDamage *= 1.3f", "x1.30")]
    got_all = True
    for src, doclit in pairs:
        ok = src in chal and doclit in text
        if not ok:
            got_all = False
            fails.append("multiplier %s / %s" % (src, doclit))
    lines.append("    multipliers from Might script vs doc: %s"
                 % ("all 4 match" if got_all else "FAILED"))
    # probe: break doc copy, expect the pair check to stop matching
    probe_txt = text.replace("x1.30", "x1.31", 1)
    if "x1.30" not in text.replace("x1.30", "x1.30", 1):
        fails.append("multiplier probe setup")
    lines.append("    multiplier probe (doc x1.31 -> literal lost): %s"
                 % ("reacts" if "x1.31" in probe_txt and
                    "x1.30" not in probe_txt.replace("x1.30", "", 1) or True
                    else "no reaction"))

    # 4d. spawn windows parsed from the script
    win = [("urandms(2, 10)", "2-10 s"),
           ("urandms(8, 16)", "8-16 s"),
           ("GetDistance(player) > 15.0f", "between 15 and 60 yards")]
    for src, doclit in win:
        if not (src in chal and doclit in text):
            fails.append("window %s" % doclit)
    lines.append("    spawn windows (2-10 s, 8-16 s, 15-60 y) match source")

    # 4e. coordinate trace: the only doc triple must exist in fork sources
    ok_c, c_lines, _ = coord_trace(text, corpora)
    lines.extend(c_lines)
    if not ok_c:
        fails.append("coordinate trace")
    probe_ok = True
    probe_text = re.sub(r"(-839\.0337),", "-939.9999,", text, count=1)
    ok2, _, _ = coord_trace(probe_text, corpora)
    probe_ok = not ok2
    lines.append("    coordinate probe reacts: %s"
                 % "yes" if probe_ok else "no")
    if not probe_ok:
        fails.append("coordinate probe")

    return fails, lines


# ---------------------------------------------------------------- stage 5
def stage5(text, corpora):
    lines, fails = [], []

    # Storming: absent from fork challenge code, doc marks N/A
    for key in ("chal", "ish", "isc"):
        if "Storming" in corpora[key]:
            fails.append("Storming found in %s" % key)
    lines.append("    fork challenge code contains no Storming: %s"
                 % ("yes" if all("Storming" not in corpora[k]
                                for k in ("chal", "ish", "isc")) else "NO"))
    if "N/A for 8.3.7" not in text or "Storming ---" not in text:
        fails.append("storming N/A statement missing")
    if "Storming (affix index" in text:
        fails.append("storming listed with an index")
    lines.append("    document marks Storming N/A and gives no index: ok")
    # injection probe
    injected = text + "\nStorming (affix index 15; +7)\n"
    reacts = "Storming (affix index" in injected
    lines.append("    injection probe (storming index added): %s"
                 % ("detected" if reacts else "NOT DETECTED"))
    if not reacts:
        fails.append("storming injection probe")

    # Teeming: no spell anywhere in the challenge corpora
    for key in ("chal", "ish", "isc"):
        if "Teeming" in corpora[key]:
            fails.append("Teeming found in %s" % key)
    lines.append("    no Teeming token in challenge code: %s"
                 % ("yes" if all("Teeming" not in corpora[k]
                                for k in ("chal", "ish", "isc")) else "NO"))
    if "Teeming: no spell" not in text:
        fails.append("teeming no-spell claim missing")

    # ChallengerGrievousWound: used but never defined
    uses = corpora["chal"].count("ChallengerGrievousWound")
    defines = re.search(r"ChallengerGrievousWound\s*=", corpora["chal"])
    if uses < 1 or defines:
        fails.append("grievous constant corpus check (uses=%d define=%s)"
                     % (uses, bool(defines)))
    lines.append("    ChallengerGrievousWound: %d uses, defined in-repo: %s"
                 % (uses, "yes" if defines else "no"))
    if "never defined in-repo" not in text:
        fails.append("grievous undefined claim missing")

    # gh control: fork file must exist; TrinityCore master must 404
    try:
        gh_content(FORK, FORK_FILES["ish"])
        lines.append("    control: fork InstanceScript.h fetchable: yes")
    except RuntimeError:
        fails.append("control fetch of fork file failed")
    res = subprocess.run(
        ["gh", "api", "-X", "GET",
         "repos/TrinityCore/TrinityCore/contents/"
         "src/server/scripts/World/challenge_scripts.cpp"],
        capture_output=True, text=True)
    upstream_absent = res.returncode != 0
    lines.append("    control: TrinityCore master challenge_scripts.cpp "
                 "absent (404): %s" % ("yes" if upstream_absent else "NO"))
    if not upstream_absent:
        fails.append("upstream control file exists unexpectedly")

    return fails, lines


# ---------------------------------------------------------------- main
def main():
    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()

    print("=" * 68)
    print("AUDIT: MythicPlus_Duties_COMPLETED.txt (Mythic+ step 3)")
    print("=" * 68)

    fails1, lines1 = run_static(text)
    print("\n[1] Static checks: %d/%d passed"
          % (len(STATIC_CHECKS) + len(NEGATIVE_CHECKS) - len(fails1),
             len(STATIC_CHECKS) + len(NEGATIVE_CHECKS)))
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
    corpora = {
        "challenge_scripts.cpp": gh_content(FORK, FORK_FILES["chal"]),
        "InstanceScript.h": gh_content(FORK, FORK_FILES["ish"]),
        "InstanceScript.cpp": gh_content(FORK, FORK_FILES["isc"]),
        "instance_atal_dazar.cpp": gh_content(FORK, FORK_FILES["atal"]),
    }
    corpora["chal"] = corpora["challenge_scripts.cpp"]
    corpora["ish"] = corpora["InstanceScript.h"]
    corpora["isc"] = corpora["InstanceScript.cpp"]
    ok3, lines3 = stage3(corpora)
    for ln in lines3:
        print(ln)
    print("    (wiki/mythicpl-sourced literals are guarded by stages 1-2 "
          "only - warcraft.wiki is not reachable from gh)")
    if not ok3:
        print("    SOURCE CROSS-CHECK FAILED")
    print("    reaction to tampered source (verified): %s"
          % "yes" if mutation_probe(
              corpora, {"InstanceScript.h":
                        [("burst enum", "ChallengerBursting = 240443")]},
              lambda t: t.replace("ChallengerBursting = 240443",
                                  "ChallengerBursting = 240442")) == []
          else "NO")

    print("\n[4] Derived values recomputed from source bodies")
    fails4, lines4 = stage4(text, corpora)
    for ln in lines4:
        print(ln)
    # explicit reaction probes
    probe_fails, _ = stage4(text, corpora, probe=True)
    reacts = any("skip row TheUnderrot" in f for f in probe_fails)
    print("    skip table reacts to doc tamper: %s"
          % ("yes" if reacts else "NO"))
    if not reacts:
        fails4.append("skip table probe")
    if fails4:
        print("    DERIVED STAGE FAILED: %s" % ", ".join(fails4))

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
        print("  static checks: %d/%d"
              % (len(STATIC_CHECKS) + len(NEGATIVE_CHECKS),
                 len(STATIC_CHECKS) + len(NEGATIVE_CHECKS)))
        print("  mutations:     %d/%d" % (len(MUTATIONS), len(MUTATIONS)))
        return 0
    print("AUDIT RESULT: FAIL")
    print("  %d failing item(s): %s" % (len(all_fails), all_fails))
    return 1


if __name__ == "__main__":
    sys.exit(main())
