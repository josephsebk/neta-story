import json, csv, yfinance as yf, time
import urllib.request

data=json.load(open("holdings_matched.json"))
prices=json.load(open("prices.json")); B=prices["baseline"]; C=prices["current"]

# Need baseline+current for any NEW equity symbols not in prices.json
have=set(B)
need=set()
for d in data:
    for h in d.get("holdings",[]):
        if h["category"]=="listed_equity" and h["eq_symbol"] and h["eq_symbol"] not in have:
            need.add(h["eq_symbol"])
print("new equity symbols to price:",len(need))
if need:
    tk=[s if s in ("META", "IVV") else s+".NS" for s in need]
    hist=yf.download(tk,start="2024-05-28",end="2024-06-12",progress=False)["Close"]
    cur=yf.download(tk,period="5d",progress=False)["Close"]
    def fv(x):
        try:
            s=x.dropna(); return float(s.iloc[0]) if len(s) else None
        except: return None
    def lv(x):
        try:
            s=x.dropna(); return float(s.iloc[-1]) if len(s) else None
        except: return None
    for s in need:
        col=s if s in ("META", "IVV") else s+".NS"
        try: B[s]=fv(hist[col]) if hasattr(hist,'columns') and col in hist.columns else fv(hist)
        except: B[s]=None
        try: C[s]=lv(cur[col]) if hasattr(cur,'columns') and col in cur.columns else lv(cur)
        except: C[s]=None
    json.dump({"baseline":B,"current":C},open("prices.json","w"))

# tata motors
try:
    tm=yf.Ticker("TATAMOTORS.NS"); h=tm.history(start="2024-05-28",end="2024-06-12")["Close"]; c=tm.history(period="5d")["Close"]
    if len(h): B["TATAMOTORS"]=float(h.iloc[0])
    if len(c): C["TATAMOTORS"]=float(c.iloc[-1])
except: pass

EQ_SYM2NAME={}
with open("EQUITY_L.csv") as f:
    for row in csv.DictReader(f): EQ_SYM2NAME[row["SYMBOL"].strip()]=row["NAME OF COMPANY"].strip()
EQ_SYM2NAME["TATAMOTORS"]="Tata Motors Limited"
EQ_SYM2NAME["APOLLOHOSP"]="Apollo Hospitals Enterprise Limited"
EQ_SYM2NAME["NDRINVIT"]="NDR InvIT Trust"
EQ_SYM2NAME["META"]="Meta Platforms, Inc."
EQ_SYM2NAME["IVV"]="iShares Core S&P 500 ETF"

# ---- Fund NAV history: fetch baseline NAV (~Jun 2024) from MFAPI for matched fund codes ----
fund_codes=sorted({h["fund_code"] for d in data for h in d.get("holdings",[]) if h["category"]=="mutual_fund" and h["fund_code"]})
print("unique fund schemes to price:",len(fund_codes))
fund_base={}; fund_cur={}
def get_nav_hist(code):
    try:
        with urllib.request.urlopen(f"https://api.mfapi.in/mf/{code}",timeout=20) as r:
            j=json.load(r)
        data_pts=j.get("data",[])
        if not data_pts: return None,None
        cur=float(data_pts[0]["nav"])
        # baseline ~ 2024-06-04: find nearest date in June 2024
        base=None
        for p in data_pts:
            dd=p["date"]  # dd-mm-yyyy
            if dd.endswith("2024") and dd.split("-")[1]=="06":
                base=float(p["nav"])
        return base,cur
    except: return None,None

from concurrent.futures import ThreadPoolExecutor, as_completed
with ThreadPoolExecutor(max_workers=10) as ex:
    futs={ex.submit(get_nav_hist,c):c for c in fund_codes}
    for f in as_completed(futs):
        c=futs[f]; b,cu=f.result(); fund_base[c]=b; fund_cur[c]=cu
priced_funds=sum(1 for c in fund_codes if fund_base.get(c) and fund_cur.get(c))
print(f"funds priced (baseline+current NAV): {priced_funds}/{len(fund_codes)}")
json.dump({"base":fund_base,"cur":fund_cur},open("fund_navs.json","w"))

def eq_ok(s): return B.get(s) and C.get(s)

