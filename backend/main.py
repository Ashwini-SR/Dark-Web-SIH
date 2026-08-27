"""
VEIL-ATLAS backend API
------------------------
Run with:
    uvicorn main:app --reload --port 8000

Endpoints:
    GET  /personas                 -> list all personas
    GET  /correlate?a=X&b=Y        -> full evidence + confidence for a pair
    GET  /graph?threshold=0.5      -> all pairs above threshold, as a graph
"""

import json
import os
from itertools import combinations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import stylolink
import chrono
from ledger import EvidenceItem, aggregate

app = FastAPI(title="VEIL-ATLAS API")

# Allow the plain HTML/JS frontend (served from anywhere/file://) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "personas.json")

with open(DATA_PATH) as f:
    PERSONAS = json.load(f)

# Pre-build stylometric profiles once at startup
STYLE_PROFILES = {
    pid: stylolink.build_profile(pid, [post["text"] for post in pdata["posts"]])
    for pid, pdata in PERSONAS.items()
}


def _correlate_pair(a_id: str, b_id: str) -> dict:
    if a_id not in PERSONAS or b_id not in PERSONAS:
        raise HTTPException(status_code=404, detail="persona not found")

    stylo_result = stylolink.compare_personas(STYLE_PROFILES[a_id], STYLE_PROFILES[b_id])
    chrono_result = chrono.compare_personas(
        a_id, PERSONAS[a_id]["posts"],
        b_id, PERSONAS[b_id]["posts"],
    )

    evidence = [
        EvidenceItem(
            source="StyloLink",
            evidence_type="INFERENCE",
            score=stylo_result["score"],
            reasons=stylo_result["reasons"],
        ),
        EvidenceItem(
            source="Chrono-Graph",
            evidence_type="INFERENCE",
            score=chrono_result["score"],
            reasons=chrono_result["reasons"],
        ),
    ]

    ledger_result = aggregate(evidence)

    return {
        "persona_a": a_id,
        "persona_b": b_id,
        "confidence": ledger_result["confidence"],
        "label": ledger_result["label"],
        "derivation": ledger_result["derivation"],
    }


@app.get("/personas")
def list_personas():
    return [
        {
            "id": pid,
            "display_name": pdata["display_name"],
            "forum": pdata["forum"],
            "post_count": len(pdata["posts"]),
        }
        for pid, pdata in PERSONAS.items()
    ]


@app.get("/correlate")
def correlate(a: str, b: str):
    return _correlate_pair(a, b)


@app.get("/graph")
def graph(threshold: float = 0.5):
    nodes = [
        {"id": pid, "label": pdata["display_name"], "forum": pdata["forum"]}
        for pid, pdata in PERSONAS.items()
    ]
    edges = []
    for a_id, b_id in combinations(PERSONAS.keys(), 2):
        result = _correlate_pair(a_id, b_id)
        if result["confidence"] >= threshold:
            edges.append(result)
    return {"nodes": nodes, "edges": edges}
