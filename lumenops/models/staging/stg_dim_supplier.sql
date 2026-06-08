with source as (
    select * from {{ source('raw', 'dim_supplier') }}
)

select
    supplier_id,
    supplier_name,
    component_type,
    country as supplier_country,
    avg_lead_time_days,
    is_single_source,
    tariff_exposure_pct,
    on_time_baseline_pct

from source
