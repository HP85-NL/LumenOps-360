with fpy as (
    select * from {{ ref('int_fpy_by_batch') }}
),

copq as (
    select * from {{ ref('int_copq_monthly') }}
),

dates as (
    select * from {{ ref('stg_dim_date') }}
),

defects as (
    select * from {{ ref('stg_dim_defect_reason') }}
)

select
    f.qc_id,
    f.batch_id,
    f.stage,
    f.inspected_date,
    f.sku,
    f.category,
    f.product_name,
    f.units_inspected,
    f.units_passed,
    f.units_rejected,
    f.defect_reason,
    f.pass_rate,
    f.rejection_rate,
    f.rejection_cost_eur,

    -- ── Defect detail ──
    dr.defect_description,
    dr.severity,
    dr.typical_root_cause,

    -- ── SPC inputs ──
    f.rolling_avg_rejection_rate,
    f.rolling_stddev_rejection_rate,
    f.rolling_avg_rejection_rate + 3 * coalesce(f.rolling_stddev_rejection_rate, 0) as ucl,
    f.rolling_avg_rejection_rate - 3 * coalesce(f.rolling_stddev_rejection_rate, 0) as lcl_raw,
    greatest(
        f.rolling_avg_rejection_rate - 3 * coalesce(f.rolling_stddev_rejection_rate, 0),
        0
    ) as lcl,

    -- ── Monthly COPQ context ──
    c.total_copq_eur as monthly_copq_eur,
    c.monthly_fpy,
    c.top_defect_reason as monthly_top_defect,

    -- ── Date dimensions ──
    d.year,
    d.quarter_label,
    d.month_name,
    d.year_month,
    d.week_iso

from fpy f
left join defects dr on f.defect_reason = dr.defect_code
left join dates d on f.inspected_date = d.date_key
left join copq c
    on date_trunc('month', f.inspected_date) = c.month_start
    and f.sku = c.sku
    