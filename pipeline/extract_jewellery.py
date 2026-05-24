"""
extract_jewellery.py
Parses the "Jewellery" row (sec vii) from each candidate's myneta affidavit HTML,
extracting per-owner (self / spouse / huf / dep1-3) entries of gold, silver,
diamond, and gemstones, with weight (grams) where extractable.

Outputs:
    gold_positions_v3.csv  - one row per (candidate, owner, jewellery_entry)
    gold_summary_v3.csv    - per-candidate aggregates by category

Usage (run from project root):
    python3 v3_out/extract_jewellery.py
"""
import os, re, csv, json, glob
from bs4 import BeautifulSoup

HTML_DIR = "_html_extracted/html"
META_CANDIDATES = "v3_out/holdings_v2.json"  # has cid -> name/party/constituency
OUT_POSITIONS = "gold_positions_v3.csv"
OUT_SUMMARY = "gold_summary_v3.csv"

# ---------- numeric helpers ----------
def clean_num(s):
    """Parse Indian-format number string ('60,00,000') to int."""
    s = s.replace(",", "").strip()
    try:
        return int(round(float(s))) if s else None
    except Exception:
        return None

# ---------- weight extraction ----------
# Patterns: "862 Gram", "770gm", "1620gm", "489 Gram", "1.5 Kilo", "25Kg", "18KGS",
# "44.450gms", "8529.88gms", "2 kg", "kg-3"
GRAM_PATS = [
    r"(\d+(?:\.\d+)?)\s*(?:grams?|gms?|gm|gr|gram)\b",
]
KG_PATS = [
    r"(\d+(?:\.\d+)?)\s*(?:kilos?|kgs?|kg)\b",
]
CARAT_PATS = [
    r"(\d+(?:\.\d+)?)\s*(?:cts?|carats?|carate)\b",  # carats (used for diamonds/gemstones)
]

def extract_weight_grams(text):
    """Return total grams found in text (None if nothing)."""
    t = text.lower()
    grams = 0.0
    matched = False
    for pat in GRAM_PATS:
        for m in re.finditer(pat, t):
            grams += float(m.group(1))
            matched = True
    for pat in KG_PATS:
        for m in re.finditer(pat, t):
            grams += float(m.group(1)) * 1000
            matched = True
    return round(grams, 3) if matched else None

def extract_carats(text):
    t = text.lower()
    carats = 0.0
    matched = False
    for pat in CARAT_PATS:
        for m in re.finditer(pat, t):
            carats += float(m.group(1))
            matched = True
    return round(carats, 3) if matched else None

# ---------- classification ----------
# Returns one of: gold, silver, diamond, gemstone, mixed, unspecified
GEMSTONE_KW = ["panna", "ruby", "emerald", "sapphire", "pearl", "moti", "gem", "stone", "navratan", "neelam", "pukhraj", "manik"]
def classify(text):
    t = text.lower()
    has_gold = bool(re.search(r"\bgold\b|\bjwellery\b|\bjewelry\b|\bjewellery\b|\bornament", t))
    has_silver = bool(re.search(r"\bsilver\b", t))
    has_diamond = bool(re.search(r"\bdiamond\b|\bdiamonds\b|\bsolitaire", t))
    has_gemstone = any(g in t for g in GEMSTONE_KW)
    flags = [has_gold, has_silver, has_diamond, has_gemstone]
    if sum(flags) > 1:
        return "mixed"
    if has_gold: return "gold"
    if has_silver: return "silver"
    if has_diamond: return "diamond"
    if has_gemstone: return "gemstone"
    # Fallback: if text mentions weight in grams but no metal, assume gold (most common)
    if extract_weight_grams(text):
        return "gold"
    return "unspecified"

