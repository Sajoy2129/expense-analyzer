"""Print a short spending summary from sample_expenses.csv.

Run with:  python analyze.py
"""

import matplotlib.pyplot as plt
import pandas as pd

DATA_FILE = "sample_expenses.csv"
CHART_FILE = "category_chart.png"
MONTHLY_CHART_FILE = "monthly_chart.png"
PIE_CHART_FILE = "category_pie.png"

# Chart colours: one blue for the data, quiet greys for text and axes.
BAR_COLOR = "#2a78d6"
TEXT_COLOR = "#0b0b0b"
LABEL_COLOR = "#52514e"
MUTED_COLOR = "#898781"
AXIS_COLOR = "#c3c2b7"
BACKGROUND_COLOR = "#ffffff"

# One fixed colour per category, so a category keeps its colour even if
# the spending order changes. The colours are chosen to stay distinct
# for colour-blind readers.
CATEGORY_COLORS = {
    "Bills": "#2a78d6",      # blue
    "Food": "#eb6834",       # orange
    "Shopping": "#1baf7a",   # aqua
    "Fun": "#eda100",        # yellow
    "Transport": "#e87ba4",  # magenta
}


def load_expenses(path):
    """Load the CSV into a DataFrame, turning the 'date' column into real dates."""
    return pd.read_csv(path, parse_dates=["date"])


def average_per_day(df):
    """Total spend divided by every calendar day in the data's date range.

    Days with no spending still count, so this is a true daily average.
    """
    days = (df["date"].max() - df["date"].min()).days + 1
    return df["amount_aed"].sum() / days


def monthly_totals(df):
    """Return total spend per calendar month, oldest month first.

    The index holds the first day of each month (a Timestamp).
    """
    months = df["date"].dt.to_period("M").dt.to_timestamp()
    return df.groupby(months)["amount_aed"].sum().sort_index()


def top_expenses(df, n):
    """Return the n most expensive single purchases, biggest first."""
    return df.nlargest(n, "amount_aed")


def print_top_expenses(expenses):
    """Print expenses as a numbered table with lined-up columns."""
    print(f"  {'#':<3}{'Date':<13}{'Category':<11}{'Description':<27}"
          f"{'Amount':>12}")
    print("  " + "-" * 66)
    for rank, row in enumerate(expenses.itertuples(), start=1):
        print(f"  {rank:<3}{row.date:%d %b %Y}  {row.category:<11}"
              f"{row.description:<27}{row.amount_aed:>8,.2f} AED")


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


def save_category_pie(by_category, path):
    """Save a pie chart of each category's share of total spend as a PNG.

    by_category must be sorted largest first, so the slices run
    clockwise from 12 o'clock, biggest to smallest.
    """
    total = by_category.sum()
    shares = by_category / total
    colors = [CATEGORY_COLORS[category] for category in by_category.index]

    # Name and share go outside each slice, so no separate legend is needed.
    labels = [f"{category}\n{share:.0%}"
              for category, share in zip(by_category.index, shares.values)]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(by_category.values, labels=labels, colors=colors,
           startangle=90, counterclock=False,  # clockwise from the top
           labeldistance=1.15,
           wedgeprops={"edgecolor": BACKGROUND_COLOR, "linewidth": 2},
           textprops={"color": TEXT_COLOR, "fontsize": 11})

    # Title states the takeaway; subtitle gives the context.
    top_category = by_category.index[0]
    ax.set_title(f"{top_category} are {shares.iloc[0]:.0%} of all spending",
                 loc="left", fontsize=13, color=TEXT_COLOR, pad=36)
    ax.text(0, 1.06, f"Share of total spend · {total:,.0f} AED",
            transform=ax.transAxes, fontsize=10, color=MUTED_COLOR)

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_monthly_chart(by_month, path):
    """Save a line chart of total spend per month as a PNG image.

    by_month comes from monthly_totals(): month start dates -> totals.
    """
    labels = [f"{month:%b}" for month in by_month.index]  # e.g. "Jul"
    x = range(len(by_month))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, by_month.values, color=BAR_COLOR, linewidth=2,
            marker="o", markersize=8)

    # Label each point with its total; there are only a few months.
    for i, amount in zip(x, by_month.values):
        ax.annotate(f"{amount:,.0f} AED", (i, amount), xytext=(0, 10),
                    textcoords="offset points", ha="center",
                    color=TEXT_COLOR, fontsize=10)

    # Title states the takeaway; subtitle gives the context.
    peak_month = by_month.idxmax()
    ax.set_title(f"Spending peaked in {peak_month:%B}",
                 loc="left", fontsize=13, color=TEXT_COLOR, pad=30)
    first, last = by_month.index[0], by_month.index[-1]
    ax.text(0, 1.04,
            f"Total spend per month, AED · {first:%b} – {last:%b %Y}",
            transform=ax.transAxes, fontsize=10, color=MUTED_COLOR)

    # Start at zero so the gaps between months aren't exaggerated.
    ax.set_ylim(0, by_month.max() * 1.2)
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:,.0f}")
    ax.set_xticks(list(x), labels)
    ax.set_xlim(-0.3, len(by_month) - 0.7)

    # Keep the axes quiet so the line stands out.
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(AXIS_COLOR)
    ax.grid(axis="y", color=AXIS_COLOR, linewidth=0.5, alpha=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, labelcolor=LABEL_COLOR, labelsize=11)

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    df = load_expenses(DATA_FILE)

    total = df["amount_aed"].sum()
    by_category = df.groupby("category")["amount_aed"].sum().sort_values(ascending=False)

    print(f"Total spent:      {total:,.2f} AED")
    print(f"Average per day:  {average_per_day(df):,.2f} AED")

    print("\nTotal per category:")
    for category, amount in by_category.items():
        print(f"  {category:<10} {amount:>10,.2f} AED")

    print("\nTop 5 expenses:")
    print_top_expenses(top_expenses(df, 5))

    by_month = monthly_totals(df)
    print("\nTotal per month:")
    for month, amount in by_month.items():
        print(f"  {month:%b %Y}   {amount:>10,.2f} AED")

    save_category_chart(by_category, df["date"].min(), df["date"].max(), CHART_FILE)
    save_monthly_chart(by_month, MONTHLY_CHART_FILE)
    save_category_pie(by_category, PIE_CHART_FILE)
    print(f"\nCharts saved to {CHART_FILE}, {MONTHLY_CHART_FILE} "
          f"and {PIE_CHART_FILE}")


if __name__ == "__main__":
    main()
