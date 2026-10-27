#!/usr/bin/env python3
"""Audit Craft_Archaeology.txt - STEP 137.

Families: S title/headings, 1-10 section content, H hygiene.
Each check is a plain substring containment on the payload text; every needle
must appear on a single line (wrap-safe). Self-test mutates the payload and
requires >= 1 failing check per mutation; each mutation literal must occur
exactly once in the payload.
"""
import sys
from pathlib import Path

PAYLOAD = Path(__file__).resolve().parent / "Craft_Archaeology.txt"
CHECKS = []


def add(fam, *needles):
    for n in needles:
        CHECKS.append((fam, n))


# --- S: title, underline, scope, headings ---------------------------------
add("S",
    "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - ARCHAEOLOGY FOR A SERVER-SIDE COMPANION",
    "levels Archaeology on a TrinityCore-based 8.3.7 server. Short answer: it can",
    "solving are absent from the core (section 8). Archaeology is a single skill",
    "Everything below was read from a source fetched this week (2026-10-27);",
    "Printed counts are exactly what the linked sources print; the TrinityCore lines",
    "TrinityCore lines",
    "are quoted at commit dc5955decd1be4877cbecad03bb41164d57014c8.",
    "1. THE SKILL LINES AND HOW A COMPANION LEARNS THEM",
    "2. TRAINERS AND THEIR POSITIONS",
    "3. CHEAPEST ROUTE 1 TO THE CAP OF EACH LINE",
    "4. MATERIALS AND WHERE EACH COMES FROM",
    "5. TRAINER COSTS",
    "6. LEVEL NEEDED",
    "7. WHAT THE CORE MUST DO FOR A CRAFT TO SUCCEED",
    "8. WHAT A SERVER-SIDE CHARACTER (NO CLIENT) CANNOT DO",
    "9. CONFLICTS AND UNVERIFIED INDEX",
    "10. SOURCES",
    )

# --- 1: skill line, learn chain, rank ladder ------------------------------
add("1",
    "Parent skill line: SKILL_ARCHAEOLOGY = 794 (TrinityCore",
    "Miscellaneous/SharedDefines.h line 5989; also LOCKTYPE 794 at line 6279 and",
    "QUEST_SORT 794 at line 6372",
    "one skill track from 1 to 950.\"",
    "  Classic        Apprentice/Journeyman/Expert/Artisan   1-300    Dwarf, Fossil, Night Elf, Troll",
    "  Burning Crusade Master                                 300-375  Draenei, Orc",
    "  Wrath          Grand Master                            375-450  Nerubian, Vrykul",
    "  Cataclysm      Illustrious Master                     450-525  Tol'vir",
    "  Mists of Pandaria Zen Master                           525-600  Mantid, Mogu, Pandaren",
    "  Warlords       Draenor Master                          600-700  Arakkoa, Orc Clans, Ogre",
    "  Legion         Legion Master                        700-800  Demon, Highborne, Highmountain Tauren",
    "  Battle for Azeroth (no name printed)                   800-950  Drust, Zandalari",
    "until level 20\"; wiki Archaeology_trainers - \"learn at level 20\".",
    "learn at level 20\".",
    "Apprentice Archaeology",
    "(spell 80836, added 4.0.0). Its wowhead Spell Details rows: \"Effect #1",
    "Learn Spell\" -> [Archaeology] (spell 78670), \"Effect #2 Learn Skill Step",
    "(794) Value: 1\".",
    "Spell 78670 \"Archaeology\" (added 4.0.0, Quick Facts Training cost: 10)",
    "artifacts up to a maximum potential skill of 75\", with Effect #1 Trade",
    "Skill and Effect #2 Learn Skill (Archaeology, 794) Value: 1.",
    "table plus individual page probes of the four boundary ranks",
    "  Apprentice            75    78670     1                   cap text \"75\"",
    "  Journeyman            150   88961     unverified          skill col (50)",
    "  Expert                225   89718     unverified          skill col (125)",
    "  Artisan               300   89719     unverified          skill col (200)",
    "  Master                375   89720     unverified          skill col (275)",
    "  Grand Master          450   89721     unverified          skill col (350)",
    "  Illustrious Master    525   89722     unverified          skill col (425)",
    "  Zen Master            600   110393    unverified          skill col (500)",
    "  Draenor Master        700   158762    9 (added 6.0.1)     cap text \"700\"",
    "  Legion Master         800   195127    10 (added 7.0.1)    cap text \"800\"",
    "  Battle for Azeroth    950   278910    11 (added 8.0.1)    cap text \"950\"",
    "values (50/125/200/275/350/425/500) equal the wiki trainer page's",
    "printed \"(1)\" on wowhead) are learnable at skill 1 on live 8.3.7: unverified.",
    "Upon learning, the player receives the Survey ability (wiki intro:",
    "Survey = spell 80451, \"Survey for archaeology fragments within a dig site.",
    "Each survey will direct you closer to the location of the fragments.\"",
    "(wowhead spell 80451, category Secondary Skill Spells, added 4.0.0;",
    "wowpedia Survey properties: 40 yd range, 1 sec cast, 3 sec cooldown,",
    "You have to click on 'Train' multiple times!\"",
    "since patch 6.0.2 fragments live in the",
    "means that you never carry them in your inventory\"",
    )

