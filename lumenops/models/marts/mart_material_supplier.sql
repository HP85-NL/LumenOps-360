with supplier as (
    select * from {{ ref('int_supplier_reliability') }}
),

materials as (
    select * from {{ ref('stg_material_requisitions') }}
),

orders as (
    select * from {{ ref('stg_sales_orders') }}
),

dates as (
    select * from {{ ref('stg_dim_date') }}
)

select
    -- ── Supplier delivery detail ──
    s.delivery_id,
    s.supplier_id,
    s.supplier_name,
    s.component_type,
    s.supplier_country,
    s.is_single_source,
    s.tariff_exposure_pct,
    s.po_date,
    s.promised_date,
    s.actual_arrival_date,
    s.lead_time_variance_days,
    s.is_supplier_on_time,
    s.qty_ordered,
    s.qty_received,
    s.qty_defective,
    s.delivery_value_eur,
    s.inbound_quality_rate,
    s.delivery_risk_bucket,
    s.current_tariff_cost_eur,
    s.double_tariff_cost_eur,

    -- ── Material shortage context ──
    shortage_summary.total_shortages,
    shortage_summary.total_shortage_qty,

    -- ── Date dimensions ──
    d.year,
    d.quarter_label,
    d.month_name,
    d.year_month,

    -- ── Supplier rolling on-time rate ──
    round(
        avg(case when s.is_supplier_on_time then 1.0 else 0.0 end) over (
            partition by s.supplier_id
            order by s.po_date
            rows between 9 preceding and current row
        ),
        4
    ) as supplier_rolling_otd

from supplier s
left join dates d on s.po_date = d.date_key
left join (
    select
        date_trunc('month', mr_raised_date) as month_start,
        count(case when shortage_flag then 1 end) as total_shortages,
        sum(case when shortage_flag then shortage_qty else 0 end) as total_shortage_qty
    from materials
    group by 1
) shortage_summary
    on date_trunc('month', s.po_date) = shortage_summary.month_start
    