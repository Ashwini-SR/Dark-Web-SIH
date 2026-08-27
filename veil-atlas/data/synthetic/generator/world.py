"""
VEIL-ATLAS synthetic world definition.

This module contains the *designed* topology of the synthetic world:
actors, personas, sources, style archetypes, activity patterns, services and
the deliberate evaluation scenarios.

EVERYTHING HERE IS FICTIONAL. No real actor, marketplace, key, wallet, domain,
certificate or person is referenced. All identifier values use obviously
synthetic prefixes (FAKE-, SYN-, synthetic-onion-, *.synthetic / *.synthetic.example).
"""

DATASET_NAME = "VEIL-ATLAS Synthetic Attribution Corpus"
DATASET_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0"
SEED = 26151  # SIH problem statement number, used as the RNG seed for reproducibility

TIMELINE_START = "2026-06-01"
TIMELINE_END = "2026-08-25"
SCAN_REFERENCE_DATE = "2026-08-26"

# --------------------------------------------------------------------------
# SOURCES
# --------------------------------------------------------------------------
SOURCES = [
    {
        "source_id": "SRC-001",
        "source_name": "ForumAlpha",
        "source_type": "forum",
        "url": "http://forumalpha.synthetic",
        "description": "Fictional general-purpose discussion forum with vendor sub-boards. Well-archived, stable identifiers, moderated.",
        "reliability": "HIGH",
        "reliability_score": 0.91,
        "collection_method": "synthetic_forum_record",
    },
    {
        "source_id": "SRC-002",
        "source_name": "ForumBeta",
        "source_type": "discussion_board",
        "url": "http://forumbeta.synthetic",
        "description": "Fictional secondary discussion board. Partial archives, occasional thread loss, moderate confidence in timestamps.",
        "reliability": "MEDIUM",
        "reliability_score": 0.68,
        "collection_method": "synthetic_forum_record",
    },
    {
        "source_id": "SRC-003",
        "source_name": "MarketGamma",
        "source_type": "marketplace",
        "url": "http://marketgamma.synthetic",
        "description": "Fictional marketplace with escrow and vendor feedback. Strong per-account records and consistent vendor pages.",
        "reliability": "HIGH",
        "reliability_score": 0.88,
        "collection_method": "synthetic_marketplace_record",
    },
    {
        "source_id": "SRC-004",
        "source_name": "MarketDelta",
        "source_type": "marketplace",
        "url": "http://marketdelta.synthetic",
        "description": "Fictional smaller marketplace. Frequent downtime, mirrors of uncertain provenance, weaker record retention.",
        "reliability": "MEDIUM",
        "reliability_score": 0.62,
        "collection_method": "synthetic_marketplace_record",
    },
    {
        "source_id": "SRC-005",
        "source_name": "BoardEpsilon",
        "source_type": "discussion_board",
        "url": "http://boardepsilon.synthetic",
        "description": "Fictional low-moderation board. Handle squatting is common and post timestamps are self-reported.",
        "reliability": "LOW",
        "reliability_score": 0.41,
        "collection_method": "synthetic_forum_record",
    },
    {
        "source_id": "SRC-006",
        "source_name": "PasteVault",
        "source_type": "paste",
        "url": "http://pastevault.synthetic",
        "description": "Fictional paste service. Anonymous drops, no account model, attribution rests entirely on self-claimed handles.",
        "reliability": "LOW",
        "reliability_score": 0.35,
        "collection_method": "synthetic_archive_record",
    },
    {
        "source_id": "SRC-007",
        "source_name": "DeepWebSigma",
        "source_type": "controlled_onion_service",
        "url": "synthetic-onion-index-001",
        "description": "Fictional research-controlled hidden-service index used for synthetic service scans and descriptor metadata.",
        "reliability": "MEDIUM",
        "reliability_score": 0.70,
        "collection_method": "synthetic_service_scan",
    },
    {
        "source_id": "SRC-008",
        "source_name": "ServiceIndex",
        "source_type": "clearnet_reference",
        "url": "https://serviceindex.synthetic",
        "description": "Fictional clearnet asset index providing certificate, banner and favicon observations for correlation testing.",
        "reliability": "HIGH",
        "reliability_score": 0.94,
        "collection_method": "synthetic_clearnet_reference",
    },
]

SOURCE_BY_ID = {s["source_id"]: s for s in SOURCES}

# --------------------------------------------------------------------------
# STYLE ARCHETYPES  (generation-only metadata -> evaluation file, never production)
# --------------------------------------------------------------------------
STYLE_ARCHETYPES = {
    "STYLE-A": {
        "label": "short lowercase, ellipsis-heavy",
        "average_sentence_length": "short",
        "punctuation_style": "frequent_ellipsis",
        "capitalization": "mostly_lowercase",
        "typo_style": "missing_apostrophes",
        "verbosity": "brief",
        "slang_level": "high",
    },
    "STYLE-B": {
        "label": "formal complete sentences, flat punctuation",
        "average_sentence_length": "medium",
        "punctuation_style": "periods_only",
        "capitalization": "standard",
        "typo_style": "none",
        "verbosity": "moderate",
        "slang_level": "low",
    },
    "STYLE-C": {
        "label": "fragmented, exclamation-heavy",
        "average_sentence_length": "very_short",
        "punctuation_style": "frequent_exclamation",
        "capitalization": "standard",
        "typo_style": "none",
        "verbosity": "brief",
        "slang_level": "medium",
    },
    "STYLE-D": {
        "label": "technical register, semicolon clauses",
        "average_sentence_length": "long",
        "punctuation_style": "semicolons",
        "capitalization": "standard",
        "typo_style": "none",
        "verbosity": "high",
        "slang_level": "none",
    },
    "STYLE-E": {
        "label": "minimalist one-liners",
        "average_sentence_length": "very_short",
        "punctuation_style": "sparse",
        "capitalization": "mostly_lowercase",
        "typo_style": "none",
        "verbosity": "minimal",
        "slang_level": "low",
    },
    "STYLE-F": {
        "label": "verbose with parenthetical asides",
        "average_sentence_length": "long",
        "punctuation_style": "parentheses",
        "capitalization": "standard",
        "typo_style": "none",
        "verbosity": "very_high",
        "slang_level": "low",
    },
    "STYLE-G": {
        "label": "typo-prone, omitted apostrophes",
        "average_sentence_length": "medium",
        "punctuation_style": "irregular_commas",
        "capitalization": "mostly_lowercase",
        "typo_style": "frequent_misspellings",
        "verbosity": "moderate",
        "slang_level": "medium",
    },
    "STYLE-H": {
        "label": "mixed capitalization, repeated punctuation",
        "average_sentence_length": "short",
        "punctuation_style": "repeated_marks",
        "capitalization": "mixed_case_emphasis",
        "typo_style": "none",
        "verbosity": "moderate",
        "slang_level": "medium",
    },
}

