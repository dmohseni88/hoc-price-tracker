#!/usr/bin/env python3
"""
Daily price tracker for the HOC foil cards using TCGTracking.com's free API,
which blends TCGplayer and Manapool pricing per product.

No auth required. Docs: https://tcgtracking.com/tcgapi/
"""

import csv
import json
import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

BASE = "https://tcgtracking.com/tcgapi/v1/1/sets/24691"  # 24691 = The Hobbit: Eternal-Legal (HOC)
CARDS_FILE = Path(__file__).parent / "cards.json"
HISTORY_FILE = Path(__file__).parent / "tcgtracking_price_history.csv"


def fetch_json(url):
    req = Request(url, headers={
        "User-Agent": "HOC-Price-Tracker/1.0 (personal use)",
        "Accept": "application/json",
    })
    with urlopen(req, timeout=20) as resp:
        return json.load(resp)


def load_cards():
    with open(CARDS_FILE) as f:
        return json.load(f)


def pick_foil_tcg_price(tcg_dict):
    """tcg_dict looks like {'Foil': {'low': .., 'market': ..}, ...}. Pick the foil entry."""
    if not tcg_dict:
        return None
    for key, val in tcg_dict.items():
        if key.lower() == "foil":
            return val
    for key, val in tcg_dict.items():
        if "foil" in key.lower() and "non" not in key.lower():
            return val
    if len(tcg_dict) == 1:
        return next(iter(tcg_dict.values()))
    return None


def main():
    cards = load_cards()
    wanted_numbers = {c["collector_number"]: c["name"] for c in cards}

    print("Fetching product list...")
    try:
        products_resp = fetch_json(f"{BASE}/cards")
    except (HTTPError, URLError) as e:
        print(f"  ! failed fetching product list: {e}")
        return

    print("Fetching pricing data...")
    try:
        pricing_resp = fetch_json(f"{BASE}/pricing")
    except (HTTPError, URLError) as e:
        print(f"  ! failed fetching pricing: {e}")
        return

    prices_by_product = pricing_resp.get("prices", {})
    today = datetime.date.today().isoformat()
    rows = []

    for product in products_resp.get("products", []):
        number = str(product.get("number", ""))
        if number not in wanted_numbers:
            continue

        product_id = str(product.get("id"))
        entry = prices_by_product.get(product_id, {})
        tcg = entry.get("tcg", {})
        manapool = entry.get("manapool", {})

        foil_tcg = pick_foil_tcg_price(tcg) or {}

        rows.append({
            "date": today,
            "collector_number": number,
            "name": product.get("name", wanted_numbers[number]),
            "tcg_foil_low": foil_tcg.get("low", ""),
            "tcg_foil_market": foil_tcg.get("market", ""),
            "manapool_foil": manapool.get("foil", ""),
            "manapool_qty": entry.get("mp_qty", ""),
        })

    if not rows:
        print("No matching cards found in product list, aborting without writing.")
        return

    found_numbers = {r["collector_number"] for r in rows}
    missing = set(wanted_numbers) - found_numbers
    if missing:
        print(f"  ! {len(missing)} card(s) not found in TCGTracking product list: "
              f"{', '.join(sorted(missing))}")

    file_exists = HISTORY_FILE.exists()
    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

    print(f"\nLogged {len(rows)} cards for {today} -> {HISTORY_FILE.name}")


if __name__ == "__main__":
    main()
