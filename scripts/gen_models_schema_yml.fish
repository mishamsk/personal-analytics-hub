# Run from the model folder

# Generate schema file
set model_folder (basename $PWD)
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
        else if test (string trim $line) = "models:"
            set found_model 1
        end
    end
end
