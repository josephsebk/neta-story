import json
import csv
import re
import os

HOLDINGS_FILE = "v3_out/holdings_matched_v3.json"
PRICES_FILE = "v3_out/prices.json"
FUND_NAVS_FILE = "v3_out/fund_navs.json"
GOLD_POSITIONS_FILE = "gold_positions_v3.csv"
OUT_FILE = "neta_dataset_v3_with_alternatives.json"

# Return Pricing Models
PM_RETURNS = {
    "gold": 1.1480,        # +114.8%
    "silver": 1.9330,      # +193.3%
    "diamond": -0.1000,    # -10.0%
    "gemstone": 0.0000,    # 0.0%
    "mixed": 1.1480,       # +114.8%
    "unspecified": 1.1480  # +114.8%
}

ALT_RETURNS = {
    "global_equity": 0.2500,     # +25.0%
    "corp_bond": 0.1660,         # +16.6%
    "us_treasury": 0.1050,       # +10.5%
    "pms": 0.1500,               # +15.0%
    "rbi_bond": 0.1670,          # +16.7%
    "crypto": 0.0700             # +7.0%
}

# Regex keywords for alternative assets
ALT_PATTERNS = {
    "global_equity": re.compile(r"\b(outside\s+india|foreign\s+equity|overseas\s+equity|foreign\s+shares?|global\s+equities|foreign\s+stock|shares?\s+outside)\b", re.I),
    "corp_bond": re.compile(r"\b(corporate\s+bonds?|corporate\s+debentures?|company\s+deposits?|ncds?|non\s+convertible\s+debentures?|corporate\s+deposits?|certificate\s+of\s+deposits?)\b", re.I),
    "us_treasury": re.compile(r"\b(us\s+treasury|us\s+treasuries|treasury\s+bills?|t-bills?|us\s+debt|us\s+security|us\s+securities)\b", re.I),
    "pms": re.compile(r"\b(pms|portfolio\s+management|estee\s+advisors|estee\s+capital|jm\s+financial\s+portfolio|pms\s+investment|portfolio\s+investment)\b", re.I),
    "rbi_bond": re.compile(r"\b(rbi\s+bonds?|reserve\s+bank\s+of\s+india\s+bonds?|rbi\s+savings\s+bonds?)\b", re.I),
    "crypto": re.compile(r"\b(bitcoin|crypto|btc|ethereum|eth)\b", re.I)
}