# --------------------------------------------------------------------------
# ACTORS  (GROUND TRUTH ONLY - never fed to the inference chain)
# --------------------------------------------------------------------------
ACTORS = [
    {
        "actor_id": "ACTOR-001",
        "display_name": "Ashen Ferry",
        "primary_category": "stolen_data",
        "risk_level": "HIGH",
        "description": "Fictional multi-persona vendor operation. Runs a long-lived marketplace persona, rebrands after a two-week quiet period, and keeps a second parallel persona on a different marketplace. Reuses key material and payment identifiers across personas.",
        "idiolect": ["same terms as before", "ping me here", "no rush on this", "as usual"],
        "connective": "anyway",
    },
    {
        "actor_id": "ACTOR-002",
        "display_name": "Glass Harbour",
        "primary_category": "credential_trading",
        "risk_level": "HIGH",
        "description": "Fictional credential-trading operator with a careful operational posture: rotates key material and payment identifiers between personas, so the only identifier overlap is a stale shared contact address.",
        "idiolect": ["for the record", "per the earlier thread", "noting this here"],
        "connective": "regardless",
    },
    {
        "actor_id": "ACTOR-003",
        "display_name": "Pale Circuit",
        "primary_category": "hacking_service",
        "risk_level": "MEDIUM",
        "description": "Fictional single-persona service advertiser. Stable handle, formal register, no rebranding. Included as a clean control actor.",
        "idiolect": ["to clarify", "I will follow up"],
        "connective": "in any case",
    },
    {
        "actor_id": "ACTOR-004",
        "display_name": "Tin Meridian",
        "primary_category": "access_broker",
        "risk_level": "HIGH",
        "description": "Fictional access-broker persona that expands from one marketplace to a second under the identical handle and key material. Demonstrates cross-source identity rather than rebranding.",
        "idiolect": ["as before", "same as the last cycle", "for completeness"],
        "connective": "that said",
    },
    {
        "actor_id": "ACTOR-005",
        "display_name": "Umber Kite",
        "primary_category": "financial_fraud",
        "risk_level": "MEDIUM",
        "description": "Fictional operator running two concurrent personas on very different schedules. Style is nearly identical across personas but the temporal signal actively contradicts linkage.",
        "idiolect": ["cant confirm yet", "same as last week", "will update"],
        "connective": "either way",
    },
    {
        "actor_id": "ACTOR-006",
        "display_name": "Copper Wren",
        "primary_category": "malware_service",
        "risk_level": "HIGH",
        "description": "Fictional service operator that abandons a persona and returns three weeks later under a new handle on the same hidden service. Key material is rotated with a near-miss variation.",
        "idiolect": ["Same Setup", "check the pinned note", "back online now"],
        "connective": "so",
    },
    {
        "actor_id": "ACTOR-007",
        "display_name": "Slate Harrier",
        "primary_category": "money_laundering",
        "risk_level": "MEDIUM",
        "description": "Fictional low-volume operator. Both personas post one-line messages only, deliberately providing insufficient text for stylometric attribution.",
        "idiolect": ["ok", "noted"],
        "connective": "",
    },
    {
        "actor_id": "ACTOR-008",
        "display_name": "Dunmoor Relay",
        "primary_category": "marketplace",
        "risk_level": "LOW",
        "description": "Fictional community operator: a moderator persona on two forums plus an unrelated-looking discussion persona. Acts as a shared network hub that many unrelated actors interact with.",
        "idiolect": ["please keep it in one thread", "logged for reference"],
        "connective": "additionally",
    },
    {
        "actor_id": "ACTOR-009",
        "display_name": "Halcyon Drift",
        "primary_category": "money_laundering",
        "risk_level": "HIGH",
        "description": "Fictional operator whose three personas write in three different registers. Linkage rests entirely on shared key material and payment identifiers, with the stylometric signal pointing the other way.",
        "idiolect": ["short window on this", "second batch later"],
        "connective": "meanwhile",
    },
]

ACTOR_BY_ID = {a["actor_id"]: a for a in ACTORS}

