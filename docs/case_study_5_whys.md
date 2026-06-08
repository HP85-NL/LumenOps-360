# 5 Whys Case Study — Why Are Customer Orders Late?

**Context:** On-Time Delivery at LumenTech BV is 80.6% — meaning roughly 1 in 5 orders arrives late. This 5 Whys analysis traces the causal chain from the customer-facing symptom back to the operational root causes, using data findings from the EDA, SPC, and Hypothesis Testing notebooks.

---

## The Problem Statement

> *"LumenTech BV's OTD rate is 80.6% against a 95% target. Customer satisfaction scores are declining, and key accounts (Gamma, Hornbach, Praxis) have escalated delivery complaints."*

---

## The 5 Whys Trace

### Why #1: Why are customer orders late?

**Because production does not complete the required quantity by the promised dispatch date.** The order-to-dispatch pipeline has multiple stages (order intake → material requisition → production → QC → packaging → dispatch), and delays accumulate across stages. The schedule adherence gap between planned and actual output means the pipeline runs behind.

**Data evidence:** OTD baseline is 80.6%. Schedule adherence varies significantly by line and shift — Line 1 outperforms Lines 2 and 3 (H3: p < 0.0001).

---

### Why #2: Why does production not complete on time?

**Because OEE is 68.20% — far below the 85% world-class target.** This means 32% of planned production capacity is lost to a combination of downtime, speed losses, and quality failures. The plant cannot produce enough good units in the scheduled time.

**Data evidence:** OEE baseline 68.20%. The gap to 85% represents ~17 percentage points of lost capacity. Lines 2 and 3 are jointly the bottleneck at 67.31–67.86% OEE versus Line 1 at 69.44%.

---

### Why #3: Why is OEE only 68%?

**Because changeover losses and staffing shortages are consuming available capacity.** Two root causes dominate:

1. **Changeover (8.56 pp OEE loss):** When the line switches SKUs, setup time, line purging, and first-article inspection consume production hours. Changeover shifts run at 60.98% OEE versus 69.54% for non-changeover shifts — the largest single effect found in hypothesis testing (H2: r = 0.571, large effect).

2. **Staffing shortages (3.33 pp OEE loss):** Shifts with < 90% staffing fill rate run at 67.85% OEE versus 71.18% for fully staffed shifts (H1: r = 0.231). With a plant-wide fill rate of only 83.1%, understaffing is structural, not occasional.

**Data evidence:** H2 (changeover): €42,348/month impact. H1 (staffing): €16,490/month impact. Combined: €58,838/month in addressable OEE loss.

---

### Why #4: Why are there so many changeovers and staffing gaps?

**Changeovers are driven by schedule volatility — management changes the production plan mid-week to accommodate urgent customer orders or shifting priorities.** Each plan change forces a SKU transition, incurring changeover time. The more frequently the plan changes, the more production hours are lost to setup rather than making products.

**Staffing gaps are structural — the Dutch labor market has 97 vacancies per 100 unemployed (DNB 2025).** Technicians and production operators are among the most acute shortage categories. LumenTech BV cannot reliably fill all planned operator positions, especially on evening shifts (H4: evening shift runs 1.55 pp lower OEE, p < 0.0001).

**Data evidence:** CHANGEOVER is the #1 downtime reason in the Pareto analysis. MANPOWER_SHORT is #2. Evening shift penalty confirmed at €7,695/month.

---

### Why #5: Why is the schedule volatile and the labor market tight?

**Schedule volatility exists because there is no formal schedule freeze policy.** Production plans can be changed at any time, by anyone with authority, without a structured cost-benefit assessment. The absence of a change-control mechanism means every urgent request translates directly into a changeover event.

**The labor shortage is a macro-economic constraint outside LumenTech BV's direct control**, but its impact can be mitigated through retention programs, temp-agency partnerships, automation of manual handling tasks, and cross-training to increase workforce flexibility.

---

## Root Cause Summary

```text
SYMPTOM:  Orders arrive late (OTD 80.6%)
     │
WHY 1:    Production doesn't finish on time
     │
WHY 2:    OEE is only 68% (32% capacity lost)
     │
WHY 3:    Changeover losses (8.56 pp) + staffing gaps (3.33 pp)
     │
WHY 4:    No schedule freeze policy + Dutch labor shortage
     │
WHY 5:    Absence of change-control governance (addressable)
          + macro labor market constraint (mitigable)
```

---

## Recommended Actions

| # | Action | Root Cause Addressed | Expected Impact | Timeframe |
|---|---|---|---|---|
| 1 | **Implement 48-hour schedule freeze policy** | Schedule volatility → changeover | Reduce changeover frequency → recover up to 8.56 pp OEE (€42,348/month) | 0–3 months |
| 2 | **Prioritize staffing fill on Lines 2–3** | Understaffing at bottleneck | Lines 2–3 are the constraint (TOC) — every operator-hour recovered here directly increases plant throughput | 0–3 months |
| 3 | **Establish temp-agency framework agreement** | Staffing fill rate < 83% | Improve fill rate toward 95% target → recover up to 3.33 pp OEE (€16,490/month) | 1–3 months |
| 4 | **Standardize changeover procedure (SMED)** | Changeover duration | Reduce per-changeover time even when changeovers are necessary. Single Minute Exchange of Die (SMED) methodology targets 50% reduction in setup time | 3–6 months |
| 5 | **Cross-train operators across product categories** | Workforce inflexibility | Reduce the impact of individual absences. Operators certified on both Indoor and Outdoor products provide scheduling flexibility | 3–6 months |
| 6 | **Pre-shift material staging for evening shift** | Evening shift OEE penalty | Ensure materials are staged before shift handover to eliminate waiting waste at shift start (€7,695/month) | 0–1 month |

---

## Combined Opportunity

| Source | OEE Recovery | Monthly € Impact |
|---|---|---|
| Schedule freeze (changeover reduction) | Up to 8.56 pp | €42,348 |
| Staffing fill improvement | Up to 3.33 pp | €16,490 |
| Evening shift protocol | Up to 1.55 pp | €7,695 |
| **Total addressable** | **~13.4 pp** | **~€66,500/month → ~€798K/year** |

---

## Connection to Project Deliverables

- **Dashboard Page 2:** OTD funnel and delay-reason Pareto visualize the symptom (Why #1)
- **Dashboard Page 3:** OEE decomposition and staffing analysis visualize Why #2 and #3
- **Dashboard Page 6:** Schedule volatility trend and scenario modeling address Why #4 and #5
- **Notebook 3 (Hypothesis Testing):** H1, H2, H4 formally confirm the causal chain with statistical evidence
- **Fishbone (fishbone_housing_damage.md):** Complements this analysis for quality-specific root causes

---

*Document generated as part of LumenOps 360 — Manufacturing Operations Intelligence.*
*The 5 Whys trace follows actual data findings — every claim is backed by a specific notebook result or dashboard page.*