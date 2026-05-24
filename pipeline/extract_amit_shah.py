import json

ds = json.load(open("v3_out/neta_dataset_v3.json"))

# Find Amit Shah
as_portfolio = None
for p in ds["portfolios"]:
    if "amit shah" in p["name"].lower():
        as_portfolio = p
        break

if not as_portfolio:
    print("Amit Shah not found!")
    exit(1)

print(f"Name: {as_portfolio['name']}")
print(f"Party: {as_portfolio['party']}")
print(f"Constituency: {as_portfolio['constituency']}")
print(f"Base Value: Rs {as_portfolio['base_value']/1e7:.2f} Cr")
print(f"Current Value: Rs {as_portfolio['cur_value']/1e7:.2f} Cr")
print(f"Return: {as_portfolio['ret_pct']:+.2f}%")
print(f"Equity Positions Count: {as_portfolio['n_equity']}")
print(f"Fund Positions Count: {as_portfolio['n_fund']}")

# Format positions as a markdown table
positions = sorted(as_portfolio["positions"], key=lambda x: -x["cur_value"])
print("\n--- POSITION TABLE ---")
print("| Rank | Security Name | Ticker | Declared Value (INR) | Current Value (INR) | Return % | Owner |")
print("| :---: | :--- | :---: | :---: | :---: | :---: | :--- |")
for i, pos in enumerate(positions):
    dv_str = f"Rs {pos['declared_value']/1e5:.2f} L" if pos['declared_value'] >= 100000 else f"Rs {pos['declared_value']:,}"
    cv_str = f"Rs {pos['cur_value']/1e5:.2f} L" if pos['cur_value'] >= 100000 else f"Rs {pos['cur_value']:,}"
    print(f"| {i+1} | {pos['name']} | `{pos['symbol']}` | {dv_str} | {cv_str} | {pos['ret_pct']:+.1f}% | {pos['owner'].capitalize()} |")
