#!/usr/bin/env python3
"""
Daily price tracker for The Hobbit companion-Commander set (HOC) foil cards.
"""

import csv
import json
import time
import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

SCRYFALL_BASE = "https://api.scryfall.com/cards/hoc"
CARDS_FILE = Path(__file__).parent / "cards.json"
HISTORY_FILE = Path(__file__).parent / "price_history.csv"
REQUEST_DELAY = 0.15


def load_cards():
    with open(CARDS_FILE) as f:
        return json.load(f)


def fetch_card(collector_number):
    url = f"{SCRYFALL_BASE}/{collector_number}"
    req = Request(url, headers={
        "User-Agent": "HOC-Price-Tracker/1.0 (personal use)",
        "Accept": "*/*",
    })
    try:
        with urlopen(req, timeout=15) as resp:
            return json.load(resp)
    except (HTTPError, URLError) as e:
        print(f"  ! failed fetching #{collector_number}: {e}")
        return None


def main():
    cards = load_cards()
    today = datetime.date.today().isoformat()
    rows = []

    for card in cards:
        num = card["collector_number"]
        print(f"Fetching #{num:>3} {card['name']}...")
        data = fetch_card(num)
        time.sleep(REQUEST_DELAY)
        if not data:
            continue

        prices = data.get("prices", {})
        rows.append({
            "date": today,
            "collector_number": num,
            "name": data.get("name", card["name"]),
            "usd_foil": prices.get("usd_foil") or "",
            "usd": prices.get("usd") or "",
            "eur_foil": prices.get("eur_foil") or "",
            "scryfall_uri": data.get("scryfall_uri", ""),
        })

    if not rows:
        print("No data fetched, aborting without writing.")
        return

    file_exists = HISTORY_FILE.exists()
    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

    print(f"\nLogged {len(rows)} cards for {today} -> {HISTORY_FILE.name}")


if __name__ == "__main__":
    main()
