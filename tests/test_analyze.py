"""Tests for analyze.py.  Run with:  python -m pytest"""

import pandas as pd
import pytest

from analyze import (compare_last_two_months, describe_change, monthly_totals,
                     top_expenses)


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


def test_compare_last_two_months_uses_the_latest_two_months():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2026-07-10", "2026-08-10", "2026-09-10",
                                "2026-09-20"]),
        "category": ["Food", "Food", "Food", "Fun"],
        "amount_aed": [999.0, 100.0, 120.0, 50.0],
    })

    previous_month, current_month, table = compare_last_two_months(df)

    assert str(previous_month) == "2026-08"
    assert str(current_month) == "2026-09"
    assert table.loc["Food", "previous"] == 100.0
    assert table.loc["Food", "current"] == 120.0
    assert table.loc["Food", "change"] == pytest.approx(0.2)
    assert table.loc["Fun", "previous"] == 0  # no Fun spending in August


@pytest.mark.parametrize("change, expected", [
    (0.2, "up 20%"),
    (-0.146, "down 15%"),
    (0.001, "no change"),
    (float("inf"), "new"),
])
def test_describe_change(change, expected):
    assert describe_change(change) == expected
