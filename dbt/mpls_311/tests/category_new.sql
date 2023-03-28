{{ config(severity = 'warn') }}

-- Identifies combinations of categorization fields that have not been previously seen, and are not part of the seed data file
-- Return distinct list of newly seen categorization fields
select distinct 
    s.subject_name, s.reason_name, s.type_name, s.title
from {{ source('staging','mpls_311data_partitioned') }} s
left join {{ ref('mpls_311_categories') }} c
on s.subject_name = c.subject_name
and s.reason_name = c.reason_name
and s.type_name = c.type_name
and s.title = c.type_name
where c.subject_name is null