# ---- Build portfolios with BOTH equity and fund positions ----
portfolios=[]
agg_eq_b=agg_eq_c=agg_fd_b=agg_fd_c=0.0
stock_hold={}; stock_val={}; fund_hold={}; fund_val={}
for d in data:
    if d.get("error"): continue
    pos=[]; eqb=eqc=fdb=fdc=0.0; seen_eq=set(); seen_fd=set()
    for h in d.get("holdings",[]):
        dv=h["declared_value"] or 0
        if dv<=0: continue
        if h["category"]=="listed_equity" and h["eq_symbol"] and eq_ok(h["eq_symbol"]):
            s=h["eq_symbol"]
            if s == "EASTSILK":
                # NCLT approved resolution plan on 2024-01-31 which extinguished entire existing equity share capital with NIL payout.
                # Trading was suspended in November 2024. Therefore, the old shares are worth Rs 0 (100% loss).
                r = -1.0
                cv = 0.0
            elif s == "RAYMOND":
                # Raymond underwent a lifestyle demerger (4:5) in 2024 and realty demerger (1:1) in 2025.
                # Accounting for both spin-offs, the actual adjusted demerged return is -22.8% (instead of -74.6% paper drop).
                r = -0.228
                cv = dv * (1 + r)
            else:
                r=(C[s]-B[s])/B[s]
                cv=dv*(1+r)
            eqb+=dv; eqc+=cv; seen_eq.add(s)
            stock_val[s]=stock_val.get(s,0)+cv
            pos.append({"kind":"equity","symbol":s,"name":EQ_SYM2NAME.get(s,s),"owner":h["owner"],
                        "declared_value":round(dv),"cur_value":round(cv),"ret_pct":round(100*r,1)})
        elif h["category"]=="mutual_fund" and h["fund_code"]:
            fc=h["fund_code"]
            if fund_base.get(fc) and fund_cur.get(fc):
                r=(fund_cur[fc]-fund_base[fc])/fund_base[fc]; cv=dv*(1+r)
                fdb+=dv; fdc+=cv; seen_fd.add(fc); fund_val[fc]=fund_val.get(fc,0)+cv
                pos.append({"kind":"fund","symbol":fc,"name":h["match_name"],"owner":h["owner"],
                            "declared_value":round(dv),"cur_value":round(cv),"ret_pct":round(100*r,1)})
    for s in seen_eq: stock_hold[s]=stock_hold.get(s,0)+1
    for fc in seen_fd: fund_hold[fc]=fund_hold.get(fc,0)+1
    tb=eqb+fdb; tc=eqc+fdc
    if tb>0:
        portfolios.append({"candidate_id":d["candidate_id"],"name":d["name"],
            "constituency":d.get("constituency",""),"party":d.get("party",""),
            "eq_value":round(eqc),"fund_value":round(fdc),"cur_value":round(tc),"base_value":round(tb),
            "ret_pct":round(100*(tc-tb)/tb,1),"n_equity":len(seen_eq),"n_fund":len(seen_fd),
            "positions":sorted(pos,key=lambda x:-x["cur_value"])})
        agg_eq_b+=eqb; agg_eq_c+=eqc; agg_fd_b+=fdb; agg_fd_c+=fdc

portfolios.sort(key=lambda x:-x["cur_value"])
C["^NSEI"] = 23719.30
nifty=100*(C["^NSEI"]-B["^NSEI"])/B["^NSEI"]
eq_idx=100*(agg_eq_c-agg_eq_b)/agg_eq_b if agg_eq_b else 0
fd_idx=100*(agg_fd_c-agg_fd_b)/agg_fd_b if agg_fd_b else 0
comb_b=agg_eq_b+agg_fd_b; comb_c=agg_eq_c+agg_fd_c
comb_idx=100*(comb_c-comb_b)/comb_b

pref_stocks=[]
for s in sorted(stock_hold,key=lambda x:-stock_hold[x]):
    ret = round(100*(C[s]-B[s])/B[s],1)
    if s == "EASTSILK":
        ret = -100.0
    elif s == "RAYMOND":
        ret = -22.8
    pref_stocks.append({
        "symbol":s,
        "name":EQ_SYM2NAME.get(s,s),
        "holders":stock_hold[s],
        "agg_cur_value":round(stock_val.get(s,0)),
        "ret_pct":ret
    })
fnav=json.load(open("fund_navs.json"))
# fund display names
FC2NAME={}
for d in data:
    for h in d.get("holdings",[]):
        if h["category"]=="mutual_fund" and h["fund_code"]: FC2NAME[h["fund_code"]]=h["match_name"]
pref_funds=[{"code":fc,"name":FC2NAME.get(fc,fc),"holders":fund_hold[fc],"agg_cur_value":round(fund_val.get(fc,0)),
             "ret_pct":round(100*(fnav["cur"][fc]-fnav["base"][fc])/fnav["base"][fc],1) if fnav["base"].get(fc) and fnav["cur"].get(fc) else None}
            for fc in sorted(fund_hold,key=lambda x:-fund_hold[x])]

out={"meta":{"baseline_date":"2024-06-04","n_portfolios":len(portfolios),
     "nifty_ret_pct":round(nifty,2),
     "equity_index_ret_pct":round(eq_idx,2),"equity_base":round(agg_eq_b),"equity_cur":round(agg_eq_c),
     "fund_index_ret_pct":round(fd_idx,2),"fund_base":round(agg_fd_b),"fund_cur":round(agg_fd_c),
     "combined_index_ret_pct":round(comb_idx,2),"combined_base":round(comb_b),"combined_cur":round(comb_c),
     "n_equity_holders":len(set(s for d in data for h in d.get("holdings",[]) if h["category"]=="listed_equity")),
     },
     "portfolios":portfolios,"preferred_stocks":pref_stocks,"preferred_funds":pref_funds}
json.dump(out,open("neta_dataset_v3.json","w"))

print(f"\n{'='*54}")
print(f"portfolios: {len(portfolios)}")
print(f"EQUITY index : Rs {agg_eq_b/1e7:>6.0f}cr -> {agg_eq_c/1e7:>6.0f}cr  {eq_idx:+.2f}%")
print(f"FUND index   : Rs {agg_fd_b/1e7:>6.0f}cr -> {agg_fd_c/1e7:>6.0f}cr  {fd_idx:+.2f}%")
print(f"COMBINED     : Rs {comb_b/1e7:>6.0f}cr -> {comb_c/1e7:>6.0f}cr  {comb_idx:+.2f}%")
print(f"NIFTY 50     : {nifty:+.2f}%")
print(f"{'='*54}")
print("\nTop 10 portfolios (equity+funds):")
for p in portfolios[:10]:
    print(f"  {p['name'][:26]:26s} {p['party'][:14]:14s} Rs{p['cur_value']/1e7:>6.1f}cr {p['ret_pct']:+6.1f}% (E{p['n_equity']}/F{p['n_fund']})")
