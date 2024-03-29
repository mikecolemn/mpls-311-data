/*
    Creates a dimension table for dates and some calculations of the dates
*/

{{ config(materialized='incremental',
          unique_key = 'case_id',
          partition_by={
            "field": "open_datetime",
            "data_type": "timestamp",
            "granularity": "year"
          }
          ) }}


with dates as (
  select
      case_id,
      --{{ dbt_utils.generate_surrogate_key(['open_datetime', 'closed_datetime', 'last_update_datetime']) }} as date_id,
      open_datetime,
      closed_datetime,
      last_update_datetime,
      TIMESTAMP_DIFF(closed_datetime, open_datetime, MINUTE) as duration_minutes,
      ROUND(TIMESTAMP_DIFF(closed_datetime, open_datetime, MINUTE) / 60,2) as duration_hours,
      ROUND(TIMESTAMP_DIFF(closed_datetime, open_datetime, MINUTE) / 60 / 24,2) as duration_days
  from {{ ref('stg_mpls_311data') }} s
  --GROUP BY open_datetime, closed_datetime, last_update_datetime
)
select *
from dates