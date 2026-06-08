# Methodology — LumenOps 360

**How operational management frameworks were applied in this project — grounded in actual data findings, not textbook theory.**

---

## DMAIC — The Analytical Spine

The entire project follows the Six Sigma DMAIC cycle. Each phase maps to a concrete deliverable.

### Define

The problem statement was built from five real shop-floor pain points experienced in LED lighting manufacturing, then validated against Signify's 2024 Annual Report and CEO disclosures. The fictional company (LumenTech BV, Eindhoven) operates in the same industry, geography, and operational context as the target employers.

**Deliverables:** Project blueprint (v1.3), business context documentation, SIPOC mapping (Suppliers → Inputs → Process → Outputs → Customers).

### Measure

Baseline KPIs were established from 18 months of simulated production data (Jan 2023 – Jun 2024) across 3 assembly lines, 2 shifts, and 9 product SKUs.

| KPI | Baseline | Target | Gap |
|---|---|---|---|
| OEE | 68.20% | 85.00% | −16.80 pp |
| First Pass Yield | 96.65% | 97.00% | −0.35 pp |
| On-Time Delivery | 80.6% | 95.00% | −14.40 pp |
| Staffing Fill Rate | 83.1% | 95.00% | −11.90 pp |

**Deliverables:** Data generation pipeline (seeded, reproducible), DuckDB warehouse, dbt staging models, Notebook 1 (EDA).

### Analyze

Three analytical layers were applied to identify root causes:

**Exploratory Data Analysis (Notebook 1):** Downtime Pareto, defect distribution, staffing-OEE correlation, delivery performance profiling.

**Statistical Process Control (Notebook 2):** p-charts and np-charts for defect rate, X-bar and R charts for OEE, Individual-Moving Range charts, Western Electric rules analysis. Key finding: the defect rate process is not in statistical control — 73 out-of-control days detected, 49.4% of days violating at least one Western Electric rule. Process capability Cpk = 0.669, meaning the process cannot reliably meet the 97% FPY target.

**Hypothesis Testing (Notebook 3):** Five formal tests, all significant at α = 0.05:

| Hypothesis | Effect Size | Practical Impact |
|---|---|---|
| H2: Changeover → lower OEE | r = 0.571 (large) | 8.56 pp, €42,348/month |
| H1: Low staffing → lower OEE | r = 0.231 (small–medium) | 3.33 pp, €16,490/month |
| H4: Evening shift → lower OEE | r = 0.107 (small) | 1.55 pp, €7,695/month |
| H3: Line 2 & 3 underperform Line 1 | H = 33.94 | 2.13 pp (L1 vs L3) |
| H5: Outdoor defect rate higher | V = 0.020 (negligible) | 2.86% vs 2.04% |

**Deliverables:** Notebooks 1–3, Fishbone diagram, 5 Whys case study.

### Improve

Improvement opportunities were quantified in euros — the language of plant leadership:

**Schedule freeze policy (48hr advance lock):** Reducing changeover-driven OEE loss. Changeover shifts lose 8.56 pp OEE — the largest single effect identified. Estimated recovery: €42,348/month.

**Workforce optimization:** Closing the staffing fill rate gap from 83% to 95% would recover 3.33 pp OEE (€16,490/month) and reduce overtime costs. Contextualized against the Dutch labor shortage — 97 vacancies per 100 unemployed (DNB 2025).

**Evening shift protocol:** Pre-shift material staging and supervision handover could close part of the 1.55 pp evening shift gap (€7,695/month).

**Combined addressable opportunity:** ~€66,500/month → ~€798K/year.

**Deliverables:** Power BI Pages 5–6 (scenario modeling), strategic recommendations in dashboard insights.

### Control

The control phase is implemented at two levels:

**Data layer:** 61 dbt tests enforce data quality constraints — accepted values for reason codes, referential integrity, not-null checks, and expression-based guards (e.g., actual_operators ≤ planned_operators × 1.5). These run on every `dbt test` execution.

**Monitoring layer:** SPC control charts in Notebook 2 provide the statistical monitoring framework. The p-chart with UCL/LCL at ±3σ would be deployed as a recurring report in a production environment, triggering investigation when the process goes out of control.

**Deliverables:** dbt schema.yml (61 tests), Notebook 2 (SPC charts).

---

## TPM & OEE — The Six Big Losses

Total Productive Maintenance classifies all capacity loss into six categories. The OEE decomposition in `int_oee_daily` maps directly to this framework:

| Loss Category | OEE Factor | LumenOps 360 Evidence |
|---|---|---|
| Breakdowns | Availability | MACHINE_FAULT downtime reason |
| Setup / Changeover | Availability | CHANGEOVER — #1 downtime driver, 8.56 pp OEE impact |
| Idling / Minor Stops | Performance | MANPOWER_SHORT, MATERIAL_SHORTAGE_INTERNAL |
| Reduced Speed | Performance | Performance factor < 1.0 in production log |
| Startup Rejects | Quality | First-batch defects after changeover |
| Production Rejects | Quality | In-line defects — FPY 96.65% baseline |

The OEE waterfall on Page 3 of the dashboard visualizes these losses from 100% planned capacity down to the actual 68.20% OEE.

---

