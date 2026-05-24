import json, numpy as np
ds=json.load(open("neta_dataset_v3.json"))
P=ds["portfolios"]
nifty=ds["meta"]["nifty_ret_pct"]

# 1. Value-weighted (current) - dominated by whales
vw=ds["meta"]["combined_index_ret_pct"]

# 2. Equal-weighted: simple mean of portfolio returns (each MP = 1 vote)
ew=np.mean([p["ret_pct"] for p in P])
ew_med=np.median([p["ret_pct"] for p in P])

# 3. Capped value-weighted: cap each portfolio's weight at 5% of total
total=sum(p["cur_value"] for p in P)
cap=0.05*total
capped_b=0; capped_c=0
for p in P:
    w=min(p["cur_value"],cap)
    # approximate base via ret
    b=w/(1+p["ret_pct"]/100)
    capped_b+=b; capped_c+=w
cap_ret=100*(capped_c-capped_b)/capped_b

# 4. Value-weighted EXCLUDING the top 3 whales
whales=set(p["candidate_id"] for p in sorted(P,key=lambda x:-x["cur_value"])[:3])
nb=sum(p["cur_value"]/(1+p["ret_pct"]/100) for p in P if p["candidate_id"] not in whales)
nc=sum(p["cur_value"] for p in P if p["candidate_id"] not in whales)
exwhale=100*(nc-nb)/nb

print(f"INDEX VARIANTS (n={len(P)} MPs)  vs Nifty {nifty:+.2f}%\n")
print(f"  Value-weighted (raw)        : {vw:+.2f}%   <- dominated by Jindal/Panda")
print(f"  Value-weighted ex-top3      : {exwhale:+.2f}%")
print(f"  Value-weighted capped @5%   : {cap_ret:+.2f}%")
print(f"  Equal-weighted (mean MP)    : {ew:+.2f}%")
print(f"  Median MP return            : {ew_med:+.2f}%")
print(f"\n  Top 3 by value: {[p['name'] for p in sorted(P,key=lambda x:-x['cur_value'])[:3]]}")
print(f"  Their share of total pool: {100*sum(p['cur_value'] for p in P if p['candidate_id'] in whales)/total:.1f}%")
