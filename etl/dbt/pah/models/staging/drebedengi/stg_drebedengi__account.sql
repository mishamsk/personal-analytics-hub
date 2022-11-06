with source as (

    select * from {{ source('drebedengi', 'account') }}

),

renamed as (

    select
        id,
        budget_family_id,
        object_type,
        name,
        is_hidden,
        is_autohide,
        is_loan,
        sort,
        wallet_user_id,
        icon_id

    from source
    where tombstone is null
)

select * from renamed

