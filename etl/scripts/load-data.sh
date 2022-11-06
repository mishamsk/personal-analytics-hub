#!/bin/bash

# Wait for the init container to finish
ping -c 1 pah_etl_init &>/dev/null
until [ $? -ne 0 ]; do
  echo "Init container hasn't finished yet"
  sleep 10
  ping -c 1 pah_etl_init &>/dev/null
done

set -x
set -e

poetry run loader load
# some weird bug with dbt hanging...
sleep 1
cd /app/dbt/pah && poetry run dbt run
