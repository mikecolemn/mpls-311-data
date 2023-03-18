/*
    Creates a fact table for mpls 311 data cases
*/

{{ config(materialized='table') }}

select 
    s.unique_hash,
    s.case_id,
    s.object_id,
    dc.category_id,
    dd.date_id,
    s.case_status,
    dg.geography_id
from {{ ref('stg_mpls_311data') }} s
inner join  {{ ref('dim_categories') }} dc
    on s.subject_name = dc.subject_name
    and s.reason_name = dc.reason_name
    and s.type_name = dc.orig_type_name
    and s.title = dc.orig_title
inner join {{ ref('dim_dates') }} dd
    on s.open_datetime = dd.open_datetime
    and s.closed_datetime = dd.closed_datetime
    and s.last_update_datetime = dd.last_update_datetime
inner join {{ ref('dim_geography') }} dg
    on s.coord_x = dg.coord_x
    on s.coord_y = dg.coord_y
    on s.geometry_x = dg.geometry_x
    on s.geometry_y = dg.geometry_y