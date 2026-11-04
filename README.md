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

- `cards.json` — the 40 cards with their HOC collector numbers.
- `track_prices.py` — fetches each card from Scryfall, appends a row per
  card to `price_history.csv` (created on first run).
- `track_tcgtracking_prices.py` — fetches TCGplayer + Manapool foil prices
  via the free TCGTracking.com API, appends to `tcgtracking_price_history.csv`.
- `trend.py` — reads the Scryfall history and prints latest price + 7d/30d
  % change + min/max seen per card. Run locally any time: `python trend.py`.
- `build_ck_index.py` — downloads Card Kingdom's full pricelist (~70 MB) and
  trims it to `ck_prices.json` (~10 MB, one entry per printing) for the Buy List.
- `docs/index.html` — the visual dashboard (see below).
- `.github/workflows/track-prices.yml` — the daily cron, runs both trackers and
  rebuilds the Card Kingdom index.

## Dashboard (GitHub Pages)

`docs/index.html` reads both CSVs straight from the repo and shows a grid
of all 40 cards with their latest Scryfall / TCGplayer / Manapool prices,
plus a per-card price-history chart.

To turn it on: repo **Settings → Pages → Source** → set to **Deploy from a
branch**, branch **main**, folder **/docs** → Save. After a minute or two
it'll be live at `https://dmohseni88.github.io/hoc-price-tracker/`.

## Buy List

The **Buy List** tab (`#/buy`) prices any cards you paste in, not just HOC.
Paste a list in the usual formats (`4 Lightning Bolt`, `4x Lightning Bolt`,
`1 Sol Ring (CMM) 400 *F*`, or just a name) and hit **Price it**
(Ctrl+Enter works too). Per card it shows:

- **TCGplayer** market price (cheapest listing underneath) and **Manapool**
  near-mint, via TCGTracking — checked on the two cheapest printings.
- **Card Kingdom** cheapest in-stock printing, plus what CK would pay you
  (buylist) for that printing.
- **Cardmarket** € from Scryfall, for reference (not in the USD totals).

Then totals for buying everything from each site, and the **cheapest mix**
(each card from whichever site is lowest). **Copy results** puts a text
summary on your clipboard. Your last pasted list is remembered in the browser.

Click **N printings ▾** under a card to open a dropdown of every printing
with its TCGplayer / Manapool / Card Kingdom / buylist / Cardmarket prices
(cheapest in each column in gold). **Use** prices that line with that
printing; **Use cheapest printing** goes back.

A set code + collector number pins that exact printing; without one (or with
"Ignore set codes" ticked) it hunts for the cheapest printing. Typos are
usually fine — Scryfall's fuzzy match fills in the card.

Card Kingdom data comes from `ck_prices.json` on the **`ck-data` branch**.
The workflow rebuilds it daily and force-pushes that branch as a single
commit, so the 10 MB file doesn't pile up in `main`'s history. Until the
workflow has run once, the Card Kingdom columns show "—".

## Notes

- Scryfall and TCGTracking prices both update roughly once a day, so running
  this more than once a day won't get you fresher data.
- `trend.py` needs a few days of history before the 7d/30d columns fill in —
  it'll show `n/a` until then. Same for the dashboard chart — it fills in
  day by day.
- No buy/sell logic baked in on purpose — it just surfaces the trend, you
  call the timing.