# --------------------------------------------------------------------------
# PERSONAS
# window: (first_active_date, last_active_date) inclusive, YYYY-MM-DD
# hours:  preferred posting hours (UTC)
# days:   all | weekdays | weekends
# cadence: steady | bursty | sparse
# --------------------------------------------------------------------------
PERSONAS = [
    {
        "persona_id": "PERSONA-001", "handle": "shadowvendor", "actor": "ACTOR-001",
        "style": "STYLE-A", "category": "stolen_data",
        "sources": ["SRC-003"], "primary_source": "SRC-003",
        "window": ("2026-06-02", "2026-07-05"), "hours": [1, 2, 3, 4], "days": "all",
        "cadence": "steady", "n_posts": 26, "status": "inactive",
        "announced_migration": True,
        "notes": "Goes quiet after a closing notice; 14-day gap before PERSONA-004 appears.",
    },
    {
        "persona_id": "PERSONA-002", "handle": "redfox77", "actor": "ACTOR-002",
        "style": "STYLE-D", "category": "credential_trading",
        "sources": ["SRC-001"], "primary_source": "SRC-001",
        "window": ("2026-06-03", "2026-07-28"), "hours": [9, 10, 11, 12], "days": "weekdays",
        "cadence": "steady", "n_posts": 24, "status": "inactive",
        "announced_migration": True,
        "notes": "9-day gap before PERSONA-007 appears on a different board.",
    },
    {
        "persona_id": "PERSONA-003", "handle": "cryptowolf", "actor": "ACTOR-003",
        "style": "STYLE-B", "category": "hacking_service",
        "sources": ["SRC-001"], "primary_source": "SRC-001",
        "window": ("2026-06-05", "2026-08-22"), "hours": [13, 14, 15, 16, 17], "days": "all",
        "cadence": "steady", "n_posts": 22, "status": "active",
        "announced_migration": False,
        "notes": "Control actor: single persona, stable handle, formal register.",
    },
    {
        "persona_id": "PERSONA-004", "handle": "darkknight99", "actor": "ACTOR-001",
        "style": "STYLE-A", "category": "stolen_data",
        "sources": ["SRC-003", "SRC-001"], "primary_source": "SRC-003",
        "window": ("2026-07-19", "2026-08-24"), "hours": [1, 2, 3, 4], "days": "all",
        "cadence": "steady", "n_posts": 30, "status": "active",
        "announced_migration": False,
        "notes": "Rebrand of PERSONA-001. Same PGP and wallet, same style, same hours.",
    },
    {
        "persona_id": "PERSONA-005", "handle": "neonbroker", "actor": "ACTOR-004",
        "style": "STYLE-F", "category": "access_broker",
        "sources": ["SRC-003", "SRC-004"], "primary_source": "SRC-003",
        "window": ("2026-06-02", "2026-08-23"), "hours": [18, 19, 20, 21, 22], "days": "all",
        "cadence": "bursty", "n_posts": 30, "status": "active",
        "announced_migration": False,
        "second_source_from": "2026-07-10",
        "notes": "Same handle observed on two marketplaces from 2026-07-10 onward.",
    },
    {
        "persona_id": "PERSONA-006", "handle": "greycartel", "actor": "ACTOR-005",
        "style": "STYLE-G", "category": "financial_fraud",
        "sources": ["SRC-002"], "primary_source": "SRC-002",
        "window": ("2026-06-04", "2026-07-30"), "hours": [9, 10, 11, 12], "days": "weekdays",
        "cadence": "steady", "n_posts": 22, "status": "inactive",
        "announced_migration": False,
        "notes": "Style twin of PERSONA-013 but on an incompatible schedule.",
    },
    {
        "persona_id": "PERSONA-007", "handle": "bytefox", "actor": "ACTOR-002",
        "style": "STYLE-D", "category": "credential_trading",
        "sources": ["SRC-002"], "primary_source": "SRC-002",
        "window": ("2026-08-06", "2026-08-25"), "hours": [9, 10, 11, 12, 13], "days": "weekdays",
        "cadence": "steady", "n_posts": 16, "status": "active",
        "announced_migration": False,
        "notes": "Rebrand of PERSONA-002. Rotated PGP and wallet; only a stale contact address overlaps.",
    },
    {
        "persona_id": "PERSONA-008", "handle": "silentbuyer", "actor": "ACTOR-006",
        "style": "STYLE-H", "category": "malware_service",
        "sources": ["SRC-004"], "primary_source": "SRC-004",
        "window": ("2026-06-06", "2026-07-12"), "hours": [20, 21, 22, 23], "days": "all",
        "cadence": "bursty", "n_posts": 18, "status": "inactive",
        "announced_migration": True,
        "notes": "Abandoned persona; 21-day gap before PERSONA-012 appears on the same service.",
    },
    {
        "persona_id": "PERSONA-009", "handle": "quartzmule", "actor": "ACTOR-007",
        "style": "STYLE-E", "category": "money_laundering",
        "sources": ["SRC-005"], "primary_source": "SRC-005",
        "window": ("2026-06-10", "2026-08-18"), "hours": [15, 16, 17, 18, 19], "days": "all",
        "cadence": "sparse", "n_posts": 8, "status": "active",
        "announced_migration": False,
        "notes": "Short-text account: insufficient data for stylometry.",
    },
    {
        "persona_id": "PERSONA-010", "handle": "pinegrove_admin", "actor": "ACTOR-008",
        "style": "STYLE-B", "category": "marketplace",
        "sources": ["SRC-001", "SRC-002"], "primary_source": "SRC-001",
        "window": ("2026-06-01", "2026-08-25"), "hours": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18], "days": "all",
        "cadence": "steady", "n_posts": 26, "status": "active",
        "announced_migration": False,
        "notes": "Moderator hub. Interacts with many unrelated personas - shared-network false-positive source.",
    },
    {
        "persona_id": "PERSONA-011", "handle": "nightmerchant", "actor": "ACTOR-001",
        "style": "STYLE-A", "category": "stolen_data",
        "sources": ["SRC-004"], "primary_source": "SRC-004",
        "window": ("2026-06-20", "2026-08-20"), "hours": [2, 3, 4, 5], "days": "all",
        "cadence": "steady", "n_posts": 24, "status": "active",
        "announced_migration": False,
        "notes": "Parallel third persona of ACTOR-001 on a different marketplace; separate wallet, separate PGP.",
    },
    {
        "persona_id": "PERSONA-012", "handle": "hollowtide", "actor": "ACTOR-006",
        "style": "STYLE-H", "category": "malware_service",
        "sources": ["SRC-004", "SRC-007"], "primary_source": "SRC-004",
        "window": ("2026-08-02", "2026-08-25"), "hours": [20, 21, 22, 23], "days": "all",
        "cadence": "bursty", "n_posts": 20, "status": "active",
        "announced_migration": False,
        "notes": "Rebrand of PERSONA-008 on the same hidden service; near-miss PGP variation.",
    },
    {
        "persona_id": "PERSONA-013", "handle": "silentnode", "actor": "ACTOR-005",
        "style": "STYLE-G", "category": "financial_fraud",
        "sources": ["SRC-005"], "primary_source": "SRC-005",
        "window": ("2026-06-15", "2026-08-25"), "hours": [22, 23, 0, 1, 2], "days": "all",
        "cadence": "steady", "n_posts": 24, "status": "active",
        "announced_migration": False,
        "notes": "Concurrent with PERSONA-006 on an opposite schedule: style agrees, timing conflicts.",
    },
    {
        "persona_id": "PERSONA-014", "handle": "emberlark", "actor": "ACTOR-007",
        "style": "STYLE-E", "category": "money_laundering",
        "sources": ["SRC-006"], "primary_source": "SRC-006",
        "window": ("2026-06-25", "2026-08-21"), "hours": [16, 17, 18, 19], "days": "all",
        "cadence": "sparse", "n_posts": 7, "status": "active",
        "announced_migration": False,
        "notes": "Second short-text account of ACTOR-007 on a low-reliability paste source.",
    },
    {
        "persona_id": "PERSONA-015", "handle": "tinvault", "actor": "ACTOR-009",
        "style": "STYLE-A", "category": "money_laundering",
        "sources": ["SRC-004"], "primary_source": "SRC-004",
        "window": ("2026-06-08", "2026-08-23"), "hours": [3, 4, 5, 6, 7], "days": "all",
        "cadence": "steady", "n_posts": 20, "status": "active",
        "announced_migration": False,
        "notes": "Shares STYLE-A with the ACTOR-001 personas but is a different actor - primary false-positive candidate.",
    },
    {
        "persona_id": "PERSONA-016", "handle": "brasspetal", "actor": "ACTOR-009",
        "style": "STYLE-E", "category": "stolen_data",
        "sources": ["SRC-006"], "primary_source": "SRC-006",
        "window": ("2026-06-12", "2026-08-15"), "hours": [12, 13, 14, 15, 16], "days": "all",
        "cadence": "sparse", "n_posts": 9, "status": "active",
        "announced_migration": False,
        "notes": "Minimalist paste-drop persona linked to ACTOR-009 only through a shared wallet identifier.",
    },
    {
        "persona_id": "PERSONA-017", "handle": "lowtidefox", "actor": "ACTOR-009",
        "style": "STYLE-D", "category": "hacking_service",
        "sources": ["SRC-002"], "primary_source": "SRC-002",
        "window": ("2026-07-05", "2026-08-25"), "hours": [19, 20, 21, 22, 23], "days": "all",
        "cadence": "steady", "n_posts": 18, "status": "active",
        "announced_migration": False,
        "notes": "Shares STYLE-D with the ACTOR-002 personas (different actor) while sharing a PGP with PERSONA-015 (same actor, different style).",
    },
    {
        "persona_id": "PERSONA-018", "handle": "mistcaller", "actor": "ACTOR-008",
        "style": "STYLE-C", "category": "fraud",
        "sources": ["SRC-005"], "primary_source": "SRC-005",
        "window": ("2026-07-01", "2026-08-19"), "hours": [11, 12, 13, 14, 15], "days": "all",
        "cadence": "bursty", "n_posts": 14, "status": "active",
        "announced_migration": False,
        "notes": "Second persona of the moderator actor, in a completely different register.",
    },
]

PERSONA_BY_ID = {p["persona_id"]: p for p in PERSONAS}

# --------------------------------------------------------------------------
# HIDDEN SERVICES  (synthetic labels only - never real .onion addresses)
# --------------------------------------------------------------------------
HIDDEN_SERVICES = [
    {
        "service_id": "SERVICE-001", "service_label": "synthetic-onion-001",
        "service_name": "Ferry Vendor Panel (synthetic)",
        "first_seen": "2026-06-02", "last_seen": "2026-08-24", "status": "online",
        "personas": ["PERSONA-001", "PERSONA-004"], "source_id": "SRC-007",
        "synthetic_domain_relation": "CLEAR-001",
    },
    {
        "service_id": "SERVICE-002", "service_label": "synthetic-onion-002",
        "service_name": "Meridian Broker Desk (synthetic)",
        "first_seen": "2026-06-04", "last_seen": "2026-08-23", "status": "online",
        "personas": ["PERSONA-005"], "source_id": "SRC-007",
        "synthetic_domain_relation": "CLEAR-002",
    },
    {
        "service_id": "SERVICE-003", "service_label": "synthetic-onion-003",
        "service_name": "Harbour Listing Mirror (synthetic)",
        "first_seen": "2026-06-06", "last_seen": "2026-08-25", "status": "online",
        "personas": ["PERSONA-002", "PERSONA-007"], "source_id": "SRC-007",
        "synthetic_domain_relation": "CLEAR-003",
    },
    {
        "service_id": "SERVICE-004", "service_label": "synthetic-onion-004",
        "service_name": "Wren Support Panel (synthetic)",
        "first_seen": "2026-06-07", "last_seen": "2026-08-25", "status": "online",
        "personas": ["PERSONA-008", "PERSONA-012"], "source_id": "SRC-007",
        "synthetic_domain_relation": "CLEAR-002",
    },
    {
        "service_id": "SERVICE-005", "service_label": "synthetic-onion-005",
        "service_name": "Kite Settlement Page (synthetic)",
        "first_seen": "2026-06-16", "last_seen": "2026-08-25", "status": "online",
        "personas": ["PERSONA-006"], "source_id": "SRC-007",
        "synthetic_domain_relation": None,
    },
    {
        "service_id": "SERVICE-006", "service_label": "synthetic-onion-006",
        "service_name": "Drift Transfer Desk (synthetic)",
        "first_seen": "2026-06-10", "last_seen": "2026-08-23", "status": "online",
        "personas": ["PERSONA-015", "PERSONA-017"], "source_id": "SRC-007",
        "synthetic_domain_relation": "CLEAR-004",
    },
    {
        "service_id": "SERVICE-007", "service_label": "synthetic-onion-007",
        "service_name": "Harrier Drop Page (synthetic)",
        "first_seen": "2026-06-14", "last_seen": "2026-08-18", "status": "intermittent",
        "personas": ["PERSONA-009"], "source_id": "SRC-007",
        "synthetic_domain_relation": None,
    },
    {
        "service_id": "SERVICE-008", "service_label": "synthetic-onion-008",
        "service_name": "Dunmoor Community Gateway (synthetic)",
        "first_seen": "2026-06-01", "last_seen": "2026-08-25", "status": "online",
        "personas": ["PERSONA-010", "PERSONA-018"], "source_id": "SRC-007",
        "synthetic_domain_relation": "CLEAR-006",
    },
]

