with orders as (
    select * from {{ ref('stg_sales_orders') }}
),

dispatch as (
    select * from {{ ref('stg_dispatch') }}
),

materials as (
    select * from {{ ref('stg_material_requisitions') }}
),

customers as (
    select * from {{ ref('stg_dim_customer') }}
),

products as (
    select * from {{ ref('stg_dim_product') }}
)

select
    o.order_id,
    o.customer_id,
    c.customer_name,
    c.segment,
    o.sku,
    p.product_name,
    p.category,
    o.order_date,
    o.promised_date,
    o.qty_ordered,
    o.unit_price_eur,
    o.order_value_eur,
    o.priority,
    o.promised_lead_time_days,

    -- ── Dispatch ──
    d.dispatch_date,
    d.days_late,
    d.delay_reason,
    d.is_on_time,
    d.delivery_bucket,

    -- ── Material ──
    m.mr_raised_date,
    m.mr_fulfilled_date,
    m.mr_lead_time_days,
    m.shortage_flag,
    m.shortage_qty,

    -- ── Revenue at risk from late delivery ──
    case
        when d.is_on_time = false then o.order_value_eur
        else 0
    end as late_order_value_eur

from orders o
left join dispatch d on o.order_id = d.order_id
left join materials m on o.order_id = m.order_id
left join customers c on o.customer_id = c.customer_id
left join products p on o.sku = p.sku
