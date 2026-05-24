import re, json, os
from bs4 import BeautifulSoup

def clean_num(s):
    s=s.replace(",","").strip()
    try: return float(s) if "." in s else int(s)
    except: return None

# Extract qty embedded in a name and return (clean_name, qty)
QTY_PATTERNS=[
    r",?\s*([\d,]+)\s*shares?\b",            # "..., 900 Shares"
    r"\beq\.?\s*shares?\s*[-:]?\s*([\d,]+)", # "Eq. Share-28"
    r"\bunits?\s*[-:]?\s*([\d,]+)",          # "Unit-296" / "Units-1515"
    r"\bshares?\s*[-:]?\s*([\d,]+)",         # "Share-48"
    r"\bq\.?\s*([\d,]+)\b",                  # "Q. 200"
]
def extract_qty(name):
    qty=None; cleaned=name
    for pat in QTY_PATTERNS:
        m=re.search(pat,cleaned,re.I)
        if m:
            q=clean_num(m.group(1))
            if q and q<1e9:  # sane share count
                qty=q; cleaned=cleaned[:m.start()]+cleaned[m.end():]
                break
    return cleaned, qty

# Clean noise from names: folio numbers, demat acct, A/C numbers
def clean_name(name):
    n=name
    n=re.sub(r"folio\s*(no\.?|number)?\s*[:\-]?\s*[\dxX/]+","",n,flags=re.I)
    n=re.sub(r"demat.*?(in\d[\dxX]+|a/?c.*)","",n,flags=re.I)
    n=re.sub(r"a/?c\.?\s*no\.?\s*[:\-]?\s*[\dxX/]+","",n,flags=re.I)
    n=re.sub(r"\bin[3e]\d{6,}\b","",n,flags=re.I)  # NSDL/ISIN-ish
    n=re.sub(r"\b\d{6,}\b","",n)                   # long bare numbers
    n=re.sub(r"[,;:\-]+\s*$","",n)
    n=re.sub(r"\s+"," ",n).strip(" ,.;:-")
    return n

def parse_cell(cell):
    """Robust: each <span class=desc> = a holding; value is the text after following <br/>.
       Handles decimals, embedded qty, free-text names."""
    out=[]; contents=list(cell.children)
    idxs=[i for i,n in enumerate(contents) if getattr(n,"name",None)=="span" and "desc" in (n.get("class") or [])]
    for k,idx in enumerate(idxs):
        raw_name=contents[idx].get_text(" ",strip=True)
        # value = first numeric text node after this desc, before next desc
        stop = idxs[k+1] if k+1<len(idxs) else len(contents)
        val=None
        for j in range(idx+1,stop):
            node=contents[j]
            if getattr(node,"name",None) is None:
                t=str(node).strip()
                if t and re.match(r"^[\d,]+(\.\d+)?$",t):
                    val=clean_num(t); break
        name_noqty, qty = extract_qty(raw_name)
        cname = clean_name(name_noqty)
        if not cname and qty is None and val is None: continue
        out.append({"raw_name":raw_name,"clean_name":cname or raw_name,"qty":qty,
                    "declared_value":int(val) if val else None})
    # Also catch aggregate-only cells (no desc spans but a bare value)
    if not idxs:
        txt=cell.get_text(" ",strip=True)
        m=re.match(r"^([\d,]+)\b",txt)
        if m and clean_num(m.group(1)):
            out.append({"raw_name":"(unspecified shares - aggregate)","clean_name":"__AGGREGATE__",
                        "qty":None,"declared_value":clean_num(m.group(1))})
    return out

def parse_candidate(cid):
    soup=BeautifulSoup(open(f"html/{cid}.html").read(),"lxml")
    h2=soup.find("h2"); name=h2.get_text(strip=True).replace("(Winner)","").strip() if h2 else f"cand_{cid}"
    holdings=[]
    for tr in soup.find_all("tr"):
        if "Bonds, Debentures and Shares" in tr.get_text(" ",strip=True):
            tds=tr.find_all("td")
            for col,owner in [(2,"self"),(3,"spouse"),(4,"huf"),(5,"dep1"),(6,"dep2"),(7,"dep3")]:
                if col<len(tds):
                    for h in parse_cell(tds[col]):
                        h["owner"]=owner; holdings.append(h)
            break
    return {"candidate_id":cid,"name":name,"holdings":holdings}

ids=json.load(open("winner_ids.json"))
meta=json.load(open("cand_meta.json"))
out=[]
for cid in ids:
    try:
        r=parse_candidate(cid)
        if str(cid) in meta: r.update(meta[str(cid)])
        out.append(r)
    except Exception as e:
        out.append({"candidate_id":cid,"error":str(e),"holdings":[]})
json.dump(out,open("holdings_v2.json","w"))

# Compare to old parse
total=sum(len(x.get("holdings",[])) for x in out)
no_val=sum(1 for x in out for h in x.get("holdings",[]) if not h["declared_value"])
with_qty=sum(1 for x in out for h in x.get("holdings",[]) if h["qty"])
nonempty=sum(1 for x in out if x.get("holdings"))
print(f"v2 parse: {total} lines (was 3850) | MPs with holdings: {nonempty} (was 287)")
print(f"  missing value: {no_val} ({100*no_val/total:.0f}%, was 9%)")
print(f"  with quantity: {with_qty} ({100*with_qty/total:.0f}%, was 28%)")
