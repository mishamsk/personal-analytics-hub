WITH 

rates as (
   select * from {{ ref('int_shared__x_change_rate') }}
),

currencies as (
    select 
        currency_code,
        currency_id
    from {{ ref('stg_drebedengi__currency') }}
),

transactions as (
   select * 
   from {{ ref('stg_drebedengi__transaction') }}
)

select 
    transaction_id,
    budget_object_id,
    user_id,
    budget_family_id,
    is_loan_transfer,
    operation_date,
    operation_type,
    account_id,
    CASE
        WHEN c.currency_code = 'USD' then amount 
        else amount / r.rate
    END as amount_usd,
    comment,
    group_id
from transactions as t
    inner join currencies as c on t.currency_id = c.currency_id
    left join rates as r on 
        c.currency_code = r.currency_code
        AND {{ date_trunc("day", "r.ts") }} = {{ date_trunc("day", "t.operation_date") }}