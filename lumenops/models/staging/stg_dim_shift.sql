with source as (
    select * from {{ source('raw', 'dim_shift') }}
)

select
    shift_id,
    shift_name,
    start_time,
    end_time

from source
