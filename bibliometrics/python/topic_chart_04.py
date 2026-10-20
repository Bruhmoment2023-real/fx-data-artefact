"""Paper 04 topic chart: what kind of monitoring does the cheating/monitoring literature study, by year?"""
import os, sys, re
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import topic_util as T

B = os.path.abspath(sys.argv[1])
M, cfg = T.load(B)
A = M[M.sublit.isin(["A_cheating_monitoring", "seed"]) & (M.year >= 1995)].copy()
cats = {
    "Online / remote proctoring": r"online (exam|test|proctor)|remote(ly)? proctor|e-proctor|webcam|proctoring software|unproctored",
    "Cameras / CCTV / video surveillance in the hall": r"cctv|closed[- ]circuit|surveillance camera|video surveillance|webcast|camera",
    "External examiners / outside monitors": r"external (examiner|monitor|invigilat)|outside (monitor|observer)|independent monitor",
    "Physical invigilation / malpractice (hall exams)": r"invigilat|examination malpractice|exam malpractice|proctor",
}
order = list(cats)
for k, p in cats.items():
    A[k] = A.txt.str.contains(p, regex=True)
# assign each record to its first matching category (priority: CCTV/external first because they are rarer and closest to the paper)
prio = ["Cameras / CCTV / video surveillance in the hall", "External examiners / outside monitors", "Online / remote proctoring", "Physical invigilation / malpractice (hall exams)"]
def lab(r):
    for k in prio:
        if r[k]:
            return k
    return "Other / general cheating"
A["modality"] = A.apply(lab, axis=1)
tab = A.groupby([A.year.astype(int), "modality"]).size().unstack(fill_value=0)
tab.to_csv(os.path.join(B, "tables", "py_monitoring_modality_by_year.csv"), encoding="utf-8-sig")
cols = prio + ["Other / general cheating"]
tab = tab.reindex(columns=[c for c in cols if c in tab.columns])
fig, ax = plt.subplots(figsize=(11, 6))
colors = ["#e76f51", "#2a9d8f", "#457b9d", "#e9c46a", "#b0b0b0"]
tab.plot.bar(stacked=True, ax=ax, color=colors[:len(tab.columns)], width=0.85)
ax.set_xlabel("Publication year"); ax.set_ylabel("Records in cheating / monitoring sub-literature")
ax.set_title(f"What kind of exam monitoring does the literature study?\nCorpus: {len(M)} records; {len(A)} in the cheating/monitoring sub-literature (OpenAlex metadata, {cfg['paper_id']})", loc="left", fontsize=11, fontweight="bold")
ax.legend(title="Setting inferred from title/abstract", fontsize=8, loc="upper left")
ax.spines[["top", "right"]].set_visible(False)
n = {k: int((A.modality == k).sum()) for k in cols}
T.save(fig, B, "py_10_monitoring_modality_by_year")
T.caption(B, "py_10_monitoring_modality_by_year.png", "Monitoring setting studied, by year",
          "Stacked counts per year of cheating/monitoring records, split by the kind of monitoring their title or abstract mentions (camera/CCTV, external examiners, online proctoring, ordinary hall invigilation, other). Totals: " + "; ".join(f"{k} {v}" for k, v in n.items()) + ".",
          "Keyword rules on title+abstract in master.csv; each record is assigned to the first matching category in the order cameras/CCTV, external examiners, online proctoring, hall invigilation; tables/py_monitoring_modality_by_year.csv has the numbers.",
          "Keyword matching misclassifies: a record that mentions 'camera' only as a technical detail lands in the CCTV bar, and records without abstracts are classified from the title alone.")
print(n)
