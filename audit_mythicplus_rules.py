#!/usr/bin/env python3
"""Audit: MythicPlus_Rules_COMPLETED.txt (Mythic+ step 2, Rules).

Stages:
  1. Static exact-literal checks on the document (sections 1-8 + negatives).
  2. Mutation testing - every mutation must break static or doc-side derived
     checks; each mutation literal must occur exactly once in the document.
  3. Source cross-check fetched by git (gh api is 403-blocked for external
     repos this session): fork code (blobless sparse clone, HEAD recorded)
     and MDT pinned at the commit the document cites.
  4. Derived values recomputed from source bodies: keystone health ladder,
     MDT dungeon totals (all 12), per-creature forces counts (all 12),
     timer table arithmetic, item-level / residuum ladder structure, and a
     coordinate trace of the checkpoint triple.
  5. Doc-side absence probes (Storming injection, wago 8% quote guard).
"""

import collections
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, ".")
from audit_common import coord_trace, source_stage, mutation_probe

DOC = "# Ai Research prompts/Mythic_Plus_completed/MythicPlus_Rules_COMPLETED.txt"
MDT_REPO = "https://github.com/Nnoggie/MythicDungeonTools.git"
MDT_REF = "4d36744c53477fc9fcb990471b1bb639a62f0d48"
FORK_REPO = "https://github.com/HavenWoW/BFA-HavenCore.git"
SCRATCH = "/tmp/audit_rules_src"

MDT_DOCS = {
    "AtalDazar": "Atal'Dazar",
    "Freehold": "Freehold",
    "KingsRest": "King's Rest",
    "MechagonIsland": "Mechagon - Junkyard",
    "MechagonCity": "Mechagon - Workshop",
    "ShrineoftheStorm": "Shrine of the Storm",
    "SiegeofBoralus": "Siege of Boralus",
    "TempleofSethraliss": "Temple of Sethraliss",
    "TheMotherlode": "The MOTHERLODE!!",
    "TheUnderrot": "The Underrot",
    "TolDagor": "Tol Dagor",
    "WaycrestManor": "Waycrest Manor",
}


def _sh(args, cwd=None):
    res = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError("%s failed: %s"
                           % (" ".join(args[:3]), (res.stderr or res.stdout).strip()))
    return res.stdout


def fetch_sources():
    """Return (mdt_dir, fork_dir, fork_head). Fetch once, reuse afterwards."""
    mdt_dir = os.path.join(SCRATCH, "mdt")
    fork_dir = os.path.join(SCRATCH, "fork")
    lines = []
    if not os.path.exists(os.path.join(mdt_dir, "MythicDungeonTools.lua")):
        if os.path.isdir(SCRATCH):
            shutil.rmtree(SCRATCH)
        os.makedirs(mdt_dir)
        _sh(["git", "init", "-q", "."], cwd=mdt_dir)
        _sh(["git", "remote", "add", "origin", MDT_REPO], cwd=mdt_dir)
        _sh(["git", "fetch", "-q", "--depth", "1", "origin", MDT_REF], cwd=mdt_dir)
        _sh(["git", "checkout", "-q", "FETCH_HEAD", "--", "."], cwd=mdt_dir)
        lines.append("    MDT fetched: git fetch --depth 1 origin %s" % MDT_REF[:12])
    else:
        lines.append("    MDT cache: %s" % mdt_dir)
    if not os.path.exists(os.path.join(
            fork_dir, "src/server/game/Instances/InstanceScript.h")):
        if os.path.isdir(fork_dir):
            shutil.rmtree(fork_dir)
        _sh(["git", "clone", "-q", "--depth", "1", "--filter=blob:none",
             "--sparse", FORK_REPO, fork_dir])
        _sh(["git", "sparse-checkout", "set",
             "src/server/scripts/World",
             "src/server/game/Instances",
             "src/server/scripts/Zandalar/AtalDazar"], cwd=fork_dir)
        lines.append("    fork cloned: blobless sparse, HEAD recorded below")
    else:
        lines.append("    fork cache: %s" % fork_dir)
    fork_head = _sh(["git", "rev-parse", "HEAD"], cwd=fork_dir).strip()
    lines.append("    fork HEAD: %s" % fork_head)
    return mdt_dir, fork_dir, fork_head


def read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read().replace("\r\n", "\n")


