with source as (
    select * from {{ source('raw', 'dim_product') }}
)

select
    sku,
    product_name,
    category,
    sub_category,
    unit_cost_eur,
    ideal_cycle_time_sec,
    bom_components_json as bom_components

from source
