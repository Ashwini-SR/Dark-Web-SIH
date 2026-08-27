# VEIL·ATLAS — Synthetic Attribution Corpus

**Dataset:** VEIL-ATLAS Synthetic Attribution Corpus · **version** 1.0.0 · **schema** 1.0
**Generated:** 2026-08-27 · **Seed:** 26151 (deterministic — regeneration is byte-identical)
**Timeline covered:** 2026-06-01 → 2026-08-25 · **Last scan date:** 2026-08-26

---

## 1. Safety statement

**Everything in this dataset is fictional.** It was generated for software development,
testing and controlled demonstration of the VEIL·ATLAS prototype (SIH PS 26151, NTRO).

It contains **no** real threat actors, criminal organisations, victims, credentials,
cryptocurrency wallets, PGP keys, hidden services, domains, certificates, forum posts or
personal information. Every identifier uses a deliberately synthetic form:

| Kind | Form used here |
|---|---|
| PGP fingerprints | `FAKE-PGP-001`, `FAKE-PGP-008-B` |
| Wallets | `SYN-WALLET-BTC-001`, `SYN-WALLET-XMR-015` |
| Hidden services | `synthetic-onion-001` … `synthetic-onion-008` (never a `.onion` address) |
| Infrastructure | `FAKE-CERT-FP-001`, `FAKE-BANNER-004`, `FAKE-FAVICON-002`, `FAKE-SW-SIG-006` |
| Domains | `forumalpha.synthetic`, `server001.synthetic.example` |
| Contacts | `contact-ferry@synthetic.example` |

Post text is abstract and non-operational — transaction and escrow state, availability,
reputation disputes, moderation, account migration. Nothing in it describes how to do
anything. The validator enforces all of this (rules R20–R24) and fails the build if a
real-looking address, key, domain, email or `.onion` string ever appears.

**This dataset must never be presented as real threat intelligence.**

---

## 2. Purpose

One connected synthetic world that every VEIL·ATLAS module can share:

```
ACTOR → PERSONA → POSTS → IDENTIFIERS → SERVICES → INFRASTRUCTURE → CLEARNET
                     ↘ TIMELINE EVENTS ↘ RELATIONSHIPS ↘ EVIDENCE ↘ CASES
```

The corpus is designed so that signals **disagree on purpose**. It supports strong
positives, weak positives, false-positive candidates, conflicting evidence, insufficient
evidence, migration/rebranding and clean negatives — because an attribution system is only
worth demonstrating if it can be shown handling uncertainty.

---

## 3. Files

### Production layer — safe as module input

| File | Records | Contents |
|---|---:|---|
| `sources.json` | 8 | Fictional sources with type, URL, reliability band and score |
| `personas.json` | 18 | Observable persona view: handle, sources, category, first/last seen, status, post count, observed identifier and service ids |
| `posts.json` | 358 | Post text with persona, source, thread, UTC timestamp, type, language, word/char counts, provenance |
| `identifiers.json` | 76 | Handle / PGP / wallet / email / alias **observations** with window, status, source, reliability |
| `infrastructure.json` | 40 | Indicators per hidden service, with confidence, reliability and clearnet cross-references |
| `hidden_services.json` | 8 | Synthetic services, their indicators, associated personas, scan dates |
| `clearnet_assets.json` | 6 | Clearnet references for correlation (one deliberate negative control) |
| `relationships.json` | 129 | Graph edges, each tagged `FACT` / `INFERENCE` / `HYPOTHESIS` |
| `timeline_events.json` | 191 | 11 event types across the full window |
| `evidence.json` | 134 | Evidence ledger: 106 facts, 19 inferences, 9 hypotheses |
| `cases.json` | 8 | Pre-built investigations with target entities, windows and evidence refs |
| `dataset_manifest.json` | — | Counts, schema version, PS-requirement map, module contract |
| `dataset_validation_report.json` | — | Machine-readable validation status, errors, warnings, statistics |

### Ground-truth layer — evaluation only, **never** model input

| File | Contents |
|---|---|
| `actors.json` | The 9 underlying synthetic actors, their personas, identifiers, services, risk and category |
| `evaluation_pairs.json` | 25 labelled persona pairs with per-family expectations |
| `evaluation_ground_truth.json` | persona→actor, post→actor, identifier→actor, style archetypes and writing-style profiles, behaviour profiles, migrations, infrastructure ground truth, case expectations, scenario coverage |

### Tooling

| File | Purpose |
|---|---|
| `generate_dataset.py` | Regenerates the whole corpus deterministically |
| `generator/world.py` | The designed topology — actors, personas, styles, services, scenarios |
| `generator/textgen.py` | Topic beats and the eight style transforms |
| `validate_dataset.py` | 24 consistency rules + leakage + safety checks; exit 0/1 |
| `inspect_dataset.py` | Human-readable summary of the corpus |

