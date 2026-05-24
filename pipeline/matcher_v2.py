import json, re, csv
from rapidfuzz import process, fuzz

# ---------- EQUITY MASTER ----------
def norm_eq(s):
    s=s.lower(); s=re.sub(r"&"," and ",s)
    # CRITICAL FIX: DO NOT STRIP "india" and "indian"!
    s=re.sub(r"\b(ltd|limited|pvt|private|corp|corporation|company|companay|co|the|eq|units?|shares?|equity|new|fv|qty|rate|no)\b"," ",s)
    s=re.sub(r"[^a-z0-9 ]"," ",s)
    # Apply custom stemming for plurals and possessives
    words = s.split()
    stemmed = []
    for w in words:
        if w in ("hospitals", "enterprises", "consumers", "holdings", "investments"):
            stemmed.append(w[:-1])
        elif w == "raymonds":
            stemmed.append("raymond")
        else:
            stemmed.append(w)
    s = " ".join(stemmed)
    return re.sub(r"\s+"," ",s).strip()

EQ=[]
with open("EQUITY_L.csv") as f:
    for row in csv.DictReader(f):
        EQ.append((norm_eq(row["NAME OF COMPANY"]),row["SYMBOL"].strip(),row["NAME OF COMPANY"].strip()))
EQ_NAMES=[e[0] for e in EQ]; EQ_SYM2NAME={e[1]:e[2] for e in EQ}; EQ_VALID=set(EQ_SYM2NAME)

# Exact match dictionary
EQ_NORM_MAP = {e[0]: (e[1], e[2]) for e in EQ}

# ---------- FUND MASTER (collapse to scheme, prefer Regular-Growth) ----------
def norm_fund(s):
    s=s.lower()
    s=re.sub(r"\b(direct|regular|reg|plan|option|growth|idcw|dividend|payout|reinvestment|reinvest|fund|scheme|the)\b"," ",s)
    s=re.sub(r"[^a-z0-9 ]"," ",s); return re.sub(r"\s+"," ",s).strip()
schemes=json.load(open("amfi_schemes.json"))
def plan_rank(nm):  # prefer Regular Growth for canonical NAV
    n=nm.lower(); r=0
    if "regular" in n or ("direct" not in n): r+=2
    if "growth" in n: r+=2
    if "idcw" in n or "dividend" in n: r-=1
    return r
FUND=[]  # (norm_name, code, full_name, nav, amc)
seen={}
for s in schemes:
    nn=norm_fund(s["name"])
    if not nn: continue
    rank=plan_rank(s["name"])
    if nn not in seen or rank>seen[nn][0]:
        seen[nn]=(rank,s)
for nn,(rank,s) in seen.items():
    FUND.append((nn,s["code"],s["name"],s["nav"],s["amc"]))
FUND_NAMES=[f[0] for f in FUND]
# ISIN exact map
ISIN2FUND={}
for s in schemes:
    for k in (s["isin1"],s["isin2"]):
        if k and k.startswith("INF"): ISIN2FUND[k]=s
print(f"equity master: {len(EQ)} | fund master (collapsed): {len(FUND)} | ISINs: {len(ISIN2FUND)}")

EQ_ALIAS={"seimens":"siemens","alemic pharmaceuticals":"alembic pharmaceuticals","tcs":"tata consultancy services",
          "l and t":"larsen and toubro","m and m financial services":"mahindra and mahindra financial services"}
EQ_HARD={"tata motors":"TATAMOTORS","reliance power":"RPOWER","reliance communications":"RCOM",
         "reliance communication":"RCOM","reliance industries":"RELIANCE","reliance":"RELIANCE",
         "tata steel":"TATASTEEL","jio financial services":"JIOFIN","jio financial":"JIOFIN",
         "hdfc bank":"HDFCBANK","icici bank":"ICICIBANK","axis bank":"AXISBANK","state bank":"SBIN","sbi":"SBIN",
         "apollo hospital enterprises":"APOLLOHOSP","ndr invit trust":"NDRINVIT","meta platform":"META","fidelity ubs s and p 500 index":"IVV"}

# Define bank exact matches and block suffix matching for banks
BANK_EXACT_ONLY = {"sbi", "hdfc bank", "icici bank", "axis bank", "state bank"}

GENERIC_WORDS = {
    "market", "share", "shares", "investment", "investments", "security", "securities",
    "stock", "stocks", "company", "companies", "mutual", "fund", "funds", "other", "various",
    "nse", "bse", "equity"
}

