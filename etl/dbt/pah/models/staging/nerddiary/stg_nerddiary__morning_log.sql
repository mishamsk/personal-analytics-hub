with source as (

    select * from {{ source('nerddiary', 'morning_log') }}

),

renamed as (

    select
        poll_id,
        user_id,
        poll_ts,
        fatigue::INTEGER,
        slept_enough::INTEGER,
        midnight_woke_up::BOOLEAN,
        cramping::INTEGER,
        awaken_by::INTEGER,
        sleep_end_time::TIMESTAMP,
        sleep_start_time::TIME

    from source

)

select * from renamed

