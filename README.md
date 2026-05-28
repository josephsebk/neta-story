# Lok Sabha 2024 Winners: Movable Assets Investment Performance Tracker

An institutional-grade portfolio reconstruction and auditing engine that evaluates the investment performance of movable assets (listed equities and mutual funds) declared by the **Lok Sabha 2024 winners**.

---

## 1. Project Overview

This project compiles, structures, parses, and audits the financial portfolios declared in the official election nomination filings of the 2024 Lok Sabha winners. By integrating real-time and historical financial feeds, it reconstructs these portfolios to track their performance against the Indian stock market benchmark (**Nifty 50 Index**) from the election baseline to today.

To ensure analytical integrity and prevent severe asset distortions, **all family/promoter holdings for the three wealthiest candidates are excluded from active performance analysis**:
- **Konda Vishweshwar Reddy**: Excluded `APOLLOHOSP` (Apollo Hospitals) and `APOLSINHOT` (Apollo Sindoori Hotels).
- **Baijayant Panda**: Excluded `IMFA` (Indian Metals & Ferro Alloys) and `ORTEL` (Ortel Communications).
- **Naveen Jindal**: Excluded all Jindal/JSW group common shares (`JSL`, `JINDALSAW`, `JSWSTEEL`, `NSIL`, `JSWHL`, `HEXATRADEX`, `SHALPAINTS`, and `JINDALSTEL`).

---

## 2. Key Technical Accomplishments & Pipeline Architecture

The pipeline implements a **multi-layered classification defense** and an **auditing suite** to solve real-world data issues present in self-declared nomination affidavits:

### A. Bank Account & Savings Isolation
Self-declared affidavits often list savings bank accounts, current accounts, and fixed deposits under generic names like "SBI" or "HDFC". Standard matching algorithms erroneously map these to common stock tickers (`SBIN` or `HDFCBANK`), distorting actual stock holdings.
- **Regex Filtering**: Implemented strict keyword regex filters (`BANK_AC_KW` and `MF_INS_KW`) in `matcher_v2.py` to intercept terms like `a/c`, `savings`, `FD`, `fixed deposit`, `provident fund`, and route them directly to `unlisted_or_other`.
- **Token Intersection Maximization**: Utilizes overlap size ratios (`len(ta & tb) / min(len(ta), len(tb))`) rather than simple fuzzy match scores, successfully separating `"State Bank of India"` from `"Bank of India"`.
- **Bank-Account Isolation Rate**: Verified **100% precise separation**—e.g., routing 96 savings accounts to unlisted and leaving only 11 legitimate State Bank of India stock holdings.

### B. Fuzzy-Matching Hardening & Corporate Action Audits
- **The FMNL Anomaly Purge**: Putta Mahesh Kumar declared *"Investment In Market Share"* valued at **Rs 45.48 Crore**. Standard fuzzy matchers mapped *"Market Share"* to *"Future Market Networks Limited (FMNL)"*. Since FMNL has a total market cap of only **Rs 68.42 Crore**, this would mean the candidate owned ~66.5% of the public company. The matcher was hardened to treat generic investment descriptions as unlisted assets, completely purging this matching distortion.
- **Insolvency Action (Eastern Silk)**: Mukeshkumar Dalal's holding in Eastern Silk Industries (`EASTSILK`) was flagged as a +3054.4% return. Our audit resolved that the NCLT approved a resolution plan completely extinguishing all existing equity share capital with NIL consideration. The asset was adjusted to a **-100% return (Rs 0)**.
- **Raymond Demerger Adjustment**: Chhatrapati Shahu Shahaji and Brijendra Singh Ola's apparent **-74.6%** paper losses in Raymond Ltd. were audited and flagged as a wealth-neutral corporate action (demerger of Raymond Lifestyle) rather than an actual loss.

### C. Automated Asset Pricing Pipeline
- **Equities Pricing**: Integrated with Yahoo Finance (`yfinance`) using real-time close feeds.
- **Mutual Funds Pricing**: Fetches baseline and current Net Asset Values (NAVs) dynamically from the Association of Mutual Funds in India (AMFI) via `api.mfapi.in`, matching baseline NAVs to the nearest trading day in June 2024.
- **Nifty 50 Benchmark**: Dynamically tracks the index starting from the nomination baseline of **22,888.15** (May 28, 2024) to the current level (**23,817.85**), representing a benchmark market return of **+4.06%**.

---

## 3. Reconstructed Portfolio & Index Metrics

Running `build_v3.py` with Yahoo Finance historical pricing feeds and the AMFI API reconstructed the portfolios with outstanding precision:

