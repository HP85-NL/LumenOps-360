#!/usr/bin/env python3
"""
LumenOps 360 — Data Generator
==============================
Generates 18 months of realistic manufacturing operations data for
LumenTech BV, Eindhoven — a fictional Dutch OEM LED lighting manufacturer.

Seed:   42 (deterministic, reproducible)
Output: 14 CSV files in data/raw/
Run:    python src/generate_data.py
"""

import os
import sys
import json
import warnings
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

# ─── Ensure src/ is importable ───────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
import config as cfg

warnings.filterwarnings("ignore", category=FutureWarning)

# ─── Seed ────────────────────────────────────────────────────
RNG = np.random.default_rng(cfg.RANDOM_SEED)


# ═══════════════════════════════════════════════════════════════
#  DIMENSION TABLES
# ═══════════════════════════════════════════════════════════════

def generate_dim_date():
    """Standard date dimension — Jan 2023 to Jun 2024."""
    dates = pd.date_range(cfg.START_DATE, cfg.END_DATE, freq="D")
    df = pd.DataFrame({"date": dates})
    df["year"] = df["date"].dt.year
    df["quarter"] = df["date"].dt.quarter
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%B")
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["day"] = df["date"].dt.day
    df["day_of_week"] = df["date"].dt.dayofweek          # 0=Mon … 6=Sun
    df["day_name"] = df["date"].dt.strftime("%A")
    df["is_weekend"] = df["day_of_week"].isin([5, 6])    # Sat/Sun
    df["is_production_day"] = df["day_of_week"] < 6      # Mon–Sat
    df["date"] = df["date"].dt.date
    return df


def generate_dim_customer():
    rows = []
    for c in cfg.CUSTOMERS:
        rows.append({
            "customer_id": c["customer_id"],
            "customer_name": c["name"],
            "country": c["country"],
            "segment": c["segment"],
        })
    return pd.DataFrame(rows)


def generate_dim_product():
    rows = []
    for p in cfg.PRODUCTS:
        rows.append({
            "sku": p["sku"],
            "product_name": p["product_name"],
            "category": p["category"],
            "sub_category": p["sub_category"],
            "unit_cost_eur": p["unit_cost_eur"],
            "ideal_cycle_time_sec": p["ideal_cycle_time_sec"],
            "bom_components_json": json.dumps(p["bom_components"]),
        })
    return pd.DataFrame(rows)


def generate_dim_line():
    rows = []
    for ln in cfg.LINES:
        rows.append({
            "line_id": ln["line_id"],
            "line_name": ln["line_name"],
            "rated_capacity_per_hour": ln["rated_capacity_per_hour"],
            "primary_category": ln["primary_category"],
        })
    return pd.DataFrame(rows)


def generate_dim_shift():
    return pd.DataFrame(cfg.SHIFTS)


def generate_dim_defect_reason():
    rows = []
    for d in cfg.DEFECT_REASONS:
        rows.append({
            "code": d["code"],
            "description": d["description"],
            "severity": d["severity"],
            "typical_root_cause": d["typical_root_cause"],
        })
    return pd.DataFrame(rows)


def generate_dim_downtime_reason():
    rows = []
    for d in cfg.DOWNTIME_REASONS:
        rows.append({
            "code": d["code"],
            "description": d["description"],
            "category": d["category"],
        })
    return pd.DataFrame(rows)


def generate_dim_supplier():
    rows = []
    for s in cfg.SUPPLIERS:
        rows.append({
            "supplier_id": s["supplier_id"],
            "supplier_name": s["name"],
            "component_type": s["component_type"],
            "country": s["country"],
            "avg_lead_time_days": s["avg_lead_time_days"],
            "is_single_source": s["is_single_source"],
            "tariff_exposure_pct": s["tariff_exposure_pct"],
            "on_time_baseline_pct": s["on_time_baseline_pct"],
        })
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def _pick_sku_for_line(line_id):
    """Weighted random SKU selection based on line-product affinity."""
    affinity = cfg.LINE_PRODUCT_AFFINITY[line_id]
    skus = list(affinity.keys())
    weights = np.array(list(affinity.values()))
    weights /= weights.sum()
    return RNG.choice(skus, p=weights)