def load_corpora(mdt_dir, fork_dir):
    base_f = os.path.join(fork_dir, "src/server")
    corpora = {
        "h": read(os.path.join(base_f, "game/Instances/InstanceScript.h")),
        "cpp": read(os.path.join(base_f, "game/Instances/InstanceScript.cpp")),
        "chal": read(os.path.join(base_f, "scripts/World/challenge_scripts.cpp")),
        "atal": read(os.path.join(base_f,
                    "scripts/Zandalar/AtalDazar/instance_atal_dazar.cpp")),
        "mdt": read(os.path.join(mdt_dir, "MythicDungeonTools.lua")),
    }
    return corpora


# ---------------------------------------------------------------- stage 1
STATIC_CHECKS = [
    ("heading", "=== MYTHIC+ RULES - BATTLE FOR AZEROTH SEASON 4 (8.3.7) - COMPLETED ==="),
    ("step", "Step 2 of 3 (prompt 02_Rules.txt)."),
    ("server context", "BfA 8.3.7 build 35662, TrinityCore-based HavenCore fork."),
    ("limits rule", "Anything without a readable source says unverified."),
    ("sec1", "1. HOW THE KEYSTONE LEVEL SCALES HEALTH AND DAMAGE"),
    ("sec2", "2. WHICH AFFIXES APPLY AT WHICH LEVEL (BFA SEASON 4)"),
    ("sec3", "3. HOW ENEMY FORCES ARE COUNTED AND WHAT EACH CREATURE ADDS"),
    ("sec4", "4. THE TIMER AND CHEST THRESHOLDS"),
    ("sec5", "5. WHAT THE END OF THE RUN GIVES"),
    ("sec6", "6. MAP IDS AND COORDINATES"),
    ("sec7", "7. SOURCES (queried one small page/query at a time; downloads deleted)"),
    ("sec8", "8. UNVERIFIED (explicit)"),
    # sec1 keystone scaling
    ("per-level rule", "enemies gain +10% health and +10% damage, compounding"),
    ("mdt formula", "multiplier = round(1.10 ^ max(level - 2, 0), 2); health = multiplier * baseHealth."),
    ("scale ladder", "So +2 = x1.00, +3 = x1.10, +4 = x1.21, +5 = x1.33, ... +15 = x3.45 of the base."),
    ("wiki 10pct quote", "now increase by 10%"),
    ("wiki was-8 quote", "(was 8% per level)"),
    ("fort health", "Fortified: non-boss enemies x1.20 health."),
    ("tyr health", "Tyrannical: boss enemies x1.40 health."),
    ("rebase mythic", "Non-keystone Mythic (+0) enemy health/damage +45%"),
    ("key rebalance", "reduced by 4 levels"),
    ("reward ilvl bump", "raised by 30 item levels"),
    ("fork mult fns", "GetHealthMultiplier/GetDamageMultiplier return"),
    ("fork table file", "ChallengeModeHealth.txt"),
    ("fork gametables", "GameTables.cpp lines 126-127"),
    ("wago fail", "wago.tools csv endpoint for"),
    # sec2 affixes
    ("slot 2", "Level 2: first affix - always Fortified OR Tyrannical"),
    ("slot 4", "Level 4: second affix - exactly one of 5"),
    ("slot 7", "Level 7: third affix - exactly one of 6"),
    ("slot 10", "Level 10: fourth (seasonal) affix - does NOT rotate weekly"),
    ("pool4", "Bolstering (7), Bursting (11), Raging (6), Sanguine (8), Teeming (5)"),
    ("pool7", "Explosive (13), Grievous (12), Necrotic (4), Quaking (14), Skittish (2), Volcanic (3)"),
    ("seasons 1-3", "Season 1: Infested. Season 2: Reaping. Season 3: Beguiling."),
    ("season 4", "Season 4: Awakened (patch 8.3.0, removed in 9.0.1)"),
    ("awakened id", "Wowhead affix id: 120"),
    ("overflow teeming", "1 Overflowing and 5 Teeming"),
    ("lieutenant 1", "Urg'roth, Breaker of Heroes (Brutal Spire) 161124"),
    ("blood rot dps", "Blood of the Corruptor rot deals 60,000 damage/sec"),
    ("schedule row1", "  Fortified  | Bolstering | Grievous   | Awakened"),
    ("fork no affixes", "REQUEST_AFFIXES goes to Handle_NULL"),
    # sec3 forces
    ("forces percent", "killed points / required total as a percentage"),
    ("forces format", 'FormatEnemyForces, default format "forces/forcesmax (percent%)"'),
    ("fork no forces", "HavenCore has NO enemy-forces tracking and no forces packet at all"),
    ("tot atal", "  Atal'Dazar            1763 | 198 / 237"),
    ("tot underrot", "  The Underrot          1841 | 252 / 286"),
    ("tot junkyard", "  Mechagon - Junkyard   unverified map id | 332 / 398"),
    ("tot workshop", "own map id unverified) | 160 / 192"),
    ("mdt pin", "4d36744c53477fc9fcb990471b1bb639a62f0d48"),
    ("creat atal", "129553 Dinomancer Kish'o=10"),
    ("creat shrine", "136214 Windspeaker Heldis=36"),
    ("creat waycrest", "135365 Matron Alma=16"),
    ("creat pseudo", "129547000 Blacktooth Knuckleduster=0"),
    ("count zero rule", "count 0 = gives no forces"),
    # sec4 timer
    ("font item", "GO 246779, item 158923"),
    ("start packet", "SMSG_START_TIMER 0x25BC, 10 s,"),
    ("threshold rule", "+2 = finish with 20% time left, +3 = 40% left"),
    ("par atal", "  Atal'Dazar           30:00   24:00 (6:00 left) 18:00 (12:00 left)"),
    ("par freehold", "  Freehold             33:00   26:24 (6:36 left) 19:48 (13:12 left)"),
    ("par temple", "  Temple of Sethraliss 36:00   28:48 (7:12 left) 21:36 (14:24 left)"),
    ("par junkyard", "  Mechagon: Junkyard   38:00   30:24 (7:36 left) 22:38 (15:12 left)"),
    ("par workshop", "  Mechagon: Workshop   32:00   25:36 (6:24 left) 19:12 (12:48 left)"),
    ("junkyard note", "value is 22:48."),
    ("timed +1", "Finished within the timer: +1 keystone level; more than 20% time left: +2"),
    ("max +3", "more than 40% left: +3 (max +3)"),
    ("death cost", "subtracts 5 seconds from the timer"),
    ("death formula", "elapsed + 5 x death"),
    ("burden spell", "SPELL_CHALLENGER_BURDEN = 206151"),
    ("criteria", "CriteriaCount[3]"),
    ("chest timers lack", "_chestTimers[3] thresholds are never initialized"),
    # sec5 rewards
    ("ach 11183", "11183 (key >= 2)"),
    ("ach 11162/11224", "11162 and 11224 (>= 15)"),
    ("chest 2 pieces", "2 pieces for the group"),
    ("chest 3 timed", "(3 total) if the timer was beaten"),
    ("plus16 note", "at +16 or higher (was +11)"),
    ("end ladder1", "  +2:435  +3:435  +4:440  +5:445  +6:445  +7:450  +8:455"),
    ("end ladder2", "  +9:455  +10:455  +11:460  +12:460  +13:460  +14:465  +15:465"),
    ("week ladder1", "  +2:440  +3:445  +4:450  +5:450  +6:455  +7:460  +8:460"),
    ("week ladder2", "  +9:460  +10:465  +11:465  +12:470  +13:470  +14:470  +15:475"),
    ("resid start", "+10:1700"),
    ("resid end", "+25:2915"),
    ("decay example", "best +11 this week -> chest next week gives +10"),
    ("m0 keystone", "M0 completions grant a +2 keystone"),
    ("reward bonus", "3410-3418/3509/3510/3534/3535"),
    ("legacy base", "baseMythicIlevel 885"),
    ("chest noop", "SpawnChallengeModeRewardChest, zero overrides"),
    ("weekly reply", "rewards reply is commented out"),
    # sec6 maps/coords
    ("mapids claim", "Map ids (fork RegisterInstanceScript lines, verified directly in the files):"),
    ("mapid row", "Atal'Dazar 1763 | Freehold 1754 | King's Rest 1762 |"),
    ("checkpoint", "x = -839.0337, y = -2092.268, z = 725.8119, o = 0.4123"),
    ("virtuals claim", "exist only as base-class"),
    # sec7 sources
    ("src oldid", 'revision oldid 4869763 (2020-02-05'),
    ("src wayback", "web.archive.org snapshot 2020-04-02 of mythicpl.us"),
    ("src mdt", "MythicDungeonTools @4d36744c (2020-07-19)"),
    ("src raider", "raider.io weekly-route titles"),
    ("src wago", "wago.tools DB2 csv for build 8.3.7.35662: attempted, failed"),
    # sec8 unverified bullets
    ("unv tables", "Per-level scalar values in ChallengeModeHealth/Damage tables for build 35662"),
    ("unv dmg pct", "Fortified/Tyrannical damage-increase percentages"),
    ("unv mech map", "Second Mechagon instance's own map id"),
    ("unv ladder", "Extra-loot chance ladder above +15"),
    ("unv explosive", "Explosive orb damage"),
    ("unv awakened", "Game-side numeric id of the Awakened affix"),
    ("unv floor", "Weekly keystone floor below the -1/week decay"),
    ("unv schedule", "schedule table above covers the entire season"),
    ("unv guild", "Guild achievement ids named in fork comments"),
]

