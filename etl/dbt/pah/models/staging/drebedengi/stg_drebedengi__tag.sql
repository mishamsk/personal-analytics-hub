with source as (

    select * from {{ source('drebedengi', 'tag') }}

),

renamed as (

    select
        id as tag_id,
        parent_id,
        budget_family_id,
        name,
        is_hidden,
        is_shared,
        sort

    from source
    where tombstone is null

)

select * from renamed

