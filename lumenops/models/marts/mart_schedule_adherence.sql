with otd as (
    select * from {{ ref('int_otd_by_order') }}
),

dates as (
    select * from {{ ref('stg_dim_date') }}
)

select
    o.order_id,
    o.customer_id,
    o.customer_name,
    o.segment,
    o.sku,
    o.product_name,
    o.category,
    o.order_date,
    o.promised_date,
    o.dispatch_date,
    o.qty_ordered,
    o.unit_price_eur,
    o.order_value_eur,
    o.priority,
    o.promised_lead_time_days,
    o.days_late,
    o.delay_reason,
    o.is_on_time,
    o.delivery_bucket,
    o.late_order_value_eur,

    -- ── Material flow ──
    o.mr_raised_date,
    o.mr_fulfilled_date,
    o.mr_lead_time_days,
    o.shortage_flag,
    o.shortage_qty,

    -- ── Date dimensions for filtering ──
    d.year,
    d.quarter_label,
    d.month_name,
    d.year_month,
    d.week_iso,

    -- ── Customer delivery score (rolling) ──
    round(
        avg(case when o.is_on_time then 1.0 else 0.0 end) over (
            partition by o.customer_id
            order by o.order_date
            rows between 29 preceding and current row
        ),
        4
    ) as customer_rolling_otd

from otd o
left join dates d on o.order_date = d.date_key
