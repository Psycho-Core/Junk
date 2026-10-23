#!/usr/bin/env python3
"""Shared helpers for the arena document audits.

The source cross-check pulls the upstream file a number came from and
verifies the exact literal is present there, so an audit is not only a
self-consistent string check on the document being audited.
"""

import base64
import re
import subprocess


def gh_content(repo, path):
    """Return the decoded text of a file from GitHub via the gh CLI."""
    result = subprocess.run(
        ["gh", "api", "-X", "GET",
         "repos/%s/contents/%s" % (repo, path), "--jq", ".content"],
        capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("gh api failed for %s/%s: %s"
                           % (repo, path, result.stderr.strip()))
    return base64.b64decode(result.stdout).decode("utf-8", "replace")


def missing(corpus, tokens):
    """tokens: list of (label, literal). Return labels whose literal is absent."""
    return [label for label, lit in tokens if lit not in corpus]


def source_stage(corpora, token_map):
    """corpora: {name: text}. token_map: {name: [(label, literal), ...]}.

    Returns (ok, lines). Also returns per-source counts for the report.
    """
    ok = True
    lines = []
    for name, tokens in token_map.items():
        corpus = corpora[name]
        gone = missing(corpus, tokens)
        lines.append("    %-28s %2d/%-2d literals found in source"
                     % (name, len(tokens) - len(gone), len(tokens)))
        for g in gone:
            lines.append("      MISSING: %s" % g)
            ok = False
    return ok, lines


def mutation_probe(corpora, token_map, mutate):
    """Apply `mutate` to each corpus and confirm the cross-check fails."""
    undetected = []
    for name, tokens in token_map.items():
        broken = dict(corpora)
        broken[name] = mutate(corpora[name])
        ok, _ = source_stage(broken, {name: tokens})
        if ok:
            undetected.append(name)
    return undetected


def _triples(corpus):
    """All (x, y, z) triples in a corpus, rounded for comparison."""
    found = set()
    for m in re.finditer(
            r"(-?\d+\.\d+)f?,\s*(-?\d+\.\d+)f?,\s*(-?\d+\.\d+)", corpus):
        found.add(tuple(round(float(m.group(i)), 3) for i in (1, 2, 3)))
    return found


def coord_trace(text, corpora):
    """Every coordinate triple in the document must exist in a source.

    If the same triple appears in a block the document marks unverified,
    it is excused - the rule is 'no invented numbers', not 'no unknowns'.
    """
    upstream = set()
    for corpus in corpora.values():
        upstream |= _triples(corpus)

    doc_triples = set()
    for m in re.finditer(
            r"(-?\d+\.\d+),\s*(-?\d+\.\d+),\s*(-?\d+\.\d+)", text):
        doc_triples.add(tuple(round(float(m.group(i)), 3) for i in (1, 2, 3)))
    # Documents that list coordinates on labelled X / Y / Z lines.
    for m in re.finditer(
            r"^\s*X:\s*(-?\d+\.\d+)\s*$\n"
            r"\s*Y:\s*(-?\d+\.\d+)\s*$\n"
            r"\s*Z:\s*(-?\d+\.\d+)\s*$", text, re.M):
        doc_triples.add(tuple(round(float(m.group(i)), 3) for i in (1, 2, 3)))

    lines, missing = [], []
    for t in sorted(doc_triples):
        hit = t in upstream
        if not hit:
            missing.append(t)
        lines.append("    %-46s %s"
                     % ("%g, %g, %g" % t,
                        "in source" if hit else "NOT IN ANY SOURCE"))
    lines.append("    %d/%d triples traced to a source file"
                 % (len(doc_triples) - len(missing), len(doc_triples)))
    return (not missing), lines, missing


def coord_trace_probe(text, corpora):
    """Confirm the trace reacts: fake a coordinate and expect a failure."""
    probe = text.replace(", ", ", 9", 1) if ", " in text else text
    ok, _, _ = coord_trace(probe, corpora)
    return not ok


def gh_gist(gist_id, filename):
    """Return the decoded text of a gist file via the gh CLI."""
    result = subprocess.run(
        ["gh", "api", "gists/%s" % gist_id,
         "--jq", '.files["%s"].content' % filename],
        capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("gh api gist %s failed: %s"
                           % (gist_id, result.stderr.strip()))
    return result.stdout
