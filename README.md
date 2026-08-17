# HOC Foil Price Tracker

Tracks daily foil (`usd_foil`) prices for the 39 special-guest / legendary cards
from *The Hobbit* companion Commander set (HOC), sourced from the [Scryfall
API](https://scryfall.com/docs/api/cards) (which mirrors TCGplayer market price).

## Setup

1. Push this folder to its own repo, or drop it into your existing repricer
   repo as a subfolder.
2. Repo Settings → Actions → General → Workflow permissions → set to
   **Read and write permissions** (needed so the workflow can commit
   `price_history.csv` back).
3. That's it — the workflow runs daily at 13:00 UTC and on-demand via the
   **Run workflow** button on the Actions tab.

## Files

- `cards.json` — the 39 cards with their HOC collector numbers.
- `track_prices.py` — fetches each card from Scryfall, appends a row per
  card to `price_history.csv` (created on first run).
- `trend.py` — reads the history and prints latest price + 7d/30d % change
  + min/max seen per card. Run locally any time: `python trend.py`.
- `.github/workflows/track-prices.yml` — the daily cron.

## Notes

- Scryfall prices update roughly once a day themselves, so running this
  more than once a day won't get you fresher data.
- `trend.py` needs a few days of history before the 7d/30d columns fill in —
  it'll show `n/a` until then.
- No buy/sell logic baked in on purpose — it just surfaces the trend, you
  call the timing.
