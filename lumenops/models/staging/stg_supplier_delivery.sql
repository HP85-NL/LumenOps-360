with source as (
    select * from {{ source('raw', 'fact_supplier_delivery') }}
)

select
    delivery_id,
    supplier_id,
    component_type,
    po_date,
    promised_date,
    actual_arrival_date,
    qty_ordered,
    qty_received,
    qty_defective,
    unit_cost_eur,

    -- Derived: lead time variance (positive = late)
    actual_arrival_date - promised_date as lead_time_variance_days,

    -- Derived: supplier on-time flag
    case
        when actual_arrival_date <= promised_date then true
        else false
    end as is_supplier_on_time,

    -- Derived: inbound quality rate
    round(
        cast(qty_received - qty_defective as double) / nullif(qty_received, 0),
        4
    ) as inbound_quality_rate,

    -- Derived: total delivery value
    qty_ordered * unit_cost_eur as delivery_value_eur

from source