---

## 4. Commands

```bash
# regenerate (optional — the corpus is already committed)
python data/synthetic/generate_dataset.py

# validate: exit code 0 = valid, non-zero = invalid, writes dataset_validation_report.json
python data/synthetic/validate_dataset.py

# inspect
python data/synthetic/inspect_dataset.py
```

Pure standard library. Python 3.8+. No third-party dependencies, no network access.

---

## 5. Production / evaluation separation

This is the rule the whole corpus is built around: **P2, P3 and P4 must never see actor
ground truth.**

* No production file contains `ACTOR-0xx`, an actor field, a style archetype, a writing-style
  profile, a behaviour profile, an expected relationship or an expected strength. The
  validator greps for all of them (rule R19) and fails if any appears.
* `actors.json` is the **ground-truth actor catalogue**. It is listed in the manifest under
  `restricted_from_inference`. P1 and P5 may read it to render the actor-profile and
  actor-graph views for the demo; the attribution chain must not.
* `relationships.json` therefore contains **no ACTOR nodes**. Actor↔persona edges live in
  `evaluation_ground_truth.actor_persona_edges`, and `MIGRATED_TO` edges live in
  `evaluation_ground_truth.migrations` — because both would otherwise hand P4 the answer.
* `cases.json` carries an `analyst_question`, not an expected outcome. Expected outcomes
  live in `evaluation_ground_truth.case_expectations`.
* Persona records expose `announced_migration` and `migration_notice_post_id` — *observable*
  facts (an account posted a closing notice) — never the persona it migrated to.
* `POSSIBLE_SAME_ACTOR` hypothesis edges are generated mechanically from **observable**
  triggers only (a shared identifier value, a shared infrastructure indicator, a shared
  service). The generator does not consult ground truth when raising them, so the edge set
  contains both true links and false-positive candidates.

---

## 6. The synthetic world

### 9 actors, 18 personas

| Actor | Personas | Designed role |
|---|---|---|
| ACTOR-001 Ashen Ferry | shadowvendor → darkknight99, + nightmerchant | Rebrand with shared PGP **and** wallet; third parallel persona on another market |
| ACTOR-002 Glass Harbour | redfox77 → bytefox | Careful operator: keys and wallet rotated, only a stale contact address carries over |
| ACTOR-003 Pale Circuit | cryptowolf | Clean single-persona control |
| ACTOR-004 Tin Meridian | neonbroker | One handle, same key, two marketplaces — cross-source identity, not a rebrand |
| ACTOR-005 Umber Kite | greycartel, silentnode | Near-identical style, opposite schedules — style vs timing conflict |
| ACTOR-006 Copper Wren | silentbuyer → hollowtide | 21-day silence, same hidden service, near-miss key variation |
| ACTOR-007 Slate Harrier | quartzmule, emberlark | Two one-line accounts — deliberately insufficient text |
| ACTOR-008 Dunmoor Relay | pinegrove_admin, mistcaller | Moderator hub (shared-network false positives) + an unrelated-looking persona |
| ACTOR-009 Halcyon Drift | tinvault, brasspetal, lowtidefox | Three registers, one actor — identifier evidence against a negative style signal |

### 8 sources

| id | name | type | reliability | posts |
|---|---|---|---|---:|
| SRC-001 | ForumAlpha | forum | HIGH 0.91 | 67 |
| SRC-002 | ForumBeta | discussion_board | MEDIUM 0.68 | 68 |
| SRC-003 | MarketGamma | marketplace | HIGH 0.88 | 75 |
| SRC-004 | MarketDelta | marketplace | MEDIUM 0.62 | 81 |
| SRC-005 | BoardEpsilon | discussion_board | LOW 0.41 | 46 |
| SRC-006 | PasteVault | paste | LOW 0.35 | 16 |
| SRC-007 | DeepWebSigma | controlled_onion_service | MEDIUM 0.70 | 5 |
| SRC-008 | ServiceIndex | clearnet_reference | HIGH 0.94 | 0 (infrastructure only) |

Reliability spread is deliberate: the strongest identifier bridge in ACTOR-009's case sits
on `SRC-006` (0.35), so P4 has to weigh a good signal from a bad source.

### 8 style archetypes

`STYLE-A` short lowercase + ellipsis · `STYLE-B` formal, flat punctuation ·
`STYLE-C` fragmented + exclamations · `STYLE-D` technical, semicolon clauses ·
`STYLE-E` minimalist one-liners · `STYLE-F` verbose with parentheticals ·
`STYLE-G` typo-prone, dropped apostrophes · `STYLE-H` mixed case + repeated punctuation.

