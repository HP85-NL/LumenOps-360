with qc as (
    select * from {{ ref('stg_qc_inspection') }}
),

products as (
    select * from {{ ref('stg_dim_product') }}
)

select
    q.qc_id,
    q.batch_id,
    q.stage,
    q.inspected_date,
    q.sku,
    p.category,
    p.product_name,
    q.units_inspected,
    q.units_passed,
    q.units_rejected,
    q.defect_reason,
    q.pass_rate,
    q.rejection_rate,

    -- ── COPQ: cost of rejected units ──
    q.units_rejected * p.unit_cost_eur as rejection_cost_eur,

    -- ── SPC inputs: will feed control charts in notebooks ──
    avg(q.rejection_rate) over (
        partition by q.sku
        order by q.inspected_date
        rows between 19 preceding and current row
    ) as rolling_avg_rejection_rate,

    stddev(q.rejection_rate) over (
        partition by q.sku
        order by q.inspected_date
        rows between 19 preceding and current row
    ) as rolling_stddev_rejection_rate

from qc q
left join products p on q.sku = p.sku