def _get_product(sku):
    """Look up product dict by SKU."""
    for p in cfg.PRODUCTS:
        if p["sku"] == sku:
            return p
    raise ValueError(f"Unknown SKU: {sku}")


def _get_line(line_id):
    """Look up line dict by ID."""
    for ln in cfg.LINES:
        if ln["line_id"] == line_id:
            return ln
    raise ValueError(f"Unknown line_id: {line_id}")


def _planned_operators(line_id):
    """Engineering standard for operators needed per shift."""
    return {1: 8, 2: 6, 3: 5}[line_id]


def _seasonal_staffing_factor(month):
    """Summer holidays (Jul-Aug) and Dec holidays reduce staffing."""
    factors = {
        1: 0.92, 2: 0.95, 3: 0.97, 4: 1.00, 5: 1.00, 6: 0.98,
        7: 0.85, 8: 0.83, 9: 0.95, 10: 0.97, 11: 0.96, 12: 0.88,
    }
    return factors[month]


# ═══════════════════════════════════════════════════════════════
#  FACT: PRODUCTION LOG
# ═══════════════════════════════════════════════════════════════

def generate_fact_production_log(dim_date_df):
    """
    One row per line × shift × production day.
    Saturday: morning shift only (5.5-day week).
    Encodes OEE decomposition, staffing, downtime with realistic correlations.

    Production runs: each line runs the SAME SKU for 3–10 consecutive shifts
    before switching. Changeovers only occur at run boundaries (~15–20% of shifts).
    """
    production_days = dim_date_df[dim_date_df["is_production_day"]].copy()
    production_days = production_days.sort_values("date").reset_index(drop=True)

    lines = [1, 2, 3]
    records = []
    prod_log_id = 0

    # Production run state: current SKU and remaining shifts before changeover
    run_state = {}
    for lid in lines:
        sku = _pick_sku_for_line(lid)
        run_state[lid] = {
            "sku": sku,
            "remaining": int(RNG.integers(4, 9)),  # initial run length
        }

    # Non-changeover downtime reasons (exclude CHANGEOVER from random draws)
    dt_codes_noco = [d["code"] for d in cfg.DOWNTIME_REASONS
                     if d["code"] != "CHANGEOVER"]
    dt_weights_noco = np.array([d["weight"] for d in cfg.DOWNTIME_REASONS
                                if d["code"] != "CHANGEOVER"])
    dt_weights_noco /= dt_weights_noco.sum()
    dt_avgs = {d["code"]: d["avg_duration_mins"] for d in cfg.DOWNTIME_REASONS}

    for _, day_row in production_days.iterrows():
        d = day_row["date"]
        dow = day_row["day_of_week"]
        month = d.month if isinstance(d, date) else d.month

        # Saturday: morning shift only
        shifts_today = [1] if dow == 5 else [1, 2]

        for line_id in lines:
            line = _get_line(line_id)
            for shift_id in shifts_today:
                prod_log_id += 1

                # ── SKU scheduling (production run logic) ──
                is_changeover = False
                if run_state[line_id]["remaining"] <= 0:
                    # End of run → changeover to a new SKU
                    old_sku = run_state[line_id]["sku"]
                    new_sku = _pick_sku_for_line(line_id)
                    # Ensure it's actually a different SKU (retry up to 5×)
                    attempts = 0
                    while new_sku == old_sku and attempts < 5:
                        new_sku = _pick_sku_for_line(line_id)
                        attempts += 1
                    run_state[line_id]["sku"] = new_sku
                    run_state[line_id]["remaining"] = int(RNG.integers(3, 11))
                    is_changeover = True

                sku = run_state[line_id]["sku"]
                run_state[line_id]["remaining"] -= 1
                product = _get_product(sku)

                # ── Staffing ──
                planned_ops = _planned_operators(line_id)
                seasonal_factor = _seasonal_staffing_factor(month)
                fill_rate = np.clip(
                    cfg.STAFFING_FILL_RATE_BASELINE * seasonal_factor
                    + RNG.normal(0, 0.05),
                    0.60, 1.00
                )
                actual_ops = max(
                    int(np.round(planned_ops * fill_rate)),
                    int(np.ceil(planned_ops * 0.5))   # minimum 50%
                )
                staffing_ratio = actual_ops / planned_ops

                # ── Downtime ──
                planned_runtime = cfg.PLANNED_RUNTIME_MINS
                downtime_mins = 0
                downtime_reason = None

                # (a) Micro-stoppages — every shift has minor losses
                # (jam clearance, operator breaks extending, minor adjustments)
                micro_stop = max(0, int(RNG.normal(18, 8)))
                downtime_mins += micro_stop

                # (b) Changeover downtime — only at run boundary
                if is_changeover:
                    changeover_time = max(15, int(RNG.normal(50, 15)))
                    downtime_mins += changeover_time
                    downtime_reason = "CHANGEOVER"

                # (c) Random downtime event (~55% of shifts)
                if RNG.random() < 0.55:
                    reason = RNG.choice(dt_codes_noco, p=dt_weights_noco)
                    avg_dur = dt_avgs[reason]
                    extra_dt = max(10, int(RNG.normal(avg_dur, avg_dur * 0.3)))
                    downtime_mins += extra_dt
                    if downtime_reason is None:
                        downtime_reason = reason

                # (c) Understaffing adds implicit downtime
                # Downtime accumulates whenever staffing is below 85%,
                # but MANPOWER_SHORT is only the PRIMARY reason when
                # it's severe (< 75%) and no other event dominates.
                if staffing_ratio < 0.85:
                    understaffing_dt = int(
                        (1.0 - staffing_ratio) * 60 + RNG.normal(0, 8)
                    )
                    understaffing_dt = max(0, understaffing_dt)
                    downtime_mins += understaffing_dt
                    if downtime_reason is None and staffing_ratio < 0.75:
                        downtime_reason = "MANPOWER_SHORT"

                # Cap downtime
                downtime_mins = min(downtime_mins, planned_runtime - 30)
                downtime_mins = max(downtime_mins, 0)
                if downtime_mins == 0:
                    downtime_reason = None

                actual_runtime = planned_runtime - downtime_mins

                # ── Performance ──
                ideal_cycle_sec = product["ideal_cycle_time_sec"]
                theoretical_units = int((actual_runtime * 60) / ideal_cycle_sec)

                perf_base = cfg.PERFORMANCE_BASELINE
                perf_noise = RNG.normal(0, 0.04)
                shift_penalty = -0.02 if shift_id == 2 else 0.0
                staff_penalty = (
                    -0.08 * (1 - staffing_ratio)
                    if staffing_ratio < 0.9 else 0.0
                )
                perf_factor = np.clip(
                    perf_base + perf_noise + shift_penalty + staff_penalty,
                    0.60, 0.98
                )

                actual_units = max(1, int(theoretical_units * perf_factor))

                # ── Planned units (shift target) ──
                planned_units = int(
                    (planned_runtime * 60 / ideal_cycle_sec)
                    * cfg.PERFORMANCE_BASELINE * 1.02
                )

                # ── Overtime ──
                overtime_hours = 0.0
                if staffing_ratio < 0.90 and RNG.random() < 0.55:
                    overtime_hours = round(
                        RNG.uniform(0.5, 2.5) * (1 - staffing_ratio) * 10, 1
                    )

                records.append({
                    "prod_log_id": prod_log_id,
                    "date": d,
                    "shift_id": shift_id,
                    "line_id": line_id,
                    "sku": sku,
                    "planned_units": planned_units,
                    "actual_units": actual_units,
                    "planned_runtime_mins": planned_runtime,
                    "actual_runtime_mins": actual_runtime,
                    "downtime_mins": downtime_mins,
                    "downtime_reason": downtime_reason,
                    "ideal_cycle_time_sec": ideal_cycle_sec,
                    "planned_operators": planned_ops,
                    "actual_operators": actual_ops,
                    "overtime_hours": overtime_hours,
                })

    df = pd.DataFrame(records)
    print(f"  fact_production_log: {len(df):,} rows")
    return df