# --- 2: trainers and positions -------------------------------------------
add("2",
    "  Belloc Brightblade  Horde      Orgrimmar      [49.0,79.6]   npc 47571",
    "  Harrison Jones      Alliance   Stormwind      [85.6,25.8]   npc 44238",
    "  Ironpants Ironforge    Alliance  Ironforge     [75.6,11.6]",
    "  Adam Hossack           Horde     Undercity     [76.0,36.4]",
    "  Elynara                Horde     Silvermoon    [81.6,63.8]",
    "  Stephanie Krutsick     neutral   Lor'danel     [50.6,20.6]",
    "  Faena Woolybush        Alliance  Theramore     [66,45]",
    "  Hammon the Jaded       Alliance  Darnassus     [43.2,83.6]",
    "  Diya                   Alliance  Exodar        [34.6,66.8]",
    "  Otoh Greyhide          Horde     Thunder Bluff [75.8,28.0]",
    "  Gerdra Fardelve        Alliance  Honor Hold    [53.5,66.0]",
    "  Sirabel                Horde     Thrallmar     [52.6,36.0]",
    "  Boduro the Seeker      neutral   Shattrath     [62.5,70.2]",
    "  Falda Fardelve         Alliance  Valiance Keep [57.5,71.6]",
    "  Hugen Goldwise         Alliance  Valgarde      [58.2,62.4]",
    "  Lindarel               Alliance  Warsong Hold  [41.2,53.8]",
    "  Ian Thomas Wall        Horde     Vengeance Landing [79.4,29.2]",
    "  Dariness               neutral   Dalaran       [48.5,38.6]",
    "  Brann Bronzebeard      neutral   Seat of Knowledge [83.5,31.0]",
    "  Elynara (MoP pins)     Horde     Dominance Offensive pins [21.1,15.0],",
    "                                  [57.2,78.6], [33.5,33.8]",
    "  Dariness the Learned   neutral   Dalaran (Broken Isles)  npc 93538",
    "    - teaches Legion Archaeology 700-800 and every lower rank.",
    "  Examiner Alerinda      Horde     Dazar'alor               npc 122701",
    "  Jane Hudson            Alliance  Boralus                 npc 136106",
    "    - both teach Battle for Azeroth Archaeology 800-950 and every lower rank.",
    "      unverified (npc ids and cities are printed by the guide above).",
    "and click Train until every rank spell in section 1 is known; then talk to the",
    )

