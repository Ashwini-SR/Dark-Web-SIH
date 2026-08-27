"""
FIH-Ledger -- Fact / Inference / Hypothesis confidence engine
-----------------------------------------------------------------
This is VEIL-ATLAS's core differentiator. It never claims two personas
"are" the same entity. It takes typed evidence objects from independent
correlation engines (StyloLink, Chrono-Graph, ...) and combines them into
a single, fully-explainable confidence score with a labeled derivation
chain -- exactly what an investigator (or an NTRO judge) needs to trust
and act on an output.

Design choice: a transparent weighted-average + label system instead of a
black-box ML classifier. This is deliberate -- explainability is a stated
requirement of the problem statement, and a simple, auditable formula is
easier to defend under questioning than a neural net you can't fully explain.
"""

from dataclasses import dataclass, field


# Evidence "type" tiers -- deterministic identifier matches would be FACT,
# our current engines (stylometry, timing) produce INFERENCE-tier evidence.
EVIDENCE_TYPES = ("FACT", "INFERENCE", "HYPOTHESIS")

# How much each source contributes to the final confidence score.
# Tune these numbers as you add more engines (e.g. TrustWeb, ID-Fusion).
SOURCE_WEIGHTS = {
    "StyloLink": 0.55,
    "Chrono-Graph": 0.45,
}

CONFIDENCE_LABELS = [
    (0.80, "HIGH confidence hypothesis"),
    (0.55, "MODERATE confidence hypothesis"),
    (0.30, "LOW confidence hypothesis"),
    (0.0, "INSUFFICIENT evidence"),
]


@dataclass
class EvidenceItem:
    source: str
    evidence_type: str  # one of EVIDENCE_TYPES
    score: float         # 0-1
    reasons: list = field(default_factory=list)


def label_for(score: float) -> str:
    for threshold, label in CONFIDENCE_LABELS:
        if score >= threshold:
            return label
    return "INSUFFICIENT evidence"


def aggregate(evidence_items: list[EvidenceItem]) -> dict:
    """
    Combine multiple evidence items into one explainable confidence score.
    Returns the full derivation chain, not just a number, so the frontend
    can show investigators exactly why the system believes what it believes.
    """
    if not evidence_items:
        return {
            "confidence": 0.0,
            "label": "INSUFFICIENT evidence",
            "derivation": [],
        }

    weighted_sum = 0.0
    weight_total = 0.0
    derivation = []

    for item in evidence_items:
        weight = SOURCE_WEIGHTS.get(item.source, 1.0 / len(evidence_items))
        contribution = weight * item.score
        weighted_sum += contribution
        weight_total += weight

        derivation.append({
            "source": item.source,
            "type": item.evidence_type,
            "raw_score": round(item.score, 3),
            "weight": weight,
            "contribution": round(contribution, 3),
            "reasons": item.reasons,
        })

    confidence = round(weighted_sum / weight_total, 3) if weight_total else 0.0

    return {
        "confidence": confidence,
        "label": label_for(confidence),
        "derivation": derivation,
    }
