import json, re

data = json.load(open("holdings_matched.json"))

bank_queries = ["sbi", "hdfc", "sabin", "state bank", "union bank", "bank of india", "indian bank", "south indian"]

print("Analyzing Bank Holdings and their Classifications:\n")
for d in data:
    for h in d.get("holdings", []):
        raw = h["raw_name"]
        clean = h["clean_name"]
        cat = h["category"]
        eq = h["eq_symbol"]
        fn = h["fund_code"]
        mn = h["match_name"]
        
        raw_l = raw.lower()
        if any(q in raw_l for q in bank_queries):
            # Print bank matching information
            if cat == "listed_equity":
                print(f"[EQUITY MATCH] MP: {d['name']} | Raw: {raw} | Clean: {clean} -> Category: {cat} (Symbol: {eq}, Match: {mn})")
            elif cat == "mutual_fund":
                print(f"[FUND MATCH] MP: {d['name']} | Raw: {raw} | Clean: {clean} -> Category: {cat} (Code: {fn}, Match: {mn})")
            else:
                # Only print a subset of unlisted to not overwhelm the output, or count them
                pass

print("\nCounting Bank terms in unlisted/other category:")
counts = {}
for d in data:
    for h in d.get("holdings", []):
        raw = h["raw_name"]
        cat = h["category"]
        if cat == "unlisted_or_other":
            raw_l = raw.lower()
            for q in bank_queries:
                if q in raw_l:
                    counts[q] = counts.get(q, 0) + 1

for q, count in counts.items():
    print(f"  Query '{q}': {count} entries correctly routed to unlisted_or_other (bank accounts/FDs/etc.)")
