# Cybit AI Ticket Triage & Runbook Copilot (PoC)

Classifies incoming service-desk tickets / security alerts, assigns a priority, retrieves the relevant
runbooks, drafts an engineer summary + customer reply, and routes uncertain or risky cases to a human.

## Run
    pip install -r requirements.txt
    python evaluate.py          # metrics (writes eval_results.json)
    streamlit run app.py        # interactive demo
    export GEMINI_API_KEY=...      # optional: LLM-drafted summary/replies via Gemini (default model gemini-3.8-flash; override with TRIAGE_MODEL)
    # Windows PowerShell:  $env:GEMINI_API_KEY="..."

## Files
- `knowledge.py`  runbooks, taxonomy, domain lexicon (all synthetic)
- `data_gen.py`   synthetic ticket generator (1,500 tickets, label noise)
- `triage.py`     pipeline: TF-IDF+LR + lexicon fusion, severity features, retrieval, grounded drafting, review gate
- `evaluate.py`   baseline vs model; random split, dev stress set, clean hold-out; retrieval hit@k; gating trade-off
- `stress_set.py` / `holdout_set.py`  hand-written tickets with wording unseen in training

All data is synthetic. Metrics are indicative only - see the Technical Approach Report for limitations.
