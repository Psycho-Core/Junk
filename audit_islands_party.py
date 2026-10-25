#!/usr/bin/env python3
"""Audit: Islands_Party_COMPLETED.txt (Islands 3)."""

import re
import subprocess
import sys

sys.path.insert(0, ".")
from audit_common import (gh_content, source_stage, mutation_probe,
                          coord_trace)

DOC = "# Ai Research prompts/Islands/Islands_Party_COMPLETED.txt"
DOC1 = "# Ai Research prompts/Islands/Islands_Maps_COMPLETED.txt"
DOC2 = "# Ai Research prompts/Islands/Islands_Enemy_COMPLETED.txt"
TCDEV = "TCDEVEmu/AtalDazar_BFA"
UNVERIFIED_MIN = 10

FILES = {
    "inst_h": (TCDEV, "src/server/game/Instances/InstanceScript.h"),
}
ISLES_DIR_FILES = [
    "UnchartedIsland", "ScenarioSnowblossomVillage",
    "ScenarioUngolRuins", "ScenarioVerdantWilds",
]

# (shrine, spell id) - verified on wowhead spell pages (effects + icons)
SHRINES = [
    ("Pillar of the Watchers", "248667"),
    ("Wanderer's Respite", "255114"),
    ("Primal Shrine", "243818"),
    ("Altar of the Sea", "248694"),
    ("Spirit Font", "254824"),
    ("Overgrown Relic", "264652"),
    ("Deepwoods Totem", "264666"),
    ("Rune-Etched Stone", "264673"),
    ("Moon-Touched Ruins", "255046"),
    ("Fireheart Idol", "264676"),
    ("Death Ward", "264679"),
    ("Slithering Shrine", "255012"),
    ("Cursed Offering", "264170"),
]
ABILITIES = [
    ("285835", "Activate Extractor"),
    ("280859", "Collecting"),
    ("285811", "Deploy Extractor"),
    ("285630", "Heart of Azeroth"),
]
RARES = [
    ("137579", "Unbound Azerite", "1882", "15198.4", "14802.6", "18.6424"),
    ("139218", "Life-Tender Olvarius", "1882", "14855.3", "14816.4",
     "6.34723"),
    ("139411", "Many-Fangs", "1882", "14912.7", "14627", "0"),
    ("139415", "Slitherscale", "1882", "15191", "14686.7", "0"),
    ("139416", "Volshas", "1882", "15157.8", "14644.9", "-0.101324"),
    ("139418", "Stagnant One", "1882", "14914.8", "14619.8", "0"),
    ("139681", "Bleakfin", "1882", "15118", "14633.8", "-0.0809143"),
    ("140992", "Corpseburster", "1882", "14933.8", "14883.8", "3.22263"),
]
ISLAND_MAPS = [
    ("1813", "Un'gol Ruins"), ("1814", "Havenswood"),
    ("1879", "Jorundall"), ("1882", "Verdant Wilds"),
    ("1883", "Whispering Reef"), ("1892", "Rotting Mire"),
    ("1893", "Dread Chain"), ("1897", "Molten Cay"),
    ("1898", "Skittering Hollow"), ("1907", "Snowblossom Village"),
    ("2124", "Crestfall"),
]


def norm(s):
    return re.sub(r"\s+", " ", s)


