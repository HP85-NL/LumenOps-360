# Fishbone (Ishikawa) Analysis — Defect Focus: Outdoor Product Quality

**Context:** Hypothesis testing (H5) confirmed that Outdoor products have a statistically significant higher defect rate (2.86%) compared to Indoor (2.04%) and Industrial (1.98%). This Fishbone analysis investigates potential root causes using the 6M framework, grounded in the defect types observed in the data: HOUSING_SCRATCH, HOUSING_DAMAGE_ASSEMBLY, DUST_CONTAMINATION, POOR_PACKAGING, FLICKER, DRIVER_FAULT, SOLDER_FAIL, COLOR_CONTAMINATION, and LUMEN_OUT_OF_SPEC.

---

## Fishbone Diagram (6M Categories)

```text
                                                    OUTDOOR PRODUCT
                                                    DEFECT RATE 2.86%
                                                    (40% above Indoor)
                                                          │
          ┌──────────────┬──────────────┬─────────────────┼──────────────┬──────────────┬
          │              │              │                                │              │              
      MAN (People)   MACHINE      METHOD            MATERIAL      MEASUREMENT    MILIEU (Environment)
          │              │              │                                │              │              
  Operator fatigue   Fixture wear   No dedicated     Outdoor         QC sampling    Dust and
  on evening shift   on outdoor     outdoor          housings        rate equal     particulate
          │          assembly jigs  assembly SOP     are larger,     across all     exposure during
  Understaffing              │              │        heavier →       categories     assembly
  (83% fill rate)    Torque tool    Changeover        more prone          │              │
  → rushed handling  calibration    from Indoor →    to handling    No separate    Temperature
          │          drift          Outdoor without   damage         pass/fail      and humidity
  Training gap:          │          full line purge       │          criteria for   variation
  outdoor products   Line 2 & 3         │            Single-source  outdoor IP     (seasonal)
  require different  (bottleneck)   Packaging spec    PCB supplier   rating              │
  handling than      have higher    same for all      → quality          │          Outdoor products
  indoor products    utilization    categories        variation      Lumen spec     stored in
                     → less                               │          tolerance      less controlled
                     maintenance                      LED chip       may be too     staging areas
                     windows                          batch-to-      wide for
                                                       batch          outdoor use
                                                       variation
```

---

## Analysis by 6M Category

### Man (People)

**Finding:** Staffing fill rate averages 83.1% across the plant (H1: p < 0.0001, r = 0.231). Understaffed shifts produce 3.33 pp lower OEE. When operators are stretched thin, handling care decreases — particularly for Outdoor products which are physically larger and heavier than Indoor panels and bulbs.

**Contributing factors:**
- Evening shift penalty (H4: 1.55 pp lower OEE, p < 0.0001) suggests fatigue-related quality lapses
- Outdoor products require different assembly techniques (IP-rated sealing, gasket placement, heavier housing manipulation) — cross-training gaps likely exist
- Dutch labor shortage (97 vacancies per 100 unemployed) makes it difficult to maintain a stable, experienced workforce

### Machine (Equipment)

**Finding:** Lines 2 and 3 are jointly the capacity constraint (H3: p < 0.0001). Higher utilization on these lines means fewer maintenance windows for fixture calibration and jig replacement.

**Contributing factors:**
- Outdoor housing fixtures (for Flood Lights, Street Lights) are larger and subject to more mechanical stress than Indoor fixtures
- Torque tools for IP-rated housing assembly may drift between calibration intervals
- Die-cast housing molds for Outdoor products have tighter tolerances that are sensitive to wear

### Method (Process)

**Finding:** Changeover is the #1 OEE killer (H2: 8.56 pp loss, r = 0.571). When a line switches from Indoor to Outdoor products, the setup complexity increases — different fixtures, different torque settings, different QC criteria.

**Contributing factors:**
- No dedicated Outdoor assembly SOP observed in the data — same general procedure applied across all categories
- Line purge between Indoor and Outdoor changeovers may be insufficient, leading to contamination carryover
- Packaging specification is uniform across categories — Outdoor products may need reinforced packaging due to weight and exposure risk

### Material

**Finding:** PCB panels and LED chips are outsourced with single-supplier dependency. Batch-to-batch variation in incoming components affects downstream quality.

**Contributing factors:**
- Outdoor housings are larger and heavier — more prone to HOUSING_SCRATCH and HOUSING_DAMAGE_ASSEMBLY during handling
- Single-source PCB supplier means limited ability to reject marginal batches without disrupting production
- LED chip binning variation may affect LUMEN_OUT_OF_SPEC rates more for Outdoor products where optical requirements differ

### Measurement

**Finding:** The same QC sampling rate and pass/fail criteria are applied across all product categories. This may underweight the distinct failure modes of Outdoor products.

**Contributing factors:**
- Outdoor products have IP (Ingress Protection) rating requirements not applicable to Indoor products — but QC may not have separate IP-specific inspection steps
- Lumen output specifications for Outdoor (flood, street) are different from Indoor (panel, bulb) — tolerance bands may need tightening
- No evidence of separate QC SPC tracking by product category — the SPC charts in Notebook 2 aggregate all categories

### Milieu (Environment)

**Finding:** Assembly environment factors disproportionately affect Outdoor products.

**Contributing factors:**
- DUST_CONTAMINATION is a documented defect code — Outdoor housings have more exposed surface area and are physically harder to keep clean during assembly
- Temperature and humidity variation (seasonal) affects adhesive curing and gasket sealing for IP-rated Outdoor products
- Outdoor products may spend more time in less-controlled staging areas between assembly and packaging due to their size

---

## Priority Root Causes (Ranked by Addressability)

| Rank | Root Cause | Category | Recommended Action | Expected Impact |
|---|---|---|---|---|
| 1 | No separate Outdoor assembly SOP | Method | Develop Outdoor-specific work instructions with IP-sealing checkpoints | Reduce HOUSING_DAMAGE_ASSEMBLY |
| 2 | Uniform QC criteria across categories | Measurement | Implement category-specific QC checklists with IP-rating verification | Catch Outdoor-specific defects earlier |
| 3 | Changeover contamination carryover | Method | Mandate full line purge when switching to/from Outdoor products | Reduce DUST_CONTAMINATION |
| 4 | Operator cross-training gap | Man | Outdoor product handling certification for all line operators | Reduce HOUSING_SCRATCH |
| 5 | Packaging spec not category-specific | Method | Reinforced packaging standard for Outdoor products (weight, transit exposure) | Reduce POOR_PACKAGING |

---

## Connection to Other Findings

This Fishbone analysis integrates findings from all three notebooks:

- **EDA (Notebook 1):** Identified Outdoor defect rate as an outlier in the defect distribution
- **SPC (Notebook 2):** Confirmed the overall defect process is not in statistical control (73 OOC days, Cpk = 0.669)
- **Hypothesis Testing (Notebook 3):** Formally confirmed Outdoor defect rate is statistically higher (H5: χ² = 1184.14, p < 0.0001)
- **Dashboard (Page 4):** Defect heatmap by product category visualizes this pattern
- **TOC (H3):** Lines 2–3 bottleneck means Outdoor products manufactured on these lines face compounded risk

---

*Document generated as part of LumenOps 360 — Manufacturing Operations Intelligence.*
*Root causes are inferred from data patterns and real manufacturing experience — not observed directly, as this is simulated data.*