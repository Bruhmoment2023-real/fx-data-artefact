"""Paper 07 topic chart: map of where the computational textbook-analysis studies (sub-literature B) were done.
Left: world map, countries named in title/abstract (setting proxy). Right: India, states named (B records; plus all records as a lighter second layer).
Boundaries: open GeoJSON (datasets/geo-countries; geohacker/india), cached in D:\\Research-Publishing\\_tools\\geo. Pure matplotlib.
"""
import os, sys, re, json
import numpy as np, pandas as pd
import requests
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import pycountry
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import topic_util as T

B = os.path.abspath(sys.argv[1])
M, cfg = T.load(B)
GEO = r"D:\Research-Publishing\_tools\geo"
os.makedirs(GEO, exist_ok=True)
URLS = {"countries.geojson": "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson",
        "india_state.geojson": "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson"}
for fn, u in URLS.items():
    fp = os.path.join(GEO, fn)
    if not os.path.exists(fp):
        r = requests.get(u, timeout=180)
        r.raise_for_status()
        open(fp, "wb").write(r.content)


def polys(geom, step):
    out = []
    gs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in gs:
        ring = np.array(poly[0])
        if len(ring) > 60:
            ring = ring[::step]
        out.append(ring)
    return out


# ---- which countries / states are named in B records
Bm = M[M.sublit == "B_computational_textbook_analysis"]
alias = {"United States of America": [r"united states", r"\bu\.s\.", r"\bamerican\b", r"\busa\b"], "United Kingdom": [r"united kingdom", r"britain", r"england", r"british", r"scotland", r"\buk\b"],
         "India": [r"\bindia\b", r"\bindian\b"], "China": [r"\bchina\b", r"\bchinese\b"], "South Korea": [r"south korea", r"\bkorea(n)?\b"], "Turkey": [r"turkey", r"turkish", r"türkiye"],
         "Russia": [r"russia(n)?\b"], "Iran": [r"\biran(ian)?\b"], "Vietnam": [r"vietnam"], "Tanzania": [r"tanzania"], "Germany": [r"germany", r"german\b"], "France": [r"france", r"french\b"],
         "Japan": [r"japan(ese)?\b"], "Israel": [r"israel(i)?\b"], "Palestine": [r"palestin"], "Netherlands": [r"netherlands", r"dutch\b"], "Spain": [r"\bspain\b", r"spanish"],
         "Italy": [r"\bitaly\b", r"italian"], "Sweden": [r"sweden", r"swedish"], "Indonesia": [r"indonesia(n)?"], "Pakistan": [r"pakistan(i)?"], "Malaysia": [r"malaysia(n)?"],
         "Brazil": [r"brazil(ian)?"], "Mexico": [r"mexic(o|an)"], "Australia": [r"australia(n)?"], "Canada": [r"canad(a|ian)"], "Singapore": [r"singapore"], "Nigeria": [r"nigeria(n)?"],
         "South Africa": [r"south africa(n)?"], "Kenya": [r"kenya(n)?"], "Egypt": [r"egypt(ian)?"], "Saudi Arabia": [r"saudi"], "Greece": [r"greece", r"greek"], "Finland": [r"finland", r"finnish"],
         "Norway": [r"norway", r"norwegian"], "Poland": [r"poland", r"polish"], "Bangladesh": [r"bangladesh(i)?"], "Sri Lanka": [r"sri lanka(n)?"], "Nepal": [r"nepal(i|ese)?\b"], "Taiwan": [r"taiwan(ese)?"],
         "Hong Kong": [r"hong kong"], "Thailand": [r"thai(land)?\b"], "Philippines": [r"philippine"], "Ghana": [r"ghana(ian)?"], "Ethiopia": [r"ethiopia(n)?"], "Switzerland": [r"switzerland", r"swiss\b"],
         "Austria": [r"austria(n)?"], "Denmark": [r"denmark", r"danish"], "Ireland": [r"ireland", r"irish"], "New Zealand": [r"new zealand"], "Argentina": [r"argentin"], "Chile": [r"\bchile(an)?\b"],
         "Colombia": [r"colombia(n)?"], "Morocco": [r"morocc"], "Jordan": [r"jordan(ian)?\b"], "Lebanon": [r"lebanon", r"lebanese"], "Serbia": [r"serbia(n)?"], "Croatia": [r"croatia(n)?"], "Romania": [r"romania(n)?"],
         "Bulgaria": [r"bulgaria(n)?"], "Hungary": [r"hungar"], "Czechia": [r"czech"], "Ukraine": [r"ukrain"], "Portugal": [r"portug"], "Belgium": [r"belgi"], "Luxembourg": [r"luxembourg"]}
txtB = Bm.txt
cnt = {c: int(txtB.str.contains("|".join(p), regex=True).sum()) for c, p in alias.items()}
cnt = {c: v for c, v in cnt.items() if v > 0}
pd.DataFrame(sorted(cnt.items(), key=lambda kv: -kv[1]), columns=["country_named", "records_B"]).to_csv(os.path.join(B, "tables", "py_textbook_studies_countries_named.csv"), index=False, encoding="utf-8-sig")
authC = Bm.countries.str.split("; ").explode()
authC = authC[authC != ""].value_counts()
authC.rename("records_B_author_country").to_csv(os.path.join(B, "tables", "py_textbook_studies_author_countries.csv"), encoding="utf-8-sig")

