"""
LumenOps 360 — Simulation Configuration
All parameters governing the data generator live here.
Change baselines to shift the narrative; re-run generate_data.py to regenerate.
"""

from datetime import date

# ─── Global ──────────────────────────────────────────────────
RANDOM_SEED = 42
START_DATE = date(2023, 1, 1)
END_DATE = date(2024, 6, 30)
OUTPUT_DIR = "data/raw"

# ─── Volume Targets ─────────────────────────────────────────
ORDERS_PER_MONTH = 150          # ~2,400 total over 18 months
SUPPLIER_DELIVERIES_PER_MONTH = 12  # PCB + LED chip combined

# ─── Baseline KPIs (intentionally sub-optimal) ──────────────
OEE_BASELINE = 0.62
AVAILABILITY_BASELINE = 0.82
PERFORMANCE_BASELINE = 0.85
QUALITY_BASELINE = 0.965        # ~3.5% defect rate
OTD_BASELINE = 0.78
STAFFING_FILL_RATE_BASELINE = 0.88  # Dutch labor shortage

# ─── Shift Configuration ────────────────────────────────────
SHIFTS = [
    {"shift_id": 1, "shift_name": "Morning", "start_time": "06:00", "end_time": "14:00"},
    {"shift_id": 2, "shift_name": "Evening", "start_time": "14:00", "end_time": "22:00"},
]
PLANNED_RUNTIME_MINS = 450      # 480 min shift minus 30 min breaks

# ─── Assembly Lines ─────────────────────────────────────────
LINES = [
    {"line_id": 1, "line_name": "Line_A", "rated_capacity_per_hour": 120,
     "primary_category": "Indoor"},
    {"line_id": 2, "line_name": "Line_B", "rated_capacity_per_hour": 80,
     "primary_category": "Outdoor"},
    {"line_id": 3, "line_name": "Line_C", "rated_capacity_per_hour": 60,
     "primary_category": "Industrial"},
]

# ─── Product Catalog ────────────────────────────────────────
PRODUCTS = [
    # Indoor
    {"sku": "IND-BAT-001", "product_name": "LED Batten Light 36W",
     "category": "Indoor", "sub_category": "Batten",
     "unit_cost_eur": 8.50, "unit_price_eur": 18.00,
     "ideal_cycle_time_sec": 28,
     "bom_components": {"housing": 1, "pcb_panel": 1, "led_chip": 12, "driver": 1, "diffuser": 1, "endcap": 2}},
    {"sku": "IND-PAN-001", "product_name": "2x2 Panel Light 40W",
     "category": "Indoor", "sub_category": "Panel",
     "unit_cost_eur": 14.00, "unit_price_eur": 32.00,
     "ideal_cycle_time_sec": 38,
     "bom_components": {"frame": 1, "pcb_panel": 2, "led_chip": 24, "driver": 1, "light_guide": 1, "backplate": 1}},
    {"sku": "IND-EPL-001", "product_name": "Edgelit Panel 600x600",
     "category": "Indoor", "sub_category": "Edgelit Panel",
     "unit_cost_eur": 16.50, "unit_price_eur": 38.00,
     "ideal_cycle_time_sec": 42,
     "bom_components": {"frame": 1, "pcb_strip": 2, "led_chip": 36, "driver": 1, "light_guide": 1, "diffuser": 1}},
    {"sku": "IND-BLB-001", "product_name": "LED Bulb A60 9W",
     "category": "Indoor", "sub_category": "Bulb",
     "unit_cost_eur": 1.80, "unit_price_eur": 4.50,
     "ideal_cycle_time_sec": 12,
     "bom_components": {"housing_plastic": 1, "pcb_round": 1, "led_chip": 6, "driver_compact": 1, "lens": 1, "base_e27": 1}},
    # Outdoor
    {"sku": "OUT-FLD-001", "product_name": "Eco Flood Light 100W",
     "category": "Outdoor", "sub_category": "Flood",
     "unit_cost_eur": 22.00, "unit_price_eur": 52.00,
     "ideal_cycle_time_sec": 55,
     "bom_components": {"housing_die_cast": 1, "pcb_panel": 2, "led_chip": 48, "driver": 1, "lens_array": 1, "bracket": 1, "gasket": 1}},
    {"sku": "OUT-STR-001", "product_name": "Street Light 150W",
     "category": "Outdoor", "sub_category": "Street",
     "unit_cost_eur": 45.00, "unit_price_eur": 95.00,
     "ideal_cycle_time_sec": 72,
     "bom_components": {"housing_die_cast": 1, "pcb_panel": 3, "led_chip": 72, "driver_hv": 1, "lens_array": 2, "arm_adapter": 1, "surge_protector": 1}},
    # Industrial
    {"sku": "IND-HBU-001", "product_name": "High Bay UFO 200W",
     "category": "Industrial", "sub_category": "High Bay",
     "unit_cost_eur": 38.00, "unit_price_eur": 85.00,
     "ideal_cycle_time_sec": 65,
     "bom_components": {"housing_finned": 1, "pcb_panel": 2, "led_chip": 60, "driver_hv": 1, "lens_120deg": 1, "hook_chain": 1}},
    {"sku": "IND-WGL-001", "product_name": "Well Glass Light 40W",
     "category": "Industrial", "sub_category": "Well Glass",
     "unit_cost_eur": 12.00, "unit_price_eur": 28.00,
     "ideal_cycle_time_sec": 35,
     "bom_components": {"housing_polycarbonate": 1, "pcb_panel": 1, "led_chip": 16, "driver": 1, "glass_cover": 1, "guard": 1}},
    {"sku": "IND-COB-001", "product_name": "COB Downlight 15W",
     "category": "Industrial", "sub_category": "COB Downlight",
     "unit_cost_eur": 6.50, "unit_price_eur": 16.00,
     "ideal_cycle_time_sec": 22,
     "bom_components": {"housing_aluminium": 1, "cob_module": 1, "driver_compact": 1, "reflector": 1, "spring_clip": 2}},
]

