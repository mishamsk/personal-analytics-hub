{{ dbt_utils.date_spine(
    datepart="day",
    start_date="cast('" + env_var('PAH_START_DATE',"2010-01-01") + "' as date)",
    end_date=dateadd("day", 1, "current_date")
   )
}}