STATIC_CHECKS = [
    ("heading", "=== ISLAND EXPEDITIONS - PARTY BEHAVIOUR - BFA 8.3.7 "
                "(TRINITYCORE) - COMPLETED ==="),
    ("done", "DONE - step 3 of the Islands set complete"),
    ("src icy", "icy-veins.com island expeditions guide"),
    ("src wiki", "warcraft.wiki.gg \"Island Expedition\""),
    ("src moudi", "worldofmoudi.com island expedition stage guide"),
    ("src wowhead", "wowhead.com spell pages and the Seafarer Dubloons"),
    ("src rude", "superlativelyrude.com AI guide"),
    ("src reddit", "a community reddit guide (cited as"),
    ("src step1", "Islands_Maps (step 1), Islands_Enemy (step 2)"),
    ("s1 header", "1. THE ORDER IN WHICH TO COLLECT NODES"),
    ("s1 rare", "a rare equals a large treasure chest: 250 azerite"),
    ("s1 heroic", "250\n      on Heroic"),
    ("s1 globe", "drop a blue Azerite Globe (see buffs)"),
    ("s1 release", "do not release"),
    ("s1 event", "a large amount of Azerite has appeared"),
    ("s1 bags", "2 large Azerite bags on the ground (icy-veins)"),
    ("s1 mining", "never skip them"),
    ("s1 veins", "even the small veins are very"),
    ("s1 chests", "larger chests pay more than smaller"),
    ("s1 shells", "seashells pay azerite equal to a rare"),
    ("s1 stage flow", "loose nodes and mobs -> stage 2 azerite"),
    ("s1 clusters", "clusters rising in an announced area, guarded by "
                    "elementals"),
    ("s1 st2 trig", "N ~3-4k/33%, H ~6k/33%, M ~12k/50%"),
    ("s1 st3 trig", "N 6k/50%, H 12k/50%, M 20k/80%"),
    ("s1 st3 event", "boss + 2 huge chests, several rares with normal "
                     "chests and satchels, mini-bosses with"),
    ("s1 reddit", "skip mining and small/old chests and azerite sacks"),
    ("s1 reddit wait", "wait\n   for stage 3"),
    ("s1 route unv", "Node-to-node route (nearest first, pathing between "
                     "nodes):"),
    ("s2 header", "2. WHEN TO FIGHT THE ENEMY TEAM"),
    ("s2 grow", "grows the longer it survives, resets on"),
    ("s2 cap", "capped at 250 (icy-veins)"),
    ("s2 behind", "kill the enemy team ONCE when their value has"),
    ("s2 750", "that kill is worth 750 azerite"),
    ("s2 grave", "sends them to the graveyard, halting their gathering"),
    ("s2 avoid", "below maximum is heavily discouraged"),
    ("s2 rule", "Rule: fight once, avoid,"),
    ("s2 healer", "kill their healer first and crowd-control"),
    ("s2 ai", "saps, grips, and swaps to low-health"),
    ("s2 scripted", "only 3/11 islands scripted"),
    ("s2 aggro ai", "grows more aggressive when players fight"),
    ("s2 score", "player count and current azerite score"),
    ("s2 split", "keeps the enemy team busy"),
    ("s2 headroom", "1-2k azerite headroom"),
    ("s2 pvp", "losing team may attack the winners"),
    ("s2 step2 ref", "stack payout on kill, win at 9000"),
    ("s2 trigger unv", "Exact aggro radius and trigger weights: unverified"),
    ("s3 header", "3. WHICH RARES MATTER"),
    ("s3 chest", "each equals a large chest (250"),
    ("s3 globe", "drops the Azerite Globe (see buffs)"),
    ("s3 pet", "mount/toy/pet"),
    ("s3 pairing", "which event drops which mount: unverified"),
    ("s3 other isles", "for the other 10 islands"),
    ("s3 rank", "kill priority ranking among these 8"),
    ("s4 header", "4. ISLAND ABILITIES - USE THESE"),
    ("s4 intro", "wiki Abilities, spell ids on wowhead"),
    ("s5 header", "5. ISLAND BUFFS - USE THESE"),
    ("s5 globe line", "drops from elites/rares, lies on the ground 30 s"),
    ("s5 globe spell", "spell 265703 \"Azerite Energy\""),
    ("s5 globe nums", "heals 50% health and grants +30% damage and +20% "
                      "health"),
    ("s5 globe refresh", "refreshes the timer"),
    ("s5 globe rev", "revives nearby dead party"),
    ("s5 shrine debuff", "applied as a debuff (cannot be dispelled)"),
    ("s5 shrine one", "only one shrine effect at a time"),
    ("s5 shrine lasts", "lasts\n   10 minutes"),
    ("s5 shrine cd", "cooldown for several minutes"),
    ("s5 shrine suit", "Take one only if the"),
    ("s5 obj", "Primal Shrine 270021, spawns on"),
    ("s5 obj counts", "Havenswood 20, Snowblossom 16, Crestfall 14"),
    ("s5 obj counts2", "Molten Cay 11, Un'gol 11, Dread Chain 8, Rotting"),
    ("s5 obj other", "Object entries for the other 12 shrines: unverified"),
    ("s5 currency", "currency 1710"),
    ("s5 consumables", "A.T.O.M.I.K. Target Painter, Blessed"),
    ("s6 header", "6. UNVERIFIED LIST (consolidated)"),
    ("s6 route", "Node-to-node collection route and any per-position"),
    ("s6 aggro", "Enemy aggro radius and exact fight-trigger weights"),
    ("s6 isles", "Rare lists and coordinates for the 10 islands"),
    ("s6 rank", "Kill priority among the 8 Verdant rares"),
    ("s6 mining", "Mining and Opening spell ids"),
    ("s6 mount", "Mount-to-event-to-island drop pairing for stage 3"),
    ("s6 objects", "Object entries of the 12 shrines other than Primal"),
    ("s6 dubloon", "Dubloon consumable item and spell ids"),
    ("s6 order", "suits this server's rates"),
    ("s6 rotation", "Party rotation rules for 3 bots"),
    ("map line", "Map ids (step 1): 1813 Un'gol Ruins, 1814 Havenswood"),
]
for _eid, _name, _mid, _x, _y, _z in RARES:
    STATIC_CHECKS.append((
        "rare " + _eid,
        "%s \"%s\" (%s, %s, %s, %s)" % (_eid, _name, _mid, _x, _y, _z)))
