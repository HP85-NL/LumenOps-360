with source as (
    select * from {{ source('raw', 'fact_material_requisitions') }}
)

select
    mr_id,
    order_id,
    sku,
    mr_raised_date,
    mr_fulfilled_date,
    shortage_flag,
    shortage_qty,

    -- Derived: fulfillment lead time in days
    mr_fulfilled_date - mr_raised_date as mr_lead_time_days

from source
