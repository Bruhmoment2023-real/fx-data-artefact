"""Second literature pass (follow-up agent #2). Reuses lit_search.py logging; slow, one GET at a time, no keys,
no logins; a 403/429 is logged and that service is abandoned for the rest of the run (no evasion).
Usage: python lit2.py <service> where service = s2 | crossref | arxiv | ideas | ssrn | scholar | s2cites | openalex_probe
"""
import sys, re, json, time, html, csv
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lit_search as L

NEW = ["histdata", "histdata.com forex", "bid-only quotes", "rollover spread foreign exchange", "5 pm New York foreign exchange",
       "intraday FX seasonality", "intraday seasonality foreign exchange spread time of day", "timestamp errors financial data",
       "time zone error high-frequency data", "daylight saving time high-frequency financial data", "data errors spurious results finance",
       "Datastream errors handle with care", "free one-minute forex data bid quotes", "spurious trading rule profit data error"]
HITS = L.ROOT / "hits.csv"
ALLQ = list(dict.fromkeys(L.QUERIES + NEW))


def hit(service, query, title, year="", venue="", ident="", extra=""):
    new = not HITS.exists()
    with open(HITS, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["service", "query", "title", "year", "venue", "id", "extra"])
        w.writerow([service, query, title, year, venue, ident, extra])


def s2():
    for q in ALLQ:
        if L.done("semanticscholar", q):
            continue
        st, tx = L.get("https://api.semanticscholar.org/graph/v1/paper/search",
                       dict(query=q, limit=20, fields="title,year,venue,externalIds,abstract,citationCount"))
        tot = n = ""
        if st == 200:
            d = json.loads(tx); tot = d.get("total", ""); n = len(d.get("data", []))
            for p in d.get("data", []):
                hit("semanticscholar", q, p.get("title"), p.get("year"), p.get("venue"), (p.get("externalIds") or {}).get("DOI", ""), p.get("citationCount"))
        L.log("semanticscholar", q, st, tot, n, L.save("s2", q, tx), "" if st == 200 else tx[:100])
        print("s2", st, tot, n, q, flush=True)
        if st == 429:
            time.sleep(60)
            if L.get("https://api.semanticscholar.org/graph/v1/paper/search", dict(query="test", limit=1))[0] == 429:
                print("s2 still limited, abandoning"); return
        time.sleep(12)


def crossref():
    for q in ALLQ:
        if L.done("crossref", q):
            continue
        st, tx = L.get("https://api.crossref.org/works", {"query.bibliographic": q, "rows": 20, "select": "DOI,title,author,issued,container-title,type,is-referenced-by-count"})
        tot = n = ""
        if st == 200:
            d = json.loads(tx)["message"]; tot = d.get("total-results", ""); n = len(d.get("items", []))
            for it in d.get("items", []):
                hit("crossref", q, (it.get("title") or [""])[0], (it.get("issued", {}).get("date-parts") or [[""]])[0][0], (it.get("container-title") or [""])[0], it.get("DOI"), it.get("is-referenced-by-count"))
        L.log("crossref", q, st, tot, n, L.save("crossref", q, tx), "" if st == 200 else tx[:100])
        print("crossref", st, tot, n, q, flush=True); time.sleep(6 if st == 200 else 45)


def arxiv():
    for q in ALLQ:
        terms = f'all:"{q}"' if len(q.split()) <= 2 else " AND ".join(f"all:{w}" for w in q.split() if len(w) > 2)
        for scope, sq in (("q-fin", f"({terms}) AND cat:q-fin.*"), ("all", terms)):
            if L.done(f"arxiv[{scope}]", sq):
                continue
            st, tx = L.get("http://export.arxiv.org/api/query", dict(search_query=sq, start=0, max_results=25))
            tot = n = ""
            if st == 200:
                m = re.search(r"<opensearch:totalResults[^>]*>(\d+)<", tx); tot = m.group(1) if m else ""; n = tx.count("<entry>")
                for e in re.findall(r"<entry>(.*?)</entry>", tx, re.S):
                    t = re.search(r"<title>(.*?)</title>", e, re.S); i = re.search(r"<id>(.*?)</id>", e); y = re.search(r"<published>(\d{4})", e)
                    hit(f"arxiv[{scope}]", q, " ".join((t.group(1) if t else "").split()), y.group(1) if y else "", "arXiv", i.group(1) if i else "")
            L.log(f"arxiv[{scope}]", sq, st, tot, n, L.save(f"arxiv-{scope}", q, tx, "xml"), "" if st == 200 else tx[:100])
            print("arxiv", scope, st, tot, n, q, flush=True)
            if st == 429:
                time.sleep(90); return
            time.sleep(10)


def ideas():
    for q in ALLQ:
        if L.done("ideas.repec.org", q):
            continue
        st, tx = L.get("https://ideas.repec.org/cgi-bin/htsearch", dict(q=q, cmd="Search!", form="extended", wm="wrd", dt="range", ul="", s="R"))
        n = 0
        if st == 200:
            for href, title in re.findall(r'<li class="list-group-item[^"]*">\s*(?:<b>\d+\.</b>)?\s*<a href="(/[pa]/[^"]+)">(.*?)</a>', tx, re.S):
                hit("ideas.repec.org", q, html.unescape(re.sub(r"<[^>]+>", "", title)).strip(), "", "", "https://ideas.repec.org" + href); n += 1
        m = re.search(r"(\d[\d,]*)\s+(?:matches|documents|results)", tx)
        L.log("ideas.repec.org", q, st, m.group(1) if m else "", n, L.save("ideas", q, tx, "html"), "" if st == 200 else tx[:100])
        print("ideas", st, n, q, flush=True)
        if st in (403, 429):
            return
        time.sleep(12)


