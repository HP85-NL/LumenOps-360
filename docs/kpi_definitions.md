# KPI Definitions — LumenOps 360

**Reference document for all Key Performance Indicators used across the Power BI dashboard, dbt models, and Jupyter notebooks.**

---

## OEE — Overall Equipment Effectiveness

| Attribute | Detail |
|---|---|
| **Formula** | Availability × Performance × Quality |
| **Target** | ≥ 85% (world-class benchmark) |
| **Baseline** | 68.20% |
| **Source model** | `int_oee_daily` |
| **Business meaning** | The single most important metric for measuring how effectively a production line converts scheduled time into good output. A 68% OEE means 32% of planned capacity is lost to downtime, speed loss, or defects. |

### OEE Components

**Availability**
| Attribute | Detail |
|---|---|
| **Formula** | Actual Runtime Minutes / Planned Runtime Minutes |
| **Target** | ≥ 90% |
| **Business meaning** | Percentage of scheduled production time the line was actually running. Losses come from breakdowns, changeovers, material shortages, and management-driven schedule changes. |

**Performance**
| Attribute | Detail |
|---|---|
| **Formula** | (Ideal Cycle Time × Actual Units) / Actual Runtime Minutes |
| **Target** | ≥ 95% |
| **Business meaning** | Speed efficiency — how close the line runs to its engineering-rated cycle time. Losses come from micro-stoppages, reduced speed, operator inexperience, and line imbalance. |

**Quality (First Pass Yield)**
| Attribute | Detail |
|---|---|
| **Formula** | Units Passed / Units Inspected |
| **Target** | ≥ 97% (internal), ≥ 99% (world-class) |
| **Baseline** | 96.65% |
| **Source model** | `int_oee_daily` (quality component), `int_fpy_by_batch` |
| **Business meaning** | Percentage of units that pass QC on the first attempt without rework or rejection. Below 97% signals systematic quality issues requiring root cause investigation. |

---

## Delivery Performance

**OTD — On-Time Delivery Rate**
| Attribute | Detail |
|---|---|
| **Formula** | Orders delivered on or before promised date / Total dispatched orders |
| **Target** | ≥ 95% |
| **Baseline** | ~80.6% |
| **Source model** | `int_otd_by_order`, `mart_schedule_adherence` |
| **Business meaning** | The customer-facing reliability metric. An 80.6% OTD means roughly 1 in 5 orders arrives late — a direct driver of customer dissatisfaction and NPS erosion. |

**Schedule Adherence**
| Attribute | Detail |
|---|---|
| **Formula** | Actual Units Produced / Planned Units |
| **Target** | 95–105% band |
| **Business meaning** | Measures plan fidelity. Below 95% = underproduction (capacity loss). Above 105% = overproduction (inventory waste). Both indicate planning or execution problems. |

**Days Late**
| Attribute | Detail |
|---|---|
| **Formula** | Dispatch Date − Promised Date |
| **Interpretation** | Negative = early, 0 = on-time, positive = late |
| **Business meaning** | The granularity behind OTD — quantifies how late orders are, not just whether they were late. A 2-day average delay has very different implications than a 14-day average. |

---

## Workforce Metrics

**Staffing Fill Rate**
| Attribute | Detail |
|---|---|
| **Formula** | Actual Operators / Planned Operators per shift |
| **Target** | ≥ 95% |
| **Baseline** | ~83.1% |
| **Source model** | `int_oee_daily`, `int_staffing_impact` |
| **Business meaning** | Workforce availability signal. In the Dutch labor market (97 vacancies per 100 unemployed — DNB 2025), chronic understaffing is structural, not occasional. An 83% fill rate means shifts routinely run with 1–2 fewer operators than planned. |

**Understaffing OEE Penalty**
| Attribute | Detail |
|---|---|
| **Formula** | Mean OEE at fill rate ≥ 95% − Mean OEE at fill rate < 90% |
| **Validated gap** | 3.33 percentage points (p < 0.0001, r = 0.231) |
| **Est. monthly impact** | €16,490 |
| **Business meaning** | Quantifies the hidden cost of running understaffed. Statistically confirmed in Notebook 3 (H1). This is the number that justifies retention investment, temp-agency contracts, or automation business cases. |

**Overtime Cost per Unit**
| Attribute | Detail |
|---|---|
| **Formula** | Total overtime € / Units produced on overtime shifts |
| **Target** | Minimize |
| **Business meaning** | Hidden cost of understaffing — when too few operators are available, overtime compensates but at premium cost and reduced efficiency. |

---

## Quality Metrics

**FPY — First Pass Yield**
| Attribute | Detail |
|---|---|
| **Formula** | Units Passed / Units Inspected (first inspection only) |
| **Target** | ≥ 97% |
| **Baseline** | 96.65% |
| **Business meaning** | The primary quality KPI. Below target at baseline, confirmed by SPC analysis (Notebook 2) as not in statistical control — 73 out-of-control days detected. Process capability Cpk = 0.669, meaning the process cannot reliably meet the 97% target. |