# --- 3: route, mechanics, skill rules -------------------------------------
add("3",
    "There is one line, cap 950.",
    "     red = over 70 yards, yellow = 30-70 yards, green = under 30 yards.",
    "     appears over your head; use the survey tool to dig, then loot the object",
    "  4. Each dig site yields 6 finds (9 on Broken Isles, Draenor, Zandalar and",
    "then it despawns and a new site appears. Sites do not change",
    "     on logout or server restart (guide wording); four sites per continent,",
    "     three on the Broken Isles, five each on Zandalar and Kul Tiras.",
    "  5. Looted finds grant culture fragments (section 4) plus a random chance at",
    "an \"out-of-date\" banner - see section 9 item 1):",
    "  - \"At all levels, players receive one skill point for every successful",
    "    collection of archaeology fragments, five skill points for creating a",
    "    common artifact, and 15 skill points for completing a rare artifact.\"",
    "  - Each site holds 6 surveys (9 for Broken Isles, Zandalar, Kul Tiras),",
    "    each survey yields 5-9 fragments, i.e. 30-54 per site (45-81 for the",
    "    nine-find continents). Dwarves get +1 per survey (Explorer racial).",
    "  - \"You will get 6-9 skill points for completing each dig site and 5 for",
    "    any artifact you solve (15 for rare ones).\"",
    "  - 1-750: Broken Isles is fastest (9 finds, sites confined to one zone;",
    "    zone rotates every two weeks). Draenor works to 700 but with more",
    "    travel; Eastern Kingdoms/Kalimdor (6 finds) are the slowest; Outland",
    "    from skill 300, Northrend from 375, Pandaria from 525.",
    "  - From about 750, fragment loots give skill much less frequently - switch",
    "    to Zandalar or Kul Tiras (9 finds). For the last 150 points (800-950):",
    "    \"you can only gain skill points by surveying in Zandalar or Kul Tiras",
    "    dig sites, and solving artifacts won't give any skill points anymore\".",
    "    The last 30-40 points are very slow (multiple sites per point).",
    "  - Monthly Darkmoon Faire quest \"Fun for the Little Ones\" (quest 29507,",
    "    Professor Thaddeus Paleo npc 14847) gives +5 skill for 15 Fossil",
    "    fragments from Eastern Kingdoms or Kalimdor sites.",
    "column): Fossil/Night Elf/Troll/Dwarf (Eastern Kingdoms and Kalimdor),",
    "all Draenor, all Broken Isles, Zandalari, Drust = skill 1; Draenei and Orc",
    "(Outland) = 300; Nerubian, Vrykul, Troll and Night Elf (Northrend) = 375;",
    "Tol'vir (Uldum) = 450; Mogu, Pandaren, Mantid (Pandaria) = 525.",
    "required for each artifact can vary from 25 to 200\"; the project offered per",
    "culture is random, so the same project must be solved repeatedly to chase a",
    "specific reward; excess fragments roll into the next project. Keystones add",
    "12 fragments to a socketed project (20 for Pandaria and Draenor keystones);",
    "commons allow one or two, rare projects often two or three; Fossil has no",
    "skill 150 and 100 Fossil fragments; Bones of Transformation needs skill 450",
    "and 150 Night Elf fragments (up to three Highborne Scrolls); Crawling Claw",
    "needs skill 450 and 150 Tol'vir fragments (up to three Tol'vir Hieroglyphics).",
    "Number of crafts to the cap: there is no fixed solve count. Fragments-per-",
    "project is random in 25-200, project rolls are random, and the skill chance",
    "per fragment loot falls off after 750 while solves stop paying at 800 - no",
    "source read this step prints cumulative solve or site totals, so exact totals",
    "are unverified. The printable constants are: 1 skill per fragment loot, +5",
    "solve (common), +15 solve (rare), 6-9 fragment loots per site, 5-9 fragments",
    "per loot (6-10 for Dwarves), 5 Darkmoon points per month.",
    )

# --- 4: materials ---------------------------------------------------------
add("4",
    "  Dwarf Archaeology Fragment    currency 384 (wowhead currency page; \"Total",
    "    Maximum: 200\"; wowpedia: found with Survey at Dwarven sites)",
    "  Troll Archaeology Fragment    currency 385 (wow-freakz currency mirror)",
    "  Cataclysm-era inventory item form: Dwarf Archaeology Fragment item 52577",
    '    (wowdb item page, category Other Trade Goods; the page\'s own comment says',
    "    it is \"Not available in the game\" since 6.0.2 - replaced by currencies)",
    "  Maximum stored per fragment type: 200 (wiki Dwarf fragment page)",
    "  Currency ids for the other 18 cultures: unverified (not probed this step).",
    "  Crate of Dwarven Archaeology Fragments item 87533 - Binds when picked up,",
    "    sold by Brann Bronzebeard at the Seat of Knowledge for 1 Restored",
    "one): Troll Tablet item 63128, Highborne Scroll item 63127, Dwarf Rune Stone",
    "item 52843, Tol'vir Hieroglyphic item 64397 (wowdb); other names verified",
    "from wowpedia with ids unverified: Draenei Tome, Orc Blood Text, Nerubian",
    "Obelisk, Vrykul Rune Stick, Mantid Amber Sliver, Mogu Statue Piece, Pandaren",
    "Pottery Shard, Arakkoa Cipher, Draenor Clan Orator Cane, Ogre Missive,",
    "Ancient Suramar Scroll (Highborne), Highmountain Ritual-Stone, Mark of the",
    "Deceiver (Demonic), Etched Drust Bone (Drust), Zandalari Idol (Zandalari);",
    "Fossil has no keystone.",
    "Nothing else is consumed: Survey has no reagents, solving consumes only",
    "fragment currency plus optional keystones, and trainers charge gold",
    "Artifact crates above (availability of that crate on 8.3.7: unverified).",
    )

