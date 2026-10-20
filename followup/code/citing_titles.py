"""Titles of the works that cite Ince & Porter (2006), via OpenCitations COCI (DOI list) + Crossref (titles, batches of 40). Slow, no keys."""
import json, requests, time, re, csv
from pathlib import Path
H={"User-Agent":"lit-check/1.0 (non-commercial research; low volume)"}
L=Path(__file__).resolve().parents[1]/"lit"
dois=sorted({x["citing"] for x in json.load(open(L/"raw"/"opencitations_coci_ince_porter.json",encoding="utf-8"))})
print("citing DOIs",len(dois))
rows=[]
for i in range(0,len(dois),40):
    b=dois[i:i+40]
    r=requests.get("https://api.crossref.org/works",params={"filter":",".join("doi:"+d for d in b),"rows":40,"select":"DOI,title,issued,container-title,is-referenced-by-count"},headers=H,timeout=90)
    if r.status_code!=200: print("crossref",r.status_code); time.sleep(30); continue
    for it in r.json()["message"]["items"]:
        rows.append(dict(doi=it["DOI"],year=(it.get("issued",{}).get("date-parts") or [[""]])[0][0],title=(it.get("title") or [""])[0],venue=(it.get("container-title") or [""])[0]))
    print(i,len(rows),flush=True); time.sleep(5)
with open(L/"ince_porter_citing_titles.csv","w",newline="",encoding="utf-8") as fh:
    w=csv.DictWriter(fh,fieldnames=["doi","year","title","venue"]); w.writeheader(); w.writerows(rows)
