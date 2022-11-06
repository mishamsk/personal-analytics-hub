{% macro explode_ancestors(model, id_column, name_column, other_columns, parent_id_column="parent_id") %}
    {% set no_parent_value = env_var('PAH_NO_PARENT_VALUE', '__NO_PARENT__') %}

    WITH RECURSIVE
    orig_model as (
        SELECT 
            *
        FROM {{ ref(model) }}
    ),

    hierarchy_tree AS (
        SELECT 
            1 as depth,		
            {{ id_column }},
            {{ parent_id_column }},
            {{ name_column }},
            {% for column in other_columns -%}
            {{ column }},
            {% endfor %}
            ARRAY[parent_id] as path,
            ARRAY[cast ('{{ no_parent_value }}' as text)] as path_names,
            ARRAY[1] as distance
        FROM orig_model
        WHERE parent_id = -1
        UNION ALL
        SELECT
            p.depth + 1 as depth,
            c.{{ id_column }},
            c.{{ parent_id_column }},
            c.{{ name_column }},
            {% for column in other_columns -%}
            c.{{ column }},
            {% endfor %}
            p.path || c.parent_id as path,
            p.path_names || cast (p.{{ name_column }} as text) as path_names,
            p.depth + 1 || p.distance as distance
        FROM
            orig_model c
            INNER JOIN hierarchy_tree p ON c.parent_id = p.{{ id_column }}
    )

    SELECT
        {{ id_column }},
        {{ name_column }},
        {% for column in other_columns -%}
        {{ column }},
        {% endfor %}
        depth,
        UNNEST(path) as ancestor_id,
        UNNEST(distance) as ancestor_distance,
        UNNEST(path_names) as ancestor_name
    FROM hierarchy_tree
{% endmacro %}