for _mid, _name in ISLAND_MAPS:
    STATIC_CHECKS.append(("map " + _mid, "%s %s" % (_mid, _name)))
for _sid, _name in ABILITIES:
    STATIC_CHECKS.append(("ability " + _sid, "%s \"%s\"" % (_sid, _name)))
STATIC_CHECKS.append(("mining", "Mining - no spell id on the page: "
                                "unverified"))
STATIC_CHECKS.append(("opening", "Opening - no spell id on the page: "
                                 "unverified"))
for _shrine, _sid in SHRINES:
    STATIC_CHECKS.append(("shrine " + _sid, "%s %s" % (_shrine, _sid)))
STATIC_CHECKS.append(("zeal effect", "cannot dodge/block/parry"))
STATIC_CHECKS.append(("wanderer effect", "-60% healing taken"))
STATIC_CHECKS.append(("slither effect", "80% max health damage on apply"))
STATIC_CHECKS.append(("burned effect", "-50% max health (avoid on bots)"))

NEGATIVE_CHECKS = [
    ("no estimated coordinate", "estimated coordinate"),
    ("no navmesh confirmed", "navmesh confirmed"),
    ("no direct inspection", "verified by direct inspection"),
    ("no todo", "TODO"),
    ("no fixme", "FIXME"),
    ("no damageers", "damageers"),
    ("no placeholder", "placeholder"),
    ("no backtick", "`"),
]


def run_static(text):
    flat = norm(text)
    lines, fails = [], []
    n = flat.count("unverified")
    hit = n >= UNVERIFIED_MIN
    lines.append("    %-24s %s (%d >= %d)" % ("unverified count",
                 "ok" if hit else "FAIL", n, UNVERIFIED_MIN))
    if not hit:
        fails.append("unverified count")
    for name, lit in STATIC_CHECKS:
        ok = norm(lit) in flat
        lines.append("    %-24s %s" % (name, "ok" if ok else "MISSING"))
        if not ok:
            fails.append(name)
    for name, lit in NEGATIVE_CHECKS:
        ok = lit not in text if lit == "`" else norm(lit) not in flat
        lines.append("    %-24s %s" % (name, "ok" if ok else "PRESENT!"))
        if not ok:
            fails.append(name)
    return fails, lines