def load_gold_positions():
    gold_data = {}
    if not os.path.exists(GOLD_POSITIONS_FILE):
        return gold_data
    with open(GOLD_POSITIONS_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = str(row["candidate_id"])
            if cid not in gold_data:
                gold_data[cid] = []
            gold_data[cid].append(row)
    return gold_data

def build_pm_positions(rows):
    pos = []
    for r in rows:
        val = int(r["declared_value_inr"]) if r.get("declared_value_inr") else 0
        wt = float(r["weight_grams"]) if r.get("weight_grams") else 0.0
        carat = float(r["carats"]) if r.get("carats") else 0.0
        cat = r["category"]
        owner = r["owner"]
        desc = r["raw_description"]
        
        if val > 0:
            ret = PM_RETURNS[cat]
            cv = val * (1 + ret)
            pos.append({
                "kind": "precious_metal",
                "symbol": cat.upper(),
                "name": f"Physical {cat.capitalize()} Holdings",
                "owner": owner,
                "declared_value": val,
                "cur_value": round(cv),
                "ret_pct": round(ret * 100, 1),
                "weight_grams": wt,
                "carats": carat,
                "description": desc
            })
    return pos

def detect_alternative_assets(holdings):
    alt_positions = []
    for h in holdings:
        # We only check unlisted_or_other holdings to avoid double-counting matched stocks/funds
        if h.get("category") == "unlisted_or_other":
            raw = h["raw_name"]
            clean = h["clean_name"]
            val = h["declared_value"]
            owner = h["owner"]
            
            if not val or val <= 0:
                continue
                
            for asset_class, pat in ALT_PATTERNS.items():
                if pat.search(raw) or pat.search(clean):
                    ret = ALT_RETURNS[asset_class]
                    cv = val * (1 + ret)
                    alt_positions.append({
                        "kind": "alternative",
                        "symbol": asset_class.upper(),
                        "name": f"{asset_class.replace('_', ' ').capitalize()} Investment",
                        "owner": owner,
                        "declared_value": val,
                        "cur_value": round(cv),
                        "ret_pct": round(ret * 100, 1),
                        "raw_description": raw
                    })
                    break  # map to the first matched asset class
    return alt_positions

def main():
    # Load prices and fund navs
    prices = json.load(open(PRICES_FILE))
    B_eq = prices["baseline"]; C_eq = prices["current"]
    fund_navs = json.load(open(FUND_NAVS_FILE))
    B_fd = fund_navs["base"]; C_fd = fund_navs["cur"]
    
    # Load newly matched holdings
    raw_data = json.load(open(HOLDINGS_FILE))
    gold_positions = load_gold_positions()
    
    # Load equity names
    EQ_SYM2NAME = {}
    if os.path.exists("EQUITY_L.csv"):
        with open("EQUITY_L.csv") as f:
            for row in csv.DictReader(f):
                EQ_SYM2NAME[row["SYMBOL"].strip()] = row["NAME OF COMPANY"].strip()
    EQ_SYM2NAME["TATAMOTORS"] = "Tata Motors Limited"
    EQ_SYM2NAME["APOLLOHOSP"] = "Apollo Hospitals Enterprise Limited"
    EQ_SYM2NAME["NDRINVIT"] = "NDR InvIT Trust"
    EQ_SYM2NAME["META"] = "Meta Platforms, Inc."
    EQ_SYM2NAME["IVV"] = "iShares Core S&P 500 ETF"

    portfolios = []
    
    # Global index statistics
    agg_eq_b = agg_eq_c = agg_fd_b = agg_fd_c = agg_pm_b = agg_pm_c = agg_alt_b = agg_alt_c = 0.0
    
    for d in raw_data:
        if d.get("error"):
            continue
            
        cid = str(d["candidate_id"])
        name = d["name"]
        party = d.get("party", "")
        constituency = d.get("constituency", "")
        
        pos = []
        eqb = eqc = fdb = fdc = 0.0
        seen_eq = set()
        seen_fd = set()
        
        # 1. Stocks and Funds
        for h in d.get("holdings", []):
            dv = h["declared_value"] or 0
            if dv <= 0:
                continue
            if h["category"] == "listed_equity" and h["eq_symbol"]:
                s = h["eq_symbol"]
                if s in B_eq and B_eq[s] is not None and s in C_eq and C_eq[s] is not None:
                    if s == "EASTSILK":
                        r = -1.0
                        cv = 0.0
                    elif s == "RAYMOND":
                        r = -0.228
                        cv = dv * (1 + r)
                    else:
                        r = (C_eq[s] - B_eq[s]) / B_eq[s]
                        cv = dv * (1 + r)
                    eqb += dv
                    eqc += cv
                    seen_eq.add(s)
                    pos.append({
                        "kind": "equity",
                        "symbol": s,
                        "name": EQ_SYM2NAME.get(s, s),
                        "owner": h["owner"],
                        "declared_value": round(dv),
                        "cur_value": round(cv),
                        "ret_pct": round(100 * r, 1)
                    })
            elif h["category"] == "mutual_fund" and h["fund_code"]:
                fc = h["fund_code"]
                if fc in B_fd and B_fd[fc] is not None and fc in C_fd and C_fd[fc] is not None:
                    r = (C_fd[fc] - B_fd[fc]) / B_fd[fc]
                    cv = dv * (1 + r)
                    fdb += dv
                    fdc += cv
                    seen_fd.add(fc)
                    pos.append({
                        "kind": "fund",
                        "symbol": fc,
                        "name": h["match_name"],
                        "owner": h["owner"],
                        "declared_value": round(dv),
                        "cur_value": round(cv),
                        "ret_pct": round(100 * r, 1)
                    })
                    
        # 2. Precious Metals
        pmb = pmc = 0.0
        pm_positions = []
        if cid in gold_positions:
            rows = gold_positions[cid]
            pm_positions = build_pm_positions(rows)
            pmb = sum(x["declared_value"] for x in pm_positions)
            pmc = sum(x["cur_value"] for x in pm_positions)
            
        # 3. Alternative Assets
        altb = altc = 0.0
        alt_positions = detect_alternative_assets(d.get("holdings", []))
        if alt_positions:
            altb = sum(x["declared_value"] for x in alt_positions)
            altc = sum(x["cur_value"] for x in alt_positions)
            
        combined_pos = pos + pm_positions + alt_positions
        base_t = eqb + fdb + pmb + altb
        cur_t = eqc + fdc + pmc + altc
        
        if base_t > 0:
            ret_p = 100 * (cur_t - base_t) / base_t
            portfolios.append({
                "candidate_id": int(cid),
                "name": name,
                "constituency": constituency,
                "party": party,
                "eq_base": round(eqb),
                "eq_value": round(eqc),
                "fund_base": round(fdb),
                "fund_value": round(fdc),
                "pm_base": round(pmb),
                "pm_value": round(pmc),
                "alt_base": round(altb),
                "alt_value": round(altc),
                "base_value": round(base_t),
                "cur_value": round(cur_t),
                "ret_pct": round(ret_p, 2),
                "n_equity": len(seen_eq),
                "n_fund": len(seen_fd),
                "n_pm": len(pm_positions),
                "n_alt": len(alt_positions),
                "positions": sorted(combined_pos, key=lambda x: -x["cur_value"])
            })
            agg_eq_b += eqb
            agg_eq_c += eqc
            agg_fd_b += fdb
            agg_fd_c += fdc
            agg_pm_b += pmb
            agg_pm_c += pmc
            agg_alt_b += altb
            agg_alt_c += altc

    portfolios.sort(key=lambda x: -x["cur_value"])
    
    # Cohort B Aggregates (all portfolios with any asset)
    tot_b = agg_eq_b + agg_fd_b + agg_pm_b + agg_alt_b
    tot_c = agg_eq_c + agg_fd_c + agg_pm_c + agg_alt_c
    tot_ret = 100 * (tot_c - tot_b) / tot_b if tot_b > 0 else 0.0
    
    meta = {
        "baseline_date": "2024-06-04",
        "n_portfolios": len(portfolios),
        "equity_base": round(agg_eq_b),
        "equity_cur": round(agg_eq_c),
        "fund_base": round(agg_fd_b),
        "fund_cur": round(agg_fd_c),
        "pm_base": round(agg_pm_b),
        "pm_cur": round(agg_pm_c),
        "alt_base": round(agg_alt_b),
        "alt_cur": round(agg_alt_c),
        "combined_base": round(tot_b),
        "combined_cur": round(tot_c),
        "combined_index_ret_pct": round(tot_ret, 2)
    }

    output_data = {
        "meta": meta,
        "portfolios": portfolios
    }
    
    with open(OUT_FILE, "w") as f:
        json.dump(output_data, f)
        
    print(f"\nSUCCESS: Generated {OUT_FILE} containing stocks, funds, physical gold, and alternative assets!")
    print(f"Index Aggregates:")
    print(f"  Portfolios   : {meta['n_portfolios']}")
    print(f"  Base Value   : Rs {meta['combined_base']/1e7:.2f} Cr")
    print(f"  Current Value: Rs {meta['combined_cur']/1e7:.2f} Cr")
    print(f"  Index Return : {meta['combined_index_ret_pct']:+.2f}%")
    print(f"  Stocks Base  : Rs {meta['equity_base']/1e7:.2f} Cr")
    print(f"  Funds Base   : Rs {meta['fund_base']/1e7:.2f} Cr")
    print(f"  Gold Base    : Rs {meta['pm_base']/1e7:.2f} Cr")
    print(f"  Alts Base    : Rs {meta['alt_base']/1e7:.2f} Cr")

if __name__ == "__main__":
    main()