# --- 5: trainer costs -----------------------------------------------------
add("5",
    "Rank cost table printed by the wiki Archaeology_trainers page (rank names and",
    "  rank                  character level   skill gate   cost",
    "  Apprentice            20                -            10 s",
    "  Journeyman            20                50           10 s",
    "  Expert                20                125          10 s",
    "  Artisan               35                200          2 g 50 s",
    "  Master                50                275          10 g",
    "  Grand Master          65                350          15 g",
    "  Illustrious Master    75                425          25 g",
    "cost: 10, matching the 10 s row. Costs for the Zen Master, Draenor Master,",
    "Legion Master and Battle for Azeroth ranks: unverified (the wiki table stops",
    "at Illustrious Master; the retail guide names no prices). The only free",
    "skill point is the monthly Darkmoon Faire +5 (section 3).",
    )

# --- 6: level needed ------------------------------------------------------
add("6",
    "Character level 20 to learn the profession at all (wiki trainers page and",
    "wiki Archaeology intro; the wowwiki-archive guide also prints \"at least level",
    "section 5's skill column: 50/125/200/275/350/425 for Journeyman through",
    "Illustrious Master; the four expansion ranks print skill (1) on wowhead and",
    "have no wiki gate row (unverified). Culture dig-site access gates: 300 for",
    "Outland, 375 for Northrend, 450 for Tol'vir, 525 for Pandaria (section 3);",
    "everything else opens at skill 1.",
    )

# --- 7: TC anchors and required machinery ---------------------------------
add("7",
    "TrinityCore anchors read this step (commit dc5955decd1be4877cbecad03bb41164d57014c8):",
    "  - SKILL_ARCHAEOLOGY = 794: Miscellaneous/SharedDefines.h line 5989; the",
    "    LOCKTYPE and QUEST_SORT mappings at lines 6279 and 6372.",
    "  - ITEM_SUBCLASS_PROFESSION_ARCHAEOLOGY = 13: ItemTemplate.h line 768; the",
    "    profession-skill array at ItemTemplate.cpp line 117 includes",
    "  - GameObject profession fields list Archaeology: GameObjectData.h lines",
    "    239-241 and 859 (Profession/Profession2/Profession3).",
    "  - ScriptedGossip.h line 51: TRADESKILL_ARCHAEOLOGY = 16 (gossip linkage",
    "  - DBCEnums.h line 2962: HideArchaeologyDigs = 0x00000100 (map-filter flag",
    "  - SpellEffects.cpp lines 279 and 283: spell effects 187",
    "    (SPELL_EFFECT_RANDOMIZE_ARCHAEOLOGY_DIGSITES) and 191",
    "    (SPELL_EFFECT_TELEPORT_TO_DIGSITE) are wired to EffectNULL.",
    "  - SpellMgr.cpp line 4630 mentions archaeology only in a comment",
    "digsite assignment (the job of effect 187); (b) a CMSG_REQUEST_SURVEY",
    "handler that decides find progress; (c) an SMSG_ARCHAEOLOGY_SURVERY_CAST",
    "reply carrying direction and distance for the tripod; (d) find object",
    "spawning with personal loot that increments the fragment currency; (e) a",
    "solve path that validates caps and culture gates, consumes currency plus",
    "keystones, creates the artifact, and rolls the +1/+5/+15 skill points. In",
    "the code read at dc5955de only the static definitions in the list above",
    "exist; the handlers are recorded in section 8 as unimplemented. Learning",
    "spell 80836, the Trade Skill effect on 78670, and trainer gossip go through",
    "generic machinery that other professions already use, so the profession can",
    "be learned and displayed; the live-server behaviour of that generic path was",
    "not test-run (unverified).",
    )

