{% macro to_utc(column_name) %}
    {{ column_name }}::timestamp at time zone '{{ env_var('PAH_DREBEDENGI_USER_TZ', 'UTC') }}'
{% endmacro %}
