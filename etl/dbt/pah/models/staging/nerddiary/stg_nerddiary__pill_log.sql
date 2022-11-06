with source as (

    select * from {{ source('nerddiary', 'pill_log') }}

),

renamed as (

    select
        poll_id,
        user_id,
        poll_ts,
        drug_type,
        drug_dose::integer,
        drug_purpose

    from source

)

select * from renamed

