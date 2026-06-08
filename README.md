# LumenOps 360 — Manufacturing Operations Intelligence

**An end-to-end operations analytics solution for a mid-size LED lighting manufacturer, built to quantify where time, material, and money are lost on the shop floor.**

> *Every insight is quantified in euros — the language of plant directors and operations leaders.*

---

## The Business Problem

LumenTech BV is a fictional Dutch OEM LED manufacturer based in Eindhoven, supplying private-label fixtures to retailers like Gamma, Hornbach, Praxis, and Action. The plant runs three assembly lines across two shifts — and the operations team is firefighting daily:

- Customer orders are chronically overdue (On-Time Delivery: **80.6%** vs. 95% target)
- OEE sits at **68.2%**, well below the 85% world-class benchmark — not because machines break, but because of changeovers, understaffing, and schedule volatility
- Quality escapes cost money that nobody is tracking (First Pass Yield: **96.7%**, with Outdoor products consistently worse)
- Shifts routinely run below planned staffing (**83.1% fill rate**), and nobody has quantified what that costs
- Monthly reviews rely on disconnected Excel exports — leadership has no unified view

These are not hypothetical problems. They map directly to pain points that **Signify** (ex-Philips Lighting) disclosed in its 2024 Annual Report and Q4 earnings call: Order & Delivery NPS dips, a €200M+ operational efficiency program, 5,160 FTE reductions amid the tightest labor market in Dutch history (97 vacancies per 100 unemployed), and supply chain fragility that pushed 3% of quarterly sales into the next quarter.

**This project models those exact problems at plant scale and quantifies the improvement opportunity: ~€66,500/month (~€798K/year).**

---

## What This Project Delivers

### Six-Page Power BI Dashboard

| Page | Business Question | Key Insight |
|------|-------------------|-------------|
| **Executive Overview** | How is the plant performing at a glance? | OEE 68.2%, OTD 80.6%, FPY 96.7% — all below target with clear improvement levers |
| **Schedule Adherence & OTD** | Where in the order-to-cash flow are we losing time? | Delay-reason Pareto reveals production scheduling as the dominant bottleneck, not logistics |
| **OEE & Workforce Impact** | Which line is our constraint, and what does understaffing cost? | Lines 2 and 3 are jointly the bottleneck; understaffed shifts lose 3.33 OEE percentage points (€16,490/month) |
| **Quality & First Pass Yield** | Which defects cost the most, and is the process stable? | SPC analysis shows the defect rate process is NOT in statistical control (73 out-of-control days, Cpk = 0.669) |
| **Material & Supplier Risk** | Where is our supply chain most fragile? | Single-source dependency on PCB and LED chip suppliers; lead time variance quantified |
| **Strategic Scenarios** | What are the top three operational moves? | Schedule freeze, staffing optimization, and changeover reduction — combined €66.5K/month opportunity |

### Three Jupyter Notebooks — Statistical Evidence

| Notebook | Purpose | Key Finding |
|----------|---------|-------------|
| **01 — Exploratory Data Analysis** | Profile all tables, validate baselines, surface patterns | 38 cells covering data inventory, downtime Pareto, staffing correlation, monthly trends |
| **02 — SPC Control Charts** | Is the manufacturing process in statistical control? | Defect rate: NOT in control (Western Electric violations on 49.4% of days). OEE: in control but stably mediocre at 68.3% |
| **03 — Hypothesis Testing** | Prove causal relationships with statistical rigor | 5 hypotheses tested (Mann-Whitney U, Kruskal-Wallis, Chi-Square) — changeover effect is the largest (8.56 OEE pp, r = 0.571, €42,348/month) |

### Framework Documentation

| Document | Framework |
|----------|-----------|
| `kpi_definitions.md` | All KPI formulas with validated baselines and business meaning |
| `methodology.md` | DMAIC, TPM/OEE, Theory of Constraints, Lean/TIMWOODS, SPC — as applied in this project |
| `fishbone_housing_damage.md` | 6M Ishikawa root cause analysis for Outdoor product defects |
| `case_study_5_whys.md` | Causal trace: 80.6% OTD → changeover losses → absence of schedule freeze governance |

