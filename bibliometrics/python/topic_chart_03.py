"""Paper 03 topic chart: methods (rows) against markets / datasets (columns), coded from title + abstract by regular expressions.
A record can fall in several cells. Output: heatmap PNG/SVG + tables/py_method_by_market.csv + the coded record list."""
import os, sys
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import topic_util as T

B = os.path.abspath(sys.argv[1])
M, cfg = T.load(B)
M = M[M.abstract.str.len() > 60].copy()   # coding needs an abstract

methods = {
    "Intraday seasonality / periodicity models": r"seasonal|periodicit|diurnal|time[- ]of[- ]day|intraday pattern|day[- ]of[- ]the[- ]week|calendar effect",
    "Volatility models (GARCH, realized vol.)": r"garch|realized volatility|realised volatility|stochastic volatility|volatility (model|persist|forecast)",
    "Event study / announcements": r"announcement|news (arrival|release)|event stud|macroeconomic (news|surprise)|central bank (communication|intervention)",
    "Spread / liquidity / order-flow regressions": r"bid[- ]ask|spread|liquidity|order flow|market depth|price impact|limit order",
    "Trading-rule backtests / anomalies": r"trading rule|technical (analysis|trading)|backtest|back-test|sharpe|momentum|carry trade|anomal|data[- ]snooping|overfitting",
    "Data cleaning / error documentation": r"data (cleaning|filter|error|quality|handling|problem)|errors? in|outliers?|time stamp|timestamp|cleaning|filtering|data base|database",
}
markets = {
    "Spot FX, interbank (EBS, Reuters)": r"\bebs\b|electronic broking|reuters|interbank|dealer|inter-dealer",
    "FX futures / options / forwards": r"futures|options|forward (rate|contract|market)|cme|imm\b",
    "Retail / broker / tick-level FX": r"retail|broker|tick data|high[- ]frequency|minute[- ]?(by|level|data)|one[- ]minute|5[- ]minute|five[- ]minute",
    "Equities / stock databases": r"equit|stock|\bcrsp\b|compustat|datastream|nyse|nasdaq|share price|individual stocks",
    "Bonds / commodities / other": r"treasur|bond|commodit|gold|oil|crude|interest rate futures|credit default",
}
fx = r"\b(foreign exchange|exchange rates?|currenc\w*|forex|\bfx\b|eur/usd|usd/jpy)\b"
rows = []
for _, r in M.iterrows():
    mm = [k for k, p in methods.items() if pd.Series([r.txt]).str.contains(p, regex=True).iloc[0]]
    kk = [k for k, p in markets.items() if pd.Series([r.txt]).str.contains(p, regex=True).iloc[0]]
    if not kk and pd.Series([r.txt]).str.contains(fx, regex=True).iloc[0]:
        kk = ["Spot FX, interbank (EBS, Reuters)"] if False else []
    rows.append((r.get("id", ""), r.title, r.year, "; ".join(mm), "; ".join(kk)))
coded = pd.DataFrame(rows, columns=["id", "title", "year", "methods", "markets"])
coded.to_csv(os.path.join(B, "tables", "py_method_market_coded_records.csv"), index=False, encoding="utf-8-sig")
mat = pd.DataFrame(0, index=list(methods), columns=list(markets))
for _, r in coded.iterrows():
    for a in filter(None, r.methods.split("; ")):
        for b in filter(None, r.markets.split("; ")):
            mat.loc[a, b] += 1
mat.to_csv(os.path.join(B, "tables", "py_method_by_market.csv"), encoding="utf-8-sig")
nm = coded.methods.ne("").sum(); nk = coded.markets.ne("").sum(); both = (coded.methods.ne("") & coded.markets.ne("")).sum()

fig, ax = plt.subplots(figsize=(11, 6.2))
im = ax.imshow(mat.values, cmap="Blues", aspect="auto")
import textwrap
ax.set_xticks(range(mat.shape[1])); ax.set_xticklabels([textwrap.fill(c, 15) for c in mat.columns], fontsize=8.5)
ax.set_yticks(range(mat.shape[0])); ax.set_yticklabels(mat.index, fontsize=9)
mx = mat.values.max() or 1
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        v = mat.values[i, j]
        ax.text(j, i, str(v), ha="center", va="center", fontsize=10, color="white" if v > 0.55 * mx else "black")
ax.set_xlabel("Market or dataset named in title/abstract"); ax.set_ylabel("Method named in title/abstract")
ax.set_title(f"Which methods have been applied to which FX and financial data?\nRecords with an abstract: {len(M)}; coded to a method: {nm}; to a market: {nk}; to both: {both} ({cfg['paper_id']})", loc="left", fontsize=11, fontweight="bold")
cb = fig.colorbar(im, ax=ax, fraction=0.03); cb.set_label("Number of records (a record can fill several cells)")
T.save(fig, B, "py_10_method_by_market")
T.caption(B, "py_10_method_by_market.png", "Methods against markets and datasets",
          "Count of corpus records whose title or abstract names each method (rows) together with each market or dataset type (columns). Empty or low cells show method-market pairings the corpus rarely contains, for example high-frequency retail bid-only data.",
          "Case-insensitive regular expressions on title+abstract of master.csv records that have an abstract (patterns in python/topic_chart_03.py); coded records in tables/py_method_market_coded_records.csv.",
          "Keyword coding, not reading: a mention is not a use, a record can sit in several cells, and records without abstracts are dropped, so low counts partly reflect missing abstracts and the search terms.")
print(mat)