Text is built in two layers: **topic beats** (what a post says) and **style transform +
actor idiolect markers** (how it is written). Two personas of one actor share the archetype
*and* the idiolect while drawing different sentences — similar style, no copied wording.
Two personas of different actors can share only the archetype, which is what makes the
false-positive candidates hard rather than fake. Zero post texts are shared between
personas.

### Infrastructure design

* `SERVICE-001` ↔ `CLEAR-001` — certificate + banner + favicon all agree (strong positive).
* `SERVICE-002` ↔ `SERVICE-004` — banner and favicon shared by two **different** actors, a
  shared-hosting-style artefact (the ambiguous case).
* `SERVICE-003` ↔ `CLEAR-003`, `SERVICE-006` ↔ `CLEAR-004`, `SERVICE-008` ↔ `CLEAR-006` — one
  matching indicator each (partial).
* `SERVICE-005`, `CLEAR-005` — no overlap at all (negative controls).

---

## 7. Evaluation scenarios

25 labelled pairs: **10 SAME_ACTOR**, 3 DIFFERENT_ACTOR, 5 UNRELATED,
3 SAME_TOPIC_DIFFERENT_STYLE, 3 DIFFERENT_TOPIC_SIMILAR_STYLE, 1 AMBIGUOUS.
Expected strength: 2 HIGH, 6 MEDIUM, 15 LOW, 2 INSUFFICIENT.

All twelve required scenarios are covered:

| Scenario | Where |
|---|---|
| 1 · same actor, shared PGP + wallet, migration gap | PAIR-001, PAIR-005 |
| 2 · same actor, similar style, no shared wallet | PAIR-004 |
| 3 · different actors, same topic, different style | PAIR-010, PAIR-011, PAIR-012, PAIR-018 |
| 4 · different actors, similar style, different identifiers | PAIR-013, PAIR-014, PAIR-015 |
| 5 · different actors, similar posting time, different style | PAIR-017 |
| 6 · possible infrastructure overlap, ambiguous identity | PAIR-016, PAIR-025 |
| 7 · strong identifier, weak behavioural evidence | PAIR-007, PAIR-008 |
| 8 · strong stylometric, conflicting other evidence | PAIR-006 |
| 9 · short-text pair, insufficient evidence | PAIR-009, PAIR-023 |
| 10 · completely unrelated | PAIR-019 – PAIR-024 |
| 11 · one actor, three personas, multiple sources | PAIR-002, PAIR-003 |
| 12 · one persona, multiple sources, same handle | CASE-007 (neonbroker) |

### Investigation cases

| Case | Question | Ground-truth expectation *(evaluation file only)* |
|---|---|---|
| CASE-001 | shadowvendor → darkknight99? | STRONG_POSITIVE |
| CASE-002 | Wren panel vs Meridian desk: same operator or same host? | AMBIGUOUS |
| CASE-003 | Shared wallet across MarketDelta and PasteVault | WEAK_POSITIVE |
| CASE-004 | greycartel vs silentnode: style agrees, timing does not | CONFLICTING_EVIDENCE |
| CASE-005 | shadowvendor vs tinvault: is shared style enough? | FALSE_POSITIVE_CANDIDATE |
| CASE-006 | quartzmule vs emberlark | INSUFFICIENT_EVIDENCE |
| CASE-007 | neonbroker on two marketplaces | STRONG_POSITIVE |
| CASE-008 | silentbuyer → hollowtide across 21 days of silence | STRONG_POSITIVE |

**CASE-008 and CASE-001 are the intended SIH demo path:** persona active → silence →
new persona appears → identifier/infrastructure reuse observed → style similarity →
inferred migration, all visible on one timeline and one graph.

### Behavioural design

Posting hours per persona are distinct and intentional: ACTOR-001's personas sit at
01:00–05:00 UTC, ACTOR-002's at 09:00–13:00 on weekdays only, greycartel at 09:00–12:00
against silentnode at 22:00–02:00 (the conflict case), neonbroker at 18:00–22:00 in bursts.
Migration gaps are all different — 14, 9 and 21 days — so nothing can be pattern-matched
off a fixed interval. All timestamps are UTC, ISO-8601, `...Z`.

---

## 8. Module contract

