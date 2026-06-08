with fpy as (
    select * from {{ ref('int_fpy_by_batch') }}
),

quality_hold_cost as (
    select
        date_trunc('month', production_date) as month_start,
        sku,
        sum(downtime_mins) * 2.50 as quality_hold_downtime_cost_eur
    from {{ ref('int_oee_daily') }}
    where downtime_reason = 'QUALITY_HOLD'
    group by 1, 2
)

select
    date_trunc('month', f.inspected_date) as month_start,
    f.sku,
    f.category,

    -- ── Scrap cost ──
    sum(f.rejection_cost_eur) as scrap_cost_eur,

    -- ── Volume metrics ──
    sum(f.units_inspected) as total_inspected,
    sum(f.units_rejected) as total_rejected,
    sum(f.units_passed) as total_passed,

    -- ── Defect rate for the month ──
    round(
        cast(sum(f.units_rejected) as double)
        / nullif(sum(f.units_inspected), 0),
        4
    ) as monthly_defect_rate,

    -- ── FPY for the month ──
    round(
        cast(sum(f.units_passed) as double)
        / nullif(sum(f.units_inspected), 0),
        4
    ) as monthly_fpy,

    -- ── Top defect reason (mode) ──
    mode(f.defect_reason) as top_defect_reason,

    -- ── Downtime cost from quality holds ──
    coalesce(qh.quality_hold_downtime_cost_eur, 0) as quality_hold_downtime_cost_eur,

    -- ── Total COPQ ──
    sum(f.rejection_cost_eur)
        + coalesce(qh.quality_hold_downtime_cost_eur, 0) as total_copq_eur

from fpy f
left join quality_hold_cost qh
    on date_trunc('month', f.inspected_date) = qh.month_start
    and f.sku = qh.sku
group by 1, 2, 3, qh.quality_hold_downtime_cost_eur
