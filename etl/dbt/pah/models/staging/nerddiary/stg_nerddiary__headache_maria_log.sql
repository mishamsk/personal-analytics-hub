with source as (

    select * from {{ source('nerddiary', 'headache_maria_log') }}

),

renamed as (

    select
        poll_id,
        user_id,
        poll_ts,
        drug_dose::INTEGER,
        case drug_helped when 'Yes' then true else false end as drug_helped,        
        comment,
        end_time::TIMESTAMP,
        case drug_used when 'yes' then true else false end as drug_used,
        start_time::TIMESTAMP,
        preiod_day::INTEGER as period_day,
        period::BOOLEAN,
        drug_type,
        headache_type

    from source

)

select * from renamed

