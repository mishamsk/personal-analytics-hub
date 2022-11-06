WITH
all_cats as (
	SELECT 
		expense_category_id as category_id,
        parent_id,
        object_type,
		"name" as category_name
	FROM staging.stg_drebedengi__expense_category e
	UNION
	SELECT 
		income_source_id as category_id,
        parent_id,
		object_type,
		"name" as category_name
	FROM {{ ref('stg_drebedengi__income_source') }}
)

SELECT
	category_id,
	category_name,
    parent_id,
	object_type
 FROM all_cats