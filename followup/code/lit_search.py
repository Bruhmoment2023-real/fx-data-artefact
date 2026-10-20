"""Literature searches with a full log. No API keys, no e-mail address, no logins.
Each query: one GET, raw response saved under followup/lit/raw/, one line appended to
followup/lit/query_log.csv (utc time, service, query, http status, total hits reported, hits kept, file).
Slow on purpose (sleep between calls); a 429/403 is logged and NOT retried around.

Usage: python lit_search.py s2 | arxiv | crossref | s2cites | openalex
"""
import sys, csv, json, time, re, hashlib, datetime as dt, urllib.parse
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1] / "lit"; RAW = ROOT / "raw"; RAW.mkdir(parents=True, exist_ok=True)
LOG = ROOT / "query_log.csv"
UA = {"User-Agent": "lit-check/1.0 (non-commercial research; low volume)"}

QUERIES = [
    "histdata", "histdata.com", "histdata.com forex one-minute data",
    "bid-only quotes foreign exchange", "bid-only price series bias backtest",
    "rollover spread foreign exchange", "bid-ask spread 5 pm New York foreign exchange",
    "spread widening New York close foreign exchange rollover",
    "intraday seasonality foreign exchange returns", "intraday patterns FX returns time of day",
    "timestamp errors financial data", "time zone errors financial data", "daylight saving time timestamp high-frequency data",
    "data errors spurious results finance", "database errors asset pricing inference",
    "Datastream data errors handle with care", "free forex data quality retail", "retail FX data quality backtest bias",
    "bid-ask bounce spurious intraday return pattern", "tom-next swap rollover foreign exchange intraday",
]


def log(service, query, status, total, kept, fname, note=""):
    new = not LOG.exists()
    with open(LOG, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new: w.writerow(["utc", "service", "query", "http_status", "total_reported", "items_returned", "raw_file", "note"])
        w.writerow([dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), service, query, status, total, kept, fname, note])


def save(service, query, text, ext="json"):
    h = hashlib.sha1(query.encode()).hexdigest()[:10]
    f = RAW / f"{service}_{re.sub(r'[^a-z0-9]+', '-', query.lower())[:50]}_{h}.{ext}"
    f.write_text(text, encoding="utf-8"); return f.name


def done(service, query):
    """True if this (service, query) already has a 200 in the log - reruns only retry failures."""
    if not LOG.exists(): return False
    with open(LOG, encoding="utf-8") as fh:
        return any(r["service"] == service and r["query"] == query and r["http_status"] == "200" for r in csv.DictReader(fh))


def get(url, params=None, timeout=60):
    try:
        r = requests.get(url, params=params, headers=UA, timeout=timeout)
        return r.status_code, r.text
    except Exception as e:
        return -1, repr(e)


def s2():
    for q in QUERIES:
        if done("semanticscholar", q): continue
        st, tx = get("https://api.semanticscholar.org/graph/v1/paper/search",
                     dict(query=q, limit=25, fields="title,year,venue,externalIds,abstract,citationCount,authors"))
        tot = n = ""
        if st == 200:
            d = json.loads(tx); tot = d.get("total", ""); n = len(d.get("data", []))
        log("semanticscholar", q, st, tot, n, save("s2", q, tx), "" if st == 200 else tx[:120])
        print("s2", st, tot, n, q, flush=True); time.sleep(8 if st == 200 else 30)


def arxiv():
    for q in QUERIES:
        terms = " AND ".join(f'all:"{w}"' if " " in w else f"all:{w}" for w in [q]) if len(q.split()) <= 2 else " AND ".join(f"all:{w}" for w in q.split() if len(w) > 2)
        for scope, sq in (("q-fin", f"({terms}) AND cat:q-fin.*"), ("all", terms)):
            if done(f"arxiv[{scope}]", sq): continue
            st, tx = get("http://export.arxiv.org/api/query", dict(search_query=sq, start=0, max_results=25))
            tot = n = ""
            if st == 200:
                m = re.search(r"<opensearch:totalResults[^>]*>(\d+)<", tx); tot = m.group(1) if m else ""
                n = tx.count("<entry>")
            log(f"arxiv[{scope}]", sq, st, tot, n, save(f"arxiv-{scope}", q, tx, "xml"), "" if st == 200 else tx[:120])
            print("arxiv", scope, st, tot, n, q, flush=True); time.sleep(6 if st == 200 else 45)


def crossref():
    for q in QUERIES:
        if done("crossref", q): continue
        st, tx = get("https://api.crossref.org/works", {"query.bibliographic": q, "rows": 20,
                                                           "select": "DOI,title,author,issued,container-title,type,is-referenced-by-count"})
        tot = n = ""
        if st == 200:
            d = json.loads(tx)["message"]; tot = d.get("total-results", ""); n = len(d.get("items", []))
        log("crossref", q, st, tot, n, save("crossref", q, tx), "" if st == 200 else tx[:120])
        print("crossref", st, tot, n, q, flush=True); time.sleep(5 if st == 200 else 30)


def s2cites():
    """Everything Semantic Scholar lists as citing Ince and Porter (2006)."""
    off = 0; allrows = []
    while True:
        st, tx = get("https://api.semanticscholar.org/graph/v1/paper/DOI:10.1111/j.1475-6803.2006.00189.x/citations",
                     dict(fields="title,year,venue,externalIds,abstract,citationCount", limit=1000, offset=off))
        if st != 200:
            log("semanticscholar-citations", f"Ince&Porter offset={off}", st, "", "", save("s2cites", f"err{off}", tx), tx[:120])
            print("s2cites", st, tx[:200]); time.sleep(40)
            if off > 0 or st in (403,): break
            st, tx = get("https://api.semanticscholar.org/graph/v1/paper/DOI:10.1111/j.1475-6803.2006.00189.x/citations",
                         dict(fields="title,year,venue,externalIds,abstract,citationCount", limit=1000, offset=off))
            if st != 200: break
        d = json.loads(tx); rows = d.get("data", [])
        log("semanticscholar-citations", f"Ince&Porter offset={off}", st, "", len(rows), save("s2cites", f"off{off}", tx))
        allrows += rows; print("s2cites", off, len(rows), flush=True)
        if "next" not in d or not rows: break
        off = d["next"]; time.sleep(10)
    (ROOT / "ince_porter_citing.json").write_text(json.dumps(allrows), encoding="utf-8")


def openalex():
    for q in QUERIES[:4]:
        st, tx = get("https://api.openalex.org/works", dict(search=q, **{"per-page": 25}, select="id,title,publication_year,doi,cited_by_count"))
        tot = n = ""
        if st == 200:
            d = json.loads(tx); tot = d["meta"]["count"]; n = len(d["results"])
        log("openalex", q, st, tot, n, save("openalex", q, tx), "" if st == 200 else tx[:160])
        print("openalex", st, tot, n, q, flush=True)
        if st != 200: break
        time.sleep(15)


if __name__ == "__main__":
    {"s2": s2, "arxiv": arxiv, "crossref": crossref, "s2cites": s2cites, "openalex": openalex}[sys.argv[1]]()