# ─── Customer Catalog ───────────────────────────────────────
CUSTOMERS = [
    {"customer_id": 1, "name": "Gamma",    "country": "NL", "segment": "Retail",    "order_weight": 0.18},
    {"customer_id": 2, "name": "Hornbach", "country": "NL", "segment": "Retail",    "order_weight": 0.15},
    {"customer_id": 3, "name": "Praxis",   "country": "NL", "segment": "Retail",    "order_weight": 0.14},
    {"customer_id": 4, "name": "Karwei",   "country": "NL", "segment": "Retail",    "order_weight": 0.10},
    {"customer_id": 5, "name": "Action",   "country": "NL", "segment": "Wholesale", "order_weight": 0.20},
    {"customer_id": 6, "name": "Jumbo",    "country": "NL", "segment": "Wholesale", "order_weight": 0.08},
    {"customer_id": 7, "name": "Coolblue", "country": "NL", "segment": "B2B",       "order_weight": 0.15},
]

# ─── Supplier Catalog ───────────────────────────────────────
SUPPLIERS = [
    {"supplier_id": 1, "name": "ShenZhen CircuitPro Ltd",
     "component_type": "PCB", "country": "China",
     "avg_lead_time_days": 21, "is_single_source": True,
     "tariff_exposure_pct": 0.25, "on_time_baseline_pct": 0.82},
    {"supplier_id": 2, "name": "Guangdong OptoChip Co",
     "component_type": "LED_CHIP", "country": "China",
     "avg_lead_time_days": 28, "is_single_source": True,
     "tariff_exposure_pct": 0.25, "on_time_baseline_pct": 0.79},
    {"supplier_id": 3, "name": "Taiwan SemiLED Corp",
     "component_type": "LED_CHIP", "country": "Taiwan",
     "avg_lead_time_days": 18, "is_single_source": False,
     "tariff_exposure_pct": 0.05, "on_time_baseline_pct": 0.91},
    {"supplier_id": 4, "name": "EuroBoard GmbH",
     "component_type": "PCB", "country": "Germany",
     "avg_lead_time_days": 10, "is_single_source": False,
     "tariff_exposure_pct": 0.00, "on_time_baseline_pct": 0.95},
]

# ─── Defect Reason Codes ────────────────────────────────────
DEFECT_REASONS = [
    {"code": "FLICKER",                 "description": "Light flickering post-assembly",
     "severity": "Critical",  "typical_root_cause": "Poor solder joint on driver-PCB interface",
     "weight": 0.12},
    {"code": "HOUSING_SCRATCH",         "description": "Cosmetic scratch on housing",
     "severity": "Minor",     "typical_root_cause": "Rough handling during transfer to QC station",
     "weight": 0.18},
    {"code": "HOUSING_DAMAGE_ASSEMBLY", "description": "Structural damage from incorrect screw torque",
     "severity": "Major",     "typical_root_cause": "Operator over-torque or wrong bit selection",
     "weight": 0.15},
    {"code": "DUST_CONTAMINATION",      "description": "Visible dust particles inside housing",
     "severity": "Minor",     "typical_root_cause": "Inadequate cleanroom protocol / open bay assembly",
     "weight": 0.14},
    {"code": "COLOR_CONTAMINATION",     "description": "Paint or colorant residue on product",
     "severity": "Minor",     "typical_root_cause": "Shared workbench with painting station nearby",
     "weight": 0.05},
    {"code": "SOLDER_FAIL",             "description": "Cold or cracked solder joint on PCB",
     "severity": "Critical",  "typical_root_cause": "Incoming PCB quality / wave-solder temperature drift",
     "weight": 0.10},
    {"code": "DRIVER_FAULT",            "description": "LED driver not functioning or unstable output",
     "severity": "Critical",  "typical_root_cause": "Defective driver component or ESD damage",
     "weight": 0.08},
    {"code": "POOR_PACKAGING",          "description": "Packaging integrity failure — crushed or open box",
     "severity": "Minor",     "typical_root_cause": "End-of-shift rush, insufficient packaging material",
     "weight": 0.12},
    {"code": "LUMEN_OUT_OF_SPEC",       "description": "Brightness below specification threshold",
     "severity": "Major",     "typical_root_cause": "LED chip binning variance or thermal derating",
     "weight": 0.06},
]