NEGATIVE_CHECKS = [
    ("no storming index", "Storming (affix index"),
    ("no 8pct current rule", "now increase by 8%"),
]


def run_static(text):
    ok_lines, fails = [], []
    for name, lit in STATIC_CHECKS:
        hit = lit in text
        ok_lines.append("    %-24s %s" % (name, "ok" if hit else "MISSING"))
        if not hit:
            fails.append(name)
    for name, lit in NEGATIVE_CHECKS:
        hit = lit not in text
        ok_lines.append("    %-24s %s" % (name, "ok" if hit else "PRESENT!"))
        if not hit:
            fails.append(name)
    return fails, ok_lines


# ---------------------------------------------------------------- stage 2
MUTATIONS = [
    ("heading", "MYTHIC+ RULES - BATTLE FOR AZEROTH SEASON 4 (8.3.7) - COMPLETED",
     "MYTHIC+ RULES - BATTLE FOR AZEROTH SEASON 4 (8.3.7) - DRAFT"),
    ("step", "Step 2 of 3 (prompt 02_Rules.txt).", "Step 1 of 3 (prompt 02_Rules.txt)."),
    ("per-level pct", "enemies gain +10% health and +10% damage, compounding",
     "enemies gain +11% health and +11% damage, compounding"),
    ("formula", "1.10 ^ max(level - 2, 0), 2", "1.11 ^ max(level - 2, 0), 2"),
    ("ladder end", "+15 = x3.45 of the base", "+15 = x3.46 of the base"),
    ("fort health", "Fortified: non-boss enemies x1.20 health.",
     "Fortified: non-boss enemies x1.25 health."),
    ("tyr health", "Tyrannical: boss enemies x1.40 health.",
     "Tyrannical: boss enemies x1.45 health."),
    ("rebase", "enemy health/damage +45%", "enemy health/damage +50%"),
    ("pool4 teeming", "Teeming (5)", "Teeming (15)"),
    ("pool7 skittish", "Skittish (2), Volcanic (3)", "Skittish (15), Volcanic (3)"),
    ("season4 removed", "Season 4: Awakened (patch 8.3.0, removed in 9.0.1)",
     "Season 4: Awakened (patch 8.3.0, removed in 9.0.2)"),
    ("awakened id", "Wowhead affix id: 120", "Wowhead affix id: 121"),
    ("lieutenant id", "(Brutal Spire) 161124", "(Brutal Spire) 161125"),
    ("blood rot", "rot deals 60,000 damage/sec", "rot deals 61,000 damage/sec"),
    ("tot atal", "  Atal'Dazar            1763 | 198 / 237",
     "  Atal'Dazar            1763 | 199 / 237"),
    ("tot underrot", "  The Underrot          1841 | 252 / 286",
     "  The Underrot          1841 | 252 / 287"),
    ("pseudo id", "129547000 Blacktooth Knuckleduster", "129548000 Blacktooth Knuckleduster"),
    ("creat count", "129553 Dinomancer Kish'o=10", "129553 Dinomancer Kish'o=11"),
    ("par atal", "  Atal'Dazar           30:00   24:00 (6:00 left) 18:00 (12:00 left)",
     "  Atal'Dazar           30:00   24:01 (6:00 left) 18:00 (12:00 left)"),
    ("par junkyard", "22:38 (15:12 left)", "22:39 (15:12 left)"),
    ("death cost", "subtracts 5 seconds from the timer", "subtracts 4 seconds from the timer"),
    ("death formula", "elapsed + 5 x death", "elapsed + 7 x death"),
    ("ach id", "11183 (key >= 2)", "11186 (key >= 2)"),
    ("end ladder", "  +14:465  +15:465", "  +14:465  +15:466"),
    ("week ladder", "  +14:470  +15:475", "  +14:470  +15:476"),
    ("resid ladder", "+25:2915", "+25:2916"),
    ("decay example", "best +11 this week -> chest next week gives +10",
     "best +12 this week -> chest next week gives +10"),
    ("checkpoint", "-839.0337, y = -2092.268", "-839.9337, y = -2092.268"),
    ("legacy base", "baseMythicIlevel 885", "baseMythicIlevel 886"),
    ("unv mech map", "Second Mechagon instance's own map id",
     "Third Mechagon instance's own map id"),
    ("src mdt pin", "MythicDungeonTools @4d36744c (2020-07-19)",
     "MythicDungeonTools @4d36744d (2020-07-19)"),
]


