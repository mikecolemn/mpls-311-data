{{ config(severity = 'warn') }}

-- Open date should always be before closed date
-- Return records where open date is after the closed date
select
    case_id,
    cast(open_datetime as timestamp) as open_datetime,
    cast(closed_datetime as timestamp) as closed_datetime
from {{ ref('stg_mpls_311data') }}
where cast(open_datetime as timestamp) > cast(closed_datetime as timestamp) 