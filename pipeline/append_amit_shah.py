import json

report_path = "/Users/macbook/.gemini/antigravity/brain/4d775da5-a1a0-4ffb-a389-8016d895282d/neta_investment_performance_report.md"
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

# Format positions as a markdown table
positions = sorted(as_portfolio["positions"], key=lambda x: -x["cur_value"])

appendix_content = f"""
---

## Appendix: Amit Shah's Detailed Portfolio

Amit Shah (BJP, Gandhinagar) holds the most diversified portfolio in the Lok Sabha, consisting of **{as_portfolio['n_equity']} trackable equity positions** and **{as_portfolio['n_fund']} mutual fund positions** spread across both his name (Self) and his spouse's name. 

### Summary Portfolio Metrics:
- **Base Disclosed Value**: **Rs {as_portfolio['base_value']/1e7:.2f} Crore**
- **Current Audited Value**: **Rs {as_portfolio['cur_value']/1e7:.2f} Crore**
- **Absolute Net Gain**: **+Rs {(as_portfolio['cur_value'] - as_portfolio['base_value'])/1e7:.2f} Crore**
- **Aggregate Return**: **{as_portfolio['ret_pct']:+.2f}%**
- **Winning Positions (>= +30%)**: **30 holdings**

### Complete Position-Level Performance Breakdown:

| Rank | Security Name | Ticker | Declared Value (INR) | Current Value (INR) | Return % | Owner |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
"""

for i, pos in enumerate(positions):
    dv = pos['declared_value']
    cv = pos['cur_value']
    
    dv_str = f"Rs {dv/1e5:.2f} Lakh" if dv >= 100000 else f"Rs {dv:,}"
    cv_str = f"Rs {cv/1e5:.2f} Lakh" if cv >= 100000 else f"Rs {cv:,}"
    
    appendix_content += f"| **{i+1}** | {pos['name']} | `{pos['symbol']}` | {dv_str} | {cv_str} | **{pos['ret_pct']:+.1f}%** | {pos['owner'].capitalize()} |\n"

# Read existing report
with open(report_path, "r") as f:
    existing_content = f.read()

# Make sure we don't append multiple times if run twice
if "## Appendix: Amit Shah's Detailed Portfolio" in existing_content:
    # Strip existing appendix
    parts = existing_content.split("---")
    # Let's find the index of the last part that contains the appendix
    non_appendix_parts = []
    for part in parts:
        if "## Appendix: Amit Shah's Detailed Portfolio" not in part:
            non_appendix_parts.append(part)
    existing_content = "---".join(non_appendix_parts)

# Append new appendix
new_content = existing_content.strip() + "\n" + appendix_content

with open(report_path, "w") as f:
    f.write(new_content)

print("Successfully appended Amit Shah's portfolio as an appendix to the performance report!")
