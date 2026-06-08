with deliveries as (
    select * from {{ ref('stg_supplier_delivery') }}
),

suppliers as (
    select * from {{ ref('stg_dim_supplier') }}
)

select
    d.delivery_id,
    d.supplier_id,
    s.supplier_name,
    s.component_type,
    s.supplier_country,
    s.is_single_source,
    s.tariff_exposure_pct,
    d.po_date,
    d.promised_date,
    d.actual_arrival_date,
    d.lead_time_variance_days,
    d.is_supplier_on_time,
    d.qty_ordered,
    d.qty_received,
    d.qty_defective,
    d.unit_cost_eur,
    d.delivery_value_eur,
    d.inbound_quality_rate,

    -- ── Tariff scenario: cost if tariff doubles ──
    d.delivery_value_eur * (s.tariff_exposure_pct / 100.0) as current_tariff_cost_eur,
    d.delivery_value_eur * (s.tariff_exposure_pct / 100.0 * 2) as double_tariff_cost_eur,

    -- ── Late delivery flag with severity ──
    case
        when d.lead_time_variance_days <= 0 then 'ON_TIME'
        when d.lead_time_variance_days between 1 and 3 then 'LATE_MINOR'
        when d.lead_time_variance_days between 4 and 7 then 'LATE_MODERATE'
        else 'LATE_SEVERE'
    end as delivery_risk_bucket

from deliveries d
left join suppliers s on d.supplier_id = s.supplier_id
