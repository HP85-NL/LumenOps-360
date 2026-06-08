with source as (
    select * from {{ source('raw', 'fact_production_log') }}
)

select
    prod_log_id,
    date as production_date,
    shift_id,
    line_id,
    sku,

    -- Production volumes
    planned_units,
    actual_units,

    -- Runtime
    planned_runtime_mins,
    actual_runtime_mins,
    downtime_mins,
    downtime_reason,
    ideal_cycle_time_sec,

    -- Staffing (v1.2 — Dutch labor shortage dimension)
    planned_operators,
    actual_operators,
    overtime_hours,

    -- Derived: staffing fill rate per shift
    round(
        cast(actual_operators as double) / nullif(planned_operators, 0),
        3
    ) as staffing_fill_rate,

    -- Derived: is this shift understaffed?
    case
        when actual_operators < planned_operators then true
        else false
    end as is_understaffed

from source
where planned_runtime_mins > 0
