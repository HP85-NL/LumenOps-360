with source as (
    select * from {{ source('raw', 'dim_downtime_reason') }}
)

select
    -- Raw column is 'code', we rename to 'downtime_code'
    code as downtime_code,
    description as downtime_description,
    category as downtime_category

from source
