/*
    Creates a dimension table for categories
*/

{{ config(materialized='table') }}

select
    {{ dbt_utils.generate_surrogate_key(['subject_name', 
                                        'reason_name', 
                                        'type_name',
                                        'title']) }} as category_id,
    subject_name,
    reason_name,
    std_type_name as type_name,
    std_title as title,
    type_name as orig_type_name,
    title as orig_title,
    source
from {{ ref('mpls_311_categories') }}

