#!/usr/bin/env python3
"""
VEIL-ATLAS synthetic dataset validator.

Checks structural consistency, referential integrity, timestamp sanity,
production/evaluation separation (no ground-truth leakage) and the safety
constraints that keep every value in this corpus obviously synthetic.

    python data/synthetic/validate_dataset.py

Exit code 0 = valid, non-zero = invalid. Writes dataset_validation_report.json.
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))

ERRORS = []
WARNINGS = []


def err(rule, message):
    ERRORS.append({"rule": rule, "message": message})


def warn(rule, message):
    WARNINGS.append({"rule": rule, "message": message})


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
# file inventory
# --------------------------------------------------------------------------
REQUIRED_FILES = [
    "actors.json", "personas.json", "posts.json", "sources.json", "identifiers.json",
    "infrastructure.json", "hidden_services.json", "clearnet_assets.json",
    "relationships.json", "timeline_events.json", "evidence.json", "cases.json",
    "evaluation_pairs.json", "evaluation_ground_truth.json", "dataset_manifest.json",
]

# Files consumed by the inference chain (P2/P3/P4). Ground truth must never appear here.
INFERENCE_INPUT_FILES = [
    "personas.json", "posts.json", "sources.json", "identifiers.json",
    "infrastructure.json", "hidden_services.json", "clearnet_assets.json",
    "relationships.json", "timeline_events.json", "evidence.json", "cases.json",
]

GROUND_TRUTH_KEYS = {
    "actor_id", "actor_ground_truth", "ground_truth_actor_id", "ground_truth",
    "true_actor", "expected_relationship", "relationship_ground_truth",
    "expected_evidence_strength", "expected_final_assessment", "style_archetype",
    "writing_style_profile", "idiolect_markers", "behaviour_profile", "label",
    "persona_to_actor", "post_to_actor",
}

# --------------------------------------------------------------------------
# safety patterns
# --------------------------------------------------------------------------
ONION_RE = re.compile(r"\.onion\b", re.I)
BTC_RE = re.compile(r"\b(?:bc1[a-z0-9]{25,62}|[13][a-km-zA-HJ-NP-Z1-9]{25,39})\b")
XMR_RE = re.compile(r"\b4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}\b")
ETH_RE = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
PGP_FP_RE = re.compile(r"\b[A-F0-9]{16,40}\b")
EMAIL_RE = re.compile(r"\b[\w.\-+]+@[\w.\-]+\.[A-Za-z]{2,}\b")
DOMAIN_RE = re.compile(r"\b[a-z0-9][a-z0-9\-]*(?:\.[a-z0-9\-]+)+\b", re.I)

ALLOWED_DOMAIN_SUFFIXES = (".synthetic", ".synthetic.example")
ALLOWED_EMAIL_SUFFIX = "@synthetic.example"

TIMELINE_LOW = datetime(2026, 5, 25, tzinfo=timezone.utc)
TIMELINE_HIGH = datetime(2026, 8, 31, tzinfo=timezone.utc)

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

# Deliberate negative-control records that are allowed to have no counterpart.
ALLOWED_ORPHANS = {"CLEAR-005"}


def parse_ts(value):
    if not isinstance(value, str) or not ISO_RE.match(value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def walk(node, path=""):
    """Yield (path, key, value) for every scalar in a nested structure."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, "%s.%s" % (path, k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, "%s[%d]" % (path, i))
    else:
        yield path, node


def iter_keys(node):
    if isinstance(node, dict):
        for k, v in node.items():
            yield k
            yield from iter_keys(v)
    elif isinstance(node, list):
        for v in node:
            yield from iter_keys(v)


def check_ids(name, records, key):
    seen = Counter(r[key] for r in records)
    dupes = [k for k, v in seen.items() if v > 1]
    if dupes:
        err("R11-16", "%s contains duplicate %s values: %s" % (name, key, dupes[:5]))
    return set(seen)


def check_window(name, rec, id_key, first="first_seen", last="last_seen"):
    a, b = rec.get(first), rec.get(last)
    if a is None or b is None:
        return
    ta, tb = parse_ts(a), parse_ts(b)
    if ta is None:
        err("R8", "%s %s has invalid %s: %r" % (name, rec.get(id_key), first, a))
        return
    if tb is None:
        err("R8", "%s %s has invalid %s: %r" % (name, rec.get(id_key), last, b))
        return
    if ta > tb:
        err("R9", "%s %s has %s after %s (%s > %s)" % (name, rec.get(id_key), first, last, a, b))