# ═══════════════════════════════════════════════════════════════
#  FACT: QC INSPECTION
# ═══════════════════════════════════════════════════════════════

def generate_fact_qc_inspection(fact_prod_df):
    """
    Two inspections per production batch:
      1) PRODUCTION_QC — after assembly
      2) PACKAGING_QC — after packaging

    Defect rate is SKU-dependent and correlated with staffing.
    """
    defect_codes = [d["code"] for d in cfg.DEFECT_REASONS]
    defect_weights = np.array([d["weight"] for d in cfg.DEFECT_REASONS])
    defect_weights /= defect_weights.sum()

    records = []
    qc_id = 0

    for _, prod in fact_prod_df.iterrows():
        batch_id = f"B-{prod['prod_log_id']:06d}"
        units_produced = prod["actual_units"]
        sku = prod["sku"]
        d = prod["date"]
        staffing_ratio = prod["actual_operators"] / prod["planned_operators"]

        # SKU-specific defect modifier
        sku_mod = cfg.SKU_DEFECT_MODIFIER.get(sku, 1.0)

        for stage in ["PRODUCTION_QC", "PACKAGING_QC"]:
            qc_id += 1

            # Packaging QC sees fewer units (some already rejected) and
            # has a lower defect rate (mostly cosmetic / packaging issues)
            if stage == "PRODUCTION_QC":
                units_inspected = units_produced
                base_defect_rate = (1 - cfg.QUALITY_BASELINE) * 0.70  # 70% of defects caught here
            else:
                # Units that passed production QC
                units_inspected = max(
                    1, units_produced - records[-1]["units_rejected"]
                )
                base_defect_rate = (1 - cfg.QUALITY_BASELINE) * 0.30  # 30% caught here

            # Adjust defect rate
            defect_rate = base_defect_rate * sku_mod
            # Understaffing increases defects (fatigue, rushing)
            if staffing_ratio < 0.85:
                defect_rate *= 1.3
            # Add noise
            defect_rate = np.clip(
                defect_rate + RNG.normal(0, 0.005),
                0.001, 0.12
            )

            units_rejected = int(np.round(units_inspected * defect_rate))
            units_rejected = min(units_rejected, units_inspected)
            units_passed = units_inspected - units_rejected

            # Pick primary defect reason
            if units_rejected > 0:
                # Packaging QC is biased toward packaging-related defects
                if stage == "PACKAGING_QC":
                    pkg_weights = defect_weights.copy()
                    pkg_idx = defect_codes.index("POOR_PACKAGING")
                    pkg_weights[pkg_idx] *= 4.0
                    dust_idx = defect_codes.index("DUST_CONTAMINATION")
                    pkg_weights[dust_idx] *= 2.0
                    pkg_weights /= pkg_weights.sum()
                    defect_reason = RNG.choice(defect_codes, p=pkg_weights)
                else:
                    defect_reason = RNG.choice(defect_codes, p=defect_weights)
            else:
                defect_reason = None

            records.append({
                "qc_id": qc_id,
                "batch_id": batch_id,
                "stage": stage,
                "sku": sku,
                "inspected_date": d,
                "units_inspected": units_inspected,
                "units_passed": units_passed,
                "units_rejected": units_rejected,
                "defect_reason": defect_reason,
            })

    df = pd.DataFrame(records)
    print(f"  fact_qc_inspection:  {len(df):,} rows")
    return df