---

## The Improvement Opportunity

All five hypotheses in Notebook 3 were rejected at α = 0.05. The combined addressable opportunity:

| Root Cause | OEE Recovery | Monthly € Impact | Method |
|------------|-------------|-------------------|--------|
| Schedule freeze (changeover reduction) | Up to 8.56 pp | €42,348 | Mann-Whitney U, r = 0.571 |
| Staffing fill improvement (85% → 95%) | Up to 3.33 pp | €16,490 | Mann-Whitney U, r = 0.231 |
| Evening shift protocol standardization | Up to 1.55 pp | €7,695 | Mann-Whitney U, r = 0.107 |
| **Total addressable** | **~13.4 pp** | **~€66,500/month → ~€798K/year** |

The largest single lever is **changeover reduction** — shifts with a changeover event lose 8.56 OEE percentage points compared to stable-run shifts. This is a scheduling governance problem, not an equipment problem, and maps directly to SMED (Single Minute Exchange of Die) methodology.

---

## Operational Management Frameworks

This project is not just a dashboard. It applies six established operations frameworks, each mapped to specific deliverables:

| Framework | Application in This Project |
|-----------|----------------------------|
| **Six Sigma (DMAIC)** | Entire project structure follows Define → Measure → Analyze → Improve → Control. dbt tests enforce the Control phase at the data layer |
| **TPM / Six Big Losses** | OEE decomposed into Availability × Performance × Quality on Dashboard Page 3. Six Big Losses quantified in euros |
| **Theory of Constraints** | Line-wise OEE comparison identifies Lines 2 and 3 as the joint constraint — not Line 3 alone, as initially assumed |
| **Lean (TIMWOODS)** | Eight wastes mapped across all dashboard pages: Waiting (OTD delays), Defects (FPY/COPQ), Inventory (material shortages) |
| **SPC (Shewhart)** | p-chart, X-bar/R, I-MR charts in Notebook 2. Western Electric rules applied. Process capability (Cp/Cpk) calculated |
| **Root Cause Analysis** | Pareto (Pages 3, 4), Fishbone/Ishikawa (docs), 5 Whys (docs) — all grounded in actual data findings |

---

## Industry Context — Why This Matters Now

The pain points modeled in this project are not academic. They reflect structural challenges facing Dutch manufacturing today:

- **Labor shortage:** The Netherlands has 97 job openings per 100 unemployed (DNB 2025). Over 76% of the working-age population is already employed — a national record. This project quantifies the OEE cost of running understaffed
- **Operational efficiency pressure:** Signify launched a €200M+ annual cost-saving reorganization, cutting ~2,700 FTE since 2023 with two-thirds of savings targeted from operational efficiency improvements
- **Supply chain fragility:** Signify's CEO disclosed that component shortages pushed 3% of quarterly revenue into the next quarter. This project models single-supplier dependency and lead time variance
- **Asset-light manufacturing:** Signify is consolidating from 41 global plants toward a leaner footprint. Dashboard Page 6 models the line consolidation scenario

Sources: Signify 2024 Annual Report, Q4 2024 Earnings Call, OECD Economic Surveys: Netherlands 2025, DNB Spring Projections 2025.

---

## Tech Stack & Architecture

### Data Flow

```
Python Generator (seed=42, reproducible)
        │
        ▼
  14 CSV files (~16,400 rows)
        │
        ▼
  DuckDB (lumenops.duckdb)
        │
        ▼
  dbt (27 models, 61 tests)
  staging → intermediate → marts
        │
        ▼
  ┌─────────────┬──────────────┐
  │  Power BI   │   Jupyter    │
  │  (6 pages)  │ (3 notebooks)│
  └─────────────┴──────────────┘
```

### Stack

| Layer | Tool | Detail |
|-------|------|--------|
| Data Generation | Python (pandas, numpy, faker) | Seeded (42), 14 tables, 18 months of daily data (Jan 2023 – Jun 2024) |
| Storage | DuckDB | Zero-infrastructure, file-based analytical database |
| Transformation | dbt (dbt-duckdb) | 27 models across staging/intermediate/marts, 61 passing tests |
| Visualization | Power BI Desktop | 6 dashboard pages, custom JSON theme, ODBC connection to DuckDB |
| Analysis | Jupyter (scipy, statsmodels, matplotlib) | EDA, SPC control charts, hypothesis testing |

