/*
    This will stage the mpls 311 data
*/

{{ config(materialized='view') }}

select 
    -- identifiers
    cast(case_id as integer) as case_id,
    cast(object_id as integer) as object_id,

    -- categorization
    subject_name,
    reason_name,
    type_name,
    title,
    
    -- dates
    cast(open_datetime as timestamp) as open_datetime,
    cast(closed_datetime as timestamp) as closed_datetime,
    cast(last_update_datetime as timestamp) as last_update_datetime,
    
    -- status
    cast(case_status as integer) as case_status,
    
    -- geography
    coord_x,
    coord_y,
    geometry_x,
    geometry_y

from {{ source('staging','raw_mpls_311data') }}