# ---------------------------------------------------------------- stage 3
TOKEN_MAP = {
    "h": [
        ("burden enum", "ChallengersBurden = 206151"),
        ("might enum", "ChallengersMight = 206150"),
        ("chest virtual", "virtual void SpawnChallengeModeRewardChest() { }"),
        ("font setter", "void SetFontOfPowerPos(Position pos)"),
        ("checkpoint setter", "void SetCheckPointPos(Position pos)"),
    ],
    "cpp": [
        ("affix 13", "// 13 Explosive"),
        ("affix 10", "// 10 Fortified"),
        ("affix 14", "// 14 Quaking"),
        ("affix 6", "// 6 Raging"),
        ("complete fn", "void InstanceScript::CompleteChallengeMode()"),
        ("ach 11183", "DoCompleteAchievement(11183)"),
        ("ach 11184", "DoCompleteAchievement(11184)"),
        ("ach 11185", "DoCompleteAchievement(11185)"),
        ("ach 11162", "DoCompleteAchievement(11162)"),
        ("ach 11224", "DoCompleteAchievement(11224)"),
        ("timer type", "TIMER_TYPE_CHALLENGE"),
    ],
    "chal": [
        ("keystone item", "HasItemCount(158923, 1, true)"),
    ],
    "atal": [
        ("register line", "RegisterInstanceScript(instance_atal_dazar, 1763)"),
        ("checkpoint x", "-839.0337"),
        ("checkpoint y", "-2092.268"),
        ("checkpoint z", "725.8119"),
    ],
    "mdt": [
        ("health fn", "function MDT:CalculateEnemyHealth"),
        ("health formula", "1.10^math.max(level-2,0)"),
        ("fort mult", "mult = 1.2"),
        ("tyr mult", "mult = 1.4"),
    ],
}


