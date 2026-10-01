"""Generate sample_expenses.csv: 3 months of realistic daily expenses in AED.

Run with:  python generate_sample_data.py
"""

import csv
import random
from datetime import date, timedelta

SEED = 42  # Fixed seed -> same "random" data every run (reproducible).
START_DATE = date(2026, 7, 1)
END_DATE = date(2026, 9, 30)
OUTPUT_FILE = "sample_expenses.csv"

# Everyday purchases: (description, min AED, max AED, chance per day 0-1).
DAILY_ITEMS = {
    "Food": [
        ("Coffee - Tim Hortons", 12, 22, 0.55),
        ("Lunch - office cafeteria", 25, 45, 0.45),
        ("Groceries - Carrefour", 60, 220, 0.20),
        ("Groceries - Lulu Hypermarket", 50, 180, 0.12),
        ("Talabat delivery", 35, 95, 0.25),
        ("Shawarma & juice", 15, 30, 0.15),
    ],
    "Transport": [
        ("Careem ride", 18, 65, 0.25),
        ("Nol card top-up", 50, 100, 0.08),
        ("Fuel - ENOC", 90, 160, 0.10),
        ("Parking - RTA", 4, 20, 0.15),
    ],
    "Shopping": [
        ("Amazon.ae order", 40, 350, 0.08),
        ("Noon order", 30, 250, 0.06),
        ("Clothes - Centrepoint", 80, 300, 0.03),
        ("Pharmacy - Aster", 20, 120, 0.05),
        ("Home items - IKEA", 60, 450, 0.02),
    ],
}

# Weekend-only fun (Saturday/Sunday in the UAE).
WEEKEND_FUN = [
    ("Cinema - VOX", 45, 120, 0.30),
    ("Brunch with friends", 150, 350, 0.20),
    ("Dinner out - Dubai Marina", 120, 300, 0.25),
    ("Bowling / arcade", 60, 150, 0.10),
    ("Dubai Aquarium tickets", 120, 200, 0.03),
]

# Fixed monthly bills: (day of month, description, min AED, max AED).
# A min/max range lets bills vary a bit, e.g. higher AC use in August.
MONTHLY_BILLS = [
    (1, "Rent - studio apartment", 4500, 4500),
    (5, "DEWA electricity & water", 550, 900),
    (8, "Etisalat home internet", 389, 389),
    (10, "du mobile plan", 125, 125),
    (12, "Gym membership", 250, 250),
    (15, "Salik toll top-up", 100, 100),
    (20, "Netflix subscription", 39, 39),
]


def random_amount(low, high):
    """Return a random amount between low and high, rounded to fils."""
    return round(random.uniform(low, high), 2)


def expenses_for_day(day):
    """Build the list of expense rows for a single date."""
    rows = []

    for category, items in DAILY_ITEMS.items():
        for description, low, high, chance in items:
            if random.random() < chance:
                rows.append((day, category, description, random_amount(low, high)))

    is_weekend = day.weekday() >= 5  # 5 = Saturday, 6 = Sunday
    if is_weekend:
        for description, low, high, chance in WEEKEND_FUN:
            if random.random() < chance:
                rows.append((day, "Fun", description, random_amount(low, high)))

    for bill_day, description, low, high in MONTHLY_BILLS:
        if day.day == bill_day:
            rows.append((day, "Bills", description, random_amount(low, high)))

    return rows


def generate_expenses(start, end):
    """Return expense rows for every day from start to end (inclusive)."""
    rows = []
    day = start
    while day <= end:
        rows.extend(expenses_for_day(day))
        day += timedelta(days=1)
    return rows


def write_csv(rows, path):
    """Write rows to a CSV file with a header line."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "category", "description", "amount_aed"])
        for day, category, description, amount in rows:
            writer.writerow([day.isoformat(), category, description, f"{amount:.2f}"])


def main():
    random.seed(SEED)
    rows = generate_expenses(START_DATE, END_DATE)
    write_csv(rows, OUTPUT_FILE)
    print(f"Wrote {len(rows)} expenses to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
