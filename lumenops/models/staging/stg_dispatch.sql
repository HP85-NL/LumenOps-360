with source as (
    select * from {{ source('raw', 'fact_dispatch') }}
)

select
    dispatch_id,
    order_id,
    dispatch_date,
    days_late,
    delay_reason,

    -- Derived: delivery classification
    case
        when days_late <= 0 then 'ON_TIME'
        when days_late between 1 and 3 then 'LATE_1_3_DAYS'
        when days_late between 4 and 7 then 'LATE_4_7_DAYS'
        else 'LATE_8_PLUS_DAYS'
    end as delivery_bucket,

    -- Derived: binary on-time flag
    case when days_late <= 0 then true else false end as is_on_time

from source