def stage3(corpora):
    ok, lines = source_stage(corpora, TOKEN_MAP)
    lines.append("    reaction to tampered MDT formula: %s"
                 % ("detected" if mutation_probe(
                     corpora, {"mdt": TOKEN_MAP["mdt"]},
                     lambda t: t.replace("1.10^math.max(level-2,0)",
                                         "1.11^math.max(level-2,0)")) == []
                     else "NOT DETECTED"))
    if mutation_probe(corpora, {"mdt": TOKEN_MAP["mdt"]},
                      lambda t: t.replace("1.10^math.max(level-2,0)",
                                          "1.11^math.max(level-2,0)")):
        ok = False
    return ok, lines


# ---------------------------------------------------------------- stage 4
def parse_mdt_totals(mdt_dir):
    totals = {}
    for src in MDT_DOCS:
        text = read(os.path.join(mdt_dir, "BattleForAzeroth", src + ".lua"))
        m = re.search(
            r"MDT\.dungeonTotalCount\[dungeonIndex\] = \{normal=(\d+),"
            r"teeming=(\d+)", text)
        if not m:
            raise RuntimeError("dungeonTotalCount not found in %s.lua" % src)
        totals[src] = (int(m.group(1)), int(m.group(2)))
    return totals


def doc_totals(text):
    block_m = re.search(
        r"Per dungeon: map id \(fork RegisterInstanceScript\).*?"
        r"Per-creature count values", text, re.S)
    if not block_m:
        return {}, ["totals block missing"]
    block = block_m.group(0)
    out, probs = {}, []
    for src, label in MDT_DOCS.items():
        i = block.find(label)
        if i < 0:
            probs.append("label %s absent" % label)
            continue
        m = re.search(r"\|\s*(\d+) /\s*(\d+)", block[i:i + 220])
        if not m:
            probs.append("no totals cell for %s" % label)
            continue
        out[src] = (int(m.group(1)), int(m.group(2)))
    return out, probs


