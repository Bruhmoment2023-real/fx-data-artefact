"""Fetch Crossref metadata (incl. abstract if deposited) for specific DOIs; save to raw/papers. Slow, no keys."""
import requests, json, time, sys, re
from pathlib import Path
H={"User-Agent":"lit-check/1.0 (non-commercial research; low volume)"}
OUT=Path(__file__).resolve().parents[1]/"raw"/"papers"
dois={"huang_masulis_1999":"10.1093/rfs/12.1.61","krohn_mueller_whelan_2024":"10.1111/jofi.13306","ince_porter_2006":"10.1111/j.1475-6803.2006.00189.x",
      "breedon_ranaldo_2013":"10.1111/jmcb.12032","ranaldo_2009":"10.1016/j.jbankfin.2009.05.019","bollerslev_domowitz_1993":"10.1111/j.1540-6261.1993.tb04760.x"}
for k,d in dois.items():
    r=requests.get(f"https://api.crossref.org/works/{d}",headers=H,timeout=60)
    (OUT/f"crossref_{k}.json").write_text(r.text,encoding="utf-8")
    m=r.json().get("message",{}) if r.status_code==200 else {}
    ab=re.sub(r"<[^>]+>"," ",m.get("abstract","")) if m else ""
    print(k,r.status_code,(m.get("title") or [""])[0][:80],"| cited_by",m.get("is-referenced-by-count"),"| abstract chars",len(ab),"| links",[l.get("URL") for l in m.get("link",[])][:2])
    if ab: print("   ",' '.join(ab.split())[:600])
    time.sleep(6)
