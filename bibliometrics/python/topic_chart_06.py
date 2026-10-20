"""Paper 06 topic chart: how many corpus records name each of the four jurisdictions, by sub-literature (coverage check)."""
import os, sys
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import topic_util as T

B = os.path.abspath(sys.argv[1])
M, cfg = T.load(B)
J = {"India": r"\bindia(n)?\b|indian contract act|companies act,? 2013|limited liability partnership act|mohori bibee",
     "United Kingdom": r"\bunited kingdom\b|\bengland\b|\bengland and wales\b|\bbritish\b|minors'? contracts act 1987|companies act 2006|\bU\.?K\.? ",
     "United States": r"\bunited states\b|\bu\.s\.|\bamerican\b|\bUSA\b|uniform (commercial|limited)|restatement|delaware",
     "Singapore": r"\bsingapore(an)?\b|minors'? contracts act|companies act 1967|acra"}
subs = [s for s in M.sublit.unique() if s != "seed"] + (["seed"] if (M.sublit == "seed").any() else [])
rows = []
for s in subs:
    g = M[M.sublit == s]
    for j, p in J.items():
        pat = p if j not in ("United States",) else p
        rows.append(dict(sublit=cfg["sublits"].get(s, {}).get("label", s), jurisdiction=j, records=int(g.txt.str.contains(pat, regex=True, case=False).sum()), of=len(g)))
d = pd.DataFrame(rows)
d.to_csv(os.path.join(B, "tables", "py_jurisdictions_named_by_sublit.csv"), index=False, encoding="utf-8-sig")
pv = d.pivot(index="sublit", columns="jurisdiction", values="records")[list(J)]
fig, ax = plt.subplots(figsize=(10, 5.5))
x = np.arange(len(pv)); w = 0.2
for i, (j, c) in enumerate(zip(J, ["#e76f51", "#457b9d", "#2a9d8f", "#e9c46a"])):
    ax.bar(x + (i - 1.5) * w, pv[j].values, w, label=j, color=c)
    for xi, v in zip(x + (i - 1.5) * w, pv[j].values):
        ax.text(xi, v, str(v), ha="center", va="bottom", fontsize=7)
ax.set_xticks(x); ax.set_xticklabels([l.replace(", ", ",\n", 1) if len(l) > 28 else l for l in pv.index], fontsize=8)
ax.set_ylabel("Corpus records naming the jurisdiction (title/abstract)"); ax.set_xlabel("Sub-literature")
ax.set_title(f"Which of the four jurisdictions does the indexed literature name?\nCorpus: {len(M)} citation-indexed records ({cfg['paper_id']}); open law-journal supplement is separate", loc="left", fontsize=11, fontweight="bold")
ax.legend(title="Jurisdiction"); ax.spines[["top", "right"]].set_visible(False)
T.save(fig, B, "py_10_jurisdictions_by_sublit")
T.caption(B, "py_10_jurisdictions_by_sublit.png", "Jurisdictions named, by sub-literature",
          "How many corpus records in each sub-literature mention India, the UK, the US or Singapore (or their key statutes) in title or abstract: a coverage check on the four-country comparison.",
          "Regular expressions on title+abstract in master.csv (patterns in python/topic_chart_06.py); counts in tables/py_jurisdictions_named_by_sublit.csv.",
          "Citation databases cover law reviews poorly, so low bars mean thin indexing, not an absence of legal scholarship; see tables/law_supplement_open_repositories.csv for the open-repository supplement.")