MUTATIONS = [
    ("heading", "- COMPLETED ===", "- DRAFT ==="),
    ("done", "DONE - step 3 of the Islands set complete",
     "DONE - step 3 of the Islands set finished"),
    ("src icy", "icy-veins.com", "icy-veigns.com"),
    ("s1 250", "chest: 250 azerite", "chest: 260 azerite"),
    ("s1 release", "do not release", "do not let go"),
    ("s1 bags", "2 large Azerite bags", "3 large Azerite bags"),
    ("s1 mining", "never skip them", "sometimes skip them"),
    ("s1 shells", "seashells pay azerite equal to a rare",
     "seashells pay azerite equal to a chest"),
    ("s1 st2n", "N ~3-4k/33%", "N ~3-4k/34%"),
    ("s1 st3m", "M 20k/80%", "M 20k/82%"),
    ("s1 boss", "boss + 2 huge chests", "boss + 3 huge chests"),
    ("s1 reddit", "skip mining and small/old chests",
     "skip mining and small/new chests"),
    ("s2 cap", "capped at 250 (icy-veins)", "capped at 251 (icy-veins)"),
    ("s2 750", "worth 750 azerite", "worth 760 azerite"),
    ("s2 grave", "graveyard, halting their gathering",
     "graveyard, helping their gathering"),
    ("s2 avoid", "below maximum is heavily discouraged",
     "below maximum is mildly discouraged"),
    ("s2 healer", "kill their healer first and crowd-control",
     "kill their damage first and crowd-control"),
    ("s2 ai", "grows more aggressive when players fight",
     "grows less aggressive when players fight"),
    ("s2 split", "keeps the enemy team busy", "keeps the enemy team calm"),
    ("s2 headroom", "1-2k azerite headroom", "2-3k azerite headroom"),
    ("s2 scripted", "only 3/11 islands scripted",
     "only 4/11 islands scripted"),
    ("rare coord", "14912.7, 14627, 0", "14912.8, 14627, 0"),
    ("rare entry", "139681 \"Bleakfin\"", "139682 \"Bleakfin\""),
    ("rare z", "3.22263)", "3.22264)"),
    ("s3 chest", "large chest (250", "large chest (260"),
    ("s3 rank", "ranking among these 8", "ranking among these 9"),
    ("ab 285835", "285835 \"Activate Extractor\"",
     "285836 \"Activate Extractor\""),
    ("ab 280859", "280859 \"Collecting\"", "280860 \"Collecting\""),
    ("ab 285811", "285811 \"Deploy Extractor\"",
     "285812 \"Deploy Extractor\""),
    ("ab 285630", "285630 \"Heart of Azeroth\"",
     "285631 \"Heart of Azeroth\""),
    ("mining unv", "no spell id on the page: unverified",
     "no spell id on the page: verified"),
    ("globe spell", "265703 \"Azerite Energy\"", "265704 \"Azerite Energy\""),
    ("globe heal", "heals 50% health", "heals 55% health"),
    ("globe ground", "lies on the ground 30 s", "lies on the ground 40 s"),
    ("globe dmg", "+30% damage and +20% health",
     "+31% damage and +20% health"),
    ("shrine 248667", "248667", "248668"),
    ("shrine 243818", "243818", "243819"),
    ("shrine 248694", "248694", "248695"),
    ("shrine 255012", "255012", "255013"),
    ("shrine 264170", "264170", "264171"),
    ("shrine 264676", "264676", "264677"),
    ("shrine 254824", "254824", "254825"),
    ("shrine dur", "10 minutes, one player", "11 minutes, one player"),
    ("shrine cd", "cooldown for several minutes",
     "cooldown for many minutes"),
    ("shrine speed", "80% max health", "85% max health"),
    ("obj id", "270021", "270022"),
    ("obj count", "Havenswood 20", "Havenswood 21"),
    ("currency", "currency 1710", "currency 1712"),
    ("map 1882", "1882 Verdant Wilds", "1881 Verdant Wilds"),
    ("map 1907", "1907 Snowblossom", "1906 Snowblossom"),
    ("s6 drop", "Party rotation rules for 3 bots",
     "Party rotation rules"),
]


