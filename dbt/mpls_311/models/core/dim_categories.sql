/*
    Creates a dimension table for categories
*/

{{ config(materialized='table') }}

select
    row_number() OVER(ORDER BY subject_name, reason_name, std_type_name, std_title) as category_id,
    subject_name,
    reason_name,
    std_type_name as type_name,
    std_title as title,
    type_name as orig_type_name,
    title as orig_title,
    source
from {{ ref('mpls_311_categories') }}

