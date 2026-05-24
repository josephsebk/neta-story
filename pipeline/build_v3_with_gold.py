import json
import csv
import os

DS_FILE = "neta_dataset_v3.json"
GOLD_POSITIONS_FILE = "gold_positions_v3.csv"
OUT_FILE = "neta_dataset_v3_with_gold.json"
PRICES_FILE = "v3_out/prices.json"
FUND_NAVS_FILE = "v3_out/fund_navs.json"
HOLDINGS_MATCHED_FILE = "v3_out/holdings_matched.json"

# Pricing Model returns
PM_RETURNS = {
    "gold": 1.1480,        # +114.8%
    "silver": 1.9330,      # +193.3%
    "diamond": -0.1000,    # -10.0%
    "gemstone": 0.0000,    # 0.0%
    "mixed": 1.1480,       # +114.8%
    "unspecified": 1.1480  # +114.8%
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

def main():
    if not os.path.exists(DS_FILE):
        print(f"Base dataset {DS_FILE} not found!")
        return

    # Load original dataset
    with open(DS_FILE) as f:
        ds = json.load(f)

    gold_positions = load_gold_positions()
    print(f"Loaded gold positions for {len(gold_positions)} candidates.")

    # ==========================================
    # COHORT A: Original 102 Portfolios + Gold
    # ==========================================
    cohort_a_portfolios = []
    agg_eq_b = agg_eq_c = agg_fd_b = agg_fd_c = agg_pm_b = agg_pm_c = 0.0
    
    for p in ds["portfolios"]:
        cid = str(p["candidate_id"])
        
        # Base values from original portfolio
        eq_b = sum(pos["declared_value"] for pos in p["positions"] if pos["kind"] == "equity")
        eq_c = sum(pos["cur_value"] for pos in p["positions"] if pos["kind"] == "equity")
        fd_b = sum(pos["declared_value"] for pos in p["positions"] if pos["kind"] == "fund")
        fd_c = sum(pos["cur_value"] for pos in p["positions"] if pos["kind"] == "fund")
        
        pm_b = pm_c = 0.0
        pm_positions = []
        
        if cid in gold_positions:
            rows = gold_positions[cid]
            pm_positions = build_pm_positions(rows)
            pm_b = sum(pos["declared_value"] for pos in pm_positions)
            pm_c = sum(pos["cur_value"] for pos in pm_positions)

        # Merge positions
        combined_positions = p["positions"] + pm_positions
        
        base_total = eq_b + fd_b + pm_b
        cur_total = eq_c + fd_c + pm_c
        ret_pct = 100 * (cur_total - base_total) / base_total if base_total > 0 else 0.0
        
        cohort_a_portfolios.append({
            "candidate_id": p["candidate_id"],
            "name": p["name"],
            "constituency": p["constituency"],
            "party": p["party"],
            "eq_base": round(eq_b),
            "eq_value": round(eq_c),
            "fund_base": round(fd_b),
            "fund_value": round(fd_c),
            "pm_base": round(pm_b),
            "pm_value": round(pm_c),
            "base_value": round(base_total),
            "cur_value": round(cur_total),
            "ret_pct": round(ret_pct, 2),
            "n_equity": p["n_equity"],
            "n_fund": p["n_fund"],
            "n_pm": len(pm_positions),
            "positions": sorted(combined_positions, key=lambda x: -x["cur_value"])
        })
        
        agg_eq_b += eq_b
        agg_eq_c += eq_c
        agg_fd_b += fd_b
        agg_fd_c += fd_c
        agg_pm_b += pm_b
        agg_pm_c += pm_c

    cohort_a_portfolios.sort(key=lambda x: -x["cur_value"])
    
    # Cohort A Aggregates
    tot_b = agg_eq_b + agg_fd_b + agg_pm_b
    tot_c = agg_eq_c + agg_fd_c + agg_pm_c
    tot_ret = 100 * (tot_c - tot_b) / tot_b if tot_b > 0 else 0.0
    
    meta_a = {
        "baseline_date": ds["meta"]["baseline_date"],
        "n_portfolios": len(cohort_a_portfolios),
        "nifty_ret_pct": ds["meta"]["nifty_ret_pct"],
        "equity_base": round(agg_eq_b),
        "equity_cur": round(agg_eq_c),
        "fund_base": round(agg_fd_b),
        "fund_cur": round(agg_fd_c),
        "pm_base": round(agg_pm_b),
        "pm_cur": round(agg_pm_c),
        "combined_base": round(tot_b),
        "combined_cur": round(tot_c),
        "combined_index_ret_pct": round(tot_ret, 2)
    }

    # ==========================================
    # COHORT B: All Candidates (Stocks, Funds, Gold)
    # ==========================================
    cohort_b_portfolios = []
    
    # Load prices and fund navs
    prices = json.load(open(PRICES_FILE))
    B_eq = prices["baseline"]; C_eq = prices["current"]
    fund_navs = json.load(open(FUND_NAVS_FILE))
    B_fd = fund_navs["base"]; C_fd = fund_navs["cur"]
    
    # Load raw candidate matched holdings
    raw_data = json.load(open(HOLDINGS_MATCHED_FILE))
    
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

    # Map candidate_id to stock/fund holdings
    candidate_holdings = {}
    for d in raw_data:
        if d.get("error"):
            continue
        cid = str(d["candidate_id"])
        candidate_holdings[cid] = d

    # Collect all unique candidate IDs across BOTH holdings_matched and gold_positions
    all_cids = set(candidate_holdings.keys()) | set(gold_positions.keys())
    
    b_eq_b = b_eq_c = b_fd_b = b_fd_c = b_pm_b = b_pm_c = 0.0

    for cid in all_cids:
        pos = []
        eqb = eqc = fdb = fdc = 0.0
        seen_eq = set()
        seen_fd = set()
        
        # 1. Process Stock and Fund Holdings if present
        if cid in candidate_holdings:
            d = candidate_holdings[cid]
            name = d["name"]
            party = d.get("party", "")
            constituency = d.get("constituency", "")
            
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
        else:
            # Candidate only has gold holdings, fetch metadata from the first gold positions row
            rows = gold_positions[cid]
            name = rows[0]["mp_name"]
            party = rows[0]["party"]
            constituency = rows[0]["constituency"]

        # 2. Process Precious Metal Holdings if present
        pmb = pmc = 0.0
        pm_positions = []
        if cid in gold_positions:
            rows = gold_positions[cid]
            pm_positions = build_pm_positions(rows)
            pmb = sum(x["declared_value"] for x in pm_positions)
            pmc = sum(x["cur_value"] for x in pm_positions)

        combined_pos = pos + pm_positions
        base_t = eqb + fdb + pmb
        cur_t = eqc + fdc + pmc
        
        if base_t > 0:
            ret_p = 100 * (cur_t - base_t) / base_t
            cohort_b_portfolios.append({
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
                "base_value": round(base_t),
                "cur_value": round(cur_t),
                "ret_pct": round(ret_p, 2),
                "n_equity": len(seen_eq),
                "n_fund": len(seen_fd),
                "n_pm": len(pm_positions),
                "positions": sorted(combined_pos, key=lambda x: -x["cur_value"])
            })
            b_eq_b += eqb
            b_eq_c += eqc
            b_fd_b += fdb
            b_fd_c += fdc
            b_pm_b += pmb
            b_pm_c += pmc

    cohort_b_portfolios.sort(key=lambda x: -x["cur_value"])
    
    # Cohort B Aggregates
    b_tot_b = b_eq_b + b_fd_b + b_pm_b
    b_tot_c = b_eq_c + b_fd_c + b_pm_c
    b_tot_ret = 100 * (b_tot_c - b_tot_b) / b_tot_b if b_tot_b > 0 else 0.0
    
    meta_b = {
        "baseline_date": ds["meta"]["baseline_date"],
        "n_portfolios": len(cohort_b_portfolios),
        "nifty_ret_pct": ds["meta"]["nifty_ret_pct"],
        "equity_base": round(b_eq_b),
        "equity_cur": round(b_eq_c),
        "fund_base": round(b_fd_b),
        "fund_cur": round(b_fd_c),
        "pm_base": round(b_pm_b),
        "pm_cur": round(b_pm_c),
        "combined_base": round(b_tot_b),
        "combined_cur": round(b_tot_c),
        "combined_index_ret_pct": round(b_tot_ret, 2)
    }

    # Save output JSON
    output_data = {
        "cohort_a": {
            "meta": meta_a,
            "portfolios": cohort_a_portfolios
        },
        "cohort_b": {
            "meta": meta_b,
            "portfolios": cohort_b_portfolios
        }
    }
    
    with open(OUT_FILE, "w") as f:
        json.dump(output_data, f)
        
    print(f"\nSUCCESS: Generated {OUT_FILE} with itemized owner allocations.")
    print(f"Cohort A (Direct Match 102 Portfolios + Gold):")
    print(f"  Base Value   : Rs {meta_a['combined_base']/1e7:.2f} Cr")
    print(f"  Current Value: Rs {meta_a['combined_cur']/1e7:.2f} Cr")
    print(f"  Return       : {meta_a['combined_index_ret_pct']:+.2f}%")
    print(f"  PM Base      : Rs {meta_a['pm_base']/1e7:.2f} Cr")
    print(f"  PM Current   : Rs {meta_a['pm_cur']/1e7:.2f} Cr")

if __name__ == "__main__":
    main()