# Indicator plan: (service_id, indicator_type, value, confidence, reliability_score)
# Shared values across services are DELIBERATE and drive the infrastructure scenarios.
INFRA_PLAN = [
    # SERVICE-001 - clean, strongly correlated with CLEAR-001
    ("SERVICE-001", "ssl_certificate", "FAKE-CERT-FP-001", "HIGH", 0.90),
    ("SERVICE-001", "server_banner", "FAKE-BANNER-001", "HIGH", 0.86),
    ("SERVICE-001", "favicon_hash", "FAKE-FAVICON-001", "MEDIUM", 0.74),
    ("SERVICE-001", "software_signature", "FAKE-SW-SIG-001", "MEDIUM", 0.71),
    ("SERVICE-001", "hostname_pattern", "node-a{n}.synthetic.example", "MEDIUM", 0.66),
    ("SERVICE-001", "descriptor_metadata", "FAKE-DESC-META-001", "MEDIUM", 0.69),
    # SERVICE-002 - shares banner + favicon with SERVICE-004 (partial / ambiguous)
    ("SERVICE-002", "ssl_certificate", "FAKE-CERT-FP-002", "HIGH", 0.89),
    ("SERVICE-002", "server_banner", "FAKE-BANNER-004", "MEDIUM", 0.64),
    ("SERVICE-002", "favicon_hash", "FAKE-FAVICON-002", "MEDIUM", 0.61),
    ("SERVICE-002", "software_signature", "FAKE-SW-SIG-002", "MEDIUM", 0.72),
    ("SERVICE-002", "service_configuration", "FAKE-CONFIG-002", "LOW", 0.48),
    # SERVICE-003
    ("SERVICE-003", "ssl_certificate", "FAKE-CERT-FP-003", "HIGH", 0.87),
    ("SERVICE-003", "server_banner", "FAKE-BANNER-003", "MEDIUM", 0.70),
    ("SERVICE-003", "favicon_hash", "FAKE-FAVICON-003", "MEDIUM", 0.63),
    ("SERVICE-003", "software_signature", "FAKE-SW-SIG-003", "MEDIUM", 0.68),
    ("SERVICE-003", "descriptor_metadata", "FAKE-DESC-META-003", "LOW", 0.44),
    # SERVICE-004 - same service across the ACTOR-006 rebrand; overlaps SERVICE-002 partially
    ("SERVICE-004", "ssl_certificate", "FAKE-CERT-FP-004", "HIGH", 0.88),
    ("SERVICE-004", "server_banner", "FAKE-BANNER-004", "MEDIUM", 0.64),
    ("SERVICE-004", "favicon_hash", "FAKE-FAVICON-002", "MEDIUM", 0.61),
    ("SERVICE-004", "software_signature", "FAKE-SW-SIG-004", "HIGH", 0.83),
    ("SERVICE-004", "service_configuration", "FAKE-CONFIG-004", "MEDIUM", 0.67),
    ("SERVICE-004", "hostname_pattern", "panel-w{n}.synthetic.example", "MEDIUM", 0.65),
    # SERVICE-005 - deliberately has no clearnet correlate
    ("SERVICE-005", "ssl_certificate", "FAKE-CERT-FP-005", "MEDIUM", 0.72),
    ("SERVICE-005", "server_banner", "FAKE-BANNER-005", "MEDIUM", 0.66),
    ("SERVICE-005", "software_signature", "FAKE-SW-SIG-005", "LOW", 0.45),
    ("SERVICE-005", "fictional_server_status_indicator", "FAKE-STATUS-005", "LOW", 0.39),
    # SERVICE-006 - partial clearnet correlation via software signature only
    ("SERVICE-006", "ssl_certificate", "FAKE-CERT-FP-006", "HIGH", 0.85),
    ("SERVICE-006", "server_banner", "FAKE-BANNER-006", "MEDIUM", 0.69),
    ("SERVICE-006", "favicon_hash", "FAKE-FAVICON-006", "MEDIUM", 0.62),
    ("SERVICE-006", "software_signature", "FAKE-SW-SIG-006", "MEDIUM", 0.73),
    ("SERVICE-006", "hostname_pattern", "desk-d{n}.synthetic.example", "LOW", 0.47),
    ("SERVICE-006", "descriptor_metadata", "FAKE-DESC-META-006", "MEDIUM", 0.64),
    # SERVICE-007 - sparse, low confidence
    ("SERVICE-007", "server_banner", "FAKE-BANNER-007", "LOW", 0.42),
    ("SERVICE-007", "fictional_server_status_indicator", "FAKE-STATUS-007", "LOW", 0.36),
    ("SERVICE-007", "descriptor_metadata", "FAKE-DESC-META-007", "LOW", 0.40),
    # SERVICE-008
    ("SERVICE-008", "ssl_certificate", "FAKE-CERT-FP-008", "HIGH", 0.86),
    ("SERVICE-008", "server_banner", "FAKE-BANNER-008", "MEDIUM", 0.71),
    ("SERVICE-008", "favicon_hash", "FAKE-FAVICON-008", "MEDIUM", 0.68),
    ("SERVICE-008", "software_signature", "FAKE-SW-SIG-008", "MEDIUM", 0.70),
    ("SERVICE-008", "service_configuration", "FAKE-CONFIG-008", "LOW", 0.49),
]

CLEARNET_ASSETS = [
    {
        "clearnet_asset_id": "CLEAR-001", "hostname": "server001.synthetic.example",
        "certificate_fingerprint": "FAKE-CERT-FP-001",
        "observed_indicators": ["FAKE-CERT-FP-001", "FAKE-BANNER-001", "FAKE-FAVICON-001"],
        "source_id": "SRC-008", "first_seen": "2026-06-05", "last_seen": "2026-08-24",
        "notes": "Full indicator agreement with SERVICE-001.",
    },
    {
        "clearnet_asset_id": "CLEAR-002", "hostname": "edge002.synthetic.example",
        "certificate_fingerprint": "FAKE-CERT-FP-021",
        "observed_indicators": ["FAKE-BANNER-004", "FAKE-FAVICON-002"],
        "source_id": "SRC-008", "first_seen": "2026-06-11", "last_seen": "2026-08-25",
        "notes": "Shared hosting-style overlap: matches SERVICE-002 and SERVICE-004 on banner and favicon only, certificate differs.",
    },
    {
        "clearnet_asset_id": "CLEAR-003", "hostname": "relay003.synthetic.example",
        "certificate_fingerprint": "FAKE-CERT-FP-003",
        "observed_indicators": ["FAKE-CERT-FP-003"],
        "source_id": "SRC-008", "first_seen": "2026-06-18", "last_seen": "2026-08-22",
        "notes": "Certificate matches SERVICE-003; no other indicator observed.",
    },
    {
        "clearnet_asset_id": "CLEAR-004", "hostname": "host004.synthetic.example",
        "certificate_fingerprint": "FAKE-CERT-FP-022",
        "observed_indicators": ["FAKE-SW-SIG-006"],
        "source_id": "SRC-008", "first_seen": "2026-06-22", "last_seen": "2026-08-20",
        "notes": "Only a common software signature matches SERVICE-006 - weak on its own.",
    },
    {
        "clearnet_asset_id": "CLEAR-005", "hostname": "mirror005.synthetic.example",
        "certificate_fingerprint": "FAKE-CERT-FP-023",
        "observed_indicators": ["FAKE-BANNER-023"],
        "source_id": "SRC-008", "first_seen": "2026-07-02", "last_seen": "2026-08-19",
        "notes": "Negative control: no overlap with any hidden service in the dataset.",
    },
    {
        "clearnet_asset_id": "CLEAR-006", "hostname": "gateway006.synthetic.example",
        "certificate_fingerprint": "FAKE-CERT-FP-024",
        "observed_indicators": ["FAKE-FAVICON-008"],
        "source_id": "SRC-008", "first_seen": "2026-06-09", "last_seen": "2026-08-25",
        "notes": "Favicon matches SERVICE-008; certificate and banner differ.",
    },
]