| Module | Consumes |
|---|---|
| **P1 — Data / identifiers / infrastructure** | `actors.json`, `personas.json`, `sources.json`, `identifiers.json`, `infrastructure.json`, `hidden_services.json`, `clearnet_assets.json` |
| **P2 — StyloLink** | `personas.json`, `posts.json` · `evaluation_pairs.json` **for scoring only, never as model input** |
| **P3 — Chrono-Graph** | `posts.json`, `timeline_events.json`, `personas.json` |
| **P4 — FIH-Ledger** | `identifiers.json`, `infrastructure.json`, `relationships.json`, `evidence.json`, `sources.json` + P2 and P3 outputs |
| **P5 — Dashboard** | `actors.json`, `personas.json`, `relationships.json`, `timeline_events.json`, `cases.json`, `hidden_services.json`, `clearnet_assets.json` + module outputs |
| **P6 — Integration** | `dataset_manifest.json`, this README, `dataset_validation_report.json`, `evaluation_ground_truth.json` |

Dashboard-ready fields are present throughout: actors carry display name, category, risk,
first/last seen, persona/source/infrastructure/relationship counts; personas carry handle,
sources, window and post count; identifiers carry `display_value` (masked) alongside `value`;
infrastructure carries type, service, clearnet relation, observed date and reliability;
relationships carry both endpoints, type, evidence refs, window and reliability.

---

## 9. Validation

`validate_dataset.py` implements 24 rules and exits non-zero on any error.

**Structure & references (R1–R7):** every persona, post, source, identifier, service,
indicator, relationship, event, evidence record and case reference resolves to an existing
entity. **Time (R8–R10):** every timestamp is ISO-8601 UTC, `first_seen ≤ last_seen`, every
`last_scan_date` is valid, all timestamps fall inside the dataset window, and each persona's
window and post count match its actual posts. **Uniqueness (R11–R16):** no duplicate ids in
any file. **Orphans (R17):** every persona has posts, every service has indicators, every
clearnet asset overlaps a service unless declared a negative control (`CLEAR-005`).
**Separation (R18–R19):** evaluation pairs reference real personas and use valid labels; no
production file exposes an actor id, a ground-truth key or evaluation vocabulary.
**Safety (R20–R24):** no `.onion` string, no address-shaped wallet value, no real-looking key
fingerprint, no non-synthetic domain, no non-synthetic email; PGP values must start
`FAKE-PGP-`, wallets `SYN-WALLET-`, services `synthetic-onion-`. Plus provenance: every post,
identifier, indicator, relationship, event and evidence record carries `source_id`,
`collection_method` and `reliability`.

**Current status: VALID — 0 errors, 0 warnings.**

---

## 10. Known limitations and deliberate deviations

1. **Relationship count is 129, above the 60–100 guide.** Covering all twelve required edge
   types across 18 personas, 76 identifier observations and 8 services cannot be done inside
   100 edges. Redundant edges were removed (service→indicator membership lives in
   `hidden_services.infrastructure_indicators` instead); what remains is the minimum that
   still covers the required types.
2. **39 posts are ≤ 6 words, above the 10–20 guide.** 24 come from the three deliberately
   minimalist personas (quartzmule, emberlark, brasspetal) that exist to test P2's
   data-sufficiency gate; the rest are naturally short posts in STYLE-A and STYLE-H.
   Overall: 39 very short, 240 medium (7–25 words), 79 long (> 25 words).
3. **`expected_final_assessment` was moved out of `cases.json`** into
   `evaluation_ground_truth.case_expectations`, and `MIGRATED_TO` edges out of
   `relationships.json` into `evaluation_ground_truth.migrations`. Both are required case
   and edge fields in the spec, but leaving them in production files would hand P4 the
   answer. Section 44 (no leakage) was treated as the stronger constraint.
4. **Only one pair is labelled `AMBIGUOUS`** (PAIR-016). Two further pairs are genuinely hard
   without being unresolvable — PAIR-006 (style agrees, timing conflicts) and PAIR-007
   (identifiers agree, style conflicts) — and are labelled by their true relation with
   conflicting per-family expectations rather than as ambiguous.
5. **No model results exist and none are claimed.** The corpus has been checked for
   *design* consistency — that the intended structure is present in the surface features —
   but nothing here reports accuracy for StyloLink, Chrono-Graph or FIH-Ledger, because
   those modules have not been built yet.
6. **English only, single register per persona.** No multilingual or code-switching cases,
   no adversarial style-imitation cases (an actor deliberately mimicking another's style),
   and no deleted/edited-post history. These are natural extensions for a v1.1.
7. **Post content is intentionally narrow.** Every post talks about transaction state,
   availability, reputation or moderation, because anything more specific would drift toward
   operational content. That makes topic modelling on this corpus less interesting than
   stylometry — which is the intended trade.

---

## 11. Regeneration

The corpus is fully determined by `SEED = 26151` in `generator/world.py`. Re-running the
generator reproduces every file byte-for-byte. To extend the world — more actors, longer
timelines, new scenarios — edit `generator/world.py`, regenerate, and run the validator;
the design lives in that one file, not in the JSON.
