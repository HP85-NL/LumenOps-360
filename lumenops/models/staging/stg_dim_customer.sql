with source as (
    select * from {{ source('raw', 'dim_customer') }}
)

select
    customer_id,
    customer_name,
    country,
    segment

from source