# --------------------------------------------------------------------------
# IDENTIFIER OBSERVATIONS
# (identifier_type, value, persona_id, source_id, first_seen, last_seen, status)
# Reuse across personas is expressed as separate observation records with the
# same value - that is what makes deterministic matching testable.
# --------------------------------------------------------------------------
IDENTIFIER_PLAN = [
    # --- handles (one observation per persona/source pair) ---
    ("handle", "shadowvendor", "PERSONA-001", "SRC-003", "2026-06-02", "2026-07-05", "stale"),
    ("handle", "shadowvendor", "PERSONA-001", "SRC-006", "2026-07-08", "2026-07-08", "stale"),
    ("handle", "redfox77", "PERSONA-002", "SRC-001", "2026-06-03", "2026-07-28", "stale"),
    ("handle", "cryptowolf", "PERSONA-003", "SRC-001", "2026-06-05", "2026-08-22", "active"),
    ("handle", "darkknight99", "PERSONA-004", "SRC-003", "2026-07-19", "2026-08-24", "active"),
    ("handle", "darkknight99", "PERSONA-004", "SRC-001", "2026-07-26", "2026-08-21", "active"),
    ("handle", "neonbroker", "PERSONA-005", "SRC-003", "2026-06-02", "2026-08-23", "active"),
    ("handle", "neonbroker", "PERSONA-005", "SRC-004", "2026-07-10", "2026-08-23", "active"),
    ("handle", "greycartel", "PERSONA-006", "SRC-002", "2026-06-04", "2026-07-30", "stale"),
    ("handle", "bytefox", "PERSONA-007", "SRC-002", "2026-08-06", "2026-08-25", "active"),
    ("handle", "silentbuyer", "PERSONA-008", "SRC-004", "2026-06-06", "2026-07-12", "stale"),
    ("handle", "quartzmule", "PERSONA-009", "SRC-005", "2026-06-10", "2026-08-18", "active"),
    ("handle", "pinegrove_admin", "PERSONA-010", "SRC-001", "2026-06-01", "2026-08-25", "active"),
    ("handle", "pinegrove_admin", "PERSONA-010", "SRC-002", "2026-06-01", "2026-08-25", "active"),
    ("handle", "nightmerchant", "PERSONA-011", "SRC-004", "2026-06-20", "2026-08-20", "active"),
    ("handle", "hollowtide", "PERSONA-012", "SRC-004", "2026-08-02", "2026-08-25", "active"),
    ("handle", "hollowtide", "PERSONA-012", "SRC-007", "2026-08-04", "2026-08-25", "active"),
    ("handle", "silentnode", "PERSONA-013", "SRC-005", "2026-06-15", "2026-08-25", "active"),
    ("handle", "emberlark", "PERSONA-014", "SRC-006", "2026-06-25", "2026-08-21", "active"),
    ("handle", "tinvault", "PERSONA-015", "SRC-004", "2026-06-08", "2026-08-23", "active"),
    ("handle", "brasspetal", "PERSONA-016", "SRC-006", "2026-06-12", "2026-08-15", "active"),
    ("handle", "lowtidefox", "PERSONA-017", "SRC-002", "2026-07-05", "2026-08-25", "active"),
    ("handle", "mistcaller", "PERSONA-018", "SRC-005", "2026-07-01", "2026-08-19", "active"),

    # --- PGP fingerprints (all obviously synthetic) ---
    # ACTOR-001: same key across the rebrand -> strongest identifier evidence in the set
    ("pgp_fingerprint", "FAKE-PGP-001", "PERSONA-001", "SRC-003", "2026-06-02", "2026-07-04", "stale"),
    ("pgp_fingerprint", "FAKE-PGP-001", "PERSONA-004", "SRC-003", "2026-07-19", "2026-08-24", "active"),
    ("pgp_fingerprint", "FAKE-PGP-014", "PERSONA-011", "SRC-004", "2026-06-20", "2026-08-20", "active"),
    # ACTOR-002: rotated keys - no PGP overlap between the two personas
    ("pgp_fingerprint", "FAKE-PGP-002", "PERSONA-002", "SRC-001", "2026-06-03", "2026-07-28", "stale"),
    ("pgp_fingerprint", "FAKE-PGP-007", "PERSONA-007", "SRC-002", "2026-08-06", "2026-08-25", "active"),
    ("pgp_fingerprint", "FAKE-PGP-003", "PERSONA-003", "SRC-001", "2026-06-05", "2026-08-22", "active"),
    # ACTOR-004: identical key on both marketplaces
    ("pgp_fingerprint", "FAKE-PGP-005", "PERSONA-005", "SRC-003", "2026-06-02", "2026-08-23", "active"),
    ("pgp_fingerprint", "FAKE-PGP-005", "PERSONA-005", "SRC-004", "2026-07-10", "2026-08-23", "active"),
    ("pgp_fingerprint", "FAKE-PGP-006", "PERSONA-006", "SRC-002", "2026-06-04", "2026-07-30", "stale"),
    ("pgp_fingerprint", "FAKE-PGP-013", "PERSONA-013", "SRC-005", "2026-06-15", "2026-08-25", "active"),
    # ACTOR-006: near-miss variation across the rebrand (partial identifier variation)
    ("pgp_fingerprint", "FAKE-PGP-008", "PERSONA-008", "SRC-004", "2026-06-06", "2026-07-12", "stale"),
    ("pgp_fingerprint", "FAKE-PGP-008-B", "PERSONA-012", "SRC-004", "2026-08-02", "2026-08-25", "active"),
    ("pgp_fingerprint", "FAKE-PGP-010", "PERSONA-010", "SRC-001", "2026-06-01", "2026-08-25", "active"),
    # ACTOR-009: identical key across two personas with very different writing styles
    ("pgp_fingerprint", "FAKE-PGP-015", "PERSONA-015", "SRC-004", "2026-06-08", "2026-08-23", "active"),
    ("pgp_fingerprint", "FAKE-PGP-015", "PERSONA-017", "SRC-002", "2026-07-05", "2026-08-25", "active"),
    ("pgp_fingerprint", "FAKE-PGP-016", "PERSONA-016", "SRC-006", "2026-07-19", "2026-07-19", "single_observation"),
    ("pgp_fingerprint", "FAKE-PGP-018", "PERSONA-018", "SRC-005", "2026-07-01", "2026-08-19", "active"),

    # --- wallet identifiers (synthetic placeholders, not address-shaped) ---
    ("wallet", "SYN-WALLET-BTC-001", "PERSONA-001", "SRC-003", "2026-06-04", "2026-07-05", "stale"),
    ("wallet", "SYN-WALLET-BTC-001", "PERSONA-004", "SRC-003", "2026-07-21", "2026-08-24", "active"),
    ("wallet", "SYN-WALLET-BTC-009", "PERSONA-011", "SRC-004", "2026-06-22", "2026-07-30", "stale"),
    ("wallet", "SYN-WALLET-XMR-002", "PERSONA-002", "SRC-001", "2026-06-05", "2026-07-28", "stale"),
    ("wallet", "SYN-WALLET-BTC-003", "PERSONA-003", "SRC-001", "2026-06-09", "2026-08-22", "active"),
    ("wallet", "SYN-WALLET-BTC-005", "PERSONA-005", "SRC-003", "2026-06-06", "2026-08-23", "active"),
    ("wallet", "SYN-WALLET-BTC-005", "PERSONA-005", "SRC-004", "2026-07-12", "2026-08-23", "active"),
    ("wallet", "SYN-WALLET-BTC-006", "PERSONA-006", "SRC-002", "2026-06-07", "2026-07-30", "stale"),
    ("wallet", "SYN-WALLET-BTC-013", "PERSONA-013", "SRC-005", "2026-06-18", "2026-08-25", "active"),
    ("wallet", "SYN-WALLET-BTC-008", "PERSONA-008", "SRC-004", "2026-06-08", "2026-07-12", "stale"),
    ("wallet", "SYN-WALLET-BTC-012", "PERSONA-012", "SRC-004", "2026-08-03", "2026-08-25", "active"),
    ("wallet", "SYN-WALLET-BTC-010", "PERSONA-010", "SRC-001", "2026-06-01", "2026-08-25", "active"),
    # ACTOR-009: shared wallet is the only bridge to the minimalist paste persona
    ("wallet", "SYN-WALLET-XMR-015", "PERSONA-015", "SRC-004", "2026-06-10", "2026-08-23", "active"),
    ("wallet", "SYN-WALLET-XMR-015", "PERSONA-016", "SRC-006", "2026-06-14", "2026-08-15", "active"),
    ("wallet", "SYN-WALLET-BTC-017", "PERSONA-017", "SRC-002", "2026-07-07", "2026-08-25", "active"),
    ("wallet", "SYN-WALLET-BTC-018", "PERSONA-018", "SRC-005", "2026-07-03", "2026-08-19", "active"),

    # --- contact / email-like identifiers (synthetic.example only) ---
    ("email", "contact-ferry@synthetic.example", "PERSONA-001", "SRC-003", "2026-06-03", "2026-07-05", "stale"),
    ("email", "contact-ferry@synthetic.example", "PERSONA-011", "SRC-004", "2026-06-21", "2026-08-20", "active"),
    ("email", "contact-actor-002@synthetic.example", "PERSONA-002", "SRC-001", "2026-06-04", "2026-07-28", "stale"),
    ("email", "contact-actor-002@synthetic.example", "PERSONA-007", "SRC-002", "2026-08-07", "2026-08-12", "stale"),
    ("email", "broker-desk@synthetic.example", "PERSONA-005", "SRC-003", "2026-06-05", "2026-08-23", "active"),
    ("email", "relay-desk@synthetic.example", "PERSONA-010", "SRC-001", "2026-06-02", "2026-08-25", "active"),
    ("email", "tide-inbox@synthetic.example", "PERSONA-012", "SRC-004", "2026-08-05", "2026-08-25", "active"),
    ("email", "vault-inbox@synthetic.example", "PERSONA-015", "SRC-004", "2026-06-11", "2026-08-23", "active"),
    ("email", "mule-inbox@synthetic.example", "PERSONA-009", "SRC-005", "2026-06-13", "2026-08-18", "active"),

    # --- aliases / signature strings ---
    ("alias", "sv", "PERSONA-001", "SRC-003", "2026-06-02", "2026-07-05", "stale"),
    ("alias", "dk99", "PERSONA-004", "SRC-003", "2026-07-19", "2026-08-24", "active"),
    ("alias", "nm", "PERSONA-011", "SRC-004", "2026-06-20", "2026-08-20", "active"),
    ("alias", "fx", "PERSONA-002", "SRC-001", "2026-06-03", "2026-07-28", "stale"),
    ("alias", "fx", "PERSONA-007", "SRC-002", "2026-08-06", "2026-08-25", "active"),
    ("alias", "lowfx", "PERSONA-017", "SRC-002", "2026-07-05", "2026-08-25", "active"),
    ("alias", "wolf", "PERSONA-003", "SRC-001", "2026-06-05", "2026-08-22", "active"),
    ("alias", "grey", "PERSONA-006", "SRC-002", "2026-06-04", "2026-07-30", "stale"),
    ("alias", "node", "PERSONA-013", "SRC-005", "2026-06-15", "2026-08-25", "active"),
    ("alias", "tide", "PERSONA-012", "SRC-004", "2026-08-02", "2026-08-25", "active"),
    ("alias", "vault", "PERSONA-015", "SRC-004", "2026-06-08", "2026-08-23", "active"),
]

