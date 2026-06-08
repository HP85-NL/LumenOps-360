with production as (
    select * from {{ ref('stg_production_log') }}
),

products as (
    select * from {{ ref('stg_dim_product') }}
)

select
    p.prod_log_id,
    p.production_date,
    p.shift_id,
    p.line_id,
    p.sku,
    pr.category,
    pr.product_name,
    p.downtime_mins,
    p.downtime_reason,

    -- ── Changeover flag ──
    case
        when p.downtime_reason = 'CHANGEOVER' then true
        else false
    end as is_changeover,

    -- ── Changeover cost (lost production minutes × €/min) ──
    case
        when p.downtime_reason = 'CHANGEOVER'
        then p.downtime_mins * 2.50
        else 0
    end as changeover_cost_eur,

    -- ── Management replan flag ──
    case
        when p.downtime_reason = 'SCHEDULE_CHANGE_MGMT' then true
        else false
    end as is_mgmt_replan,

    -- ── SKU changed from previous shift on same line ──
    lag(p.sku) over (
        partition by p.line_id
        order by p.production_date, p.shift_id
    ) as prev_sku,

    case
        when p.sku != lag(p.sku) over (
            partition by p.line_id
            order by p.production_date, p.shift_id
        ) then true
        else false
    end as is_sku_switch,

    -- ── Daily changeover count per line ──
    count(case when p.downtime_reason = 'CHANGEOVER' then 1 end) over (
        partition by p.line_id, p.production_date
    ) as daily_changeovers_on_line

from production p
left join products pr on p.sku = pr.sku