# ═══════════════════════════════════════════════════════════════
#  FACT: SALES ORDERS
# ═══════════════════════════════════════════════════════════════

def generate_fact_sales_orders(dim_date_df):
    """
    ~150 orders/month, distributed across customers and products.
    Priority split: 70% Standard, 22% Urgent, 8% VIP.
    Lead time: Standard=14-21d, Urgent=5-10d, VIP=3-7d.
    """
    cust_ids = [c["customer_id"] for c in cfg.CUSTOMERS]
    cust_weights = np.array([c["order_weight"] for c in cfg.CUSTOMERS])
    cust_weights /= cust_weights.sum()

    skus = [p["sku"] for p in cfg.PRODUCTS]
    # Customer-product affinity — Action/Jumbo skew toward Indoor/Bulbs
    sku_weights_default = np.ones(len(skus)) / len(skus)

    priorities = list(cfg.PRIORITY_WEIGHTS.keys())
    priority_w = np.array(list(cfg.PRIORITY_WEIGHTS.values()))

    lead_time_ranges = {
        "Standard": (14, 21),
        "Urgent": (5, 10),
        "VIP": (3, 7),
    }

    # Typical order quantities by category
    qty_ranges = {
        "Indoor":     (50, 500),
        "Outdoor":    (20, 200),
        "Industrial": (10, 100),
    }

    records = []
    order_counter = 0

    # Generate month-by-month
    current = cfg.START_DATE.replace(day=1)
    end = cfg.END_DATE
    while current <= end:
        month = current.month
        year = current.year
        demand_mult = cfg.MONTHLY_DEMAND_MULTIPLIER.get(month, 1.0)
        n_orders = int(cfg.ORDERS_PER_MONTH * demand_mult + RNG.normal(0, 5))
        n_orders = max(50, n_orders)

        # Eligible order dates in this month (weekdays only)
        month_dates = dim_date_df[
            (dim_date_df["date"] >= current)
            & (dim_date_df["date"] < current + timedelta(days=32))
            & (dim_date_df["day_of_week"] < 5)  # Mon-Fri
        ]["date"].values

        if len(month_dates) == 0:
            current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
            continue

        for _ in range(n_orders):
            order_counter += 1
            order_id = f"SO-{year}-{order_counter:05d}"

            customer_id = int(RNG.choice(cust_ids, p=cust_weights))
            sku = RNG.choice(skus, p=sku_weights_default)
            product = _get_product(sku)

            priority = RNG.choice(priorities, p=priority_w)

            order_date = month_dates[int(RNG.integers(0, len(month_dates)))]
            if not isinstance(order_date, date):
                order_date = pd.Timestamp(order_date).date()

            lt_min, lt_max = lead_time_ranges[priority]
            lead_days = int(RNG.integers(lt_min, lt_max + 1))
            promised_date = order_date + timedelta(days=lead_days)

            cat = product["category"]
            q_min, q_max = qty_ranges[cat]
            qty = int(RNG.integers(q_min, q_max + 1))

            # Price = list price ± small customer-specific discount
            discount = RNG.uniform(0, 0.08) if customer_id in [5, 6] else RNG.uniform(0, 0.03)
            unit_price = round(product["unit_cost_eur"] / 0.45 * (1 - discount), 2)
            # Keep realistic — don't go below 1.5× cost
            unit_price = max(unit_price, product["unit_cost_eur"] * 1.5)
            unit_price = round(unit_price, 2)

            records.append({
                "order_id": order_id,
                "customer_id": customer_id,
                "sku": sku,
                "order_date": order_date,
                "promised_date": promised_date,
                "qty_ordered": qty,
                "unit_price_eur": unit_price,
                "priority": priority,
            })

        # Next month
        current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)

    df = pd.DataFrame(records)
    print(f"  fact_sales_orders:   {len(df):,} rows")
    return df


