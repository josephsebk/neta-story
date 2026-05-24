import json

ds = json.load(open("neta_dataset_v3.json"))

for p in ds["portfolios"]:
    if p["name"] in ("KONDA VISHWESHWAR REDDY", "BAIJAYANT PANDA", "NAVEEN JINDAL"):
        print(f"\nPortfolio of {p['name']}:")
        for pos in p["positions"]:
            print(f"  {pos['kind']} | {pos['symbol']} | {pos['name']} | Owner: {pos['owner']} | Declared: {pos['declared_value']} | Current: {pos['cur_value']} | Ret: {pos['ret_pct']}%")