# --- 8: cannot-do ---------------------------------------------------------
add("8",
    "Verified dead ends in the core at dc5955de:",
    "  - Receive digsite generation: SPELL_EFFECT_RANDOMIZE_ARCHAEOLOGY_DIGSITES",
    "    (187) is EffectNULL (SpellEffects.cpp line 279), so no spell in the",
    "  - Travel to a site by spell: SPELL_EFFECT_TELEPORT_TO_DIGSITE (191) is",
    "    EffectNULL (SpellEffects.cpp line 283).",
    "  - Ask the server to survey: opcode CMSG_REQUEST_SURVEY 0x3D030E is",
    "    STATUS_UNHANDLED bound to Handle_NULL (Opcodes.cpp line 990) - every",
    "  - Receive survey direction: opcode SMSG_ARCHAEOLOGY_SURVERY_CAST 0x45001D",
    "    is STATUS_UNHANDLED on both sides (Opcodes.h line 1155, Opcodes.cpp",
    "    line 1234) - the server never emits the packet that would point the",
    "  - Use an archaeology loot channel: there is no LOOT_ARCHAEOLOGY value in",
    "    the LootType list (Loot.h lines 100-116).",
    "  - Solve or keystone machinery: case-sensitive greps for SolveArtifact,",
    "    ARCHAEOLOGY_FIND, ArchaeologyFind and Keystone across src/server return",
    "    zero hits; SKILL_ARCHAEOLOGY's only .cpp use is the ItemTemplate",
    "    profession array (ItemTemplate.cpp line 117); Player.cpp matches no",
    "    literal 794 skill handling; the Darkmoon quest 29507 is not in the DB",
    "Consequence chain: no digsite assignment -> nothing to survey -> survey",
    "requests dropped and survey replies never built -> no finds, no fragment",
    "currency, no solves, no +1/+5/+15 skill points. The companion can be taught",
    "skill 794 through the generic trainer path, and will see an empty",
    "archaeology journal, but it cannot gain a single skill point or complete a",
    "single artifact on this core as shipped. Making it work is not a tuning",
    "change: it needs a digsite manager (effect 187), a survey handler and",
    "reply packet, personal find objects with loot, fragment currency state on",
    "the player, and a solve handler with skill rolls - a whole subsystem that",
    "does not exist in this repository.",
    )

# --- 9: conflicts and unverified index ------------------------------------
add("9",
    "  1. The wiki's Levels section (source of the 1 / 5 / 15 skill rules) carries",
    "     an explicit \"This section contains information that is out-of-date\"",
    "  2. Era conflict on when fragment loots stop paying: the gotwarcraft",
    "  3. The wiki trainer cost table uses pre-BfA rank names and stops at",
    "  4. Learn-spell ids probed this step: 80836, 78670, 88961, 89718, 89719,",
    "  5. Fragment currency ids verified: Dwarf 384, Troll 385. The other 18",
    "  6. Keystone item ids verified: 63128, 63127, 52843, 64397. The remaining",
    "  7. The wiki trainer page lists no BfA trainers (Examiner Alerinda, Jane",
    "  8. Site counts: wiki section Zones and dig sites says \"There are four dig",
    "  9. Light thresholds vary by source: retail guide red over 70 / yellow",
    " 10. The solve request (what packet or spell the client sends when the",
    " 11. Skill-gate semantics for the four expansion rank spells (wowhead",
    " 12. Wowpedia artifacts examples (Fossilized Raptor 150/100, Bones of",
    " 13. Crate of Dwarven Archaeology Fragments (87533) vendors are MoP/WoD",
    " 14. The retail guide's Midnight note (\"Archaeology didn't get any content",
    " 15. Northrend sites yielding Troll and Night Elf fragments (guide table)",
    " 16. Live-server behaviour of the generic learning path (section 7): no",
    )