# ═══════════════════════════════════════════════════════════════
#  FACT: MATERIAL REQUISITIONS
# ═══════════════════════════════════════════════════════════════

def generate_fact_material_requisitions(fact_orders_df):
    """
    One MR per sales order. MR raised 1-3 days after order date.
    Fulfillment takes 10-120 minutes (store-to-floor).
    ~15% of MRs have shortage events.
    """
    records = []
    mr_counter = 0

    for _, order in fact_orders_df.iterrows():
        mr_counter += 1
        order_date = order["order_date"]
        if isinstance(order_date, np.datetime64):
            order_date = pd.Timestamp(order_date).date()

        year = order_date.year
        mr_id = f"MR-{year}-{mr_counter:05d}"

        # MR raised 1-3 business days after order
        days_to_raise = int(RNG.integers(1, 4))
        mr_raised = datetime.combine(
            order_date + timedelta(days=days_to_raise),
            datetime.min.time()
        ) + timedelta(hours=int(RNG.integers(7, 15)),
                      minutes=int(RNG.integers(0, 60)))

        # Fulfillment time
        base_minutes = int(RNG.integers(10, 45))
        has_shortage = RNG.random() < 0.15

        if has_shortage:
            # Shortage delays fulfillment significantly
            delay_minutes = int(RNG.integers(60, 480))  # 1-8 hours
            fulfill_minutes = base_minutes + delay_minutes
            shortage_qty = max(1, int(order["qty_ordered"] * RNG.uniform(0.05, 0.20)))
        else:
            fulfill_minutes = base_minutes
            shortage_qty = 0

        mr_fulfilled = mr_raised + timedelta(minutes=fulfill_minutes)

        records.append({
            "mr_id": mr_id,
            "order_id": order["order_id"],
            "sku": order["sku"],
            "mr_raised_date": mr_raised,
            "mr_fulfilled_date": mr_fulfilled,
            "shortage_flag": has_shortage,
            "shortage_qty": shortage_qty,
        })

    df = pd.DataFrame(records)
    print(f"  fact_material_req:   {len(df):,} rows")
    return df