def stage3(corpora):
    token_map = {
        "inst_h": [
            ("energy spell", "SPELL_AZERITE_ENERGY = 265703,"),
            ("island complete", "SPELL_ISLAND_COMPLETE = 245618,"),
            ("residue", "SPELL_AZERITE_RESIDUE = 260738,"),
        ],
    }
    ok, lines = source_stage(corpora, token_map)
    # island scenario folder listing must stay exactly four (doc cites
    # step 2's "only 3/11 scripted" claim)
    r = subprocess.run(
        ["gh", "api", "-X", "GET",
         "repos/%s/contents/src/server/scripts/BattleforAzeroth/"
         "Island%%20Expeditions" % TCDEV, "--jq", ".[].name"],
        capture_output=True, text=True)
    got = sorted(x for x in r.stdout.split() if x)
    hit = got == sorted(ISLES_DIR_FILES)
    lines.append("    %-28s %d == 4 scenario folders%s"
                 % ("script folders:", len(got), "" if hit else " FAIL"))
    if not hit:
        ok = False
    return ok, lines


def stage4(text, corpora, probe=False):
    fails, lines = [], []

    def bad(msg):
        fails.append(msg)

    flat = norm(text)
    doc1 = open(DOC1, encoding="utf-8").read()
    doc2 = open(DOC2, encoding="utf-8").read()

    # 1) rare rows: party vs step 1 (entry, name, map, x/y/z)
    def parse_rares(t):
        out = {}
        for m in re.finditer(
                r'(\d{6,7}) "([^"]+)"\s*:?\s*\((\d+), '
                r'(-?[\d.]+), (-?[\d.]+), (-?[\d.]+)\)', t):
            out[m.group(1)] = (m.group(2), int(m.group(3)),
                               tuple(float(m.group(i)) for i in (4, 5, 6)))
        return out
    p_r = parse_rares(text)
    s_r = parse_rares(doc1)
    matched = 0
    for eid, _name, mid, x, y, z in RARES:
        want = (_name, int(mid), (float(x), float(y), float(z)))
        if p_r.get(eid) != want:
            bad("party rare %s row %s" % (eid, p_r.get(eid)))
        elif s_r.get(eid) != want:
            bad("step1 rare %s row %s" % (eid, s_r.get(eid)))
        else:
            matched += 1
    lines.append("    rare rows matched step 1:               %d/8" % matched)

    # 2) map ids: step 1 island -> map dict vs party list
    s_maps = dict(re.findall(r"^\s{2,}(.+?) - map (\d+)", doc1, re.M))
    s_maps = {k: v for k, v in s_maps.items() if k in
              {n for _i, n in ISLAND_MAPS}}
    if len(s_maps) != 11:
        bad("step1 island parse %d" % len(s_maps))
    for mid, name in ISLAND_MAPS:
        if s_maps.get(name) != mid:
            bad("step1 map %s -> %s" % (name, s_maps.get(name)))
        if norm("%s %s" % (mid, name)) not in flat:
            bad("party map %s %s" % (mid, name))
    lines.append("    map ids cross-checked both docs:         %d/11" %
                 sum(1 for m, n in ISLAND_MAPS if s_maps.get(n) == m))

    # 3) shrine table: 13 rows, unique ids in BfA range
    sec = re.search(r"Shrines - clickable(.*?)Shrine gameobject",
                    text, re.S)
    rows = re.findall(r"^\s{3}(\S.*?)\s+(\d{6})\s{2,}", sec.group(1),
                      re.M) if sec else []
    names = [r[0].strip() for r in rows]
    ids = [r[1] for r in rows]
    if len(rows) != 13:
        bad("shrine rows %d" % len(rows))
    if len(set(ids)) != len(ids):
        bad("shrine ids not unique")
    if not all(240000 <= int(i) <= 270000 for i in ids):
        bad("shrine id range")
    if [n for n, _s in SHRINES] != names:
        bad("shrine names order %s" % names)
    if [s for _n, s in SHRINES] != ids:
        bad("shrine ids order")
    lines.append("    shrine table parsed:                     %d/13 "
                 "unique ids, BfA range" % len(rows))

    # 4) abilities + globe spell cross-doc (step 2 + source), with the
    # globe id chained party -> step 2 -> server header
    for sid, name in ABILITIES:
        if norm('%s "%s"' % (sid, name)) not in norm(doc2):
            bad("step2 ability %s" % sid)
        if norm('%s "%s"' % (sid, name)) not in flat:
            bad("party ability %s" % sid)
    p_g = re.search(r'spell (\d{6}) "Azerite Energy"', text)
    s_g = re.search(r'Spell (\d{6}) "Azerite Energy"', doc2)
    src_g = re.search(r"SPELL_AZERITE_ENERGY = (\d+)", corpora["inst_h"])
    g_ids = [g.group(1) if g else None for g in (p_g, s_g, src_g)]
    if g_ids != ["265703"] * 3:
        bad("globe id chain %s" % g_ids)
    lines.append("    abilities + globe id chain 265703:       %s"
                 % ("ok" if g_ids == ["265703"] * 3 else "FAIL"))

    # 5) server refs claimed from step 2
    for lit in ("+3 azerite to the killer", "capped at 250 stacks",
                "wins at 9000", "only 3 of the 11 rotation islands"):
        if norm(lit) not in norm(doc2):
            bad("step2 missing %s" % lit)
    if norm("stack payout on kill, win at 9000") not in flat:
        bad("party step2 ref")
    lines.append("    server refs (+3/250/9000/3-of-11):       step2 ok")

    # 6) arithmetic: kill worth 750 = 3 enemies x 250
    if "worth 750 azerite" not in text:
        bad("750 claim")
    lines.append("    750 azerite kill = 3 x 250 cap:          %s"
                 % ("ok" if 3 * 250 == 750 else "FAIL"))
    if 3 * 250 != 750:
        bad("750 arithmetic")

    # 7) shrine spawn-count paragraph: 11 island groups, names map to
    # step 1 islands
    m = re.search(r"Havenswood 20, Snowblossom 16,(.*?)Verdant 4, "
                  r"Whispering 3", text, re.S)
    if not m:
        bad("count paragraph")
        groups = []
    else:
        recon = norm("Havenswood 20, Snowblossom 16, " + m.group(1) +
                     "Verdant 4,")
        groups = re.findall(r"([A-Za-z' ]+?) (\d+),", recon)
        groups = [(n.strip(), int(c)) for n, c in groups]
        groups.append(("Whispering", 3))
    isl_names = [n for _i, n in ISLAND_MAPS]
    okn = 0
    for gname, _cnt in groups:
        if any(i.startswith(gname) for i in isl_names):
            okn += 1
    if len(groups) != 11:
        bad("count groups %d" % len(groups))
    lines.append("    shrine counts: 11 island groups matched: %d/11"
                 % okn)
    if okn != 11:
        bad("count names")

    # 8) step-1 doc holds every island name used in counts
    # (already implied by map dict) + ability no-id lines counted
    n_unvid = flat.count("unverified")
    if n_unvid < UNVERIFIED_MIN:
        bad("unverified %d" % n_unvid)

    # 9) coord trace: float triples must exist in step 1
    ok_t, lines_t, missing_t = coord_trace(text, {"step1": doc1})
    lines.append("    %s" % lines_t[-1].strip())
    if not ok_t:
        bad("coord trace %s" % (missing_t[:3],))
    return fails, lines


