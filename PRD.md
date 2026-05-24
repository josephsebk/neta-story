# Neta Stock & MF Tracker — Product Requirements Document

**Status:** Working proof-of-concept. Data pipeline validated end-to-end; data-quality hardening and front-end still pending.
**Last updated:** 22 May 2026
**Owner:** Joseph / Unni

---

## 1. Concept

Indian electoral candidates disclose their movable assets, including shares and mutual fund units, in self-sworn affidavits filed with the Election Commission. ADR republishes these on myneta.info in a semi-structured form.

This project turns those disclosures into a financial product:

- Track the **performance** of each MP's disclosed equity portfolio from a fixed baseline (the 2024 filing) to today.
- Surface the **most preferred stocks and funds** across all MPs.
- Build a **composite "Neta Index"** of MP portfolios and benchmark it against the Nifty 50.

Scope for the proof-of-concept was deliberately narrowed to **Lok Sabha 2024 winners** (the 543 sitting MPs).

---

## 2. What has been done

### 2.1 Source investigation
- Confirmed myneta.info exposes per-candidate affidavit pages at `candidate.php?candidate_id=N`.
- Confirmed the section **"Bonds, Debentures and Shares in companies"** contains the holdings, broken out per family member (self / spouse / HUF / dependents).
- Critically, confirmed the raw HTML is **more structured than the rendered page suggests**: each holding is its own `<span class="desc">Name Quantity</span>` followed by a value node. This made DOM-based parsing reliable rather than fragile regex on rendered text.

### 2.2 Scraping
- Pulled all winner candidate IDs from the winners list (`get_ids.py`). **485 of 543** captured; ~58 missing due to table formatting quirks (see open items).
- Built a resumable, concurrent scraper (`scrape_resume.py`) that fetches each affidavit, parses the holdings cell per owner column, and checkpoints to disk. Full run completes in well under a minute at 6 workers.
- Direct requests work; the older `archives.nseindia.com` is blocked (403) but `nsearchives.nseindia.com` serves the equity master.

### 2.3 Parsing
- DOM parser extracts `(security_name, quantity, declared_value)` per holding.
- On the test candidate (Supriya Sule) it cleanly extracted **85 self-column holdings** with correct name/qty/value separation.

### 2.4 Classification & ticker matching
Each holding is classified as **listed_equity**, **mutual_fund**, or **unlisted_or_other**.

- Listed equities are matched to NSE symbols using the official NSE equity master (`EQUITY_L.csv`, 2,365 names) with fuzzy matching (rapidfuzz).
- A first naive pass at WRatio ≥ 90 produced **dangerous false positives** (e.g. "INDIANB" became a 63-MP garbage bucket catching every bank-ish string; gold bonds matched to "DBCORP").
- Hardened in `reclassify.py` with: a generic-bank denylist, a noise filter (gold bonds, liquid bees, NSC, PPF, insurance), explicit hard-overrides for high-frequency names (Tata Motors, Reliance variants), mutual-fund and unlisted keyword filters ("Pvt", "Sahakari", "Foundation", "Trust"), and a **token-set containment guard** on top of a raised threshold (≥ 92). This collapsed INDIANB from 63 to a believable 12 and removed the bond/co-op noise.

### 2.5 Pricing & performance
- `yfinance` reliably returns NSE prices (`SYMBOL.NS`) and the Nifty 50 (`^NSEI`), both historical and current.
- Methodology chosen: take the **disclosed share quantity**, value it at a **fixed 4 June 2024 baseline** using historical prices, and track the same basket to today. This yields a true price-return series comparable to Nifty (cleaner than comparing declared affidavit value to current value, since declared values diverge from market price and filing dates vary).
- **241 of 256** matched tickers priced for both dates. Misses are post-June-2024 listings (BAJAJHFL, ICICIAMC), a few residual bad matches, and a TATAMOTORS symbol quirk (handled separately).

### 2.6 Current headline output (NOT yet trustworthy — see §3)
- **40 MPs** have a trackable listed-equity portfolio (quantity disclosed + priceable).
- Provisional Neta Index: **+7.36%** vs Nifty **+4.06%** over the window.
- **This number is currently distorted by a handful of quantity-parse errors** producing impossible portfolios (e.g. multi-thousand-crore single positions). It must not be quoted until §3.1 is fixed.

---

## 3. What still needs to be done

### 3.1 Data-quality hardening (BLOCKER — do first)
The index is currently dominated by a few corrupt rows where a quantity was mis-parsed (an account number, a value, or a "no. of shares" phrase captured as the share count). Concretely:
- PATHAN YUSUF (~Rs 6,505 cr), KHAN SAUMITRA (~Rs 3,640 cr), DR. SHARMILA SARKAR (~Rs 2,656 cr) are clearly wrong.
Required fixes:
- **Sanity-bound each position**: cross-check `qty × baseline_price` against the affidavit's **declared_value** for that line. If they diverge by more than, say, 3–5×, flag and drop or correct the quantity. The declared value is the ground truth we already scraped and are currently underusing.
- Handle quantity strings embedded in names ("No of Shares-6200", "Q. 4* 200 Rate") that the trailing-integer heuristic mis-reads.
- Add an absolute plausibility cap and a per-position outlier review list.
- Re-run the index only after this; expect the headline number to change materially.

