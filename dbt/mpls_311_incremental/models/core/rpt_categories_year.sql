/*
    Creates a report table for category groups, rolled up by year of open_datetime
*/

{{ config(materialized='table') }}

select 
  EXTRACT(YEAR FROM dd.open_datetime) as OpenYear, 
  EXTRACT(MONTH FROM dd.open_datetime) as OpenMonth,
  dc.subject_name,
  dc.reason_name,
  dc.type_name,
  dc.title,
  COUNT(1) as RecCount
from {{ ref('fact_311data') }} f
inner join {{ ref('dim_categories') }} dc
  on f.category_id = dc.category_id
inner join {{ ref('dim_dates') }} dd
  on f.date_id = dd.date_id
group by 
  EXTRACT(YEAR FROM dd.open_datetime), 
  EXTRACT(MONTH FROM dd.open_datetime),
  dc.subject_name,
  dc.reason_name,
  dc.type_name,
  dc.title
