#!/usr/bin/env python3
"""
VEIL-ATLAS synthetic dataset inspector.

Prints a human-readable summary of the corpus: entity counts, per-persona
activity, source distribution, post-length statistics, the case list and the
evaluation pairs grouped by ground-truth label.

    python data/synthetic/inspect_dataset.py
"""

import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return json.load(fh)


def rule(title):
    print("\n" + title)
    print("-" * len(title))


def main():
    actors = load("actors.json")
    personas = load("personas.json")
    posts = load("posts.json")
    sources = load("sources.json")
    identifiers = load("identifiers.json")
    infra = load("infrastructure.json")
    services = load("hidden_services.json")
    clearnet = load("clearnet_assets.json")
    relationships = load("relationships.json")
    events = load("timeline_events.json")
    evidence = load("evidence.json")
    cases = load("cases.json")
    pairs = load("evaluation_pairs.json")
    truth = load("evaluation_ground_truth.json")
    manifest = load("dataset_manifest.json")

    handle = {p["persona_id"]: p["handle"] for p in personas}
    source_name = {s["source_id"]: s["source_name"] for s in sources}

    print("=" * 78)
    print("%s  v%s" % (manifest["dataset_name"], manifest["dataset_version"]))
    print("=" * 78)
    print(manifest["safety_statement"])

    rule("COUNTS")
    for label, value in (
            ("actors (ground truth)", len(actors)),
            ("personas", len(personas)),
            ("sources", len(sources)),
            ("posts", len(posts)),
            ("identifiers", len(identifiers)),
            ("infrastructure indicators", len(infra)),
            ("hidden services", len(services)),
            ("clearnet assets", len(clearnet)),
            ("relationships", len(relationships)),
            ("timeline events", len(events)),
            ("evidence records", len(evidence)),
            ("investigation cases", len(cases)),
            ("evaluation pairs", len(pairs))):
        print("  %-28s %4d" % (label, value))
    print("  %-28s %s .. %s" % ("timeline",
                                manifest["timeline_start"][:10], manifest["timeline_end"][:10]))
    print("  %-28s %s" % ("last scan date", manifest["last_scan_date"][:10]))

    rule("TOP PERSONAS BY POST COUNT")
    counts = Counter(p["persona_id"] for p in posts)
    for pid, n in counts.most_common():
        p = next(x for x in personas if x["persona_id"] == pid)
        print("  %-14s %-16s %3d posts  %s .. %s  [%s]  %s"
              % (pid, handle[pid], n, p["first_seen"][:10], p["last_seen"][:10],
                 ",".join(p["source_ids"]), p["status"]))

    rule("SOURCE DISTRIBUTION")
    per_source = Counter(p["source_id"] for p in posts)
    for s in sources:
        print("  %-8s %-14s %-22s %-7s %.2f  %4d posts"
              % (s["source_id"], s["source_name"], s["source_type"],
                 s["reliability"], s["reliability_score"], per_source.get(s["source_id"], 0)))

    rule("POST LENGTH STATISTICS (words)")
    lengths = sorted(p["word_count"] for p in posts)
    n = len(lengths)
    print("  min %d / median %d / mean %.1f / max %d"
          % (lengths[0], lengths[n // 2], sum(lengths) / float(n), lengths[-1]))
    print("  very short (<= 6 words): %d" % sum(1 for x in lengths if x <= 6))
    print("  medium (7-25 words):     %d" % sum(1 for x in lengths if 7 <= x <= 25))
    print("  long (> 25 words):       %d" % sum(1 for x in lengths if x > 25))

    rule("IDENTIFIERS BY TYPE")
    for k, v in sorted(Counter(i["identifier_type"] for i in identifiers).items()):
        print("  %-20s %3d" % (k, v))
    reuse = defaultdict(set)
    for i in identifiers:
        reuse[(i["identifier_type"], i["value"])].add(i["associated_persona"])
    shared = {k: v for k, v in reuse.items() if len(v) > 1}
    print("  values observed for more than one persona: %d" % len(shared))
    for (itype, value), pset in sorted(shared.items()):
        print("    %-16s %-34s %s" % (itype, value, ", ".join(sorted(pset))))

    rule("INFRASTRUCTURE")
    for k, v in sorted(Counter(r["indicator_type"] for r in infra).items()):
        print("  %-36s %3d" % (k, v))
    print("  services: %d, clearnet assets: %d" % (len(services), len(clearnet)))
    for s in services:
        print("    %-12s %-22s %2d indicators  personas: %s"
              % (s["service_id"], s["service_label"], len(s["infrastructure_indicators"]),
                 ", ".join(s["associated_personas"])))

    rule("RELATIONSHIPS BY TYPE")
    for k, v in sorted(Counter(r["relationship_type"] for r in relationships).items()):
        print("  %-28s %3d" % (k, v))
    print("  by evidence class: %s"
          % dict(Counter(r["evidence_class"] for r in relationships)))

    rule("TIMELINE EVENTS BY TYPE")
    for k, v in sorted(Counter(e["event_type"] for e in events).items()):
        print("  %-28s %3d" % (k, v))

    rule("EVIDENCE LEDGER")
    for k, v in sorted(Counter(e["evidence_class"] for e in evidence).items()):
        print("  %-28s %3d" % (k, v))

    rule("INVESTIGATION CASES")
    for c in cases:
        print("  %-10s [%s] %s" % (c["case_id"], c["priority"], c["title"]))
        print("             entities: %s" % ", ".join(c["target_entities"]))
        print("             window:   %s .. %s"
              % (c["timeline_window"][0][:10], c["timeline_window"][1][:10]))

    rule("EVALUATION PAIRS BY GROUND-TRUTH LABEL")
    grouped = defaultdict(list)
    for p in pairs:
        grouped[p["relationship_ground_truth"]].append(p)
    for label in ("SAME_ACTOR", "DIFFERENT_ACTOR", "AMBIGUOUS",
                  "SAME_TOPIC_DIFFERENT_STYLE", "DIFFERENT_TOPIC_SIMILAR_STYLE", "UNRELATED"):
        plist = grouped.get(label, [])
        print("\n  %s  (%d)" % (label, len(plist)))
        for p in plist:
            print("    %-9s %-14s <-> %-14s  style=%-12s temporal=%-12s ident=%-8s infra=%-8s -> %s"
                  % (p["pair_id"], handle[p["account_a"]], handle[p["account_b"]],
                     p["stylometric_expectation"], p["temporal_expectation"],
                     p["identifier_expectation"], p["infrastructure_expectation"],
                     p["expected_evidence_strength"]))

    rule("SCENARIO COVERAGE (evaluation)")
    for sid, refs in sorted(truth["scenario_coverage"].items()):
        print("  %-12s %-2d  %s" % (sid, len(refs), truth["scenarios"][sid]))

    rule("GROUND-TRUTH ACTOR CATALOGUE (evaluation / dashboard reference only)")
    for a in actors:
        print("  %-10s %-16s %-20s risk=%-7s personas=%d  sources=%s"
              % (a["actor_id"], a["display_name"], a["primary_category"],
                 a["risk_level"], a["persona_count"], ",".join(a["known_sources"])))
        print("             %s" % ", ".join("%s (%s)" % (p, handle[p]) for p in a["known_personas"]))

    rule("MIGRATIONS (ground truth)")
    for m in truth["migrations"]:
        print("  %-9s %-10s %-14s -> %-14s gap=%2dd  %s"
              % (m["migration_id"], m["actor_id"], handle[m["from_persona"]],
                 handle[m["to_persona"]], m["gap_days"], m["migration_type"]))

    print("\nSource name reference: %s" % ", ".join(
        "%s=%s" % (k, v) for k, v in sorted(source_name.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
