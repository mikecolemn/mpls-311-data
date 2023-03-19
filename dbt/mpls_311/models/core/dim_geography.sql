/*
    Creates a dimension table for geography information
*/

{{ config(materialized='table') }}

select
    {{ dbt_utils.generate_surrogate_key(['coord_x', 
                                        'coord_y', 
                                        'geometry_x',
                                        'geometry_y']) }} as geography_id,
    coord_x,
    coord_y,
    geometry_x,
    geometry_y
from {{ ref('stg_mpls_311data') }} s
GROUP BY coord_x, coord_y, geometry_x, geometry_y