# ---------- cell parsing ----------
def parse_cell(cell):
    """
    A jewellery cell has structure like:
      <span class="desc">Description1</span><br/> 60,00,000 <br/> 60 Lacs+
      <span class="desc">Description2</span><br/> 10,40,55,576 ...
    """
    out = []
    contents = list(cell.children)
    desc_idxs = [i for i, n in enumerate(contents)
                 if getattr(n, "name", None) == "span" and "desc" in (n.get("class") or [])]

    if desc_idxs:
        for k, idx in enumerate(desc_idxs):
            raw_name = contents[idx].get_text(" ", strip=True)
            stop = desc_idxs[k+1] if k+1 < len(desc_idxs) else len(contents)
            val = None
            for j in range(idx+1, stop):
                node = contents[j]
                if getattr(node, "name", None) is None:
                    t = str(node).strip()
                    if t and re.match(r"^[\d,]+(\.\d+)?$", t):
                        val = clean_num(t)
                        break
            if not raw_name and val is None:
                continue
            out.append({"raw_name": raw_name, "declared_value": val})
        return out

    # Fallback: cell with no <span class="desc"> - try to extract a single name+value
    txt = cell.get_text(" || ", strip=True)
    if not txt or txt.lower().strip() in ("nil", "0", "-", ""):
        return []
    # Try to find a value (Indian-format number, no decimal usually)
    m = re.search(r"([\d,]{4,})", txt)
    if m and clean_num(m.group(1)):
        v = clean_num(m.group(1))
        # description = everything before the number
        desc = txt[:m.start()].strip(" ||,;:-")
        if desc:
            out.append({"raw_name": desc, "declared_value": v})
    return out