# --------------------------------------------------------------------------
# EVALUATION PAIRS (ground truth - evaluation file only)
# --------------------------------------------------------------------------
# label options: SAME_ACTOR | DIFFERENT_ACTOR | SAME_TOPIC_DIFFERENT_STYLE |
#                DIFFERENT_TOPIC_SIMILAR_STYLE | AMBIGUOUS | UNRELATED
# expected strength: HIGH_EXPECTED | MEDIUM_EXPECTED | LOW_EXPECTED | INSUFFICIENT
EVALUATION_PAIRS = [
    ("PERSONA-001", "PERSONA-004", "SAME_ACTOR", "HIGH", "CONSISTENT", "STRONG", "SHARED", "HIGH_EXPECTED",
     "Rebrand of the same synthetic actor: identical PGP and wallet, identical style archetype and idiolect, same posting hours, 14-day migration gap.", "SCENARIO-01"),
    ("PERSONA-004", "PERSONA-011", "SAME_ACTOR", "HIGH", "PARTIAL", "PARTIAL", "NONE", "MEDIUM_EXPECTED",
     "Same synthetic actor operating two concurrent personas on different marketplaces; style and idiolect agree, key material and wallets differ, only a shared contact address bridges them.", "SCENARIO-11"),
    ("PERSONA-001", "PERSONA-011", "SAME_ACTOR", "HIGH", "PARTIAL", "PARTIAL", "NONE", "MEDIUM_EXPECTED",
     "Same synthetic actor; overlapping active windows and shared contact address, but no shared key or wallet.", "SCENARIO-11"),
    ("PERSONA-002", "PERSONA-007", "SAME_ACTOR", "HIGH", "CONSISTENT", "WEAK", "SHARED", "MEDIUM_EXPECTED",
     "Same synthetic actor with rotated key material and no shared wallet; only a stale contact address overlaps. Style and schedule agree.", "SCENARIO-02"),
    ("PERSONA-008", "PERSONA-012", "SAME_ACTOR", "HIGH", "CONSISTENT", "PARTIAL", "SHARED", "HIGH_EXPECTED",
     "Rebrand on the same hidden service after a 21-day gap; near-miss PGP variation, identical style archetype, identical posting hours.", "SCENARIO-01"),
    ("PERSONA-006", "PERSONA-013", "SAME_ACTOR", "HIGH", "CONFLICTING", "NONE", "NONE", "MEDIUM_EXPECTED",
     "Same synthetic actor, near-identical style, but concurrent activity on opposite schedules and no shared identifiers. Style and timing disagree by design.", "SCENARIO-08"),
    ("PERSONA-015", "PERSONA-017", "SAME_ACTOR", "LOW", "PARTIAL", "STRONG", "SHARED", "MEDIUM_EXPECTED",
     "Same synthetic actor with a shared PGP but deliberately different writing registers - identifier evidence must outweigh a negative stylometric signal.", "SCENARIO-07"),
    ("PERSONA-015", "PERSONA-016", "SAME_ACTOR", "LOW", "PARTIAL", "STRONG", "NONE", "MEDIUM_EXPECTED",
     "Same synthetic actor bridged only by a shared wallet; the second persona is a minimalist paste account with little usable text.", "SCENARIO-07"),
    ("PERSONA-009", "PERSONA-014", "SAME_ACTOR", "INSUFFICIENT", "PARTIAL", "NONE", "NONE", "INSUFFICIENT",
     "Same synthetic actor, but both personas post one-line messages only - deliberately below any reasonable stylometric data-sufficiency threshold.", "SCENARIO-09"),
    ("PERSONA-003", "PERSONA-017", "SAME_TOPIC_DIFFERENT_STYLE", "LOW", "PARTIAL", "NONE", "NONE", "LOW_EXPECTED",
     "Different synthetic actors discussing the same service category in clearly different registers.", "SCENARIO-03"),
    ("PERSONA-009", "PERSONA-015", "SAME_TOPIC_DIFFERENT_STYLE", "LOW", "PARTIAL", "NONE", "NONE", "LOW_EXPECTED",
     "Different synthetic actors on the same topic; minimalist versus ellipsis-heavy register.", "SCENARIO-03"),
    ("PERSONA-006", "PERSONA-018", "SAME_TOPIC_DIFFERENT_STYLE", "LOW", "PARTIAL", "NONE", "NONE", "LOW_EXPECTED",
     "Different synthetic actors in adjacent fraud categories with sharply different punctuation habits.", "SCENARIO-03"),
    ("PERSONA-001", "PERSONA-015", "DIFFERENT_TOPIC_SIMILAR_STYLE", "HIGH", "PARTIAL", "NONE", "NONE", "LOW_EXPECTED",
     "Primary false-positive candidate: different synthetic actors sharing STYLE-A, different topics, no shared identifiers, partially overlapping hours.", "SCENARIO-04"),
    ("PERSONA-002", "PERSONA-017", "DIFFERENT_TOPIC_SIMILAR_STYLE", "HIGH", "CONFLICTING", "NONE", "NONE", "LOW_EXPECTED",
     "Different synthetic actors sharing STYLE-D across different topics; schedules do not overlap.", "SCENARIO-04"),
    ("PERSONA-003", "PERSONA-010", "DIFFERENT_TOPIC_SIMILAR_STYLE", "MEDIUM", "PARTIAL", "NONE", "NONE", "LOW_EXPECTED",
     "Different synthetic actors sharing a formal register; one is a moderator persona, the other a service advertiser.", "SCENARIO-04"),
    ("PERSONA-005", "PERSONA-012", "AMBIGUOUS", "LOW", "CONSISTENT", "NONE", "PARTIAL", "LOW_EXPECTED",
     "Different synthetic actors whose services share a banner and favicon (shared-hosting-style overlap) and whose posting hours coincide; identifiers and style disagree.", "SCENARIO-06"),
    ("PERSONA-011", "PERSONA-013", "DIFFERENT_ACTOR", "LOW", "CONSISTENT", "NONE", "NONE", "LOW_EXPECTED",
     "Different synthetic actors with strongly overlapping late-night posting windows but different styles and no shared identifiers.", "SCENARIO-05"),
    ("PERSONA-006", "PERSONA-010", "DIFFERENT_ACTOR", "LOW", "CONSISTENT", "NONE", "NONE", "LOW_EXPECTED",
     "Different synthetic actors connected only by interacting with the same moderator hub on the same board.", "SCENARIO-03"),
    ("PERSONA-004", "PERSONA-002", "DIFFERENT_ACTOR", "LOW", "CONFLICTING", "NONE", "NONE", "LOW_EXPECTED",
     "Different synthetic actors, different styles, non-overlapping schedules, no shared identifiers.", "SCENARIO-10"),
    ("PERSONA-012", "PERSONA-018", "UNRELATED", "LOW", "CONFLICTING", "NONE", "NONE", "LOW_EXPECTED",
     "Negative control pair.", "SCENARIO-10"),
    ("PERSONA-005", "PERSONA-016", "UNRELATED", "LOW", "CONFLICTING", "NONE", "NONE", "LOW_EXPECTED",
     "Negative control pair.", "SCENARIO-10"),
    ("PERSONA-003", "PERSONA-011", "UNRELATED", "LOW", "CONFLICTING", "NONE", "NONE", "LOW_EXPECTED",
     "Negative control pair.", "SCENARIO-10"),
    ("PERSONA-007", "PERSONA-014", "UNRELATED", "INSUFFICIENT", "PARTIAL", "NONE", "NONE", "INSUFFICIENT",
     "Negative control pair where one side has almost no usable text.", "SCENARIO-09"),
    ("PERSONA-008", "PERSONA-016", "UNRELATED", "LOW", "CONFLICTING", "NONE", "NONE", "LOW_EXPECTED",
     "Negative control pair.", "SCENARIO-10"),
    ("PERSONA-010", "PERSONA-018", "SAME_ACTOR", "LOW", "PARTIAL", "NONE", "SHARED", "LOW_EXPECTED",
     "Hard same-actor case: one moderator persona and one discussion persona of the same synthetic actor, sharing only a hidden service and no identifiers, in different registers.", "SCENARIO-06"),
]

