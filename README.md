# Target-Costing Workbench — Should-Cost, Attainment & Negotiation Pack

**Author:** Ichwan Ramadhanil · Cost Planning Engineer, Hino Motors (Toyota Group)
**Stack:** Python (model) · Excel with live formulas (tracker) · CSV outputs
**Companion repo:** [cost-to-serve-analytics](https://github.com/iramadhanil/cost-to-serve-analytics) — the same cost discipline applied to e-commerce logistics (incl. supplier freight benchmarking, analysis 07).

## What this is
A working demonstration of the **target-costing workflow used in automotive purchasing**, on an
illustrative 26-part BOM for an electric coolant pump assembly (BLDC motor + controller + housing):

1. **Should-cost every part** — two methods, matching how purchasing actually works:
   - *Drawing parts* (castings, moldings, windings, stampings): bottom-up **weight x material market rate + process cost + overhead + supplier margin**
   - *Catalog parts* (semiconductors, passives): **distributor market-price benchmark** — weight-based costing is meaningless for silicon
2. **Set the target** — current assembly cost x (1 − 8%), the classic next-generation cost-reduction assumption
3. **Quantify the gap** per part, per commodity, per supplier → **attainment** vs target
4. **Build the negotiation pack** — Pareto-ranked gaps with a recommended lever per part
   (should-cost re-quote / market re-quote / VA-VE workshop / volume bundling)

## Headline results (computed — run it yourself)

| Metric | Value |
|---|---|
| Current assembly cost | ¥5,727 |
| Bottom-up should-cost | ¥5,085 (−11.2%) |
| Target cost (−8%) | ¥5,269 |
| **Target attainment if should-cost achieved** | **140% — target fully covered, with buffer** |
| Annual value @ 120k units/yr | **¥77.0M** |
| Largest commodity gap | Electromech: ¥297/unit (13.1% of commodity spend) |
| #1 negotiation target | Stator core: ¥177/unit gap → ¥21.3M/yr — should-cost re-quote |

## Files
| File | What it does |
|---|---|
| `data/bom.csv` | 26-part BOM (part, commodity, supplier, material, weight, current price, market ref) |
| `generate_bom.py` | Reproducibly generates the BOM (fixed seed) |
| `should_cost.py` | The model: should-cost → target → gap → negotiation pack. Run: `python should_cost.py` |
| `results/` | Computed outputs: per-part should-cost, commodity waterfall, negotiation pack, summary |
| `build_tracker.py` | Generates the Excel tracker programmatically (openpyxl) — formulas, not pasted values |
| `target_cost_tracker.xlsx` | **Live-formula Excel twin** — edit blue cells (material rates, overhead, target %) and attainment recalculates. Verified: Excel results match the Python model to the yen. |

## Honesty note (read this)
The **method is real** — it is the daily discipline of cost planning in the Toyota Group
(target costing, genchi genbutsu on cost breakdowns, supplier should-cost).
The **data is synthetic** (fixed-seed generator, order-of-magnitude realistic rates) because real
part-level cost data from my work is confidential. Every number in this repo is reproducible
from the committed code.

## Why this matters for a purchasing role
Buyers negotiate from cost breakdowns. This workbench produces exactly what a buyer needs at
the table: the should-cost, the gap, the size of the prize per supplier, and which lever to
pull — before the first RFQ round. At Hino I build these analyses for truck platforms; this
repo shows the same mechanics end-to-end on shareable data.
