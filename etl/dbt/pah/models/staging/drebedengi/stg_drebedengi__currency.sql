with source as (

    select * from {{ source('drebedengi', 'currency') }}

),

renamed as (

    select
        id as currency_id,
        user_name,
        currency_code,
        exchange_rate,
        budget_family_id,
        is_default,
        is_autoupdate,
        is_hidden

    from source
    where tombstone is null

)

select * from renamed