def ssrn():
    for q in ALLQ:
        if L.done("ssrn", q):
            continue
        st, tx = L.get("https://papers.ssrn.com/sol3/results.cfm", dict(txtKey_Words=q, npage=1))
        L.log("ssrn", q, st, "", "", L.save("ssrn", q, tx, "html"), "" if st == 200 else tx[:100].replace("\n", " "))
        print("ssrn", st, q, flush=True)
        if st != 200:
            print("ssrn blocked; abandoning"); return
        time.sleep(15)


def scholar():
    for q in ALLQ:
        if L.done("scholar", q):
            continue
        st, tx = L.get("https://scholar.google.com/scholar", dict(q=q, hl="en"))
        n = 0
        if st == 200 and "gs_rt" in tx:
            for t in re.findall(r'<h3 class="gs_rt".*?>(.*?)</h3>', tx, re.S):
                hit("scholar", q, html.unescape(re.sub(r"<[^>]+>", "", t)).strip()); n += 1
        L.log("scholar", q, st, "", n, L.save("scholar", q, tx, "html"), "" if (st == 200 and n) else (tx[:100].replace("\n", " ")))
        print("scholar", st, n, q, flush=True)
        if st != 200 or not n:
            print("scholar blocked or captcha; abandoning"); return
        time.sleep(30)


def s2cites():
    st, tx = L.get("https://api.semanticscholar.org/graph/v1/paper/search", dict(query="Individual equity return data from Thomson Datastream: handle with care", limit=5, fields="title,year,venue,externalIds,citationCount"))
    L.log("semanticscholar", "title lookup Ince Porter", st, "", "", L.save("s2", "title lookup Ince Porter", tx), "" if st == 200 else tx[:100]); print("lookup", st, tx[:300])
    if st != 200:
        return
    data = json.loads(tx).get("data", []); pid = next((p["paperId"] for p in data if "Datastream" in (p.get("title") or "")), None)
    print("paperId", pid)
    if not pid:
        return
    time.sleep(12); off = 0; rows = []
    while True:
        st, tx = L.get(f"https://api.semanticscholar.org/graph/v1/paper/{pid}/citations", dict(fields="title,year,venue,externalIds,abstract,citationCount", limit=500, offset=off))
        L.log("semanticscholar-citations", f"Ince&Porter {pid} offset={off}", st, "", "", L.save("s2cites", f"ip{off}", tx), "" if st == 200 else tx[:100])
        print("cites", st, off, flush=True)
        if st != 200:
            break
        d = json.loads(tx); rows += d.get("data", [])
        if "next" not in d:
            break
        off = d["next"]; time.sleep(12)
    (L.ROOT / "ince_porter_citing.json").write_text(json.dumps(rows), encoding="utf-8"); print("citing rows", len(rows))


def openalex_probe():
    st, tx = L.get("https://api.openalex.org/works", dict(search="histdata", **{"per-page": 5}, select="id,title,publication_year"))
    L.log("openalex", "histdata (probe)", st, "", "", L.save("openalex", "histdata-probe2", tx), tx[:160]); print(st, tx[:200])




def openalex():
    """Slow OpenAlex pass (budget was exhausted on 2026-10-13, reset by 2026-10-17). Stops at the first non-200."""
    sel = "id,title,publication_year,doi,cited_by_count,type"
    for q in ALLQ:
        if L.done("openalex", q):
            continue
        st, tx = L.get("https://api.openalex.org/works", dict(search=q, **{"per-page": 15}, select=sel))
        tot = n = ""
        if st == 200:
            d = json.loads(tx); tot = d["meta"]["count"]; n = len(d["results"])
            for w in d["results"]:
                hit("openalex", q, w.get("title"), w.get("publication_year"), "", w.get("doi") or w.get("id"), w.get("cited_by_count"))
        L.log("openalex", q, st, tot, n, L.save("openalex", q, tx), "" if st == 200 else tx[:100])
        print("openalex", st, tot, n, q, flush=True)
        if st != 200:
            return
        time.sleep(10)


def openalex_cites():
    """Works citing Ince & Porter (2006) (OpenAlex id W3125720591 from OpenCitations) that mention FX / time / data-error terms."""
    terms = '"foreign exchange" OR forex OR timestamp OR "time zone" OR "daylight saving" OR "bid-ask" OR "high-frequency" OR "data error" OR "data errors"'
    for page in (1, 2):
        st, tx = L.get("https://api.openalex.org/works", {"filter": f"cites:W3125720591,title_and_abstract.search:({terms})", "per-page": 50, "page": page, "select": "id,title,publication_year,doi,cited_by_count"})
        L.log("openalex-cites", f"cites:W3125720591 AND terms page{page}", st, "", "", L.save("openalex", f"cites{page}", tx), "" if st == 200 else tx[:100])
        print("cites", st, tx[:200], flush=True)
        if st != 200:
            return
        d = json.loads(tx)
        for w in d["results"]:
            hit("openalex-cites", "cites Ince&Porter AND FX/time terms", w.get("title"), w.get("publication_year"), "", w.get("doi") or w.get("id"), w.get("cited_by_count"))
        if len(d["results"]) < 50:
            return
        time.sleep(10)


if __name__ == "__main__":
    globals()[sys.argv[1]]()