### 3.2 Complete the candidate set
- Recover the ~58 missing winners (parse the winners table more robustly, or page through constituency-by-constituency).
- Decide whether to extend beyond winners to **all ~8,300 candidates** (the original disclosures are richest there) or keep to MPs.

### 3.3 Mutual fund standardisation (currently weak)
- MF holdings are extracted (661 positions, 121 MPs) but names are raw and inconsistent ("Mutual Fund", "SBI Mutual Fund", scheme codes like INF...). To track MF performance we need to map scheme names/codes to AMFI NAV data (AMFI publishes daily NAV with scheme codes). This is a separate matching problem from equities and is not yet started.
- "Most preferred fund" can be approximated now by AMC/keyword grouping even before full NAV tracking.

### 3.4 Methodology refinements
- Corporate actions: splits, bonuses, and mergers between June 2024 and now will distort `qty × price` (e.g. a stock that split 1:5 will look like a 80% loss). Need to adjust using yfinance's adjusted/split data or an actions feed.
- Delisted / suspended names (RCOM, Kingfisher-type) should be marked as such, not silently dropped.
- Baseline date: confirm per-candidate filing dates rather than a single 4 June 2024 date if precision matters.
- Spouse/HUF/dependent holdings are currently pooled into the candidate. Decide whether to keep pooled or split.

### 3.5 Front-end / website (not started)
Target views:
1. **Leaderboard** — MPs ranked by portfolio return, with party and constituency filters.
2. **Stock popularity** — most-held stocks, with each stock's own return and aggregate neta exposure.
3. **Neta Index vs Nifty** — a time series chart, not just two endpoints (requires fetching the full daily price history for the basket and rebasing both to 100).
4. **Per-MP detail** — full position table with declared vs current value.
5. **Fund view** — once §3.3 lands.

The dataset is already shaped for this: `neta_dataset.json` has `meta`, `portfolios[]` (with nested `positions[]`), and `preferred_stocks[]`. A static site reading that JSON, or a small API, would suffice. For a time-series index chart we additionally need a daily-history fetch step.

### 3.6 Refresh & automation
- Prices are a point-in-time snapshot. For a live tracker, schedule a daily price refresh (the holdings basket is fixed; only prices move).
- Affidavit scrape only needs re-running per election.

### 3.7 Caveats to surface in the product
- Affidavits are **self-declared**, dated to filing, and represent **disclosed** holdings only.
- Many MPs disclose value but **not quantity** → untrackable, excluded from the index. The index reflects only the trackable subset, which should be stated prominently.
- Unlisted/private company shares dominate raw holdings (2,140 of ~3,850 lines) and are intentionally excluded from market tracking.

---

## 4. Deliverables in this package

```
neta_tracker/
├── PRD.md                        ← this document
├── data/
│   ├── neta_dataset.json         ← FINAL structured dataset (powers the site): meta + portfolios + preferred_stocks
│   ├── portfolios_summary.csv    ← 40 trackable MP portfolios, one row each
│   ├── positions_detail.csv      ← 402 individual trackable positions (qty, base/cur price, return)
│   ├── preferred_stocks.csv      ← 240 stocks ranked by # MPs holding
│   ├── all_holdings_raw.csv      ← 3,850 extracted holdings incl. unlisted/MF/unmatched (full extraction)
│   ├── all_holdings_clean.json   ← all holdings with cleaned classification (machine-readable)
│   ├── all_holdings.json         ← pre-reclassification scrape (kept for diffing)
│   ├── prices.json               ← baseline (Jun 2024) + current prices per symbol incl. ^NSEI
│   ├── sample_holdings.json      ← original 3-candidate POC sample
│   └── winner_ids.json           ← 485 winner candidate IDs scraped
├── code/
│   ├── get_ids.py                ← scrape winner candidate IDs
│   ├── scrape_resume.py          ← resumable concurrent affidavit scraper + parser + classifier
│   ├── reclassify.py             ← hardened classifier / ticker matcher (re-run without re-scraping)
│   ├── fetch_prices.py           ← baseline + current price fetch
│   ├── build_dataset.py          ← performance engine + Neta Index, builds neta_dataset.json
│   └── export_csv.py             ← CSV exports
└── reference/
    └── EQUITY_L.csv              ← NSE equity master (2,365 symbols) used for matching
```

### Pipeline run order
`get_ids.py` → `scrape_resume.py` → `reclassify.py` → `fetch_prices.py` → `build_dataset.py` → `export_csv.py`

### Dependencies
`requests`, `beautifulsoup4`, `lxml`, `rapidfuzz`, `yfinance`

---

## 5. Immediate next step
Fix §3.1 (quantity sanity-check against declared value). It is the single thing standing between the current draft index and a number you can publish. Everything downstream — leaderboard, index chart, popularity — is built and waiting on clean inputs.
