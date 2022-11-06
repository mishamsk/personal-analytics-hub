{% macro get_max_depth(ref) %}
    {%- set sql_statement %}
        select max(depth) as max_depth from {{ ref }}
    {% endset -%}

    {%- set results = dbt_utils.get_query_results_as_dict(sql_statement) -%}
    {% if execute %}
    {%- set max_depth = results['max_depth']|first|int -%}
    {% else %}
    {%- set max_depth = 0 -%}
    {% endif %}

    {{ return(max_depth) }}
{% endmacro %}
