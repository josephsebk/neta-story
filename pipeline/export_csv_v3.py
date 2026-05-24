import json, csv, os

def export_csvs(json_path, output_dir):
    print(f"Loading dataset from: {json_path}")
    ds = json.load(open(json_path))
    
    # 1. portfolios_v3.csv
    portfolios_path = os.path.join(output_dir, "portfolios_v3.csv")
    with open(portfolios_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["candidate_id", "name", "constituency", "party", "n_equity", "n_fund", "equity_value", "fund_value", "total_current_value", "base_value", "return_pct"])
        for p in ds["portfolios"]:
            w.writerow([
                p["candidate_id"],
                p["name"],
                p["constituency"],
                p["party"],
                p["n_equity"],
                p["n_fund"],
                p["eq_value"],
                p["fund_value"],
                p["cur_value"],
                p["base_value"],
                p["ret_pct"]
            ])
    print(f"Saved: {portfolios_path}")
            
    # 2. positions_v3.csv
    positions_path = os.path.join(output_dir, "positions_v3.csv")
    with open(positions_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["candidate_id", "mp_name", "party", "kind", "symbol_or_code", "security_name", "owner", "declared_value", "current_value", "return_pct"])
        for p in ds["portfolios"]:
            for pos in p["positions"]:
                w.writerow([
                    p["candidate_id"],
                    p["name"],
                    p["party"],
                    pos["kind"],
                    pos["symbol"],
                    pos["name"],
                    pos["owner"],
                    pos["declared_value"],
                    pos["cur_value"],
                    pos["ret_pct"]
                ])
    print(f"Saved: {positions_path}")

    # 3. preferred_stocks_v3.csv
    stocks_path = os.path.join(output_dir, "preferred_stocks_v3.csv")
    with open(stocks_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["symbol", "name", "n_mps", "agg_current_value", "stock_return_pct"])
        for s in ds["preferred_stocks"]:
            w.writerow([
                s["symbol"],
                s["name"],
                s["holders"],
                s["agg_cur_value"],
                s["ret_pct"]
            ])
    print(f"Saved: {stocks_path}")

    # 4. preferred_funds_v3.csv
    funds_path = os.path.join(output_dir, "preferred_funds_v3.csv")
    with open(funds_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["amfi_code", "scheme_name", "n_mps", "agg_current_value", "fund_return_pct"])
        for fund in ds["preferred_funds"]:
            w.writerow([
                fund["code"],
                fund["name"],
                fund["holders"],
                fund["agg_cur_value"],
                fund["ret_pct"]
            ])
    print(f"Saved: {funds_path}")

if __name__ == "__main__":
    # Export in v3_out
    export_csvs("neta_dataset_v3.json", ".")
    
    # Export in parent directory
    export_csvs("neta_dataset_v3.json", "..")
    
    # Copy neta_dataset_v3.json to parent directory
    import shutil
    shutil.copy("neta_dataset_v3.json", "../neta_dataset_v3.json")
    print("Copied neta_dataset_v3.json to parent directory")
