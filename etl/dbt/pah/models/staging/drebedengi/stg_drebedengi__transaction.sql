with source as (

    select * from {{ source('drebedengi', 'transaction') }}

),

renamed as (

    select
        id as transaction_id,
        budget_object_id,
        user_nuid as user_id,
        budget_family_id,
        is_loan_transfer,
        {{ to_utc('operation_date') }} as operation_date,
        currency_id,
        operation_type,
        account_id,
        {{ cents_to_dollars('amount') }} as amount,
        comment,
        group_id

    from source
    where tombstone is null

)

select * from renamed