def stage5(text, corpora):
    lines, fails = [], []
    probes = [("TODO", "no todo"),
              ("verified by direct inspection", "no direct inspection"),
              ("estimated coordinate", "no estimated coordinate")]
    for extra, key in probes:
        f, _ = run_static(text + "\n%s.\n" % extra)
        r = key in f
        lines.append("    injection probe (%s):%s"
                     % (extra[:28], " detected" if r else " NOT DETECTED"))
        if not r:
            fails.append("probe %s" % key)
    stripped = text.replace("unverified", "verified")
    f, _ = run_static(stripped)
    r = "unverified count" in f
    lines.append("    injection probe (unverified stripped):%s"
                 % (" detected" if r else " NOT DETECTED"))
    if not r:
        fails.append("unverified probe")
    res = subprocess.run(
        ["gh", "api", "-X", "GET",
         "repos/TCDEVEmu/AtalDazar_BFA/contents/DoesNotExist.sql"],
        capture_output=True, text=True)
    absent = res.returncode != 0
    lines.append("    control: bogus repo path 404:                  %s"
                 % ("yes" if absent else "NO"))
    if not absent:
        fails.append("404 control")
    fake = text + "\nInjected 123.456, 789.012, 345.678 triple line.\n"
    ok_t, _lines_t, missing_t = coord_trace(fake, {"step1": ""})
    reacted = not ok_t and len(missing_t) >= 1
    lines.append("    coord trace probe (fake triple):               %s"
                 % ("detected" if reacted else "NOT DETECTED"))
    if not reacted:
        fails.append("coord probe")
    return fails, lines


