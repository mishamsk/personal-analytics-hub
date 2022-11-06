with source as (

    select * from {{ source('drebedengi', 'change_record') }}

),

renamed as (

    select
        revision_id,
        action_type,
        change_object_type,
        object_id,
        date

    from source

)

select * from renamed

