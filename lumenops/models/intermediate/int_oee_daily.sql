with production as (
    select * from {{ ref('stg_production_log') }}
),

quality as (
    select
        batch_id,
        sum(units_inspected) as total_inspected,
        sum(units_passed) as total_passed,
        sum(units_rejected) as total_rejected
    from {{ ref('stg_qc_inspection') }}
    where stage = 'PRODUCTION_QC'
    group by batch_id
)

select
    p.prod_log_id,
    p.production_date,
    p.shift_id,
    p.line_id,
    p.sku,

    -- ── Availability ──
    p.planned_runtime_mins,
    p.actual_runtime_mins,
    p.downtime_mins,
    p.downtime_reason,
    round(
        cast(p.actual_runtime_mins as double) / nullif(p.planned_runtime_mins, 0),
        4
    ) as availability,

    -- ── Performance ──
    p.ideal_cycle_time_sec,
    p.actual_units,
    p.planned_units,
    round(
        (p.ideal_cycle_time_sec * p.actual_units / 60.0)
        / nullif(p.actual_runtime_mins, 0),
        4
    ) as performance,

    -- ── Quality (from QC join) ──
    coalesce(q.total_inspected, p.actual_units) as units_inspected,
    coalesce(q.total_passed, p.actual_units) as units_passed,
    coalesce(q.total_rejected, 0) as units_rejected,
    round(
        cast(coalesce(q.total_passed, p.actual_units) as double)
        / nullif(coalesce(q.total_inspected, p.actual_units), 0),
        4
    ) as quality,

    -- ── OEE ──
    round(
        (cast(p.actual_runtime_mins as double) / nullif(p.planned_runtime_mins, 0))
        * ((p.ideal_cycle_time_sec * p.actual_units / 60.0) / nullif(p.actual_runtime_mins, 0))
        * (cast(coalesce(q.total_passed, p.actual_units) as double)
           / nullif(coalesce(q.total_inspected, p.actual_units), 0)),
        4
    ) as oee,

    -- ── Staffing (Dutch labor shortage dimension) ──
    p.planned_operators,
    p.actual_operators,
    p.overtime_hours,
    p.staffing_fill_rate,
    p.is_understaffed

from production p
left join quality q on q.batch_id = 'B-' || lpad(cast(p.prod_log_id as varchar), 6, '0')
