import json

ds = json.load(open("neta_dataset_v3.json"))

# Define promoter stock symbols to exclude
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

# Reconstruct portfolios without promoter holdings
reconstructed_portfolios = []
all_individual_positions = []
stock_returns = {}
stock_names = {}

# Keep track of stock popularity and returns
for p in ds["portfolios"]:
    cname = p["name"]
    pos_list = []
    eq_b = eq_c = fd_b = fd_c = 0.0
    seen_eq = set()
    seen_fd = set()
    
    for pos in p["positions"]:
        symbol = pos["symbol"]
        kind = pos["kind"]
        owner = pos["owner"]
        dv = pos["declared_value"]
        cv = pos["cur_value"]
        ret = pos["ret_pct"]
        
        # Check if it's a promoter holding to exclude
        if is_promoter_holding(cname, symbol):
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
            stock_returns[symbol] = ret
            stock_names[symbol] = pos["name"]
        elif kind == "fund":
            fd_b += dv
            fd_c += cv
            seen_fd.add(symbol)
            
    tb = eq_b + fd_b
    tc = eq_c + fd_c
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
            "positions": pos_list,
            "eq_base": eq_b,
            "eq_cur": eq_c,
            "fund_base": fd_b,
            "fund_cur": fd_c
        })

print(f"Total reconstructed portfolios after promoter exclusions: {len(reconstructed_portfolios)}")

# 1. Best and worst investors (by return % and current value)
# Filter for portfolio value >= 10 Lakhs to avoid tiny portfolios distorting returns
print("\n--- BEST INVESTORS (BY RETURN % - PORTFOLIO >= 10 LAKHS) ---")
large_ports = [p for p in reconstructed_portfolios if p["base_value"] >= 1000000]
best_by_ret = sorted(large_ports, key=lambda x: -x["ret_pct"])
for i, p in enumerate(best_by_ret[:10]):
    print(f"{i+1}. {p['name']} ({p['party']}) | Base: Rs {p['base_value']/1e7:.2f} Cr | Cur: Rs {p['cur_value']/1e7:.2f} Cr | Return: {p['ret_pct']:+.2f}% (E{p['n_equity']}/F{p['n_fund']})")

print("\n--- WORST INVESTORS (BY RETURN % - PORTFOLIO >= 10 LAKHS) ---")
worst_by_ret = sorted(large_ports, key=lambda x: x["ret_pct"])
for i, p in enumerate(worst_by_ret[:10]):
    print(f"{i+1}. {p['name']} ({p['party']}) | Base: Rs {p['base_value']/1e7:.2f} Cr | Cur: Rs {p['cur_value']/1e7:.2f} Cr | Return: {p['ret_pct']:+.2f}% (E{p['n_equity']}/F{p['n_fund']})")

print("\n--- BEST INVESTORS BY ABSOLUTE GAINS (INR) ---")
best_by_abs = sorted(reconstructed_portfolios, key=lambda x: -(x["cur_value"] - x["base_value"]))
for i, p in enumerate(best_by_abs[:10]):
    gain = p["cur_value"] - p["base_value"]
    print(f"{i+1}. {p['name']} ({p['party']}) | Base: Rs {p['base_value']/1e7:.2f} Cr | Cur: Rs {p['cur_value']/1e7:.2f} Cr | Gain: Rs {gain/1e7:+.2f} Cr | Return: {p['ret_pct']:+.2f}%")

print("\n--- WORST INVESTORS BY ABSOLUTE LOSSES (INR) ---")
worst_by_abs = sorted(reconstructed_portfolios, key=lambda x: (x["cur_value"] - x["base_value"]))
for i, p in enumerate(worst_by_abs[:10]):
    gain = p["cur_value"] - p["base_value"]
    print(f"{i+1}. {p['name']} ({p['party']}) | Base: Rs {p['base_value']/1e7:.2f} Cr | Cur: Rs {p['cur_value']/1e7:.2f} Cr | Loss: Rs {gain/1e7:+.2f} Cr | Return: {p['ret_pct']:+.2f}%")

# 2. How do MPs on average compare to Nifty?
# Nifty return over this window is +4.06%
total_base = sum(p["base_value"] for p in reconstructed_portfolios)
total_cur = sum(p["cur_value"] for p in reconstructed_portfolios)
aggregate_ret = 100 * (total_cur - total_base) / total_base
simple_avg_ret = sum(p["ret_pct"] for p in reconstructed_portfolios) / len(reconstructed_portfolios)

