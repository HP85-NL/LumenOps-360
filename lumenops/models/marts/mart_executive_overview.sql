with oee as (
    select * from {{ ref('int_oee_daily') }}
),

otd as (
    select * from {{ ref('int_otd_by_order') }}
),

copq as (
    select * from {{ ref('int_copq_monthly') }}
),

staffing as (
    select * from {{ ref('int_staffing_impact') }}
),

dates as (
    select * from {{ ref('stg_dim_date') }}
)

select
    d.date_key,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    d.quarter_label,
    d.year_month,

    -- ── OEE metrics (daily, by line) ──
    o.prod_log_id,
    o.line_id,
    o.shift_id,
    o.sku,
    o.availability,
    o.performance,
    o.quality,
    o.oee,
    o.downtime_mins,
    o.downtime_reason,
    o.actual_units,
    o.planned_units,

    -- ── Staffing ──
    s.staffing_fill_rate,
    s.staffing_bucket,
    s.overtime_cost_eur,
    s.lost_output_cost_eur,

    -- ── OTD snapshot (order-level, for KPI cards) ──
    (select round(avg(case when ot.is_on_time then 1.0 else 0.0 end), 4)
     from otd ot
     where ot.order_date <= d.date_key) as cumulative_otd_rate,

    -- ── COPQ snapshot (monthly) ──
    c.total_copq_eur,
    c.monthly_fpy,
    c.monthly_defect_rate

from oee o
inner join dates d on o.production_date = d.date_key
left join staffing s on o.prod_log_id = s.prod_log_id
left join copq c
    on date_trunc('month', o.production_date) = c.month_start
    and o.sku = c.sku
    