# ═══════════════════════════════════════════════════════════════
#  FACT: DISPATCH
# ═══════════════════════════════════════════════════════════════

def generate_fact_dispatch(fact_orders_df):
    """
    One dispatch per sales order. OTD baseline ~78%.
    days_late: negative=early, 0=on-time, positive=late.
    """
    records = []
    dispatch_counter = 0

    for _, order in fact_orders_df.iterrows():
        dispatch_counter += 1
        order_id = order["order_id"]
        promised = order["promised_date"]
        if isinstance(promised, np.datetime64):
            promised = pd.Timestamp(promised).date()
        priority = order["priority"]

        # Determine if on-time
        # Priority affects OTD: VIP gets more attention
        otd_prob = cfg.OTD_BASELINE
        if priority == "VIP":
            otd_prob = min(0.95, otd_prob + 0.12)
        elif priority == "Urgent":
            otd_prob = min(0.90, otd_prob + 0.05)

        is_on_time = RNG.random() < otd_prob

        if is_on_time:
            # Delivered 0-2 days early or exactly on time
            days_offset = -int(RNG.integers(0, 3))
        else:
            # Late: 1-14 days, skewed toward 1-5
            days_offset = max(1, int(RNG.exponential(3.5) + 1))
            days_offset = min(days_offset, 21)

        dispatch_date = promised + timedelta(days=days_offset)

        # Delay reason (only if late)
        delay_reason = None
        if days_offset > 0:
            delay_reason = RNG.choice(cfg.DELAY_REASONS)

        dispatch_id = f"DSP-{dispatch_date.year}-{dispatch_counter:05d}"

        records.append({
            "dispatch_id": dispatch_id,
            "order_id": order_id,
            "dispatch_date": dispatch_date,
            "days_late": days_offset,
            "delay_reason": delay_reason,
        })

    df = pd.DataFrame(records)
    print(f"  fact_dispatch:       {len(df):,} rows")
    return df


# ═══════════════════════════════════════════════════════════════
#  FACT: SUPPLIER DELIVERY
# ═══════════════════════════════════════════════════════════════

