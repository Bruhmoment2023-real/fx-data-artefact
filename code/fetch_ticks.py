"""Download a few months of histdata.com Generic-ASCII TICK files (bid AND ask) through the
public download form (no login). Polite: one request pair every ~5 s. Files are saved unmodified.

Usage: python fetch_ticks.py EURUSD:2017:1 EURUSD:2017:7 ...
"""
import re, sys, time
from pathlib import Path
import requests

OUT = Path(__file__).resolve().parents[1] / "data_ticks"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"

def get(s, pair, year, month):
    f = OUT / f"{pair}_T_{year}{month:02d}.zip"
    if f.exists() and f.stat().st_size > 1000:
        return f
    page = f"https://www.histdata.com/download-free-forex-historical-data/?/ascii/tick-data-quotes/{pair.lower()}/{year}/{month}"
    r = s.get(page, timeout=60); r.raise_for_status()
    m = re.search(r'id="tk" value="([^"]+)"', r.text)
    if not m:
        print("no token", pair, year, month); return None
    data = dict(tk=m.group(1), date=str(year), datemonth=f"{year}{month:02d}", platform="ASCII", timeframe="T", fxpair=pair)
    time.sleep(1.5)
    z = s.post("https://www.histdata.com/get.php", data=data, headers={"Referer": page}, timeout=600)
    if z.status_code != 200 or z.content[:2] != b"PK":
        print("no zip", pair, year, month, z.status_code, z.content[:80]); return None
    f.write_bytes(z.content); time.sleep(3.5)
    return f

if __name__ == "__main__":
    s = requests.Session(); s.headers.update({"User-Agent": UA})
    for a in sys.argv[1:]:
        p, y, m = a.split(":")
        f = get(s, p, int(y), int(m))
        print(a, f, (f.stat().st_size if f else None), flush=True)
