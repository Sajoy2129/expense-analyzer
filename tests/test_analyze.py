"""Tests for analyze.py.  Run with:  python -m pytest"""

import pandas as pd

from analyze import monthly_totals, top_expenses


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


def test_top_expenses_returns_the_biggest_first():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2026-07-01"] * 4),
        "amount_aed": [20.0, 500.0, 5.0, 75.0],
    })

    result = top_expenses(df, 2)

    assert list(result["amount_aed"]) == [500.0, 75.0]
