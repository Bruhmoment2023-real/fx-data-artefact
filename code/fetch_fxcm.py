"""Download FXCM's public one-minute candle files (bid AND ask OHLC, UTC timestamps, weekly files).
Public URL pattern, no login:  https://candledata.fxcorporate.com/m1/<PAIR>/<YEAR>/<WEEK>.csv.gz
Used only as an independent second source to check the histdata clock and the bid/ask mechanism.

Usage: python fetch_fxcm.py EURUSD:2013-2019 USDJPY:2016 ...
"""
import sys, time
from pathlib import Path
import requests

OUT = Path(__file__).resolve().parents[1] / "data_fxcm"
OUT.mkdir(exist_ok=True)

if __name__ == "__main__":
    s = requests.Session(); s.headers.update({"User-Agent": "Mozilla/5.0 (research; one-off download)"})
    for a in sys.argv[1:]:
        pair, yrs = a.split(":")
        y0, y1 = (yrs.split("-") + [yrs])[:2] if "-" in yrs else (yrs, yrs)
        for y in range(int(y0), int(y1) + 1):
            got = 0
            for w in range(1, 54):
                f = OUT / f"{pair}_m1_{y}_w{w:02d}.csv.gz"
                if f.exists() and f.stat().st_size > 500:
                    got += 1; continue
                r = s.get(f"https://candledata.fxcorporate.com/m1/{pair}/{y}/{w}.csv.gz", timeout=60)
                if r.status_code == 200 and r.content[:2] == b"\x1f\x8b":
                    f.write_bytes(r.content); got += 1
                time.sleep(0.4)
            print(pair, y, "weeks", got, flush=True)
