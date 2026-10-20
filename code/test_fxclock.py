"""pytest tests for fxclock. Synthetic tests need no data; the last two read raw histdata
zips and are skipped automatically if the archive is not present.

Run:  python -m pytest -q test_fxclock.py
"""
from pathlib import Path
import numpy as np, pandas as pd, pytest
import fxclock as fc


def utc(s):
    return pd.Timestamp(s, tz="UTC")


def conv(label, c="two_era"):
    return fc.label_to_utc([pd.Timestamp(label)], c)[0]


# ---- era 1: New York wall clock -------------------------------------------------------
def test_era1_winter():
    assert conv("2015-01-14 16:59") == utc("2015-01-14 21:59")

def test_era1_summer():
    assert conv("2015-07-15 16:59") == utc("2015-07-15 20:59")

def test_era1_us_only_dst_week():      # US DST from 8 Mar 2015, EU from 29 Mar 2015
    assert conv("2015-03-13 16:59") == utc("2015-03-13 20:59")

def test_era1_autumn_gap_week():       # EU back 25 Oct 2015, US back 1 Nov 2015
    assert conv("2015-10-30 16:59") == utc("2015-10-30 20:59")


# ---- era 2: EU-calendar clock ---------------------------------------------------------
def test_era2_winter():
    assert conv("2024-01-10 16:59") == utc("2024-01-10 21:59")

def test_era2_summer():
    assert conv("2024-07-10 16:59") == utc("2024-07-10 20:59")

def test_era2_us_only_dst_week():      # label is an hour early relative to New York
    assert conv("2024-03-15 15:59") == utc("2024-03-15 20:59")

def test_era2_autumn_gap_week():
    assert conv("2024-11-01 15:59") == utc("2024-11-01 20:59")

def test_era2_after_eu_switch():
    assert conv("2024-04-05 16:59") == utc("2024-04-05 20:59")


def test_vendor_documented_clock_is_fixed():
    assert conv("2024-07-10 16:59", "fixed_est") == utc("2024-07-10 21:59")
    assert conv("2024-01-10 16:59", "fixed_est") == utc("2024-01-10 21:59")

def test_conventions_agree_in_winter():
    lab = pd.date_range("2016-01-04", "2016-02-26", freq="37min")
    a = fc.label_to_utc(lab, "two_era"); b = fc.label_to_utc(lab, "fixed_est"); c = fc.label_to_utc(lab, "eu_dst")
    assert (a == b).all() and (a == c).all()

def test_switch_date_is_immaterial_inside_winter():
    lab = pd.date_range("2018-06-01", "2019-06-30", freq="53min")
    a = fc.label_to_utc(lab, "two_era", pd.Timestamp("2018-11-05"))
    b = fc.label_to_utc(lab, "two_era", pd.Timestamp("2019-03-09"))
    assert (a == b).all()

def test_weekly_close_maps_to_1659_new_york_in_every_regime():
    for lab in ["2015-01-16 16:59", "2015-03-13 16:59", "2015-07-17 16:59",
                "2024-01-12 16:59", "2024-03-15 15:59", "2024-07-12 16:59"]:
        ny = fc.utc_to_ny(fc.label_to_utc([pd.Timestamp(lab)]))[0]
        assert (ny.hour, ny.minute) == (16, 59), lab

def test_monotone_and_one_to_one_in_trading_hours():
    lab = pd.date_range("2019-03-04", "2019-04-05 16:59", freq="1min")
    lab = lab[lab.dayofweek < 5]
    u = fc.label_to_utc(lab)
    assert u.is_monotonic_increasing and u.is_unique

def test_output_is_tz_aware_utc():
    u = fc.label_to_utc(pd.date_range("2018-12-28", "2019-01-04", freq="1h"))
    assert str(u.tz) == "UTC"


# ---- rollover mask --------------------------------------------------------------------
def test_rollover_mask_default_is_ten_minutes():
    u = pd.date_range("2024-07-10 00:00", "2024-07-10 23:59", freq="1min", tz="UTC")
    m = fc.rollover_mask(u)
    assert m.sum() == 10
    ny = fc.utc_to_ny(u[m])
    assert ny[0].strftime("%H:%M") == "16:55" and ny[-1].strftime("%H:%M") == "17:04"

def test_rollover_mask_follows_new_york_dst():
    assert fc.rollover_mask([utc("2024-07-10 20:59")])[0]      # 16:59 EDT
    assert not fc.rollover_mask([utc("2024-07-10 21:59")])[0]  # 17:59 EDT
    assert fc.rollover_mask([utc("2024-01-10 21:59")])[0]      # 16:59 EST
    assert not fc.rollover_mask([utc("2024-01-10 20:59")])[0]

def test_mask_returns_zeroes_only_window_and_copies():
    u = pd.date_range("2024-01-10 21:50", periods=20, freq="1min", tz="UTC")
    r = np.ones(20)
    out = fc.mask_returns(r, u)
    assert out.sum() == 10 and r.sum() == 20 and out[:5].sum() == 5

def test_wide_mask():
    u = pd.date_range("2024-01-10 00:00", "2024-01-10 23:59", freq="1min", tz="UTC")
    assert fc.rollover_mask(u, before=5, after=65).sum() == 70

def test_tz_aware_labels_rejected():
    with pytest.raises(ValueError):
        fc.label_to_utc(pd.date_range("2024-01-01", periods=3, freq="1min", tz="UTC"))

def test_dst_regime_examples():
    r = fc.dst_regime(pd.to_datetime(["2024-01-10", "2024-03-15", "2024-07-10", "2024-11-01", "2024-11-05"]))
    assert list(r) == [0, 1, 2, 1, 0]

def test_diagnose_clock_on_synthetic_new_york_clock():
    days = pd.date_range("2015-01-05", "2015-12-18", freq="B")
    lab = pd.DatetimeIndex([d + pd.Timedelta(hours=h, minutes=59) for d in days for h in (10, 16)])
    t = fc.diagnose_clock(lab).set_index("regime")
    assert (t.modal_last_bar == "16:59").all() and set(t.index) == {0, 1, 2}


# ---- data-backed tests (skipped without the archive) ----------------------------------
from fxio import ZIPDIR  # honours HISTDATA_ZIPDIR; real-file tests skip if absent
need_data = pytest.mark.skipif(not ZIPDIR.exists(), reason="raw histdata archive not available")


@need_data
@pytest.mark.parametrize("year,expect", [(2016, ["16:59", "16:59", "16:59"]), (2024, ["16:59", "15:59", "16:59"])])
def test_real_files_show_the_two_eras(year, expect):
    import fxio
    df = fxio.read_pair_year("EURUSD", year)
    t = fc.diagnose_clock(df.t).set_index("regime")
    assert [t.modal_last_bar[r] for r in (0, 1, 2)] == expect


@need_data
@pytest.mark.parametrize("year", [2016, 2024])
def test_real_weekly_close_is_1659_new_york_after_conversion(year):
    import fxio
    df = fxio.read_pair_year("EURUSD", year)
    gap = df.t.diff().shift(-1)
    last = df.t[(gap > pd.Timedelta(hours=30)) & (gap < pd.Timedelta(hours=80))]
    last = last[last.dt.dayofweek == 4]
    ny = fc.utc_to_ny(fc.label_to_utc(last))
    share = ((ny.hour == 16) & (ny.minute == 59)).mean()
    assert share > 0.9, share
