import csv
import os

POSITIONS_CSV = "gold_positions_v3.csv"
SUMMARY_CSV = "gold_summary_v3.csv"

def verify():
    if not os.path.exists(POSITIONS_CSV) or not os.path.exists(SUMMARY_CSV):
        print("Gold CSV files not found!")
        return

    # Load positions
    positions = []
    with open(POSITIONS_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            positions.append(row)

    # Load summaries
    summaries = {}
    with open(SUMMARY_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            summaries[row["candidate_id"]] = row

    print(f"Loaded {len(positions)} individual positions in {POSITIONS_CSV}")
    print(f"Loaded {len(summaries)} candidate summaries in {SUMMARY_CSV}")

    # Check: Sum of positions per candidate matches summary
    mismatches = []
    cand_sums = {}
    for p in positions:
        cid = p["candidate_id"]
        val = int(p["declared_value_inr"]) if p["declared_value_inr"] else 0
        cat = p["category"]
        
        if cid not in cand_sums:
            cand_sums[cid] = {
                "total": 0,
                "gold": 0, "silver": 0, "diamond": 0, 
                "gemstone": 0, "mixed": 0, "unspecified": 0
            }
        cand_sums[cid]["total"] += val
        if cat in cand_sums[cid]:
            cand_sums[cid][cat] += val
        else:
            print(f"Unknown category {cat} in position: {p}")

    for cid, summary in summaries.items():
        pos_total = cand_sums.get(cid, {}).get("total", 0)
        sum_total = int(summary["total_declared_value_inr"])
        
        # Check total declared value
        if pos_total != sum_total:
            mismatches.append({
                "candidate_id": cid,
                "name": summary["mp_name"],
                "positions_total": pos_total,
                "summary_total": sum_total,
                "diff": pos_total - sum_total
            })
            
        # Check individual categories
        for cat in ["gold", "silver", "diamond", "gemstone", "mixed", "unspecified"]:
            pos_cat_val = cand_sums.get(cid, {}).get(cat, 0)
            sum_cat_val = int(summary[f"{cat}_value_inr"]) if summary.get(f"{cat}_value_inr") else 0
            if pos_cat_val != sum_cat_val:
                print(f"Category mismatch for cid {cid} ({summary['mp_name']}) in '{cat}': positions={pos_cat_val}, summary={sum_cat_val}")

    if mismatches:
        print(f"\nFound {len(mismatches)} total value mismatches between positions and summary:")
        for m in mismatches:
            print(f"  Candidate: {m['name']} (ID {m['candidate_id']}) | Positions: {m['positions_total']} | Summary: {m['summary_total']} | Diff: {m['diff']}")
    else:
        print("\nSUCCESS: All itemized declared values in positions match summary totals perfectly!")

    # Audit weights and anomalies
    print("\n--- Weight & Price Anomaly Audit ---")
    anomalies = []
    for p in positions:
        cid = p["candidate_id"]
        name = p["mp_name"]
        val = int(p["declared_value_inr"]) if p["declared_value_inr"] else 0
        weight = float(p["weight_grams"]) if p["weight_grams"] else None
        cat = p["category"]
        desc = p["raw_description"]

        if weight and val:
            implied_rate = val / weight
            # Gold rate in May 2024 was ~7,200 Rs/g. If implied rate is way off (e.g. < 500 Rs/g or > 50,000 Rs/g), flag it
            if cat == "gold":
                if implied_rate < 1000 or implied_rate > 30000:
                    anomalies.append({
                        "name": name,
                        "desc": desc,
                        "value": val,
                        "weight": weight,
                        "rate": implied_rate,
                        "reason": f"Implied Gold rate {implied_rate:.2f} Rs/g is highly abnormal (Nominal is ~7,200 Rs/g)"
                    })
            elif cat == "silver":
                # Silver rate in May 2024 was ~90-100 Rs/g (~96,000 per kg). If implied rate < 10 Rs/g or > 500 Rs/g, flag it
                if implied_rate < 10 or implied_rate > 500:
                    anomalies.append({
                        "name": name,
                        "desc": desc,
                        "value": val,
                        "weight": weight,
                        "rate": implied_rate,
                        "reason": f"Implied Silver rate {implied_rate:.2f} Rs/g is abnormal (Nominal is ~96 Rs/g)"
                    })

    if anomalies:
        print(f"Found {len(anomalies)} weight/rate anomalies due to transcription typos in raw affidavits:")
        for a in anomalies[:10]:
            print(f"  MP: {a['name']} | Desc: '{a['desc']}' | Declared Value: Rs {a['value']:,} | Extracted Weight: {a['weight']} g | Implied Rate: {a['rate']:.2f} Rs/g")
            print(f"    Reason: {a['reason']}")
        if len(anomalies) > 10:
            print(f"  ... and {len(anomalies) - 10} more anomalies.")
    else:
        print("No weight/rate anomalies found!")

if __name__ == "__main__":
    verify()
