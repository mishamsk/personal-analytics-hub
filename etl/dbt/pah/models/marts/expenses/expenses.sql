WITH 

expense_transactions as (
   select * 
   from {{ ref('int_shared__transaction_in_usd') }}
   where operation_type = 'EXPENSE'
),

cats as (
    select *        
    from {{ ref('int_shared__expense_category_with_hierarchy') }}
),

cpi as (
    select 
        date,
        value / first_value(value) over(partition by area_code, item_code order by date desc) as value
    from {{ ref('int_shared__cpi') }}
    where
        {# TODO: Change to proper mapping #}
        item_code = 'SA0'        
        AND area_code = '{{ env_var('PAH_CPI_AREA_CODE', '0000') }}'    
)

select 
    t.*,
    t.amount_usd / cpi.value as amount_in_usd_adjusted,
    c.category_name,
    c.category_group,
    c.depth as category_depth,
    {%- for i in range(1, get_max_depth(ref('int_shared__expense_category_ancestors')) + 1) %}
	c.cat_lev{{i}}_name,
    {%- endfor %}
    cpi.value
from expense_transactions as t
    inner join cats as c on t.budget_object_id = c.expense_category_id
    left join cpi 
        on {{ date_trunc("month", "cpi.date") }} = {{ date_trunc("month", "t.operation_date") }}            