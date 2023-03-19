/*
    Creates a fact table for mpls 311 data cases
*/

{{ config(materialized='table') }}

select 
    s.case_id,
    s.object_id,
    dc.category_id,
    dd.date_id,
    s.case_status,
    dg.geography_id
from {{ ref('stg_mpls_311data') }} s
inner join  {{ ref('dim_categories') }} dc
    on dc.category_id = {{ dbt_utils.generate_surrogate_key(['s.subject_name', 
                                                            's.reason_name', 
                                                            's.type_name',
                                                            's.title']) }}
inner join {{ ref('dim_dates') }} dd
    on dd.date_id = {{ dbt_utils.generate_surrogate_key(['s.open_datetime',
                                                         's.closed_datetime',
                                                         's.last_update_datetime']) }}
inner join {{ ref('dim_geography') }} dg
    on dg.geography_id = {{ dbt_utils.generate_surrogate_key(['s.coord_x', 
                                                            's.coord_y', 
                                                            's.geometry_x',
                                                            's.geometry_y']) }}