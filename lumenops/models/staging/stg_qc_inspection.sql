with source as (
    select * from {{ source('raw', 'fact_qc_inspection') }}
)

select
    qc_id,
    batch_id,
    stage,
    inspected_date,
    sku,
    units_inspected,
    units_passed,
    units_rejected,
    defect_reason,

    -- Derived: pass rate for this inspection
    round(
        cast(units_passed as double) / nullif(units_inspected, 0),
        4
    ) as pass_rate,

    -- Derived: rejection rate
    round(
        cast(units_rejected as double) / nullif(units_inspected, 0),
        4
    ) as rejection_rate

from source
where units_inspected > 0