**Defect Rate**
| Attribute | Detail |
|---|---|
| **Formula** | Units Rejected / Units Inspected |
| **Target** | ≤ 1% |
| **Business meaning** | Overall quality signal. Analyzed by product category in Notebook 3 (H5): Outdoor products run 40% higher defect rate (2.86%) than Indoor (2.04%) and Industrial (1.98%). |

**COPQ — Cost of Poor Quality**
| Attribute | Detail |
|---|---|
| **Formula** | Scrap Cost + Rework Cost + Warranty Cost + Downtime Cost from Defects |
| **Target** | Minimize |
| **Source model** | `int_copq_monthly`, `mart_quality_fpy` |
| **Business meaning** | Translates quality failures into € — the language plant directors respond to. Includes both visible costs (scrap, rework) and hidden costs (line stoppages triggered by quality holds). |

---

## Supply Chain Metrics

**Supplier On-Time Rate**
| Attribute | Detail |
|---|---|
| **Formula** | Supplier deliveries on or before promised date / Total deliveries |
| **Target** | ≥ 95% |
| **Source model** | `int_supplier_reliability`, `mart_material_supplier` |
| **Business meaning** | Inbound supply reliability. Critical for PCB and LED chip suppliers where LumenTech BV has single-source dependency. |

**Supplier Lead Time Variance**
| Attribute | Detail |
|---|---|
| **Formula** | Standard deviation of (Actual Arrival Date − Promised Date) |
| **Target** | < 2 days |
| **Business meaning** | Measures supplier predictability. High variance forces larger safety stock buffers, increasing working capital. |

**Single-Source Exposure %**
| Attribute | Detail |
|---|---|
| **Formula** | Revenue from SKUs dependent on a single supplier / Total revenue |
| **Target** | < 30% |
| **Business meaning** | Supply chain concentration risk. Mirrors the vulnerability Signify's CEO cited when 3% of quarterly sales slipped due to component shortages from concentrated supplier bases. |

**Revenue at Risk from Supply Disruption**
| Attribute | Detail |
|---|---|
| **Formula** | Sum of order value for SKUs in stockout-risk state |
| **Target** | Minimize |
| **Business meaning** | € exposure if a key supplier fails to deliver. Used in scenario modeling on Page 6 of the dashboard. |

**Tariff Exposure**
| Attribute | Detail |
|---|---|
| **Formula** | Weighted average tariff rate on inbound components |
| **Application** | Scenario-based modeling |
| **Business meaning** | Geopolitical cost sensitivity. Models the impact of tariff changes on landed component cost — directly relevant given 2025 tariff shifts affecting Chinese and Mexican imports to EU/US markets. |

---

## Production Efficiency Metrics

**MR Fulfillment Lead Time**
| Attribute | Detail |
|---|---|
| **Formula** | Material Requisition Fulfilled Date − MR Raised Date |
| **Target** | < 30 minutes |
| **Business meaning** | Store-to-floor responsiveness. Slow MR fulfillment causes production line waiting — one of the 8 Lean wastes (TIMWOODS). |

**Yield-Adjusted BOM Factor**
| Attribute | Detail |
|---|---|
| **Formula** | 1 / (1 − Historical Defect Rate) |
| **Application** | SKU-specific |
| **Business meaning** | The material buffer needed to account for expected QC rejections. If a SKU has 4% defect rate, you need 1.042× raw material — not 1.00×. Failure to apply this factor is the root cause of "last-minute material shortages" cited in Pain Point #2. |

**Changeover Impact**
| Attribute | Detail |
|---|---|
| **Validated gap** | 8.56 OEE percentage points (p < 0.0001, r = 0.571) |
| **Est. monthly impact** | €42,348 |
| **Business meaning** | The single largest OEE driver identified in this analysis. Changeover shifts lose ~8.6 pp OEE vs non-changeover shifts. Confirmed in Notebook 3 (H2) as a large effect. Justifies schedule freeze policy (48hr advance lock) as the highest-ROI operational improvement. |

**Bottleneck Utilization (TOC)**
| Attribute | Detail |
|---|---|
| **Formula** | Bottleneck Line Run Time / Available Time |
| **Target** | ≥ 85% at constraint |
| **Finding** | Lines 2 & 3 are jointly the capacity constraint. Line 1 outperforms both (69.44% vs 67.31–67.86%). Confirmed in Notebook 3 (H3). |
| **Business meaning** | Per Theory of Constraints, an hour lost at the bottleneck is an hour lost for the entire plant. An hour saved at a non-bottleneck is a mirage. |

---

*Document generated as part of LumenOps 360 — Manufacturing Operations Intelligence.*
*All baselines validated against 18 months of simulated data (Jan 2023 – Jun 2024).*
*Statistical claims reference Notebook 3 (Hypothesis Testing) results.*
