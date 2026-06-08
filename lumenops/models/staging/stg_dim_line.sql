with source as (
    select * from {{ source('raw', 'dim_line') }}
)

select
    line_id,
    line_name,
    rated_capacity_per_hour

from source