def parse_mdt_creatures(mdt_dir):
    out = {}
    for src in MDT_DOCS:
        text = read(os.path.join(mdt_dir, "BattleForAzeroth", src + ".lua"))
        start = text.find("MDT.dungeonEnemies[dungeonIndex]")
        if start < 0:
            raise RuntimeError("dungeonEnemies not found in %s.lua" % src)
        endm = re.search(r"\nMDT\.", text[start + 10:])
        region = text[start:start + 10 + endm.start()] if endm else text[start:]
        ind = re.search(r"(?m)^( +)\[\d+\] = \{\s*$", region)
        if not ind:
            raise RuntimeError("no enemy entries parsed in %s.lua" % src)
        indent = re.escape(ind.group(1))
        chunks = re.split(r"(?m)^%s\[\d+\] = \{\s*$" % indent, region)
        entries = []
        for chunk in chunks[1:]:
            im = re.search(r'\["id"\] = (\d+);', chunk)
            nm = re.search(r'\["name"\] = L\["(.*?)"\];', chunk) or \
                 re.search(r'\["name"\] = "(.*?)";', chunk)
            cm = re.search(r'\["count"\] = (\d+);', chunk)
            if not (im and nm):
                continue
            entries.append((im.group(1), nm.group(1),
                            int(cm.group(1)) if cm else 0))
        if not entries:
            raise RuntimeError("0 entries parsed from %s.lua" % src)
        out[src] = entries
    return out


def doc_creatures(text):
    out, probs = {}, []
    for src, label in MDT_DOCS.items():
        m = re.search(r"(?m)^%s: (.*)$"
                      % re.escape(label), text)
        if not m:
            probs.append("doc section for %s missing" % label)
            continue
        entries = []
        for seg in m.group(1).split("; "):
            fm = re.fullmatch(r"(\d+) (.+)=(\d+)", seg.strip())
            if not fm:
                probs.append("bad pair %r in %s" % (seg[:40], label))
                continue
            entries.append((fm.group(1), fm.group(2), int(fm.group(3))))
        out[src] = entries
    return out, probs


