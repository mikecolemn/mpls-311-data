/*
    Creates a dimension table for categories
*/

{{ config(materialized='table') }}


with stg_categories as (
    select subject_name,
        reason_name,
        type_name,
        title
    from {{ ref('stg_mpls_311data') }} s
    GROUP BY subject_name,
        reason_name,
        type_name,
        title
),
categories as (
    select coalesce(mc.subject_name, sg.subject_name) as subject_name,
            coalesce(mc.reason_name, sg.reason_name) as reason_name,
            coalesce(mc.std_type_name, sg.type_name) as type_name,
            coalesce(mc.std_title, sg.title) as title,
            coalesce(mc.type_name, sg.type_name) as orig_type_name,
            coalesce(mc.title, sg.title) as orig_title,
            case when mc.subject_name is null and sg.subject_name is not null then 'NEW' else mc.source end as source
    from stg_categories sg
    full outer join  {{ ref('mpls_311_categories') }} mc
        on sg.subject_name = mc.subject_name
        and sg.reason_name = mc.reason_name
        and sg.type_name = mc.type_name
        and sg.title = mc.title
)
select
    {{ dbt_utils.generate_surrogate_key(['subject_name', 
                                        'reason_name', 
                                        'orig_type_name',
                                        'orig_title']) }} as category_id,
    subject_name,
    reason_name,
    type_name,
    title,
    orig_type_name,
    orig_title,
    source
from categories sg

