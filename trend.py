#!/usr/bin/env python3
"""
Print a trend summary from price_history.csv: latest foil price, % change
over the last 7 and 30 days, and the min/max seen so far. No buy/sell
signal logic on purpose — just the numbers, so you can make the call.

Usage: python trend.py
"""

import csv
import datetime
from collections import defaultdict
from pathlib import Path

HISTORY_FILE = Path(__file__).parent / "price_history.csv"


def load_history():
    series_by_card = defaultdict(list)
    with open(HISTORY_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["usd_foil"]:
                series_by_card[row["name"]].append((row["date"], float(row["usd_foil"])))
    for name in series_by_card:
        series_by_card[name].sort()
    return series_by_card


def pct_change(old, new):
    if old == 0:
        return None
    return (new - old) / old * 100


def value_on_or_before(series, target_date):
    candidates = [price for date, price in series if date <= target_date]
    return candidates[-1] if candidates else None


def fmt_pct(value):
    return f"{value:+.1f}%" if value is not None else "n/a"


def main():
    if not HISTORY_FILE.exists():
        print("No price_history.csv yet. Run track_prices.py first.")
        return

    history = load_history()
    if not history:
        print("price_history.csv exists but has no foil price data yet.")
        return

    today = datetime.date.today()
    d7 = (today - datetime.timedelta(days=7)).isoformat()
    d30 = (today - datetime.timedelta(days=30)).isoformat()

    print(f"{'Card':<32}{'Latest':>10}{'7d':>10}{'30d':>10}{'Min':>10}{'Max':>10}")
    print("-" * 82)
    for name, series in sorted(history.items()):
        latest_date, latest_price = series[-1]
        p7 = value_on_or_before(series, d7)
        p30 = value_on_or_before(series, d30)
        prices = [p for _, p in series]

        print(
            f"{name:<32}"
            f"{latest_price:>10.2f}"
            f"{fmt_pct(pct_change(p7, latest_price) if p7 else None):>10}"
            f"{fmt_pct(pct_change(p30, latest_price) if p30 else None):>10}"
            f"{min(prices):>10.2f}"
            f"{max(prices):>10.2f}"
        )

    print(f"\nData through {history[next(iter(history))][-1][0]}. "
          f"{len(next(iter(history.values())))} day(s) logged for that card so far.")


if __name__ == "__main__":
    main()
