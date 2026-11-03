#!/usr/bin/env python3
"""
Builds a compact Card Kingdom price index for the Buy List page.

Card Kingdom's public pricelist (https://api.cardkingdom.com/api/v2/pricelist)
is ~70 MB — too big for a browser page. This trims it to one entry per
Scryfall printing:

    { "<first 12 hex chars of scryfall_id>":
        [url_nonfoil, retail_nonfoil, buy_nonfoil, url_foil, retail_foil, buy_foil] }

Retail is only set when Card Kingdom has it in stock; buy is only set when
they're actively buying. URLs drop the "https://www.cardkingdom.com/mtg/" prefix.

The output (ck_prices.json) is force-pushed to the `ck-data` branch by the
workflow rather than committed to main, so the daily rebuild doesn't bloat history.
"""

import json
import sys
from pathlib import Path
from urllib.request import urlopen, Request

PRICELIST = "https://api.cardkingdom.com/api/v2/pricelist"
OUT_FILE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "ck_prices.json"


def fetch_json(url):
    req = Request(url, headers={
        "User-Agent": "HOC-Price-Tracker/1.0 (personal use)",
        "Accept": "application/json",
    })
    with urlopen(req, timeout=120) as resp:
        return json.load(resp)


def num(x):
    try:
        n = float(x)
    except (TypeError, ValueError):
        return None
    return n if n > 0 else None


def main():
    print("Fetching Card Kingdom pricelist...")
    data = fetch_json(PRICELIST)
    rows = data.get("data", [])
    index = {}

    for r in rows:
        sid = (r.get("scryfall_id") or "").replace("-", "")[:12]
        if not sid:
            continue
        entry = index.setdefault(sid, ["", None, None, "", None, None])
        i = 3 if str(r.get("is_foil")).lower() == "true" else 0
        url = (r.get("url") or "").removeprefix("mtg/")
        retail = num(r.get("price_retail")) if (r.get("qty_retail") or 0) > 0 else None
        buy = num(r.get("price_buy")) if (r.get("qty_buying") or 0) > 0 else None

        if not entry[i]:
            entry[i] = url
        # A printing can appear more than once (variants) — keep cheapest retail, best buy.
        if retail is not None and (entry[i + 1] is None or retail < entry[i + 1]):
            entry[i + 1] = retail
            entry[i] = url
        if buy is not None and (entry[i + 2] is None or buy > entry[i + 2]):
            entry[i + 2] = buy

    out = {
        "updated": data.get("meta", {}).get("created_at", ""),
        "base_url": "https://www.cardkingdom.com/mtg/",
        "cards": index,
    }
    OUT_FILE.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"Indexed {len(index)} printings -> {OUT_FILE} ({OUT_FILE.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