GENERIC_INVESTMENT_KW = re.compile(
    r"\b(market\s+shares?|share\s+market|listed\s+shares?|equity\s+shares?|investment\s+in\s+shares?|other\s+shares?|quoted\s+shares?|unquoted\s+shares?|equity\s+investment|share\s+investments?|various\s+shares?|miscellaneous\s+shares?|investment\s+in\s+market)\b", 
    re.I
)

BANK_AC_KW = re.compile(
    r"\b(a/c|acct|account|savings|saving|fd|fixed\s+deposit|deposit|deposits|current\s+a/c|current\s+account|balance|cash|sb\s+a/c|sb\s+account|fdr|term\s+deposit|flexi\s+deposit|savings\s+bank|savings\s+a/c|cc\s+a/c|c/a|savings\s+account|fixed\s+deposits|recurring\s+deposit|rd|sweep|ppf|provident\s+fund|branch|sol\s+id)\b", 
    re.I
)
MF_INS_KW = re.compile(
    r"\b(mutual\s+fund|mutual\s+funds|mf|growth|dividend|idcw|prudence|magnum|hybrid|liquid|index\s+fund|gilt|elss|tax\s+saver|balanced\s+advantage|life\s+insurance|sbi\s+life|lic|policy|premium|pension|retirement|ulip|fund|funds|scheme|schemes|regular|direct|growth|nav|etf|bonds|bond|perpetual|gold\s+bond|sgb)\b", 
    re.I
)

FUND_KW=re.compile(r"\b(fund|flexi\s*cap|flexicap|fleci|multi\s*cap|small\s*cap|mid\s*cap|large\s*cap|bluechip|nifty|sensex|elss|tax saver|balanced advantage|hybrid|gilt|liquid|index|focused|value|consumption|infrastructure|pharma|banking|psu|momentum|nasdaq|gold etf|silver etf|nav|folio)\b",re.I)
UNLISTED_KW=re.compile(r"\b(pvt|private|sahakari|sahkari|sehkari|charitable|foundation|abhiyaan|samajik|cooperative|co-?op|co op|trust|nidhi|peoples|urban co|nagri|nagari|kendriya|jila|gramin|grameen|sugar factory|society)\b",re.I)
NOISE_KW=re.compile(r"\b(gold bond|sgb|kisan vikas|^nsc|ppf|postal saving|perpetual bond|infrastructure bond|liquid bees|gold bees)\b",re.I)

def match_equity(clean, raw):
    n=EQ_ALIAS.get(norm_eq(clean),norm_eq(clean))
    if not n or n in GENERIC_WORDS: return None
    
    # 1. Exact match in normalized master list first!
    if n in EQ_NORM_MAP:
        sym, full_name = EQ_NORM_MAP[n]
        return (sym, full_name, 100.0)
        
    # 2. Hardcoded override match
    for k,sym in EQ_HARD.items():
        if k in BANK_EXACT_ONLY:
            if n==k: return (sym,EQ_SYM2NAME.get(sym,sym),100.0)
        else:
            if n==k or n.startswith(k+" "): return (sym,EQ_SYM2NAME.get(sym,sym),100.0)
            
    # 3. Process extract with strict coverage check and intersection maximization
    matches = process.extract(n, EQ_NAMES, limit=5, scorer=fuzz.token_set_ratio)
    if matches:
        best_cand = None
        best_sym = None
        best_full = None
        max_intersection = -1
        best_score = -1
        best_sort_ratio = -1
        
        ta = set(n.split())
        for matched_name, score, index in matches:
            cand = EQ[index][0]
            sym = EQ[index][1]
            full_name = EQ[index][2]
            
            tb = set(cand.split())
            intersection = ta & tb
            tsr = len(intersection)/min(len(ta),len(tb)) if ta and tb else 0
            coverage = len(intersection)/len(ta) if ta else 0
            sort_ratio = fuzz.token_sort_ratio(n, cand)
            
            # Check if raw or clean has equity indicators
            has_eq_indicator = any(x in clean.lower() or x in raw.lower() for x in ["share", "shares", "equity", "eq"])
            
            # Strict thresholds:
            # - token_set_ratio score >= 92
            # - token subset ratio tsr >= 0.6
            # - coverage >= 0.6 OR has_eq_indicator and coverage >= 0.3
            is_valid = score >= 92 and tsr >= 0.6 and (coverage >= 0.6 or (has_eq_indicator and coverage >= 0.3))
            
            if is_valid:
                # We want to maximize the size of intersection, and break ties with token_sort_ratio then score
                if (len(intersection) > max_intersection) or \
                   (len(intersection) == max_intersection and sort_ratio > best_sort_ratio) or \
                   (len(intersection) == max_intersection and sort_ratio == best_sort_ratio and score > best_score):
                    max_intersection = len(intersection)
                    best_sort_ratio = sort_ratio
                    best_score = score
                    best_cand = cand
                    best_sym = sym
                    best_full = full_name
                    
        if best_sym:
            return (best_sym, best_full, round(best_score, 1))
            
    return None

