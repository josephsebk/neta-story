import json

DS_FILE = "neta_dataset_v3_with_alternatives.json"

PROMOTER_MAP = {
    "KONDA VISHWESHWAR REDDY": {"APOLLOHOSP", "APOLSINHOT"},
    "BAIJAYANT PANDA": {"IMFA", "ORTEL"},
    "NAVEEN JINDAL": {"JSL", "JINDALSAW", "JSWSTEEL", "NSIL", "JSWHL", "HEXATRADEX", "SHALPAINTS", "JINDALSTEL"},
    "VAMSI KRISHNA GADDAM": {"VISAKAIND"}
}

def is_promoter_holding(candidate_name, symbol):
    if candidate_name in PROMOTER_MAP:
        if symbol in PROMOTER_MAP[candidate_name]:
            return True
    return False

def main():
    with open(DS_FILE) as f:
        data = json.load(f)
        
    portfolios = data["portfolios"]
    print(f"\n==========================================")
    print(f"ANALYSIS WITH GOLD & ALTERNATIVE ASSETS (463 MPs)")
    print(f"==========================================")
    
    reconstructed_portfolios = []
    all_individual_positions = []
    
    for p in portfolios:
        cname = p["name"]
        pos_list = []
        eq_b = eq_c = fd_b = fd_c = pm_b = pm_c = alt_b = alt_c = 0.0
        seen_eq = set()
        seen_fd = set()
        seen_pm = set()
        seen_alt = set()
        
        for pos in p["positions"]:
            symbol = pos.get("symbol")
            kind = pos["kind"]
            dv = pos["declared_value"]
            cv = pos["cur_value"]
            ret = pos["ret_pct"]
            
            # Check if promoter equity to exclude
            if kind == "equity" and is_promoter_holding(cname, symbol):
                continue
                
            pos_list.append(pos)
            all_individual_positions.append({
                "candidate": cname,
                "party": p["party"],
                "constituency": p["constituency"],
                **pos
            })
            
            if kind == "equity":
                eq_b += dv
                eq_c += cv
                seen_eq.add(symbol)
            elif kind == "fund":
                fd_b += dv
                fd_c += cv
                seen_fd.add(symbol)
            elif kind == "precious_metal":
                pm_b += dv
                pm_c += cv
                seen_pm.add(symbol)
            elif kind == "alternative":
                alt_b += dv
                alt_c += cv
                seen_alt.add(symbol)
                
        tb = eq_b + fd_b + pm_b + alt_b
        tc = eq_c + fd_c + pm_c + alt_c
        
        if tb > 0:
            ret_pct = 100 * (tc - tb) / tb
            reconstructed_portfolios.append({
                "candidate_id": p["candidate_id"],
                "name": cname,
                "party": p["party"],
                "constituency": p["constituency"],
                "base_value": tb,
                "cur_value": tc,
                "ret_pct": round(ret_pct, 2),
                "n_equity": len(seen_eq),
                "n_fund": len(seen_fd),
                "n_pm": len(seen_pm),
                "n_alt": len(seen_alt),
                "positions": pos_list,
                "eq_base": eq_b,
                "eq_cur": eq_c,
                "fund_base": fd_b,
                "fund_cur": fd_c,
                "pm_base": pm_b,
                "pm_cur": pm_c,
                "alt_base": alt_b,
                "alt_cur": alt_c
            })
            
    print(f"Total reconstructed ex-promoter portfolios: {len(reconstructed_portfolios)}")
    
    # 1. Benchmark & Index Returns
    total_base = sum(p["base_value"] for p in reconstructed_portfolios)
    total_cur = sum(p["cur_value"] for p in reconstructed_portfolios)
    aggregate_ret = 100 * (total_cur - total_base) / total_base if total_base > 0 else 0.0
    simple_avg_ret = sum(p["ret_pct"] for p in reconstructed_portfolios) / len(reconstructed_portfolios) if reconstructed_portfolios else 0.0
    
    eq_tot_b = sum(p["eq_base"] for p in reconstructed_portfolios)
    eq_tot_c = sum(p["eq_cur"] for p in reconstructed_portfolios)
    eq_ret = 100 * (eq_tot_c - eq_tot_b) / eq_tot_b if eq_tot_b > 0 else 0.0
    
    fd_tot_b = sum(p["fund_base"] for p in reconstructed_portfolios)
    fd_tot_c = sum(p["fund_cur"] for p in reconstructed_portfolios)
    fd_ret = 100 * (fd_tot_c - fd_tot_b) / fd_tot_b if fd_tot_b > 0 else 0.0
    
    pm_tot_b = sum(p["pm_base"] for p in reconstructed_portfolios)
    pm_tot_c = sum(p["pm_cur"] for p in reconstructed_portfolios)
    pm_ret = 100 * (pm_tot_c - pm_tot_b) / pm_tot_b if pm_tot_b > 0 else 0.0
    
    alt_tot_b = sum(p["alt_base"] for p in reconstructed_portfolios)
    alt_tot_c = sum(p["alt_cur"] for p in reconstructed_portfolios)
    alt_ret = 100 * (alt_tot_c - alt_tot_b) / alt_tot_b if alt_tot_b > 0 else 0.0
    
    print(f"\n--- RECONSTRUCTED DISCRETIONARY PORTFOLIO METRICS ---")
    print(f"  EQUITY Index: Rs {eq_tot_b/1e7:.2f} Cr -> Rs {eq_tot_c/1e7:.2f} Cr ({eq_ret:+.2f}%)")
    print(f"  FUND Index:   Rs {fd_tot_b/1e7:.2f} Cr -> Rs {fd_tot_c/1e7:.2f} Cr ({fd_ret:+.2f}%)")
    print(f"  GOLD/PM Index:Rs {pm_tot_b/1e7:.2f} Cr -> Rs {pm_tot_c/1e7:.2f} Cr ({pm_ret:+.2f}%)")
    print(f"  ALT Index:    Rs {alt_tot_b/1e7:.2f} Cr -> Rs {alt_tot_c/1e7:.2f} Cr ({alt_ret:+.2f}%)")
    print(f"  COMBINED discretionary Portfolio:")
    print(f"    Asset-Weighted Aggregate Return: {aggregate_ret:.2f}% (Base: Rs {total_base/1e7:.2f} Cr, Cur: Rs {total_cur/1e7:.2f} Cr)")
    print(f"    Simple Average Return Per MP:    {simple_avg_ret:.2f}%")
    print(f"    MPs Beating Nifty 50 (+3.63%):   {sum(1 for p in reconstructed_portfolios if p['ret_pct'] > 3.63)} / {len(reconstructed_portfolios)} ({100 * sum(1 for p in reconstructed_portfolios if p['ret_pct'] > 3.63) / len(reconstructed_portfolios):.1f}%)")

    # 2. Shashi Tharoor Case Study
    st = next((p for p in reconstructed_portfolios if p["candidate_id"] == 2313), None)
    if st:
        print(f"\n--- SHASHI THAROOR PORTFOLIO DEEP DIVE ---")
        print(f"  Base Value   : Rs {st['base_value']/1e7:.4f} Cr (Rs {st['base_value']:,})")
        print(f"  Current Value: Rs {st['cur_value']/1e7:.4f} Cr (Rs {st['cur_value']:,})")
        print(f"  Combined Ret : {st['ret_pct']:+.2f}%")
        print(f"  Asset Breakdown:")
        print(f"    Domestic Funds: Rs {st['fund_base']/1e7:.4f} Cr ({st['n_fund']} funds matched)")
        print(f"    Physical Gold : Rs {st['pm_base']/1e7:.4f} Cr (543 grams)")
        print(f"    Alternatives  : Rs {st['alt_base']/1e7:.4f} Cr ({st['n_alt']} offshore/PMS positions)")

    # 3. Leaderboard: Best Investors (Base >= 10L to avoid tiny base distortions)
    large_ports = [p for p in reconstructed_portfolios if p["base_value"] >= 1000000]
    best_by_ret = sorted(large_ports, key=lambda x: -x["ret_pct"])
    print("\n--- TOP 5 BEST INVESTORS (BY RETURN % - PORTFOLIO >= 10 LAKHS) ---")
    for i, p in enumerate(best_by_ret[:5]):
        print(f"  {i+1}. {p['name']} ({p['party']}) | Base: Rs {p['base_value']/1e7:.2f} Cr | Cur: Rs {p['cur_value']/1e7:.2f} Cr | Return: {p['ret_pct']:+.2f}% | (PM Base: Rs {p['pm_base']/1e7:.2f} Cr, Alt Base: Rs {p['alt_base']/1e7:.2f} Cr)")
        
    worst_by_ret = sorted(large_ports, key=lambda x: x["ret_pct"])
    print("\n--- TOP 5 WORST INVESTORS (BY RETURN % - PORTFOLIO >= 10 LAKHS) ---")
    for i, p in enumerate(worst_by_ret[:5]):
        print(f"  {i+1}. {p['name']} ({p['party']}) | Base: Rs {p['base_value']/1e7:.2f} Cr | Cur: Rs {p['cur_value']/1e7:.2f} Cr | Return: {p['ret_pct']:+.2f}% | (PM Base: Rs {p['pm_base']/1e7:.2f} Cr)")

    best_by_abs = sorted(reconstructed_portfolios, key=lambda x: -(x["cur_value"] - x["base_value"]))
    print("\n--- TOP 5 ABSOLUTE WEALTH GAINERS (INR) ---")
    for i, p in enumerate(best_by_abs[:5]):
        gain = p["cur_value"] - p["base_value"]
        print(f"  {i+1}. {p['name']} ({p['party']}) | Base: Rs {p['base_value']/1e7:.2f} Cr | Cur: Rs {p['cur_value']/1e7:.2f} Cr | Gain: Rs {gain/1e7:+.2f} Cr | Return: {p['ret_pct']:+.2f}%")

    # 4. Spouse vs Self Performance
    spouse_base = spouse_cur = 0.0
    self_base = self_cur = 0.0
    spouse_returns = []
    self_returns = []
    
    for p in reconstructed_portfolios:
        sp_b = sp_c = 0.0
        sl_b = sl_c = 0.0
        for pos in p["positions"]:
            owner = pos["owner"].lower()
            dv = pos["declared_value"]
            cv = pos["cur_value"]
            if "spouse" in owner:
                spouse_base += dv
                spouse_cur += cv
                sp_b += dv
                sp_c += cv
            elif "self" in owner or "huf" in owner:
                self_base += dv
                self_cur += cv
                sl_b += dv
                sl_c += cv
                
        if sp_b > 0:
            spouse_returns.append(100 * (sp_c - sp_b) / sp_b)
        if sl_b > 0:
            self_returns.append(100 * (sl_c - sl_b) / sl_b)
            
    spouse_agg_ret = 100 * (spouse_cur - spouse_base) / spouse_base if spouse_base > 0 else 0.0
    self_agg_ret = 100 * (self_cur - self_base) / self_base if self_base > 0 else 0.0
    spouse_simple_avg = sum(spouse_returns) / len(spouse_returns) if spouse_returns else 0.0
    self_simple_avg = sum(self_returns) / len(self_returns) if self_returns else 0.0
    
    print(f"\n--- SPOUSE VS MP (SELF/HUF) PERFORMANCE ---")
    print(f"  Spouse Aggregate Return:     {spouse_agg_ret:.2f}% (Base: Rs {spouse_base/1e7:.2f} Cr, Cur: Rs {spouse_cur/1e7:.2f} Cr)")
    print(f"  Self/HUF Aggregate Return:   {self_agg_ret:.2f}% (Base: Rs {self_base/1e7:.2f} Cr, Cur: Rs {self_cur/1e7:.2f} Cr)")
    print(f"  Spouse Simple Average Return: {spouse_simple_avg:.2f}% (over {len(spouse_returns)} candidates)")
    print(f"  Self/HUF Simple Average Return: {self_simple_avg:.2f}% (over {len(self_returns)} candidates)")

if __name__ == "__main__":
    main()