### A. Total Reconstructed Assets (Including Family Promoter Stakes)
> [!IMPORTANT]
> This represents the total raw aggregate values across all 102 portfolios. It is heavily dominated by family promoter stakes (such as Konda Vishweshwar Reddy's Apollo Hospitals holdings).
```
======================================================
portfolios: 102
EQUITY index : Rs   2831cr ->   3954cr  +39.63%
FUND index   : Rs     70cr ->     77cr  +10.63%
COMBINED     : Rs   2901cr ->   4031cr  +38.93%
NIFTY 50     : +3.63% (Closing price close-to-close)
======================================================
```

#### Top 10 Portfolios (Total Assets, Including Family Stakes)
1. **KONDA VISHWESHWAR REDDY** (BJP) — **Rs 3,707.7 Cr** (+40.7%) (E14/F1)
2. **BAIJAYANT PANDA** (BJP) — **Rs 93.9 Cr** (+89.7%) (E6/F9)
3. **NAVEEN JINDAL** (BJP) — **Rs 45.6 Cr** (+5.6%) (E10/F0)
4. **AMIT SHAH** (BJP) — **Rs 34.4 Cr** (+5.4%) (E150/F0)
5. **ANURAG SHARMA** (BJP) — **Rs 19.7 Cr** (+11.7%) (E5/F15)
6. **CHHATRAPATI SHAHU SHAHAJI** (INC) — **Rs 18.7 Cr** (+2.4%) (E15/F0)
7. **SUPRIYA SULE** (NCP-SP) — **Rs 12.6 Cr** (+5.4%) (E32/F9)
8. **RAMASAHAYAM RAGHURAM REDDY** (INC) — **Rs 10.0 Cr** (+11.8%) (E16/F2)
9. **PIYUSH GOYAL** (BJP) — **Rs 8.8 Cr** (+1.8%) (E21/F1)
10. **RAVI SHANKAR PRASAD** (BJP) — **Rs 8.4 Cr** (+15.3%) (E0/F14)

### B. True Discretionary Public Index (Excluding Apollo, IMFA, Jindal, and Visaka)
> [!TIP]
> This represents their discretionary, public stock and mutual fund holdings, completely removing massive promoter blocks.
```
======================================================
portfolios: 102
EQUITY index : Rs    108cr ->    113cr  +4.21%
FUND index   : Rs     70cr ->     77cr  +10.63%
COMBINED     : Rs    178cr ->    190cr  +6.73%
NIFTY 50     : +3.63% (Closing price close-to-close)
======================================================
```

#### Top 10 Portfolios (Discretionary ex-promoters)
1. **AMIT SHAH** (BJP) — **Rs 34.39 Cr** (+5.4%) (E150/F0)
2. **ANURAG SHARMA** (BJP) — **Rs 19.72 Cr** (+11.7%) (E5/F15)
3. **CHHATRAPATI SHAHU SHAHAJI** (INC) — **Rs 18.73 Cr** (+2.4%) (E15/F0)
4. **SUPRIYA SULE** (NCP-SP) — **Rs 12.62 Cr** (+5.4%) (E32/F9)
5. **RAMASAHAYAM RAGHURAM REDDY** (INC) — **Rs 10.01 Cr** (+11.8%) (E16/F2)
6. **PIYUSH GOYAL** (BJP) — **Rs 8.85 Cr** (+1.8%) (E21/F1)
7. **RAVI SHANKAR PRASAD** (BJP) — **Rs 8.42 Cr** (+15.3%) (E0/F14)
8. **BAIJAYANT PANDA** (BJP) — **Rs 7.94 Cr** (-2.2%) (E4/F9)
9. **RAHUL GANDHI** (INC) — **Rs 7.68 Cr** (+5.7%) (E22/F3)
10. **RACHNA BANERJEE** (AITC) — **Rs 6.38 Cr** (+8.7%) (E32/F48)

---

## 4. Key Performance Insights

### A. Spouses Outperform the MPs
Analyzing ex-promoter portfolios by ownership category reveals that spouses manage money more dynamically than candidates themselves:
* **Spouse / Dependent**: **+8.69% Aggregate Return** (+8.37% Median Return) on **Rs 35.97 Crore** AUM (52 Spouses).
* **Self / HUF**: **+4.59% Aggregate Return** (+6.88% Median Return) on **Rs 148.66 Crore** AUM (90 MPs).

### B. Political Party Performance
Ranked by aggregate return percentage (only including parties with $\ge 2$ trackable portfolios):
1. **TDP**: 6 MPs | Aggregate **+8.96%** | Median Return **+7.00%** | Total AUM: **Rs 3.85 Cr**
2. **AITC**: 9 MPs | Aggregate **+7.33%** | Median Return **+6.80%** | Total AUM: **Rs 15.90 Cr**
3. **BJP**: 51 MPs | Aggregate **+6.94%** | Median Return **+10.10%** | Total AUM: **Rs 107.12 Cr**
4. **SP**: 2 MPs | Aggregate **+6.43%** | Median Return **+21.85%** | Total AUM: **Rs 0.07 Cr**
5. **AAP**: 2 MPs | Aggregate **+5.62%** | Median Return **+5.55%** | Total AUM: **Rs 0.64 Cr**
6. **NCP-SP**: 3 MPs | Aggregate **+5.43%** | Median Return **+5.50%** | Total AUM: **Rs 12.66 Cr**
7. **INC**: 20 MPs | Aggregate **+1.88%** | Median Return **+6.40%** | Total AUM: **Rs 53.20 Cr**
8. **DMK**: 2 MPs | Aggregate **+0.27%** | Median Return **+7.40%** | Total AUM: **Rs 1.69 Cr**

### C. Top Diversified "Super Pickers"
 Diversified candidates with multiple stock holdings returning $\ge$ +30%:
1. **Amit Shah** (BJP): **30 holdings** returning $\ge$ +30% ( diversified across 150+ stocks).
2. **Brijendra Singh Ola** (INC): **14 holdings** returning $\ge$ +30%.
3. **Rachna Banerjee** (AITC): **12 holdings** returning $\ge$ +30%.
4. **Arun Nehru** (DMK): **9 holdings** returning $\ge$ +30%.
5. **Supriya Sule** (NCP-SP): **8 holdings** returning $\ge$ +30%.
6. **Shatrughan Prasad Sinha** (AITC): **5 holdings** returning $\ge$ +30%.

---

## 5. Most Preferred Assets (Ex-Promoters)

### Top Stocks
* **By Number of Holders**: **Reliance Industries (`RELIANCE`)** is the most preferred stock (18 MPs), followed by **HDFC Bank (`HDFCBANK`)** with 15 MPs, **ITC** (14 MPs), and **Tata Steel** (12 MPs).
* **By Current Value (AUM)**: **United Spirits (`UNITDSPR`)** holds the highest concentration (**Rs 5.94 Crore** across 3 MPs), followed by **L&T** (**Rs 5.36 Crore** across 5 MPs), **Bharat Forge (`BHARATFORG`)** (**Rs 3.94 Crore** across 4 MPs), and **Canara Bank (`CANBK`)** (**Rs 3.83 Crore** across 4 MPs).

### Top Mutual Funds
* **By Number of Holders**: **ICICI Prudential MNC Fund** (`147345`) is the most popular scheme (10 MPs), followed by **Axis Small Cap Fund** (8 MPs) and **HDFC Flexi Cap Fund** (7 MPs).
* **By Current Value (AUM)**: **JM Low Duration Fund** (`143607`) represents the highest concentration (**Rs 4.18 Crore** across 2 MPs), followed by **SBI Equity Hybrid Fund** (**Rs 3.84 Crore**).

---

## 6. Directory File Structure

The project directory is structured as follows:

```
├── EQUITY_L.csv                # NSE Listed Equities Master List
├── portfolios_v3.csv           # Reconstructed candidate portfolio aggregates
├── positions_v3.csv            # Reconstructed position-level disclosures
├── preferred_stocks_v3.csv      # Preferred stocks analytics
├── preferred_funds_v3.csv       # Preferred mutual funds analytics
├── neta_dataset_v3.json        # Unified JSON database (includes complete tree)
├── PRD.md                      # Product Requirements Document
├── README.md                   # This Project Documentation file
└── v3_out/                     # Pipeline source directory
    ├── build_v3.py             # Main portfolio builder and pricer
    ├── matcher_v2.py           # Classification & matching engine
    ├── run_detailed_analysis.py# Analytics generation script (Ex-Promoter analysis)
    ├── export_csv_v3.py        # Exporter to flat CSVs
    └── amfi_schemes.json       # AMFI master list of mutual fund schemes
```

---

## 7. How to Run the Pipeline

To execute the portfolio parsing, matching, re-pricing, and analysis from scratch:

1. **Step 1: Clean and Match Holdings**
   Run the classification and matching engine on raw holdings:
   ```bash
   python3 matcher_v2.py
   ```
   *This generates `holdings_matched.json`.*

2. **Step 2: Pricing and Portfolio Rebuild**
   Fetch Yahoo Finance pricing and AMFI NAVs to reconstruct the portfolios:
   ```bash
   python3 build_v3.py
   ```
   *This outputs portfolio indexes and compiles `neta_dataset_v3.json`.*

3. **Step 3: Run Ex-Promoter Performance Analysis**
   Execute the analysis suite to calculate return rankings, spouses vs candidate metrics, party performances, and super pickers:
   ```bash
   python3 run_detailed_analysis.py
   ```

4. **Step 4: Export CSV flat files**
   Export the unified database into structured flat CSVs for external reporting or spreadsheets:
   ```bash
   python3 export_csv_v3.py
   ```
