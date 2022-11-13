#!/bin/bash

# Wait for the init container to finish
ping -c 1 pah_etl_init &>/dev/null
until [ $? -ne 0 ]; do
  echo "Init container hasn't finished yet"
  sleep 10
  ping -c 1 pah_etl_init &>/dev/null
done

set -e

cd /app/dbt/pah
poetry run loader --log-path /app/log/ load
# some weird bug with dbt hanging...
sleep 1
poetry run dbt run >> /app/log/dbt.log