# --------------------------------------------------------------------------
# INFRASTRUCTURE GROUND TRUTH (evaluation only)
# --------------------------------------------------------------------------
INFRA_GROUND_TRUTH = [
    ("SERVICE-001", "CLEAR-001", "SAME_INFRASTRUCTURE",
     "Certificate, banner and favicon all agree; designed as the strong positive clearnet correlation."),
    ("SERVICE-003", "CLEAR-003", "POSSIBLE_SHARED_INFRASTRUCTURE",
     "Certificate matches but no second indicator corroborates it."),
    ("SERVICE-002", "SERVICE-004", "POSSIBLE_SHARED_INFRASTRUCTURE",
     "Banner and favicon shared between two services operated by different synthetic actors - a shared-hosting-style artefact, not co-ownership."),
    ("SERVICE-002", "CLEAR-002", "POSSIBLE_SHARED_INFRASTRUCTURE",
     "Banner and favicon match, certificate differs."),
    ("SERVICE-004", "CLEAR-002", "POSSIBLE_SHARED_INFRASTRUCTURE",
     "Banner and favicon match, certificate differs."),
    ("SERVICE-006", "CLEAR-004", "POSSIBLE_SHARED_INFRASTRUCTURE",
     "Only a common software signature matches; weak on its own."),
    ("SERVICE-008", "CLEAR-006", "POSSIBLE_SHARED_INFRASTRUCTURE",
     "Favicon matches, certificate and banner differ."),
    ("SERVICE-005", "CLEAR-005", "DIFFERENT_INFRASTRUCTURE",
     "Negative control: no indicator overlap."),
    ("SERVICE-001", "SERVICE-006", "DIFFERENT_INFRASTRUCTURE",
     "Negative control: no indicator overlap."),
    ("SERVICE-007", "SERVICE-008", "DIFFERENT_INFRASTRUCTURE",
     "Negative control: no indicator overlap."),
    ("SERVICE-001", "SERVICE-003", "DIFFERENT_INFRASTRUCTURE",
     "Negative control: no indicator overlap."),
]

# --------------------------------------------------------------------------
# SCENARIO REGISTRY (evaluation only)
# --------------------------------------------------------------------------
SCENARIOS = {
    "SCENARIO-01": "Same actor, different persona, same PGP and wallet, similar style, migration gap.",
    "SCENARIO-02": "Same actor, different persona, similar style, no shared wallet.",
    "SCENARIO-03": "Different actors, same topic, different style.",
    "SCENARIO-04": "Different actors, similar style, different identifiers.",
    "SCENARIO-05": "Different actors, similar posting time, different style.",
    "SCENARIO-06": "Possible infrastructure overlap with ambiguous identity.",
    "SCENARIO-07": "Strong identifier evidence, weak behavioural or stylometric evidence.",
    "SCENARIO-08": "Strong stylometric evidence with conflicting behavioural or identifier evidence.",
    "SCENARIO-09": "Short-text account pair with insufficient stylometric evidence.",
    "SCENARIO-10": "Completely unrelated accounts.",
    "SCENARIO-11": "One actor with three personas across multiple sources.",
    "SCENARIO-12": "One persona appearing across multiple sources under the same handle.",
}

