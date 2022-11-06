WITH 

x_change_rates as (
   select * from {{ ref('stg_economy__x_change_rate') }}
),

usd_rates AS (
	SELECT
		xr.x_change_rate_id,
		xr.ts,
		xr.currency_code,
		(xr.rate / xr_ref.rate)::NUMERIC(10,
			2) AS rate
	FROM
		x_change_rates xr
	LEFT JOIN x_change_rates xr_ref ON xr.ts = xr_ref.ts
		AND xr.base_currency_code = xr_ref.base_currency_code
	WHERE
		xr.base_currency_code <> 'USD'
		AND xr.currency_code <> 'USD'
		AND xr_ref.currency_code = 'USD'
	UNION
	SELECT
		xr.x_change_rate_id,
		xr.ts,
		xr.base_currency_code as currency_code,
		(1 / xr.rate)::NUMERIC(10,
			2) AS rate
	FROM
		x_change_rates xr
	WHERE
		xr.base_currency_code <> 'USD'
		AND xr.currency_code = 'USD'
    UNION
    SELECT
		xr.x_change_rate_id,
		xr.ts,
		xr.currency_code as currency_code,
		xr.rate AS rate
	FROM
		x_change_rates xr
	WHERE
		xr.base_currency_code = 'USD'
),
usd_rate_range as (
	select currency_code, rate, ts as ts_start, LEAD(ts, 1, {{ dateadd("day", 1, "current_date") }}) OVER (PARTITION BY currency_code ORDER BY ts) as ts_end
	from usd_rates
),
dates as (
	select date_day as ts 
    from {{ ref('all_dates') }}
    where 
   		date_day >= (select MIN(ts) from usd_rates) AND 
    	date_day <= (select MAX(ts) from usd_rates)    	
)

select
	d.ts,
	urr.currency_code,
	urr.rate
from
	dates as d
	inner join usd_rate_range as urr
		ON d.ts >= urr.ts_start
     		AND d.ts < urr.ts_end
