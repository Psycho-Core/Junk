#!/usr/bin/env python3
"""Shared helpers for the arena document audits.

The source cross-check pulls the upstream file a number came from and
verifies the exact literal is present there, so an audit is not only a
self-consistent string check on the document being audited.
"""

import base64
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