def generate_fact_supplier_delivery(dim_date_df):
    """
    ~12 supplier deliveries per month (PCB + LED_CHIP combined).
    Models: on-time rate, lead time variance, inbound defects, qty shortfalls.
    """
    records = []
    delivery_counter = 0

    # Monthly iteration
    current = cfg.START_DATE.replace(day=1)
    end = cfg.END_DATE
    while current <= end:
        month = current.month
        year = current.year
        n_deliveries = int(cfg.SUPPLIER_DELIVERIES_PER_MONTH
                           + RNG.integers(-2, 3))
        n_deliveries = max(6, n_deliveries)

        for _ in range(n_deliveries):
            delivery_counter += 1

            # Pick supplier
            supplier = RNG.choice(cfg.SUPPLIERS)
            supplier_id = supplier["supplier_id"]
            component = supplier["component_type"]

            # PO date: random weekday in the month
            month_days = pd.date_range(
                current, current + timedelta(days=27), freq="B"
            )
            if len(month_days) == 0:
                continue
            po_idx = int(RNG.integers(0, len(month_days)))
            po_date = month_days[po_idx].date()

            # Promised date
            lead = supplier["avg_lead_time_days"]
            promised_date = po_date + timedelta(days=lead)

            # Actual arrival: on-time baseline + noise
            on_time_prob = supplier["on_time_baseline_pct"]
            is_on_time = RNG.random() < on_time_prob

            if is_on_time:
                variance_days = int(RNG.integers(-2, 1))  # early or exact
            else:
                variance_days = max(1, int(RNG.exponential(4) + 1))
                variance_days = min(variance_days, 30)

            actual_arrival = promised_date + timedelta(days=variance_days)

            # Quantity
            qty_ordered = int(RNG.integers(500, 5001))
            # Qty received: occasionally short
            if RNG.random() < 0.08:
                qty_received = int(qty_ordered * RNG.uniform(0.85, 0.98))
            else:
                qty_received = qty_ordered

            # Inbound defects
            inbound_defect_rate = RNG.uniform(0.005, 0.03)
            qty_defective = int(qty_received * inbound_defect_rate)

            # Unit cost (component level)
            if component == "PCB":
                unit_cost = round(RNG.uniform(1.20, 3.80), 2)
            else:
                unit_cost = round(RNG.uniform(0.08, 0.35), 2)

            delivery_id = f"SD-{year}-{delivery_counter:05d}"

            records.append({
                "delivery_id": delivery_id,
                "supplier_id": supplier_id,
                "component_type": component,
                "po_date": po_date,
                "promised_date": promised_date,
                "actual_arrival_date": actual_arrival,
                "qty_ordered": qty_ordered,
                "qty_received": qty_received,
                "qty_defective": qty_defective,
                "unit_cost_eur": unit_cost,
            })

        # Next month
        current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)

    df = pd.DataFrame(records)
    print(f"  fact_supplier_del:   {len(df):,} rows")
    return df