def main():
    # ---------------------------------------------------------------- files
    for f in REQUIRED_FILES:
        if not os.path.exists(os.path.join(HERE, f)):
            err("R0", "missing required file: %s" % f)
    if ERRORS:
        return finish({})

    data = {f: load(f) for f in REQUIRED_FILES}

    actors = data["actors.json"]
    personas = data["personas.json"]
    posts = data["posts.json"]
    sources = data["sources.json"]
    identifiers = data["identifiers.json"]
    infra = data["infrastructure.json"]
    services = data["hidden_services.json"]
    clearnet = data["clearnet_assets.json"]
    relationships = data["relationships.json"]
    events = data["timeline_events.json"]
    evidence = data["evidence.json"]
    cases = data["cases.json"]
    pairs = data["evaluation_pairs.json"]
    truth = data["evaluation_ground_truth.json"]
    manifest = data["dataset_manifest.json"]

    # ------------------------------------------------------- ids / duplicates
    persona_ids = check_ids("personas.json", personas, "persona_id")
    post_ids = check_ids("posts.json", posts, "post_id")
    source_ids = check_ids("sources.json", sources, "source_id")
    ident_ids = check_ids("identifiers.json", identifiers, "identifier_id")
    infra_ids = check_ids("infrastructure.json", infra, "indicator_id")
    service_ids = check_ids("hidden_services.json", services, "service_id")
    clear_ids = check_ids("clearnet_assets.json", clearnet, "clearnet_asset_id")
    rel_ids = check_ids("relationships.json", relationships, "relationship_id")
    event_ids = check_ids("timeline_events.json", events, "event_id")
    evid_ids = check_ids("evidence.json", evidence, "evidence_id")
    case_ids = check_ids("cases.json", cases, "case_id")
    pair_ids = check_ids("evaluation_pairs.json", pairs, "pair_id")
    actor_ids = check_ids("actors.json", actors, "actor_id")

    all_entities = (persona_ids | source_ids | ident_ids | infra_ids | service_ids
                    | clear_ids | post_ids | rel_ids | evid_ids | event_ids)

    # ------------------------------------------------- R1-R7 referential checks
    for p in posts:
        if p["persona_id"] not in persona_ids:
            err("R2", "post %s references unknown persona %s" % (p["post_id"], p["persona_id"]))
        if p["source_id"] not in source_ids:
            err("R3", "post %s references unknown source %s" % (p["post_id"], p["source_id"]))

    for i in identifiers:
        if i["associated_persona"] not in persona_ids:
            err("R4", "identifier %s references unknown persona %s"
                % (i["identifier_id"], i["associated_persona"]))
        if i["source_id"] not in source_ids:
            err("R3", "identifier %s references unknown source %s"
                % (i["identifier_id"], i["source_id"]))

    for rec in infra:
        if rec["service_id"] not in service_ids:
            err("R5", "infrastructure %s references unknown service %s"
                % (rec["indicator_id"], rec["service_id"]))
        if rec["source_id"] not in source_ids:
            err("R3", "infrastructure %s references unknown source %s"
                % (rec["indicator_id"], rec["source_id"]))
        for ref in rec.get("clearnet_asset_refs", []):
            if ref not in clear_ids:
                err("R5", "infrastructure %s references unknown clearnet asset %s"
                    % (rec["indicator_id"], ref))

    for s in services:
        for pid in s["associated_personas"]:
            if pid not in persona_ids:
                err("R1", "service %s references unknown persona %s" % (s["service_id"], pid))
        for ind in s["infrastructure_indicators"]:
            if ind not in infra_ids:
                err("R5", "service %s references unknown indicator %s" % (s["service_id"], ind))
        if s["synthetic_domain_relation"] and s["synthetic_domain_relation"] not in clear_ids:
            err("R5", "service %s references unknown clearnet asset %s"
                % (s["service_id"], s["synthetic_domain_relation"]))
        if s["source_id"] not in source_ids:
            err("R3", "service %s references unknown source %s" % (s["service_id"], s["source_id"]))

    for a in clearnet:
        if a["source_id"] not in source_ids:
            err("R3", "clearnet asset %s references unknown source %s"
                % (a["clearnet_asset_id"], a["source_id"]))

    for r in relationships:
        for side in ("source_entity", "target_entity"):
            if r[side] not in all_entities:
                err("R6", "relationship %s references unknown entity %s"
                    % (r["relationship_id"], r[side]))
        if r["source_id"] not in source_ids:
            err("R3", "relationship %s references unknown source %s"
                % (r["relationship_id"], r["source_id"]))
        for ref in r["evidence_refs"]:
            if ref not in all_entities:
                err("R6", "relationship %s references unknown evidence ref %s"
                    % (r["relationship_id"], ref))
        if r["evidence_class"] not in ("FACT", "INFERENCE", "HYPOTHESIS"):
            err("R6", "relationship %s has invalid evidence_class %s"
                % (r["relationship_id"], r["evidence_class"]))
        if r["relationship_type"] in ("POSSIBLE_SAME_ACTOR", "SHARES_IDENTIFIER",
                                      "SHARES_INFRASTRUCTURE") and r["evidence_class"] == "FACT":
            err("R6", "relationship %s marks a probabilistic link as a FACT" % r["relationship_id"])

    for e in events:
        if e["persona_id"] and e["persona_id"] not in persona_ids:
            err("R7", "event %s references unknown persona %s" % (e["event_id"], e["persona_id"]))
        if e["entity_id"] and e["entity_id"] not in all_entities:
            err("R7", "event %s references unknown entity %s" % (e["event_id"], e["entity_id"]))
        if e["source_id"] and e["source_id"] not in source_ids:
            err("R3", "event %s references unknown source %s" % (e["event_id"], e["source_id"]))
        for ref in e["evidence_reference"]:
            if ref not in all_entities:
                err("R7", "event %s references unknown evidence ref %s" % (e["event_id"], ref))

    for ev in evidence:
        for ent in ev["entities"]:
            if ent not in all_entities:
                err("R6", "evidence %s references unknown entity %s" % (ev["evidence_id"], ent))
        for ref in ev["evidence_refs"]:
            if ref not in all_entities:
                err("R6", "evidence %s references unknown ref %s" % (ev["evidence_id"], ref))
        if ev["evidence_class"] not in ("FACT", "INFERENCE", "HYPOTHESIS"):
            err("R6", "evidence %s has invalid class %s" % (ev["evidence_id"], ev["evidence_class"]))

    for c in cases:
        for ent in c["target_entities"]:
            if ent not in all_entities:
                err("R6", "case %s references unknown entity %s" % (c["case_id"], ent))
        for pid in c["relevant_posts"]:
            if pid not in post_ids:
                err("R6", "case %s references unknown post %s" % (c["case_id"], pid))
        for iid in c["relevant_identifiers"]:
            if iid not in ident_ids:
                err("R6", "case %s references unknown identifier %s" % (c["case_id"], iid))
        for ind in c["relevant_infrastructure"]:
            if ind not in infra_ids:
                err("R6", "case %s references unknown indicator %s" % (c["case_id"], ind))
        for sid in c["relevant_sources"]:
            if sid not in source_ids:
                err("R3", "case %s references unknown source %s" % (c["case_id"], sid))
        for ref in c["evidence_refs"]:
            if ref not in evid_ids:
                err("R6", "case %s references unknown evidence %s" % (c["case_id"], ref))

    for pr in pairs:
        for side in ("account_a", "account_b"):
            if pr[side] not in persona_ids:
                err("R18", "evaluation pair %s references unknown persona %s"
                    % (pr["pair_id"], pr[side]))
        if pr["relationship_ground_truth"] not in (
                "SAME_ACTOR", "DIFFERENT_ACTOR", "SAME_TOPIC_DIFFERENT_STYLE",
                "DIFFERENT_TOPIC_SIMILAR_STYLE", "AMBIGUOUS", "UNRELATED"):
            err("R18", "evaluation pair %s has invalid label %s"
                % (pr["pair_id"], pr["relationship_ground_truth"]))
        if pr["expected_evidence_strength"] not in (
                "HIGH_EXPECTED", "MEDIUM_EXPECTED", "LOW_EXPECTED", "INSUFFICIENT"):
            err("R18", "evaluation pair %s has invalid expected strength %s"
                % (pr["pair_id"], pr["expected_evidence_strength"]))

    for a in actors:
        for pid in a["known_personas"]:
            if pid not in persona_ids:
                err("R6", "actor %s references unknown persona %s" % (a["actor_id"], pid))
        for iid in a["known_identifiers"]:
            if iid not in ident_ids:
                err("R6", "actor %s references unknown identifier %s" % (a["actor_id"], iid))
        for sid in a["known_infrastructure"]:
            if sid not in service_ids:
                err("R6", "actor %s references unknown service %s" % (a["actor_id"], sid))

    # ground-truth files must cover every persona exactly once
    if set(truth["persona_to_actor"]) != persona_ids:
        err("R19", "evaluation_ground_truth.persona_to_actor does not cover every persona")
    if set(truth["persona_to_actor"].values()) - actor_ids:
        err("R19", "evaluation_ground_truth references unknown actors")
    if set(truth["post_to_actor"]) != post_ids:
        err("R19", "evaluation_ground_truth.post_to_actor does not cover every post")

    # ------------------------------------------------- R8/R9/R10 timestamps
    for name, records, key in (
            ("posts.json", posts, "post_id"),
            ("personas.json", personas, "persona_id"),
            ("identifiers.json", identifiers, "identifier_id"),
            ("infrastructure.json", infra, "indicator_id"),
            ("hidden_services.json", services, "service_id"),
            ("clearnet_assets.json", clearnet, "clearnet_asset_id"),
            ("relationships.json", relationships, "relationship_id"),
            ("timeline_events.json", events, "event_id"),
            ("evidence.json", evidence, "evidence_id"),
            ("actors.json", actors, "actor_id")):
        for rec in records:
            check_window(name, rec, key)
            for field in ("timestamp", "observed_at", "last_scan_date", "scan_date",
                          "first_seen", "last_seen", "created_at"):
                if field in rec and rec[field] is not None:
                    ts = parse_ts(rec[field])
                    if ts is None:
                        err("R8", "%s %s has non ISO-8601 %s: %r"
                            % (name, rec.get(key), field, rec[field]))
                    elif not (TIMELINE_LOW <= ts <= TIMELINE_HIGH):
                        err("R8", "%s %s has %s outside the dataset timeline: %s"
                            % (name, rec.get(key), field, rec[field]))

    for rec in services + infra + identifiers + personas + actors:
        if not parse_ts(rec.get("last_scan_date", "")):
            err("R10", "record %s has an invalid or missing last_scan_date"
                % (rec.get("service_id") or rec.get("indicator_id") or rec.get("identifier_id")
                   or rec.get("persona_id") or rec.get("actor_id")))

    for c in cases:
        for value in c["timeline_window"]:
            if not parse_ts(value):
                err("R8", "case %s has an invalid timeline_window value %r" % (c["case_id"], value))

    # persona window must agree with its posts
    by_persona = defaultdict(list)
    for p in posts:
        by_persona[p["persona_id"]].append(p["timestamp"])
    for p in personas:
        stamps = sorted(by_persona.get(p["persona_id"], []))
        if not stamps:
            err("R17", "persona %s has no posts (orphan persona)" % p["persona_id"])
            continue
        if p["first_seen"] != stamps[0] or p["last_seen"] != stamps[-1]:
            err("R9", "persona %s first_seen/last_seen does not match its posts"
                % p["persona_id"])
        if p["post_count"] != len(stamps):
            err("R9", "persona %s post_count %d does not match %d posts"
                % (p["persona_id"], p["post_count"], len(stamps)))

    # ------------------------------------------------------- R17 orphan checks
    referenced_sources = ({p["source_id"] for p in posts}
                          | {i["source_id"] for i in identifiers}
                          | {r["source_id"] for r in relationships}
                          | {a["source_id"] for a in clearnet}
                          | {s["source_id"] for s in services})
    for s in sources:
        if s["source_id"] not in referenced_sources:
            warn("R17", "source %s is never referenced by any observation" % s["source_id"])

    ident_referenced = {i["associated_persona"] for i in identifiers}
    for p in personas:
        if p["persona_id"] not in ident_referenced:
            warn("R17", "persona %s has no identifier observations" % p["persona_id"])

    svc_with_indicators = {rec["service_id"] for rec in infra}
    for s in services:
        if s["service_id"] not in svc_with_indicators:
            err("R17", "service %s has no infrastructure indicators" % s["service_id"])

    infra_values = {rec["value"] for rec in infra}
    for a in clearnet:
        overlap = [v for v in a["observed_indicators"] if v in infra_values]
        if not overlap and a["clearnet_asset_id"] not in ALLOWED_ORPHANS:
            err("R17", "clearnet asset %s shares no indicator with any service and is not "
                       "declared a negative control" % a["clearnet_asset_id"])

    # ---------------------------------------------- R19 ground-truth leakage
    for fname in INFERENCE_INPUT_FILES:
        payload = data[fname]
        keys = set(iter_keys(payload))
        leaked = keys & GROUND_TRUTH_KEYS
        if leaked:
            err("R19", "%s exposes ground-truth key(s) %s to the inference chain"
                % (fname, sorted(leaked)))
        blob = json.dumps(payload)
        hits = set(re.findall(r"\bACTOR-\d{3}\b", blob))
        if hits:
            err("R19", "%s contains actor ground-truth identifiers: %s" % (fname, sorted(hits)[:5]))
        # \b so that the production hypothesis edge type POSSIBLE_SAME_ACTOR is not
        # mistaken for the evaluation label SAME_ACTOR
        for word in ("SAME_ACTOR", "DIFFERENT_ACTOR", "HIGH_EXPECTED", "MEDIUM_EXPECTED",
                     "LOW_EXPECTED", "INSUFFICIENT_EVIDENCE", "FALSE_POSITIVE_CANDIDATE",
                     "STRONG_POSITIVE", "WEAK_POSITIVE", "CONFLICTING_EVIDENCE",
                     "SAME_INFRASTRUCTURE", "POSSIBLE_SHARED_INFRASTRUCTURE"):
            if re.search(r"\b%s\b" % word, blob):
                err("R19", "%s contains evaluation vocabulary %r" % (fname, word))
        if "SCENARIO-" in blob:
            err("R19", "%s references an evaluation scenario id" % fname)

    if manifest.get("restricted_from_inference") != [
            "actors.json", "evaluation_pairs.json", "evaluation_ground_truth.json"]:
        err("R19", "dataset_manifest.restricted_from_inference does not list the ground-truth files")

    # ------------------------------------------------------ R20-R24 safety
    for fname in REQUIRED_FILES:
        blob = json.dumps(data[fname])
        if ONION_RE.search(blob):
            err("R22", "%s contains a .onion address" % fname)
        for rx, rule, what in ((BTC_RE, "R23", "bitcoin-like address"),
                               (XMR_RE, "R23", "monero-like address"),
                               (ETH_RE, "R23", "ethereum-like address"),
                               (PGP_FP_RE, "R20", "real-looking key fingerprint")):
            m = rx.search(blob)
            if m:
                err(rule, "%s contains a %s: %r" % (fname, what, m.group(0)[:24]))
        for email in set(EMAIL_RE.findall(blob)):
            if not email.endswith(ALLOWED_EMAIL_SUFFIX):
                err("R24", "%s contains a non-synthetic email address: %s" % (fname, email))
        for dom in set(DOMAIN_RE.findall(blob)):
            low = dom.lower()
            last_label = low.rsplit(".", 1)[-1]
            # ".synthetic" and the reserved ".example" TLD are the only permitted
            # network names; the remaining extensions are this dataset's own filenames.
            if last_label in ("synthetic", "example", "json", "md", "py", "csv"):
                continue
            if re.fullmatch(r"[\d.]+", low):
                continue
            err("R21", "%s contains a non-synthetic domain-like value: %s" % (fname, dom))

    for i in identifiers:
        v, t = i["value"], i["identifier_type"]
        if t == "pgp_fingerprint" and not v.startswith("FAKE-PGP-"):
            err("R20", "identifier %s: PGP value %r is not obviously synthetic" % (i["identifier_id"], v))
        if t == "wallet" and not v.startswith("SYN-WALLET-"):
            err("R20", "identifier %s: wallet value %r is not obviously synthetic" % (i["identifier_id"], v))
        if t == "email" and not v.endswith(ALLOWED_EMAIL_SUFFIX):
            err("R24", "identifier %s: email %r is not synthetic" % (i["identifier_id"], v))
        if not i.get("synthetic"):
            err("R20", "identifier %s is not flagged synthetic" % i["identifier_id"])

    for s in services:
        if not s["service_label"].startswith("synthetic-onion-"):
            err("R22", "service %s does not use a synthetic label" % s["service_id"])

    for rec in infra:
        if not (rec["value"].startswith("FAKE-") or rec["value"].endswith(".synthetic.example")):
            err("R20", "infrastructure %s value %r is not obviously synthetic"
                % (rec["indicator_id"], rec["value"]))

    if manifest.get("synthetic_only") is not True:
        err("R20", "dataset_manifest.synthetic_only is not true")

    # ------------------------------------------------------- provenance (R28)
    for name, records, key in (("posts.json", posts, "post_id"),
                               ("identifiers.json", identifiers, "identifier_id"),
                               ("infrastructure.json", infra, "indicator_id"),
                               ("relationships.json", relationships, "relationship_id"),
                               ("timeline_events.json", events, "event_id"),
                               ("evidence.json", evidence, "evidence_id")):
        for rec in records:
            for field in ("source_id", "collection_method", "reliability"):
                if not rec.get(field):
                    err("R28", "%s %s is missing %s" % (name, rec.get(key), field))

    # -------------------------------------------------- manifest count checks
    counts = {
        "total_actors": len(actors), "total_personas": len(personas), "total_posts": len(posts),
        "total_sources": len(sources), "total_identifiers": len(identifiers),
        "total_infrastructure_indicators": len(infra), "total_hidden_services": len(services),
        "total_clearnet_assets": len(clearnet), "total_relationships": len(relationships),
        "total_events": len(events), "total_evidence_records": len(evidence),
        "total_cases": len(cases), "total_evaluation_pairs": len(pairs),
    }
    for k, v in counts.items():
        if manifest.get(k) != v:
            err("R0", "manifest %s says %r but the data contains %d" % (k, manifest.get(k), v))

    # ------------------------------------------------------------ statistics
    lengths = [p["word_count"] for p in posts]
    lengths.sort()
    stats = {
        "counts": counts,
        "timeline": {
            "first_post": min(p["timestamp"] for p in posts),
            "last_post": max(p["timestamp"] for p in posts),
            "last_scan_date": manifest["last_scan_date"],
        },
        "pairwise_evaluation_counts": dict(Counter(p["relationship_ground_truth"] for p in pairs)),
        "pairwise_expected_strength": dict(Counter(p["expected_evidence_strength"] for p in pairs)),
        "scenario_coverage": {k: len(v) for k, v in truth["scenario_coverage"].items()},
        "source_reliability_distribution": dict(Counter(s["reliability"] for s in sources)),
        "posts_per_source": dict(Counter(p["source_id"] for p in posts)),
        "persona_distribution": dict(Counter(p["persona_id"] for p in posts)),
        "personas_per_actor": dict(Counter(truth["persona_to_actor"].values())),
        "identifier_type_distribution": dict(Counter(i["identifier_type"] for i in identifiers)),
        "infrastructure_type_distribution": dict(Counter(r["indicator_type"] for r in infra)),
        "relationship_type_distribution": dict(Counter(r["relationship_type"] for r in relationships)),
        "evidence_class_distribution": dict(Counter(e["evidence_class"] for e in evidence)),
        "event_type_distribution": dict(Counter(e["event_type"] for e in events)),
        "post_length_distribution": {
            "min_words": lengths[0],
            "median_words": lengths[len(lengths) // 2],
            "max_words": lengths[-1],
            "mean_words": round(sum(lengths) / float(len(lengths)), 2),
            "very_short_posts_max_6_words": sum(1 for x in lengths if x <= 6),
            "medium_posts_7_to_25_words": sum(1 for x in lengths if 7 <= x <= 25),
            "long_posts_over_25_words": sum(1 for x in lengths if x > 25),
        },
    }
    return finish(stats)


def finish(stats):
    status = "VALID" if not ERRORS else "INVALID"
    report = {
        "validation_status": status,
        "validated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "error_count": len(ERRORS),
        "warning_count": len(WARNINGS),
        "errors": ERRORS,
        "warnings": WARNINGS,
        "statistics": stats,
    }
    with open(os.path.join(HERE, "dataset_validation_report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print("VEIL-ATLAS dataset validation: %s" % status)
    print("  errors:   %d" % len(ERRORS))
    print("  warnings: %d" % len(WARNINGS))
    for e in ERRORS[:40]:
        print("  ERROR [%s] %s" % (e["rule"], e["message"]))
    for w in WARNINGS[:20]:
        print("  WARN  [%s] %s" % (w["rule"], w["message"]))
    print("  report written to dataset_validation_report.json")
    return 0 if not ERRORS else 1


if __name__ == "__main__":
    sys.exit(main())