states = {"Karnataka": "Karnataka", "Tamil Nadu": "Tamil Nadu", "Kerala": "Kerala", "Maharashtra": "Maharashtra", "Bihar": "Bihar", "Uttar Pradesh": "Uttar Pradesh", "Andhra Pradesh": "Andhra Pradesh",
          "Telangana": "Telangana", "Gujarat": "Gujarat", "Rajasthan": "Rajasthan", "Madhya Pradesh": "Madhya Pradesh", "West Bengal": "West Bengal", "Odisha": "Odisha", "Orissa": "Odisha", "Punjab": "Punjab",
          "Haryana": "Haryana", "Delhi": "Delhi", "Assam": "Assam", "Jharkhand": "Jharkhand", "Chhattisgarh": "Chhattisgarh", "Himachal Pradesh": "Himachal Pradesh", "Uttarakhand": "Uttarakhand", "Goa": "Goa",
          "Jammu and Kashmir": "Jammu & Kashmir", "Kashmir": "Jammu & Kashmir", "Manipur": "Manipur", "Tripura": "Tripura", "Meghalaya": "Meghalaya", "Nagaland": "Nagaland", "Sikkim": "Sikkim"}
def scount(df):
    c = {}
    for k, v in states.items():
        n = int(df.txt.str.contains(r"\b" + k.lower() + r"\b", regex=True).sum())
        if n:
            c[v] = c.get(v, 0) + n
    return c
sB, sAll = scount(Bm), scount(M)
pd.DataFrame({"records_B": pd.Series(sB), "records_all_corpus": pd.Series(sAll)}).fillna(0).astype(int).sort_values("records_all_corpus", ascending=False).to_csv(
    os.path.join(B, "tables", "py_indian_states_named_B_and_all.csv"), encoding="utf-8-sig")

# ---- draw
world = json.load(open(os.path.join(GEO, "countries.geojson"), encoding="utf-8"))
ind = json.load(open(os.path.join(GEO, "india_state.geojson"), encoding="utf-8"))
fig, axs = plt.subplots(1, 2, figsize=(17, 7.2), gridspec_kw=dict(width_ratios=[1.7, 1]))
ax = axs[0]
vmax = max(cnt.values()) if cnt else 1
cm = plt.get_cmap("YlOrRd")
used = set()
for f in world["features"]:
    nm = f["properties"].get("name") or f["properties"].get("ADMIN") or ""
    if nm == "Antarctica":
        continue
    key = {"United States": "United States of America"}.get(nm, nm)
    n = cnt.get(key) or cnt.get(nm) or 0
    if n:
        used.add(key)
    for ring in polys(f["geometry"], 4):
        ax.add_patch(Polygon(ring, closed=True, facecolor=cm(0.12 + 0.88 * n / vmax) if n else "#e8e8e8", edgecolor="white", lw=0.3))
ax.set_xlim(-170, 180); ax.set_ylim(-58, 84); ax.set_aspect(1.2); ax.set_xticks([]); ax.set_yticks([])
ax.set_title("World: countries named in titles/abstracts of computational textbook-analysis studies", fontsize=10, loc="left")
top = sorted(cnt.items(), key=lambda kv: -kv[1])[:8]
ax.text(-168, -55, "Most named: " + "; ".join(f"{k} {v}" for k, v in top), fontsize=8, va="bottom")
sm = plt.cm.ScalarMappable(cmap=cm, norm=plt.Normalize(0, vmax)); fig.colorbar(sm, ax=ax, shrink=0.55, pad=0.01, label="Records naming the country (sub-literature B)")
ax2 = axs[1]
smax = max(sAll.values()) if sAll else 1
for f in ind["features"]:
    nm = f["properties"].get("NAME_1") or f["properties"].get("ST_NM") or f["properties"].get("name") or ""
    nm2 = {"Orissa": "Odisha", "Jammu and Kashmir": "Jammu & Kashmir", "NCT of Delhi": "Delhi", "Uttaranchal": "Uttarakhand"}.get(nm, nm)
    n = sAll.get(nm2, 0)
    for ring in polys(f["geometry"], 6):
        ax2.add_patch(Polygon(ring, closed=True, facecolor=plt.get_cmap("Blues")(0.15 + 0.85 * n / smax) if n else "#e8e8e8", edgecolor="white", lw=0.4))
ax2.set_xlim(67, 98); ax2.set_ylim(6, 37); ax2.set_aspect(1.05); ax2.set_xticks([]); ax2.set_yticks([])
ax2.set_title("India: states named in titles/abstracts (all corpus records)", fontsize=10, loc="left")
topS = sorted(sAll.items(), key=lambda kv: -kv[1])[:6]
ax2.text(67.3, 6.3, "Most named: " + "; ".join(f"{k} {v}" for k, v in topS) + f"\nSub-literature B only: {sum(sB.values())} state mentions", fontsize=8, va="bottom")
fig.suptitle(f"Where were the studies done? Setting named in the literature map ({len(M)} records; sub-literature B = {len(Bm)} computational textbook-analysis records)", x=0.01, ha="left", fontweight="bold", fontsize=12)
T.save(fig, B, "py_10_study_settings_map")
T.caption(B, "py_10_study_settings_map.png", "Map of study settings (countries and Indian states)",
          f"Left: world map shaded by how many computational textbook-analysis records (sub-literature B, n={len(Bm)}) name each country in the title or abstract. Right: India shaded by how many corpus records name each state.",
          "Name matching with aliases (e.g. 'Indian', 'British') on title+abstract in master.csv; boundaries from open GeoJSON (datasets/geo-countries, geohacker/india) cached in _tools/geo. Tables: py_textbook_studies_countries_named.csv, py_textbook_studies_author_countries.csv, py_indian_states_named_B_and_all.csv.",
          "A name in an abstract is a proxy for a study setting, not proof of one, records without abstracts count only by title, and 'India' is partly a search term, so its shading is inflated by design. State boundaries are an outdated open file and are not authoritative.")
print(len(cnt), "countries;", len(sAll), "states")
