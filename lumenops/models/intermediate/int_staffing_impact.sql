with oee as (
    select * from {{ ref('int_oee_daily') }}
),

products as (
    select * from {{ ref('stg_dim_product') }}
)

select
    o.prod_log_id,
    o.production_date,
    o.shift_id,
    o.line_id,
    o.sku,
    p.category,
    o.planned_operators,
    o.actual_operators,
    o.staffing_fill_rate,
    o.is_understaffed,
    o.overtime_hours,
    o.oee,
    o.availability,
    o.performance,
    o.quality,
    o.actual_units,
    o.planned_units,

    -- ── Staffing bucket for analysis ──
    case
        when o.staffing_fill_rate >= 0.95 then 'FULLY_STAFFED'
        when o.staffing_fill_rate >= 0.85 then 'MINOR_GAP'
        when o.staffing_fill_rate >= 0.75 then 'MODERATE_GAP'
        else 'SEVERE_SHORTAGE'
    end as staffing_bucket,

    -- ── Lost units from understaffing ──
    case
        when o.is_understaffed then o.planned_units - o.actual_units
        else 0
    end as units_lost_to_understaffing,

    -- ── € cost of lost output ──
    case
        when o.is_understaffed
        then (o.planned_units - o.actual_units) * p.unit_cost_eur * 1.4
        else 0
    end as lost_output_cost_eur,

    -- ── € cost of overtime ──
    o.overtime_hours * 35.0 as overtime_cost_eur

from oee o
left join products p on o.sku = p.sku
