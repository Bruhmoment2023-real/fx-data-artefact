"""Step 7: figures (PNG, 200 dpi) from the tables. No raw data is read.
Outputs: results/figures/fig1 ... fig7
"""
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results" / "tables"; D = ROOT / "results" / "daily"; MS = ROOT / "results" / "minute_stats"
F = ROOT / "results" / "figures"; F.mkdir(parents=True, exist_ok=True)
HEAD = ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD"]
ALL = HEAD + ["USDCHF", "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"]
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 100})
hours = lambda ax: (ax.set_xticks(range(0, 1441, 120)), ax.set_xticklabels([f"{h:02d}" for h in range(0, 25, 2)]))


def fig1():
    p = pd.read_csv(T / "T1_minute_profile_ny.csv"); p = p[p["sample"] == "2015-2026"]
    fig, axs = plt.subplots(2, 2, figsize=(11, 6.5), sharex=True)
    for ax, pair in zip(axs.ravel(), HEAD):
        x = p[p.pair == pair]
        ax.bar(x.ny_minute, x.t, width=1.0, color="#7a8ba3", linewidth=0)
        r = x[x.ny_minute == 1019]
        ax.bar(r.ny_minute, r.t, width=4, color="#c0392b")
        ax.annotate(f"16:59  t = {r.t.iloc[0]:.1f}\nmean = {r.mean_bp.iloc[0]:.2f} bp", (1019, r.t.iloc[0]), xytext=(560, r.t.iloc[0] * 0.8),
                    arrowprops=dict(arrowstyle="-", color="#c0392b"), color="#c0392b")
        ax.axhline(0, color="k", lw=0.5); ax.axhline(3, color="grey", lw=0.5, ls=":"); ax.axhline(-3, color="grey", lw=0.5, ls=":")
        ax.set_title(f"{pair}  (n per minute about {int(x.n.median())} days)"); ax.set_ylabel("t-statistic of mean 1-min return"); hours(ax)
    for ax in axs[1]: ax.set_xlabel("New York time (hour)")
    fig.suptitle("Figure 1. Mean one-minute bid-to-bid return for each of the 1,440 minutes of the New York day, 2015-2026 (histdata.com M1)")
    fig.tight_layout(); fig.savefig(F / "fig1_minute_of_day_profile.png", dpi=200); plt.close(fig)


def fig2():
    w = pd.read_csv(T / "T4_window_1630_1829_by_minute.csv")
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, s in zip(axs, ("2009-2014", "2015-2026")):
        for pair in ALL:
            x = w[(w.pair == pair) & (w["sample"] == s)]
            ax.plot(x.minute, x.cum_mean_bp, lw=1.6 if pair in HEAD else 0.9, label=pair)
        ax.axvline(1020, color="k", lw=0.6, ls="--"); ax.axhline(0, color="k", lw=0.4)
        ax.set_xticks([990, 1005, 1020, 1035, 1050, 1065, 1080, 1095, 1110]); ax.set_xticklabels(["16:30", "16:45", "17:00", "17:15", "17:30", "17:45", "18:00", "18:15", "18:30"])
        ax.set_title(s); ax.set_xlabel("New York time")
    axs[0].set_ylabel("cumulative mean bid return from 16:30 (bp)"); axs[1].legend(ncol=2, fontsize=7, frameon=False)
    fig.suptitle("Figure 2. Average path of the bid around the 17:00 New York rollover")
    fig.tight_layout(); fig.savefig(F / "fig2_rollover_window.png", dpi=200); plt.close(fig)


def fig3():
    a = pd.read_csv(T / "T2_rollover_by_pair_year.csv"); a = a[~a.year.astype(str).str.contains("-")].copy(); a["year"] = a.year.astype(int)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
    for pair in ALL:
        x = a[a.pair == pair]
        axs[0].plot(x.year, x.r1659_mean, marker="o", ms=3, lw=1.5 if pair in HEAD else 0.8, label=pair)
        axs[1].plot(x.year, x.r1659_t, marker="o", ms=3, lw=1.5 if pair in HEAD else 0.8, label=pair)
    axs[0].set_ylabel("mean return of the 16:59 NY bar (bp)"); axs[1].set_ylabel("t-statistic within the year")
    for ax in axs: ax.axhline(0, color="k", lw=0.5); ax.set_xlabel("year"); ax.axvline(2014.5, color="grey", ls=":", lw=0.8)
    axs[1].axhline(-2, color="grey", lw=0.5, ls=":"); axs[0].legend(ncol=2, fontsize=7, frameon=False)
    fig.suptitle("Figure 3. The 16:59 New York bar by year: absent before 2015, present in every year since")
    fig.tight_layout(); fig.savefig(F / "fig3_rollover_bar_by_year.png", dpi=200); plt.close(fig)


