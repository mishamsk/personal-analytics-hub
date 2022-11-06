# Run from the source folder

# Set sources to the list of source tables
set sources $argv

set model_folder (basename $PWD)
set source_name $model_folder

# Generate sources file
set sources_file _{$model_folder}_sources.yml

echo -n "version: 2

sources:
  - name: $model_folder
    schema: $model_folder
    tables:
" >$sources_file

for source in $sources
    echo "      - name: $source" >>$sources_file
end

# Generate models
for source in $sources
    dbt --profiles-dir ../../../ run-operation generate_base_model --args '{"source_name": "'$source_name'", "table_name": "'$source'"}' | tail -n +3 >stg_{$model_folder}__$source.sql
end

# Generate schema file
set schema_file _{$model_folder}_schema.yml

echo -n "version: 2

models:
" >$schema_file

for source in (find . -type f -name "*.sql" -print0 | string split0 | string sub -s 3 -e -4)
    if test $source = _{$model_folder}_schema
        continue
    end

    set output (dbt --profiles-dir ../../../ run-operation generate_model_yaml --args '{"model_name": "'$source'"}')
    set found_model 0
    for line in $output
        if test $found_model -eq 1
            echo $line >>$schema_file
        else if test $line = "models:"
            set found_model 1
        end
    end
end
