import json

ds = json.load(open("v3_out/neta_dataset_v3.json"))
all_pos = []
for p in ds["portfolios"]:
    for pos in p["positions"]:
        all_pos.append((p["name"], p["party"], pos))

global_words = ["global", "world", "overseas", "us equity", "nasdaq", "s&p 500", "nyse", "meta", "alphabet", "google", "apple", "microsoft", "amazon", "nvidia", "jpm", "dbs", "sgx", "singapore", "schwab", "fidelity", "etf"]
found = []
for name, party, pos in all_pos:
    p_name = pos["name"].lower()
    p_sym = pos["symbol"].lower()
    if any(w in p_name or w in p_sym for w in global_words):
        found.append((name, party, pos))

print(f"Found {len(found)} candidate global/overseas holdings:")
for f in sorted(found, key=lambda x: -x[2]["cur_value"]):
    print(f"MP: {f[0]} ({f[1]}) | Symbol: {f[2]['symbol']} | Name: {f[2]['name']} | Kind: {f[2]['kind']} | Declared: Rs {f[2]['declared_value']/1e5:.2f} L | Current: Rs {f[2]['cur_value']/1e5:.2f} L | Return: {f[2]['ret_pct']}%")
