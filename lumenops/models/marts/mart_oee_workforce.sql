with staffing as (
    select * from {{ ref('int_staffing_impact') }}
),

volatility as (
    select * from {{ ref('int_schedule_volatility') }}
),

dates as (
    select * from {{ ref('stg_dim_date') }}
),

lines as (
    select * from {{ ref('stg_dim_line') }}
),

shifts as (
    select * from {{ ref('stg_dim_shift') }}
)

select
    s.prod_log_id,
    s.production_date,
    s.shift_id,
    sh.shift_name,
    s.line_id,
    l.line_name,
    s.sku,
    s.category,
    s.oee,
    s.availability,
    s.performance,
    s.quality,
    s.actual_units,
    s.planned_units,

    -- ── Staffing ──
    s.planned_operators,
    s.actual_operators,
    s.staffing_fill_rate,
    s.staffing_bucket,
    s.is_understaffed,
    s.overtime_hours,
    s.overtime_cost_eur,
    s.lost_output_cost_eur,
    s.units_lost_to_understaffing,

    -- ── Schedule volatility ──
    v.is_changeover,
    v.changeover_cost_eur,
    v.is_mgmt_replan,
    v.is_sku_switch,
    v.daily_changeovers_on_line,

    -- ── Date dimensions ──
    d.year,
    d.quarter_label,
    d.month_name,
    d.year_month,
    d.week_iso,
    d.day_name,

    -- ── OEE trend (13-week rolling) ──
    avg(s.oee) over (
        partition by s.line_id
        order by s.production_date
        rows between 77 preceding and current row
    ) as rolling_13wk_oee

from staffing s
left join volatility v on s.prod_log_id = v.prod_log_id
left join dates d on s.production_date = d.date_key
left join lines l on s.line_id = l.line_id
left join shifts sh on s.shift_id = sh.shift_id