# --------------------------------------------------------------------------
# MIGRATION GROUND TRUTH (evaluation only)
# --------------------------------------------------------------------------
MIGRATIONS = [
    {
        "migration_id": "MIG-001", "actor_id": "ACTOR-001",
        "from_persona": "PERSONA-001", "to_persona": "PERSONA-004",
        "from_last_active": "2026-07-05", "to_first_active": "2026-07-19",
        "gap_days": 14, "migration_type": "REBRAND_SAME_SOURCE",
        "notes": "Closing notice posted, account left dormant, new handle appears on the same marketplace with the same key material.",
    },
    {
        "migration_id": "MIG-002", "actor_id": "ACTOR-002",
        "from_persona": "PERSONA-002", "to_persona": "PERSONA-007",
        "from_last_active": "2026-07-28", "to_first_active": "2026-08-06",
        "gap_days": 9, "migration_type": "REBRAND_CROSS_SOURCE",
        "notes": "Moves from ForumAlpha to ForumBeta with rotated key material; only a stale contact address carries over.",
    },
    {
        "migration_id": "MIG-003", "actor_id": "ACTOR-006",
        "from_persona": "PERSONA-008", "to_persona": "PERSONA-012",
        "from_last_active": "2026-07-12", "to_first_active": "2026-08-02",
        "gap_days": 21, "migration_type": "REBRAND_SAME_SERVICE",
        "notes": "Same hidden service and support panel; PGP value varies by a single suffix.",
    },
    {
        "migration_id": "MIG-004", "actor_id": "ACTOR-004",
        "from_persona": "PERSONA-005", "to_persona": "PERSONA-005",
        "from_last_active": "2026-08-23", "to_first_active": "2026-07-10",
        "gap_days": 0, "migration_type": "SOURCE_EXPANSION_SAME_HANDLE",
        "notes": "Not a rebrand: the same handle and key material simply appear on a second marketplace from 2026-07-10.",
    },
]

# --------------------------------------------------------------------------
# INVESTIGATION CASES
# --------------------------------------------------------------------------
CASES = [
    {
        "case_id": "CASE-001",
        "title": "Possible migration from shadowvendor to darkknight99",
        "analyst_question": "Did the shadowvendor account stop trading, or did it continue under a new handle on the same marketplace?",
        "target_personas": ["PERSONA-001", "PERSONA-004"],
        "timeline_window": ["2026-06-02", "2026-08-24"],
        "priority": "HIGH",
        "expected_final_assessment": "STRONG_POSITIVE",
        "expectation_notes": "All four evidence families agree: identical key material, identical wallet, same style archetype and idiolect, same posting hours, 14-day gap. This is the reference strong-positive case.",
    },
    {
        "case_id": "CASE-002",
        "title": "Possible infrastructure reuse between the Wren support panel and the Meridian broker desk",
        "analyst_question": "Do the two hidden services share an operator, or only a hosting environment?",
        "target_personas": ["PERSONA-005", "PERSONA-012"],
        "target_services": ["SERVICE-002", "SERVICE-004"],
        "timeline_window": ["2026-06-04", "2026-08-25"],
        "priority": "MEDIUM",
        "expected_final_assessment": "AMBIGUOUS",
        "expectation_notes": "Banner and favicon overlap plus coinciding posting hours, against differing certificates, differing key material and differing style. Should not resolve to a positive link.",
    },
    {
        "case_id": "CASE-003",
        "title": "Shared wallet identifier across MarketDelta and PasteVault",
        "analyst_question": "Is the paste-drop account operated by the same party as the MarketDelta transfer account?",
        "target_personas": ["PERSONA-015", "PERSONA-016"],
        "timeline_window": ["2026-06-08", "2026-08-23"],
        "priority": "MEDIUM",
        "expected_final_assessment": "WEAK_POSITIVE",
        "expectation_notes": "A single shared wallet observation on a LOW-reliability source, with almost no text on one side. Correct behaviour is a weak positive, not a confident link.",
    },
    {
        "case_id": "CASE-004",
        "title": "Stylometric similarity with conflicting temporal evidence: greycartel and silentnode",
        "analyst_question": "Two accounts write almost identically but are active at opposite ends of the day. Same operator or not?",
        "target_personas": ["PERSONA-006", "PERSONA-013"],
        "timeline_window": ["2026-06-04", "2026-08-25"],
        "priority": "HIGH",
        "expected_final_assessment": "CONFLICTING_EVIDENCE",
        "expectation_notes": "Ground truth is same actor, but the temporal signal actively contradicts it. Tests that fusion neither ignores the conflict nor lets it veto a strong stylometric signal.",
    },
    {
        "case_id": "CASE-005",
        "title": "False-positive check: shadowvendor and tinvault",
        "analyst_question": "Two accounts share a distinctive writing style. Is that enough?",
        "target_personas": ["PERSONA-001", "PERSONA-015"],
        "timeline_window": ["2026-06-02", "2026-08-23"],
        "priority": "MEDIUM",
        "expected_final_assessment": "FALSE_POSITIVE_CANDIDATE",
        "expectation_notes": "Same style archetype, different actors, different idiolect markers, different topics, no shared identifiers or infrastructure. Should be rejected or heavily discounted.",
    },
    {
        "case_id": "CASE-006",
        "title": "Insufficient evidence: quartzmule and emberlark",
        "analyst_question": "Can anything be concluded about two very low-volume accounts?",
        "target_personas": ["PERSONA-009", "PERSONA-014"],
        "timeline_window": ["2026-06-10", "2026-08-21"],
        "priority": "LOW",
        "expected_final_assessment": "INSUFFICIENT_EVIDENCE",
        "expectation_notes": "Ground truth is same actor, but the dataset deliberately withholds enough text or identifiers to support that. The correct output is an explicit insufficiency verdict.",
    },
    {
        "case_id": "CASE-007",
        "title": "Cross-marketplace identity under one handle: neonbroker",
        "analyst_question": "Is the neonbroker account on MarketDelta the same account as on MarketGamma, or a squatter?",
        "target_personas": ["PERSONA-005"],
        "timeline_window": ["2026-06-02", "2026-08-23"],
        "priority": "MEDIUM",
        "expected_final_assessment": "STRONG_POSITIVE",
        "expectation_notes": "Identical handle, identical PGP and identical wallet observed on both marketplaces with continuous activity - the clean cross-source identity case.",
    },
    {
        "case_id": "CASE-008",
        "title": "Rebrand across a three-week silence: silentbuyer to hollowtide",
        "analyst_question": "Did the abandoned silentbuyer account return under a new handle?",
        "target_personas": ["PERSONA-008", "PERSONA-012"],
        "target_services": ["SERVICE-004"],
        "timeline_window": ["2026-06-06", "2026-08-25"],
        "priority": "HIGH",
        "expected_final_assessment": "STRONG_POSITIVE",
        "expectation_notes": "Same hidden service across the gap, near-miss key variation, identical style archetype and posting hours. The main temporal-graph demo case.",
    },
]

# PS 26151 capabilities this dataset is designed to exercise.
SUPPORTED_PS_REQUIREMENTS = [
    "multi_source_footprint_collection",
    "marketplace_forum_deepweb_sources",
    "handle_and_persona_identification",
    "pgp_key_tracking",
    "wallet_identifier_tracking",
    "hidden_service_infrastructure_indicators",
    "clearnet_infrastructure_correlation",
    "cross_marketplace_actor_mapping",
    "relationship_graph_construction",
    "stylometric_persona_identification",
    "behavioural_profiling",
    "rebranded_and_migrated_persona_linking",
    "timeline_based_investigation",
    "attribution_confidence_evaluation",
    "source_and_reliability_metadata",
    "actor_profiles",
    "category_classification",
    "first_seen_last_seen",
    "last_scan_date",
    "csv_json_report_export",
    "fact_inference_hypothesis_separation",
]
