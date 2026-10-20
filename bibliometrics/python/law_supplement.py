"""Paper 06 only: supplement the citation-indexed corpus with open law-journal / repository records.

Citation databases cover law reviews poorly, so this queries the OpenAIRE Graph API (which aggregates institutional and
law-school repositories such as Digital Commons, plus Crossref/DOAJ) and CORE (if it answers without a key) with exact phrases,
screens titles with the same inclusion rules as the main corpus, and writes tables/law_supplement_open_repositories.csv.
These records are NOT in the bibliometric corpus (most have no DOI, no reference list and no citation counts).

Usage: python law_supplement.py <bibliometrics_dir>
"""
import os, re, sys, json
from urllib.parse import quote
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import pipeline as PL

B = os.path.abspath(sys.argv[1])
cfg = PL.load_cfg(B)
C.HOST_INTERVAL["api.openaire.eu"] = 1.0
C.HOST_INTERVAL["api.core.ac.uk"] = 6.0
QUERIES = cfg.get("law_supplement_queries") or [
    '"infancy doctrine"', '"minors\' contracts"', '"contractual capacity" minors', '"capacity to contract" minor', '"contracts with minors"',
    '"age of majority" contract', '"Mohori Bibee"', '"Minors\' Contracts Act"', '"minor" "Indian Contract Act"', '"disaffirmance" minor contract',
    '"minor" partnership "benefits of partnership"', '"minor" director "Companies Act"', '"minimum age" company director', '"minor" shareholder company law',
    '"child entrepreneurs" law', '"minor entrepreneurs"', '"young entrepreneurs" "legal capacity"', '"infant" "member of a company"', '"minors" "limited liability company"',
    '"kidfluencers" contract', '"child influencers" contract law',
]
M = pd.read_csv(os.path.join(B, "data", "clean", "master.csv"), encoding="utf-8-sig", keep_default_na=False)
have_doi, have_t = set(M.doi), set(M.title.map(C.norm_title))
rows, qlog = {}, []
for q in QUERIES:
    n_oa = n_core = 0
    for page in (1, 2):
        d = C.fetch_json(f"https://api.openaire.eu/graph/v1/researchProducts?search={quote(q)}&type=publication&pageSize=100&page={page}", retries=3)
        res = (d or {}).get("results") or []
        for it in res:
            t = it.get("mainTitle") or ""
            doi = ""
            for p in it.get("pids") or []:
                if (p.get("scheme") or "").lower() == "doi":
                    doi = C.norm_doi(p.get("value"))
            urls = [u for ins in (it.get("instances") or []) for u in (ins.get("urls") or [])]
            hosts = sorted({(ins.get("hostedBy") or {}).get("value") or "" for ins in (it.get("instances") or [])} - {""})
            k = doi or C.norm_title(t)
            if not k or k in rows:
                continue
            rows[k] = dict(title=t, authors="; ".join(a.get("fullName") or "" for a in (it.get("authors") or [])[:6]), year=(it.get("publicationDate") or "")[:4],
                           venue=((it.get("container") or {}).get("name") or it.get("publisher") or ""), hosted_by="; ".join(hosts)[:150], doi=doi, url=(urls[0] if urls else ""),
                           open_access=(it.get("bestAccessRight") or {}).get("label") or "", abstract=" ".join(it.get("descriptions") or [])[:1500], source_db="OpenAIRE", query=q)
            n_oa += 1
        if len(res) < 100:
            break
    d = C.fetch_json(f"https://api.core.ac.uk/v3/search/works/?q={quote(q)}&limit=50", retries=2)
    for it in (d or {}).get("results") or []:
        t = it.get("title") or ""
        doi = C.norm_doi(it.get("doi"))
        k = doi or C.norm_title(t)
        if not k or k in rows:
            continue
        rows[k] = dict(title=t, authors="; ".join(a.get("name") or "" for a in (it.get("authors") or [])[:6]), year=str(it.get("yearPublished") or ""),
                       venue=it.get("publisher") or "", hosted_by="; ".join(dp.get("name", "") for dp in (it.get("dataProviders") or []) if isinstance(dp, dict))[:150], doi=doi,
                       url=it.get("downloadUrl") or (it.get("links") or [{}])[0].get("url", ""), open_access="Open Access (CORE)", abstract=(it.get("abstract") or "")[:1500], source_db="CORE", query=q)
        n_core += 1
    qlog.append(dict(query=q, openaire_new=n_oa, core_new=n_core, core_status="ok" if d else "no response / key required"))
    print(q, n_oa, n_core, flush=True)
out = []
for k, r in rows.items():
    t = r["title"]
    if cfg["_exc"].search(t) or PL.CONTAINER_RE.search(t):
        continue
    sl = PL.match_sublits(t + " . " + r["abstract"], cfg, t)
    sl = [s for s in sl if not s.startswith("B_")]          # the supplement is for the two legal sub-literatures
    if not sl:
        continue
    r["sub_literature"] = sl[0]
    r["already_in_corpus"] = int((r["doi"] and r["doi"] in have_doi) or C.norm_title(t) in have_t)
    r["abstract"] = r["abstract"][:400]
    out.append(r)
df = pd.DataFrame(out)
if len(df):
    df = df.sort_values(["already_in_corpus", "sub_literature", "year"], ascending=[True, True, False])
os.makedirs(os.path.join(B, "tables"), exist_ok=True)
df.to_csv(os.path.join(B, "tables", "law_supplement_open_repositories.csv"), index=False, encoding="utf-8-sig")
pd.DataFrame(qlog).to_csv(os.path.join(B, "tables", "law_supplement_query_log.csv"), index=False, encoding="utf-8-sig")
C.jdump({"raw_records": len(rows), "passed_rules": len(df), "not_in_corpus": int((df.already_in_corpus == 0).sum()) if len(df) else 0}, os.path.join(B, "tables", "law_supplement_counts.json"), indent=1)
C.save_api_log(os.path.join(B, "data", "api_log.json"))
print(f"law supplement: {len(rows)} raw records, {len(df)} pass the rules, {int((df.already_in_corpus == 0).sum()) if len(df) else 0} not already in corpus")
