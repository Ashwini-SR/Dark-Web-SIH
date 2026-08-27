"""
Chrono-Graph -- temporal behavior correlation engine
------------------------------------------------------
Two independent signals, both explainable and cheap to compute:

1. Active-hours similarity: builds a 24-hour posting histogram per persona
   and compares them. People's sleep/wake cycles are hard to fully fake,
   so a shared unusual posting-hour pattern (e.g. always 1-3am) is a
   genuinely useful correlation signal.

2. Migration/handover detection: checks whether persona A's activity stops
   right around when persona B's activity starts -- a classic real-world
   rebranding pattern.
"""

from datetime import datetime
import math


def _parse_hours(posts: list[dict]) -> list[int]:
    return [datetime.fromisoformat(p["timestamp"]).hour for p in posts]


def _build_histogram(hours: list[int]) -> list[float]:
    """24-bucket normalized histogram of posting hours."""
    hist = [0] * 24
    for h in hours:
        hist[h] += 1
    total = sum(hist) or 1
    return [c / total for c in hist]


def _cosine(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1))
    n2 = math.sqrt(sum(b * b for b in v2))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)


def _get_span(posts: list[dict]):
    timestamps = [datetime.fromisoformat(p["timestamp"]) for p in posts]
    if not timestamps:
        return None, None
    return min(timestamps), max(timestamps)


def compare_personas(persona_a_id: str, posts_a: list[dict],
                      persona_b_id: str, posts_b: list[dict]) -> dict:
    reasons = []

    # --- signal 1: active-hours similarity ---
    hours_a = _parse_hours(posts_a)
    hours_b = _parse_hours(posts_b)
    hist_a = _build_histogram(hours_a)
    hist_b = _build_histogram(hours_b)
    hour_similarity = _cosine(hist_a, hist_b)

    if hour_similarity > 0.8:
        reasons.append("both personas post during the same unusual hours (possible shared timezone)")

    # --- signal 2: migration/handover timing ---
    start_a, end_a = _get_span(posts_a)
    start_b, end_b = _get_span(posts_b)

    handover_score = 0.0
    if end_a and start_b:
        gap_days = (start_b - end_a).total_seconds() / 86400.0
        # Strong signal if B starts shortly (0-21 days) after A stops.
        if 0 <= gap_days <= 21:
            handover_score = max(0.0, 1 - gap_days / 21.0)
            reasons.append(
                f"persona B appeared {gap_days:.1f} days after persona A went silent (possible migration)"
            )

    combined_score = round(0.5 * hour_similarity + 0.5 * handover_score, 3)

    if not reasons:
        reasons = ["no strong temporal correlation detected"]

    return {
        "source": "Chrono-Graph",
        "persona_a": persona_a_id,
        "persona_b": persona_b_id,
        "score": combined_score,
        "hour_similarity": round(hour_similarity, 3),
        "handover_score": round(handover_score, 3),
        "reasons": reasons,
    }
