import json

DS_FILE = "neta_dataset_v3_with_gold.json"

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

def analyze_cohort(cohort_name, portfolios):
    print(f"\n==========================================")
    print(f"ANALYSIS FOR COHORT: {cohort_name.upper()}")
    print(f"==========================================")
    
    reconstructed_portfolios = []
    all_individual_positions = []
    
    for p in portfolios:
        cname = p["name"]
        pos_list = []
        eq_b = eq_c = fd_b = fd_c = pm_b = pm_c = 0.0
        seen_eq = set()
        seen_fd = set()
        seen_pm = set()
        
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
                
        tb = eq_b + fd_b + pm_b
        tc = eq_c + fd_c + pm_c
        
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
                "positions": pos_list,
                "eq_base": eq_b,
                "eq_cur": eq_c,
                "fund_base": fd_b,
                "fund_cur": fd_c,
                "pm_base": pm_b,
                "pm_cur": pm_c
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
    
    print(f"\n--- RECONSTRUCTED DISCRETIONARY PORTFOLIO METRICS ---")
    print(f"  EQUITY Index: Rs {eq_tot_b/1e7:.2f} Cr -> Rs {eq_tot_c/1e7:.2f} Cr ({eq_ret:+.2f}%)")
    print(f"  FUND Index:   Rs {fd_tot_b/1e7:.2f} Cr -> Rs {fd_tot_c/1e7:.2f} Cr ({fd_ret:+.2f}%)")
    print(f"  GOLD/PM Index:Rs {pm_tot_b/1e7:.2f} Cr -> Rs {pm_tot_c/1e7:.2f} Cr ({pm_ret:+.2f}%)")
    print(f"  COMBINED discretionary Portfolio:")
    print(f"    Asset-Weighted Aggregate Return: {aggregate_ret:.2f}% (Base: Rs {total_base/1e7:.2f} Cr, Cur: Rs {total_cur/1e7:.2f} Cr)")
    print(f"    Simple Average Return Per MP:    {simple_avg_ret:.2f}%")
    print(f"    MPs Beating Nifty 50 (+3.63%):   {sum(1 for p in reconstructed_portfolios if p['ret_pct'] > 3.63)} / {len(reconstructed_portfolios)} ({100 * sum(1 for p in reconstructed_portfolios if p['ret_pct'] > 3.63) / len(reconstructed_portfolios):.1f}%)")

    # 2. Leaderboard: Best Investors (Base >= 10L to avoid tiny base distortions)
    large_ports = [p for p in reconstructed_portfolios if p["base_value"] >= 1000000]
    best_by_ret = sorted(large_ports, key=lambda x: -x["ret_pct"])
    print("\n--- TOP 5 BEST INVESTORS (BY RETURN % - PORTFOLIO >= 10 LAKHS) ---")
    for i, p in enumerate(best_by_ret[:5]):
        print(f"  {i+1}. {p['name']} ({p['party']}) | Base: Rs {p['base_value']/1e7:.2f} Cr | Cur: Rs {p['cur_value']/1e7:.2f} Cr | Return: {p['ret_pct']:+.2f}% | (PM Base: Rs {p['pm_base']/1e7:.2f} Cr)")
        
    worst_by_ret = sorted(large_ports, key=lambda x: x["ret_pct"])
    print("\n--- TOP 5 WORST INVESTORS (BY RETURN % - PORTFOLIO >= 10 LAKHS) ---")
    for i, p in enumerate(worst_by_ret[:5]):
        print(f"  {i+1}. {p['name']} ({p['party']}) | Base: Rs {p['base_value']/1e7:.2f} Cr | Cur: Rs {p['cur_value']/1e7:.2f} Cr | Return: {p['ret_pct']:+.2f}% | (PM Base: Rs {p['pm_base']/1e7:.2f} Cr)")

    best_by_abs = sorted(reconstructed_portfolios, key=lambda x: -(x["cur_value"] - x["base_value"]))
    print("\n--- TOP 5 ABSOLUTE WEALTH GAINERS (INR) ---")
    for i, p in enumerate(best_by_abs[:5]):
        gain = p["cur_value"] - p["base_value"]
        print(f"  {i+1}. {p['name']} ({p['party']}) | Base: Rs {p['base_value']/1e7:.2f} Cr | Cur: Rs {p['cur_value']/1e7:.2f} Cr | Gain: Rs {gain/1e7:+.2f} Cr | Return: {p['ret_pct']:+.2f}%")

    worst_by_abs = sorted(reconstructed_portfolios, key=lambda x: (x["cur_value"] - x["base_value"]))
    print("\n--- TOP 5 ABSOLUTE WEALTH LOSERS (INR) ---")
    for i, p in enumerate(worst_by_abs[:5]):
        loss = p["cur_value"] - p["base_value"]
        print(f"  {i+1}. {p['name']} ({p['party']}) | Base: Rs {p['base_value']/1e7:.2f} Cr | Cur: Rs {p['cur_value']/1e7:.2f} Cr | Loss: Rs {loss/1e7:+.2f} Cr | Return: {p['ret_pct']:+.2f}%")

    # 3. Party Performance (at least 2 MPs)
    party_stats = {}
    for p in reconstructed_portfolios:
        party = p["party"]
        if party not in party_stats:
            party_stats[party] = {"base": 0.0, "cur": 0.0, "count": 0, "returns": []}
        party_stats[party]["base"] += p["base_value"]
        party_stats[party]["cur"] += p["cur_value"]
        party_stats[party]["count"] += 1
        party_stats[party]["returns"].append(p["ret_pct"])

    print("\n--- POLITICAL PARTY PERFORMANCE (>= 2 MPs) ---")
    party_performance = []
    for party, stats in party_stats.items():
        if stats["count"] >= 2:
            agg_ret = 100 * (stats["cur"] - stats["base"]) / stats["base"]
            simple_avg = sum(stats["returns"]) / len(stats["returns"])
            party_performance.append({
                "party": party,
                "count": stats["count"],
                "base": stats["base"],
                "cur": stats["cur"],
                "agg_ret": agg_ret,
                "simple_avg": simple_avg
            })
    party_performance = sorted(party_performance, key=lambda x: -x["agg_ret"])
    for i, stats in enumerate(party_performance):
        print(f"  {i+1}. {stats['party']:<20} ({stats['count']} MPs) | Aggregate: {stats['agg_ret']:+.2f}% | Simple Avg: {stats['simple_avg']:+.2f}% | Total Value: Rs {stats['cur']/1e7:.2f} Cr")

    # 3.5 Spouse vs Self Performance
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

    # 4. Top Gold Holders
    print("\n--- TOP 5 DECLARED GOLD/PM HOLDERS ---")
    gold_holders = sorted(reconstructed_portfolios, key=lambda x: -x["pm_base"])
    for i, p in enumerate(gold_holders[:10]):
        print(f"  {i+1}. {p['name']:<30} ({p['party']:<10}) | Declared PM: Rs {p['pm_base']/1e7:>6.2f} Cr | Current PM: Rs {p['pm_cur']/1e7:>6.2f} Cr | Combined Portfolio Return: {p['ret_pct']:+.2f}%")

    return {
        "reconstructed_portfolios": reconstructed_portfolios,
        "meta": {
            "equity_base": eq_tot_b, "equity_cur": eq_tot_c, "equity_ret": eq_ret,
            "fund_base": fd_tot_b, "fund_cur": fd_tot_c, "fund_ret": fd_ret,
            "pm_base": pm_tot_b, "pm_cur": pm_tot_c, "pm_ret": pm_ret,
            "combined_base": total_base, "combined_cur": total_cur, "combined_ret": aggregate_ret,
            "simple_avg": simple_avg_ret
        }
    }

def main():
    with open(DS_FILE) as f:
        data = json.load(f)
        
    res_a = analyze_cohort("cohort_a", data["cohort_a"]["portfolios"])
    res_b = analyze_cohort("cohort_b", data["cohort_b"]["portfolios"])

if __name__ == "__main__":
    main()
