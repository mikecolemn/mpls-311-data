{{ config(severity = 'warn') }}

-- if the case_status = 0 (closed) then closed_datetime should be populated
-- if the case_status = 1 (open) then the closed_datetime should not be populated
-- Return records where either of these are false
select
    case_id,
    case_status,
    cast(closed_datetime as timestamp) as closed_datetime
from {{ ref('stg_mpls_311data') }}
where (case_status = 0 and closed_datetime is null)
  or (case_status = 1 and closed_datetime is not null)