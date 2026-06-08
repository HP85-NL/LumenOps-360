with source as (
    select * from {{ source('raw', 'fact_sales_orders') }}
)

select
    order_id,
    customer_id,
    sku,
    order_date,
    promised_date,
    qty_ordered,
    unit_price_eur,
    priority,

    -- Derived: order value
    qty_ordered * unit_price_eur as order_value_eur,

    -- Derived: lead time promised to customer
    promised_date - order_date as promised_lead_time_days

from source