print(f"\n--- PERFORMANCE COMPARISON TO NIFTY (+4.06%) ---")
print(f"Aggregate (Asset-Weighted) MP Portfolio Return: {aggregate_ret:.2f}%")
print(f"Simple Average MP Portfolio Return: {simple_avg_ret:.2f}%")
print(f"Number of MPs beating Nifty 50 (+4.06%): {sum(1 for p in reconstructed_portfolios if p['ret_pct'] > 4.06)} / {len(reconstructed_portfolios)} ({100 * sum(1 for p in reconstructed_portfolios if p['ret_pct'] > 4.06) / len(reconstructed_portfolios):.1f}%)")

# 3. Do spouses do better than MPs?
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

spouse_agg_ret = 100 * (spouse_cur - spouse_base) / spouse_base
self_agg_ret = 100 * (self_cur - self_base) / self_base
spouse_simple_avg = sum(spouse_returns) / len(spouse_returns) if spouse_returns else 0.0
self_simple_avg = sum(self_returns) / len(self_returns) if self_returns else 0.0

print(f"\n--- SPOUSE VS MP (SELF/HUF) PERFORMANCE ---")
print(f"Spouse Aggregate Return: {spouse_agg_ret:.2f}% (Base: Rs {spouse_base/1e7:.2f} Cr, Cur: Rs {spouse_cur/1e7:.2f} Cr)")
print(f"Self/HUF Aggregate Return: {self_agg_ret:.2f}% (Base: Rs {self_base/1e7:.2f} Cr, Cur: Rs {self_cur/1e7:.2f} Cr)")
print(f"Spouse Simple Average Return: {spouse_simple_avg:.2f}% (over {len(spouse_returns)} candidates with spouse holdings)")
print(f"Self/HUF Simple Average Return: {self_simple_avg:.2f}% (over {len(self_returns)} candidates)")

# 4. Best & Worst Stock Pickers (Individual Holdings level)
# Let's look at all individual equity positions
print("\n--- BEST STOCK PICKERS (TOP 10 INDIVIDUAL HOLDINGS BY RETURN %) ---")
eq_positions = [p for p in all_individual_positions if p["kind"] == "equity"]
best_picks = sorted(eq_positions, key=lambda x: -x["ret_pct"])
for i, pos in enumerate(best_picks[:15]):
    print(f"{i+1}. {pos['candidate']} ({pos['party']}) | Stock: {pos['symbol']} ({pos['name']}) | Declared: Rs {pos['declared_value']/1e7:.4f} Cr | Cur: Rs {pos['cur_value']/1e7:.4f} Cr | Return: {pos['ret_pct']:+.1f}% | Owner: {pos['owner']}")

print("\n--- WORST STOCK PICKERS (TOP 10 INDIVIDUAL HOLDINGS BY RETURN %) ---")
worst_picks = sorted(eq_positions, key=lambda x: x["ret_pct"])
for i, pos in enumerate(worst_picks[:15]):
    print(f"{i+1}. {pos['candidate']} ({pos['party']}) | Stock: {pos['symbol']} ({pos['name']}) | Declared: Rs {pos['declared_value']/1e7:.4f} Cr | Cur: Rs {pos['cur_value']/1e7:.4f} Cr | Return: {pos['ret_pct']:+.1f}% | Owner: {pos['owner']}")

# 5. Which party does better?
party_stats = {}
for p in reconstructed_portfolios:
    party = p["party"]
    if party not in party_stats:
        party_stats[party] = {"base": 0.0, "cur": 0.0, "count": 0, "returns": []}
    party_stats[party]["base"] += p["base_value"]
    party_stats[party]["cur"] += p["cur_value"]
    party_stats[party]["count"] += 1
    party_stats[party]["returns"].append(p["ret_pct"])

print("\n--- PARTY PERFORMANCE ---")
party_performance = []
for party, stats in party_stats.items():
    if stats["count"] >= 2:  # only include parties with at least 2 MPs to be representative
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
    print(f"{i+1}. {stats['party']} ({stats['count']} MPs) | Aggregate Return: {stats['agg_ret']:+.2f}% | Simple Avg Return: {stats['simple_avg']:+.2f}% | Total Portfolio: Rs {stats['cur']/1e7:.2f} Cr")

# 6. Anyone who has multiple best performing holdings?
# Let's count best performing stock holdings (say stocks with return > 30%) per candidate
print("\n--- MPS WITH MULTIPLE HIGH-PERFORMING STOCK HOLDINGS (>30% return) ---")
from collections import Counter
high_perf_counts = Counter()
for pos in eq_positions:
    if pos["ret_pct"] >= 30.0:
        high_perf_counts[pos["candidate"]] += 1

for name, count in high_perf_counts.most_common(10):
    print(f"  {name}: {count} holdings with return >= 30%")