# ═══════════════════════════════════════════════════════════════
#  MAIN — ORCHESTRATE & EXPORT
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  LumenOps 360 — Data Generator")
    print(f"  Seed: {cfg.RANDOM_SEED}")
    print(f"  Range: {cfg.START_DATE} → {cfg.END_DATE}")
    print("=" * 60)

    # Resolve output directory relative to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(project_root, cfg.OUTPUT_DIR)
    os.makedirs(out_dir, exist_ok=True)

    # ── Dimensions ──────────────────────────────────────────
    print("\n▸ Generating dimension tables...")
    dim_date = generate_dim_date()
    dim_customer = generate_dim_customer()
    dim_product = generate_dim_product()
    dim_line = generate_dim_line()
    dim_shift = generate_dim_shift()
    dim_defect = generate_dim_defect_reason()
    dim_downtime = generate_dim_downtime_reason()
    dim_supplier = generate_dim_supplier()

    dims = {
        "dim_date": dim_date,
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "dim_line": dim_line,
        "dim_shift": dim_shift,
        "dim_defect_reason": dim_defect,
        "dim_downtime_reason": dim_downtime,
        "dim_supplier": dim_supplier,
    }
    for name, df in dims.items():
        path = os.path.join(out_dir, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"  {name}: {len(df):,} rows → {path}")

    # ── Facts ───────────────────────────────────────────────
    print("\n▸ Generating fact tables...")

    fact_prod = generate_fact_production_log(dim_date)
    fact_qc = generate_fact_qc_inspection(fact_prod)
    fact_orders = generate_fact_sales_orders(dim_date)
    fact_mr = generate_fact_material_requisitions(fact_orders)
    fact_dispatch = generate_fact_dispatch(fact_orders)
    fact_supplier_del = generate_fact_supplier_delivery(dim_date)

    facts = {
        "fact_production_log": fact_prod,
        "fact_qc_inspection": fact_qc,
        "fact_sales_orders": fact_orders,
        "fact_material_requisitions": fact_mr,
        "fact_dispatch": fact_dispatch,
        "fact_supplier_delivery": fact_supplier_del,
    }
    for name, df in facts.items():
        path = os.path.join(out_dir, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"  → saved {path}")

    # ── Summary ─────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  GENERATION COMPLETE")
    print("=" * 60)
    total_rows = sum(len(df) for df in {**dims, **facts}.values())
    print(f"  Total tables: {len(dims) + len(facts)}")
    print(f"  Total rows:   {total_rows:,}")
    print(f"  Output dir:   {out_dir}")

    # ── Quick KPI sanity check ──────────────────────────────
    print("\n▸ Sanity check (baseline KPIs)...")

    # OEE components
    avail = fact_prod["actual_runtime_mins"] / fact_prod["planned_runtime_mins"]
    perf = (fact_prod["actual_units"] * fact_prod["ideal_cycle_time_sec"]) / (
        fact_prod["actual_runtime_mins"] * 60
    )
    perf = perf.clip(upper=1.0)

    # Quality from QC
    prod_qc = fact_qc[fact_qc["stage"] == "PRODUCTION_QC"]
    quality_rate = prod_qc["units_passed"].sum() / prod_qc["units_inspected"].sum()

    avg_avail = avail.mean()
    avg_perf = perf.mean()
    avg_oee = avg_avail * avg_perf * quality_rate

    # OTD
    otd_rate = (fact_dispatch["days_late"] <= 0).mean()

    # Staffing fill rate
    sfr = (fact_prod["actual_operators"] / fact_prod["planned_operators"]).mean()

    # Defect rate
    total_inspected = fact_qc["units_inspected"].sum()
    total_rejected = fact_qc["units_rejected"].sum()
    defect_rate = total_rejected / total_inspected

    print(f"  Avg Availability:     {avg_avail:.1%}")
    print(f"  Avg Performance:      {avg_perf:.1%}")
    print(f"  Avg Quality (FPY):    {quality_rate:.1%}")
    print(f"  Avg OEE:              {avg_oee:.1%}")
    print(f"  OTD Rate:             {otd_rate:.1%}")
    print(f"  Staffing Fill Rate:   {sfr:.1%}")
    print(f"  Overall Defect Rate:  {defect_rate:.1%}")

    targets = {
        "OEE": (avg_oee, 0.55, 0.72),
        "OTD": (otd_rate, 0.70, 0.85),
        "FPY": (quality_rate, 0.93, 0.98),
        "Staffing Fill Rate": (sfr, 0.80, 0.95),
    }
    print("\n  Baseline validation:")
    all_ok = True
    for kpi, (val, lo, hi) in targets.items():
        status = "✓" if lo <= val <= hi else "✗ OUT OF RANGE"
        if status != "✓":
            all_ok = False
        print(f"    {kpi:25s} {val:.1%}  [{lo:.0%}–{hi:.0%}]  {status}")

    if all_ok:
        print("\n  ✅ All baselines within expected ranges.")
    else:
        print("\n  ⚠️  Some baselines outside range — review config.py.")

    print("\n  Done. Ready for: python src/load_to_duckdb.py")


if __name__ == "__main__":
    main()
