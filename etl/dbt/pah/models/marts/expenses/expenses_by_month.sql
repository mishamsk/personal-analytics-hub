WITH eca_only_max_depth AS (
	SELECT
		eca.expense_category_id,
		CASE eca.ancestor_id
		WHEN - 1 THEN
			eca. "name"
		ELSE
			eca.ancestor_name
		END AS ancestor_name,
		CASE eca.ancestor_id
		WHEN - 1 THEN
			eca.expense_category_id
		ELSE
			eca.ancestor_id
		END AS ancestor_id,
		CASE eca.ancestor_id
		WHEN - 1 THEN
			md. "depth"
		ELSE
			ad. "depth"
		END AS "depth"
	FROM
		{{ ref('int_shared__expense_category_ancestors') }} eca
		INNER JOIN {{ ref('int_shared__expense_category_with_group') }} md ON eca.expense_category_id = md.expense_category_id
			AND eca. "depth" = md. "depth"
	LEFT JOIN {{ ref('int_shared__expense_category_with_group') }} ad ON eca.ancestor_id = ad.expense_category_id
)
SELECT
	date_trunc('month', t.operation_date) AS oper_month,
	sum(abs(t.amount_usd)) AS amount_in_usd,
	c.ancestor_name AS category_name,
	c.depth AS category_depth
FROM
	{{ ref('int_shared__transaction_in_usd') }} t
	INNER JOIN eca_only_max_depth c ON t.budget_object_id = c.expense_category_id
GROUP BY
	oper_month,
	category_name,
	category_depth