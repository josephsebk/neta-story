import json, csv
ds=json.load(open("neta_dataset.json"))

# 1. Portfolio-level summary
with open("portfolios_summary.csv","w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["candidate_id","name","constituency","party","n_positions","base_value_jun2024","current_value","return_pct"])
    for p in ds["portfolios"]:
        w.writerow([p["candidate_id"],p["name"],p["constituency"],p["party"],p["n_positions"],p["base_value"],p["cur_value"],p["ret_pct"]])

# 2. Position-level detail (every neta-stock line that is trackable)
with open("positions_detail.csv","w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["candidate_id","name","party","symbol","stock_name","owner","qty","base_price","cur_price","base_value","cur_value","return_pct"])
    for p in ds["portfolios"]:
        for pos in p["positions"]:
            w.writerow([p["candidate_id"],p["name"],p["party"],pos["symbol"],pos["name"],pos["owner"],
                        pos["qty"],pos["base_price"],pos["cur_price"],pos["base_value"],pos["cur_value"],pos["ret_pct"]])

# 3. Preferred stocks (popularity)
with open("preferred_stocks.csv","w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["symbol","stock_name","n_mps_holding","aggregate_current_value","stock_return_pct"])
    for s in ds["preferred_stocks"]:
        w.writerow([s["symbol"],s["name"],s["holders"],s["agg_cur_value"],s["ret_pct"]])

# 4. ALL raw holdings (including unlisted/MF/unmatched) - the full extracted dataset
raw=json.load(open("all_holdings_clean.json"))
with open("all_holdings_raw.csv","w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["candidate_id","name","constituency","party","raw_name","owner","qty","declared_value","category","symbol","match_score"])
    for d in raw:
        if d.get("error"): continue
        for h in d.get("holdings",[]):
            w.writerow([d["candidate_id"],d["name"],d.get("constituency",""),d.get("party",""),
                        h["raw_name"],h["owner"],h["qty"],h["declared_value"],h["category"],h["symbol"],h["match_score"]])

for fn in ["portfolios_summary.csv","positions_detail.csv","preferred_stocks.csv","all_holdings_raw.csv"]:
    n=sum(1 for _ in open(fn))-1
    print(f"  {fn}: {n} rows")
