with source as (

    select * from {{ source('drebedengi', 'expense_category') }}

),

renamed as (

    select
        id as expense_category_id,
        parent_id,
        budget_family_id,
        object_type,
        name,
        is_hidden,
        sort

    from source
    where tombstone is null

)

select * from renamed

