"""Streaming reader for histdata.com Generic-ASCII M1 zips (read-only).

One zip (one pair-year, or one pair-month for the current year) is loaded at a time,
so peak memory is one file (~400k rows). Timestamps are returned exactly as the vendor
labels them ("label time"); no time-zone conversion is applied here.
"""
from __future__ import annotations
import os
import zipfile
from pathlib import Path
from zoneinfo import ZoneInfo
import datetime as dt
import numpy as np
import pandas as pd

# Folder holding the histdata.com Generic-ASCII M1 zips (named <PAIR>_<YEAR>[...].zip). Not shipped;
# set HISTDATA_ZIPDIR or put the zips in <repo>/data/raw/histdata_zips (see README).
ZIPDIR = Path(os.environ.get("HISTDATA_ZIPDIR", Path(__file__).resolve().parents[1] / "data" / "raw" / "histdata_zips"))
NY, LDN = ZoneInfo("America/New_York"), ZoneInfo("Europe/London")


def zips_for(pair: str, zipdir: Path = ZIPDIR) -> list[tuple[int, Path]]:
    out = []
    for f in sorted(zipdir.glob(f"{pair}_*.zip")):
        out.append((int(f.stem.split("_")[1]), f))
    return out


def read_zip(f: Path) -> pd.DataFrame:
    z = zipfile.ZipFile(f)
    name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
    df = pd.read_csv(z.open(name), sep=";", header=None,
                     names=["dt", "o", "h", "l", "c", "v"], usecols=[0, 1, 2, 3, 4])
    df["t"] = pd.to_datetime(df["dt"], format="%Y%m%d %H%M%S")
    df = df.drop(columns="dt").drop_duplicates("t").sort_values("t").reset_index(drop=True)
    return df


def read_pair_year(pair: str, year: int, zipdir: Path = ZIPDIR) -> pd.DataFrame | None:
    fs = [f for y, f in zips_for(pair, zipdir) if y == year]
    if not fs:
        return None
    df = pd.concat([read_zip(f) for f in fs], ignore_index=True)
    return df.drop_duplicates("t").sort_values("t").reset_index(drop=True)


def dst_state_for_dates(dates: pd.Series) -> pd.Series:
    """0 = US and UK both on standard time, 1 = US on daylight time and UK not
    (the 'mismatch' weeks in March and Oct/Nov), 2 = both on daylight time.
    Evaluated at local noon of each calendar date."""
    uniq = pd.unique(dates)
    m = {}
    for d in uniq:
        d0 = pd.Timestamp(d)
        noon_ny = dt.datetime(d0.year, d0.month, d0.day, 12, tzinfo=NY)
        noon_ld = dt.datetime(d0.year, d0.month, d0.day, 12, tzinfo=LDN)
        us = noon_ny.utcoffset() != dt.timedelta(hours=-5)
        uk = noon_ld.utcoffset() != dt.timedelta(0)
        m[d] = 0 if (not us and not uk) else (1 if (us and not uk) else (2 if (us and uk) else 3))
    return dates.map(m)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Adds label minute-of-day, weekday, DST state and bid-to-bid returns in basis points.
    ret_cc is the close-to-close log return and is NaN unless the previous bar is exactly
    one minute earlier (so no return ever spans a gap)."""
    t = df["t"]
    df["minute"] = (t.dt.hour * 60 + t.dt.minute).astype("int16")
    df["dow"] = t.dt.dayofweek.astype("int8")
    df["date"] = t.dt.normalize()
    df["dst"] = dst_state_for_dates(df["date"]).astype("int8")
    lc = np.log(df["c"].to_numpy())
    consec = np.r_[False, np.diff(t.to_numpy()).astype("timedelta64[m]").astype(int) == 1]
    r = np.r_[np.nan, np.diff(lc)] * 1e4
    r[~consec] = np.nan
    df["ret_cc"] = r
    df["ret_oc"] = (lc - np.log(df["o"].to_numpy())) * 1e4
    df["range_bp"] = (df["h"] - df["l"]) / df["c"] * 1e4
    return df
