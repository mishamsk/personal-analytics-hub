WITH 

headache_maria_log as (
   select * from {{ ref('stg_nerddiary__headache_maria_log') }}
),
dates AS (
	SELECT
		all_dates.date_day AS ts
	FROM
		{{ ref('all_dates') }}
	WHERE
		all_dates.date_day >= (
			SELECT
				min(ml.start_time)
			FROM
				headache_maria_log AS ml)
),
GROUPS AS (
	SELECT
		ds.ts,
		count(ml.start_time) OVER (ORDER BY ds.ts) AS
	last_headache_group,
	ROW_NUMBER() over (ORDER BY ds.ts) - count(ml.start_time) OVER (ORDER BY ds.ts) as consec_headache_group
FROM
	dates AS ds
	LEFT JOIN headache_maria_log AS ml ON ds.ts = date_trunc('day',
	ml.start_time)
)
SELECT
	ds.ts,
	extract(day from date_trunc('day', ds.ts) - date_trunc('day', first_value(ds.ts) over (partition by consec_headache_group ORDER BY ds.ts))) as headache_streak,	
	extract(day from date_trunc('day', ds.ts) - date_trunc('day', first_value(ml.start_time) OVER (PARTITION BY g.last_headache_group ORDER BY ds.ts))) AS headless_streak,
		ml.*
	FROM
		dates AS ds
		INNER JOIN GROUPS g ON g.ts = ds.ts
		LEFT JOIN headache_maria_log AS ml ON ds.ts = date_trunc('day', ml.start_time)