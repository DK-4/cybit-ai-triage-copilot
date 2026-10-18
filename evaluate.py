"""Offline evaluation: baseline vs. TF-IDF+LR on (a) random held-out split, (b) out-of-template stress set.
Also reports retrieval hit@k and the confidence-gating trade-off. Run: python evaluate.py"""
import json
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.model_selection import train_test_split

from data_gen import generate
from knowledge import CATEGORY_TO_RUNBOOK
from stress_set import STRESS
from holdout_set import HOLDOUT
from triage import TriageEngine

def predict_cat(eng, xs):
    return [eng.category_probs(x)[0][int(eng.category_probs(x)[1].argmax())] for x in xs]

def main():
    df = generate()
    tr, te = train_test_split(df, test_size=0.25, random_state=7, stratify=df.category)
    eng = TriageEngine().fit(tr.text, tr.category, tr.priority)
    out = {}

    # --- majority-class baseline
    for tgt in ("category", "priority"):
        d = DummyClassifier(strategy="most_frequent").fit(tr.text, tr[tgt])
        out[f"baseline_{tgt}_acc"] = accuracy_score(te[tgt], d.predict(te.text))

    # --- random split (note: shares templates with train, so optimistic)
    pc = predict_cat(eng, list(te.text)); pp = eng.pri_model.predict(te.text)
    out["split_category_acc"] = accuracy_score(te.category, pc)
    out["split_category_macroF1"] = f1_score(te.category, pc, average="macro")
    out["split_priority_acc"] = accuracy_score(te.priority, pp)
    out["split_priority_within1"] = float(np.mean([abs(int(a[1]) - int(b[1])) <= 1 for a, b in zip(te.priority, pp)]))
    out["split_P1_recall"] = float(np.mean([p == "P1" for t, p in zip(te.priority, pp) if t == "P1"]))

    # --- stress set (unseen wording)
    sx = [s[0] for s in STRESS]; sc = [s[1] for s in STRESS]; sp = [s[2] for s in STRESS]
    spc = predict_cat(eng, sx); spp = eng.pri_model.predict(sx)
    out["stress_n"] = len(STRESS)
    out["stress_category_acc"] = accuracy_score(sc, spc)
    out["stress_priority_acc"] = accuracy_score(sp, spp)
    out["stress_priority_within1"] = float(np.mean([abs(int(a[1]) - int(b[1])) <= 1 for a, b in zip(sp, spp)]))
    p1_idx = [i for i, p in enumerate(sp) if p == "P1"]
    out["stress_P1_recall"] = float(np.mean([spp[i] == "P1" for i in p1_idx]))

    # --- clean hold-out (never used for tuning)
    hx = [h[0] for h in HOLDOUT]; hc = [h[1] for h in HOLDOUT]; hp = [h[2] for h in HOLDOUT]
    hpc = predict_cat(eng, hx); hpp = eng.pri_model.predict(hx)
    out["holdout_n"] = len(HOLDOUT)
    out["holdout_category_acc"] = accuracy_score(hc, hpc)
    out["holdout_category_macroF1"] = f1_score(hc, hpc, average="macro")
    out["holdout_priority_acc"] = accuracy_score(hp, hpp)
    out["holdout_priority_within1"] = float(np.mean([abs(int(a[1]) - int(b[1])) <= 1 for a, b in zip(hp, hpp)]))
    h1 = [i for i, p in enumerate(hp) if p == "P1"]
    out["holdout_P1_recall"] = float(np.mean([hpp[i] == "P1" for i in h1]))
    ha = hw = 0; hres = []
    for t, c in zip(hx, hc):
        r = eng.triage(t, use_llm=False); hres.append(r)
        if not r.needs_human:
            ha += 1; hw += (r.category != c)
    out["holdout_auto_handled_share"] = ha / len(hx)
    out["holdout_auto_handled_cat_errors"] = hw
    out["holdout_P1_flagged_for_human"] = float(np.mean([hres[i].needs_human for i in h1]))
    hit = {1: 0, 3: 0}
    for r, c in zip(hres, hc):
        ranked = [x[0] for x in r.runbooks]; gold = CATEGORY_TO_RUNBOOK[c]
        hit[1] += ranked[0] == gold; hit[3] += gold in ranked
    out["holdout_retrieval_hit@1"] = hit[1] / len(hx); out["holdout_retrieval_hit@3"] = hit[3] / len(hx)
    print("Hold-out errors (category / priority):")
    for t, g, p, gp, pp_ in zip(hx, hc, hpc, hp, hpp):
        if g != p or gp != pp_: print(f"  - '{t[:60]}' cat {g}->{p} | pri {gp}->{pp_}")

    # --- retrieval hit@k on stress set (correct runbook = category's runbook)
    hits = {1: 0, 3: 0}
    for text, cat in zip(sx, sc):
        ranked = [r[0] for r in eng.retrieve(text, None, k=3)]          # retrieval alone, no classifier boost
        gold = CATEGORY_TO_RUNBOOK[cat]
        hits[1] += ranked[0] == gold; hits[3] += gold in ranked
    out["stress_retrieval_hit@1_no_boost"] = hits[1] / len(sx)
    out["stress_retrieval_hit@3_no_boost"] = hits[3] / len(sx)
    hits = {1: 0, 3: 0}
    for text, pred in zip(sx, spc):
        ranked = [r[0] for r in eng.retrieve(text, pred, k=3)]
        gold = CATEGORY_TO_RUNBOOK[sc[sx.index(text)]]
        hits[1] += ranked[0] == gold; hits[3] += gold in ranked
    out["stress_retrieval_hit@1_hybrid"] = hits[1] / len(sx)
    out["stress_retrieval_hit@3_hybrid"] = hits[3] / len(sx)

    # --- gating on stress set: automation rate vs. error leakage
    auto = wrong_auto = 0
    for text, c, p in zip(sx, sc, sp):
        r = eng.triage(text, use_llm=False)
        if not r.needs_human:
            auto += 1
            wrong_auto += (r.category != c)
    out["stress_auto_handled_share"] = auto / len(sx)
    out["stress_auto_handled_cat_errors"] = wrong_auto

    print(json.dumps({k: round(v, 3) if isinstance(v, float) else v for k, v in out.items()}, indent=2))
    json.dump(out, open("eval_results.json", "w"), indent=2)
    print("\nPer-category report (random split):")
    print(classification_report(te.category, pc, digits=2))
    print("Stress-set errors (category):")
    for t, g, p in zip(sx, sc, spc):
        if g != p: print(f"  - '{t[:70]}' gold={g} pred={p}")
    print("Stress-set errors (priority):")
    for t, g, p in zip(sx, sp, spp):
        if g != p: print(f"  - '{t[:60]}' gold={g} pred={p}")

if __name__ == "__main__":
    main()
