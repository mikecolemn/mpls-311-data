/*
    Creates a dimension table for geography information
*/

{{ config(materialized='table') }}

select
    row_number() OVER(ORDER BY case_id) as geography_id,
    case_id,
    coord_x,
    coord_y,
    geometry_x,
    geometry_y
from {{ ref('stg_mpls_311data') }} s