# ---------- main extractor ----------
def main():
    # Load candidate metadata
    meta = {}
    with open(META_CANDIDATES) as f:
        for c in json.load(f):
            meta[str(c["candidate_id"])] = {
                "name": c.get("name"),
                "party": c.get("party", ""),
                "constituency": c.get("constituency", ""),
            }

    positions = []
    summary = {}  # cid -> { category -> {n, value, weight_g} }
    no_jewellery_section = []
    parse_errors = []

    files = sorted(glob.glob(f"{HTML_DIR}/*.html"))
    print(f"Parsing {len(files)} HTML files...")

    for fp in files:
        cid = os.path.splitext(os.path.basename(fp))[0]
        m = meta.get(cid, {"name": f"cand_{cid}", "party": "", "constituency": ""})
        try:
            soup = BeautifulSoup(open(fp, encoding="utf-8", errors="ignore").read(), "lxml")
        except Exception as e:
            parse_errors.append((cid, str(e)))
            continue

        jewellery_row = None
        for tr in soup.find_all("tr"):
            text = tr.get_text(" ", strip=True)
            if "Jewellery" in text and "give details" in text:
                jewellery_row = tr
                break
        if not jewellery_row:
            no_jewellery_section.append(cid)
            continue

        tds = jewellery_row.find_all("td")
        # TD layout: 0=sr.no, 1=desc, 2=self, 3=spouse, 4=huf, 5=dep1, 6=dep2, 7=dep3, 8=total
        for col, owner in [(2, "self"), (3, "spouse"), (4, "huf"),
                           (5, "dep1"), (6, "dep2"), (7, "dep3")]:
            if col >= len(tds):
                continue
            entries = parse_cell(tds[col])
            for e in entries:
                raw = e["raw_name"]
                val = e["declared_value"]
                if val is None and not raw:
                    continue
                cat = classify(raw)
                wgrams = extract_weight_grams(raw)
                carats = extract_carats(raw)
                
                # Back-calculate weights if value is present but weight text is missing
                is_estimated = False
                if wgrams is None and val is not None:
                    if cat == "gold":
                        wgrams = round(val / 7293.0, 3)
                        is_estimated = True
                    elif cat == "silver":
                        wgrams = round(val / 96.50, 3)
                        is_estimated = True
                
                positions.append({
                    "candidate_id": cid,
                    "mp_name": m["name"],
                    "party": m["party"],
                    "constituency": m["constituency"],
                    "owner": owner,
                    "category": cat,
                    "raw_description": raw,
                    "declared_value_inr": val if val is not None else "",
                    "weight_grams": wgrams if wgrams is not None else "",
                    "carats": carats if carats is not None else "",
                    "weight_estimated": "True" if is_estimated else "False",
                })
                # summary aggregation
                if cid not in summary:
                    summary[cid] = {"name": m["name"], "party": m["party"],
                                    "constituency": m["constituency"],
                                    "by_cat": {}}
                bc = summary[cid]["by_cat"].setdefault(cat, {"n": 0, "value": 0, "weight_g": 0.0})
                bc["n"] += 1
                if val: bc["value"] += val
                if wgrams: bc["weight_g"] += wgrams

    # Write positions CSV
    with open(OUT_POSITIONS, "w", newline="") as f:
        cols = ["candidate_id", "mp_name", "party", "constituency", "owner",
                "category", "raw_description", "declared_value_inr",
                "weight_grams", "carats", "weight_estimated"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(positions)

    # Write summary CSV (one row per candidate)
    cats_order = ["gold", "silver", "diamond", "gemstone", "mixed", "unspecified"]
    sum_rows = []
    for cid, info in summary.items():
        row = {
            "candidate_id": cid,
            "mp_name": info["name"],
            "party": info["party"],
            "constituency": info["constituency"],
            "total_declared_value_inr": 0,
            "total_declared_value_cr": 0.0,
        }
        for c in cats_order:
            bc = info["by_cat"].get(c, {"n": 0, "value": 0, "weight_g": 0.0})
            row[f"{c}_n_entries"] = bc["n"]
            row[f"{c}_value_inr"] = bc["value"]
            row[f"{c}_weight_g"] = round(bc["weight_g"], 3) if bc["weight_g"] else 0
            row["total_declared_value_inr"] += bc["value"]
        row["total_declared_value_cr"] = round(row["total_declared_value_inr"] / 1e7, 4)
        sum_rows.append(row)

    sum_rows.sort(key=lambda r: -r["total_declared_value_inr"])
    with open(OUT_SUMMARY, "w", newline="") as f:
        cols = ["candidate_id", "mp_name", "party", "constituency",
                "total_declared_value_inr", "total_declared_value_cr"]
        for c in cats_order:
            cols += [f"{c}_n_entries", f"{c}_value_inr", f"{c}_weight_g"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(sum_rows)

    # ---------- console summary ----------
    print(f"\nParsed {len(positions)} jewellery entries across {len(summary)} candidates")
    print(f"Candidates with no jewellery section: {len(no_jewellery_section)}")
    print(f"HTML parse errors: {len(parse_errors)}")

    total_value = sum(r["total_declared_value_inr"] for r in sum_rows)
    print(f"\nTotal declared jewellery value across all MPs: Rs {total_value/1e7:,.2f} Cr")
    print("\nBy category (all candidates pooled):")
    cat_totals = {}
    cat_weights = {}
    cat_n = {}
    for p in positions:
        c = p["category"]
        cat_n[c] = cat_n.get(c, 0) + 1
        v = p["declared_value_inr"] or 0
        cat_totals[c] = cat_totals.get(c, 0) + (v if isinstance(v, int) else 0)
        wg = p["weight_grams"] or 0
        cat_weights[c] = cat_weights.get(c, 0) + (wg if isinstance(wg, (int, float)) else 0)
    for c in cats_order:
        n = cat_n.get(c, 0); v = cat_totals.get(c, 0); wg = cat_weights.get(c, 0)
        print(f"  {c:<12} | {n:>5} entries | Rs {v/1e7:>10,.2f} Cr | {wg:>10,.0f} grams")

    print("\nTop 15 candidates by total declared jewellery value:")
    for r in sum_rows[:15]:
        print(f"  {r['mp_name']:<40} ({r['party'][:20]:<20}) | Rs {r['total_declared_value_cr']:>10,.2f} Cr | gold {r.get('gold_weight_g',0):>7,.0f} g | silver {r.get('silver_weight_g',0):>7,.0f} g")

if __name__ == "__main__":
    main()
