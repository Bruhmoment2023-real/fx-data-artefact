"""Clock conversion and rollover mask for histdata.com free FX data.

Why this exists
---------------
histdata.com documents its timestamps as "Eastern Standard Time (EST) time-zone WITHOUT
Day Light Savings adjustments", i.e. a fixed UTC-5 clock. The raw files do not behave that
way. Measured from the files themselves (weekly close/open, 08:30 New York data releases,
the Tokyo fixing), the labels behave as:

  era 1 (files up to and including 2018):  New York wall-clock time, daylight saving INCLUDED
  era 2 (files from 2019 onwards):         UTC-5 while Europe is on winter time and UTC-4 while
                                           Europe is on summer time (the EU/UK calendar, not the US one)

Both eras give UTC-5 in the northern winter, so any switch date between the US clock change
of 4 Nov 2018 and the US clock change of 10 Mar 2019 produces identical output. The default
below (1 Jan 2019) is therefore a convention, not a measured date.

Public functions
----------------
label_to_utc(labels, convention="two_era")    -> tz-aware UTC DatetimeIndex
utc_to_ny(utc)                                -> tz-aware America/New_York DatetimeIndex
ny_minute_of_day(utc)                         -> int array, minutes after New York midnight
rollover_mask(utc, before=5, after=5)         -> bool array, True inside the rollover window
mask_returns(returns, utc, before=5, after=5) -> returns with the window set to 0.0
diagnose_clock(labels)                        -> small table: weekly close label by DST regime

No machine-wide state, no I/O. Requires pandas >= 2 and the IANA tz database (tzdata on Windows).
"""
from __future__ import annotations
import numpy as np
import pandas as pd

ERA_SWITCH = pd.Timestamp("2019-01-01")          # convention, see module docstring
CONVENTIONS = ("two_era", "new_york", "eu_dst", "fixed_est")
ROLLOVER_MINUTE = 17 * 60                         # 17:00 New York


def _as_naive_index(labels) -> pd.DatetimeIndex:
    idx = pd.DatetimeIndex(labels)
    if idx.tz is not None:
        raise ValueError("labels must be naive vendor timestamps (no tz attached)")
    return idx


def _utc_from_local_rule(labels: pd.DatetimeIndex, zone: str, zone_std_utc_offset_h: int) -> pd.DatetimeIndex:
    """labels are UTC-5 when `zone` is on standard time and UTC-4 when `zone` is on daylight time.
    The DST state is read at the instant label+5h, which is unambiguous except inside the single
    changeover hour on a Sunday morning, when the FX market is closed."""
    guess = (labels + pd.Timedelta(hours=5)).tz_localize("UTC")
    local = guess.tz_convert(zone)
    off_h = (local.tz_localize(None) - guess.tz_localize(None)) / pd.Timedelta(hours=1)
    on_dst = np.asarray(off_h) > zone_std_utc_offset_h + 0.5
    utc = guess - pd.to_timedelta(on_dst.astype(int), unit="h")
    return pd.DatetimeIndex(utc)


def label_to_utc(labels, convention: str = "two_era", era_switch: pd.Timestamp = ERA_SWITCH) -> pd.DatetimeIndex:
    """Convert histdata label times to true UTC.

    convention:
      "two_era"   (recommended) New York wall clock before `era_switch`, EU-calendar clock after.
      "new_york"  New York wall clock for every row.
      "eu_dst"    EU-calendar clock for every row.
      "fixed_est" what the vendor documents: label + 5 h, all year. Wrong for about 7 months a year.
    """
    idx = _as_naive_index(labels)
    if convention not in CONVENTIONS:
        raise ValueError(f"convention must be one of {CONVENTIONS}")
    if convention == "fixed_est":
        return (idx + pd.Timedelta(hours=5)).tz_localize("UTC")
    if convention == "new_york":
        return _utc_from_local_rule(idx, "America/New_York", -5)
    if convention == "eu_dst":
        return _utc_from_local_rule(idx, "Europe/London", 0)
    ny = _utc_from_local_rule(idx, "America/New_York", -5)
    eu = _utc_from_local_rule(idx, "Europe/London", 0)
    late = np.asarray(idx >= era_switch)
    return ny.where(~late, eu)


def utc_to_ny(utc) -> pd.DatetimeIndex:
    idx = pd.DatetimeIndex(utc)
    if idx.tz is None:
        raise ValueError("utc must be tz-aware")
    return idx.tz_convert("America/New_York")


def ny_minute_of_day(utc) -> np.ndarray:
    ny = utc_to_ny(utc)
    return np.asarray(ny.hour * 60 + ny.minute)


def rollover_mask(utc, before: int = 5, after: int = 5) -> np.ndarray:
    """True for bars whose New York start minute lies in [17:00 - before, 17:00 + after).
    Defaults flag the ten one-minute bars 16:55 ... 17:04 New York time.
    Use after=65 to also cover the 17:05 and 18:00 bid rebounds."""
    m = ny_minute_of_day(utc)
    return (m >= ROLLOVER_MINUTE - before) & (m < ROLLOVER_MINUTE + after)


def mask_returns(returns, utc, before: int = 5, after: int = 5) -> np.ndarray:
    """Return a copy of `returns` with rollover-window bars set to zero (flat over the window)."""
    r = np.array(returns, dtype=float, copy=True)
    r[rollover_mask(utc, before, after)] = 0.0
    return r


def _is_dst(noon_naive: pd.DatetimeIndex, zone: str, std_h: float) -> np.ndarray:
    loc = noon_naive.tz_localize(zone)
    off = (loc.tz_localize(None) - loc.tz_convert("UTC").tz_localize(None)) / pd.Timedelta(hours=1)
    return np.asarray(off) > std_h + 0.5


def dst_regime(dates) -> np.ndarray:
    """0 = US and EU/UK both on winter time; 1 = US on daylight time, EU/UK not;
    2 = both on summer time. Evaluated at local noon of each calendar date."""
    noon = pd.DatetimeIndex(pd.DatetimeIndex(dates).normalize() + pd.Timedelta(hours=12))
    us = _is_dst(noon, "America/New_York", -5)
    eu = _is_dst(noon, "Europe/London", 0)
    return np.where(~us & ~eu, 0, np.where(us & ~eu, 1, np.where(us & eu, 2, 3)))


def diagnose_clock(labels) -> pd.DataFrame:
    """Detect the clock convention from timestamps alone.

    For every week, take the label time of the last bar before the weekend. FX closes at
    17:00 New York, so the last one-minute bar is 16:59 New York. The table reports the most
    common last-bar label by regime (see dst_regime).
    Reading: 16:59 / 16:59 / 16:59 -> New York wall clock; 16:59 / 15:59 / 16:59 -> EU-calendar
    clock; 16:59 / 15:59 / 15:59 -> a true fixed UTC-5 clock, which is what the vendor documents.
    """
    idx = _as_naive_index(labels).sort_values()
    s = pd.Series(idx)
    gap = s.diff().shift(-1)
    last = s[(gap > pd.Timedelta(hours=30)) & (gap < pd.Timedelta(hours=80))]
    last = last[last.dt.dayofweek == 4]
    df = pd.DataFrame({"regime": dst_regime(last), "hhmm": last.dt.strftime("%H:%M").to_numpy()})
    rows = []
    for r, g in df.groupby("regime"):
        vc = g.hhmm.value_counts()
        rows.append(dict(regime=int(r), weeks=len(g), modal_last_bar=vc.index[0], share_modal=round(vc.iloc[0] / len(g), 3)))
    return pd.DataFrame(rows)
