with source as (

    select * from {{ source('drebedengi', 'income_source') }}

),

renamed as (

    select
        id as income_source_id,
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

