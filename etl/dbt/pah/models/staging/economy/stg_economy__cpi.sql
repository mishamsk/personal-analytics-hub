with source as (

    select * from {{ source('economy', 'cpi') }}

),

renamed as (

    select
        date,
        area_code,
        item_code,
        value,
        footnotes
    from source

)

select * from renamed