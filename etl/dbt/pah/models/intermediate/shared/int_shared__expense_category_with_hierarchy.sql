WITH
joined as (
SELECT
	eca.expense_category_id,
	eca."name" as category_name,
	eg.category_group,    
	eca."depth"
    {%- for i in range(1, get_max_depth(ref('int_shared__expense_category_ancestors')) + 1) %}
	, max(case when eca."depth" - eca.ancestor_distance = {{i}} then eca.ancestor_name when eca."depth" - eca.ancestor_distance = 0 and eca."depth" = {{i}} then eca."name" end) as cat_lev{{i}}_name
    {%- endfor %}
FROM
	{{ ref('int_shared__expense_category_ancestors') }} eca
	left join {{ ref('int_shared__expense_category_with_group') }} eg on eca.expense_category_id = eg.expense_category_id
GROUP BY
	eca.expense_category_id, category_name, category_group, eca."depth"
)

SELECT
	*
 FROM joined