### dbt Model Architecture

```
models/
├── staging/          Raw → clean, renamed, typed (14 models)
├── intermediate/     Business logic + KPI calculations (7 models)
│   ├── int_oee_daily.sql
│   ├── int_fpy_by_batch.sql
│   ├── int_otd_by_order.sql
│   ├── int_copq_monthly.sql
│   ├── int_staffing_impact.sql
│   ├── int_supplier_reliability.sql
│   └── int_schedule_volatility.sql
└── marts/            1:1 with Power BI pages (6 models)
    ├── mart_executive_overview.sql
    ├── mart_schedule_adherence.sql
    ├── mart_oee_workforce.sql
    ├── mart_quality_fpy.sql
    ├── mart_material_supplier.sql
    └── mart_strategic_scenarios.sql
```

Business logic lives entirely in dbt — Power BI handles visualization only.

---

## Design System

| Role | Color | Hex |
|------|-------|-----|
| Primary | Navy | `#1B2A49` |
| Accent / Alert | Ember | `#E84A27` |
| Secondary | Steel Blue | `#6B8CAE` |
| Success | Sage | `#4F7942` |
| Background | Soft Ivory | `#F5F3EE` |
| Text | Charcoal | `#2D2D2D` |

Applied consistently across Power BI (custom JSON theme), Jupyter visualizations (matplotlib), and summary cards.

---

## Repository Structure

```
LumenOps-360/
├── README.md
├── docs/
│   ├── LumenOps_360_Blueprint.md       # Project blueprint (v1.3 final)
│   ├── kpi_definitions.md              # KPI formulas + validated baselines
│   ├── methodology.md                  # DMAIC, TPM, TOC, Lean, SPC applied
│   ├── case_study_5_whys.md            # Root cause trace: OTD → changeover
│   └── fishbone_housing_damage.md      # Ishikawa analysis for Outdoor defects
├── src/
│   ├── generate_data.py                # Reproducible data generator (seed=42)
│   ├── load_to_duckdb.py               # CSV → DuckDB loader with integrity checks
│   └── config.py                       # Simulation parameters
├── lumenops/                           # dbt project root
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/
│       ├── intermediate/
│       └── marts/
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_spc_control_charts.ipynb
│   └── 03_hypothesis_testing.ipynb
├── data/
│   ├── raw/                            # 14 generated CSVs
│   └── lumenops.duckdb
├── powerbi/
│   ├── LumenOps_360.pbix
│   └── LumenOps_360_Theme.json
└── assets/
    └── design_system.md
```

---

## How to Reproduce

```bash
# 1. Clone the repository
git clone https://github.com/[your-username]/LumenOps-360.git
cd LumenOps-360

# 2. Install dependencies
pip install dbt-duckdb duckdb pandas numpy faker seaborn matplotlib scipy statsmodels jupyter

# 3. Generate the data (seed=42 ensures identical output)
cd src
python generate_data.py

# 4. Load into DuckDB
python load_to_duckdb.py

# 5. Run dbt
cd ../lumenops
dbt run --profiles-dir .
dbt test --profiles-dir .

# 6. Open notebooks or Power BI
# Jupyter notebooks connect to ../data/lumenops.duckdb
# Power BI connects via DuckDB ODBC driver
```

---

## About the Author

**Harshil Patel** — Electronics Engineering graduate and former Production Engineer at an LED lighting manufacturer. This project draws on real shop-floor experience: the production flow, defect types, downtime codes, and operational pain points are grounded in lived experience, not textbook theory.

This is the third project in a deliberate portfolio sequence: **BI 360** (FMCG) → **SwiftRoute/Hoogland Outdoors** (Logistics) → **LumenOps 360** (Manufacturing) — each progressively deeper in domain coverage and analytical sophistication.

---

*Built with Python, DuckDB, dbt, Power BI, and Jupyter. Targeting operations analyst and data analyst roles in Dutch manufacturing.*
