with source as (
    select * from {{ source('raw', 'dim_date') }}
)

select
    -- Raw column is 'date', we rename to 'date_key' for consistency
    date as date_key,
    year,
    quarter,
    month,
    month_name,
    week as week_iso,
    day_of_week,
    day_name,
    is_weekend,

    -- Derived
    year as fiscal_year,
    'Q' || quarter as quarter_label,
    year || '-' || lpad(month::varchar, 2, '0') as year_month

from source