def fig4():
    x = pd.read_csv(T / "T6_weekly_close_open_labels_EURUSD.csv", parse_dates=["last_bar_label", "next_bar_label"])
    x = x[x.last_bar_label.dt.dayofweek == 4]
    hh = x.last_bar_label.dt.hour + x.last_bar_label.dt.minute / 60
    fig, axs = plt.subplots(1, 3, figsize=(13.5, 4.2))
    cols = {0: "#2c7fb8", 1: "#c0392b", 2: "#7fbf7b"}; names = {0: "US and EU on winter time", 1: "US on daylight time, EU not", 2: "both on summer time"}
    for r in (0, 2, 1):
        m = x.regime == r
        axs[0].scatter(x.last_bar_label[m], hh[m], s=9 if r != 1 else 22, color=cols[r], label=names[r], zorder=3 if r == 1 else 2)
    axs[0].set_ylim(14.5, 17.5); axs[0].set_yticks([15, 16, 17]); axs[0].set_yticklabels(["15:00", "16:00", "17:00"])
    axs[0].set_ylabel("label time of the last bar on Friday"); axs[0].legend(fontsize=7, frameon=False, loc="lower left")
    axs[0].set_title("(a) weekly close in the vendor's clock, EURUSD")
    d = pd.read_parquet(MS / "EURUSD.parquet"); d = d[d.dow < 5]
    for ax, (lo, hi, ttl) in zip(axs[1:], ((2009, 2018, "(b) files 2009-2018"), (2019, 2026, "(c) files 2019-2026"))):
        for r in (0, 2, 1):
            g = d[(d.year.between(lo, hi)) & (d.dst == r)].groupby("minute")[["n", "sabs"]].sum()
            g = g.loc[390:630]; ax.plot(g.index, g.sabs / g.n, color=cols[r], lw=1.2 if r != 1 else 1.8, label=names[r])
        ax.set_xticks([390, 450, 510, 570, 630]); ax.set_xticklabels(["06:30", "07:30", "08:30", "09:30", "10:30"]); ax.set_title(ttl + ": mean |1-min return|, EURUSD")
        ax.set_xlabel("label time (vendor's clock)"); ax.axvline(510, color="grey", lw=0.5, ls=":"); ax.axvline(450, color="grey", lw=0.5, ls=":")
    axs[1].set_ylabel("bp")
    fig.suptitle("Figure 4. The clock: New York wall time until 2018; from 2019 the label follows the European calendar, so 08:30 New York releases appear at 07:30 for 3-4 weeks a year")
    fig.tight_layout(); fig.savefig(F / "fig4_clock_evidence.png", dpi=200); plt.close(fig)


def fig5():
    f = T / "F2b_fxcm_window_by_minute.csv"
    if not f.exists(): return
    x = pd.read_csv(f); pairs = [p for p in HEAD if p in set(x.pair)]
    fig, axs = plt.subplots(2, len(pairs), figsize=(4.6 * len(pairs), 6.2), sharex=True, squeeze=False)
    for j, pair in enumerate(pairs):
        g = x[(x.pair == pair) & (x.era == "2015-2023")].sort_values("minute")
        for k, c in (("bid", "#c0392b"), ("ask", "#2c7fb8"), ("mid", "k")):
            axs[0, j].plot(g.minute, g[f"{k}_ret_bp"].cumsum(), color=c, lw=1.6, label=k)
        axs[0, j].axvline(1020, color="k", lw=0.5, ls="--"); axs[0, j].axhline(0, color="k", lw=0.4); axs[0, j].set_title(f"{pair}, FXCM bid/ask candles 2015-2023")
        axs[1, j].plot(g.minute, g.spread_bp, color="#555", lw=1.4); axs[1, j].axvline(1020, color="k", lw=0.5, ls="--")
        axs[1, j].set_xticks([990, 1020, 1050, 1080, 1110]); axs[1, j].set_xticklabels(["16:30", "17:00", "17:30", "18:00", "18:30"]); axs[1, j].set_xlabel("New York time")
    axs[0, 0].set_ylabel("cumulative mean return from 16:30 (bp)"); axs[1, 0].set_ylabel("mean quoted spread (bp of mid)"); axs[0, 0].legend(frameon=False)
    fig.suptitle("Figure 5. Mechanism, from a second source with both sides of the quote: the bid falls, the ask rises, the mid moves far less")
    fig.tight_layout(); fig.savefig(F / "fig5_mechanism_bid_ask_mid.png", dpi=200); plt.close(fig)