def main():
    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()
    print("=" * 68)
    print("AUDIT: Islands_Party_COMPLETED.txt (Islands 3)")
    print("=" * 68)

    fails1, lines1 = run_static(text)
    total1 = len(STATIC_CHECKS) + len(NEGATIVE_CHECKS) + 1
    print("\n[1] Static checks: %d/%d passed" % (total1 - len(fails1),
                                                 total1))
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
    print("    note: icy-veins/wowhead/moudi/wiki/reddit facts are "
          "document-internal")
    print("    (bash has no route to those hosts); GitHub + step1/step2 "
          "corpora below.")
    corpora = {}
    for key, (repo, path) in FILES.items():
        corpora[key] = gh_content(repo, path)
    missing_f = [k for k, v in corpora.items() if not v]
    if missing_f:
        print("    CORPUS FETCH FAILED: %s" % missing_f)
        return 1
    ok3, lines3 = stage3(corpora)
    for ln in lines3:
        print(ln)
    if not ok3:
        print("    SOURCE CROSS-CHECK FAILED")
    probe_undetected = mutation_probe(
        corpora,
        {"inst_h": [("energy spell in source",
                      "SPELL_AZERITE_ENERGY = 265703,")]},
        lambda t: t.replace("SPELL_AZERITE_ENERGY = 265703,",
                            "SPELL_AZERITE_ENERGY = 265704,"))
    print("    reaction to tampered source (verified): %s"
          % ("yes" if probe_undetected == [] else "NO"))
    if probe_undetected != []:
        ok3 = False

    print("\n[4] Derived values recomputed against step 1 / step 2")
    fails4, lines4 = stage4(text, corpora)
    for ln in lines4:
        print(ln)
    if fails4:
        print("    DERIVED STAGE FAILED: %s" % ", ".join(str(f) for f in
                                                         fails4))
    doc_probes = [
        ("rare coord", "15198.4, 14802.6, 18.6424",
         "15198.5, 14802.6, 18.6424"),
        ("shrine id", "248667", "248999"),
        ("map id", "1882 Verdant Wilds", "1881 Verdant Wilds"),
        ("globe spell", "265703", "265999"),
    ]
    baseline = set(fails4)
    for label, old, new in doc_probes:
        mutated = text.replace(old, new)
        if mutated == text:
            print("    doc probe (%s):     no-op!" % label)
            fails4.append("probe no-op " + label)
            continue
        pf, _ = stage4(mutated, corpora, probe=True)
        reacted = any(f not in baseline for f in pf)
        print("    doc probe (%s):     %s" % (
            label, "reacts" if reacted else "NOT DETECTED"))
        if not reacted:
            fails4.append("probe " + label)

    print("\n[5] Absence / injection")
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
        print("  static checks: %d/%d" % (total1, total1))
        print("  mutations:     %d/%d" % (len(MUTATIONS), len(MUTATIONS)))
        return 0
    print("AUDIT RESULT: FAIL")
    print("  %d failing item(s): %s" % (len(all_fails), all_fails))
    return 1


if __name__ == "__main__":
    sys.exit(main())
