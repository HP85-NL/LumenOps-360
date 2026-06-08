with volatility as (
    select * from {{ ref('int_schedule_volatility') }}
),

oee as (
    select * from {{ ref('int_oee_daily') }}
),

supplier as (
    select * from {{ ref('int_supplier_reliability') }}
),

staffing as (
    select * from {{ ref('int_staffing_impact') }}
),

dates as (
    select * from {{ ref('stg_dim_date') }}
)

select
    v.prod_log_id,
    v.production_date,
    v.shift_id,
    v.line_id,
    v.sku,
    v.category,
    v.product_name,

    -- ── Current state ──
    o.oee,
    o.availability,
    o.performance,
    o.quality,
    o.downtime_mins,
    o.downtime_reason,
    v.is_changeover,
    v.changeover_cost_eur,
    v.is_mgmt_replan,
    v.is_sku_switch,
    v.daily_changeovers_on_line,

    -- ── Staffing context ──
    st.staffing_fill_rate,
    st.staffing_bucket,
    st.overtime_cost_eur,
    st.lost_output_cost_eur,

    -- ── Scenario A: Schedule freeze (20% changeover reduction) ──
    case
        when v.is_changeover
        then v.changeover_cost_eur * 0.20
        else 0
    end as scenario_a_savings_eur,

    -- ── Scenario B: Staffing to 95% fill rate ──
    case
        when st.staffing_fill_rate < 0.95
        then st.lost_output_cost_eur * 0.60
        else 0
    end as scenario_b_savings_eur,

    -- ── Scenario C: Tariff shock (from supplier data) ──
    -- Aggregated at report level in Power BI

    -- ── Date dimensions ──
    d.year,
    d.quarter_label,
    d.month_name,
    d.year_month,
    d.week_iso

from volatility v
left join oee o on v.prod_log_id = o.prod_log_id
left join staffing st on v.prod_log_id = st.prod_log_id
left join dates d on v.production_date = d.date_key