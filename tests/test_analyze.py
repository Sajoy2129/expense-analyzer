"""Tests for analyze.py.  Run with:  python -m pytest"""

import pandas as pd

from analyze import monthly_totals


def test_monthly_totals_sums_each_month_in_order():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2026-08-03", "2026-07-01", "2026-07-31",
                                "2026-08-20"]),
        "amount_aed": [5.0, 10.0, 20.0, 1.5],
    })

    result = monthly_totals(df)

    assert list(result.index) == [pd.Timestamp("2026-07-01"),
                                  pd.Timestamp("2026-08-01")]
    assert list(result.values) == [30.0, 6.5]
