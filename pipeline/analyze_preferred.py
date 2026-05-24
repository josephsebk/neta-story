import json

ds = json.load(open("neta_dataset_v3.json"))

# Define promoter stocks to exclude
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

# Aggregate stocks and funds from reconstructed portfolios (ex-promoter holdings)
stock_stats = {}
fund_stats = {}

for p in ds["portfolios"]:
    cname = p["name"]
    seen_eq = set()
    seen_fd = set()
    
    for pos in p["positions"]:
        symbol = pos["symbol"]
        kind = pos["kind"]
        cv = pos["cur_value"]
        name = pos["name"]
        ret = pos["ret_pct"]
        
        if is_promoter_holding(cname, symbol):
            continue
            
        if kind == "equity":
            if symbol not in stock_stats:
                stock_stats[symbol] = {"symbol": symbol, "name": name, "holders": 0, "agg_val": 0.0, "returns": []}
            if symbol not in seen_eq:
                stock_stats[symbol]["holders"] += 1
                seen_eq.add(symbol)
            stock_stats[symbol]["agg_val"] += cv
            stock_stats[symbol]["returns"].append(ret)
            
        elif kind == "fund":
            if symbol not in fund_stats:
                fund_stats[symbol] = {"code": symbol, "name": name, "holders": 0, "agg_val": 0.0, "returns": []}
            if symbol not in seen_fd:
                fund_stats[symbol]["holders"] += 1
                seen_fd.add(symbol)
            fund_stats[symbol]["agg_val"] += cv
            fund_stats[symbol]["returns"].append(ret)

# Calculate average return for each asset
for symbol, stats in stock_stats.items():
    stats["avg_ret"] = sum(stats["returns"]) / len(stats["returns"]) if stats["returns"] else 0.0

for code, stats in fund_stats.items():
    stats["avg_ret"] = sum(stats["returns"]) / len(stats["returns"]) if stats["returns"] else 0.0

# Print results
print("=== TOP 10 MOST PREFERRED STOCKS BY NUMBER OF HOLDERS (EX-PROMOTERS) ===")
by_holders = sorted(stock_stats.values(), key=lambda x: -x["holders"])
for i, s in enumerate(by_holders[:10]):
    print(f"{i+1}. {s['symbol']} ({s['name']}) | Holders: {s['holders']} MPs | Current Value: Rs {s['agg_val']/1e7:.2f} Cr | Return: {s['avg_ret']:+.1f}%")

print("\n=== TOP 10 MOST PREFERRED STOCKS BY CURRENT VALUE (EX-PROMOTERS) ===")
by_value = sorted(stock_stats.values(), key=lambda x: -x["agg_val"])
for i, s in enumerate(by_value[:10]):
    print(f"{i+1}. {s['symbol']} ({s['name']}) | Holders: {s['holders']} MPs | Current Value: Rs {s['agg_val']/1e7:.2f} Cr | Return: {s['avg_ret']:+.1f}%")

print("\n=== TOP 10 MOST PREFERRED MUTUAL FUNDS BY NUMBER OF HOLDERS ===")
fund_by_holders = sorted(fund_stats.values(), key=lambda x: -x["holders"])
for i, f in enumerate(fund_by_holders[:10]):
    print(f"{i+1}. {f['code']} ({f['name']}) | Holders: {f['holders']} MPs | Current Value: Rs {f['agg_val']/1e7:.2f} Cr | Return: {f['avg_ret']:+.1f}%")

print("\n=== TOP 10 MOST PREFERRED MUTUAL FUNDS BY CURRENT VALUE ===")
fund_by_value = sorted(fund_stats.values(), key=lambda x: -x["agg_val"])
for i, f in enumerate(fund_by_value[:10]):
    print(f"{i+1}. {f['code']} ({f['name']}) | Holders: {f['holders']} MPs | Current Value: Rs {f['agg_val']/1e7:.2f} Cr | Return: {f['avg_ret']:+.1f}%")
