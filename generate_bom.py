"""Generate the illustrative BOM for the target-costing workbench.
Data is SYNTHETIC (fixed seed) — realistic structure, invented numbers.
Real part-level cost data from my day job is confidential; the method is the point.
"""
import csv, random

random.seed(42)

# part_name, commodity, material, unit_weight_g, base_price_jpy (current supplier price)
PARTS = [
    # Electronics
    ("Main PCB (4-layer FR4)",        "Electronics", "FR4",       82,  612),
    ("MCU 32-bit (motor control)",    "Electronics", "Silicon",    4,  438),
    ("Gate driver IC",                "Electronics", "Silicon",    2,  186),
    ("Power MOSFET (40V)",            "Electronics", "Silicon",    3,   92),
    ("Current sense shunt",           "Electronics", "Alloy",      2,   34),
    ("DC-link capacitor (electrolytic)","Electronics","Aluminum",  18,  118),
    ("Ceramic capacitor set (MLCC)",  "Electronics", "Ceramic",    6,   64),
    ("Connector 6-pin sealed",        "Electronics", "PA66",      14,  142),
    ("EMC filter choke",              "Electronics", "Ferrite",   26,   96),
    ("Position sensor (Hall)",        "Electronics", "Silicon",    3,  128),
    # Electromechanical
    ("Stator core (laminated)",       "Electromech", "Steel",    412,  684),
    ("Stator winding (copper)",       "Electromech", "Copper",   187,  542),
    ("Rotor assembly",                "Electromech", "Steel",    298,  486),
    ("Ferrite magnet set",            "Electromech", "Ferrite",  118,  214),
    ("Shaft (stainless)",             "Electromech", "SUS304",    64,  156),
    ("Bearing 608ZZ pair",            "Electromech", "Steel",     28,  164),
    # Mechanical
    ("Pump housing (die-cast Al)",    "Mechanical",  "ADC12",    342,  517),
    ("Volute cover (PPS-GF40)",       "Mechanical",  "PPS",       96,  238),
    ("Impeller (PPS-GF40)",           "Mechanical",  "PPS",       42,  147),
    ("Mechanical seal",               "Mechanical",  "Carbon/SiC",12,  216),
    ("O-ring set (EPDM)",             "Mechanical",  "EPDM",       8,   38),
    ("Mounting bracket (stamped)",    "Mechanical",  "Steel",    118,  128),
    ("Thermal pad",                   "Mechanical",  "Silicone",   9,   42),
    # Fasteners & packaging
    ("Screw set M4/M5 (x8)",          "Fasteners",   "Steel",     22,   26),
    ("Label + serial plate",          "Packaging",   "PET",        3,   12),
    ("Protective cap set",            "Packaging",   "PE",         7,   14),
]

SUPPLIERS = {
    "Electronics": ["Denki Parts KK", "Sunrise Micro", "Nagoya Circuits"],
    "Electromech": ["Chubu Motor Works", "Aichi Windings"],
    "Mechanical":  ["Toyokawa Diecast", "Mikawa Polymer", "Sealtech JP"],
    "Fasteners":   ["Hamamatsu Fastener"],
    "Packaging":   ["Shizuoka Pack"],
}

with open("data/bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["part_no","part_name","commodity","supplier","material",
                "qty_per_unit","unit_weight_g","current_price_jpy","market_ref_jpy"])
    for i,(name, comm, mat, wt, price) in enumerate(PARTS, 1):
        qty = 2 if "MOSFET" in name else 1
        # keep supplier assignment technology-consistent
        if comm == "Mechanical":
            supplier = ("Toyokawa Diecast" if mat in ("ADC12","Steel") else
                        "Sealtech JP" if "seal" in name.lower() or mat in ("EPDM","Silicone","Carbon/SiC") else
                        "Mikawa Polymer")
        elif comm == "Electromech":
            supplier = "Aichi Windings" if "winding" in name.lower() else "Chubu Motor Works"
        else:
            supplier = random.choice(SUPPLIERS[comm])
        # sprinkle realistic price noise so gaps differ by supplier
        noisy = round(price * random.uniform(0.97, 1.12))
        # catalog electronics carry an independent distributor market benchmark
        market_ref = round(noisy * random.uniform(0.80, 0.97)) if comm == "Electronics" else ""
        w.writerow([f"P-{i:03d}", name, comm, supplier, mat, qty, wt, noisy, market_ref])
print("data/bom.csv written:", len(PARTS), "parts")