def match_fund(clean, raw):
    # ISIN exact
    mi=re.search(r"\bINF[0-9A-Z]{9}\b",raw)
    if mi and mi.group(0) in ISIN2FUND:
        s=ISIN2FUND[mi.group(0)]; return (s["code"],s["name"],s["nav"],100.0)
    n=norm_fund(clean)
    if not n or n in GENERIC_WORDS or len(n.split()) <= 1: return None
    m=process.extractOne(n,FUND_NAMES,scorer=fuzz.token_set_ratio)
    if m:
        f=FUND[m[2]]; sc=m[1]
        ta=set(n.split()); tb=set(f[0].split())
        tsr=len(ta&tb)/min(len(ta),len(tb)) if ta and tb else 0
        if sc>=88 and tsr>=0.55: return (f[1],f[2],f[3],round(sc,1))
    return None

# Classify+match every holding
data=json.load(open("holdings_v2.json"))
from collections import Counter
cat_count=Counter()
for d in data:
    for h in d.get("holdings",[]):
        raw=h["raw_name"]; clean=h["clean_name"]
        h["eq_symbol"]=None; h["fund_code"]=None; h["fund_nav"]=None; h["category"]="unlisted_or_other"; h["match_name"]=None
        if clean=="__AGGREGATE__":
            h["category"]="aggregate_shares"; cat_count["aggregate"]+=1; continue
            
        # 1. Strict bank account check
        if BANK_AC_KW.search(raw) or BANK_AC_KW.search(clean):
            h["category"]="unlisted_or_other"; cat_count["unlisted"]+=1; continue
            
        # 1b. Generic stock market/shares holding check
        if GENERIC_INVESTMENT_KW.search(clean):
            h["category"]="unlisted_or_other"; cat_count["unlisted"]+=1; continue
            
        if NOISE_KW.search(raw): h["category"]="other_security"; cat_count["other"]+=1; continue
        
        # 2. Fund/insurance check
        is_fundish=bool(FUND_KW.search(raw)) and not re.search(r"\bbank ltd\b|\bbank limited\b",raw,re.I)
        is_mf_ins = bool(MF_INS_KW.search(raw)) or bool(MF_INS_KW.search(clean))
        
        if is_fundish or is_mf_ins:
            fm=match_fund(clean,raw)
            if fm: 
                h.update({"fund_code":fm[0],"match_name":fm[1],"fund_nav":fm[2],"category":"mutual_fund","match_score":fm[3]})
                cat_count["fund"]+=1
                continue
            else:
                # Block fallback to equity for obvious funds/insurance/bonds unless they have equity keywords
                if not re.search(r"\b(shares?|eq|equity|dvr)\b", raw, re.I):
                    h["category"]="unlisted_or_other"
                    cat_count["unlisted"]+=1
                    continue
                    
        if UNLISTED_KW.search(raw): h["category"]="unlisted_or_other"; cat_count["unlisted"]+=1; continue
        
        # 3. Equity matching
        em=match_equity(clean, raw)
        if em: 
            h.update({"eq_symbol":em[0],"match_name":em[1],"category":"listed_equity","match_score":em[2]})
            cat_count["equity"]+=1
            continue
            
        # 4. Fallback: try fund even if not flagged
        fm=match_fund(clean,raw)
        if fm: 
            h.update({"fund_code":fm[0],"match_name":fm[1],"fund_nav":fm[2],"category":"mutual_fund","match_score":fm[3]})
            cat_count["fund"]+=1
            continue
            
        cat_count["unmatched"]+=1
        
json.dump(data,open("holdings_matched.json","w"))
print("\nClassification result:")
for k,v in cat_count.most_common(): print(f"  {k:12s} {v}")
