"""Print a short spending summary from sample_expenses.csv.

Run with:  python analyze.py
"""

import matplotlib.pyplot as plt
import pandas as pd

DATA_FILE = "sample_expenses.csv"
CHART_FILE = "category_chart.png"

# Chart colours: one blue for the bars, quiet greys for text and axes.
BAR_COLOR = "#2a78d6"
TEXT_COLOR = "#0b0b0b"
LABEL_COLOR = "#52514e"
MUTED_COLOR = "#898781"
AXIS_COLOR = "#c3c2b7"


def load_expenses(path):
    """Load the CSV into a DataFrame, turning the 'date' column into real dates."""
    return pd.read_csv(path, parse_dates=["date"])


def average_per_day(df):
    """Total spend divided by every calendar day in the data's date range.

    Days with no spending still count, so this is a true daily average.
    """
    days = (df["date"].max() - df["date"].min()).days + 1
    return df["amount_aed"].sum() / days


def save_category_chart(by_category, start, end, path):
    """Save a horizontal bar chart of spend per category as a PNG image.

    by_category must be sorted largest first; start and end are the
    first and last dates in the data, shown in the subtitle.
    """
    total = by_category.sum()
    shares = by_category / total  # each category's fraction of the total

    # Reverse so the biggest category is drawn at the top.
    data = by_category.iloc[::-1]
    data_shares = shares.iloc[::-1]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(data.index, data.values, height=0.45, color=BAR_COLOR)

    # Write each total and its share just past the end of its bar.
    labels = [f"{amount:,.0f} AED · {share:.0%}"
              for amount, share in zip(data.values, data_shares.values)]
    ax.bar_label(bars, labels=labels, padding=6, color=TEXT_COLOR, fontsize=10)

    # Title states the takeaway; subtitle gives the context.
    top_category = by_category.index[0]
    ax.set_title(f"{top_category} take {shares.iloc[0]:.0%} of spending",
                 loc="left", fontsize=13, color=TEXT_COLOR, pad=30)
    period = f"{start.day} {start:%b} – {end.day} {end:%b %Y}"
    ax.text(0, 1.04, f"Total {total:,.0f} AED · {period}",
            transform=ax.transAxes, fontsize=10, color=MUTED_COLOR)

    # Keep the axes quiet so the bars stand out.
    ax.spines[["top", "right", "bottom"]].set_visible(False)
    ax.spines["left"].set_color(AXIS_COLOR)
    ax.xaxis.set_visible(False)
    ax.tick_params(axis="y", length=0, labelcolor=LABEL_COLOR, labelsize=11)
    ax.set_xlim(0, data.max() * 1.25)  # leave room for the labels

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    df = load_expenses(DATA_FILE)

    total = df["amount_aed"].sum()
    by_category = df.groupby("category")["amount_aed"].sum().sort_values(ascending=False)
    biggest = df.loc[df["amount_aed"].idxmax()]

    print(f"Total spent:      {total:,.2f} AED")
    print(f"Average per day:  {average_per_day(df):,.2f} AED")

    print("\nTotal per category:")
    for category, amount in by_category.items():
        print(f"  {category:<10} {amount:>10,.2f} AED")

    print("\nBiggest single expense:")
    print(f"  {biggest['amount_aed']:,.2f} AED - {biggest['description']} "
          f"({biggest['category']}, {biggest['date']:%d %b %Y})")

    save_category_chart(by_category, df["date"].min(), df["date"].max(), CHART_FILE)
    print(f"\nChart saved to {CHART_FILE}")


if __name__ == "__main__":
    main()
