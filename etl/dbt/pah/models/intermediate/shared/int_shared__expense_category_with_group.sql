WITH
joined as (
	SELECT
        expense_category_id,
        "name",
        "depth",
        ancestor_group AS category_group
    FROM (
        SELECT
            ca.*,
            CASE WHEN cg.category_group IS NOT NULL THEN
                cg.category_group
            ELSE
                cga.category_group
            END AS ancestor_group,
            RANK() OVER (PARTITION BY ca.expense_category_id ORDER BY ca.ancestor_distance) AS rank
        FROM
            {{ ref('int_shared__expense_category_ancestors') }} ca
        LEFT JOIN {{ ref('expense_category_group') }} cg ON ca."name" = cg."name"
        LEFT JOIN {{ ref('expense_category_group') }} cga ON ca.ancestor_name = cga."name"
    WHERE
        CASE WHEN cg.category_group IS NOT NULL THEN
            cg.category_group
        ELSE
            cga.category_group
        END IS NOT NULL) AS ranked
    WHERE
        rank = 1
)

SELECT
	*
 FROM joined