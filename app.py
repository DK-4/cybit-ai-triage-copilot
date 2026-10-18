"""Streamlit demo: Cybit AI Ticket Triage & Runbook Copilot.
Run:  streamlit run app.py      (optional: export GEMINI_API_KEY=... for LLM-drafted replies)"""
import os
import pandas as pd
import streamlit as st

from data_gen import generate
from knowledge import PRIORITY_MEANING, RUNBOOKS
from triage import TriageEngine, llm_provider

st.set_page_config(page_title="Cybit Triage Copilot (PoC)", page_icon="🎫", layout="wide")

@st.cache_resource
def load_engine():
    df = generate()
    return TriageEngine().fit(df.text, df.category, df.priority)

eng = load_engine()
provider = llm_provider()
has_key = provider is not None

st.title("🎫 AI Ticket Triage & Runbook Copilot")
st.caption("Proof of concept for Cybit's managed-services desk. Trained on synthetic data only - no real customer data.")

with st.sidebar:
    st.header("Settings")
    use_llm = st.toggle("Use LLM for drafting", value=has_key, disabled=not has_key,
                        help="Needs GEMINI_API_KEY (or GOOGLE_API_KEY). Otherwise a deterministic template drafter is used.")
    st.caption(f"LLM provider: {provider or 'none (template drafter)'}")
    eng.conf_threshold = st.slider("Human-review confidence threshold", 0.2, 0.9, eng.conf_threshold, 0.05)
    st.markdown("**Priority guide**")
    for k, v in PRIORITY_MEANING.items():
        st.markdown(f"- **{k}** - {v}")

EXAMPLES = [
    "Entire sales floor can't log in, getting account disabled errors",
    "Someone typed her password into a link in a text message and now worried",
    "Backup job failed again, repository almost full",
    "Qlik dashboard shows last week's numbers",
    "please can I get Visio added to my licence",
]
col1, col2 = st.columns([3, 2])
with col1:
    pick = st.selectbox("Load an example", ["(write your own)"] + EXAMPLES)
    text = st.text_area("Incoming ticket", value="" if pick.startswith("(") else pick, height=120)
    go = st.button("Triage ticket", type="primary", disabled=not text.strip())

if go:
    r = eng.triage(text, use_llm=use_llm)
    with col2:
        st.metric("Category", r.category, f"conf {r.category_conf:.0%}")
        st.metric("Priority", r.priority, f"conf {r.priority_conf:.0%}")
        if r.needs_human:
            st.warning("**Human review required**\n\n" + "\n".join(f"- {x}" for x in r.review_reasons))
        else:
            st.success("Confident - draft can be reviewed in the normal queue")
    st.subheader("Summary")
    st.write(r.summary)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Suggested next steps")
        for i, s in enumerate(r.next_steps, 1):
            st.markdown(f"{i}. {s}")
    with c2:
        st.subheader("Draft customer reply")
        st.info(r.customer_reply)
        st.caption(f"Drafted by: {r.drafted_by} (always reviewed by an engineer before sending)")
        if r.llm_error:
            st.error(f"LLM call failed, template used instead: {r.llm_error}")
    st.subheader("Retrieved runbooks (grounding sources)")
    st.dataframe(pd.DataFrame([{"id": a, "title": b, "similarity": round(c, 2)} for a, b, c in r.runbooks]),
                 hide_index=True, width="stretch")
    with st.expander("View top runbook"):
        rb = RUNBOOKS[r.runbooks[0][0]]
        st.markdown(f"**{rb['title']}**")
        for i, s in enumerate(rb["steps"], 1):
            st.markdown(f"{i}. {s}")