def fig6():
    r = pd.read_csv(T / "demo_rule_2x2.csv"); r = r[(r["sample"] == "2015-2026") & (r.clock.isin(["documented", "true"]))]
    cells = [("documented", "none", "#f4a582", "documented clock, no mask"), ("documented", "narrow", "#fddbc7", "documented clock, masked"),
             ("true", "none", "#b2182b", "true clock, no mask"), ("true", "narrow", "#92c5de", "true clock, masked")]
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.4), gridspec_kw={"width_ratios": [1.5, 1]})
    xs = np.arange(len(ALL))
    for i, (c, m, col, lab) in enumerate(cells):
        v = [r[(r.pair == p) & (r.clock == c) & (r["mask"] == m)].sharpe.iloc[0] for p in ALL]
        axs[0].bar(xs + (i - 1.5) * 0.2, v, 0.2, color=col, label=lab)
    axs[0].set_xticks(xs); axs[0].set_xticklabels(ALL, rotation=30); axs[0].axhline(0, color="k", lw=0.5); axs[0].set_ylabel("annualised Sharpe ratio, zero cost")
    axs[0].legend(frameon=False, fontsize=8); axs[0].set_title("(a) 'short the last New York hour', 2015-2026")
    for c, m, col, lab in cells:
        d = pd.read_parquet(D / f"AUDUSD_{'fixed_est' if c == 'documented' else 'two_era'}.parquet")
        d = d[(d.date.dt.dayofweek < 5) & (d.n16 >= 30) & (d.date.dt.year >= 2015)]
        pnl = -(d.h16 - (d.mA if m == "narrow" else 0))
        axs[1].plot(d.date, pnl.cumsum(), color=col, lw=1.4, label=lab)
    axs[1].axhline(0, color="k", lw=0.5); axs[1].set_ylabel("cumulative P&L (bp)"); axs[1].set_title("(b) AUDUSD cumulative P&L, bid-to-bid, zero cost")
    fig.suptitle("Figure 6. The pre-specified demonstration rule under the 2 x 2 design")
    fig.tight_layout(); fig.savefig(F / "fig6_demo_rule_2x2.png", dpi=200); plt.close(fig)


def fig7():
    s = pd.read_csv(T / "hour_scan.csv"); s = s[s.clock == "true"]
    fig, axs = plt.subplots(1, 3, figsize=(13.5, 4.0), sharey=True)
    for ax, m in zip(axs, ("none", "narrow", "wide")):
        x = s[s["mask"] == m].pivot(index="pair", columns="ny_hour", values="t").reindex(ALL)
        im = ax.imshow(x.to_numpy(), aspect="auto", cmap="RdBu", vmin=-12, vmax=12)
        ax.set_xticks(range(0, 24, 2)); ax.set_xlabel("New York hour"); ax.set_title({"none": "(a) no mask", "narrow": "(b) mask 16:55-17:04", "wide": "(c) mask 16:55-18:04"}[m])
        ax.set_yticks(range(len(ALL))); ax.set_yticklabels(ALL)
    fig.colorbar(im, ax=axs, label="t-statistic, long the hour (clipped at +/-12)", shrink=0.9)
    fig.suptitle("Figure 7. What a time-of-day search sees: t-statistic of the mean hourly bid return, 2009-2026, true clock")
    fig.savefig(F / "fig7_hour_scan_heatmap.png", dpi=200, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7):
        f(); print(f.__name__, "ok", flush=True)