## Theory of Constraints (TOC)

Eli Goldratt's principle: the throughput of any system is limited by its bottleneck.

**Applied finding:** Kruskal-Wallis test (H = 33.94, p < 0.0001) confirmed that assembly line OEE differs significantly across lines. Pairwise comparison revealed that Lines 2 and 3 are jointly the capacity constraint (67.86% and 67.31% OEE respectively), while Line 1 operates at 69.44%.

**The five focusing steps applied:**

1. **Identify** the constraint → Lines 2 & 3 (Page 3 OEE by line chart)
2. **Exploit** the constraint → Maximize uptime on Lines 2–3 by prioritizing changeover reduction and staffing fill on these lines first
3. **Subordinate** everything else → Schedule decisions should protect Lines 2–3 throughput, even if Line 1 runs below full utilization
4. **Elevate** the constraint → Capital investment, automation, or line rebalancing (Page 6 scenario modeling)
5. **Repeat** → After improvement, re-measure to see if the constraint has shifted

**Key insight:** An hour lost at Lines 2–3 is an hour lost for the entire plant. An hour saved at Line 1 produces no additional throughput — it just creates WIP inventory.

---

## Lean Manufacturing — TIMWOODS

The 8 Lean Wastes provide the diagnostic vocabulary for identifying where value is lost. Each waste is mapped to data the project surfaces:

| Waste | LumenOps 360 Evidence |
|---|---|
| **T — Transportation** | Material movement time captured in MR fulfillment lead time |
| **I — Inventory** | WIP accumulation visible in production-to-dispatch lag |
| **M — Motion** | Operator movement — noted qualitatively; staffing fill rate as proxy |
| **W — Waiting** | Downtime from MATERIAL_SHORTAGE_INTERNAL, PCB_SHORTAGE_SUPPLIER, MANPOWER_SHORT |
| **O — Overproduction** | Schedule adherence > 105% indicates overproduction |
| **O — Over-processing** | Rework cycles — units failing QC and re-entering production |
| **D — Defects** | FPY 96.65%, defect Pareto, COPQ in € |
| **S — Skills (unused talent)** | Understaffing forces remaining operators into narrow tasks — addressed in recommendations |

The Waiting waste is the most directly quantified: CHANGEOVER, MANPOWER_SHORT, and MATERIAL_SHORTAGE together account for the majority of named downtime minutes.

---

## Statistical Process Control (SPC)

SPC provides the mathematical framework for distinguishing between common-cause variation (inherent to the process) and special-cause variation (assignable, fixable).

**Charts implemented in Notebook 2:**

| Chart Type | Application | Key Finding |
|---|---|---|
| p-chart | Defect rate (proportion defective) | 73 out-of-control days — process not stable |
| np-chart | Defect count (absolute) | Confirms p-chart findings at count level |
| X-bar and R | OEE subgroup means and range | OEE process is in statistical control but centered far below 85% target |
| I-MR | Individual defect rate observations | Confirms special-cause signals in quality process |

**Western Electric rules applied:**
- Rule 1: Point beyond 3σ — 10 violations
- Rule 2: 2 of 3 beyond 2σ — 82 violations
- Rule 3: 4 of 5 beyond 1σ — 103 violations
- Rule 4: 8 consecutive on same side of center — 84 violations

49.4% of production days violate at least one rule — confirming that the quality process requires intervention, not just monitoring.

**Process capability:** Cp = 0.815, Cpk = 0.669, corresponding to 2.01σ. The process cannot reliably meet the 97% FPY target. Improvement must shift the process mean (increase Cpk) and reduce variation (increase Cp).

---

## Root Cause Analysis Toolkit

### Pareto Analysis (80/20 Rule)

Applied to both downtime reasons and defect types across the EDA and dashboard:

**Downtime:** CHANGEOVER and MANPOWER_SHORT together account for the majority of named downtime minutes — confirming these as the vital few.

**Defects:** Analyzed by product category (H5) — Outdoor products carry 40% higher defect rate (2.86%) than Indoor (2.04%) and Industrial (1.98%).

### Fishbone Diagram (Ishikawa)

A full 6M root cause analysis was conducted for the top operational issue — documented in `fishbone_housing_damage.md`.

### 5 Whys

A structured root cause trace was conducted for chronic OTD failure — documented in `case_study_5_whys.md`.

---

## Framework Integration

These frameworks are not applied in isolation. They form an integrated analytical system:

DMAIC provides the project structure
└── Measure phase uses TPM/OEE decomposition
└── Analyze phase uses:
├── Lean/TIMWOODS for waste identification
├── TOC for bottleneck identification
├── SPC for process stability assessment
├── Pareto for vital-few prioritization
├── Fishbone for root cause mapping
└── 5 Whys for causal chain tracing
└── Control phase uses:
├── dbt tests for data quality enforcement
└── SPC charts for ongoing monitoring

Every framework connects to a specific dashboard page, a specific dbt model, or a specific notebook cell. Nothing is included for decoration — each framework earns its place by producing a quantified, actionable insight.

---

*Document generated as part of LumenOps 360 — Manufacturing Operations Intelligence.*
*All findings reference validated data from 18 months of simulated operations (Jan 2023 – Jun 2024).*