# --- 10: sources ----------------------------------------------------------
add("10",
    "  - warcraft.wiki.gg/wiki/Archaeology (read: chunks 0, 2, 3, 4 of 23 -",
    "  - warcraft.wiki.gg/wiki/Archaeology_trainers (oldid 6503370, all three",
    "  - warcraft.wiki.gg/wiki/Dwarf_Archaeology_Fragment and",
    "  - warcraft.wiki.gg/wiki/Crate_of_Dwarven_Archaeology_Fragments (item",
    "  - wowhead.com/spell=80451 (Survey), spell=80836 (Apprentice Archaeology),",
    "  - wow-professions.com/guides/wow-archaeology-guide (retail 1-950 guide,",
    "  - wowpedia.fandom.com/wiki/Keystone (chunks 0-1 - socket mechanics and the",
    "  - wowdb.com/items/87533 and its comment thread (6.0.2 currency move);",
    "  - TrinityCore git at commit dc5955decd1be4877cbecad03bb41164d57014c8:",
    "    SharedDefines.h, ItemTemplate.h/.cpp, GameObjectData.h, ScriptedGossip.h,",
    "  - Era-flagged, conflict notes only: gotwarcraft.com Cataclysm guide (2012),",
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
    long_lines = [i for i, ln in enumerate(lines, 1) if len(ln) > 100]
    if long_lines:
        out.append(f"line(s) over 100 columns: {long_lines[:5]}")
    for i, ln in enumerate(lines, 1):
        if ln != ln.rstrip():
            out.append(f"trailing whitespace on line {i}")
            break
    want = "BATTLE FOR AZEROTH 8.3.7 (BUILD 35662) - ARCHAEOLOGY FOR A SERVER-SIDE COMPANION"
    if lines[0] != want:
        out.append("title line mismatch")
    if not (len(lines) > 1 and set(lines[1]) == {"="} and len(lines[1]) == len(want)):
        out.append("title underline mismatch")
    return out


def run_checks(text):
    failures = []
    for fam, needle in CHECKS:
        if needle not in text:
            failures.append((fam, needle))
    return failures


def report(text):
    failures = run_checks(text)
    h = hygiene_failures(text)
    by_fam = {}
    for fam, _ in CHECKS:
        by_fam[fam] = by_fam.get(fam, 0) + 1
    total = len(CHECKS)
    for fam in sorted(by_fam, key=lambda f: (f == "H", f)):
        nf = sum(1 for f, _ in failures if f == fam)
        status = "PASS" if nf == 0 else f"FAIL {nf}"
        print(f"family {fam}: {by_fam[fam] - nf}/{by_fam[fam]} {status}")
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
    # (S) title
    ("ARCHAEOLOGY FOR A SERVER-SIDE COMPANION", "ARCHAEOLOGY FOR A SERVER SIDE COMPANION"),
    # (1) skill line / ladder
    ("SKILL_ARCHAEOLOGY = 794 (TrinityCore", "SKILL_ARCHAEOLOGY = 795 (TrinityCore"),
    ("one skill track from 1 to 950", "one skill track from 1 to 951"),
    ("Spell 78670 \"Archaeology\" (added 4.0.0", "Spell 78671 \"Archaeology\" (added 4.0.0"),
    # (2) trainers
    ("npc 47571", "npc 47572"),
    ("npc 122701", "npc 122702"),
    # (3) route
    ("Each dig site yields 6 finds", "Each dig site yields 7 finds"),
    ("Tol'vir (Uldum) = 450; Mogu, Pandaren, Mantid (Pandaria) = 525.",
     "Tol'vir (Uldum) = 451; Mogu, Pandaren, Mantid (Pandaria) = 525."),
    # (4) materials
    ("currency 384 (wowhead currency page", "currency 386 (wowhead currency page"),
    ("  Troll Archaeology Fragment    currency 385 (wow-freakz currency mirror)",
     "  Troll Archaeology Fragment    currency 387 (wow-freakz currency mirror)"),
    ("Maximum stored per fragment type: 200", "Maximum stored per fragment type: 201"),
    # (5) costs
    ("Illustrious Master    75                425          25 g",
     "Illustrious Master    75                425          26 g"),
    ("printed by the wiki Archaeology_trainers page", "printed by the wiki Archaeology_trainers guide"),
    # (6) level
    ("Character level 20 to learn the profession at all", "Character level 21 to learn the profession at all"),
    # (7) core must do
    ("HideArchaeologyDigs = 0x00000100", "HideArchaeologyDigs = 0x00000101"),
    # (8) cannot do
    ("CMSG_REQUEST_SURVEY 0x3D030E is", "CMSG_REQUEST_SURVEY 0x3D030F is"),
    ("SMSG_ARCHAEOLOGY_SURVERY_CAST 0x45001D", "SMSG_ARCHAEOLOGY_SURVERY_CAST 0x45001E"),
    ("no LOOT_ARCHAEOLOGY value in", "no LOOT_ARCHAEOLOGY_COUNT value in"),
    # (9) conflicts
    ("Dwarf 384, Troll 385. The other 18", "Dwarf 385, Troll 385. The other 18"),
    ("wiki trainer page lists no BfA trainers", "wiki trainer page lists some BfA trainers"),
    # (10) sources
    (" wowhead.com/spell=80451 (Survey)", " wowhead.com/spell=80452 (Survey)"),
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
