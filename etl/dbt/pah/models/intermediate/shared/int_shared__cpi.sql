WITH 

cpi_raw as (
   select * from {{ ref('stg_economy__cpi') }}
)

select
	r.*,
	ac.area_name,
	ic.item_name
from
	cpi_raw as r
	left join {{ ref('cpi_area_codes') }} as ac
		ON r.area_code = ac.area_code
    left join {{ ref('cpi_item_codes') }} as ic
        ON r.item_code = ic.item_code
