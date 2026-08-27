#!/usr/bin/env python3
"""
VEIL-ATLAS synthetic dataset generator.

Builds the complete synthetic corpus under data/synthetic/ from the designed
world in generator/world.py. Fully deterministic: the same seed always produces
byte-identical output.

    python data/synthetic/generate_dataset.py

EVERYTHING PRODUCED BY THIS SCRIPT IS FICTIONAL. It is not, and must never be
presented as, real threat intelligence.
"""

import json
import os
import random
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from generator import world as W  # noqa: E402
from generator import textgen as T  # noqa: E402

OUT = HERE
GENERATED_AT = "2026-08-27T00:00:00Z"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def d(datestr):
    return datetime.strptime(datestr, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def iso_date(datestr):
    return d(datestr).strftime("%Y-%m-%dT00:00:00Z")


TL_START = d(W.TIMELINE_START)
TL_END = d(W.TIMELINE_END) + timedelta(hours=23, minutes=59)
SCAN_REF = d(W.SCAN_REFERENCE_DATE)


def day_ok(day, pattern):
    if pattern == "weekdays":
        return day.weekday() < 5
    if pattern == "weekends":
        return day.weekday() >= 5
    return True


def candidate_days(persona):
    start, end = d(persona["window"][0]), d(persona["window"][1])
    days, cur = [], start
    while cur <= end:
        if day_ok(cur, persona["days"]):
            days.append(cur)
        cur += timedelta(days=1)
    return days


def gen_timestamps(rng, persona):
    """Distribute n_posts across the persona's active window using its cadence."""
    days = candidate_days(persona)
    n = persona["n_posts"]
    cadence = persona["cadence"]
    picked = []

    if cadence == "bursty":
        n_bursts = max(3, n // 5)
        burst_days = sorted(rng.sample(days, min(n_bursts, len(days))))
        for i in range(n):
            base = burst_days[i % len(burst_days)]
            picked.append(base + timedelta(days=rng.randint(0, 1)))
    elif cadence == "sparse":
        picked = sorted(rng.sample(days, min(n, len(days))))
        while len(picked) < n:
            picked.append(rng.choice(days))
    else:  # steady
        if n <= len(days):
            step = len(days) / float(n)
            for i in range(n):
                idx = int(i * step) + rng.randint(0, max(0, int(step) - 1))
                picked.append(days[min(idx, len(days) - 1)])
        else:
            for i in range(n):
                picked.append(days[i % len(days)])

    stamps = []
    for day in picked:
        hour = rng.choice(persona["hours"])
        ts = day + timedelta(hours=hour, minutes=rng.randrange(0, 60), seconds=rng.randrange(0, 60))
        # keep the first and last day inside the declared window
        ts = max(TL_START, min(ts, TL_END))
        stamps.append(ts)
    stamps.sort()
    # force exact window endpoints so first_seen/last_seen match the design
    first_day, last_day = d(persona["window"][0]), d(persona["window"][1])
    stamps[0] = first_day + timedelta(hours=rng.choice(persona["hours"]), minutes=rng.randrange(0, 60))
    stamps[-1] = last_day + timedelta(hours=rng.choice(persona["hours"]), minutes=rng.randrange(0, 60))
    stamps.sort()
    return stamps


def source_for_post(persona, ts, rng):
    """Which source a given post lands on (multi-source personas only)."""
    pid = persona["persona_id"]
    if pid == "PERSONA-004":
        return "SRC-001" if (ts >= d("2026-07-26") and rng.random() < 0.35) else "SRC-003"
    if pid == "PERSONA-005":
        if ts >= d(persona["second_source_from"]):
            return "SRC-004" if rng.random() < 0.45 else "SRC-003"
        return "SRC-003"
    if pid == "PERSONA-010":
        return "SRC-002" if rng.random() < 0.4 else "SRC-001"
    if pid == "PERSONA-012":
        return "SRC-007" if rng.random() < 0.2 else "SRC-004"
    return persona["primary_source"]


def src(sid):
    return W.SOURCE_BY_ID[sid]


# --------------------------------------------------------------------------
# 1. POSTS
# --------------------------------------------------------------------------
def build_posts():
    raw = []
    for idx, p in enumerate(W.PERSONAS):
        rng = random.Random(W.SEED + idx * 101)
        actor = W.ACTOR_BY_ID[p["actor"]]
        stamps = gen_timestamps(rng, p)
        types = W.textgen_types = T.POST_TYPES_BY_CATEGORY[p["category"]]
        thread_pool = ["THREAD-%s-%02d" % (p["persona_id"].split("-")[1], i) for i in range(1, 7)]
        for i, ts in enumerate(stamps):
            ptype = rng.choice(types)
            if p["announced_migration"] and i == len(stamps) - 1:
                ptype = "migration_notice"
            text = T.make_post_text(rng, p["style"], p["category"], ptype,
                                    actor["idiolect"], actor["connective"],
                                    variant=int(p["persona_id"].split("-")[1]))
            sid = source_for_post(p, ts, rng)
            raw.append({
                "_ts": ts,
                "persona_id": p["persona_id"],
                "source_id": sid,
                "text": text,
                "category": p["category"],
                "post_type": ptype,
                "thread_id": rng.choice(thread_pool),
                "actor": p["actor"],
            })
    raw.sort(key=lambda r: (r["_ts"], r["persona_id"]))

    posts, post_truth = [], {}
    for i, r in enumerate(raw, start=1):
        s = src(r["source_id"])
        pid = "POST-%04d" % i
        posts.append({
            "post_id": pid,
            "persona_id": r["persona_id"],
            "source_id": r["source_id"],
            "thread_id": r["thread_id"],
            "timestamp": iso(r["_ts"]),
            "text": r["text"],
            "category": r["category"],
            "language": "en",
            "post_type": r["post_type"],
            "word_count": T.word_count(r["text"]),
            "char_count": len(r["text"]),
            "observed_at": iso(r["_ts"] + timedelta(hours=6)),
            "collection_method": s["collection_method"],
            "reliability": s["reliability"],
            "reliability_score": s["reliability_score"],
        })
        post_truth[pid] = r["actor"]
    return posts, post_truth


# --------------------------------------------------------------------------
# 2. IDENTIFIERS
# --------------------------------------------------------------------------
def mask(value, itype):
    if itype in ("pgp_fingerprint", "wallet") and len(value) > 12:
        return value[:10] + "…" + value[-3:]
    if itype == "email":
        name, _, domain = value.partition("@")
        return name[:3] + "…@" + domain
    return value


def build_identifiers():
    identifiers, truth = [], {}
    for i, (itype, value, persona, source, fs, ls, status) in enumerate(W.IDENTIFIER_PLAN, start=1):
        s = src(source)
        iid = "IDENT-%03d" % i
        identifiers.append({
            "identifier_id": iid,
            "identifier_type": itype,
            "value": value,
            "display_value": mask(value, itype),
            "associated_persona": persona,
            "source_id": source,
            "first_seen": iso_date(fs),
            "last_seen": iso_date(ls),
            "observed_at": iso_date(fs),
            "last_scan_date": iso_date(W.SCAN_REFERENCE_DATE),
            "status": status,
            "collection_method": s["collection_method"],
            "reliability": s["reliability"],
            "reliability_score": s["reliability_score"],
            "synthetic": True,
        })
        truth[iid] = W.PERSONA_BY_ID[persona]["actor"]
    return identifiers, truth


# --------------------------------------------------------------------------
# 3. INFRASTRUCTURE + SERVICES + CLEARNET
# --------------------------------------------------------------------------
def build_infrastructure():
    rng = random.Random(W.SEED + 7)
    infra = []
    svc_first = {s["service_id"]: d(s["first_seen"]) for s in W.HIDDEN_SERVICES}
    for i, (svc, itype, value, conf, rel) in enumerate(W.INFRA_PLAN, start=1):
        observed = svc_first[svc] + timedelta(days=rng.randint(0, 20), hours=rng.randint(0, 23))
        observed = min(observed, d("2026-08-25"))
        infra.append({
            "indicator_id": "INFRA-%03d" % i,
            "service_id": svc,
            "indicator_type": itype,
            "value": value,
            "observed_at": iso(observed),
            "first_seen": iso(observed),
            "last_seen": iso(min(observed + timedelta(days=rng.randint(20, 60)), d("2026-08-25"))),
            "last_scan_date": iso_date(W.SCAN_REFERENCE_DATE),
            "source_id": "SRC-007",
            "collection_method": "synthetic_service_scan",
            "confidence": conf,
            "reliability": conf,
            "reliability_score": rel,
            "synthetic": True,
        })

    # clearnet cross-references, computed from shared indicator values
    by_value = {}
    for rec in infra:
        by_value.setdefault(rec["value"], []).append(rec["indicator_id"])
    for asset in W.CLEARNET_ASSETS:
        for rec in infra:
            if rec["value"] in asset["observed_indicators"]:
                rec.setdefault("clearnet_asset_refs", []).append(asset["clearnet_asset_id"])
    for rec in infra:
        rec.setdefault("clearnet_asset_refs", [])
    return infra


def build_services(infra):
    by_service = {}
    for rec in infra:
        by_service.setdefault(rec["service_id"], []).append(rec["indicator_id"])
    services = []
    for s in W.HIDDEN_SERVICES:
        services.append({
            "service_id": s["service_id"],
            "service_label": s["service_label"],
            "service_name": s["service_name"],
            "first_seen": iso_date(s["first_seen"]),
            "last_seen": iso_date(s["last_seen"]),
            "status": s["status"],
            "infrastructure_indicators": by_service.get(s["service_id"], []),
            "associated_personas": s["personas"],
            "source_id": s["source_id"],
            "scan_date": iso_date(W.SCAN_REFERENCE_DATE),
            "last_scan_date": iso_date(W.SCAN_REFERENCE_DATE),
            "synthetic_domain_relation": s["synthetic_domain_relation"],
            "collection_method": "synthetic_service_scan",
            "reliability": src(s["source_id"])["reliability"],
            "reliability_score": src(s["source_id"])["reliability_score"],
        })
    return services


def build_clearnet():
    assets = []
    for a in W.CLEARNET_ASSETS:
        s = src(a["source_id"])
        assets.append({
            "clearnet_asset_id": a["clearnet_asset_id"],
            "hostname": a["hostname"],
            "certificate_fingerprint": a["certificate_fingerprint"],
            "observed_indicators": a["observed_indicators"],
            "source_id": a["source_id"],
            "first_seen": iso_date(a["first_seen"]),
            "last_seen": iso_date(a["last_seen"]),
            "observed_at": iso_date(a["first_seen"]),
            "last_scan_date": iso_date(W.SCAN_REFERENCE_DATE),
            "collection_method": s["collection_method"],
            "reliability": s["reliability"],
            "reliability_score": s["reliability_score"],
            "notes": a["notes"],
            "synthetic": True,
        })
    return assets


# --------------------------------------------------------------------------
# 4. PERSONAS (production view - no actor, no style profile)
# --------------------------------------------------------------------------
def build_personas(posts, identifiers, services):
    counts, firsts, lasts, srcs = {}, {}, {}, {}
    for p in posts:
        pid = p["persona_id"]
        counts[pid] = counts.get(pid, 0) + 1
        ts = p["timestamp"]
        firsts[pid] = min(firsts.get(pid, ts), ts)
        lasts[pid] = max(lasts.get(pid, ts), ts)
        srcs.setdefault(pid, set()).add(p["source_id"])

    ident_by_persona = {}
    for i in identifiers:
        ident_by_persona.setdefault(i["associated_persona"], []).append(i["identifier_id"])
    svc_by_persona = {}
    for s in services:
        for pid in s["associated_personas"]:
            svc_by_persona.setdefault(pid, []).append(s["service_id"])

    migration_notice = {}
    for p in posts:
        if p["post_type"] == "migration_notice":
            migration_notice[p["persona_id"]] = p["post_id"]

    out = []
    for p in W.PERSONAS:
        pid = p["persona_id"]
        out.append({
            "persona_id": pid,
            "handle": p["handle"],
            "source_ids": sorted(srcs.get(pid, {p["primary_source"]})),
            "primary_source_id": p["primary_source"],
            "primary_category": p["category"],
            "first_seen": firsts[pid],
            "last_seen": lasts[pid],
            "last_scan_date": iso_date(W.SCAN_REFERENCE_DATE),
            "status": p["status"],
            "post_count": counts[pid],
            "observed_identifier_ids": sorted(ident_by_persona.get(pid, [])),
            "observed_service_ids": sorted(svc_by_persona.get(pid, [])),
            "announced_migration": p["announced_migration"],
            "migration_notice_post_id": migration_notice.get(pid),
            "collection_method": src(p["primary_source"])["collection_method"],
            "reliability": src(p["primary_source"])["reliability"],
            "reliability_score": src(p["primary_source"])["reliability_score"],
        })
    return out


# --------------------------------------------------------------------------
# 5. RELATIONSHIPS (production - observable layer only, no ACTOR nodes)
# --------------------------------------------------------------------------
def build_relationships(personas, identifiers, infra, services, clearnet, posts):
    rels = []
    n = [0]

    def add(src_e, src_t, tgt_e, tgt_t, rtype, fs, ls, refs, source_id, cls, note=""):
        n[0] += 1
        s = src(source_id)
        rels.append({
            "relationship_id": "REL-%03d" % n[0],
            "source_entity": src_e,
            "source_entity_type": src_t,
            "target_entity": tgt_e,
            "target_entity_type": tgt_t,
            "relationship_type": rtype,
            "evidence_class": cls,          # FACT | INFERENCE | HYPOTHESIS
            "first_seen": fs,
            "last_seen": ls,
            "evidence_refs": refs,
            "source_id": source_id,
            "collection_method": s["collection_method"],
            "reliability": s["reliability"],
            "reliability_score": s["reliability_score"],
            "note": note,
        })

    persona_map = {p["persona_id"]: p for p in personas}

    # --- FACT edges: persona -> identifier ---
    seen_pairs = set()
    for i in identifiers:
        key = (i["associated_persona"], i["identifier_type"], i["value"])
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        rtype = {
            "handle": "USES_HANDLE",
            "pgp_fingerprint": "USES_PGP",
            "wallet": "USES_WALLET",
        }.get(i["identifier_type"], "USES_IDENTIFIER")
        if i["identifier_type"] == "alias":
            continue  # aliases stay as identifier records only, to keep the graph readable
        add(i["associated_persona"], "PERSONA", i["identifier_id"], "IDENTIFIER", rtype,
            i["first_seen"], i["last_seen"], [i["identifier_id"]], i["source_id"], "FACT")

    # --- FACT edges: persona -> source ---
    posted = {}
    for p in posts:
        posted.setdefault((p["persona_id"], p["source_id"]), []).append(p)
    for (pid, sid), plist in sorted(posted.items()):
        ts = sorted(x["timestamp"] for x in plist)
        add(pid, "PERSONA", sid, "SOURCE", "POSTED_ON", ts[0], ts[-1],
            [x["post_id"] for x in plist[:3]], sid, "FACT",
            "%d posts observed" % len(plist))

    # --- FACT edges: persona -> service ---
    for s in services:
        for pid in s["associated_personas"]:
            add(pid, "PERSONA", s["service_id"], "SERVICE", "ASSOCIATED_WITH_SERVICE",
                s["first_seen"], s["last_seen"], s["infrastructure_indicators"][:3],
                s["source_id"], "FACT")

    # --- FACT edges: service -> collecting source ---
    # (service -> indicator membership is already carried by hidden_services.infrastructure_indicators,
    #  so it is not duplicated as edges here)
    for s in services:
        add(s["service_id"], "SERVICE", s["source_id"], "SOURCE", "OBSERVED_BY",
            s["first_seen"], s["last_seen"], s["infrastructure_indicators"][:3],
            s["source_id"], "FACT", "Service catalogued by a synthetic service scan")

    # --- INFERENCE edges: two personas observed using the same identifier value ---
    by_value = {}
    for i in identifiers:
        if i["identifier_type"] in ("pgp_fingerprint", "wallet", "email", "alias"):
            by_value.setdefault((i["identifier_type"], i["value"]), []).append(i)
    for (itype, value), recs in sorted(by_value.items()):
        pset = sorted({r["associated_persona"] for r in recs})
        if len(pset) < 2:
            continue
        for a in range(len(pset)):
            for b in range(a + 1, len(pset)):
                refs = [r["identifier_id"] for r in recs if r["associated_persona"] in (pset[a], pset[b])]
                fs = min(r["first_seen"] for r in recs)
                ls = max(r["last_seen"] for r in recs)
                # a shared-identifier inference is only as strong as its weakest
                # supporting observation, so the edge inherits that source
                worst_rec = min(recs, key=lambda r: r["reliability_score"])
                worst = worst_rec["reliability_score"]
                sid = worst_rec["source_id"]
                add(pset[a], "PERSONA", pset[b], "PERSONA", "SHARES_IDENTIFIER", fs, ls, refs, sid,
                    "INFERENCE",
                    "Both accounts observed using the same %s value (%s); weakest supporting source score %.2f"
                    % (itype, value, worst))

    # --- INFERENCE edges: shared infrastructure indicator values ---
    infra_by_value = {}
    for rec in infra:
        infra_by_value.setdefault(rec["value"], []).append(rec)
    for value, recs in sorted(infra_by_value.items()):
        svcs = sorted({r["service_id"] for r in recs})
        if len(svcs) >= 2:
            for a in range(len(svcs)):
                for b in range(a + 1, len(svcs)):
                    refs = [r["indicator_id"] for r in recs]
                    add(svcs[a], "SERVICE", svcs[b], "SERVICE", "SHARES_INFRASTRUCTURE",
                        min(r["first_seen"] for r in recs), max(r["last_seen"] for r in recs),
                        refs, "SRC-007", "INFERENCE",
                        "Both services expose the indicator value %s" % value)
    for asset in clearnet:
        for value in asset["observed_indicators"]:
            for rec in infra_by_value.get(value, []):
                add(rec["service_id"], "SERVICE", asset["clearnet_asset_id"], "CLEARNET_ASSET",
                    "SHARES_INFRASTRUCTURE", rec["first_seen"], asset["last_seen"],
                    [rec["indicator_id"]], asset["source_id"], "INFERENCE",
                    "Clearnet asset and hidden service share the indicator value %s" % value)

    # --- HYPOTHESIS edges: candidate same-actor links ---
    # Generated mechanically from OBSERVABLE triggers only (shared identifier value or
    # shared infrastructure indicator), so both true links and false-positive
    # candidates appear. No ground truth is consulted here.
    candidates = {}
    for r in rels:
        if r["relationship_type"] == "SHARES_IDENTIFIER":
            key = tuple(sorted([r["source_entity"], r["target_entity"]]))
            candidates.setdefault(key, []).append(r["relationship_id"])
    svc_personas = {s["service_id"]: s["associated_personas"] for s in services}
    for r in list(rels):
        if r["relationship_type"] == "SHARES_INFRASTRUCTURE" and r["target_entity_type"] == "SERVICE":
            left = svc_personas.get(r["source_entity"], [])
            right = svc_personas.get(r["target_entity"], [])
            for a in left:
                for b in right:
                    if a == b:
                        continue
                    key = tuple(sorted([a, b]))
                    candidates.setdefault(key, []).append(r["relationship_id"])
    for s in services:
        plist = s["associated_personas"]
        for a in range(len(plist)):
            for b in range(a + 1, len(plist)):
                key = tuple(sorted([plist[a], plist[b]]))
                candidates.setdefault(key, []).append(s["service_id"])

    for (a, b), refs in sorted(candidates.items()):
        pa, pb = persona_map[a], persona_map[b]
        add(a, "PERSONA", b, "PERSONA", "POSSIBLE_SAME_ACTOR",
            min(pa["first_seen"], pb["first_seen"]), max(pa["last_seen"], pb["last_seen"]),
            sorted(set(refs)), "SRC-007", "HYPOTHESIS",
            "Candidate link raised by shared observable evidence; not confirmed and not to be treated as a fact.")

    return rels


# --------------------------------------------------------------------------
# 6. TIMELINE EVENTS
# --------------------------------------------------------------------------
def build_timeline(personas, posts, identifiers, infra, services, relationships):
    events = []
    n = [0]

    def add(etype, ts, description, persona_id=None, source_id=None, refs=None, entity=None):
        n[0] += 1
        s = src(source_id) if source_id else None
        events.append({
            "event_id": "EVT-%04d" % n[0],
            "event_type": etype,
            "timestamp": ts,
            "persona_id": persona_id,
            "entity_id": entity,
            "source_id": source_id,
            "description": description,
            "evidence_reference": refs or [],
            "collection_method": s["collection_method"] if s else "synthetic_service_scan",
            "reliability": s["reliability"] if s else "MEDIUM",
            "reliability_score": s["reliability_score"] if s else 0.70,
        })

    first_post = {}
    for p in posts:
        first_post.setdefault(p["persona_id"], p)

    for p in personas:
        created = max(TL_START, d(p["first_seen"][:10]) - timedelta(days=1))
        add("ACCOUNT_CREATED", iso(created + timedelta(hours=7)),
            "Account %s first observed on %s." % (p["handle"], src(p["primary_source_id"])["source_name"]),
            p["persona_id"], p["primary_source_id"])
        fp = first_post[p["persona_id"]]
        add("FIRST_POST", fp["timestamp"],
            "First recorded post by %s." % p["handle"],
            p["persona_id"], fp["source_id"], [fp["post_id"]])
        if p["status"] == "inactive":
            add("ACCOUNT_INACTIVE", iso(d(p["last_seen"][:10]) + timedelta(days=1, hours=12)),
                "No further activity recorded for %s after this date." % p["handle"],
                p["persona_id"], p["primary_source_id"],
                [p["migration_notice_post_id"]] if p["migration_notice_post_id"] else [])
        if p["announced_migration"]:
            add("MIGRATION_START", p["last_seen"],
                "%s posted a closing notice and stopped posting on this source." % p["handle"],
                p["persona_id"], p["primary_source_id"],
                [p["migration_notice_post_id"]] if p["migration_notice_post_id"] else [])
        if d(p["first_seen"][:10]) > TL_START + timedelta(days=25):
            add("NEW_PERSONA_APPEARS", p["first_seen"],
                "New account %s begins posting on %s." % (p["handle"], src(p["primary_source_id"])["source_name"]),
                p["persona_id"], p["primary_source_id"], [first_post[p["persona_id"]]["post_id"]])

    for i in identifiers:
        etype = {
            "pgp_fingerprint": "PGP_OBSERVED",
            "wallet": "WALLET_OBSERVED",
        }.get(i["identifier_type"], "IDENTIFIER_OBSERVED")
        add(etype, i["observed_at"],
            "%s value %s observed for %s on %s."
            % (i["identifier_type"], i["value"], i["associated_persona"], src(i["source_id"])["source_name"]),
            i["associated_persona"], i["source_id"], [i["identifier_id"]])

    for s in services:
        add("SERVICE_OBSERVED", s["first_seen"],
            "Hidden service %s first catalogued." % s["service_label"],
            None, s["source_id"], s["infrastructure_indicators"][:2], s["service_id"])

    for rec in infra:
        add("INFRASTRUCTURE_OBSERVED", rec["observed_at"],
            "%s indicator %s observed on %s." % (rec["indicator_type"], rec["value"], rec["service_id"]),
            None, rec["source_id"], [rec["indicator_id"]], rec["service_id"])

    for r in relationships:
        if r["relationship_type"] in ("SHARES_IDENTIFIER", "SHARES_INFRASTRUCTURE"):
            add("RELATIONSHIP_DISCOVERED", r["last_seen"],
                "%s: %s <-> %s. %s" % (r["relationship_type"], r["source_entity"], r["target_entity"], r["note"]),
                r["source_entity"] if r["source_entity_type"] == "PERSONA" else None,
                r["source_id"], [r["relationship_id"]])

    events.sort(key=lambda e: (e["timestamp"], e["event_id"]))
    for i, e in enumerate(events, start=1):
        e["event_id"] = "EVT-%04d" % i
    return events


# --------------------------------------------------------------------------
# 7. EVIDENCE LEDGER (FACT / INFERENCE / HYPOTHESIS)
# --------------------------------------------------------------------------
def build_evidence(personas, posts, identifiers, infra, services, clearnet, relationships):
    ev = []
    n = [0]

    def add(cls, statement, entities, refs, source_id, observed_at, note=""):
        n[0] += 1
        s = src(source_id)
        ev.append({
            "evidence_id": "EVID-%03d" % n[0],
            "evidence_class": cls,
            "statement": statement,
            "entities": entities,
            "evidence_refs": refs,
            "source_id": source_id,
            "observed_at": observed_at,
            "collection_method": s["collection_method"],
            "reliability": s["reliability"],
            "reliability_score": s["reliability_score"],
            "note": note,
        })

    # FACTS - directly observed synthetic records
    for i in identifiers:
        if i["identifier_type"] in ("pgp_fingerprint", "wallet", "email"):
            add("FACT",
                "%s was observed using %s value %s on %s."
                % (i["associated_persona"], i["identifier_type"], i["value"], src(i["source_id"])["source_name"]),
                [i["associated_persona"], i["identifier_id"]], [i["identifier_id"]],
                i["source_id"], i["observed_at"])
    for p in personas:
        add("FACT",
            "%s posted %d records on %s between %s and %s."
            % (p["handle"], p["post_count"], ", ".join(p["source_ids"]), p["first_seen"][:10], p["last_seen"][:10]),
            [p["persona_id"]], [], p["primary_source_id"], p["last_seen"])
    for rec in infra:
        add("FACT",
            "Indicator %s of type %s was observed on %s."
            % (rec["value"], rec["indicator_type"], rec["service_id"]),
            [rec["service_id"], rec["indicator_id"]], [rec["indicator_id"]],
            rec["source_id"], rec["observed_at"])
    for a in clearnet:
        add("FACT",
            "Clearnet asset %s exposed indicators %s."
            % (a["hostname"], ", ".join(a["observed_indicators"])),
            [a["clearnet_asset_id"]], [], a["source_id"], a["observed_at"])

    # INFERENCES - derived from observed records, still evidence-level
    for r in relationships:
        if r["evidence_class"] == "INFERENCE":
            add("INFERENCE",
                "%s and %s are linked by %s. %s"
                % (r["source_entity"], r["target_entity"], r["relationship_type"], r["note"]),
                [r["source_entity"], r["target_entity"]], r["evidence_refs"] + [r["relationship_id"]],
                r["source_id"], r["last_seen"],
                "Derived relationship, not a direct observation.")

    # HYPOTHESES - open questions raised for analyst review, no truth value attached
    for r in relationships:
        if r["relationship_type"] == "POSSIBLE_SAME_ACTOR":
            add("HYPOTHESIS",
                "%s and %s may belong to the same underlying actor."
                % (r["source_entity"], r["target_entity"]),
                [r["source_entity"], r["target_entity"]], r["evidence_refs"] + [r["relationship_id"]],
                r["source_id"], r["last_seen"],
                "Unverified hypothesis raised from observable overlap; requires corroboration from independent evidence families.")
    return ev


# --------------------------------------------------------------------------
# 8. CASES (production view - no expected outcome)
# --------------------------------------------------------------------------
def build_cases(posts, identifiers, infra, services, evidence, personas):
    persona_map = {p["persona_id"]: p for p in personas}
    posts_by_persona = {}
    for p in posts:
        posts_by_persona.setdefault(p["persona_id"], []).append(p["post_id"])
    ident_by_persona = {}
    for i in identifiers:
        ident_by_persona.setdefault(i["associated_persona"], []).append(i["identifier_id"])

    out = []
    for c in W.CASES:
        targets = c["target_personas"]
        svc_ids = c.get("target_services", [])
        for pid in targets:
            svc_ids += persona_map[pid]["observed_service_ids"]
        svc_ids = sorted(set(svc_ids))
        infra_ids = [r["indicator_id"] for r in infra if r["service_id"] in svc_ids]
        rel_posts = []
        for pid in targets:
            rel_posts += posts_by_persona.get(pid, [])[:12]
        rel_idents = []
        for pid in targets:
            rel_idents += ident_by_persona.get(pid, [])
        rel_sources = sorted({s for pid in targets for s in persona_map[pid]["source_ids"]})
        ev_refs = [e["evidence_id"] for e in evidence
                   if any(t in e["entities"] for t in targets)][:25]
        out.append({
            "case_id": c["case_id"],
            "title": c["title"],
            "analyst_question": c["analyst_question"],
            "status": "open",
            "priority": c["priority"],
            "target_entities": targets + svc_ids,
            "relevant_sources": rel_sources,
            "relevant_posts": sorted(rel_posts),
            "relevant_identifiers": sorted(set(rel_idents)),
            "relevant_infrastructure": sorted(infra_ids),
            "timeline_window": [iso_date(c["timeline_window"][0]), iso_date(c["timeline_window"][1])],
            "evidence_refs": ev_refs,
            "created_at": GENERATED_AT,
            "last_scan_date": iso_date(W.SCAN_REFERENCE_DATE),
        })
    return out


# --------------------------------------------------------------------------
# 9. ACTORS (ground-truth catalogue, restricted from the inference chain)
# --------------------------------------------------------------------------
def build_actors(personas, identifiers, services, relationships):
    persona_map = {p["persona_id"]: p for p in personas}
    out = []
    for a in W.ACTORS:
        pids = [p["persona_id"] for p in W.PERSONAS if p["actor"] == a["actor_id"]]
        ids = [i["identifier_id"] for i in identifiers if i["associated_persona"] in pids]
        svcs = sorted({s["service_id"] for s in services
                       if any(p in pids for p in s["associated_personas"])})
        sources = sorted({s for pid in pids for s in persona_map[pid]["source_ids"]})
        rel_count = sum(1 for r in relationships
                        if r["source_entity"] in pids or r["target_entity"] in pids
                        or r["source_entity"] in svcs or r["target_entity"] in svcs)
        infra_count = sum(1 for s in services if s["service_id"] in svcs
                          for _ in s["infrastructure_indicators"])
        out.append({
            "actor_id": a["actor_id"],
            "display_name": a["display_name"],
            "primary_category": a["primary_category"],
            "risk_level": a["risk_level"],
            "first_seen": min(persona_map[p]["first_seen"] for p in pids),
            "last_seen": max(persona_map[p]["last_seen"] for p in pids),
            "last_scan_date": iso_date(W.SCAN_REFERENCE_DATE),
            "persona_count": len(pids),
            "known_personas": pids,
            "known_identifiers": sorted(ids),
            "known_infrastructure": svcs,
            "known_sources": sources,
            "infrastructure_count": infra_count,
            "relationship_count": rel_count,
            "description": a["description"],
        })
    return out


# --------------------------------------------------------------------------
# 10. EVALUATION FILES
# --------------------------------------------------------------------------
def build_evaluation_pairs():
    pairs = []
    for i, (a, b, label, style_exp, temporal_exp, ident_exp, infra_exp, strength, reason, scenario) in \
            enumerate(W.EVALUATION_PAIRS, start=1):
        pairs.append({
            "pair_id": "PAIR-%03d" % i,
            "account_a": a,
            "account_b": b,
            "relationship_ground_truth": label,
            "stylometric_expectation": style_exp,
            "temporal_expectation": temporal_exp,
            "identifier_expectation": ident_exp,
            "infrastructure_expectation": infra_exp,
            "expected_evidence_strength": strength,
            "scenario": scenario,
            "reason": reason,
        })
    return pairs


def build_ground_truth(posts, post_truth, identifiers, ident_truth, personas, pairs):
    persona_profiles = {}
    for p in W.PERSONAS:
        actor = W.ACTOR_BY_ID[p["actor"]]
        prod = next(x for x in personas if x["persona_id"] == p["persona_id"])
        persona_profiles[p["persona_id"]] = {
            "actor_id": p["actor"],
            "style_archetype": p["style"],
            "writing_style_profile": W.STYLE_ARCHETYPES[p["style"]],
            "idiolect_markers": actor["idiolect"],
            "behaviour_profile": {
                "active_hours_utc": sorted(p["hours"]),
                "day_pattern": p["days"],
                "cadence": p["cadence"],
                "active_window": [prod["first_seen"], prod["last_seen"]],
                "post_count": prod["post_count"],
            },
            "design_notes": p["notes"],
        }

    scenario_coverage = {}
    for pr in pairs:
        scenario_coverage.setdefault(pr["scenario"], []).append(pr["pair_id"])
    scenario_coverage.setdefault("SCENARIO-12", []).append("CASE-007")

    return {
        "_warning": (
            "GROUND TRUTH - EVALUATION ONLY. This file must never be loaded by P2 (StyloLink), "
            "P3 (Chrono-Graph) or P4 (FIH-Ledger) during inference. It exists to score their output."
        ),
        "dataset_version": W.DATASET_VERSION,
        "persona_to_actor": {p["persona_id"]: p["actor"] for p in W.PERSONAS},
        "post_to_actor": post_truth,
        "identifier_to_actor": ident_truth,
        "service_to_actor": {
            s["service_id"]: sorted({W.PERSONA_BY_ID[p]["actor"] for p in s["personas"]})
            for s in W.HIDDEN_SERVICES
        },
        "persona_generation_profiles": persona_profiles,
        "style_archetypes": W.STYLE_ARCHETYPES,
        "actor_persona_edges": [
            {"actor_id": p["actor"], "persona_id": p["persona_id"], "relationship_type": "OPERATES"}
            for p in W.PERSONAS
        ],
        "migrations": W.MIGRATIONS,
        "infrastructure_ground_truth": [
            {"entity_a": a, "entity_b": b, "ground_truth": label, "reason": reason}
            for a, b, label, reason in W.INFRA_GROUND_TRUTH
        ],
        "case_expectations": {
            c["case_id"]: {
                "expected_final_assessment": c["expected_final_assessment"],
                "expectation_notes": c["expectation_notes"],
                "target_personas": c["target_personas"],
            } for c in W.CASES
        },
        "scenarios": W.SCENARIOS,
        "scenario_coverage": scenario_coverage,
    }


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------
def write(name, payload):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return path


def main():
    posts, post_truth = build_posts()
    identifiers, ident_truth = build_identifiers()
    infra = build_infrastructure()
    services = build_services(infra)
    clearnet = build_clearnet()
    personas = build_personas(posts, identifiers, services)
    relationships = build_relationships(personas, identifiers, infra, services, clearnet, posts)
    timeline = build_timeline(personas, posts, identifiers, infra, services, relationships)
    evidence = build_evidence(personas, posts, identifiers, infra, services, clearnet, relationships)
    cases = build_cases(posts, identifiers, infra, services, evidence, personas)
    actors = build_actors(personas, identifiers, services, relationships)
    pairs = build_evaluation_pairs()
    ground_truth = build_ground_truth(posts, post_truth, identifiers, ident_truth, personas, pairs)

    manifest = {
        "dataset_name": W.DATASET_NAME,
        "dataset_version": W.DATASET_VERSION,
        "schema_version": W.SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "generator_seed": W.SEED,
        "synthetic_only": True,
        "safety_statement": (
            "Every record in this dataset is fictional and was generated for software development, "
            "testing and controlled demonstration of the VEIL-ATLAS prototype. It contains no real "
            "threat actors, personas, keys, wallets, hidden services, domains, certificates or "
            "personal information, and must never be presented as real threat intelligence."
        ),
        "timeline_start": iso_date(W.TIMELINE_START),
        "timeline_end": iso_date(W.TIMELINE_END),
        "last_scan_date": iso_date(W.SCAN_REFERENCE_DATE),
        "total_actors": len(actors),
        "total_personas": len(personas),
        "total_posts": len(posts),
        "total_sources": len(W.SOURCES),
        "total_identifiers": len(identifiers),
        "total_infrastructure_indicators": len(infra),
        "total_hidden_services": len(services),
        "total_clearnet_assets": len(clearnet),
        "total_relationships": len(relationships),
        "total_events": len(timeline),
        "total_evidence_records": len(evidence),
        "total_cases": len(cases),
        "total_evaluation_pairs": len(pairs),
        "supported_ps_requirements": W.SUPPORTED_PS_REQUIREMENTS,
        "production_files": [
            "personas.json", "posts.json", "sources.json", "identifiers.json",
            "infrastructure.json", "hidden_services.json", "clearnet_assets.json",
            "relationships.json", "timeline_events.json", "evidence.json", "cases.json",
        ],
        "ground_truth_files": [
            "actors.json", "evaluation_pairs.json", "evaluation_ground_truth.json",
        ],
        "inference_input_files": [
            "personas.json", "posts.json", "sources.json", "identifiers.json",
            "infrastructure.json", "hidden_services.json", "clearnet_assets.json",
            "relationships.json", "timeline_events.json", "evidence.json",
        ],
        "restricted_from_inference": [
            "actors.json", "evaluation_pairs.json", "evaluation_ground_truth.json",
        ],
        "module_contract": {
            "P1_data": ["actors.json", "personas.json", "sources.json", "identifiers.json",
                        "infrastructure.json", "hidden_services.json", "clearnet_assets.json"],
            "P2_stylolink": ["personas.json", "posts.json",
                             "evaluation_pairs.json (TESTING ONLY - never as model input)"],
            "P3_chrono_graph": ["posts.json", "timeline_events.json", "personas.json"],
            "P4_fih_ledger": ["identifiers.json", "infrastructure.json", "relationships.json",
                              "evidence.json", "sources.json",
                              "P2 stylometric output", "P3 temporal output"],
            "P5_dashboard": ["actors.json", "personas.json", "relationships.json",
                             "timeline_events.json", "cases.json", "hidden_services.json",
                             "clearnet_assets.json", "module outputs"],
            "P6_integration": ["dataset_manifest.json", "README.md",
                               "dataset_validation_report.json", "evaluation_ground_truth.json"],
        },
    }

    written = []
    written.append(write("actors.json", actors))
    written.append(write("personas.json", personas))
    written.append(write("posts.json", posts))
    written.append(write("sources.json", W.SOURCES))
    written.append(write("identifiers.json", identifiers))
    written.append(write("infrastructure.json", infra))
    written.append(write("hidden_services.json", services))
    written.append(write("clearnet_assets.json", clearnet))
    written.append(write("relationships.json", relationships))
    written.append(write("timeline_events.json", timeline))
    written.append(write("evidence.json", evidence))
    written.append(write("cases.json", cases))
    written.append(write("evaluation_pairs.json", pairs))
    written.append(write("evaluation_ground_truth.json", ground_truth))
    written.append(write("dataset_manifest.json", manifest))

    print("Generated %d files in %s" % (len(written), OUT))
    for k in ("total_actors", "total_personas", "total_posts", "total_sources",
              "total_identifiers", "total_infrastructure_indicators", "total_hidden_services",
              "total_clearnet_assets", "total_relationships", "total_events",
              "total_evidence_records", "total_cases", "total_evaluation_pairs"):
        print("  %-38s %s" % (k, manifest[k]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
