with source as (

    select * from {{ source('economy', 'x_change_rate') }}

),

renamed as (

    select
        id as x_change_rate_id,
		ts,
		base_currency_code,
		currency_code,
		rate
    from source

)

select * from renamed