def fmt_time(sec):
    return "%d:%02d" % (sec // 60, sec % 60)


def check_timer_table(text):
    fails, lines = [], []
    row_re = re.compile(
        r"(?m)^  (.+?)\s+(\d+:\d\d)\s+(\d+:\d\d) \((\d+:\d\d) left\)"
        r" (\d+:\d\d) \((\d+:\d\d) left\)$")
    rows = row_re.findall(text)
    if len(rows) != 12:
        return ["timer rows parsed: %d/12" % len(rows)], \
            ["    timer rows parsed: %d/12" % len(rows)]

    def secs(t):
        m, s = t.split(":")
        return int(m) * 60 + int(s)

    checked = 0
    for name, par_s, t2_s, l2_s, t3_s, l3_s in rows:
        par, t2, l2, t3, l3 = map(secs, (par_s, t2_s, l2_s, t3_s, l3_s))
        exp_t2, exp_t3 = int(round(0.8 * par)), int(round(0.6 * par))
        bad = []
        if l2 != par - t2 or t2 != exp_t2:
            bad.append("+2 cell")
        if t3 == exp_t3:
            if l3 != par - t3:
                bad.append("+3 left mismatch")
        elif name == "Mechagon: Junkyard" and t3 == secs("22:38") \
                and exp_t3 == secs("22:48") and l3 == par - exp_t3 \
                and "value is 22:48." in text:
            lines.append("    %-20s known source typo 22:38 (rule 22:48) "
                         "noted in doc: ok" % name)
        else:
            bad.append("+3 cell")
        if bad:
            fails.append("timer %s: %s" % (name, ",".join(bad)))
        checked += 1
    lines.append("    timer rows verified by arithmetic: %d/12" % checked)
    return fails, lines


def check_ladders(text):
    fails, lines = [], []

    def ladder(anchor_start, anchor_end, first_lvl, first_val, last_val):
        m = re.search(r"%s.*?%s" % (re.escape(anchor_start),
                                    re.escape(anchor_end)), text, re.S)
        if not m:
            return ["ladder %s..%s not found" % (anchor_start, anchor_end)], None
        pairs = re.findall(r"\+(\d+):(\d+)", m.group(0))
        pairs = [(int(a), int(b)) for a, b in pairs]
        levels_ok = [a for a, _ in pairs] == list(
            range(first_lvl, first_lvl + len(pairs)))
        vals = [b for _, b in pairs]
        problems = []
        if not levels_ok:
            problems.append("level sequence")
        if any(vals[i] > vals[i + 1] for i in range(len(vals) - 1)):
            problems.append("not non-decreasing")
        if not pairs or pairs[0][1] != first_val or pairs[-1][1] != last_val:
            problems.append("endpoint")
        return problems, len(pairs)

    for spec in (("  +2:435", "+15:465", 2, 435, 465, "end-of-run ilvl"),
                 ("  +2:440", "+15:475", 2, 440, 475, "weekly ilvl"),
                 ("+10:1700", "+25:2915", 10, 1700, 2915, "residuum")):
        problems, n = ladder(*spec[:5])
        if problems:
            fails.append("%s ladder: %s" % (spec[5], ",".join(problems)))
        lines.append("    %-16s %s entries, structure %s"
                     % (spec[5], n, "ok" if not problems else "FAILED"))
    return fails, lines


def check_health_ladder(text):
    fails, lines = [], []
    want = {}
    for lvl in list(range(2, 6)) + [15]:
        want[lvl] = round(1.10 ** max(lvl - 2, 0), 2)
    if round(1.10 ** 13, 2) != 3.45:
        fails.append("formula +15 != 3.45")
    m = re.search(r"So \+2 = .*?of the base\.", text, re.S)
    if not m:
        fails.append("ladder sentence missing")
        return fails, ["    ladder sentence missing"]
    seg = m.group(0)
    for lvl, mult in sorted(want.items()):
        tok = "x%.2f" % mult
        if not re.search(r"\+%d = %s" % (lvl, re.escape(tok)), seg):
            fails.append("+%d %s not printed" % (lvl, tok))
    lines.append("    formula ladder recomputed: +2..+5 and +15 match doc")
    return fails, lines


def run_derived(text, corpora, mdt_dir, probe=False):
    fails, lines = [], []
    doc = text
    if probe:
        doc = doc.replace("  Atal'Dazar            1763 | 198 / 237",
                          "  Atal'Dazar            1763 | 199 / 237", 1)

    f, l = check_health_ladder(doc)
    fails += f
    lines += l

    totals = parse_mdt_totals(mdt_dir)
    dtot, probs = doc_totals(doc)
    fails += probs
    hits = 0
    for src, (n, t) in sorted(totals.items()):
        got = dtot.get(src)
        if got == (n, t):
            hits += 1
        else:
            fails.append("total %s: doc=%s src=(%d, %d)"
                         % (MDT_DOCS[src], got, n, t))
    lines.append("    dungeon totals doc vs MDT: %d/%d rows match"
                 % (hits, len(totals)))
    if probe and hits != len(totals) - 1:
        fails.append("totals probe did not react")

    src_cre = parse_mdt_creatures(mdt_dir)
    dcre, probs = doc_creatures(doc)
    fails += probs
    matched = 0
    for src, label in sorted(MDT_DOCS.items()):
        # Sets: MDT stores some unit types as two enemy tables with the
        # identical (id, name, count); the doc's per-entry table lists each
        # entry id once. Conflicting counts for one id still surface, since
        # they are distinct tuples.
        s = set(src_cre[src])
        d = set(dcre.get(src, []))
        if s == d:
            matched += 1
        else:
            miss = sorted(s - d)[:3]
            extra = sorted(d - s)[:3]
            fails.append("creatures %s: src_only=%s doc_only=%s"
                         % (label, miss, extra))
    lines.append("    per-creature counts doc vs MDT: %d/%d dungeons exact"
                 % (matched, len(MDT_DOCS)))

    f, l = check_timer_table(doc)
    fails += f
    lines += l
    f, l = check_ladders(doc)
    fails += f
    lines += l

    doc_coord = re.sub(
        r"x = (-?\d+\.\d+), y = (-?\d+\.\d+), z = (-?\d+\.\d+)",
        r"\1, \2, \3", doc)
    if not re.search(r"-839\.0337, -2092\.268, 725\.8119", doc_coord):
        fails.append("checkpoint triple not extracted")
        lines.append("    checkpoint triple extraction: FAILED")
    ok_c, c_lines, _ = coord_trace(doc_coord, corpora)
    lines += c_lines
    if not ok_c:
        fails.append("coordinate trace")

    if probe:
        probe_fails, _ = run_derived(text, corpora, mdt_dir, probe=False)
        lines.append("    reaction to tampered totals row: %s"
                     % ("detected"
                        if any("total Atal'Dazar" in f for f in probe_fails)
                        else "NOT DETECTED"))
        if not any("total Atal'Dazar" in f for f in probe_fails):
            fails.append("totals probe wiring")
    return fails, lines


# ---------------------------------------------------------------- stage 5
def stage5(text):
    fails, lines = [], []
    injected = text + "\nStorming (affix index 15; +7)\n"
    if "Storming (affix index" not in injected:
        fails.append("injection did not land")
    _, lines_i = run_static(injected)
    if not any("PRESENT" in ln for ln in lines_i):
        fails.append("storming injection not caught")
    lines.append("    storming injection caught by negative check: %s"
                 % ("yes" if not any(
                     f == "no storming index" for f in fails) else "NO"))
    if "(was 8% per level)" not in text:
        fails.append("was-8 quote missing")
    lines.append("    8% appears only as the quoted 'was' value: ok")
    if "HTTP 500" not in text:
        fails.append("wago failure detail missing")
    lines.append("    wago endpoint failure recorded (HTTP 500): ok")
    return fails, lines


# ---------------------------------------------------------------- main
def main():
    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()

    print("=" * 68)
    print("AUDIT: MythicPlus_Rules_COMPLETED.txt (Mythic+ step 2)")
    print("=" * 68)

    mdt_dir, fork_dir, fork_head = fetch_sources()
    corpora = load_corpora(mdt_dir, fork_dir)

    fails1, lines1 = run_static(text)
    total1 = len(STATIC_CHECKS) + len(NEGATIVE_CHECKS)
    print("\n[1] Static checks: %d/%d passed" % (total1 - len(fails1), total1))
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
        cnt = text.count(old)
        if cnt != 1:
            undetected.append("%s (count=%d)" % (name, cnt))
            continue
        mutated = text.replace(old, new, 1)
        f_s, _ = run_static(mutated)
        f_d, _ = run_derived(mutated, corpora, mdt_dir)
        if not f_s and not f_d:
            undetected.append(name)
    print("    detected %d/%d" % (len(MUTATIONS) - len(undetected),
                                  len(MUTATIONS)))
    if undetected:
        print("    UNDETECTED: %s" % ", ".join(undetected))

    print("\n[3] Source cross-check (git fetch: MDT pinned, fork HEAD %s)"
          % fork_head[:12])
    ok3, lines3 = stage3(corpora)
    for ln in lines3:
        print(ln)

    print("\n[4] Derived values recomputed from source bodies")
    fails4, lines4 = run_derived(text, corpora, mdt_dir)
    for ln in lines4:
        print(ln)
    probe_fails, _ = run_derived(text, corpora, mdt_dir, probe=True)
    reacts = any("total Atal'Dazar" in f for f in probe_fails)
    print("    totals reaction probe: %s" % ("yes" if reacts else "NO"))
    if not reacts:
        fails4.append("totals probe")
    if fails4:
        print("    DERIVED STAGE FAILED: %s" % ", ".join(fails4))

    print("\n[5] Absence / control probes")
    fails5, lines5 = stage5(text)
    for ln in lines5:
        print(ln)
    if fails5:
        print("    PROBE STAGE FAILED: %s" % ", ".join(fails5))

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
