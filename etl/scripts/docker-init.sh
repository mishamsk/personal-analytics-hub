#!/usr/bin/env bash

STEP_CNT=4

echo_step() {
cat <<EOF

######################################################################


Init Step ${1}/${STEP_CNT} [${2}] -- ${3}


######################################################################

EOF
}

# Wait for the database
psql $PAH_DATABASE_URL -p 5542 -c "select 1" &>/dev/null
while [ $? -ne 0 ]; do
  echo "Waiting for database to be ready..."
  sleep 1
  psql $PAH_DATABASE_URL -p 5542 -c "select 1" &>/dev/null
done

# Wait for the superset init container to finish
ping -c 1 pah_superset_init &>/dev/null
until [ $? -ne 0 ]; do
  echo "Init container hasn't finished yet"
  sleep 10
  ping -c 1 pah_superset_init &>/dev/null
done

set -e


# Initialize the database
echo_step "1" "Starting" "Applying DB migrations"
poetry run alembic upgrade head
echo_step "1" "Complete" "Applying DB migrations"

cd /app/dbt/pah
# Install dbt deps
echo_step "2" "Starting" "Installing dbt deps"
poetry run dbt deps
echo_step "2" "Complete" "Installing dbt deps"

# Load seed data
echo_step "3" "Starting" "Loading seed data"
poetry run dbt seed
echo_step "3" "Complete" "Loading seed data"

# Load data once
# echo_step "4" "Starting" "Loading data (initial)"
# poetry run loader load
# sleep 1
# cd /app/dbt/pah && poetry run dbt run
# echo_step "4" "Complete" "Loading data (initial)"
