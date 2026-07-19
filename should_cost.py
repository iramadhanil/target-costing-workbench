"""Should-cost model + target-cost attainment for an electric coolant pump assembly.

Method (the same discipline used in automotive target costing):
  should_cost = material (weight x market rate, + scrap)
              + process   (machine-rate x cycle time proxy by commodity)
              + overhead  (SG&A % on material+process)
              + supplier margin %
  gap        = current supplier price - should_cost   -> negotiation agenda
  target     = current assembly cost x (1 - TARGET_REDUCTION) -> attainment tracking

Data in data/bom.csv is SYNTHETIC (see generate_bom.py). Method over data.
Outputs: results/should_cost_by_part.csv, results/commodity_waterfall.csv,
         results/negotiation_pack.csv, results/summary.md
"""
import csv, os
from collections import defaultdict

ANNUAL_VOLUME = 120_000          # units / year
TARGET_REDUCTION = 0.08          # target = -8% vs current assembly cost

# JPY per kg market material rates (illustrative, order-of-magnitude realistic)
# JPY/kg for drawing-based parts. Catalog electronics are NOT weight-costed —
# they are benchmarked against distributor market prices (market_ref_jpy in the BOM),
# which is how purchasing actually treats catalog vs drawing parts.
MATERIAL_RATE = {"FR4": 2400, "Alloy": 3200, "Aluminum": 950,
    "Ceramic": 3000, "PA66": 780, "Ferrite": 1500, "Steel": 320, "Copper": 1450,
    "SUS304": 680, "ADC12": 640, "PPS": 1250, "Carbon/SiC": 8000, "EPDM": 900,
    "Silicone": 800, "PET": 400, "PE": 260}
SCRAP = 0.03
# process cost proxy per commodity: JPY per unit weight band + fixed handling
PROCESS = {"Electromech": (0.55, 40),
           "Mechanical": (0.5, 18), "Fasteners": (0.1, 4), "Packaging": (0.1, 3)}
HANDLING_CATALOG = 0.02   # inbound handling on market-benchmarked catalog parts
OVERHEAD = 0.12
MARGIN = 0.10

def should_cost(row):
    if row["commodity"] == "Electronics":
        # catalog part: benchmark = distributor market reference + inbound handling
        return round(float(row["market_ref_jpy"]) * (1 + HANDLING_CATALOG), 1)
    # drawing part: bottom-up material + process + overhead + margin
    wt_kg = float(row["unit_weight_g"]) / 1000
    material = wt_kg * MATERIAL_RATE[row["material"]] * (1 + SCRAP)
    var_rate, fixed = PROCESS[row["commodity"]]
    process = float(row["unit_weight_g"]) * var_rate + fixed
    base = material + process
    return round(base * (1 + OVERHEAD) * (1 + MARGIN), 1)

def main():
    os.makedirs("results", exist_ok=True)
    rows = list(csv.DictReader(open("data/bom.csv")))
    for r in rows:
        r["qty"] = int(r["qty_per_unit"])
        r["current_ext"] = float(r["current_price_jpy"]) * r["qty"]
        r["should_unit"] = should_cost(r)
        r["should_ext"] = round(r["should_unit"] * r["qty"], 1)
        r["gap_ext"] = round(r["current_ext"] - r["should_ext"], 1)
        r["annual_gap"] = round(r["gap_ext"] * ANNUAL_VOLUME)

    current_total = sum(r["current_ext"] for r in rows)
    should_total = sum(r["should_ext"] for r in rows)
    target_total = current_total * (1 - TARGET_REDUCTION)
    addressable = sum(max(r["gap_ext"], 0) for r in rows)
    attainment = (current_total - should_total) / (current_total - target_total)

    with open("results/should_cost_by_part.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["part_no","part_name","commodity","supplier","qty","current_ext_jpy",
                    "should_cost_ext_jpy","gap_jpy","annual_gap_jpy"])
        for r in sorted(rows, key=lambda x: -x["gap_ext"]):
            w.writerow([r["part_no"], r["part_name"], r["commodity"], r["supplier"],
                        r["qty"], r["current_ext"], r["should_ext"], r["gap_ext"], r["annual_gap"]])

    comm = defaultdict(lambda: [0.0, 0.0])
    for r in rows:
        comm[r["commodity"]][0] += r["current_ext"]
        comm[r["commodity"]][1] += r["should_ext"]
    with open("results/commodity_waterfall.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["commodity","current_jpy","should_cost_jpy","gap_jpy","gap_pct_of_current"])
        for c,(cur,sh) in sorted(comm.items(), key=lambda kv: -(kv[1][0]-kv[1][1])):
            w.writerow([c, round(cur,1), round(sh,1), round(cur-sh,1), round(100*(cur-sh)/cur,1)])

    # negotiation pack: positive-gap parts, Pareto with cumulative share
    neg = [r for r in sorted(rows, key=lambda x: -x["gap_ext"]) if r["gap_ext"] > 0]
    cum = 0.0
    with open("results/negotiation_pack.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank","part_no","part_name","supplier","gap_jpy","annual_gap_jpy","cum_share_pct","lever"])
        for i,r in enumerate(neg,1):
            cum += r["gap_ext"]
            lever = ("market re-quote (distributor benchmark)" if r["commodity"] == "Electronics"
                     else "should-cost re-quote" if r["gap_ext"] > 80
                     else "VA/VE workshop" if r["commodity"] in ("Mechanical","Electromech")
                     else "volume bundling")
            w.writerow([i, r["part_no"], r["part_name"], r["supplier"], r["gap_ext"],
                        r["annual_gap"], round(100*cum/addressable,1), lever])

    with open("results/summary.md", "w") as f:
        f.write(f"""# Target-cost attainment summary (synthetic BOM, {len(rows)} parts)

| Metric | Value |
|---|---|
| Current assembly cost | ¥{current_total:,.0f} |
| Should-cost (bottom-up) | ¥{should_total:,.0f} |
| Target cost (-{TARGET_REDUCTION:.0%}) | ¥{target_total:,.0f} |
| Total gap current vs should | ¥{current_total-should_total:,.0f} ({100*(current_total-should_total)/current_total:.1f}% of current) |
| Addressable gap (positive-gap parts) | ¥{addressable:,.0f} |
| Target attainment if should-cost achieved | {attainment:.0%} of required reduction |
| Annual value @ {ANNUAL_VOLUME:,} units | ¥{(current_total-should_total)*ANNUAL_VOLUME:,.0f} |

Top negotiation targets and levers: see `negotiation_pack.csv`.
""")
    print(f"current ¥{current_total:,.0f} | should ¥{should_total:,.0f} | target ¥{target_total:,.0f} | attainment {attainment:.0%}")
    print("results/ written: should_cost_by_part.csv, commodity_waterfall.csv, negotiation_pack.csv, summary.md")

if __name__ == "__main__":
    main()
