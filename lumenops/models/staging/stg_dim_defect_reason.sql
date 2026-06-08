with source as (
    select * from {{ source('raw', 'dim_defect_reason') }}
)

select
    -- Raw column is 'code', we rename to 'defect_code'
    code as defect_code,
    description as defect_description,
    severity,
    typical_root_cause

from source
