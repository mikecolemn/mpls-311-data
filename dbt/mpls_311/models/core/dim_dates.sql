/*
    Creates a dimension table for dates and some calculations of the dates
*/

{{ config(materialized='table') }}

select
    {{ dbt_utils.generate_surrogate_key(['open_datetime', 'closed_datetime', 'last_update_datetime']) }} as date_id,
    open_datetime,
    closed_datetime,
    last_update_datetime,
    TIMESTAMP_DIFF(closed_datetime, open_datetime, MINUTE) as duration_minutes,
    ROUND(TIMESTAMP_DIFF(closed_datetime, open_datetime, MINUTE) / 60,2) as duration_hours,
    ROUND(TIMESTAMP_DIFF(closed_datetime, open_datetime, MINUTE) / 60 / 24,2) as duration_days
from {{ ref('stg_mpls_311data') }} s
GROUP BY open_datetime, closed_datetime, last_update_datetime