# VEIL·ATLAS — Working Prototype v0.1

Mapping the shadows, one evidence-backed edge at a time.

This is a **working skeleton**, not a toy mockup — it's already correctly
distinguishing linked personas from unrelated ones using real (if simple)
stylometric + temporal analysis, aggregated through an explainable
confidence engine. Everything below runs today, in under 2 minutes of setup.

## What's implemented right now

- `data/generate_dataset.py` — generates a legal, self-authored synthetic dataset
  of 5 "personas" across 2 fake forums, with two personas deliberately linked
  by writing style + a realistic migration-timing pattern.
- `backend/stylolink.py` — stylometric similarity engine (function-word usage,
  punctuation habits, sentence length + TF-IDF content similarity), fully explainable.
- `backend/chrono.py` — temporal correlation: posting-hour similarity + "migration
  handover" detection (persona A goes quiet right as persona B appears).
- `backend/ledger.py` — the FIH-Ledger: combines evidence from multiple sources
  into ONE transparent, weighted confidence score with a full derivation chain.
  Never says "these are the same person" — only ever a labeled, explainable hypothesis.
- `backend/main.py` — FastAPI server exposing `/personas`, `/correlate`, `/graph`.
- `frontend/index.html` — investigator dashboard: interactive graph (click an
  edge to see the full evidence breakdown), confidence-colored links, threshold slider.

## How to run it (do this today)

```bash
# 1. Install dependencies (lightweight, no big downloads)
pip install -r requirements.txt

# 2. Generate the demo dataset
cd data
python3 generate_dataset.py
cd ..

# 3. Start the backend
cd backend
uvicorn main:app --reload --port 8000
# leave this running in its own terminal

# 4. Open the frontend
# just double-click frontend/index.html, or serve it:
cd ../frontend
python3 -m http.server 8080
# then open http://localhost:8080 in your browser
```

You should see a graph with 5 persona nodes. `shadowvendor` and `darkknight_99`
will be connected with a ~85% "HIGH confidence" link — click it to see exactly
why (matching lowercase style, matching ellipsis habit, same odd posting hours,
9.9-day migration gap). Unrelated personas won't be linked at threshold 0.5.

## What each team member should build next (in priority order)

1. **Person 1 (data):** Optionally supplement the synthetic dataset with real,
   public academic dark-web research corpora (e.g. DUTA-10K) for a "validated
   against real data" claim — keep this as an addition, not a replacement, so
   the live demo stays reliable.
2. **Person 2 (StyloLink):** Add 2-3 more stylometric features (emoji usage,
   typo-pattern fingerprinting) — each new feature = another line in the
   evidence reasons list, which judges love seeing.
3. **Person 3 (Chrono-Graph):** Add a simple visual timeline (a horizontal bar
   per persona showing when they were active) — huge visual payoff, cheap to build.
4. **Person 4 (Ledger):** Add a 3rd evidence source — the easiest next win is
   **exact identifier matching** (shared PGP key string / shared wallet string /
   shared image hash) as a `FACT`-tier evidence type with weight ~0.9+, to show
   the fact/inference/hypothesis distinction in action, not just inference-only.
5. **Person 5 (Frontend):** Add the case-building panel (drag personas into a
   "case", export button for CSV/JSON/PDF) — this is what satisfies requirements
   #8 and #9 from the problem statement and is highly visible in a demo.
6. **Person 6 (Integration/PPT):** Wire a "Generate Report" button that dumps
   the derivation chain of all case links into a downloadable JSON/CSV, and
   build the PPT/demo script around the exact flow already working today.