# ─── Downtime Reason Codes ──────────────────────────────────
DOWNTIME_REASONS = [
    {"code": "CHANGEOVER",                "description": "SKU transition / line setup change",
     "category": "Planned",   "weight": 0.28, "avg_duration_mins": 45},
    {"code": "MANPOWER_SHORT",            "description": "Operator absence or understaffing",
     "category": "Unplanned", "weight": 0.22, "avg_duration_mins": 60},
    {"code": "MATERIAL_SHORTAGE_INTERNAL","description": "Store could not deliver material on time",
     "category": "Unplanned", "weight": 0.12, "avg_duration_mins": 35},
    {"code": "SCHEDULE_CHANGE_MGMT",      "description": "Mid-shift schedule change from management",
     "category": "Unplanned", "weight": 0.10, "avg_duration_mins": 30},
    {"code": "MACHINE_FAULT",             "description": "Equipment breakdown or malfunction",
     "category": "Unplanned", "weight": 0.08, "avg_duration_mins": 55},
    {"code": "PCB_SHORTAGE_SUPPLIER",     "description": "PCB supplier delivery delayed",
     "category": "External",  "weight": 0.06, "avg_duration_mins": 120},
    {"code": "LED_CHIP_SHORTAGE_SUPPLIER","description": "LED chip supplier delivery delayed",
     "category": "External",  "weight": 0.05, "avg_duration_mins": 120},
    {"code": "QUALITY_HOLD",              "description": "Line stopped for QC investigation",
     "category": "Unplanned", "weight": 0.04, "avg_duration_mins": 40},
    {"code": "POWER_OUTAGE",              "description": "External power supply interruption",
     "category": "External",  "weight": 0.02, "avg_duration_mins": 90},
    {"code": "CLEANING_MAINTENANCE",      "description": "Planned preventive maintenance or cleaning",
     "category": "Planned",   "weight": 0.03, "avg_duration_mins": 25},
]

# ─── Seasonality Multipliers (index 1-12 → Jan-Dec) ────────
# Slightly higher demand in Q3-Q4 (construction / retail stocking)
MONTHLY_DEMAND_MULTIPLIER = {
    1: 0.85, 2: 0.88, 3: 0.95, 4: 1.00, 5: 1.02, 6: 1.05,
    7: 0.92, 8: 0.90, 9: 1.08, 10: 1.15, 11: 1.12, 12: 0.95,
}

# ─── Priority Distribution ──────────────────────────────────
PRIORITY_WEIGHTS = {"Standard": 0.70, "Urgent": 0.22, "VIP": 0.08}

# ─── Delay Reason Weights (for dispatch) ────────────────────
DELAY_REASONS = [
    "Production backlog", "Material shortage", "QC hold",
    "Packaging delay", "Logistics scheduling", "Customer reschedule",
]

# ─── SKU-specific defect rate modifiers ─────────────────────
# Some products are harder to build (higher defect rate)
SKU_DEFECT_MODIFIER = {
    "IND-BAT-001": 1.0,   # baseline
    "IND-PAN-001": 1.3,   # complex panel assembly
    "IND-EPL-001": 1.4,   # edgelit = precision
    "IND-BLB-001": 0.7,   # simple bulb
    "OUT-FLD-001": 1.2,   # outdoor = gasket sealing
    "OUT-STR-001": 1.5,   # most complex product
    "IND-HBU-001": 1.3,   # heavy, precision
    "IND-WGL-001": 0.9,   # moderate
    "IND-COB-001": 0.8,   # simple downlight
}

# ─── Line-product affinity (probability of being scheduled) ─
# Rows = lines (A, B, C), columns = product index
LINE_PRODUCT_AFFINITY = {
    1: {  # Line A — Indoor-heavy
        "IND-BAT-001": 0.22, "IND-PAN-001": 0.18, "IND-EPL-001": 0.15,
        "IND-BLB-001": 0.20, "OUT-FLD-001": 0.05, "OUT-STR-001": 0.02,
        "IND-HBU-001": 0.05, "IND-WGL-001": 0.05, "IND-COB-001": 0.08,
    },
    2: {  # Line B — Outdoor-heavy
        "IND-BAT-001": 0.05, "IND-PAN-001": 0.05, "IND-EPL-001": 0.03,
        "IND-BLB-001": 0.07, "OUT-FLD-001": 0.30, "OUT-STR-001": 0.25,
        "IND-HBU-001": 0.10, "IND-WGL-001": 0.10, "IND-COB-001": 0.05,
    },
    3: {  # Line C — Industrial-heavy
        "IND-BAT-001": 0.05, "IND-PAN-001": 0.05, "IND-EPL-001": 0.03,
        "IND-BLB-001": 0.02, "OUT-FLD-001": 0.08, "OUT-STR-001": 0.07,
        "IND-HBU-001": 0.30, "IND-WGL-001": 0.22, "IND-COB-001": 0.18,
    },
}
